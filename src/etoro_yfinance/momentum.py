"""Momentum strategy — signals + scoring, ported from bustelberg/bbterminal.

Faithful port of backend/momentum/signals.py (vectorized panel path) and
scoring.py. Operates on a plain {ticker: price Series} / {ticker: volume Series}
index — no DB. Signals are computed as rolling time series per ticker (one pass),
then read at each monthly cutoff; scoring min-max normalizes each signal within
its category, weight-averages to a 0-100 category score, then equal-weights the
categories into `momentum_score`. Selection takes top-N sectors × top-N per sector.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

MAX_STALENESS_DAYS = 30

# Default Momentum strategy signal defs (key, label, default_weight, group,
# description) — verbatim from bbterminal's PRICE_SIGNAL_DEFS.
PRICE_SIGNAL_DEFS: list[dict] = [
    {"key": "mom_12_1", "label": "12-1M Return", "default_weight": 3, "group": "price",
     "description": "12-month return skipping the most recent month (Jegadeesh-Titman)."},
    {"key": "mom_6m", "label": "6M Return", "default_weight": 2, "group": "price",
     "description": "Total price return over the last 6 months."},
    {"key": "volatility_adjusted_return_6m", "label": "Vol-Adj Return", "default_weight": 2,
     "group": "price", "description": "6M return ÷ annualized 6M volatility (Sharpe-like)."},
    {"key": "drawdown_from_recent_high_pct", "label": "Drawdown", "default_weight": 1,
     "group": "price", "description": "Current price vs 52-week high (closer to 0 = stronger)."},
    {"key": "above_200ma", "label": "Above 200 MA", "default_weight": 1, "group": "price",
     "description": "1 if price is above the 200-day moving average, else 0."},
    {"key": "vol_20d_vs_60d", "label": "Volume Surge", "default_weight": 1, "group": "volume",
     "description": "20-day avg volume ÷ 60-day avg volume (>1 = rising interest)."},
    {"key": "vol_trend_3m", "label": "Volume Trend 3M", "default_weight": 1, "group": "volume",
     "description": "% change in avg daily volume: current month vs 3 months ago."},
]
DEFAULT_WEIGHTS: dict[str, float] = {s["key"]: s["default_weight"] for s in PRICE_SIGNAL_DEFS}


def strategy_signals() -> list[dict]:
    """Signal defs grouped by category with each category's weight (equal per
    category — price and volume at 50% each)."""
    cats = _category_keys()
    cw = round(100.0 / len(cats))
    by_group: dict[str, list[dict]] = {}
    for s in PRICE_SIGNAL_DEFS:
        by_group.setdefault(s["group"], []).append(s)
    return [{"name": g, "weight_pct": cw, "signals": by_group[g]} for g in cats]

_PRICE_COLS = ("mom_12_1", "mom_6m", "volatility_adjusted_return_6m",
               "drawdown_from_recent_high_pct", "above_200ma")
_VOL_COLS = ("vol_20d_vs_60d", "vol_trend_3m")


# ── signal panels (rolling time series per ticker) ───────────────────────────
def _asof_values(series: pd.Series, targets: pd.DatetimeIndex) -> np.ndarray:
    if len(series) == 0:
        return np.full(len(targets), np.nan)
    pos = series.index.searchsorted(targets, side="right") - 1
    out = np.full(len(targets), np.nan)
    valid = pos >= 0
    if valid.any():
        out[valid] = series.values[pos[valid]]
    return out


def _price_panel(series: pd.Series) -> pd.DataFrame:
    idx = series.index
    if len(series) < 20:
        return pd.DataFrame(index=idx, columns=list(_PRICE_COLS), dtype="float64")
    vals = series.values
    num_1m = _asof_values(series, idx - pd.DateOffset(months=1))
    num_12m = _asof_values(series, idx - pd.DateOffset(months=12))
    num_6m = _asof_values(series, idx - pd.DateOffset(months=6))
    with np.errstate(divide="ignore", invalid="ignore"):
        mom_12_1 = np.round(np.where((num_12m > 0) & ~np.isnan(num_1m) & ~np.isnan(num_12m),
                                     (num_1m / num_12m - 1.0) * 100.0, np.nan), 2)
        mom_6m = np.round(np.where((num_6m > 0) & ~np.isnan(num_6m),
                                   (vals / num_6m - 1.0) * 100.0, np.nan), 2)
    std = series.pct_change().rolling(126, min_periods=2).std().values
    ann_vol = np.round(std * (252 ** 0.5) * 100.0, 2)
    with np.errstate(divide="ignore", invalid="ignore"):
        vol_adj = np.round(np.where((ann_vol > 0) & ~np.isnan(ann_vol) & ~np.isnan(mom_6m),
                                    mom_6m / ann_vol, np.nan), 4)
    rmax = series.rolling(252, min_periods=1).max().values
    with np.errstate(divide="ignore", invalid="ignore"):
        drawdown = np.round(np.where(rmax > 0, (vals / rmax - 1.0) * 100.0, np.nan), 2)
    ma200 = series.rolling(200, min_periods=1).mean().values
    above = np.where(ma200 == 0, np.nan, (vals > ma200).astype(float))
    return pd.DataFrame({"mom_12_1": mom_12_1, "mom_6m": mom_6m,
                         "volatility_adjusted_return_6m": vol_adj,
                         "drawdown_from_recent_high_pct": drawdown,
                         "above_200ma": above}, index=idx)


def _volume_panel(vol: pd.Series) -> pd.DataFrame:
    idx = vol.index
    if vol.empty or len(vol) < 20:
        return pd.DataFrame(index=idx, columns=list(_VOL_COLS), dtype="float64")
    short = vol.rolling(20, min_periods=20).mean().values
    long = vol.rolling(60, min_periods=60).mean().values
    with np.errstate(divide="ignore", invalid="ignore"):
        v20_60 = np.round(np.where((long > 0) & ~np.isnan(long) & ~np.isnan(short),
                                   short / long, np.nan), 4)
    recent = vol.rolling("21D", closed="right").mean()
    daily = vol.reindex(pd.date_range(idx[0], idx[-1], freq="D"))
    past_win = daily.rolling("21D", closed="both").mean()
    past = past_win.reindex(idx - pd.DateOffset(months=3) + pd.DateOffset(days=21)).values
    with np.errstate(divide="ignore", invalid="ignore"):
        vtrend = np.round(np.where((past > 0) & ~np.isnan(past) & ~np.isnan(recent.values),
                                   (recent.values / past - 1.0) * 100.0, np.nan), 2)
    return pd.DataFrame({"vol_20d_vs_60d": v20_60, "vol_trend_3m": vtrend}, index=idx)


def signals_at_cutoffs(price_index: dict[str, pd.Series], volume_index: dict[str, pd.Series],
                       sectors: dict[str, str], cutoffs: list[pd.Timestamp]) -> dict:
    """{cutoff: signals_df} — for each ticker, build its rolling panels once and
    read at each cutoff (strict `<`, 30-day staleness guard, ≥20 bars)."""
    cutoff_idx = pd.DatetimeIndex(cutoffs)
    per_cut: dict[pd.Timestamp, list[dict]] = {c: [] for c in cutoffs}
    for tkr, series in price_index.items():
        if series is None or len(series) < 20:
            continue
        pp = _price_panel(series)
        vol = volume_index.get(tkr)
        vp = _volume_panel(vol) if vol is not None and len(vol) else None
        positions = series.index.searchsorted(cutoff_idx, side="left") - 1
        for c, pos in zip(cutoffs, positions, strict=False):
            if pos < 0 or pos + 1 < 20:
                continue
            anchor = series.index[pos]
            if (c - anchor).days > MAX_STALENESS_DAYS:
                continue
            row = {"company_id": tkr, "sector": sectors.get(tkr)}
            row.update(pp.iloc[pos].to_dict())
            if vp is not None:
                vpos = vp.index.searchsorted(anchor, side="right") - 1
                if vpos >= 0 and vpos + 1 >= 20:
                    row.update({k: vp.iloc[vpos].get(k) for k in _VOL_COLS})
            per_cut[c].append(row)
    return {c: (pd.DataFrame(rows) if rows else pd.DataFrame()) for c, rows in per_cut.items()}


# ── scoring (ported from scoring.py) ─────────────────────────────────────────
def _category_keys() -> dict[str, list[str]]:
    cats: dict[str, list[str]] = {}
    for s in PRICE_SIGNAL_DEFS:
        cats.setdefault(s["group"], []).append(s["key"])
    return cats


def _score_category(df: pd.DataFrame, weights: dict, keys: list[str], col: str) -> pd.DataFrame:
    df = df.copy()
    active = {k: weights.get(k, 0) for k in keys if k in df.columns and weights.get(k, 0) != 0}
    if not active:
        df[col] = np.nan
        return df
    wsum = sum(abs(w) for w in active.values())
    score = np.zeros(len(df))
    for k, w in active.items():
        s = pd.to_numeric(df[k], errors="coerce").astype(float)
        lo, hi = s.min(), s.max()
        norm = pd.Series(0.5, index=df.index) if pd.isna(lo) or pd.isna(hi) or lo == hi \
            else (s - lo) / (hi - lo)
        score += norm.fillna(0.5).values * (w / wsum)
    df[col] = (score * 100).round(2)
    return df


def score_universe(signals_df: pd.DataFrame, weights: dict | None = None,
                   *, exclude_incomplete: bool = True) -> pd.DataFrame:
    if signals_df.empty:
        return signals_df
    weights = weights or DEFAULT_WEIGHTS
    cats = _category_keys()
    cw = {c: 1.0 / len(cats) for c in cats}          # equal category weight
    df = signals_df
    if exclude_incomplete and len(df):
        required = [k for cat, ks in cats.items() if cw.get(cat, 0) != 0
                    for k in ks if k in df.columns and weights.get(k, 0) != 0]
        if required:
            df = df[df[required].notna().all(axis=1)].copy()
    for cat, keys in cats.items():
        df = _score_category(df, weights, keys, f"score_{cat}")
    final = np.zeros(len(df))
    has_any = np.zeros(len(df), dtype=bool)
    for cat in cats:
        col = f"score_{cat}"
        if col in df.columns:
            has_any |= df[col].notna().values
            final += df[col].fillna(0).values * cw.get(cat, 0)
    df["momentum_score"] = np.where(has_any, np.round(final, 2), 50.0)
    return df


def select_from_scored(scored: pd.DataFrame, *, top_n_sectors: int = 4,
                       top_n_per_sector: int = 6, min_sector_size: int = 0) -> pd.DataFrame:
    if scored.empty:
        return pd.DataFrame()
    if min_sector_size > 0:                      # drop thin sectors before ranking
        sizes = scored.groupby("sector")["company_id"].transform("size")
        scored = scored[sizes.fillna(0) >= min_sector_size].copy()
        if scored.empty:
            return pd.DataFrame()
    sect = (scored.groupby("sector")["momentum_score"].mean()
            .sort_values(ascending=False).reset_index())
    chosen = sect.head(top_n_sectors)["sector"].tolist()
    if not chosen:
        return pd.DataFrame()
    rank = {s: i + 1 for i, s in enumerate(chosen)}
    inc = scored[scored["sector"].isin(chosen)].copy()
    if inc.empty:
        return pd.DataFrame()
    inc["sector_rank"] = inc["sector"].map(rank)
    inc = inc.sort_values(["sector_rank", "momentum_score"], ascending=[True, False])
    sel = inc.groupby("sector_rank", sort=False).head(top_n_per_sector).reset_index(drop=True)
    sel["company_rank"] = sel.groupby("sector_rank", sort=False).cumcount() + 1
    return sel
