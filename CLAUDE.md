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
uv run python scripts/fetch_factors.py          # ingest missing covariance factor proxies (network)
```

Always run Python via `uv run python` — never bare `python`/`python3`.

## Tests: unit tests only

**The suite must stay fast enough to run after every edit (~2s).** Only unit
tests belong in `tests/`: pure functions and small synthetic frames, no network,
no real price store, no web server, no browser, no sleeping. A test that needs
the data on disk is not a unit test — build a tmp store via `MOMENTUM_DATA_DIR`
(see the `data_dir` fixture in `tests/test_prices.py`) or synthesise the few
bars the case needs.

Verify against real data or a running app **ad hoc from the shell**, not by
adding a slow test — that check is for the change you are making now, and the
suite pays its cost forever.

## What this repo is

Quant research stack on the eToro tradable universe (~15k instruments mapped to
yfinance tickers): a local Parquet price store, a rebalanced backtester, an
alpha-signal library with a statistical admission battery, and a read-only
FastAPI+HTMX web UI. Trading itself lives only in `scripts/etoro_trade.py`; the
web never touches broker credentials.

## Architecture (the parts that span files)

**Data layer** — `src/etoro_yfinance/prices.py`. Three per-ticker Parquet
stores, **all floored at `MIN_DATE` = 1999-01-04** (the euro's first ECB fixing,
so the three stores cover the same span):
`data/prices_raw/` (Yahoo as fetched — the record), `data/prices/` =
`clean_frame(raw)` (what research reads), `data/prices_eur/` = `to_eur(clean)`
(ECB-converted; `volume` = EUR turnover). `load_prices(ticker, eur=, raw=,
columns=)` reads only requested columns.

**Quality is enforced at ingestion, not by callers.** `write_prices` fills raw
and clean together; `clean_frame` cuts to `MIN_DATE`, drops Yahoo's *negative*
adjustment factor (BZU.MI stored `adj_close` −95.83 against `close` 4.66, whose
sign flip read as −103%), applies splits Yahoo left out of `adj_close` (GDC's
1:250 landed as +20,650%), nulls bad prints via a two-sided local-median test
(a bar ≥5× from the median *before* **and** *after* it), truncates at
redenominations (a ×100 jump that persists = a reused symbol, e.g. ZETA-USD
0.000060 → 1.6708), and nulls `high`/`low` that contradict `open`/`close`
(~19% of stocks had bars where `close` sat outside the range). `repair_adj_close`
still exists and runs inside `clean_frame`; **stored series never need it
again**. Re-tuning a threshold means `scripts/clean_store.py --apply` (rebuild
clean from raw) then `scripts/build_eur_series.py` — never a re-fetch.

Reverse splits whose `splits` value explains the jump are deliberately left
alone (PPCB's 1:2 stamped on a ×62,500 bar does *not* explain it, so that one
is treated as a redenomination).

**Instrument admission** — `rejection_reason(df)` drops whole series rather
than repairing bars, so they exist in `prices_raw/` but in neither other store:
`frozen` (≥ `MAX_FROZEN_RUN` = 60 identical closes in a row — a dead or halted
listing whose flat stretch reads as zero volatility and flatters vol-targeting,
Sortino and every low-vol signal) and `sub-penny` (median close < `MIN_PRICE` =
0.01, where one tick is a whole return). Currently 444 of 9,432 rejected: 406
frozen, 29 sub-penny, 9 empty. A ticker that goes stale later is removed from
the clean and euro stores on its next ingest.

**Every ingested series is audited.** `write_prices` writes
`data/quality/<ticker>.json` (admitted/reason, rows and price cells raw vs
clean, worst raw move, frozen run, median price); `scripts/data_quality.py`
aggregates them, `--rescan` recomputes from the stores after a threshold
change, `--rejects` lists every excluded ticker. `MOMENTUM_DATA_DIR` env var
relocates the data dir (tests use it with tmp stores).

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

**Covariance** — `src/etoro_yfinance/covariance.py`, surfaced at `/correlation`.
A diagnostic factor risk model `V = BΩBᵀ + Ψ` over EUR returns: `B` from
EWMA-weighted least squares of each instrument on the `FACTORS` proxies (config
— `scripts/fetch_factors.py` ingests any that aren't in the store), `Ω` in two
clocks (fast vol, slow correlation), `Ψ` diagonal residual variance. Every
estimator is a causal EWMA (`S_t = x_t + θS_{t−1}`, weight-sum normalized), so
`pair_pass()` emits the model's implied correlation for each day in **one
forward pass** — the tracking chart is a test against the realized rolling
correlation, not a fit. `fit()`/`overview()` do the whole-universe version (top-N
by turnover; every pair of 5k names is 13M points). Nothing here trades. Known
property, not a bug: the 8 proxies are collinear (market↔tech ≈ 0.88), so
individual betas offset each other — read the exposure set, not one bar.

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
