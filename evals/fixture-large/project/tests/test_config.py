import json

import pytest

from linkcrawl.config import defaults
from linkcrawl.config.env import read_env_overrides, unknown_env_vars
from linkcrawl.config.file_loader import find_config_file, load_config_file
from linkcrawl.config.settings import resolve_settings, resolve_with_origins
from linkcrawl.core.errors import ConfigError


def test_defaults_apply_when_nothing_overrides(tmp_path):
    settings = resolve_settings(environ={}, cwd=str(tmp_path))
    assert settings.timeout == defaults.DEFAULT_TIMEOUT_SECONDS
    assert settings.max_attempts == defaults.DEFAULT_MAX_ATTEMPTS
    assert settings.respect_robots is True
    assert settings.cache_ttl == defaults.DEFAULT_CACHE_TTL_SECONDS


def test_env_overrides_are_parsed_by_field_type():
    values = read_env_overrides({
        "LINKCRAWL_TIMEOUT": "2.5",
        "LINKCRAWL_MAX_ATTEMPTS": "2",
        "LINKCRAWL_RESPECT_ROBOTS": "off",
        "LINKCRAWL_PLUGINS": "a.b:setup, c.d:setup",
    })
    assert values == {
        "timeout": 2.5,
        "max_attempts": 2,
        "respect_robots": False,
        "plugins": ("a.b:setup", "c.d:setup"),
    }


def test_env_override_with_bad_value_names_the_variable():
    with pytest.raises(ConfigError, match="LINKCRAWL_MAX_ATTEMPTS"):
        read_env_overrides({"LINKCRAWL_MAX_ATTEMPTS": "many"})


def test_env_can_be_disabled():
    assert read_env_overrides({"LINKCRAWL_TIMEOUT": "1", "LINKCRAWL_NO_ENV": "1"}) == {}


def test_unknown_prefixed_variables_are_reported():
    assert unknown_env_vars({"LINKCRAWL_TIMEOUTS": "1", "HOME": "/"}) == {
        "LINKCRAWL_TIMEOUTS": "1"}


def test_ini_file_is_found_and_loaded(tmp_path):
    (tmp_path / "linkcrawl.ini").write_text("[linkcrawl]\ntimeout = 4\ncache-ttl = 60\n")
    assert find_config_file(str(tmp_path)).endswith("linkcrawl.ini")
    assert load_config_file(cwd=str(tmp_path)) == {"timeout": 4.0, "cache_ttl": 60}


def test_json_file_with_unknown_key_is_rejected(tmp_path):
    path = tmp_path / ".linkcrawl.json"
    path.write_text(json.dumps({"timeout": 3, "tiemout": 4}))
    with pytest.raises(ConfigError, match="tiemout"):
        load_config_file(str(path))


def test_setup_cfg_without_section_is_ignored(tmp_path):
    (tmp_path / "setup.cfg").write_text("[metadata]\nname = x\n")
    assert find_config_file(str(tmp_path)) is None


def test_precedence_is_defaults_file_env_cli(tmp_path):
    (tmp_path / "linkcrawl.ini").write_text(
        "[linkcrawl]\ntimeout = 4\nmax_attempts = 3\nrate_limit = 1\n")
    resolved = resolve_with_origins(
        cli_overrides={"timeout": 1.5},
        environ={"LINKCRAWL_MAX_ATTEMPTS": "2"},
        cwd=str(tmp_path))
    assert resolved.settings.timeout == 1.5
    assert resolved.settings.max_attempts == 2
    assert resolved.settings.rate_limit == 1.0
    assert resolved.origins["timeout"] == "command line"
    assert resolved.origins["max_attempts"] == "environment"
    assert resolved.origins["rate_limit"] == "file"
    assert resolved.origins["user_agent"] == "defaults"


def test_validation_collects_every_problem(tmp_path):
    with pytest.raises(ConfigError) as info:
        resolve_settings({"max_attempts": 0, "timeout": 0}, environ={}, cwd=str(tmp_path))
    message = str(info.value)
    assert "max_attempts" in message
    assert "timeout" in message


def test_replace_revalidates(make_settings):
    settings = make_settings()
    assert settings.replace(cache_ttl=0).cache_enabled is False
    with pytest.raises(ConfigError):
        settings.replace(report_format="html")
