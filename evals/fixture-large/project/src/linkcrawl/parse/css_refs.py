"""url() and @import references in CSS."""

from __future__ import annotations

import re
from typing import List

from linkcrawl.parse.base import (ExtractedLink, absolutize, is_ignorable, line_at,
                                  line_offsets, unique)

URL_FUNCTION = re.compile(r"url\(\s*(?P<quote>['\"]?)(?P<href>.*?)(?P=quote)\s*\)", re.IGNORECASE)
IMPORT_STRING = re.compile(r"@import\s+(?P<quote>['\"])(?P<href>[^'\"]+)(?P=quote)", re.IGNORECASE)
COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


def _blank_comments(css: str) -> str:
    return COMMENT.sub(lambda match: re.sub(r"[^\n]", " ", match.group(0)), css)


def extract_css_refs(css: str, base_url: str) -> List[ExtractedLink]:
    source = _blank_comments(css)
    offsets = line_offsets(source)
    links: List[ExtractedLink] = []
    for pattern in (URL_FUNCTION, IMPORT_STRING):
        for match in pattern.finditer(source):
            href = match.group("href").strip()
            if is_ignorable(href):
                continue
            links.append(ExtractedLink(absolutize(base_url, href), "css",
                                       line_at(offsets, match.start())))
    links.sort(key=lambda link: link.line or 0)
    return unique(links)
