"""FastAPI app — read-only views + a gated job-request endpoint. No credentials.

The app reads the universe artifacts, the performance snapshot, and the SQLite
run/job tables. The single state-changing endpoint, POST /execution/request,
only inserts a `job` row; the worker (separate process, holds creds) is what
actually trades. A LIVE request additionally requires the user to type a
confirmation phrase, so a stray click can't fire real orders.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ibkr_portfolio_connect.db import (
    get_run,
    get_session,
    init_db,
    list_jobs,
    list_runs,
    orders_for_run,
    recent_events,
    request_job,
)

from . import data as datamod

_HERE = Path(__file__).parent
CONFIRM_PHRASE = "EXECUTE"


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(title="Momentum stack", docs_url=None, redoc_url=None)
    templates = Jinja2Templates(directory=str(_HERE / "templates"))
    app.mount("/static", StaticFiles(directory=str(_HERE / "static")), name="static")

    def page(request: Request, name: str, ctx: dict[str, Any]) -> HTMLResponse:
        return templates.TemplateResponse(request, name, {"active": ctx.pop("active", ""), **ctx})

    # ── universe ─────────────────────────────────────────────────────────────
    @app.get("/", response_class=HTMLResponse)
    def index() -> RedirectResponse:
        return RedirectResponse("/universe")

    @app.get("/universe", response_class=HTMLResponse)
    def universe(request: Request, q: str = "", conf: str = "", only_issues: bool = False) -> HTMLResponse:
        rows = datamod.load_universe_rows()
        stats = datamod.universe_stats(rows)
        rows = _filter_rows(rows, q=q, conf=conf, only_issues=only_issues)
        return page(request, "universe.html", {
            "active": "universe", "rows": rows[:2000], "stats": stats,
            "q": q, "conf": conf, "only_issues": only_issues, "shown": len(rows),
        })

    @app.get("/universe/rows", response_class=HTMLResponse)
    def universe_rows(request: Request, q: str = "", conf: str = "", only_issues: bool = False) -> HTMLResponse:
        rows = _filter_rows(datamod.load_universe_rows(), q=q, conf=conf, only_issues=only_issues)
        return templates.TemplateResponse(request, "_universe_rows.html",
                                          {"rows": rows[:2000], "shown": len(rows)})

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

    # ── api / health ─────────────────────────────────────────────────────────
    @app.get("/api/performance")
    def api_performance() -> JSONResponse:
        return JSONResponse(datamod.load_performance())

    @app.get("/healthz")
    def healthz() -> dict[str, bool]:
        return {"ok": True}

    return app


def _filter_rows(rows: list[dict[str, Any]], *, q: str, conf: str, only_issues: bool) -> list[dict[str, Any]]:
    ql = q.lower().strip()
    out = []
    for r in rows:
        if conf and r.get("conf") != conf:
            continue
        if only_issues and r.get("conf") in ("high",) and r.get("tmatch"):
            continue
        if ql and ql not in (
            f"{r.get('bb_name','')} {r.get('ibkr_name','')} {r.get('ticker','')} {r.get('isin','')}".lower()
        ):
            continue
        out.append(r)
    return out


app = create_app()


def main() -> int:
    import uvicorn

    host = os.environ.get("MOMENTUM_WEB_HOST", "127.0.0.1")
    port = int(os.environ.get("MOMENTUM_WEB_PORT", "8800"))
    uvicorn.run("ibkr_portfolio_connect.web.server:app", host=host, port=port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
