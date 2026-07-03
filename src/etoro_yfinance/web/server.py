"""FastAPI app — read-only views over the eToro→yfinance universe. No credentials.

The app reads a single offline-built artifact (data/etoro_universe_mapping.json)
and system diagnostics. It never calls eToro or any broker — trading lives in the
CLI (scripts/etoro_trade.py). Pages: Home, eToro↔yfinance universe, Diagnostics.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..yfinance_map import is_crypto_quote_dupe, is_future
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
                 min_adv: str = "", sector: str = "") -> HTMLResponse:
        snap = datamod.load_etoro_universe()
        age = datamod.snapshot_age_seconds("etoro_universe_mapping.json", time.time())
        rows = _filter_universe(snap.get("rows", []), q=q, asset_type=asset_type,
                                status=status, show_internal=show_internal,
                                min_adv=_to_float(min_adv), sector=sector)
        counts = snap.get("counts", {})
        return page(request, "universe.html", {
            "active": "universe", "snap": snap, "age": age, "rows": rows[:_UNIVERSE_CAP],
            "q": q, "asset_type": asset_type, "status": status, "shown": len(rows),
            "show_internal": show_internal, "min_adv": min_adv, "sector": sector,
            "validated": bool(counts.get("validated")),
            "eligible": bool(counts.get("eligibility_checked")),
            "liquid": bool(counts.get("liquidity_checked")),
            "has_sector": bool(counts.get("sector_known")),
        })

    @app.get("/universe/rows", response_class=HTMLResponse)
    def universe_rows(request: Request, q: str = "", asset_type: str = "",
                      status: str = "", show_internal: bool = False,
                      min_adv: str = "", sector: str = "") -> HTMLResponse:
        snap = datamod.load_etoro_universe()
        rows = _filter_universe(snap.get("rows", []), q=q, asset_type=asset_type,
                                status=status, show_internal=show_internal,
                                min_adv=_to_float(min_adv), sector=sector)
        counts = snap.get("counts", {})
        return templates.TemplateResponse(request, "_universe_rows.html",
                                          {"rows": rows[:_UNIVERSE_CAP], "shown": len(rows),
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

    @app.get("/universe/chart", response_class=HTMLResponse)
    def universe_chart(request: Request, t: str = "", name: str = "",
                       scale: str = "log") -> HTMLResponse:
        """Modal fragment: side-by-side price+volume charts for one yfinance
        ticker — native (left) and EUR-converted (right), read from the local
        Parquet stores. Log price by default (scale=linear switches both)."""
        from .. import currency, prices
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


def _to_float(s: str) -> float:
    """Parse a query value to float; blank/invalid → 0.0 (empty form fields send '')."""
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def _filter_universe(
    rows: list[dict[str, Any]], *, q: str, asset_type: str, status: str,
    show_internal: bool = False, min_adv: float = 0.0, sector: str = "",
) -> list[dict[str, Any]]:
    sl = sector.lower().strip()
    ql = q.lower().strip()
    crypto_syms = {(r.get("symbol") or "").upper() for r in rows
                   if r.get("status") == "crypto"}
    out = []
    for r in rows:
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
        if sl and sl not in (r.get("sector") or "").lower():
            continue
        if ql and ql not in (
            f"{r.get('symbol','')} {r.get('name','')} {r.get('yf','')}".lower()
        ):
            continue
        out.append(r)
    return out


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
