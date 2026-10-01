"""Environment-variable overrides.

Each variable below overrides one setting. Values are parsed by the field's
parser in linkcrawl.config.schema, so LINKCRAWL_RESPECT_ROBOTS=no is False.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Mapping, Optional

from linkcrawl.config.schema import coerce
from linkcrawl.core.errors import ConfigError

ENV_PREFIX = "LINKCRAWL_"

ENV_VARS: Dict[str, str] = {
    "LINKCRAWL_TIMEOUT": "timeout",
    "LINKCRAWL_CONNECT_TIMEOUT": "connect_timeout",
    "LINKCRAWL_MAX_ATTEMPTS": "max_attempts",
    "LINKCRAWL_BACKOFF_BASE": "backoff_base",
    "LINKCRAWL_BACKOFF_MAX": "backoff_max",
    "LINKCRAWL_RATE_LIMIT": "rate_limit",
    "LINKCRAWL_RESPECT_ROBOTS": "respect_robots",
    "LINKCRAWL_USER_AGENT": "user_agent",
    "LINKCRAWL_MAX_DEPTH": "max_depth",
    "LINKCRAWL_CACHE_TTL": "cache_ttl",
    "LINKCRAWL_CACHE_PATH": "cache_path",
    "LINKCRAWL_FORMAT": "report_format",
    "LINKCRAWL_PLUGINS": "plugins",
}

CONFIG_PATH_VAR = "LINKCRAWL_CONFIG"
DISABLE_VAR = "LINKCRAWL_NO_ENV"


def read_env_overrides(environ: Optional[Mapping[str, str]] = None) -> Dict[str, Any]:
    """Return the settings that the environment overrides, already parsed."""
    env = os.environ if environ is None else environ
    if env.get(DISABLE_VAR):
        return {}
    overrides: Dict[str, Any] = {}
    for var, field_name in ENV_VARS.items():
        raw = env.get(var)
        if raw is None or raw == "":
            continue
        try:
            overrides[field_name] = coerce(field_name, raw)
        except ValueError as error:
            raise ConfigError(str(error), source="environment", key=var) from error
    return overrides


def config_path_from_env(environ: Optional[Mapping[str, str]] = None) -> Optional[str]:
    env = os.environ if environ is None else environ
    value = env.get(CONFIG_PATH_VAR)
    return value or None


def unknown_env_vars(environ: Optional[Mapping[str, str]] = None) -> Dict[str, str]:
    """Variables with the linkcrawl prefix that no setting reads (likely typos)."""
    env = os.environ if environ is None else environ
    known = set(ENV_VARS) | {CONFIG_PATH_VAR, DISABLE_VAR}
    return {key: value for key, value in env.items()
            if key.startswith(ENV_PREFIX) and key not in known}
