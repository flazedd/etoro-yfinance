"""Tests for the pinned conid-map data model + pre-trade gate (no IBKR)."""

from __future__ import annotations

from typing import Any

import pytest

from ibkr_portfolio_connect.conid_map import (
    ConidMap,
    ConidMapError,
    classify,
    load_map,
    make_entry,
    require_reviewed_conid,
    save_map,
)

NOW = "2026-06-14T00:00:00+00:00"


def _holding(company_id: int = 4433, **over: Any) -> dict[str, Any]:
    h = {
        "company_id": company_id,
        "ticker": "CSG",
        "company_name": "CSG CLASS A NV",
        "isin": "NL0015073TS8",
        "exchange": "XAMS",
        "currency": "EUR",
    }
    h.update(over)
    return h


def _entry(reviewed: bool = True, conid: int = 848752492, **over: Any):  # type: ignore[no-untyped-def]
    e = make_entry(
        _holding(),
        conid=conid,
        ibkr_symbol="CSG1",
        ibkr_listing="AEB",
        resolved_via="isin",
        reviewed=reviewed,
        now=NOW,
    )
    for k, v in over.items():
        setattr(e, k, v)
    return e


def test_classify_added_changed_unchanged() -> None:
    assert classify(None, 1) == "added"
    assert classify(_entry(conid=1), 1) == "unchanged"
    assert classify(_entry(conid=1), 2) == "changed"


def test_require_reviewed_conid_happy_path() -> None:
    m = ConidMap()
    m.put(_entry(reviewed=True))
    assert require_reviewed_conid(m, 4433) == 848752492


def test_require_missing_raises() -> None:
    with pytest.raises(ConidMapError, match="not in the conid map"):
        require_reviewed_conid(ConidMap(), 9999)


def test_require_unreviewed_raises() -> None:
    m = ConidMap()
    m.put(_entry(reviewed=False))
    with pytest.raises(ConidMapError, match="not reviewed"):
        require_reviewed_conid(m, 4433)


def test_require_isin_drift_raises() -> None:
    m = ConidMap()
    m.put(_entry(reviewed=True))
    with pytest.raises(ConidMapError, match="ISIN drift"):
        require_reviewed_conid(m, 4433, expected_isin="NL0000000000")


def test_round_trip_save_load(tmp_path: Any) -> None:
    path = tmp_path / "conid_map.json"
    m = ConidMap(strategy_id=14, generated_at=NOW)
    m.put(_entry(reviewed=True))
    save_map(m, path)
    loaded = load_map(path)
    assert loaded.strategy_id == 14
    assert loaded.get(4433) is not None
    assert loaded.get(4433).conid == 848752492  # type: ignore[union-attr]
    assert loaded.get(4433).reviewed is True  # type: ignore[union-attr]


def test_load_missing_returns_empty(tmp_path: Any) -> None:
    assert load_map(tmp_path / "nope.json").entries == {}
