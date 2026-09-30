import random
import urllib.error
import socket

from linkcrawl.net.backoff import ExponentialBackoff
from linkcrawl.net.errors import DnsFailure, TimeoutExceeded
from linkcrawl.net.response import FetchResponse
from linkcrawl.net.retry import RetryPolicy


def test_backoff_doubles_and_caps():
    backoff = ExponentialBackoff(base=0.5, multiplier=2.0, maximum=3.0)
    assert backoff.schedule(6) == [0.5, 1.0, 2.0, 3.0, 3.0]


def test_jitter_stays_within_spread():
    backoff = ExponentialBackoff(1.0, 2.0, 30.0, jitter=0.1, rng=random.Random(7))
    for attempt in range(1, 5):
        raw = backoff.raw_delay(attempt)
        assert raw * 0.9 <= backoff.delay(attempt) <= raw * 1.1


def _policy(attempts=4, sleeps=None):
    return RetryPolicy(attempts, ExponentialBackoff(0.5, 2.0, 30.0),
                       sleep=(sleeps.append if sleeps is not None else lambda s: None))


def test_retries_503_until_success():
    sleeps = []
    responses = iter([FetchResponse("u", status=503), FetchResponse("u", status=503),
                      FetchResponse("u", status=200)])
    result = _policy(sleeps=sleeps).execute(lambda attempt: next(responses))
    assert result.status == 200
    assert result.attempts == 3
    assert sleeps == [0.5, 1.0]


def test_404_is_not_retried():
    calls = []
    result = _policy().execute(lambda attempt: calls.append(attempt) or FetchResponse("u", status=404))
    assert calls == [1]
    assert result.attempts == 1


def test_gives_up_after_max_attempts():
    error = TimeoutExceeded("u", "timed out")
    result = _policy(attempts=3).execute(lambda attempt: FetchResponse("u", error=error))
    assert result.attempts == 3
    assert result.error is error


def test_dns_failure_is_not_retried():
    error = DnsFailure("u", "nope")
    result = _policy().execute(lambda attempt: FetchResponse("u", error=error))
    assert result.attempts == 1


def test_retry_after_is_honoured_up_to_backoff_max():
    policy = _policy()
    response = FetchResponse("u", status=429, headers={"Retry-After": "12"})
    assert policy.delay_for(1, response) == 12.0
    response = FetchResponse("u", status=429, headers={"Retry-After": "600"})
    assert policy.delay_for(1, response) == 30.0


def test_client_retries_through_fake_opener(make_components):
    url = "https://example.com/flaky"
    components = make_components(routes={
        url: [(503, {}, b""), (503, {}, b""), (200, {}, b"")],
    }, respect_robots=False)
    response = components.client.check(url)
    assert response.status == 200
    assert response.attempts == 3
    assert components.opener.count(url, "HEAD") == 3


def test_client_maps_socket_timeout(make_components):
    url = "https://example.com/slow"
    components = make_components(routes={url: urllib.error.URLError(socket.timeout())},
                                 respect_robots=False, max_attempts=2)
    response = components.client.check(url)
    assert isinstance(response.error, TimeoutExceeded)
    assert response.attempts == 2
