"""RPi4 system diagnostics for the /diagnostics page — no credentials, no deps.

Everything here reads the local machine only (``/proc``, ``/sys``, ``os``,
``shutil``), so it adds no dependency to the lean web extra and needs no broker
access. On a non-Linux dev box the Linux-only probes (``/proc/meminfo``, the
thermal zone, ``/proc/uptime``) simply return None and the page shows an em dash.

Each metric carries a ``status`` of ok / warn / crit so the template can colour
it and the page can roll the worst one up into an overall health verdict.
"""

from __future__ import annotations

import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

OK, WARN, CRIT = "ok", "warn", "crit"
_RANK = {OK: 0, WARN: 1, CRIT: 2}

# Thresholds (percent used) — RPi4-class box with an SD/SSD card.
DISK_WARN, DISK_CRIT = 80.0, 92.0
MEM_WARN, MEM_CRIT = 85.0, 95.0
TEMP_WARN, TEMP_CRIT = 70.0, 80.0  # Celsius; the Pi throttles around 80-85.


def _pct_status(pct: float, warn: float, crit: float) -> str:
    if pct >= crit:
        return CRIT
    if pct >= warn:
        return WARN
    return OK


def disk(path: str | None = None) -> dict[str, Any]:
    target = path or os.environ.get("MOMENTUM_DATA_DIR", str(Path.cwd()))
    try:
        usage = shutil.disk_usage(target)
    except OSError:
        return {"status": WARN, "available": False, "path": target}
    pct = usage.used / usage.total * 100.0 if usage.total else 0.0
    return {
        "status": _pct_status(pct, DISK_WARN, DISK_CRIT),
        "available": True,
        "path": target,
        "total_gb": usage.total / 1e9,
        "used_gb": usage.used / 1e9,
        "free_gb": usage.free / 1e9,
        "used_pct": pct,
    }


def _meminfo() -> dict[str, int]:
    """Parse /proc/meminfo into kB ints (Linux only)."""
    out: dict[str, int] = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, _, rest = line.partition(":")
            out[key.strip()] = int(rest.strip().split()[0])
    except (OSError, ValueError, IndexError):
        pass
    return out


def memory() -> dict[str, Any]:
    info = _meminfo()
    total_kb = info.get("MemTotal")
    avail_kb = info.get("MemAvailable")
    if not total_kb or avail_kb is None:
        return {"status": OK, "available": False}
    used_kb = total_kb - avail_kb
    pct = used_kb / total_kb * 100.0
    return {
        "status": _pct_status(pct, MEM_WARN, MEM_CRIT),
        "available": True,
        "total_gb": total_kb / 1e6,
        "used_gb": used_kb / 1e6,
        "free_gb": avail_kb / 1e6,
        "used_pct": pct,
    }


def cpu_temp() -> dict[str, Any]:
    """RPi SoC temperature from the thermal zone, in °C."""
    for zone in sorted(Path("/sys/class/thermal").glob("thermal_zone*/temp")):
        try:
            milli = int(zone.read_text().strip())
        except (OSError, ValueError):
            continue
        celsius = milli / 1000.0
        return {"status": _pct_status(celsius, TEMP_WARN, TEMP_CRIT),
                "available": True, "celsius": celsius}
    return {"status": OK, "available": False}


def load() -> dict[str, Any]:
    cores = os.cpu_count() or 1
    try:
        one, five, fifteen = os.getloadavg()
    except (OSError, AttributeError):
        return {"status": OK, "available": False, "cores": cores}
    # >1.0 load-per-core sustained is the warn line; 1.5x is crit.
    per_core = one / cores
    status = CRIT if per_core >= 1.5 else WARN if per_core >= 1.0 else OK
    return {"status": status, "available": True, "cores": cores,
            "one": one, "five": five, "fifteen": fifteen, "per_core": per_core}


def uptime_seconds() -> float | None:
    try:
        return float(Path("/proc/uptime").read_text().split()[0])
    except (OSError, ValueError, IndexError):
        return None


def overall(parts: list[dict[str, Any]]) -> str:
    worst = OK
    for p in parts:
        if _RANK.get(p.get("status", OK), 0) > _RANK[worst]:
            worst = p["status"]
    return worst


def collect(now: float, *, db_path: str | None = None,
            snapshots: dict[str, float | None] | None = None) -> dict[str, Any]:
    """Gather every metric into one dict the template renders directly.

    `now` and any snapshot ages are passed in by the caller (the web layer owns
    the clock and the filesystem lookups) so this stays pure and testable.
    """
    d = disk()
    m = memory()
    t = cpu_temp()
    ld = load()

    db_size_mb = None
    if db_path:
        try:
            db_size_mb = Path(db_path).stat().st_size / 1e6
        except OSError:
            db_size_mb = None

    return {
        "overall": overall([d, m, t, ld]),
        "disk": d,
        "memory": m,
        "temp": t,
        "load": ld,
        "uptime_seconds": uptime_seconds(),
        "host": platform.node(),
        "platform": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "python": sys.version.split()[0],
        "db_size_mb": db_size_mb,
        "snapshots": snapshots or {},
    }
