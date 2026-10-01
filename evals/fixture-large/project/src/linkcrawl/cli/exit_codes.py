"""Exit statuses of the linkcrawl command, and how a run's counts map to them."""

from __future__ import annotations

from linkcrawl.report.summary import Summary

EXIT_OK = 0
EXIT_BROKEN_LINKS = 1
EXIT_USAGE = 2
EXIT_CONFIG_ERROR = 3
EXIT_SKIPPED_LINKS = 4
EXIT_NOTHING_CHECKED = 5
EXIT_INTERNAL_ERROR = 70
EXIT_INTERRUPTED = 130

DESCRIPTIONS = {
    EXIT_OK: "every checked link is OK (skipped links do not count by default)",
    EXIT_BROKEN_LINKS: "at least one link is broken",
    EXIT_USAGE: "the command line was invalid",
    EXIT_CONFIG_ERROR: "a setting, config file or plugin is invalid",
    EXIT_SKIPPED_LINKS: "no link is broken, but links were skipped and --fail-on-skipped is set",
    EXIT_NOTHING_CHECKED: "no URL was given or found",
    EXIT_INTERNAL_ERROR: "linkcrawl failed unexpectedly",
    EXIT_INTERRUPTED: "interrupted by the user",
}


def exit_code_for(summary: Summary, fail_on_skipped: bool = False) -> int:
    """Broken outranks skipped; skipped fails the run only with fail_on_skipped."""
    if summary.total == 0:
        return EXIT_NOTHING_CHECKED
    if summary.broken > 0:
        return EXIT_BROKEN_LINKS
    if fail_on_skipped and summary.skipped > 0:
        return EXIT_SKIPPED_LINKS
    return EXIT_OK


def describe(code: int) -> str:
    return DESCRIPTIONS.get(code, "unknown exit status")
