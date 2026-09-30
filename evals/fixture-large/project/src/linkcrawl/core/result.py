"""The result model: one CheckResult per checked link."""

from __future__ import annotations

import enum
from dataclasses import dataclass, replace
from typing import Any, Dict, Optional


class LinkStatus(str, enum.Enum):
    """The three outcomes a link can have."""

    OK = "ok"
    BROKEN = "broken"
    SKIPPED = "skipped"


class ResultSource(str, enum.Enum):
    """Where a result came from."""

    NETWORK = "network"
    CACHE = "cache"
    POLICY = "policy"


@dataclass(frozen=True)
class CheckResult:
    url: str
    status: LinkStatus
    http_status: Optional[int] = None
    reason: str = ""
    source: ResultSource = ResultSource.NETWORK
    attempts: int = 0
    elapsed_seconds: float = 0.0
    checked_at: float = 0.0
    parent: Optional[str] = None
    depth: int = 0

    @property
    def ok(self) -> bool:
        return self.status is LinkStatus.OK

    @property
    def broken(self) -> bool:
        return self.status is LinkStatus.BROKEN

    @property
    def skipped(self) -> bool:
        return self.status is LinkStatus.SKIPPED

    @property
    def from_cache(self) -> bool:
        return self.source is ResultSource.CACHE

    def with_source(self, source: ResultSource) -> "CheckResult":
        return replace(self, source=source)

    def with_context(self, parent: Optional[str], depth: int) -> "CheckResult":
        return replace(self, parent=parent, depth=depth)

    def with_reason(self, reason: str) -> "CheckResult":
        return replace(self, reason=reason)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status.value,
            "http_status": self.http_status,
            "reason": self.reason,
            "source": self.source.value,
            "attempts": self.attempts,
            "elapsed_seconds": round(self.elapsed_seconds, 4),
            "checked_at": self.checked_at,
            "parent": self.parent,
            "depth": self.depth,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CheckResult":
        try:
            status = LinkStatus(data["status"])
        except (KeyError, ValueError) as error:
            raise ValueError(f"result has no valid status: {data!r}") from error
        source = ResultSource(data.get("source", ResultSource.NETWORK.value))
        http_status = data.get("http_status")
        return cls(
            url=str(data["url"]),
            status=status,
            http_status=int(http_status) if http_status is not None else None,
            reason=str(data.get("reason", "")),
            source=source,
            attempts=int(data.get("attempts", 0)),
            elapsed_seconds=float(data.get("elapsed_seconds", 0.0)),
            checked_at=float(data.get("checked_at", 0.0)),
            parent=data.get("parent"),
            depth=int(data.get("depth", 0)),
        )


def ok_result(url: str, http_status: Optional[int], **fields: Any) -> CheckResult:
    return CheckResult(url=url, status=LinkStatus.OK, http_status=http_status, **fields)


def broken_result(url: str, reason: str, http_status: Optional[int] = None,
                  **fields: Any) -> CheckResult:
    return CheckResult(url=url, status=LinkStatus.BROKEN, http_status=http_status,
                       reason=reason, **fields)


def skipped_result(url: str, reason: str, **fields: Any) -> CheckResult:
    fields.setdefault("source", ResultSource.POLICY)
    return CheckResult(url=url, status=LinkStatus.SKIPPED, reason=reason, **fields)
