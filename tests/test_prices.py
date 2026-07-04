"""Tests for the Parquet price store and the EUR conversion.

The EUR conversion is where the silent 100× errors live (GBp vs GBP, share
count vs notional volume), so it's pinned against hand-computed values.
All filesystem tests run against a tmp data dir via MOMENTUM_DATA_DIR.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

from etoro_yfinance import prices

_IDX = pd.date_range("2024-01-02", periods=3, freq="D")


def _frame(close: float = 100.0, volume: float = 10.0) -> pd.DataFrame:
    return pd.DataFrame({"close": close, "adj_close": close, "volume": volume}, index=_IDX)


def _ecb(**cols: float) -> pd.DataFrame:
    return pd.DataFrame(cols, index=_IDX)  # CCY per EUR


def test_to_eur_usd_prices_and_equity_turnover() -> None:
    out = prices.to_eur(_frame(close=100.0, volume=10.0), "USD", "us", _ecb(USD=2.0))
    assert out is not None
    assert (out["close"] == 50.0).all()  # 100 USD @ 2 USD/EUR
    assert (out["adj_close"] == 50.0).all()
    assert (out["volume"] == 500.0).all()  # 100 × 10 shares / 2


def test_to_eur_gbp_pence_are_divided_by_100() -> None:
    # 250 GBp = 2.50 GBP; at 0.5 GBP/EUR that's 5 EUR. Missing the sub-unit
    # factor would yield 500 EUR — the classic silent 100× error.
    out = prices.to_eur(_frame(close=250.0), "GBp", "intl", _ecb(GBP=0.5))
    assert out is not None
    assert (out["close"] == 5.0).all()


def test_to_eur_crypto_volume_is_already_notional() -> None:
    out = prices.to_eur(_frame(close=100.0, volume=1000.0), "USD", "crypto", _ecb(USD=2.0))
    assert out is not None
    assert (out["volume"] == 500.0).all()  # USD notional / rate only


def test_to_eur_unknown_currency_returns_none() -> None:
    assert prices.to_eur(_frame(), "XXX", "us", _ecb(USD=2.0)) is None
    assert prices.to_eur(_frame(), "USD", "us", None) is None


def test_drop_unclosed_removes_todays_bar() -> None:
    today = datetime.now(UTC).date()
    idx = pd.DatetimeIndex([pd.Timestamp(today - timedelta(days=1)), pd.Timestamp(today)])
    df = pd.DataFrame({"close": [1.0, 2.0]}, index=idx)
    out = prices.drop_unclosed(df)
    assert len(out) == 1
    assert out.index[0].date() == today - timedelta(days=1)


def test_normalize_maps_yfinance_columns_and_dtypes() -> None:
    idx = pd.date_range("2024-01-02", periods=2, freq="D", tz="UTC")
    raw = pd.DataFrame(
        {"Open": [1.0, 2.0], "Close": [1.5, 2.5], "Adj Close": [1.4, 2.4], "Volume": [100, None]},
        index=idx,
    )
    out = prices._normalize(raw)
    assert out is not None
    assert list(out.columns) == ["date", "open", "close", "adj_close", "volume"]
    assert out["close"].dtype == "float32"
    assert out["volume"].dtype == "int64"
    assert out["volume"].tolist() == [100, 0]  # NaN volume → 0
    assert prices._normalize(None) is None


@pytest.fixture
def data_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    return tmp_path


def test_write_and_load_roundtrip(data_dir: Path) -> None:
    idx = pd.date_range("2024-01-02", periods=5, freq="D")
    raw = pd.DataFrame({"Close": range(5), "Adj Close": range(5), "Volume": 100}, index=idx)
    assert prices.write_prices("AAPL", raw) == 5
    assert prices.available_tickers() == ["AAPL"]
    df = prices.load_prices("AAPL")
    assert df is not None
    assert len(df) == 5
    assert "adj_close" in df.columns
    assert prices.load_prices("MISSING") is None


def test_load_matrix_is_wide_by_ticker(data_dir: Path) -> None:
    idx = pd.date_range("2024-01-02", periods=4, freq="D")
    for t, base in (("AAA", 1.0), ("BBB", 10.0)):
        raw = pd.DataFrame({"Adj Close": [base + i for i in range(4)], "Volume": 1}, index=idx)
        prices.write_prices(t, raw)
    m = prices.load_matrix("adj_close")
    assert list(m.columns) == ["AAA", "BBB"]
    assert len(m) == 4
    assert m["BBB"].iloc[0] == 10.0


def test_safe_name_slashes(data_dir: Path) -> None:
    idx = pd.date_range("2024-01-02", periods=2, freq="D")
    raw = pd.DataFrame({"Adj Close": [1.0, 2.0], "Volume": 1}, index=idx)
    assert prices.write_prices("BAD/TICKER", raw) == 2  # writes BAD_TICKER.parquet
    assert prices.load_prices("BAD/TICKER") is not None
