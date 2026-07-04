"""Environment-driven configuration via pydantic-settings.

Only the variables the eToro client reads. `extra="ignore"` so unrelated vars in
`.env` (or leftover keys) don't trip startup.
"""

from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- eToro brokerage ---
    # The public key (x-api-key) is shared across environments. The user key
    # (x-user-key) is environment-scoped — a demo key and a real key are separate,
    # so store both; ETORO_ENV picks which one is used. Optional — the client
    # raises a clear error only when you actually try to trade with them unset.
    etoro_api_key: SecretStr | None = None  # public key (x-api-key), shared
    etoro_user_key_demo: SecretStr | None = None  # demo user key (x-user-key)
    etoro_user_key_real: SecretStr | None = None  # real user key (x-user-key)
    etoro_user_key: SecretStr | None = None  # optional generic fallback
    etoro_env: str = "demo"  # "demo" (virtual money) or "real" (live)
    etoro_order_currency: str = "usd"  # currency for amount-based (notional) buys
    etoro_default_leverage: int = 1  # 1 = real stock, no CFD leverage

    # --- Networking ---
    http_timeout_seconds: float = 30.0
