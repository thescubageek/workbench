import pytest

from linkcrawl.core.classify import classify
from linkcrawl.core.result import LinkStatus
from linkcrawl.net.errors import ConnectionFailed, TooManyRedirects
from linkcrawl.net.response import FetchResponse


@pytest.mark.parametrize("code, expected", [
    (200, LinkStatus.OK),
    (204, LinkStatus.OK),
    (301, LinkStatus.BROKEN),
    (399, LinkStatus.BROKEN),
    (400, LinkStatus.BROKEN),
    (404, LinkStatus.BROKEN),
    (429, LinkStatus.SKIPPED),
    (500, LinkStatus.BROKEN),
])
def test_status_codes(code, expected):
    status, _reason = classify(FetchResponse("u", status=code, attempts=1))
    assert status is expected


def test_accepted_status_is_ok():
    status, reason = classify(FetchResponse("u", status=403), accepted_statuses=[403])
    assert status is LinkStatus.OK
    assert "accepted" in reason


def test_network_error_is_broken_with_attempt_count():
    error = ConnectionFailed("u", "refused")
    status, reason = classify(FetchResponse("u", error=error, attempts=4))
    assert status is LinkStatus.BROKEN
    assert reason == "connection: refused after 4 attempt(s)"


def test_too_many_redirects():
    status, reason = classify(FetchResponse("u", error=TooManyRedirects("u", "loop")))
    assert status is LinkStatus.BROKEN
    assert reason == "too many redirects"


def test_unsupported_scheme_is_skipped(make_components):
    result = make_components().checker.check("ftp://example.com/file")
    assert result.skipped
    assert "unsupported scheme" in result.reason


def test_excluded_pattern_is_skipped(make_components):
    components = make_components(exclude_patterns=["*/private/*"], respect_robots=False)
    result = components.checker.check("https://example.com/private/x")
    assert result.skipped
    assert result.reason.startswith("excluded by pattern")


def test_external_link_skipped_when_check_external_off(make_components):
    components = make_components(start_urls=["https://example.com/"],
                                 check_external=False, respect_robots=False)
    assert components.checker.check("https://other.example/").skipped


def test_head_rejected_falls_back_to_get(make_components):
    url = "https://example.com/nohead"
    components = make_components(routes={url: [(405, {}, b""), (200, {}, b"")]},
                                 respect_robots=False)
    assert components.checker.check(url).ok
    assert components.opener.count(url, "GET") == 1
