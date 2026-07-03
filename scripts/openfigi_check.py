"""Resolve ISINs → ticker / FIGI / exchange via OpenFIGI (Bloomberg's free API).

OpenFIGI maps a known ISIN to its security identifiers. (It does NOT go the other
way — you can't get an ISIN from a ticker — which is why the eToro universe is
mapped to yfinance by symbol, not ISIN.) Useful when you already have ISINs and
want their tickers/venues.

    uv run python scripts/openfigi_check.py US0378331005 NL0011821202
    echo "US0378331005" | uv run python scripts/openfigi_check.py -

No API key needed (free tier: ~25 req/min x 10 ISINs per request).
"""

from __future__ import annotations

import json
import sys
import time

import requests

_URL = "https://api.openfigi.com/v3/mapping"
_BATCH = 10           # max jobs/request without an API key
_PER_MIN_SLEEP = 2.6  # stay under the ~25 req/min unauthenticated cap


def map_isins(isins: list[str]) -> dict[str, list[dict]]:
    """ISIN -> list of OpenFIGI records (each with figi/name/ticker/exchCode)."""
    out: dict[str, list[dict]] = {}
    for i in range(0, len(isins), _BATCH):
        chunk = isins[i : i + _BATCH]
        jobs = [{"idType": "ID_ISIN", "idValue": v} for v in chunk]
        r = requests.post(_URL, json=jobs, headers={"Content-Type": "application/json"}, timeout=30)
        if r.status_code == 429:
            time.sleep(8)
            r = requests.post(_URL, json=jobs, headers={"Content-Type": "application/json"}, timeout=30)
        r.raise_for_status()
        for isin, res in zip(chunk, r.json(), strict=False):
            out[isin] = res.get("data") or []
        if i + _BATCH < len(isins):
            time.sleep(_PER_MIN_SLEEP)
    return out


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    isins = [ln.strip() for ln in sys.stdin if ln.strip()] if args == ["-"] else args

    mapped = map_isins(isins)
    for isin in isins:
        recs = mapped.get(isin, [])
        if not recs:
            print(f"{isin}: (no OpenFIGI record)")
            continue
        top = recs[0]
        tickers = sorted({str(d.get("ticker")) for d in recs if d.get("ticker")})
        exch = sorted({str(d.get("exchCode")) for d in recs if d.get("exchCode")})[:8]
        print(f"{isin}: {top.get('name')} | ticker={','.join(tickers)} | "
              f"figi={top.get('figi')} | exch={','.join(exch)}")
    print(f"\n{json.dumps({k: len(v) for k, v in mapped.items()})}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
