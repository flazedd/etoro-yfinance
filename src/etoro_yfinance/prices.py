"""Local Parquet stores of daily OHLCV per instrument, for fast backtests.

Three stores, one file per yfinance ticker in each, **all floored at
``MIN_DATE`` (1999-01-04, the euro's first ECB fixing)**:

    data/prices_raw/    Yahoo's numbers as fetched, in our schema. The record.
    data/prices/        clean_frame(raw)  — what the research reads.
    data/prices_eur/    to_eur(clean)     — prices in EUR, volume = EUR turnover.

Each row:

    date        date32          (trading day, tz-naive)
    open/high/low/close         float32   (raw, unadjusted)
    adj_close                   float32   (split+dividend adjusted)
    volume                      int64
    dividends/splits            float32   (corporate actions on that day)

``write_prices`` fills the raw and clean stores together during the universe
validation pass (``scripts/etoro_universe.py --validate``), straight from the
same full-history download used to compute the coverage windows. The euro store
is derived from the clean one by ``scripts/build_eur_series.py``, and the clean
store can be rebuilt from raw at any time by ``scripts/clean_store.py`` — so
re-tuning the quality filter never means re-fetching from the network.

Read side:
    load_prices("AAPL")                 -> one ticker's clean DataFrame (or None)
    load_prices("AAPL", raw=True)       -> the same ticker, untouched
    load_matrix("adj_close", tickers)   -> wide date x ticker matrix for
                                           vectorized backtests
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from etoro_yfinance.web.data import data_dir

# yfinance column -> our schema.
_RENAME = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume",
    "Dividends": "dividends",
    "Stock Splits": "splits",
}
_FLOAT_COLS = ("open", "high", "low", "close", "adj_close", "dividends", "splits")


def prices_dir(eur: bool = False, raw: bool = False) -> Path:
    """One of the three stores. ``raw`` wins over ``eur``: there is no raw euro
    store, because the euro series is by definition derived from the clean one."""
    if raw:
        return data_dir() / "prices_raw"
    return data_dir() / ("prices_eur" if eur else "prices")


def _safe_name(ticker: str) -> str:
    # Yahoo tickers are filesystem-safe except for the odd '/' (e.g. junk symbols).
    return ticker.replace("/", "_")


def drop_unclosed(df: pd.DataFrame) -> pd.DataFrame:
    """Drop any bar dated today-or-later (UTC): the current session hasn't closed,
    so its candle is still moving. Backtests must only see completed daily bars.
    `df` is a DatetimeIndex-ed yfinance frame; returns the closed-bars subset."""
    today = datetime.now(UTC).date()
    idx = pd.to_datetime(df.index)
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    return df[idx.date < today]


# ── EUR conversion (derived series) ──────────────────────────────────────────
def load_ecb_rates() -> pd.DataFrame | None:
    """The ECB reference-rate table (date × CCY-per-EUR). None if not fetched."""
    p = data_dir() / "ecb_rates.parquet"
    return pd.read_parquet(p) if p.exists() else None


def to_eur(
    df: pd.DataFrame, ccy: str, status: str, ecb: pd.DataFrame | None
) -> pd.DataFrame | None:
    """Convert one native OHLCV frame to euros. Prices → EUR (sub-units handled);
    `volume` → EUR turnover (equities: price×shares; crypto: USD notional). Rates
    are forward-filled onto trading days; pre-1999 rows have no EUR and become NaN.
    Returns a DataFrame with the same columns (values in EUR) or None if the
    currency isn't in the ECB table."""
    from etoro_yfinance import currency as ccymod

    major, factor = ccymod.normalize(ccy)
    if ecb is None or major not in ecb.columns:
        return None
    idx = pd.to_datetime(df.index)  # date -> Timestamp
    rate = ecb[major].reindex(idx, method="ffill").to_numpy()  # CCY per EUR

    out = pd.DataFrame(index=df.index)
    for c in ("open", "high", "low", "close", "adj_close"):
        if c in df.columns:
            out[c] = ((df[c] / factor) / rate).astype("float32")
    if ccymod.is_notional_volume(status):  # crypto: volume is USD notional
        out["volume"] = (df["volume"] / rate).astype("float32")
    else:  # equity: turnover = price×shares
        out["volume"] = ((df["close"] / factor) * df["volume"] / rate).astype("float32")
    return out


def write_prices_eur(
    ticker: str, df: pd.DataFrame | None, ccy: str, status: str, ecb: pd.DataFrame | None
) -> int:
    """Derive and persist the EUR series for one ticker. Returns row count (0 if
    unconvertible)."""
    out = to_eur(df, ccy, status, ecb) if df is not None and len(df) else None
    if out is None or len(out) == 0:
        return 0
    # `df` is expected to be the CLEAN native series, so the euro store is
    # clean by construction; the floor is re-applied in case a caller passes
    # something else. Converting already-clean prices (rather than cleaning the
    # converted ones) keeps the two stores' NULLs and truncations identical.
    return _write(ticker, _cut(out), prices_dir(eur=True))


def _normalize(df: pd.DataFrame | None) -> pd.DataFrame | None:
    """A raw yfinance history frame -> tidy DataFrame with our schema + dtypes."""
    if df is None or len(df) == 0:
        return None
    if isinstance(df.columns, pd.MultiIndex):  # single-ticker MultiIndex
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    df = df.loc[:, ~df.columns.duplicated()]  # guard junk 2-ticker frames

    out = pd.DataFrame(index=df.index)
    for src, dst in _RENAME.items():
        if src in df.columns:
            out[dst] = df[src]

    dates = pd.to_datetime(out.index)
    if getattr(dates, "tz", None) is not None:
        dates = dates.tz_localize(None)
    out.insert(0, "date", dates.normalize().date if hasattr(dates, "date") else dates)
    out = out.reset_index(drop=True)
    out["date"] = pd.to_datetime(out["date"]).dt.date  # -> date32 in parquet

    for c in _FLOAT_COLS:
        if c in out.columns:
            out[c] = out[c].astype("float32")
    if "volume" in out.columns:
        out["volume"] = out["volume"].fillna(0).astype("int64")
    return out


def quality_dir() -> Path:
    return data_dir() / "quality"


def store_coverage(df: pd.DataFrame) -> dict[str, Any]:
    """One store's view of a series: how much of it there is, what it spans, and
    the handful of scalars that betray a bad OHLCV series.

    ``rows`` counts bars, ``cells`` the non-NULL prices among them (the two
    diverge where the filter nulled a bad print). Price and volume coverage are
    the first and last bar that actually carries one. The rest are quality
    tells, each aimed at a failure mode this store actually contains:

    * ``max_up`` / ``max_down`` — the extreme daily moves. A print error, an
      unadjusted split or a reused symbol all show up here first and nowhere
      else as clearly (TIA-USD's +68,063,638%).
    * ``flat_pct`` — share of bars whose price did not move at all. Catches
      dead listings, halted names and sub-penny quantization in one number;
      an active instrument sits near zero, a stub near 100%.
    * ``zero_vol_pct`` — share of bars that traded nothing. High means the
      price is a quote, not a trade, so its returns are not harvestable.
    * ``gap_days`` — the largest hole between consecutive bars. Separates a
      continuous history from one stitched across a delisting.
    * ``ohlc_bad`` — bars where ``close`` sits outside ``[low, high]``. A pure
      internal contradiction: it cannot be a real bar, so any count above zero
      means the source is unreliable (~19% of stocks, before repair).
    """
    cov: dict[str, Any] = {"rows": len(df), "cells": 0}
    for field, col in (("price", "adj_close"), ("vol", "volume")):
        cov[f"{field}_from"] = cov[f"{field}_to"] = None
        if col not in df.columns or df.empty:
            continue
        v = df[col].to_numpy(dtype="float64")
        with np.errstate(invalid="ignore"):
            have = np.isfinite(v) & (v > 0)
        if have.any():
            idx = np.where(have)[0]
            cov[f"{field}_from"] = str(df.index[idx[0]])[:10]
            cov[f"{field}_to"] = str(df.index[idx[-1]])[:10]
    cols = [c for c in _PRICE_COLS if c in df.columns]
    cov["cells"] = int(df[cols].notna().sum().sum()) if cols and len(df) else 0

    cov.update(
        max_up=None, max_down=None, flat_pct=None,
        zero_vol_pct=None, gap_days=None, ohlc_bad=None,
    )
    if df.empty:
        return cov

    price = "adj_close" if "adj_close" in df.columns else "close"
    if price in df.columns:
        p = df[price].to_numpy(dtype="float64")
        with np.errstate(invalid="ignore", divide="ignore"):
            r = np.empty(len(p), dtype="float64")
            r[0] = np.nan
            r[1:] = p[1:] / p[:-1] - 1.0
            fin = np.isfinite(r)
        if fin.any():
            cov["max_up"] = round(float(np.max(r[fin])), 4)
            cov["max_down"] = round(float(np.min(r[fin])), 4)
            cov["flat_pct"] = round(float(np.mean(r[fin] == 0.0) * 100), 2)

    if "volume" in df.columns:
        v = df["volume"].to_numpy(dtype="float64")
        with np.errstate(invalid="ignore"):
            fin = np.isfinite(v)
        if fin.any():
            cov["zero_vol_pct"] = round(float(np.mean(v[fin] == 0) * 100), 2)

    if len(df) > 1:
        days = pd.to_datetime(pd.Series(df.index)).diff().dt.days.to_numpy()[1:]
        if len(days) and np.isfinite(days).any():
            cov["gap_days"] = int(np.nanmax(days))

    if {"high", "low", "close"} <= set(df.columns):
        h, lo, c = (df[k].to_numpy(dtype="float64") for k in ("high", "low", "close"))
        o = df["open"].to_numpy(dtype="float64") if "open" in df.columns else c
        with np.errstate(invalid="ignore"):
            bad = (h < np.fmax.reduce([o, c, lo]) * (1 - _OHLC_TOL)) | (
                lo > np.fmin.reduce([o, c, h]) * (1 + _OHLC_TOL)
            )
        cov["ohlc_bad"] = int(np.nansum(bad))
    return cov


def quality_report(ticker: str, raw: pd.DataFrame, clean: pd.DataFrame) -> dict[str, Any]:
    """What the filter found and did for one series. Written at ingestion for
    every instrument, so the store is always auditable without a rescan
    (``scripts/data_quality.py`` aggregates these).

    ``raw`` and ``clean`` hold that store's :func:`store_coverage`, which is what
    the universe page's raw/clean toggle reads."""
    admitted = len(clean) > 0
    rep: dict[str, Any] = {
        "ticker": ticker,
        "admitted": admitted,
        "reason": None if admitted else (rejection_reason(_repaired_view(raw)) or "empty"),
        "raw": store_coverage(raw),
        "clean": store_coverage(clean),
    }
    if "close" in raw.columns:
        c = raw["close"].to_numpy(dtype="float64")
        with np.errstate(invalid="ignore", divide="ignore"):
            r = np.empty(len(c), dtype="float64")
            if len(c):
                r[0] = np.nan
                r[1:] = c[1:] / c[:-1] - 1.0
            finite = np.isfinite(r)
            rep["worst_move"] = round(float(np.max(np.abs(r[finite]))), 4) if finite.any() else None
            rep["frozen_run"] = longest_flat_run(c)
            rep["median_price"] = (
                round(float(np.nanmedian(c)), 6) if np.isfinite(c).any() else None
            )
    return rep


def _repaired_view(raw: pd.DataFrame) -> pd.DataFrame:
    """The bar-level repair without the admission check — so a rejected series
    can still report *why* it was rejected."""
    out = clean_frame(raw, admit=False)
    return out if len(out) else raw


def write_quality(ticker: str, report: dict[str, Any]) -> None:
    d = quality_dir()
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{_safe_name(ticker)}.json").write_text(json.dumps(report))


def _write(ticker: str, df: pd.DataFrame, d: Path) -> int:
    """Persist a date-indexed frame to one store. Returns the row count."""
    if len(df) == 0:
        return 0
    d.mkdir(parents=True, exist_ok=True)
    df.reset_index().to_parquet(d / f"{_safe_name(ticker)}.parquet", index=False)
    return len(df)


def write_prices(ticker: str, df: pd.DataFrame | None) -> int:
    """Persist one ticker to the raw **and** clean stores. Returns the clean row
    count (what the research will see).

    The raw store keeps Yahoo's numbers as fetched, in our schema and floored at
    ``MIN_DATE`` — nothing else is touched, so the filter can be re-tuned and
    the clean store rebuilt from it (``scripts/clean_store.py``) without going
    back to the network. Ingestion is where quality is enforced
    (:func:`clean_frame`), so readers of the clean store assume it is clean."""
    out = _normalize(df)
    if out is None or len(out) == 0:
        return 0
    out = out.set_index("date")
    raw = _cut(out)
    clean = clean_frame(out)
    _write(ticker, raw, prices_dir(raw=True))
    n = _write(ticker, clean, prices_dir())
    if n == 0:  # rejected now, but it may have been admitted by an earlier run
        for d in (prices_dir(), prices_dir(eur=True)):
            (d / f"{_safe_name(ticker)}.parquet").unlink(missing_ok=True)
    write_quality(ticker, quality_report(ticker, raw, clean))
    return n


def available_tickers(eur: bool = False) -> list[str]:
    d = prices_dir(eur=eur)
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.parquet"))


def load_prices(
    ticker: str, eur: bool = False, columns: Iterable[str] | None = None, raw: bool = False
) -> pd.DataFrame | None:
    """One ticker's OHLCV DataFrame (date-indexed), or None if not stored. With
    eur=True, returns the derived euro series (prices in EUR, `volume` = EUR
    turnover). `columns` restricts the read to those fields (parquet is columnar,
    so unread columns cost nothing); None loads everything.

    What is stored is already clean — :func:`clean_frame` runs at ingestion, so
    readers never repair anything. ``raw=True`` reads the untouched Yahoo store
    instead: for auditing the data or re-tuning the filter, not for research."""
    p = prices_dir(eur=eur, raw=raw) / f"{_safe_name(ticker)}.parquet"
    if not p.exists():
        return None
    cols = None
    if columns is not None:
        # Requested fields may be absent from older files — read what exists
        # and let the caller notice the missing column.
        avail = set(pq.read_schema(p).names)
        cols = ["date", *(c for c in columns if c in avail)]
    return pd.read_parquet(p, columns=cols).set_index("date").sort_index()


# ══════════════════════════════════════════════════════════════════════════════
# Data-quality filter — raw Yahoo OHLCV in, analysis-ready OHLCV out.
#
# Audited over the whole store (9,432 tickers / 41.1M bars), four defects are
# common enough to matter. Each is repaired here so no consumer has to know:
#
#   1. pre-MIN_DATE history — thin, badly adjusted, and survivorship-dominated.
#   2. negative `adj_close` — Yahoo applies a negative adjustment factor to some
#      long-history dividend payers (BZU.MI: close 4.66, adj_close -95.83 for
#      3,397 bars). Returns inside the block survive (negative ÷ negative), so
#      nothing traps it, but the bar where it flips sign reads as -103%.
#   3. bad prints — an excursion (price leaves and comes back) or a rescale (a
#      jump that persists, e.g. a reused crypto symbol: ZETA-USD 0.000068 →
#      1.6708). One name printing +68,063,638% dominates any index it enters.
#   4. OHLC that contradicts itself — `close` outside [low, high] on 0.11% of
#      bars, ~19% of stocks (ING.L: open=high=low=31350 with close=24750). CLV
#      and Parkinson-range signals read pure noise off those bars.
#
# Thresholds are deliberately loose: every rule must leave a real crash, a real
# rally and a split untouched. Bad bars are rare (~0.1% of the store), so the
# cost of a slightly conservative rule is negligible and the cost of a
# false positive — deleting a genuine move — is not.
# ══════════════════════════════════════════════════════════════════════════════
# Hard floor: nothing before this is served by any store. Set to the euro's
# first ECB fixing, so the three stores cover the same span — the euro series
# cannot exist before it whatever the native stores hold.
MIN_DATE = pd.Timestamp("1999-01-04")

RESCALE_MIN = 99.0  # ×100 in a bar, and it sticks → the series was redenominated
PRINT_RATIO = 5.0  # a bar this far from its local median is a bad print

# Instrument admission. These reject the *whole series* rather than repair bars:
# the data is not wrong, the instrument is untradeable, and carrying it quietly
# distorts anything vol-aware. Both keep their raw history — only the clean and
# euro stores drop them.
MAX_FROZEN_RUN = 60  # identical closes in a row (~a quarter): dead, halted or untraded
MIN_PRICE = 0.01  # median close under a cent: one tick is a whole return
_LEVEL_WINDOW = 5  # bars each side used to read the local price level
_SPLIT_TOL = 0.35  # how exactly an adj_close jump must match 1/split to be one
_OHLC_TOL = 1e-4  # float32 slack when testing high/low against open/close
_F32_MAX = float(np.finfo("float32").max)
_PRICE_COLS = ("open", "high", "low", "close", "adj_close")


def _split_correction(adj: np.ndarray, splits: np.ndarray) -> np.ndarray:
    """Per-bar factor that adjusts ``adj_close`` for splits Yahoo failed to apply.

    ``adj_close`` is supposed to be split-adjusted, so it should not move on a
    split bar. For 15 tickers it does — GDC's 1:250 reverse split lands in
    ``adj_close`` as a +20,650% return, dwarfing every glitch this filter was
    written for. The tell is that the jump equals exactly 1/split, so lifting
    every earlier bar by that factor restores the true return.

    :func:`repair_adj_close` cannot see these: on a reverse split ``close``
    jumps by the same factor, so the two series agree and nothing looks broken.
    """
    with np.errstate(invalid="ignore", divide="ignore"):
        fa = np.empty(len(adj), dtype="float64")
        fa[0] = np.nan
        fa[1:] = adj[1:] / adj[:-1]
        s = np.nan_to_num(splits, nan=0.0)
        unapplied = (s != 0) & (np.abs(fa * s - 1.0) < _SPLIT_TOL) & (np.abs(fa - 1.0) > 0.5)
    if not unapplied.any():
        return np.ones(len(adj), dtype="float64")
    factors = np.where(unapplied, np.where(s != 0, 1.0 / np.where(s == 0, 1.0, s), 1.0), 1.0)
    return np.concatenate([np.cumprod(factors[::-1])[::-1][1:], [1.0]])


def _local_levels(close: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Median price of the window before each bar, and of the window after it.
    Medians ignore NULLs, so bars already discarded do not set the level."""
    s = pd.Series(close)
    before = s.rolling(_LEVEL_WINDOW, min_periods=1).median().shift(1).to_numpy()
    after = s[::-1].rolling(_LEVEL_WINDOW, min_periods=1).median()[::-1].shift(-1).to_numpy()
    return before, after


def _bad_print_mask(close: np.ndarray) -> np.ndarray:
    """Bars whose price disagrees with the neighbourhood on *both* sides.

    A two-sided Hampel test: a bar more than ``PRINT_RATIO``× away from the
    median of the bars before it **and** from the median of the bars after it is
    garbage — 2420.55 in a series trading at 6.28, or 0.002 where the price is
    0.131. Requiring both sides is what lets a genuine level shift through: at a
    redenomination the new price disagrees with the past but agrees with the
    future, so it is a rescale (spliced) rather than a print (nulled).

    A real crash, rally or split moves both medians with it and never trips the
    ratio. A 5× move inside five bars that then persists would — for real
    instruments that is a rescale, which is exactly how it is then treated.
    """
    before, after = _local_levels(close)
    with np.errstate(invalid="ignore", divide="ignore"):
        off_b = (close / before >= PRINT_RATIO) | (close / before <= 1.0 / PRINT_RATIO)
        off_a = (close / after >= PRINT_RATIO) | (close / after <= 1.0 / PRINT_RATIO)
        return np.isfinite(close) & off_b & off_a


def _rescale_start(close: np.ndarray, splits: np.ndarray | None) -> int:
    """Index of the first trustworthy bar: everything before the last
    redenomination is a different price scale and is dropped.

    A jump of ``RESCALE_MIN``× that *stays* at the new level means the symbol
    was reused or the series redenominated (ZETA-USD: 0.000060 → 1.6708 and
    never back; OP-USD ×2001). The pre-jump bars are then not this instrument's
    prices, so they are truncated rather than spliced onto the new level:
    splicing fabricates a history, and repeated corrections compound — FLTR.L
    reached a 1e52 factor and overflowed float32 before this was truncation.

    Two exemptions keep real corporate actions and penny-tick noise out:

    * a bar whose **split explains the step** is a reverse split, where ``close``
      genuinely multiplies (QNCX 0.921 → 16.75 with ``splits`` 0.05 — a 1:20).
      It looks identical to a rescale in the price alone, and ``adj_close``
      cannot tell them apart because Yahoo stores it equal to ``close`` on those
      bars. The split must *account* for the jump: PPCB carries a 1:2 split
      (×2) on a bar that moves ×62,500, so the action explains nothing and the
      bar is still a rescale.
    * the threshold sits at ×100, well above the ×10-ish steps produced by
      sub-penny quantization, where one tick is the whole price (MOND ticks
      0.0001 → 0.0010 and that is a single increment, not a 900% return).
    """
    n = len(close)
    valid = pd.Series(close).ffill().to_numpy()  # compare consecutive *valid* prices
    before, after = _local_levels(close)
    with np.errstate(invalid="ignore", divide="ignore"):
        step = np.empty(n, dtype="float64")
        step[0] = np.nan
        step[1:] = valid[1:] / valid[:-1]
        persistent = after / before >= 1.0 + RESCALE_MIN
        jump = (step - 1.0 >= RESCALE_MIN) & persistent & np.isfinite(close)
    if splits is not None:
        s = np.nan_to_num(splits, nan=0.0)
        with np.errstate(invalid="ignore", divide="ignore"):
            # the action accounts for the step: price multiplies by 1/split
            explained = (s != 0) & (np.abs(step * s - 1.0) < _SPLIT_TOL)
        for shift in (-1, 0, 1):  # the split may be stamped a bar either side
            jump &= ~np.roll(explained, shift)
    return int(np.where(jump)[0][-1]) if jump.any() else 0


def longest_flat_run(close: np.ndarray) -> int:
    """Longest run of identical consecutive closes. NULLs break a run (NaN never
    equals NaN), so a repaired bar does not stitch two flat stretches together."""
    if len(close) < 2:
        return 0
    same = np.zeros(len(close), dtype=bool)
    with np.errstate(invalid="ignore"):
        same[1:] = close[1:] == close[:-1]
    best = run = 0
    for s in same:
        run = run + 1 if s else 0
        best = max(best, run)
    return int(best)


def rejection_reason(df: pd.DataFrame) -> str | None:
    """Why this instrument does not belong in the clean store, or None to admit.

    Judged on the *repaired* series, so it answers "is there a tradeable
    instrument here", not "did Yahoo send us junk":

    * ``frozen`` — ``MAX_FROZEN_RUN`` identical closes in a row. A flat stretch
      is not a wrong price, it is a dead or halted listing, and it reads as zero
      volatility: it flatters vol-targeting, Sortino and every low-vol signal.
    * ``sub-penny`` — a median close under ``MIN_PRICE``. At that level one tick
      is a large fraction of the price (MOND ticks 0.0001 → 0.0010, +900%), so
      the return series is quantization noise whatever the filter does.
    """
    col = next((c for c in ("close", "adj_close") if c in df.columns), None)
    if col is None or df.empty:
        return "empty"
    close = df[col].to_numpy(dtype="float64")
    if not np.isfinite(close).any():
        return "empty"
    if longest_flat_run(close) >= MAX_FROZEN_RUN:
        return "frozen"
    if float(np.nanmedian(close)) < MIN_PRICE:
        return "sub-penny"
    return None


def _cut(df: pd.DataFrame) -> pd.DataFrame:
    """Rows at or after ``MIN_DATE``. Applied to all three stores."""
    idx = pd.to_datetime(pd.Series(df.index, index=df.index))
    return df[(idx >= MIN_DATE).to_numpy()]


def _null_impossible(out: pd.DataFrame, present: list[str]) -> None:
    """NULL prices that cannot be prices: missing, zero, negative, or beyond
    what the float32 store can hold. Mutates `out` in place."""
    for c in present:
        v = out[c].to_numpy(dtype="float64", copy=True)
        with np.errstate(invalid="ignore"):
            v[~np.isfinite(v) | (v <= 0) | (np.abs(v) > _F32_MAX)] = np.nan
        out[c] = v


def clean_frame(df: pd.DataFrame, admit: bool = True) -> pd.DataFrame:
    """Raw Yahoo OHLCV → analysis-ready OHLCV. Pure; safe to apply twice.

    Runs at **ingestion** (:func:`write_prices`, :func:`write_prices_eur`), so
    everything in the store is already clean and no reader repairs anything. In
    order: cut to ``MIN_DATE``; NULL impossible prices; rebuild ``adj_close``
    (sign dropped, level shifts spliced); splice out rescales; NULL excursion
    bars; NULL ``high``/``low`` on bars where they contradict ``open``/``close``.
    ``volume`` is never altered — a bad price does not make its volume wrong.

    Finally :func:`rejection_reason` decides whether there is a tradeable
    instrument here at all; if not the frame comes back **empty** and the series
    is left out of the clean store entirely (it stays in the raw one). Pass
    ``admit=False`` to skip that and get the repaired bars regardless.

    Date-indexed frame in, date-indexed frame out.
    """
    if df is None or df.empty:
        return df
    out = _cut(df).copy()
    if out.empty:
        return out
    present = [c for c in _PRICE_COLS if c in out.columns]
    if "adj_close" in out.columns:
        # Yahoo's negative adjustment factor carries no information. Drop the
        # sign FIRST — before the validity pass below would read those bars as
        # missing — then let the splice repair the seam it leaves behind.
        out["adj_close"] = out["adj_close"].astype("float64").abs()

    _null_impossible(out, present)
    if "adj_close" in out.columns:
        if "splits" in out.columns:  # a split Yahoo left out of the adjustment
            out["adj_close"] = out["adj_close"].to_numpy(dtype="float64") * _split_correction(
                out["adj_close"].to_numpy(dtype="float64"),
                out["splits"].to_numpy(dtype="float64"),
            )
        out["adj_close"] = repair_adj_close(out)

    if "close" in out.columns:
        # Null bad prints first: a garbage stretch would otherwise set the
        # median that decides whether a jump is a persistent redenomination.
        bad = _bad_print_mask(out["close"].to_numpy(dtype="float64"))
        for c in present:
            v = out[c].to_numpy(dtype="float64", copy=True)
            v[bad] = np.nan  # the price was wrong on those bars
            out[c] = v
        splits = out["splits"].to_numpy(dtype="float64") if "splits" in out.columns else None
        start = _rescale_start(out["close"].to_numpy(dtype="float64"), splits)
        if start:
            out = out.iloc[start:].copy()  # the older scale is a different series
            present = [c for c in _PRICE_COLS if c in out.columns]

    if {"high", "low"} <= set(out.columns):
        o = out["open"].to_numpy(dtype="float64") if "open" in out.columns else None
        c = out["close"].to_numpy(dtype="float64") if "close" in out.columns else None
        hi = out["high"].to_numpy(dtype="float64")
        lo = out["low"].to_numpy(dtype="float64")
        ends = [x for x in (o, c) if x is not None]
        with np.errstate(invalid="ignore"):
            bad = np.zeros(len(hi), dtype=bool)
            if ends:  # the range must contain the bars it brackets
                bad |= hi < np.fmax.reduce([*ends, lo]) * (1 - _OHLC_TOL)
                bad |= lo > np.fmin.reduce([*ends, hi]) * (1 + _OHLC_TOL)
            bad |= hi < lo
        out.loc[bad, ["high", "low"]] = np.nan

    _null_impossible(out, present)  # again: splicing can push a value out of range
    for c in present:  # the store is float32; keep it that way
        out[c] = out[c].astype("float32")
    if admit and rejection_reason(out) is not None:  # not an instrument, not just bad bars
        return out.iloc[:0]
    return out


# On a clean bar the adj_close daily factor equals the close daily factor
# (dividends and splits shift close, never adj_close returns). When they
# diverge beyond this ratio the adjustment chain is corrupt for that bar.
_GLITCH_RATIO = 1.8


def repair_adj_close(df: pd.DataFrame) -> pd.Series:
    """`adj_close` with broken-adjustment level shifts spliced out.

    Yahoo's dividend/split factors are occasionally corrupt (e.g. TELIA1.HE
    prints persistent ×14 / ×2 overnight jumps in adj_close while close moves
    normally). A bar whose adj_close return diverges from its close return by
    ≥×1.8 — while close itself stays inside a ±2× day (so split bars, where
    close is the one that moves, are exempt) — is repaired by rescaling the
    series from that bar on, making the bar's return match the raw close.
    Real spikes (where both series jump together) are untouched."""
    s = df["adj_close"].astype("float64")
    if "close" not in df.columns:
        return s
    fa = s / s.shift(1)
    fc = (df["close"].astype("float64") / df["close"].shift(1)).fillna(1.0)
    r = fa / fc
    bad = ((r > _GLITCH_RATIO) | (r < 1 / _GLITCH_RATIO)) & (fc < 2.0) & (fc > 0.5)
    if not bad.any():
        return s
    corr = (fc[bad] / fa[bad]).reindex(s.index).fillna(1.0).cumprod()
    return s * corr


def load_matrix(
    field: str = "adj_close", tickers: Iterable[str] | None = None, eur: bool = False
) -> pd.DataFrame:
    """Wide date x ticker matrix of one field — the fast path for cross-sectional
    / vectorized backtests (feed straight to vectorbt, polars, or numpy).
    Missing cells are NaN where a ticker's history doesn't span the date. With
    eur=True, reads the euro-converted store."""
    names = list(tickers) if tickers is not None else available_tickers(eur=eur)
    cols = {}
    for t in names:
        p = prices_dir(eur=eur) / f"{_safe_name(t)}.parquet"
        if not p.exists():
            continue
        s = pd.read_parquet(p, columns=["date", field])
        cols[t] = s.set_index("date")[field]
    if not cols:
        return pd.DataFrame()
    return pd.DataFrame(cols).sort_index()
