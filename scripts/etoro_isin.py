"""Best-effort, FREE ISIN enrichment for an eToro universe JSON.

eToro publishes no ISIN and OpenFIGI can't derive one from a ticker, so there is
no clean source. This does the honest best-effort thing:

  source    = Business Insider's ticker-suggest endpoint (what yfinance's
              ``.isin`` wraps, but hit DIRECTLY so it needs no Yahoo crumb and
              won't rate-limit into oblivion on a bulk run). It returns every
              listing that matches the query, each with its own ticker + ISIN —
              including cross-listings (e.g. ASML: the Amsterdam ordinary
              NL0010273215, the NY registered line, and the Argentine CEDEAR).
  select    = we know each row's eToro exchange, so pick the candidate whose
              ISIN country matches the listing venue, tie-broken by ticker. That
              resolves the ordinary-vs-ADR/CEDEAR ambiguity a blind lookup gets
              wrong.
  verify    = OpenFIGI ISIN->ticker (free, authoritative, the one direction it
              supports) as a final gate: keep the chosen ISIN only if OpenFIGI
              maps it back to a ticker matching the row's base symbol.

Trades recall for precision: a written ISIN has been round-trip confirmed;
everything unconfirmed stays ``null``. Crypto is skipped (no ISIN). Internal /
unmapped rows (no ``yf``) are skipped.

    uv run python scripts/etoro_isin.py                       # cache-fill the default mapping file
    uv run python scripts/etoro_isin.py --limit 40 --sample   # quick precision smoke test
    uv run python scripts/etoro_isin.py --write               # merge verified ISINs back into the JSON
    uv run python scripts/etoro_isin.py --target data/universe_backtest.json --write

Progress + candidates are cached in ``data/isin_cache.json`` keyed by yf ticker,
so reruns only do the outstanding work. An ``OPENFIGI_API_KEY`` env var lifts the
OpenFIGI rate limit (100 jobs/request, higher rpm) — strongly recommended.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

from etoro_yfinance.web.data import data_dir  # noqa: E402

_OPENFIGI_URL = "https://api.openfigi.com/v3/mapping"
_BI_URL = "https://markets.businessinsider.com/ajax/SearchController_Suggest"
_SKIP_TYPES = {"Crypto"}  # no ISIN for coins

# eToro exchange name -> ISIN country prefix of the listing's home line. Used to
# disambiguate cross-listings (pick the venue's own ISIN, not a foreign DR).
_EXCH_COUNTRY = {
    "Nasdaq": "US", "NYSE": "US", "OTC Markets Stock Exchange": "US",
    "Chicago Board Options Exchange": "US", "Regular Trading Hours - RTH": "US",
    "FRA": "DE", "Xetra ETFs": "DE",
    "LSE": "GB", "LSE_AIM": "GB", "LSE AIM Auction": "GB", "LSE Auction": "GB",
    "Euronext Paris": "FR", "Bolsa De Madrid": "ES", "Borsa Italiana": "IT",
    "SIX": "CH", "TYO": "JP", "Tokyo Stock Exchange": "JP",
    "Oslo Stock Exchange": "NO", "Stockholm  Stock Exchange": "SE",
    "Copenhagen Stock Exchange": "DK", "Helsinki Stock Exchange": "FI",
    "Toronto Stock Exchange": "CA", "TSX Venture Exchange": "CA",
    "Hong Kong Exchanges": "HK", "Euronext Lisbon": "PT", "Euronext Brussels": "BE",
    "Tadawul": "SA", "Euronext Amsterdam": "NL", "Sydney": "AU", "Vienna": "AT",
    "Dublin EN": "IE", "Prague SE": "CZ", "Warsaw": "PL", "Budapest": "HU",
    "Dubai Financial Market": "AE", "Abu Dhabi": "AE",
    "Shenzen Stock Exchange": "CN", "Shanghai Stock Exchange": "CN",
    "National Stock Exchange of India": "IN", "Singapore Exchange": "SG",
    "Nasdaq Iceland": "IS", "Nasdaq Tallinn": "EE", "Nasdaq Vilnius": "LT",
    "Nasdaq Riga": "LV", "Korea Exchange": "KR", "Taiwan Stock Exchange": "TW",
}

_CACHE_SCHEMA = 2  # bump to invalidate stale caches (v1 = yfinance-sourced)


def _cache_path() -> Path:
    return data_dir() / "isin_cache.json"


def _load_cache() -> dict[str, dict]:
    p = _cache_path()
    if not p.exists():
        return {}
    doc = json.loads(p.read_text())
    if doc.get("_schema") != _CACHE_SCHEMA:  # old schema -> start fresh
        return {}
    return doc.get("rows", {})


def _save_cache(cache: dict[str, dict]) -> None:
    _cache_path().write_text(json.dumps({"_schema": _CACHE_SCHEMA, "rows": cache}, indent=0))


# ---- ISIN validation -------------------------------------------------------


def valid_isin(code: str) -> bool:
    """12 chars, 2-letter country + 9 alnum + check digit (ISO 6166 Luhn)."""
    if not code or len(code) != 12 or not code[:2].isalpha() or not code[2:].isalnum():
        return False
    digits = "".join(str(int(c, 36)) for c in code[:11].upper())  # letters -> 10..35
    total, dbl = 0, True  # double from the rightmost body digit inward
    for ch in reversed(digits):
        d = int(ch) * (2 if dbl else 1)
        total += d - 9 if d > 9 else d
        dbl = not dbl
    return (10 - total % 10) % 10 == int(code[11])


def _base_symbol(yf_ticker: str) -> str:
    """AAPL -> AAPL, ASML.AS -> ASML, BRK-B -> BRKB, RDS-A -> RDSA."""
    return yf_ticker.split(".")[0].replace("-", "").upper()


# ---- Business Insider candidates ------------------------------------------

# mmSuggestDeliver(0, new Array(headers...), new Array(new Array("Name","Cat",
# "TICKER|ISIN|...", "bias", "ext", "ids"), ...))
_ROW_RE = re.compile(
    r'new Array\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"'
)
_ISIN_RE = re.compile(r"\b([A-Z]{2}[A-Z0-9]{9}[0-9])\b")


def _bi_candidates(symbol: str, client: httpx.Client, retries: int = 3) -> list[dict] | None:
    """Every BI hit for a query: {name, ticker, isin} (valid ISINs only).
    Returns None on a fetch failure (throttle/network) so the caller can leave
    the row uncached and retry it on a later run — vs [] for 'looked, found
    nothing'. BI soft-blocks the IP with 406 after a burst; back off and retry a
    few times, then give up (and stay uncached)."""
    text = None
    for attempt in range(retries + 1):
        last = attempt == retries  # no sleep after the final attempt — fail fast
        try:
            r = client.get(_BI_URL, params={"max_results": 20, "query": symbol}, timeout=20)
        except Exception:
            if last:
                return None
            time.sleep(2 * (attempt + 1))
            continue
        if r.status_code == 200:
            text = r.text
            break
        if r.status_code in (403, 406, 429) or r.status_code >= 500:  # soft block / transient
            if last:
                return None
            time.sleep(15 * (attempt + 1))
            continue
        return None  # hard non-200 (e.g. 404) — nothing to find
    if text is None:
        return None
    out: list[dict] = []
    for name, _category, keywords in _ROW_RE.findall(text):
        if name == "Name" or not keywords:  # header row / no identifiers
            continue
        m = _ISIN_RE.search(keywords)
        if not m or not valid_isin(m.group(1)):
            continue
        out.append({"name": name, "ticker": keywords.split("|", 1)[0], "isin": m.group(1)})
    return out


def _name_key(s: str) -> str:
    """Leading word of a name, alnum-normalized: 'ASML NV' -> 'asml'."""
    parts = (s or "").lower().split()
    return re.sub(r"[^a-z0-9]", "", parts[0]) if parts else ""


def _choose(cands: list[dict], base: str, country: str | None, name: str = "") -> dict | None:
    """Pick the right listing. An ISIN is issuer-domicile-based and
    venue-independent for ordinaries (nVent trades NYSE on an IE ISIN), so an
    exact ticker match is the strongest signal for 'right company'. Country only
    disambiguates *cross-listings of the same company* (ASML's NL ordinary vs its
    US registered line vs its AR CEDEAR)."""
    valid = [c for c in cands if valid_isin(c["isin"])]
    if not valid:
        return None
    tmatch = [c for c in valid if c["ticker"].replace("-", "").upper() == base]
    if country:
        # 1. exact ticker AND listing-country ISIN — unambiguous.
        tc = [c for c in tmatch if c["isin"][:2] == country]
        if tc:
            return {**tc[0], "conf": "ticker+country"}
        # 2. home line whose ticker differs but whose name + country match
        #    (ASML.AS -> 'ASML NV' / ASMLF / NL0010273215).
        key = _name_key(name)
        if key:
            nc = [
                c for c in valid
                if c["isin"][:2] == country and _name_key(c["name"]).startswith(key)
            ]
            if nc:
                return {**nc[0], "conf": "name+country"}
    # 3. exact ticker, any country — right company, foreign domicile.
    if tmatch:
        return {**tmatch[0], "conf": "ticker"}
    # 4. a same-country candidate with nothing else to anchor on (BI ranks by
    #    relevance, so the first is usually right — but flag the lower confidence).
    if country:
        cc = [c for c in valid if c["isin"][:2] == country]
        if cc:
            return {**cc[0], "conf": "country?"}
    return None


# ---- OpenFIGI verification -------------------------------------------------


def _openfigi_map(isins: list[str], api_key: str | None) -> dict[str, list[dict]]:
    """ISIN -> OpenFIGI records. Batches under the tier's job cap."""
    headers = {"X-OPENFIGI-APIKEY": api_key} if api_key else {}
    batch = 100 if api_key else 10
    sleep = 0.3 if api_key else 2.6
    out: dict[str, list[dict]] = {}
    for i in range(0, len(isins), batch):
        chunk = isins[i : i + batch]
        jobs = [{"idType": "ID_ISIN", "idValue": v} for v in chunk]
        for attempt in range(4):
            r = httpx.post(_OPENFIGI_URL, json=jobs, headers=headers, timeout=30)
            if r.status_code == 429:
                time.sleep(8 * (attempt + 1))
                continue
            r.raise_for_status()
            break
        else:
            raise RuntimeError("OpenFIGI kept rate-limiting; supply OPENFIGI_API_KEY")
        for isin, res in zip(chunk, r.json(), strict=False):
            out[isin] = res.get("data") or []
        if i + batch < len(isins):
            time.sleep(sleep)
    return out


def _verify(candidate: str, base: str, records: list[dict]) -> bool:
    """True iff some OpenFIGI record's ticker base-matches the yf base symbol."""
    for rec in records:
        tkr = (rec.get("ticker") or "").replace("/", "").replace("-", "").upper()
        if tkr and (tkr == base or tkr.startswith(base) or base.startswith(tkr)):
            return True
    return False


# ---- driver ----------------------------------------------------------------


def _bi_alive(client: httpx.Client) -> bool:
    try:
        r = client.get(_BI_URL, params={"max_results": 1, "query": "AAPL"}, timeout=15)
        return r.status_code == 200
    except Exception:
        return False


def _crawl_fetch(pending: list[dict], cache: dict, work, headers: dict) -> None:
    """Patient single-threaded crawl for the free BI source, which soft-blocks
    the IP with 406 after a burst. Fetch fast (retries=0) until failures cluster,
    then probe every 30s until the block clears, then resume. Saves as it goes —
    Ctrl-C / kill and rerun resumes from the cache."""
    total = len(pending)
    got, consec_fail, i = 0, 0, 0
    with httpx.Client(headers=headers) as client:
        while i < total:
            row = pending[i]
            yft, rec = work(row, client, 0)  # one shot; wave loop handles the wait
            if rec is None:
                consec_fail += 1
                if consec_fail >= 15:  # cluster of failures — blocked, or just misses?
                    if _bi_alive(client):
                        consec_fail = 0  # BI answers — these were genuine no-data rows
                        i += 1
                        continue
                    _save_cache(cache)
                    print(f"  BI blocked at {got}/{total} done — waiting for unblock…",
                          file=sys.stderr)
                    waited = 0
                    while not _bi_alive(client):
                        time.sleep(30)
                        waited += 30
                        if waited % 120 == 0:
                            print(f"    still blocked after {waited}s…", file=sys.stderr)
                    print(f"  unblocked after ~{waited}s, resuming", file=sys.stderr)
                    i = max(0, i - (consec_fail - 1))  # retry rows skipped during the block
                    consec_fail = 0
                    continue
                i += 1  # isolated failure (genuine 404-ish) — skip on
                continue
            cache[yft] = rec
            consec_fail = 0
            got += 1
            i += 1
            if got % 100 == 0:
                _save_cache(cache)
                print(f"  BI {got}/{total} fetched", file=sys.stderr)
    _save_cache(cache)
    print(f"  BI crawl done: {got}/{total} fetched", file=sys.stderr)


def _load_rows(target: Path) -> tuple[dict | list, list[dict]]:
    doc = json.loads(target.read_text())
    if isinstance(doc, dict) and "rows" in doc:
        return doc, doc["rows"]
    if isinstance(doc, dict) and "instruments" in doc:
        return doc, doc["instruments"]
    return doc, doc  # bare list


def run(
    target: Path, *, write: bool, limit: int | None, sample: bool, workers: int,
    crawl: bool, no_fetch: bool = False,
) -> None:
    api_key = os.getenv("OPENFIGI_API_KEY")
    cache = _load_cache()
    doc, rows = _load_rows(target)

    todo = [r for r in rows if r.get("yf") and r.get("type") not in _SKIP_TYPES]
    if sample:  # spread the smoke test across the file, not just the mega-caps
        step = max(1, len(todo) // (limit or 40))
        todo = todo[::step]
    if limit:
        todo = todo[:limit]

    # 1) Business Insider candidates (cache miss only).
    pending = [] if no_fetch else [r for r in todo if r["yf"] not in cache]
    print(f"{len(todo)} eligible rows · {len(pending)} need a BI lookup", file=sys.stderr)
    headers = {"User-Agent": "Mozilla/5.0 (compatible; isin-enrich/1.0)"}

    def work(row: dict, client: httpx.Client, retries: int) -> tuple[str, dict | None]:
        base = _base_symbol(row["yf"])
        country = _EXCH_COUNTRY.get(row.get("exchange") or "")
        cands = _bi_candidates(base, client, retries=retries)
        if cands is None:  # fetch failed — don't cache, retry next run
            return row["yf"], None
        chosen = _choose(cands, base, country, row.get("name") or "")
        return row["yf"], {
            "chosen": chosen,  # {name,ticker,isin,conf} or None
            "isin": chosen["isin"] if chosen else None,
            "verified": False,
        }

    if crawl:
        _crawl_fetch(pending, cache, work, headers)
    else:
        with httpx.Client(headers=headers) as client, ThreadPoolExecutor(workers) as pool:
            futs = {pool.submit(work, r, client, 3): r["yf"] for r in pending}
            fails = 0
            for n, fut in enumerate(as_completed(futs), 1):
                yft, rec = fut.result()
                if rec is None:
                    fails += 1
                    continue
                cache[yft] = rec
                if n % 200 == 0:
                    _save_cache(cache)
                    print(f"  BI {n}/{len(pending)} ({fails} fails)", file=sys.stderr)
        _save_cache(cache)

    # Rows whose BI fetch failed (throttle) never made it into the cache — they
    # get retried on the next run. Everything below tolerates their absence.
    done = sum(1 for r in todo if r["yf"] in cache)
    missing = len(todo) - done
    if missing:
        print(f"{missing}/{len(todo)} rows uncached (BI throttle) — rerun to fill", file=sys.stderr)

    # 2) OpenFIGI-verify chosen ISINs we haven't confirmed yet.
    to_verify = {
        r["yf"]: cache[r["yf"]]["isin"]
        for r in todo
        if r["yf"] in cache and cache[r["yf"]]["isin"] and not cache[r["yf"]]["verified"]
    }
    uniq = sorted(set(to_verify.values()))
    print(f"{len(uniq)} distinct chosen ISINs to verify via OpenFIGI", file=sys.stderr)
    figi = _openfigi_map(uniq, api_key) if uniq else {}
    for yft, isin in to_verify.items():
        cache[yft]["verified"] = _verify(isin, _base_symbol(yft), figi.get(isin, []))
    _save_cache(cache)

    # 3) report.
    chosen_n = sum(1 for r in todo if r["yf"] in cache and cache[r["yf"]]["isin"])
    have = sum(1 for r in todo if r["yf"] in cache and cache[r["yf"]]["verified"])
    print(
        f"\nverified ISIN: {have}/{len(todo)} eligible "
        f"({chosen_n} chosen, {chosen_n - have} rejected by OpenFIGI)",
        file=sys.stderr,
    )
    if sample:
        for r in todo:
            c = cache.get(r["yf"])
            if not c:
                print(f"  ?? {r['yf']:14} (uncached)")
                continue
            mark = "OK " if c["verified"] else ("x  " if c["isin"] else "-  ")
            ch = c.get("chosen") or {}
            print(f"  {mark}{r['yf']:14} {c['isin'] or '':14} "
                  f"{(ch.get('conf') or ''):8} {ch.get('name') or ''}")

    # 4) optionally merge back into the target JSON.
    if write:
        n = 0
        for r in rows:
            c = cache.get(r.get("yf") or "")
            if c and c["verified"]:
                r["isin"] = c["isin"]
                n += 1
        target.write_text(json.dumps(doc, indent=1))
        print(f"wrote {n} ISINs into {target}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", default=None, help="universe JSON (default: mapping file)")
    ap.add_argument("--write", action="store_true", help="merge verified ISINs into the JSON")
    ap.add_argument("--limit", type=int, default=None, help="cap rows processed")
    ap.add_argument("--sample", action="store_true", help="spread --limit across the file + print")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--crawl", action="store_true",
                    help="patient single-thread crawl that waits out BI's IP block (for a full run)")
    ap.add_argument("--no-fetch", action="store_true",
                    help="skip BI entirely; just verify cached candidates and write")
    args = ap.parse_args()

    target = (
        data_dir() / "etoro_universe_mapping.json" if args.target is None else Path(args.target)
    )
    if not target.exists():
        print(f"no such file: {target}", file=sys.stderr)
        return 2
    run(target, write=args.write, limit=args.limit, sample=args.sample,
        workers=args.workers, crawl=args.crawl, no_fetch=args.no_fetch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
