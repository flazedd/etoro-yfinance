"""Tests for the Parquet price store and the EUR conversion.

The EUR conversion is where the silent 100× errors live (GBp vs GBP, share
count vs notional volume), so it's pinned against hand-computed values.
All filesystem tests run against a tmp data dir via MOMENTUM_DATA_DIR.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
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


def test_write_prices_fills_raw_and_clean_stores(data_dir: Path) -> None:
    # One absurd print and some pre-floor history: the raw store keeps the print
    # (floored at MIN_DATE), the clean store repairs it.
    idx = pd.DatetimeIndex(
        ["1998-06-01", "1999-01-04", "1999-01-05", "1999-01-06", "1999-01-07", "1999-01-08"]
    )
    px = [9.0, 10.0, 10.1, 5000.0, 10.2, 10.3]
    raw_in = pd.DataFrame({"Close": px, "Adj Close": px, "Volume": 100}, index=idx)
    assert prices.write_prices("AAA", raw_in) == 5  # clean row count, 1998 dropped

    raw = prices.load_prices("AAA", raw=True)
    clean = prices.load_prices("AAA")
    assert raw is not None
    assert clean is not None
    assert len(raw) == 5  # the floor applies to the raw store too
    assert str(raw.index[0]) == "1999-01-04"
    assert raw["close"].max() == pytest.approx(5000.0)  # untouched: it is the record
    assert bool(clean["close"].isna().iloc[2])  # cleaned: the bad print is gone
    assert prices.prices_dir(raw=True) != prices.prices_dir()
    assert prices.load_prices("MISSING", raw=True) is None


def test_eur_store_is_derived_from_the_clean_store(data_dir: Path) -> None:
    idx = pd.date_range("2020-01-02", periods=4, freq="D")
    px = [10.0, 10.1, 5000.0, 10.2]
    prices.write_prices("BBB", pd.DataFrame({"Close": px, "Adj Close": px, "Volume": 2}, index=idx))
    clean = prices.load_prices("BBB")
    assert clean is not None
    ecb = pd.DataFrame({"USD": 2.0}, index=idx)
    assert prices.write_prices_eur("BBB", clean, "USD", "us", ecb) == 4
    eur = prices.load_prices("BBB", eur=True)
    assert eur is not None
    # the NULL the filter left in the clean series is still NULL after conversion
    assert bool(eur["close"].isna().iloc[2])
    assert eur["close"].iloc[0] == pytest.approx(5.0)  # 10 USD @ 2 USD/EUR


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


# ── data-quality filter (runs at ingestion) ──────────────────────────────────
def _ohlcv(**cols: list[float]) -> pd.DataFrame:
    n = len(next(iter(cols.values())))
    return pd.DataFrame(cols, index=pd.date_range("2020-01-02", periods=n, freq="D"))


def test_clean_frame_enforces_the_date_floor() -> None:
    idx = pd.DatetimeIndex(["1998-12-30", "1999-01-04", "2000-06-05"])
    df = pd.DataFrame({"close": [1.0, 2.0, 3.0], "adj_close": [1.0, 2.0, 3.0]}, index=idx)
    out = prices.clean_frame(df)
    assert len(out) == 2  # MIN_DATE itself is kept
    assert str(out.index[0].date()) == "1999-01-04"
    assert prices.clean_frame(df.iloc[:1]).empty  # everything below the floor


def test_clean_frame_rebuilds_negative_adj_close() -> None:
    # The BZU.MI shape: adj_close = close × a NEGATIVE constant, then Yahoo
    # switches to a positive factor and the seam reads as a −103% day.
    close = [10.0, 10.2, 10.1, 10.3, 10.4]
    adj = [-20.0, -20.4, -20.2, 5.15, 5.2]  # factor −2.0, then +0.5
    out = prices.clean_frame(_ohlcv(close=close, adj_close=adj))
    a = out["adj_close"].astype("float64")
    assert (a > 0).all()  # no negative prices survive
    r = (a / a.shift(1) - 1.0).to_numpy()[1:]
    expected = pd.Series(close).pct_change().to_numpy()[1:]
    assert r == pytest.approx(expected, abs=1e-5)  # returns now track close throughout


def test_clean_frame_nulls_bad_prints() -> None:
    # A price that leaves and comes straight back is garbage: NULL just that bar.
    exc = prices.clean_frame(_ohlcv(close=[10.0, 10.1, 5000.0, 10.2, 10.3]))
    assert exc["close"].isna().sum() == 1
    assert exc["close"].iloc[-1] == pytest.approx(10.3)
    # FLTR.L's shape: one absurd print, level unchanged either side.
    spot = prices.clean_frame(_ohlcv(close=[6.42, 6.28, 2420.55, 6.28, 6.30]))
    c = spot["close"].astype("float64")
    assert bool(c.isna().iloc[2])
    assert c.iloc[1] == pytest.approx(6.28)  # neighbours untouched — no rescaling
    assert c.iloc[3] == pytest.approx(6.28)


def test_clean_frame_truncates_at_a_redenomination() -> None:
    # ZETA-USD's shape: ×10,000 and it stays. The old scale is a different
    # series, so it is dropped rather than spliced onto the new level.
    out = prices.clean_frame(_ohlcv(close=[0.001, 0.00102, 20.0, 20.4, 20.2]))
    assert len(out) == 3
    assert out["close"].iloc[0] == pytest.approx(20.0)
    r = (out["close"].astype("float64").pct_change()).to_numpy()[1:]
    assert r == pytest.approx([0.02, -0.0098], abs=1e-3)  # post-jump returns intact


def test_clean_frame_keeps_reverse_splits_and_penny_ticks() -> None:
    # QNCX's shape: 0.921 → 16.75 is a 1:20 reverse split, and `close` really
    # does multiply. Only the splits column can say so — adj_close is stored
    # equal to close on those bars.
    split = _ohlcv(
        close=[0.9, 0.92, 0.921, 16.75, 17.23, 17.0],
        splits=[0.0, 0.0, 0.05, 0.0, 0.0, 0.0],
    )
    out = prices.clean_frame(split)
    assert len(out) == 6  # nothing truncated
    assert out["close"].iloc[0] == pytest.approx(0.9)
    # MOND's shape: 0.0001 → 0.0010 is one tick at sub-penny quotation, ×10 —
    # below the ×100 bar, so it is not read as a rescale. The instrument is
    # rejected outright instead (see the admission tests), not truncated.
    tick = _ohlcv(close=[0.0001, 0.0001, 0.001, 0.001, 0.001])
    assert len(prices.clean_frame(tick, admit=False)) == 5
    assert prices.rejection_reason(tick) == "sub-penny"
    # PPCB's shape: a 1:2 split (×2) stamped on a bar that moves ×62,500. The
    # action explains nothing, so it stays a rescale and the old scale goes.
    unexplained = _ohlcv(
        close=[0.015, 0.015, 0.010, 625.0, 225.0, 250.0],
        splits=[0.0, 0.0, 0.0, 0.5, 0.0, 0.0],
    )
    assert len(prices.clean_frame(unexplained)) == 3


def test_clean_frame_applies_splits_yahoo_left_out_of_adj_close() -> None:
    # GDC's shape: a 1:250 reverse split that Yahoo applied to `close` but not
    # to `adj_close`, which then reads as a +20,650% return.
    df = _ohlcv(
        close=[0.014, 0.012, 2.49, 2.05, 2.26],
        adj_close=[0.014, 0.012, 2.49, 2.05, 2.26],
        splits=[0.0, 0.0, 0.004, 0.0, 0.0],
    )
    a = prices.clean_frame(df)["adj_close"].astype("float64")
    r = a.pct_change().to_numpy()
    assert abs(r[2]) < 0.35  # the split bar is a normal day again, not +20,650%
    assert a.iloc[0] > 1.0  # pre-split bars lifted onto the post-split scale
    assert r[3] == pytest.approx(2.05 / 2.49 - 1.0, abs=1e-4)  # later returns untouched


# ── instrument admission (in raw, out of clean) ──────────────────────────────
def test_frozen_instrument_is_rejected() -> None:
    live = _ohlcv(close=[10.0 + (i % 7) * 0.1 for i in range(200)])
    assert prices.rejection_reason(live) is None
    dead = _ohlcv(close=[10.0] * (prices.MAX_FROZEN_RUN + 5) + [10.0 + i * 0.1 for i in range(50)])
    assert prices.rejection_reason(dead) == "frozen"
    assert prices.clean_frame(dead).empty  # dropped from the clean store entirely
    assert len(prices.clean_frame(dead, admit=False)) == len(dead)  # bars still repairable
    # a shorter flat stretch is just an illiquid patch, not a dead listing
    quiet = _ohlcv(close=[10.0] * (prices.MAX_FROZEN_RUN - 5) + [10.0 + i * 0.1 for i in range(50)])
    assert prices.rejection_reason(quiet) is None


def test_frozen_run_is_broken_by_a_nulled_bar() -> None:
    # NaN never equals NaN, so a repaired bar must not stitch two flat runs into
    # one long one and get the instrument thrown out.
    half = prices.MAX_FROZEN_RUN // 2 + 2
    close = np.array([10.0] * half + [np.nan] + [10.0] * half)
    assert prices.longest_flat_run(close) < prices.MAX_FROZEN_RUN


def test_sub_penny_instrument_is_rejected() -> None:
    penny = _ohlcv(close=[0.004 + (i % 5) * 0.0001 for i in range(60)])
    assert prices.rejection_reason(penny) == "sub-penny"
    assert prices.clean_frame(penny).empty
    # judged on the median, so a name that only dipped under a cent survives
    dipped = _ohlcv(close=[0.005] * 10 + [0.5 + i * 0.01 for i in range(60)])
    assert prices.rejection_reason(dipped) is None


def test_rejected_instrument_stays_in_raw_but_leaves_clean(data_dir: Path) -> None:
    idx = pd.date_range("2020-01-02", periods=prices.MAX_FROZEN_RUN + 10, freq="D")
    flat = [5.0] * len(idx)
    assert prices.write_prices("DEAD", pd.DataFrame(
        {"Close": flat, "Adj Close": flat, "Volume": 1}, index=idx)) == 0
    assert prices.load_prices("DEAD", raw=True) is not None  # the record keeps it
    assert prices.load_prices("DEAD") is None  # research never sees it
    rep = json.loads((prices.quality_dir() / "DEAD.json").read_text())
    assert rep["admitted"] is False
    assert rep["reason"] == "frozen"


def test_previously_admitted_instrument_is_removed_when_it_goes_stale(data_dir: Path) -> None:
    idx = pd.date_range("2020-01-02", periods=80, freq="D")
    good = [10.0 + i * 0.1 for i in range(80)]
    assert prices.write_prices("XX", pd.DataFrame(
        {"Close": good, "Adj Close": good, "Volume": 1}, index=idx)) == 80
    assert prices.load_prices("XX") is not None
    # re-ingested later, now flatlined: the stale clean file must not survive
    flat = [10.0] * 80
    assert prices.write_prices("XX", pd.DataFrame(
        {"Close": flat, "Adj Close": flat, "Volume": 1}, index=idx)) == 0
    assert prices.load_prices("XX") is None


def test_quality_report_is_written_for_every_ingested_series(data_dir: Path) -> None:
    idx = pd.date_range("2020-01-02", periods=60, freq="D")
    px = [10.0 + i * 0.1 for i in range(60)]
    px[30] = 5000.0  # one bad print
    prices.write_prices("QQ", pd.DataFrame({"Close": px, "Adj Close": px, "Volume": 7}, index=idx))
    rep = json.loads((prices.quality_dir() / "QQ.json").read_text())
    assert rep["ticker"] == "QQ"
    assert rep["admitted"] is True
    assert rep["reason"] is None
    assert rep["raw"]["rows"] == 60
    assert rep["clean"]["cells"] < rep["raw"]["cells"]  # the bad print was nulled
    assert rep["worst_move"] > 100  # measured on the RAW series, before repair
    assert rep["raw"]["price_from"] == "2020-01-02"
    # both stores are described, which is what the universe page's toggle reads
    assert rep["clean"]["rows"] == 60
    assert rep["clean"]["vol_from"] == "2020-01-02"


def test_clean_frame_never_stores_a_value_float32_cannot_hold() -> None:
    out = prices.clean_frame(_ohlcv(close=[1e300, 1.0, 1.01, 1.0, 1.02]))
    assert bool(out["close"].isna().iloc[0])
    assert not np.isinf(out["close"].to_numpy()).any()


def test_clean_frame_nulls_high_low_that_contradict_the_bar() -> None:
    # The ING.L shape: open=high=low, close far outside the range.
    out = prices.clean_frame(
        _ohlcv(
            open=[31350.0, 100.0], high=[31350.0, 105.0],
            low=[31350.0, 99.0], close=[24750.0, 101.0],
        )
    )
    assert bool(out["high"].isna().iloc[0])
    assert bool(out["low"].isna().iloc[0])
    assert out["close"].iloc[0] == pytest.approx(24750.0)  # close is kept, it is the reliable one
    assert out["high"].iloc[1] == pytest.approx(105.0)  # a consistent bar is untouched


def test_clean_frame_keeps_real_moves_and_is_idempotent() -> None:
    # A crash, a rebound and a doubling that all persist — none is a bad print.
    real = _ohlcv(close=[100.0, 45.0, 52.0, 104.0, 106.0], adj_close=[100.0, 45.0, 52.0, 104.0, 106.0])
    once = prices.clean_frame(real)
    assert once["close"].notna().all()
    assert once["close"].tolist() == pytest.approx(real["close"].tolist())
    twice = prices.clean_frame(once)
    assert twice["close"].tolist() == pytest.approx(once["close"].tolist())


def test_clean_frame_leaves_volume_alone() -> None:
    out = prices.clean_frame(_ohlcv(close=[10.0, 5000.0, 10.1], volume=[7.0, 9.0, 11.0]))
    assert out["volume"].tolist() == [7.0, 9.0, 11.0]  # a bad price ≠ a bad volume


def test_write_prices_stores_cleaned_data(data_dir: Path) -> None:
    idx = pd.date_range("1998-12-31", periods=6, freq="D")
    raw = pd.DataFrame(
        {"Close": [9.9, 10.0, 10.1, 5000.0, 10.2, 10.3],
         "Adj Close": [9.9, 10.0, 10.1, 5000.0, 10.2, 10.3], "Volume": 100},
        index=idx,
    )
    n = prices.write_prices("TEST", raw)
    assert n == 2  # only 1999-01-04 and 1999-01-05 clear the floor
    df = prices.load_prices("TEST")
    assert df is not None
    assert str(df.index[0]) == "1999-01-04"


def _repair_frame(close: list[float], adj: list[float]) -> pd.DataFrame:
    idx = pd.date_range("2024-01-02", periods=len(close), freq="D")
    return pd.DataFrame({"close": close, "adj_close": adj}, index=idx)


def test_repair_adj_close_splices_out_adjustment_glitch() -> None:
    # adj_close jumps ×10 overnight while close moves −10% (the TELIA1.HE
    # shape): the level shift is divided out so the bar's return matches close.
    df = _repair_frame(close=[10.0, 10.0, 9.0, 9.0], adj=[1.0, 1.0, 9.0, 9.0])
    out = prices.repair_adj_close(df)
    assert out.iloc[0] == 1.0 and out.iloc[1] == 1.0
    assert out.iloc[2] == pytest.approx(0.9)  # follows close's −10%
    assert out.iloc[3] == pytest.approx(0.9)  # later bars rescaled too


def test_repair_adj_close_keeps_real_spikes_and_splits() -> None:
    # Real spike: close and adj_close jump together — no repair.
    spike = _repair_frame(close=[1.0, 5.0, 5.0], adj=[1.0, 5.0, 5.0])
    assert prices.repair_adj_close(spike).tolist() == [1.0, 5.0, 5.0]
    # Split: close halves, adj_close smooth — no repair (adj is the truth).
    split = _repair_frame(close=[10.0, 5.0, 5.0], adj=[9.0, 9.0, 9.0])
    assert prices.repair_adj_close(split).tolist() == [9.0, 9.0, 9.0]


def test_repair_adj_close_without_close_column_is_identity() -> None:
    df = pd.DataFrame({"adj_close": [1.0, 8.0]}, index=pd.date_range("2024-01-02", periods=2))
    assert prices.repair_adj_close(df).tolist() == [1.0, 8.0]
