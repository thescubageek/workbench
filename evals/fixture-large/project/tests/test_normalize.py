import pytest

from linkcrawl.crawl.frontier import Frontier
from linkcrawl.crawl.normalize import normalize_url, origin


@pytest.mark.parametrize("raw, expected", [
    ("HTTP://Example.COM:80/a/../b", "http://example.com/b"),
    ("https://example.com:443", "https://example.com/"),
    ("https://example.com:8443/x/", "https://example.com:8443/x/"),
    ("https://example.com/p?b=2&a=1#frag", "https://example.com/p?a=1&b=2"),
    ("https://example.com/p?utm_source=x&id=3&gclid=q", "https://example.com/p?id=3"),
    ("https://example.com/a%20b", "https://example.com/a%20b"),
    ("mailto:someone@example.com", "mailto:someone@example.com"),
])
def test_normalize(raw, expected):
    assert normalize_url(raw) == expected


def test_relative_resolution():
    assert normalize_url("../c.html", base="https://example.com/a/b/") == \
        "https://example.com/a/c.html"


def test_origin():
    assert origin("https://Example.com:443/path?q=1") == "https://example.com"


def test_frontier_deduplicates_equivalent_urls():
    frontier = Frontier()
    assert frontier.push("https://example.com/a#one", depth=0)
    assert not frontier.push("HTTPS://EXAMPLE.com/a#two", depth=1)
    assert len(frontier) == 1
    item = frontier.pop()
    assert item.url == "https://example.com/a"
    assert item.depth == 0


def test_frontier_drops_when_full():
    frontier = Frontier(max_size=1)
    frontier.push("https://example.com/1", 0)
    assert not frontier.push("https://example.com/2", 0)
    assert frontier.dropped == 1
