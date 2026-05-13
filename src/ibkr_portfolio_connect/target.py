"""Fetch and validate the target-portfolio JSON over HTTP(S).

The producing service is built elsewhere. We trust the URL/host (it's the
user's own service), but never trust the payload: it goes through pydantic
validation before anything else looks at it.
"""

from __future__ import annotations

import httpx
from pydantic import HttpUrl, ValidationError

from .schema import TargetPortfolio


class TargetFetchError(Exception):
    """Raised when the target portfolio cannot be fetched or fails validation."""


def fetch_target_portfolio(
    url: str | HttpUrl,
    *,
    bearer_token: str | None = None,
    timeout: float = 30.0,
    transport: httpx.BaseTransport | None = None,
) -> TargetPortfolio:
    """GET the URL and parse the response body as a TargetPortfolio.

    Raises `TargetFetchError` on any network failure, non-2xx response, or
    schema validation failure. Never coerces bad input into "valid-looking"
    output.
    """
    headers = {"Accept": "application/json"}
    if bearer_token is not None:
        headers["Authorization"] = f"Bearer {bearer_token}"

    try:
        with httpx.Client(timeout=timeout, transport=transport) as client:
            resp = client.get(str(url), headers=headers)
    except httpx.HTTPError as e:
        raise TargetFetchError(f"network error fetching target portfolio: {e}") from e

    if resp.status_code >= 400:
        raise TargetFetchError(f"target URL returned HTTP {resp.status_code}: {resp.text[:500]}")

    if not resp.content:
        raise TargetFetchError("target URL returned an empty response body")

    try:
        return TargetPortfolio.model_validate_json(resp.content)
    except ValidationError as e:
        raise TargetFetchError(f"target JSON failed schema validation: {e}") from e
