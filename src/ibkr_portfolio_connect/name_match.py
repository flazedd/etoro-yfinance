"""Company-name similarity for verifying a bbterminal->IBKR conid mapping.

The resolver picks a conid; this scores whether IBKR's *name* for that conid is
the same company bbterminal named. It's the orthogonal signal that catches a
wrong ISIN in bbterminal (e.g. an ISIN that actually belongs to SM Energy being
labelled "SM Investments") — a case ISIN-matching alone can never catch.

Pure stdlib (difflib), so it's cheap and unit-testable offline.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

# Legal-form / boilerplate tokens that carry no identity. Dropped from both
# sides before token comparison so "Diageo PLC" == "DIAGEO PLC-SPONSORED ADR".
_NOISE = {
    "THE", "AND", "CO", "COMPANY", "CORP", "CORPORATION", "INC", "INCORPORATED",
    "LTD", "LIMITED", "LLC", "PLC", "AG", "SA", "SE", "NV", "AB", "ASA", "OYJ",
    "SPA", "BV", "GMBH", "KGAA", "AS", "OY", "PT", "TBK", "BHD", "PCL",
    "GROUP", "GRP", "HOLDING", "HOLDINGS", "HLDGS", "HLDG",
    "SPONSORED", "UNSPONSORED", "ADR", "ADS", "GDR", "REG", "REGISTERED",
    "SHS", "SHARES", "SHARE", "CLASS", "CL", "SERIES", "SER", "NPV", "NEW",
    "COMMON", "STOCK", "ORD", "ORDINARY", "REIT", "TRUST", "RESTRICTED",
}
# Common cross-language equivalences so e.g. a German "n"/class suffix or an
# accent doesn't sink the score. Kept tiny on purpose.
_FOLD = str.maketrans("ÀÁÂÄÃÅÇÈÉÊËÌÍÎÏÑÒÓÔÖÕÙÚÛÜÝ", "AAAAAACEEEEIIIINOOOOOUUUUY")


# Common ticker-style abbreviations IBKR/Bloomberg use that mean the same word —
# expanded so "EDISON INTL" matches "EDISON INTERNATIONAL".
_SYN = {
    "INTL": "INTERNATIONAL", "INTERNAT": "INTERNATIONAL", "NATL": "NATIONAL",
    "FINL": "FINANCIAL", "MGMT": "MANAGEMENT", "SVCS": "SERVICES", "SVC": "SERVICE",
    "MFG": "MANUFACTURING", "PHARM": "PHARMACEUTICAL", "TELECOM": "TELECOMMUNICATIONS",
    "CHEM": "CHEMICAL", "IND": "INDUSTRIES", "INDS": "INDUSTRIES",
}


def normalize(name: str) -> str:
    """Uppercase, de-accent, &->AND, strip punctuation, expand common
    abbreviations -> canonical string."""
    s = (name or "").upper().translate(_FOLD).replace("&", " AND ")
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    s = " ".join(_SYN.get(w, w) for w in s.split())
    return re.sub(r"\s+", " ", s).strip()


def _ordered_tokens(name: str) -> list[str]:
    return [t for t in normalize(name).split() if t and t not in _NOISE]


def _tokens(name: str) -> set[str]:
    return set(_ordered_tokens(name))


def _compact(name: str) -> str:
    """Identity tokens concatenated, order preserved — so spacing / punctuation /
    word-segmentation differences vanish. "MC DONALD'S-CORP" and "McDonald's Corp"
    both compact to "MCDONALDS" (CORP is noise)."""
    return "".join(_ordered_tokens(name))


def _overlap(ta: set[str], tb: set[str]) -> int:
    """Count identity tokens shared by both names, treating one token as a
    prefix of the other (len>=4) as a match so "CHEM" == "CHEMICAL"."""
    used: set[str] = set()
    matched = 0
    for x in ta:
        for y in tb:
            if y in used:
                continue
            if x == y or (len(x) >= 4 and len(y) >= 4 and (x.startswith(y) or y.startswith(x))):
                matched += 1
                used.add(y)
                break
    return matched


def similarity(a: str, b: str) -> float:
    """0..1 confidence that names `a` and `b` are the same company.

    Token evidence dominates: when both names carry >=2 identity tokens, a
    character-level ratio can't rescue a token disagreement (so "SM Investments"
    vs "SM Energy" stays low). For single-token names ("ROCHE") the char ratio
    is the reliable signal. A containment bonus rewards subset names
    ("ROCHE" vs "ROCHE HOLDING").
    """
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return 0.0
    # Spacing/punctuation/segmentation-only difference: the de-spaced identity
    # strings are identical (or one is a prefix of the other = subset name).
    # "MC DONALD'S-CORP" vs "McDonald's Corp" -> both "MCDONALDS".
    ca, cb = _compact(a), _compact(b)
    if ca and cb:
        if ca == cb:
            return 1.0
        if len(ca) >= 6 and len(cb) >= 6 and (ca.startswith(cb) or cb.startswith(ca)):
            return 0.95
    seq = SequenceMatcher(None, na, nb).ratio()
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return seq
    matched = _overlap(ta, tb)
    jac = matched / (len(ta) + len(tb) - matched) if matched else 0.0
    containment = matched / min(len(ta), len(tb))  # subset -> 1.0
    token_score = max(jac, 0.9 * containment)
    if len(ta) >= 2 and len(tb) >= 2:
        return max(token_score, 0.5 * seq)  # token disagreement can't be charmed away
    return max(token_score, seq)
