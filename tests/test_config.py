"""Tests for environment-driven settings (eToro)."""

from __future__ import annotations

from pathlib import Path

import pytest

from etoro_yfinance.config import Settings


def _isolate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Point pydantic-settings at a non-existent file so the host's real .env never leaks.
    Settings.model_config["env_file"] = str(tmp_path / ".env.missing")
    for k in ("ETORO_API_KEY", "ETORO_USER_KEY_DEMO", "ETORO_USER_KEY_REAL",
              "ETORO_USER_KEY", "ETORO_ENV"):
        monkeypatch.delenv(k, raising=False)


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _isolate(monkeypatch, tmp_path)
    s = Settings()  # no required fields
    assert s.etoro_env == "demo"
    assert s.etoro_default_leverage == 1
    assert s.etoro_order_currency == "usd"
    assert s.http_timeout_seconds == 30.0
    assert s.etoro_api_key is None
    assert s.etoro_user_key_demo is None


def test_settings_reads_etoro_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("ETORO_API_KEY", "PUB")
    monkeypatch.setenv("ETORO_USER_KEY_REAL", "REALKEY")
    monkeypatch.setenv("ETORO_ENV", "real")
    s = Settings()
    assert s.etoro_env == "real"
    assert s.etoro_api_key.get_secret_value() == "PUB"
    assert s.etoro_user_key_real.get_secret_value() == "REALKEY"


def test_settings_ignores_unrelated_vars(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _isolate(monkeypatch, tmp_path)
    # Unknown / leftover env vars must not trip startup (extra="ignore").
    monkeypatch.setenv("SOME_LEGACY_VAR", "U1234567")
    monkeypatch.setenv("ANOTHER_UNRELATED_KEY", "x")
    s = Settings()
    assert s.etoro_env == "demo"
