"""Factor covariance model — V = BΩBᵀ + Ψ — over the eToro universe.

A diagnostic model, not a trading model: it exists so a human can look at the
/correlation page and judge whether the covariance structure the optimizer
would eventually consume matches reality.

The pieces
    B (N×K)   factor exposures — one weighted least-squares regression of each
              instrument's daily returns on the K factor returns
    Ω (K×K)   factor covariance, built in two clocks: a FAST EWMA for factor
              volatilities (regimes change quickly) and a SLOW one for factor
              correlations (they are structural)
    Ψ (N×N)   diagonal idiosyncratic variance — the EWMA variance of each
              regression's residual; off-diagonal terms are assumed zero
    V         B Ω Bᵀ + Ψ, converted to correlations for display

Every estimator here is a *causal* EWMA: the estimate on day t uses days ≤ t
only. That is what makes the tracking chart honest — the model line at any
date is what the model would have said on that date, so plotting it against the
realized rolling correlation is a fair test rather than a fit of the past.
Concretely, each accumulator obeys S_t = x_t + θ·S_{t−1} with θ = 2^(−1/H) for
half-life H, so today's weight is 1 and a day k steps back weighs θ^k. The
weight sum is carried alongside and divided out, so the estimate is unbiased
from the first observation rather than shrunk toward a zero prior.

Returns are read from the EUR-converted store: a covariance matrix mixing
JPY-, GBP- and USD-quoted series would be measuring FX as much as anything
else, and the rest of this repo backtests in EUR for the same reason. Returns
are treated as mean-zero in every EWMA (at daily frequency the mean is noise);
the realized rolling correlation does de-mean, because it is a plain windowed
sample statistic.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from etoro_yfinance import prices

# ── config ───────────────────────────────────────────────────────────────────
# Each factor is one tradable proxy whose daily return IS the factor return.
# This is configuration: add or swap an entry and every exposure, Ω cell and
# variance split downstream is recomputed from it (restart the web server —
# Python modules do not hot-reload).
FACTORS: dict[str, str] = {
    "market": "ACWI",
    "rates": "IEF",
    "credit": "HYG",
    "dollar": "UUP",
    "commodity": "DBC",
    "energy": "XLE",
    "tech": "XLK",
    "financials": "XLF",
}

# ── fixed parameters ─────────────────────────────────────────────────────────
H_B = 250  # exposure EWMA half-life (days) — slow, exposures are stable
H_PSI = 60  # idiosyncratic vol half-life
H_OMEGA_V = 30  # factor vol half-life — fast
H_OMEGA_C = 250  # factor correlation half-life — slow
REAL_WINDOW = 60  # rolling realized-correlation window
MIN_HISTORY = 300  # days required before the model emits output
RIDGE = 1e-8  # added to the diagonal of (FᵀWF) before inverting

# Days older than this contribute < 0.5% weight at the slowest half-life (250d),
# so the fit is capped there: it bounds work on the whole-universe pass without
# changing any number visibly.
MAX_DAYS = 2500


@dataclass(frozen=True)
class Params:
    """The half-lives and windows above, overridable per request — the point of
    a diagnostic page is being able to move a knob and watch what changes."""

    h_b: float = H_B
    h_psi: float = H_PSI
    h_omega_v: float = H_OMEGA_V
    h_omega_c: float = H_OMEGA_C
    real_window: int = REAL_WINDOW
    min_history: int = MIN_HISTORY
    ridge: float = RIDGE

    def as_dict(self) -> dict[str, float]:
        return {
            "h_b": self.h_b,
            "h_psi": self.h_psi,
            "h_omega_v": self.h_omega_v,
            "h_omega_c": self.h_omega_c,
            "real_window": self.real_window,
            "min_history": self.min_history,
        }


DEFAULT_PARAMS = Params()


def factor_names() -> list[str]:
    return list(FACTORS)


def factor_tickers() -> list[str]:
    return list(FACTORS.values())


# ── returns ──────────────────────────────────────────────────────────────────
def ewma_weights(n: int, halflife: float) -> np.ndarray:
    """Weights for `n` days in date order: the last (most recent) day weighs 1,
    a day k steps back weighs θ^k with θ = 2^(−1/halflife)."""
    theta = 2.0 ** (-1.0 / float(halflife))
    return theta ** np.arange(n - 1, -1, -1, dtype="float64")


def _decay(halflife: float) -> float:
    return 2.0 ** (-1.0 / float(halflife))


def daily_returns(ticker: str, eur: bool = True) -> pd.Series | None:
    """One instrument's daily adjusted-close returns, or None if unusable.

    Runs the store's adj_close through repair_adj_close first: Yahoo's
    adjustment chains occasionally print a phantom overnight jump, and a single
    ×14 bar would dominate every covariance this instrument appears in."""
    df = prices.load_prices(ticker, eur=eur, columns=["adj_close", "close"])
    if df is None or len(df) < 2 or "adj_close" not in df.columns:
        return None
    px = prices.repair_adj_close(df).astype("float64")
    px = px[px > 0]
    if len(px) < 2:
        return None
    r = px.pct_change()
    r = r[np.isfinite(r.to_numpy())]
    r.index = pd.to_datetime(r.index)
    return r if len(r) else None


_FACTOR_CACHE: dict[tuple[Any, ...], pd.DataFrame] = {}


def factor_returns(eur: bool = True) -> pd.DataFrame:
    """The K factor return series aligned on their common trading days
    (date × factor name). Cached on the factor set, so editing FACTORS and
    restarting rebuilds it."""
    key = (tuple(FACTORS.items()), eur)
    hit = _FACTOR_CACHE.get(key)
    if hit is not None:
        return hit
    cols: dict[str, pd.Series] = {}
    for name, ticker in FACTORS.items():
        s = daily_returns(ticker, eur=eur)
        if s is None:
            raise MissingFactorError(name, ticker)
        cols[name] = s
    df = pd.DataFrame(cols).dropna()  # inner join on date
    _FACTOR_CACHE[key] = df
    return df


class MissingFactorError(RuntimeError):
    """A configured factor proxy has no stored price history."""

    def __init__(self, name: str, ticker: str) -> None:
        super().__init__(
            f"factor {name!r} proxy {ticker!r} has no stored prices — "
            f"run: uv run python scripts/fetch_factors.py"
        )
        self.name, self.ticker = name, ticker


def _clip(df: pd.DataFrame, end: str | None, max_days: int | None) -> pd.DataFrame:
    if end:
        df = df[df.index <= pd.Timestamp(end)]
    if max_days and len(df) > max_days:
        df = df.iloc[-max_days:]
    return df


# ── the factor block: Ω from a return matrix ─────────────────────────────────
def factor_covariance(f: np.ndarray, params: Params) -> tuple[np.ndarray, np.ndarray]:
    """(Ω, C) from the T×K factor return matrix — volatilities on the fast
    clock, correlations on the slow one, Ω = D C D."""
    t = f.shape[0]
    wv = ewma_weights(t, params.h_omega_v)
    wc = ewma_weights(t, params.h_omega_c)
    var = (wv @ (f * f)) / wv.sum()
    d = np.sqrt(np.maximum(var, 0.0))
    sc = f.T @ (wc[:, None] * f)
    dg = np.sqrt(np.maximum(np.diag(sc), 1e-300))
    corr = sc / np.outer(dg, dg)
    np.fill_diagonal(corr, 1.0)
    return (d[:, None] * corr) * d[None, :], corr


# ── the whole-universe fit ───────────────────────────────────────────────────
@dataclass
class Model:
    """A fitted covariance model over `names`, as of the last date in `dates`."""

    names: list[str]
    factors: list[str]
    dates: list[str]
    params: Params
    f: np.ndarray  # T×K factor returns
    r: np.ndarray  # T×N instrument returns (0 where absent — see `mask`)
    mask: np.ndarray  # T×N: the instrument traded that day
    b: np.ndarray  # N×K exposures
    omega: np.ndarray  # K×K factor covariance
    corr_omega: np.ndarray  # K×K factor correlations (the heatmap)
    psi: np.ndarray  # N idiosyncratic variances
    var_total: np.ndarray  # N EWMA total variances
    v: np.ndarray  # N×N reconstructed covariance

    @property
    def r2(self) -> np.ndarray:
        """Share of each instrument's variance the factors explain."""
        with np.errstate(divide="ignore", invalid="ignore"):
            out = 1.0 - self.psi / self.var_total
        return np.where(np.isfinite(out), out, np.nan)

    def correlation(self) -> np.ndarray:
        d = np.sqrt(np.maximum(np.diag(self.v), 1e-300))
        c = self.v / np.outer(d, d)
        np.fill_diagonal(c, 1.0)
        return np.clip(c, -1.0, 1.0)

    def realized_correlation(self) -> np.ndarray:
        """Plain rolling correlation over the trailing realized window — the
        truth the model is checked against. De-meaned, unlike the EWMAs."""
        w = self.r[-self.params.real_window :]
        x = w - w.mean(axis=0, keepdims=True)
        sd = np.sqrt((x * x).sum(axis=0))
        sd = np.where(sd > 0, sd, np.nan)
        c = (x.T @ x) / np.outer(sd, sd)
        return np.clip(c, -1.0, 1.0)

    def variance_split(self, i: int) -> list[dict[str, Any]]:
        """How instrument i's variance divides among the factors and its own
        noise. Factor k's share is b_ik² Ω_kk / V_ii (the diagonal-only
        approximation — exact only if factors were uncorrelated), the
        idiosyncratic share is Ψ_ii / V_ii; the shares are renormalized to sum
        to 1 so the stacked bar is a full bar."""
        parts = self.b[i] ** 2 * np.diag(self.omega)
        rows = [*zip(self.factors, parts, strict=True), ("idiosyncratic", self.psi[i])]
        total = float(sum(v for _, v in rows))
        if not (total > 0):
            return []
        return [{"factor": k, "share": float(v / total)} for k, v in rows]

    def waterfall(self, i: int, j: int) -> list[dict[str, Any]]:
        """Per-factor contributions to the pair's covariance: the full
        row×column term contrib_k = b_ak (Ω b_b)_k. These sum exactly to
        (BΩBᵀ)_ab, so the bars land on V_ab (Ψ is diagonal → 0 off-diagonal)."""
        return _contributions(self.factors, self.b[i], self.b[j], self.omega)


def _contributions(
    factors: Sequence[str], ba: np.ndarray, bb: np.ndarray, omega: np.ndarray
) -> list[dict[str, Any]]:
    contrib = ba * (omega @ bb)
    cov = float(contrib.sum())
    rows = [
        {
            "factor": f,
            "beta_a": float(ba[k]),
            "beta_b": float(bb[k]),
            "contribution": float(contrib[k]),
            "contribution_pct": (float(contrib[k] / cov) if cov else None),
        }
        for k, f in enumerate(factors)
    ]
    rows.sort(key=lambda d: -abs(d["contribution"]))
    return rows


def build_matrix(
    tickers: Iterable[str],
    *,
    eur: bool = True,
    end: str | None = None,
    max_days: int | None = MAX_DAYS,
    params: Params = DEFAULT_PARAMS,
    require_recent: bool = True,
    progress: Any = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(factor returns, instrument returns) on the factors' common trading days.

    Instruments are reindexed onto the factor calendar; a day an instrument did
    not trade stays NaN and is masked out of that instrument's own regression
    rather than dropped for everybody (one Tokyo holiday would otherwise cost
    every name a day). Instruments with fewer than `min_history` observations —
    or, with require_recent, a gap inside the realized window — are dropped:
    a realized correlation cannot be formed for them at all."""
    f = _clip(factor_returns(eur=eur), end, max_days)
    cols: dict[str, pd.Series] = {}
    names = list(dict.fromkeys(tickers))
    for n, t in enumerate(names):
        if progress and n % 50 == 0:
            progress(n / max(len(names), 1), f"loading prices {n}/{len(names)}")
        s = daily_returns(t, eur=eur)
        if s is None:
            continue
        s = s.reindex(f.index)
        if int(s.notna().sum()) < params.min_history:
            continue
        if require_recent and s.iloc[-params.real_window :].isna().any():
            continue
        cols[t] = s
    r = pd.DataFrame(cols, index=f.index) if cols else pd.DataFrame(index=f.index)
    return f, r


def fit(
    tickers: Iterable[str] | None = None,
    *,
    frames: tuple[pd.DataFrame, pd.DataFrame] | None = None,
    eur: bool = True,
    end: str | None = None,
    max_days: int | None = MAX_DAYS,
    params: Params = DEFAULT_PARAMS,
    progress: Any = None,
) -> Model:
    """Fit B, Ω, Ψ and V as of the last available day. Pass `frames` to reuse an
    already-built (factors, instruments) pair from build_matrix."""
    f_df, r_df = frames if frames is not None else build_matrix(
        tickers or [], eur=eur, end=end, max_days=max_days, params=params, progress=progress
    )
    f = f_df.to_numpy("float64")
    mask = r_df.notna().to_numpy()
    r = np.nan_to_num(r_df.to_numpy("float64"))
    t, k = f.shape
    n = r.shape[1]
    if progress:
        progress(0.7, f"fitting {n} exposures")

    # Weighted least squares per instrument, all N at once. The weight matrix
    # is the EWMA decay times the instrument's own trading mask, so a name that
    # started late is regressed on the days it actually has.
    wb = ewma_weights(t, params.h_b)[:, None] * mask  # T×N
    gram = np.einsum("tk,tl,tn->nkl", f, f, wb, optimize=True)  # N×K×K
    rhs = np.einsum("tk,tn->nk", f, wb * r, optimize=True)  # N×K
    gram += params.ridge * np.eye(k)[None, :, :]
    b = np.linalg.solve(gram, rhs[:, :, None])[:, :, 0] if n else np.zeros((0, k))

    # Idiosyncratic variance: the EWMA variance of what the factors miss.
    resid = (r - f @ b.T) * mask
    wp = ewma_weights(t, params.h_psi)[:, None] * mask
    wsum = np.maximum(wp.sum(axis=0), 1e-300)
    psi = (wp * resid * resid).sum(axis=0) / wsum
    var_total = (wp * r * r).sum(axis=0) / wsum

    omega, corr = factor_covariance(f, params)
    if progress:
        progress(0.85, "reconstructing covariance")
    v = b @ omega @ b.T + np.diag(psi)
    return Model(
        names=list(r_df.columns),
        factors=factor_names(),
        dates=[str(d.date()) for d in f_df.index],
        params=params,
        f=f,
        r=r,
        mask=mask,
        b=b,
        omega=omega,
        corr_omega=corr,
        psi=psi,
        var_total=var_total,
        v=v,
    )


# ── the causal per-day pass (the tracking chart) ─────────────────────────────
@dataclass
class PairPass:
    """The output of one forward pass over a pair: the model's implied
    correlation on every day, plus the final-day state behind it."""

    dates: list[str]
    model: list[float | None]
    b_a: np.ndarray
    b_b: np.ndarray
    omega: np.ndarray
    corr_omega: np.ndarray
    psi: tuple[float, float]
    var_total: tuple[float, float]
    fitted: np.ndarray  # T×2 running-fit values b_t·f_t
    resid: np.ndarray  # T×2 residuals
    v: np.ndarray  # 2×2 covariance as of the last day


def pair_pass(f: np.ndarray, ra: np.ndarray, rb: np.ndarray, params: Params) -> PairPass:
    """One forward pass computing the model's implied correlation for a pair on
    every day, using only data through that day.

    Every estimator is a recursive EWMA, so this is a single sweep rather than a
    refit per day: the accumulators are rolled forward, the two exposure vectors
    are solved from them, and V restricted to the pair falls out. Nothing here
    can see the future, which is what makes the resulting line comparable to the
    realized correlation."""
    t, k = f.shape
    thb, thp, thv, thc = (
        _decay(params.h_b),
        _decay(params.h_psi),
        _decay(params.h_omega_v),
        _decay(params.h_omega_c),
    )
    gram = np.zeros((k, k))
    cross = np.zeros((k, 2))
    sv = np.zeros(k)
    sc = np.zeros((k, k))
    wv = wc = 0.0
    pvar = np.zeros(2)  # residual EWMA accumulators
    tvar = np.zeros(2)  # total-return EWMA accumulators
    wp = 0.0
    eye = np.eye(k)

    # Below this many observations the K betas are not identified and the solve
    # returns noise; skip it (and the residuals it would poison). Far below
    # min_history, so it never touches an emitted value.
    warmup = 2 * k

    out: list[float | None] = []
    fitted = np.full((t, 2), np.nan)
    resid = np.full((t, 2), np.nan)
    beta = np.zeros((k, 2))
    omega = np.zeros((k, k))
    corr = np.eye(k)
    v = np.zeros((2, 2))
    for i in range(t):
        fi = f[i]
        ri = np.array([ra[i], rb[i]])
        gram = thb * gram + np.outer(fi, fi)
        cross = thb * cross + np.outer(fi, ri)
        sv = thv * sv + fi * fi
        wv = thv * wv + 1.0
        sc = thc * sc + np.outer(fi, fi)
        wc = thc * wc + 1.0

        if i >= warmup:
            beta = np.linalg.solve(gram + params.ridge * eye, cross)  # K×2
            fit_i = fi @ beta
            e = ri - fit_i
            fitted[i] = fit_i
            resid[i] = e
            pvar = thp * pvar + e * e
            tvar = thp * tvar + ri * ri
            wp = thp * wp + 1.0

        if i + 1 < params.min_history or wp <= 0:
            out.append(None)
            continue

        d = np.sqrt(np.maximum(sv / wv, 0.0))
        dg = np.sqrt(np.maximum(np.diag(sc), 1e-300))
        corr = sc / np.outer(dg, dg)
        np.fill_diagonal(corr, 1.0)
        omega = (d[:, None] * corr) * d[None, :]
        v = beta.T @ omega @ beta + np.diag(pvar / wp)
        den = math.sqrt(max(v[0, 0], 0.0) * max(v[1, 1], 0.0))
        out.append(float(np.clip(v[0, 1] / den, -1.0, 1.0)) if den > 0 else None)

    wp = max(wp, 1e-300)
    return PairPass(
        dates=[],
        model=out,
        b_a=beta[:, 0].copy(),
        b_b=beta[:, 1].copy(),
        omega=omega,
        corr_omega=corr,
        psi=(float(pvar[0] / wp), float(pvar[1] / wp)),
        var_total=(float(tvar[0] / wp), float(tvar[1] / wp)),
        fitted=fitted,
        resid=resid,
        v=v,
    )


def rolling_correlation(ra: np.ndarray, rb: np.ndarray, window: int) -> np.ndarray:
    """Plain trailing-window sample correlation, NaN until the window is full."""
    a = pd.Series(ra)
    b = pd.Series(rb)
    return a.rolling(window).corr(b).to_numpy()


# ── the API payloads ─────────────────────────────────────────────────────────
_RESID_POINTS = 250  # days shown in the residual scatter


def pair_report(
    a: str,
    b: str,
    *,
    eur: bool = True,
    end: str | None = None,
    max_days: int | None = None,  # a pair is cheap — plot its whole overlap
    params: Params = DEFAULT_PARAMS,
) -> dict[str, Any]:
    """Everything the pair inspector shows: exposures, the shared-factor
    decomposition, the model-vs-realized series, and the internals panels."""
    f_df = _clip(factor_returns(eur=eur), end, max_days)
    sa, sb = daily_returns(a, eur=eur), daily_returns(b, eur=eur)
    if sa is None:
        return {"error": f"no stored price history for {a}"}
    if sb is None:
        return {"error": f"no stored price history for {b}"}
    df = pd.DataFrame({"a": sa, "b": sb}).reindex(f_df.index).dropna()
    if len(df) < params.min_history:
        return {
            "error": (
                f"{a} and {b} overlap on only {len(df)} trading days — "
                f"{params.min_history} are needed before the model says anything"
            )
        }
    f = f_df.loc[df.index].to_numpy("float64")
    ra = df["a"].to_numpy("float64")
    rb = df["b"].to_numpy("float64")

    p = pair_pass(f, ra, rb, params)
    realized = rolling_correlation(ra, rb, params.real_window)
    dates = [str(d.date()) for d in df.index]
    series = [
        {
            "date": dates[i],
            "model": (None if p.model[i] is None else round(p.model[i], 4)),
            "realized": (None if not np.isfinite(realized[i]) else round(float(realized[i]), 4)),
        }
        for i in range(len(dates))
        if p.model[i] is not None
    ]

    factors = factor_names()
    shared = _contributions(factors, p.b_a, p.b_b, p.omega)
    d_a, d_b = math.sqrt(max(p.v[0, 0], 0.0)), math.sqrt(max(p.v[1, 1], 0.0))
    model_corr = float(np.clip(p.v[0, 1] / (d_a * d_b), -1, 1)) if d_a * d_b > 0 else None

    def exposures(beta: np.ndarray) -> list[dict[str, Any]]:
        rows = [{"factor": f, "beta": round(float(beta[k]), 4)} for k, f in enumerate(factors)]
        rows.sort(key=lambda d: -abs(d["beta"]))
        return rows

    def internals(i: int, ticker: str) -> dict[str, Any]:
        var_i = float(p.v[i, i])
        psi_i = p.psi[i]
        parts = p.b_a if i == 0 else p.b_b
        shares = (parts**2) * np.diag(p.omega)
        total = float(shares.sum() + psi_i)
        split = [
            {"factor": f, "share": round(float(shares[k] / total), 4)}
            for k, f in enumerate(factors)
        ] + [{"factor": "idiosyncratic", "share": round(psi_i / total, 4)}]
        split.sort(key=lambda d: (d["factor"] == "idiosyncratic", -d["share"]))
        ok = np.isfinite(p.resid[:, i])
        idx = np.flatnonzero(ok)[-_RESID_POINTS:]
        r2 = 1.0 - psi_i / p.var_total[i] if p.var_total[i] > 0 else None
        return {
            "ticker": ticker,
            "r2": (round(float(r2), 4) if r2 is not None and np.isfinite(r2) else None),
            "vol_annual": round(math.sqrt(max(var_i, 0.0) * 252) * 100, 2),
            "variance_split": split,
            "residual_points": [
                {"fitted": round(float(p.fitted[j, i]), 6), "residual": round(float(p.resid[j, i]), 6)}
                for j in idx
            ],
        }

    return {
        "a": a,
        "b": b,
        "params": params.as_dict(),
        "days": len(dates),
        "start": dates[0],
        "end": dates[-1],
        "exposures": {a: exposures(p.b_a), b: exposures(p.b_b)},
        "shared_factors": shared,
        "model_correlation": (round(model_corr, 4) if model_corr is not None else None),
        "realized_correlation": (
            round(float(realized[-1]), 4) if np.isfinite(realized[-1]) else None
        ),
        "covariance": float(p.v[0, 1]),
        "series": series,
        "internals": {
            a: internals(0, a),
            b: internals(1, b),
            "omega": {"factors": factors, "matrix": [[round(float(x), 4) for x in row] for row in p.corr_omega]},
            "factor_vol": [
                round(float(math.sqrt(max(p.omega[k, k], 0.0) * 252) * 100), 2)
                for k in range(len(factors))
            ],
            "waterfall": [
                *[{"factor": r["factor"], "contribution": r["contribution"]} for r in shared],
                {"factor": "idiosyncratic", "contribution": 0.0},
            ],
            "total": float(p.v[0, 1]),
        },
    }


def overview(
    tickers: Iterable[str],
    *,
    eur: bool = True,
    end: str | None = None,
    max_days: int | None = MAX_DAYS,
    params: Params = DEFAULT_PARAMS,
    max_pairs: int | None = None,
    progress: Any = None,
) -> dict[str, Any]:
    """Whole-universe diagnostics: every pair's model-implied vs realized
    correlation, how tightly they agree, and whether V is invertible."""
    model = fit(tickers, eur=eur, end=end, max_days=max_days, params=params, progress=progress)
    n = len(model.names)
    if n < 2:
        return {"error": "need at least 2 instruments with enough history", "pairs": []}
    if progress:
        progress(0.9, "comparing to realized")
    mc = model.correlation()
    rc = model.realized_correlation()
    iu, ju = np.triu_indices(n, k=1)
    m, r = mc[iu, ju], rc[iu, ju]
    ok = np.isfinite(m) & np.isfinite(r)
    m, r, iu, ju = m[ok], r[ok], iu[ok], ju[ok]

    agreement = float(np.corrcoef(m, r)[0, 1]) if len(m) > 2 and m.std() and r.std() else None
    mae = float(np.abs(m - r).mean()) if len(m) else None
    eig = float(np.linalg.eigvalsh(model.v).min()) if n else None

    keep = np.arange(len(m))
    if max_pairs and len(m) > max_pairs:  # thin the scatter, keep the statistics
        keep = np.linspace(0, len(m) - 1, max_pairs).astype(int)
    names = model.names
    r2 = model.r2
    return {
        "pairs": [
            {
                "a": names[iu[i]],
                "b": names[ju[i]],
                "model": round(float(m[i]), 4),
                "realized": round(float(r[i]), 4),
            }
            for i in keep
        ],
        "agreement": (round(agreement, 4) if agreement is not None else None),
        "min_eigenvalue": eig,
        "mean_abs_error": (round(mae, 4) if mae is not None else None),
        "n_pairs": len(m),
        "n_instruments": n,
        "days": len(model.dates),
        "start": model.dates[0] if model.dates else None,
        "end": model.dates[-1] if model.dates else None,
        "factors": model.factors,
        "params": params.as_dict(),
        "median_r2": (round(float(np.nanmedian(r2)), 4) if n else None),
        "corr_omega": [[round(float(x), 4) for x in row] for row in model.corr_omega],
        "factor_vol": [
            round(float(math.sqrt(max(model.omega[k, k], 0.0) * 252) * 100), 2)
            for k in range(len(model.factors))
        ],
    }
