"""Shared fixtures: an in-memory urllib opener so no test touches the network."""

from __future__ import annotations

import email.message
import io
import urllib.error

import pytest

from linkcrawl.config.settings import resolve_settings
from linkcrawl.core.pipeline import build_components
from linkcrawl.net.backoff import ExponentialBackoff
from linkcrawl.net.client import HttpClient
from linkcrawl.net.rate_limit import NullRateLimiter
from linkcrawl.net.retry import RetryPolicy
from linkcrawl.net.timeouts import Timeouts
from linkcrawl.store.cache import ResultCache
from linkcrawl.store.clock import FixedClock
from linkcrawl.store.json_store import MemoryStore


def _message(headers):
    message = email.message.Message()
    for key, value in (headers or {}).items():
        message[key] = value
    return message


class FakeHandle:
    def __init__(self, url, status, headers, body):
        self.status = status
        self.headers = _message(headers)
        self._url = url
        self._body = io.BytesIO(body)

    def geturl(self):
        return self._url

    def read(self, size=-1):
        return self._body.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeOpener:
    """routes maps URL -> (status, headers, body), an exception, or a list of those
    consumed one per request (the last one repeats)."""

    def __init__(self, routes=None):
        self.routes = dict(routes or {})
        self.calls = []

    def count(self, url, method=None):
        return sum(1 for m, u, _ in self.calls if u == url and (method is None or m == method))

    def open(self, request, timeout=None):
        url = request.full_url
        method = request.get_method()
        self.calls.append((method, url, timeout))
        route = self.routes.get(url, (404, {}, b"not found"))
        if isinstance(route, list):
            route = route.pop(0) if len(route) > 1 else route[0]
        if isinstance(route, BaseException):
            raise route
        status, headers, body = route
        if status >= 400:
            raise urllib.error.HTTPError(url, status, "error", _message(headers),
                                         io.BytesIO(body))
        return FakeHandle(url, status, headers, body)


def html(body, status=200):
    return (status, {"Content-Type": "text/html; charset=utf-8"}, body.encode("utf-8"))


@pytest.fixture
def make_settings(tmp_path):
    def factory(**overrides):
        return resolve_settings(overrides, environ={}, cwd=str(tmp_path))
    return factory


@pytest.fixture
def clock():
    return FixedClock()


@pytest.fixture
def make_components(make_settings, clock):
    def factory(routes=None, start_urls=(), store=None, **overrides):
        settings = make_settings(**overrides)
        opener = FakeOpener(routes)
        sleeps = []
        client = HttpClient(
            timeouts=Timeouts.from_settings(settings),
            retry=RetryPolicy(settings.max_attempts,
                              ExponentialBackoff.from_settings(settings),
                              sleep=sleeps.append),
            rate_limiter=NullRateLimiter(),
            user_agent=settings.user_agent,
            opener=opener,
        )
        cache = ResultCache(store or MemoryStore(), settings.cache_ttl, clock=clock)
        components = build_components(settings, start_urls=start_urls, client=client,
                                      cache=cache, wall_clock=clock)
        components.opener = opener
        components.sleeps = sleeps
        return components
    return factory
