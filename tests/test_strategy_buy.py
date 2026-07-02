"""Tests for the whole-strategy buy (batch): sizing every holding, previewing
in one NAV read, sequential placement that survives a single failed order."""

from __future__ import annotations

import json
import types
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from typing import Any, ClassVar

import pytest

from ibkr_portfolio_connect import db as dbmod
from ibkr_portfolio_connect.ibkr_client import IBKRError, PlaceOrderReply
from ibkr_portfolio_connect.web import worker


@pytest.fixture
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    p = tmp_path / "t.db"
    monkeypatch.setenv("MOMENTUM_DB_PATH", str(p))
    dbmod._engine = None
    dbmod.init_db()
    yield p
    dbmod._engine = None


def _settings(**over: Any) -> Any:
    base: dict[str, Any] = {"ibkr_account_id": "U123", "sizing_currency": "EUR",
                            "http_timeout_seconds": 5.0, "max_trade_pct_of_nav": Decimal("50"),
                            "trading_hours_only": False}
    base.update(over)
    return types.SimpleNamespace(**base)


class _FakeIBKR:
    fail_conids: ClassVar[set[int]] = set()
    placed: ClassVar[list[int]] = []

    def __init__(self, *a: Any, **k: Any) -> None: ...
    def __enter__(self) -> _FakeIBKR: return self
    def __exit__(self, *a: Any) -> None: ...

    def portfolio_summary(self, acct: str) -> dict[str, Any]:
        return {"netliquidation": {"amount": "51.00", "currency": "EUR"}}

    def what_if_market_order(self, acct: str, **kw: Any) -> dict[str, Any]:
        return {"amount": {"amount": "2.00", "currency": "USD"},
                "commission": {"amount": "1.00", "currency": "USD"}}

    def place_market_day_order(self, acct: str, *, conid: int, **kw: Any) -> list[PlaceOrderReply]:
        if conid in _FakeIBKR.fail_conids:
            raise IBKRError(f"rejected {conid}")
        _FakeIBKR.placed.append(conid)
        return [PlaceOrderReply(order_id=f"OID-{conid}", order_status="Submitted")]


def _mk_batch(tickets: list[dict[str, Any]], total_pct: float = 50.0,
              ticket_status: str | None = None, batch_status: str | None = None) -> int:
    with dbmod.get_session() as s:
        b = dbmod.create_order_batch(s, strategy_id=28, strategy_name="Offensief",
                                     total_pct=total_pct,
                                     status=batch_status or dbmod.TICKET_REQUESTED)
        for t in tickets:
            fields = {"batch_id": b.id, "listing_exchange": "NYSE", "fractional": True,
                      "currency": "USD", **t}
            if ticket_status:
                fields["status"] = ticket_status
            dbmod.create_order_ticket(s, **fields)
        return int(b.id)


def _run_batch(kind: str, batch_id: int, settings: Any) -> None:
    with dbmod.get_session() as s:
        dbmod.request_job(s, kind=kind, payload=json.dumps({"batch_id": batch_id}))
        job = dbmod.claim_next_job(s)
        assert job is not None
        worker.process_job(s, job, settings)


def test_batch_preview_sizes_all_and_blocks_untradable(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    bid = _mk_batch([
        {"conid": 1, "symbol": "AAA", "weight": 0.05, "pct_of_nav": 2.5, "price_eur_ref": 40.0},
        # non-fractional pricey → 0 whole shares → blocked, but batch continues.
        {"conid": 2, "symbol": "BBB", "weight": 0.05, "pct_of_nav": 2.5, "price_eur_ref": 355.0,
         "fractional": False, "listing_exchange": "SEHK"},
        {"conid": 3, "symbol": "CCC", "weight": 0.04, "pct_of_nav": 2.0, "price_eur_ref": 10.0},
    ])
    _run_batch(dbmod.JOB_KIND_BATCH_PREVIEW, bid, _settings())

    with dbmod.get_session() as s:
        batch = dbmod.get_order_batch(s, bid)
        ts = {t.symbol: t for t in dbmod.tickets_for_batch(s, bid)}
    assert batch.status == dbmod.TICKET_PREVIEWED
    assert batch.nav_eur == 51.0
    assert ts["AAA"].status == dbmod.TICKET_PREVIEWED
    # target €1.275 quantizes to €1.28 → 1.28/40 = 0.032 shares.
    assert ts["AAA"].target_eur == pytest.approx(1.28)
    assert ts["AAA"].quantity == pytest.approx(0.032)
    assert ts["CCC"].status == dbmod.TICKET_PREVIEWED
    assert ts["BBB"].status == dbmod.TICKET_BLOCKED
    assert "whole shares" in ts["BBB"].error


def test_batch_place_is_sequential_and_survives_a_failure(
    tmp_db: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    _FakeIBKR.placed = []
    _FakeIBKR.fail_conids = {2}  # the middle order is rejected by IBKR
    bid = _mk_batch([
        {"conid": 1, "symbol": "AAA", "quantity": 0.05, "pct_of_nav": 2.5, "price_eur_ref": 40.0},
        {"conid": 2, "symbol": "BBB", "quantity": 0.05, "pct_of_nav": 2.5, "price_eur_ref": 40.0},
        {"conid": 3, "symbol": "CCC", "quantity": 0.20, "pct_of_nav": 2.0, "price_eur_ref": 10.0},
    ], ticket_status=dbmod.TICKET_CONFIRMED, batch_status=dbmod.TICKET_CONFIRMED)

    _run_batch(dbmod.JOB_KIND_BATCH_PLACE, bid, _settings())

    with dbmod.get_session() as s:
        batch = dbmod.get_order_batch(s, bid)
        ts = {t.symbol: t for t in dbmod.tickets_for_batch(s, bid)}
    # The failure on BBB did NOT stop AAA/CCC from placing.
    assert _FakeIBKR.placed == [1, 3]
    assert ts["AAA"].status == dbmod.TICKET_PLACED
    assert ts["AAA"].order_id == "OID-1"
    assert ts["BBB"].status == dbmod.TICKET_FAILED
    assert "rejected 2" in ts["BBB"].error
    assert ts["CCC"].status == dbmod.TICKET_PLACED
    assert batch.status == dbmod.TICKET_PLACED  # at least one placed


def test_batch_place_skips_blocked_children(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    _FakeIBKR.placed = []
    _FakeIBKR.fail_conids = set()
    with dbmod.get_session() as s:
        b = dbmod.create_order_batch(s, strategy_id=28, strategy_name="X",
                                     total_pct=50.0, status=dbmod.TICKET_CONFIRMED)
        dbmod.create_order_ticket(s, batch_id=b.id, conid=1, symbol="OK", quantity=0.1,
                                  status=dbmod.TICKET_CONFIRMED)
        dbmod.create_order_ticket(s, batch_id=b.id, conid=2, symbol="SKIP", quantity=None,
                                  status=dbmod.TICKET_BLOCKED, error="not fractional-tradable")
        bid = int(b.id)
    _run_batch(dbmod.JOB_KIND_BATCH_PLACE, bid, _settings())
    assert _FakeIBKR.placed == [1]  # only the confirmed one


def test_batch_place_refuses_unconfirmed_batch(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    _FakeIBKR.placed = []
    bid = _mk_batch([{"conid": 1, "symbol": "AAA", "quantity": 0.1}],
                    batch_status=dbmod.TICKET_PREVIEWED)  # NOT confirmed
    _run_batch(dbmod.JOB_KIND_BATCH_PLACE, bid, _settings())
    with dbmod.get_session() as s:
        batch = dbmod.get_order_batch(s, bid)
    assert batch.status == dbmod.TICKET_FAILED
    assert _FakeIBKR.placed == []


# ── web routes ────────────────────────────────────────────────────────────────


def test_buy_basket_route_builds_tickets_and_confirm_gate(
    tmp_db: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import asyncio

    import httpx

    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    (tmp_path / "mapping_snapshot.json").write_text(json.dumps({"rows": [
        {"company_id": 5470, "isin": "US80004C2008", "ticker": "SNDK", "conid": 111,
         "confidence": "high", "ibkr_symbol": "SNDK", "ibkr_listing": "NASDAQ", "tradable": True},
        {"company_id": 99, "isin": "JP1", "ticker": "285A", "conid": 222,
         "ibkr_symbol": "285A", "ibkr_listing": "TSEJ", "tradable": True}]}))
    (tmp_path / "strategies_snapshot.json").write_text(json.dumps({"count": 1, "strategies": [
        {"strategy_id": 28, "name": "Offensief", "enabled": True, "holdings": [
            {"company_id": 5470, "ticker": "SNDK", "company_name": "SanDisk", "currency": "USD",
             "target_weight": 0.05, "entry_price_eur": 40.0},
            {"company_id": 99, "ticker": "285A", "company_name": "Kioxia", "currency": "JPY",
             "target_weight": 0.05, "entry_price_eur": 355.0},
            {"company_id": -1, "ticker": "CASH", "company_name": "Cash", "target_weight": 0.9}]}]}))

    from ibkr_portfolio_connect.web import server
    app = server.create_app()

    async def drive() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as ac:
            r = await ac.post("/strategies/buy-basket",
                              data={"strategy_id": "28", "total_pct": "50"}, follow_redirects=False)
            assert r.status_code == 303
            bid = int(r.headers["location"].split("/")[-1])

            with dbmod.get_session() as s:
                tickets = dbmod.tickets_for_batch(s, bid)
                jobs = dbmod.list_jobs(s, limit=5)
            # Two tradable holdings → two tickets (CASH has no conid, skipped).
            assert len(tickets) == 2
            aaa = next(t for t in tickets if t.symbol == "SNDK")
            assert aaa.pct_of_nav == pytest.approx(2.5)   # 50pct x 0.05 weight
            assert aaa.fractional is True                 # NASDAQ
            assert any(j.kind == dbmod.JOB_KIND_BATCH_PREVIEW for j in jobs)

            assert (await ac.get(f"/basket/{bid}")).status_code == 200

            # Confirm is refused unless the batch is PREVIEWED + phrase matches.
            await ac.post(f"/basket/{bid}/confirm", data={"confirm": "no"}, follow_redirects=False)
            with dbmod.get_session() as s:
                assert not any(j.kind == dbmod.JOB_KIND_BATCH_PLACE for j in dbmod.list_jobs(s, limit=9))

            with dbmod.get_session() as s:
                batch = dbmod.get_order_batch(s, bid)
                batch.status = dbmod.TICKET_PREVIEWED
                dbmod.save_order_batch(s, batch)
                for t in dbmod.tickets_for_batch(s, bid):
                    t.status = dbmod.TICKET_PREVIEWED
                    dbmod.save_order_ticket(s, t)
            await ac.post(f"/basket/{bid}/confirm", data={"confirm": "EXECUTE"}, follow_redirects=False)
            with dbmod.get_session() as s:
                jobs = dbmod.list_jobs(s, limit=9)
                batch = dbmod.get_order_batch(s, bid)
            assert any(j.kind == dbmod.JOB_KIND_BATCH_PLACE for j in jobs)
            assert batch.status == dbmod.TICKET_CONFIRMED

    asyncio.run(drive())
