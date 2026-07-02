"""Sizing + preview-parsing for the manual single-stock test-buy.

Pure, IBKR-free helpers so the risky math is unit-testable: turn a "% of NAV"
into a concrete share quantity (fractional on US listings, whole-share-floored
elsewhere), and distil IBKR's raw what-if blob into the few numbers the preview
card shows. The worker owns the actual IBKR calls and DB writes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

# IBKR fractional shares are (in practice) a US-listings feature. We treat these
# listing-exchange codes as fractional-eligible; everything else is whole-share.
US_FRACTIONAL_LISTINGS = {"ARCA", "NASDAQ", "NYSE", "BATS", "AMEX", "PINK", "IEX", "NYSENAT"}

# Round fractional quantities to a sane precision (IBKR accepts small fractions).
_FRACTIONAL_DECIMALS = 5


def is_fractional_eligible(listing_exchange: str | None) -> bool:
    return (listing_exchange or "").upper() in US_FRACTIONAL_LISTINGS


@dataclass
class Sizing:
    """Result of sizing an order — either a placeable `quantity`, or a
    `blocked_reason` explaining why this % can't be turned into an order."""

    target_eur: Decimal
    fractional: bool
    quantity: float | None = None
    est_cost_eur: Decimal | None = None
    blocked_reason: str | None = None

    @property
    def ok(self) -> bool:
        return self.quantity is not None and self.blocked_reason is None


def size_order(
    *, nav_eur: Decimal, pct: Decimal, price_eur: Decimal, fractional: bool
) -> Sizing:
    """`pct`% of `nav_eur` → shares at `price_eur`. Fractional listings keep the
    exact fraction; the rest floor to whole shares and block if that rounds to
    zero (so a €2.55 intent never becomes a whole €355 share)."""
    target = (nav_eur * pct / Decimal("100")).quantize(Decimal("0.01"))
    out = Sizing(target_eur=target, fractional=fractional)

    if price_eur is None or price_eur <= 0:
        out.blocked_reason = "no reference price to size against"
        return out
    if target <= 0:
        out.blocked_reason = "target amount is zero — raise the % or fund the account"
        return out

    exact = target / price_eur
    if fractional:
        qty = round(float(exact), _FRACTIONAL_DECIMALS)
        if qty <= 0:
            out.blocked_reason = f"target €{target} is below the minimum fractional size"
            return out
        out.quantity = qty
    else:
        whole = math.floor(exact)
        if whole < 1:
            out.blocked_reason = (
                f"€{target} buys 0 whole shares at €{price_eur:.2f}/share and this "
                f"listing isn't fractional-tradable — raise the % or pick a cheaper name"
            )
            return out
        out.quantity = float(whole)

    out.est_cost_eur = (Decimal(str(out.quantity)) * price_eur).quantize(Decimal("0.01"))
    return out


@dataclass
class WhatIf:
    """The few fields we surface from IBKR's raw what-if response."""

    order_value: str | None = None      # amount + currency, IBKR's own string
    commission: str | None = None
    init_margin: str | None = None
    warnings: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


def _amount_str(node: Any) -> str | None:
    """IBKR what-if values arrive as {'amount': '2.55', 'currency': 'USD'} or a
    bare string/number — normalise to a short display string."""
    if node is None:
        return None
    if isinstance(node, dict):
        amt = node.get("amount", node.get("value"))
        ccy = node.get("currency", "")
        if amt is None:
            return None
        return f"{amt} {ccy}".strip()
    return str(node)


def parse_whatif(raw: dict[str, Any]) -> WhatIf:
    """Best-effort extraction — IBKR's shape varies by account/instrument, so
    every field is optional and the raw blob is retained for the details view."""
    warnings: list[str] = []
    for key in ("warn", "warning", "error", "message"):
        v = raw.get(key)
        if isinstance(v, str) and v.strip():
            warnings.append(v.strip())
    return WhatIf(
        order_value=_amount_str(raw.get("amount")),
        commission=_amount_str(raw.get("commission")),
        init_margin=_amount_str(raw.get("initial") or raw.get("initMargin")
                                or raw.get("initMarginChange")),
        warnings=warnings,
        raw=raw,
    )
