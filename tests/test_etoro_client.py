"""Tests for the eToro broker client — hermetic (httpx.MockTransport, no network).

Asserts the exact request shapes we send eToro (paths incl. the demo/real split,
headers, JSON bodies) and that responses map onto the broker-neutral dataclasses.
"""

from __future__ import annotations

import json
import types
from collections.abc import Callable
from decimal import Decimal

import httpx
import pytest
from pydantic import SecretStr

from etoro_yfinance.broker import (
    Broker,
    BrokerAuthError,
    BrokerError,
    Instrument,
)
from etoro_yfinance.etoro_client import EtoroClient, etoro_from_settings

_INST = Instrument(broker="etoro", instrument_id="1001", symbol="AAPL", currency="USD")


def _mk(handler: Callable[[httpx.Request], httpx.Response], env: str = "demo", **kw: object) -> EtoroClient:
    return EtoroClient(api_key="AK", user_key="UK", env=env,
                       transport=httpx.MockTransport(handler), **kw)  # type: ignore[arg-type]


def test_requires_keys_and_valid_env() -> None:
    with pytest.raises(BrokerAuthError):
        EtoroClient(api_key="", user_key="UK")
    with pytest.raises(BrokerError):
        EtoroClient(api_key="AK", user_key="UK", env="paper")


def test_implements_broker_protocol() -> None:
    with _mk(lambda r: httpx.Response(200, json={})) as c:
        assert isinstance(c, Broker)


def test_auth_headers_on_every_request() -> None:
    seen: dict[str, str] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen.update(dict(req.headers))
        return httpx.Response(200, json={"clientPortfolio": {"credit": 1}})

    with _mk(handler) as c:
        c.balance()
    assert seen["x-api-key"] == "AK"
    assert seen["x-user-key"] == "UK"
    assert seen["x-request-id"]  # a per-request uuid


def test_resolve_requires_exact_symbol_match() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/api/v1/market-data/search"
        assert req.url.params["internalSymbolFull"] == "AAPL"
        return httpx.Response(200, json={"items": [
            {"internalSymbolFull": "AAPLX", "instrumentId": 9},  # partial — must be ignored
            {"internalSymbolFull": "AAPL", "instrumentId": 1001,
             "instrumentDisplayName": "Apple", "instrumentCurrency": "USD"},
        ]})

    with _mk(handler) as c:
        inst = c.resolve_symbol("AAPL")
    assert inst.instrument_id == "1001"
    assert inst.symbol == "AAPL"
    assert inst.broker == "etoro"


def test_resolve_partial_only_and_empty_raise() -> None:
    with _mk(lambda r: httpx.Response(200, json={"items": [
            {"internalSymbolFull": "AAPLX", "instrumentId": 9}]})) as c, pytest.raises(BrokerError):
        c.resolve_symbol("AAPL")
    with _mk(lambda r: httpx.Response(200, json={"items": []})) as c, pytest.raises(BrokerError):
        c.resolve_symbol("ZZZZ")


def test_preview_buy_demo_path_body_and_totals() -> None:
    captured: dict[str, object] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["path"] = req.url.path
        captured["body"] = json.loads(req.content)
        return httpx.Response(200, json={"instrumentId": 1001, "symbol": "AAPL", "costs": [
            {"costType": "markup", "amount": "0.15", "currency": "USD"},
            {"costType": "transactionFee", "amount": "0.05", "currency": "USD"},
        ]})

    with _mk(handler) as c:
        prev = c.preview_buy(instrument=_INST, amount=Decimal("100"))
    assert captured["path"] == "/api/v2/trading/info/demo/costs"
    body = captured["body"]
    assert body["action"] == "open"
    assert body["transaction"] == "buy"
    assert body["instrumentId"] == 1001
    assert body["amount"] == 100.0
    assert body["orderCurrency"] == "usd"
    assert body["settlementType"] == "real"
    assert prev.est_cost == Decimal("0.20")
    assert prev.currency == "USD"
    assert len(prev.lines) == 2


def test_buy_demo_path_units_body_and_order_id() -> None:
    captured: dict[str, object] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["path"] = req.url.path
        captured["body"] = json.loads(req.content)
        return httpx.Response(200, json={"orderId": 13902598, "token": "t", "referenceId": "r"})

    with _mk(handler) as c:
        res = c.buy(instrument=_INST, units=Decimal("3"))
    assert captured["path"] == "/api/v2/trading/execution/demo/orders"
    assert captured["body"]["units"] == 3.0
    assert "amount" not in captured["body"]
    assert res.order_id == "13902598"
    assert res.broker == "etoro"


def test_buy_real_env_drops_demo_segment() -> None:
    captured: dict[str, object] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["path"] = req.url.path
        return httpx.Response(200, json={"orderId": 1})

    with _mk(handler, env="real") as c:
        c.buy(instrument=_INST, amount=Decimal("50"))
    assert captured["path"] == "/api/v2/trading/execution/orders"


def test_buy_requires_exactly_one_of_amount_units() -> None:
    with _mk(lambda r: httpx.Response(200, json={})) as c:
        with pytest.raises(BrokerError):
            c.buy(instrument=_INST)
        with pytest.raises(BrokerError):
            c.buy(instrument=_INST, amount=Decimal("1"), units=Decimal("1"))


def test_close_position_demo_path_body_and_result() -> None:
    captured: dict[str, object] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["path"] = req.url.path
        captured["body"] = json.loads(req.content)
        return httpx.Response(200, json={
            "orderForClose": {"orderID": 13904638, "positionID": 2150941015}, "token": "t"})

    with _mk(handler) as c:
        res = c.close_position(position_id="2150941015", instrument_id="1111", units=Decimal("2"))
    assert captured["path"] == "/api/v1/trading/execution/demo/market-close-orders/positions/2150941015"
    assert captured["body"] == {"InstrumentId": 1111, "UnitsToDeduct": 2.0}
    assert res.order_id == "13904638"
    assert res.status == "closing"


def test_close_whole_position_omits_units() -> None:
    captured: dict[str, object] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(req.content)
        return httpx.Response(200, json={"orderForClose": {"orderID": 1}})

    with _mk(handler) as c:
        c.close_position(position_id="5", instrument_id="9")
    assert "UnitsToDeduct" not in captured["body"]


def test_balance_reads_env_aware_pnl_credit() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/api/v1/trading/info/demo/pnl"  # demo-aware, not /balances
        return httpx.Response(200, json={
            "clientPortfolio": {"credit": 10000.5, "unrealizedPnL": 251, "bonusCredit": 500}})

    with _mk(handler) as c:
        b = c.balance()
    assert b.cash == Decimal("10000.5")
    assert b.total == Decimal("10000.5")
    assert b.currency == "USD"


def test_balance_real_env_drops_demo_segment() -> None:
    captured: dict[str, object] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["path"] = req.url.path
        return httpx.Response(200, json={"clientPortfolio": {"credit": 5}})

    with _mk(handler, env="real") as c:
        c.balance()
    assert captured["path"] == "/api/v1/trading/info/pnl"


def _settings(env: str, **over: object) -> types.SimpleNamespace:
    base: dict[str, object] = {
        "etoro_api_key": SecretStr("PUB"),
        "etoro_user_key_demo": SecretStr("DEMOKEY"),
        "etoro_user_key_real": SecretStr("REALKEY"),
        "etoro_user_key": None,
        "etoro_env": env, "etoro_order_currency": "usd", "etoro_default_leverage": 1,
        "http_timeout_seconds": 5.0,
    }
    base.update(over)
    return types.SimpleNamespace(**base)


def test_from_settings_selects_env_specific_user_key() -> None:
    t = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
    with etoro_from_settings(_settings("demo"), transport=t) as c:
        assert c._client.headers["x-user-key"] == "DEMOKEY"
        assert c._client.headers["x-api-key"] == "PUB"
    with etoro_from_settings(_settings("real"), transport=t) as c:
        assert c._client.headers["x-user-key"] == "REALKEY"


def test_from_settings_falls_back_to_generic_user_key() -> None:
    t = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
    s = _settings("demo", etoro_user_key_demo=None, etoro_user_key=SecretStr("GENERIC"))
    with etoro_from_settings(s, transport=t) as c:
        assert c._client.headers["x-user-key"] == "GENERIC"


def test_list_instruments_fetches_by_type_and_normalises() -> None:
    seen_paths: list[str] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen_paths.append(str(req.url))
        if req.url.path == "/api/v1/market-data/instrument-types":
            return httpx.Response(200, json={"instrumentTypes": [
                {"instrumentTypeID": 5, "instrumentTypeDescription": "Stocks"}]})
        return httpx.Response(200, json={"instrumentDisplayDatas": [
            {"instrumentID": 1001, "symbolFull": "AAPL", "instrumentTypeID": 5,
             "exchangeID": 4, "instrumentDisplayName": "Apple", "isInternalInstrument": False},
            {"instrumentID": 610, "symbolFull": "ETORIAN610", "instrumentTypeID": 5,
             "exchangeID": 4, "instrumentDisplayName": "ETORIAN610", "isInternalInstrument": True},
        ]})

    with _mk(handler) as c:
        rows = c.list_instruments()
    assert any("instrumentTypeIds=5" in p for p in seen_paths)  # enumerated by type
    assert rows[0] == {"instrument_id": 1001, "symbol": "AAPL", "type_id": 5,
                       "exchange_id": 4, "name": "Apple", "is_internal": False,
                       "stocks_industry_id": None}
    assert rows[1]["is_internal"] is True


def test_candles_parses_ohlcv_and_sorts_oldest_first() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/api/v1/market-data/instruments/100000/history/candles/desc/OneDay/2"
        return httpx.Response(200, json={"interval": "OneDay", "candles": [
            {"fromDate": "2026-07-03T00:00:00Z", "open": 2, "high": 3, "low": 1, "close": 2.5, "volume": None},
            {"fromDate": "2026-07-02T00:00:00Z", "open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": 10},
        ]})

    with _mk(handler) as c:
        rows = c.candles("100000", interval="OneDay", count=2)
    assert [r.date for r in rows] == ["2026-07-02T00:00:00Z", "2026-07-03T00:00:00Z"]
    assert rows[0].close == Decimal("1.5")
    assert rows[0].volume == Decimal("10")
    assert rows[1].volume is None


def test_candles_rejects_bad_interval_and_caps_count() -> None:
    captured: dict[str, object] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["path"] = req.url.path
        return httpx.Response(200, json={"candles": []})

    with _mk(handler) as c:
        with pytest.raises(BrokerError):
            c.candles("1", interval="OneYear")
        c.candles("1", count=5000)  # over the 1000 cap
    assert str(captured["path"]).endswith("/OneDay/1000")


def test_http_errors_map_to_broker_errors() -> None:
    with _mk(lambda r: httpx.Response(401, json={"error": "bad key"})) as c, \
            pytest.raises(BrokerAuthError):
        c.balance()
    with _mk(lambda r: httpx.Response(500, text="boom")) as c, pytest.raises(BrokerError):
        c.balance()
