"""The alpha-signal library: registry hygiene + IC harness correctness on a
synthetic context where the answer is known by construction."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from etoro_yfinance import signals


def _ctx(n_days: int = 800, n_names: int = 250, seed: int = 7) -> signals.Ctx:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-01", periods=n_days, freq="D")
    # random walks with per-name drift so cross-sections have structure
    drift = rng.normal(0.0005, 0.001, n_names)
    rets = rng.normal(0, 0.01, (n_days, n_names)) + drift
    A = 100 * np.cumprod(1 + rets, axis=0)
    R = np.full_like(A, np.nan)
    R[1:] = A[1:] / A[:-1] - 1
    return signals.Ctx(
        idx=idx,
        names=[f"T{i}" for i in range(n_names)],
        A=A,
        R=R,
        H=A * 1.01,
        L=A * 0.99,
        T=np.abs(rng.normal(1e6, 1e5, (n_days, n_names))),
        fresh=np.ones((n_days, n_names), dtype=bool),
        sec=pd.Series(rng.choice(["A", "B", "C"], n_names)),
        spreads=np.full(n_names, 0.2),
        # first 60% stocks, then ETF, then crypto — all big enough to be scored
        itype=np.array(
            ["Stocks"] * (n_names * 6 // 10)
            + ["ETF"] * (n_names * 2 // 10)
            + ["Crypto"] * (n_names - n_names * 6 // 10 - n_names * 2 // 10),
            dtype=object,
        ),
    )


def test_registry_is_well_formed() -> None:
    names = [s.name for s in signals.SIGNALS]
    assert len(names) == len(set(names)), "duplicate signal names"
    assert len(names) >= 20
    assert all(s.sign in (-1, 1) for s in signals.SIGNALS)
    assert all(s.description for s in signals.SIGNALS)
    # every signal carries a real explanation, meaningfully longer than the hypothesis
    assert all(len(s.explanation) > 100 for s in signals.SIGNALS)
    assert len({s.family for s in signals.SIGNALS}) >= 5


def test_all_signals_compute_on_synthetic_context() -> None:
    ctx = _ctx()
    p = 700
    for s in signals.SIGNALS:
        v = s.fn(ctx, p)
        assert v.shape == (len(ctx.names),), s.name
        assert np.isfinite(v).mean() > 0.9, f"{s.name} mostly NaN"


def test_ic_harness_scores_a_perfect_signal_as_one() -> None:
    ctx = _ctx()
    # a signal that IS the next-month return must have IC ~ +1; its negation ~ -1
    def oracle(c: signals.Ctx, p: int) -> np.ndarray:
        nxt = c.idx[p] + pd.offsets.MonthBegin(1)  # the harness's next cutoff
        pn = min(int(c.idx.searchsorted(nxt, "right")) - 1, len(c.idx) - 1)
        return c.A[pn] / c.A[p] - 1

    saved = signals.SIGNALS[:]
    try:
        signals.SIGNALS[:] = [
            signals.Signal("oracle", "test", +1, "cheats", oracle),
            signals.Signal("anti", "test", -1, "cheats inverted", lambda c, p: -oracle(c, p)),
        ]
        board = signals.evaluate(ctx, "2021-01-01", "2022-02-01")
        by = board.set_index("signal")
        assert by.loc["oracle", "mean_ic"] > 0.95
        assert by.loc["anti", "mean_ic"] < -0.95
        assert bool(by.loc["oracle", "sign_ok"]) and bool(by.loc["anti", "sign_ok"])
        # the full battery: a perfect signal must clear every gate
        for name in ("oracle", "anti"):
            assert by.loc[name, "p_boot"] < 0.01
            assert by.loc[name, "spread_net_ann"] > 0
            assert by.loc[name, "mono"] > 0.9
            assert by.loc[name, "scope"] == "all"  # a perfect signal works in every type
            assert bool(by.loc[name, "admitted"])
        # regime columns exist and the dominant regime (most months) is populated
        assert {"ic_bull", "ic_bear", "ic_calm", "ic_turb"} <= set(board.columns)
        assert by.loc["oracle", "ic_bull"] is not None or by.loc["oracle", "ic_bear"] is not None
        combo = signals.combo_ic(ctx, "2021-01-01", "2022-02-01")
        assert combo["mean_ic"] > 0.95  # both members point the same way once signed
    finally:
        signals.SIGNALS[:] = saved


def test_random_signal_scores_near_zero_and_is_rejected() -> None:
    ctx = _ctx()
    rng = np.random.default_rng(0)
    saved = signals.SIGNALS[:]
    try:
        signals.SIGNALS[:] = [
            signals.Signal("noise", "test", +1, "no alpha", lambda c, p: rng.normal(size=len(c.names)))
        ]
        board = signals.evaluate(ctx, "2021-01-01", "2022-02-01")
        assert abs(float(board.iloc[0]["mean_ic"])) < 0.05
        assert not bool(board.iloc[0]["admitted"])  # the battery must reject noise
    finally:
        signals.SIGNALS[:] = saved


def _oracle_signals() -> list[signals.Signal]:
    def oracle(c: signals.Ctx, p: int) -> np.ndarray:
        nxt = c.idx[p] + pd.offsets.MonthBegin(1)
        pn = min(int(c.idx.searchsorted(nxt, "right")) - 1, len(c.idx) - 1)
        return c.A[pn] / c.A[p] - 1

    return [signals.Signal("oracle", "test", +1, "cheats", oracle)]


def test_placebo_run_admits_nothing() -> None:
    # even a perfect look-ahead signal must die when the future is shuffled —
    # if it doesn't, the harness itself leaks.
    ctx = _ctx()
    saved = signals.SIGNALS[:]
    try:
        signals.SIGNALS[:] = _oracle_signals()
        board = signals.evaluate(ctx, "2021-01-01", "2022-02-01", placebo=True)
        assert not board["admitted"].fillna(False).any()
    finally:
        signals.SIGNALS[:] = saved


def test_advisory_columns_and_detail_series() -> None:
    ctx = _ctx()
    saved = signals.SIGNALS[:]
    try:
        signals.SIGNALS[:] = _oracle_signals()
        board, detail = signals.evaluate(ctx, "2021-01-01", "2022-02-01", with_detail=True)
        row = board.iloc[0]
        for col in ("ic_marginal", "ic_lag2", "ic_liquid", "ic_trend", "spread_net_2x",
                    "spread_net_3x", "beta_corr", "flags", "timing_dup"):
            assert col in board.columns, col
        # the lag probe exposes the oracle: its foresight is tied to exact
        # timing, so a 2-day-stale copy loses it — flagged as lag-fragile
        assert row["ic_lag2"] < 0.5
        assert "lag-fragile" in row["flags"]
        # with no other admitted signals, marginal IC ≈ the plain IC
        assert row["ic_marginal"] > 0.9
        s = detail["signals"]["oracle"]
        assert len(s["dates"]) == len(s["ic"]) == len(s["gross"]) == len(s["cost"]) == row["months"]
        assert len(s["dec"]) == 10
    finally:
        signals.SIGNALS[:] = saved
