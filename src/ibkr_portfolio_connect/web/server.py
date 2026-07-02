"""FastAPI app — read-only views + a gated job-request endpoint. No credentials.

The app reads the universe artifacts, the performance snapshot, and the SQLite
run/job tables. The single state-changing endpoint, POST /execution/request,
only inserts a `job` row; the worker (separate process, holds creds) is what
actually trades. A LIVE request additionally requires the user to type a
confirmation phrase, so a stray click can't fire real orders.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ibkr_portfolio_connect.db import (
    JOB_KIND_BATCH_PLACE,
    JOB_KIND_BATCH_PREVIEW,
    JOB_KIND_MAPPING,
    JOB_KIND_ORDER_PLACE,
    JOB_KIND_ORDER_PREVIEW,
    JOB_KIND_PORTFOLIO,
    JOB_KIND_STRATEGIES,
    TICKET_CONFIRMED,
    TICKET_PLACING,
    TICKET_PREVIEWED,
    TICKET_REQUESTED,
    create_order_batch,
    create_order_ticket,
    default_db_path,
    get_order_batch,
    get_order_ticket,
    get_run,
    get_session,
    init_db,
    list_jobs,
    list_runs,
    orders_for_run,
    placed_order_tickets,
    recent_events,
    request_job,
    save_order_batch,
    save_order_ticket,
    tickets_for_batch,
)
from ibkr_portfolio_connect.order_ticket import is_fractional_eligible

from . import data as datamod
from . import diagnostics as diag

_HERE = Path(__file__).parent
CONFIRM_PHRASE = "EXECUTE"


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(title="Momentum stack", docs_url=None, redoc_url=None)
    templates = Jinja2Templates(directory=str(_HERE / "templates"))
    app.mount("/static", StaticFiles(directory=str(_HERE / "static")), name="static")

    # Cache-bust static assets by the built CSS's mtime, so a rebuilt tailwind.css
    # is picked up on the next page load instead of a stale browser-cached copy.
    try:
        asset_v = str(int((_HERE / "static" / "tailwind.css").stat().st_mtime))
    except OSError:
        asset_v = "0"
    templates.env.globals["asset_v"] = asset_v

    def page(request: Request, name: str, ctx: dict[str, Any]) -> HTMLResponse:
        return templates.TemplateResponse(request, name, {"active": ctx.pop("active", ""), **ctx})

    # ── home ─────────────────────────────────────────────────────────────────
    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return page(request, "home.html", {"active": "home", "home": _home_summary()})

    @app.get("/mapping", response_class=HTMLResponse)
    def mapping(request: Request, q: str = "", kind: str = "", status: str = "",
                queued: str = "") -> HTMLResponse:
        snap = datamod.load_mapping()
        age = datamod.snapshot_age_seconds("mapping_snapshot.json", time.time())
        rows = _filter_mapping(snap.get("rows", []), q=q, kind=kind, status=status)
        return page(request, "mapping.html", {
            "active": "mapping", "snap": snap, "age": age, "rows": rows[:3000],
            "q": q, "kind": kind, "status": status, "shown": len(rows),
            "refresh": _refresh_status(JOB_KIND_MAPPING), "queued": queued,
        })

    @app.get("/mapping/rows", response_class=HTMLResponse)
    def mapping_rows(request: Request, q: str = "", kind: str = "", status: str = "") -> HTMLResponse:
        rows = _filter_mapping(datamod.load_mapping().get("rows", []), q=q, kind=kind, status=status)
        return templates.TemplateResponse(request, "_mapping_rows.html",
                                          {"rows": rows[:3000], "shown": len(rows)})

    @app.post("/mapping/refresh")
    def mapping_refresh() -> RedirectResponse:
        with get_session() as s:
            request_job(s, kind=JOB_KIND_MAPPING, requested_by="web",
                        note="refresh mapping from IBKR")
        return RedirectResponse("/mapping?queued=1", status_code=303)

    # ── execution ────────────────────────────────────────────────────────────
    @app.get("/execution", response_class=HTMLResponse)
    def execution(request: Request) -> HTMLResponse:
        with get_session() as s:
            runs = list_runs(s, limit=50)
            jobs = list_jobs(s, limit=10)
            latest_plan = next((r for r in runs if r.dry_run), None)
            plan_orders = (
                orders_for_run(s, latest_plan.id)
                if latest_plan and latest_plan.id is not None else []
            )
            events = recent_events(s, limit=15)
        return page(request, "execution.html", {
            "active": "execution", "runs": runs, "jobs": jobs,
            "latest_plan": latest_plan, "plan_orders": plan_orders, "events": events,
            "confirm_phrase": CONFIRM_PHRASE,
        })

    @app.post("/execution/request")
    def execution_request(mode: str = Form("dry"), confirm: str = Form("")) -> RedirectResponse:
        dry = mode != "live"
        if not dry and confirm.strip() != CONFIRM_PHRASE:
            # Refuse a live run without the typed confirmation.
            return RedirectResponse("/execution?error=confirm", status_code=303)
        with get_session() as s:
            request_job(s, dry_run=dry, requested_by="web",
                        note="dry-run plan" if dry else "live execution")
        return RedirectResponse("/execution", status_code=303)

    @app.get("/execution/runs/{run_id}", response_class=HTMLResponse)
    def run_detail(request: Request, run_id: int) -> HTMLResponse:
        with get_session() as s:
            run = get_run(s, run_id)
            orders = orders_for_run(s, run_id) if run else []
        return page(request, "run_detail.html", {"active": "execution", "run": run, "orders": orders})

    # ── performance ──────────────────────────────────────────────────────────
    @app.get("/performance", response_class=HTMLResponse)
    def performance(request: Request) -> HTMLResponse:
        snap = datamod.load_performance()
        return page(request, "performance.html", {"active": "performance", "snap": snap})

    # ── portfolio (live IBKR holdings) ───────────────────────────────────────
    @app.get("/portfolio", response_class=HTMLResponse)
    def portfolio(request: Request, queued: str = "") -> HTMLResponse:
        snap = datamod.load_portfolio()
        age = datamod.snapshot_age_seconds("portfolio_snapshot.json", time.time())
        return page(request, "portfolio.html",
                    {"active": "portfolio", "snap": snap, "age": age,
                     "refresh": _refresh_status(JOB_KIND_PORTFOLIO), "queued": queued})

    @app.post("/portfolio/refresh")
    def portfolio_refresh() -> RedirectResponse:
        with get_session() as s:
            request_job(s, kind=JOB_KIND_PORTFOLIO, requested_by="web",
                        note="refresh portfolio from IBKR")
        return RedirectResponse("/portfolio?queued=1", status_code=303)

    # ── strategies (scheduled bbterminal strategies + holdings) ──────────────
    @app.get("/strategies", response_class=HTMLResponse)
    def strategies(request: Request, queued: str = "") -> HTMLResponse:
        snap = datamod.load_strategies()
        age = datamod.snapshot_age_seconds("strategies_snapshot.json", time.time())
        strats = _enrich_strategies(snap.get("strategies", []), datamod.load_mapping())
        return page(request, "strategies.html",
                    {"active": "strategies", "snap": snap, "age": age, "strategies": strats,
                     "refresh": _refresh_status(JOB_KIND_STRATEGIES), "queued": queued,
                     "max_pct": _max_order_pct()})

    @app.post("/strategies/refresh")
    def strategies_refresh() -> RedirectResponse:
        with get_session() as s:
            request_job(s, kind=JOB_KIND_STRATEGIES, requested_by="web",
                        note="refresh strategies from bbterminal")
        return RedirectResponse("/strategies?queued=1", status_code=303)

    @app.get("/api/strategies")
    def api_strategies() -> JSONResponse:
        return JSONResponse(datamod.load_strategies())

    # ── single-stock manual test-buy (preview → confirm → place) ─────────────
    @app.post("/strategies/buy")
    def strategies_buy(
        conid: int = Form(...), symbol: str = Form(""), name: str = Form(""),
        currency: str = Form(""), listing_exchange: str = Form(""),
        strategy_id: str = Form(""), price_eur: str = Form(""),
        ref_price_local: str = Form(""), pct: float = Form(5.0),
    ) -> RedirectResponse:
        """Web NEVER trades — this only records an OrderTicket and queues a
        what-if job. The worker sizes + previews; the user must then confirm."""
        def _f(v: str) -> float | None:
            try:
                return float(v) if v not in ("", "None") else None
            except ValueError:
                return None

        with get_session() as s:
            ticket = create_order_ticket(
                s, conid=conid, symbol=symbol, name=name, currency=currency,
                listing_exchange=listing_exchange,
                strategy_id=int(strategy_id) if strategy_id.isdigit() else None,
                pct_of_nav=max(0.0, float(pct)), price_eur_ref=_f(price_eur),
                ref_price_local=_f(ref_price_local),
                fractional=is_fractional_eligible(listing_exchange), requested_by="web",
            )
            request_job(s, kind=JOB_KIND_ORDER_PREVIEW, requested_by="web",
                        note=f"preview buy {symbol}", payload=json.dumps({"ticket_id": ticket.id}))
            tid = ticket.id
        return RedirectResponse(f"/trade/{tid}", status_code=303)

    @app.get("/trade/{ticket_id}", response_class=HTMLResponse)
    def trade(request: Request, ticket_id: int, error: str = "") -> HTMLResponse:
        with get_session() as s:
            ticket = get_order_ticket(s, ticket_id)
        preview: dict[str, Any] = {}
        if ticket and ticket.preview_json:
            try:
                preview = json.loads(ticket.preview_json)
            except json.JSONDecodeError:
                preview = {}
        # Still-working states self-reload until the worker lands a terminal one.
        polling = ticket is not None and ticket.status in (
            TICKET_REQUESTED, TICKET_CONFIRMED, TICKET_PLACING)
        return page(request, "trade.html", {
            "active": "strategies", "ticket": ticket, "preview": preview,
            "confirm_phrase": CONFIRM_PHRASE, "polling": polling, "error": error,
        })

    @app.post("/trade/{ticket_id}/confirm")
    def trade_confirm(ticket_id: int, confirm: str = Form("")) -> RedirectResponse:
        with get_session() as s:
            ticket = get_order_ticket(s, ticket_id)
            if ticket is None:
                return RedirectResponse("/strategies", status_code=303)
            # Only a PREVIEWED ticket with the exact phrase may become a real order.
            if confirm.strip() != CONFIRM_PHRASE or ticket.status != TICKET_PREVIEWED:
                return RedirectResponse(f"/trade/{ticket_id}?error=confirm", status_code=303)
            ticket.status = TICKET_CONFIRMED
            save_order_ticket(s, ticket)
            request_job(s, kind=JOB_KIND_ORDER_PLACE, requested_by="web",
                        note=f"place buy {ticket.symbol}", payload=json.dumps({"ticket_id": ticket.id}))
        return RedirectResponse(f"/trade/{ticket_id}", status_code=303)

    # ── whole-strategy buy (basket: preview all → confirm → place one by one) ─
    @app.post("/strategies/buy-basket")
    def strategies_buy_basket(strategy_id: int = Form(...), total_pct: float = Form(50.0)) -> RedirectResponse:
        """Create one ticket per tradable holding (sized total-pct x weight) under
        a batch, and queue a single what-if job. No IBKR calls here."""
        strat = next((s for s in _enrich_strategies(
            datamod.load_strategies().get("strategies", []), datamod.load_mapping())
            if s.get("strategy_id") == strategy_id), None)
        if strat is None:
            return RedirectResponse("/strategies", status_code=303)
        total = max(0.0, float(total_pct))
        with get_session() as s:
            batch = create_order_batch(s, strategy_id=strategy_id,
                                       strategy_name=strat.get("name", ""),
                                       total_pct=total, requested_by="web")
            for h in strat.get("holdings", []):
                if not h.get("conid"):
                    continue
                weight = float(h.get("target_weight") or 0.0)
                create_order_ticket(
                    s, batch_id=batch.id, weight=weight, conid=h["conid"],
                    symbol=h.get("ibkr_symbol") or h.get("ticker") or "",
                    name=h.get("company_name") or "", currency=h.get("currency") or "",
                    listing_exchange=h.get("ibkr_listing") or "", strategy_id=strategy_id,
                    pct_of_nav=total * weight, price_eur_ref=_as_float(h.get("entry_price_eur")),
                    ref_price_local=_as_float(h.get("entry_price_local")),
                    fractional=is_fractional_eligible(h.get("ibkr_listing")), requested_by="web",
                )
            request_job(s, kind=JOB_KIND_BATCH_PREVIEW, requested_by="web",
                        note=f"preview strategy buy {strat.get('name', '')}",
                        payload=json.dumps({"batch_id": batch.id}))
            bid = batch.id
        return RedirectResponse(f"/basket/{bid}", status_code=303)

    @app.get("/basket/{batch_id}", response_class=HTMLResponse)
    def basket(request: Request, batch_id: int, error: str = "") -> HTMLResponse:
        with get_session() as s:
            batch = get_order_batch(s, batch_id)
            tickets = tickets_for_batch(s, batch_id) if batch else []
        buyable = [t for t in tickets if t.status in (
            TICKET_PREVIEWED, TICKET_CONFIRMED, TICKET_PLACING, "placed")]
        filled = [t for t in tickets if t.slippage_eur is not None]
        totals = {
            "n": len(tickets),
            "buyable": len(buyable),
            "blocked": sum(1 for t in tickets if t.status == "blocked"),
            "placed": sum(1 for t in tickets if t.status == "placed"),
            "failed": sum(1 for t in tickets if t.status == "failed"),
            "est_eur": sum(t.est_cost_eur or 0.0 for t in buyable),
            "slippage_eur": sum(t.slippage_eur for t in filled) if filled else None,
            "slippage_pct": (sum(t.slippage_pct or 0.0 for t in filled) / len(filled)) if filled else None,
        }
        polling = batch is not None and batch.status in (
            TICKET_REQUESTED, TICKET_CONFIRMED, TICKET_PLACING)
        return page(request, "basket.html", {
            "active": "strategies", "batch": batch, "tickets": tickets,
            "totals": totals, "confirm_phrase": CONFIRM_PHRASE, "polling": polling, "error": error,
        })

    @app.post("/basket/{batch_id}/confirm")
    def basket_confirm(batch_id: int, confirm: str = Form("")) -> RedirectResponse:
        with get_session() as s:
            batch = get_order_batch(s, batch_id)
            if batch is None:
                return RedirectResponse("/strategies", status_code=303)
            if confirm.strip() != CONFIRM_PHRASE or batch.status != TICKET_PREVIEWED:
                return RedirectResponse(f"/basket/{batch_id}?error=confirm", status_code=303)
            for t in tickets_for_batch(s, batch_id):
                if t.status == TICKET_PREVIEWED:
                    t.status = TICKET_CONFIRMED
                    save_order_ticket(s, t)
            batch.status = TICKET_CONFIRMED
            save_order_batch(s, batch)
            request_job(s, kind=JOB_KIND_BATCH_PLACE, requested_by="web",
                        note=f"place strategy buy {batch.strategy_name}",
                        payload=json.dumps({"batch_id": batch_id}))
        return RedirectResponse(f"/basket/{batch_id}", status_code=303)

    # ── positions (per-strategy attributed ledger — Option B) ────────────────
    @app.get("/positions", response_class=HTMLResponse)
    def positions(request: Request) -> HTMLResponse:
        return page(request, "positions.html", {"active": "positions", "book": _strategy_book()})

    @app.get("/api/positions")
    def api_positions() -> JSONResponse:
        return JSONResponse(_strategy_book())

    # ── diagnostics (RPi4 system health) ─────────────────────────────────────
    @app.get("/diagnostics", response_class=HTMLResponse)
    def diagnostics(request: Request) -> HTMLResponse:
        return page(request, "diagnostics.html", {"active": "diagnostics", "d": _diag()})

    # ── api / health ─────────────────────────────────────────────────────────
    @app.get("/api/performance")
    def api_performance() -> JSONResponse:
        return JSONResponse(datamod.load_performance())

    @app.get("/api/portfolio")
    def api_portfolio() -> JSONResponse:
        return JSONResponse(datamod.load_portfolio())

    @app.get("/api/diagnostics")
    def api_diagnostics() -> JSONResponse:
        return JSONResponse(_diag())

    @app.get("/api/mapping")
    def api_mapping() -> JSONResponse:
        return JSONResponse(datamod.load_mapping())

    @app.get("/healthz")
    def healthz() -> dict[str, bool]:
        return {"ok": True}

    return app


def _refresh_status(kind: str) -> dict[str, Any]:
    """Whether a refresh job of this kind is queued/running, plus the most recent
    finished one — so a page can show 'refreshing…' and the last result."""
    with get_session() as s:
        jobs = [j for j in list_jobs(s, limit=50) if j.kind == kind]
    pending = next((j for j in jobs if j.finished_at is None), None)
    last = next((j for j in jobs if j.finished_at is not None), None)
    return {
        "pending": pending is not None,
        "pending_status": pending.status if pending else None,
        "last_status": last.status if last else None,
        "last_error": (last.error if last else "") or "",
        "last_finished": last.finished_at.isoformat(timespec="seconds") if last and last.finished_at else None,
    }


def _as_float(v: Any) -> float | None:
    try:
        return float(v) if v not in (None, "", "None") else None
    except (TypeError, ValueError):
        return None


def _strategy_book() -> dict[str, Any]:
    """Per-strategy attributed positions (Option B — logical separation in one
    IBKR account). Aggregates PLACED buy tickets by strategy_id, joins the
    portfolio snapshot for current value / P&L, and reconciles Σ attributed
    shares per conid against IBKR's single netted position so the split can't
    silently drift. Reads DB + snapshot only — no IBKR calls."""
    portfolio = datamod.load_portfolio()
    pos_by_conid = {p["conid"]: p for p in portfolio.get("positions", []) if p.get("conid")}
    names = {s.get("strategy_id"): s.get("name")
             for s in datamod.load_strategies().get("strategies", [])}

    with get_session() as s:
        placed = placed_order_tickets(s)

    sym_by_conid = {t.conid: t.symbol for t in placed}
    strategies: dict[Any, dict[str, Any]] = {}
    attributed: dict[int, float] = {}
    for t in placed:
        strat = strategies.setdefault(t.strategy_id, {
            "strategy_id": t.strategy_id,
            "name": names.get(t.strategy_id)
            or (f"strategy #{t.strategy_id}" if t.strategy_id else "unattributed"),
            "positions": {},
        })
        pos = strat["positions"].setdefault(t.conid, {
            "conid": t.conid, "symbol": t.symbol, "name": t.name, "qty": 0.0, "cost_eur": 0.0})
        pos["qty"] += t.quantity or 0.0
        pos["cost_eur"] += t.est_cost_eur or 0.0
        attributed[t.conid] = attributed.get(t.conid, 0.0) + (t.quantity or 0.0)

    out_strats: list[dict[str, Any]] = []
    for strat in strategies.values():
        rows, cost_sum, val_sum, have_val = [], 0.0, 0.0, False
        for pos in strat["positions"].values():
            snap = pos_by_conid.get(pos["conid"])
            per_share = ((snap.get("market_value") or 0.0) / snap["quantity"]
                         if snap and snap.get("quantity") else None)
            value = pos["qty"] * per_share if per_share is not None else None
            pnl = (value - pos["cost_eur"]) if value is not None else None
            rows.append({**pos, "value_eur": value, "pnl_eur": pnl,
                         "pnl_pct": (pnl / pos["cost_eur"] * 100)
                         if pnl is not None and pos["cost_eur"] else None})
            cost_sum += pos["cost_eur"]
            if value is not None:
                val_sum += value
                have_val = True
        rows.sort(key=lambda r: r["cost_eur"], reverse=True)
        out_strats.append({
            "strategy_id": strat["strategy_id"], "name": strat["name"], "positions": rows,
            "cost_eur": cost_sum, "value_eur": val_sum if have_val else None,
            "pnl_eur": (val_sum - cost_sum) if have_val else None})
    out_strats.sort(key=lambda s: (s["strategy_id"] is None, s["strategy_id"] or 0))

    recon = []
    for conid in sorted(set(attributed) | set(pos_by_conid)):
        snap = pos_by_conid.get(conid)
        ibkr_qty = float(snap["quantity"]) if snap and snap.get("quantity") is not None else 0.0
        attr_qty = attributed.get(conid, 0.0)
        diff = ibkr_qty - attr_qty
        if attr_qty == 0:
            flag = "unattributed"          # IBKR holds it, no strategy claims it
        elif abs(diff) <= 1e-6:
            flag = "matched"
        else:
            flag = "over" if diff > 0 else "under"
        recon.append({"conid": conid, "symbol": (snap or {}).get("symbol") or sym_by_conid.get(conid, ""),
                      "attributed": attr_qty, "ibkr": ibkr_qty, "diff": diff, "flag": flag})
    recon.sort(key=lambda r: (r["flag"] == "matched", r["symbol"]))

    return {"strategies": out_strats, "reconciliation": recon,
            "has_portfolio": bool(portfolio), "n_positions": portfolio.get("n_positions"),
            "portfolio_age": datamod.snapshot_age_seconds("portfolio_snapshot.json", time.time()),
            "n_placed": len(placed)}


def _max_order_pct() -> float:
    """The single-order size ceiling shown as the % input's max — mirrors the
    worker's `max_trade_pct_of_nav` cap. Read from env (default 50) so the
    credential-free web never has to build a full Settings()."""
    try:
        return float(os.environ.get("MAX_TRADE_PCT_OF_NAV", "50"))
    except ValueError:
        return 50.0


def _enrich_strategies(strategies: list[dict[str, Any]],
                       mapping: dict[str, Any]) -> list[dict[str, Any]]:
    """Attach each holding's IBKR resolution (conid, confidence, quote link) from
    the local mapping snapshot — no network, mirrors the Mapping tab. Matches on
    company_id, then ISIN — both globally unique, so no risk of a same-ticker
    collision picking the wrong company. ETFs are keyed by benchmark_id in the
    mapping, so they only line up via ISIN. Unmatched holdings (e.g. CASH) stay
    bare."""
    rows = mapping.get("rows", [])
    by_cid = {str(r.get("company_id")): r for r in rows}
    by_isin = {r["isin"]: r for r in rows if r.get("isin")}
    out: list[dict[str, Any]] = []
    for strat in strategies:
        holdings = []
        for h in strat.get("holdings", []):
            m = (by_cid.get(str(h.get("company_id")))
                 or by_isin.get(h.get("isin"))
                 or {})
            holdings.append({
                **h,
                "conid": m.get("conid"),
                "confidence": m.get("confidence"),
                "ibkr_symbol": m.get("ibkr_symbol"),
                "ibkr_listing": m.get("ibkr_listing"),
                "ibkr_quote_url": m.get("ibkr_quote_url"),
                "tradable": m.get("tradable"),
            })
        out.append({**strat, "holdings": holdings})
    return out


def _home_summary() -> dict[str, Any]:
    """Light, credential-free rollup for the landing page — one live stat per
    page, read from the same snapshots/DB each page uses. Everything degrades to
    an empty/None value the template renders as a hint."""
    now = time.time()
    mapping = datamod.load_mapping()
    portfolio = datamod.load_portfolio()
    performance = datamod.load_performance()
    with get_session() as s:
        runs = list_runs(s, limit=1)
        jobs = list_jobs(s, limit=50)
        last_run = runs[0] if runs else None
        exec_info = {
            "last_status": last_run.status if last_run else None,
            "last_dry_run": last_run.dry_run if last_run else None,
            "pending": sum(1 for j in jobs if j.finished_at is None),
        }
    return {
        "mapping": {
            "counts": mapping.get("counts", {}),
            "label": mapping.get("label"),
            "age": datamod.snapshot_age_seconds("mapping_snapshot.json", now),
        },
        "portfolio": {
            "nav": portfolio.get("nav"),
            "n_positions": portfolio.get("n_positions"),
            "age": datamod.snapshot_age_seconds("portfolio_snapshot.json", now),
        },
        "performance": {
            "since_inception_return_pct": performance.get("since_inception_return_pct"),
            "mtd_return_pct": performance.get("mtd_return_pct"),
            "age": datamod.snapshot_age_seconds("performance_snapshot.json", now),
        },
        "execution": exec_info,
        "diagnostics": {"overall": _diag().get("overall")},
    }


def _diag() -> dict[str, Any]:
    now = time.time()
    return diag.collect(
        now,
        db_path=str(default_db_path()),
        snapshots={
            "portfolio": datamod.snapshot_age_seconds("portfolio_snapshot.json", now),
            "performance": datamod.snapshot_age_seconds("performance_snapshot.json", now),
        },
    )


def _filter_mapping(
    rows: list[dict[str, Any]], *, q: str, kind: str, status: str
) -> list[dict[str, Any]]:
    ql = q.lower().strip()
    out = []
    for r in rows:
        if kind and r.get("kind") != kind:
            continue
        if status == "tradable" and not r.get("tradable"):
            continue
        if status == "unresolved" and r.get("tradable"):
            continue
        if ql and ql not in (
            f"{r.get('name','')} {r.get('ticker','')} {r.get('isin','')} "
            f"{r.get('ibkr_symbol','')} {r.get('conid','')}".lower()
        ):
            continue
        out.append(r)
    return out


app = create_app()


def main() -> int:
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="Momentum read-only web UI")
    parser.add_argument("--host", default=os.environ.get("MOMENTUM_WEB_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MOMENTUM_WEB_PORT", "8800")))
    parser.add_argument(
        "--reload", action="store_true",
        default=os.environ.get("MOMENTUM_WEB_RELOAD", "").lower() in ("1", "true", "yes"),
        help="auto-restart on code changes (local dev only)",
    )
    args = parser.parse_args()

    # reload watches this package so edits to routes/data loaders take effect
    # without a manual restart; templates/static are already re-read per request.
    reload_dirs = [str(_HERE.parent)] if args.reload else None
    uvicorn.run(
        "ibkr_portfolio_connect.web.server:app",
        host=args.host, port=args.port, log_level="info",
        reload=args.reload, reload_dirs=reload_dirs,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
