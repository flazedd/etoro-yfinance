# Deploying the momentum web UI (e.g. Raspberry Pi 4)

The app is a single **read-only** FastAPI service that renders the eToro↔yfinance
universe mapping and diagnostics. It holds **no broker credentials** and never
trades — eToro trading is the separate manual CLI (`scripts/etoro_trade.py`).

## Deploy

On the device (needs `git`, `sudo`, and systemd):

```bash
git clone <this-repo> ~/etoro-yfinance
cd ~/etoro-yfinance
make deploy
```

`make deploy` runs [`install.sh`](install.sh), which:

1. installs [`uv`](https://docs.astral.sh/uv/) if it's missing,
2. builds the venv with the web deps (`uv sync --extra web`),
3. writes a `momentum-web.service` systemd unit (user, repo path, and bind
   address auto-detected) and enables + starts it.

It's **idempotent** — after a `git pull`, run `make deploy` again to update
deps and restart the service.

Then open `http://<device-ip>:8800`.

## Configuration

Override via env vars when running `make deploy` (they're baked into the unit):

| Var | Default | Meaning |
|-----|---------|---------|
| `MOMENTUM_WEB_HOST` | `0.0.0.0` | bind address (`0.0.0.0` = reachable on the LAN/tailnet) |
| `MOMENTUM_WEB_PORT` | `8800` | port |
| `MOMENTUM_DATA_DIR` | `<repo>/data` | dir the UI reads its JSON from |

```bash
MOMENTUM_WEB_PORT=9000 make deploy
```

Rebuild the data the UI serves with:

```bash
uv run python scripts/etoro_universe.py
```

## Operating it

```bash
systemctl status momentum-web        # is it up?
journalctl -u momentum-web -f        # tail logs
sudo systemctl restart momentum-web  # restart
```

## Access — don't expose a brokerage-adjacent box

Prefer reaching the device over **Tailscale** on its tailnet name rather than
port-forwarding your router. If you want TLS or a tailnet hostname, put
[Caddy](https://caddyserver.com/) in front — see [`Caddyfile`](Caddyfile) — and
bind the app to `127.0.0.1` (`MOMENTUM_WEB_HOST=127.0.0.1 make deploy`) so only
Caddy is exposed.
