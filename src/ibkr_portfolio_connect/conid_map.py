"""Pinned, human-reviewed bbterminal-company -> IBKR-conid registry.

The rebalancer must never resolve contracts live the morning of a trade — a
symbol search can drift into the wrong instrument, and IBKR's secdef endpoint
503s intermittently. Instead we resolve once (ISIN-first), pin the conid to a
version-controlled file keyed by bbterminal `company_id`, and a human reviews
each entry before it can be traded.

Two operations use this file:
  * sync  (scripts/sync_conid_map.py)  — resolve current holdings, add/update
    entries, flag new/changed ones as unreviewed. Needs IBKR.
  * check (the pre-trade gate)         — verify every current holding has a
    reviewed entry whose conid we can trust. Pure; no IBKR, no drift.

Conids are public reference data, so this file is committed: `git blame` is the
audit trail of who approved which contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

SCHEMA_VERSION = 1
DEFAULT_MAP_PATH = Path("conid_map.json")


class ConidMapError(Exception):
    """A holding can't be traded from the map (missing / unreviewed / drifted)."""


class ConidMapEntry(BaseModel):
    company_id: int
    ticker: str
    company_name: str
    isin: str | None = None
    bbterminal_exchange: str
    currency: str
    conid: int
    ibkr_symbol: str
    ibkr_listing: str
    resolved_via: str  # "isin" | "ticker"
    reviewed: bool = False
    last_resolved: str  # ISO-8601 UTC, stamped by sync


class ConidMap(BaseModel):
    schema_version: int = SCHEMA_VERSION
    strategy_id: int | None = None
    generated_at: str | None = None
    entries: dict[str, ConidMapEntry] = Field(default_factory=dict)

    def get(self, company_id: int) -> ConidMapEntry | None:
        return self.entries.get(str(company_id))

    def put(self, entry: ConidMapEntry) -> None:
        self.entries[str(entry.company_id)] = entry


def load_map(path: Path = DEFAULT_MAP_PATH) -> ConidMap:
    """Load the map, or return an empty one if the file doesn't exist yet."""
    if not path.exists():
        return ConidMap()
    return ConidMap.model_validate_json(path.read_text())


def save_map(m: ConidMap, path: Path = DEFAULT_MAP_PATH) -> None:
    path.write_text(json.dumps(m.model_dump(mode="json"), indent=2) + "\n")


def classify(existing: ConidMapEntry | None, new_conid: int) -> str:
    """Compare a freshly resolved conid against what's on file.

    "added"     — company_id not seen before
    "changed"   — same company, but the conid moved (corporate action / fix);
                  must be re-reviewed before trading
    "unchanged" — conid identical to the reviewed entry
    """
    if existing is None:
        return "added"
    if existing.conid != new_conid:
        return "changed"
    return "unchanged"


def require_reviewed_conid(
    m: ConidMap, company_id: int, *, expected_isin: str | None = None
) -> int:
    """Return the pinned conid for a holding, or raise if it can't be trusted.

    This is the pre-trade gate: a holding is only tradeable if it has an entry
    that a human has marked `reviewed` and whose ISIN still matches what
    bbterminal reports (guards against a company_id being silently repointed).
    """
    entry = m.get(company_id)
    if entry is None:
        raise ConidMapError(
            f"company_id {company_id} is not in the conid map — run "
            "scripts/sync_conid_map.py and review it"
        )
    if not entry.reviewed:
        raise ConidMapError(
            f"{entry.ticker} (company_id {company_id}) is in the map but not "
            "reviewed — approve it before trading"
        )
    if expected_isin and entry.isin and expected_isin != entry.isin:
        raise ConidMapError(
            f"{entry.ticker} (company_id {company_id}) ISIN drift: map has "
            f"{entry.isin}, bbterminal now reports {expected_isin} — re-sync + review"
        )
    return entry.conid


def make_entry(
    holding: dict[str, Any],
    *,
    conid: int,
    ibkr_symbol: str,
    ibkr_listing: str,
    resolved_via: str,
    reviewed: bool,
    now: str,
) -> ConidMapEntry:
    """Build an entry from a bbterminal holding + its resolved IBKR contract."""
    return ConidMapEntry(
        company_id=int(holding["company_id"]),
        ticker=str(holding.get("ticker", "")),
        company_name=str(holding.get("company_name", "")),
        isin=(str(holding["isin"]) if holding.get("isin") else None),
        bbterminal_exchange=str(holding.get("exchange", "")),
        currency=str(holding.get("currency", "")),
        conid=conid,
        ibkr_symbol=ibkr_symbol,
        ibkr_listing=ibkr_listing,
        resolved_via=resolved_via,
        reviewed=reviewed,
        last_resolved=now,
    )
