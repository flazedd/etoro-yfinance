"""Single-command runners for the read-only web UI — dev & prod.

    momentum-dev    # web with --reload (auto-restart on code edits)
    momentum-prod   # web, no reload
    momentum-up     # web, no reload (alias)

The app is fully read-only (it renders data/etoro_universe_mapping.json). There
is no worker or credentialed snapshot job anymore — rebuild the universe with
`uv run python scripts/etoro_universe.py` when you want fresh data.
"""

from __future__ import annotations

import os
import sys

from etoro_yfinance.web import server


def _run(reload: bool) -> int:
    if reload:
        os.environ["MOMENTUM_WEB_RELOAD"] = "1"
    return server.main()


def main() -> int:   # momentum-up
    return _run(reload=False)


def dev() -> int:    # momentum-dev
    return _run(reload=True)


def prod() -> int:   # momentum-prod
    return _run(reload=False)


if __name__ == "__main__":
    sys.exit(main())
