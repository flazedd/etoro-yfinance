"""Tests for the slippage / cost attribution module."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from ibkr_portfolio_connect.cost import (
    RebalanceReport,
    build_report,
    save_report,
    serialize_report,
)
from ibkr_portfolio_connect.executor import ExecutionSummary, TradeResult
from ibkr_portfolio_connect.schema import OrderSide, Trade


def _trade(
    symbol: str = "VTI",
    side: OrderSide = OrderSide.BUY,
    quantity: int = 10,
    conid: int = 1,
    reference_price: Decimal | None = Decimal("100"),
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


def _result(
    trade: Trade,
    *,
    success: bool = True,
    fill_price: Decimal | None = None,
    commission: Decimal | None = None,
) -> TradeResult:
    return TradeResult(
        trade=trade,
        success=success,
        order_id="1",
        final_status="Filled" if success else "Rejected",
        fill_price=fill_price,
        commission=commission,
    )


class TestComputeCostSignConvention:
    def test_buy_above_reference_is_cost(self) -> None:
        # Bought 10 VTI at $101 vs $100 ref → paid $10 more
        trade = _trade(side=OrderSide.BUY, quantity=10, reference_price=Decimal("100"))
        summary = ExecutionSummary(results=[_result(trade, fill_price=Decimal("101"))])
        report = build_report(summary, nav=Decimal("10000"))
        cost = report.trades[0]
        assert cost.slippage_dollars == Decimal("10")  # +ve = cost
        assert cost.slippage_pct == Decimal("1")

    def test_buy_below_reference_is_savings(self) -> None:
        trade = _trade(side=OrderSide.BUY, quantity=10, reference_price=Decimal("100"))
        summary = ExecutionSummary(results=[_result(trade, fill_price=Decimal("99.50"))])
        report = build_report(summary, nav=Decimal("10000"))
        cost = report.trades[0]
        assert cost.slippage_dollars == Decimal("-5.00")  # -ve = savings
        assert cost.slippage_pct == Decimal("-0.50")

    def test_sell_below_reference_is_cost(self) -> None:
        # Sold 10 VTI at $99 vs $100 ref → received $10 less
        trade = _trade(side=OrderSide.SELL, quantity=10, reference_price=Decimal("100"))
        summary = ExecutionSummary(results=[_result(trade, fill_price=Decimal("99"))])
        report = build_report(summary, nav=Decimal("10000"))
        cost = report.trades[0]
        assert cost.slippage_dollars == Decimal("10")
        assert cost.slippage_pct == Decimal("1")

    def test_sell_above_reference_is_savings(self) -> None:
        trade = _trade(side=OrderSide.SELL, quantity=10, reference_price=Decimal("100"))
        summary = ExecutionSummary(results=[_result(trade, fill_price=Decimal("101"))])
        report = build_report(summary, nav=Decimal("10000"))
        cost = report.trades[0]
        assert cost.slippage_dollars == Decimal("-10")
        assert cost.slippage_pct == Decimal("-1")


class TestComputeCostMissingData:
    def test_no_reference_price_yields_none_slippage(self) -> None:
        # Liquidation trade — no reference price
        trade = _trade(reference_price=None)
        summary = ExecutionSummary(results=[_result(trade, fill_price=Decimal("99"))])
        report = build_report(summary, nav=Decimal("10000"))
        cost = report.trades[0]
        assert cost.slippage_pct is None
        assert cost.slippage_dollars is None
        assert cost.fill_price == Decimal("99")  # still surfaced

    def test_no_fill_price_yields_none_slippage(self) -> None:
        trade = _trade(reference_price=Decimal("100"))
        summary = ExecutionSummary(results=[_result(trade, fill_price=None)])
        report = build_report(summary, nav=Decimal("10000"))
        cost = report.trades[0]
        assert cost.slippage_pct is None
        assert cost.slippage_dollars is None

    def test_failed_trade_carries_no_slippage(self) -> None:
        trade = _trade(reference_price=Decimal("100"))
        summary = ExecutionSummary(results=[_result(trade, success=False)])
        report = build_report(summary, nav=Decimal("10000"))
        assert report.n_failed == 1
        assert report.trades[0].slippage_dollars is None


class TestPortfolioAggregates:
    def test_total_slippage_sums_signed(self) -> None:
        # Two trades: +$10 cost on VTI, -$3 savings on BND → net +$7
        vti = _trade("VTI", quantity=10, conid=1, reference_price=Decimal("100"))
        bnd = _trade("BND", quantity=3, conid=2, reference_price=Decimal("100"))
        summary = ExecutionSummary(
            results=[
                _result(vti, fill_price=Decimal("101")),  # +$10
                _result(bnd, fill_price=Decimal("99")),  # -$3
            ]
        )
        report = build_report(summary, nav=Decimal("10000"))
        assert report.total_slippage_dollars == Decimal("7")

    def test_total_commission_sums(self) -> None:
        vti = _trade("VTI", reference_price=Decimal("100"))
        bnd = _trade("BND", conid=2, reference_price=Decimal("100"))
        summary = ExecutionSummary(
            results=[
                _result(vti, fill_price=Decimal("100"), commission=Decimal("0.35")),
                _result(bnd, fill_price=Decimal("100"), commission=Decimal("0.20")),
            ]
        )
        report = build_report(summary, nav=Decimal("10000"))
        assert report.total_commission_dollars == Decimal("0.55")

    def test_total_cost_pct_of_nav(self) -> None:
        vti = _trade("VTI", quantity=10, reference_price=Decimal("100"))
        # $10 slippage + $0.50 commission = $10.50 on $10000 NAV = 0.105%
        summary = ExecutionSummary(
            results=[
                _result(vti, fill_price=Decimal("101"), commission=Decimal("0.50")),
            ]
        )
        report = build_report(summary, nav=Decimal("10000"))
        assert report.total_cost_dollars == Decimal("10.50")
        assert report.total_cost_pct_of_nav == Decimal("0.105")

    def test_zero_nav_returns_zero_pct(self) -> None:
        report = RebalanceReport(nav=Decimal("0"), trades=[])
        assert report.total_cost_pct_of_nav == Decimal("0")

    def test_dry_run_flag_passes_through(self) -> None:
        summary = ExecutionSummary(results=[], dry_run=True)
        report = build_report(summary, nav=Decimal("10000"))
        assert report.dry_run is True


class TestSlippagePctScaling:
    def test_buy_5pct_above(self) -> None:
        trade = _trade(side=OrderSide.BUY, quantity=1, reference_price=Decimal("100"))
        summary = ExecutionSummary(results=[_result(trade, fill_price=Decimal("105"))])
        report = build_report(summary, nav=Decimal("10000"))
        assert report.trades[0].slippage_pct == Decimal("5")


class TestPersistence:
    def test_serialize_round_trip(self) -> None:
        vti = _trade("VTI", quantity=10, reference_price=Decimal("100.50"))
        summary = ExecutionSummary(
            results=[
                _result(
                    vti,
                    success=True,
                    fill_price=Decimal("100.75"),
                    commission=Decimal("0.35"),
                )
            ]
        )
        report = build_report(summary, nav=Decimal("10000"))
        blob = serialize_report(report)
        # Round-trips through JSON without loss
        parsed = json.loads(json.dumps(blob))
        assert parsed["nav"] == "10000"
        assert parsed["overall_success"] is True
        assert parsed["trades"][0]["symbol"] == "VTI"
        assert parsed["trades"][0]["fill_price"] == "100.75"
        assert parsed["trades"][0]["reference_price"] == "100.50"

    def test_serialize_handles_none_values(self) -> None:
        # Failed trade — no fill price, no commission, no slippage
        vti = _trade("VTI", reference_price=Decimal("100"))
        summary = ExecutionSummary(results=[_result(vti, success=False)])
        blob = serialize_report(build_report(summary, nav=Decimal("10000")))
        t = blob["trades"][0]
        assert t["fill_price"] is None
        assert t["commission"] is None
        assert t["slippage_pct"] is None

    def test_save_writes_json_to_dir(self, tmp_path: Path) -> None:
        vti = _trade("VTI", quantity=5, reference_price=Decimal("100"))
        summary = ExecutionSummary(results=[_result(vti, success=True, fill_price=Decimal("100"))])
        report = build_report(summary, nav=Decimal("10000"))
        ts = datetime(2026, 5, 18, 14, 30, 0, tzinfo=UTC)
        path = save_report(report, report_dir=tmp_path, now=ts)
        assert path.name == "20260518-143000.json"
        assert path.parent == tmp_path
        loaded = json.loads(path.read_text())
        assert loaded["nav"] == "10000"
        assert loaded["trades"][0]["symbol"] == "VTI"

    def test_save_creates_missing_dir(self, tmp_path: Path) -> None:
        report = RebalanceReport(nav=Decimal("100"), trades=[])
        target = tmp_path / "deeper" / "still-deeper"
        path = save_report(report, report_dir=target)
        assert path.parent == target
        assert target.is_dir()
