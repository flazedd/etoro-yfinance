"""Buy/replace rebalance driven by the bbterminal strategy + pinned conid map.

The flow, wake-up to fills:

  1. gate on bbterminal health (is_healthy_strict) and strategy freshness
  2. read the scheduled strategy's holdings (the new target portfolio)
  3. for each holding, look up its REVIEWED conid in conid_map.json — refuse if
     any is missing/unreviewed/ISIN-drifted (we never resolve live at trade time)
  4. read current IBKR positions + account NAV (in the sizing currency, EUR)
  5. diff current -> target with the pure engine (sells what's gone, buys/trims
     the rest) — this is the "replace old portfolio with new" step
  6. run source-agnostic safety caps, then place MIDPRICE DAY orders (or dry-run)

Sizing is done in EUR: target weight x NAV(EUR) / entry_price_eur = shares. The
share count is currency-correct as long as NAV and price are the same currency,
which is why we gate the account NAV currency == sizing_currency.

The pure functions (build_targets / extract_nav / plan_trades) take plain data
so they're unit-tested without a live gateway; run_bb_rebalance wires in I/O.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from .bbterminal_client import BBTerminalClient
from .config import Settings
from .conid_map import ConidMap, load_map, require_reviewed_conid
from .cost import RebalanceReport, build_report, save_report
from .executor import execute_trades
from .ibkr_client import IBKRClient
from .notify import Notifier, build_notifier
from .rebalance import ResolvedTarget, compute_trades
from .safety import PreTradeSafetyError, check_trade_caps
from .schema import Trade

log = logging.getLogger(__name__)

# IBKR uses one of these keys for "net liquidation value" depending on version.
NAV_FIELD_CANDIDATES: tuple[str, ...] = (
    "netliquidation",
    "totalnetliquidation",
    "equitywithloanvalue",
)


class RebalanceInputError(Exception):
    """A precondition for trading failed (unhealthy strategy, stale data, wrong
    NAV currency). Distinct from PreTradeSafetyError, which is about the trades."""


# ---- pure planning ----------------------------------------------------------


def build_targets(holdings: list[dict[str, Any]], conid_map: ConidMap) -> list[ResolvedTarget]:
    """Turn bbterminal holdings into resolved, reviewed targets sized in EUR.

    Raises ConidMapError (from require_reviewed_conid) if any holding isn't a
    reviewed entry in the map — so an unvetted name can never reach the diff.
    """
    targets: list[ResolvedTarget] = []
    for h in holdings:
        company_id = int(h["company_id"])
        isin = str(h["isin"]) if h.get("isin") else None
        conid = require_reviewed_conid(conid_map, company_id, expected_isin=isin)
        entry = conid_map.get(company_id)
        weight_pct = Decimal(str(h["target_weight"])) * Decimal("100")
        price_eur = Decimal(str(h["entry_price_eur"]))
        targets.append(
            ResolvedTarget(
                conid=conid,
                symbol=str(h.get("ticker", "")),
                exchange=entry.ibkr_listing if entry else "SMART",
                weight_pct=weight_pct,
                reference_price=price_eur,
            )
        )
    return targets


def extract_nav(summary: dict[str, Any], *, required_currency: str) -> Decimal:
    """Pull net-liquidation value out of /portfolio/{id}/summary and verify it
    is in the expected currency (we don't auto-FX in v1).

    Accepts `{"netliquidation": {"amount": X, "currency": "EUR"}}` or a bare
    `{"netliquidation": X}` (currency unverifiable -> trusted with a warning).
    """
    for field in NAV_FIELD_CANDIDATES:
        if field not in summary:
            continue
        v = summary[field]
        if isinstance(v, dict):
            amount = v.get("amount", v.get("value"))
            currency = v.get("currency")
        else:
            amount, currency = v, None
        if amount is None:
            continue
        try:
            d = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            continue
        if d <= 0:
            continue
        if currency and str(currency).upper() != required_currency.upper():
            raise RebalanceInputError(
                f"account NAV is in {currency}, but sizing currency is "
                f"{required_currency}; v1 does not auto-convert FX. Set the account "
                f"base currency to {required_currency} or add FX conversion."
            )
        if not currency:
            log.warning("portfolio summary did not report a NAV currency; "
                        "trusting it is %s", required_currency)
        return d
    raise RebalanceInputError(
        f"could not extract net liquidation from portfolio summary; keys={list(summary)[:10]}"
    )


def plan_trades(
    *,
    holdings: list[dict[str, Any]],
    conid_map: ConidMap,
    positions: list[Any],
    nav: Decimal,
) -> list[Trade]:
    """Pure: holdings + map + current positions + NAV(EUR) -> ordered trade list."""
    targets = build_targets(holdings, conid_map)
    return compute_trades(current=positions, targets=targets, nav=nav)


def check_strategy_freshness(
    detail: dict[str, Any], *, max_age_days: float | None, now: date | None = None
) -> None:
    """Refuse to trade on a stale strategy snapshot."""
    if max_age_days is None:
        return
    as_of_raw = detail.get("as_of_date")
    if not as_of_raw:
        raise RebalanceInputError("strategy has no as_of_date; refusing to trade on unknown vintage")
    try:
        as_of = date.fromisoformat(str(as_of_raw))
    except ValueError as e:
        raise RebalanceInputError(f"unparseable as_of_date {as_of_raw!r}: {e}") from e
    today = now or datetime.now(UTC).date()
    age_days = (today - as_of).days
    if age_days > max_age_days:
        raise RebalanceInputError(
            f"strategy as_of_date {as_of} is {age_days}d old, exceeds "
            f"max_strategy_age_days={max_age_days}"
        )


# ---- orchestration ----------------------------------------------------------


def run_bb_rebalance(
    settings: Settings,
    *,
    client: IBKRClient | None = None,
    bb: BBTerminalClient | None = None,
    notifier: Notifier | None = None,
    sleeper: Callable[[float], None] = time.sleep,
    dry_run: bool | None = None,
) -> RebalanceReport:
    """Run one full buy/replace rebalance from the bbterminal source.

    `dry_run` overrides settings.dry_run when given (the CLI passes it). Tests
    inject `client` / `bb` / `notifier`; production builds them from env.
    """
    do_dry = settings.dry_run if dry_run is None else dry_run
    bb = bb or BBTerminalClient.from_env()
    notifier = notifier or build_notifier(
        ntfy_topic=settings.ntfy_topic, ntfy_server=settings.ntfy_server
    )

    # --- bbterminal gates (no orders yet) ---
    health = bb.health()
    if settings.require_strategy_healthy and not health.get("is_healthy_strict", False):
        raise RebalanceInputError(
            f"bbterminal not healthy (is_healthy_strict=false): {health.get('problems')}. "
            "Set REQUIRE_STRATEGY_HEALTHY=false to override."
        )
    scheds = bb.schedules(enabled_only=True)
    if not scheds:
        raise RebalanceInputError("no enabled scheduled strategy")
    strategy_id = scheds[0]["strategy_id"]
    detail = bb.schedule(strategy_id)
    check_strategy_freshness(detail, max_age_days=settings.max_strategy_age_days)
    holdings = detail.get("holdings", [])

    conid_map = load_map(settings.conid_map_path)
    # Resolve+review-gate up front so we fail before any IBKR write if a name
    # isn't vetted. (Raises ConidMapError.)
    targets = build_targets(holdings, conid_map)

    if client is None:
        client = IBKRClient(timeout=settings.http_timeout_seconds)

    with client:
        visible_accounts = client.iserver_accounts()
        positions = client.positions(settings.ibkr_account_id)
        nav = extract_nav(
            client.portfolio_summary(settings.ibkr_account_id),
            required_currency=settings.sizing_currency,
        )
        trades = compute_trades(current=positions, targets=targets, nav=nav)
        _log_plan(trades, nav, strategy_id, do_dry)

        try:
            check_trade_caps(
                settings=settings, trades=trades, nav=nav, visible_accounts=visible_accounts
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
            dry_run=do_dry,
            enforce_rth=settings.trading_hours_only,
            settle_timeout=settings.order_settle_timeout_seconds,
            poll_interval=settings.order_poll_interval_seconds,
            sleeper=sleeper,
        )

    report = build_report(summary, nav=nav)
    if settings.report_dir is not None:
        save_report(report, report_dir=settings.report_dir)
    notifier.notify(report)
    return report


def _log_plan(trades: list[Trade], nav: Decimal, strategy_id: int, dry_run: bool) -> None:
    log.info("=== bbterminal rebalance plan (strategy #%s) ===", strategy_id)
    log.info("NAV (%s): %s  dry_run=%s", "sizing ccy", nav, dry_run)
    if not trades:
        log.info("No trades needed — already in line with target.")
        return
    for t in trades:
        log.info("  %-4s %-7d %-8s (%s)", t.side.value, t.quantity, t.symbol, t.reason)
