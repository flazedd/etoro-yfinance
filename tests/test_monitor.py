"""Unit tests for the regime monitor's compute (build spec §5–§7).

Everything here is store-free: synthetic series exercise the equal-weighted index
build, the per-day MA-crossover labelling, and the filtered/always-in metrics.
Sector plumbing is tested by monkeypatching the universe loader and price store.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from etoro_yfinance import monitor as mon


def _series(start: str, values: list[float]) -> pd.Series:
    idx = pd.bdate_range(start, periods=len(values))
    return pd.Series(values, index=idx, dtype="float64")


# ── equal-weighted blend ──────────────────────────────────────────────────────
def test_equal_weighted_blend_is_zero_on_opposite_moves() -> None:
    # Day 2: A +1%, B -1% → group return 0%.
    a = _series("2020-01-01", [100.0, 101.0])
    b = _series("2020-01-01", [100.0, 99.0])
    gdf = mon.build_group_daily({"A": a, "B": b})
    assert np.isnan(gdf["group_return"].iloc[0])  # seed day
    assert gdf["group_return"].iloc[1] == pytest.approx(0.0, abs=1e-12)


def test_seed_day_is_base_and_null_return() -> None:
    a = _series("2020-01-01", [100.0, 110.0, 121.0])
    gdf = mon.build_group_daily({"A": a})
    assert gdf["index_value"].iloc[0] == mon.INDEX_BASE
    assert np.isnan(gdf["group_return"].iloc[0])
    assert gdf["group_return"].iloc[1] == pytest.approx(0.10)
    assert gdf["index_value"].iloc[1] == pytest.approx(110.0)


def test_member_added_midway_is_excluded_until_it_has_a_return() -> None:
    a = _series("2020-01-01", [100.0, 101.0, 102.0, 103.0])
    b = pd.Series([50.0, 55.0], index=pd.bdate_range("2020-01-03", periods=2))
    gdf = mon.build_group_daily({"A": a, "B": b})
    day3 = gdf.loc[pd.Timestamp("2020-01-03"), "group_return"]
    assert day3 == pytest.approx(102.0 / 101.0 - 1.0)  # only A had a prior bar


# ── labelling: no dwell — the label is the raw MA crossover, per day ──────────
def test_confirmed_labels_default_is_bull_before_ma() -> None:
    assert mon.confirmed_labels([None, None, None]) == ["bull", "bull", "bull"]


def test_label_is_raw_crossover_no_dwell() -> None:
    # The label follows the raw comparison immediately — a single bear day flips.
    assert mon.confirmed_labels(["bull", "bull", "bear", "bull"]) == [
        "bull", "bull", "bear", "bull",
    ]
    # Pre-MA (None) holds the neutral bull default, then tracks the raw label.
    assert mon.confirmed_labels([None, None, "bear", "bull", "bear"]) == [
        "bull", "bull", "bear", "bull", "bear",
    ]


# ── filtered / always-in metrics ──────────────────────────────────────────────
def _gdf(returns: list[float | None], confirmed: list[str]) -> pd.DataFrame:
    idx = pd.bdate_range("2020-01-01", periods=len(returns))
    return pd.DataFrame(
        {"group_return": returns, "confirmed_label": confirmed}, index=idx
    )


def test_filtered_stream_zeros_returns_following_a_bear_label() -> None:
    returns = [0.0, 0.01, -0.02, 0.03]
    confirmed = ["bull", "bull", "bear", "bear"]
    m = mon.group_metrics(_gdf(returns, confirmed))
    filt = np.array([0.0, 0.01, -0.02, 0.0])  # prev-day labels [bull,bull,bull,bear]
    n = len(filt)
    exp = float(np.prod(1.0 + filt)) ** (mon.TRADING_DAYS_YR / n) - 1.0
    assert m["cagr_sma"] == pytest.approx(round(exp, 6))


def test_filtered_metrics_use_previous_day_label() -> None:
    returns = [0.05, -0.03, 0.02, -0.06, 0.04, -0.01]
    labels_a = ["bull", "bull", "bull", "bear", "bear", "bear"]
    labels_b = ["bull", "bull", "bull", "bull", "bear", "bear"]  # shifted one day
    m_a = mon.group_metrics(_gdf(returns, labels_a))
    m_b = mon.group_metrics(_gdf(returns, labels_b))
    assert m_a["cagr_sma"] != m_b["cagr_sma"]
    assert m_a["sharpe_sma"] != m_b["sharpe_sma"]


def test_metric_edge_cases() -> None:
    assert mon._stream_metrics(np.array([0.0, 0.0, 0.0]))["sharpe"] == 0.0
    assert mon._stream_metrics(np.array([0.01, 0.02]))["sortino"] == 0.0
    assert mon._stream_metrics(np.array([-1.0, 0.5]))["cagr"] == -1.0


def test_sharpe_annualization() -> None:
    r = np.array([0.01, -0.005, 0.02, -0.01, 0.015])
    exp = r.mean() / r.std(ddof=1) * math.sqrt(252)
    assert mon._stream_metrics(r)["sharpe"] == pytest.approx(exp)


def test_max_drawdown() -> None:
    # wealth 1 → 1.1 → 0.55 → 0.605; worst peak-to-trough is 0.55/1.1 - 1 = -0.5
    assert mon._max_drawdown(np.array([0.1, -0.5, 0.1])) == pytest.approx(-0.5)
    assert mon._max_drawdown(np.array([0.01, 0.01, 0.01])) == pytest.approx(0.0)  # monotonic up
    m = mon.group_metrics(_gdf([0.0, -0.2, 0.1], ["bull", "bull", "bull"]))
    assert m["maxdd_always"] is not None
    assert m["maxdd_sma"] is not None


def test_vol_exposure_bounded_zero_in_bear_and_de_risks_in_turbulence() -> None:
    # A steadily rising index with a deterministic low-vol ripple, then a violent
    # high-vol crash into a bear trend.
    calm = 100.0 * (1.0008 ** np.arange(320)) * (1.0 + 0.003 * np.sin(np.arange(320) / 4.0))
    down = list(calm[-1] * (0.97 ** np.arange(1, 80)))  # steep, high-vol drop → bear
    gdf = mon.build_group_daily({"A": _series("2015-01-01", list(calm) + down)})
    assert "vol_exposure" in gdf.columns
    exp = gdf["vol_exposure"].to_numpy()
    trend = gdf["confirmed_label"].tolist()
    assert exp.min() >= 0.0
    assert exp.max() <= mon.VOL_CAP + 1e-9
    assert all(exp[i] == 0.0 for i, v in enumerate(trend) if v == "bear")  # bear → cash
    # invested through the calm bull stretch (after the 60d vol warm-up)
    assert float(np.mean(exp[100:300])) > 0.5


def test_vol_and_sma_variants_are_scored() -> None:
    up = list(100.0 * (1.001 ** np.arange(300)))
    down = list(up[-1] * (0.985 ** np.arange(1, 60)))
    gdf = mon.build_group_daily({"A": _series("2016-01-01", up + down)})
    m = mon.group_metrics(gdf)
    for fam in ("cagr", "sharpe", "sortino", "maxdd"):
        assert m[f"{fam}_sma"] is not None
        assert m[f"{fam}_vol"] is not None


def test_group_metrics_without_vol_exposure_yields_none() -> None:
    m = mon.group_metrics(_gdf([0.0, 0.01, -0.02], ["bull", "bull", "bear"]))
    assert m["sharpe_sma"] is not None
    assert m["sharpe_vol"] is None  # no vol_exposure column → vol keys None


def _mkseries(index: list[float], trend: list[str]) -> list[dict]:  # type: ignore[type-arg]
    return [
        {"date": f"2020-01-{i + 1:02d}", "index": index[i], "trend_label": trend[i],
         "exposure": 1.0 if trend[i] == "bull" else 0.0}
        for i in range(len(index))
    ]


def test_net_metrics_credit_mm_yield_and_charge_costs() -> None:
    # Index rises then falls; sma sits in cash for the back half (bear).
    series = _mkseries(
        [100.0, 110.0, 121.0, 121.0, 110.0, 100.0],
        ["bull", "bull", "bull", "bear", "bear", "bear"],
    )
    free = mon.sector_metrics_net(series, mm_pct=0.0, cost_bps=0.0)
    yielded = mon.sector_metrics_net(series, mm_pct=10.0, cost_bps=0.0)
    costly = mon.sector_metrics_net(series, mm_pct=10.0, cost_bps=50.0)
    # A money-market yield on the cash (bear) leg raises net CAGR; costs lower it.
    assert yielded["cagr_sma"] > free["cagr_sma"]
    assert costly["cagr_sma"] < yielded["cagr_sma"]
    # always-in is pure buy-and-hold — untouched by yield/cost, and 0 here (round trip).
    assert free["cagr_always"] == pytest.approx(0.0)
    assert yielded["cagr_always"] == pytest.approx(0.0)
    # every metric key is present
    assert set(mon.METRIC_KEYS) <= set(yielded)


def test_net_edge_from_metrics() -> None:
    m = {"cagr_sma": 0.08, "cagr_vol": 0.06, "cagr_always": 0.05}
    assert mon.net_edge(m, "sma")["edge"] == pytest.approx(0.03)
    assert mon.net_edge(m, "vol")["edge"] == pytest.approx(0.01)
    assert mon.net_edge({"cagr_sma": None, "cagr_always": 0.05}, "sma") is None
    assert mon.net_edge(None, "sma") is None


def test_net_metrics_none_without_series() -> None:
    assert all(v is None for v in mon.sector_metrics_net(None, 4.0, 5.0).values())
    assert all(v is None for v in mon.sector_metrics_net([], 4.0, 5.0).values())


def test_net_summary_counts_profitable_sectors() -> None:
    edges = [{"edge": 0.02}, {"edge": -0.01}, {"edge": 0.005}, None]
    s = mon.net_summary(edges)
    assert s["n"] == 3
    assert s["profitable"] == 2
    assert s["median"] == pytest.approx(round(float(np.median([0.02, -0.01, 0.005])), 6))


def test_filter_scorecard() -> None:
    def mk(sma, always, vol, dd_sma, dd_a, dd_vol, has_data=True):  # type: ignore[no-untyped-def]
        return {
            "date_from": "2020-01-01" if has_data else None,
            "metrics": {
                "sharpe_sma": sma, "sharpe_always": always, "sharpe_vol": vol,
                "sortino_sma": None, "sortino_always": None, "sortino_vol": None,
                "cagr_sma": None, "cagr_always": None, "cagr_vol": None,
                "maxdd_sma": dd_sma, "maxdd_always": dd_a, "maxdd_vol": dd_vol,
            },
        }

    summaries = [
        mk(1.0, 0.5, 1.2, -0.2, -0.4, -0.15),
        mk(0.4, 0.6, 0.5, -0.3, -0.2, -0.35),  # vol deeper than sma here
        mk(0.8, 0.8, 0.7, -0.1, -0.5, -0.05),
        mk(9.9, 0.0, 9.9, 0.0, 0.0, 0.0, has_data=False),  # no data → excluded
    ]
    sc = mon.filter_scorecard(summaries)
    assert sc["n"] == 3
    assert sc["sharpe"]["always"] == 0.6  # median(0.5, 0.6, 0.8)
    assert sc["sharpe"]["sma"] == 0.8  # median(1.0, 0.4, 0.8)
    assert sc["sharpe"]["vol"] == 0.7  # median(1.2, 0.5, 0.7)
    assert sc["sharpe"]["win"] == round(1 / 3, 3)  # sma > always: only 1.0 > 0.5
    assert sc["sharpe"]["beats"] == round(2 / 3, 3)  # vol > sma in 2 of 3 (1.2>1.0, 0.5>0.4)
    assert sc["maxdd"]["beats"] == round(2 / 3, 3)  # vol shallower than sma in 2 of 3
    assert sc["sortino"]["sma"] is None  # no sortino data


# ── MA / label integration ────────────────────────────────────────────────────
def test_short_history_has_no_ma_but_computes_metrics() -> None:
    a = _series("2020-01-01", list(100.0 * (1.005 ** np.arange(50))))
    gdf = mon.build_group_daily({"A": a})
    assert gdf["ma_200"].isna().all()
    assert set(gdf["confirmed_label"]) == {"bull"}
    assert mon._state(gdf)["label"] == "bull"
    assert mon.group_metrics(gdf)["cagr_always"] is not None


def test_index_crosses_ma_into_confirmed_bear() -> None:
    up = list(100.0 * (1.001 ** np.arange(230)))
    down = list(up[-1] * (0.99 ** np.arange(1, 40)))
    gdf = mon.build_group_daily({"A": _series("2018-01-01", up + down)})
    assert gdf["ma_200"].notna().any()
    labels = gdf["confirmed_label"].tolist()
    assert "bull" in labels
    assert labels[-1] == "bear"


def test_empty_group_is_bull_with_null_metrics() -> None:
    gdf = mon.build_group_daily({})
    assert gdf.empty
    assert mon._state(gdf) == {"label": "bull", "since": None, "date_from": None, "date_to": None}
    assert all(v is None for v in mon.group_metrics(gdf).values())


# ── sector plumbing (universe + store monkeypatched) ──────────────────────────
_UNIVERSE = [
    {"yf": "AAA", "sector": "Tech", "name": "Alpha"},
    {"yf": "BBB", "sector": "Tech", "name": "Beta"},
    {"yf": "CCC", "sector": "Energy", "name": "Gamma"},
    {"yf": None, "sector": "Tech", "name": "skip-no-ticker"},
    {"yf": "DDD", "sector": None, "name": "skip-no-sector"},
]


@pytest.fixture
def store(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(mon, "_sectors_cache", None)
    monkeypatch.setattr(mon, "_universe_instruments", lambda: _UNIVERSE)
    return tmp_path


def test_sector_tickers_and_list(store: Path) -> None:
    assert mon.sector_tickers() == {"Tech": ["AAA", "BBB"], "Energy": ["CCC"]}
    assert mon.list_sectors() == ["Energy", "Tech"]


def test_sector_returns_equal_weight(store: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Two constituents moving oppositely → equal-weighted return ~0 on day 2.
    def fake_load(t: str, columns: object = None) -> pd.DataFrame:
        idx = pd.bdate_range("2020-01-01", periods=2)
        px = {"AAA": [100.0, 101.0], "BBB": [100.0, 99.0]}[t]
        return pd.DataFrame({"adj_close": px, "close": px}, index=idx)

    monkeypatch.setattr(mon.prices, "load_prices", fake_load)
    monkeypatch.setattr(mon.prices, "repair_adj_close", lambda df: df["adj_close"])
    grp, n = mon._sector_returns(["AAA", "BBB"])
    assert n == 2
    assert np.isnan(grp.iloc[0])  # seed
    assert grp.iloc[1] == pytest.approx(0.0, abs=1e-12)


def test_run_daily_update_caches_each_sector(store: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mon, "_sector_returns", lambda tk: (None, 0))  # no price data
    res = mon.run_daily_update()
    assert res["sectors_updated"] == 2
    # cached defaults: no data → bull, null metrics, but the count is live
    s = {x["name"]: x for x in mon.list_summaries()}
    assert s["Tech"]["count"] == 2
    assert s["Tech"]["variants"]["vol"]["label"] == "bull"
    assert s["Tech"]["variants"]["sma"]["label"] == "bull"
    assert s["Tech"]["date_from"] is None
    assert mon.load_cache("Tech") is not None


def test_sector_series_unknown_raises(store: Path) -> None:
    with pytest.raises(mon.NotFoundError):
        mon.sector_series("Nonexistent")
