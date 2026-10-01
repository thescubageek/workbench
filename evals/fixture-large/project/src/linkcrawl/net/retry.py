"""The retry policy: which outcomes are retried, and how long to wait between them."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Callable, FrozenSet, Optional

from linkcrawl.net.backoff import ExponentialBackoff
from linkcrawl.net.response import FetchResponse

if TYPE_CHECKING:
    from linkcrawl.config.settings import Settings

RETRYABLE_STATUS_CODES: FrozenSet[int] = frozenset({429, 500, 502, 503, 504})
HONOR_RETRY_AFTER_STATUSES: FrozenSet[int] = frozenset({429, 503})

Attempt = Callable[[int], FetchResponse]


class RetryPolicy:
    def __init__(self, max_attempts: int, backoff: ExponentialBackoff,
                 retry_statuses: FrozenSet[int] = RETRYABLE_STATUS_CODES,
                 sleep: Callable[[float], None] = time.sleep):
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.max_attempts = max_attempts
        self.backoff = backoff
        self.retry_statuses = retry_statuses
        self._sleep = sleep

    @classmethod
    def from_settings(cls, settings: "Settings",
                      sleep: Callable[[float], None] = time.sleep) -> "RetryPolicy":
        return cls(max_attempts=settings.max_attempts,
                   backoff=ExponentialBackoff.from_settings(settings),
                   sleep=sleep)

    def should_retry(self, attempt: int, response: FetchResponse) -> bool:
        if attempt >= self.max_attempts:
            return False
        if response.error is not None:
            return response.error.retryable
        return response.status in self.retry_statuses

    def delay_for(self, attempt: int, response: FetchResponse) -> float:
        """Seconds to wait after `attempt` failed, honouring Retry-After if sent."""
        delay = self.backoff.delay(attempt)
        if response.status in HONOR_RETRY_AFTER_STATUSES:
            hinted = response.retry_after_seconds()
            if hinted is not None:
                delay = max(delay, min(hinted, self.backoff.maximum))
        return delay

    def execute(self, operation: Attempt) -> FetchResponse:
        attempt = 1
        while True:
            response = operation(attempt)
            if not self.should_retry(attempt, response):
                return response.with_attempts(attempt)
            self._sleep(self.delay_for(attempt, response))
            attempt += 1


def single_attempt() -> RetryPolicy:
    return RetryPolicy(max_attempts=1, backoff=ExponentialBackoff(0.0, 1.0, 0.0))
