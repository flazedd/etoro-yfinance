"""Send a fake rebalancer push notification to ntfy.sh to verify setup.

Builds a synthetic RebalanceReport (mix of success + failure trades, with
sample fill prices + slippage) and sends it through the real NtfyNotifier.
Useful for confirming the topic is working — and that the cost summary line
renders sensibly — before relying on the monthly cron.

    uv run python scripts/test_ntfy.py <topic-name>
    uv run python scripts/test_ntfy.py <topic-name> --dry-run
    uv run python scripts/test_ntfy.py <topic-name> --all-fail
"""

from __future__ import annotations

import sys
from decimal import Decimal

from ibkr_portfolio_connect.cost import RebalanceReport, TradeCost
from ibkr_portfolio_connect.notify import NtfyNotifier
from ibkr_portfolio_connect.schema import OrderSide, Trade


def _trade(symbol: str, qty: int, side: OrderSide, conid: int) -> Trade:
    return Trade(
        conid=conid,
        symbol=symbol,
        exchange="SMART",
        side=side,
        quantity=qty,
        reason="ntfy connectivity test",
        reference_price=Decimal("100"),
    )


def _filled_cost(
    trade: Trade,
    *,
    fill_price: Decimal,
    slippage_pct: Decimal,
    commission: Decimal = Decimal("0.35"),
) -> TradeCost:
    slippage_dollars = (fill_price - trade.reference_price) * Decimal(trade.quantity)  # type: ignore[operator]
    if trade.side is OrderSide.SELL:
        slippage_dollars = -slippage_dollars
    return TradeCost(
        trade=trade,
        success=True,
        fill_price=fill_price,
        commission=commission,
        slippage_pct=slippage_pct,
        slippage_dollars=slippage_dollars,
        final_status="Filled",
    )


def _failed_cost(trade: Trade, *, error: str, status: str = "Rejected") -> TradeCost:
    return TradeCost(
        trade=trade,
        success=False,
        fill_price=None,
        commission=None,
        slippage_pct=None,
        slippage_dollars=None,
        final_status=status,
        error=error,
    )


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: test_ntfy.py <topic> [--dry-run|--all-fail]", file=sys.stderr)
        return 2

    topic = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "--mixed"

    voo = _trade("VOO", 5, OrderSide.BUY, conid=10000001)
    bnd = _trade("BND", 3, OrderSide.SELL, conid=10000002)
    nav = Decimal("10000")

    if mode == "--dry-run":
        report = RebalanceReport(
            nav=nav,
            dry_run=True,
            trades=[
                TradeCost(
                    trade=voo,
                    success=True,
                    fill_price=None,
                    commission=None,
                    slippage_pct=None,
                    slippage_dollars=None,
                    final_status="DRY_RUN",
                ),
                TradeCost(
                    trade=bnd,
                    success=True,
                    fill_price=None,
                    commission=None,
                    slippage_pct=None,
                    slippage_dollars=None,
                    final_status="DRY_RUN",
                ),
            ],
        )
    elif mode == "--all-fail":
        report = RebalanceReport(
            nav=nav,
            trades=[
                _failed_cost(voo, error="order rejected: insufficient buying power"),
                _failed_cost(bnd, error="exchange closed"),
            ],
        )
    else:
        report = RebalanceReport(
            nav=nav,
            trades=[
                _filled_cost(
                    voo,
                    fill_price=Decimal("100.30"),
                    slippage_pct=Decimal("0.30"),
                ),
                _failed_cost(bnd, error="contract not tradable"),
            ],
        )

    NtfyNotifier(topic).notify(report)
    print(f"sent {mode} push to https://ntfy.sh/{topic}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
