"""Local Parquet store of daily OHLCV per instrument, for fast backtests.

One file per yfinance ticker at ``data/prices/<ticker>.parquet``:

    date        date32          (trading day, tz-naive)
    open/high/low/close         float32   (raw, unadjusted)
    adj_close                   float32   (split+dividend adjusted)
    volume                      int64
    dividends/splits            float32   (corporate actions on that day)

Written during the universe validation pass (``scripts/etoro_universe.py
--validate``) straight from the same full-history download used to compute the
coverage windows — one fetch, both outputs.

Read side:
    load_prices("AAPL")                 -> one ticker's DataFrame (or None)
    load_matrix("adj_close", tickers)   -> wide date x ticker matrix for
                                           vectorized backtests
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from etoro_yfinance.web.data import data_dir

# yfinance column -> our schema.
_RENAME = {
    "Open": "open", "High": "high", "Low": "low", "Close": "close",
    "Adj Close": "adj_close", "Volume": "volume",
    "Dividends": "dividends", "Stock Splits": "splits",
}
_FLOAT_COLS = ("open", "high", "low", "close", "adj_close", "dividends", "splits")


def prices_dir(eur: bool = False) -> Path:
    return data_dir() / ("prices_eur" if eur else "prices")


def _safe_name(ticker: str) -> str:
    # Yahoo tickers are filesystem-safe except for the odd '/' (e.g. junk symbols).
    return ticker.replace("/", "_")


def drop_unclosed(df):
    """Drop any bar dated today-or-later (UTC): the current session hasn't closed,
    so its candle is still moving. Backtests must only see completed daily bars.
    `df` is a DatetimeIndex-ed yfinance frame; returns the closed-bars subset."""
    import pandas as pd
    from datetime import UTC, datetime

    today = datetime.now(UTC).date()
    idx = pd.to_datetime(df.index)
    try:
        idx = idx.tz_localize(None)
    except (TypeError, AttributeError):
        pass  # already tz-naive
    return df[idx.date < today]


# ── EUR conversion (derived series) ──────────────────────────────────────────
def load_ecb_rates():
    """The ECB reference-rate table (date × CCY-per-EUR). None if not fetched."""
    import pandas as pd

    p = data_dir() / "ecb_rates.parquet"
    return pd.read_parquet(p) if p.exists() else None


def to_eur(df, ccy: str, status: str, ecb):
    """Convert one native OHLCV frame to euros. Prices → EUR (sub-units handled);
    `volume` → EUR turnover (equities: price×shares; crypto: USD notional). Rates
    are forward-filled onto trading days; pre-1999 rows have no EUR and become NaN.
    Returns a DataFrame with the same columns (values in EUR) or None if the
    currency isn't in the ECB table."""
    import pandas as pd

    from etoro_yfinance import currency as ccymod

    major, factor = ccymod.normalize(ccy)
    if ecb is None or major not in ecb.columns:
        return None
    idx = pd.to_datetime(df.index)                       # date -> Timestamp
    rate = ecb[major].reindex(idx, method="ffill").to_numpy()  # CCY per EUR

    out = pd.DataFrame(index=df.index)
    for c in ("open", "high", "low", "close", "adj_close"):
        if c in df.columns:
            out[c] = ((df[c] / factor) / rate).astype("float32")
    if ccymod.is_notional_volume(status):                # crypto: volume is USD notional
        out["volume"] = (df["volume"] / rate).astype("float32")
    else:                                                # equity: turnover = price×shares
        out["volume"] = ((df["close"] / factor) * df["volume"] / rate).astype("float32")
    return out


def write_prices_eur(ticker: str, df, ccy: str, status: str, ecb) -> int:
    """Derive and persist the EUR series for one ticker. Returns row count (0 if
    unconvertible)."""
    out = to_eur(df, ccy, status, ecb) if df is not None and len(df) else None
    if out is None or len(out) == 0:
        return 0
    d = prices_dir(eur=True)
    d.mkdir(parents=True, exist_ok=True)
    out.reset_index().to_parquet(d / f"{_safe_name(ticker)}.parquet", index=False)
    return len(out)


def _normalize(df):
    """A raw yfinance history frame -> tidy DataFrame with our schema + dtypes."""
    import pandas as pd

    if df is None or len(df) == 0:
        return None
    if isinstance(df.columns, pd.MultiIndex):          # single-ticker MultiIndex
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    df = df.loc[:, ~df.columns.duplicated()]           # guard junk 2-ticker frames

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


def write_prices(ticker: str, df) -> int:
    """Normalize and persist one ticker's history. Returns the row count."""
    out = _normalize(df)
    if out is None or len(out) == 0:
        return 0
    d = prices_dir()
    d.mkdir(parents=True, exist_ok=True)
    out.to_parquet(d / f"{_safe_name(ticker)}.parquet", index=False)
    return len(out)


def available_tickers(eur: bool = False) -> list[str]:
    d = prices_dir(eur=eur)
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.parquet"))


def load_prices(ticker: str, eur: bool = False):
    """One ticker's OHLCV DataFrame (date-indexed), or None if not stored. With
    eur=True, returns the derived euro series (prices in EUR, `volume` = EUR
    turnover)."""
    import pandas as pd

    p = prices_dir(eur=eur) / f"{_safe_name(ticker)}.parquet"
    if not p.exists():
        return None
    return pd.read_parquet(p).set_index("date").sort_index()


def load_matrix(field: str = "adj_close", tickers: Iterable[str] | None = None,
                eur: bool = False):
    """Wide date x ticker matrix of one field — the fast path for cross-sectional
    / vectorized backtests (feed straight to vectorbt, polars, or numpy).
    Missing cells are NaN where a ticker's history doesn't span the date. With
    eur=True, reads the euro-converted store."""
    import pandas as pd

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
