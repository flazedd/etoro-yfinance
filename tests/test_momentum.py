"""Tests for the momentum signals + scoring — the math the backtest trades on.

Signals are checked against first-principles expectations on synthetic series
(so a silent change in a rolling window or an as-of lookup fails loudly), and
the cutoff reader is checked for look-ahead: data after a cutoff must never
change that cutoff's signals.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from hypothesis import given
from hypothesis import strategies as st

from etoro_yfinance import momentum

_START = "2019-01-01"
_DAYS = 800  # > 2 years of daily (calendar) bars


def _series(daily_growth: float = 0.001, days: int = _DAYS, wobble: float = 0.0) -> pd.Series:
    """Geometric price series on a calendar-daily index (so `t - N months`
    always lands on an existing bar and expectations are exact). `wobble` adds
    a deterministic ripple so returns have non-zero volatility (a perfectly
    smooth series has std=0 and an undefined vol-adjusted return)."""
    idx = pd.date_range(_START, periods=days, freq="D")
    n = np.arange(days)
    px = 100.0 * (1.0 + daily_growth) ** n * (1.0 + wobble * np.sin(n / 3.0))
    return pd.Series(px, index=idx)


def _expected_return_pct(s: pd.Series, at: pd.Timestamp, months: int) -> float:
    past = s.loc[at - pd.DateOffset(months=months)]
    return round(float((s.loc[at] / past - 1.0) * 100.0), 2)


def test_price_signals_match_first_principles() -> None:
    s = _series()
    cutoff = pd.Timestamp("2020-06-01")
    panels = momentum.signals_at_cutoffs({"AAA": s}, {}, {"AAA": "Tech"}, [cutoff])
    row = panels[cutoff].iloc[0]
    anchor = s.index[s.index.searchsorted(cutoff, side="left") - 1]  # strictly before

    assert row["company_id"] == "AAA"
    assert row["mom_6m"] == _expected_return_pct(s, anchor, 6)
    # 12-1 momentum: t-1m vs t-12m.
    p1 = s.loc[anchor - pd.DateOffset(months=1)]
    p12 = s.loc[anchor - pd.DateOffset(months=12)]
    assert row["mom_12_1"] == round((p1 / p12 - 1.0) * 100.0, 2)
    # A strictly rising series sits on its high and above its 200-day MA.
    assert row["drawdown_from_recent_high_pct"] == 0.0
    assert row["above_200ma"] == 1.0


def test_volume_signals_flat_volume_is_neutral() -> None:
    s = _series()
    vol = pd.Series(1000.0, index=s.index)
    cutoff = pd.Timestamp("2020-06-01")
    panels = momentum.signals_at_cutoffs({"AAA": s}, {"AAA": vol}, {"AAA": "T"}, [cutoff])
    row = panels[cutoff].iloc[0]
    assert row["vol_20d_vs_60d"] == 1.0  # 20d avg == 60d avg
    assert abs(row["vol_trend_3m"]) < 1e-9  # no trend in constant volume


def test_no_look_ahead_at_cutoff() -> None:
    """Mutating every bar ON/AFTER the cutoff must not move that cutoff's signals."""
    cutoff = pd.Timestamp("2020-06-01")
    clean = _series()
    poisoned = clean.copy()
    poisoned.loc[poisoned.index >= cutoff] *= 5.0  # a fake post-cutoff moonshot

    a = momentum.signals_at_cutoffs({"AAA": clean}, {}, {"AAA": "T"}, [cutoff])[cutoff]
    b = momentum.signals_at_cutoffs({"AAA": poisoned}, {}, {"AAA": "T"}, [cutoff])[cutoff]
    pd.testing.assert_frame_equal(a, b)


def test_min_history_days_gates_on_price_and_volume_age() -> None:
    cutoff = pd.Timestamp("2020-06-01")
    s = _series()  # price history starts 2019-01-01 → ~517 days before cutoff
    vol = pd.Series(1000.0, index=s.index)

    def at(min_history_days: int | None) -> pd.DataFrame:
        return momentum.signals_at_cutoffs(
            {"AAA": s}, {"AAA": vol}, {"AAA": "T"}, [cutoff], min_history_days=min_history_days
        )[cutoff]

    assert not at(None).empty  # parity default
    assert not at(365).empty
    assert at(730).empty
    # Volume history younger than the requirement blocks the ticker even
    # though the price series is old enough.
    young_vol = vol.loc["2020-01-01":]
    panels = momentum.signals_at_cutoffs(
        {"AAA": s}, {"AAA": young_vol}, {"AAA": "T"}, [cutoff], min_history_days=365
    )
    assert panels[cutoff].empty


def test_stale_and_short_series_are_excluded() -> None:
    cutoff = pd.Timestamp("2020-06-01")
    stale = _series().loc[: cutoff - pd.Timedelta(days=momentum.MAX_STALENESS_DAYS + 10)]
    short = _series(days=10)
    panels = momentum.signals_at_cutoffs(
        {"STALE": stale, "SHORT": short}, {}, {"STALE": "T", "SHORT": "T"}, [cutoff]
    )
    assert panels[cutoff].empty


def test_score_universe_ranks_stronger_momentum_higher() -> None:
    cutoff = pd.Timestamp("2020-06-01")
    fast, slow = _series(0.002, wobble=0.002), _series(0.0005, wobble=0.002)
    panels = momentum.signals_at_cutoffs(
        {"FAST": fast, "SLOW": slow}, {}, {"FAST": "T", "SLOW": "T"}, [cutoff]
    )
    scored = momentum.score_universe(panels[cutoff])
    by_id = scored.set_index("company_id")["momentum_score"]
    assert by_id["FAST"] > by_id["SLOW"]
    assert ((scored["momentum_score"] >= 0) & (scored["momentum_score"] <= 100)).all()


@given(
    st.lists(
        st.floats(min_value=-1e6, max_value=1e6) | st.just(float("nan")), min_size=1, max_size=30
    )
)
def test_scores_always_bounded_0_100(vals: list[float]) -> None:
    df = pd.DataFrame(
        {
            "company_id": [f"T{i}" for i in range(len(vals))],
            "sector": "X",
            "mom_12_1": vals,
            "mom_6m": vals,
            "volatility_adjusted_return_6m": vals,
            "drawdown_from_recent_high_pct": vals,
            "above_200ma": vals,
            "vol_20d_vs_60d": vals,
            "vol_trend_3m": vals,
        }
    )
    scored = momentum.score_universe(df, exclude_incomplete=False)
    s = scored["momentum_score"]
    assert s.notna().all()
    assert ((s >= 0) & (s <= 100)).all()


def _scored(rows: list[tuple[str, str, float]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["company_id", "sector", "momentum_score"])


def test_select_takes_top_sectors_then_top_names() -> None:
    scored = _scored(
        [
            ("A1", "Alpha", 90.0),
            ("A2", "Alpha", 80.0),
            ("A3", "Alpha", 10.0),
            ("B1", "Beta", 60.0),
            ("B2", "Beta", 50.0),
            ("C1", "Gamma", 5.0),
        ]
    )
    sel = momentum.select_from_scored(scored, top_n_sectors=2, top_n_per_sector=2)
    # Alpha (mean 60) and Beta (mean 55) beat Gamma (5); two best names each.
    assert list(sel["company_id"]) == ["A1", "A2", "B1", "B2"]
    assert list(sel["company_rank"]) == [1, 2, 1, 2]


def test_select_min_sector_size_drops_thin_sectors() -> None:
    scored = _scored(
        [
            ("A1", "Alpha", 90.0),
            ("A2", "Alpha", 80.0),
            ("LONE", "Solo", 99.0),  # highest score, but a one-name sector
        ]
    )
    sel = momentum.select_from_scored(
        scored, top_n_sectors=2, top_n_per_sector=2, min_sector_size=2
    )
    assert "LONE" not in set(sel["company_id"])
    assert set(sel["sector"]) == {"Alpha"}


def test_strategy_signals_weights_sum_to_100() -> None:
    cats = momentum.strategy_signals()
    assert math.isclose(sum(c["weight_pct"] for c in cats), 100.0, abs_tol=1.0)
    keys = [s["key"] for c in cats for s in c["signals"]]
    assert sorted(keys) == sorted(momentum.DEFAULT_WEIGHTS)
