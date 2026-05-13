"""Environment-driven configuration via pydantic-settings.

Only includes the variables the rebalancer itself reads. IBeam-consumed vars
(IBKR_USERNAME, IBKR_PASSWORD, IBKR_TOTP_SECRET) live in the same `.env` file
but are ignored here via `extra="ignore"`.
"""

from __future__ import annotations

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
    ibkr_gateway_url: str = "https://localhost:5000"
    ibkr_gateway_verify_ssl: bool = False

    target_portfolio_url: HttpUrl
    target_portfolio_auth_token: SecretStr | None = None

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
