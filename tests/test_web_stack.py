"""Tests for the web/worker/publisher stack (DB queue, loaders, gating)."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path

import pytest

from ibkr_portfolio_connect import db as dbmod
from ibkr_portfolio_connect import publisher
from ibkr_portfolio_connect.cost import RebalanceReport
from ibkr_portfolio_connect.web import data as webdata
from ibkr_portfolio_connect.web import worker


@pytest.fixture
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    p = tmp_path / "t.db"
    monkeypatch.setenv("MOMENTUM_DB_PATH", str(p))
    dbmod._engine = None
    dbmod.init_db()
    yield p
    dbmod._engine = None


# ── job queue ─────────────────────────────────────────────────────────────────


def test_job_queue_roundtrip(tmp_db: Path) -> None:
    with dbmod.get_session() as s:
        job = dbmod.request_job(s, dry_run=True, note="preview")
        assert job.id is not None
        assert job.status == dbmod.JOB_REQUESTED

    with dbmod.get_session() as s:
        claimed = dbmod.claim_next_job(s)
        assert claimed is not None
        assert claimed.status == dbmod.JOB_CLAIMED
        # nothing left to claim
        assert dbmod.claim_next_job(s) is None


# ── universe loaders ──────────────────────────────────────────────────────────


def test_gurufocus_url_rule() -> None:
    assert webdata.gurufocus_url("United States", "NYSE", "AA") == \
        "https://www.gurufocus.com/stock/AA/summary"
    assert webdata.gurufocus_url("Japan", "TSE", "8031") == \
        "https://www.gurufocus.com/stock/TSE:8031/summary"
    assert webdata.gurufocus_url("Spain", "XMAD", "") == ""


def test_load_mapping_reads_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    assert webdata.load_mapping() == {}  # no snapshot yet -> empty (page shows a hint)
    (tmp_path / "mapping_snapshot.json").write_text(json.dumps({
        "generated_at": "2026-07-01T05:30:00+00:00", "universe_id": 15, "label": "LEONTEQ",
        "counts": {"total": 2, "equities": 1, "etfs": 1, "tradable": 2,
                   "unresolved": 0, "retryable": 0},
        "rows": [
            {"kind": "equity", "name": "Alcoa", "ticker": "AA", "conid": 111, "tradable": True},
            {"kind": "etf", "name": "Invesco Momentum", "ticker": "SPMO", "conid": 222, "tradable": True},
        ],
    }))
    snap = webdata.load_mapping()
    assert snap["counts"]["total"] == 2
    assert {r["kind"] for r in snap["rows"]} == {"equity", "etf"}


# ── worker status mapping ─────────────────────────────────────────────────────


def test_run_status_mapping() -> None:
    nav = Decimal("100000")
    assert worker._run_status(RebalanceReport(nav=nav, trades=[], dry_run=True)) == dbmod.RUN_DRY_RUN
    assert worker._run_status(
        RebalanceReport(nav=nav, trades=[], aborted_reason="stale")) == dbmod.RUN_ABORTED
    # no trades, live -> success (already aligned)
    assert worker._run_status(RebalanceReport(nav=nav, trades=[], dry_run=False)) == dbmod.RUN_SUCCESS


def test_float_coercion() -> None:
    assert worker._f(None) is None
    assert worker._f(Decimal("1.5")) == 1.5
    assert worker._f("oops") is None


# ── publisher ─────────────────────────────────────────────────────────────────


class _FakeBB:
    def schedules(self, enabled_only: bool = True) -> list[dict[str, object]]:
        return [{"strategy_id": 13, "name": "MomentumTopSelectie"}]

    def schedule(self, sid: int) -> dict[str, object]:
        return {"name": "MomentumTopSelectie", "as_of_date": "2026-06-12",
                "next_rebalance_at": "2026-07-06T02:00:00+00:00",
                "holdings": [{"ticker": "SNDK", "company_name": "SanDisk"}]}

    def performance(self, sid: int) -> dict[str, object]:
        return {"inception_date": "2026-05-01", "mtd_return_pct": 1.23,
                "since_inception_return_pct": 4.56, "daily_returns": []}


def test_build_snapshot_and_write_local(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    snap = publisher.build_snapshot(_FakeBB())  # type: ignore[arg-type]
    assert snap["strategy_id"] == 13
    assert snap["mtd_return_pct"] == 1.23
    assert len(snap["holdings"]) == 1
    out = publisher.write_local(snap)
    assert out.exists()
    assert json.loads(out.read_text())["name"] == "MomentumTopSelectie"


def test_publish_to_repo_commits_then_noop(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "site"
    repo.mkdir()
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(repo), *args], check=True)
    monkeypatch.setenv("MOMENTUM_SITE_DATA_PATH", "data/perf.json")
    snap = {"name": "S", "mtd_return_pct": 1.0, "as_of_date": "2026-06-12"}

    info1 = publisher.publish_to_repo(snap, repo, push=False)
    assert info1["committed"] == "true"
    assert (repo / "data" / "perf.json").exists()

    info2 = publisher.publish_to_repo(snap, repo, push=False)  # identical -> no commit
    assert info2["committed"] == "false"


# ── web endpoints + live-trade gate ───────────────────────────────────────────


def test_web_endpoints_and_live_gate(tmp_db: Path, tmp_path: Path,
                                     monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio

    import httpx

    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path / "empty"))
    from ibkr_portfolio_connect.web import server
    app = server.create_app()

    async def drive() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as ac:
            assert (await ac.get("/healthz")).json() == {"ok": True}
            for path in ("/", "/mapping", "/execution", "/performance"):
                assert (await ac.get(path)).status_code == 200

            # The home page links to every section and carries the nav bar.
            home = (await ac.get("/")).text
            for href in ('href="/mapping"', 'href="/portfolio"', 'href="/execution"',
                         'href="/performance"', 'href="/diagnostics"'):
                assert href in home

            # LIVE without the confirmation phrase must NOT queue anything.
            await ac.post("/execution/request", data={"mode": "live", "confirm": "nope"})
            with dbmod.get_session() as s:
                assert dbmod.list_jobs(s) == []

            # A dry-run request, then a LIVE request WITH the phrase, both queue.
            await ac.post("/execution/request", data={"mode": "dry"})
            await ac.post("/execution/request",
                          data={"mode": "live", "confirm": server.CONFIRM_PHRASE})
            with dbmod.get_session() as s:
                jobs = dbmod.list_jobs(s)
                assert len(jobs) == 2
                assert {j.dry_run for j in jobs} == {True, False}

    asyncio.run(drive())


# ── portfolio snapshot + diagnostics ──────────────────────────────────────────


class _FakePos:
    def __init__(self, conid: int, sym: str, qty: str, mv: str, ccy: str, px: str) -> None:
        self.conid, self.symbol, self.asset_class = conid, sym, "STK"
        self.quantity, self.market_value = Decimal(qty), Decimal(mv)
        self.currency, self.mkt_price = ccy, Decimal(px)


class _FakeIBKR:
    def portfolio_summary(self, account_id: str) -> dict:
        return {"netliquidation": {"amount": 100000, "currency": "EUR"},
                "totalcashvalue": {"amount": 5000, "currency": "EUR"}}

    def positions(self, account_id: str) -> list:
        # Returned out of value order to prove the snapshot sorts by |market value|.
        return [_FakePos(2, "SAP", "-5", "-500", "EUR", "100"),
                _FakePos(1, "AAPL", "10", "2500", "USD", "250")]


def test_portfolio_snapshot_builder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from ibkr_portfolio_connect import portfolio_snapshot as ps

    snap = ps.build_snapshot(_FakeIBKR(), "U123", base_currency="EUR")
    assert snap["nav"] == {"amount": 100000.0, "currency": "EUR"}
    assert snap["n_positions"] == 2
    # Sorted by absolute market value, weight computed off NAV.
    assert [p["symbol"] for p in snap["positions"]] == ["AAPL", "SAP"]
    assert snap["positions"][0]["weight_pct"] == pytest.approx(2.5)

    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    out = ps.write_local(snap, tmp_path)
    assert out.exists()
    assert webdata.load_portfolio()["account_id"] == "U123"


def test_diagnostics_collect_and_status() -> None:
    from ibkr_portfolio_connect.web import diagnostics as diag

    # Pure threshold logic.
    assert diag._pct_status(50, 80, 92) == diag.OK
    assert diag._pct_status(85, 80, 92) == diag.WARN
    assert diag._pct_status(95, 80, 92) == diag.CRIT
    assert diag.overall([{"status": diag.OK}, {"status": diag.CRIT}, {"status": diag.WARN}]) == diag.CRIT

    d = diag.collect(1_000_000.0, db_path=None,
                     snapshots={"portfolio": 120.0, "performance": None})
    assert d["overall"] in (diag.OK, diag.WARN, diag.CRIT)
    assert d["disk"]["available"] is True  # shutil.disk_usage works everywhere
    assert d["snapshots"]["portfolio"] == 120.0


def test_portfolio_and_diagnostics_pages_render(tmp_db: Path, tmp_path: Path,
                                                monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio

    import httpx

    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path / "empty"))
    from ibkr_portfolio_connect.web import server
    app = server.create_app()

    async def drive() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as ac:
            # Both pages render even with no snapshot present (hint shown).
            for path in ("/portfolio", "/diagnostics", "/api/portfolio", "/api/diagnostics"):
                assert (await ac.get(path)).status_code == 200
            assert "System diagnostics" in (await ac.get("/diagnostics")).text

    asyncio.run(drive())


def test_strategies_page_renders_and_merges_ibkr(tmp_db: Path, tmp_path: Path,
                                                 monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio

    import httpx

    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    (tmp_path / "mapping_snapshot.json").write_text(json.dumps({"rows": [
        {"company_id": 5470, "isin": "US80004C2008", "ticker": "SNDK",
         "conid": 760250490, "confidence": "high", "ibkr_symbol": "SNDK",
         "ibkr_quote_url": "http://ib/760250490", "tradable": True}]}))
    (tmp_path / "strategies_snapshot.json").write_text(json.dumps({
        "generated_at": "2026-07-02T19:00:00+00:00", "count": 1, "strategies": [
            {"strategy_id": 28, "name": "Offensief", "enabled": True, "frequency": "monthly",
             "next_rebalance_at": "2026-07-04T02:00:00+00:00", "mtd_return_pct": 0.33,
             "holdings": [{"company_id": 5470, "ticker": "SNDK", "isin": "US80004C2008",
                           "company_name": "SanDisk Corp", "target_weight": 0.0417,
                           "side": "long", "score": 54.94}]}]}))

    from ibkr_portfolio_connect.web import server
    app = server.create_app()

    async def drive() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as ac:
            html = (await ac.get("/strategies")).text
            assert "Offensief" in html
            assert "SanDisk Corp" in html
            assert "760250490" in html            # conid merged from mapping
            assert 'href="/strategies"' in (await ac.get("/")).text  # nav wired

            # Refresh queues a strategies job (not a rebalance).
            await ac.post("/strategies/refresh")
    asyncio.run(drive())

    with dbmod.get_session() as s:
        jobs = dbmod.list_jobs(s, limit=5)
    assert any(j.kind == dbmod.JOB_KIND_STRATEGIES for j in jobs)


# ── web-triggered refresh jobs (mapping / portfolio) ──────────────────────────


def test_refresh_job_runs_via_worker(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import types

    from ibkr_portfolio_connect.web import worker

    with dbmod.get_session() as s:
        dbmod.request_job(s, kind=dbmod.JOB_KIND_MAPPING, note="refresh mapping")

    seen: dict[str, str] = {}
    monkeypatch.setattr(worker, "_run_refresh",
                        lambda kind, settings: seen.setdefault("kind", kind) or "1479 tradable, 0 unresolved")

    with dbmod.get_session() as s:
        job = dbmod.claim_next_job(s)
        assert job is not None
        assert job.kind == dbmod.JOB_KIND_MAPPING
        worker.process_job(s, job, types.SimpleNamespace())  # type: ignore[arg-type]
        assert job.status == dbmod.JOB_DONE
        assert job.finished_at is not None

    assert seen["kind"] == dbmod.JOB_KIND_MAPPING
    with dbmod.get_session() as s:
        titles = [e.title for e in dbmod.recent_events(s, limit=10)]
    assert any("mapping refresh finished" in t for t in titles)


def test_refresh_job_error_is_recorded_not_raised(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import types

    from ibkr_portfolio_connect.web import worker

    with dbmod.get_session() as s:
        dbmod.request_job(s, kind=dbmod.JOB_KIND_PORTFOLIO)

    def boom(kind: str, settings: object) -> str:
        raise RuntimeError("IBKR unreachable")

    monkeypatch.setattr(worker, "_run_refresh", boom)
    with dbmod.get_session() as s:
        job = dbmod.claim_next_job(s)
        worker.process_job(s, job, types.SimpleNamespace())  # type: ignore[arg-type]
        assert job.status == dbmod.JOB_ERROR
        assert "IBKR unreachable" in job.error


def test_mapping_refresh_button_enqueues_and_shows_pending(
    tmp_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import asyncio

    import httpx

    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path / "empty"))
    from ibkr_portfolio_connect.web import server
    app = server.create_app()

    async def drive() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as ac:
            r = await ac.post("/mapping/refresh")
            assert r.status_code in (303, 200)  # redirect to /mapping?queued=1
            with dbmod.get_session() as s:
                jobs = dbmod.list_jobs(s)
            assert len(jobs) == 1
            assert jobs[0].kind == dbmod.JOB_KIND_MAPPING
            # the page now shows the disabled "Refreshing…" button
            page = (await ac.get("/mapping")).text
            assert "Refreshing…" in page
            assert "Refresh queued" in page

    asyncio.run(drive())
