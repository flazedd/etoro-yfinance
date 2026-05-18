"""End-to-end rebalance orchestration.

Reads the target portfolio, reads current IBKR state, computes the trade
list, places the trades, and pushes a notification. The CLI calls
`run_rebalance(settings)`; everything else is internal helpers.

The module is structured so each helper is a pure function (or near enough)
so they can be unit-tested without spinning up a real gateway.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from .config import Settings
from .cost import RebalanceReport, build_report, save_report
from .executor import execute_trades
from .ibkr_client import IBKRClient
from .notify import Notifier, build_notifier
from .rebalance import ResolvedTarget, compute_trades
from .safety import PreTradeSafetyError, check_safety
from .schema import TargetPortfolio, Trade
from .target import fetch_target_portfolio

log = logging.getLogger(__name__)

# IBKR uses one of these keys for "net liquidation value" depending on the
# summary endpoint version.
NAV_FIELD_CANDIDATES: tuple[str, ...] = (
    "netliquidation",
    "totalnetliquidation",
    "equitywithloanvalue",
)


def run_rebalance(
    settings: Settings,
    *,
    client: IBKRClient | None = None,
    target_transport: httpx.BaseTransport | None = None,
    notifier: Notifier | None = None,
    sleeper: Callable[[float], None] = time.sleep,
) -> RebalanceReport:
    """Run one full rebalance and return the cost-attributed report.

    Raises only on unrecoverable input errors (e.g. cannot fetch target,
    cannot extract NAV). Anything else surfaces in the returned report.

    Pass `client` to inject a pre-built IBKRClient (used by tests). When
    omitted, a real one is constructed from settings — which under OAuth
    triggers the live session token handshake at construction time.
    """
    target = _fetch_target(settings, transport=target_transport)
    notifier = notifier or build_notifier(
        ntfy_topic=settings.ntfy_topic, ntfy_server=settings.ntfy_server
    )

    if client is None:
        client = IBKRClient(timeout=settings.http_timeout_seconds)

    with client:
        visible_accounts = client.iserver_accounts()
        positions = client.positions(settings.ibkr_account_id)
        nav = _extract_nav(client.portfolio_summary(settings.ibkr_account_id))
        resolved_targets = _resolve_target_conids(client, target)

        trades = compute_trades(current=positions, targets=resolved_targets, nav=nav)
        _log_plan(trades, nav, settings)

        try:
            check_safety(
                settings=settings,
                target=target,
                trades=trades,
                nav=nav,
                visible_accounts=visible_accounts,
            )
        except PreTradeSafetyError as e:
            log.error("pre-trade safety check failed: %s", e)
            aborted = RebalanceReport(nav=nav, trades=[], aborted_reason=str(e))
            notifier.notify(aborted)
            raise

        summary = execute_trades(
            client,
            settings.ibkr_account_id,
            trades,
            dry_run=settings.dry_run,
            enforce_rth=settings.trading_hours_only,
            settle_timeout=settings.order_settle_timeout_seconds,
            poll_interval=settings.order_poll_interval_seconds,
            sleeper=sleeper,
        )

    report = build_report(summary, nav=nav)
    if settings.report_dir is not None:
        saved_to = save_report(report, report_dir=settings.report_dir)
        log.info("report saved to %s", saved_to)
    notifier.notify(report)
    return report


# ---- helpers ----------------------------------------------------------------


def run_what_if(
    settings: Settings,
    *,
    client: IBKRClient | None = None,
    target_transport: httpx.BaseTransport | None = None,
) -> list[dict[str, Any]]:
    """Like run_rebalance, but calls IBKR's whatif endpoint per trade instead
    of placing orders. Returns a list of `{"trade": Trade, "preview": dict}`
    where each preview is IBKR's commission + margin response.

    Pre-trade safety checks still run — we wouldn't want a what-if to surface
    "$50k commission!" because we're previewing against the wrong account.
    """
    target = _fetch_target(settings, transport=target_transport)

    if client is None:
        client = IBKRClient(timeout=settings.http_timeout_seconds)

    previews: list[dict[str, Any]] = []
    with client:
        visible_accounts = client.iserver_accounts()
        positions = client.positions(settings.ibkr_account_id)
        nav = _extract_nav(client.portfolio_summary(settings.ibkr_account_id))
        resolved_targets = _resolve_target_conids(client, target)

        trades = compute_trades(current=positions, targets=resolved_targets, nav=nav)
        _log_plan(trades, nav, settings)

        check_safety(
            settings=settings,
            target=target,
            trades=trades,
            nav=nav,
            visible_accounts=visible_accounts,
        )

        for t in trades:
            preview = client.what_if_order(
                settings.ibkr_account_id,
                conid=t.conid,
                side=t.side,
                quantity=t.quantity,
            )
            previews.append({"trade": t, "preview": preview})

    return previews


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
                reference_price=tp.reference_price,
            )
        )
    return resolved


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
