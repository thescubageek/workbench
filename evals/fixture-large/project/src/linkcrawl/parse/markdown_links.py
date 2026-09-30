"""Link extraction from Markdown: inline links, images, reference definitions, autolinks."""

from __future__ import annotations

import re
from typing import List

from linkcrawl.parse.base import (ExtractedLink, absolutize, is_ignorable, line_at,
                                  line_offsets, unique)

INLINE_LINK = re.compile(r"(!?)\[(?P<text>[^\]]*)\]\((?P<href><[^>]*>|[^)\s]+)(?:\s+\"[^\"]*\")?\)")
REFERENCE_DEFINITION = re.compile(r"^[ \t]{0,3}\[(?P<label>[^\]]+)\]:\s*(?P<href>\S+)", re.MULTILINE)
AUTOLINK = re.compile(r"<(?P<href>https?://[^>\s]+)>")
FENCE = re.compile(r"^(```|~~~)", re.MULTILINE)


def _strip_fenced_code(text: str) -> str:
    """Blank out fenced code blocks, keeping newlines so line numbers still match."""
    out: List[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if FENCE.match(line.lstrip()):
            in_fence = not in_fence
            out.append("\n" if line.endswith("\n") else "")
            continue
        if in_fence:
            out.append("\n" if line.endswith("\n") else "")
        else:
            out.append(line)
    return "".join(out)


def extract_markdown_links(text: str, base_url: str) -> List[ExtractedLink]:
    source = _strip_fenced_code(text)
    offsets = line_offsets(source)
    links: List[ExtractedLink] = []
    for match in INLINE_LINK.finditer(source):
        href = match.group("href").strip("<>")
        if is_ignorable(href):
            continue
        kind = "md-image" if match.group(1) else "md-link"
        links.append(ExtractedLink(absolutize(base_url, href), kind,
                                   line_at(offsets, match.start()), match.group("text")))
    for match in REFERENCE_DEFINITION.finditer(source):
        href = match.group("href").strip("<>")
        if is_ignorable(href):
            continue
        links.append(ExtractedLink(absolutize(base_url, href), "md-reference",
                                   line_at(offsets, match.start()), match.group("label")))
    for match in AUTOLINK.finditer(source):
        links.append(ExtractedLink(absolutize(base_url, match.group("href")), "md-autolink",
                                   line_at(offsets, match.start())))
    return unique(links)
