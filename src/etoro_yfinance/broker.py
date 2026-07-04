"""Broker-agnostic trading interface.

A narrow, broker-neutral surface: resolve a symbol, preview an order's cost,
place a buy, close a long, read account value. `EtoroClient` implements this
`Broker` Protocol; a new venue just implements `Broker` and returns these
dataclasses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Protocol, runtime_checkable


class BrokerError(Exception):
    """Any broker-side failure (HTTP, API error, bad response shape)."""


class BrokerAuthError(BrokerError):
    """Credentials missing or rejected (e.g. 401/403)."""


@dataclass(frozen=True)
class Instrument:
    """A tradable resolved to a broker-native id (eToro instrumentId, IBKR
    conid, ...). `instrument_id` is a string so it's broker-shape-neutral."""

    broker: str
    instrument_id: str
    symbol: str
    name: str = ""
    currency: str = ""


@dataclass(frozen=True)
class CostLine:
    """One line of a preview's cost breakdown (fee/spread/markup/...)."""

    kind: str
    amount: Decimal
    currency: str = ""


@dataclass(frozen=True)
class OrderPreview:
    """What a buy would cost before committing — the broker's what-if."""

    instrument_id: str
    symbol: str
    est_cost: Decimal | None = None  # summed cost lines, if any
    currency: str = ""
    lines: list[CostLine] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OrderResult:
    """The outcome of placing (or closing) an order."""

    broker: str
    order_id: str
    status: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Candle:
    """One OHLCV bar. `date` is the bar's start (ISO string, as the broker gives
    it); prices/volume are Decimal (None if the broker omitted them)."""

    date: str
    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    close: Decimal | None = None
    volume: Decimal | None = None


@dataclass(frozen=True)
class Balance:
    """Account value snapshot. `total` = NAV / total account value,
    `cash` = available buying power."""

    total: Decimal | None = None
    cash: Decimal | None = None
    currency: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Broker(Protocol):
    """The minimal trading surface the app needs from any venue. Buy = open a
    long at market; sell = close an existing long by units. Implementations
    raise `BrokerError` / `BrokerAuthError` on failure."""

    name: str

    def resolve_symbol(self, symbol: str) -> Instrument: ...

    def preview_buy(
        self,
        *,
        instrument: Instrument,
        amount: Decimal | None = None,
        units: Decimal | None = None,
    ) -> OrderPreview: ...

    def buy(
        self,
        *,
        instrument: Instrument,
        amount: Decimal | None = None,
        units: Decimal | None = None,
    ) -> OrderResult: ...

    def close_position(
        self,
        *,
        position_id: str,
        instrument_id: str,
        units: Decimal | None = None,
    ) -> OrderResult: ...

    def balance(self) -> Balance: ...
