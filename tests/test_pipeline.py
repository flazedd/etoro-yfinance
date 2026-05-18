"""Tests for the rebalance orchestrator.

Unit-level helpers (`_extract_nav`) are tested directly. `run_rebalance` is
exercised end-to-end with a fake IBKRClient (method-level mocking) injected
via the `client` parameter; the target URL is still mocked via an httpx
transport since target.py uses httpx.

The pre-OAuth pipeline used a marketdata snapshot to fetch prices for target
conids not currently held. That whole path is gone — sizing now uses the
reference_price embedded in each TargetPosition of schema v2.
"""

from __future__ import annotations

from decimal import Decimal
from types import TracebackType
from typing import Any, Self, cast

import httpx
import pytest

from ibkr_portfolio_connect.config import Settings
from ibkr_portfolio_connect.cost import RebalanceReport
from ibkr_portfolio_connect.ibkr_client import (
    AuthStatus,
    IBKRClient,
    PlaceOrderReply,
)
from ibkr_portfolio_connect.pipeline import _extract_nav, run_rebalance, run_what_if
from ibkr_portfolio_connect.schema import CurrentPosition, OrderSide

# ---- Fake IBKRClient for method-level mocking ------------------------------


class _FakeIBKR:
    """Method-level fake of IBKRClient.

    Tests configure canned responses via attributes and read call history
    back for assertions. Construction is free (no OAuth handshake).
    """

    def __init__(self) -> None:
        self.positions_data: list[CurrentPosition] = []
        self.summary_data: dict[str, Any] = {}
        # (symbol, exchange) → conid for resolve_conid
        self.conid_map: dict[tuple[str, str], int] = {}
        self.order_status_data: dict[str, Any] = {"order_status": "Filled"}
        self.visible_accounts: list[str] = []
        # Call history
        self.placed_orders: list[dict[str, Any]] = []
        self.tickle_called: bool = False

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    def auth_status(self) -> AuthStatus:
        return AuthStatus(authenticated=True, connected=True)

    def ensure_authenticated(self) -> AuthStatus:
        return self.auth_status()

    def tickle(self) -> dict[str, Any]:
        self.tickle_called = True
        return {}

    def iserver_accounts(self) -> list[str]:
        return list(self.visible_accounts)

    def positions(self, account_id: str) -> list[CurrentPosition]:
        return list(self.positions_data)

    def portfolio_summary(self, account_id: str) -> dict[str, Any]:
        return dict(self.summary_data)

    def resolve_conid(self, symbol: str, exchange: str, *, asset_class: str = "STK") -> int:
        return self.conid_map[(symbol, exchange)]

    def place_midprice_day_order(
        self,
        account_id: str,
        *,
        conid: int,
        side: OrderSide,
        quantity: int,
        listing_exchange: str | None = None,
    ) -> list[PlaceOrderReply]:
        order_id = str(100 + len(self.placed_orders))
        self.placed_orders.append(
            {
                "account_id": account_id,
                "conid": conid,
                "side": side,
                "quantity": quantity,
                "listing_exchange": listing_exchange,
                "order_id": order_id,
            }
        )
        return [PlaceOrderReply(order_id=order_id, order_status="Submitted")]

    def order_status(self, order_id: str) -> dict[str, Any]:
        return dict(self.order_status_data)

    def what_if_order(
        self,
        account_id: str,
        *,
        conid: int,
        side: OrderSide,
        quantity: int,
        listing_exchange: str | None = None,
    ) -> dict[str, Any]:
        # Return a canned preview keyed by conid so tests can scope behavior.
        return {
            "commission": "0.35",
            "initMargin": "100.00",
            "_test_conid": conid,
            "_test_side": side.value,
            "_test_quantity": quantity,
        }


def _as_client(fake: _FakeIBKR) -> IBKRClient:
    return cast(IBKRClient, fake)


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
        with pytest.raises(ValueError, match="could not extract"):
            _extract_nav({"netliquidation": 0})

    def test_raises_when_missing(self) -> None:
        with pytest.raises(ValueError, match="could not extract"):
            _extract_nav({"randomkey": 1})

    def test_raises_when_unparseable(self) -> None:
        with pytest.raises(ValueError, match="could not extract"):
            _extract_nav({"netliquidation": "not-a-number"})


# ---- end-to-end run_rebalance ---------------------------------------------


class _StubNotifier:
    def __init__(self) -> None:
        self.report: RebalanceReport | None = None

    def notify(self, report: RebalanceReport) -> None:
        self.report = report


def _settings_for_run(*, dry_run: bool = True, account: str = "U1") -> Settings:
    return Settings(
        ibkr_account_id=account,
        target_portfolio_url="https://target.invalid/p.json",  # type: ignore[arg-type]
        dry_run=dry_run,
        trading_hours_only=False,
        ntfy_topic=None,
        # Disable pre-trade safety thresholds — they have their own test suite,
        # and stale-reference dates in fixtures here would constantly trip them.
        min_nav_dollars=None,
        max_trade_pct_of_nav=None,
        max_total_churn_pct_of_nav=None,
        max_reference_age_hours=None,
    )


def _build_target_handler(body: dict[str, Any]) -> httpx.MockTransport:
    def handle(_r: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    return httpx.MockTransport(handle)


def _target_body() -> dict[str, Any]:
    return {
        "schema_version": 2,
        "generated_at": "2026-05-12T12:00:00Z",
        "base_currency": "USD",
        "cash_buffer_pct": 0.5,
        "positions": [
            {
                "symbol": "VTI",
                "exchange": "ARCA",
                "asset_class": "STK",
                "weight_pct": 60.0,
                "reference_price": 100.0,
                "reference_price_at": "2026-05-12T12:00:00Z",
            },
            {
                "symbol": "BND",
                "exchange": "NASDAQ",
                "asset_class": "STK",
                "weight_pct": 39.5,
                "reference_price": 100.0,
                "reference_price_at": "2026-05-12T12:00:00Z",
            },
        ],
    }


def _make_fake_for_rebalance(positions: list[CurrentPosition]) -> _FakeIBKR:
    """Build a fake configured for the 'standard' rebalance scenario:
    $10k account, VTI conid=1 and BND conid=2 with $100 reference prices."""
    fake = _FakeIBKR()
    fake.positions_data = positions
    fake.summary_data = {"netliquidation": {"amount": 10000.0, "currency": "USD"}}
    fake.conid_map = {("VTI", "ARCA"): 1, ("BND", "NASDAQ"): 2}
    fake.visible_accounts = ["U1"]  # matches _settings_for_run(account="U1")
    return fake


def test_run_rebalance_dry_run_end_to_end() -> None:
    settings = _settings_for_run(dry_run=True)
    fake = _make_fake_for_rebalance(
        [
            CurrentPosition(
                conid=1,
                symbol="VTI",
                asset_class="STK",
                quantity=Decimal("30"),
                market_value=Decimal("3000"),
                currency="USD",
                mkt_price=Decimal("100"),
            )
        ]
    )
    notif = _StubNotifier()

    report = run_rebalance(
        settings,
        client=_as_client(fake),
        target_transport=_build_target_handler(_target_body()),
        notifier=notif,
        sleeper=lambda _: None,
    )
    assert report.dry_run is True
    assert report.overall_success is True
    assert fake.placed_orders == []
    assert notif.report is report


def test_run_rebalance_live_end_to_end_places_orders() -> None:
    settings = _settings_for_run(dry_run=False)
    fake = _make_fake_for_rebalance(
        [
            CurrentPosition(
                conid=1,
                symbol="VTI",
                asset_class="STK",
                quantity=Decimal("30"),
                market_value=Decimal("3000"),
                currency="USD",
                mkt_price=Decimal("100"),
            )
        ]
    )
    notif = _StubNotifier()

    report = run_rebalance(
        settings,
        client=_as_client(fake),
        target_transport=_build_target_handler(_target_body()),
        notifier=notif,
        sleeper=lambda _: None,
    )
    assert report.overall_success is True
    # Start: 30 VTI @ $100 ($3000), 0 BND on $10k account.
    # Target: 60% VTI ($6000 -> 60), 39.5% BND ($3950 -> 39).
    # Expect: BUY 30 VTI (60 - 30), BUY 39 BND.
    placed = sorted((o["conid"], o["quantity"]) for o in fake.placed_orders)
    assert placed == [(1, 30), (2, 39)]


def test_run_what_if_returns_previews_without_placing_orders() -> None:
    settings = _settings_for_run(dry_run=False)
    fake = _make_fake_for_rebalance(
        [
            CurrentPosition(
                conid=1,
                symbol="VTI",
                asset_class="STK",
                quantity=Decimal("30"),
                market_value=Decimal("3000"),
                currency="USD",
                mkt_price=Decimal("100"),
            )
        ]
    )
    previews = run_what_if(
        settings,
        client=_as_client(fake),
        target_transport=_build_target_handler(_target_body()),
    )
    # Expect 2 trades planned (BUY 30 VTI, BUY 39 BND); each gets a preview.
    assert len(previews) == 2
    assert fake.placed_orders == []  # no orders placed!
    for item in previews:
        assert "trade" in item
        assert "preview" in item
        assert item["preview"]["commission"] == "0.35"


def test_run_rebalance_handles_no_trades() -> None:
    settings = _settings_for_run(dry_run=False)
    fake = _make_fake_for_rebalance(
        [
            CurrentPosition(
                conid=1,
                symbol="VTI",
                asset_class="STK",
                quantity=Decimal("60"),
                market_value=Decimal("6000"),
                currency="USD",
                mkt_price=Decimal("100"),
            ),
            CurrentPosition(
                conid=2,
                symbol="BND",
                asset_class="STK",
                quantity=Decimal("39"),
                market_value=Decimal("3900"),
                currency="USD",
                mkt_price=Decimal("100"),
            ),
        ]
    )
    notif = _StubNotifier()

    report = run_rebalance(
        settings,
        client=_as_client(fake),
        target_transport=_build_target_handler(_target_body()),
        notifier=notif,
        sleeper=lambda _: None,
    )
    assert report.overall_success is True
    assert report.n_total == 0
    assert fake.placed_orders == []
