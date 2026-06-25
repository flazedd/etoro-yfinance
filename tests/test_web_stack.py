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


def test_universe_rows_join_and_stats(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    (tmp_path / "leonteq_universe.json").write_text(json.dumps({"members": [
        {"company_id": 1, "ticker": "AA", "exchange": "NYSE", "country": "United States",
         "currency": "USD", "isin": "US1", "company_name": "Alcoa"},
        {"company_id": 2, "ticker": "8031", "exchange": "TSE", "country": "Japan",
         "currency": "JPY", "isin": "JP1", "company_name": "Mitsui"},
    ]}))
    (tmp_path / "leonteq_mapping_verification.json").write_text(json.dumps({"results": {
        "1": {"ibkr_name": "ALCOA CORP", "ibkr_symbol": "AA", "ticker_match": True,
              "listing_match": True, "ibkr_listing": "AMEX", "conid": 111,
              "name_score": 1.0, "confidence": "high", "ccy_ok": True},
    }}))
    (tmp_path / "leonteq_liquidity.json").write_text(json.dumps({"results": {
        "1": {"adv_eur": 1234567.0}}}))
    (tmp_path / "leonteq_openfigi.json").write_text(json.dumps({"results": {
        "1": {"verdict": "triple_match"}}}))

    rows = webdata.load_universe_rows()
    assert len(rows) == 2
    alcoa = next(r for r in rows if r["cid"] == "1")
    assert alcoa["conf"] == "high"
    assert alcoa["tmatch"] is True
    assert alcoa["adv"] == 1234567.0
    assert alcoa["figi"] == "triple_match"
    mitsui = next(r for r in rows if r["cid"] == "2")
    assert mitsui["conf"] == "unresolved"  # no verification entry
    assert mitsui["gf"].endswith("/stock/TSE:8031/summary")

    stats = webdata.universe_stats(rows)
    assert stats == {"total": 2, "resolved": 1, "ticker_match": 1,
                     "with_adv": 1, "high": 1, "medium": 0, "low": 0}


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
            for path in ("/universe", "/execution", "/performance"):
                assert (await ac.get(path)).status_code == 200

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
