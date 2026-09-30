"""Config-file loading.

Two formats are read: an INI file with a [linkcrawl] section, and a JSON file
holding one object. The first file found in CONFIG_FILENAMES wins, unless a
path is given explicitly.
"""

from __future__ import annotations

import configparser
import json
import os
from typing import Any, Dict, Optional

from linkcrawl.config.schema import FIELDS_BY_NAME, coerce
from linkcrawl.core.errors import ConfigError

CONFIG_FILENAMES = ("linkcrawl.ini", ".linkcrawl.json", "setup.cfg")
INI_SECTION = "linkcrawl"


def find_config_file(cwd: Optional[str] = None) -> Optional[str]:
    base = cwd or os.getcwd()
    for name in CONFIG_FILENAMES:
        candidate = os.path.join(base, name)
        if not os.path.isfile(candidate):
            continue
        if name == "setup.cfg" and not _ini_has_section(candidate):
            continue
        return candidate
    return None


def _ini_has_section(path: str) -> bool:
    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
    except configparser.Error:
        return False
    return parser.has_section(INI_SECTION)


def load_config_file(path: Optional[str] = None, cwd: Optional[str] = None) -> Dict[str, Any]:
    """Return parsed settings from a config file, or {} when there is none."""
    resolved = path or find_config_file(cwd)
    if resolved is None:
        return {}
    if not os.path.isfile(resolved):
        raise ConfigError("config file not found", source=resolved)
    if resolved.endswith(".json"):
        raw = _read_json(resolved)
    else:
        raw = _read_ini(resolved)
    return _coerce_all(raw, resolved)


def _read_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as error:
        raise ConfigError(f"cannot read JSON config: {error}", source=path) from error
    if not isinstance(data, dict):
        raise ConfigError("top level must be an object", source=path)
    section = data.get(INI_SECTION, data)
    if not isinstance(section, dict):
        raise ConfigError(f"'{INI_SECTION}' must be an object", source=path)
    return section


def _read_ini(path: str) -> Dict[str, Any]:
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with open(path, encoding="utf-8") as handle:
            parser.read_file(handle)
    except (OSError, configparser.Error) as error:
        raise ConfigError(f"cannot read INI config: {error}", source=path) from error
    if not parser.has_section(INI_SECTION):
        return {}
    return dict(parser.items(INI_SECTION))


def _coerce_all(raw: Dict[str, Any], source: str) -> Dict[str, Any]:
    values: Dict[str, Any] = {}
    for key, value in raw.items():
        name = key.strip().lower().replace("-", "_")
        if name not in FIELDS_BY_NAME:
            raise ConfigError("unknown setting", source=source, key=key)
        try:
            values[name] = coerce(name, value)
        except ValueError as error:
            raise ConfigError(str(error), source=source, key=key) from error
    return values
