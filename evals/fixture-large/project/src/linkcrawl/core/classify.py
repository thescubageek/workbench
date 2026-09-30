"""Turn a FetchResponse into a LinkStatus and a human-readable reason."""

from __future__ import annotations

from typing import Iterable, Tuple

from linkcrawl.core.result import LinkStatus
from linkcrawl.net.errors import TooManyRedirects
from linkcrawl.net.response import FetchResponse

BROKEN_STATUS_MIN = 400
RATE_LIMITED_STATUS = 429
REDIRECT_RANGE = range(300, 400)


def classify(response: FetchResponse,
             accepted_statuses: Iterable[int] = ()) -> Tuple[LinkStatus, str]:
    """Decide the status of a link from the final response after all retries."""
    if response.error is not None:
        if isinstance(response.error, TooManyRedirects):
            return LinkStatus.BROKEN, "too many redirects"
        return (LinkStatus.BROKEN,
                f"{response.describe_error()} after {response.attempts} attempt(s)")
    code = response.status
    if code is None:
        return LinkStatus.BROKEN, "no HTTP status"
    if code in set(accepted_statuses):
        return LinkStatus.OK, f"HTTP {code} accepted by configuration"
    if code == RATE_LIMITED_STATUS:
        return (LinkStatus.SKIPPED,
                f"rate limited by server (HTTP 429) after {response.attempts} attempt(s)")
    if code in REDIRECT_RANGE:
        return LinkStatus.BROKEN, f"unfollowed redirect (HTTP {code})"
    if code >= BROKEN_STATUS_MIN:
        return LinkStatus.BROKEN, f"HTTP {code}"
    return LinkStatus.OK, ""


def is_server_error(code: int) -> bool:
    return 500 <= code <= 599
