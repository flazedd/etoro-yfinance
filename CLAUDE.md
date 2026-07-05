# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv run python -m pytest tests/ -q               # full test suite (~1s, keep it green)
uv run python -m pytest tests/test_backtest.py::test_name -q   # single test
uv run ruff check src tests scripts             # lint (line length 100, py311)
uv run momentum-dev                             # web UI with reload → http://127.0.0.1:8800/
uv run python -m etoro_yfinance.web.server --port 8642   # ad-hoc server on another port
uv run python scripts/alpha_lab.py              # signal scoreboard (develop window, ~5 min)
uv run python scripts/alpha_lab.py --placebo    # harness self-test: must admit nothing
uv run python scripts/etoro_universe.py         # rebuild the eToro→yfinance mapping (network)
```

Always run Python via `uv run python` — never bare `python`/`python3`.

## What this repo is

Quant research stack on the eToro tradable universe (~15k instruments mapped to
yfinance tickers): a local Parquet price store, a rebalanced backtester, an
alpha-signal library with a statistical admission battery, and a read-only
FastAPI+HTMX web UI. Trading itself lives only in `scripts/etoro_trade.py`; the
web never touches broker credentials.

## Architecture (the parts that span files)

**Data layer** — `src/etoro_yfinance/prices.py`. Per-ticker Parquet files in
`data/prices/` (native OHLCV) and `data/prices_eur/` (ECB-converted; `volume` =
EUR turnover). `load_prices(ticker, eur=, columns=)` reads only requested
columns. **Always run adjusted closes through `repair_adj_close(df)`**: Yahoo's
adjustment chains are occasionally corrupt (e.g. TELIA1.HE printed a persistent
×14 overnight jump); the repair splices out bars where the adj_close return
diverges ≥×1.8 from the close return while close stays calm. Splits and real
spikes are untouched. `MOMENTUM_DATA_DIR` env var relocates the data dir (tests
use it with tmp stores).

**Universes** — `src/etoro_yfinance/universe.py`. Saved as
`data/universe_<name>.json`; `universe.load(name)["instruments"]` gives rows
with `yf`, `sector`, `type` (Stocks/ETF/Crypto), `spread_pct` (full eToro
spread %). ~91 "sectors" mix GICS-style with ETF category labels. The default
saved universe is `backtest` (~5.1k rows).

**Backtester** — `src/etoro_yfinance/backtest.py::run(rows, start=, end=, …)`.
Monthly/quarterly cutoff grid; at each cutoff only assets with ≥2y of prior
price+volume history are eligible (younger names join as they mature);
benchmark = gross equal-weight of exactly the eligible set. Strategy pays half
the eToro spread per weight actually traded. Loading is windowed to
`[start − 730d − slack, end]` — signals need pre-start history, so never
truncate harder. Selectors live in `STRATEGIES` ("momentum" via
`momentum.py`, "sortino"); overlays compose with any selector: `trend_filter`
(pick below its own 200d mean → its slice sits in cash) and `vol_target`
(inverse-vol weights + book scaled by target/realized vol, capped at 1.0).
Results carry `yearly` (calendar-year returns + nested portfolios) and
`criteria` — a pass/fail checklist against `STABILITY_CRITERIA`
(CAGR ≥ 20%, Sharpe ≥ 1.2, maxDD ≥ −20%, worst full year ≥ −5%, worst rolling
5y CAGR ≥ 10%).

**Alpha lab** — `src/etoro_yfinance/signals.py`. A registry of cross-sectional
signals (`@_register(name, family, sign, description, explanation)`), each with
an a-priori hypothesis; adding a signal is one decorated function over the
`Ctx` matrices (day×name numpy). `evaluate(ctx, start, end)` scores monthly
rank-ICs and admits a signal only through four gates: **C**onfidence
(moving-block-bootstrap p, Benjamini–Hochberg FDR across the whole library),
**T**radability (top-decile edge net of real spreads, long-only),
**R**obustness (right sign ≥60% of years + ≥1 instrument type supports it
alone), **A**rtifact-free (decile monotonicity ≥ 0.6). Advisory columns (never
gate): marginal IC vs the admitted library, timing-dup correlation, lag-2d IC,
trimmed IC, 2×/3× cost curve, liquid-half IC, beta corr, IC trend — summarized
in `flags` (`FLAG_INFO` maps names → 3-char abbr + tooltip text).
`placebo=True` shuffles forward returns and must admit nothing.
`combo_ic` is the family-balanced combination (equal weight *within* family,
then across families — never flat across signals; momentum variants correlate
0.6–0.95).

**Web** — `src/etoro_yfinance/web/`. FastAPI + Jinja2 + HTMX; long jobs
(backtest, alpha-lab scoring) run in a background thread with a shared
in-memory job store polled every 600ms until the result fragment (no
`hx-trigger`) replaces the progress bar. Alpha-lab runs persist to
`data/alphalab/<run_id>.json`; `/alphalab/cached` serves the newest run
matching (universe, window, fdr_q, exact signal set) instantly, and the
per-signal Chart modal reads those files. Charts are TradingView Lightweight
Charts v5 (vendored at `web/static/lightweight-charts.standalone.production.js`
— offline, `chart.addSeries(LWC.LineSeries, …)` API, set
`timeScale.minBarSpacing: 0` or `fitContent()` silently crops long ranges).
The instrument price/volume modal still uses server-rendered SVG
(`web/charts.py`). Generic tooltip: any element with `data-tip` gets a
cursor-following tooltip (JS in `base.html`); `&#10;&#10;` inside the
attribute renders as a blank line (`#tip` is `white-space: pre-line`).

## Research discipline (do not violate)

- **Develop on 2005-01-01→2019-01-01; 2019+ is the held-out validation
  window.** Signals/strategies are tuned on develop only; validate is consulted
  once per candidate, at admission time. Repeatedly checking tweaks against
  2019+ turns it into a second develop set.
- Signal hypotheses (direction + rationale) are declared in code **before**
  evaluation. No hypothesis, no signal.
- Established empirical facts from prior runs (develop window unless noted):
  the only fully validated signal is `sharpe_12_1` (vol-adjusted 12-1 momentum;
  it replicated on 2019+). `rev_1w`/`rev_1m` passed develop but failed
  validation — `rev_1w` is lag-fragile (74% of its IC dies with a 2-day stale
  signal) and was visibly decaying in-sample. Low-vol signals have strong ICs
  but *anti-monotonic* decile returns (unharvestable long-only here). Momentum
  is ~3× stronger in ETFs than stocks; sector momentum works via ETFs, not
  single names; single-name reversal is absent in ETFs (mechanism-consistent).
  Momentum's alpha lives in calm/bull months and dies in bear months.
- The eToro-today universe means **survivorship bias flatters every backtest**;
  results always carry that caveat.

## Gotchas

- `web/static/tailwind.css` is a **precompiled subset** checked into the repo —
  utility classes not already used somewhere may not exist (e.g. `gap-x-5`,
  `h-4`, `opacity-50` are missing). Grep the CSS before using a new class, or
  use inline styles.
- Templates hot-reload; Python does not — restart the server after editing
  `.py` files.
- pytest escalates warnings: an all-NaN slice through `np.nanmean` fails tests.
  Guard with counts/`errstate` (see `signals.py` patterns).
- Equity/price series in the backtest are float32-derived; use `round()` before
  JSON-serializing numpy scalars.
- The synthetic test store (`tests/test_backtest.py::_write_store`) has
  ~0.7%/yr realized vol and all-up drifts — pick test thresholds accordingly.
- Browser verification: no playwright in the project; use system Chrome via
  `puppeteer-core` (headless synthetic mouse events don't reach Lightweight
  Charts — use `page.mouse` trusted input).
