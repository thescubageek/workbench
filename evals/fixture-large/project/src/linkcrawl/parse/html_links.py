"""Link extraction from HTML with the standard-library HTMLParser."""

from __future__ import annotations

from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

from linkcrawl.parse.base import ExtractedLink, absolutize, is_ignorable, unique
from linkcrawl.parse.css_refs import extract_css_refs

LINK_ATTRIBUTES: Dict[str, Tuple[str, ...]] = {
    "a": ("href",),
    "area": ("href",),
    "link": ("href",),
    "img": ("src",),
    "script": ("src",),
    "iframe": ("src",),
    "source": ("src",),
    "video": ("src", "poster"),
    "audio": ("src",),
    "form": ("action",),
}
SRCSET_TAGS = ("img", "source")
NOFOLLOW_REL = "nofollow"


class _LinkCollector(HTMLParser):
    def __init__(self, base_url: str, follow_nofollow: bool):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.follow_nofollow = follow_nofollow
        self.links: List[ExtractedLink] = []
        self._in_style = False
        self._style_chunks: List[str] = []
        self._style_line = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        values = {name.lower(): value for name, value in attrs if value is not None}
        line = self.getpos()[0]
        if tag == "base" and values.get("href"):
            self.base_url = absolutize(self.base_url, values["href"])
            return
        if tag == "style":
            self._in_style = True
            self._style_line = line
            return
        if tag == "a" and not self.follow_nofollow:
            rel = values.get("rel", "").lower().split()
            if NOFOLLOW_REL in rel:
                return
        for attribute in LINK_ATTRIBUTES.get(tag, ()):
            href = values.get(attribute)
            if href is not None:
                self._add(href, tag, line)
        if tag in SRCSET_TAGS and values.get("srcset"):
            for candidate in _split_srcset(values["srcset"]):
                self._add(candidate, tag, line)
        if values.get("style"):
            for ref in extract_css_refs(values["style"], self.base_url):
                self.links.append(ExtractedLink(ref.url, "css", line))

    def handle_endtag(self, tag: str) -> None:
        if tag == "style" and self._in_style:
            css = "".join(self._style_chunks)
            for ref in extract_css_refs(css, self.base_url):
                offset = ref.line - 1 if ref.line else 0
                self.links.append(ExtractedLink(ref.url, "css", self._style_line + offset))
            self._in_style = False
            self._style_chunks = []

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self._style_chunks.append(data)

    def _add(self, href: str, tag: str, line: int) -> None:
        if is_ignorable(href):
            return
        self.links.append(ExtractedLink(absolutize(self.base_url, href), tag, line))


def _split_srcset(value: str) -> List[str]:
    candidates = []
    for part in value.split(","):
        pieces = part.strip().split()
        if pieces:
            candidates.append(pieces[0])
    return candidates


def extract_html_links(html: str, base_url: str,
                       follow_nofollow: bool = True) -> List[ExtractedLink]:
    collector = _LinkCollector(base_url, follow_nofollow)
    collector.feed(html)
    collector.close()
    return unique(collector.links)
