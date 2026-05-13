"""Tests for the ntfy.sh notifier."""

from __future__ import annotations

import logging
from typing import Any

import httpx
import pytest

from ibkr_portfolio_connect.executor import ExecutionSummary, TradeResult
from ibkr_portfolio_connect.notify import (
    LogOnlyNotifier,
    NtfyNotifier,
    _format,
    build_notifier,
)
from ibkr_portfolio_connect.schema import OrderSide, Trade


def _trade(symbol: str = "VTI", side: OrderSide = OrderSide.BUY, qty: int = 5) -> Trade:
    return Trade(conid=1, symbol=symbol, exchange="ARCA", side=side, quantity=qty, reason="test")


def _summary_ok() -> ExecutionSummary:
    return ExecutionSummary(
        results=[
            TradeResult(trade=_trade("VTI"), success=True, order_id="1", final_status="Filled"),
            TradeResult(
                trade=_trade("BND", qty=2), success=True, order_id="2", final_status="Filled"
            ),
        ],
        dry_run=False,
    )


def _summary_partial_fail() -> ExecutionSummary:
    return ExecutionSummary(
        results=[
            TradeResult(trade=_trade("VTI"), success=True, order_id="1", final_status="Filled"),
            TradeResult(
                trade=_trade("BND", side=OrderSide.SELL, qty=2),
                success=False,
                final_status="Rejected",
                error="no permissions",
            ),
        ],
        dry_run=False,
    )


def _summary_dry() -> ExecutionSummary:
    return ExecutionSummary(
        results=[
            TradeResult(trade=_trade("VTI"), success=True, final_status="DRY_RUN"),
        ],
        dry_run=True,
    )


# ---- _format --------------------------------------------------------------


class TestFormat:
    def test_ok_summary(self) -> None:
        title, body = _format(_summary_ok())
        assert "OK" in title
        assert "2/2" in title
        assert "BUY 5 VTI" in body
        assert "BUY 2 BND" in body

    def test_failure_summary(self) -> None:
        title, body = _format(_summary_partial_fail())
        assert "FAILED" in title
        assert "no permissions" in body
        assert "Rejected" in body

    def test_dry_run_title(self) -> None:
        title, body = _format(_summary_dry())
        assert "DRY RUN" in title
        assert "BUY 5 VTI" in body

    def test_empty(self) -> None:
        title, body = _format(ExecutionSummary(results=[], dry_run=False))
        assert "0/0" in title
        assert body == "(no trades)"


# ---- LogOnlyNotifier ------------------------------------------------------


def test_log_only_notifier_logs(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="ibkr_portfolio_connect.notify"):
        LogOnlyNotifier().notify(_summary_ok())
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
        ).notify(_summary_ok())

        assert captured["url"] == "https://ntfy.example/my-topic"
        assert "BUY 5 VTI" in captured["body"]
        assert captured["headers"]["title"].startswith("ibkr-rebalance: OK")
        assert captured["headers"]["priority"] == "default"
        assert captured["headers"]["tags"] == "white_check_mark"

    def test_sends_high_priority_on_failure(self) -> None:
        captured: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["headers"] = dict(request.headers)
            return httpx.Response(200)

        NtfyNotifier(
            "t",
            transport=httpx.MockTransport(handler),
        ).notify(_summary_partial_fail())
        assert captured["headers"]["priority"] == "high"
        assert captured["headers"]["tags"] == "warning"

    def test_swallows_http_error(self, caplog: pytest.LogCaptureFixture) -> None:
        def handler(_r: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("ntfy down")

        with caplog.at_level(logging.WARNING, logger="ibkr_portfolio_connect.notify"):
            NtfyNotifier("t", transport=httpx.MockTransport(handler)).notify(_summary_ok())
        assert any("ntfy push error" in r.message for r in caplog.records)

    def test_swallows_500_response(self, caplog: pytest.LogCaptureFixture) -> None:
        def handler(_r: httpx.Request) -> httpx.Response:
            return httpx.Response(500, text="broken")

        with caplog.at_level(logging.WARNING, logger="ibkr_portfolio_connect.notify"):
            NtfyNotifier("t", transport=httpx.MockTransport(handler)).notify(_summary_ok())
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
