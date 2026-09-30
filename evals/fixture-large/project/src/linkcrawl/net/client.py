"""The HTTP client: one wrapper over urllib used for every request linkcrawl makes.

check() sends HEAD first and falls back to GET when the server rejects HEAD.
Every attempt goes through the host rate limiter; the retry policy decides
whether a failed attempt is repeated.
"""

from __future__ import annotations

import socket
import time
import urllib.error
import urllib.request
from typing import TYPE_CHECKING, Callable, Dict, Optional, Tuple

from linkcrawl.net.errors import (ConnectionFailed, DnsFailure, InvalidUrl, NetworkError,
                                  TimeoutExceeded, TooManyRedirects)
from linkcrawl.net.rate_limit import HostRateLimiter
from linkcrawl.net.response import FetchResponse
from linkcrawl.net.retry import RetryPolicy
from linkcrawl.net.timeouts import Timeouts

if TYPE_CHECKING:
    from linkcrawl.config.settings import Settings

METHOD_FALLBACK_STATUSES = frozenset({403, 405, 501})
READ_CHUNK_BYTES = 64 * 1024


class _LimitedRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, max_redirects: int):
        super().__init__()
        self.max_redirections = max_redirects
        self.max_repeats = min(self.max_repeats, max_redirects or 1)

    def http_error_302(self, req, fp, code, msg, headers):
        visited = getattr(req, "redirect_dict", {})
        if len(visited) >= self.max_redirections:
            raise TooManyRedirects(req.full_url, f"more than {self.max_redirections} redirects")
        return super().http_error_302(req, fp, code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


def build_opener(max_redirects: int) -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(_LimitedRedirectHandler(max_redirects))


class HttpClient:
    def __init__(self, timeouts: Timeouts, retry: RetryPolicy, rate_limiter: HostRateLimiter,
                 user_agent: str, max_redirects: int = 5,
                 opener: Optional[urllib.request.OpenerDirector] = None,
                 clock: Callable[[], float] = time.monotonic):
        self.timeouts = timeouts
        self.retry = retry
        self.rate_limiter = rate_limiter
        self.user_agent = user_agent
        self.max_redirects = max_redirects
        self._opener = opener or build_opener(max_redirects)
        self._clock = clock
        self.requests_sent = 0

    @classmethod
    def from_settings(cls, settings: "Settings",
                      rate_limiter: Optional[HostRateLimiter] = None) -> "HttpClient":
        return cls(timeouts=Timeouts.from_settings(settings),
                   retry=RetryPolicy.from_settings(settings),
                   rate_limiter=rate_limiter or HostRateLimiter.from_settings(settings),
                   user_agent=settings.user_agent,
                   max_redirects=settings.max_redirects)

    def check(self, url: str) -> FetchResponse:
        """Status of url: HEAD, then GET if the server does not accept HEAD."""
        response = self.fetch(url, method="HEAD")
        if response.status in METHOD_FALLBACK_STATUSES:
            response = self.fetch(url, method="GET", max_bytes=0)
        return response

    def fetch(self, url: str, method: str = "GET", max_bytes: int = 0,
              timeouts: Optional[Timeouts] = None) -> FetchResponse:
        chosen = timeouts or self.timeouts
        return self.retry.execute(
            lambda attempt: self._attempt(url, method, max_bytes, chosen))

    def get_body(self, url: str, max_bytes: int,
                 timeouts: Optional[Timeouts] = None) -> Tuple[FetchResponse, bytes]:
        response = self.fetch(url, method="GET", max_bytes=max_bytes, timeouts=timeouts)
        return response, response.body

    def _request(self, url: str, method: str) -> urllib.request.Request:
        headers = {"User-Agent": self.user_agent, "Accept": "*/*"}
        return urllib.request.Request(url, method=method, headers=headers)

    def _attempt(self, url: str, method: str, max_bytes: int,
                 timeouts: Timeouts) -> FetchResponse:
        self.rate_limiter.acquire(url)
        started = self._clock()
        self.requests_sent += 1
        try:
            request = self._request(url, method)
        except ValueError as error:
            return self._failed(url, method, InvalidUrl(url, str(error)), started)
        try:
            with self._opener.open(request, timeout=timeouts.socket_timeout()) as handle:
                body = _read_limited(handle, max_bytes) if max_bytes else b""
                return FetchResponse(url=url, status=handle.status,
                                     final_url=handle.geturl(),
                                     headers=_headers(handle.headers),
                                     elapsed_seconds=self._clock() - started,
                                     method=method, body=body)
        except urllib.error.HTTPError as error:
            return FetchResponse(url=url, status=error.code, final_url=error.geturl(),
                                 headers=_headers(error.headers),
                                 elapsed_seconds=self._clock() - started, method=method)
        except TooManyRedirects as error:
            return self._failed(url, method, error, started)
        except urllib.error.URLError as error:
            return self._failed(url, method, _classify_url_error(url, error), started)
        except (socket.timeout, TimeoutError):
            return self._failed(url, method,
                                TimeoutExceeded(url, f"no response in {timeouts.socket_timeout()}s"),
                                started)
        except (ConnectionError, OSError) as error:
            return self._failed(url, method, ConnectionFailed(url, str(error)), started)

    def _failed(self, url: str, method: str, error: NetworkError,
                started: float) -> FetchResponse:
        return FetchResponse(url=url, error=error, method=method,
                             elapsed_seconds=self._clock() - started)


def _classify_url_error(url: str, error: urllib.error.URLError) -> NetworkError:
    reason = error.reason
    if isinstance(reason, (socket.timeout, TimeoutError)):
        return TimeoutExceeded(url, "timed out")
    if isinstance(reason, socket.gaierror):
        return DnsFailure(url, f"cannot resolve host: {reason}")
    if isinstance(reason, TooManyRedirects):
        return reason
    return ConnectionFailed(url, str(reason))


def _headers(message) -> Dict[str, str]:
    if message is None:
        return {}
    return {key: value for key, value in message.items()}


def _read_limited(handle, max_bytes: int) -> bytes:
    chunks = []
    remaining = max_bytes
    while remaining > 0:
        chunk = handle.read(min(READ_CHUNK_BYTES, remaining))
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)
