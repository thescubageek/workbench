"""Networking: an HTTP client over urllib with retries, backoff and rate limits."""

from linkcrawl.net.client import HttpClient
from linkcrawl.net.response import FetchResponse

__all__ = ["FetchResponse", "HttpClient"]
