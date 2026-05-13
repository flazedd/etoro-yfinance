"""End-to-end rebalance orchestration.

Reads the target portfolio, reads current IBKR state, computes the trade
list, places the trades, and pushes a notification. The CLI calls
`run_rebalance(settings)`; everything else is internal helpers.

The module is structured so each helper is a pure function (or near enough)
so they can be unit-tested without spinning up a real gateway.
"""

from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from .config import Settings
from .executor import ExecutionSummary, execute_trades
from .ibkr_client import IBKRClient
from .notify import Notifier, build_notifier
from .rebalance import ResolvedTarget, compute_trades
from .schema import CurrentPosition, TargetPortfolio, Trade
from .target import fetch_target_portfolio

log = logging.getLogger(__name__)

# IBKR uses one of these keys for "net liquidation value" depending on the
# summary endpoint version.
NAV_FIELD_CANDIDATES: tuple[str, ...] = (
    "netliquidation",
    "totalnetliquidation",
    "equitywithloanvalue",
)
SNAPSHOT_FIELD_LAST_PRICE = "31"
SNAPSHOT_RETRY_ATTEMPTS = 3
SNAPSHOT_RETRY_DELAY_SECONDS = 1.0

# Snapshot prices can come back as "100.50", "C100.50" (close), "H100.50"
# (high), etc. — strip any leading letter then parse.
_SNAPSHOT_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def run_rebalance(
    settings: Settings,
    *,
    ibkr_transport: httpx.BaseTransport | None = None,
    target_transport: httpx.BaseTransport | None = None,
    notifier: Notifier | None = None,
    sleeper: Callable[[float], None] = time.sleep,
) -> ExecutionSummary:
    """Run one full rebalance and return the execution summary.

    Raises only on unrecoverable input errors (e.g. cannot fetch target,
    cannot extract NAV). Anything else surfaces in the returned summary.
    """
    target = _fetch_target(settings, transport=target_transport)
    notifier = notifier or build_notifier(
        ntfy_topic=settings.ntfy_topic, ntfy_server=settings.ntfy_server
    )

    with IBKRClient(
        settings.ibkr_gateway_url,
        verify_ssl=settings.ibkr_gateway_verify_ssl,
        timeout=settings.http_timeout_seconds,
        transport=ibkr_transport,
    ) as client:
        client.ensure_authenticated()
        client.tickle()

        positions = client.positions(settings.ibkr_account_id)
        nav = _extract_nav(client.portfolio_summary(settings.ibkr_account_id))
        resolved_targets = _resolve_target_conids(client, target)
        prices = _collect_prices(client, positions, resolved_targets, sleeper=sleeper)

        trades = compute_trades(current=positions, targets=resolved_targets, nav=nav, prices=prices)
        _log_plan(trades, nav, settings)

        summary = execute_trades(
            client,
            settings.ibkr_account_id,
            trades,
            dry_run=settings.dry_run,
            enforce_rth=settings.trading_hours_only,
            settle_timeout=settings.order_settle_timeout_seconds,
            poll_interval=settings.order_poll_interval_seconds,
        )

    notifier.notify(summary)
    return summary


# ---- helpers ----------------------------------------------------------------


def _fetch_target(settings: Settings, *, transport: httpx.BaseTransport | None) -> TargetPortfolio:
    token = (
        settings.target_portfolio_auth_token.get_secret_value()
        if settings.target_portfolio_auth_token
        else None
    )
    return fetch_target_portfolio(
        settings.target_portfolio_url,
        bearer_token=token,
        timeout=settings.http_timeout_seconds,
        transport=transport,
    )


def _extract_nav(summary: dict[str, Any]) -> Decimal:
    """Pull net liquidation value out of /portfolio/{id}/summary.

    The endpoint shape varies a little between gateway versions; we accept
    either `{"netliquidation": {"amount": 12345.67}}` or
    `{"netliquidation": 12345.67}`.
    """
    for field in NAV_FIELD_CANDIDATES:
        if field not in summary:
            continue
        v = summary[field]
        amount = v.get("amount", v.get("value")) if isinstance(v, dict) else v
        if amount is None:
            continue
        try:
            d = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            continue
        if d > 0:
            return d
    raise ValueError(
        f"could not extract net liquidation from portfolio summary; keys={list(summary)[:10]}"
    )


def _resolve_target_conids(client: IBKRClient, target: TargetPortfolio) -> list[ResolvedTarget]:
    resolved: list[ResolvedTarget] = []
    for tp in target.positions:
        conid = client.resolve_conid(tp.symbol, tp.exchange, asset_class=tp.asset_class.value)
        resolved.append(
            ResolvedTarget(
                conid=conid,
                symbol=tp.symbol,
                exchange=tp.exchange,
                weight_pct=tp.weight_pct,
            )
        )
    return resolved


def _collect_prices(
    client: IBKRClient,
    positions: list[CurrentPosition],
    targets: list[ResolvedTarget],
    *,
    sleeper: Callable[[float], None],
) -> dict[int, Decimal]:
    """Build conid → price for every conid the diff engine needs.

    Strategy: positions already include `mktPrice`; for target conids not
    currently held, hit /iserver/marketdata/snapshot. IBKR's first snapshot
    call can return empty data while it warms up, so we retry briefly.
    """
    prices: dict[int, Decimal] = {}
    for p in positions:
        if p.mkt_price is not None and p.mkt_price > 0:
            prices[p.conid] = p.mkt_price

    needed = [t.conid for t in targets if t.conid not in prices]
    if not needed:
        return prices

    for attempt in range(SNAPSHOT_RETRY_ATTEMPTS):
        rows = client.marketdata_snapshot(needed, fields=[SNAPSHOT_FIELD_LAST_PRICE])
        for row in rows:
            cid = _to_int(row.get("conid"))
            if cid is None or cid in prices:
                continue
            price = _parse_snapshot_price(row)
            if price is not None and price > 0:
                prices[cid] = price
        needed = [c for c in needed if c not in prices]
        if not needed:
            break
        log.info(
            "snapshot warm-up: %d conid(s) still without price (attempt %d/%d)",
            len(needed),
            attempt + 1,
            SNAPSHOT_RETRY_ATTEMPTS,
        )
        sleeper(SNAPSHOT_RETRY_DELAY_SECONDS)

    if needed:
        raise ValueError(
            f"could not resolve market prices for conids {needed} after "
            f"{SNAPSHOT_RETRY_ATTEMPTS} attempts"
        )
    return prices


def _parse_snapshot_price(row: dict[str, Any]) -> Decimal | None:
    raw = row.get(SNAPSHOT_FIELD_LAST_PRICE)
    if raw is None:
        return None
    m = _SNAPSHOT_NUMBER_RE.search(str(raw))
    if not m:
        return None
    try:
        return Decimal(m.group(0))
    except InvalidOperation:
        return None


def _to_int(v: Any) -> int | None:
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _log_plan(trades: list[Trade], nav: Decimal, settings: Settings) -> None:
    log.info("=== Rebalance plan ===")
    log.info("Account NAV: %s", nav)
    log.info("Dry run: %s", settings.dry_run)
    log.info("Enforce RTH: %s", settings.trading_hours_only)
    if not trades:
        log.info("No trades needed — portfolio is already in line.")
        return
    for t in trades:
        log.info("  %-4s %-7d %-6s  (%s)", t.side.value, t.quantity, t.symbol, t.reason)
