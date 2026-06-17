"""Read-only LAN dashboard for the rebalancer — a SEPARATE long-lived process.

Security stance (the whole reason this is its own module/process):
  * It imports NO broker client and holds NO OAuth credentials.
  * It only reads the run-record JSONs in REPORT_DIR and the rotating log file.
  * It exposes only GETs. There is no endpoint that can place or cancel an order.
Bind it to your LAN and never expose it to the public internet.

It deliberately does NOT load the trading `Settings` (which requires an account
id); it reads just the handful of paths it needs, so it can run with nothing but
REPORT_DIR / LOG_DIR set.

    uv run --extra dashboard ibkr-dashboard
    # or: uv run --extra dashboard python -m ibkr_portfolio_connect.dashboard_server
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DashboardConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )
    report_dir: Path | None = None
    log_dir: Path | None = None
    log_filename: str = "rebalance.log"
    log_tail_lines: int = Field(default=300, ge=1, le=5000)
    dashboard_host: str = "0.0.0.0"
    dashboard_port: int = 8080

    @property
    def log_path(self) -> Path | None:
        return (self.log_dir / self.log_filename) if self.log_dir else None


def create_app(config: DashboardConfig | None = None) -> Any:
    """Build the FastAPI app. Factory form so tests can inject a config and
    drive it with starlette's TestClient."""
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse

    from . import dashboard

    cfg = config or DashboardConfig()
    app = FastAPI(title="ibkr-rebalance dashboard", docs_url=None, redoc_url=None)

    @app.get("/", response_class=HTMLResponse)
    def index() -> Any:
        records = dashboard.load_records(cfg.report_dir)
        tail = dashboard.tail_log(cfg.log_path, cfg.log_tail_lines)
        return HTMLResponse(dashboard.render_html(records, log_tail=tail, live=True))

    @app.get("/api/runs")
    def api_runs() -> Any:
        return JSONResponse(dashboard.load_records(cfg.report_dir))

    @app.get("/api/runs/{run_id}")
    def api_run(run_id: str) -> Any:
        for rec in dashboard.load_records(cfg.report_dir):
            if rec.get("id") == run_id:
                return JSONResponse(rec)
        raise HTTPException(status_code=404, detail="run not found")

    @app.get("/api/logs")
    def api_logs(n: int = cfg.log_tail_lines) -> Any:
        n = max(1, min(n, 5000))
        return JSONResponse({"lines": dashboard.tail_log(cfg.log_path, n)})

    @app.get("/healthz")
    def healthz() -> Any:
        return JSONResponse({"ok": True})

    return app


def main() -> None:
    import uvicorn

    cfg = DashboardConfig()
    uvicorn.run(create_app(cfg), host=cfg.dashboard_host, port=cfg.dashboard_port)


if __name__ == "__main__":
    main()
