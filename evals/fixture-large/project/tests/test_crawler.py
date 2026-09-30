from conftest import html

from linkcrawl.crawl.crawler import crawl

SITE = {
    "https://example.com/": html('<a href="/a">a</a> <a href="/b">b</a> '
                                 '<a href="https://other.example/x">x</a>'),
    "https://example.com/a": html('<a href="/deep">deep</a> <a href="/">home</a>'),
    "https://example.com/b": (404, {}, b""),
    "https://example.com/deep": html('<a href="/deeper">deeper</a>'),
    "https://example.com/deeper": html(""),
    "https://other.example/x": html('<a href="https://other.example/y">y</a>'),
}


def test_crawl_respects_depth_and_does_not_expand_external(make_components):
    components = make_components(routes=SITE, start_urls=["https://example.com/"],
                                 respect_robots=False, max_depth=2)
    results = crawl(components.settings, components, ["https://example.com/"])
    by_url = {r.url: r for r in results}
    assert set(by_url) == {
        "https://example.com/",
        "https://example.com/a",
        "https://example.com/b",
        "https://other.example/x",
        "https://example.com/deep",
    }
    assert by_url["https://example.com/b"].broken
    assert by_url["https://example.com/deep"].depth == 2
    assert by_url["https://example.com/deep"].parent == "https://example.com/a"
    assert components.opener.count("https://other.example/x", "GET") == 0


def test_crawl_stops_at_max_pages(make_components):
    components = make_components(routes=SITE, start_urls=["https://example.com/"],
                                 respect_robots=False, max_pages=2)
    results = crawl(components.settings, components, ["https://example.com/"])
    assert len(results) == 2


def test_crawl_seeds_from_sitemap(make_components):
    sitemap = (b'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/'
               b'sitemap/0.9"><url><loc>https://example.com/deeper</loc></url></urlset>')
    routes = dict(SITE)
    routes["https://example.com/sitemap.xml"] = (200, {"Content-Type": "application/xml"},
                                                 sitemap)
    components = make_components(routes=routes, respect_robots=False, max_depth=0)
    results = crawl(components.settings, components, [],
                    sitemap="https://example.com/sitemap.xml")
    assert [r.url for r in results] == ["https://example.com/deeper"]
