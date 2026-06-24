# ibkr-portfolio-connect

[![CI](https://github.com/flazedd/ibkr-portfolio-connect/actions/workflows/ci.yml/badge.svg)](https://github.com/flazedd/ibkr-portfolio-connect/actions/workflows/ci.yml)

Monthly auto-rebalancer for an Interactive Brokers account. A cron job on a
Raspberry Pi fetches a target portfolio (JSON over HTTP), reads current IBKR
positions, and places the minimal set of trades to bring the account in line
with the target.

## Web app (momentum-stack)

A FastAPI + HTMX UI for the RPi4 with three pages, split by credential boundary
(the web holds **no** creds; the worker is the only thing that trades):

- **`/universe`** — the LEONTEQ universe → IBKR mapping (confidence, ticker/exchange
  match, currency, ADV, OpenFIGI verdict, GuruFocus links), from the pipeline artifacts.
- **`/execution`** — request the monthly rebalance: *Preview (dry-run)* or *Execute LIVE*
  (gated by a typed confirmation). The web inserts a job row; the worker runs it through
  every gate and records the plan, fills, reference prices and slippage.
- **`/performance`** — bbterminal strategy performance (MTD / since-inception / daily
  returns + holdings), snapshotted by the publisher and committed to a GitHub Pages repo.

```bash
uv sync --extra web
uv run momentum-web                 # read-only UI        (no creds)        :8800
uv run momentum-trade-worker        # claims + executes jobs  (creds)
uv run momentum-publish --push      # bbterminal perf -> site repo  (creds)
```

Pieces: `web/server.py` (UI), `web/worker.py` (trader), `db.py` (SQLite/SQLModel
queue + run log), `publisher.py` (performance → git). Deployment (systemd units +
Caddy + the credential split) is in [`deploy/README.md`](deploy/README.md).

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
                         │ HTTPS (OAuth 1.0a, signed)
                         ▼
                Interactive Brokers
                (api.ibkr.com / CP Web API v1)
```

No long-running gateway or browser-based auto-login process is involved.
The rebalancer signs every request with a private key it loads at startup
and talks to IBKR directly.

## Key choices

- **API:** IBKR Client Portal API v1 (cpapi-v1). Offline docs are mirrored
  under [`docs/ibkr/`](docs/ibkr/).
- **Auth:** OAuth 1.0a via [IBind](https://github.com/Voyz/ibind). One-time
  enrollment generates a consumer key + access token tied to a local RSA
  keypair; thereafter the rebalancer runs headlessly with no 2FA prompts
  and no gateway process. (The earlier IBeam + TOTP design has been removed.)
- **Rebalance mode:** diff-and-minimize — only buy/sell the deltas, never
  full liquidate.
- **Order type:** market DAY (liquid ETFs, easy to reason about).
- **Shares:** whole shares only in v1; leftover stays in the cash buffer.
- **Notifications:** ntfy.sh push (set `NTFY_TOPIC` in `.env`). Failures
  always send `priority: high`.
- **Stack:** Python 3.11, `uv`, `httpx`, `pydantic`, `typer`, `ibind`.

## Target portfolio schema (v2)

See [`examples/target-portfolio.example.json`](examples/target-portfolio.example.json)
for the exact contract your producing service must satisfy. Summary:

```json
{
  "schema_version": 2,
  "generated_at": "<ISO-8601 UTC>",
  "base_currency": "USD",
  "cash_buffer_pct": 0.5,
  "positions": [
    {
      "symbol": "...",
      "exchange": "...",
      "asset_class": "STK",
      "weight_pct": 99.5,
      "reference_price": 285.50,
      "reference_price_at": "<ISO-8601 UTC>"
    }
  ]
}
```

Rules:

- `sum(weight_pct) + cash_buffer_pct == 100`
- `base_currency` must be `USD`
- v2 supports `STK` only (stocks + ETFs)
- `exchange` is the primary listing — the rebalancer resolves
  `symbol+exchange → conid` via the IBKR `secdef/search` endpoint and routes
  orders SMART
- `reference_price` is the per-share price your producing service observed
  when generating the target. The rebalancer uses it for share-count sizing
  AND as the benchmark for slippage attribution. Use a recent price (this
  morning's open / yesterday's close / whatever's freshest in your data).
- `reference_price_at` is the timestamp the reference price was observed

## Execution + slippage report

Orders are placed as **MIDPRICE DAY** — IBKR pegs the order to the bid-ask
midpoint and auto-adjusts as the market moves, giving you fills near mid on
liquid ETFs without blind MKT slippage.

After every run, the notification body includes a per-trade table and a
total-cost summary line:

```
OK  BUY 5 VTI @ 285.42 slip +0.04%
OK  BUY 3 BND @ 72.39 slip -0.01%
total: $1.25 (0.01% of NAV)  slip $0.90  comm $0.35
```

Sign convention: positive slippage means "worse than reference" (paid more
for a buy, received less for a sell); negative means savings. `total cost %
of NAV` is your stated metric — what fraction of the account was spent on
rebalancing (slippage + commissions).

## Configuration

Copy [`.env.example`](.env.example) to `.env` and fill in. Never commit `.env`.

Required values fall into three groups:

- **OAuth credentials** (`IBIND_OAUTH1A_*`) — see the [OAuth setup](#oauth-setup)
  section below.
- **Account** — `IBKR_ACCOUNT_ID` (paper `DUQxxxxxx` for testing, live
  `Uxxxxxxx` for production).
- **Target source** — `TARGET_PORTFOLIO_URL` and optional bearer token.

### Multiple environment profiles (paper vs live)

If you enroll OAuth separately for paper and live (recommended — paper is a
separate enrollment per IBKR), you can keep two side-by-side profiles and
toggle which one `.env` points at:

```
.env             # symlink → .env.live or .env.paper
.env.live        # live OAuth credentials + Uxxxxxxx account
.env.paper       # paper OAuth credentials + DUQxxxxxx account
```

Switch via the helper script:

```bash
uv run python scripts/use_env.py paper   # rebalancer now talks to paper
uv run python scripts/use_env.py live    # rebalancer now talks to live
uv run python scripts/use_env.py         # show current profile
```

All `.env.*` files are gitignored (only `.env.example` is tracked).

## Local development

```bash
uv sync                                       # install deps
uv run pytest -q                              # 129 tests, ~1 second
uv run ruff check . && uv run ruff format --check .
uv run mypy --strict src tests
uv run ibkr-portfolio-connect --help          # CLI sanity check
```

Run a real (non-dry) rebalance only after OAuth is active and you've
inspected `--dry-run` output:

```bash
uv run ibkr-portfolio-connect --dry-run       # print planned trades, exit 0
uv run ibkr-portfolio-connect                 # place orders
```

## OAuth setup

OAuth enrollment is a one-time process per IBKR account. Plan a week — IBKR
activates new consumer keys on weekend server restarts and propagation can
take several days.

### 1. Generate keys locally

```bash
mkdir -p ~/ibkr-oauth && cd ~/ibkr-oauth
openssl genrsa -out private_signature.pem 2048
openssl rsa  -in private_signature.pem  -pubout -out public_signature.pem
openssl genrsa -out private_encryption.pem 2048
openssl rsa  -in private_encryption.pem -pubout -out public_encryption.pem
openssl dhparam -out dhparam.pem 2048          # ~30s
chmod 600 ~/ibkr-oauth/private_*.pem
```

### 2. Register at IBKR

Open the OAuth self-service portal (force the US domain to avoid regional
quirks):

```
https://ndcdyn.interactivebrokers.com/sso/Login?action=OAUTH&RL=1&ip2loc=US
```

- Invent a 9-character alphanumeric **Consumer Key** (e.g. via a password
  generator). Store it in your password manager.
- Upload `public_signature.pem`, `public_encryption.pem`, and `dhparam.pem`.
- Submit — IBKR returns an **Access Token** and **Access Token Secret**.
  Copy both into your password manager **immediately**; the page warns
  they disappear on refresh.

### 3. Extract the DH prime

IBind wants the DH prime as a hex string, not the PEM file:

```bash
uv run python scripts/extract_dh_prime.py ~/ibkr-oauth/dhparam.pem
```

Paste the output into `IBIND_OAUTH1A_DH_PRIME` in `.env`.

### 4. Wait for activation, then test

```bash
uv run python scripts/check_oauth.py
```

While IBKR is still propagating, you'll see:

```
{"error":"id: ...., error: invalid consumer","statusCode":401}
```

Once activation completes (typically next weekend) the same command prints
your accounts and tickle response. That's the green light.

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
$EDITOR .env                                  # fill in OAuth creds, account, target
```

### 3. Copy OAuth keys to the Pi

The private keys generated on your dev machine in step 1 of [OAuth setup](#oauth-setup)
need to live in `~/ibkr-oauth/` on the Pi (this path is referenced by
`docker-compose.yml`):

```bash
# from your dev machine
scp -r ~/ibkr-oauth pi@<pi-host>:~/ibkr-oauth
ssh pi@<pi-host> 'chmod 600 ~/ibkr-oauth/private_*.pem'
```

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
  (b) `api.ibkr.com`.
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

To validate end-to-end delivery without running a full rebalance:

```bash
uv run python scripts/test_ntfy.py <topic>            # mixed success/failure
uv run python scripts/test_ntfy.py <topic> --dry-run  # blue, normal priority
uv run python scripts/test_ntfy.py <topic> --all-fail # red, priority: high
```

## Dashboard (read-only observability)

For a monthly job, push notifications are the real-time channel; the dashboard
is the **audit trail and history**. It answers "what did the last run do, and
why" without SSHing in to grep logs.

**How it works.** When `REPORT_DIR` / `LOG_DIR` are set (the compose stack sets
them automatically), each run writes:

- `REPORT_DIR/<timestamp>.json` — a full record: start/finish, the bbterminal
  health + freshness gates, NAV, current-vs-target positions, planned trades,
  fills + slippage, and final status. Written at every checkpoint, so a run that
  crashes or hangs still leaves a `status: running` breadcrumb.
- `LOG_DIR/rebalance.log` — a rotating log file (in addition to stderr).

**Security model — this is the important part.** The dashboard is a *separate
process* that **only reads those files**. It imports no broker client, holds no
OAuth credentials, and exposes only `GET` endpoints — there is no way to place
or cancel an order through it. Bind it to your LAN; **never** port-forward it.

Two ways to view it:

```bash
# (a) Live server on the LAN — view at http://<pi-host>:8080
docker compose up -d dashboard
#     or bare-metal:
uv run --extra dashboard ibkr-dashboard

# (b) Static snapshot — a self-contained HTML file, no server needed
uv run python scripts/build_dashboard.py --report-dir data/runs --log-dir data/logs
open data/dashboard.html
```

The compose `dashboard` service mounts the run records + logs **read-only**,
restarts automatically, and carries its own `fastapi`/`uvicorn` (installed via
the `dashboard` extra) so the trade-placing `rebalancer` image stays lean.

> The dashboard shows only what the cron job last recorded. It does **not**
> poll IBKR for "positions right now" — that would mean putting credentials on
> the web-facing process. If you want fresher between-run data, add a small
> read-only snapshot cron; keep it out of the server.

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
├── ibkr_client.py     # IBind+OAuth adapter (positions/orders/secdef/snapshots)
├── target.py          # HTTP-fetch the target JSON and validate
├── rebalance.py       # pure diff engine (whole-share, sorted SELL→BUY)
├── executor.py        # place orders, walk reply chain, poll status, dry-run
└── notify.py          # ntfy.sh push notifier

scripts/
├── check_oauth.py        # standalone OAuth connectivity test
├── extract_dh_prime.py   # one-off helper: dhparam.pem → hex string for .env
├── place_trade.py        # ad-hoc one-shot trade against a chosen account
├── test_ntfy.py          # send a fake push to validate ntfy setup
├── test_target_fetch.py  # fetch + validate a local target portfolio
└── use_env.py            # switch .env symlink between profiles (paper/live)
```

### Ad-hoc trade testing

For one-off paper trades (independent of the monthly cron), use
`scripts/place_trade.py`. Required: `--account` (paper `DUQxxxxxxx` is the
safe default). Defaults to ARCA for conid resolution (works for most ETFs).

```bash
# Plan only, do not place:
uv run python scripts/place_trade.py VOO BUY 1 --account DUQ970095 --dry-run

# Place with confirmation prompt:
uv run python scripts/place_trade.py VOO BUY 1 --account DUQ970095

# For stocks on other listings:
uv run python scripts/place_trade.py AAPL BUY 1 --account DUQ970095 --exchange NASDAQ
```


## Known limitations

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
- **OAuth activation latency.** A freshly-registered consumer key only
  works after IBKR's next weekend server restart (can be 1–2 weeks).
  Plan accordingly.
