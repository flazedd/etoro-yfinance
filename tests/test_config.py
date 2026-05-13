"""Tests for environment-driven settings."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from ibkr_portfolio_connect.config import Settings


def _common_env(monkeypatch: pytest.MonkeyPatch, *, env_file: Path) -> None:
    monkeypatch.setenv("IBKR_ACCOUNT_ID", "U1234567")
    monkeypatch.setenv("TARGET_PORTFOLIO_URL", "https://example.invalid/target.json")
    # Point pydantic-settings at a non-existent file so the host's real .env never leaks.
    Settings.model_config["env_file"] = str(env_file)


def test_settings_load_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _common_env(monkeypatch, env_file=tmp_path / ".env.missing")
    s = Settings()  # type: ignore[call-arg]
    assert s.ibkr_account_id == "U1234567"
    assert str(s.target_portfolio_url) == "https://example.invalid/target.json"
    assert s.dry_run is False  # default
    assert s.trading_hours_only is True  # default
    assert s.ibkr_gateway_verify_ssl is False  # default


def test_settings_rejects_missing_required(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Clear required vars
    monkeypatch.delenv("IBKR_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("TARGET_PORTFOLIO_URL", raising=False)
    Settings.model_config["env_file"] = str(tmp_path / ".env.missing")
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_settings_ignores_ibeam_vars(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _common_env(monkeypatch, env_file=tmp_path / ".env.missing")
    monkeypatch.setenv("IBKR_USERNAME", "someone")
    monkeypatch.setenv("IBKR_PASSWORD", "secret")
    monkeypatch.setenv("IBKR_TOTP_SECRET", "ABCD")
    # Should not blow up; these are consumed by IBeam, not the rebalancer.
    s = Settings()  # type: ignore[call-arg]
    assert s.ibkr_account_id == "U1234567"


def test_dry_run_truthy_strings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _common_env(monkeypatch, env_file=tmp_path / ".env.missing")
    monkeypatch.setenv("DRY_RUN", "true")
    s = Settings()  # type: ignore[call-arg]
    assert s.dry_run is True
