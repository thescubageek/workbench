import pytest

from linkcrawl.cli import cmd_check
from linkcrawl.cli.args import UsageError, parse_args
from linkcrawl.cli.exit_codes import (EXIT_BROKEN_LINKS, EXIT_CONFIG_ERROR,
                                      EXIT_NOTHING_CHECKED, EXIT_OK, EXIT_SKIPPED_LINKS,
                                      EXIT_USAGE, exit_code_for)
from linkcrawl.cli.main import main
from linkcrawl.cli.overrides import cli_overrides
from linkcrawl.report.summary import Summary


@pytest.mark.parametrize("summary, fail_on_skipped, expected", [
    (Summary(total=3, ok=3), False, EXIT_OK),
    (Summary(total=3, ok=2, broken=1), False, EXIT_BROKEN_LINKS),
    (Summary(total=3, ok=2, skipped=1), False, EXIT_OK),
    (Summary(total=3, ok=2, skipped=1), True, EXIT_SKIPPED_LINKS),
    (Summary(total=3, broken=1, skipped=2), True, EXIT_BROKEN_LINKS),
    (Summary(), False, EXIT_NOTHING_CHECKED),
])
def test_exit_code_for(summary, fail_on_skipped, expected):
    assert exit_code_for(summary, fail_on_skipped) == expected


def test_overrides_only_include_given_options():
    args = parse_args(["check", "https://example.com/", "--timeout", "2", "--no-cache",
                       "--ignore-robots"])
    assert cli_overrides(args) == {"timeout": 2.0, "cache_ttl": 0, "respect_robots": False}


def test_bad_option_is_a_usage_error():
    with pytest.raises(UsageError):
        parse_args(["check", "--max-attempts", "lots"])
    assert main(["check", "--max-attempts", "lots"]) == EXIT_USAGE


def test_invalid_setting_is_a_config_error(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LINKCRAWL_MAX_ATTEMPTS", "0")
    assert main(["check", "https://example.com/"]) == EXIT_CONFIG_ERROR


def test_check_command_end_to_end(monkeypatch, tmp_path, capsys, make_components):
    routes = {
        "https://example.com/ok": (200, {}, b""),
        "https://example.com/gone": (410, {}, b""),
    }

    def fake_build(settings, start_urls=()):
        components = make_components(routes=routes, respect_robots=False)
        components.settings = settings
        return components

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cmd_check, "build_components", fake_build)
    code = main(["check", "https://example.com/ok", "https://example.com/gone",
                 "--no-cache", "--ignore-robots", "--save", str(tmp_path / "r.json")])
    out = capsys.readouterr().out
    assert code == EXIT_BROKEN_LINKS
    assert "FAIL 410 https://example.com/gone" in out
    assert main(["report", str(tmp_path / "r.json"), "--format", "json"]) == EXIT_BROKEN_LINKS


def test_url_file_skips_comments(tmp_path):
    path = tmp_path / "urls.txt"
    path.write_text("# header\nhttps://a.example/\n\n  https://b.example/  \n")
    assert cmd_check.read_url_file(str(path)) == ["https://a.example/", "https://b.example/"]


def test_config_command_shows_origins(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "linkcrawl.ini").write_text("[linkcrawl]\nrate_limit = 0.5\n")
    monkeypatch.setenv("LINKCRAWL_CACHE_TTL", "10")
    assert main(["config", "--timeout", "3"]) == EXIT_OK
    out = capsys.readouterr().out
    lines = {line.split()[0]: line for line in out.splitlines() if line and " " in line}
    assert lines["timeout"].endswith("[command line]")
    assert lines["cache_ttl"].endswith("[environment]")
    assert lines["rate_limit"].endswith("[file]")
    assert lines["max_attempts"].endswith("[defaults]")
