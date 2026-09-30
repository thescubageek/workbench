"""Map parsed command-line options onto setting names (the highest-precedence layer)."""

from __future__ import annotations

import argparse
from typing import Any, Dict

OPTION_TO_SETTING = {
    "timeout": "timeout",
    "connect_timeout": "connect_timeout",
    "max_attempts": "max_attempts",
    "backoff_base": "backoff_base",
    "rate_limit": "rate_limit",
    "respect_robots": "respect_robots",
    "cache_ttl": "cache_ttl",
    "cache_path": "cache_path",
    "exclude_patterns": "exclude_patterns",
    "include_patterns": "include_patterns",
    "accepted_statuses": "accepted_statuses",
    "plugins": "plugins",
    "report_format": "report_format",
    "fail_on_skipped": "fail_on_skipped",
    "max_depth": "max_depth",
    "max_pages": "max_pages",
    "check_external": "check_external",
}


def cli_overrides(args: argparse.Namespace) -> Dict[str, Any]:
    """Only options the user actually gave; None means 'not given'."""
    overrides: Dict[str, Any] = {}
    for option, setting in OPTION_TO_SETTING.items():
        value = getattr(args, option, None)
        if value is None:
            continue
        overrides[setting] = value
    if getattr(args, "no_cache", False):
        overrides["cache_ttl"] = 0
    return overrides
