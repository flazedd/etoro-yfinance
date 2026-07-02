"""Slippage: fill price captured after placing, compared to the bbterminal
reference (entry) price — per transaction and summed per whole-strategy buy."""

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
                            "trading_hours_only": False, "order_settle_timeout_seconds": 5.0,
                            "order_poll_interval_seconds": 0.0}
    base.update(over)
    return types.SimpleNamespace(**base)


class _FakeIBKR:
    """Fills every conid at a price 2.5% above its reference (40 → 41)."""
    fills: ClassVar[dict[int, str]] = {}

    def __init__(self, *a: Any, **k: Any) -> None: ...
    def __enter__(self) -> _FakeIBKR: return self
    def __exit__(self, *a: Any) -> None: ...
    def init_brokerage_session(self) -> None: ...

    def place_market_day_order(self, acct: str, *, conid: int, **kw: Any) -> list[PlaceOrderReply]:
        return [PlaceOrderReply(order_id=f"OID-{conid}", order_status="Submitted")]

    def order_status(self, order_id: str) -> dict[str, Any]:
        conid = int(order_id.split("-")[-1])
        return {"order_status": "Filled", "avg_price": _FakeIBKR.fills.get(conid, "41.00")}


def _run(kind: str, payload: dict[str, Any], settings: Any) -> None:
    with dbmod.get_session() as s:
        dbmod.request_job(s, kind=kind, payload=json.dumps(payload))
        job = dbmod.claim_next_job(s)
        assert job is not None
        worker.process_job(s, job, settings)


def test_single_buy_captures_fill_and_slippage(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    _FakeIBKR.fills = {111: "41.00"}
    with dbmod.get_session() as s:
        t = dbmod.create_order_ticket(
            s, status=dbmod.TICKET_CONFIRMED, conid=111, symbol="AAA", quantity=0.1,
            ref_price_local=40.0, price_eur_ref=40.0)
        tid = int(t.id)

    _run(dbmod.JOB_KIND_ORDER_PLACE, {"ticket_id": tid}, _settings())

    with dbmod.get_session() as s:
        t = dbmod.get_order_ticket(s, tid)
    assert t.status == dbmod.TICKET_PLACED
    assert t.fill_price == pytest.approx(41.0)
    # (41-40)/40 = +2.5% (paid above reference = a cost).
    assert t.slippage_pct == pytest.approx(2.5)
    # 2.5% of the €4 reference cost (0.1 x €40) = €0.10.
    assert t.slippage_eur == pytest.approx(0.10)


def test_no_reference_price_leaves_slippage_none(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    with dbmod.get_session() as s:
        t = dbmod.create_order_ticket(s, status=dbmod.TICKET_CONFIRMED, conid=111, symbol="AAA",
                                      quantity=0.1, ref_price_local=None, price_eur_ref=40.0)
        tid = int(t.id)
    _run(dbmod.JOB_KIND_ORDER_PLACE, {"ticket_id": tid}, _settings())
    with dbmod.get_session() as s:
        t = dbmod.get_order_ticket(s, tid)
    assert t.fill_price == pytest.approx(41.0)  # fill still captured
    assert t.slippage_pct is None               # but no reference to compare


def test_batch_records_per_ticket_slippage(tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ibkr_portfolio_connect.ibkr_client.IBKRClient", _FakeIBKR)
    _FakeIBKR.fills = {1: "41.00", 2: "20.50"}  # +2.5% and +2.5%
    with dbmod.get_session() as s:
        b = dbmod.create_order_batch(s, strategy_id=28, strategy_name="X",
                                     total_pct=50.0, status=dbmod.TICKET_CONFIRMED)
        dbmod.create_order_ticket(s, batch_id=b.id, status=dbmod.TICKET_CONFIRMED, conid=1,
                                  symbol="AAA", quantity=0.1, ref_price_local=40.0, price_eur_ref=40.0)
        dbmod.create_order_ticket(s, batch_id=b.id, status=dbmod.TICKET_CONFIRMED, conid=2,
                                  symbol="BBB", quantity=1.0, ref_price_local=20.0, price_eur_ref=20.0)
        bid = int(b.id)

    _run(dbmod.JOB_KIND_BATCH_PLACE, {"batch_id": bid}, _settings())

    with dbmod.get_session() as s:
        ts = {t.symbol: t for t in dbmod.tickets_for_batch(s, bid)}
    assert ts["AAA"].slippage_pct == pytest.approx(2.5)
    assert ts["BBB"].slippage_pct == pytest.approx(2.5)
    # €0.10 (AAA) + €0.50 (BBB: 2.5% of 1x€20) = €0.60 total slippage.
    total = sum(t.slippage_eur for t in ts.values())
    assert total == pytest.approx(0.60)
