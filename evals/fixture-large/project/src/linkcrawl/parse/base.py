"""Shared types and filters for the link extractors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Set

from linkcrawl.crawl.normalize import normalize_url, resolve

IGNORED_SCHEMES = ("mailto:", "javascript:", "tel:", "data:", "about:", "sms:")


@dataclass(frozen=True)
class ExtractedLink:
    url: str
    kind: str
    line: Optional[int] = None
    text: str = ""


def is_ignorable(href: str) -> bool:
    stripped = href.strip()
    if not stripped or stripped.startswith("#"):
        return True
    return stripped.lower().startswith(IGNORED_SCHEMES)


def absolutize(base: str, href: str) -> str:
    return normalize_url(resolve(base, href))


def unique(links: Iterable[ExtractedLink]) -> List[ExtractedLink]:
    seen: Set[str] = set()
    out: List[ExtractedLink] = []
    for link in links:
        if link.url in seen:
            continue
        seen.add(link.url)
        out.append(link)
    return out


def line_offsets(text: str) -> List[int]:
    offsets = [0]
    for index, char in enumerate(text):
        if char == "\n":
            offsets.append(index + 1)
    return offsets


def line_at(offsets: List[int], position: int) -> int:
    low, high = 0, len(offsets) - 1
    while low < high:
        middle = (low + high + 1) // 2
        if offsets[middle] <= position:
            low = middle
        else:
            high = middle - 1
    return low + 1


def iter_nonempty(values: Iterable[Optional[str]]) -> Iterator[str]:
    for value in values:
        if value and value.strip():
            yield value.strip()
