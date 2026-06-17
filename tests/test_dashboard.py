"""Tests for the read-only dashboard renderer + server."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ibkr_portfolio_connect import dashboard
from ibkr_portfolio_connect.dashboard_server import DashboardConfig, create_app

# starlette's TestClient still imports `httpx` (not `httpx2`) and emits a
# deprecation warning; the repo promotes warnings to errors, so scope an ignore
# to the tests that actually drive the ASGI app over HTTP.
_testclient = pytest.mark.filterwarnings(
    "ignore::starlette.exceptions.StarletteDeprecationWarning"
)


def _write(d: Path, name: str, rec: dict) -> None:
    (d / name).write_text(json.dumps(rec))


def test_load_records_sorts_newest_first_and_tolerates_junk(tmp_path: Path) -> None:
    _write(tmp_path, "20260601-100000.json", {"started_at": "2026-06-01T10:00:00", "status": "success"})
    _write(tmp_path, "20260701-100000.json", {"started_at": "2026-07-01T10:00:00", "status": "failed"})
    (tmp_path / "broken.json").write_text("{not json")
    (tmp_path / "notarun.txt").write_text("ignored")

    recs = dashboard.load_records(tmp_path)
    assert [r["status"] for r in recs] == ["failed", "success"]  # newest first
    assert recs[0]["id"] == "20260701-100000"  # id defaulted from filename


def test_load_records_missing_dir_returns_empty(tmp_path: Path) -> None:
    assert dashboard.load_records(tmp_path / "nope") == []
    assert dashboard.load_records(None) == []


def test_tail_log_returns_last_n_lines(tmp_path: Path) -> None:
    p = tmp_path / "rebalance.log"
    p.write_text("".join(f"line {i}\n" for i in range(100)))
    tail = dashboard.tail_log(p, 5)
    assert tail == ["line 95\n", "line 96\n", "line 97\n", "line 98\n", "line 99\n"]
    assert dashboard.tail_log(tmp_path / "missing.log", 5) == []


def test_render_html_is_self_contained_and_embeds_data(tmp_path: Path) -> None:
    recs = [{"id": "r1", "started_at": "2026-07-01T10:00:00", "status": "success", "nav": "1000"}]
    html = dashboard.render_html(recs, log_tail=["hello\n"], live=False)
    assert "<title>" in html
    assert "/*__DATA__*/" not in html  # placeholder replaced
    assert '"status": "success"' in html or '"status":"success"' in html
    assert "hello" in html


@_testclient
def test_server_endpoints(tmp_path: Path) -> None:
    from fastapi.testclient import TestClient

    _write(tmp_path, "20260701-143000.json",
           {"started_at": "2026-07-01T14:30:00", "status": "success", "nav": "12345"})
    log = tmp_path / "rebalance.log"
    log.write_text("log line one\nlog line two\n")

    cfg = DashboardConfig(report_dir=tmp_path, log_dir=tmp_path)
    client = TestClient(create_app(cfg))

    assert client.get("/healthz").json() == {"ok": True}

    idx = client.get("/")
    assert idx.status_code == 200
    assert "ibkr-rebalance dashboard" in idx.text

    runs = client.get("/api/runs").json()
    assert len(runs) == 1
    assert runs[0]["id"] == "20260701-143000"

    assert client.get("/api/runs/20260701-143000").status_code == 200
    assert client.get("/api/runs/does-not-exist").status_code == 404

    logs = client.get("/api/logs?n=1").json()
    assert logs["lines"] == ["log line two\n"]


@_testclient
def test_server_handles_no_data_dirs() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(create_app(DashboardConfig(report_dir=None, log_dir=None)))
    assert client.get("/").status_code == 200
    assert client.get("/api/runs").json() == []
    assert client.get("/api/logs").json() == {"lines": []}
