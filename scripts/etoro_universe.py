"""Build the eToro-universe → yfinance mapping the web page reads.

Fetches the spot eToro tradable universe (stocks, ETFs, crypto) and maps each
execution instrument to its yfinance analysis ticker (see
etoro_yfinance.to_yfinance). Writes {data_dir}/etoro_universe_mapping.json.

Commodity/Indices/Forex are intentionally excluded: on eToro those are only
tradable as CFDs (futures-based, no spot underlying). See SPOT_TYPES.

    uv run python scripts/etoro_universe.py              # build the mapping
    uv run python scripts/etoro_universe.py --validate   # also live-check yfinance (slow)

No orders; read-only market-data + your eToro key. ISIN is intentionally absent
— eToro doesn't publish it, and OpenFIGI can't derive it from a ticker.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime

from dotenv import load_dotenv

load_dotenv()

from etoro_yfinance.config import Settings  # noqa: E402
from etoro_yfinance.etoro_client import etoro_from_settings  # noqa: E402
from etoro_yfinance.web.data import data_dir  # noqa: E402
from etoro_yfinance.yfinance_map import (  # noqa: E402
    MAPPED_STATUSES,
    TYPE_CRYPTO,
    TYPE_ETF,
    TYPE_STOCKS,
    is_crypto_quote_dupe,
    is_future,
    to_yfinance,
)

# Asset types with a real spot underlying (you own the asset). Everything else
# eToro offers — Commodity, Indices, Forex — is CFD/futures-based only, so we
# leave it out of the universe entirely.
SPOT_TYPES = {"Stocks", "ETF", "Crypto"}


def build(validate: bool, revalidate: bool = False,
          eligibility: bool = False, reeligibility: bool = False,
          spread: bool = False, respread: bool = False) -> dict:
    settings = Settings()  # type: ignore[call-arg]
    with etoro_from_settings(settings) as c:
        ex_by_id = {e["id"]: e["name"] for e in c.exchanges()}
        ty_by_id = {t["id"]: t["name"] for t in c.instrument_types()}
        ind_by_id = c.stocks_industries()   # eToro stock sector taxonomy
        spot_type_ids = [tid for tid, name in ty_by_id.items() if name in SPOT_TYPES]
        universe = c.list_instruments(type_ids=spot_type_ids)

    # ETF fund categories from Yahoo (scripts/etf_categories.py), if built.
    _etf_cat_path = data_dir() / "etf_category_cache.json"
    etf_cat = json.loads(_etf_cat_path.read_text()) if _etf_cat_path.exists() else {}
    # Fallback sectors from Yahoo for instruments eToro left unclassified
    # (scripts/backfill_sectors.py), keyed by yfinance ticker.
    _ovr_path = data_dir() / "sector_override_cache.json"
    sector_override = json.loads(_ovr_path.read_text()) if _ovr_path.exists() else {}

    # All crypto symbols (for the quote-duplicate base check below).
    crypto_syms = {(r["symbol"] or "").upper() for r in universe
                   if r["type_id"] == TYPE_CRYPTO and not r.get("is_internal")}

    rows = []
    for r in universe:
        exch = ex_by_id.get(r["exchange_id"])
        if is_future(r["symbol"], exch):
            continue  # dated futures (CME crypto futures etc.) — spot universe only
        if r["type_id"] == TYPE_CRYPTO and is_crypto_quote_dupe(r["symbol"], crypto_syms):
            continue  # same coin quoted in another currency (BTCEUR vs BTC) — keep USD
        if r.get("is_internal"):
            # eToro synthetic instruments (ETORIAN…, portfolios) — not real tickers.
            yf_t, status = None, "internal"
        else:
            yf_t, status = to_yfinance(symbol=r["symbol"], type_id=r["type_id"], exchange_name=exch)
        # Sector: stocks → eToro industry; crypto → "Crypto"; ETF → Yahoo fund
        # category (eToro's stock taxonomy is meaningless for funds); else None.
        if r["type_id"] == TYPE_STOCKS:
            sector = ind_by_id.get(r.get("stocks_industry_id"))
        elif r["type_id"] == TYPE_CRYPTO:
            sector = "Crypto"
        elif r["type_id"] == TYPE_ETF:
            sector = etf_cat.get(yf_t)
        else:
            sector = None
        if not sector and yf_t:                       # Yahoo fallback for unclassified
            sector = sector_override.get(yf_t)
        rows.append({
            "instrument_id": r["instrument_id"], "symbol": r["symbol"],
            "name": r["name"], "type": ty_by_id.get(r["type_id"]),
            "exchange": exch, "yf": yf_t, "status": status, "sector": sector,
            "isin": None,  # eToro exposes no ISIN
        })

    if validate:
        _validate_yfinance(rows, revalidate=revalidate)

    if eligibility:
        _probe_eligibility(rows, reprobe=reeligibility)

    if spread:
        _probe_spreads(rows, reprobe=respread)

    counts = {
        "total": len(rows),
        "mapped": sum(1 for x in rows if x["status"] in MAPPED_STATUSES),
        "by_status": dict(Counter(x["status"] for x in rows).most_common()),
        "by_type": dict(Counter(x["type"] for x in rows).most_common()),
    }
    if validate:
        mapped = [x for x in rows if x["status"] in MAPPED_STATUSES and x["yf"]]
        counts["validated"] = True
        counts["yf_ok"] = sum(1 for x in mapped if x.get("yf_ok"))
        # Confirmed on Yahoo but missing one series (e.g. price but no volume).
        counts["yf_partial"] = sorted(
            x["yf"] for x in mapped
            if not x.get("yf_ok") and (x.get("yf_price_ok") or x.get("yf_vol_ok")))
        # Neither series seen: dead/delisted ticker OR not yet probed (throttled).
        # Re-run --validate to retry these (cached results are skipped).
        counts["yf_unresolved"] = sorted(
            x["yf"] for x in mapped
            if not x.get("yf_price_ok") and not x.get("yf_vol_ok"))
    if eligibility:
        counts["eligibility_checked"] = True
        counts["tradable"] = sum(1 for x in rows if x.get("tradable"))
        counts["rules_known"] = sum(1 for x in rows if x.get("rules"))
    if spread:
        counts["spread_checked"] = True
        counts["spread_known"] = sum(1 for x in rows if x.get("spread_pct") is not None)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "source": "etoro", "analysis_source": "yfinance",
        "counts": counts, "exchanges": ex_by_id, "rows": rows,
    }


# yfinance/Yahoo validation knobs.
#
# EMPIRICAL FINDING (measured on this universe): Yahoo's throttle is a
# CONCURRENCY limit, not a sequential-rate limit. threads=8 (hundreds of
# in-flight requests) hard-blocks after ~1.5k and won't recover mid-run; but
# strictly SEQUENTIAL requests ran 100% clean at up to ~5/s over 400 consecutive
# probes. So we probe one-at-a-time at a brisk delay and keep the canary/back-off
# only as a safety net for surprises.
#
# yfinance's download() SWALLOWS the throttle (YFRateLimitError -> empty frame),
# and a delisted ticker ALSO returns empty — so empties are ambiguous. The canary
# disambiguates: on a run of empties, probe a known-good ticker; if it works the
# empties are dead tickers (cache them, continue); if it's ALSO empty we're
# throttled (back off + slow down). Progress is cached to disk; runs are resumable.
_YF_RPS = 10.0                             # target rate; real throughput is
_YF_MIN_DELAY = 0.1                        # network-bound to ~4-5/s at this floor
_YF_MAX_DELAY = 5.0                        # ceiling after back-offs (s)
_YF_COOLDOWN = 90                          # base back-off on throttle (s); doubles
_YF_MAX_COOLDOWN = 900
_YF_MAX_THROTTLES = 12                     # abort (resume later) after this many
_YF_CANARY = "AAPL"                        # known-liquid ticker for the canary
_YF_CACHE = "yf_validation_cache.json"     # under data_dir(); persists results


def _yf_probe(yf, ticker: str):
    """One full-history request. PERSISTS the OHLCV to the Parquet store and
    returns what we actually have data-wise: {price_from, price_to, vol_from,
    vol_to, bars} (ISO dates, or None where that series is absent; bars = number
    of daily rows stored). Returns None for the whole dict if the frame is empty
    (throttled or delisted — the caller disambiguates).

    Fetches raw + adjusted with corporate actions (auto_adjust=False, actions=True)
    so the store keeps close, adj_close, dividends and splits."""
    import pandas as pd

    from etoro_yfinance import prices

    try:
        f = yf.download(ticker, period="max", interval="1d", progress=False,
                        threads=False, auto_adjust=False, actions=True)
    except Exception:
        f = None
    if f is None or len(f) == 0:
        return None
    # Single-ticker download can come back with a MultiIndex (field, ticker) or
    # flat columns depending on the yfinance version — flatten to the field level,
    # then drop any duplicate field columns so f[name] is always a 1-D Series.
    if isinstance(f.columns, pd.MultiIndex):
        f = f.copy()
        f.columns = f.columns.get_level_values(0)
    f = f.loc[:, ~f.columns.duplicated()]
    f = prices.drop_unclosed(f)   # exclude today's still-open session bar
    if len(f) == 0:
        return None

    def window(name, positive=False):
        if name not in f.columns:
            return None, None
        col = f[name]
        mask = (col.fillna(0).to_numpy() > 0) if positive else col.notna().to_numpy()
        idx = f.index[mask.ravel()]
        if len(idx) == 0:
            return None, None
        return str(idx.min().date()), str(idx.max().date())

    try:
        price_from, price_to = window("Close")
        vol_from, vol_to = window("Volume", positive=True)
        bars = prices.write_prices(ticker, f)   # persist OHLCV for backtests
    except Exception:
        return None   # unparseable frame shape — treat as empty (canary decides)
    return {"price_from": price_from, "price_to": price_to,
            "vol_from": vol_from, "vol_to": vol_to, "bars": int(bars)}


def _validate_yfinance(rows: list[dict], *, revalidate: bool = False) -> None:
    """Confirm each mapped ticker has BOTH a price and a volume daily series on
    Yahoo (period=1mo). Sets per row: yf_price_ok, yf_vol_ok, yf_ok.

    Adaptive + resumable: probes sequentially, uses a canary to tell a throttle
    from a dead ticker, backs off (and permanently slows) when Yahoo throttles,
    and caches every definitive answer so re-running skips resolved tickers.
    A throttle can never be baked in as a false 'unavailable'."""
    import time

    import yfinance as yf

    cache_path = data_dir() / _YF_CACHE
    cache: dict = {}
    if cache_path.exists() and not revalidate:
        try:
            cache = json.loads(cache_path.read_text())
        except Exception:
            cache = {}

    tickers = sorted({x["yf"] for x in rows if x["yf"]})
    todo = [t for t in tickers if t not in cache]
    print(f"validate: {len(tickers) - len(todo)}/{len(tickers)} cached, "
          f"probing {len(todo)}")

    def save() -> None:
        cache_path.write_text(json.dumps(cache))

    delay = max(_YF_MIN_DELAY, 1.0 / _YF_RPS if _YF_RPS > 0 else 0.0)
    cooldown = _YF_COOLDOWN
    throttles = 0
    t0 = time.time()
    done = 0
    try:
        for t in todo:
            res = _yf_probe(yf, t)
            if res is None:
                # One quick retry guards against a rare single-request hiccup.
                time.sleep(min(delay, 0.5))
                res = _yf_probe(yf, t)
            if res is None:
                # Still empty. Throttle or genuinely delisted? Ask the canary.
                if _yf_probe(yf, _YF_CANARY) is not None:
                    # canary alive => dead (no coverage window at all)
                    res = {"price_from": None, "price_to": None,
                           "vol_from": None, "vol_to": None, "bars": 0}
                else:
                    # Canary also empty => throttled. Back off + slow down.
                    throttles += 1
                    save()
                    new_delay = min(_YF_MAX_DELAY, delay * 1.5)
                    print(f"  THROTTLED (event {throttles}/{_YF_MAX_THROTTLES}) after "
                          f"{done} done in {time.time() - t0:.0f}s — canary empty. "
                          f"cooldown {cooldown}s, delay {delay:.1f}->{new_delay:.1f}s",
                          flush=True)
                    if throttles >= _YF_MAX_THROTTLES:
                        print("  too many throttles; stopping. Re-run to resume.",
                              flush=True)
                        break
                    time.sleep(cooldown)
                    cooldown = min(_YF_MAX_COOLDOWN, cooldown * 2)
                    delay = new_delay
                    continue   # ticker stays uncached -> retried on re-run

            cache[t] = res
            done += 1
            if done % 100 == 0:
                save()
                ok = sum(1 for v in cache.values() if v["price_from"] and v["vol_from"])
                dead = sum(1 for v in cache.values()
                           if not v["price_from"] and not v["vol_from"])
                rate = done / max(time.time() - t0, 1)
                print(f"  {done}/{len(todo)} done · {ok} ok · {dead} dead · "
                      f"~{rate:.2f}/s", flush=True)
            time.sleep(delay)
    finally:
        save()

    for x in rows:
        t = x["yf"]
        c = cache.get(t) if t else None
        for k in ("price_from", "price_to", "vol_from", "vol_to", "bars"):
            x[k] = c.get(k) if c else None
        x["yf_price_ok"] = bool(c and c.get("price_from"))
        x["yf_vol_ok"] = bool(c and c.get("vol_from"))
        x["yf_ok"] = x["yf_price_ok"] and x["yf_vol_ok"]


# eToro trading-eligibility knobs. The endpoint takes <=100 instrument ids/call
# and shares the default 60-req/60s quota (stricter in practice), so we pace
# conservatively and back off on 429 rather than giving up.
_ELIG_CACHE = "eligibility_cache.json"     # under data_dir(); persists per-id rules
_ELIG_BATCH = 100                          # API cap per request
_ELIG_PACE = 1.5                           # seconds between calls (~40/min)
_ELIG_COOLDOWN = 30                        # base back-off (s) on 429; doubles
_ELIG_MAX_COOLDOWN = 300
_ELIG_MAX_RETRIES = 6                      # per-batch 429 retries before skipping


def _probe_eligibility(rows: list[dict], *, reprobe: bool = False) -> None:
    """Fetch each instrument's full trading rule set (position limits, order
    types, SL/TP bounds, leverage) via the eligibility endpoint — NO orders —
    and store it per row as `rules` plus flattened summary fields. Resumable:
    cached ids are skipped; re-run to fill gaps."""
    import time

    from etoro_yfinance import eligibility as elig

    settings = Settings()  # type: ignore[call-arg]
    cache_path = data_dir() / _ELIG_CACHE
    cache: dict = {}
    if cache_path.exists() and not reprobe:
        try:
            cache = json.loads(cache_path.read_text())
        except Exception:
            cache = {}

    ids = [r["instrument_id"] for r in rows if r.get("instrument_id") is not None]
    todo = [i for i in ids if str(i) not in cache]
    print(f"eligibility: {len(ids) - len(todo)}/{len(ids)} cached, probing {len(todo)}")

    def save() -> None:
        cache_path.write_text(json.dumps(cache))

    with etoro_from_settings(settings) as c:
        k = 0
        cooldown = _ELIG_COOLDOWN
        retries = 0
        try:
            while k < len(todo):
                batch = todo[k:k + _ELIG_BATCH]
                try:
                    res = c.eligibility(batch)      # {id: rules}; missing => not returned
                except Exception as e:
                    msg = str(e)
                    if ("429" in msg or "TooManyRequests" in msg) and retries < _ELIG_MAX_RETRIES:
                        retries += 1
                        print(f"  429 at {k} — backing off {cooldown}s "
                              f"(retry {retries}/{_ELIG_MAX_RETRIES})", flush=True)
                        save()
                        time.sleep(cooldown)
                        cooldown = min(_ELIG_MAX_COOLDOWN, cooldown * 2)
                        continue                     # retry the same batch
                    print(f"  stopped: {e}. Re-run to resume.", flush=True)
                    break
                cooldown = _ELIG_COOLDOWN
                retries = 0
                for iid in batch:
                    cache[str(iid)] = res.get(int(iid))  # None marks "checked, none"
                k += _ELIG_BATCH
                if (k // _ELIG_BATCH) % 5 == 0 or k >= len(todo):
                    save()
                    trad = sum(1 for v in cache.values() if v and v.get("allowOpenPosition"))
                    print(f"  {min(k, len(todo))}/{len(todo)} probed · {trad} tradable",
                          flush=True)
                time.sleep(_ELIG_PACE)
        finally:
            save()

    for x in rows:
        iid = x.get("instrument_id")
        e = cache.get(str(iid)) if iid is not None else None
        x["rules"] = e or None
        summ = elig.summarize(e) if e else dict.fromkeys(elig.SUMMARY_KEYS)
        x.update(summ)


# eToro live-rates (spread) knobs. Shared 120-req/60s quota; batch of 100 ids per
# call, paced under the limit, with 429 back-off (mirrors the eligibility probe).
_SPREAD_CACHE = "spread_cache.json"
_SPREAD_BATCH = 100
_SPREAD_PACE = 0.6
_SPREAD_COOLDOWN = 30
_SPREAD_MAX_COOLDOWN = 300
_SPREAD_MAX_RETRIES = 6


def _probe_spreads(rows: list[dict], *, reprobe: bool = False) -> None:
    """Fetch live bid/ask per instrument (no orders) and store spread_pct per row.
    Resumable: cached ids are skipped; re-run to fill gaps."""
    import time

    from etoro_yfinance import liquidity as liq

    settings = Settings()  # type: ignore[call-arg]
    cache_path = data_dir() / _SPREAD_CACHE
    cache: dict = {}
    if cache_path.exists() and not reprobe:
        try:
            cache = json.loads(cache_path.read_text())
        except Exception:
            cache = {}

    ids = [r["instrument_id"] for r in rows if r.get("instrument_id") is not None]
    todo = [i for i in ids if str(i) not in cache]
    print(f"spread: {len(ids) - len(todo)}/{len(ids)} cached, probing {len(todo)}")

    def save() -> None:
        cache_path.write_text(json.dumps(cache))

    with etoro_from_settings(settings) as c:
        k = 0
        cooldown = _SPREAD_COOLDOWN
        retries = 0
        try:
            while k < len(todo):
                batch = todo[k:k + _SPREAD_BATCH]
                try:
                    res = c.market_rates(batch)
                except Exception as e:
                    msg = str(e)
                    if ("429" in msg or "TooManyRequests" in msg) and retries < _SPREAD_MAX_RETRIES:
                        retries += 1
                        print(f"  429 at {k} — backing off {cooldown}s "
                              f"(retry {retries}/{_SPREAD_MAX_RETRIES})", flush=True)
                        save()
                        time.sleep(cooldown)
                        cooldown = min(_SPREAD_MAX_COOLDOWN, cooldown * 2)
                        continue
                    print(f"  stopped: {e}. Re-run to resume.", flush=True)
                    break
                cooldown = _SPREAD_COOLDOWN
                retries = 0
                for iid in batch:
                    r = res.get(int(iid))
                    cache[str(iid)] = ({"bid": r.get("bid"), "ask": r.get("ask"),
                                        "spread_pct": liq.spread_pct(r)} if r else None)
                k += _SPREAD_BATCH
                if (k // _SPREAD_BATCH) % 5 == 0 or k >= len(todo):
                    save()
                    got = sum(1 for v in cache.values() if v and v.get("spread_pct") is not None)
                    print(f"  {min(k, len(todo))}/{len(todo)} probed · {got} with spread",
                          flush=True)
                time.sleep(_SPREAD_PACE)
        finally:
            save()

    for x in rows:
        iid = x.get("instrument_id")
        e = cache.get(str(iid)) if iid is not None else None
        x["spread_pct"] = e.get("spread_pct") if e else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the eToro→yfinance universe mapping.")
    ap.add_argument("--validate", action="store_true",
                    help="live-check yfinance price+volume (slow, rate-limited, resumable)")
    ap.add_argument("--revalidate", action="store_true",
                    help="with --validate: ignore the cache and re-probe every ticker")
    ap.add_argument("--eligibility", action="store_true",
                    help="fetch eToro trading rules per instrument (no orders, resumable)")
    ap.add_argument("--reeligibility", action="store_true",
                    help="with --eligibility: ignore the cache and re-probe every instrument")
    ap.add_argument("--spread", action="store_true",
                    help="fetch eToro live bid/ask spread per instrument (no orders, resumable)")
    ap.add_argument("--respread", action="store_true",
                    help="with --spread: ignore the cache and re-probe every instrument")
    args = ap.parse_args()

    doc = build(args.validate or args.revalidate, revalidate=args.revalidate,
                eligibility=args.eligibility or args.reeligibility,
                reeligibility=args.reeligibility,
                spread=args.spread or args.respread, respread=args.respread)
    out = data_dir() / "etoro_universe_mapping.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1))

    c = doc["counts"]
    print(f"\nwrote {out}")
    print(f"total={c['total']}  mapped={c['mapped']} ({100 * c['mapped'] // max(c['total'], 1)}%)")
    print("by status:", c["by_status"])
    print("by type:  ", c["by_type"])
    if c.get("validated"):
        partial, unresolved = c["yf_partial"], c["yf_unresolved"]
        print(f"yf price+volume ok: {c['yf_ok']}/{c['mapped']}")
        if partial:
            print(f"partial ({len(partial)}, on Yahoo but missing a series): "
                  f"{', '.join(partial[:30])}{' …' if len(partial) > 30 else ''}")
        if unresolved:
            print(f"unresolved ({len(unresolved)}, delisted or not-yet-probed — "
                  f"re-run --validate to retry): "
                  f"{', '.join(unresolved[:30])}{' …' if len(unresolved) > 30 else ''}")
        if not partial and not unresolved:
            print("100% hit rate — every mapped ticker has price + volume.")
    if c.get("eligibility_checked"):
        print(f"eToro tradable: {c['tradable']}/{c['total']} "
              f"(rules known for {c['rules_known']})")
    if c.get("spread_checked"):
        print(f"spread known: {c['spread_known']}/{c['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
