"""Mapping snapshot — LEONTEQ universe + ETFs, each linked to its IBKR contract.

The single credentialed job behind the read-only `/mapping` page. It fetches the
LEONTEQ universe (~1500 members) and every ETF from bbterminal, resolves each to
a tradeable IBKR conid, and writes one plain JSON file the web renders. The web
NEVER calls bbterminal or IBKR — it only reads data/mapping_snapshot.json.

    momentum-mapping-snapshot            # fetch + resolve everything + write the snapshot

Resolution is ISIN-first (`resolve_contract` for equities, collision-free and
honoring the reviewed CONID_OVERRIDES; `resolve_etf_tradability` for ETFs).

**Why this is robust about IBKR limits.** IBKR's `secdef/search` rate-limits and
then IP-BLOCKS a fast full sweep (429 Too Many Requests) — that, not missing
listings, is what leaves names "unresolved". So this job:
  * throttles between lookups (MAPPING_THROTTLE_SECONDS, default 0.4s),
  * backs off + retries on a 429, and re-inits the brokerage session on a
    "no bridge" error (secdef/search needs an initialized iserver session),
  * CACHES every resolved ISIN -> conid in data/mapping_conid_cache.json (seeded
    from a prior snapshot), so resolved names are never looked up again — a
    re-run only retries the ones still missing, and repeated runs converge to
    100% without re-hammering IBKR.

Config (env): BBTERMINAL_*/SUPABASE_* (bbterminal), IBKR OAuth (IBind),
MAPPING_UNIVERSE_ID (override), MAPPING_THROTTLE_SECONDS, MOMENTUM_DATA_DIR.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .bbterminal_client import BBTerminalClient
from .config import Settings
from .contract_resolver import (
    ContractResolutionError,
    ResolvedContract,
    resolve_contract,
    resolve_etf_tradability,
)
from .ibkr_client import IBKRClient, IBKRError
from .web.data import gurufocus_url

log = logging.getLogger(__name__)

IBKR_QUOTE = (
    "https://www.interactivebrokers.ie/portal/"
    "?loginType=1&action=ACCT_MGMT_MAIN&clt=0#/quote/{conid}"
)
_CACHE_FILE = "mapping_conid_cache.json"
_CACHE_KEYS = ("conid", "ibkr_symbol", "ibkr_listing", "ibkr_venues", "method")

# Substrings marking a *transient* IBKR error worth retrying (and re-running for)
# rather than a real no-listing verdict: a dropped brokerage session, or a 429.
_SESSION_ERROR_MARKERS = ("no bridge", "brokerage", "please query", "/accounts", "session")
_RATE_LIMIT_MARKERS = ("429", "too many requests")


def _num(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_session_error(msg: str) -> bool:
    m = msg.lower()
    return any(k in m for k in _SESSION_ERROR_MARKERS)


def _is_rate_limit(msg: str) -> bool:
    m = msg.lower()
    return any(k in m for k in _RATE_LIMIT_MARKERS)


def _is_transient(msg: str) -> bool:
    return _is_session_error(msg) or _is_rate_limit(msg)


def discover_universe(bb: BBTerminalClient) -> tuple[int, str]:
    """The universe to map: MAPPING_UNIVERSE_ID env override, else the newest
    frozen universe whose label mentions LEONTEQ. Falls back to id 15."""
    override = os.environ.get("MAPPING_UNIVERSE_ID")
    if override:
        return int(override), ""
    try:
        unis = bb.universes(include_all=True)
    except Exception:
        log.warning("universe discovery failed; defaulting to id 15", exc_info=True)
        return 15, "LEONTEQ"
    leonteq = [u for u in unis if "LEONTEQ" in str(u.get("label", "")).upper()]
    if not leonteq:
        return 15, "LEONTEQ"
    best = max(leonteq, key=lambda u: str(u.get("as_of_date") or u.get("frozen_at") or ""))
    return int(best["universe_id"]), str(best.get("label") or "")


def load_qa(data_dir: Path, slug: str = "leonteq") -> dict[str, dict[str, Any]]:
    """Per-company QA enrichment keyed by company_id (str): name-match confidence,
    ADV, OpenFIGI verdict — from the offline pipeline artifacts, when present."""
    def _read(name: str) -> dict[str, Any]:
        try:
            return dict(json.loads((data_dir / name).read_text()).get("results", {}))
        except (OSError, json.JSONDecodeError, AttributeError):
            return {}

    ver = _read(f"{slug}_mapping_verification.json")
    liq = _read(f"{slug}_liquidity.json")
    fig = _read(f"{slug}_openfigi.json")
    out: dict[str, dict[str, Any]] = {}
    for cid in set(ver) | set(liq) | set(fig):
        v = ver.get(cid, {})
        out[str(cid)] = {
            "confidence": v.get("confidence"),
            "name_score": v.get("name_score"),
            "ticker_match": v.get("ticker_match"),
            "ccy_ok": v.get("ccy_ok"),
            "ibkr_name": v.get("ibkr_name"),
            "adv_eur": _num(liq.get(cid, {}).get("adv_eur")),
            "figi": fig.get(cid, {}).get("verdict"),
        }
    return out


def load_cache(data_dir: Path) -> dict[str, dict[str, Any]]:
    """ISIN -> resolved IBKR fields. Loads data/mapping_conid_cache.json; if it's
    absent, seeds from a prior mapping_snapshot.json's resolved rows so a re-run
    only re-looks-up the names that are still missing."""
    try:
        return {str(k): dict(v) for k, v in json.loads((data_dir / _CACHE_FILE).read_text()).items()}
    except (OSError, json.JSONDecodeError):
        pass
    cache: dict[str, dict[str, Any]] = {}
    try:
        snap = json.loads((data_dir / "mapping_snapshot.json").read_text())
        for r in snap.get("rows", []):
            if r.get("tradable") and r.get("isin") and r.get("conid"):
                cache[str(r["isin"])] = {k: r.get(k) for k in _CACHE_KEYS}
    except (OSError, json.JSONDecodeError):
        pass
    return cache


def save_cache(data_dir: Path, cache: dict[str, dict[str, Any]]) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / _CACHE_FILE).write_text(json.dumps(cache, ensure_ascii=False))


def _apply_resolution(base: dict[str, Any], res: dict[str, Any]) -> dict[str, Any]:
    conid = res.get("conid")
    base.update({
        "status": "resolved", "tradable": True, "conid": conid,
        "ibkr_symbol": res.get("ibkr_symbol"), "ibkr_listing": res.get("ibkr_listing"),
        "ibkr_venues": res.get("ibkr_venues") or [], "method": res.get("method"),
        "note": "", "ibkr_quote_url": IBKR_QUOTE.format(conid=conid) if conid else None,
    })
    return base


def _error_row(base: dict[str, Any], *, method: str, note: str) -> dict[str, Any]:
    base.update({
        "status": "error", "tradable": False, "conid": None, "ibkr_symbol": None,
        "ibkr_listing": None, "ibkr_venues": [], "method": method, "note": note,
        "ibkr_quote_url": None,
    })
    return base


def build_snapshot(
    bb: BBTerminalClient, ibkr: IBKRClient, *, data_dir: Path,
    ignore_cache: bool = False, throttle: float | None = None,
) -> dict[str, Any]:
    """Fetch the universe + ETFs and resolve every one to an IBKR contract,
    reusing the ISIN cache and throttling / backing off to dodge IBKR's 429."""
    universe_id, label = discover_universe(bb)
    members = bb.universe(universe_id).get("members", [])
    etfs = bb.etfs()
    qa = load_qa(data_dir)
    cache = {} if ignore_cache else load_cache(data_dir)
    if throttle is None:
        throttle = float(os.environ.get("MAPPING_THROTTLE_SECONDS", "0.4"))
    log.info("mapping %d members + %d ETFs (universe #%s %r); %d cached ISINs, throttle %.2fs",
             len(members), len(etfs), universe_id, label, len(cache), throttle)

    # secdef/search needs an initialized iserver brokerage session. Prime it once.
    ibkr.init_brokerage_session()

    def _resolve_with_bridge(fn: Any) -> Any:
        """Run a resolver call; re-init the brokerage session on a 'no bridge'
        error and back off on a 429, retrying either. Works for both equities
        (resolve_contract) and ETFs (resolve_etf_tradability)."""
        last: IBKRError | None = None
        for attempt in range(4):
            try:
                return fn()
            except IBKRError as e:
                last, s = e, str(e)
                if attempt < 3 and _is_session_error(s):
                    log.warning("session error; re-initializing brokerage session")
                    ibkr.init_brokerage_session()
                    time.sleep(1.0)
                    continue
                if attempt < 3 and _is_rate_limit(s):
                    backoff = 10.0 * (2 ** attempt)  # 10, 20, 40s
                    log.warning("IBKR 429 rate-limit; backing off %.0fs (attempt %d)", backoff, attempt + 1)
                    time.sleep(backoff)
                    continue
                raise
        raise last or IBKRError("resolve retries exhausted")

    rows: list[dict[str, Any]] = []
    misses = 0

    def _note_miss() -> None:
        nonlocal misses
        misses += 1
        time.sleep(throttle)                       # be gentle only when we hit IBKR
        if misses % 200 == 0:
            save_cache(data_dir, cache)            # checkpoint progress

    # ── equities ──────────────────────────────────────────────────────────────
    for i, m in enumerate(members):
        cid = str(m.get("company_id"))
        q = qa.get(cid, {})
        country, exch, ticker, isin = m.get("country"), m.get("exchange"), m.get("ticker"), m.get("isin")
        base = {
            "kind": "equity", "company_id": m.get("company_id"), "name": m.get("company_name"),
            "isin": isin, "ticker": ticker, "exchange": exch, "country": country,
            "currency": m.get("currency"), "sector": m.get("sector"),
            "confidence": q.get("confidence"), "name_score": q.get("name_score"),
            "adv_eur": q.get("adv_eur"), "figi": q.get("figi"),
            "ticker_match": q.get("ticker_match"), "ccy_ok": q.get("ccy_ok"),
            "gurufocus_url": gurufocus_url(country, exch, ticker),
        }
        if isin and isin in cache:
            rows.append(_apply_resolution(base, cache[isin]))
            continue
        try:
            rc: ResolvedContract = _resolve_with_bridge(
                lambda m=m: resolve_contract(
                    ibkr, m.get("ticker") or "", m.get("exchange") or "",
                    m.get("currency") or "", isin=m.get("isin"),
                )
            )
            res = {"conid": rc.conid, "ibkr_symbol": rc.ibkr_symbol,
                   "ibkr_listing": rc.ibkr_listing, "ibkr_venues": rc.routing_exchanges,
                   "method": rc.method}
            rows.append(_apply_resolution(base, res))
            if isin:
                cache[isin] = res
        except ContractResolutionError as e:
            rows.append(_error_row(base, method="none", note=str(e)))
        except IBKRError as e:
            rows.append(_error_row(base, method="error", note=f"IBKR: {e}"))
        _note_miss()
        if (i + 1) % 100 == 0:
            log.info("… %d/%d equities (%d live lookups so far)", i + 1, len(members), misses)
            try:
                ibkr.tickle()
            except Exception:
                log.debug("tickle failed; ignoring", exc_info=True)

    # ── ETFs ──────────────────────────────────────────────────────────────────
    for etf in etfs:
        isin = str(etf.get("isin") or "")
        ticker, name = str(etf.get("ticker") or ""), str(etf.get("name") or "")
        q = qa.get(str(etf.get("benchmark_id")), {})
        base = {
            "kind": "etf", "company_id": etf.get("benchmark_id"), "name": etf.get("name"),
            "isin": etf.get("isin"), "ticker": etf.get("ticker"), "exchange": None, "country": None,
            "currency": etf.get("currency"), "sector": etf.get("sector") or "ETF",
            "confidence": q.get("confidence"), "name_score": q.get("name_score"),
            "adv_eur": q.get("adv_eur"), "figi": q.get("figi"),
            "ticker_match": q.get("ticker_match"), "ccy_ok": q.get("ccy_ok"),
            "gurufocus_url": "",
        }
        if isin and isin in cache:
            rows.append(_apply_resolution(base, cache[isin]))
            continue
        try:
            trad = _resolve_with_bridge(
                lambda i=isin, t=ticker, n=name: resolve_etf_tradability(ibkr, i, ticker=t, name=n)
            )
        except IBKRError as e:
            rows.append(_error_row(base, method="error", note=f"IBKR: {e}"))
            _note_miss()
            continue
        if trad.tradable and trad.conid is not None:
            res = {"conid": trad.conid, "ibkr_symbol": trad.ibkr_symbol,
                   "ibkr_listing": trad.preferred_listing, "ibkr_venues": trad.ibkr_listings,
                   "method": trad.method}
            base["name_score"] = trad.name_score
            rows.append(_apply_resolution(base, res))
            if isin:
                cache[isin] = res
        else:
            base["name_score"] = trad.name_score
            rows.append(_error_row(base, method=trad.method, note="no IBKR listing for ISIN"))
        _note_miss()

    save_cache(data_dir, cache)
    rows.sort(key=lambda r: (r["kind"], (r["ticker"] or "").upper()))
    return _finalize(rows, universe_id=universe_id, label=label)


def _finalize(rows: list[dict[str, Any]], *, universe_id: int, label: str) -> dict[str, Any]:
    eq = [r for r in rows if r["kind"] == "equity"]
    etf = [r for r in rows if r["kind"] == "etf"]
    tradable = [r for r in rows if r["tradable"]]
    retryable = [r for r in rows if not r["tradable"] and _is_transient(r.get("note", ""))]
    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "universe_id": universe_id,
        "label": label,
        "counts": {
            "total": len(rows), "equities": len(eq), "etfs": len(etf),
            "tradable": len(tradable), "unresolved": len(rows) - len(tradable),
            "retryable": len(retryable),
        },
        "rows": rows,
    }


def write_local(snapshot: dict[str, Any], data_dir: Path | None = None) -> Path:
    data_dir = data_dir or Path(os.environ.get("MOMENTUM_DATA_DIR", "data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    out = data_dir / "mapping_snapshot.json"
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
    return out


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv()
    p = argparse.ArgumentParser(description="Snapshot the LEONTEQ + ETF -> IBKR mapping")
    p.add_argument("--fresh", action="store_true", help="ignore the ISIN cache and re-resolve everything")
    p.add_argument("--throttle", type=float, default=None, help="seconds between IBKR lookups (default 0.4)")
    args = p.parse_args()

    settings = Settings()  # type: ignore[call-arg]  # pydantic-settings reads env
    data_dir = Path(os.environ.get("MOMENTUM_DATA_DIR", "data"))
    bb = BBTerminalClient.from_env()
    with IBKRClient(timeout=settings.http_timeout_seconds) as ibkr:
        snapshot = build_snapshot(bb, ibkr, data_dir=data_dir,
                                  ignore_cache=args.fresh, throttle=args.throttle)

    out = write_local(snapshot, data_dir)
    c = snapshot["counts"]
    tail = f"; {c['retryable']} hit transient IBKR errors — just re-run to fill them in" if c["retryable"] else ""
    print(
        f"wrote {out} — {c['total']} instruments "
        f"({c['equities']} equities + {c['etfs']} ETFs), "
        f"{c['tradable']} tradable on IBKR, {c['unresolved']} unresolved{tail}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
