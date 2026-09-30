"""A per-host token-bucket rate limiter.

Each host gets its own bucket that refills at `rate` tokens per second and holds
at most `burst` tokens. A rate of 0 disables limiting. robots.txt Crawl-delay
can raise the minimum interval for one host (see set_min_interval).
"""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING, Callable, Dict, Optional
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from linkcrawl.config.settings import Settings


class TokenBucket:
    def __init__(self, rate: float, burst: int, clock: Callable[[], float]):
        self.rate = rate
        self.capacity = float(burst)
        self.tokens = float(burst)
        self._clock = clock
        self._updated = clock()
        self.min_interval = 0.0
        self._last_grant: Optional[float] = None

    def _refill(self) -> None:
        now = self._clock()
        elapsed = max(0.0, now - self._updated)
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self._updated = now

    def wait_time(self) -> float:
        """Seconds until a token is available and the minimum interval has passed."""
        self._refill()
        wait = 0.0
        if self.tokens < 1.0:
            wait = (1.0 - self.tokens) / self.rate
        if self._last_grant is not None and self.min_interval > 0:
            since = self._clock() - self._last_grant
            wait = max(wait, self.min_interval - since)
        return max(0.0, wait)

    def take(self) -> None:
        self._refill()
        self.tokens = max(0.0, self.tokens - 1.0)
        self._last_grant = self._clock()


class HostRateLimiter:
    def __init__(self, rate: float, burst: int,
                 clock: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], None] = time.sleep):
        self.rate = rate
        self.burst = burst
        self._clock = clock
        self._sleep = sleep
        self._buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()
        self.total_wait = 0.0

    @classmethod
    def from_settings(cls, settings: "Settings") -> "HostRateLimiter":
        return cls(rate=settings.rate_limit, burst=settings.rate_burst)

    @property
    def enabled(self) -> bool:
        return self.rate > 0

    @staticmethod
    def host_of(url: str) -> str:
        return (urlsplit(url).hostname or "").lower()

    def _bucket(self, host: str) -> TokenBucket:
        bucket = self._buckets.get(host)
        if bucket is None:
            bucket = TokenBucket(self.rate, self.burst, self._clock)
            self._buckets[host] = bucket
        return bucket

    def set_min_interval(self, url: str, seconds: float) -> None:
        if not self.enabled or seconds <= 0:
            return
        with self._lock:
            bucket = self._bucket(self.host_of(url))
            bucket.min_interval = max(bucket.min_interval, seconds)

    def acquire(self, url: str) -> float:
        """Block until a request to url's host is allowed; return seconds waited."""
        if not self.enabled:
            return 0.0
        host = self.host_of(url)
        with self._lock:
            bucket = self._bucket(host)
            wait = bucket.wait_time()
        if wait > 0:
            self._sleep(wait)
            self.total_wait += wait
        with self._lock:
            bucket.take()
        return wait


class NullRateLimiter(HostRateLimiter):
    def __init__(self):
        super().__init__(rate=0.0, burst=1)
