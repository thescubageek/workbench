"""Counts over a list of results. The CLI's exit code is derived from these counts."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from linkcrawl.core.result import CheckResult, LinkStatus


@dataclass(frozen=True)
class Summary:
    total: int = 0
    ok: int = 0
    broken: int = 0
    skipped: int = 0
    from_cache: int = 0
    attempts: int = 0
    skip_reasons: Dict[str, int] = field(default_factory=dict)
    broken_reasons: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_results(cls, results: Iterable[CheckResult]) -> "Summary":
        items: List[CheckResult] = list(results)
        counts = Counter(result.status for result in items)
        skip_reasons = Counter(_reason_key(r.reason) for r in items if r.skipped)
        broken_reasons = Counter(_reason_key(r.reason) for r in items if r.broken)
        return cls(
            total=len(items),
            ok=counts.get(LinkStatus.OK, 0),
            broken=counts.get(LinkStatus.BROKEN, 0),
            skipped=counts.get(LinkStatus.SKIPPED, 0),
            from_cache=sum(1 for r in items if r.from_cache),
            attempts=sum(r.attempts for r in items),
            skip_reasons=dict(skip_reasons),
            broken_reasons=dict(broken_reasons),
        )

    @property
    def has_broken(self) -> bool:
        return self.broken > 0

    @property
    def has_skipped(self) -> bool:
        return self.skipped > 0

    def headline(self) -> str:
        parts = [f"{self.total} checked", f"{self.ok} ok", f"{self.broken} broken",
                 f"{self.skipped} skipped"]
        if self.from_cache:
            parts.append(f"{self.from_cache} from cache")
        return ", ".join(parts)

    def to_dict(self) -> Dict[str, object]:
        return {
            "total": self.total,
            "ok": self.ok,
            "broken": self.broken,
            "skipped": self.skipped,
            "from_cache": self.from_cache,
            "attempts": self.attempts,
            "skip_reasons": dict(self.skip_reasons),
            "broken_reasons": dict(self.broken_reasons),
        }


def _reason_key(reason: str) -> str:
    """Group reasons that differ only in detail, e.g. 'HTTP 404' and 'HTTP 410' stay apart
    but 'disallowed by robots.txt (unavailable: ...)' groups with the plain form."""
    head = reason.split(" (", 1)[0]
    return head.split(";", 1)[0].strip() or "unspecified"
