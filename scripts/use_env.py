"""Switch the active .env between profiles (.env.live, .env.paper, ...).

Without arguments, prints which profile is currently active. With a profile
name, atomically repoints .env at .env.<profile>.

    uv run python scripts/use_env.py            # show current profile
    uv run python scripts/use_env.py live       # switch to .env.live
    uv run python scripts/use_env.py paper      # switch to .env.paper
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def main() -> int:
    env = REPO_ROOT / ".env"

    if len(sys.argv) == 1:
        if env.is_symlink():
            print(f".env -> {env.readlink()}")
        elif env.is_file():
            print(".env exists as a regular file (not a profile symlink)")
        else:
            print(".env does not exist")
        return 0

    if len(sys.argv) != 2:
        print("usage: use_env.py [profile]", file=sys.stderr)
        return 2

    profile = sys.argv[1]
    target = REPO_ROOT / f".env.{profile}"
    if not target.is_file():
        print(f"FAILED: {target.name} does not exist in {REPO_ROOT}", file=sys.stderr)
        return 1

    if env.exists() or env.is_symlink():
        env.unlink()
    env.symlink_to(target.name)
    print(f".env -> {target.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
