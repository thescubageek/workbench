"""Depth limits: how far from a start URL the crawler follows links.

A start URL has depth 0. A link found on a page at depth d has depth d + 1. A
link is checked when its depth is at most max_depth; a page is expanded (its
links extracted) only when its depth is below max_depth.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DepthLimit:
    max_depth: int

    def allows(self, depth: int) -> bool:
        return 0 <= depth <= self.max_depth

    def can_expand(self, depth: int) -> bool:
        return depth < self.max_depth

    def child_depth(self, depth: int) -> int:
        return depth + 1


UNLIMITED = DepthLimit(max_depth=10 ** 6)
