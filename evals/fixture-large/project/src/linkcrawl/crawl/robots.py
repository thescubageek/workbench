"""robots.txt handling.

robots.txt is fetched once per origin with the shared HTTP client. A link that
robots.txt disallows for our user agent is not requested: it gets a SKIPPED
result. When robots.txt is missing (4xx) everything is allowed; when the server
fails (5xx or no response) everything on that origin is disallowed until the
next run.
"""

from __future__ import annotations

import urllib.robotparser
from typing import TYPE_CHECKING, Dict, Optional

from linkcrawl.core.result import CheckResult, skipped_result
from linkcrawl.crawl.normalize import origin

if TYPE_CHECKING:
    from linkcrawl.net.client import HttpClient

ROBOTS_PATH = "/robots.txt"
ROBOTS_MAX_BYTES = 512 * 1024
ROBOTS_SKIP_REASON = "disallowed by robots.txt"


class RobotsPolicy:
    def __init__(self, client: "HttpClient", user_agent: str):
        self.client = client
        self.user_agent = user_agent
        self._parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self.fetch_failures: Dict[str, str] = {}

    def _agent_token(self) -> str:
        return self.user_agent.split("/", 1)[0].strip() or "*"

    def _load(self, site: str) -> urllib.robotparser.RobotFileParser:
        parser = urllib.robotparser.RobotFileParser(site + ROBOTS_PATH)
        response, body = self.client.get_body(site + ROBOTS_PATH, ROBOTS_MAX_BYTES,
                                              timeouts=self.client.timeouts.for_robots())
        if response.error is not None:
            self.fetch_failures[site] = response.describe_error()
            parser.disallow_all = True
        elif response.status is not None and response.status >= 500:
            self.fetch_failures[site] = f"HTTP {response.status}"
            parser.disallow_all = True
        elif response.status is not None and response.status >= 400:
            parser.allow_all = True
        else:
            text = body.decode("utf-8", errors="replace")
            parser.parse(text.splitlines())
        return parser

    def parser_for(self, url: str) -> urllib.robotparser.RobotFileParser:
        site = origin(url)
        parser = self._parsers.get(site)
        if parser is None:
            parser = self._load(site)
            self._parsers[site] = parser
        return parser

    def is_allowed(self, url: str) -> bool:
        return self.parser_for(url).can_fetch(self._agent_token(), url)

    def crawl_delay(self, url: str) -> Optional[float]:
        delay = self.parser_for(url).crawl_delay(self._agent_token())
        return float(delay) if delay is not None else None

    def sitemaps(self, url: str):
        return list(self.parser_for(url).site_maps() or [])

    def skip_if_disallowed(self, url: str) -> Optional[CheckResult]:
        """A SKIPPED result when robots.txt disallows url, otherwise None."""
        if self.is_allowed(url):
            return None
        site = origin(url)
        reason = ROBOTS_SKIP_REASON
        if site in self.fetch_failures:
            reason = f"{ROBOTS_SKIP_REASON} (unavailable: {self.fetch_failures[site]})"
        return skipped_result(url, reason)


class AllowAllRobots:
    """Used when respect_robots is off."""

    def is_allowed(self, url: str) -> bool:
        return True

    def crawl_delay(self, url: str) -> Optional[float]:
        return None

    def sitemaps(self, url: str):
        return []

    def skip_if_disallowed(self, url: str) -> Optional[CheckResult]:
        return None
