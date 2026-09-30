"""Cache keys: a stable digest of the normalized URL."""

from __future__ import annotations

import hashlib

from linkcrawl.crawl.normalize import normalize_url

KEY_LENGTH = 32


def cache_key(url: str) -> str:
    digest = hashlib.sha256(normalize_url(url).encode("utf-8")).hexdigest()
    return digest[:KEY_LENGTH]
