"""Sitemap reading: urlset and sitemapindex documents, as seed URLs for a crawl."""

from __future__ import annotations

import gzip
import xml.etree.ElementTree as ElementTree
from typing import TYPE_CHECKING, List, Set

from linkcrawl.crawl.normalize import normalize_url

if TYPE_CHECKING:
    from linkcrawl.net.client import HttpClient

SITEMAP_NAMESPACE = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
SITEMAP_MAX_NESTING = 2
SITEMAP_MAX_BYTES = 10 * 1024 * 1024
SITEMAP_MAX_URLS = 50_000


class SitemapError(Exception):
    pass


def _local(tag: str) -> str:
    return tag.split("}", 1)[-1]


def parse_sitemap(data: bytes):
    """Return (kind, locations) where kind is 'urlset' or 'sitemapindex'."""
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as error:
        raise SitemapError(f"not valid XML: {error}") from error
    kind = _local(root.tag)
    if kind not in ("urlset", "sitemapindex"):
        raise SitemapError(f"unexpected root element <{kind}>")
    locations: List[str] = []
    for child in root:
        for node in child:
            if _local(node.tag) == "loc" and node.text:
                locations.append(node.text.strip())
    return kind, locations


class SitemapReader:
    def __init__(self, client: "HttpClient", max_nesting: int = SITEMAP_MAX_NESTING):
        self.client = client
        self.max_nesting = max_nesting
        self.errors: List[str] = []

    def read(self, url: str) -> List[str]:
        urls: List[str] = []
        self._read(url, 0, urls, set())
        return urls[:SITEMAP_MAX_URLS]

    def _read(self, url: str, nesting: int, out: List[str], visited: Set[str]) -> None:
        key = normalize_url(url)
        if key in visited:
            return
        visited.add(key)
        response, body = self.client.get_body(url, SITEMAP_MAX_BYTES)
        if not response.transport_ok or (response.status or 0) >= 400:
            self.errors.append(f"{url}: {response.describe_error() or response.status}")
            return
        try:
            kind, locations = parse_sitemap(body)
        except SitemapError as error:
            self.errors.append(f"{url}: {error}")
            return
        if kind == "urlset":
            out.extend(locations)
            return
        if nesting >= self.max_nesting:
            self.errors.append(f"{url}: sitemap index nested deeper than {self.max_nesting}")
            return
        for child in locations:
            self._read(child, nesting + 1, out, visited)
            if len(out) >= SITEMAP_MAX_URLS:
                return
