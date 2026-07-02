"""Single-command runners for the momentum stack — dev & prod.

Three entry points, all thin wrappers over one supervisor:

    momentum-dev    # DEV:  web (--reload) + worker + cache-aware bbterminal refresh
    momentum-prod   # PROD: web + worker + cache-aware bbterminal refresh (no reload)
    momentum-up     # bare supervisor; flags default to off (compose your own)

The supervisor runs the read-only web UI and the trade worker as child
processes, streams their logs with a per-service prefix, and stops them together
on Ctrl-C (if one exits, the rest are brought down too).

**Smart cache / bbterminal.** The web never calls bbterminal or IBKR — that's the
credential boundary. Instead the snapshot jobs (`mapping_snapshot`,
`portfolio_snapshot`) fetch from bbterminal/IBKR and write `data/*.json`, which
the web reads. On startup (and, with --snapshot-interval, on a timer) the runner
refreshes those snapshots **only when they're older than a TTL** — so a dev
restart is instant and reuses the cache, and a stale cache is refreshed in the
background without blocking the UI. Needs creds; skipped cleanly without them.

For real production, the systemd units in deploy/ (separate users, the credential
split, scheduled timers) remain the deployment model — these commands are the
convenient all-in-one for a dev box or a single-host/Docker run.
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

_PY = sys.executable

# (label, module, snapshot filename, default TTL seconds). A snapshot is
# refreshed only when missing or older than its TTL (unless --fresh).
_SNAPSHOTS: list[tuple[str, str, str, int]] = [
    ("mapping", "ibkr_portfolio_connect.mapping_snapshot", "mapping_snapshot.json", 12 * 3600),
    ("portfolio", "ibkr_portfolio_connect.portfolio_snapshot", "portfolio_snapshot.json", 3600),
    ("strategies", "ibkr_portfolio_connect.strategies_snapshot", "strategies_snapshot.json", 6 * 3600),
]


def _data_dir() -> Path:
    return Path(os.environ.get("MOMENTUM_DATA_DIR", "data"))


def _age_seconds(path: Path) -> float | None:
    try:
        return max(0.0, time.time() - path.stat().st_mtime)
    except OSError:
        return None


def _have_creds() -> bool:
    """Do we have enough env to hit bbterminal? (IBKR OAuth is validated lazily
    by the snapshot jobs themselves.)"""
    return bool(os.environ.get("BBTERMINAL_PASSWORD") and os.environ.get("BBTERMINAL_EMAIL"))


def _build_services(args: argparse.Namespace) -> list[tuple[str, list[str]]]:
    """The (name, argv) list to supervise, given parsed args."""
    web = [_PY, "-m", "ibkr_portfolio_connect.web.server",
           "--host", str(args.host), "--port", str(args.port)]
    if args.reload:
        web.append("--reload")
    services = [("web", web)]
    if args.worker and not args.web_only:
        services.append(("worker", [_PY, "-m", "ibkr_portfolio_connect.web.worker",
                                    "--poll", str(args.poll)]))
    return services


def _relay(name: str, proc: subprocess.Popen[str], width: int) -> None:
    tag = f"[{name}]".ljust(width)
    if proc.stdout is None:
        return
    for line in proc.stdout:
        sys.stdout.write(f"{tag} {line}")
        sys.stdout.flush()


def _run_prefixed(name: str, argv: list[str], width: int) -> int:
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1)
    _relay(name, proc, width)
    return proc.wait()


def _refresh_snapshots(force: bool, width: int, stopping: threading.Event) -> None:
    """Refresh each snapshot from bbterminal/IBKR when stale (TTL) or forced.
    Runs in a background thread so the UI is up immediately; logged with a
    [refresh] prefix. Skipped cleanly if creds are absent."""
    tag = "[refresh]".ljust(width)
    if not _have_creds():
        sys.stdout.write(f"{tag} no bbterminal creds — serving cached data/*.json as-is\n")
        sys.stdout.flush()
        return
    for label, module, filename, ttl in _SNAPSHOTS:
        if stopping.is_set():
            return
        age = _age_seconds(_data_dir() / filename)
        if not force and age is not None and age < ttl:
            sys.stdout.write(f"{tag} {label}: cache fresh ({age / 3600:.1f}h < {ttl / 3600:.0f}h TTL) — skip\n")
            sys.stdout.flush()
            continue
        why = "forced" if force else ("missing" if age is None else f"stale {age / 3600:.1f}h")
        sys.stdout.write(f"{tag} {label}: refreshing from bbterminal ({why})…\n")
        sys.stdout.flush()
        try:
            _run_prefixed(f"refresh:{label}", [_PY, "-m", module], width)
        except Exception as e:  # keep the UI up regardless
            sys.stdout.write(f"{tag} {label}: refresh failed: {e}\n")
            sys.stdout.flush()


def _run(args: argparse.Namespace) -> int:
    # Load .env so the snapshot refresh (and worker, in its own process) see creds.
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    services = _build_services(args)
    names = [n for n, _ in services] + (["refresh"] if args.snapshots else [])
    width = max(len(n) for n in names) + 2

    stopping = threading.Event()
    shutdown_done = threading.Event()

    procs: list[tuple[str, subprocess.Popen[str]]] = []
    for name, argv in services:
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, bufsize=1)
        procs.append((name, proc))
        threading.Thread(target=_relay, args=(name, proc, width), daemon=True).start()

    print(f"\nmomentum: {', '.join(n for n, _ in services)} running — "
          f"open http://{args.host}:{args.port}/   (Ctrl-C to stop)\n", flush=True)

    # Cache-aware snapshot refresh: once on startup, then every interval (if set).
    def _refresh_loop() -> None:
        first = True
        while not stopping.is_set():
            _refresh_snapshots(force=args.fresh and first, width=width, stopping=stopping)
            first = False
            if args.snapshot_interval <= 0:
                return
            stopping.wait(args.snapshot_interval)

    if args.snapshots and not args.web_only:
        threading.Thread(target=_refresh_loop, daemon=True).start()

    def shutdown() -> None:
        if shutdown_done.is_set():
            return
        shutdown_done.set()
        for _, proc in procs:
            if proc.poll() is None:
                proc.terminate()
        deadline = time.time() + 8
        for _, proc in procs:
            try:
                proc.wait(timeout=max(0.0, deadline - time.time()))
            except subprocess.TimeoutExpired:
                proc.kill()

    def _on_signal(*_: Any) -> None:
        if not stopping.is_set():
            print("\nmomentum: stopping…", flush=True)
        stopping.set()

    signal.signal(signal.SIGINT, _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)

    exit_code = 0
    while not stopping.is_set():
        for name, proc in procs:
            rc = proc.poll()
            if rc is not None:
                print(f"\n[{name}] exited ({rc}); shutting down the rest.", flush=True)
                exit_code = rc or 0
                stopping.set()
                break
        stopping.wait(0.3)
    shutdown()
    return exit_code


def _parser(mode: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog=f"momentum-{mode}" if mode != "up" else "momentum-up",
        description={
            "dev": "Dev: web (--reload) + worker + cache-aware bbterminal refresh, one command.",
            "prod": "Prod: web + worker + cache-aware bbterminal refresh, one command.",
            "up": "Bare supervisor for the momentum stack (compose flags yourself).",
        }[mode],
    )
    bool_opt = argparse.BooleanOptionalAction
    p.add_argument("--reload", action=bool_opt, help="auto-restart the web UI on code edits")
    p.add_argument("--worker", action=bool_opt, help="run the trade worker alongside the UI")
    p.add_argument("--snapshots", action=bool_opt,
                   help="refresh data/*.json from bbterminal on startup when stale (TTL)")
    p.add_argument("--web-only", action="store_true",
                   help="only the read-only UI — no worker, no refresh, no creds needed")
    p.add_argument("--fresh", action="store_true", help="ignore the cache TTL and refresh now")
    p.add_argument("--snapshot-interval", type=float, default=0.0,
                   help="also refresh every N seconds in the background (0 = startup only)")
    p.add_argument("--host", default=os.environ.get("MOMENTUM_WEB_HOST", "127.0.0.1"))
    p.add_argument("--port", default=os.environ.get("MOMENTUM_WEB_PORT", "8800"))
    p.add_argument("--poll", type=float, default=5.0, help="worker poll interval (s)")
    # Per-mode defaults (users can still override any with the flags above).
    defaults = {
        "up":   {"reload": False, "worker": True, "snapshots": False},
        "dev":  {"reload": True,  "worker": True, "snapshots": True},
        "prod": {"reload": False, "worker": True, "snapshots": True},
    }[mode]
    p.set_defaults(**defaults)
    return p


def _main(mode: str) -> int:
    args = _parser(mode).parse_args()
    if args.web_only:
        args.worker = False
        args.snapshots = False
    return _run(args)


def main() -> int:   # momentum-up
    return _main("up")


def dev() -> int:    # momentum-dev
    return _main("dev")


def prod() -> int:   # momentum-prod
    return _main("prod")


if __name__ == "__main__":
    raise SystemExit(main())
