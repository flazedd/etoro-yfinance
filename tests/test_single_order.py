"""Tests for the manual single-stock test-buy: sizing, worker preview/place,
and the web routes (credential boundary + confirm gate)."""

from __future__ import annotations

import json
import types
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path
from typing import Any, ClassVar

import pytest

from ibkr_portfolio_connect import db as dbmod
from ibkr_portfolio_connect.ibkr_client import PlaceOrderReply
from ibkr_portfolio_connect.order_ticket import (
    is_fractional_eligible,
    parse_whatif,
    size_order,
)
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


# ── sizing ────────────────────────────────────────────────────────────────────


def test_sizing_fractional_vs_whole_vs_blocked() -> None:
    # US fractional: 5% of €51 at €40 → 0.06375 shares.
    frac = size_order(nav_eur=Decimal("51"), pct=Decimal("5"), price_eur=Decimal("40"), fractional=True)
    assert frac.ok
    assert frac.quantity == pytest.approx(0.06375)
    assert frac.est_cost_eur == Decimal("2.55")

    # Non-fractional pricey name → 0 whole shares → blocked (never over-buys).
    pricey = size_order(nav_eur=Decimal("51"), pct=Decimal("5"), price_eur=Decimal("355"), fractional=False)
    assert not pricey.ok
    assert "0 whole shares" in (pricey.blocked_reason or "")

    # Non-fractional cheap name → floor(2.55) = 2 shares.
    cheap = size_order(nav_eur=Decimal("51"), pct=Decimal("5"), price_eur=Decimal("1"), fractional=False)
    assert cheap.quantity == 2.0


def test_fractional_eligibility_by_listing() -> None:
    assert is_fractional_eligible("NYSE")
    assert not is_fractional_eligible("SEHK")
    assert not is_fractional_eligible(None)


def test_parse_whatif_extracts_and_survives_odd_shapes() -> None:
    wi = parse_whatif({"amount": {"amount": "2.55", "currency": "USD"},
                       "commission": {"amount": "1.00", "currency": "USD"},
                       "warn": "Fractional quantity"})
    assert wi.order_value == "2.55 USD"
    assert wi.commission == "1.00 USD"
    assert wi.warnings == ["Fractional quantity"]
    assert parse_whatif({}).order_value is None  # empty is fine


# ── fake IBKR client for worker tests ─────────────────────────────────────────


class _FakeIBKR:
    placed: ClassVar[list[dict[str, Any]]] = []

    def __init__(self, *a: Any, **k: Any) -> None: ...
    def __enter__(self) -> _FakeIBKR: return self
    def __exit__(self, *a: Any) -> None: ...

    def portfolio_summary(self, acct: str) -> dict[str, Any]:
        return {"netliquidation": {"amount": "51.00", "currency": "EUR"}}

    def what_if_market_order(self, acct: str, **kw: Any) -> dict[str, Any]:
        return {"amount": {"amount": "2.55", "currency": "USD"},
                "commission": {"amount": "1.00", "currency": "USD"}}

    def place_market_day_order(self, acct: str, **kw: Any) -> list[PlaceOrderReply]:
        _FakeIBKR.placed.append(kw)
        return [PlaceOrderReply(order_id="OID-1", order_status="Submitted")]


def _mk_ticket(**over: Any) -> int:
    fields: dict[str, Any] = {"conid": 760250490, "symbol": "SNDK", "name": "SanDisk",
                              "currency": "USD", "listing_exchange": "NYSE", "pct_of_nav": 5.0,
                              "price_eur_ref": 40.0, "fractional": True}
    fields.update(over)
    with dbmod.get_session() as s:
        t = dbmod.create_order_ticket(s, **fields)
        return int(t.id)


def _run_job(kind: str, ticket_id: int, settings: Any) -> None:
    with dbmod.get_session() as s:
        dbmod.request_job(s, kind=kind, payload=json.dumps({"ticket_id": ticket_id}))
        job = dbmod.claim_next_job(s)
        assert job is not None
        worker.process_job(s, job, settings)


def test_preview_sizes_and_previews(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    tid = _mk_ticket()
    _run_job(dbmod.JOB_KIND_ORDER_PREVIEW, tid, _settings())

    with dbmod.get_session() as s:
        t = dbmod.get_order_ticket(s, tid)
    assert t.status == dbmod.TICKET_PREVIEWED
    assert t.nav_eur == 51.0
    assert t.quantity == pytest.approx(0.06375)
    assert json.loads(t.preview_json)["commission"] == "1.00 USD"


def test_preview_blocks_non_fractional_pricey(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    tid = _mk_ticket(fractional=False, price_eur_ref=355.0, listing_exchange="SEHK", symbol="KIOXIA")
    _run_job(dbmod.JOB_KIND_ORDER_PREVIEW, tid, _settings())

    with dbmod.get_session() as s:
        t = dbmod.get_order_ticket(s, tid)
    assert t.status == dbmod.TICKET_BLOCKED
    assert "whole shares" in t.error


def test_preview_blocks_over_cap(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    tid = _mk_ticket(pct_of_nav=80.0)
    _run_job(dbmod.JOB_KIND_ORDER_PREVIEW, tid, _settings())
    with dbmod.get_session() as s:
        t = dbmod.get_order_ticket(s, tid)
    assert t.status == dbmod.TICKET_BLOCKED
    assert "cap" in t.error


def test_place_requires_confirmed_status(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    _FakeIBKR.placed = []
    tid = _mk_ticket()  # status = requested, NOT confirmed
    _run_job(dbmod.JOB_KIND_ORDER_PLACE, tid, _settings())
    with dbmod.get_session() as s:
        t = dbmod.get_order_ticket(s, tid)
    assert t.status == dbmod.TICKET_FAILED
    assert _FakeIBKR.placed == []  # never reached IBKR


def test_place_confirmed_ticket_submits(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    _FakeIBKR.placed = []
    tid = _mk_ticket(quantity=0.06375, status=dbmod.TICKET_CONFIRMED)
    _run_job(dbmod.JOB_KIND_ORDER_PLACE, tid, _settings())
    with dbmod.get_session() as s:
        t = dbmod.get_order_ticket(s, tid)
    assert t.status == dbmod.TICKET_PLACED
    assert t.order_id == "OID-1"
    assert len(_FakeIBKR.placed) == 1


def test_place_blocked_outside_rth(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    monkeypatch.setattr("ibkr_portfolio_connect.executor.is_rth", lambda now: False)
    _FakeIBKR.placed = []
    tid = _mk_ticket(quantity=0.06375, status=dbmod.TICKET_CONFIRMED)
    _run_job(dbmod.JOB_KIND_ORDER_PLACE, tid, _settings(trading_hours_only=True))
    with dbmod.get_session() as s:
        t = dbmod.get_order_ticket(s, tid)
    assert t.status == dbmod.TICKET_BLOCKED
    assert "trading hours" in t.error
    assert _FakeIBKR.placed == []


# ── web routes: credential boundary + confirm gate ────────────────────────────


def test_buy_and_confirm_routes_queue_jobs_only(tmp_db: Path, tmp_path: Path,
                                                 monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio

    import httpx

    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path / "empty"))
    from ibkr_portfolio_connect.web import server
    app = server.create_app()

    async def drive() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as ac:
            r = await ac.post("/strategies/buy", data={
                "conid": "760250490", "symbol": "SNDK", "name": "SanDisk",
                "currency": "USD", "listing_exchange": "NYSE", "strategy_id": "28",
                "price_eur": "40.0", "pct": "5"}, follow_redirects=False)
            assert r.status_code == 303
            assert r.headers["location"].startswith("/trade/")
            tid = int(r.headers["location"].split("/")[-1])

            # A preview job was queued; nothing placed (web holds no creds).
            with dbmod.get_session() as s:
                jobs = dbmod.list_jobs(s, limit=5)
                t = dbmod.get_order_ticket(s, tid)
            assert any(j.kind == dbmod.JOB_KIND_ORDER_PREVIEW for j in jobs)
            assert t.fractional is True
            assert t.pct_of_nav == 5.0

            assert (await ac.get(f"/trade/{tid}")).status_code == 200

            # Confirm is refused unless the ticket is PREVIEWED and phrase matches.
            await ac.post(f"/trade/{tid}/confirm", data={"confirm": "nope"}, follow_redirects=False)
            with dbmod.get_session() as s:
                assert not any(j.kind == dbmod.JOB_KIND_ORDER_PLACE for j in dbmod.list_jobs(s, limit=9))

            # Simulate the worker having previewed it, then confirm correctly.
            with dbmod.get_session() as s:
                t = dbmod.get_order_ticket(s, tid)
                t.status = dbmod.TICKET_PREVIEWED
                t.quantity = 0.06375
                dbmod.save_order_ticket(s, t)
            await ac.post(f"/trade/{tid}/confirm", data={"confirm": "EXECUTE"}, follow_redirects=False)
            with dbmod.get_session() as s:
                jobs = dbmod.list_jobs(s, limit=9)
                t = dbmod.get_order_ticket(s, tid)
            assert any(j.kind == dbmod.JOB_KIND_ORDER_PLACE for j in jobs)
            assert t.status == dbmod.TICKET_CONFIRMED

    asyncio.run(drive())
