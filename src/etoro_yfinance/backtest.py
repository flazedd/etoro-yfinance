"""Periodically rebalanced backtest over a chosen universe (EUR total return).

At each period start (monthly by default, quarterly optional — see REBALANCE):
consider only assets that already have ≥2 years of
price AND volume history (younger listings join once they qualify — the
considered set grows over time), compute signals from data strictly before that
date, score + select (default: top 4 sectors × top 6 per sector), equal-weight
the picks, hold to the next month-start. Signals & returns use the EUR
adjusted-close series (currency-comparable, splits/divs handled); volume signals
use raw share volume. Benchmark = equal-weight of the eligible universe,
rebalanced the same way under the same 2-year rule.

Costs: the strategy pays half the eToro spread (`spread_pct` on each universe
row) on every name entering or leaving the basket — buy at the ask, sell at the
bid; names held through a rebalance pay nothing. Names without a known spread
are charged the median of the known ones. The benchmark is gross (a reference
index, not a tradable book). Caveat the results either way: the universe is
built from instruments tradable on eToro *today*, so delisted names are absent
— survivorship bias flatters both curves.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd

from etoro_yfinance import momentum, prices

_MIN_BARS = 20  # min price history before a rebalance to be eligible (mirrors signals)
# At each rebalance an asset is considered only once it has this much price AND
# volume history before the cutoff. Young listings join as they mature.
MIN_HISTORY_DAYS = 730  # 2 years

# Selectable strategies (key -> UI label). Both share the same rebalance
# cadence, eligibility rules, cost model and benchmark — they differ only in
# how each period's basket is picked.
STRATEGIES = {
    "momentum": "Momentum (bbterminal)",
    "sortino": "Sortino lookback — top N by 1-month Sortino",
}

# Rebalance cadence: key -> (pandas date_range freq for the cutoff grid,
# periods per year for annualizing the per-period stats).
REBALANCE = {
    "monthly": ("MS", 12),
    "quarterly": ("QS", 4),  # calendar quarters (Jan/Apr/Jul/Oct starts)
}

_SORTINO_WINDOW = 21  # trading days ≈ one month of daily returns
_SORTINO_MIN_RETS = 15  # need most of a month of returns to be ranked


def sortino_ratio(rets: np.ndarray) -> float:
    """Mean daily return over downside deviation (target 0, unannualized — the
    ranking is scale-invariant). A month with no negative returns and a positive
    mean has no downside risk → +inf, so a flawless month outranks everything."""
    rets = rets[np.isfinite(rets)]
    if len(rets) == 0:
        return 0.0
    mean = float(rets.mean())
    downside = float(np.sqrt(np.mean(np.minimum(rets, 0.0) ** 2)))
    if downside == 0.0:
        return float("inf") if mean > 0 else 0.0
    return mean / downside


# Cap a single name's one-month return to kill data-glitch spikes (e.g. Yahoo
# ticker-reuse splices like WLD-USD printing +15,000%). +400% is far above any
# real monthly move, so genuine winners are untouched.
_RET_CAP, _RET_FLOOR = 4.0, -0.95


def _max_dd(equity: list[float]) -> float:
    if len(equity) < 2:
        return 0.0
    eq = np.array(equity)
    return float((eq / np.maximum.accumulate(eq) - 1).min())


def _stats(equity: list[float], years: float, periods_per_year: int = 12) -> dict[str, float]:
    if len(equity) < 2:
        return {}
    eq = np.array(equity)
    rets = eq[1:] / eq[:-1] - 1
    ann = np.sqrt(periods_per_year)
    ann_vol = float(rets.std(ddof=1) * ann) if len(rets) > 1 else 0.0
    sharpe = float(rets.mean() / rets.std(ddof=1) * ann) if rets.std(ddof=1) > 0 else 0.0
    cagr = float(eq[-1] ** (1 / years) - 1) if years > 0 and eq[-1] > 0 else 0.0
    return {
        "total_return": float(eq[-1] - 1),
        "cagr": cagr,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": _max_dd(equity),
    }


def run(
    rows: list[dict[str, Any]],
    *,
    start: str,
    end: str,
    strategy: str = "momentum",
    rebalance: str = "monthly",
    top_n_sectors: int = 4,
    top_n_per_sector: int = 6,
    min_sector_size: int = 0,
    top_n: int = 30,
    weights: dict[str, float] | None = None,
    progress: Callable[[float, str], None] | None = None,
) -> dict[str, Any]:
    """Run a periodically rebalanced backtest. `rows` = universe instruments
    (need yf + sector; `spread_pct` per row prices the rebalance costs).

    `strategy` picks the selector (see STRATEGIES): "momentum" scores + selects
    top sectors × top names (top_n_sectors/top_n_per_sector/min_sector_size/
    weights); "sortino" takes the `top_n` names by the Sortino ratio of the past
    month's daily returns. `rebalance` sets the cadence (see REBALANCE) — the
    basket is re-picked at each period start and held to the next.
    `progress(frac, label)` is called 0.0→1.0."""
    if strategy not in STRATEGIES:
        return {"error": f"unknown strategy {strategy!r} (choose from {list(STRATEGIES)})"}
    if rebalance not in REBALANCE:
        return {"error": f"unknown rebalance {rebalance!r} (choose from {list(REBALANCE)})"}
    freq, periods_per_year = REBALANCE[rebalance]

    def _p(frac: float, label: str) -> None:
        if progress:
            progress(min(1.0, max(0.0, frac)), label)

    # Dedup by yfinance ticker; load EUR adj-close (signals + returns) + raw volume.
    price_index: dict[str, pd.Series] = {}
    volume_index: dict[str, pd.Series] = {}
    sectors: dict[str, str | None] = {}
    spreads: dict[str, float] = {}  # yf -> full spread in % ((ask-bid)/mid×100)
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
        if r.get("spread_pct") is not None:
            spreads[yf] = float(r["spread_pct"])
        nat = prices.load_prices(yf)
        if nat is not None and "volume" in nat.columns:
            v = nat["volume"].astype("float64")
            v.index = pd.to_datetime(v.index)
            volume_index[yf] = v

    cutoffs = list(pd.date_range(start=start, end=end, freq=freq))
    if len(cutoffs) < 2 or not price_index:
        return {"error": f"need ≥2 {rebalance} rebalances and a non-empty universe with data"}

    panels: dict[pd.Timestamp, pd.DataFrame] = {}
    if strategy == "momentum":  # the sortino selector ranks directly off prices
        _p(0.5, "computing signals")
        panels = momentum.signals_at_cutoffs(
            price_index, volume_index, sectors, cutoffs, min_history_days=MIN_HISTORY_DAYS
        )

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

    def _seg(names: list[str], c: pd.Timestamp, win: pd.DatetimeIndex, run: float) -> list[float]:
        """Daily equity of an equal-weight buy-hold basket entered at c, valued on
        each day in `win`. Per-name growth factor is clipped to [lo_f, hi_f] so a
        single data-glitch spike can't dominate the equal-weight mean."""
        if not names or len(win) == 0:
            return [run] * len(win)
        entry = price_m.loc[c, names]
        fac = price_m.loc[win, names].div(entry).clip(lower=lo_f, upper=hi_f)
        return list(fac.mean(axis=1) * run)

    # Rebalance costs: half the spread on each side of a turnover (buy at ask,
    # sell at bid). Unknown spreads get the median known one, so missing data
    # doesn't silently mean "free trading".
    known_spreads = sorted(spreads.values())
    default_spread = known_spreads[len(known_spreads) // 2] if known_spreads else 0.0

    def _half_spread(t: str) -> float:
        return spreads.get(t, default_spread) / 2.0 / 100.0

    def _turnover_cost(new: list[str], old: set[str]) -> float:
        """Fraction of equity paid in spread at one rebalance (entries at the
        new equal weight, exits at the old equal weight)."""
        if not new and not old:
            return 0.0
        enter = sum(_half_spread(t) for t in new if t not in old) / len(new) if new else 0.0
        exit_ = sum(_half_spread(t) for t in old if t not in new) / len(old) if old else 0.0
        return enter + exit_

    def _bench_eligible(c: pd.Timestamp) -> list[str]:
        """Universe names considered at cutoff c: the same 2-year price+volume
        history rule the strategy uses, plus ≥_MIN_BARS bars and a fresh last
        bar — so the benchmark is the equal-weight of exactly the set the
        strategy could have picked from (and glitchy first prints of brand-new
        listings can't distort it)."""
        out = []
        for t in all_tickers:
            idx = price_index[t].index
            pos = idx.searchsorted(c, side="left")  # bars strictly before c
            if pos < _MIN_BARS or (c - idx[pos - 1]).days > momentum.MAX_STALENESS_DAYS:
                continue
            v = volume_index.get(t)
            if (
                (c - idx[0]).days < MIN_HISTORY_DAYS
                or v is None
                or len(v) == 0
                or (c - v.index[0]).days < MIN_HISTORY_DAYS
            ):
                continue
            out.append(t)
        return out

    def _sc(row: Any, col: str) -> float | None:
        v = row.get(col)
        return round(float(v), 1) if v is not None and pd.notna(v) else None

    def _sortino_picks(c: pd.Timestamp, names: list[str]) -> list[tuple[str, float]]:
        """The top-`top_n` of `names` by the Sortino ratio of the ~1 month of
        daily returns strictly before c (ties — e.g. several flawless months
        at +inf — broken by mean return)."""
        ranked = []
        for t in names:
            s = price_index[t]
            pos = int(s.index.searchsorted(c, side="left"))
            vals = s.values[max(0, pos - (_SORTINO_WINDOW + 1)) : pos].astype("float64")
            # Keep only usable closes: zero prints (Yahoo glitches, float32
            # underflow on micro-priced coins) would blow up the return divide.
            vals = vals[np.isfinite(vals) & (vals > 0)]
            if len(vals) < _SORTINO_MIN_RETS + 1:
                continue
            rets = np.diff(vals) / vals[:-1]
            ranked.append((t, sortino_ratio(rets), float(rets.mean())))
        ranked.sort(key=lambda x: (x[1], x[2]), reverse=True)
        return [(t, sr) for t, sr, _ in ranked[: max(1, top_n)]]

    dates: list[str] = []
    strat_daily: list[float] = []
    bench_daily: list[float] = []
    period_s, period_b = [1.0], [1.0]  # values at each cutoff → stats
    run_s = run_b = 1.0
    cost_mult = 1.0  # cumulative (1 - cost) → total drag
    prev_picks: set[str] = set()
    holdings_per: list[int] = []
    portfolios: list[dict[str, Any]] = []  # one record per held period
    last_holdings: list[dict[str, Any]] = []
    n_steps = len(cutoffs) - 1

    for i in range(n_steps):
        if i % 3 == 0:
            _p(0.55 + 0.45 * i / n_steps, f"rebalancing {cutoffs[i].date()!s}")
        c, nxt = cutoffs[i], cutoffs[i + 1]
        b_names = _bench_eligible(c)
        if strategy == "sortino":
            ranked = _sortino_picks(c, b_names)
            picks = [t for t, _ in ranked]
            holdings = [
                {
                    "ticker": t,
                    "sector": sectors.get(t),
                    "score": None if np.isinf(sr) else round(sr, 2),
                    "score_price": None,
                    "score_volume": None,
                }
                for t, sr in ranked
            ]
        else:
            scored = momentum.score_universe(panels.get(c, pd.DataFrame()), weights)
            sel = momentum.select_from_scored(
                scored,
                top_n_sectors=top_n_sectors,
                top_n_per_sector=top_n_per_sector,
                min_sector_size=min_sector_size,
            )
            picks = list(sel["company_id"]) if not sel.empty else []
            holdings = [
                {
                    "ticker": r_["company_id"],
                    "sector": r_["sector"],
                    "score": _sc(r_, "momentum_score"),
                    "score_price": _sc(r_, "score_price"),
                    "score_volume": _sc(r_, "score_volume"),
                }
                for _, r_ in sel.iterrows()
            ]
        if holdings:
            last_holdings = holdings

        # Pay the spread on this month's turnover before valuing the segment,
        # so every daily mark from c onward reflects it. Benchmark stays gross.
        cost = _turnover_cost(picks, prev_picks)
        run_before = run_s  # period entry value, pre-cost → net period return
        run_s *= 1.0 - cost
        cost_mult *= 1.0 - cost
        prev_picks = set(picks)

        # Value each basket daily over [c, nxt] inclusive; append all but the last
        # (nxt is the next month's opening point) — the last value carries forward.
        win = all_days[(all_days >= c) & (all_days <= nxt)]
        s_vals = _seg(picks, c, win, run_s)
        b_vals = _seg(b_names, c, win, run_b)
        dates += [str(d.date()) for d in win[:-1]]
        strat_daily += s_vals[:-1]
        bench_daily += b_vals[:-1]
        run_s, run_b = s_vals[-1], b_vals[-1]
        period_s.append(run_s)
        period_b.append(run_b)
        holdings_per.append(len(picks))

        # Per-period record: net return (spread cost included) and the Sortino
        # of the basket's own daily returns over the holding period.
        seg = np.array(s_vals, dtype="float64")
        seg_rets = np.diff(seg) / seg[:-1] if len(seg) > 1 else np.array([])
        p_sortino = sortino_ratio(seg_rets)
        portfolios.append(
            {
                "date": str(c.date()),
                "to": str(nxt.date()),
                "n": len(picks),
                "return_pct": round((run_s / run_before - 1.0) * 100, 2) if run_before else 0.0,
                "sortino": None if np.isinf(p_sortino) else round(p_sortino, 2),
                "holdings": holdings,
            }
        )

    # Final point at the last cutoff.
    dates.append(str(cutoffs[-1].date()))
    strat_daily.append(run_s)
    bench_daily.append(run_b)

    years = (cutoffs[-1] - cutoffs[0]).days / 365.25
    stats = _stats(period_s, years, periods_per_year)
    bench_stats = _stats(period_b, years, periods_per_year)
    # Monthly points miss intramonth pain — take max drawdown from the daily curve.
    if stats:
        stats["max_drawdown"] = _max_dd(strat_daily)
    if bench_stats:
        bench_stats["max_drawdown"] = _max_dd(bench_daily)
    return {
        "dates": dates,
        "equity": strat_daily,
        "benchmark": bench_daily,
        "stats": stats,
        "benchmark_stats": bench_stats,
        "periods": n_steps,
        "avg_holdings": round(float(np.mean(holdings_per)), 1) if holdings_per else 0,
        "universe_size": len(price_index),
        "last_holdings": last_holdings,
        "portfolios": portfolios,
        "cost_drag": round(1.0 - cost_mult, 4),  # equity fraction lost to spreads
        "spread_known": len(spreads),
        "default_spread_pct": round(default_spread, 3),
        "notes": [
            "At each rebalance only assets with ≥2 years of prior price + volume "
            "history are considered (strategy and benchmark alike); younger "
            "listings join once they qualify.",
            f"Strategy pays half the eToro spread on each entry/exit "
            f"(known for {len(spreads)}/{len(price_index)} names; "
            f"others charged the median {default_spread:.2f}%). Benchmark is gross.",
            "Universe = instruments tradable on eToro today — delisted names are "
            "absent, so survivorship bias flatters both curves.",
        ],
        "params": {
            "strategy": strategy,
            "rebalance": rebalance,
            "top_n_sectors": top_n_sectors,
            "top_n_per_sector": top_n_per_sector,
            "min_sector_size": min_sector_size,
            "top_n": top_n,
            "start": start,
            "end": end,
        },
    }
