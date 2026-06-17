"""Tests for the ntfy.sh notifier."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

import httpx
import pytest

from ibkr_portfolio_connect.cost import RebalanceReport, TradeCost
from ibkr_portfolio_connect.notify import (
    LogOnlyNotifier,
    NtfyNotifier,
    _format,
    build_notifier,
)
from ibkr_portfolio_connect.schema import OrderSide, Trade


def _trade(
    symbol: str = "VTI",
    side: OrderSide = OrderSide.BUY,
    qty: int = 5,
    reference_price: Decimal | None = Decimal("100"),
) -> Trade:
    return Trade(
        conid=1,
        symbol=symbol,
        exchange="ARCA",
        side=side,
        quantity=qty,
        reason="test",
        reference_price=reference_price,
    )


def _cost(
    trade: Trade,
    *,
    success: bool = True,
    fill_price: Decimal | None = None,
    slippage_pct: Decimal | None = None,
    slippage_dollars: Decimal | None = None,
    commission: Decimal | None = None,
    final_status: str | None = None,
    error: str | None = None,
) -> TradeCost:
    return TradeCost(
        trade=trade,
        success=success,
        fill_price=fill_price,
        commission=commission,
        slippage_pct=slippage_pct,
        slippage_dollars=slippage_dollars,
        final_status=final_status,
        error=error,
    )


def _report_ok() -> RebalanceReport:
    return RebalanceReport(
        nav=Decimal("10000"),
        trades=[
            _cost(
                _trade("VTI"),
                success=True,
                fill_price=Decimal("100.50"),
                slippage_pct=Decimal("0.50"),
                slippage_dollars=Decimal("2.50"),
                commission=Decimal("0.35"),
                final_status="Filled",
            ),
            _cost(
                _trade("BND", qty=2),
                success=True,
                fill_price=Decimal("100"),
                slippage_pct=Decimal("0"),
                slippage_dollars=Decimal("0"),
                commission=Decimal("0.35"),
                final_status="Filled",
            ),
        ],
    )


def _report_partial_fail() -> RebalanceReport:
    return RebalanceReport(
        nav=Decimal("10000"),
        trades=[
            _cost(
                _trade("VTI"),
                success=True,
                fill_price=Decimal("100"),
                slippage_pct=Decimal("0"),
                slippage_dollars=Decimal("0"),
                commission=Decimal("0.35"),
                final_status="Filled",
            ),
            _cost(
                _trade("BND", side=OrderSide.SELL, qty=2),
                success=False,
                final_status="Rejected",
                error="no permissions",
            ),
        ],
    )


def _report_dry() -> RebalanceReport:
    return RebalanceReport(
        nav=Decimal("10000"),
        dry_run=True,
        trades=[
            _cost(_trade("VTI"), success=True, final_status="DRY_RUN"),
        ],
    )


# ---- _format --------------------------------------------------------------


class TestFormat:
    def test_ok_summary(self) -> None:
        title, body = _format(_report_ok())
        assert "OK" in title
        assert "2/2" in title
        assert "cost" in title  # cost percentage shown
        assert "BUY 5 VTI" in body
        assert "BUY 2 BND" in body
        assert "@ 100.50" in body
        assert "+0.50%" in body
        assert "total:" in body

    def test_failure_summary(self) -> None:
        title, body = _format(_report_partial_fail())
        assert "FAILED" in title
        assert "no permissions" in body
        assert "Rejected" in body

    def test_dry_run_title(self) -> None:
        title, body = _format(_report_dry())
        assert "DRY RUN" in title
        assert "BUY 5 VTI" in body
        # No totals line in dry-run mode
        assert "total:" not in body

    def test_empty(self) -> None:
        title, body = _format(RebalanceReport(nav=Decimal("10000"), trades=[]))
        assert "0/0" in title
        assert body == "(no trades)"


# ---- LogOnlyNotifier ------------------------------------------------------


def test_log_only_notifier_logs(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="ibkr_portfolio_connect.notify"):
        LogOnlyNotifier().notify(_report_ok())
    assert any("OK" in r.message for r in caplog.records)


# ---- NtfyNotifier ---------------------------------------------------------


class TestNtfyNotifier:
    def test_sends_post_with_headers_on_success(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["body"] = request.content.decode("utf-8")
            captured["headers"] = dict(request.headers)
            return httpx.Response(200)

        NtfyNotifier(
            "my-topic",
            server="https://ntfy.example",
            transport=httpx.MockTransport(handler),
        ).notify(_report_ok())

        assert captured["url"] == "https://ntfy.example/my-topic"
        assert "BUY 5 VTI" in captured["body"]
        assert captured["headers"]["title"].startswith("ibkr-rebalance: OK")
        assert captured["headers"]["priority"] == "default"
        assert captured["headers"]["tags"] == "white_check_mark"

    def test_event_sends_freeform_push(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["body"] = request.content.decode("utf-8")
            captured["headers"] = dict(request.headers)
            return httpx.Response(200)

        NtfyNotifier("t", transport=httpx.MockTransport(handler)).event(
            "ibkr-rebalance: run started", "dry_run=False", priority="high"
        )
        assert captured["body"] == "dry_run=False"
        assert captured["headers"]["title"] == "ibkr-rebalance: run started"
        assert captured["headers"]["priority"] == "high"
        assert captured["headers"]["tags"] == "rotating_light"

    def test_sends_high_priority_on_failure(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["headers"] = dict(request.headers)
            return httpx.Response(200)

        NtfyNotifier(
            "t",
            transport=httpx.MockTransport(handler),
        ).notify(_report_partial_fail())
        assert captured["headers"]["priority"] == "high"
        assert captured["headers"]["tags"] == "warning"

    def test_swallows_http_error(self, caplog: pytest.LogCaptureFixture) -> None:
        def handler(_r: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("ntfy down")

        with caplog.at_level(logging.WARNING, logger="ibkr_portfolio_connect.notify"):
            NtfyNotifier("t", transport=httpx.MockTransport(handler)).notify(_report_ok())
        assert any("ntfy push error" in r.message for r in caplog.records)

    def test_swallows_500_response(self, caplog: pytest.LogCaptureFixture) -> None:
        def handler(_r: httpx.Request) -> httpx.Response:
            return httpx.Response(500, text="broken")

        with caplog.at_level(logging.WARNING, logger="ibkr_portfolio_connect.notify"):
            NtfyNotifier("t", transport=httpx.MockTransport(handler)).notify(_report_ok())
        assert any("ntfy push failed" in r.message for r in caplog.records)


# ---- build_notifier -------------------------------------------------------


class TestBuildNotifier:
    def test_returns_log_only_when_topic_missing(self) -> None:
        assert isinstance(build_notifier(ntfy_topic=None), LogOnlyNotifier)

    def test_returns_log_only_when_topic_empty(self) -> None:
        assert isinstance(build_notifier(ntfy_topic=""), LogOnlyNotifier)

    def test_returns_ntfy_notifier_when_topic_present(self) -> None:
        n = build_notifier(ntfy_topic="my-topic")
        assert isinstance(n, NtfyNotifier)
