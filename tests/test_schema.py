"""Tests for the target-portfolio JSON contract and internal types."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ibkr_portfolio_connect.schema import (
    AssetClass,
    CurrentPosition,
    OrderSide,
    TargetPortfolio,
    TargetPosition,
    Trade,
)


def _valid_kwargs(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "schema_version": 1,
        "generated_at": datetime(2026, 5, 12, 12, 0, 0, tzinfo=UTC),
        "base_currency": "USD",
        "cash_buffer_pct": Decimal("0.5"),
        "positions": [
            {
                "symbol": "VTI",
                "exchange": "ARCA",
                "asset_class": "STK",
                "weight_pct": Decimal("60.0"),
            },
            {
                "symbol": "VXUS",
                "exchange": "NASDAQ",
                "asset_class": "STK",
                "weight_pct": Decimal("30.0"),
            },
            {
                "symbol": "BND",
                "exchange": "NASDAQ",
                "asset_class": "STK",
                "weight_pct": Decimal("9.5"),
            },
        ],
    }
    base.update(overrides)
    return base


class TestTargetPortfolio:
    def test_canonical_example_validates(self) -> None:
        p = TargetPortfolio(**_valid_kwargs())  # type: ignore[arg-type]
        assert p.schema_version == 1
        assert len(p.positions) == 3
        assert p.positions[0].symbol == "VTI"

    def test_weights_must_sum_to_100(self) -> None:
        kwargs = _valid_kwargs(cash_buffer_pct=Decimal("1.0"))  # sum becomes 100.5
        with pytest.raises(ValidationError, match="must equal 100"):
            TargetPortfolio(**kwargs)  # type: ignore[arg-type]

    def test_weights_sum_tolerance(self) -> None:
        # Tiny float-noise drift is accepted.
        kwargs = _valid_kwargs(cash_buffer_pct=Decimal("0.50001"))
        TargetPortfolio(**kwargs)  # type: ignore[arg-type]  # no error

    def test_rejects_non_usd_base_currency_in_v1(self) -> None:
        with pytest.raises(ValidationError, match="must be 'USD'"):
            TargetPortfolio(**_valid_kwargs(base_currency="EUR"))  # type: ignore[arg-type]

    def test_rejects_duplicate_position(self) -> None:
        positions = [
            {
                "symbol": "VTI",
                "exchange": "ARCA",
                "asset_class": "STK",
                "weight_pct": Decimal("50"),
            },
            {
                "symbol": "vti",
                "exchange": "arca",
                "asset_class": "STK",
                "weight_pct": Decimal("49.5"),
            },
        ]
        with pytest.raises(ValidationError, match="duplicate position"):
            TargetPortfolio(**_valid_kwargs(positions=positions))  # type: ignore[arg-type]

    def test_rejects_unknown_asset_class(self) -> None:
        positions = [
            {
                "symbol": "ESM5",
                "exchange": "CME",
                "asset_class": "FUT",
                "weight_pct": Decimal("99.5"),
            },
        ]
        with pytest.raises(ValidationError):
            TargetPortfolio(**_valid_kwargs(positions=positions))  # type: ignore[arg-type]

    def test_rejects_negative_weight(self) -> None:
        positions = [
            {
                "symbol": "VTI",
                "exchange": "ARCA",
                "asset_class": "STK",
                "weight_pct": Decimal("-1"),
            },
            {
                "symbol": "BND",
                "exchange": "NASDAQ",
                "asset_class": "STK",
                "weight_pct": Decimal("100.5"),
            },
        ]
        with pytest.raises(ValidationError):
            TargetPortfolio(**_valid_kwargs(positions=positions))  # type: ignore[arg-type]

    def test_rejects_extra_top_level_fields(self) -> None:
        with pytest.raises(ValidationError):
            TargetPortfolio(**_valid_kwargs(extra_field="oops"))  # type: ignore[arg-type]

    def test_rejects_extra_position_fields(self) -> None:
        positions = [
            {
                "symbol": "VTI",
                "exchange": "ARCA",
                "asset_class": "STK",
                "weight_pct": Decimal("99.5"),
                "leverage": 2,
            },
        ]
        with pytest.raises(ValidationError):
            TargetPortfolio(**_valid_kwargs(positions=positions))  # type: ignore[arg-type]

    def test_requires_at_least_one_position(self) -> None:
        with pytest.raises(ValidationError):
            TargetPortfolio(**_valid_kwargs(positions=[]))  # type: ignore[arg-type]

    def test_only_schema_version_1(self) -> None:
        with pytest.raises(ValidationError):
            TargetPortfolio(**_valid_kwargs(schema_version=2))  # type: ignore[arg-type]

    def test_is_frozen(self) -> None:
        p = TargetPortfolio(**_valid_kwargs())  # type: ignore[arg-type]
        with pytest.raises(ValidationError):
            p.cash_buffer_pct = Decimal("1.0")


class TestTargetPosition:
    def test_weight_must_be_nonneg(self) -> None:
        with pytest.raises(ValidationError):
            TargetPosition(
                symbol="VTI",
                exchange="ARCA",
                asset_class=AssetClass.STK,
                weight_pct=Decimal("-0.0001"),
            )

    def test_weight_capped_at_100(self) -> None:
        with pytest.raises(ValidationError):
            TargetPosition(
                symbol="VTI",
                exchange="ARCA",
                asset_class=AssetClass.STK,
                weight_pct=Decimal("100.5"),
            )

    def test_symbol_stripped(self) -> None:
        p = TargetPosition(
            symbol="  VTI  ",
            exchange="ARCA",
            asset_class=AssetClass.STK,
            weight_pct=Decimal("10"),
        )
        assert p.symbol == "VTI"


class TestTrade:
    def test_quantity_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            Trade(
                conid=1,
                symbol="VTI",
                exchange="ARCA",
                side=OrderSide.BUY,
                quantity=0,
                reason="rebalance",
            )

    def test_round_trip(self) -> None:
        t = Trade(
            conid=42,
            symbol="VTI",
            exchange="ARCA",
            side=OrderSide.BUY,
            quantity=5,
            reason="new position",
        )
        assert t.side is OrderSide.BUY
        assert t.quantity == 5


class TestCurrentPosition:
    def test_basic(self) -> None:
        c = CurrentPosition(
            conid=756733,
            symbol="SPY",
            asset_class="STK",
            quantity=Decimal("5"),
            market_value=Decimal("2355.8"),
            currency="USD",
        )
        assert c.quantity == Decimal("5")
        assert c.market_value == Decimal("2355.8")

    def test_short_position_signed(self) -> None:
        c = CurrentPosition(
            conid=1,
            symbol="X",
            asset_class="STK",
            quantity=Decimal("-10"),
            market_value=Decimal("-2000"),
            currency="USD",
        )
        assert c.quantity < 0
        assert c.market_value < 0
