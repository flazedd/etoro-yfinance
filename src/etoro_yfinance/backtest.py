"""Monthly-rebalanced momentum backtest over a chosen universe (EUR total return).

At the 1st of each month: compute signals from data strictly before that date,
score + select (default: top 4 sectors × top 6 per sector), equal-weight the
picks, hold to the next month-start. Signals & returns use the EUR adjusted-close
series (currency-comparable, splits/divs handled); volume signals use raw share
volume. Benchmark = equal-weight of the whole universe, rebalanced the same way.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from etoro_yfinance import momentum, prices

_MIN_BARS = 20  # min price history before a rebalance to be eligible (mirrors signals)
# Cap a single name's one-month return to kill data-glitch spikes (e.g. Yahoo
# ticker-reuse splices like WLD-USD printing +15,000%). +400% is far above any
# real monthly move, so genuine winners are untouched.
_RET_CAP, _RET_FLOOR = 4.0, -0.95


def _stats(equity: list[float], years: float) -> dict:
    if len(equity) < 2:
        return {}
    eq = np.array(equity)
    rets = eq[1:] / eq[:-1] - 1
    dd = float((eq / np.maximum.accumulate(eq) - 1).min())
    ann_vol = float(rets.std(ddof=1) * np.sqrt(12)) if len(rets) > 1 else 0.0
    sharpe = float(rets.mean() / rets.std(ddof=1) * np.sqrt(12)) if rets.std(ddof=1) > 0 else 0.0
    cagr = float(eq[-1] ** (1 / years) - 1) if years > 0 and eq[-1] > 0 else 0.0
    return {"total_return": float(eq[-1] - 1), "cagr": cagr, "ann_vol": ann_vol,
            "sharpe": sharpe, "max_drawdown": dd}


def run(rows: list[dict], *, start: str, end: str, top_n_sectors: int = 4,
        top_n_per_sector: int = 6, min_sector_size: int = 0, weights: dict | None = None,
        progress=None) -> dict:
    """Run the momentum backtest. `rows` = universe instruments (need yf + sector).
    `progress(frac, label)` is called 0.0→1.0 as data loads and the loop runs."""
    def _p(frac: float, label: str) -> None:
        if progress:
            progress(min(1.0, max(0.0, frac)), label)

    # Dedup by yfinance ticker; load EUR adj-close (signals + returns) + raw volume.
    price_index: dict[str, pd.Series] = {}
    volume_index: dict[str, pd.Series] = {}
    sectors: dict[str, str] = {}
    n_rows = len(rows) or 1
    for i, r in enumerate(rows):
        if i % 50 == 0:
            _p(0.45 * i / n_rows, f"loading prices {i}/{n_rows}")
        yf = r.get("yf")
        if not yf or yf in price_index:
            continue
        eur = prices.load_prices(yf, eur=True)
        if eur is None or "adj_close" not in eur.columns:
            continue
        s = eur["adj_close"].dropna()
        s.index = pd.to_datetime(s.index)
        if len(s) < 20:
            continue
        price_index[yf] = s
        sectors[yf] = r.get("sector")
        nat = prices.load_prices(yf)
        if nat is not None and "volume" in nat.columns:
            v = nat["volume"].astype("float64")
            v.index = pd.to_datetime(v.index)
            volume_index[yf] = v

    cutoffs = list(pd.date_range(start=start, end=end, freq="MS"))
    if len(cutoffs) < 2 or not price_index:
        return {"error": "need ≥2 monthly rebalances and a non-empty universe with data"}

    _p(0.5, "computing signals")
    panels = momentum.signals_at_cutoffs(price_index, volume_index, sectors, cutoffs)

    all_tickers = list(price_index)
    # Daily mark-to-market axis: every trading day in range + the cutoffs, so the
    # equity curve is drawn daily even though holdings only change monthly. Wide
    # ffilled price matrix (float32) lets each month's basket be valued daily
    # with one vectorized slice.
    lo, hi = cutoffs[0], cutoffs[-1]
    day_vals = np.unique(np.concatenate([s.index.values for s in price_index.values()]))
    # ffill over the FULL history (incl. pre-start bars) so the first cutoff — even
    # a market holiday like Jan 1 — inherits the prior close instead of NaN; then
    # restrict the iterate/display axis to [start, end].
    full_days = pd.DatetimeIndex(day_vals).union(pd.DatetimeIndex(cutoffs))
    price_m = pd.DataFrame(price_index).reindex(full_days).ffill().astype("float32")
    all_days = full_days[(full_days >= lo) & (full_days <= hi)]
    lo_f, hi_f = 1 + _RET_FLOOR, 1 + _RET_CAP

    def _seg(names, c, win, run):
        """Daily equity of an equal-weight buy-hold basket entered at c, valued on
        each day in `win`. Per-name growth factor is clipped to [lo_f, hi_f] so a
        single data-glitch spike can't dominate the equal-weight mean."""
        if not names or len(win) == 0:
            return [run] * len(win)
        entry = price_m.loc[c, names]
        fac = price_m.loc[win, names].div(entry).clip(lower=lo_f, upper=hi_f)
        return (fac.mean(axis=1) * run).tolist()

    def _bench_eligible(c):
        """Universe names with ≥_MIN_BARS bars before c and a fresh last bar —
        excludes brand-new listings whose glitchy first prints would distort the
        equal-weight benchmark (e.g. a just-launched coin printing +15,000%)."""
        out = []
        for t in all_tickers:
            idx = price_index[t].index
            pos = idx.searchsorted(c, side="left")     # bars strictly before c
            if pos >= _MIN_BARS and (c - idx[pos - 1]).days <= momentum.MAX_STALENESS_DAYS:
                out.append(t)
        return out

    def _sc(row, col):
        v = row.get(col)
        return round(float(v), 1) if v is not None and pd.notna(v) else None

    dates: list[str] = []
    strat_daily: list[float] = []
    bench_daily: list[float] = []
    monthly_s, monthly_b = [1.0], [1.0]     # values at each cutoff → stats
    run_s = run_b = 1.0
    holdings_per: list[int] = []
    last_holdings: list[dict] = []
    n_steps = len(cutoffs) - 1

    for i in range(n_steps):
        if i % 3 == 0:
            _p(0.55 + 0.45 * i / n_steps, f"rebalancing {cutoffs[i].date()!s}")
        c, nxt = cutoffs[i], cutoffs[i + 1]
        scored = momentum.score_universe(panels.get(c, pd.DataFrame()), weights)
        sel = momentum.select_from_scored(scored, top_n_sectors=top_n_sectors,
                                          top_n_per_sector=top_n_per_sector,
                                          min_sector_size=min_sector_size)
        picks = sel["company_id"].tolist() if not sel.empty else []
        b_names = _bench_eligible(c)

        # Value each basket daily over [c, nxt] inclusive; append all but the last
        # (nxt is the next month's opening point) — the last value carries forward.
        win = all_days[(all_days >= c) & (all_days <= nxt)]
        s_vals = _seg(picks, c, win, run_s)
        b_vals = _seg(b_names, c, win, run_b)
        dates += [str(d.date()) for d in win[:-1]]
        strat_daily += s_vals[:-1]
        bench_daily += b_vals[:-1]
        run_s, run_b = s_vals[-1], b_vals[-1]
        monthly_s.append(run_s)
        monthly_b.append(run_b)
        holdings_per.append(len(picks))
        if i == n_steps - 1 and not sel.empty:
            last_holdings = [{"ticker": r_["company_id"], "sector": r_["sector"],
                              "score": _sc(r_, "momentum_score"),
                              "score_price": _sc(r_, "score_price"),
                              "score_volume": _sc(r_, "score_volume")}
                             for _, r_ in sel.iterrows()]

    # Final point at the last cutoff.
    dates.append(str(cutoffs[-1].date()))
    strat_daily.append(run_s)
    bench_daily.append(run_b)

    years = (cutoffs[-1] - cutoffs[0]).days / 365.25
    return {
        "dates": dates, "equity": strat_daily, "benchmark": bench_daily,
        "stats": _stats(monthly_s, years), "benchmark_stats": _stats(monthly_b, years),
        "periods": n_steps,
        "avg_holdings": round(float(np.mean(holdings_per)), 1) if holdings_per else 0,
        "universe_size": len(price_index),
        "last_holdings": last_holdings,
        "params": {"top_n_sectors": top_n_sectors, "top_n_per_sector": top_n_per_sector,
                   "min_sector_size": min_sector_size, "start": start, "end": end},
    }
