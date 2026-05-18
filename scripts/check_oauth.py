"""Standalone OAuth 1.0a connectivity test.

Reads IBIND_* env vars from .env and attempts a minimal authenticated request
against IBKR's hosted API. Use this to verify the OAuth registration has been
activated by IBKR before doing any project-wide refactor.

Exit codes:
  0  authenticated successfully
  1  reached IBKR but unauthorized (consumer key likely not yet activated)
  2  configuration error (missing env var, missing key file, etc.)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env BEFORE importing ibind — ibind reads env vars at module import time.
load_dotenv()

from ibind import IbkrClient  # noqa: E402, I001


REQUIRED_VARS = (
    "IBIND_USE_OAUTH",
    "IBIND_OAUTH1A_CONSUMER_KEY",
    "IBIND_OAUTH1A_ACCESS_TOKEN",
    "IBIND_OAUTH1A_ACCESS_TOKEN_SECRET",
    "IBIND_OAUTH1A_SIGNATURE_KEY_FP",
    "IBIND_OAUTH1A_ENCRYPTION_KEY_FP",
    "IBIND_OAUTH1A_DH_PRIME",
)


def main() -> int:
    missing = [v for v in REQUIRED_VARS if not os.environ.get(v)]
    if missing:
        print(f"missing env vars: {', '.join(missing)}", file=sys.stderr)
        return 2

    for var in ("IBIND_OAUTH1A_SIGNATURE_KEY_FP", "IBIND_OAUTH1A_ENCRYPTION_KEY_FP"):
        p = Path(os.environ[var]).expanduser()
        if not p.is_file():
            print(f"{var} = {p} does not exist", file=sys.stderr)
            return 2

    print("constructing IbkrClient with OAuth 1.0a")
    client = IbkrClient(use_oauth=True)

    try:
        print("\n-- tickle (live session token + ping) --")
        print(client.tickle().data)

        print("\n-- portfolio_accounts --")
        print(client.portfolio_accounts().data)
    except Exception as e:
        print(f"\nrequest failed: {e!r}", file=sys.stderr)
        return _classify(e)

    print("\nOK — OAuth is active and authenticated.")
    return 0


def _classify(e: BaseException) -> int:
    msg = str(e).lower()
    if any(s in msg for s in ("401", "403", "unauthor", "forbidden")):
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
