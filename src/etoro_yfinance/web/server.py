"""FastAPI app — read-only views over the eToro→yfinance universe. No credentials.

The app reads a single offline-built artifact (data/etoro_universe_mapping.json)
and system diagnostics. It never calls eToro or any broker — trading lives in the
CLI (scripts/etoro_trade.py). Pages: Home, eToro↔yfinance universe, Diagnostics.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from etoro_yfinance import universe as universe_mod
from etoro_yfinance.yfinance_map import is_crypto_quote_dupe, is_future

from . import data as datamod
from . import diagnostics as diag

_HERE = Path(__file__).parent
_UNIVERSE_CAP = 1500  # rows rendered at once (the universe is ~15.5k)


def create_app() -> FastAPI:
    app = FastAPI(title="eToro ↔ yfinance", docs_url=None, redoc_url=None)
    templates = Jinja2Templates(directory=str(_HERE / "templates"))
    app.mount("/static", StaticFiles(directory=str(_HERE / "static")), name="static")

    # Cache-bust static assets by the newest stylesheet mtime (tailwind + app).
    try:
        css = (_HERE / "static" / "tailwind.css", _HERE / "static" / "app.css")
        asset_v = str(int(max(p.stat().st_mtime for p in css)))
    except OSError:
        asset_v = "0"
    templates.env.globals["asset_v"] = asset_v

    def page(request: Request, name: str, ctx: dict[str, Any]) -> HTMLResponse:
        return templates.TemplateResponse(request, name, {"active": ctx.pop("active", ""), **ctx})

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return page(request, "home.html", {"active": "home", "home": _home_summary()})

    # ── eToro universe → yfinance mapping (read-only; built offline) ──────────
    @app.get("/universe", response_class=HTMLResponse)
    def universe(request: Request, q: str = "", asset_type: str = "",
                 status: str = "", show_internal: bool = False,
                 min_adv: str = "", sector: str = "", view: str = "") -> HTMLResponse:
        snap = datamod.load_etoro_universe()
        all_rows = snap.get("rows", [])
        age = datamod.snapshot_age_seconds("etoro_universe_mapping.json", time.time())
        saved = universe_mod.list_saved()
        madv = _to_float(min_adv)
        ids = universe_mod.member_ids(view) if view in saved else None
        rows = _filter_universe(all_rows, q=q, asset_type=asset_type, status=status,
                                show_internal=show_internal, min_adv=madv, sector=sector,
                                universe_ids=ids)
        facets = _facet_counts(all_rows, q=q, asset_type=asset_type, status=status,
                               sector=sector, min_adv=madv, show_internal=show_internal,
                               view=view, saved=saved)
        counts = snap.get("counts", {})
        return page(request, "universe.html", {
            "active": "universe", "snap": snap, "age": age, "rows": rows[:_UNIVERSE_CAP],
            "q": q, "asset_type": asset_type, "status": status, "shown": len(rows),
            "show_internal": show_internal, "min_adv": min_adv, "sector": sector,
            "saved_universes": saved, "view": view, **facets,
            "validated": bool(counts.get("validated")),
            "eligible": bool(counts.get("eligibility_checked")),
            "liquid": bool(counts.get("liquidity_checked")),
            "has_sector": bool(counts.get("sector_known")),
        })

    @app.get("/universe/rows", response_class=HTMLResponse)
    def universe_rows(request: Request, q: str = "", asset_type: str = "",
                      status: str = "", show_internal: bool = False,
                      min_adv: str = "", sector: str = "", view: str = "") -> HTMLResponse:
        snap = datamod.load_etoro_universe()
        all_rows = snap.get("rows", [])
        saved = universe_mod.list_saved()
        madv = _to_float(min_adv)
        ids = universe_mod.member_ids(view) if view in saved else None
        rows = _filter_universe(all_rows, q=q, asset_type=asset_type, status=status,
                                show_internal=show_internal, min_adv=madv, sector=sector,
                                universe_ids=ids)
        facets = _facet_counts(all_rows, q=q, asset_type=asset_type, status=status,
                               sector=sector, min_adv=madv, show_internal=show_internal,
                               view=view, saved=saved)
        counts = snap.get("counts", {})
        return templates.TemplateResponse(request, "_universe_rows.html", {
            "rows": rows[:_UNIVERSE_CAP], "shown": len(rows), "oob": True,
            "asset_type": asset_type, "status": status, "sector": sector, "view": view,
            "saved_universes": saved, **facets,
            "validated": bool(counts.get("validated")),
            "eligible": bool(counts.get("eligibility_checked")),
            "liquid": bool(counts.get("liquidity_checked")),
            "has_sector": bool(counts.get("sector_known"))})

    @app.get("/universe/rules", response_class=HTMLResponse)
    def universe_rules(request: Request, t: str = "", name: str = "", sym: str = "") -> HTMLResponse:
        """Modal fragment: the full eToro trading rule set for one instrument id."""
        rules = datamod.load_instrument_rules(t) if t else None
        return templates.TemplateResponse(request, "_rules.html",
                                          {"rules": rules, "iid": t, "name": name, "sym": sym})

    @app.get("/universe/new", response_class=HTMLResponse)
    def universe_new(request: Request) -> HTMLResponse:
        """The create-universe criteria form (modal)."""
        return templates.TemplateResponse(request, "_universe_new.html", {})

    @app.get("/universe/create", response_class=HTMLResponse)
    def universe_create(request: Request, name: str = "backtest", min_adv: str = "1000000",
                        min_bars: str = "252", recent_days: str = "7",
                        max_spread: str = "", require_sector: str = "") -> HTMLResponse:
        """Build + persist a universe under the criteria, return a confirmation
        (count, per-condition verification, per-sector breakdown)."""
        doc = universe_mod.save(
            name,
            min_adv=_to_float(min_adv),
            min_bars=int(_to_float(min_bars)),
            recent_days=int(_to_float(recent_days)) or None,
            max_spread=(_to_float(max_spread) if max_spread.strip() else None),
            require_sector=(require_sector == "true"),
        )
        return templates.TemplateResponse(request, "_universe_created.html", {"doc": doc})

    @app.get("/universe/chart", response_class=HTMLResponse)
    def universe_chart(request: Request, t: str = "", name: str = "",
                       scale: str = "log") -> HTMLResponse:
        """Modal fragment: side-by-side price+volume charts for one yfinance
        ticker — native (left) and EUR-converted (right), read from the local
        Parquet stores. Log price by default (scale=linear switches both)."""
        from etoro_yfinance import currency, prices

        from . import charts

        log = scale != "linear"

        def panel(df):
            if df is None or len(df) == 0:
                return None, None, None, None
            svg = charts.price_volume_svg(df, log=log)
            span = (str(df.index[0]), str(df.index[-1]), len(df))
            close = (df["close"] if "close" in df.columns else df["adj_close"]).dropna()
            last = (charts.fmt_price(float(close.iloc[-1])), str(close.index[-1])) \
                if len(close) else (None, None)
            return svg, span, last[0], last[1]

        native = panel(prices.load_prices(t) if t else None)
        eur = panel(prices.load_prices(t, eur=True) if t else None)
        ccy = currency.currency_for(t, None) if t else None
        return templates.TemplateResponse(request, "_chart.html", {
            "ticker": t, "name": name, "log": log, "ccy": ccy or "native",
            "svg": native[0], "span": native[1], "last_price": native[2], "last_date": native[3],
            "svg_eur": eur[0], "last_eur": eur[2], "last_date_eur": eur[3],
        })

    # ── backtest (monthly momentum on a chosen universe) ─────────────────────
    @app.get("/backtest", response_class=HTMLResponse)
    def backtest_page(request: Request) -> HTMLResponse:
        from etoro_yfinance import momentum
        latest = max((r.get("price_to") or "" for r in
                      datamod.load_etoro_universe().get("rows", [])), default="")
        return page(request, "backtest.html", {
            "active": "backtest", "saved_universes": universe_mod.list_saved(),
            "strategy": momentum.strategy_signals(),
            "end_default": latest or str(date.today()), "start_default": "2018-01-01"})

    @app.get("/backtest/run", response_class=HTMLResponse)
    def backtest_run(request: Request, view: str = "", start: str = "2018-01-01",
                     end: str = "", top_n_sectors: str = "4",
                     top_n_per_sector: str = "6", min_sector_size: str = "0") -> HTMLResponse:
        """Kick off the backtest in a background thread; return a polling progress
        bar. Results are fetched by /backtest/progress once done."""
        from etoro_yfinance import backtest as bt

        rows = (universe_mod.load(view).get("instruments", [])
                if view in universe_mod.list_saved() else universe_mod.select())
        job_id = uuid.uuid4().hex[:12]
        with _BT_LOCK:
            _BT_JOBS[job_id] = {"pct": 0.0, "label": "starting…", "result": None,
                                "error": None, "view": view or "(default)"}

        def _progress(frac: float, label: str) -> None:
            with _BT_LOCK:
                if job_id in _BT_JOBS:
                    _BT_JOBS[job_id].update(pct=frac, label=label)

        def _worker() -> None:
            try:
                res = bt.run(rows, start=start, end=end or str(date.today()),
                             top_n_sectors=int(_to_float(top_n_sectors)) or 4,
                             top_n_per_sector=int(_to_float(top_n_per_sector)) or 6,
                             min_sector_size=int(_to_float(min_sector_size)),
                             progress=_progress)
                with _BT_LOCK:
                    _BT_JOBS[job_id].update(pct=1.0, result=res)
            except Exception as e:  # surface failures to the poller
                with _BT_LOCK:
                    _BT_JOBS[job_id].update(pct=1.0, error=str(e))

        threading.Thread(target=_worker, daemon=True).start()
        return templates.TemplateResponse(request, "_backtest_running.html",
                                          {"job_id": job_id, "pct": 0, "label": "starting…"})

    @app.get("/backtest/progress", response_class=HTMLResponse)
    def backtest_progress(request: Request, job: str = "") -> HTMLResponse:
        from . import charts

        with _BT_LOCK:
            j = dict(_BT_JOBS.get(job) or {})
        if not j:
            return templates.TemplateResponse(request, "_backtest_result.html",
                                              {"res": {"error": "job expired — re-run"},
                                               "svg": None, "view": ""})
        if j.get("result") is None and not j.get("error"):
            return templates.TemplateResponse(request, "_backtest_running.html",
                                              {"job_id": job, "pct": j["pct"], "label": j["label"]})
        # Done (or failed): render results and drop the job.
        with _BT_LOCK:
            _BT_JOBS.pop(job, None)
        res = j.get("result") or {"error": j.get("error")}
        svg = (charts.equity_svg(res["dates"], {"Strategy": res["equity"],
                                                "Benchmark": res["benchmark"]})
               if "error" not in res else None)
        return templates.TemplateResponse(request, "_backtest_result.html",
                                          {"res": res, "svg": svg, "view": j.get("view", "")})

    # ── diagnostics (system health) ──────────────────────────────────────────
    @app.get("/diagnostics", response_class=HTMLResponse)
    def diagnostics(request: Request) -> HTMLResponse:
        return page(request, "diagnostics.html", {"active": "diagnostics", "d": _diag()})

    @app.get("/api/diagnostics")
    def api_diagnostics() -> JSONResponse:
        return JSONResponse(_diag())

    @app.get("/healthz")
    def healthz() -> dict[str, bool]:
        return {"ok": True}

    return app


def _home_summary() -> dict[str, Any]:
    """Light rollup for the landing page — universe coverage + system health."""
    snap = datamod.load_etoro_universe()
    return {
        "universe": {
            "counts": snap.get("counts", {}),
            "generated_at": snap.get("generated_at"),
            "age": datamod.snapshot_age_seconds("etoro_universe_mapping.json", time.time()),
        },
        "diagnostics": {"overall": _diag().get("overall")},
    }


def _diag() -> dict[str, Any]:
    now = time.time()
    return diag.collect(now, snapshots={
        "etoro universe": datamod.snapshot_age_seconds("etoro_universe_mapping.json", now),
    })


# In-memory backtest jobs (single-process): id -> {pct, label, result, error, view}.
_BT_JOBS: dict[str, dict] = {}
_BT_LOCK = threading.Lock()


def _to_float(s: str) -> float:
    """Parse a query value to float; blank/invalid → 0.0 (empty form fields send '')."""
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def _filter_universe(
    rows: list[dict[str, Any]], *, q: str, asset_type: str, status: str,
    show_internal: bool = False, min_adv: float = 0.0, sector: str = "",
    universe_ids: set | None = None,
) -> list[dict[str, Any]]:
    ql = q.lower().strip()
    crypto_syms = {(r.get("symbol") or "").upper() for r in rows
                   if r.get("status") == "crypto"}
    out = []
    for r in rows:
        # Restrict to a saved universe's members (by execution instrument_id).
        if universe_ids is not None and r.get("instrument_id") not in universe_ids:
            continue
        # Dated futures and non-USD-quoted crypto duplicates (BTCEUR vs BTC) are
        # never part of the spot universe — excluded here too so a pre-filter
        # snapshot can't leak them into the view.
        if is_future(r.get("symbol"), r.get("exchange")):
            continue
        if r.get("status") == "crypto" and is_crypto_quote_dupe(r.get("symbol"), crypto_syms):
            continue
        # Liquidity floor: drop names below the requested median €/day turnover
        # (rows with unknown turnover are dropped when a floor is set).
        if min_adv > 0 and (r.get("adv_eur") or 0) < min_adv:
            continue
        # Hide eToro synthetic/dormant instruments by default, unless the user
        # opted in or is explicitly filtering to status=internal.
        if (not show_internal and status != "internal"
                and r.get("status") == "internal"):
            continue
        if asset_type and r.get("type") != asset_type:
            continue
        if status and r.get("status") != status:
            continue
        if sector and (r.get("sector") or "") != sector:
            continue
        if ql and ql not in (
            f"{r.get('symbol','')} {r.get('name','')} {r.get('yf','')}".lower()
        ):
            continue
        out.append(r)
    return out


def _facet_counts(rows, *, q, asset_type, status, sector, min_adv, show_internal,
                  view, saved):
    """Faceted option counts: each dropdown counts with every OTHER active filter
    applied (excluding its own selection), so the numbers show what picking each
    option would yield given the rest of the filters."""
    view_ids = universe_mod.member_ids(view) if view in saved else None

    def f(*, atype=asset_type, st=status, sc=sector, uids=view_ids):
        return _filter_universe(rows, q=q, asset_type=atype, status=st, sector=sc,
                                min_adv=min_adv, show_internal=show_internal,
                                universe_ids=uids)

    types = Counter(r.get("type") for r in f(atype="")
                    if r.get("status") != "internal").most_common()
    statuses = Counter(r.get("status") for r in f(st="")).most_common()
    sectors = Counter(r.get("sector") for r in f(sc="")
                      if r.get("sector") and r.get("status") != "internal").most_common()
    no_view = f(uids=None)                       # view facet ignores the view restriction
    mem = {u: universe_mod.member_ids(u) for u in saved}
    view_counts = [(u, sum(1 for r in no_view if r.get("instrument_id") in mem[u]))
                   for u in saved]
    return {"types": types, "statuses": statuses, "sectors": sectors,
            "all_count": len(no_view), "view_counts": view_counts}


app = create_app()


def main() -> int:
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="eToro↔yfinance read-only web UI")
    parser.add_argument("--host", default=os.environ.get("MOMENTUM_WEB_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MOMENTUM_WEB_PORT", "8800")))
    parser.add_argument(
        "--reload", action="store_true",
        default=os.environ.get("MOMENTUM_WEB_RELOAD", "").lower() in ("1", "true", "yes"),
        help="auto-restart on code changes (local dev only)",
    )
    args = parser.parse_args()

    reload_dirs = [str(_HERE.parent)] if args.reload else None
    uvicorn.run(
        "etoro_yfinance.web.server:app",
        host=args.host, port=args.port, log_level="info",
        reload=args.reload, reload_dirs=reload_dirs,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
