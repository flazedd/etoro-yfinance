"""Push notifications via ntfy.sh.

A no-op `LogOnlyNotifier` is used when `ntfy_topic` is unset so the rest of
the code never branches on "is notifications configured" — it just calls
`notify(...)` and trusts the implementation.

The notifier consumes a `RebalanceReport` (executor + cost attribution) so
the push body can include per-trade slippage and the total rebalancing cost.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Protocol

import httpx

from .cost import RebalanceReport, TradeCost

log = logging.getLogger(__name__)


class Notifier(Protocol):
    def notify(self, report: RebalanceReport) -> None: ...

    def event(self, title: str, body: str, *, priority: str = "default") -> None:
        """A free-form push not tied to a RebalanceReport — e.g. 'run started'
        or an early gate abort that happens before any trades are computed."""
        ...


class LogOnlyNotifier:
    """Used when no notification channel is configured. Logs the result."""

    def notify(self, report: RebalanceReport) -> None:
        title, body = _format(report)
        log.info("[%s] %s", title, body.replace("\n", " | "))

    def event(self, title: str, body: str, *, priority: str = "default") -> None:
        log.info("[%s] %s", title, body.replace("\n", " | "))


class NtfyNotifier:
    """Sends a single POST to ntfy.sh's HTTP push endpoint."""

    def __init__(
        self,
        topic: str,
        *,
        server: str = "https://ntfy.sh",
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._topic = topic
        self._server = server.rstrip("/")
        self._timeout = timeout
        self._transport = transport

    def notify(self, report: RebalanceReport) -> None:
        title, body = _format(report)
        priority = "default" if report.overall_success else "high"
        tags = "white_check_mark" if report.overall_success else "warning"
        self._post(title, body, priority=priority, tags=tags)

    def event(self, title: str, body: str, *, priority: str = "default") -> None:
        tags = "rotating_light" if priority == "high" else "information_source"
        self._post(title, body, priority=priority, tags=tags)

    def _post(self, title: str, body: str, *, priority: str, tags: str) -> None:
        # Always log to INFO too — keeps the terminal/cron-log informative
        # even when push is configured.
        log.info("[%s] %s", title, body.replace("\n", " | "))
        headers = {"Title": title, "Priority": priority, "Tags": tags}
        url = f"{self._server}/{self._topic}"
        try:
            with httpx.Client(timeout=self._timeout, transport=self._transport) as c:
                resp = c.post(url, content=body.encode("utf-8"), headers=headers)
            if resp.status_code >= 400:
                log.warning("ntfy push failed: %d %s", resp.status_code, resp.text[:200])
        except httpx.HTTPError as e:
            # Notification failures must NOT abort the rebalancer; we already
            # placed the trades. Log and move on.
            log.warning("ntfy push error: %s", e)


def _format(report: RebalanceReport) -> tuple[str, str]:
    if report.aborted_reason is not None:
        title = "ibkr-rebalance: ABORTED (pre-trade safety)"
        body = f"SAFETY: {report.aborted_reason}"
        return title, body

    if report.dry_run:
        title = f"ibkr-rebalance: DRY RUN ({report.n_total} planned)"
    elif report.overall_success:
        cost_pct = f"{report.total_cost_pct_of_nav:.2f}".rstrip("0").rstrip(".") or "0"
        title = f"ibkr-rebalance: OK ({report.n_successful}/{report.n_total}) cost {cost_pct}%"
    else:
        title = f"ibkr-rebalance: FAILED ({report.n_failed} of {report.n_total} failed)"

    lines: list[str] = [_trade_line(c) for c in report.trades]
    if not report.dry_run and report.trades:
        lines.append(_totals_line(report))

    body = "\n".join(lines) if lines else "(no trades)"
    return title, body


def _trade_line(c: TradeCost) -> str:
    prefix = "OK " if c.success else "ERR"
    label = c.label

    if not c.success:
        status = f" [{c.final_status}]" if c.final_status else ""
        err = f" — {c.error}" if c.error else ""
        return f"{prefix} {label}{status}{err}"

    parts: list[str] = []
    if c.fill_price is not None:
        parts.append(f"@ {c.fill_price}")
    if c.slippage_pct is not None:
        sign = "+" if c.slippage_pct >= 0 else ""
        parts.append(f"slip {sign}{c.slippage_pct:.2f}%")
    suffix = " " + " ".join(parts) if parts else ""
    return f"{prefix} {label}{suffix}"


def _totals_line(report: RebalanceReport) -> str:
    cost_pct = f"{report.total_cost_pct_of_nav:.3f}".rstrip("0").rstrip(".") or "0"
    slip = f"{report.total_slippage_dollars:.2f}"
    comm = f"{report.total_commission_dollars:.2f}"
    return (
        f"total: ${_dollars(report.total_cost_dollars)} ({cost_pct}% of NAV)  "
        f"slip ${slip}  comm ${comm}"
    )


def _dollars(d: Decimal) -> str:
    return f"{d:.2f}"


def build_notifier(
    *,
    ntfy_topic: str | None,
    ntfy_server: str = "https://ntfy.sh",
    transport: httpx.BaseTransport | None = None,
) -> Notifier:
    if not ntfy_topic:
        return LogOnlyNotifier()
    return NtfyNotifier(ntfy_topic, server=ntfy_server, transport=transport)
