# Deploying the momentum stack on a Raspberry Pi 4

Three long-lived pieces + two timers, split by credential boundary:

| Unit | User | Holds creds? | Role |
|------|------|--------------|------|
| `momentum-web.service` | `momentum` | **no** | read-only FastAPI UI (universe / execution / performance) |
| `momentum-trade-worker.service` | `trader` | **yes** | claims job requests, runs the rebalance, writes results |
| `momentum-rebalance.timer` → `.service` | `trader` | yes | queues the monthly run (worker executes it) |
| `momentum-publish.timer` → `.service` | `trader` | yes | snapshots bbterminal performance → commits to the Pages repo |

The web can only *request* a run (a row in SQLite). Only the worker trades.

## 1. Install

```bash
sudo install -d -o trader -g trader /var/lib/momentum /var/lib/momentum/data
sudo git clone <this-repo> /opt/momentum-stack
cd /opt/momentum-stack
uv sync --extra web                # builds .venv with the web + trade deps
uv run --no-sync momentum-web --help   # sanity
```

Seed the data dir with the universe artifacts (so the mapping page has content):

```bash
sudo -u trader cp data/leonteq_*.json /var/lib/momentum/data/
```

## 2. Credentials (the boundary)

```bash
sudo install -d -o root -g root -m 750 /etc/momentum

# trader.env — ALL the secrets (chmod 600, owned by trader)
sudo install -o trader -g trader -m 600 /dev/null /etc/momentum/trader.env
# put in it: IBIND_OAUTH1A_*, IBKR_ACCOUNT_ID, BBTERMINAL_*, SUPABASE_*,
#   SIZING_CURRENCY=EUR, REQUIRE_STRATEGY_HEALTHY=true,
#   DRY_RUN=true            # flip to false ONLY when you want live trading
#   MOMENTUM_SITE_REPO_DIR=/var/lib/momentum/site-repo
#   MOMENTUM_SITE_DATA_PATH=data/performance.json
#   MOMENTUM_DEPLOY_KEY=/etc/momentum/deploy_key
#   MOMENTUM_PUBLISH_PUSH=1

# web.env — NO broker secrets. Only non-sensitive UI config (or leave empty).
sudo install -o momentum -g momentum -m 600 /dev/null /etc/momentum/web.env
```

## 3. The GitHub Pages repo (performance site)

```bash
# create an empty repo on GitHub with Pages enabled, then on the Pi:
sudo -u trader git clone git@github.com:<you>/<perf-site>.git /var/lib/momentum/site-repo
# add the deploy key (write access) to that repo's Deploy Keys, key file at MOMENTUM_DEPLOY_KEY
```

`momentum-publish --push` writes `data/performance.json` into that repo and pushes;
Pages rebuilds. (Tell me the repo + the JSON path your site wants and I'll match it.)

## 4. Services

```bash
sudo cp deploy/*.service deploy/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now momentum-web.service momentum-trade-worker.service
sudo systemctl enable --now momentum-rebalance.timer momentum-publish.timer
journalctl -u momentum-trade-worker -f
```

Align `momentum-rebalance.timer`'s `OnCalendar` with the strategy's
`next_rebalance_at` (shown on the Performance page).

## 5. Access (don't expose a brokerage box)

Install Caddy, use `deploy/Caddyfile`. Prefer reaching the Pi over **Tailscale**
on its tailnet name rather than opening a port. If you must expose it publicly,
add auth in the Caddyfile first.

## Safety notes

- `DRY_RUN=true` is the default; the monthly timer and the worker both honor it.
  Live trading happens only when `DRY_RUN=false` **and** (for ad-hoc runs) the
  user types the confirmation phrase in the UI.
- Every live order still passes the existing gates: bbterminal health +
  freshness, the reviewed `conid_map.json`, pre-trade safety caps, and RTH.
