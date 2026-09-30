"""Scope: which URLs are internal, and which are excluded by pattern."""

from __future__ import annotations

import fnmatch
from typing import Iterable, Optional, Sequence, Set, Tuple

from linkcrawl.crawl.normalize import host

EXCLUDED_REASON = "excluded by pattern"
NOT_INCLUDED_REASON = "not matched by any include pattern"
EXTERNAL_REASON = "external link (check_external is off)"


class Scope:
    def __init__(self, start_urls: Iterable[str] = (),
                 include: Sequence[str] = (), exclude: Sequence[str] = ()):
        self.hosts: Set[str] = {host(url) for url in start_urls if host(url)}
        self.include: Tuple[str, ...] = tuple(include)
        self.exclude: Tuple[str, ...] = tuple(exclude)

    def add_start(self, url: str) -> None:
        name = host(url)
        if name:
            self.hosts.add(name)

    def is_internal(self, url: str) -> bool:
        name = host(url)
        if not self.hosts:
            return True
        return any(name == h or name.endswith("." + h) for h in self.hosts)

    def exclusion_reason(self, url: str) -> Optional[str]:
        for pattern in self.exclude:
            if fnmatch.fnmatch(url, pattern):
                return f"{EXCLUDED_REASON} {pattern!r}"
        if self.include and not any(fnmatch.fnmatch(url, p) for p in self.include):
            return NOT_INCLUDED_REASON
        return None

    def is_excluded(self, url: str) -> bool:
        return self.exclusion_reason(url) is not None
