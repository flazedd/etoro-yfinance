"""Typer CLI entrypoint."""

from __future__ import annotations

import logging
import sys
from typing import Annotated

import typer
from pydantic import HttpUrl

from .config import Settings
from .pipeline import run_rebalance

app = typer.Typer(no_args_is_help=False, add_completion=False, rich_markup_mode=None)


@app.command()
def rebalance(
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Print the planned trades and exit; place no orders.",
        ),
    ] = False,
    target_url: Annotated[
        str | None,
        typer.Option(
            "--target-url",
            help="Override TARGET_PORTFOLIO_URL from .env for this run.",
        ),
    ] = None,
    account: Annotated[
        str | None,
        typer.Option(
            "--account",
            help="Override IBKR_ACCOUNT_ID from .env for this run.",
        ),
    ] = None,
    no_rth: Annotated[
        bool,
        typer.Option(
            "--no-rth",
            help="Disable regular-trading-hours enforcement (use with care).",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="DEBUG-level logging."),
    ] = False,
) -> None:
    """Run one rebalance pass: target JSON → IBKR positions → diff → execute."""
    _setup_logging(verbose=verbose)

    settings = _load_settings(
        dry_run=dry_run, target_url=target_url, account=account, no_rth=no_rth
    )

    try:
        summary = run_rebalance(settings)
    except Exception as e:
        logging.getLogger(__name__).exception("rebalance run failed: %s", e)
        raise typer.Exit(code=2) from e

    raise typer.Exit(code=0 if summary.overall_success else 1)


def _setup_logging(*, verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        stream=sys.stderr,
    )


def _load_settings(
    *,
    dry_run: bool,
    target_url: str | None,
    account: str | None,
    no_rth: bool,
) -> Settings:
    settings = Settings()  # type: ignore[call-arg]  # pydantic-settings reads env
    overrides: dict[str, object] = {}
    if dry_run:
        overrides["dry_run"] = True
    if no_rth:
        overrides["trading_hours_only"] = False
    if target_url:
        overrides["target_portfolio_url"] = HttpUrl(target_url)
    if account:
        overrides["ibkr_account_id"] = account
    return settings.model_copy(update=overrides) if overrides else settings


def main() -> None:
    """Console-script entry. Wired up via pyproject.toml [project.scripts]."""
    app()
