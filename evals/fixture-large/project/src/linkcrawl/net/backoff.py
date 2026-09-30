"""Exponential backoff with a cap and optional jitter."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from linkcrawl.config.settings import Settings


class ExponentialBackoff:
    """Delay before attempt n+1 is base * multiplier ** (n - 1), capped at maximum."""

    def __init__(self, base: float, multiplier: float, maximum: float,
                 jitter: float = 0.0, rng: Optional[random.Random] = None):
        self.base = base
        self.multiplier = multiplier
        self.maximum = maximum
        self.jitter = jitter
        self._rng = rng or random.Random()

    @classmethod
    def from_settings(cls, settings: "Settings",
                      rng: Optional[random.Random] = None) -> "ExponentialBackoff":
        return cls(base=settings.backoff_base,
                   multiplier=settings.backoff_multiplier,
                   maximum=settings.backoff_max,
                   jitter=settings.backoff_jitter,
                   rng=rng)

    def raw_delay(self, attempt: int) -> float:
        if attempt < 1:
            raise ValueError("attempt numbers start at 1")
        return min(self.maximum, self.base * (self.multiplier ** (attempt - 1)))

    def delay(self, attempt: int) -> float:
        raw = self.raw_delay(attempt)
        if self.jitter <= 0 or raw == 0:
            return raw
        spread = raw * self.jitter
        return max(0.0, min(self.maximum, raw + self._rng.uniform(-spread, spread)))

    def schedule(self, attempts: int) -> List[float]:
        """Delays slept between attempts, without jitter (attempts - 1 values)."""
        return [self.raw_delay(n) for n in range(1, attempts)]

    def total(self, attempts: int) -> float:
        return sum(self.schedule(attempts))


class NoBackoff(ExponentialBackoff):
    def __init__(self):
        super().__init__(base=0.0, multiplier=1.0, maximum=0.0, jitter=0.0)
