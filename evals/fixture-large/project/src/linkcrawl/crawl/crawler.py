"""The crawler: check each URL in the frontier and expand internal HTML pages."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Callable, Iterable, List, Optional

from linkcrawl.core.errors import CrawlAborted
from linkcrawl.core.result import CheckResult
from linkcrawl.crawl.depth import DepthLimit
from linkcrawl.crawl.frontier import Frontier
from linkcrawl.parse.dispatch import can_extract, extract_links

if TYPE_CHECKING:
    from linkcrawl.config.settings import Settings
    from linkcrawl.core.checker import LinkChecker
    from linkcrawl.core.pipeline import Components

ProgressCallback = Callable[[CheckResult, int], None]


class Crawler:
    def __init__(self, settings: "Settings", components: "Components",
                 progress: Optional[ProgressCallback] = None):
        self.settings = settings
        self.components = components
        self.checker: "LinkChecker" = components.checker
        self.frontier = Frontier()
        self.depth = DepthLimit(settings.max_depth)
        self.progress = progress
        self.pages_expanded = 0
        self.started_at = 0.0

    def seed(self, urls: Iterable[str]) -> int:
        added = 0
        for url in urls:
            self.components.scope.add_start(url)
            if self.frontier.push(url, depth=0):
                added += 1
        return added

    def seed_from_sitemap(self, sitemap_url: str) -> int:
        return self.seed(self.components.sitemaps.read(sitemap_url))

    def run(self) -> List[CheckResult]:
        self.started_at = time.monotonic()
        results: List[CheckResult] = []
        try:
            while self.frontier and len(results) < self.settings.max_pages:
                item = self.frontier.pop()
                result = self.checker.check(item.url, parent=item.parent, depth=item.depth)
                results.append(result)
                if self.progress is not None:
                    self.progress(result, len(self.frontier))
                if self._should_expand(result):
                    self._expand(result)
        except KeyboardInterrupt as interrupt:
            raise CrawlAborted("interrupted", results) from interrupt
        return results

    def _should_expand(self, result: CheckResult) -> bool:
        if not result.ok:
            return False
        if not self.depth.can_expand(result.depth):
            return False
        return self.components.scope.is_internal(result.url)

    def _expand(self, result: CheckResult) -> None:
        self._apply_crawl_delay(result.url)
        response, body = self.components.client.get_body(result.url,
                                                          self.settings.max_body_bytes)
        if not response.transport_ok or not can_extract(response.content_type, result.url):
            return
        self.pages_expanded += 1
        base = response.final_url or result.url
        child_depth = self.depth.child_depth(result.depth)
        for link in extract_links(body, response.content_type, base):
            if self.depth.allows(child_depth):
                self.frontier.push(link.url, depth=child_depth, parent=result.url)

    def _apply_crawl_delay(self, url: str) -> None:
        delay = self.components.robots.crawl_delay(url)
        if delay:
            self.components.rate_limiter.set_min_interval(url, delay)


def crawl(settings: "Settings", components: "Components", start_urls: Iterable[str],
          sitemap: Optional[str] = None,
          progress: Optional[ProgressCallback] = None) -> List[CheckResult]:
    crawler = Crawler(settings, components, progress=progress)
    crawler.seed(start_urls)
    if sitemap:
        crawler.seed_from_sitemap(sitemap)
    return crawler.run()
