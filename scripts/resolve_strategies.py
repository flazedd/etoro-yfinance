"""Resolve each scheduled strategy's holdings to IBKR contracts + render a view.

The scheduled strategies (MomentumTopSelectie Offensief/Neutraal/Defensief) hold
mostly single stocks that are already in the LEONTEQ universe — those reuse the
universe's ISIN-first resolution (data/leonteq_ibkr_resolution.json), keyed by
company_id, so we don't re-probe IBKR for them.

What's new are a handful of ETFs (Invesco SPMO/DBC/UUP, iShares IAU). They carry
no ISIN and aren't in the universe, and a plain ticker search is unsafe — "IAU"
also matches I-80 Gold Corp (TSE), "DBC" matches a Polish tyre maker (WSE). So we
resolve an ETF by symbol search and pick the row whose IBKR company name actually
matches the holding name, preferring the US listing (ARCA/NASDAQ/NYSE/...).

    uv run python scripts/resolve_strategies.py            # JSON + HTML
    uv run python scripts/resolve_strategies.py --refresh-etf   # re-probe ETFs

Outputs:
  data/strat_<id>_resolution.json   per-strategy resolved holdings
  data/strat_etf_resolution.json    cached ETF -> conid (name-matched)
  data/strategies_review.html       one table per strategy, with IBKR links

Read-only against IBKR (reference data); places no orders.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from ibkr_portfolio_connect import name_match  # noqa: E402

DATA_DIR = Path("data")
STRATS = {18: "offensief", 19: "neutraal", 20: "defensief"}
US_LISTINGS = {"ARCA", "NASDAQ", "NYSE", "BATS", "AMEX", "PINK", "IEX"}
IBKR_QUOTE = (
    "https://www.interactivebrokers.ie/portal/"
    "?loginType=1&action=ACCT_MGMT_MAIN&clt=0#/quote/{conid}"
)
NAME_OK = 0.55  # similarity floor for a confident ETF name match


def _is_etf(h: dict[str, Any]) -> bool:
    return h.get("sector") == "ETF" or (h.get("company_id") or 0) < 0 or not h.get("isin")


def _ibkr_name(row: dict[str, Any]) -> str:
    """companyHeader is 'INVESCO S&P 500 MOMENTUM ETF - ARCA'; drop the venue."""
    header = str(row.get("companyHeader") or "")
    return header.rsplit(" - ", 1)[0].strip() if " - " in header else header


def resolve_etf(client: Any, ticker: str, name: str) -> dict[str, Any]:
    """Pick the IBKR STK row that best matches `name`, preferring a US listing."""
    best: tuple[float, bool, dict[str, Any]] | None = None
    for row in client.secdef_search_raw(ticker):
        if not isinstance(row, dict):
            continue
        secs = {str(s.get("secType", "")).upper() for s in (row.get("sections") or [])}
        if "STK" not in secs:
            continue
        listing = str(row.get("description") or "").upper()
        score = name_match.similarity(name, _ibkr_name(row))
        key = (score, listing in US_LISTINGS, row)
        if best is None or key[:2] > best[:2]:
            best = key
    if best is None:
        return {"status": "not_on_ibkr", "name_score": 0.0}
    score, is_us, row = best
    return {
        "status": "resolved" if score >= NAME_OK else "weak_match",
        "conid": int(row["conid"]),
        "ibkr_symbol": str(row.get("symbol")),
        "ibkr_listing": str(row.get("description") or "").upper(),
        "ibkr_name": _ibkr_name(row),
        "name_score": round(score, 3),
        "us_listing": is_us,
        "method": "etf_name",
    }


def _load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())  # type: ignore[no-any-return]
    except (OSError, json.JSONDecodeError):
        return {}


def build() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh-etf", action="store_true", help="re-probe ETFs (ignore cache)")
    args = ap.parse_args()

    uni_res = _load(DATA_DIR / "leonteq_ibkr_resolution.json").get("results", {})
    verif = _load(DATA_DIR / "leonteq_mapping_verification.json").get("results", {})
    etf_cache = {} if args.refresh_etf else _load(DATA_DIR / "strat_etf_resolution.json")

    client = None
    need_etf = any(
        _is_etf(h) and h["ticker"] not in etf_cache
        for sid, slug in STRATS.items()
        for h in _load(DATA_DIR / f"strat_{sid}_{slug}_schedule.json").get("holdings", [])
    )
    if need_etf:
        from ibkr_portfolio_connect.ibkr_client import IBKRClient

        client = IBKRClient()

    per_strategy: dict[int, dict[str, Any]] = {}
    for sid, slug in STRATS.items():
        sched = _load(DATA_DIR / f"strat_{sid}_{slug}_schedule.json")
        rows: list[dict[str, Any]] = []
        for h in sched.get("holdings", []):
            cid = h.get("company_id")
            row = {
                "company_id": cid,
                "ticker": h.get("ticker"),
                "exchange": h.get("exchange"),
                "currency": h.get("currency"),
                "isin": h.get("isin"),
                "name": h.get("company_name"),
                "sector": h.get("sector"),
                "weight": h.get("target_weight"),
                "is_etf": _is_etf(h),
            }
            if _is_etf(h):
                tk = h["ticker"]
                if tk not in etf_cache:
                    etf_cache[tk] = resolve_etf(client, tk, h.get("company_name") or tk)
                row.update(etf_cache[tk])
            else:
                u = uni_res.get(str(cid)) or uni_res.get(cid) or {}
                v = verif.get(str(cid)) or verif.get(cid) or {}
                row.update(
                    {
                        "status": u.get("status", "pending"),
                        "conid": u.get("conid"),
                        "ibkr_symbol": u.get("ibkr_symbol"),
                        "ibkr_listing": u.get("ibkr_listing"),
                        "method": u.get("method"),
                        "confidence": v.get("confidence"),
                        "name_score": v.get("name_score"),
                    }
                )
            row["ibkr_url"] = IBKR_QUOTE.format(conid=row["conid"]) if row.get("conid") else None
            rows.append(row)
        per_strategy[sid] = {"strategy_id": sid, "name": sched.get("name"), "holdings": rows}
        out = DATA_DIR / f"strat_{sid}_resolution.json"
        out.write_text(json.dumps(per_strategy[sid], indent=2))

    (DATA_DIR / "strat_etf_resolution.json").write_text(json.dumps(etf_cache, indent=2))
    _render_html(per_strategy)

    # console summary
    for sid, s in per_strategy.items():
        hs = s["holdings"]
        res = sum(1 for r in hs if r.get("conid"))
        etfs = [r for r in hs if r["is_etf"]]
        pend = sum(1 for r in hs if r.get("status") == "pending")
        print(
            f"strat {sid} {STRATS[sid]:9} {res}/{len(hs)} have conid"
            f" | {len(etfs)} ETF(s) | {pend} pending (universe sweep)"
        )
        for r in etfs:
            print(
                f"    ETF {r['ticker']:5} -> conid={r.get('conid')} {r.get('ibkr_listing')}"
                f" name_score={r.get('name_score')} ({r.get('status')}) {r.get('ibkr_name')}"
            )
    return 0


def _render_html(per_strategy: dict[int, dict[str, Any]]) -> None:
    def cell(r: dict[str, Any]) -> str:
        tk = html.escape(str(r.get("ticker") or ""))
        nm = html.escape(str(r.get("name") or ""))
        link = (
            f'<a href="{r["ibkr_url"]}" target="_blank">{r["conid"]}</a>'
            if r.get("ibkr_url")
            else '<span class="bad">unresolved</span>'
        )
        badge = "ETF" if r["is_etf"] else (r.get("confidence") or "")
        score = r.get("name_score")
        score_s = "" if score is None else f"{float(score):.2f}"
        weak = r.get("status") in ("weak_match", "pending", "not_on_ibkr", None) and r.get(
            "status"
        ) not in ("resolved",)
        cls = "bad" if weak and not r.get("conid") else ""
        return (
            f'<tr class="{cls}"><td>{tk}</td><td>{nm}</td>'
            f'<td>{html.escape(str(r.get("isin") or "—"))}</td>'
            f'<td>{html.escape(str(r.get("exchange") or "—"))}</td>'
            f'<td>{html.escape(str(r.get("ibkr_listing") or "—"))}</td>'
            f"<td>{link}</td><td>{html.escape(str(badge))}</td><td>{score_s}</td>"
            f'<td>{(r.get("weight") or 0) * 100:.2f}%</td></tr>'
        )

    sections = []
    for sid, s in per_strategy.items():
        body = "".join(cell(r) for r in s["holdings"])
        sections.append(
            f"<h2>#{sid} {html.escape(str(s['name']))} "
            f"<small>({len(s['holdings'])} holdings)</small></h2>"
            "<table><thead><tr><th>Ticker</th><th>Name</th><th>ISIN</th>"
            "<th>bb exch</th><th>IBKR listing</th><th>conid → IBKR</th>"
            "<th>conf</th><th>name</th><th>weight</th></tr></thead>"
            f"<tbody>{body}</tbody></table>"
        )
    page = (
        "<!doctype html><meta charset='utf-8'><title>Strategy holdings → IBKR</title>"
        "<style>body{font:13px system-ui;margin:24px;color:#1e293b}"
        "table{border-collapse:collapse;margin:8px 0 28px;width:100%}"
        "th,td{border-bottom:1px solid #e2e8f0;padding:4px 8px;text-align:left}"
        "th{background:#0f172a;color:#fff;position:sticky;top:0}"
        "tr.bad td{background:#fef2f2}.bad{color:#dc2626}"
        "a{color:#2563eb}h2 small{color:#64748b;font-weight:400}</style>"
        f"<h1>Scheduled strategies → IBKR</h1>{''.join(sections)}"
    )
    (DATA_DIR / "strategies_review.html").write_text(page)


if __name__ == "__main__":
    sys.exit(build())
