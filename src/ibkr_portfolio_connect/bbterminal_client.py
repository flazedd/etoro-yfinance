"""Minimal admin-API client for bbterminal.

The source of truth for "what should the portfolio be". Authenticates against
Supabase (email/password), then calls the bbterminal admin API with the minted
JWT. Tokens last ~1h; this client refreshes them transparently ~60s before
expiry and retries once on a 401, so a long-running bot on the Pi never has to
think about bearer tokens.

This is vendored (with light edits) from the bbterminal API docs so it can be
reviewed against that reference 1:1. Reads creds from env vars via `from_env()`
so the password never lives in source.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, cast

import requests


class BBTerminalError(Exception):
    """Wrapped HTTP error with the response body for actionable messages."""


@dataclass
class BBTerminalClient:
    base_url: str  # e.g. "https://bbterminal-production.up.railway.app"
    supabase_url: str  # e.g. "https://abc.supabase.co"
    supabase_anon_key: str
    email: str
    password: str
    timeout: int = 30
    # Refresh ~60 s before expiry so we don't race the boundary.
    refresh_buffer_seconds: int = 60

    _access_token: str | None = field(default=None, init=False, repr=False)
    _refresh_token: str | None = field(default=None, init=False, repr=False)
    _expires_at: float | None = field(default=None, init=False, repr=False)

    # ─── Auth lifecycle ──────────────────────────────────────────

    def _login(self) -> None:
        """Trade email/password for a fresh access + refresh token pair."""
        r = requests.post(
            f"{self.supabase_url}/auth/v1/token",
            params={"grant_type": "password"},
            headers={
                "apikey": self.supabase_anon_key,
                "Content-Type": "application/json",
            },
            json={"email": self.email, "password": self.password},
            timeout=self.timeout,
        )
        if r.status_code >= 400:
            raise BBTerminalError(f"Login failed: {r.status_code} {r.text[:200]}")
        self._apply_token_response(r.json())

    def _refresh(self) -> None:
        """Refresh-token swap. Falls back to full login if the refresh
        token is revoked or expired."""
        if not self._refresh_token:
            self._login()
            return
        r = requests.post(
            f"{self.supabase_url}/auth/v1/token",
            params={"grant_type": "refresh_token"},
            headers={
                "apikey": self.supabase_anon_key,
                "Content-Type": "application/json",
            },
            json={"refresh_token": self._refresh_token},
            timeout=self.timeout,
        )
        if r.status_code >= 400:
            self._login()
            return
        self._apply_token_response(r.json())

    def _apply_token_response(self, data: dict[str, Any]) -> None:
        self._access_token = data["access_token"]
        self._refresh_token = data.get("refresh_token", self._refresh_token)
        # Prefer absolute "expires_at" (unix seconds); fall back to offset.
        self._expires_at = data.get("expires_at") or (
            time.time() + data.get("expires_in", 3600)
        )

    def _ensure_token(self) -> str:
        """Return a valid access token, refreshing transparently when
        the current one is missing or near expiry."""
        if not self._access_token or not self._expires_at:
            self._login()
        elif time.time() >= self._expires_at - self.refresh_buffer_seconds:
            self._refresh()
        assert self._access_token is not None
        return self._access_token

    # ─── HTTP plumbing ───────────────────────────────────────────

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Authenticated request with one auto-retry on 401 (token
        race / sudden revocation)."""
        url = f"{self.base_url}{path}"
        last_status = None
        for attempt in range(2):
            token = self._ensure_token()
            headers = {
                **(kwargs.pop("headers", {}) or {}),
                "Authorization": f"Bearer {token}",
            }
            r = requests.request(
                method, url, headers=headers, timeout=self.timeout, **kwargs
            )
            last_status = r.status_code
            if r.status_code == 401 and attempt == 0:
                # Force re-login next loop iteration.
                self._access_token = None
                self._expires_at = None
                continue
            if r.status_code >= 400:
                raise BBTerminalError(f"{method} {path} -> {r.status_code} {r.text[:300]}")
            if r.headers.get("content-type", "").startswith("application/json"):
                return r.json()
            return r.text
        raise BBTerminalError(f"Auth retry exhausted (last status {last_status})")

    # ─── Convenience wrappers per admin endpoint ─────────────────

    def whoami(self) -> dict[str, Any]:
        """Quick startup sanity check — returns {id, email, role}.
        Bail fast if role != 'admin'."""
        return cast(dict[str, Any], self._request("GET", "/api/auth/me"))

    def schedules(self, enabled_only: bool = True) -> list[dict[str, Any]]:
        """List every scheduled strategy + its next rebalance date
        (lightweight; no holdings). Use it to find the strategy_id to
        pass to schedule()."""
        return cast(
            list[dict[str, Any]],
            self._request(
                "GET",
                "/api/admin/schedules",
                params={"enabled_only": str(enabled_only).lower()},
            ),
        )

    def schedule(self, strategy_id: int) -> dict[str, Any]:
        """One strategy's CURRENT holdings — order-ready. Each holding
        carries ticker, exchange, country, currency, company_name, side,
        target_weight, score, entry_price_local, entry_price_eur. Also
        returns as_of_date / latest_price_date — gate on those (or
        health()) so you never trade on stale data."""
        return cast(dict[str, Any], self._request("GET", f"/api/admin/schedules/{strategy_id}"))

    def performance(self, strategy_id: int) -> dict[str, Any]:
        """One strategy's performance stats: mtd_return_pct,
        since_inception_return_pct, inception_date, as_of_date, and a
        daily_returns time-series (may be empty for a young strategy)."""
        return cast(
            dict[str, Any],
            self._request("GET", f"/api/admin/schedules/{strategy_id}/performance"),
        )

    def health(self) -> dict[str, Any]:
        """Composite go/no-go. Gate trades on is_healthy_strict."""
        return cast(dict[str, Any], self._request("GET", "/api/admin/health"))

    def universes(self, include_all: bool = False) -> list[dict[str, Any]]:
        """List universes — id, label, kind, frozen_at, month range.

        By default returns only the frozen static snapshots (the canonical
        "X (as of YYYY-MM)" sets). Pass include_all=True to also see the live
        template-managed canonicals, the LongEquity time-series universe,
        criteria-derived and imported-index universes. Pick a universe_id to
        pass to universe()."""
        resp = self._request(
            "GET",
            "/api/admin/universes",
            params={"include_all": str(include_all).lower()},
        )
        return cast(list[dict[str, Any]], cast(dict[str, Any], resp)["universes"])

    def universe(self, universe_id: int, month: str | None = None) -> dict[str, Any]:
        """One universe's full membership. Each member carries ticker,
        exchange, country, currency, isin, company_name, sector, industry,
        latest_close_local, latest_close_eur, latest_close_date, fx_rate_per_eur.

        `month` (YYYY-MM) only does anything for the multi-month LongEquity
        time-series universe; for any single-month frozen set it is ignored."""
        params = {"month": month} if month else None
        return cast(
            dict[str, Any],
            self._request("GET", f"/api/admin/universes/{universe_id}", params=params),
        )

    # ─── Factory ─────────────────────────────────────────────────

    @classmethod
    def from_env(cls) -> BBTerminalClient:
        """Construct from env vars. Useful so the IBKR script never
        embeds the password literally — keep it in .env / your
        secrets manager.

        Accepts BBTERMINAL_BASE_URL (this repo's existing name) or
        BBTERMINAL_URL (the docs' name) for the API base.
        """
        base_url = os.environ.get("BBTERMINAL_BASE_URL") or os.environ.get("BBTERMINAL_URL")
        required = {
            "BBTERMINAL_BASE_URL/BBTERMINAL_URL": base_url,
            "SUPABASE_URL": os.environ.get("SUPABASE_URL"),
            "SUPABASE_ANON_KEY": os.environ.get("SUPABASE_ANON_KEY"),
            "BBTERMINAL_EMAIL": os.environ.get("BBTERMINAL_EMAIL"),
            "BBTERMINAL_PASSWORD": os.environ.get("BBTERMINAL_PASSWORD"),
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise BBTerminalError(f"Missing env vars: {', '.join(missing)}")
        assert base_url is not None  # for type-checkers; guarded by `missing` above
        return cls(
            base_url=base_url.rstrip("/"),
            supabase_url=os.environ["SUPABASE_URL"].rstrip("/"),
            supabase_anon_key=os.environ["SUPABASE_ANON_KEY"],
            email=os.environ["BBTERMINAL_EMAIL"],
            password=os.environ["BBTERMINAL_PASSWORD"],
        )
