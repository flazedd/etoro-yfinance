"""Tests for pre-trade safety checks."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from ibkr_portfolio_connect.config import Settings
from ibkr_portfolio_connect.safety import PreTradeSafetyError, check_safety
from ibkr_portfolio_connect.schema import (
    AssetClass,
    OrderSide,
    TargetPortfolio,
    TargetPosition,
    Trade,
)

NOW = datetime(2026, 5, 18, 12, 0, 0, tzinfo=UTC)
FRESH_REF = NOW - timedelta(hours=1)


def _settings(**overrides: object) -> Settings:
    base: dict[str, object] = {
        "ibkr_account_id": "U1",
        "target_portfolio_url": "https://target.invalid/p.json",
        "min_nav_dollars": Decimal("1000"),
        "max_trade_pct_of_nav": Decimal("50"),
        "max_total_churn_pct_of_nav": Decimal("100"),
        "max_reference_age_hours": 24.0,
    }
    base.update(overrides)
    return Settings(**base)  # type: ignore[arg-type]


def _target(*, ref_at: datetime = FRESH_REF) -> TargetPortfolio:
    return TargetPortfolio(
        schema_version=2,
        generated_at=ref_at,
        base_currency="USD",
        cash_buffer_pct=Decimal("0.5"),
        positions=[
            TargetPosition(
                symbol="VTI",
                exchange="ARCA",
                asset_class=AssetClass.STK,
                weight_pct=Decimal("60"),
                reference_price=Decimal("100"),
                reference_price_at=ref_at,
            ),
            TargetPosition(
                symbol="BND",
                exchange="NASDAQ",
                asset_class=AssetClass.STK,
                weight_pct=Decimal("39.5"),
                reference_price=Decimal("100"),
                reference_price_at=ref_at,
            ),
        ],
    )


def _trade(
    *,
    symbol: str = "VTI",
    side: OrderSide = OrderSide.BUY,
    quantity: int = 10,
    reference_price: Decimal | None = Decimal("100"),
    conid: int = 1,
) -> Trade:
    return Trade(
        conid=conid,
        symbol=symbol,
        exchange="ARCA",
        side=side,
        quantity=quantity,
        reason="test",
        reference_price=reference_price,
    )


def _check(**overrides: object) -> None:
    """Run check_safety with sensible defaults; pass overrides to vary."""
    defaults: dict[str, object] = {
        "settings": _settings(),
        "target": _target(),
        "trades": [_trade()],
        "nav": Decimal("10000"),
        "visible_accounts": ["U1"],
        "now": NOW,
    }
    defaults.update(overrides)
    check_safety(**defaults)  # type: ignore[arg-type]


class TestAccountVisibility:
    def test_passes_when_account_in_visible_list(self) -> None:
        _check(visible_accounts=["U1", "DUQ123"])

    def test_passes_when_visible_list_empty(self) -> None:
        # Skipped — IBKR may not return accounts under certain conditions.
        _check(visible_accounts=[])

    def test_raises_when_account_not_visible(self) -> None:
        with pytest.raises(PreTradeSafetyError, match="not in OAuth-visible accounts"):
            _check(visible_accounts=["DUQ123"])


class TestMinNav:
    def test_passes_at_threshold(self) -> None:
        # Trade $100 against $1000 NAV — well within other caps.
        _check(nav=Decimal("1000"), trades=[_trade(quantity=1)])

    def test_raises_below_threshold(self) -> None:
        with pytest.raises(PreTradeSafetyError, match="below min_nav_dollars"):
            _check(nav=Decimal("999"))

    def test_disabled_when_none(self) -> None:
        _check(
            settings=_settings(
                min_nav_dollars=None,
                max_trade_pct_of_nav=None,
                max_total_churn_pct_of_nav=None,
            ),
            nav=Decimal("1"),
        )


class TestMaxTradePct:
    def test_passes_within_cap(self) -> None:
        # 10 shares @ $100 = $1000, cap = 50% of $10000 = $5000 → ok
        _check(trades=[_trade(quantity=10)])

    def test_raises_above_cap(self) -> None:
        # 60 shares @ $100 = $6000, cap = $5000
        with pytest.raises(PreTradeSafetyError, match=r"exceeds .* of NAV"):
            _check(trades=[_trade(quantity=60)])

    def test_disabled_when_none(self) -> None:
        _check(
            settings=_settings(
                max_trade_pct_of_nav=None,
                max_total_churn_pct_of_nav=None,
            ),
            trades=[_trade(quantity=10000)],
        )

    def test_liquidation_trade_skipped(self) -> None:
        # No reference_price → skip the per-trade cap (size unknown).
        _check(trades=[_trade(quantity=10000, reference_price=None)])


class TestMaxChurn:
    def test_passes_within_cap(self) -> None:
        # 2 trades x 10 shares x $100 = $2000, cap = 100% of $10000 = $10000 → ok
        _check(trades=[_trade(quantity=10), _trade(symbol="BND", conid=2, quantity=10)])

    def test_raises_above_cap(self) -> None:
        # cap = $10000; build 11 trades of 10 shares x $100 = $11000 total
        trades = [_trade(quantity=10, conid=i, symbol=f"S{i}") for i in range(1, 12)]
        with pytest.raises(PreTradeSafetyError, match="total trade volume"):
            _check(trades=trades)

    def test_disabled_when_none(self) -> None:
        trades = [_trade(quantity=10, conid=i, symbol=f"S{i}") for i in range(1, 50)]
        _check(settings=_settings(max_total_churn_pct_of_nav=None), trades=trades)


class TestStaleReference:
    def test_passes_when_fresh(self) -> None:
        _check(target=_target(ref_at=NOW - timedelta(hours=1)))

    def test_raises_when_stale(self) -> None:
        with pytest.raises(
            PreTradeSafetyError, match=r"is .* old, exceeds max_reference_age_hours"
        ):
            _check(target=_target(ref_at=NOW - timedelta(hours=25)))

    def test_disabled_when_none(self) -> None:
        _check(
            settings=_settings(max_reference_age_hours=None),
            target=_target(ref_at=NOW - timedelta(days=365)),
        )


class TestErrorOrder:
    """First failing check wins — order matters when multiple would fail."""

    def test_account_check_fires_before_nav_check(self) -> None:
        with pytest.raises(PreTradeSafetyError, match="not in OAuth-visible"):
            _check(visible_accounts=["DUQ"], nav=Decimal("1"))
