"""Environment-driven configuration via pydantic-settings.

Only includes the variables the rebalancer itself reads. IBind's OAuth vars
(IBIND_OAUTH1A_*) live in the same `.env` but are consumed by IBind directly
at import time, not via this Settings object — hence `extra="ignore"`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from pydantic import Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    ibkr_account_id: str = Field(min_length=1)

    # Legacy plain-JSON target source (target.py path). The live source is now
    # bbterminal (see below), so this is optional.
    target_portfolio_url: HttpUrl | None = None
    target_portfolio_auth_token: SecretStr | None = None

    # --- bbterminal source ---
    # Currency the strategy is denominated in; sizing uses entry_price_eur and
    # the account NAV must be in this currency (we don't auto-FX in v1).
    sizing_currency: str = "EUR"
    # Refuse to trade unless bbterminal health.is_healthy_strict is true.
    require_strategy_healthy: bool = True
    # Path to the reviewed conid map the rebalancer trades off.
    conid_map_path: Path = Path("conid_map.json")
    # Refuse if the strategy's as_of_date is older than this many days.
    max_strategy_age_days: float | None = 14.0

    dry_run: bool = False
    trading_hours_only: bool = True

    # ntfy.sh notifications
    ntfy_topic: str | None = None
    ntfy_server: str = "https://ntfy.sh"

    # Networking
    http_timeout_seconds: float = 30.0
    # How long to poll order status after submission before giving up.
    order_settle_timeout_seconds: float = 120.0
    # Poll interval while waiting for fills.
    order_poll_interval_seconds: float = 2.0

    # --- Pre-trade safety thresholds ---
    # All Optional — set any to None in .env (e.g. MIN_NAV_DOLLARS=) to disable.
    # Defaults are conservative. Tighten as you build trust in the pipeline.
    min_nav_dollars: Decimal | None = Decimal("1000")
    """Refuse to trade if account NAV is below this — catches parse bugs / empty account."""

    max_trade_pct_of_nav: Decimal | None = Decimal("50")
    """Refuse any single trade whose estimated value exceeds this % of NAV."""

    max_total_churn_pct_of_nav: Decimal | None = Decimal("100")
    """Refuse if total trade volume exceeds this % of NAV (catches mass-liquidation bugs)."""

    max_reference_age_hours: float | None = 24.0
    """Refuse if any target position's reference_price_at is older than this."""

    # --- Report persistence ---
    report_dir: Path | None = None
    """If set, each RebalanceReport is serialized to {report_dir}/{ts}.json."""
