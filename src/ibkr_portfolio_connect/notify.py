"""Push notifications via ntfy.sh.

A no-op `LogOnlyNotifier` is used when `ntfy_topic` is unset so the rest of
the code never branches on "is notifications configured" — it just calls
`notify(...)` and trusts the implementation.
"""

from __future__ import annotations

import logging
from typing import Protocol

import httpx

from .executor import ExecutionSummary

log = logging.getLogger(__name__)


class Notifier(Protocol):
    def notify(self, summary: ExecutionSummary) -> None: ...


class LogOnlyNotifier:
    """Used when no notification channel is configured. Logs the result."""

    def notify(self, summary: ExecutionSummary) -> None:
        title, body = _format(summary)
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

    def notify(self, summary: ExecutionSummary) -> None:
        title, body = _format(summary)
        priority = "default" if summary.overall_success else "high"
        tags = "white_check_mark" if summary.overall_success else "warning"
        headers = {
            "Title": title,
            "Priority": priority,
            "Tags": tags,
        }
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


def _format(summary: ExecutionSummary) -> tuple[str, str]:
    if summary.dry_run:
        title = f"ibkr-rebalance: DRY RUN ({summary.n_total} planned)"
    elif summary.overall_success:
        title = f"ibkr-rebalance: OK ({summary.n_successful}/{summary.n_total})"
    else:
        title = f"ibkr-rebalance: FAILED ({summary.n_failed} of {summary.n_total} failed)"

    lines: list[str] = []
    for r in summary.results:
        prefix = "OK " if r.success else "ERR"
        suffix = f" [{r.final_status}]" if r.final_status else ""
        if r.error:
            suffix += f" — {r.error}"
        lines.append(f"{prefix} {r.label}{suffix}")
    body = "\n".join(lines) if lines else "(no trades)"
    return title, body


def build_notifier(
    *,
    ntfy_topic: str | None,
    ntfy_server: str = "https://ntfy.sh",
    transport: httpx.BaseTransport | None = None,
) -> Notifier:
    if not ntfy_topic:
        return LogOnlyNotifier()
    return NtfyNotifier(ntfy_topic, server=ntfy_server, transport=transport)
