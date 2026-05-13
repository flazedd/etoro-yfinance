# ibkr-portfolio-connect

Monthly auto-rebalancer for an Interactive Brokers account. A cron job on a
Raspberry Pi fetches a target portfolio (JSON over HTTP), reads current IBKR
positions, and places the minimal set of trades to bring the account in line
with the target.

## Architecture

```
                  ┌──────────────────────────┐
                  │  target portfolio JSON   │  served by some other service
                  │  (HTTP GET, schema v1)   │
                  └────────────┬─────────────┘
                               │
            cron (1st of month)│
                               ▼
            ┌──────────────────────────────────┐
            │  rebalancer (this repo)          │   docker-compose oneshot
            │   1. fetch target JSON           │
            │   2. read current positions      │
            │   3. compute minimal trade list  │
            │   4. place market DAY orders     │
            │   5. notify success/failure      │
            └────────────┬─────────────────────┘
                         │ HTTPS (localhost:5000)
                         ▼
            ┌──────────────────────────────────┐
            │  IBeam (Dockerized)              │   long-running service
            │  - headless Chrome auto-login    │
            │  - hosts IBKR Client Portal      │
            │    Gateway (cpapi-v1)            │
            └────────────┬─────────────────────┘
                         │ HTTPS
                         ▼
                Interactive Brokers
```

## Key choices

- **API:** IBKR Client Portal API v1 (cpapi-v1). Offline docs are mirrored
  under [`docs/ibkr/`](docs/ibkr/).
- **Auth:** [IBeam](https://github.com/Voyz/ibeam) handles unattended login
  (username + password + TOTP). Without it, sessions die and the cron job
  fails silently.
- **Rebalance mode:** diff-and-minimize — only buy/sell the deltas, never
  full liquidate.
- **Order type:** market DAY (liquid ETFs, easy to reason about).
- **Shares:** whole shares only in v1; leftover stays in the cash buffer.
- **Notifications:** ntfy.sh push (set `NTFY_TOPIC` in `.env`). Failures
  always send `priority: high`.
- **Stack:** Python 3.11, `uv`, `httpx`, `pydantic`, `typer`.

## Target portfolio schema

See [`examples/target-portfolio.example.json`](examples/target-portfolio.example.json)
for the exact contract your producing service must satisfy. Summary:

```json
{
  "schema_version": 1,
  "generated_at": "<ISO-8601 UTC>",
  "base_currency": "USD",
  "cash_buffer_pct": 0.5,
  "positions": [
    { "symbol": "...", "exchange": "...", "asset_class": "STK", "weight_pct": 99.5 }
  ]
}
```

Rules: `sum(weight_pct) + cash_buffer_pct == 100`; v1 supports `STK` only
(stocks + ETFs); `exchange` is the primary listing — the rebalancer resolves
`symbol+exchange → conid` via the IBKR `secdef/search` endpoint and routes
via SMART.

## Configuration

Copy [`.env.example`](.env.example) to `.env` and fill in. Never commit `.env`.

The same `.env` file is consumed by both the rebalancer and IBeam.

## Local development

```bash
uv sync                                       # install deps
uv run pytest -q                              # 144 tests, ~1 second
uv run ruff check . && uv run ruff format --check .
uv run mypy --strict src tests
uv run ibkr-portfolio-connect --help          # CLI sanity check
```

Run a real (non-dry) rebalance only after the gateway is up and you've
inspected `--dry-run` output:

```bash
uv run ibkr-portfolio-connect --dry-run       # print planned trades, exit 0
uv run ibkr-portfolio-connect                 # place orders
```

## Raspberry Pi deployment

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in for the group change to apply.
```

### 2. Clone and configure

```bash
git clone https://github.com/flazedd/ibkr-portfolio-connect.git
cd ibkr-portfolio-connect
cp .env.example .env
$EDITOR .env                                  # fill in every blank
```

You'll need:

- IBKR live username + password (NOT your paper username — use the live
  trader name even if you point at a paper account).
- The base32 TOTP secret you got when enrolling soft 2FA in the IBKR client
  portal (IB Key → "I want to use a different method" → set up authenticator app).
- The target portfolio URL your other service publishes.
- A randomly-generated string for `NTFY_TOPIC` (anyone with the topic can
  read your push, so make it long).

### 3. Start the gateway

```bash
docker compose up -d ibeam
docker compose logs -f ibeam                  # watch it log in
```

When you see `Client login succeeds` (or equivalent), the gateway is ready.
The healthcheck should also turn green within ~90s.

### 4. Smoke-test the rebalancer

```bash
docker compose run --rm rebalancer --dry-run
```

You should see the planned trade list logged and a "DRY RUN" ntfy push on
your phone. If anything fails here, fix it before scheduling the cron.

### 5. Schedule the cron

Edit the host's user crontab:

```bash
crontab -e
```

Add (run at 14:30 UTC = 10:30 EDT on the 1st of each month — comfortably
inside the US market open):

```
30 14 1 * * cd /home/pi/ibkr-portfolio-connect && /usr/bin/docker compose run --rm rebalancer >> /var/log/ibkr-rebalance.log 2>&1
```

Notes:

- The exact path to `docker` may vary. Use `which docker` to confirm.
- The rebalancer's exit code reflects success (`0`), partial trade failure
  (`1`), or unrecoverable error (`2`). The ntfy push will already have told
  you which.
- The job needs network access to (a) your target-portfolio URL and
  (b) interactivebrokers.com (via the gateway). The Pi's clock must be
  correct or the TOTP will fail — install `systemd-timesyncd` or `chrony`.
- For the first few months, run with `--dry-run` (edit the crontab line to
  add the flag) and confirm the proposed trades look sane before letting it
  loose.

## Notifications

Notifications go to [ntfy.sh](https://ntfy.sh) — a free, no-signup push
service. Pick a random topic name and put it in `NTFY_TOPIC`:

1. Install the ntfy mobile app and subscribe to your topic.
2. The rebalancer pushes one message per run with the trade summary.
3. Failures use `priority: high` so they ring through Do-Not-Disturb on
   most setups.

If `NTFY_TOPIC` is unset, the result is only logged — fine for testing,
but you'll never know if a monthly run silently failed.

## Offline API docs

Full IBKR Client Portal v1 documentation is mirrored under
[`docs/ibkr/`](docs/ibkr/) so you can grep without a network round-trip:

- `cpapi-v1.md` — full reference, one big file (~450 KB)
- `cpapi-v1-sections/` — same content split per-endpoint (257 files)
- `cpapi-v1-index.md` — table of contents linking to each section
- `market-data-subscriptions.md`, `ibkr-api-home.md` — supplementary

## Project layout

```
src/ibkr_portfolio_connect/
├── __init__.py        # re-exports main from cli
├── cli.py             # typer CLI entry point
├── pipeline.py        # orchestrator: fetch → read → compute → execute → notify
├── config.py          # pydantic-settings; reads .env
├── schema.py          # target portfolio + internal types (pydantic v2)
├── ibkr_client.py     # cpapi-v1 wrapper (httpx; auth/orders/positions/market data)
├── target.py          # HTTP-fetch the target JSON and validate
├── rebalance.py       # pure diff engine (whole-share, sorted SELL→BUY)
├── executor.py        # place orders, walk reply chain, poll status, dry-run
└── notify.py          # ntfy.sh push notifier
```

## Known v1 limitations

- **`base_currency` must be `USD`.** Multi-currency accounts are not supported.
- **Stocks/ETFs only** (`asset_class: "STK"`). Options, futures, FX,
  crypto are not supported.
- **Whole shares only.** Any pre-existing fractional residue is ignored
  (we can't trade out of it via the cpapi orders endpoint).
- **No holiday calendar.** `TRADING_HOURS_ONLY=true` only checks weekday
  and 09:30–16:00 ET; a run on a market holiday will reach IBKR and be
  rejected. Either disable the cron on holidays manually or set
  `TRADING_HOURS_ONLY=false` and rely on IBKR's own rejection.
- **No retry on individual trade failure.** If an order is rejected, the
  rebalancer reports the failure and continues with the remaining trades;
  the next month's run will pick up the slack.
