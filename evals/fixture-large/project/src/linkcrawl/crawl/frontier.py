"""The crawl frontier: a breadth-first queue of URLs with de-duplication."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Iterator, Optional, Set

from linkcrawl.crawl.normalize import normalize_url


@dataclass(frozen=True)
class FrontierItem:
    url: str
    depth: int
    parent: Optional[str] = None


class Frontier:
    def __init__(self, max_size: int = 100_000):
        self.max_size = max_size
        self._queue: Deque[FrontierItem] = deque()
        self._seen: Set[str] = set()
        self.dropped = 0

    def __len__(self) -> int:
        return len(self._queue)

    def __bool__(self) -> bool:
        return bool(self._queue)

    def __iter__(self) -> Iterator[FrontierItem]:
        return iter(list(self._queue))

    def seen(self, url: str) -> bool:
        return normalize_url(url) in self._seen

    def push(self, url: str, depth: int, parent: Optional[str] = None) -> bool:
        """Queue url unless it was queued before; return True if it was added."""
        key = normalize_url(url)
        if key in self._seen:
            return False
        if len(self._queue) >= self.max_size:
            self.dropped += 1
            return False
        self._seen.add(key)
        self._queue.append(FrontierItem(url=key, depth=depth, parent=parent))
        return True

    def pop(self) -> FrontierItem:
        return self._queue.popleft()

    def seen_count(self) -> int:
        return len(self._seen)
