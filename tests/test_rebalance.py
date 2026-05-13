"""Tests for the diff engine.

This is the algorithmic core: a bug here silently moves real money the wrong
direction. We cover both example-based unit tests and property-based tests
with hypothesis, plus the explicit invariant that running the engine twice
in a row is idempotent (the second run produces no trades).
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from ibkr_portfolio_connect.rebalance import ResolvedTarget, _trunc_to_int, compute_trades
from ibkr_portfolio_connect.schema import CurrentPosition, OrderSide


def _pos(
    conid: int,
    symbol: str = "X",
    qty: str | Decimal = "0",
    mv: str | Decimal = "0",
) -> CurrentPosition:
    return CurrentPosition(
        conid=conid,
        symbol=symbol,
        asset_class="STK",
        quantity=Decimal(str(qty)),
        market_value=Decimal(str(mv)),
        currency="USD",
    )


def _target(
    conid: int, symbol: str = "X", exchange: str = "ARCA", weight: str = "10"
) -> ResolvedTarget:
    return ResolvedTarget(conid=conid, symbol=symbol, exchange=exchange, weight_pct=Decimal(weight))


# ---- explicit unit tests ---------------------------------------------------


class TestComputeTrades:
    def test_empty_current_buys_full_target(self) -> None:
        targets = [
            _target(1, "VTI", "ARCA", "60"),
            _target(2, "BND", "NASDAQ", "39.5"),
        ]
        # NAV = 10_000, price = 100 each
        trades = compute_trades(
            current=[],
            targets=targets,
            nav=Decimal("10000"),
            prices={1: Decimal("100"), 2: Decimal("100")},
        )
        assert len(trades) == 2
        assert all(t.side is OrderSide.BUY for t in trades)
        by_symbol = {t.symbol: t for t in trades}
        assert by_symbol["VTI"].quantity == 60  # 60% of 10000 / 100
        assert by_symbol["BND"].quantity == 39  # floor(3950/100) = 39

    def test_no_trades_when_aligned(self) -> None:
        targets = [_target(1, "VTI", "ARCA", "60")]
        current = [_pos(1, "VTI", qty="60", mv="6000")]
        trades = compute_trades(
            current=current,
            targets=targets,
            nav=Decimal("10000"),
            prices={1: Decimal("100")},
        )
        assert trades == []

    def test_sells_excess_when_overweight(self) -> None:
        targets = [_target(1, "VTI", "ARCA", "50")]
        current = [_pos(1, "VTI", qty="70", mv="7000")]
        # Target = 50% * 10_000 / 100 = 50 shares, currently 70 → SELL 20
        trades = compute_trades(
            current=current,
            targets=targets,
            nav=Decimal("10000"),
            prices={1: Decimal("100")},
        )
        assert len(trades) == 1
        assert trades[0].side is OrderSide.SELL
        assert trades[0].quantity == 20
        assert trades[0].reason == "rebalance down"

    def test_buys_to_top_up_underweight(self) -> None:
        targets = [_target(1, "VTI", "ARCA", "60")]
        current = [_pos(1, "VTI", qty="40", mv="4000")]
        trades = compute_trades(
            current=current,
            targets=targets,
            nav=Decimal("10000"),
            prices={1: Decimal("100")},
        )
        assert trades[0].side is OrderSide.BUY
        assert trades[0].quantity == 20
        assert trades[0].reason == "rebalance up"

    def test_liquidates_position_not_in_target(self) -> None:
        targets = [_target(1, "VTI", "ARCA", "99.5")]
        current = [
            _pos(2, "OLD", qty="5", mv="500"),
        ]
        trades = compute_trades(
            current=current,
            targets=targets,
            nav=Decimal("10000"),
            prices={1: Decimal("100")},
        )
        # Expect one SELL (OLD) and one BUY (VTI)
        assert len(trades) == 2
        sells = [t for t in trades if t.side is OrderSide.SELL]
        buys = [t for t in trades if t.side is OrderSide.BUY]
        assert len(sells) == 1
        assert sells[0].symbol == "OLD"
        assert sells[0].quantity == 5
        assert sells[0].reason == "liquidate: not in target"
        assert buys[0].symbol == "VTI"
        assert buys[0].quantity == 99  # floor(9950/100)

    def test_covers_short_not_in_target(self) -> None:
        targets = [_target(1, "VTI", "ARCA", "99.5")]
        current = [_pos(2, "SHRT", qty="-7", mv="-700")]
        trades = compute_trades(
            current=current,
            targets=targets,
            nav=Decimal("10000"),
            prices={1: Decimal("100")},
        )
        cover = next(t for t in trades if t.symbol == "SHRT")
        assert cover.side is OrderSide.BUY
        assert cover.quantity == 7
        assert cover.reason == "cover short: not in target"

    def test_zero_weight_target_sells_existing(self) -> None:
        # weight_pct=0 on a held position should sell to zero.
        targets = [_target(1, "VTI", "ARCA", "0"), _target(2, "BND", "NASDAQ", "99.5")]
        current = [_pos(1, "VTI", qty="10", mv="1000")]
        trades = compute_trades(
            current=current,
            targets=targets,
            nav=Decimal("10000"),
            prices={1: Decimal("100"), 2: Decimal("100")},
        )
        sell_vti = next(t for t in trades if t.symbol == "VTI")
        assert sell_vti.side is OrderSide.SELL
        assert sell_vti.quantity == 10
        assert sell_vti.reason == "rebalance down"

    def test_fractional_current_treats_integer_portion_as_held(self) -> None:
        # 10.5 shares held with target == 15 → BUY 5 (the .5 dust is ignored).
        targets = [_target(1, "VTI", "ARCA", "60")]
        current = [_pos(1, "VTI", qty="10.5", mv="1050")]
        trades = compute_trades(
            current=current,
            targets=targets,
            nav=Decimal("10000"),
            prices={1: Decimal("100")},
        )
        assert trades[0].side is OrderSide.BUY
        assert trades[0].quantity == 50  # 60 - 10

    def test_fractional_dust_only_position_skipped(self) -> None:
        # 0.25 shares of an unrelated symbol → can't sell fractional, skip.
        targets = [_target(1, "VTI", "ARCA", "99.5")]
        current = [_pos(2, "DUST", qty="0.25", mv="25")]
        trades = compute_trades(
            current=current,
            targets=targets,
            nav=Decimal("10000"),
            prices={1: Decimal("100")},
        )
        symbols = {t.symbol for t in trades}
        assert "DUST" not in symbols

    def test_trades_sorted_sells_first(self) -> None:
        targets = [_target(1, "AAA", "ARCA", "50"), _target(2, "ZZZ", "ARCA", "49.5")]
        current = [
            _pos(1, "AAA", qty="100", mv="10000"),  # need to SELL down
            _pos(3, "OUT", qty="5", mv="500"),  # need to SELL to liquidate
        ]
        trades = compute_trades(
            current=current,
            targets=targets,
            nav=Decimal("10000"),
            prices={1: Decimal("100"), 2: Decimal("100")},
        )
        # Sells come first, alphabetical within group.
        sides = [t.side for t in trades]
        assert sides == sorted(sides, key=lambda s: 0 if s is OrderSide.SELL else 1)
        sells = [t for t in trades if t.side is OrderSide.SELL]
        assert [t.symbol for t in sells] == sorted([t.symbol for t in sells])

    def test_no_zero_quantity_trades(self) -> None:
        # Target weight rounds to exactly the current whole share count.
        targets = [_target(1, "VTI", "ARCA", "10")]  # 10% of 10000 / 100 = 10 shares
        current = [_pos(1, "VTI", qty="10", mv="1000")]
        trades = compute_trades(
            current=current,
            targets=targets,
            nav=Decimal("10000"),
            prices={1: Decimal("100")},
        )
        assert trades == []

    def test_idempotent_after_one_run(self) -> None:
        """Running again with the post-trade state produces no further trades.

        This is the key invariant — once we've rebalanced, a second invocation
        with the same target should be a no-op (modulo fractional dust).
        """
        targets = [
            _target(1, "VTI", "ARCA", "60"),
            _target(2, "BND", "NASDAQ", "39.5"),
        ]
        prices = {1: Decimal("100"), 2: Decimal("100")}
        nav = Decimal("10000")
        trades = compute_trades(current=[], targets=targets, nav=nav, prices=prices)

        # Simulate execution: positions = the trades.
        new_positions = [
            CurrentPosition(
                conid=t.conid,
                symbol=t.symbol,
                asset_class="STK",
                quantity=Decimal(t.quantity),
                market_value=Decimal(t.quantity) * prices[t.conid],
                currency="USD",
            )
            for t in trades
        ]
        # Same NAV (cash spent = position value gained, ignoring fees).
        second_pass = compute_trades(current=new_positions, targets=targets, nav=nav, prices=prices)
        assert second_pass == []


# ---- error cases -----------------------------------------------------------


class TestComputeTradesErrors:
    def test_zero_nav(self) -> None:
        with pytest.raises(ValueError, match="nav must be positive"):
            compute_trades(
                current=[],
                targets=[_target(1)],
                nav=Decimal("0"),
                prices={1: Decimal("100")},
            )

    def test_negative_nav(self) -> None:
        with pytest.raises(ValueError, match="nav must be positive"):
            compute_trades(
                current=[],
                targets=[_target(1)],
                nav=Decimal("-1"),
                prices={1: Decimal("100")},
            )

    def test_empty_targets(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            compute_trades(current=[], targets=[], nav=Decimal("1000"), prices={})

    def test_missing_price(self) -> None:
        with pytest.raises(ValueError, match="missing price"):
            compute_trades(
                current=[],
                targets=[_target(1, "VTI", "ARCA", "99.5")],
                nav=Decimal("10000"),
                prices={},
            )

    def test_zero_price(self) -> None:
        with pytest.raises(ValueError, match="must be positive"):
            compute_trades(
                current=[],
                targets=[_target(1, "VTI", "ARCA", "99.5")],
                nav=Decimal("10000"),
                prices={1: Decimal("0")},
            )


# ---- property-based tests --------------------------------------------------


# Strategies for hypothesis: decimals constrained to financial-sensible ranges.
def _safe_decimal(lo: Decimal, hi: Decimal) -> st.SearchStrategy[Decimal]:
    return st.decimals(
        min_value=lo,
        max_value=hi,
        allow_nan=False,
        allow_infinity=False,
        places=2,
    )


@st.composite
def _scenario(
    draw: st.DrawFn,
) -> tuple[list[CurrentPosition], list[ResolvedTarget], Decimal, dict[int, Decimal]]:
    n_targets = draw(st.integers(min_value=1, max_value=8))
    nav = draw(_safe_decimal(Decimal("1000"), Decimal("10000000")))

    # Build targets with weights summing to <= 100 (the rebalancer permits a
    # cash buffer = 100 - sum_weights to remain in cash).
    raw_weights = draw(
        st.lists(
            _safe_decimal(Decimal("0"), Decimal("100")),
            min_size=n_targets,
            max_size=n_targets,
        )
    )
    total = sum(raw_weights, Decimal("0"))
    assume(total > 0)
    # Normalize to sum to at most 99 (leave at least 1% cash buffer).
    scale = Decimal("99") / total
    weights = [(w * scale).quantize(Decimal("0.01")) for w in raw_weights]

    targets: list[ResolvedTarget] = []
    prices: dict[int, Decimal] = {}
    for i, w in enumerate(weights):
        conid = 1000 + i
        price = draw(_safe_decimal(Decimal("1"), Decimal("5000")))
        targets.append(ResolvedTarget(conid=conid, symbol=f"S{i}", exchange="ARCA", weight_pct=w))
        prices[conid] = price

    # Currently-held positions: some target conids and some unrelated ones.
    current: list[CurrentPosition] = []
    n_held = draw(st.integers(min_value=0, max_value=n_targets + 2))
    used_conids: set[int] = set()
    for _ in range(n_held):
        # Either hold one of the target conids, or an unrelated one.
        if draw(st.booleans()):
            conid = draw(st.sampled_from([t.conid for t in targets]))
        else:
            conid = draw(st.integers(min_value=9000, max_value=9999))
        if conid in used_conids:
            continue
        used_conids.add(conid)
        qty = draw(_safe_decimal(Decimal("-100"), Decimal("100")))
        # Pick any plausible price for non-target conid
        price_for_mv = prices.get(conid) or draw(_safe_decimal(Decimal("1"), Decimal("5000")))
        current.append(
            CurrentPosition(
                conid=conid,
                symbol=f"H{conid}",
                asset_class="STK",
                quantity=qty,
                market_value=qty * price_for_mv,
                currency="USD",
            )
        )

    return current, targets, nav, prices


@given(scenario=_scenario())
@settings(max_examples=200, deadline=None)
def test_property_targets_end_at_target_shares(
    scenario: tuple[list[CurrentPosition], list[ResolvedTarget], Decimal, dict[int, Decimal]],
) -> None:
    """For every target conid, post-trade integer share count equals floor(weight*nav/price)."""
    current, targets, nav, prices = scenario
    trades = compute_trades(current=current, targets=targets, nav=nav, prices=prices)

    current_int: dict[int, int] = {p.conid: _trunc_to_int(p.quantity) for p in current}
    new_int = dict(current_int)
    for t in trades:
        delta = t.quantity if t.side is OrderSide.BUY else -t.quantity
        new_int[t.conid] = new_int.get(t.conid, 0) + delta

    for tgt in targets:
        expected = int((tgt.weight_pct / Decimal("100")) * nav / prices[tgt.conid])
        assert new_int.get(tgt.conid, 0) == expected, (
            f"{tgt.symbol}: expected {expected}, got {new_int.get(tgt.conid, 0)}"
        )


@given(scenario=_scenario())
@settings(max_examples=200, deadline=None)
def test_property_non_target_end_at_zero_whole(
    scenario: tuple[list[CurrentPosition], list[ResolvedTarget], Decimal, dict[int, Decimal]],
) -> None:
    """Positions not in the target end up at zero integer shares (dust may remain)."""
    current, targets, nav, prices = scenario
    trades = compute_trades(current=current, targets=targets, nav=nav, prices=prices)
    target_conids = {t.conid for t in targets}

    current_int = {p.conid: _trunc_to_int(p.quantity) for p in current}
    new_int = dict(current_int)
    for t in trades:
        delta = t.quantity if t.side is OrderSide.BUY else -t.quantity
        new_int[t.conid] = new_int.get(t.conid, 0) + delta

    for conid, qty in new_int.items():
        if conid in target_conids:
            continue
        assert qty == 0, f"non-target conid {conid} ended at {qty}, should be 0"


@given(scenario=_scenario())
@settings(max_examples=200, deadline=None)
def test_property_all_trade_quantities_positive(
    scenario: tuple[list[CurrentPosition], list[ResolvedTarget], Decimal, dict[int, Decimal]],
) -> None:
    """Trade.quantity is always a strictly positive integer."""
    current, targets, nav, prices = scenario
    trades = compute_trades(current=current, targets=targets, nav=nav, prices=prices)
    for t in trades:
        assert isinstance(t.quantity, int)
        assert t.quantity > 0


@given(scenario=_scenario())
@settings(max_examples=200, deadline=None)
def test_property_trades_sorted_sells_first(
    scenario: tuple[list[CurrentPosition], list[ResolvedTarget], Decimal, dict[int, Decimal]],
) -> None:
    current, targets, nav, prices = scenario
    trades = compute_trades(current=current, targets=targets, nav=nav, prices=prices)
    # All sells come before all buys.
    seen_buy = False
    for t in trades:
        if t.side is OrderSide.BUY:
            seen_buy = True
        elif seen_buy:
            pytest.fail(f"SELL after BUY in trade list: {trades}")


# ---- helper sanity ---------------------------------------------------------


@pytest.mark.parametrize(
    ("input_dec", "expected"),
    [
        ("0", 0),
        ("0.5", 0),
        ("-0.5", 0),
        ("10", 10),
        ("10.5", 10),
        ("10.99", 10),
        ("-10", -10),
        ("-10.5", -10),
        ("-10.99", -10),
    ],
)
def test_trunc_to_int(input_dec: str, expected: int) -> None:
    assert _trunc_to_int(Decimal(input_dec)) == expected
