"""Per-attempt timeouts.

urllib takes one timeout for the whole socket, so the value passed to urlopen
is the larger of the connect and read timeouts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linkcrawl.config.settings import Settings

ROBOTS_TIMEOUT_CAP_SECONDS = 5.0


@dataclass(frozen=True)
class Timeouts:
    connect: float
    read: float

    @classmethod
    def from_settings(cls, settings: "Settings") -> "Timeouts":
        return cls(connect=settings.connect_timeout, read=settings.timeout)

    def socket_timeout(self) -> float:
        return max(self.connect, self.read)

    def for_robots(self) -> "Timeouts":
        """robots.txt is small; never wait longer than the cap for it."""
        return Timeouts(connect=min(self.connect, ROBOTS_TIMEOUT_CAP_SECONDS),
                        read=min(self.read, ROBOTS_TIMEOUT_CAP_SECONDS))

    def worst_case(self, attempts: int, total_delay: float) -> float:
        """Upper bound on the wall time a link can take across all attempts."""
        return attempts * self.socket_timeout() + total_delay
