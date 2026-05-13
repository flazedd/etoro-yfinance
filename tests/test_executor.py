"""Tests for the order executor.

We mock IBKRClient at the method level (not via HTTP) so we can drive
the reply chain and status polling deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo

import pytest

from ibkr_portfolio_connect.executor import (
    NotInTradingHoursError,
    execute_trades,
    is_rth,
)
from ibkr_portfolio_connect.ibkr_client import IBKRError, PlaceOrderReply
from ibkr_portfolio_connect.schema import OrderSide, Trade

NY = ZoneInfo("America/New_York")


# ---- fake client -----------------------------------------------------------


@dataclass
class FakeClient:
    """Captures calls and lets each test scripted responses."""

    place_responses: list[list[dict[str, Any]]] = field(default_factory=list)
    confirm_responses: list[list[dict[str, Any]]] = field(default_factory=list)
    status_responses: list[dict[str, Any]] = field(default_factory=list)

    place_calls: list[dict[str, Any]] = field(default_factory=list)
    confirm_calls: list[dict[str, Any]] = field(default_factory=list)
    status_calls: list[str] = field(default_factory=list)

    def place_market_day_order(
        self,
        account_id: str,
        *,
        conid: int,
        side: OrderSide,
        quantity: int,
        listing_exchange: str | None = None,
    ) -> list[PlaceOrderReply]:
        self.place_calls.append(
            {
                "account_id": account_id,
                "conid": conid,
                "side": side,
                "quantity": quantity,
            }
        )
        if not self.place_responses:
            raise IBKRError("test: no scripted place response")
        return [PlaceOrderReply.model_validate(x) for x in self.place_responses.pop(0)]

    def confirm_reply(self, reply_id: str, *, confirmed: bool = True) -> list[PlaceOrderReply]:
        self.confirm_calls.append({"reply_id": reply_id, "confirmed": confirmed})
        if not self.confirm_responses:
            raise IBKRError("test: no scripted confirm response")
        return [PlaceOrderReply.model_validate(x) for x in self.confirm_responses.pop(0)]

    def order_status(self, order_id: str) -> dict[str, Any]:
        self.status_calls.append(order_id)
        if not self.status_responses:
            return {"order_status": "Filled"}  # default end state
        return self.status_responses.pop(0)


def _trade(
    symbol: str = "VTI",
    side: OrderSide = OrderSide.BUY,
    quantity: int = 10,
    conid: int = 100,
    exchange: str = "ARCA",
    reason: str = "test",
) -> Trade:
    return Trade(
        conid=conid,
        symbol=symbol,
        exchange=exchange,
        side=side,
        quantity=quantity,
        reason=reason,
    )


# ---- fake clock/sleep helpers ---------------------------------------------


class FakeClock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


class FakeSleeper:
    def __init__(self, clock: FakeClock) -> None:
        self.clock = clock
        self.calls: list[float] = []

    def __call__(self, secs: float) -> None:
        self.calls.append(secs)
        self.clock.t += secs


def in_rth_now() -> datetime:
    # A Tuesday at 10:30am NY
    return datetime(2026, 5, 12, 10, 30, tzinfo=NY)


# ---- dry-run --------------------------------------------------------------


class TestDryRun:
    def test_dry_run_produces_no_client_calls(self) -> None:
        client = FakeClient()
        trades = [_trade("VTI"), _trade("BND", quantity=5)]
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            trades,
            dry_run=True,
            enforce_rth=False,
        )
        assert summary.dry_run is True
        assert summary.n_total == 2
        assert summary.n_successful == 2
        assert all(r.final_status == "DRY_RUN" for r in summary.results)
        assert client.place_calls == []

    def test_dry_run_ignores_trading_hours(self) -> None:
        client = FakeClient()
        # Saturday — RTH would refuse
        sat = datetime(2026, 5, 9, 12, 0, tzinfo=NY)
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            [_trade()],
            dry_run=True,
            enforce_rth=True,
            now=lambda: sat,
        )
        assert summary.dry_run is True
        assert summary.overall_success is True


# ---- happy path -----------------------------------------------------------


class TestHappyPath:
    def test_single_trade_immediate_fill(self) -> None:
        client = FakeClient(
            place_responses=[[{"order_id": "111", "order_status": "Submitted"}]],
            status_responses=[{"order_status": "Filled"}],
        )
        clock = FakeClock()
        sleeper = FakeSleeper(clock)
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            [_trade("VTI", quantity=5)],
            enforce_rth=False,
            clock=clock,
            sleeper=sleeper,
            now=in_rth_now,
        )
        assert summary.overall_success
        result = summary.results[0]
        assert result.order_id == "111"
        assert result.final_status == "Filled"
        assert client.place_calls[0]["quantity"] == 5

    def test_reply_required_then_filled(self) -> None:
        client = FakeClient(
            place_responses=[[{"id": "abc", "message": ["please confirm"]}]],
            confirm_responses=[[{"order_id": "111", "order_status": "Submitted"}]],
            status_responses=[{"order_status": "Filled"}],
        )
        clock = FakeClock()
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            [_trade()],
            enforce_rth=False,
            clock=clock,
            sleeper=FakeSleeper(clock),
            now=in_rth_now,
        )
        assert summary.overall_success
        assert client.confirm_calls == [{"reply_id": "abc", "confirmed": True}]

    def test_double_reply_chain(self) -> None:
        client = FakeClient(
            place_responses=[[{"id": "abc", "message": ["confirm 1"]}]],
            confirm_responses=[
                [{"id": "def", "message": ["confirm 2"]}],
                [{"order_id": "222", "order_status": "Submitted"}],
            ],
            status_responses=[{"order_status": "Filled"}],
        )
        clock = FakeClock()
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            [_trade()],
            enforce_rth=False,
            clock=clock,
            sleeper=FakeSleeper(clock),
            now=in_rth_now,
        )
        assert summary.overall_success
        assert [c["reply_id"] for c in client.confirm_calls] == ["abc", "def"]


# ---- error paths ----------------------------------------------------------


class TestErrors:
    def test_place_returns_200_error(self) -> None:
        client = FakeClient(place_responses=[[{"error": "Insufficient funds"}]])
        clock = FakeClock()
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            [_trade()],
            enforce_rth=False,
            clock=clock,
            sleeper=FakeSleeper(clock),
            now=in_rth_now,
        )
        result = summary.results[0]
        assert result.success is False
        assert result.error == "Insufficient funds"
        assert summary.overall_success is False

    def test_client_raises_ibkr_error(self) -> None:
        client = FakeClient()  # no place_responses → raises
        clock = FakeClock()
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            [_trade()],
            enforce_rth=False,
            clock=clock,
            sleeper=FakeSleeper(clock),
            now=in_rth_now,
        )
        assert summary.results[0].success is False
        assert "no scripted" in (summary.results[0].error or "")

    def test_order_rejected_marked_failure(self) -> None:
        client = FakeClient(
            place_responses=[[{"order_id": "111", "order_status": "Submitted"}]],
            status_responses=[{"order_status": "Rejected", "error": "no permissions"}],
        )
        clock = FakeClock()
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            [_trade()],
            enforce_rth=False,
            clock=clock,
            sleeper=FakeSleeper(clock),
            now=in_rth_now,
        )
        result = summary.results[0]
        assert result.success is False
        assert result.final_status == "Rejected"
        assert result.error == "no permissions"

    def test_reply_chain_exhausted(self) -> None:
        # Always returns "needs reply"; should bail after max iterations.
        client = FakeClient(
            place_responses=[[{"id": "1", "message": ["confirm"]}]],
            confirm_responses=[[{"id": f"r{i}", "message": ["please confirm"]}] for i in range(10)],
        )
        clock = FakeClock()
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            [_trade()],
            enforce_rth=False,
            clock=clock,
            sleeper=FakeSleeper(clock),
            now=in_rth_now,
            max_reply_chain=3,
        )
        assert summary.results[0].success is False
        assert "exceeded" in (summary.results[0].error or "")

    def test_multiple_trades_one_fails_others_continue(self) -> None:
        client = FakeClient(
            place_responses=[
                [{"order_id": "111", "order_status": "Submitted"}],  # trade 1 ok
                [{"error": "rejected"}],  # trade 2 fail
                [{"order_id": "333", "order_status": "Submitted"}],  # trade 3 ok
            ],
            status_responses=[{"order_status": "Filled"}, {"order_status": "Filled"}],
        )
        clock = FakeClock()
        trades = [_trade("A"), _trade("B"), _trade("C")]
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            trades,
            enforce_rth=False,
            clock=clock,
            sleeper=FakeSleeper(clock),
            now=in_rth_now,
        )
        assert summary.n_total == 3
        assert summary.n_successful == 2
        assert summary.n_failed == 1
        assert summary.results[1].error == "rejected"


# ---- status polling --------------------------------------------------------


class TestStatusPolling:
    def test_polls_until_terminal(self) -> None:
        client = FakeClient(
            place_responses=[[{"order_id": "111"}]],
            status_responses=[
                {"order_status": "Submitted"},
                {"order_status": "Working"},
                {"order_status": "Filled"},
            ],
        )
        clock = FakeClock()
        sleeper = FakeSleeper(clock)
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            [_trade()],
            enforce_rth=False,
            clock=clock,
            sleeper=sleeper,
            now=in_rth_now,
            poll_interval=1.0,
        )
        assert summary.results[0].final_status == "Filled"
        assert len(client.status_calls) == 3
        assert sleeper.calls == [1.0, 1.0]  # sleeps between poll #1→2, #2→3

    def test_timeout_is_soft_success(self) -> None:
        # Status never reaches terminal — order may still fill, treat as soft success.
        client = FakeClient(
            place_responses=[[{"order_id": "111"}]],
            status_responses=[{"order_status": "Submitted"} for _ in range(10)],
        )
        clock = FakeClock()
        sleeper = FakeSleeper(clock)
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            [_trade()],
            enforce_rth=False,
            clock=clock,
            sleeper=sleeper,
            now=in_rth_now,
            settle_timeout=3.0,
            poll_interval=1.0,
        )
        r = summary.results[0]
        assert r.success is True
        assert r.final_status == "Submitted"


# ---- trading hours --------------------------------------------------------


class TestTradingHours:
    def test_is_rth_weekday_10am(self) -> None:
        assert is_rth(datetime(2026, 5, 12, 10, 0, tzinfo=NY))

    def test_is_rth_weekday_9_29am(self) -> None:
        assert not is_rth(datetime(2026, 5, 12, 9, 29, tzinfo=NY))

    def test_is_rth_weekday_4pm(self) -> None:
        # 16:00:00 is exclusive end
        assert not is_rth(datetime(2026, 5, 12, 16, 0, tzinfo=NY))

    def test_is_rth_saturday(self) -> None:
        assert not is_rth(datetime(2026, 5, 9, 11, 0, tzinfo=NY))

    def test_is_rth_handles_utc_input(self) -> None:
        # 14:00 UTC == 10:00 EDT (in May)
        assert is_rth(datetime(2026, 5, 12, 14, 0, tzinfo=UTC))

    def test_refuses_outside_rth_when_enforced(self) -> None:
        client = FakeClient(place_responses=[[{"order_id": "1"}]])
        sat = datetime(2026, 5, 9, 12, 0, tzinfo=NY)
        with pytest.raises(NotInTradingHoursError):
            execute_trades(
                client,  # type: ignore[arg-type]
                "U1",
                [_trade()],
                enforce_rth=True,
                now=lambda: sat,
                clock=FakeClock(),
                sleeper=FakeSleeper(FakeClock()),
            )

    def test_proceeds_outside_rth_when_not_enforced(self) -> None:
        client = FakeClient(
            place_responses=[[{"order_id": "111"}]],
            status_responses=[{"order_status": "Filled"}],
        )
        sat = datetime(2026, 5, 9, 12, 0, tzinfo=NY)
        clock = FakeClock()
        summary = execute_trades(
            client,  # type: ignore[arg-type]
            "U1",
            [_trade()],
            enforce_rth=False,
            now=lambda: sat,
            clock=clock,
            sleeper=FakeSleeper(clock),
        )
        assert summary.overall_success


# ---- empty input -----------------------------------------------------------


def test_empty_trade_list_returns_empty_summary() -> None:
    client = FakeClient()
    summary = execute_trades(
        client,  # type: ignore[arg-type]
        "U1",
        [],
        enforce_rth=False,
        clock=FakeClock(),
        sleeper=FakeSleeper(FakeClock()),
        now=in_rth_now,
    )
    assert summary.n_total == 0
    assert summary.overall_success is True
