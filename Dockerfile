# Rebalancer container. Built for both amd64 and arm64 (Raspberry Pi).
# Run with `docker compose run --rm rebalancer`; it is a oneshot, not a
# long-running service.

FROM python:3.11-slim AS base

# Pull in `uv` (Astral's fast Python package manager) from its official image.
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

# Install deps first (better layer caching: this layer only invalidates when
# pyproject.toml / uv.lock change).
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy the source last and install the project itself.
COPY src ./src
RUN uv sync --frozen --no-dev

# Drop privileges. The .venv is already owned by root but accessible
# read-only by rebalancer.
RUN useradd --create-home --shell /usr/sbin/nologin --uid 1000 rebalancer
USER rebalancer

# Default action is one rebalance pass. The CLI exits 0 on success,
# 1 on partial trade failure, 2 on an unrecoverable run failure.
ENTRYPOINT ["ibkr-portfolio-connect"]
