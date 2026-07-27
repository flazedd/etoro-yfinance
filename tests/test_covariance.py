"""Tests for the factor covariance model — V = BΩBᵀ + Ψ.

Everything runs against a synthetic tmp store (MOMENTUM_DATA_DIR) whose
instruments are *built* from known factor exposures plus known idiosyncratic
noise. That makes the model correctly specified by construction, so the tests
can assert what it must recover (the exposures, the pairwise correlations) as
well as the invariants that must hold whatever the data (causality, the
decompositions summing to their totals, V staying invertible).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

from etoro_yfinance import covariance as cov

# name -> synthetic proxy ticker. Kept distinct from the real FACTORS values so
# a stray real parquet can never satisfy a test.
_FACTORS = {
    "market": "F_MKT",
    "rates": "F_RATES",
    "sector": "F_SECT",
}
# instrument -> (exposures in _FACTORS order, idiosyncratic vol per day)
_INSTRUMENTS: dict[str, tuple[list[float], float]] = {
    "PURE": ([1.0, 0.0, 0.0], 0.0020),  # market only
    "TWIN": ([0.9, 0.0, 0.0], 0.0020),  # nearly the same thing
    "SECT1": ([0.6, 0.0, 1.1], 0.0025),  # market + its sector
    "SECT2": ([0.5, 0.0, 1.0], 0.0025),  # ditto — should link via `sector`
    "BOND": ([0.1, 1.2, 0.0], 0.0015),  # rates driven
    "NOISE": ([0.0, 0.0, 0.0], 0.0120),  # no factor structure at all
}
_DAYS = 1500
_FACTOR_VOL = {"market": 0.009, "rates": 0.004, "sector": 0.011}


def _write_series(root: Path, ticker: str, dates: pd.DatetimeIndex, rets: np.ndarray) -> None:
    px = 100.0 * np.cumprod(1.0 + rets)
    frame = pd.DataFrame(
        {
            "date": dates,
            "adj_close": px.astype("float32"),
            "close": px.astype("float32"),
            "volume": np.full(len(dates), 1000, dtype="int64"),
        }
    )
    for sub in ("prices", "prices_eur"):
        d = root / sub
        d.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(d / f"{ticker}.parquet", index=False)


def _build_store(root: Path, seed: int = 7) -> dict[str, np.ndarray]:
    """Write the synthetic factors and the instruments generated from them.
    Returns the factor return matrix keyed by factor name."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2016-01-04", periods=_DAYS)
    f = {name: rng.normal(0.0, _FACTOR_VOL[name], _DAYS) for name in _FACTORS}
    for name, ticker in _FACTORS.items():
        _write_series(root, ticker, dates, f[name])
    fm = np.column_stack([f[name] for name in _FACTORS])
    for ticker, (betas, idio) in _INSTRUMENTS.items():
        r = fm @ np.array(betas) + rng.normal(0.0, idio, _DAYS)
        _write_series(root, ticker, dates, r)
    return f


@pytest.fixture
def store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, np.ndarray]:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(cov, "FACTORS", dict(_FACTORS))
    monkeypatch.setattr(cov, "_FACTOR_CACHE", {})
    return _build_store(tmp_path)


_ALL = list(_INSTRUMENTS)


# ── the EWMA convention every estimator shares ───────────────────────────────
def test_ewma_weights_put_weight_one_on_today() -> None:
    w = cov.ewma_weights(5, halflife=2)
    assert w[-1] == pytest.approx(1.0)
    assert w[-3] == pytest.approx(0.5)  # one half-life back (2 days) → ½
    assert w[0] == pytest.approx(2.0 ** (-4 / 2))


# ── the fit recovers what generated the data ─────────────────────────────────
def test_exposures_recover_the_generating_betas(store: dict[str, np.ndarray]) -> None:
    model = cov.fit(_ALL)
    assert model.names == _ALL
    assert model.factors == list(_FACTORS)
    for i, ticker in enumerate(model.names):
        want = np.array(_INSTRUMENTS[ticker][0])
        assert model.b[i] == pytest.approx(want, abs=0.08), ticker


def test_r2_is_high_for_factor_driven_and_low_for_noise(store: dict[str, np.ndarray]) -> None:
    model = cov.fit(_ALL)
    r2 = dict(zip(model.names, model.r2, strict=True))
    assert r2["PURE"] > 0.8  # built almost entirely from the market factor
    assert r2["SECT1"] > 0.8
    assert r2["NOISE"] < 0.2  # nothing but its own noise


def test_model_correlations_match_the_realized_ones(store: dict[str, np.ndarray]) -> None:
    """The generating process IS a factor model, so implied and realized
    correlation must agree across pairs — the page's headline check."""
    res = cov.overview(_ALL)
    assert res["n_instruments"] == len(_ALL)
    assert res["n_pairs"] == len(_ALL) * (len(_ALL) - 1) // 2
    assert res["agreement"] > 0.9
    assert res["mean_abs_error"] < 0.15


def test_v_stays_invertible(store: dict[str, np.ndarray]) -> None:
    """Acceptance check 5: Ψ > 0 on the diagonal keeps V positive-definite."""
    res = cov.overview(_ALL)
    assert res["min_eigenvalue"] > 0


# ── the causal guarantee ─────────────────────────────────────────────────────
def test_model_line_never_uses_future_data(store: dict[str, np.ndarray]) -> None:
    """Acceptance check 4: truncating the price history to end at day t must not
    change the model value plotted at any day ≤ t."""
    full = cov.pair_report("SECT1", "SECT2")
    cut = full["series"][len(full["series"]) // 2]["date"]
    trunc = cov.pair_report("SECT1", "SECT2", end=cut)
    seen = {s["date"]: s["model"] for s in full["series"]}
    overlap = [s for s in trunc["series"] if s["date"] in seen]
    assert len(overlap) > 100
    for s in overlap:
        assert s["model"] == seen[s["date"]]


def test_series_starts_at_min_history(store: dict[str, np.ndarray]) -> None:
    params = cov.Params(min_history=400)
    res = cov.pair_report("PURE", "TWIN", params=params)
    assert res["days"] - len(res["series"]) == params.min_history - 1


def test_realized_correlation_is_null_until_its_window_is_full() -> None:
    """Acceptance check 3: the realized line has no value before REAL_WINDOW
    days exist (the model line starts later still, at MIN_HISTORY)."""
    rng = np.random.default_rng(1)
    a, b = rng.normal(size=200), rng.normal(size=200)
    roll = cov.rolling_correlation(a, b, window=60)
    assert np.isnan(roll[:59]).all()
    assert np.isfinite(roll[59:]).all()


# ── the decompositions are true decompositions ───────────────────────────────
def test_waterfall_sums_to_the_pair_covariance(store: dict[str, np.ndarray]) -> None:
    """Acceptance check 11: the bars must land on V_ab."""
    res = cov.pair_report("SECT1", "SECT2")
    total = sum(r["contribution"] for r in res["internals"]["waterfall"])
    assert total == pytest.approx(res["covariance"], rel=1e-9)
    shared = sum(r["contribution"] for r in res["shared_factors"])
    assert shared == pytest.approx(res["covariance"], rel=1e-9)
    pct = sum(r["contribution_pct"] for r in res["shared_factors"])
    assert pct == pytest.approx(1.0, rel=1e-6)


def test_variance_split_segments_sum_to_one(store: dict[str, np.ndarray]) -> None:
    """Acceptance check 10, for both the batch model and the pair payload."""
    model = cov.fit(_ALL)
    for i in range(len(model.names)):
        assert sum(s["share"] for s in model.variance_split(i)) == pytest.approx(1.0)
    res = cov.pair_report("SECT1", "BOND")
    for t in ("SECT1", "BOND"):
        shares = [s["share"] for s in res["internals"][t]["variance_split"]]
        assert sum(shares) == pytest.approx(1.0, abs=1e-3)
        assert min(shares) >= 0.0


def test_reconstructed_variance_matches_the_sample(store: dict[str, np.ndarray]) -> None:
    """Acceptance check 7: V_ii from B Ω Bᵀ + Ψ must match the instrument's own
    variance, measured on the same EWMA clock."""
    model = cov.fit(_ALL)
    w = cov.ewma_weights(model.r.shape[0], model.params.h_psi)[:, None] * model.mask
    sample = (w * model.r * model.r).sum(axis=0) / w.sum(axis=0)
    assert np.diag(model.v) == pytest.approx(sample, rel=0.25)


# ── the model responds to its knobs and its config ───────────────────────────
def test_shorter_factor_vol_halflife_makes_the_model_line_react_faster(
    store: dict[str, np.ndarray],
) -> None:
    """Acceptance check 6."""

    def wiggle(h: float) -> float:
        res = cov.pair_report("SECT1", "BOND", params=cov.Params(h_omega_v=h))
        line = np.array([s["model"] for s in res["series"]], dtype="float64")
        return float(np.abs(np.diff(line)).mean())

    assert wiggle(10) > 2 * wiggle(250)


def test_adding_a_factor_adds_an_exposure(
    store: dict[str, np.ndarray], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Acceptance check 8: the factor set is config — extend it and every
    exposure is recomputed with a bar for the new factor."""
    before = cov.pair_report("SECT1", "SECT2")
    assert len(before["exposures"]["SECT1"]) == len(_FACTORS)

    monkeypatch.setattr(cov, "FACTORS", {**_FACTORS, "extra": "F_SECT"})
    monkeypatch.setattr(cov, "_FACTOR_CACHE", {})
    after = cov.pair_report("SECT1", "SECT2")
    assert len(after["exposures"]["SECT1"]) == len(_FACTORS) + 1
    assert {e["factor"] for e in after["exposures"]["SECT1"]} == {*_FACTORS, "extra"}


def test_dropping_the_dominant_factor_bends_the_residuals(
    store: dict[str, np.ndarray], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Acceptance check 12: a well-specified fit leaves a shapeless residual
    cloud; remove the factor that drives the instrument and structure appears."""

    def slope(ticker: str) -> float:
        res = cov.pair_report(ticker, "BOND")
        pts = res["internals"][ticker]["residual_points"]
        x = np.array([p["fitted"] for p in pts])
        y = np.array([p["residual"] for p in pts])
        return abs(float(np.polyfit(x, y, 1)[0]))

    intact = slope("SECT1")
    assert intact < 0.15  # correctly specified → no visible tilt

    monkeypatch.setattr(cov, "FACTORS", {"rates": _FACTORS["rates"]})
    monkeypatch.setattr(cov, "_FACTOR_CACHE", {})
    assert slope("SECT1") > 3 * max(intact, 0.02)


def test_missing_factor_proxy_names_the_fix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(cov, "FACTORS", {"nope": "NOT_STORED"})
    monkeypatch.setattr(cov, "_FACTOR_CACHE", {})
    with pytest.raises(cov.MissingFactorError, match="fetch_factors"):
        cov.factor_returns()


# ── the pair payload the page renders ────────────────────────────────────────
def test_related_pair_reads_as_related_and_unrelated_as_unrelated(
    store: dict[str, np.ndarray],
) -> None:
    """Acceptance checks 1 and 2: two names built from the same sector factor
    must correlate through it; a rates-driven name must not."""
    same = cov.pair_report("SECT1", "SECT2")
    assert same["model_correlation"] > 0.7
    assert same["shared_factors"][0]["factor"] == "sector"

    apart = cov.pair_report("BOND", "NOISE")
    assert abs(apart["model_correlation"]) < 0.2


def test_pair_report_reports_unusable_inputs(store: dict[str, np.ndarray]) -> None:
    assert "error" in cov.pair_report("PURE", "NOT_STORED")
    assert "error" in cov.pair_report("PURE", "TWIN", params=cov.Params(min_history=99_000))


def test_exposures_and_series_are_json_safe(store: dict[str, np.ndarray]) -> None:
    """The payload is handed to JSONResponse and to |tojson — no numpy scalars."""
    import json

    res: dict[str, Any] = cov.pair_report("SECT1", "SECT2")
    json.dumps(res)  # raises TypeError on a numpy float
    json.dumps(cov.overview(_ALL))
