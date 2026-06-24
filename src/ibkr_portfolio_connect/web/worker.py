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
    JOB_RUNNING,
    RUN_ABORTED,
    RUN_DRY_RUN,
    RUN_FAILED,
    RUN_PARTIAL,
    RUN_SUCCESS,
    Event,
    Job,
    OrderLog,
    RunSummary,
    claim_next_job,
    get_session,
    init_db,
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
    """Run one claimed job to completion, recording everything."""
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
