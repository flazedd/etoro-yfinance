"""Alpha-signal library: candidate cross-sectional signals + the IC harness.

Each signal is registered with an a-priori hypothesis (its `sign` and one-line
rationale, declared BEFORE looking at results — the guard against data mining).
`evaluate()` scores every signal on monthly cutoffs: rank-IC vs next-month
return, t-stat, first/second-half ICs, hit rate and coverage — the scoreboard
that decides admission to the combined strategy. `redundancy()` reports how
correlated signals are cross-sectionally, so the combination can weight
*families* (distinct ideas) instead of counting the same idea many times.

Convention: a signal's raw value is whatever is natural to compute; `sign` says
which direction the hypothesis expects (+1 high value → high future return).
The IC in the scoreboard is reported RAW (unsigned), so a healthy negative-sign
signal shows a negative mean IC.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from etoro_yfinance import prices

MIN_NAMES = 200  # a monthly cross-section thinner than this is skipped
_HISTORY_BARS = 252  # signals may look back up to a year


@dataclass
class Ctx:
    """Wide day×name matrices the signal functions compute from."""

    idx: pd.DatetimeIndex
    names: list[str]
    A: np.ndarray  # adj_close, ffilled (float64)
    R: np.ndarray  # daily returns of A, aligned to idx[1:] (R[p] = ret into idx[p+1]... see note)
    H: np.ndarray  # high (EUR), NaN where no bar
    L: np.ndarray  # low (EUR), NaN where no bar
    T: np.ndarray  # EUR turnover, NaN where no bar
    fresh: np.ndarray  # bool: a real bar within the last 7 calendar days
    sec: pd.Series  # sector per name (aligned to `names`)
    spreads: np.ndarray  # full eToro spread % per name (median-filled)
    itype: np.ndarray  # instrument type per name: "Stocks" | "ETF" | "Crypto" | "?"


@dataclass
class Signal:
    name: str
    family: str
    sign: int  # +1: high value → outperformance expected; -1: inverse
    description: str  # one-line hypothesis
    fn: Callable[[Ctx, int], np.ndarray] = field(repr=False)
    explanation: str = ""  # a few sentences: what it computes, why, caveats


SIGNALS: list[Signal] = []


def _register(name: str, family: str, sign: int, description: str, explanation: str) -> Callable:
    def deco(fn: Callable[[Ctx, int], np.ndarray]) -> Callable:
        SIGNALS.append(Signal(name, family, sign, description, fn, explanation))
        return fn

    return deco


# ── context ──────────────────────────────────────────────────────────────────
def build_context(
    rows: list[dict[str, Any]],
    start: str,
    end: str,
    progress: Callable[[float, str], None] | None = None,
) -> Ctx:
    """Load the repaired EUR series for `rows` into wide matrices covering
    [start - 1y lookback, end + a few days for the last forward return]."""
    lo = pd.Timestamp(start) - pd.Timedelta(days=400)
    hi = pd.Timestamp(end) + pd.Timedelta(days=45)
    cols = ["adj_close", "close", "high", "low", "volume"]
    px: dict[str, pd.Series] = {}
    extra: dict[str, pd.DataFrame] = {}
    sec: dict[str, str] = {}
    n = len(rows) or 1
    for i, r in enumerate(rows):
        if progress and i % 100 == 0:
            progress(i / n, f"loading {i}/{n}")
        yf = r.get("yf")
        if not yf or yf in px:
            continue
        df = prices.load_prices(yf, eur=True, columns=cols)
        if df is None or "adj_close" not in df.columns:
            continue
        s = prices.repair_adj_close(df).dropna()
        s.index = pd.to_datetime(s.index)
        s = s.loc[lo:hi]
        if len(s) < 60:
            continue
        px[yf] = s.astype("float64")
        df.index = pd.to_datetime(df.index)
        extra[yf] = df.loc[lo:hi]
        sec[yf] = r.get("sector") or "(none)"

    names = list(px)
    raw = pd.DataFrame(px)
    idx = raw.index
    A = raw.ffill().to_numpy("float64")
    R = np.full_like(A, np.nan)
    R[1:] = A[1:] / A[:-1] - 1.0

    def _mat(col: str) -> np.ndarray:
        return pd.DataFrame(
            {t: extra[t][col] for t in names if col in extra[t].columns}
        ).reindex(idx).reindex(columns=names).to_numpy("float64")

    by_yf = {r.get("yf"): r for r in rows if r.get("yf")}
    spr = np.array(
        [
            float(by_yf.get(t, {}).get("spread_pct") or np.nan)
            for t in names
        ]
    )
    med = float(np.nanmedian(spr)) if np.isfinite(spr).any() else 0.0
    return Ctx(
        idx=idx,
        names=names,
        A=A,
        R=R,
        H=_mat("high"),
        L=_mat("low"),
        T=_mat("volume"),  # EUR store: volume = EUR turnover
        fresh=raw.ffill(limit=7).notna().to_numpy(),
        sec=pd.Series([sec[t] for t in names]),
        spreads=np.where(np.isfinite(spr), spr, med),
        itype=np.array([by_yf.get(t, {}).get("type") or "?" for t in names], dtype=object),
    )


# ── market regime (equal-weight universe index) ──────────────────────────────
def _eq_index(ctx: Ctx) -> tuple[np.ndarray, np.ndarray]:
    """Equal-weight universe index level and its trailing 63-day realized vol,
    both aligned to ctx.idx. Daily returns are clipped to ±50% before averaging
    so a single blow-up bar can't hijack the index."""
    with np.errstate(all="ignore"):
        clipped = np.clip(ctx.R, -0.5, 0.5)
        cnt = np.isfinite(clipped).sum(axis=1)
        eq_ret = np.where(cnt > 0, np.nansum(clipped, axis=1) / np.maximum(cnt, 1), 0.0)
    eq_curve = np.cumprod(1.0 + eq_ret)
    roll_vol = pd.Series(eq_ret).rolling(63).std().to_numpy()
    return eq_curve, roll_vol


def _regime_at(eq_curve: np.ndarray, roll_vol: np.ndarray, p: int) -> tuple[bool, bool]:
    """(bull, turbulent) at day `p`, using only data strictly before `p`.
    bull = index at/above its trailing 200-day mean; turbulent = current 63-day
    vol above the median of its own prior history (needs >60 prior samples)."""
    prior = eq_curve[max(0, p - 200) : p]
    bull = bool(eq_curve[p] >= np.mean(prior)) if len(prior) else True
    hist = roll_vol[63:p]
    hist = hist[np.isfinite(hist)]
    turb = bool(
        len(hist) > 60 and np.isfinite(roll_vol[p]) and roll_vol[p] > np.median(hist)
    )
    return bull, turb


def regime_series(
    ctx: Ctx, start: str | None = None, end: str | None = None
) -> dict[str, list[Any]]:
    """Daily bull/bear × calm/turbulent classification of the equal-weight
    universe index — the same definitions `evaluate()` buckets its per-regime
    ICs by, computed for every day so the regime timeline can be charted. The
    classification at each day uses only pre-day history (no look-ahead); the
    returned arrays are sliced to [start, end] for display while the index and
    its 200-day mean still carry their full warm-up behind the scenes."""
    eq_curve, roll_vol = _eq_index(ctx)
    n = len(eq_curve)
    ma200 = np.empty(n)
    bull = np.empty(n, dtype=bool)
    turb = np.empty(n, dtype=bool)
    for p in range(n):
        prior = eq_curve[max(0, p - 200) : p]
        ma200[p] = float(np.mean(prior)) if len(prior) else eq_curve[p]
        bull[p], turb[p] = _regime_at(eq_curve, roll_vol, p)
    lo = 0 if start is None else int(ctx.idx.searchsorted(pd.Timestamp(start), "left"))
    hi = n if end is None else int(ctx.idx.searchsorted(pd.Timestamp(end), "right"))
    sl = slice(lo, hi)
    return {
        "dates": [str(d.date()) for d in ctx.idx[sl]],
        "index": [round(float(v), 4) for v in eq_curve[sl]],
        "ma200": [round(float(v), 4) for v in ma200[sl]],
        "bull": [bool(v) for v in bull[sl]],
        "turb": [bool(v) for v in turb[sl]],
    }


# ── signals (hypotheses declared in `sign` + description) ────────────────────
@_register(
    "mom_12_1",
    "momentum",
    +1,
    "12m return skipping the last month persists",
    "Total return over the past 12 months, excluding the most recent month — the classic "
    "'12-1' momentum measure. Assets that led over the past year tend to keep leading for "
    "the next few months, one of the most robust effects in markets. The latest month is "
    "skipped because very recent moves tend to reverse (see rev_1m). Caveat: momentum "
    "crashes hard when markets snap back sharply (e.g. 2009).",
)
def _mom_12_1(c: Ctx, p: int) -> np.ndarray:
    return c.A[p - 21] / c.A[p - 252] - 1


@_register(
    "mom_6_1",
    "momentum",
    +1,
    "6m return skipping the last month persists",
    "Total return over the past 6 months excluding the latest month — a faster momentum "
    "look. It picks up new leaders sooner than 12-1 momentum but is noisier and produces "
    "more turnover; mostly useful inside a blend rather than alone.",
)
def _mom_6_1(c: Ctx, p: int) -> np.ndarray:
    return c.A[p - 21] / c.A[p - 126] - 1


@_register(
    "mom_3_1",
    "momentum",
    +1,
    "3m return skipping the last month persists",
    "Total return over the past 3 months excluding the latest month — the fastest momentum "
    "variant in the library. On its own it is mostly noise (the horizon is short enough "
    "that reversal fights it); it earns its place as diversification inside the momentum "
    "family.",
)
def _mom_3_1(c: Ctx, p: int) -> np.ndarray:
    return c.A[p - 21] / c.A[p - 63] - 1


@_register(
    "sharpe_12_1",
    "momentum",
    +1,
    "vol-adjusted momentum is cleaner than raw",
    "12-1 momentum divided by the asset's daily-return volatility over the same window — "
    "return per unit of risk instead of raw return. It prefers steady climbers over names "
    "that got there in a few wild jumps, and historically holds up better than raw "
    "momentum in turbulent markets. Highly correlated with mom_12_1 (same family slot).",
)
def _sharpe_12_1(c: Ctx, p: int) -> np.ndarray:
    mom = c.A[p - 21] / c.A[p - 252] - 1
    vol = np.nanstd(c.R[p - 252 : p - 21], axis=0)
    return mom / np.where(vol > 0, vol, np.nan)


@_register(
    "dist_52w_hi",
    "momentum",
    +1,
    "names near their 52w high keep going (anchoring)",
    "Today's price relative to its highest point of the past year (0% = at the high, "
    "−50% = far below it). Names near their 52-week high tend to keep rising: investors "
    "anchor on the old high and hesitate to pay more than it, so good news gets priced "
    "in only gradually — the drift continues after the breakout.",
)
def _dist_hi(c: Ctx, p: int) -> np.ndarray:
    return c.A[p] / np.nanmax(c.A[p - 252 : p], axis=0) - 1


@_register(
    "ma_50_200",
    "momentum",
    +1,
    "golden-cross style long trend",
    "The 50-day average price relative to the 200-day average — the classic golden-cross "
    "gauge. Positive when the medium-term trend sits above the long-term trend, i.e. an "
    "established uptrend; deeply negative in entrenched downtrends. A slower, smoother "
    "cousin of the momentum returns.",
)
def _ma_ratio(c: Ctx, p: int) -> np.ndarray:
    return np.nanmean(c.A[p - 50 : p], axis=0) / np.nanmean(c.A[p - 200 : p], axis=0) - 1


@_register(
    "res_mom_12_1",
    "momentum",
    +1,
    "momentum net of the sector move (idiosyncratic part)",
    "12-1 momentum minus the average 12-1 momentum of the asset's sector — the part of "
    "the trend the asset earned on its own rather than by belonging to a hot sector. "
    "This isolates stock-specific strength and tends to be steadier than raw momentum "
    "because sector booms and busts cancel out of it.",
)
def _res_mom(c: Ctx, p: int) -> np.ndarray:
    mom = pd.Series(c.A[p - 21] / c.A[p - 252] - 1)
    return (mom - mom.groupby(c.sec).transform("mean")).to_numpy()


@_register(
    "rev_1m",
    "reversal",
    -1,
    "1-month winners mean-revert",
    "Return over the most recent month. Strong recent gains tend to partially give back "
    "over the following month — buying frenzies cool off and forced selling rebounds — "
    "so LOW values are attractive and the signal is traded inverted. This is exactly why "
    "the momentum signals skip the latest month.",
)
def _rev_1m(c: Ctx, p: int) -> np.ndarray:
    return c.A[p] / c.A[p - 21] - 1


@_register(
    "rev_1w",
    "reversal",
    -1,
    "1-week winners mean-revert harder",
    "Return over the most recent week — the same mean-reversion effect as rev_1m but "
    "sharper and shorter-lived. Currently the strongest signal in the library. Caveat: "
    "fast signals decay fast — a monthly rebalance captures only part of the effect, "
    "and its high implied turnover makes it the most cost-sensitive signal here.",
)
def _rev_1w(c: Ctx, p: int) -> np.ndarray:
    return c.A[p] / c.A[p - 5] - 1


@_register(
    "vol_63",
    "low_risk",
    -1,
    "low-volatility anomaly (3m)",
    "Standard deviation of daily returns over the past 3 months — how much the price "
    "wiggles day to day. The low-volatility anomaly: boring, stable names have "
    "historically delivered better returns than exciting volatile ones, which get "
    "chronically overbought by lottery-seeking buyers. Low values are attractive.",
)
def _vol_63(c: Ctx, p: int) -> np.ndarray:
    return np.nanstd(c.R[p - 63 : p], axis=0)


@_register(
    "vol_252",
    "low_risk",
    -1,
    "low-volatility anomaly (12m)",
    "Same low-volatility idea as vol_63 but measured over a full year — a slower, "
    "steadier read of how risky a name habitually is, less swayed by one turbulent "
    "month. Largely redundant with vol_63 (they share the family slot).",
)
def _vol_252(c: Ctx, p: int) -> np.ndarray:
    return np.nanstd(c.R[p - 252 : p], axis=0)


@_register(
    "downside_vol_63",
    "low_risk",
    -1,
    "downside semivol is the risk that matters",
    "Like vol_63 but built from negative days only (downside semideviation) — it "
    "measures crash-proneness rather than movement in general. The theory: investors "
    "fear losses specifically, so downside risk should carry the real penalty. In "
    "practice it tracks plain volatility closely.",
)
def _dvol(c: Ctx, p: int) -> np.ndarray:
    r = c.R[p - 63 : p]
    return np.sqrt(np.nanmean(np.minimum(r, 0.0) ** 2, axis=0))


@_register(
    "max_day_1m",
    "low_risk",
    -1,
    "lottery names (one huge day) get overbought",
    "The single biggest daily gain in the past month. A huge one-day pop marks a name as "
    "a 'lottery ticket'; such names attract speculative buying, get overpriced, and then "
    "underperform — the MAX effect. Low values (no wild days) are attractive.",
)
def _maxday(c: Ctx, p: int) -> np.ndarray:
    return np.nanmax(c.R[p - 21 : p], axis=0)


@_register(
    "skew_126",
    "low_risk",
    -1,
    "high skew = lottery preference, overpriced",
    "Skewness of daily returns over 6 months — whether the return distribution leans "
    "toward rare big up-days (positive skew) or rare big down-days (negative). Lottery "
    "preference theory says positively skewed names get overpriced and lag. Not admitted "
    "here: the effect showed no consistent sign in this universe.",
)
def _skew(c: Ctx, p: int) -> np.ndarray:
    r = c.R[p - 126 : p]
    m = np.nanmean(r, axis=0)
    s = np.nanstd(r, axis=0)
    with np.errstate(all="ignore"):
        return np.nanmean((r - m) ** 3, axis=0) / np.where(s > 0, s**3, np.nan)


@_register(
    "parkinson_63",
    "low_risk",
    -1,
    "high-low range vol (catches intraday risk)",
    "A volatility estimate built from each day's high-to-low range instead of "
    "close-to-close changes (the Parkinson estimator) — it sees intraday turbulence "
    "that closing prices hide. Same low-volatility hypothesis as vol_63 and largely "
    "redundant with it.",
)
def _parkinson(c: Ctx, p: int) -> np.ndarray:
    with np.errstate(all="ignore"):
        hl = np.log(c.H[p - 63 : p] / c.L[p - 63 : p]) ** 2
        return np.sqrt(np.nanmean(hl, axis=0) / (4 * np.log(2.0)))


@_register(
    "frac_up_6m",
    "trend_quality",
    +1,
    "steady grinders beat streaky names",
    "The share of days over the past 6 months that closed higher than the day before — "
    "how consistent the climb is, ignoring the size of the moves. A 60%-up-days name is "
    "a steady grinder; the hypothesis is that smooth persistent demand continues, while "
    "streaky names driven by a few events don't.",
)
def _fracup(c: Ctx, p: int) -> np.ndarray:
    return np.nanmean(c.R[p - 126 : p] > 0, axis=0)


@_register(
    "trend_r2_126",
    "trend_quality",
    +1,
    "a clean linear uptrend continues",
    "Fit a straight line through the past 6 months of (log) prices; this is the R² of "
    "that fit, signed by the slope's direction. Near +1 means a clean, orderly uptrend; "
    "near 0 means choppy noise; negative means an orderly DOWNtrend. Orderly trends "
    "reflect steady information flow and tend to continue.",
)
def _trend_r2(c: Ctx, p: int) -> np.ndarray:
    w = np.log(np.where(c.A[p - 126 : p] > 0, c.A[p - 126 : p], np.nan))
    t = np.arange(w.shape[0], dtype="float64")[:, None]
    tm = t - t.mean()
    wm = w - np.nanmean(w, axis=0)
    with np.errstate(all="ignore"):
        cov = np.nansum(tm * wm, axis=0)
        r2 = cov**2 / (np.nansum(tm**2, axis=0) * np.nansum(wm**2, axis=0))
        return np.sign(cov) * r2


@_register(
    "clv_21",
    "trend_quality",
    +1,
    "closing near the daily high = quiet accumulation",
    "Where the price closes within each day's high-low range, averaged over a month "
    "(+1 = always at the day's high, −1 = always at the low). Closing near highs is "
    "classically read as quiet accumulation by patient buyers. Not admitted: it worked "
    "backwards in this universe.",
)
def _clv(c: Ctx, p: int) -> np.ndarray:
    h, lo_, a = c.H[p - 21 : p], c.L[p - 21 : p], c.A[p - 21 : p]
    with np.errstate(all="ignore"):
        return np.nanmean((2 * a - h - lo_) / np.where(h > lo_, h - lo_, np.nan), axis=0)


@_register(
    "turnover_surge",
    "volume",
    +1,
    "rising turnover flags fresh interest",
    "Average EUR trading turnover of the last 20 days relative to the last 60 — is money "
    "flowing through this name faster than usual? Rising activity often accompanies new "
    "information and attention, and moves that arrive on rising volume tend to carry "
    "further than moves on thin air.",
)
def _tsurge(c: Ctx, p: int) -> np.ndarray:
    with np.errstate(all="ignore"):
        return np.nanmean(c.T[p - 20 : p], axis=0) / np.nanmean(c.T[p - 60 : p], axis=0)


@_register(
    "amihud_63",
    "volume",
    +1,
    "illiquidity premium: |ret| per EUR traded",
    "Amihud illiquidity: how much the price moves per euro traded, averaged over 3 "
    "months. High = a thin market where small flows move the price. Classic theory says "
    "illiquid names must pay a return premium to compensate. Not admitted here — "
    "plausibly because the eToro universe is pre-screened toward liquid instruments.",
)
def _amihud(c: Ctx, p: int) -> np.ndarray:
    with np.errstate(all="ignore"):
        t = c.T[p - 63 : p]
        return np.nanmean(np.abs(c.R[p - 63 : p]) / np.where(t > 0, t, np.nan), axis=0)


@_register(
    "sector_mom_1m",
    "sector",
    +1,
    "hot sectors stay hot (1m)",
    "The average past-month return of the asset's sector, assigned to every member — a "
    "pure 'be in the right sector' bet at a monthly horizon. Not admitted: sector "
    "rankings persist too weakly for the effect to help at the individual-name level "
    "(measured rank persistence ≈ +0.06).",
)
def _sec_mom_1m(c: Ctx, p: int) -> np.ndarray:
    r = pd.Series(c.A[p] / c.A[p - 21] - 1)
    return r.groupby(c.sec).transform("mean").to_numpy()


@_register(
    "sector_mom_12_1",
    "sector",
    +1,
    "hot sectors stay hot (12-1m)",
    "The sector's average 12-1 momentum assigned to every member — slow sector rotation: "
    "hold whatever belongs to the strongest sectors of the past year. Not admitted: the "
    "effect flipped sign between the two halves of the develop window.",
)
def _sec_mom_12(c: Ctx, p: int) -> np.ndarray:
    r = pd.Series(c.A[p - 21] / c.A[p - 252] - 1)
    return r.groupby(c.sec).transform("mean").to_numpy()


# ── evaluation ───────────────────────────────────────────────────────────────
def _cutoff_positions(ctx: Ctx, start: str, end: str) -> list[tuple[int, int]]:
    cuts = pd.date_range(start=start, end=end, freq="MS")
    out = []
    for i in range(len(cuts) - 1):
        p = int(ctx.idx.searchsorted(cuts[i], "right")) - 1
        pn = int(ctx.idx.searchsorted(cuts[i + 1], "right")) - 1
        if p >= _HISTORY_BARS and pn > p:
            out.append((p, pn))
    return out


def _base_mask(ctx: Ctx, p: int, nxt: np.ndarray) -> np.ndarray:
    return (
        ctx.fresh[p]
        & np.isfinite(nxt)
        & np.isfinite(ctx.A[p - _HISTORY_BARS])  # seasoned: a year of history
        & (ctx.A[p] > 0)
    )


def _rank_ic(a: np.ndarray, b: np.ndarray) -> float:
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    return float(np.corrcoef(ra, rb)[0, 1])


_CLASS_MIN = 50  # min names for a per-asset-class IC to count
_MIN_YEAR_MONTHS = 6  # a year needs this many monthly ICs to enter the yearly hit rate

# Advisory flag → (≤3-char abbreviation, hover explanation). The engine emits
# the full names in `flags`; UIs render the short form with the tooltip.
FLAG_INFO = {
    "decaying": (
        "DEC",
        "Decaying: the fitted IC trend, extrapolated over half the window, wipes out ≥40% "
        "of the mean IC — the effect is eroding and likely to keep fading (this is what "
        "killed rev_1w out-of-sample).",
    ),
    "event-driven": (
        "EVT",
        "Event-driven: remove its 5 best months and the mean IC falls below half — the "
        "edge comes from a few episodes, not a steady effect.",
    ),
    "cost-fragile": (
        "CST",
        "Cost-fragile: the top-decile edge turns negative at just 2× assumed spread "
        "costs — little margin for real-world trading friction.",
    ),
    "beta-like": (
        "BET",
        "Beta-like: the monthly top-decile edge correlates ≥0.5 with the universe "
        "return — much of it is market direction, not selection skill.",
    ),
    "illiquid-alpha": (
        "ILQ",
        "Illiquid alpha: the IC within the most liquid half of the universe is under "
        "half the overall IC — the edge concentrates in names that can't absorb money.",
    ),
    "lag-fragile": (
        "LAG",
        "Lag-fragile: computing the signal 2 days stale halves the IC — the edge depends "
        "on precise timing, a hallmark of microstructure artifacts (bid-ask bounce, "
        "stale closes).",
    ),
    "timing-dup": (
        "TIM",
        "Timing duplicate: its monthly IC series correlates ≥0.7 with an admitted "
        "signal — it earns in the same months, so it adds little diversification.",
    ),
    "redundant": (
        "RED",
        "Redundant: the marginal IC (after the admitted library explains its share) is "
        "under 40% of the raw IC — mostly a repackaging of signals you already have.",
    ),
}


def _block_boot_p(ic: np.ndarray, sign: int, n_boot: int = 2000, block: int = 6) -> float:
    """One-sided moving-block-bootstrap p-value for 'mean IC is 0': how often a
    resampled zero-mean series (blocks preserve autocorrelation) beats the
    observed mean in the hypothesized direction. Seeded → reproducible."""
    x = ic - ic.mean()
    n = len(x)
    block = min(block, n)
    rng = np.random.default_rng(0)
    starts = rng.integers(0, n - block + 1, size=(n_boot, -(-n // block)))
    take = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(n_boot, -1)[:, :n]
    means = x[take].mean(axis=1)
    stat = sign * ic.mean()
    return float(((sign * means >= stat).sum() + 1) / (n_boot + 1))


def _bh_fdr(pvals: list[float | None], q: float) -> list[bool]:
    """Benjamini–Hochberg: which p-values survive at false-discovery rate q."""
    idx = [i for i, p in enumerate(pvals) if p is not None]
    ranked = sorted(idx, key=lambda i: pvals[i])
    m = len(ranked)
    passed = set()
    thresh = 0
    for k, i in enumerate(ranked, start=1):
        if pvals[i] <= k / m * q:
            thresh = k
    for k, i in enumerate(ranked, start=1):
        if k <= thresh:
            passed.add(i)
    return [i in passed for i in range(len(pvals))]


def evaluate(
    ctx: Ctx,
    start: str,
    end: str,
    progress: Callable[[float, str], None] | None = None,
    n_boot: int = 2000,
    fdr_q: float = 0.10,
    placebo: bool = False,
    with_detail: bool = False,
) -> pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]:
    """Monthly rank-IC scoreboard + the admission battery for every registered
    signal on [start, end). Four gates decide `admitted`:

    - confidence: block-bootstrap p-value survives Benjamini–Hochberg FDR at
      `fdr_q` across the whole library (the multiple-testing guard);
    - tradability: the hypothesized-best decile beats the universe *long-only*,
      net of spread costs on that bucket's monthly turnover;
    - robustness: the IC has the hypothesized sign in ≥60% of years, and at
      least one instrument type (Stocks / ETF / Crypto) independently supports
      it — the `scope` column names which ones do;
    - cleanliness: decile returns rise monotonically with the signal
      (|Spearman| of the bucket curve ≥ 0.6 in the hypothesized direction).

    Horizon ICs at ~1w/1m/3m are reported for decay inspection, and per-regime
    ICs (bull/bear × calm/turbulent, classified a priori from the equal-weight
    universe index using only pre-cutoff data) for regime inspection — neither
    is gated.

    Advisory columns (reported + summarized in `flags`, not gated): marginal
    IC vs the admitted library (orthogonality), IC-timing correlation with
    admitted signals, execution-lag IC (signal 2 days stale), best-5-months
    trimmed IC (event concentration), net spread at 2×/3× costs, liquid-half
    IC, top-decile-spread beta to the universe, and the IC trend (decay slope).

    `placebo=True` shuffles forward returns within each month — the battery
    must then admit nothing (a harness self-test against look-ahead bugs).
    `with_detail=True` also returns per-signal monthly series for charts."""
    pos = _cutoff_positions(ctx, start, end)

    # Regime classification per cutoff — fixed definitions, no look-ahead
    # (bull = EW index at/above its own 200-day mean; turbulent = trailing
    # 63-day index vol above the median of its prior history). Shared with the
    # regime-timeline chart via _eq_index / _regime_at so the two never drift.
    eq_curve, roll_vol = _eq_index(ctx)

    def _regime(p: int) -> tuple[bool, bool]:
        return _regime_at(eq_curve, roll_vol, p)

    def _fwd(p: int, days: int) -> np.ndarray | None:
        tgt = ctx.idx[p] + pd.Timedelta(days=days)
        if tgt > ctx.idx[-1]:
            return None
        q_ = int(ctx.idx.searchsorted(tgt, "right")) - 1
        if q_ <= p:
            return None
        with np.errstate(all="ignore"):
            return np.clip(ctx.A[q_] / ctx.A[p] - 1, -0.95, 4.0)

    types = ("Stocks", "ETF", "Crypto")
    type_masks = {ty: ctx.itype == ty for ty in types}
    acc: dict[str, dict[str, Any]] = {
        s.name: {
            "ic": [], "dates": [], "yr": [], "cover": [], "ic1w": [], "ic3m": [],
            "ic_type": {ty: [] for ty in types},
            "ic_regime": {rg: [] for rg in ("bull", "bear", "calm", "turb")},
            "ic_lag2": [], "ic_liq": [],
            "gross": [], "cost": [], "uni": [], "dec": [], "prev_top": None,
        }
        for s in SIGNALS
    }
    # per-month stores for the phase-2 orthogonality pass
    ranks_store: list[dict[str, np.ndarray]] = []
    nxt_store: list[np.ndarray] = []
    for i, (p, pn) in enumerate(pos):
        if progress and i % 6 == 0:
            progress(i / len(pos), f"scoring {ctx.idx[p].date()!s}")
        with np.errstate(all="ignore"):
            nxt = np.clip(ctx.A[pn] / ctx.A[p] - 1, -0.95, 4.0)
        if placebo:  # scramble the future within the month: real alpha must vanish
            rng = np.random.default_rng(1000 + i)
            fin = np.isfinite(nxt)
            vals = nxt[fin]
            rng.shuffle(vals)
            nxt = nxt.copy()
            nxt[fin] = vals
        nxt_1w, nxt_3m = _fwd(p, 7), _fwd(p, 91)
        base = _base_mask(ctx, p, nxt)
        bull, turb = _regime(p)
        uni_m = float(np.mean(nxt[base])) if base.any() else np.nan
        with np.errstate(all="ignore"):
            liq = np.nanmean(ctx.T[max(0, p - 63) : p], axis=0)
        liqb = liq[base & np.isfinite(liq)]
        liquid_mask = np.isfinite(liq) & (liq >= (np.median(liqb) if len(liqb) else np.inf))
        month_ranks: dict[str, np.ndarray] = {}
        ranks_store.append(month_ranks)
        nxt_store.append(nxt)
        for s in SIGNALS:
            with np.errstate(all="ignore"):
                v = s.fn(ctx, p)
            ok = base & np.isfinite(v)
            if int(ok.sum()) < MIN_NAMES:
                continue
            a = acc[s.name]
            ic_m = _rank_ic(v[ok], nxt[ok])
            a["ic"].append(ic_m)
            a["dates"].append(str(ctx.idx[p].date()))
            a["ic_regime"]["bull" if bull else "bear"].append(ic_m)
            a["ic_regime"]["turb" if turb else "calm"].append(ic_m)
            a["yr"].append(int(ctx.idx[p].year))
            a["cover"].append(int(ok.sum()))
            a["uni"].append(uni_m)
            for tgt, key in ((nxt_1w, "ic1w"), (nxt_3m, "ic3m")):
                if tgt is not None:
                    okh = ok & np.isfinite(tgt)
                    if int(okh.sum()) >= MIN_NAMES:
                        a[key].append(_rank_ic(v[okh], tgt[okh]))
            for ty in types:
                okc = ok & type_masks[ty]
                if int(okc.sum()) >= _CLASS_MIN:
                    a["ic_type"][ty].append(_rank_ic(v[okc], nxt[okc]))
            # execution-lag probe: the same signal computed 2 days earlier —
            # microstructure artifacts (bid-ask bounce, stale closes) die here
            with np.errstate(all="ignore"):
                v2 = s.fn(ctx, p - 2)
            ok2 = base & np.isfinite(v2)
            if int(ok2.sum()) >= MIN_NAMES:
                a["ic_lag2"].append(_rank_ic(v2[ok2], nxt[ok2]))
            # liquid-half probe: does the alpha survive where money can flow?
            okl = ok & liquid_mask
            if int(okl.sum()) >= _CLASS_MIN:
                a["ic_liq"].append(_rank_ic(v[okl], nxt[okl]))
            # pct ranks: reused for deciles now and the orthogonality pass later
            ids = np.where(ok)[0]
            pr_ok = pd.Series(v[ok]).rank(pct=True).to_numpy()
            pr = np.full(len(ctx.names), np.nan, dtype="float32")
            pr[ids] = pr_ok
            month_ranks[s.name] = pr
            dec = np.minimum((pr_ok * 10).astype(int), 9)
            a["dec"].append([float(np.mean(nxt[ids[dec == d]])) if (dec == d).any() else np.nan for d in range(10)])
            # Heavy ties (e.g. many names exactly at their 52w high) can leave
            # the extreme bucket empty — record NaN rather than poison averages.
            best = dec == (9 if s.sign > 0 else 0)
            if best.any():
                top = frozenset(ids[best])
                gross = float(np.mean(nxt[ids[best]]) - np.mean(nxt[ok]))
                prev = a["prev_top"]
                frac_new = 0.5 if prev is None else 1.0 - len(top & prev) / max(len(top), 1)
                a["gross"].append(gross)
                a["cost"].append(frac_new * float(np.mean(ctx.spreads[ids[best]])) / 100.0)
                a["prev_top"] = top
            else:
                a["gross"].append(np.nan)
                a["cost"].append(np.nan)

    def _mean_t(vals: list[float]) -> tuple[float | None, float | None]:
        arr = np.array(vals)
        if len(arr) < 12:
            return (round(float(arr.mean()), 4) if len(arr) else None), None
        if arr.std() == 0:  # a constant IC series (perfect synthetic signals)
            m = float(arr.mean())
            return round(m, 4), (float("inf") * np.sign(m) if m else 0.0)
        return round(float(arr.mean()), 4), round(float(arr.mean() / arr.std() * np.sqrt(len(arr))), 2)

    rows = []
    for s in SIGNALS:
        a = acc[s.name]
        ic = np.array(a["ic"])
        if len(ic) < 12:
            rows.append({"signal": s.name, "family": s.family, "sign": s.sign, "months": len(ic)})
            continue
        h = len(ic) // 2
        p_boot = _block_boot_p(ic, s.sign, n_boot=n_boot)
        # yearly hit rate over years with enough months
        yr = pd.Series(ic).groupby(pd.Series(a["yr"]))
        yr_means = yr.mean()[yr.size() >= _MIN_YEAR_MONTHS]
        yearly_hit = float((np.sign(yr_means) == s.sign).mean()) if len(yr_means) else None
        # per-type support: does each instrument type independently show the
        # effect (t ≥ 1 in the hypothesized direction, ≥12 months of data)?
        type_ic: dict[str, float | None] = {}
        supporters = []
        for ty in types:
            m_ty, t_ty = _mean_t(a["ic_type"][ty])
            type_ic[ty] = m_ty
            if t_ty is not None and t_ty * s.sign >= 1.0:
                supporters.append(ty.lower())
        scope = "all" if len(supporters) == 3 else "+".join(supporters) if supporters else "none"
        # decile monotonicity of the average bucket curve, signed by hypothesis
        curve = np.nanmean(np.array(a["dec"], dtype="float64"), axis=0)
        vd = np.isfinite(curve)
        mono = round(s.sign * _rank_ic(np.arange(10)[vd].astype("float64"), curve[vd]), 2) if vd.sum() >= 5 else None
        gross = np.array(a["gross"], dtype="float64")
        cost = np.array(a["cost"], dtype="float64")
        fin_g = np.isfinite(gross)

        def _net_ann(k: float) -> float:
            return round(float(np.mean(gross[fin_g] - k * cost[fin_g]) * 12 * 100), 2) if fin_g.any() else 0.0

        spread_net_ann = _net_ann(1.0)
        # beta disguise: does the top-decile edge just track the market?
        uni = np.array(a["uni"], dtype="float64")
        fin_b = fin_g & np.isfinite(uni)
        beta_corr = (
            round(float(np.corrcoef(gross[fin_b] - cost[fin_b], uni[fin_b])[0, 1]), 2)
            if int(fin_b.sum()) > 24
            else None
        )
        # decay: linear trend of the signed IC series, per year
        sic = s.sign * ic
        ic_trend = round(float(np.polyfit(np.arange(len(sic)), sic, 1)[0] * 12), 4)
        # event concentration: mean IC without the 5 best months
        ic_trim5 = (
            round(float(np.mean(np.delete(ic, np.argsort(-sic)[:5]))), 4) if len(ic) > 20 else None
        )
        ic1w, _ = _mean_t(a["ic1w"])
        ic3m, _ = _mean_t(a["ic3m"])
        g_trade = spread_net_ann > 0
        g_robust = yearly_hit is not None and yearly_hit >= 0.6 and scope != "none"
        g_clean = mono is not None and mono >= 0.6
        rows.append(
            {
                "signal": s.name,
                "family": s.family,
                "sign": s.sign,
                "mean_ic": round(float(ic.mean()), 4),
                "t_stat": round(float(ic.mean() / ic.std() * np.sqrt(len(ic))), 2),
                "ic_h1": round(float(ic[:h].mean()), 4),
                "ic_h2": round(float(ic[h:].mean()), 4),
                "pct_pos": round(float((ic > 0).mean() * 100), 0),
                "months": len(ic),
                "avg_names": int(np.mean(a["cover"])),
                "sign_ok": bool(np.sign(ic[:h].mean()) == s.sign and np.sign(ic[h:].mean()) == s.sign),
                "p_boot": round(p_boot, 4),
                "spread_net_ann": spread_net_ann,
                "yearly_hit": round(yearly_hit, 2) if yearly_hit is not None else None,
                "years": int(len(yr_means)),
                "scope": scope,
                "ic_stocks": type_ic["Stocks"],
                "ic_etf": type_ic["ETF"],
                "ic_crypto": type_ic["Crypto"],
                "ic_bull": _mean_t(a["ic_regime"]["bull"])[0],
                "ic_bear": _mean_t(a["ic_regime"]["bear"])[0],
                "ic_calm": _mean_t(a["ic_regime"]["calm"])[0],
                "ic_turb": _mean_t(a["ic_regime"]["turb"])[0],
                "ic_lag2": _mean_t(a["ic_lag2"])[0],
                "ic_liquid": _mean_t(a["ic_liq"])[0],
                "ic_trim5": ic_trim5,
                "ic_trend": ic_trend,
                "spread_net_2x": _net_ann(2.0),
                "spread_net_3x": _net_ann(3.0),
                "beta_corr": beta_corr,
                "mono": mono,
                "ic_1w": ic1w,
                "ic_3m": ic3m,
                "g_trade": g_trade,
                "g_robust": g_robust,
                "g_clean": g_clean,
            }
        )
    board = pd.DataFrame(rows)
    # confidence gate: FDR across the whole library (multiple-testing guard)
    if "p_boot" in board.columns:
        board["g_conf"] = _bh_fdr([p if p == p else None for p in board["p_boot"]], fdr_q)
        board["admitted"] = (
            board["g_conf"].fillna(False)
            & board["g_trade"].fillna(False)
            & board["g_robust"].fillna(False)
            & board["g_clean"].fillna(False)
        )
    else:  # every signal too short to score
        board["g_conf"] = False
        board["admitted"] = False

    # ── phase 2: value relative to the admitted library ─────────────────────
    if progress:
        progress(1.0, "orthogonality vs admitted library")
    admitted_names = list(board.loc[board["admitted"].fillna(False), "signal"])
    sic_by_date = {
        s.name: dict(
            zip(acc[s.name]["dates"], (np.array(acc[s.name]["ic"]) * s.sign).tolist())
        )
        for s in SIGNALS
    }
    marg: dict[str, float | None] = {}
    timing: dict[str, str | None] = {}
    timing_val: dict[str, float | None] = {}
    n_others: dict[str, int] = {}
    for s in SIGNALS:
        if len(acc[s.name]["ic"]) < 12:
            continue
        others = [o for o in admitted_names if o != s.name]
        n_others[s.name] = len(others)
        # timing duplication: even a cross-sectionally different signal adds
        # nothing if it earns in exactly the same months as the library
        mine = sic_by_date[s.name]
        best: tuple[float, str] | None = None
        for o in others:
            common = [d for d in mine if d in sic_by_date[o]]
            if len(common) < 24:
                continue
            r = float(np.corrcoef([mine[d] for d in common], [sic_by_date[o][d] for d in common])[0, 1])
            if best is None or abs(r) > abs(best[0]):
                best = (r, o)
        timing[s.name] = f"{best[0]:+.2f} {best[1]}" if best else None
        timing_val[s.name] = best[0] if best else None
        # marginal IC: rank-IC of the part of this signal the admitted library
        # can't explain (per-month cross-sectional residual)
        mi: list[float] = []
        for m, month_ranks in enumerate(ranks_store):
            y = month_ranks.get(s.name)
            if y is None:
                continue
            xs = [month_ranks[o] for o in others if o in month_ranks]
            nxt_m = nxt_store[m]
            valid = np.isfinite(y) & np.isfinite(nxt_m)
            for xc in xs:
                valid &= np.isfinite(xc)
            if int(valid.sum()) < MIN_NAMES:
                continue
            yv = y[valid].astype("float64")
            if xs:
                mat = np.column_stack(
                    [xc[valid].astype("float64") for xc in xs] + [np.ones(int(valid.sum()))]
                )
                beta, *_ = np.linalg.lstsq(mat, yv, rcond=None)
                yv = yv - mat @ beta
            mi.append(_rank_ic(yv, nxt_m[valid]))
        marg[s.name] = round(float(np.mean(mi)), 4) if len(mi) >= 12 else None
    board["ic_marginal"] = board["signal"].map(marg)
    board["timing_dup"] = board["signal"].map(timing)

    # advisory warning flags (never gate admission — they say "handle with care")
    def _flags(r: pd.Series) -> str:
        mean_ic = r.get("mean_ic")
        if mean_ic is None or mean_ic != mean_ic:
            return ""
        ms = r["sign"] * mean_ic
        if ms <= 0:
            return ""
        out = []
        if r["ic_trend"] is not None and r["ic_trend"] < 0 and abs(r["ic_trend"]) * (r["months"] / 24.0) >= 0.4 * ms:
            out.append("decaying")
        if r["ic_trim5"] is not None and r["sign"] * r["ic_trim5"] < 0.5 * ms:
            out.append("event-driven")
        if r["spread_net_2x"] is not None and r["spread_net_2x"] <= 0:
            out.append("cost-fragile")
        if r["beta_corr"] is not None and abs(r["beta_corr"]) >= 0.5:
            out.append("beta-like")
        if r["ic_liquid"] is not None and r["sign"] * r["ic_liquid"] < 0.5 * ms:
            out.append("illiquid-alpha")
        if r["ic_lag2"] is not None and r["sign"] * r["ic_lag2"] < 0.5 * ms:
            out.append("lag-fragile")
        tv = timing_val.get(r["signal"])
        if tv is not None and abs(tv) >= 0.7:
            out.append("timing-dup")
        mg = marg.get(r["signal"])
        if mg is not None and n_others.get(r["signal"], 0) > 0 and r["sign"] * mg < 0.4 * ms:
            out.append("redundant")
        return ",".join(out)

    board["flags"] = board.apply(_flags, axis=1)
    if not with_detail:
        return board

    detail = {
        "signals": {
            s.name: {
                "sign": s.sign,
                "dates": acc[s.name]["dates"],
                "ic": [round(float(x), 4) for x in acc[s.name]["ic"]],
                "gross": [None if x != x else round(float(x), 5) for x in acc[s.name]["gross"]],
                "cost": [None if x != x else round(float(x), 5) for x in acc[s.name]["cost"]],
                "dec": [
                    None if x != x else round(float(x), 5)
                    for x in np.nanmean(np.array(acc[s.name]["dec"], dtype="float64"), axis=0)
                ]
                if acc[s.name]["dec"]
                else [],
            }
            for s in SIGNALS
            if acc[s.name]["ic"]
        },
    }
    return board, detail


def redundancy(
    ctx: Ctx,
    start: str,
    end: str,
    every: int = 6,
    progress: Callable[[float, str], None] | None = None,
) -> pd.DataFrame:
    """Average cross-sectional rank correlation between signals (sampled every
    `every`-th month) — near-duplicates should share one family slot, not two."""
    pos = _cutoff_positions(ctx, start, end)[::every]
    names = [s.name for s in SIGNALS]
    acc = np.zeros((len(SIGNALS), len(SIGNALS)))
    cnt = np.zeros_like(acc)
    for i, (p, pn) in enumerate(pos):
        if progress:
            progress(i / len(pos), f"correlating {ctx.idx[p].date()!s}")
        nxt = np.clip(ctx.A[pn] / ctx.A[p] - 1, -0.95, 4.0)
        base = _base_mask(ctx, p, nxt)
        vals = []
        for s in SIGNALS:
            with np.errstate(all="ignore"):
                v = s.fn(ctx, p)
            vals.append(np.where(base & np.isfinite(v), v, np.nan))
        for i in range(len(SIGNALS)):
            for j in range(i + 1, len(SIGNALS)):
                ok = np.isfinite(vals[i]) & np.isfinite(vals[j])
                if ok.sum() < MIN_NAMES:
                    continue
                r = _rank_ic(vals[i][ok], vals[j][ok])
                acc[i, j] += r
                cnt[i, j] += 1
    with np.errstate(all="ignore"):
        m = np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan)
    return pd.DataFrame(m, index=names, columns=names)


def combo_ic(
    ctx: Ctx, start: str, end: str, members: list[str] | None = None
) -> dict[str, Any]:
    """IC of the family-balanced combination: signed pct-ranks averaged within
    each family, families averaged equally. `members` defaults to all signals."""
    chosen = [s for s in SIGNALS if members is None or s.name in members]
    pos = _cutoff_positions(ctx, start, end)
    ics = []
    for p, pn in pos:
        nxt = np.clip(ctx.A[pn] / ctx.A[p] - 1, -0.95, 4.0)
        base = _base_mask(ctx, p, nxt)
        fam_scores: dict[str, list[np.ndarray]] = {}
        for s in chosen:
            with np.errstate(all="ignore"):
                v = s.fn(ctx, p)
            ok = base & np.isfinite(v)
            if int(ok.sum()) < MIN_NAMES:
                continue
            pr = pd.Series(np.where(ok, v, np.nan)).rank(pct=True).to_numpy() - 0.5
            fam_scores.setdefault(s.family, []).append(s.sign * np.where(ok, pr, 0.0))
        if not fam_scores:
            continue
        fams = [np.mean(v, axis=0) for v in fam_scores.values()]
        score = np.mean(fams, axis=0)
        ok = base & np.isfinite(score)
        if int(ok.sum()) >= MIN_NAMES:
            ics.append(_rank_ic(score[ok], nxt[ok]))
    a = np.array(ics)
    return {
        "mean_ic": round(float(a.mean()), 4),
        "t_stat": round(float(a.mean() / a.std() * np.sqrt(len(a))), 2),
        "pct_pos": round(float((a > 0).mean() * 100), 0),
        "months": len(a),
        "families": sorted({s.family for s in chosen}),
    }
