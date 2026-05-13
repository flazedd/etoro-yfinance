"""Tests for the rebalance orchestrator.

The unit-level helpers (`_extract_nav`, `_parse_snapshot_price`, `_collect_prices`)
are tested directly. `run_rebalance` is exercised end-to-end with mocked
httpx transports so the IBKR gateway and target URL never touch the network.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

import httpx
import pytest

from ibkr_portfolio_connect.config import Settings
from ibkr_portfolio_connect.executor import ExecutionSummary
from ibkr_portfolio_connect.ibkr_client import IBKRClient
from ibkr_portfolio_connect.pipeline import (
    _collect_prices,
    _extract_nav,
    _parse_snapshot_price,
    run_rebalance,
)
from ibkr_portfolio_connect.rebalance import ResolvedTarget
from ibkr_portfolio_connect.schema import CurrentPosition

# ---- _extract_nav ----------------------------------------------------------


class TestExtractNav:
    def test_nested_amount_form(self) -> None:
        assert _extract_nav({"netliquidation": {"amount": 12345.67, "currency": "USD"}}) == Decimal(
            "12345.67"
        )

    def test_nested_value_form(self) -> None:
        assert _extract_nav({"netliquidation": {"value": 100.0, "currency": "USD"}}) == Decimal(
            "100.0"
        )

    def test_scalar_form(self) -> None:
        assert _extract_nav({"netliquidation": 5000}) == Decimal("5000")

    def test_falls_through_to_alternate_key(self) -> None:
        assert _extract_nav({"equitywithloanvalue": {"amount": 999}}) == Decimal("999")

    def test_skips_zero(self) -> None:
        # netliquidation is 0 → keep looking for a positive alternative
        with pytest.raises(ValueError, match="could not extract"):
            _extract_nav({"netliquidation": 0})

    def test_raises_when_missing(self) -> None:
        with pytest.raises(ValueError, match="could not extract"):
            _extract_nav({"randomkey": 1})

    def test_raises_when_unparseable(self) -> None:
        with pytest.raises(ValueError, match="could not extract"):
            _extract_nav({"netliquidation": "not-a-number"})


# ---- _parse_snapshot_price -------------------------------------------------


class TestParseSnapshotPrice:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("100.50", Decimal("100.50")),
            ("C100.50", Decimal("100.50")),  # closing-price prefix
            ("H250.0", Decimal("250.0")),
            (100.5, Decimal("100.5")),
            ("-3.25", Decimal("-3.25")),
            (None, None),
            ("", None),
            ("nope", None),
        ],
    )
    def test_parse(self, raw: object, expected: Decimal | None) -> None:
        assert _parse_snapshot_price({"31": raw}) == expected

    def test_no_field_returns_none(self) -> None:
        assert _parse_snapshot_price({}) is None


# ---- _collect_prices -------------------------------------------------------


class TestCollectPrices:
    def _client_with_snapshot(self, snapshot_response: list[dict[str, Any]]) -> IBKRClient:
        def handler(_r: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=snapshot_response)

        return IBKRClient(
            "https://localhost:5000",
            verify_ssl=False,
            transport=httpx.MockTransport(handler),
        )

    def test_uses_position_mkt_price(self) -> None:
        client = self._client_with_snapshot([])  # should never be called
        positions = [
            CurrentPosition(
                conid=1,
                symbol="VTI",
                asset_class="STK",
                quantity=Decimal("10"),
                market_value=Decimal("1000"),
                currency="USD",
                mkt_price=Decimal("100"),
            )
        ]
        targets = [ResolvedTarget(conid=1, symbol="VTI", exchange="ARCA", weight_pct=Decimal("99"))]
        prices = _collect_prices(client, positions, targets, sleeper=lambda _: None)
        assert prices == {1: Decimal("100")}

    def test_snapshot_fallback_for_missing(self) -> None:
        client = self._client_with_snapshot([{"conid": "2", "31": "200.00"}])
        positions: list[CurrentPosition] = []
        targets = [
            ResolvedTarget(conid=2, symbol="BND", exchange="NASDAQ", weight_pct=Decimal("99"))
        ]
        prices = _collect_prices(client, positions, targets, sleeper=lambda _: None)
        assert prices == {2: Decimal("200.00")}

    def test_snapshot_retry_until_warmed_up(self) -> None:
        # Returns empty on first call, full data on second.
        call_count = {"n": 0}

        def handler(_r: httpx.Request) -> httpx.Response:
            call_count["n"] += 1
            if call_count["n"] == 1:
                return httpx.Response(200, json=[])
            return httpx.Response(200, json=[{"conid": "2", "31": "200.00"}])

        client = IBKRClient(
            "https://localhost:5000",
            verify_ssl=False,
            transport=httpx.MockTransport(handler),
        )
        targets = [
            ResolvedTarget(conid=2, symbol="BND", exchange="NASDAQ", weight_pct=Decimal("99"))
        ]
        sleeps: list[float] = []
        prices = _collect_prices(client, [], targets, sleeper=lambda s: sleeps.append(s))
        assert prices == {2: Decimal("200.00")}
        assert call_count["n"] == 2
        assert sleeps == [1.0]

    def test_snapshot_gives_up_after_retries(self) -> None:
        client = self._client_with_snapshot([])  # always empty
        targets = [
            ResolvedTarget(conid=2, symbol="BND", exchange="NASDAQ", weight_pct=Decimal("99"))
        ]
        with pytest.raises(ValueError, match="could not resolve market prices"):
            _collect_prices(client, [], targets, sleeper=lambda _: None)


# ---- end-to-end run_rebalance ---------------------------------------------


class _StubNotifier:
    def __init__(self) -> None:
        self.summary: ExecutionSummary | None = None

    def notify(self, summary: ExecutionSummary) -> None:
        self.summary = summary


def _settings_for_run(*, dry_run: bool = True, account: str = "U1") -> Settings:
    """Build a Settings object without reading any real .env."""
    return Settings(
        ibkr_account_id=account,
        target_portfolio_url="https://target.invalid/p.json",  # type: ignore[arg-type]
        ibkr_gateway_url="https://gw.invalid",
        ibkr_gateway_verify_ssl=False,
        dry_run=dry_run,
        trading_hours_only=False,
        ntfy_topic=None,
    )


def _build_gateway_handler() -> tuple[httpx.MockTransport, dict[str, list[dict[str, Any]]]]:
    """Realistic gateway: returns scripted responses for all endpoints the
    pipeline calls. Returns (transport, call_log)."""
    call_log: dict[str, list[dict[str, Any]]] = {}

    def log(name: str, request: httpx.Request) -> None:
        call_log.setdefault(name, []).append(
            {"url": str(request.url), "body": request.content.decode() if request.content else ""}
        )

    def handle(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/iserver/auth/status"):
            log("auth_status", request)
            return httpx.Response(200, json={"authenticated": True, "connected": True})
        if path.endswith("/tickle"):
            log("tickle", request)
            return httpx.Response(200, json={"session": "abc"})
        if path == "/v1/api/portfolio/U1/positions/0":
            log("positions", request)
            return httpx.Response(
                200,
                json=[
                    {
                        "conid": 1,
                        "contractDesc": "VTI",
                        "position": 30,
                        "mktPrice": 100.0,
                        "mktValue": 3000.0,
                        "currency": "USD",
                        "assetClass": "STK",
                    }
                ],
            )
        if path == "/v1/api/portfolio/U1/summary":
            log("summary", request)
            return httpx.Response(
                200, json={"netliquidation": {"amount": 10000.0, "currency": "USD"}}
            )
        if path.endswith("/iserver/secdef/search"):
            sym = request.url.params.get("symbol", "")
            log("secdef", request)
            return httpx.Response(
                200,
                json=[
                    {
                        "conid": 1 if sym == "VTI" else 2 if sym == "BND" else 3,
                        "symbol": sym,
                        "sections": [{"secType": "STK", "exchange": "ARCA,NASDAQ"}],
                    }
                ],
            )
        if path.endswith("/iserver/marketdata/snapshot"):
            log("snapshot", request)
            # Return prices for conids 2 (BND) — VTI is already covered by positions
            return httpx.Response(
                200,
                json=[{"conid": "2", "31": "100.00"}],
            )
        if path == "/v1/api/iserver/account/U1/orders":
            log("place_order", request)
            return httpx.Response(
                200,
                json=[{"order_id": "111", "order_status": "Submitted"}],
            )
        if path.startswith("/v1/api/iserver/account/order/status/"):
            log("order_status", request)
            return httpx.Response(200, json={"order_status": "Filled"})
        return httpx.Response(404, json={"err": f"unmocked {path}"})

    return httpx.MockTransport(handle), call_log


def _build_target_handler(body: dict[str, Any]) -> httpx.MockTransport:
    def handle(_r: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    return httpx.MockTransport(handle)


def _target_body() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at": "2026-05-12T12:00:00Z",
        "base_currency": "USD",
        "cash_buffer_pct": 0.5,
        "positions": [
            {"symbol": "VTI", "exchange": "ARCA", "asset_class": "STK", "weight_pct": 60.0},
            {"symbol": "BND", "exchange": "NASDAQ", "asset_class": "STK", "weight_pct": 39.5},
        ],
    }


def test_run_rebalance_dry_run_end_to_end() -> None:
    settings = _settings_for_run(dry_run=True)
    gw, calls = _build_gateway_handler()
    notif = _StubNotifier()

    summary = run_rebalance(
        settings,
        ibkr_transport=gw,
        target_transport=_build_target_handler(_target_body()),
        notifier=notif,
        sleeper=lambda _: None,
    )
    assert summary.dry_run is True
    assert summary.overall_success is True
    # No orders should have been placed
    assert "place_order" not in calls
    assert notif.summary is summary


def test_run_rebalance_live_end_to_end_places_orders() -> None:
    settings = _settings_for_run(dry_run=False)
    gw, calls = _build_gateway_handler()
    notif = _StubNotifier()

    summary = run_rebalance(
        settings,
        ibkr_transport=gw,
        target_transport=_build_target_handler(_target_body()),
        notifier=notif,
        sleeper=lambda _: None,
    )
    assert summary.overall_success is True
    # We started with 30 VTI @ $100 ($3000) and 0 BND on a $10k account.
    # Target: 60% VTI ($6000 → 60 shares), 39.5% BND ($3950 → 39 shares).
    # Expect: BUY 30 VTI (60 - 30), BUY 39 BND.
    assert "place_order" in calls
    bodies = [json.loads(c["body"]) for c in calls["place_order"]]
    placed = sorted((b["orders"][0]["conid"], b["orders"][0]["quantity"]) for b in bodies)
    assert placed == [(1, 30), (2, 39)]


def test_run_rebalance_handles_no_trades() -> None:
    """Account already matches target → no orders placed but pipeline succeeds."""
    settings = _settings_for_run(dry_run=False)

    def handle(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/iserver/auth/status"):
            return httpx.Response(200, json={"authenticated": True, "connected": True})
        if path.endswith("/tickle"):
            return httpx.Response(200, json={})
        if path == "/v1/api/portfolio/U1/positions/0":
            return httpx.Response(
                200,
                json=[
                    {
                        "conid": 1,
                        "contractDesc": "VTI",
                        "position": 60,
                        "mktPrice": 100.0,
                        "mktValue": 6000.0,
                        "currency": "USD",
                        "assetClass": "STK",
                    },
                    {
                        "conid": 2,
                        "contractDesc": "BND",
                        "position": 39,
                        "mktPrice": 100.0,
                        "mktValue": 3900.0,
                        "currency": "USD",
                        "assetClass": "STK",
                    },
                ],
            )
        if path == "/v1/api/portfolio/U1/summary":
            return httpx.Response(200, json={"netliquidation": {"amount": 10000.0}})
        if path.endswith("/iserver/secdef/search"):
            sym = request.url.params.get("symbol", "")
            return httpx.Response(
                200,
                json=[
                    {
                        "conid": 1 if sym == "VTI" else 2,
                        "symbol": sym,
                        "sections": [{"secType": "STK", "exchange": "ARCA,NASDAQ"}],
                    }
                ],
            )
        return httpx.Response(404, text=path)

    notif = _StubNotifier()
    summary = run_rebalance(
        settings,
        ibkr_transport=httpx.MockTransport(handle),
        target_transport=_build_target_handler(_target_body()),
        notifier=notif,
        sleeper=lambda _: None,
    )
    assert summary.overall_success is True
    assert summary.n_total == 0
