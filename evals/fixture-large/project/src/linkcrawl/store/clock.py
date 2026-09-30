"""Wall-clock sources. The cache uses wall time, since entries outlive the process."""

from __future__ import annotations

import time


class SystemClock:
    def now(self) -> float:
        return time.time()


class FixedClock:
    """A clock for tests: time moves only when advance() is called."""

    def __init__(self, start: float = 1_700_000_000.0):
        self.current = start

    def now(self) -> float:
        return self.current

    def advance(self, seconds: float) -> None:
        self.current += seconds
