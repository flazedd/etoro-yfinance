"""Tests for universe selection — each criterion must actually filter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from etoro_yfinance import universe


def _row(**over: Any) -> dict[str, Any]:
    """A row that passes every default criterion; override one field per test."""
    base: dict[str, Any] = {
        "instrument_id": 1,
        "symbol": "AAPL",
        "name": "Apple",
        "yf": "AAPL",
        "type": "Stocks",
        "exchange": "Nasdaq",
        "sector": "Technology",
        "status": "us",
        "tradable": True,
        "adv_eur": 5_000_000.0,
        "spread_pct": 0.1,
        "bars": 400,
        "price_from": "2018-01-01",
        "price_to": "2024-06-28",
        "vol_from": "2018-01-01",
        "vol_to": "2024-06-28",
        "min_exposure": 10,
        "max_leverage": 5,
    }
    base.update(over)
    return base


def _select(rows: list[dict[str, Any]], **kw: Any) -> list[str]:
    return [r["symbol"] for r in universe.select(rows=rows, **kw)]


def test_select_passes_a_fully_qualified_row() -> None:
    assert _select([_row()]) == ["AAPL"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "unmapped"),  # not mapped to yfinance
        ("yf", None),  # no analysis ticker
        ("price_from", None),  # no price history
        ("vol_from", None),  # no volume history
        ("tradable", False),  # not executable on eToro
        ("adv_eur", 10_000.0),  # below the €1m/day liquidity floor
        ("bars", 100),  # not enough history
        ("sector", None),  # sector required by default
    ],
)
def test_select_drops_on_each_criterion(field: str, value: Any) -> None:
    rows = [_row(), _row(symbol="BAD", instrument_id=2, **{field: value})]
    assert _select(rows) == ["AAPL"]


def test_select_staleness_uses_latest_close_as_reference() -> None:
    rows = [
        _row(price_to="2024-06-28"),
        _row(symbol="STALE", instrument_id=2, price_to="2024-05-01"),
    ]
    assert _select(rows, recent_days=7) == ["AAPL"]
    # recent_days=None disables the staleness check.
    assert _select(rows, recent_days=None) == ["AAPL", "STALE"]


def test_select_max_spread_drops_wide_and_unknown() -> None:
    rows = [
        _row(),
        _row(symbol="WIDE", instrument_id=2, spread_pct=3.0),
        _row(symbol="UNK", instrument_id=3, spread_pct=None),
    ]
    assert _select(rows, max_spread=1.0) == ["AAPL"]
    assert _select(rows) == ["AAPL", "WIDE", "UNK"]  # no cap → all pass


def test_sector_gap_lists_only_the_sector_misses() -> None:
    rows = [
        _row(),
        _row(symbol="NOSEC", instrument_id=2, sector=None),
        _row(symbol="ILLIQ", instrument_id=3, sector=None, adv_eur=1.0),
    ]
    gap = universe.sector_gap(rows=rows)
    assert [r["symbol"] for r in gap] == ["NOSEC"]  # ILLIQ fails liquidity too


def test_earliest_start_is_first_member_coverage_plus_two_years() -> None:
    # The OLDEST member sets the start (assets join the backtest as they reach
    # 2y of history); per member, the later of price/volume coverage counts.
    rows = [
        _row(price_from="2018-01-05", vol_from="2018-03-01"),
        _row(symbol="YOUNG", price_from="2021-03-15", vol_from="2021-06-20"),
    ]
    assert universe.earliest_start(rows) == "2020-03-01"
    assert universe.earliest_start(rows, years=3) == "2021-03-01"


def test_earliest_start_floors_at_eur_epoch() -> None:
    # A 1960s listing can't start the EUR backtest before ECB rates exist.
    rows = [_row(price_from="1962-01-02", vol_from="1962-01-02")]
    assert universe.earliest_start(rows) == "2001-01-04"


def test_earliest_start_falls_back_to_price_and_handles_gaps() -> None:
    # No vol_from (older saved docs) → price_from gates; no coverage → skipped.
    rows = [_row(price_from="2020-05-01", vol_from=None), _row(price_from=None, vol_from=None)]
    assert universe.earliest_start(rows) == "2022-05-01"
    assert universe.earliest_start([]) is None
    assert universe.earliest_start([_row(price_from=None)]) is None


def test_earliest_start_leap_day() -> None:
    rows = [_row(price_from="2020-02-29", vol_from="2020-02-29")]
    assert universe.earliest_start(rows) == "2022-03-01"


def test_save_load_member_ids_roundtrip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    rows = [_row(), _row(symbol="MSFT", instrument_id=2, yf="MSFT")]
    doc = universe.save("My Test!", rows=rows, min_adv=1.0)
    assert doc["name"] == "MyTest"  # unsafe chars stripped
    assert doc["count"] == 2
    assert doc["checks"]["total"] == 2
    assert universe.list_saved() == ["MyTest"]
    assert universe.member_ids("MyTest") == {1, 2}
    loaded = universe.load("MyTest")
    assert [i["symbol"] for i in loaded["instruments"]] == ["AAPL", "MSFT"]
    assert universe.load("missing") == {}
