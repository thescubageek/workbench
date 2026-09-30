"""The per-link checker: the decision sequence that gives every link its status.

Order of checks for one URL:
  1. unsupported scheme          -> SKIPPED
  2. exclude / include patterns  -> SKIPPED
  3. external link, if check_external is off -> SKIPPED
  4. robots.txt disallow, if respect_robots is on -> SKIPPED
  5. fresh cache entry           -> the cached result, no request
  6. HTTP check (with retries)   -> classify() decides OK / BROKEN / SKIPPED
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from linkcrawl.core.classify import classify
from linkcrawl.core.result import CheckResult, ResultSource, skipped_result
from linkcrawl.crawl.normalize import normalize_url
from linkcrawl.crawl.scope import EXTERNAL_REASON
from linkcrawl.plugins.hooks import AFTER_CHECK, BEFORE_CHECK

if TYPE_CHECKING:
    from linkcrawl.config.settings import Settings
    from linkcrawl.core.pipeline import Components

SUPPORTED_SCHEMES = ("http", "https")


class LinkChecker:
    def __init__(self, settings: "Settings", components: "Components"):
        self.settings = settings
        self.components = components
        self.checked = 0

    def check(self, url: str, parent: Optional[str] = None, depth: int = 0) -> CheckResult:
        target = normalize_url(url)
        hooks = self.components.hooks
        override = hooks.first(BEFORE_CHECK, url=target, settings=self.settings)
        if isinstance(override, CheckResult):
            result = override
        else:
            result = self._decide(target)
        result = result.with_context(parent, depth)
        result = hooks.transform(AFTER_CHECK, result, settings=self.settings)
        self.checked += 1
        return result

    def _decide(self, url: str) -> CheckResult:
        scheme = url.split(":", 1)[0].lower()
        if scheme not in SUPPORTED_SCHEMES:
            return skipped_result(url, f"unsupported scheme {scheme!r}")
        scope = self.components.scope
        exclusion = scope.exclusion_reason(url)
        if exclusion is not None:
            return skipped_result(url, exclusion)
        if not self.settings.check_external and not scope.is_internal(url):
            return skipped_result(url, EXTERNAL_REASON)
        if self.settings.respect_robots:
            verdict = self.components.robots.skip_if_disallowed(url)
            if verdict is not None:
                return verdict
        cached = self.components.cache.get(url)
        if cached is not None:
            return cached
        return self._check_network(url)

    def _check_network(self, url: str) -> CheckResult:
        response = self.components.client.check(url)
        status, reason = classify(response, self.settings.accepted_statuses)
        result = CheckResult(
            url=url,
            status=status,
            http_status=response.status,
            reason=reason,
            source=ResultSource.NETWORK,
            attempts=response.attempts,
            elapsed_seconds=response.elapsed_seconds,
            checked_at=self.components.wall_clock.now(),
        )
        self.components.cache.put(result)
        return result
