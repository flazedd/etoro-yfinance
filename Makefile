.PHONY: dev deploy

# Local dev server: syncs the web deps, runs uvicorn with auto-reload on :8800.
dev:
	uv run --extra web momentum-dev

# Deploy on the target device (e.g. RPi4): installs uv + deps, then installs and
# starts a systemd service. Idempotent — re-run after `git pull` to update.
deploy:
	./deploy/install.sh
