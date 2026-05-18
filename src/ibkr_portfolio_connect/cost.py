"""Slippage attribution: turn ExecutionSummary + NAV into a RebalanceReport.

For every trade we compare the fill price (from IBKR's order_status) against
the upstream reference_price (carried on Trade). Slippage is signed so the
sum is meaningful as a portfolio-level cost.

Sign convention:
  - BUY: positive slippage if fill_price > reference_price (paid more = cost)
  - SELL: positive slippage if fill_price < reference_price (received less = cost)

slippage_pct and slippage_dollars are None when the trade lacks either a
reference_price (liquidations of non-target positions) or a fill_price
(orders that didn't fill, or where IBKR didn't surface avg_price).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from .executor import ExecutionSummary, TradeResult
from .schema import OrderSide, Trade


@dataclass(frozen=True, slots=True)
class TradeCost:
    trade: Trade
    success: bool
    fill_price: Decimal | None
    commission: Decimal | None
    slippage_pct: Decimal | None
    slippage_dollars: Decimal | None
    final_status: str | None = None
    error: str | None = None

    @property
    def label(self) -> str:
        return f"{self.trade.side.value} {self.trade.quantity} {self.trade.symbol}"


@dataclass(frozen=True, slots=True)
class RebalanceReport:
    nav: Decimal
    trades: list[TradeCost]
    dry_run: bool = False
    aborted_reason: str | None = None
    """Set when a pre-trade safety check aborted the run before execution.
    When non-None, `trades` is empty and `overall_success` is False."""

    @property
    def n_total(self) -> int:
        return len(self.trades)

    @property
    def n_successful(self) -> int:
        return sum(1 for c in self.trades if c.success)

    @property
    def n_failed(self) -> int:
        return sum(1 for c in self.trades if not c.success)

    @property
    def overall_success(self) -> bool:
        return self.aborted_reason is None and self.n_failed == 0

    @property
    def total_slippage_dollars(self) -> Decimal:
        """Sum of per-trade signed slippage. None values count as 0."""
        return sum(
            (c.slippage_dollars for c in self.trades if c.slippage_dollars is not None),
            start=Decimal("0"),
        )

    @property
    def total_commission_dollars(self) -> Decimal:
        return sum(
            (c.commission for c in self.trades if c.commission is not None),
            start=Decimal("0"),
        )

    @property
    def total_cost_dollars(self) -> Decimal:
        return self.total_slippage_dollars + self.total_commission_dollars

    @property
    def total_cost_pct_of_nav(self) -> Decimal:
        """Total rebalancing cost as % of account NAV. The headline number."""
        if self.nav <= 0:
            return Decimal("0")
        return (self.total_cost_dollars / self.nav) * Decimal("100")


def build_report(summary: ExecutionSummary, *, nav: Decimal) -> RebalanceReport:
    """Compute slippage attribution from execution results.

    `nav` is the account net liquidation value used to scale total_cost_pct.
    """
    costs = [_compute_cost(r) for r in summary.results]
    return RebalanceReport(nav=nav, trades=costs, dry_run=summary.dry_run)


def _compute_cost(result: TradeResult) -> TradeCost:
    trade = result.trade
    ref = trade.reference_price
    fill = result.fill_price

    slippage_pct: Decimal | None = None
    slippage_dollars: Decimal | None = None

    if ref is not None and ref > 0 and fill is not None and fill > 0:
        # Per-share difference, normalized so that positive = cost regardless
        # of trade side.
        diff = fill - ref
        if trade.side is OrderSide.SELL:
            diff = -diff
        slippage_pct = (diff / ref) * Decimal("100")
        slippage_dollars = diff * Decimal(trade.quantity)

    return TradeCost(
        trade=trade,
        success=result.success,
        fill_price=fill,
        commission=result.commission,
        slippage_pct=slippage_pct,
        slippage_dollars=slippage_dollars,
        final_status=result.final_status,
        error=result.error,
    )


# ----- persistence ---------------------------------------------------------


def serialize_report(report: RebalanceReport) -> dict[str, Any]:
    """Convert a RebalanceReport to a JSON-safe dict.

    All Decimal values are stringified to preserve precision through the
    round-trip; consumers should parse back to Decimal where needed.
    """
    return {
        "nav": str(report.nav),
        "dry_run": report.dry_run,
        "aborted_reason": report.aborted_reason,
        "n_total": report.n_total,
        "n_successful": report.n_successful,
        "n_failed": report.n_failed,
        "overall_success": report.overall_success,
        "total_slippage_dollars": str(report.total_slippage_dollars),
        "total_commission_dollars": str(report.total_commission_dollars),
        "total_cost_dollars": str(report.total_cost_dollars),
        "total_cost_pct_of_nav": str(report.total_cost_pct_of_nav),
        "trades": [_serialize_trade_cost(c) for c in report.trades],
    }


def _serialize_trade_cost(c: TradeCost) -> dict[str, Any]:
    return {
        "symbol": c.trade.symbol,
        "side": c.trade.side.value,
        "quantity": c.trade.quantity,
        "conid": c.trade.conid,
        "exchange": c.trade.exchange,
        "reason": c.trade.reason,
        "reference_price": _opt_str(c.trade.reference_price),
        "success": c.success,
        "final_status": c.final_status,
        "error": c.error,
        "fill_price": _opt_str(c.fill_price),
        "commission": _opt_str(c.commission),
        "slippage_pct": _opt_str(c.slippage_pct),
        "slippage_dollars": _opt_str(c.slippage_dollars),
    }


def _opt_str(d: Decimal | None) -> str | None:
    return str(d) if d is not None else None


def save_report(
    report: RebalanceReport,
    *,
    report_dir: Path,
    now: datetime | None = None,
) -> Path:
    """Serialize report to {report_dir}/{YYYYmmdd-HHMMSS}.json.

    Creates report_dir (and parents) if missing. Returns the path written.
    """
    now = now or datetime.now(UTC)
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{now.strftime('%Y%m%d-%H%M%S')}.json"
    path.write_text(json.dumps(serialize_report(report), indent=2))
    return path
