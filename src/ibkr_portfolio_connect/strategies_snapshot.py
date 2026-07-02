"""Snapshot the scheduled strategies + their current holdings from bbterminal.

The credentialed side (worker / launcher refresh) runs this and writes
`data/strategies_snapshot.json`; the read-only web app only reads that file, so
the Strategies page never touches bbterminal itself (same credential boundary as
the mapping and portfolio snapshots).

    momentum-strategies-snapshot            # enabled scheduled strategies only
    momentum-strategies-snapshot --all      # include disabled ones too
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .bbterminal_client import BBTerminalClient

log = logging.getLogger(__name__)

# The bbterminal schedule fields worth carrying into the snapshot verbatim.
_META = (
    "name", "enabled", "frequency", "next_rebalance_at", "last_run_at",
    "as_of_date", "latest_price_date", "holdings_count",
)


def build_snapshot(bb: BBTerminalClient, *, enabled_only: bool = True) -> dict[str, Any]:
    """Pull every scheduled strategy and its current order-ready holdings.

    Performance stats (mtd / since-inception) are best-effort — a young strategy
    may not have them yet, so a failure there never sinks the whole snapshot."""
    scheds = bb.schedules(enabled_only=enabled_only)
    strategies: list[dict[str, Any]] = []
    for s in scheds:
        sid = int(s["strategy_id"])
        detail = bb.schedule(sid)
        row: dict[str, Any] = {"strategy_id": sid}
        row.update({k: detail.get(k, s.get(k)) for k in _META})
        try:
            perf = bb.performance(sid)
            row.update({
                "inception_date": perf.get("inception_date"),
                "mtd_return_pct": perf.get("mtd_return_pct"),
                "since_inception_return_pct": perf.get("since_inception_return_pct"),
            })
        except Exception as e:  # perf is optional enrichment — never sink the snapshot
            log.warning("performance(%s) failed; skipping perf stats: %s", sid, e)
            row.update({"inception_date": None, "mtd_return_pct": None,
                        "since_inception_return_pct": None})
        row["holdings"] = detail.get("holdings", [])
        strategies.append(row)
        log.info("strategy %s %r — %d holdings", sid, row.get("name"), len(row["holdings"]))

    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "enabled_only": enabled_only,
        "count": len(strategies),
        "strategies": strategies,
    }


def write_local(snapshot: dict[str, Any], data_dir: Path | None = None) -> Path:
    data_dir = data_dir or Path(os.environ.get("MOMENTUM_DATA_DIR", "data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    out = data_dir / "strategies_snapshot.json"
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
    return out


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv()
    p = argparse.ArgumentParser(description="Snapshot scheduled strategies + holdings from bbterminal")
    p.add_argument("--all", action="store_true", help="include disabled/unscheduled strategies")
    args = p.parse_args()

    data_dir = Path(os.environ.get("MOMENTUM_DATA_DIR", "data"))
    bb = BBTerminalClient.from_env()
    snapshot = build_snapshot(bb, enabled_only=not args.all)
    out = write_local(snapshot, data_dir)
    print(f"wrote {out} — {snapshot['count']} strategies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
