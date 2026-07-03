#!/usr/bin/env bash
#
# Single-command deploy for the read-only momentum web UI.
#
#   ./deploy/install.sh
#
# Idempotent: run it once to deploy, and again after `git pull` to update.
# It installs uv (if missing), builds the venv with the web deps, and installs +
# starts a systemd service that binds the LAN and restarts on failure/reboot.
#
# The app is fully read-only (renders MOMENTUM_DATA_DIR). It holds NO broker
# credentials — eToro trading is the separate manual CLI (scripts/etoro_trade.py),
# not a service. Rebuild the data with `uv run python scripts/etoro_universe.py`.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_USER="$(id -un)"
HOST="${MOMENTUM_WEB_HOST:-0.0.0.0}"   # 0.0.0.0 = reachable on the LAN / tailnet
PORT="${MOMENTUM_WEB_PORT:-8800}"
DATA_DIR="${MOMENTUM_DATA_DIR:-$REPO/data}"

echo "==> repo:  $REPO"
echo "==> user:  $RUN_USER"
echo "==> bind:  $HOST:$PORT"

# 1. uv
if ! command -v uv >/dev/null 2>&1; then
  echo "==> installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
UV="$(command -v uv)"

# 2. deps
echo "==> uv sync --extra web"
cd "$REPO"
"$UV" sync --extra web

# 3. systemd service (generated so paths/user match this checkout)
UNIT=/etc/systemd/system/momentum-web.service
echo "==> writing $UNIT"
sudo tee "$UNIT" >/dev/null <<EOF
[Unit]
Description=Momentum web UI (read-only; holds no broker credentials)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$RUN_USER
WorkingDirectory=$REPO
Environment=MOMENTUM_WEB_HOST=$HOST
Environment=MOMENTUM_WEB_PORT=$PORT
Environment=MOMENTUM_DATA_DIR=$DATA_DIR
ExecStart=$REPO/.venv/bin/momentum-web
Restart=on-failure
RestartSec=5
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

echo "==> enabling + starting service"
sudo systemctl daemon-reload
sudo systemctl enable --now momentum-web.service
sudo systemctl restart momentum-web.service   # pick up new code/deps on re-run

echo
echo "Done. Web UI on http://$(hostname -I 2>/dev/null | awk '{print $1}'):$PORT"
echo "  logs:    journalctl -u momentum-web -f"
echo "  status:  systemctl status momentum-web"
echo "Reach it over Tailscale rather than port-forwarding the router."
