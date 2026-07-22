"""Regime monitor — 200-day-MA bull/bear labelling per universe sector.

Each sector's timeseries is the **equal-weighted index of every instrument in
that sector** (taken straight from the universe — no manual membership). Each
day is labelled `bull`/`bear` by whether that index sits above or below its
200-day moving average (no dwell — the label flips the day the index crosses),
and reported two ways — filtered (sit in cash when the *previous* day was bear)
vs always-in — via CAGR / Sharpe / Sortino. No trading; analysis only.

Storage is project-native: sectors + constituents come from the curated
`backtest` universe (fallback: the enriched snapshot); the derived per-sector
series + metrics are cached to ``data/monitor/sector_<name>.json`` by
:func:`run_daily_update`. Prices come from the local Parquet store, always run
through ``repair_adj_close`` (CLAUDE.md mandate).

All formulas follow the build spec §5–§7 exactly; the constants are §8.
"""

from __future__ import annotations

import json
import math
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from etoro_yfinance import prices
from etoro_yfinance.web.data import data_dir

# ── §8 fixed parameters ───────────────────────────────────────────────────────
MA_LENGTH = 200  # days in the moving average
INDEX_BASE = 100.0  # starting index value
TRADING_DAYS_YR = 252  # annualization constant

# "Vol-target" A/B variant — instead of a binary in/out, size the position
# inversely to recent volatility (still gated bear→cash by the 200-SMA trend):
# exposure = min(CAP, target/realized), where target is the index's own trailing
# median realized vol (lookahead-free), so it de-risks in turbulence and re-risks
# in calm. Attacks Sharpe/Sortino + the crash tail without relying on whipsaw.
VOL_WINDOW = 60  # trailing days for realized volatility
VOL_CAP = 1.0  # max exposure (1.0 = no leverage; the brake can only de-risk)

# Each family is reported three ways: `_always` (buy & hold), `_sma` (the raw
# 200-day-SMA cross — "old") and `_vol` (the vol-targeted variant — "new").
# Higher is better for all four families (a shallower max-DD is a higher, less
# negative number), so a filter "wins" a sector when its value exceeds always-in.
_METRIC_FAMILIES = ("sharpe", "sortino", "cagr", "maxdd")
_METRIC_VARIANTS = ("always", "sma", "vol")
METRIC_KEYS = tuple(f"{fam}_{v}" for fam in _METRIC_FAMILIES for v in _METRIC_VARIANTS)

# The two toggleable filters (label column, since, chart shading, table metrics).
# Both take their bull/bear direction from the 200-SMA trend; `vol` differs only
# in position size, so it shares the trend label but has its own metrics.
FILTERS = ("sma", "vol")
FILTER_LABELS = {"sma": "200-SMA", "vol": "Vol-target"}
_VARIANT_LABEL_COL = {"sma": "confirmed_label", "vol": "confirmed_label"}


class MonitorError(Exception):
    """Base for user-facing monitor errors."""


class NotFoundError(MonitorError):
    """A sector does not exist (→ 404)."""


# ══════════════════════════════════════════════════════════════════════════════
# Pure compute — no I/O, directly unit-tested.
# ══════════════════════════════════════════════════════════════════════════════
def confirmed_labels(raw: list[str | None]) -> list[str]:
    """The label per day: simply the raw MA-crossover result (bull = index ≥ its
    200-day MA, bear = below). No dwell — the label flips the day the index
    crosses. Bull is the neutral default before the MA exists (raw ``None``)."""
    conf: list[str] = ["bull"] * len(raw)
    for t in range(len(raw)):
        if raw[t] is not None:
            conf[t] = raw[t]  # type: ignore[assignment]
        elif t > 0:
            conf[t] = conf[t - 1]  # pre-MA: hold the neutral default
    return conf


_COLS = ["group_return", "index_value", "ma_200", "raw_label", "confirmed_label"]


def _finalize(group_return: pd.Series) -> pd.DataFrame:
    """Equal-weighted daily returns → the per-day table (compound index §5.3,
    200-day MA §6.1, raw §6.2 crossover = the label — bull above, bear below)."""
    if group_return is None or len(group_return) == 0:
        return pd.DataFrame(columns=_COLS)
    grid = pd.DatetimeIndex(group_return.index)
    gr = group_return.to_numpy(dtype="float64")
    gr = np.where(np.isfinite(gr), gr, np.nan)  # a bad bar (e.g. ÷0 → inf) is NULL, not a spike

    s_val = np.empty(len(grid), dtype="float64")
    for i in range(len(grid)):
        if i == 0:
            s_val[i] = INDEX_BASE
        elif np.isnan(gr[i]):
            s_val[i] = s_val[i - 1]  # NULL return → carry the index forward
        else:
            s_val[i] = s_val[i - 1] * (1.0 + gr[i])
    index_value = pd.Series(s_val, index=grid)

    ma = index_value.rolling(MA_LENGTH, min_periods=MA_LENGTH).mean()
    ma_v = ma.to_numpy(dtype="float64")
    raw: list[str | None] = [
        None if np.isnan(ma_v[i]) else ("bull" if s_val[i] >= ma_v[i] else "bear")
        for i in range(len(grid))
    ]

    conf = confirmed_labels(raw)  # raw 200-SMA cross ("sma")
    return pd.DataFrame(
        {
            "group_return": gr,
            "index_value": s_val,
            "ma_200": ma_v,
            "raw_label": raw,
            "confirmed_label": conf,
            "vol_exposure": _vol_exposure(gr, conf, grid),  # continuous size for "vol"
        },
        index=grid,
    )


def _vol_exposure(gr: np.ndarray, trend: list[str], grid: pd.DatetimeIndex) -> np.ndarray:
    """Vol-targeted exposure per day: 0 when the trend is bear, else
    min(CAP, target/realized) where realized is trailing annualized vol and
    target is its own expanding-median (lookahead-free) — a risk brake that only
    de-risks above-typical-vol periods. Full exposure during the vol warm-up."""
    r = pd.Series(gr, index=grid)
    realized = r.rolling(VOL_WINDOW, min_periods=VOL_WINDOW).std(ddof=1) * math.sqrt(TRADING_DAYS_YR)
    target = realized.expanding(min_periods=VOL_WINDOW).median()  # trailing typical vol
    rv, tv = realized.to_numpy(dtype="float64"), target.to_numpy(dtype="float64")
    exposure = np.zeros(len(grid), dtype="float64")
    for i in range(len(grid)):
        if trend[i] != "bull":
            continue
        if np.isnan(rv[i]) or np.isnan(tv[i]) or rv[i] <= 0:
            exposure[i] = VOL_CAP  # warm-up → fully in, like the SMA filter
        else:
            exposure[i] = min(VOL_CAP, tv[i] / rv[i])
    return exposure


def build_group_daily(members: dict[str, pd.Series]) -> pd.DataFrame:
    """The per-day table for an equal-weighted basket of member adj-close series.

    ``members`` maps ticker → a date-indexed adj_close Series. Each member's
    return is vs its OWN previous available day (§5.1); the group return is the
    equal-weighted mean over members present that day (§5.2). Empty DataFrame if
    no member has data.
    """
    clean = {t: s for t, s in members.items() if s is not None and len(s) > 0}
    if not clean:
        return pd.DataFrame(columns=_COLS)
    grid = pd.DatetimeIndex(sorted(set().union(*(set(s.index) for s in clean.values()))))
    ret = pd.DataFrame(index=grid)
    for t, s in clean.items():
        ret[t] = s.sort_index().pct_change().reindex(grid)
    n_members = ret.notna().sum(axis=1)  # M_t
    group_return = ret.mean(axis=1, skipna=True)
    group_return[n_members == 0] = np.nan  # no computable return → NULL (§5.2)
    return _finalize(group_return)


def _max_drawdown(r: np.ndarray) -> float:
    """Worst peak-to-trough of the compounded stream, as a negative fraction."""
    if len(r) == 0:
        return 0.0
    w = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(w)
    peak = np.where(peak > 0, peak, 1.0)  # avoid ÷0 on a total wipeout (w == 0)
    return float((w / peak - 1.0).min())


def _stream_metrics(r: np.ndarray) -> dict[str, float | None]:
    """CAGR / Sharpe / Sortino / max-drawdown for one daily-return stream."""
    n = len(r)
    if n == 0:
        return {"cagr": None, "sharpe": None, "sortino": None, "maxdd": None}
    prod = float(np.prod(1.0 + r))
    cagr = -1.0 if prod <= 0 else prod ** (TRADING_DAYS_YR / n) - 1.0
    mean = float(np.mean(r))
    sd = float(np.std(r, ddof=1)) if n > 1 else 0.0
    sharpe = 0.0 if sd == 0 else mean / sd * math.sqrt(TRADING_DAYS_YR)
    neg = r[r < 0]  # forced-to-0 bear days are zeros, not negatives
    if len(neg) < 2:
        sortino = 0.0
    else:
        dd = float(np.std(neg, ddof=1))
        sortino = 0.0 if dd == 0 else mean / dd * math.sqrt(TRADING_DAYS_YR)
    return {"cagr": cagr, "sharpe": sharpe, "sortino": sortino, "maxdd": _max_drawdown(r)}


def _filtered_stream(gr: np.ndarray, labels: list[str]) -> np.ndarray:
    """Returns held only after a bull day (cash after bear) — the previous day's
    label gates today's return, so there is no lookahead."""
    prev = ["bull", *labels[:-1]]
    return np.where(np.array(prev) == "bull", gr, 0.0)


def group_metrics(gdf: pd.DataFrame) -> dict[str, float | None]:
    """CAGR/Sharpe/Sortino/max-DD three ways: always-in, the raw 200-SMA cross
    (``sma``, binary in/out) and the vol-targeted variant (``vol``, continuous
    exposure). A variant is None if its input column is absent from the table."""
    if gdf.empty:
        return dict.fromkeys(METRIC_KEYS)
    gr = np.nan_to_num(gdf["group_return"].to_numpy(dtype="float64"), nan=0.0)  # NULL → 0
    streams = {"always": _stream_metrics(gr)}
    if "confirmed_label" in gdf.columns:  # binary: held only after a bull day
        streams["sma"] = _stream_metrics(_filtered_stream(gr, list(gdf["confirmed_label"])))
    if "vol_exposure" in gdf.columns:  # continuous: prior day's exposure × today's return
        exp = gdf["vol_exposure"].to_numpy(dtype="float64")
        exp_prev = np.concatenate([[0.0], exp[:-1]])  # position set on prior close (no lookahead)
        streams["vol"] = _stream_metrics(exp_prev * gr)
    out: dict[str, float | None] = dict.fromkeys(METRIC_KEYS)
    for fam in _METRIC_FAMILIES:
        for variant, m in streams.items():
            out[f"{fam}_{variant}"] = m[fam]
    return out


def _state(gdf: pd.DataFrame, label_col: str = "confirmed_label") -> dict[str, Any]:
    """Current label, its 'since' date, and the covered range, for one variant's
    label column."""
    if gdf.empty:
        return {"label": "bull", "since": None, "date_from": None, "date_to": None}
    conf = list(gdf[label_col])
    dates = [d.strftime("%Y-%m-%d") for d in gdf.index]
    label = conf[-1]
    i = len(conf) - 1
    while i > 0 and conf[i - 1] == label:  # earliest day of the current unbroken run
        i -= 1
    return {"label": label, "since": dates[i], "date_from": dates[0], "date_to": dates[-1]}


# ══════════════════════════════════════════════════════════════════════════════
# Sectors — constituents derived from the universe (no manual membership).
# ══════════════════════════════════════════════════════════════════════════════
_sectors_cache: dict[str, list[str]] | None = None


def _universe_instruments() -> list[dict[str, Any]]:
    try:
        from etoro_yfinance import universe as u

        insts = u.load("backtest").get("instruments", [])
    except Exception:
        insts = []
    if not insts:
        try:
            from etoro_yfinance.web import data as wd

            insts = wd.load_etoro_universe().get("rows", [])
        except Exception:
            insts = []
    return insts


def sector_tickers() -> dict[str, list[str]]:
    """sector → every yfinance ticker in it (deduped), from the universe."""
    global _sectors_cache
    if _sectors_cache is None:
        d: dict[str, list[str]] = {}
        for r in _universe_instruments():
            sec, yf = r.get("sector"), r.get("yf")
            if not sec or not yf:
                continue
            lst = d.setdefault(sec, [])
            if yf not in lst:
                lst.append(yf)
        _sectors_cache = d
    return _sectors_cache


def list_sectors() -> list[str]:
    return sorted(sector_tickers().keys())


def _sector_returns(tickers: list[str]) -> tuple[pd.Series | None, int]:
    """Equal-weighted daily return of a sector's constituents, and the number of
    tickers that actually had price data.

    Each ticker's adj_close is repaired (CLAUDE.md), assembled into a wide
    matrix; the per-ticker return is vs its previous available day (``ffill`` +
    shift bridges non-trading gaps), then equal-weighted across the names present
    each day. Fully vectorized over the matrix — no per-ticker Python loop for
    the returns.
    """
    cols: dict[str, pd.Series] = {}
    for t in tickers:
        df = prices.load_prices(t, columns=["adj_close", "close"])
        if df is None or "adj_close" not in df.columns or df.empty:
            continue
        s = prices.repair_adj_close(df).dropna()
        if len(s):
            cols[t] = s
    if not cols:
        return None, 0
    mat = pd.DataFrame(cols)
    mat.index = pd.to_datetime(mat.index)
    mat = mat.sort_index()
    ret = mat / mat.ffill().shift(1) - 1.0  # return vs each name's previous available bar
    ret = ret.replace([np.inf, -np.inf], np.nan)  # zero-price bars → exclude, don't blow up
    return ret.mean(axis=1, skipna=True), mat.shape[1]


def sector_daily(tickers: list[str]) -> pd.DataFrame:
    grp, _ = _sector_returns(tickers)
    return _finalize(grp) if grp is not None else pd.DataFrame(columns=_COLS)


# ══════════════════════════════════════════════════════════════════════════════
# Derived docs — computed + cached by the daily job, read by the API.
# ══════════════════════════════════════════════════════════════════════════════
def _dir() -> Path:
    d = data_dir() / "monitor"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") or "sector"


def _cache_path(name: str) -> Path:
    return _dir() / f"sector_{_safe(name)}.json"


def load_cache(name: str) -> dict[str, Any] | None:
    p = _cache_path(name)
    return json.loads(p.read_text()) if p.exists() else None


def has_any_cache() -> bool:
    """True once at least one sector has been computed (its series cached)."""
    return any(_dir().glob("sector_*.json"))


def _write_cache(name: str, doc: dict[str, Any]) -> None:
    _cache_path(name).write_text(json.dumps(doc, ensure_ascii=False))


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _num(v: float | None, ndigits: int) -> float | None:
    """JSON-safe rounded float: None for missing / non-finite (NaN, ±inf)."""
    if v is None:
        return None
    v = float(v)
    return round(v, ndigits) if math.isfinite(v) else None


def compute_sector(name: str) -> dict[str, Any]:
    """Build the full derived doc (per-variant state + metrics + chart series)."""
    tickers = sector_tickers().get(name, [])
    grp, n_used = _sector_returns(tickers)
    gdf = _finalize(grp) if grp is not None else pd.DataFrame(columns=_COLS)
    series = [
        {
            "date": d.strftime("%Y-%m-%d"),
            "index": _num(row.index_value, 4),
            "ma_200": _num(row.ma_200, 4),
            "trend_label": row.confirmed_label,  # green/red shading (shared by both)
            "exposure": _num(row.vol_exposure, 3),  # vol-target position size (0..1)
        }
        for d, row in zip(gdf.index, gdf.itertuples(), strict=True)
    ]
    variants = {}
    for v, col in _VARIANT_LABEL_COL.items():
        st = _state(gdf, col if col in gdf.columns else "confirmed_label")
        variants[v] = {"label": st["label"], "since": st["since"], "exposure": None}
    if "vol_exposure" in gdf.columns and len(gdf):  # current position size for the vol variant
        variants["vol"]["exposure"] = _num(float(gdf["vol_exposure"].iloc[-1]), 3)
    rng = _state(gdf)
    metrics = group_metrics(gdf)
    return {
        "name": name,
        "count": len(tickers),
        "n_used": n_used,
        "date_from": rng["date_from"],
        "date_to": rng["date_to"],
        "variants": variants,
        "metrics": {k: _num(v, 6) for k, v in metrics.items()},
        "series": series,
        "computed_at": _now(),
    }


def _default_doc(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "count": len(sector_tickers().get(name, [])),
        "n_used": None,
        "date_from": None,
        "date_to": None,
        "variants": {v: {"label": "bull", "since": None, "exposure": None} for v in FILTERS},
        "metrics": dict.fromkeys(METRIC_KEYS),
    }


def sector_summary(name: str) -> dict[str, Any]:
    """The cached derived doc without the (large) series, or a default if uncomputed.

    Backfills any metric keys missing from an older cache (written before a new
    metric was added) with None, so the UI renders it as "—" rather than raising.
    """
    doc = load_cache(name)
    if doc is None:
        return _default_doc(name)
    out = {k: v for k, v in doc.items() if k != "series"}
    out["count"] = len(sector_tickers().get(name, []))  # keep count live vs the universe
    out.setdefault("n_used", None)
    metrics = dict(out.get("metrics") or {})
    for k in METRIC_KEYS:
        metrics.setdefault(k, None)
    out["metrics"] = metrics
    variants = dict(out.get("variants") or {})
    for v in FILTERS:
        d = dict(variants.get(v) or {})
        d.setdefault("label", "bull")
        d.setdefault("since", None)
        d.setdefault("exposure", None)
        variants[v] = d
    out["variants"] = variants
    return out


def list_summaries() -> list[dict[str, Any]]:
    return [sector_summary(s) for s in list_sectors()]


def filter_scorecard(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate, across every sector with data, how the regime filter compares
    to always-in. For each metric family it reports the median filtered vs
    always value and the breadth — the share of sectors the filter improved
    (higher Sharpe/Sortino/CAGR, or a shallower — less negative — max drawdown).

    Descriptive only: sectors overlap and survivorship-biased, so treat this as a
    dashboard read, not a significance test.
    """
    rows = [s for s in summaries if s.get("date_from") and s.get("metrics")]
    out: dict[str, Any] = {"n": len(rows)}

    def med(xs: list[float]) -> float | None:
        return round(float(np.median(xs)), 4) if xs else None

    def share(pairs: list[tuple[float, float]]) -> float | None:
        return round(sum(1 for x, y in pairs if x > y) / len(pairs), 3) if pairs else None

    for fam in _METRIC_FAMILIES:
        triples = []
        for s in rows:
            m = s["metrics"]
            a, sm, vl = (m.get(f"{fam}_{v}") for v in ("always", "sma", "vol"))
            if a is not None and sm is not None:
                triples.append((a, sm, vl))
        if not triples:
            out[fam] = dict.fromkeys(("always", "sma", "vol", "win", "win_vol", "beats"), None)
            out[fam]["n"] = 0
            continue
        vol = [(a, sm, vl) for a, sm, vl in triples if vl is not None]
        out[fam] = {
            "always": med([a for a, _, _ in triples]),
            "sma": med([sm for _, sm, _ in triples]),
            "vol": med([vl for _, _, vl in vol]),
            "win": share([(sm, a) for a, sm, _ in triples]),  # old (SMA) beats always-in
            "win_vol": share([(vl, a) for a, _, vl in vol]),  # new (vol) beats always-in
            "beats": share([(vl, sm) for _, sm, vl in vol]),  # new beats old
            "n": len(triples),
            "n_vol": len(vol),
        }
    return out


def sector_series(name: str) -> dict[str, Any]:
    if name not in sector_tickers():
        raise NotFoundError(f"sector '{name}' not found")
    doc = load_cache(name)
    return {"name": name, "series": doc["series"] if doc else []}


def run_daily_update() -> dict[str, Any]:
    """Recompute + cache every sector's derived doc. Idempotent."""
    t0 = time.monotonic()
    sectors = list_sectors()
    for name in sectors:
        _write_cache(name, compute_sector(name))
    return {
        "status": "ok",
        "sectors_updated": len(sectors),
        "duration_seconds": round(time.monotonic() - t0, 3),
    }
