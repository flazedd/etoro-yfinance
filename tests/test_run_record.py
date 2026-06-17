"""Tests for the per-run audit recorder."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from ibkr_portfolio_connect.run_record import (
    ABORTED,
    DRY_RUN,
    FAILED,
    PARTIAL,
    RUNNING,
    SUCCESS,
    RunRecorder,
    status_from_report,
    summarize_positions,
    summarize_targets,
    summarize_trades,
)


class _Report:
    def __init__(self, dry_run: bool, ok: bool, n_successful: int) -> None:
        self.dry_run = dry_run
        self.overall_success = ok
        self.n_successful = n_successful


def test_recorder_writes_file_named_by_start(tmp_path: Path) -> None:
    rec = RunRecorder(tmp_path, dry_run=False, now=datetime(2026, 7, 1, 14, 30, 0, tzinfo=UTC))
    rec.persist()
    assert rec.path == tmp_path / "20260701-143000.json"
    assert rec.path.exists()
    assert json.loads(rec.path.read_text())["status"] == RUNNING


def test_recorder_noop_when_dir_none() -> None:
    rec = RunRecorder(None, dry_run=False)
    rec.update(nav=Decimal("1"))  # must not raise
    assert rec.path is None


def test_recorder_finish_sets_status_and_finished(tmp_path: Path) -> None:
    rec = RunRecorder(tmp_path, dry_run=False)
    rec.update(nav=Decimal("12345.67"))
    rec.finish(SUCCESS, now=datetime(2026, 7, 1, 14, 35, 0, tzinfo=UTC))
    blob = json.loads(rec.path.read_text())  # type: ignore[arg-type]
    assert blob["status"] == SUCCESS
    assert blob["finished_at"] == "2026-07-01T14:35:00+00:00"
    assert blob["nav"] == "12345.67"  # Decimal serialized as string


def test_recorder_persist_swallows_write_errors(tmp_path: Path) -> None:
    # report_dir is actually a FILE -> mkdir/write fails, but must not raise.
    f = tmp_path / "afile"
    f.write_text("x")
    rec = RunRecorder(f, dry_run=False)
    rec.persist()  # no exception


def test_status_from_report() -> None:
    assert status_from_report(_Report(dry_run=True, ok=False, n_successful=0)) == DRY_RUN
    assert status_from_report(_Report(dry_run=False, ok=True, n_successful=3)) == SUCCESS
    assert status_from_report(_Report(dry_run=False, ok=False, n_successful=1)) == PARTIAL
    assert status_from_report(_Report(dry_run=False, ok=False, n_successful=0)) == FAILED


def test_summarizers_are_defensive() -> None:
    # positions: dict with mixed key spellings, and a sparse one
    pos = summarize_positions([
        {"conid": 5171, "contractDesc": "BP", "position": 10, "mktValue": "500", "currency": "USD"},
        {"conidEx": "1@SEHK"},
    ])
    assert pos[0]["symbol"] == "BP"
    assert pos[0]["position"] == 10.0
    assert pos[1]["conid"] == "1@SEHK"
    assert pos[1]["position"] is None

    class _T:
        def __init__(self) -> None:
            self.conid = 111
            self.symbol = "AI"
            self.exchange = "SBF"
            self.weight_pct = Decimal("4.17")
            self.reference_price = Decimal("180.5")

    tg = summarize_targets([_T()])
    assert tg[0] == {
        "conid": 111, "symbol": "AI", "exchange": "SBF",
        "weight_pct": "4.17", "reference_price": "180.5",
    }


def test_aborted_constant_roundtrips(tmp_path: Path) -> None:
    rec = RunRecorder(tmp_path, dry_run=False)
    rec.finish(ABORTED, abort_reason="bbterminal not healthy")
    blob = json.loads(rec.path.read_text())  # type: ignore[arg-type]
    assert blob["status"] == ABORTED
    assert blob["abort_reason"] == "bbterminal not healthy"


def test_summarize_trades_reads_enum_side() -> None:
    class _Side:
        value = "SELL"

    class _Trade:
        side = _Side()
        quantity = 5
        symbol = "XYZ"
        conid = 9
        reason = "no longer in target"
        reference_price = None

    out = summarize_trades([_Trade()])
    assert out[0]["side"] == "SELL"
    assert out[0]["reference_price"] is None
