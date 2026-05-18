"""Typer CLI entrypoint."""

from __future__ import annotations

import logging
import sys
from decimal import Decimal, InvalidOperation
from typing import Annotated, Any

import typer
from pydantic import HttpUrl

from .config import Settings
from .pipeline import run_rebalance, run_what_if
from .safety import PreTradeSafetyError

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
    what_if: Annotated[
        bool,
        typer.Option(
            "--what-if",
            help=(
                "Compute trades and call IBKR's whatif endpoint per trade to "
                "preview commission + margin impact. Places no orders."
            ),
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

    if what_if:
        try:
            previews = run_what_if(settings)
        except PreTradeSafetyError as e:
            logging.getLogger(__name__).error("aborted: %s", e)
            raise typer.Exit(code=2) from e
        _print_what_if(previews)
        raise typer.Exit(code=0)

    try:
        report = run_rebalance(settings)
    except PreTradeSafetyError as e:
        # Already logged + pushed by pipeline; just exit non-zero cleanly.
        logging.getLogger(__name__).error("aborted: %s", e)
        raise typer.Exit(code=2) from e
    except Exception as e:
        logging.getLogger(__name__).exception("rebalance run failed: %s", e)
        raise typer.Exit(code=2) from e

    raise typer.Exit(code=0 if report.overall_success else 1)


def _print_what_if(previews: list[dict[str, Any]]) -> None:
    """Render a what-if preview table to stdout."""
    if not previews:
        typer.echo("=== What-If preview ===\n(no trades planned)")
        return

    typer.echo("=== What-If preview ===")
    total_commission = Decimal("0")
    commission_known = False
    for item in previews:
        trade = item["trade"]
        preview = item["preview"]
        comm = preview.get("commission")
        init_margin = preview.get("initMargin") or preview.get("init_margin")
        equity = preview.get("equityWithLoanAfter") or preview.get("equity_with_loan")

        line = f"  {trade.side.value:4s} {trade.quantity:>6d} {trade.symbol:<6s}"
        if comm is not None:
            line += f"  commission≈{comm}"
            try:
                total_commission += Decimal(str(comm))
                commission_known = True
            except (InvalidOperation, TypeError):
                pass
        if init_margin is not None:
            line += f"  init_margin={init_margin}"
        if equity is not None:
            line += f"  equity_after={equity}"
        typer.echo(line)

    if commission_known:
        typer.echo(f"\nTotal estimated commission: ${total_commission}")
    typer.echo("\nNo orders placed.")


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
