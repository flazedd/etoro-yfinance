"""Trade worker — the ONLY process that holds credentials and places orders.

It polls the SQLite `job` table for requests created by the web, runs one full
bbterminal->IBKR rebalance via run_bb_rebalance (dry-run or live per the job),
and writes the resulting RunSummary / OrderLog / Event rows back so the web can
display the plan, the fills, and the slippage.

    momentum-trade-worker            # poll forever (systemd service)
    momentum-trade-worker --once     # claim at most one job then exit (timer/cron)

Live execution still passes through every existing gate (bbterminal health +
freshness, the reviewed conid_map, pre-trade safety caps, RTH). The web can only
*request* a run; it can never place an order.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv

from ibkr_portfolio_connect.bb_rebalance import RebalanceInputError, run_bb_rebalance
from ibkr_portfolio_connect.bbterminal_client import BBTerminalClient
from ibkr_portfolio_connect.config import Settings
from ibkr_portfolio_connect.cost import RebalanceReport
from ibkr_portfolio_connect.db import (
    JOB_DONE,
    JOB_ERROR,
    JOB_KIND_BATCH_PLACE,
    JOB_KIND_BATCH_PREVIEW,
    JOB_KIND_MAPPING,
    JOB_KIND_ORDER_PLACE,
    JOB_KIND_ORDER_PREVIEW,
    JOB_KIND_PORTFOLIO,
    JOB_KIND_STRATEGIES,
    JOB_RUNNING,
    RUN_ABORTED,
    RUN_DRY_RUN,
    RUN_FAILED,
    RUN_PARTIAL,
    RUN_SUCCESS,
    TICKET_BLOCKED,
    TICKET_CONFIRMED,
    TICKET_FAILED,
    TICKET_PLACED,
    TICKET_PLACING,
    TICKET_PREVIEWED,
    Event,
    Job,
    OrderLog,
    RunSummary,
    claim_next_job,
    get_order_batch,
    get_order_ticket,
    get_session,
    init_db,
    save_order_batch,
    save_order_ticket,
    tickets_for_batch,
)
from ibkr_portfolio_connect.safety import PreTradeSafetyError

log = logging.getLogger(__name__)


def _f(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _run_status(report: RebalanceReport) -> str:
    if report.aborted_reason:
        return RUN_ABORTED
    if report.dry_run:
        return RUN_DRY_RUN
    if report.n_total == 0 or report.n_failed == 0:
        return RUN_SUCCESS
    if report.n_successful > 0:
        return RUN_PARTIAL
    return RUN_FAILED


def _record_report(
    session: Any, job: Job, report: RebalanceReport, *, strategy_id: int | None,
    strategy_name: str, as_of: str,
) -> RunSummary:
    run = RunSummary(
        job_id=job.id,
        strategy_id=strategy_id,
        strategy_name=strategy_name,
        as_of_date=as_of,
        dry_run=report.dry_run,
        status=_run_status(report),
        nav_eur=_f(report.nav),
        n_trades=report.n_total,
        n_success=report.n_successful,
        n_failed=report.n_failed,
        total_slippage_eur=_f(report.total_slippage_dollars),
        total_commission_eur=_f(report.total_commission_dollars),
        total_cost_pct=_f(report.total_cost_pct_of_nav),
        aborted_reason=report.aborted_reason or "",
    )
    session.add(run)
    session.commit()
    session.refresh(run)

    for tc in report.trades:
        t = tc.trade
        session.add(OrderLog(
            run_id=run.id,
            conid=getattr(t, "conid", None),
            symbol=getattr(t, "symbol", ""),
            exchange=getattr(t, "exchange", ""),
            side=getattr(t.side, "value", str(getattr(t, "side", ""))),
            quantity=_f(getattr(t, "quantity", 0)) or 0.0,
            reference_price=_f(getattr(t, "reference_price", None)),
            fill_price=_f(tc.fill_price),
            slippage_pct=_f(tc.slippage_pct),
            slippage_eur=_f(tc.slippage_dollars),
            commission=_f(tc.commission),
            status=tc.final_status or "",
            error=tc.error or "",
        ))
    session.commit()
    return run


def _record_aborted(session: Any, job: Job, *, status: str, reason: str,
                    strategy_id: int | None, strategy_name: str, as_of: str) -> RunSummary:
    run = RunSummary(
        job_id=job.id, strategy_id=strategy_id, strategy_name=strategy_name,
        as_of_date=as_of, dry_run=job.dry_run, status=status, aborted_reason=reason,
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def process_job(session: Any, job: Job, settings: Settings) -> None:
    """Run one claimed job to completion, recording everything. Dispatches on
    the job's kind — a data-refresh (no trading) or the rebalance."""
    if job.kind in (JOB_KIND_MAPPING, JOB_KIND_PORTFOLIO, JOB_KIND_STRATEGIES):
        _process_refresh(session, job, settings)
    elif job.kind in (JOB_KIND_ORDER_PREVIEW, JOB_KIND_ORDER_PLACE):
        _process_order(session, job, settings)
    elif job.kind in (JOB_KIND_BATCH_PREVIEW, JOB_KIND_BATCH_PLACE):
        _process_batch(session, job, settings)
    else:
        _process_rebalance(session, job, settings)


def _process_refresh(session: Any, job: Job, settings: Settings) -> None:
    """A read-only data refresh requested from the web: re-run a snapshot job
    (mapping or portfolio) and write its JSON. Never trades."""
    from datetime import UTC, datetime

    job.status = JOB_RUNNING
    session.add(job)
    session.commit()

    label = {JOB_KIND_MAPPING: "mapping", JOB_KIND_PORTFOLIO: "portfolio",
             JOB_KIND_STRATEGIES: "strategies"}.get(job.kind, "refresh")
    session.add(Event(level="info", title=f"{label} refresh started",
                      body=f"job #{job.id} ({job.requested_by})"))
    session.commit()

    try:
        summary = _run_refresh(job.kind, settings)
        job.status = JOB_DONE
        session.add(Event(level="info", title=f"{label} refresh finished", body=summary))
    except Exception as e:
        job.status = JOB_ERROR
        job.error = str(e)
        session.add(Event(level="error", title=f"{label} refresh error", body=str(e)))
        log.error("refresh job #%s failed", job.id, exc_info=True)

    job.finished_at = datetime.now(UTC)
    session.add(job)
    session.commit()


def _run_refresh(kind: str, settings: Settings) -> str:
    """Do the actual snapshot fetch (holds creds) and return a one-line summary."""
    from pathlib import Path

    from ibkr_portfolio_connect.ibkr_client import IBKRClient

    data_dir = Path(os.environ.get("MOMENTUM_DATA_DIR", "data"))
    if kind == JOB_KIND_MAPPING:
        from ibkr_portfolio_connect import mapping_snapshot as ms
        bb = BBTerminalClient.from_env()
        with IBKRClient(timeout=settings.http_timeout_seconds) as ibkr:
            snap = ms.build_snapshot(bb, ibkr, data_dir=data_dir)
        ms.write_local(snap, data_dir)
        c = snap["counts"]
        return (f"{c['tradable']} tradable, {c['unresolved']} unresolved"
                + (f" ({c['retryable']} retryable — re-run)" if c.get("retryable") else ""))

    if kind == JOB_KIND_STRATEGIES:
        # bbterminal only — no IBKR session needed to snapshot the schedules.
        from ibkr_portfolio_connect import strategies_snapshot as ss
        snap = ss.build_snapshot(BBTerminalClient.from_env())
        ss.write_local(snap, data_dir)
        return f"{snap['count']} strategies"

    from ibkr_portfolio_connect import portfolio_snapshot as ps
    with IBKRClient(timeout=settings.http_timeout_seconds) as ibkr:
        snap = ps.build_snapshot(ibkr, settings.ibkr_account_id,
                                 base_currency=settings.sizing_currency)
    ps.write_local(snap, data_dir)
    return f"{snap['n_positions']} positions"


def _process_order(session: Any, job: Job, settings: Settings) -> None:
    """A single manual test-buy: what-if it (preview) or place it (after the
    user's typed confirm). The web only ever creates the ticket + flips it to
    CONFIRMED; every IBKR call lives here. Never touches the rebalance path."""
    import json
    from datetime import UTC, datetime

    job.status = JOB_RUNNING
    session.add(job)
    session.commit()

    try:
        ticket_id = int(json.loads(job.payload or "{}").get("ticket_id"))
    except (ValueError, TypeError, json.JSONDecodeError):
        ticket_id = 0
    ticket = get_order_ticket(session, ticket_id) if ticket_id else None
    if ticket is None:
        job.status = JOB_ERROR
        job.error = f"order job #{job.id}: no ticket (payload={job.payload!r})"
        session.add(Event(level="error", title="order job error", body=job.error))
        job.finished_at = datetime.now(UTC)
        session.add(job)
        session.commit()
        return

    verb = "preview" if job.kind == JOB_KIND_ORDER_PREVIEW else "place"
    try:
        if job.kind == JOB_KIND_ORDER_PREVIEW:
            summary = _run_order_preview(session, ticket, settings)
        else:
            summary = _run_order_place(session, ticket, settings)
        job.status = JOB_DONE
        session.add(Event(level="info", title=f"order {verb}: {ticket.symbol}", body=summary))
    except Exception as e:
        job.status = JOB_ERROR
        job.error = str(e)
        # A place that raised leaves a real-money order in doubt — mark FAILED so
        # the UI shows it loudly; a preview that raised just can't be sized.
        ticket.status = TICKET_FAILED if job.kind == JOB_KIND_ORDER_PLACE else TICKET_BLOCKED
        ticket.error = str(e)
        save_order_ticket(session, ticket)
        session.add(Event(level="error", title=f"order {verb} error: {ticket.symbol}", body=str(e)))
        log.error("order job #%s (%s) failed", job.id, verb, exc_info=True)

    job.finished_at = datetime.now(UTC)
    session.add(job)
    session.commit()


def _preview_ticket(session: Any, ibkr: Any, ticket: Any, nav: Any, settings: Settings) -> str:
    """Size ONE ticket against a known NAV and what-if it → PREVIEWED / BLOCKED.
    No client creation or NAV fetch (the caller owns those) so a whole-strategy
    batch shares one IBKR session + one NAV read across all its holdings."""
    import json
    from decimal import Decimal

    from ibkr_portfolio_connect.ibkr_client import IBKRError
    from ibkr_portfolio_connect.order_ticket import parse_whatif, size_order
    from ibkr_portfolio_connect.schema import OrderSide

    ticket.nav_eur = float(nav)
    pct = Decimal(str(ticket.pct_of_nav))
    cap = settings.max_trade_pct_of_nav
    if cap is not None and pct > cap:
        ticket.status = TICKET_BLOCKED
        ticket.error = f"{pct}% exceeds the per-order cap of {cap}% of NAV"
        save_order_ticket(session, ticket)
        return f"blocked: {ticket.error}"

    price = Decimal(str(ticket.price_eur_ref)) if ticket.price_eur_ref else Decimal("0")
    sizing = size_order(nav_eur=nav, pct=pct, price_eur=price, fractional=ticket.fractional)
    ticket.target_eur = float(sizing.target_eur)
    if not sizing.ok:
        ticket.status = TICKET_BLOCKED
        ticket.error = sizing.blocked_reason or "could not size the order"
        save_order_ticket(session, ticket)
        return f"blocked: {ticket.error}"

    ticket.quantity = sizing.quantity
    ticket.est_cost_eur = float(sizing.est_cost_eur) if sizing.est_cost_eur is not None else None
    try:
        raw = ibkr.what_if_market_order(
            settings.ibkr_account_id, conid=ticket.conid, side=OrderSide.BUY,
            quantity=sizing.quantity, listing_exchange=ticket.listing_exchange or None,
        )
    except IBKRError as e:
        ticket.status = TICKET_BLOCKED
        ticket.error = f"IBKR declined the preview (commonly = not fractional-tradable): {e}"
        save_order_ticket(session, ticket)
        return f"blocked: {ticket.error}"

    wi = parse_whatif(raw)
    ticket.preview_json = json.dumps({
        "order_value": wi.order_value, "commission": wi.commission,
        "init_margin": wi.init_margin, "warnings": wi.warnings, "raw": wi.raw,
    }, default=str)
    ticket.error = ""
    ticket.status = TICKET_PREVIEWED
    save_order_ticket(session, ticket)
    return f"previewed {sizing.quantity} {ticket.symbol} (~€{ticket.est_cost_eur})"


def _submit_ticket(session: Any, ibkr: Any, ticket: Any, settings: Settings) -> str:
    """Place ONE ready ticket → PLACED, or FAILED on an IBKR error (caught, not
    raised, so a batch keeps going past a single bad fill)."""
    import json

    from ibkr_portfolio_connect.ibkr_client import IBKRError
    from ibkr_portfolio_connect.schema import OrderSide

    if not ticket.quantity or ticket.quantity <= 0:
        ticket.status = TICKET_FAILED
        ticket.error = "no quantity to place"
        save_order_ticket(session, ticket)
        return f"failed: {ticket.error}"

    ticket.status = TICKET_PLACING
    save_order_ticket(session, ticket)
    try:
        replies = ibkr.place_market_day_order(
            settings.ibkr_account_id, conid=ticket.conid, side=OrderSide.BUY,
            quantity=ticket.quantity, listing_exchange=ticket.listing_exchange or None,
        )
    except IBKRError as e:
        ticket.status = TICKET_FAILED
        ticket.error = str(e)
        save_order_ticket(session, ticket)
        return f"failed: {e}"

    reply = replies[0] if replies else None
    ticket.order_id = (reply.order_id or "") if reply else ""
    ticket.place_json = json.dumps([r.model_dump() for r in replies], default=str)
    _capture_slippage(ibkr, ticket, settings)  # best-effort: fill price + slippage
    ticket.error = ""
    ticket.status = TICKET_PLACED
    save_order_ticket(session, ticket)
    slip = f", slip {ticket.slippage_pct:+.2f}%" if ticket.slippage_pct is not None else ""
    return f"placed order {ticket.order_id or '(id pending)'} — {ticket.quantity} {ticket.symbol}{slip}"


def _capture_slippage(ibkr: Any, ticket: Any, settings: Settings) -> None:
    """Poll the just-placed order for its average fill price, then compute
    slippage vs bbterminal's reference (entry) price: signed % where + means we
    paid above the reference (a cost). Best-effort — leaves the fields None if
    the order hasn't filled or IBKR didn't surface a price."""
    import time as _time

    from ibkr_portfolio_connect.executor import _extract_fill_price, _poll_status

    if not ticket.order_id:
        return
    try:
        _status, _err, blob = _poll_status(
            client=ibkr, order_id=ticket.order_id,
            settle_timeout=settings.order_settle_timeout_seconds,
            poll_interval=settings.order_poll_interval_seconds,
            clock=_time.monotonic, sleeper=_time.sleep,
        )
    except Exception:
        log.warning("fill poll failed for order %s", ticket.order_id, exc_info=True)
        return

    fill = _extract_fill_price(blob or {})
    if fill is None:
        return
    ticket.fill_price = float(fill)
    ref = ticket.ref_price_local
    if ref and ref > 0:
        slip_pct = (float(fill) - ref) / ref * 100.0
        ticket.slippage_pct = slip_pct
        # EUR slippage = signed % applied to the reference cost in EUR.
        ticket.slippage_eur = slip_pct / 100.0 * (ticket.quantity or 0.0) * (ticket.price_eur_ref or 0.0)


def _run_order_preview(session: Any, ticket: Any, settings: Settings) -> str:
    """Single manual buy: fetch live NAV, then size + what-if the one ticket."""
    from ibkr_portfolio_connect.bb_rebalance import extract_nav
    from ibkr_portfolio_connect.ibkr_client import IBKRClient

    with IBKRClient(timeout=settings.http_timeout_seconds) as ibkr:
        nav = extract_nav(ibkr.portfolio_summary(settings.ibkr_account_id),
                          required_currency=settings.sizing_currency)
        return _preview_ticket(session, ibkr, ticket, nav, settings)


def _run_order_place(session: Any, ticket: Any, settings: Settings) -> str:
    """Single manual buy: refuse anything not CONFIRMED or outside RTH, else place."""
    from datetime import UTC, datetime

    from ibkr_portfolio_connect.executor import is_rth
    from ibkr_portfolio_connect.ibkr_client import IBKRClient

    if ticket.status != TICKET_CONFIRMED:
        raise RuntimeError(f"ticket #{ticket.id} is {ticket.status}, not confirmed — refusing to place")
    if settings.trading_hours_only and not is_rth(datetime.now(UTC)):
        ticket.status = TICKET_BLOCKED
        ticket.error = "outside regular trading hours — a MKT DAY order would be rejected; retry during RTH"
        save_order_ticket(session, ticket)
        return f"blocked: {ticket.error}"
    with IBKRClient(timeout=settings.http_timeout_seconds) as ibkr:
        return _submit_ticket(session, ibkr, ticket, settings)


def _process_batch(session: Any, job: Job, settings: Settings) -> None:
    """A whole-strategy buy: what-if every child ticket (preview) or place them
    one by one (place). The web only creates the batch + flips it CONFIRMED."""
    import json
    from datetime import UTC, datetime

    job.status = JOB_RUNNING
    session.add(job)
    session.commit()

    try:
        batch_id = int(json.loads(job.payload or "{}").get("batch_id"))
    except (ValueError, TypeError, json.JSONDecodeError):
        batch_id = 0
    batch = get_order_batch(session, batch_id) if batch_id else None
    if batch is None:
        job.status = JOB_ERROR
        job.error = f"batch job #{job.id}: no batch (payload={job.payload!r})"
        session.add(Event(level="error", title="batch job error", body=job.error))
        job.finished_at = datetime.now(UTC)
        session.add(job)
        session.commit()
        return

    verb = "preview" if job.kind == JOB_KIND_BATCH_PREVIEW else "place"
    try:
        if job.kind == JOB_KIND_BATCH_PREVIEW:
            summary = _run_batch_preview(session, batch, settings)
        else:
            summary = _run_batch_place(session, batch, settings)
        job.status = JOB_DONE
        session.add(Event(level="info", title=f"strategy buy {verb}: {batch.strategy_name}", body=summary))
    except Exception as e:
        job.status = JOB_ERROR
        job.error = str(e)
        batch.status = TICKET_FAILED
        batch.error = str(e)
        save_order_batch(session, batch)
        session.add(Event(level="error", title=f"strategy buy {verb} error", body=str(e)))
        log.error("batch job #%s (%s) failed", job.id, verb, exc_info=True)

    job.finished_at = datetime.now(UTC)
    session.add(job)
    session.commit()


def _run_batch_preview(session: Any, batch: Any, settings: Settings) -> str:
    """What-if every holding once, sharing one IBKR session + one NAV read."""
    from ibkr_portfolio_connect.bb_rebalance import extract_nav
    from ibkr_portfolio_connect.ibkr_client import IBKRClient

    tickets = tickets_for_batch(session, batch.id)
    with IBKRClient(timeout=settings.http_timeout_seconds) as ibkr:
        nav = extract_nav(ibkr.portfolio_summary(settings.ibkr_account_id),
                          required_currency=settings.sizing_currency)
        batch.nav_eur = float(nav)
        save_order_batch(session, batch)
        for ticket in tickets:
            _preview_ticket(session, ibkr, ticket, nav, settings)

    n_ok = sum(1 for t in tickets_for_batch(session, batch.id) if t.status == TICKET_PREVIEWED)
    batch.status = TICKET_PREVIEWED
    save_order_batch(session, batch)
    return f"{n_ok}/{len(tickets)} holdings buyable"


def _run_batch_place(session: Any, batch: Any, settings: Settings) -> str:
    """Place each CONFIRMED child ticket in turn, committing after each so the
    overview updates live. A failure is recorded and the batch moves on."""
    from datetime import UTC, datetime

    from ibkr_portfolio_connect.executor import is_rth
    from ibkr_portfolio_connect.ibkr_client import IBKRClient

    if batch.status != TICKET_CONFIRMED:
        raise RuntimeError(f"batch #{batch.id} is {batch.status}, not confirmed — refusing to place")
    if settings.trading_hours_only and not is_rth(datetime.now(UTC)):
        batch.status = TICKET_BLOCKED
        batch.error = "outside regular trading hours — MKT DAY orders would be rejected; retry during RTH"
        save_order_batch(session, batch)
        return f"blocked: {batch.error}"

    batch.status = TICKET_PLACING
    save_order_batch(session, batch)

    tickets = tickets_for_batch(session, batch.id)
    placed = failed = 0
    with IBKRClient(timeout=settings.http_timeout_seconds) as ibkr:
        for ticket in tickets:
            if ticket.status != TICKET_CONFIRMED:
                continue  # blocked / already-terminal holdings are skipped
            summary = _submit_ticket(session, ibkr, ticket, settings)
            done = ticket.status == TICKET_PLACED
            placed += 1 if done else 0
            failed += 0 if done else 1
            session.add(Event(level="info" if done else "warn",
                              title=f"strategy buy: {ticket.symbol}", body=summary))
            session.commit()

    batch.status = TICKET_PLACED if placed else TICKET_FAILED
    batch.error = "" if placed else "no orders were placed"
    save_order_batch(session, batch)
    return f"placed {placed}, failed {failed}"


def _process_rebalance(session: Any, job: Job, settings: Settings) -> None:
    """Run one claimed rebalance job to completion, recording everything."""
    job.status = JOB_RUNNING
    session.add(job)
    session.commit()

    # Strategy metadata up front (the worker has creds) for nice labelling.
    strategy_id: int | None = None
    strategy_name = ""
    as_of = ""
    bb = BBTerminalClient.from_env()
    try:
        scheds = bb.schedules(enabled_only=True)
        if scheds:
            strategy_id = scheds[0].get("strategy_id")
            strategy_name = scheds[0].get("name", "")
            if strategy_id is not None:
                as_of = bb.schedule(strategy_id).get("as_of_date", "")
    except Exception:
        log.warning("could not fetch strategy metadata", exc_info=True)

    mode = "dry-run" if job.dry_run else "LIVE"
    session.add(Event(level="info", title=f"rebalance {mode} started",
                      body=f"job #{job.id} ({job.requested_by})"))
    session.commit()

    try:
        report = run_bb_rebalance(settings, bb=bb, dry_run=job.dry_run)
        run = _record_report(session, job, report,
                             strategy_id=strategy_id, strategy_name=strategy_name, as_of=as_of)
        job.status = JOB_DONE
    except (RebalanceInputError, PreTradeSafetyError) as e:
        run = _record_aborted(session, job, status=RUN_ABORTED, reason=str(e),
                              strategy_id=strategy_id, strategy_name=strategy_name, as_of=as_of)
        job.status = JOB_DONE  # the job ran; the run is aborted (a normal outcome)
        session.add(Event(run_id=run.id, level="warn", title="rebalance aborted (gate)", body=str(e)))
    except Exception as e:
        run = _record_aborted(session, job, status="error", reason=str(e),
                              strategy_id=strategy_id, strategy_name=strategy_name, as_of=as_of)
        job.status = JOB_ERROR
        job.error = str(e)
        session.add(Event(run_id=run.id, level="error", title="rebalance error", body=str(e)))
        log.error("job #%s failed", job.id, exc_info=True)

    from datetime import UTC, datetime
    job.finished_at = datetime.now(UTC)
    job.run_id = run.id
    session.add(job)
    session.add(Event(run_id=run.id, level="info",
                      title=f"rebalance {mode} finished", body=f"status={run.status}"))
    session.commit()


def run_once(settings: Settings) -> bool:
    """Claim and process at most one job. Returns True if a job was handled."""
    with get_session() as session:
        job = claim_next_job(session)
        if job is None:
            return False
        log.info("claimed job #%s (dry_run=%s)", job.id, job.dry_run)
        process_job(session, job, settings)
        return True


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    load_dotenv()
    parser = argparse.ArgumentParser(description="Momentum trade worker")
    parser.add_argument("--once", action="store_true", help="process one job then exit")
    parser.add_argument("--enqueue", action="store_true",
                        help="queue an automatic monthly run (dry per DRY_RUN) then exit; "
                             "the always-on worker processes it")
    parser.add_argument("--poll", type=float, default=5.0, help="seconds between polls")
    args = parser.parse_args()

    init_db()
    settings = Settings()  # type: ignore[call-arg]  # pydantic-settings reads env

    if args.enqueue:
        from ibkr_portfolio_connect.db import get_session, request_job
        with get_session() as s:
            job = request_job(s, dry_run=settings.dry_run, requested_by="timer",
                              note="scheduled monthly rebalance")
        print(f"queued job #{job.id} (dry_run={settings.dry_run})")
        return 0

    if args.once:
        handled = run_once(settings)
        print("processed one job" if handled else "no jobs queued")
        return 0

    log.info("worker polling every %ss (Ctrl-C to stop)", args.poll)
    while True:
        try:
            if not run_once(settings):
                time.sleep(args.poll)
        except KeyboardInterrupt:
            log.info("worker stopped")
            return 0
        except Exception:
            log.error("worker loop error", exc_info=True)
            time.sleep(args.poll)


if __name__ == "__main__":
    sys.exit(main())
