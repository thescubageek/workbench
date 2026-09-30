"""The result cache.

A re-check of a URL whose cached result is younger than the TTL returns the
cached result and sends no request. Only OK results are cached, so a broken or
skipped link is always checked again. A TTL of 0 disables the cache.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, FrozenSet, Optional

from linkcrawl.core.result import CheckResult, LinkStatus, ResultSource
from linkcrawl.store.clock import SystemClock
from linkcrawl.store.json_store import JsonStore
from linkcrawl.store.keys import cache_key

if TYPE_CHECKING:
    from linkcrawl.config.settings import Settings

CACHE_FORMAT_VERSION = 2
CACHEABLE_STATUSES: FrozenSet[LinkStatus] = frozenset({LinkStatus.OK})


class ResultCache:
    def __init__(self, store: JsonStore, ttl_seconds: int, clock=None):
        self.store = store
        self.ttl_seconds = ttl_seconds
        self.clock = clock or SystemClock()
        self._entries: Dict[str, Dict[str, Any]] = {}
        self._loaded = False
        self._dirty = False
        self.hits = 0
        self.misses = 0
        self.expired = 0

    @classmethod
    def from_settings(cls, settings: "Settings", clock=None) -> "ResultCache":
        return cls(JsonStore(settings.cache_path), settings.cache_ttl, clock=clock)

    @property
    def enabled(self) -> bool:
        return self.ttl_seconds > 0

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        data = self.store.load()
        if data.get("version") == CACHE_FORMAT_VERSION:
            self._entries = dict(data.get("entries", {}))
        self._loaded = True

    def age_of(self, entry: Dict[str, Any]) -> float:
        return self.clock.now() - float(entry.get("checked_at", 0.0))

    def is_fresh(self, entry: Dict[str, Any]) -> bool:
        return self.age_of(entry) < self.ttl_seconds

    def get(self, url: str) -> Optional[CheckResult]:
        """The cached result for url if it is still fresh, otherwise None."""
        if not self.enabled:
            return None
        self._ensure_loaded()
        entry = self._entries.get(cache_key(url))
        if entry is None:
            self.misses += 1
            return None
        if not self.is_fresh(entry):
            self.expired += 1
            self.misses += 1
            return None
        self.hits += 1
        return CheckResult.from_dict(entry).with_source(ResultSource.CACHE)

    def put(self, result: CheckResult) -> bool:
        if not self.enabled or result.status not in CACHEABLE_STATUSES:
            return False
        if result.source is ResultSource.CACHE:
            return False
        self._ensure_loaded()
        entry = result.to_dict()
        entry["checked_at"] = result.checked_at or self.clock.now()
        self._entries[cache_key(result.url)] = entry
        self._dirty = True
        return True

    def invalidate(self, url: str) -> bool:
        self._ensure_loaded()
        removed = self._entries.pop(cache_key(url), None) is not None
        self._dirty = self._dirty or removed
        return removed

    def prune(self) -> int:
        self._ensure_loaded()
        stale = [key for key, entry in self._entries.items() if not self.is_fresh(entry)]
        for key in stale:
            del self._entries[key]
        if stale:
            self._dirty = True
        return len(stale)

    def flush(self) -> None:
        if not self.enabled or not self._dirty:
            return
        self.prune()
        self.store.save({"version": CACHE_FORMAT_VERSION, "entries": self._entries})
        self._dirty = False

    def __len__(self) -> int:
        self._ensure_loaded()
        return len(self._entries)
