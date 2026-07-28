"""Tests for the web's read-only loaders — the raw/clean store overlay.

Store-free: a tiny synthetic mapping snapshot plus hand-written quality reports
in a tmp data dir, so the whole raw/clean switch is exercised without touching
the real 9k-instrument store.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from etoro_yfinance.web import data as wd


def _report(ticker: str, *, admitted: bool = True, reason: str | None = None) -> dict[str, Any]:
    """A quality report whose two stores disagree, so the overlay is visible."""
    return {
        "ticker": ticker,
        "admitted": admitted,
        "reason": reason,
        "raw": {
            "rows": 1000, "cells": 5000,
            "price_from": "1999-01-04", "price_to": "2026-07-02",
            "vol_from": "1999-01-04", "vol_to": "2026-07-02",
        },
        "clean": {
            "rows": 400 if admitted else 0, "cells": 2000 if admitted else 0,
            "price_from": "2020-05-06" if admitted else None,
            "price_to": "2026-07-02" if admitted else None,
            "vol_from": "2020-05-06" if admitted else None,
            "vol_to": "2026-07-02" if admitted else None,
        },
    }


@pytest.fixture
def store(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    snap = {
        "generated_at": "2026-07-02",
        "counts": {},
        "rows": [
            {"instrument_id": 1, "symbol": "AAA", "yf": "AAA", "status": "us", "bars": 9},
            {"instrument_id": 2, "symbol": "BBB", "yf": "BBB", "status": "us", "bars": 9},
            {"instrument_id": 3, "symbol": "CCC", "yf": None, "status": "unmapped"},
        ],
    }
    (tmp_path / "etoro_universe_mapping.json").write_text(json.dumps(snap))
    q = tmp_path / "quality"
    q.mkdir()
    (q / "AAA.json").write_text(json.dumps(_report("AAA")))
    (q / "BBB.json").write_text(json.dumps(_report("BBB", admitted=False, reason="frozen")))
    return tmp_path


def _by_yf(doc: dict[str, Any]) -> dict[str, Any]:
    return {r["yf"]: r for r in doc["rows"] if r.get("yf")}


def test_clean_is_the_default_store(store: Path) -> None:
    rows = _by_yf(wd.load_etoro_universe())
    assert rows["AAA"]["bars"] == 400  # the clean store's count, not the snapshot's 9
    assert rows["AAA"]["price_from"] == "2020-05-06"


def test_raw_store_shows_yahoo_as_fetched(store: Path) -> None:
    rows = _by_yf(wd.load_etoro_universe("raw"))
    assert rows["AAA"]["bars"] == 1000
    assert rows["AAA"]["price_from"] == "1999-01-04"
    assert rows["AAA"]["vol_to"] == "2026-07-02"


def test_rejected_instrument_is_marked_only_in_the_clean_view(store: Path) -> None:
    clean = _by_yf(wd.load_etoro_universe("clean"))
    assert clean["BBB"]["dropped"] is True
    assert clean["BBB"]["drop_reason"] == "frozen"
    assert not clean["BBB"]["bars"]  # nothing in the clean store
    raw = _by_yf(wd.load_etoro_universe("raw"))
    assert raw["BBB"]["dropped"] is False  # the raw store still has it
    assert raw["BBB"]["bars"] == 1000
    assert clean["AAA"]["dropped"] is False  # an admitted name is never marked


def test_unknown_store_falls_back_to_clean(store: Path) -> None:
    for name in ("bogus", "", "RAW"):
        assert _by_yf(wd.load_etoro_universe(name))["AAA"]["bars"] == 400


def test_instrument_without_a_report_keeps_its_snapshot_row(store: Path) -> None:
    # CCC is unmapped, so it was never ingested and has no quality report.
    rows = {r["symbol"]: r for r in wd.load_etoro_universe()["rows"]}
    assert rows["CCC"]["dropped"] is False
    assert rows["CCC"]["drop_reason"] is None


def test_no_quality_reports_at_all_leaves_the_page_working(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    snap = {"counts": {}, "rows": [{"instrument_id": 1, "symbol": "AAA", "yf": "AAA", "bars": 9}]}
    (tmp_path / "etoro_universe_mapping.json").write_text(json.dumps(snap))
    rows = _by_yf(wd.load_etoro_universe())
    assert rows["AAA"]["bars"] == 9  # falls back to the snapshot's own coverage
    assert rows["AAA"]["dropped"] is False
    assert wd.load_quality() == {}
