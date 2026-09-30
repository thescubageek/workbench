"""The outcome of one fetch, after retries."""

from __future__ import annotations

import email.utils
import time
from dataclasses import dataclass, field, replace
from typing import Dict, Optional

from linkcrawl.net.errors import NetworkError


@dataclass(frozen=True)
class FetchResponse:
    url: str
    status: Optional[int] = None
    final_url: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    elapsed_seconds: float = 0.0
    attempts: int = 0
    error: Optional[NetworkError] = None
    method: str = "HEAD"
    body: bytes = b""

    @property
    def transport_ok(self) -> bool:
        return self.error is None and self.status is not None

    @property
    def redirected(self) -> bool:
        return self.final_url is not None and self.final_url != self.url

    @property
    def content_type(self) -> str:
        value = self.header("content-type") or ""
        return value.split(";", 1)[0].strip().lower()

    def header(self, name: str) -> Optional[str]:
        wanted = name.lower()
        for key, value in self.headers.items():
            if key.lower() == wanted:
                return value
        return None

    def retry_after_seconds(self, now: Optional[float] = None) -> Optional[float]:
        """Parse a Retry-After header given as seconds or as an HTTP date."""
        value = self.header("retry-after")
        if not value:
            return None
        value = value.strip()
        if value.isdigit():
            return float(value)
        try:
            parsed = email.utils.parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
        if parsed is None:
            return None
        current = time.time() if now is None else now
        return max(0.0, parsed.timestamp() - current)

    def with_attempts(self, attempts: int) -> "FetchResponse":
        return replace(self, attempts=attempts)

    def describe_error(self) -> str:
        if self.error is None:
            return ""
        return f"{self.error.kind}: {self.error.message}"
