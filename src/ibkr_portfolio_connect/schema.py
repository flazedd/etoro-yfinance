"""Schemas: the target-portfolio JSON contract plus internal trade/position types.

The target portfolio is the external contract a separate service produces and the
rebalancer consumes (see examples/target-portfolio.example.json). Everything else
in this module is internal to the rebalancer.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

# Weight-sum check tolerance. Producers are expected to normalize before sending;
# this is just defensive against float-to-decimal round-trip noise.
WEIGHTS_SUM_TOLERANCE = Decimal("0.0001")


class AssetClass(StrEnum):
    """IBKR asset class. v1 supports stocks/ETFs only."""

    STK = "STK"


class OrderSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


Percent = Annotated[Decimal, Field(ge=Decimal("0"), le=Decimal("100"))]
TrimmedString = Annotated[
    str, StringConstraints(min_length=1, max_length=64, strip_whitespace=True)
]


class TargetPosition(BaseModel):
    """A single line in the target portfolio (schema v2)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    symbol: TrimmedString
    exchange: TrimmedString
    asset_class: AssetClass
    weight_pct: Percent
    # Per-share price the upstream service observed when generating this target.
    # The diff engine uses it to compute share counts and the slippage report
    # uses it as the benchmark for fills.
    reference_price: Decimal = Field(gt=0)
    reference_price_at: datetime


class TargetPortfolio(BaseModel):
    """External contract (schema v2) for the JSON the rebalancer consumes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: int = Field(ge=2, le=2)
    generated_at: datetime
    base_currency: Annotated[str, StringConstraints(min_length=3, max_length=3, to_upper=True)]
    cash_buffer_pct: Percent
    positions: list[TargetPosition] = Field(min_length=1)

    @field_validator("base_currency")
    @classmethod
    def _only_usd_in_v2(cls, v: str) -> str:
        if v != "USD":
            raise ValueError(f"base_currency must be 'USD' in v2, got {v!r}")
        return v

    @model_validator(mode="after")
    def _weights_sum_to_100(self) -> TargetPortfolio:
        total = (
            sum((p.weight_pct for p in self.positions), start=Decimal("0")) + self.cash_buffer_pct
        )
        if abs(total - Decimal("100")) > WEIGHTS_SUM_TOLERANCE:
            raise ValueError(f"sum(weight_pct) + cash_buffer_pct must equal 100; got {total}")
        return self

    @model_validator(mode="after")
    def _no_duplicate_positions(self) -> TargetPortfolio:
        seen: set[tuple[str, str]] = set()
        for p in self.positions:
            key = (p.symbol.upper(), p.exchange.upper())
            if key in seen:
                raise ValueError(f"duplicate position: {p.symbol} on {p.exchange}")
            seen.add(key)
        return self


class CurrentPosition(BaseModel):
    """A position currently held in the IBKR account, normalized from cpapi-v1.

    `quantity` and `market_value` are signed: negative values mean a short
    position. Numeric fields are Decimal so the diff engine can do exact
    money math.
    """

    model_config = ConfigDict(frozen=True)

    conid: int = Field(gt=0)
    symbol: TrimmedString
    asset_class: str  # raw from IBKR; rebalancer filters to STK upstream
    quantity: Decimal
    market_value: Decimal
    currency: TrimmedString
    # Per-share market price as reported by IBKR alongside the position. Kept
    # for diagnostic / logging purposes; sizing now uses the upstream-supplied
    # reference_price on TargetPosition instead.
    mkt_price: Decimal | None = None


class Trade(BaseModel):
    """A planned trade emitted by the diff engine and consumed by the executor.

    `reference_price` is the per-share price the upstream target service
    observed when generating the target portfolio. It carries through to
    the slippage report so we can attribute fills against the benchmark.
    None for liquidation trades (positions no longer in the target), which
    are sized purely from current quantity, not from a target reference.
    """

    model_config = ConfigDict(frozen=True)

    conid: int = Field(gt=0)
    symbol: TrimmedString
    exchange: TrimmedString
    side: OrderSide
    quantity: int = Field(gt=0)  # whole shares only in v1
    reason: TrimmedString
    reference_price: Decimal | None = None
