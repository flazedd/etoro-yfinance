"""Tests for the momentum dev/prod launcher — arg wiring, per-mode defaults, and
the cache-aware snapshot TTL gate. Process supervision itself is covered by a
manual smoke test, not unit tests."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from ibkr_portfolio_connect import launcher


def _args(**kw: object) -> argparse.Namespace:
    base = {"reload": False, "worker": True, "snapshots": False, "web_only": False,
            "fresh": False, "snapshot_interval": 0.0, "host": "127.0.0.1",
            "port": "8800", "poll": 5.0}
    base.update(kw)
    return argparse.Namespace(**base)


def test_default_runs_web_and_worker() -> None:
    assert [n for n, _ in launcher._build_services(_args())] == ["web", "worker"]


def test_web_only_drops_worker() -> None:
    assert [n for n, _ in launcher._build_services(_args(worker=False))] == ["web"]
    assert [n for n, _ in launcher._build_services(_args(web_only=True))] == ["web"]


def test_reload_and_bind_flags_flow_to_web_argv() -> None:
    ((_, web),) = launcher._build_services(_args(web_only=True, worker=False, reload=True,
                                                 host="0.0.0.0", port="9000"))
    assert "--reload" in web
    assert web[web.index("--host") + 1] == "0.0.0.0"
    assert web[web.index("--port") + 1] == "9000"


@pytest.mark.parametrize(("mode", "reload_", "snapshots"), [
    ("up", False, False), ("dev", True, True), ("prod", False, True)])
def test_mode_defaults(mode: str, reload_: bool, snapshots: bool) -> None:
    args = launcher._parser(mode).parse_args([])
    assert args.reload is reload_
    assert args.snapshots is snapshots
    assert args.worker is True


def test_web_only_forces_worker_and_snapshots_off() -> None:
    # _main applies the web-only override; emulate it on parsed dev args.
    args = launcher._parser("dev").parse_args(["--web-only"])
    if args.web_only:
        args.worker = False
        args.snapshots = False
    assert args.worker is False
    assert args.snapshots is False


def test_snapshot_skips_fresh_cache_and_refreshes_stale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("BBTERMINAL_EMAIL", "x@example.com")
    monkeypatch.setenv("BBTERMINAL_PASSWORD", "secret")
    # A fresh mapping snapshot (just written) + a missing portfolio one.
    (tmp_path / "mapping_snapshot.json").write_text("{}")

    ran: list[str] = []
    monkeypatch.setattr(launcher, "_run_prefixed",
                        lambda name, argv, width: ran.append(name) or 0)

    launcher._refresh_snapshots(force=False, width=10, stopping=__import__("threading").Event())
    # mapping is fresh -> skipped; portfolio + strategies are missing -> refreshed.
    assert ran == ["refresh:portfolio", "refresh:strategies"]


def test_snapshot_skipped_without_creds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("BBTERMINAL_PASSWORD", raising=False)
    ran: list[str] = []
    monkeypatch.setattr(launcher, "_run_prefixed",
                        lambda name, argv, width: ran.append(name) or 0)
    launcher._refresh_snapshots(force=False, width=10, stopping=__import__("threading").Event())
    assert ran == []  # no creds -> nothing runs, UI still serves cached data
