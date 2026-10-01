from linkcrawl.core.result import LinkStatus, ResultSource
from linkcrawl.crawl.robots import ROBOTS_SKIP_REASON

ROBOTS = b"User-agent: *\nDisallow: /private/\nCrawl-delay: 2\n"


def test_disallowed_link_is_skipped_without_a_request(make_components):
    components = make_components(routes={
        "https://example.com/robots.txt": (200, {"Content-Type": "text/plain"}, ROBOTS),
        "https://example.com/private/page": (200, {}, b""),
    })
    result = components.checker.check("https://example.com/private/page")
    assert result.status is LinkStatus.SKIPPED
    assert result.reason == ROBOTS_SKIP_REASON
    assert result.source is ResultSource.POLICY
    assert components.opener.count("https://example.com/private/page") == 0


def test_allowed_link_is_checked(make_components):
    components = make_components(routes={
        "https://example.com/robots.txt": (200, {}, ROBOTS),
        "https://example.com/public": (200, {}, b""),
    })
    assert components.checker.check("https://example.com/public").ok
    assert components.robots.crawl_delay("https://example.com/public") == 2.0


def test_missing_robots_allows_everything(make_components):
    components = make_components(routes={
        "https://example.com/private/page": (200, {}, b""),
    })
    assert components.checker.check("https://example.com/private/page").ok


def test_robots_server_error_disallows_origin(make_components):
    components = make_components(routes={
        "https://example.com/robots.txt": (503, {}, b""),
        "https://example.com/page": (200, {}, b""),
    }, max_attempts=1)
    result = components.checker.check("https://example.com/page")
    assert result.skipped
    assert "unavailable: HTTP 503" in result.reason


def test_robots_is_fetched_once_per_origin(make_components):
    components = make_components(routes={
        "https://example.com/robots.txt": (200, {}, ROBOTS),
        "https://example.com/a": (200, {}, b""),
        "https://example.com/b": (200, {}, b""),
    })
    components.checker.check("https://example.com/a")
    components.checker.check("https://example.com/b")
    assert components.opener.count("https://example.com/robots.txt") == 1


def test_ignore_robots_checks_disallowed_link(make_components):
    components = make_components(routes={
        "https://example.com/robots.txt": (200, {}, ROBOTS),
        "https://example.com/private/page": (200, {}, b""),
    }, respect_robots=False)
    assert components.checker.check("https://example.com/private/page").ok
    assert components.opener.count("https://example.com/robots.txt") == 0
