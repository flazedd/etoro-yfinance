"""Pure diff engine: (current positions, targets with reference_price, NAV) → trades.

No I/O. No globals. Same inputs → same outputs. The algorithmic core of the
rebalancer, kept deliberately simple so it's easy to reason about and test
exhaustively (including property tests in tests/test_rebalance.py).

Algorithm:
  - For each target position: target_shares = floor((weight_pct / 100) * NAV / reference_price).
    The trade is the delta from the integer portion of the currently held
    quantity to target_shares.
  - For each currently-held position NOT in the target: trade the integer
    portion to zero (sell if long, buy if short).
  - Whole shares only. Any fractional residue on existing positions cannot be
    traded out by v1 and is ignored.
  - Cash buffer is implicit: cash unallocated by target weights stays as cash.

Sizing uses each target's `reference_price` (supplied by the upstream service
in the target portfolio JSON). No live market-data calls are involved here or
in the orchestrator — the producing service is responsible for using a price
recent enough that the rebalance is meaningful.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .schema import CurrentPosition, OrderSide, Trade


@dataclass(frozen=True, slots=True)
class ResolvedTarget:
    """A target-portfolio entry with its IBKR conid resolved.

    `reference_price` carries through from `TargetPosition.reference_price`
    and is used for both share-count sizing here and post-trade slippage
    measurement downstream.
    """

    conid: int
    symbol: str
    exchange: str
    weight_pct: Decimal
    reference_price: Decimal


def compute_trades(
    *,
    current: list[CurrentPosition],
    targets: list[ResolvedTarget],
    nav: Decimal,
) -> list[Trade]:
    """Compute the whole-share trade set that moves current → target.

    Args:
        current: positions currently held in the IBKR account.
        targets: target positions with conids and reference_prices resolved.
        nav: total account net asset value (positions + cash).

    Returns:
        Trades sorted with sells first (to free cash), then buys, each group
        sorted by symbol for deterministic output. Trades with zero quantity
        are never emitted.

    Raises:
        ValueError: if nav <= 0, targets is empty, or any reference_price <= 0.
    """
    if nav <= 0:
        raise ValueError(f"nav must be positive, got {nav}")
    if not targets:
        raise ValueError("targets must not be empty")

    for t in targets:
        if t.reference_price <= 0:
            raise ValueError(
                f"reference_price for {t.symbol} (conid {t.conid}) must be positive, "
                f"got {t.reference_price}"
            )

    target_conids = {t.conid for t in targets}
    current_by_conid: dict[int, CurrentPosition] = {p.conid: p for p in current}

    trades: list[Trade] = []

    # (1) Positions held but not in target: trade the integer portion to zero.
    for conid, pos in current_by_conid.items():
        if conid in target_conids:
            continue
        whole = _trunc_to_int(pos.quantity)
        if whole == 0:
            continue
        # No reference_price for liquidations — the target doesn't list it.
        if whole > 0:
            trades.append(
                Trade(
                    conid=conid,
                    symbol=pos.symbol,
                    exchange="SMART",
                    side=OrderSide.SELL,
                    quantity=whole,
                    reason="liquidate: not in target",
                    reference_price=None,
                )
            )
        else:
            trades.append(
                Trade(
                    conid=conid,
                    symbol=pos.symbol,
                    exchange="SMART",
                    side=OrderSide.BUY,
                    quantity=-whole,
                    reason="cover short: not in target",
                    reference_price=None,
                )
            )

    # (2) Target positions: compute delta against integer portion of current.
    for t in targets:
        target_value = (t.weight_pct / Decimal("100")) * nav
        target_shares = int(target_value / t.reference_price)

        if t.conid in current_by_conid:
            current_whole = _trunc_to_int(current_by_conid[t.conid].quantity)
        else:
            current_whole = 0

        diff = target_shares - current_whole
        if diff == 0:
            continue
        if diff > 0:
            reason = "new position" if current_whole <= 0 else "rebalance up"
            trades.append(
                Trade(
                    conid=t.conid,
                    symbol=t.symbol,
                    exchange=t.exchange,
                    side=OrderSide.BUY,
                    quantity=diff,
                    reason=reason,
                    reference_price=t.reference_price,
                )
            )
        else:
            reason = "rebalance down" if current_whole > 0 else "deepen short"
            trades.append(
                Trade(
                    conid=t.conid,
                    symbol=t.symbol,
                    exchange=t.exchange,
                    side=OrderSide.SELL,
                    quantity=-diff,
                    reason=reason,
                    reference_price=t.reference_price,
                )
            )

    trades.sort(key=lambda t: (0 if t.side is OrderSide.SELL else 1, t.symbol))
    return trades


def _trunc_to_int(d: Decimal) -> int:
    """Truncate toward zero. 10.5 → 10, -10.5 → -10, 10.0 → 10."""
    return int(d)
