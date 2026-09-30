"""Range and consistency checks on a fully resolved Settings object."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from linkcrawl.core.errors import ConfigError

if TYPE_CHECKING:
    from linkcrawl.config.settings import Settings

MIN_TIMEOUT_SECONDS = 0.1
MAX_TIMEOUT_SECONDS = 300.0
MAX_ATTEMPTS_LIMIT = 10
REPORT_FORMATS = ("text", "json", "junit")


def collect_problems(settings: "Settings") -> List[str]:
    problems: List[str] = []
    for name in ("timeout", "connect_timeout"):
        value = getattr(settings, name)
        if not MIN_TIMEOUT_SECONDS <= value <= MAX_TIMEOUT_SECONDS:
            problems.append(
                f"{name} must be between {MIN_TIMEOUT_SECONDS} and "
                f"{MAX_TIMEOUT_SECONDS} seconds, got {value}")
    if not 1 <= settings.max_attempts <= MAX_ATTEMPTS_LIMIT:
        problems.append(
            f"max_attempts must be between 1 and {MAX_ATTEMPTS_LIMIT}, "
            f"got {settings.max_attempts}")
    if settings.backoff_base < 0:
        problems.append("backoff_base must not be negative")
    if settings.backoff_multiplier < 1:
        problems.append("backoff_multiplier must be at least 1")
    if settings.backoff_max < settings.backoff_base:
        problems.append("backoff_max must not be smaller than backoff_base")
    if not 0 <= settings.backoff_jitter < 1:
        problems.append("backoff_jitter must be in [0, 1)")
    if settings.rate_limit < 0:
        problems.append("rate_limit must not be negative (use 0 to disable)")
    if settings.rate_burst < 1:
        problems.append("rate_burst must be at least 1")
    if settings.max_depth < 0:
        problems.append("max_depth must not be negative")
    if settings.max_pages < 1:
        problems.append("max_pages must be at least 1")
    if settings.max_redirects < 0:
        problems.append("max_redirects must not be negative")
    if settings.cache_ttl < 0:
        problems.append("cache_ttl must not be negative (use 0 to disable)")
    if settings.report_format not in REPORT_FORMATS:
        problems.append(
            f"report_format must be one of {', '.join(REPORT_FORMATS)}, "
            f"got {settings.report_format!r}")
    for code in settings.accepted_statuses:
        if not 100 <= code <= 599:
            problems.append(f"accepted_statuses has an invalid HTTP status {code}")
    for spec in settings.plugins:
        if ":" not in spec:
            problems.append(f"plugin {spec!r} must be written as module:function")
    return problems


def validate_settings(settings: "Settings") -> None:
    problems = collect_problems(settings)
    if problems:
        raise ConfigError("; ".join(problems), source="settings")
