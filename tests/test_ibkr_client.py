"""Tests for the IBKR Client Portal API wrapper.

These never hit the real gateway; all HTTP is mocked via httpx.MockTransport.
The goal is to lock the URL paths, request shapes, and response parsing.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from decimal import Decimal
from typing import Any

import httpx
import pytest

from ibkr_portfolio_connect.ibkr_client import (
    IBKRAuthError,
    IBKRClient,
    IBKRError,
    _to_current_position,
)
from ibkr_portfolio_connect.schema import OrderSide

GATEWAY = "https://localhost:5000"
API = "/v1/api"


# ---- helpers ---------------------------------------------------------------


HandlerKey = tuple[str, str]
HandlerMap = dict[HandlerKey, Callable[[httpx.Request], httpx.Response]]


def _client_with(handlers: HandlerMap) -> IBKRClient:
    def _dispatch(request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in handlers:
            return handlers[key](request)
        return httpx.Response(404, json={"err": f"unmocked {key}"})

    transport = httpx.MockTransport(_dispatch)
    return IBKRClient(GATEWAY, verify_ssl=False, transport=transport)


def _json(body: Any, status: int = 200) -> httpx.Response:
    return httpx.Response(status, json=body)


# ---- auth ------------------------------------------------------------------


class TestAuth:
    def test_auth_status_ok(self) -> None:
        with _client_with(
            {
                ("POST", f"{API}/iserver/auth/status"): lambda r: _json(
                    {"authenticated": True, "connected": True, "competing": False}
                ),
            }
        ) as c:
            s = c.auth_status()
            assert s.authenticated is True
            assert s.connected is True

    def test_auth_status_unauthenticated(self) -> None:
        with _client_with(
            {
                ("POST", f"{API}/iserver/auth/status"): lambda r: _json(
                    {"authenticated": False, "connected": True}
                ),
            }
        ) as c:
            s = c.auth_status()
            assert s.authenticated is False

    def test_401_raises_auth_error(self) -> None:
        with (
            _client_with(
                {
                    ("POST", f"{API}/iserver/auth/status"): lambda r: httpx.Response(
                        401, text="nope"
                    ),
                }
            ) as c,
            pytest.raises(IBKRAuthError),
        ):
            c.auth_status()

    def test_ensure_authenticated_retries_once(self) -> None:
        # First call returns not-authenticated, reauthenticate is called,
        # second call returns authenticated.
        calls = {"status": 0, "reauth": 0}

        def status_handler(_r: httpx.Request) -> httpx.Response:
            calls["status"] += 1
            authed = calls["status"] >= 2
            return _json({"authenticated": authed, "connected": True})

        def reauth_handler(_r: httpx.Request) -> httpx.Response:
            calls["reauth"] += 1
            return _json({})

        with _client_with(
            {
                ("POST", f"{API}/iserver/auth/status"): status_handler,
                ("POST", f"{API}/iserver/reauthenticate"): reauth_handler,
            }
        ) as c:
            c.ensure_authenticated()
        assert calls["reauth"] == 1
        assert calls["status"] == 2

    def test_ensure_authenticated_gives_up(self) -> None:
        with (
            _client_with(
                {
                    ("POST", f"{API}/iserver/auth/status"): lambda r: _json(
                        {"authenticated": False, "connected": False, "message": "dead"}
                    ),
                    ("POST", f"{API}/iserver/reauthenticate"): lambda r: _json({}),
                }
            ) as c,
            pytest.raises(IBKRAuthError, match="dead"),
        ):
            c.ensure_authenticated()


class TestTickle:
    def test_tickle(self) -> None:
        with _client_with(
            {
                ("POST", f"{API}/tickle"): lambda r: _json({"session": "abc", "ssoExpires": 1000}),
            }
        ) as c:
            data = c.tickle()
        assert data["session"] == "abc"


# ---- positions -------------------------------------------------------------


class TestPositions:
    def test_positions_single_page(self) -> None:
        page = [
            {
                "acctId": "U1",
                "conid": 756733,
                "contractDesc": "SPY",
                "position": 5.0,
                "mktPrice": 471.16,
                "mktValue": 2355.8,
                "currency": "USD",
                "assetClass": "STK",
            }
        ]
        with _client_with({("GET", f"{API}/portfolio/U1/positions/0"): lambda r: _json(page)}) as c:
            positions = c.positions("U1")
        assert len(positions) == 1
        p = positions[0]
        assert p.conid == 756733
        assert p.symbol == "SPY"
        assert p.quantity == Decimal("5.0")
        assert p.market_value == Decimal("2355.8")

    def test_positions_paginated(self) -> None:
        # Build 100 fake rows for page 0, 1 row for page 1
        page_0 = [
            {
                "conid": 1000 + i,
                "contractDesc": f"T{i}",
                "position": 1.0,
                "mktValue": 100.0,
                "currency": "USD",
                "assetClass": "STK",
            }
            for i in range(100)
        ]
        page_1 = [
            {
                "conid": 9999,
                "contractDesc": "EXTRA",
                "position": 2.0,
                "mktValue": 50.0,
                "currency": "USD",
                "assetClass": "STK",
            }
        ]
        with _client_with(
            {
                ("GET", f"{API}/portfolio/U1/positions/0"): lambda r: _json(page_0),
                ("GET", f"{API}/portfolio/U1/positions/1"): lambda r: _json(page_1),
            }
        ) as c:
            positions = c.positions("U1")
        assert len(positions) == 101
        assert positions[-1].symbol == "EXTRA"

    def test_positions_short_position_signed(self) -> None:
        page = [
            {
                "conid": 1,
                "contractDesc": "SHORT",
                "position": -10.0,
                "mktValue": -2000.0,
                "currency": "USD",
                "assetClass": "STK",
            }
        ]
        with _client_with({("GET", f"{API}/portfolio/U1/positions/0"): lambda r: _json(page)}) as c:
            positions = c.positions("U1")
        assert positions[0].quantity == Decimal("-10.0")
        assert positions[0].market_value == Decimal("-2000.0")


# ---- secdef / resolve_conid -----------------------------------------------


class TestResolveConid:
    def _search_payload(self) -> list[dict[str, Any]]:
        return [
            {
                "conid": 12345,
                "symbol": "VTI",
                "description": "VANGUARD TOTAL STOCK MARKET ETF",
                "sections": [
                    {"secType": "STK", "exchange": "ARCA,BATS,NYSE"},
                    {"secType": "OPT"},
                ],
            },
            {
                "conid": 99999,
                "symbol": "VTI-OTHER",
                "sections": [{"secType": "STK", "exchange": "ARCA"}],
            },
        ]

    def test_resolve_conid_exact_match(self) -> None:
        payload = self._search_payload()
        with _client_with({("GET", f"{API}/iserver/secdef/search"): lambda r: _json(payload)}) as c:
            conid = c.resolve_conid("VTI", "ARCA")
        assert conid == 12345

    def test_resolve_conid_falls_back_to_first_match_on_unknown_exchange(self) -> None:
        payload = self._search_payload()
        with _client_with({("GET", f"{API}/iserver/secdef/search"): lambda r: _json(payload)}) as c:
            conid = c.resolve_conid("VTI", "MADEUPEXCH")
        assert conid == 12345

    def test_resolve_conid_no_match_raises(self) -> None:
        with (
            _client_with({("GET", f"{API}/iserver/secdef/search"): lambda r: _json([])}) as c,
            pytest.raises(IBKRError, match="no STK match"),
        ):
            c.resolve_conid("NOPE", "ARCA")


# ---- place_order / reply flow ---------------------------------------------


class TestPlaceOrder:
    def test_place_order_confirmed(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(request.content)
            return _json([{"order_id": "111", "order_status": "Submitted", "encrypt_message": "1"}])

        with _client_with({("POST", f"{API}/iserver/account/U1/orders"): handler}) as c:
            replies = c.place_market_day_order("U1", conid=42, side=OrderSide.BUY, quantity=5)
        assert len(replies) == 1
        assert replies[0].kind == "confirmed"
        assert replies[0].order_id == "111"
        # Verify request body shape — this is the IBKR contract we depend on.
        order = captured["body"]["orders"][0]
        assert order["conid"] == 42
        assert order["orderType"] == "MKT"
        assert order["tif"] == "DAY"
        assert order["side"] == "BUY"
        assert order["quantity"] == 5
        assert order["acctId"] == "U1"
        assert order["manualIndicator"] is False

    def test_place_order_returns_reply_required(self) -> None:
        with _client_with(
            {
                ("POST", f"{API}/iserver/account/U1/orders"): lambda r: _json(
                    [
                        {
                            "id": "abc-123",
                            "message": ["Order exceeds size limits..."],
                            "isSuppressed": False,
                            "messageIds": ["o163"],
                        }
                    ]
                ),
            }
        ) as c:
            replies = c.place_market_day_order("U1", conid=1, side=OrderSide.SELL, quantity=2)
        assert replies[0].kind == "reply_required"
        assert replies[0].id == "abc-123"

    def test_place_order_returns_200_with_error(self) -> None:
        with _client_with(
            {
                ("POST", f"{API}/iserver/account/U1/orders"): lambda r: _json(
                    {"error": "Insufficient funds"}
                ),
            }
        ) as c:
            replies = c.place_market_day_order("U1", conid=1, side=OrderSide.BUY, quantity=999)
        assert replies[0].kind == "error"
        assert "Insufficient" in (replies[0].error or "")

    def test_confirm_reply(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = json.loads(request.content)
            return _json([{"order_id": "999", "order_status": "Submitted"}])

        with _client_with({("POST", f"{API}/iserver/reply/abc-123"): handler}) as c:
            replies = c.confirm_reply("abc-123")
        assert replies[0].kind == "confirmed"
        assert captured["body"] == {"confirmed": True}


# ---- portfolio summary / market data ---------------------------------------


class TestPortfolioSummary:
    def test_portfolio_summary(self) -> None:
        with _client_with(
            {
                ("GET", f"{API}/portfolio/U1/summary"): lambda r: _json(
                    {
                        "netliquidation": {"amount": 12345.67, "currency": "USD"},
                        "totalcashvalue": {"amount": 1000.0, "currency": "USD"},
                    }
                ),
            }
        ) as c:
            summary = c.portfolio_summary("U1")
        assert summary["netliquidation"]["amount"] == 12345.67


class TestMarketdataSnapshot:
    def test_marketdata_snapshot_passes_conids_and_fields(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["params"] = dict(request.url.params)
            return _json([{"conid": "1", "31": "100.50"}, {"conid": "2", "31": "200.0"}])

        with _client_with({("GET", f"{API}/iserver/marketdata/snapshot"): handler}) as c:
            rows = c.marketdata_snapshot([1, 2])
        assert len(rows) == 2
        assert captured["params"]["conids"] == "1,2"
        assert captured["params"]["fields"] == "31"

    def test_marketdata_snapshot_empty_conids_is_noop(self) -> None:
        with _client_with({}) as c:
            assert c.marketdata_snapshot([]) == []

    def test_marketdata_snapshot_custom_fields(self) -> None:
        captured: dict[str, str] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["fields"] = request.url.params.get("fields", "")
            return _json([])

        with _client_with({("GET", f"{API}/iserver/marketdata/snapshot"): handler}) as c:
            c.marketdata_snapshot([1], fields=["31", "84", "86"])
        assert captured["fields"] == "31,84,86"


# ---- order_status / live_orders --------------------------------------------


class TestOrderStatus:
    def test_order_status(self) -> None:
        with _client_with(
            {
                ("GET", f"{API}/iserver/account/order/status/111"): lambda r: _json(
                    {"order_id": "111", "order_status": "Filled"}
                ),
            }
        ) as c:
            assert c.order_status("111")["order_status"] == "Filled"

    def test_live_orders_returns_list(self) -> None:
        with _client_with(
            {
                ("GET", f"{API}/iserver/account/orders"): lambda r: _json(
                    {"orders": [{"orderId": 1, "status": "Filled"}]}
                ),
            }
        ) as c:
            assert len(c.live_orders()) == 1


# ---- gateway URL handling --------------------------------------------------


class TestGatewayUrl:
    def test_appends_v1_api_when_missing(self) -> None:
        with _client_with({}) as c:
            assert c._base == f"{GATEWAY}/v1/api"

    def test_preserves_v1_api_when_present(self) -> None:
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
        with IBKRClient(f"{GATEWAY}/v1/api", transport=transport) as c:
            assert c._base == f"{GATEWAY}/v1/api"


# ---- low-level: error propagation -----------------------------------------


def test_non_2xx_raises_ibkr_error() -> None:
    with (
        _client_with({("POST", f"{API}/tickle"): lambda r: httpx.Response(500, text="oof")}) as c,
        pytest.raises(IBKRError, match="500"),
    ):
        c.tickle()


def test_to_current_position_normalizes_missing_fields() -> None:
    raw = {"conid": 1, "position": 2.0}
    p = _to_current_position(raw)
    assert p.symbol == "1"  # falls back to conid
    assert p.currency == "USD"  # default
    assert p.asset_class == "STK"  # default
    assert p.market_value == Decimal("0")
