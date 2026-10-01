"""Choose an extractor by content type, falling back to the URL's extension."""

from __future__ import annotations

from typing import Callable, Dict, List
from urllib.parse import urlsplit

from linkcrawl.parse.base import ExtractedLink
from linkcrawl.parse.css_refs import extract_css_refs
from linkcrawl.parse.html_links import extract_html_links
from linkcrawl.parse.markdown_links import extract_markdown_links

Extractor = Callable[[str, str], List[ExtractedLink]]

EXTRACTORS_BY_TYPE: Dict[str, Extractor] = {
    "text/html": extract_html_links,
    "application/xhtml+xml": extract_html_links,
    "text/markdown": extract_markdown_links,
    "text/x-markdown": extract_markdown_links,
    "text/css": extract_css_refs,
}
EXTRACTORS_BY_EXTENSION: Dict[str, Extractor] = {
    ".html": extract_html_links,
    ".htm": extract_html_links,
    ".md": extract_markdown_links,
    ".markdown": extract_markdown_links,
    ".css": extract_css_refs,
}
DEFAULT_ENCODING = "utf-8"


def _extension(url: str) -> str:
    path = urlsplit(url).path
    dot = path.rfind(".")
    if dot == -1 or "/" in path[dot:]:
        return ""
    return path[dot:].lower()


def extractor_for(content_type: str, url: str):
    extractor = EXTRACTORS_BY_TYPE.get(content_type)
    if extractor is None and content_type in ("", "text/plain", "application/octet-stream"):
        extractor = EXTRACTORS_BY_EXTENSION.get(_extension(url))
    return extractor


def can_extract(content_type: str, url: str) -> bool:
    return extractor_for(content_type, url) is not None


def decode(body: bytes, encoding: str = DEFAULT_ENCODING) -> str:
    if body.startswith(b"\xef\xbb\xbf"):
        body = body[3:]
    return body.decode(encoding, errors="replace")


def extract_links(body: bytes, content_type: str, base_url: str) -> List[ExtractedLink]:
    extractor = extractor_for(content_type, base_url)
    if extractor is None:
        return []
    return extractor(decode(body), base_url)
