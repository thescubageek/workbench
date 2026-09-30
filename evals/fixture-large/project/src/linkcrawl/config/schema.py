"""The schema of settings: name, parser, default and help text for each field.

Every layer (config file, environment, command line) produces raw values. The
parsers here turn those raw values into typed values, so each layer coerces
input the same way.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple

from linkcrawl.config import defaults

_TRUE_WORDS = frozenset({"1", "true", "yes", "on"})
_FALSE_WORDS = frozenset({"0", "false", "no", "off"})


def parse_bool(raw: Any) -> bool:
    if isinstance(raw, bool):
        return raw
    text = str(raw).strip().lower()
    if text in _TRUE_WORDS:
        return True
    if text in _FALSE_WORDS:
        return False
    raise ValueError(f"expected a boolean, got {raw!r}")


def parse_float(raw: Any) -> float:
    if isinstance(raw, bool):
        raise ValueError("expected a number, got a boolean")
    return float(raw)


def parse_int(raw: Any) -> int:
    if isinstance(raw, bool):
        raise ValueError("expected an integer, got a boolean")
    if isinstance(raw, float) and not raw.is_integer():
        raise ValueError(f"expected an integer, got {raw!r}")
    return int(raw)


def parse_str(raw: Any) -> str:
    return str(raw).strip()


def parse_str_list(raw: Any) -> Tuple[str, ...]:
    if isinstance(raw, (list, tuple)):
        items = [str(item).strip() for item in raw]
    else:
        items = [part.strip() for part in str(raw).split(",")]
    return tuple(item for item in items if item)


def parse_int_list(raw: Any) -> Tuple[int, ...]:
    return tuple(int(item) for item in parse_str_list(raw))


@dataclass(frozen=True)
class FieldSpec:
    name: str
    parse: Callable[[Any], Any]
    default: Any
    help: str


FIELDS: Tuple[FieldSpec, ...] = (
    FieldSpec("timeout", parse_float, defaults.DEFAULT_TIMEOUT_SECONDS,
              "read timeout per attempt, in seconds"),
    FieldSpec("connect_timeout", parse_float, defaults.DEFAULT_CONNECT_TIMEOUT_SECONDS,
              "connect timeout per attempt, in seconds"),
    FieldSpec("max_attempts", parse_int, defaults.DEFAULT_MAX_ATTEMPTS,
              "attempts per link, including the first"),
    FieldSpec("backoff_base", parse_float, defaults.DEFAULT_BACKOFF_BASE_SECONDS,
              "delay before the second attempt, in seconds"),
    FieldSpec("backoff_multiplier", parse_float, defaults.DEFAULT_BACKOFF_MULTIPLIER,
              "factor applied to the delay after each attempt"),
    FieldSpec("backoff_max", parse_float, defaults.DEFAULT_BACKOFF_MAX_SECONDS,
              "upper bound on any single delay, in seconds"),
    FieldSpec("backoff_jitter", parse_float, defaults.DEFAULT_BACKOFF_JITTER,
              "random spread applied to each delay, as a fraction"),
    FieldSpec("rate_limit", parse_float, defaults.DEFAULT_RATE_LIMIT_PER_HOST,
              "requests per second per host; 0 disables the limit"),
    FieldSpec("rate_burst", parse_int, defaults.DEFAULT_RATE_BURST,
              "requests a host may receive in a burst"),
    FieldSpec("respect_robots", parse_bool, defaults.DEFAULT_RESPECT_ROBOTS,
              "skip links that robots.txt disallows"),
    FieldSpec("user_agent", parse_str, defaults.DEFAULT_USER_AGENT,
              "User-Agent header and robots.txt agent name"),
    FieldSpec("max_depth", parse_int, defaults.DEFAULT_MAX_DEPTH,
              "how many links deep the crawler follows from a start URL"),
    FieldSpec("max_pages", parse_int, defaults.DEFAULT_MAX_PAGES,
              "stop the crawl after this many links"),
    FieldSpec("max_redirects", parse_int, defaults.DEFAULT_MAX_REDIRECTS,
              "redirects followed before a link counts as broken"),
    FieldSpec("max_body_bytes", parse_int, defaults.DEFAULT_MAX_BODY_BYTES,
              "largest page body read for link extraction"),
    FieldSpec("check_external", parse_bool, defaults.DEFAULT_CHECK_EXTERNAL,
              "check links that leave the start hosts"),
    FieldSpec("cache_ttl", parse_int, defaults.DEFAULT_CACHE_TTL_SECONDS,
              "seconds a cached OK result stays valid; 0 disables the cache"),
    FieldSpec("cache_path", parse_str, defaults.DEFAULT_CACHE_PATH,
              "file the result cache is kept in"),
    FieldSpec("report_format", parse_str, defaults.DEFAULT_REPORT_FORMAT,
              "text, json or junit"),
    FieldSpec("fail_on_skipped", parse_bool, defaults.DEFAULT_FAIL_ON_SKIPPED,
              "exit non-zero when any link was skipped"),
    FieldSpec("slow_threshold", parse_float, defaults.DEFAULT_SLOW_THRESHOLD_SECONDS,
              "responses slower than this are annotated as slow"),
    FieldSpec("include_patterns", parse_str_list, defaults.DEFAULT_INCLUDE_PATTERNS,
              "glob patterns a URL must match to be checked"),
    FieldSpec("exclude_patterns", parse_str_list, defaults.DEFAULT_EXCLUDE_PATTERNS,
              "glob patterns that make a URL skipped"),
    FieldSpec("accepted_statuses", parse_int_list, defaults.DEFAULT_ACCEPTED_STATUSES,
              "HTTP statuses counted as OK even when 400 or above"),
    FieldSpec("plugins", parse_str_list, defaults.DEFAULT_PLUGINS,
              "plugin setup functions, as module:function"),
)

FIELDS_BY_NAME: Dict[str, FieldSpec] = {spec.name: spec for spec in FIELDS}


def default_values() -> Dict[str, Any]:
    return {spec.name: spec.default for spec in FIELDS}


def coerce(name: str, raw: Any) -> Any:
    """Parse one raw value for the named field; raises KeyError or ValueError."""
    spec = FIELDS_BY_NAME[name]
    return spec.parse(raw)
