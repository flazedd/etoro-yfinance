"""Order executor: send trades to IBKR, walk the reply chain, poll status.

Two modes:
  - dry_run=True  → return a summary marking every trade as DRY_RUN; no calls.
  - dry_run=False → place each trade as MKT DAY, confirm any warning replies,
                    poll order_status until terminal or timeout.

Per IBKR docs we never place a second order before the first has been fully
acknowledged ("when no further warnings are received deferring to /reply").
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from datetime import time as dtime
from zoneinfo import ZoneInfo

from .ibkr_client import IBKRClient, IBKRError, PlaceOrderReply
from .schema import Trade

log = logging.getLogger(__name__)

NY = ZoneInfo("America/New_York")
RTH_START = dtime(9, 30)
RTH_END = dtime(16, 0)

# IBKR order statuses that mean "done, no more polling needed".
TERMINAL_STATUSES = frozenset({"Filled", "Cancelled", "Rejected", "Inactive"})

DEFAULT_SETTLE_TIMEOUT = 120.0
DEFAULT_POLL_INTERVAL = 2.0
DEFAULT_MAX_REPLY_CHAIN = 5


class NotInTradingHoursError(Exception):
    """Raised when execution is attempted outside RTH with enforce_rth=True."""


@dataclass(frozen=True, slots=True)
class TradeResult:
    trade: Trade
    success: bool
    order_id: str | None = None
    final_status: str | None = None
    error: str | None = None

    @property
    def label(self) -> str:
        return f"{self.trade.side.value} {self.trade.quantity} {self.trade.symbol}"


@dataclass(frozen=True, slots=True)
class ExecutionSummary:
    results: list[TradeResult] = field(default_factory=list)
    dry_run: bool = False

    @property
    def n_total(self) -> int:
        return len(self.results)

    @property
    def n_successful(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def n_failed(self) -> int:
        return sum(1 for r in self.results if not r.success)

    @property
    def overall_success(self) -> bool:
        return self.n_failed == 0


def is_rth(now: datetime) -> bool:
    """True if `now` (interpreted in America/New_York) is within RTH on a weekday.

    Does not account for holidays — that's a known v1 limitation. Users who
    need holiday awareness should run the cron only on confirmed market days
    or disable TRADING_HOURS_ONLY for that month.
    """
    now_ny = now.astimezone(NY)
    if now_ny.weekday() >= 5:  # Sat/Sun
        return False
    return RTH_START <= now_ny.time() < RTH_END


def execute_trades(
    client: IBKRClient,
    account_id: str,
    trades: list[Trade],
    *,
    dry_run: bool = False,
    enforce_rth: bool = True,
    settle_timeout: float = DEFAULT_SETTLE_TIMEOUT,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    max_reply_chain: int = DEFAULT_MAX_REPLY_CHAIN,
    clock: Callable[[], float] = time.monotonic,
    sleeper: Callable[[float], None] = time.sleep,
    now: Callable[[], datetime] = lambda: datetime.now(tz=NY),
) -> ExecutionSummary:
    """Place each trade and report results. Stops trading on the first hard
    failure (place-order error or post-reply error); transient timeouts on
    status polling do NOT stop execution — the order may still fill later.
    """
    if dry_run:
        dry_results = [TradeResult(trade=t, success=True, final_status="DRY_RUN") for t in trades]
        return ExecutionSummary(results=dry_results, dry_run=True)

    if not trades:
        return ExecutionSummary(results=[], dry_run=False)

    if enforce_rth and not is_rth(now()):
        raise NotInTradingHoursError(f"refusing to execute outside RTH (now={now().isoformat()})")

    results: list[TradeResult] = []
    for trade in trades:
        try:
            result = _execute_single(
                client=client,
                account_id=account_id,
                trade=trade,
                settle_timeout=settle_timeout,
                poll_interval=poll_interval,
                max_reply_chain=max_reply_chain,
                clock=clock,
                sleeper=sleeper,
            )
        except IBKRError as e:
            log.exception("trade execution raised for %s", trade.symbol)
            result = TradeResult(trade=trade, success=False, error=str(e))
        results.append(result)

    return ExecutionSummary(results=results, dry_run=False)


def _execute_single(
    *,
    client: IBKRClient,
    account_id: str,
    trade: Trade,
    settle_timeout: float,
    poll_interval: float,
    max_reply_chain: int,
    clock: Callable[[], float],
    sleeper: Callable[[float], None],
) -> TradeResult:
    replies = client.place_market_day_order(
        account_id,
        conid=trade.conid,
        side=trade.side,
        quantity=trade.quantity,
    )
    order_id, walk_err = _walk_reply_chain(client, replies, max_reply_chain)
    if walk_err is not None:
        return TradeResult(trade=trade, success=False, error=walk_err)
    if order_id is None:
        return TradeResult(
            trade=trade,
            success=False,
            error="reply chain produced neither order_id nor error",
        )

    status, status_err = _poll_status(
        client=client,
        order_id=order_id,
        settle_timeout=settle_timeout,
        poll_interval=poll_interval,
        clock=clock,
        sleeper=sleeper,
    )
    if status == "Filled":
        return TradeResult(trade=trade, success=True, order_id=order_id, final_status=status)
    if status in {"Cancelled", "Rejected", "Inactive"}:
        return TradeResult(
            trade=trade,
            success=False,
            order_id=order_id,
            final_status=status,
            error=status_err,
        )
    # Non-terminal (e.g. Submitted): order may still fill. Mark as soft-success
    # so notification surfaces partial state without aborting the run.
    log.info(
        "order %s for %s ended polling in non-terminal state %r",
        order_id,
        trade.symbol,
        status,
    )
    return TradeResult(
        trade=trade,
        success=True,
        order_id=order_id,
        final_status=status,
    )


def _walk_reply_chain(
    client: IBKRClient,
    replies: list[PlaceOrderReply],
    max_iter: int,
) -> tuple[str | None, str | None]:
    """Walk through warning replies until we get a confirmed order_id, an
    error, or hit the max-iteration safety bound.

    Returns (order_id, error). Exactly one is non-None when the chain
    terminates cleanly; both can be None if the chain produced an empty/
    unrecognized reply (treated as soft failure by the caller).
    """
    current = replies
    for _ in range(max_iter):
        if not current:
            return None, "empty reply from place-order"
        first = current[0]
        kind = first.kind
        if kind == "confirmed":
            assert first.order_id is not None
            return first.order_id, None
        if kind == "error":
            return None, first.error or "unspecified IBKR error"
        if kind == "reply_required":
            assert first.id is not None
            log.info("confirming order reply %s", first.id)
            current = client.confirm_reply(first.id, confirmed=True)
            continue
        return None, f"unrecognized reply shape: {first.model_dump(exclude_none=True)}"
    return None, f"reply chain exceeded {max_iter} iterations"


def _poll_status(
    *,
    client: IBKRClient,
    order_id: str,
    settle_timeout: float,
    poll_interval: float,
    clock: Callable[[], float],
    sleeper: Callable[[float], None],
) -> tuple[str | None, str | None]:
    """Poll until a terminal status or timeout. Returns (status, error)."""
    deadline = clock() + settle_timeout
    last_status: str | None = None
    while True:
        blob = client.order_status(order_id)
        status = (
            str(
                blob.get("order_status") or blob.get("status") or blob.get("order_ccp_status") or ""
            )
            or None
        )
        if status is not None:
            last_status = status
        if status in TERMINAL_STATUSES:
            err = str(blob.get("error", "")) or None if status != "Filled" else None
            return status, err
        if clock() >= deadline:
            log.warning(
                "order %s did not terminate within %.1fs (last status: %r)",
                order_id,
                settle_timeout,
                last_status,
            )
            return last_status, None
        sleeper(poll_interval)
