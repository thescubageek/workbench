"""The resolved Settings object and the function that builds it.

Layers are applied in LAYER_ORDER; a later layer overrides an earlier one.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Optional, Tuple

from linkcrawl.config.env import config_path_from_env, read_env_overrides
from linkcrawl.config.file_loader import load_config_file
from linkcrawl.config.schema import FIELDS_BY_NAME, default_values
from linkcrawl.config.validation import validate_settings
from linkcrawl.core.errors import ConfigError

LAYER_ORDER = ("defaults", "file", "environment", "command line")


@dataclass(frozen=True)
class Settings:
    timeout: float
    connect_timeout: float
    max_attempts: int
    backoff_base: float
    backoff_multiplier: float
    backoff_max: float
    backoff_jitter: float
    rate_limit: float
    rate_burst: int
    respect_robots: bool
    user_agent: str
    max_depth: int
    max_pages: int
    max_redirects: int
    max_body_bytes: int
    check_external: bool
    cache_ttl: int
    cache_path: str
    report_format: str
    fail_on_skipped: bool
    slow_threshold: float
    include_patterns: Tuple[str, ...]
    exclude_patterns: Tuple[str, ...]
    accepted_statuses: Tuple[int, ...]
    plugins: Tuple[str, ...]

    @property
    def cache_enabled(self) -> bool:
        return self.cache_ttl > 0

    @property
    def rate_limit_enabled(self) -> bool:
        return self.rate_limit > 0

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def replace(self, **changes: Any) -> "Settings":
        values = self.as_dict()
        values.update(changes)
        updated = Settings(**values)
        validate_settings(updated)
        return updated


@dataclass(frozen=True)
class ResolvedSettings:
    settings: Settings
    origins: Dict[str, str]
    config_path: Optional[str]


def resolve_settings(cli_overrides: Optional[Mapping[str, Any]] = None,
                     environ: Optional[Mapping[str, str]] = None,
                     config_path: Optional[str] = None,
                     cwd: Optional[str] = None) -> Settings:
    return resolve_with_origins(cli_overrides, environ, config_path, cwd).settings


def resolve_with_origins(cli_overrides: Optional[Mapping[str, Any]] = None,
                         environ: Optional[Mapping[str, str]] = None,
                         config_path: Optional[str] = None,
                         cwd: Optional[str] = None) -> ResolvedSettings:
    """Merge every layer and record which layer set each value."""
    path = config_path or config_path_from_env(environ)
    layers = (
        ("defaults", default_values()),
        ("file", load_config_file(path, cwd)),
        ("environment", read_env_overrides(environ)),
        ("command line", _clean_cli(cli_overrides or {})),
    )
    values: Dict[str, Any] = {}
    origins: Dict[str, str] = {}
    for layer_name, layer_values in layers:
        for key, value in layer_values.items():
            values[key] = value
            origins[key] = layer_name
    settings = Settings(**values)
    validate_settings(settings)
    return ResolvedSettings(settings=settings, origins=origins, config_path=path)


def _clean_cli(overrides: Mapping[str, Any]) -> Dict[str, Any]:
    cleaned: Dict[str, Any] = {}
    for key, value in overrides.items():
        if value is None:
            continue
        if key not in FIELDS_BY_NAME:
            raise ConfigError("unknown setting", source="command line", key=key)
        cleaned[key] = FIELDS_BY_NAME[key].parse(value)
    return cleaned
