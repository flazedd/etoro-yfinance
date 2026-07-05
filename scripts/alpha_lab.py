"""Alpha lab: score every registered signal on a universe + window.

    uv run python scripts/alpha_lab.py                      # develop window
    uv run python scripts/alpha_lab.py --window validate    # held-out test (use sparingly!)
    uv run python scripts/alpha_lab.py --redundancy         # + correlation between signals

Prints the IC scoreboard with the four-gate admission battery (see
signals.evaluate: FDR-corrected bootstrap confidence, long-only tradability
net of spreads, yearly/asset-class robustness, decile monotonicity), the
family-balanced combo of all signals, and the combo of the admitted ones.
"""

from __future__ import annotations

import argparse
import warnings

from etoro_yfinance import signals, universe

# all-NaN windows are routine for young/stale names; nan-aware ops handle them
warnings.filterwarnings("ignore", category=RuntimeWarning)

WINDOWS = {"develop": ("2005-01-01", "2019-01-01"), "validate": ("2019-01-01", "2026-12-31")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--universe", default="backtest")
    ap.add_argument("--window", choices=list(WINDOWS), default="develop")
    ap.add_argument("--fdr-q", type=float, default=0.10, help="false-discovery rate for the confidence gate")
    ap.add_argument("--redundancy", action="store_true", help="print signal correlations")
    ap.add_argument(
        "--placebo", action="store_true",
        help="harness self-test: shuffle forward returns — the battery must admit nothing",
    )
    args = ap.parse_args()

    start, end = WINDOWS[args.window]
    rows = universe.load(args.universe)["instruments"]
    print(f"universe {args.universe!r} ({len(rows)} rows) · {start} → {end} · loading…")
    ctx = signals.build_context(rows, start, end)
    print(f"{len(ctx.names)} names with data · {len(signals.SIGNALS)} signals"
          + (" · PLACEBO (shuffled returns)" if args.placebo else "") + "\n")

    board = signals.evaluate(ctx, start, end, fdr_q=args.fdr_q, placebo=args.placebo)
    cols = [
        "signal", "family", "sign", "mean_ic", "t_stat", "p_boot", "ic_marginal",
        "spread_net_ann", "spread_net_2x", "yearly_hit", "scope", "ic_lag2", "ic_liquid",
        "ic_trim5", "ic_trend", "beta_corr", "mono", "flags",
        "g_conf", "g_trade", "g_robust", "g_clean", "admitted",
    ]
    board = board.reindex(columns=cols).sort_values(
        ["admitted", "t_stat"],
        ascending=False,
        key=lambda c: c.abs() if c.name == "t_stat" else c.fillna(False),
    )
    board["flags"] = board["flags"].map(
        lambda s: ",".join(signals.FLAG_INFO[f][0] for f in s.split(",") if f)
        if isinstance(s, str)
        else s
    )
    print(board.to_string(index=False))

    admitted = board[board["admitted"].fillna(False)]["signal"].tolist()
    print(f"\nadmitted (all four gates, FDR q={args.fdr_q}): {admitted or '—'}")
    if args.placebo:
        print("placebo verdict:", "CLEAN — nothing admitted" if not admitted else "LEAK — investigate!")
        return 0 if not admitted else 1
    print("combo (all signals):     ", signals.combo_ic(ctx, start, end))
    if admitted:
        print("combo (admitted only):   ", signals.combo_ic(ctx, start, end, admitted))

    if args.redundancy:
        red = signals.redundancy(ctx, start, end)
        pairs = red.stack().sort_values(key=abs, ascending=False)
        print("\nmost-correlated pairs (|rank corr| ≥ 0.6):")
        print(pairs[pairs.abs() >= 0.6].to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
