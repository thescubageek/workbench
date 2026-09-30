"""URL normalization, so that one resource is checked and cached once."""

from __future__ import annotations

import posixpath
from typing import Optional
from urllib.parse import parse_qsl, quote, unquote, urlencode, urljoin, urlsplit, urlunsplit

DEFAULT_PORTS = {"http": 80, "https": 443}
TRACKING_PARAM_PREFIXES = ("utm_",)
TRACKING_PARAMS = frozenset({"fbclid", "gclid", "mc_cid", "mc_eid"})
_SAFE_PATH_CHARS = "/:@!$&'()*+,;=-._~%"


def resolve(base: str, href: str) -> str:
    return urljoin(base, href.strip())


def _clean_path(path: str) -> str:
    if not path:
        return "/"
    trailing = path.endswith("/")
    collapsed = posixpath.normpath(path)
    if collapsed == ".":
        collapsed = "/"
    if trailing and not collapsed.endswith("/"):
        collapsed += "/"
    if not collapsed.startswith("/"):
        collapsed = "/" + collapsed
    return quote(unquote(collapsed), safe=_SAFE_PATH_CHARS)


def _clean_query(query: str) -> str:
    pairs = [(key, value) for key, value in parse_qsl(query, keep_blank_values=True)
             if not _is_tracking(key)]
    pairs.sort()
    return urlencode(pairs)


def _is_tracking(key: str) -> bool:
    lowered = key.lower()
    return lowered in TRACKING_PARAMS or lowered.startswith(TRACKING_PARAM_PREFIXES)


def normalize_url(url: str, base: Optional[str] = None) -> str:
    """Absolute, lower-cased scheme and host, no default port, no fragment,
    tracking parameters removed and the remaining query sorted."""
    absolute = resolve(base, url) if base else url.strip()
    parts = urlsplit(absolute)
    scheme = parts.scheme.lower()
    if scheme not in DEFAULT_PORTS:
        return absolute
    host = (parts.hostname or "").lower().rstrip(".")
    port = parts.port
    netloc = host
    if port is not None and port != DEFAULT_PORTS[scheme]:
        netloc = f"{host}:{port}"
    if parts.username:
        credentials = parts.username
        if parts.password:
            credentials += f":{parts.password}"
        netloc = f"{credentials}@{netloc}"
    return urlunsplit((scheme, netloc, _clean_path(parts.path), _clean_query(parts.query), ""))


def origin(url: str) -> str:
    parts = urlsplit(normalize_url(url))
    return f"{parts.scheme}://{parts.netloc}"


def host(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def is_http(url: str) -> bool:
    return urlsplit(url).scheme.lower() in DEFAULT_PORTS
