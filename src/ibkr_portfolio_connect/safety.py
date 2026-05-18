"""Pre-trade safety checks.

Fires once we have positions, NAV, target, and the computed trade list —
but BEFORE execute_trades. Each check is gated by a Settings threshold
(set to None to disable individually) and raises PreTradeSafetyError on
violation. The pipeline catches that exception, fires a high-priority
notification with the reason, and aborts.

Designed to catch operator-error and target-service-bug disasters:
- Trading against the wrong account (paper/live profile mix-up)
- Acting on a NAV that parsed wrong / account is empty
- A target portfolio that demands an outsized single trade
- A target portfolio that would churn the entire account
- Acting on a reference_price generated days ago (market has moved)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from .config import Settings
from .schema import TargetPortfolio, Trade


class PreTradeSafetyError(Exception):
    """A pre-trade safety check failed; pipeline must abort before execution."""


def check_safety(
    *,
    settings: Settings,
    target: TargetPortfolio,
    trades: list[Trade],
    nav: Decimal,
    visible_accounts: list[str],
    now: datetime | None = None,
) -> None:
    """Run all configured checks. Raise PreTradeSafetyError on first failure.

    `visible_accounts` is the list returned by client.iserver_accounts() —
    used to verify our configured account is actually accessible (catches
    paper-vs-live profile mistakes).
    """
    now = now or datetime.now(UTC)

    # 1. Account-ID-in-visible-accounts — always enforced when we have a list.
    if visible_accounts and settings.ibkr_account_id not in visible_accounts:
        raise PreTradeSafetyError(
            f"configured IBKR_ACCOUNT_ID={settings.ibkr_account_id!r} is not in "
            f"OAuth-visible accounts {visible_accounts}; likely wrong env profile"
        )

    # 2. NAV sanity.
    if settings.min_nav_dollars is not None and nav < settings.min_nav_dollars:
        raise PreTradeSafetyError(
            f"NAV {nav} below min_nav_dollars {settings.min_nav_dollars}; refusing to trade"
        )

    # 3. Per-trade size cap.
    if settings.max_trade_pct_of_nav is not None and nav > 0:
        cap_dollars = nav * settings.max_trade_pct_of_nav / Decimal("100")
        for t in trades:
            est = _trade_est_value(t)
            if est is None:
                continue
            if est > cap_dollars:
                raise PreTradeSafetyError(
                    f"trade {t.side.value} {t.quantity} {t.symbol} estimated value "
                    f"${est:.2f} exceeds {settings.max_trade_pct_of_nav}% of NAV "
                    f"(cap ${cap_dollars:.2f})"
                )

    # 4. Total-churn cap.
    if settings.max_total_churn_pct_of_nav is not None and nav > 0:
        cap_dollars = nav * settings.max_total_churn_pct_of_nav / Decimal("100")
        total = sum(
            (_trade_est_value(t) or Decimal("0") for t in trades),
            start=Decimal("0"),
        )
        if total > cap_dollars:
            raise PreTradeSafetyError(
                f"total trade volume ${total:.2f} exceeds "
                f"{settings.max_total_churn_pct_of_nav}% of NAV "
                f"(cap ${cap_dollars:.2f})"
            )

    # 5. Stale reference prices.
    if settings.max_reference_age_hours is not None:
        max_age = timedelta(hours=settings.max_reference_age_hours)
        for tp in target.positions:
            age = now - tp.reference_price_at
            if age > max_age:
                hours = age.total_seconds() / 3600
                raise PreTradeSafetyError(
                    f"reference_price for {tp.symbol} is {hours:.1f}h old, exceeds "
                    f"max_reference_age_hours={settings.max_reference_age_hours}"
                )


def _trade_est_value(trade: Trade) -> Decimal | None:
    """Estimated dollar value of a trade at its reference price.

    None for liquidation trades (no reference_price available); those skip
    the per-trade and total-churn caps. That's intentional: liquidations
    are sized by quantity-held, not by target weight, and we don't have a
    reliable price to estimate value with.
    """
    if trade.reference_price is None:
        return None
    return trade.reference_price * Decimal(trade.quantity)
