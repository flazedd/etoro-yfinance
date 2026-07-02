"""Tests for the per-strategy position ledger (Option B: logical separation)."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from ibkr_portfolio_connect import db as dbmod


@pytest.fixture
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    p = tmp_path / "t.db"
    monkeypatch.setenv("MOMENTUM_DB_PATH", str(p))
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    dbmod._engine = None
    dbmod.init_db()
    yield p
    dbmod._engine = None


def _placed(sid: int, conid: int, symbol: str, qty: float, cost: float) -> None:
    with dbmod.get_session() as s:
        dbmod.create_order_ticket(s, status=dbmod.TICKET_PLACED, strategy_id=sid, conid=conid,
                                  symbol=symbol, name=symbol, quantity=qty, est_cost_eur=cost)


def _write_snapshots(tmp_path: Path) -> None:
    (tmp_path / "strategies_snapshot.json").write_text(json.dumps({"strategies": [
        {"strategy_id": 28, "name": "Offensief"}, {"strategy_id": 29, "name": "Neutraal"}]}))
    (tmp_path / "portfolio_snapshot.json").write_text(json.dumps({"n_positions": 3, "positions": [
        {"conid": 111, "symbol": "SNDK", "quantity": 0.3, "market_value": 15.0},   # €50/share
        {"conid": 222, "symbol": "AAPL", "quantity": 1.0, "market_value": 45.0},
        {"conid": 999, "symbol": "GHOST", "quantity": 5.0, "market_value": 100.0}]}))  # unattributed


def test_strategy_book_aggregates_values_and_reconciles(
    tmp_db: Path, tmp_path: Path
) -> None:
    from ibkr_portfolio_connect.web import server

    # Two strategies share conid 111 (SNDK); strat 28 also holds AAPL.
    _placed(28, 111, "SNDK", 0.1, 4.0)
    _placed(29, 111, "SNDK", 0.2, 8.0)
    _placed(28, 222, "AAPL", 1.0, 40.0)
    _write_snapshots(tmp_path)

    book = server._strategy_book()
    strat = {s["strategy_id"]: s for s in book["strategies"]}

    # Offensief: SNDK 0.1x€50 = €5 (cost €4 → +€1); AAPL €45 (cost €40 → +€5).
    off = strat[28]
    assert off["name"] == "Offensief"
    assert off["cost_eur"] == pytest.approx(44.0)
    assert off["value_eur"] == pytest.approx(50.0)
    assert off["pnl_eur"] == pytest.approx(6.0)
    sndk = next(p for p in off["positions"] if p["symbol"] == "SNDK")
    assert sndk["value_eur"] == pytest.approx(5.0)
    assert sndk["pnl_eur"] == pytest.approx(1.0)

    # Neutraal: SNDK 0.2x€50 = €10 (cost €8 → +€2).
    assert strat[29]["value_eur"] == pytest.approx(10.0)
    assert strat[29]["pnl_eur"] == pytest.approx(2.0)

    recon = {r["symbol"]: r for r in book["reconciliation"]}
    # 0.1 + 0.2 attributed = 0.3 = IBKR → matched.
    assert recon["SNDK"]["attributed"] == pytest.approx(0.3)
    assert recon["SNDK"]["flag"] == "matched"
    assert recon["AAPL"]["flag"] == "matched"
    # IBKR holds GHOST but no buy claims it → unattributed.
    assert recon["GHOST"]["flag"] == "unattributed"
    assert recon["GHOST"]["diff"] == pytest.approx(5.0)


def test_strategy_book_without_portfolio_shows_cost_only(tmp_db: Path, tmp_path: Path) -> None:
    from ibkr_portfolio_connect.web import server

    _placed(28, 111, "SNDK", 0.1, 4.0)
    # No portfolio snapshot written → value/pnl unknown, cost still shown.
    book = server._strategy_book()
    off = book["strategies"][0]
    assert off["cost_eur"] == pytest.approx(4.0)
    assert off["value_eur"] is None
    assert off["pnl_eur"] is None


def test_positions_page_renders(tmp_db: Path, tmp_path: Path,
                                monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio

    import httpx

    _placed(28, 111, "SNDK", 0.1, 4.0)
    _write_snapshots(tmp_path)
    from ibkr_portfolio_connect.web import server
    app = server.create_app()

    async def drive() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as ac:
            html = (await ac.get("/positions")).text
            assert "Offensief" in html
            assert "Reconciliation" in html
            assert 'href="/positions"' in (await ac.get("/")).text  # nav wired
            body: dict[str, Any] = (await ac.get("/api/positions")).json()
            assert body["n_placed"] == 1

    asyncio.run(drive())
