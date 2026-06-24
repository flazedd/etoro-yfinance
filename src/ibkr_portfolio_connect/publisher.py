"""Performance publisher — bbterminal API -> local snapshot + GitHub Pages repo.

Run by the credentialed side (the trader user) on a timer. It:
  1. fetches the enabled strategy's performance + current holdings from bbterminal,
  2. writes data/performance_snapshot.json (what the read-only web page renders),
  3. optionally commits that JSON into a checkout of the public site repo and
     pushes it (GitHub Pages rebuilds on push).

    momentum-publish                 # fetch + write local snapshot only
    momentum-publish --push          # also commit + push to the site repo

Config (env):
  MOMENTUM_SITE_REPO_DIR   local checkout of the GitHub Pages repo to publish into
  MOMENTUM_SITE_DATA_PATH  path within that repo for the JSON (default: data/performance.json)
  MOMENTUM_DEPLOY_KEY      optional SSH private-key path used for the push
  MOMENTUM_PUBLISH_PUSH=1  push without needing the --push flag

This is the only component that holds bbterminal creds AND a git deploy key.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .bbterminal_client import BBTerminalClient

log = logging.getLogger(__name__)


def build_snapshot(bb: BBTerminalClient, strategy_id: int | None = None) -> dict[str, Any]:
    """Pull performance + holdings for the enabled strategy (or a given id)."""
    if strategy_id is None:
        scheds = bb.schedules(enabled_only=True)
        if not scheds:
            raise RuntimeError("no enabled scheduled strategy on bbterminal")
        strategy_id = int(scheds[0]["strategy_id"])

    detail = bb.schedule(strategy_id)
    perf = bb.performance(strategy_id)
    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "strategy_id": strategy_id,
        "name": detail.get("name") or perf.get("name", ""),
        "as_of_date": detail.get("as_of_date"),
        "next_rebalance_at": detail.get("next_rebalance_at"),
        "inception_date": perf.get("inception_date"),
        "mtd_return_pct": perf.get("mtd_return_pct"),
        "since_inception_return_pct": perf.get("since_inception_return_pct"),
        "daily_returns": perf.get("daily_returns", []),
        "holdings": detail.get("holdings", []),
    }


def write_local(snapshot: dict[str, Any], data_dir: Path | None = None) -> Path:
    data_dir = data_dir or Path(os.environ.get("MOMENTUM_DATA_DIR", "data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    out = data_dir / "performance_snapshot.json"
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
    return out


def _git(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    full_env = {**os.environ, **(env or {})}
    res = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, env=full_env, check=False,
    )
    if res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {res.stderr.strip()}")
    return res.stdout.strip()


def publish_to_repo(snapshot: dict[str, Any], repo_dir: Path, *, push: bool) -> dict[str, str]:
    """Write the snapshot into the site repo, commit, and (optionally) push."""
    if not (repo_dir / ".git").exists():
        raise RuntimeError(f"{repo_dir} is not a git checkout")
    rel = os.environ.get("MOMENTUM_SITE_DATA_PATH", "data/performance.json")
    target = repo_dir / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))

    _git(repo_dir, "add", rel)
    status = _git(repo_dir, "status", "--porcelain", rel)
    if not status:
        log.info("no change in %s — nothing to commit", rel)
        return {"committed": "false", "commit": _git(repo_dir, "rev-parse", "--short", "HEAD")}

    msg = (f"Update performance: {snapshot.get('name','strategy')} "
           f"MTD {snapshot.get('mtd_return_pct')}% as of {snapshot.get('as_of_date')}")
    _git(repo_dir, "commit", "-m", msg)
    commit = _git(repo_dir, "rev-parse", "--short", "HEAD")

    if push:
        env = {}
        key = os.environ.get("MOMENTUM_DEPLOY_KEY")
        if key:
            env["GIT_SSH_COMMAND"] = f"ssh -i {key} -o IdentitiesOnly=yes"
        _git(repo_dir, "push", env=env)
        log.info("pushed %s to site repo", commit)
    return {"committed": "true", "commit": commit, "pushed": str(push)}


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv()
    parser = argparse.ArgumentParser(description="Publish bbterminal performance")
    parser.add_argument("--strategy", type=int, default=None, help="strategy id (default: enabled one)")
    parser.add_argument("--push", action="store_true", help="commit + push to the site repo")
    parser.add_argument("--no-local", action="store_true", help="skip writing the local web snapshot")
    args = parser.parse_args()

    bb = BBTerminalClient.from_env()
    snapshot = build_snapshot(bb, strategy_id=args.strategy)

    if not args.no_local:
        out = write_local(snapshot)
        print(f"wrote {out}")

    repo_dir = os.environ.get("MOMENTUM_SITE_REPO_DIR")
    push = args.push or os.environ.get("MOMENTUM_PUBLISH_PUSH") == "1"
    if repo_dir:
        info = publish_to_repo(snapshot, Path(repo_dir), push=push)
        snapshot["published"] = {
            "repo": repo_dir, "commit": info.get("commit", ""),
            "at": snapshot["generated_at"],
        }
        if not args.no_local:
            write_local(snapshot)  # re-write with the publish stamp
        print(f"site repo: committed={info.get('committed')} commit={info.get('commit')} pushed={info.get('pushed','false')}")
    else:
        print("MOMENTUM_SITE_REPO_DIR not set — local snapshot only (no git publish)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
