"""End-to-end tests for the monthly momentum backtest on a synthetic store.

Five tickers in two sectors with distinct drifts are written to a tmp Parquet
store (one listed too recently to clear the 2-year eligibility gate); the run
must produce a coherent daily equity curve, pay spread costs on turnover,
consider only seasoned assets, and report the survivorship/costs caveats.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

from etoro_yfinance import backtest

_TICKERS = {  # ticker -> (sector, daily growth, history start)
    "TECH1": ("Technology", 0.0020, "2018-06-01"),
    "TECH2": ("Technology", 0.0015, "2018-06-01"),
    "FIN1": ("Financial", 0.0005, "2018-06-01"),
    "FIN2": ("Financial", 0.0002, "2018-06-01"),
    # Hottest growth but listed 2019-12 → never has 2y of history within the
    # backtest window, so the eligibility gate must keep it out of every basket.
    "YOUNG": ("Technology", 0.0030, "2019-12-01"),
}


def _write_store(root: Path) -> None:
    (root / "prices_eur").mkdir(parents=True)
    (root / "prices").mkdir(parents=True)
    for t, (_, g, start) in _TICKERS.items():
        idx = pd.date_range(start, "2021-07-01", freq="D")
        n = np.arange(len(idx))
        # A deterministic ripple keeps daily volatility non-zero so the
        # vol-adjusted signal is defined and nothing is excluded from scoring.
        px = 100.0 * (1.0 + g) ** n * (1.0 + 0.002 * np.sin(n / 3.0))
        eur = pd.DataFrame(
            {
                "date": idx,
                "adj_close": px.astype("float32"),
                "close": px.astype("float32"),
                "volume": (px * 1000).astype("float32"),
            }
        )
        eur.to_parquet(root / "prices_eur" / f"{t}.parquet", index=False)
        nat = pd.DataFrame(
            {
                "date": idx,
                "close": px.astype("float32"),
                "volume": np.full(len(idx), 1000, dtype="int64"),
            }
        )
        nat.to_parquet(root / "prices" / f"{t}.parquet", index=False)


def _rows(spread: float | None) -> list[dict[str, Any]]:
    return [{"yf": t, "sector": sec, "spread_pct": spread} for t, (sec, _, _) in _TICKERS.items()]


@pytest.fixture
def store(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    _write_store(tmp_path)
    return tmp_path


def _run(spread: float | None, **kw: Any) -> dict[str, Any]:
    return backtest.run(
        _rows(spread),
        start="2021-01-01",
        end="2021-06-01",
        top_n_sectors=2,
        top_n_per_sector=2,
        **kw,
    )


def test_run_produces_coherent_daily_curves(store: Path) -> None:
    seen: list[float] = []
    res = _run(0.0, progress=lambda frac, label: seen.append(frac))
    assert "error" not in res
    assert len(res["dates"]) == len(res["equity"]) == len(res["benchmark"])
    assert res["equity"][0] == pytest.approx(1.0)  # zero spread → no entry cost
    assert res["universe_size"] == 5
    assert res["periods"] == 5  # Jan..Jun = 5 monthly steps
    assert all(v > 0 for v in res["equity"])
    assert res["stats"]["max_drawdown"] <= 0
    assert res["benchmark_stats"]["total_return"] > 0  # all series drift upward
    assert seen == sorted(seen)  # progress is called and never goes backwards
    assert 0.0 <= seen[-1] <= 1.0
    assert res["notes"]  # survivorship/cost caveats


def test_spread_costs_reduce_equity(store: Path) -> None:
    gross = _run(0.0)
    net = _run(1.0)  # 1% full spread everywhere
    assert gross["cost_drag"] == 0.0
    # Everything enters at the first rebalance: half of the 1% spread.
    assert net["cost_drag"] == pytest.approx(0.005, rel=0.2)
    assert net["equity"][-1] < gross["equity"][-1]
    # The benchmark stays gross — identical either way.
    assert net["benchmark"][-1] == pytest.approx(gross["benchmark"][-1])


def test_unknown_spreads_fall_back_to_median(store: Path) -> None:
    rows = _rows(1.0)
    rows[0]["spread_pct"] = None  # one unknown name
    res = backtest.run(
        rows, start="2021-01-01", end="2021-06-01", top_n_sectors=2, top_n_per_sector=2
    )
    assert res["spread_known"] == 4
    assert res["default_spread_pct"] == 1.0  # median of the known ones
    assert res["cost_drag"] > 0


def test_young_asset_is_not_considered_until_it_has_two_years(store: Path) -> None:
    # YOUNG has the strongest momentum in the top sector, but its history starts
    # 2019-12 — under 2 years at every cutoff in the window. Without the
    # eligibility gate it would headline the Technology picks.
    res = _run(0.0)
    assert "error" not in res
    picked = {h["ticker"] for h in res["last_holdings"]}
    assert "YOUNG" not in picked
    assert {"TECH1", "TECH2"} <= picked  # the seasoned tech names fill the sector


def test_portfolios_record_every_period(store: Path) -> None:
    res = _run(1.0)
    ps = res["portfolios"]
    assert len(ps) == res["periods"]
    assert [p["date"] for p in ps] == sorted(p["date"] for p in ps)
    # Compounding the net per-period returns reproduces the final equity.
    eq = 1.0
    for p in ps:
        eq *= 1.0 + p["return_pct"] / 100.0
    assert eq == pytest.approx(res["equity"][-1], rel=1e-3)
    # Each record carries its basket; the young listing is never in any of them.
    for p in ps:
        assert p["n"] == len(p["holdings"]) > 0
        assert p["sortino"] is None or isinstance(p["sortino"], float)
        assert "YOUNG" not in {h["ticker"] for h in p["holdings"]}
    assert [h["ticker"] for h in ps[-1]["holdings"]] == [h["ticker"] for h in res["last_holdings"]]


def test_run_rejects_empty_or_too_short(store: Path) -> None:
    assert "error" in backtest.run([], start="2021-01-01", end="2021-06-01")
    # A window with fewer than two month-starts can't rebalance even once.
    assert "error" in backtest.run(_rows(0.0), start="2021-01-02", end="2021-01-15")


def test_sortino_ratio_known_values() -> None:
    # mean = 0.02/3; downside dev = sqrt(mean([0,0,0.01^2])) = 0.01/sqrt(3)
    rets = np.array([0.01, 0.02, -0.01])
    expected = (0.02 / 3) / (0.01 / np.sqrt(3))
    assert backtest.sortino_ratio(rets) == pytest.approx(expected)
    assert backtest.sortino_ratio(np.array([0.01, 0.02])) == float("inf")  # flawless month
    assert backtest.sortino_ratio(np.array([0.0, 0.0])) == 0.0
    assert backtest.sortino_ratio(np.array([])) == 0.0
    assert backtest.sortino_ratio(np.array([np.nan, 0.01, -0.01])) == pytest.approx(0.0)


def test_sortino_strategy_picks_best_risk_adjusted_names(store: Path) -> None:
    res = backtest.run(
        _rows(1.0), start="2021-01-01", end="2021-06-01", strategy="sortino", top_n=2
    )
    assert "error" not in res
    assert res["params"]["strategy"] == "sortino"
    picked = {h["ticker"] for h in res["last_holdings"]}
    # Same ripple everywhere → ranking follows drift; YOUNG (strongest drift)
    # is still blocked by the 2-year eligibility gate.
    assert picked == {"TECH1", "TECH2"}
    assert "YOUNG" not in picked
    assert all(h["score"] is None or h["score"] > 0 for h in res["last_holdings"])
    assert res["cost_drag"] > 0  # spread costs apply to this strategy too
    assert res["avg_holdings"] == 2


def test_sortino_survives_zero_price_glitches(store: Path) -> None:
    # Real Yahoo data contains zero closes (glitches / float32 underflow on
    # micro-priced coins). With pytest's warnings-as-errors, any divide-by-zero
    # RuntimeWarning in the picker fails this test.
    idx = pd.date_range("2018-06-01", "2021-07-01", freq="D")
    px = np.full(len(idx), 50.0, dtype="float64")
    px[-30:-10] = 0.0  # zero prints inside the final 1-month lookback
    glitch = pd.DataFrame(
        {
            "date": idx,
            "adj_close": px.astype("float32"),
            "close": px.astype("float32"),
            "volume": np.full(len(idx), 1000.0, dtype="float32"),
        }
    )
    glitch.to_parquet(store / "prices_eur" / "GLITCH.parquet", index=False)
    nat = pd.DataFrame(
        {
            "date": idx,
            "close": px.astype("float32"),
            "volume": np.full(len(idx), 1000, dtype="int64"),
        }
    )
    nat.to_parquet(store / "prices" / "GLITCH.parquet", index=False)

    rows = [*_rows(1.0), {"yf": "GLITCH", "sector": "Technology", "spread_pct": 1.0}]
    res = backtest.run(rows, start="2021-01-01", end="2021-06-01", strategy="sortino", top_n=2)
    assert "error" not in res
    picked = {h["ticker"] for h in res["last_holdings"]}
    assert "GLITCH" not in picked  # too few usable closes in its window


def test_unknown_strategy_errors(store: Path) -> None:
    res = backtest.run(_rows(0.0), start="2021-01-01", end="2021-06-01", strategy="sharpe")
    assert "unknown strategy" in res["error"]
    res = backtest.run(_rows(0.0), start="2021-01-01", end="2021-06-01", rebalance="weekly")
    assert "unknown rebalance" in res["error"]


def test_quarterly_rebalance(store: Path) -> None:
    res = backtest.run(
        _rows(1.0),
        start="2021-01-01",
        end="2021-07-01",
        rebalance="quarterly",
        top_n_sectors=2,
        top_n_per_sector=2,
    )
    assert "error" not in res
    assert res["params"]["rebalance"] == "quarterly"
    assert res["periods"] == 2  # Jan→Apr, Apr→Jul
    # Same picks held both quarters → only the initial half-spread is paid.
    assert res["cost_drag"] == pytest.approx(0.005, rel=0.2)
    # Jan..Jul monthly on the same window pays no more (same stable basket),
    # but the equity axes must both span the window daily.
    monthly = backtest.run(
        _rows(1.0),
        start="2021-01-01",
        end="2021-07-01",
        top_n_sectors=2,
        top_n_per_sector=2,
    )
    assert len(res["dates"]) == len(monthly["dates"])


def test_max_dd_from_daily_curve() -> None:
    assert backtest._max_dd([1.0, 1.2, 0.6, 0.9]) == pytest.approx(-0.5)
    assert backtest._max_dd([1.0]) == 0.0
    assert backtest._stats([1.0, 1.1, 1.21], 2 / 12)["total_return"] == pytest.approx(0.21)


def test_yearly_returns_compound_to_total(store: Path) -> None:
    res = _run(0.0)
    ys = res["yearly"]
    assert ys and all(y["portfolios"] for y in ys)
    # every portfolio lands in its start-date's year
    for y in ys:
        assert all(p["date"][:4] == y["year"] for p in y["portfolios"])
    assert sum(len(y["portfolios"]) for y in ys) == len(res["portfolios"])
    # yearly returns compound back to the full-period totals (both curves)
    for key, curve in (("return_pct", "equity"), ("benchmark_return_pct", "benchmark")):
        total = 1.0
        for y in ys:
            total *= 1 + y[key] / 100
        assert total - 1 == pytest.approx(res[curve][-1] - 1, abs=0.02)


def test_stability_criteria_reported(store: Path) -> None:
    res = _run(0.0)
    cs = res["criteria"]
    assert len(cs) == 5
    assert all({"label", "value", "ok"} <= set(c) for c in cs)
    # 5-month run: no full calendar year and no 5y window → undecidable (None),
    # the CAGR/Sharpe/DD checks are decidable booleans.
    assert [c["ok"] for c in cs[-2:]] == [None, None]
    assert all(isinstance(c["ok"], bool) for c in cs[:3])


def test_trend_filter_moves_downtrending_pick_to_cash(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    (tmp_path / "prices_eur").mkdir(parents=True)
    (tmp_path / "prices").mkdir(parents=True)
    idx = pd.date_range("2018-06-01", "2021-07-01", freq="D")
    n = np.arange(len(idx))
    for t, g in (("UP", 0.001), ("DOWN", -0.001)):
        px = 100.0 * (1.0 + g) ** n * (1.0 + 0.002 * np.sin(n / 3.0))
        pd.DataFrame(
            {
                "date": idx,
                "adj_close": px.astype("float32"),
                "close": px.astype("float32"),
                "volume": (px * 1000).astype("float32"),
            }
        ).to_parquet(tmp_path / "prices_eur" / f"{t}.parquet", index=False)
        pd.DataFrame(
            {"date": idx, "close": px.astype("float32"), "volume": np.full(len(idx), 1000)}
        ).to_parquet(tmp_path / "prices" / f"{t}.parquet", index=False)
    rows = [{"yf": t, "sector": "Tech", "spread_pct": 0.0} for t in ("UP", "DOWN")]
    kw: dict[str, Any] = {"start": "2021-01-01", "end": "2021-06-01", "strategy": "sortino"}
    base = backtest.run(rows, **kw)
    filt = backtest.run(rows, trend_filter=True, **kw)
    # DOWN is picked (top_n covers everything) but trades below its 200d mean →
    # its slice sits in cash; skipping the loser must beat holding it.
    assert all(p["trend_dropped"] == 1 for p in filt["portfolios"])
    assert all(p["trend_dropped"] == 0 for p in base["portfolios"])
    assert filt["equity"][-1] > base["equity"][-1]


def test_vol_target_scales_exposure_down(store: Path) -> None:
    base = _run(0.0)
    low = _run(0.0, vol_target=0.3)  # target ≪ the fixture's ~0.7% vol → must de-risk
    assert all(p["exposure"] == 1.0 for p in base["portfolios"])
    assert all(p["exposure"] <= 1.0 for p in low["portfolios"])
    # after the 63-day warmup the book scales down into cash
    assert any(p["exposure"] < 1.0 for p in low["portfolios"])
    # over the de-risked stretch the daily curve must be visibly calmer
    def _tail_vol(res: dict[str, Any]) -> float:
        eq = np.array(res["equity"][-40:])
        r = np.diff(eq) / eq[:-1]
        return float(r.std())

    assert _tail_vol(low) < _tail_vol(base)
