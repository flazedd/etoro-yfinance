# etoro-yfinance

[![CI](https://github.com/flazedd/etoro-yfinance/actions/workflows/ci.yml/badge.svg)](https://github.com/flazedd/etoro-yfinance/actions/workflows/ci.yml)

Map the entire **eToro** tradable universe to **yfinance** analysis tickers,
browse it in a read-only web UI, and trade on eToro from a CLI. OpenFIGI is
available for ISIN → ticker/FIGI lookups.

- **eToro** — execution (the broker). `EtoroClient` implements a broker-agnostic
  `Broker` protocol over eToro's public REST API.
- **yfinance** — analysis (price/volume history). eToro's `symbolFull` already
  carries the Yahoo suffix (`SIE.DE`, `1810.HK`), so the map is by symbol, not ISIN.
- **OpenFIGI** — optional ISIN → ticker/FIGI resolution.

## Setup

```bash
uv sync --extra web          # web UI deps (fastapi/uvicorn/jinja2)
cp .env.example .env         # then paste your eToro API keys
```

eToro keys come from the [API Portal](https://api-portal.etoro.com/) (Settings ›
Trading › API Key Management): one shared **public** key (`ETORO_API_KEY`) plus a
per-environment **user** key (`ETORO_USER_KEY_DEMO` / `_REAL`). `ETORO_ENV` picks
demo vs real.

## CLI — trade + build the universe

```bash
# Account value / resolve / preview / buy / sell (buy & sell prompt to confirm)
uv run python scripts/etoro_trade.py balance
uv run python scripts/etoro_trade.py preview AAPL --amount 100
uv run python scripts/etoro_trade.py buy AAPL --amount 100
uv run python scripts/etoro_trade.py sell --position-id <id> --instrument-id <id> --units 2

# Build the eToro→yfinance universe mapping (writes data/etoro_universe_mapping.json)
uv run python scripts/etoro_universe.py
uv run python scripts/etoro_universe.py --validate   # also live-check yfinance (slow)

# OpenFIGI: ISIN -> ticker/FIGI
uv run python scripts/openfigi_check.py US0378331005
```

`sell` = close an existing long by units (needs the eToro positionId + instrumentId).
Demo is the default environment; flip `ETORO_ENV=real` (with a real key) to go live.

## Web UI (read-only, no credentials)

```bash
uv run momentum-dev          # web with --reload  →  http://127.0.0.1:8800/
uv run momentum-prod         # web, no reload
```

Pages: **Home** (universe coverage + health), **eToro ↔ yfinance** (the full
mapping — search + filter by type/status, sortable, per-row Yahoo link), and
**Diagnostics** (system health). The web only reads
`data/etoro_universe_mapping.json`; it never calls eToro. Rebuild that file with
`scripts/etoro_universe.py`.

## Tests

```bash
uv run pytest -q
uv run ruff check . && uv run mypy src/etoro_yfinance
```
