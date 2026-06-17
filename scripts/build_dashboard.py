"""Render a static, self-contained dashboard.html from the run records.

The offline counterpart to the live server (dashboard_server.py): same page,
but with the data baked in so it needs nothing running. Generate it after a run
(or on a small cron) and open it locally / sync it off-box.

    uv run python scripts/build_dashboard.py                       # uses REPORT_DIR/LOG_DIR from .env
    uv run python scripts/build_dashboard.py --report-dir runs --log-dir logs
    open data/dashboard.html

Read-only; no broker access.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from ibkr_portfolio_connect import dashboard  # noqa: E402
from ibkr_portfolio_connect.dashboard_server import DashboardConfig  # noqa: E402


def main() -> int:
    cfg = DashboardConfig()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, default=cfg.report_dir,
                        help="dir of run-record JSONs (default: REPORT_DIR from .env)")
    parser.add_argument("--log-dir", type=Path, default=cfg.log_dir,
                        help="dir holding rebalance.log (default: LOG_DIR from .env)")
    parser.add_argument("--out", type=Path, default=Path("data/dashboard.html"))
    parser.add_argument("--log-lines", type=int, default=cfg.log_tail_lines)
    args = parser.parse_args()

    if args.report_dir is None:
        print("no --report-dir and REPORT_DIR unset; nothing to render", file=sys.stderr)
        return 1

    records = dashboard.load_records(args.report_dir)
    log_path = (args.log_dir / cfg.log_filename) if args.log_dir else None
    tail = dashboard.tail_log(log_path, args.log_lines)
    html = dashboard.render_html(records, log_tail=tail, live=False)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html)
    print(f"wrote {args.out}  ({len(records)} runs, {len(tail)} log lines)")
    print(f"open it:  open {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
