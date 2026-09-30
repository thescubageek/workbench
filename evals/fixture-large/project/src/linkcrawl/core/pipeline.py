"""Composition root: build every component from one Settings object."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

from linkcrawl.config.settings import Settings
from linkcrawl.core.checker import LinkChecker
from linkcrawl.crawl.robots import AllowAllRobots, RobotsPolicy
from linkcrawl.crawl.scope import Scope
from linkcrawl.crawl.sitemap import SitemapReader
from linkcrawl.net.client import HttpClient
from linkcrawl.net.rate_limit import HostRateLimiter
from linkcrawl.plugins.builtin import register_builtins
from linkcrawl.plugins.loader import load_plugins
from linkcrawl.plugins.registry import HookRegistry
from linkcrawl.store.cache import ResultCache
from linkcrawl.store.clock import SystemClock


@dataclass
class Components:
    settings: Settings
    rate_limiter: HostRateLimiter
    client: HttpClient
    robots: object
    sitemaps: SitemapReader
    scope: Scope
    cache: ResultCache
    hooks: HookRegistry
    wall_clock: object = field(default_factory=SystemClock)
    checker: Optional[LinkChecker] = None

    def close(self) -> None:
        self.cache.flush()


def build_components(settings: Settings, start_urls: Iterable[str] = (),
                     client: Optional[HttpClient] = None,
                     cache: Optional[ResultCache] = None,
                     wall_clock=None) -> Components:
    clock = wall_clock or SystemClock()
    rate_limiter = HostRateLimiter.from_settings(settings)
    http = client or HttpClient.from_settings(settings, rate_limiter=rate_limiter)
    if client is not None:
        rate_limiter = client.rate_limiter
    robots = RobotsPolicy(http, settings.user_agent) if settings.respect_robots \
        else AllowAllRobots()
    hooks = HookRegistry()
    register_builtins(hooks, settings)
    load_plugins(hooks, settings.plugins)
    components = Components(
        settings=settings,
        rate_limiter=rate_limiter,
        client=http,
        robots=robots,
        sitemaps=SitemapReader(http),
        scope=Scope(start_urls, settings.include_patterns, settings.exclude_patterns),
        cache=cache or ResultCache.from_settings(settings, clock=clock),
        hooks=hooks,
        wall_clock=clock,
    )
    components.checker = LinkChecker(settings, components)
    return components
