"""Render a report, write it, and save raw results when asked."""

from __future__ import annotations

import os
import sys
from typing import List, Optional, TextIO

from linkcrawl.core.result import CheckResult
from linkcrawl.plugins.hooks import BEFORE_REPORT
from linkcrawl.plugins.registry import HookRegistry
from linkcrawl.report.registry import get_reporter
from linkcrawl.report.summary import Summary
from linkcrawl.store.results_file import save_results


def render_report(results: List[CheckResult], report_format: str, verbose: bool = False,
                  hooks: Optional[HookRegistry] = None) -> tuple:
    summary = Summary.from_results(results)
    if hooks is not None:
        changed = hooks.first(BEFORE_REPORT, results=results, summary=summary)
        if changed is not None:
            results = list(changed)
            summary = Summary.from_results(results)
    reporter = get_reporter(report_format, verbose=verbose)
    return reporter.render(results, summary), summary


def write_report(text: str, output: Optional[str], stream: Optional[TextIO] = None) -> None:
    if not output or output == "-":
        (stream or sys.stdout).write(text)
        return
    directory = os.path.dirname(os.path.abspath(output))
    os.makedirs(directory, exist_ok=True)
    with open(output, "w", encoding="utf-8") as handle:
        handle.write(text)


def maybe_save(results: List[CheckResult], path: Optional[str], command: str) -> None:
    if path:
        save_results(path, results, meta={"command": command})


class Progress:
    """One line per result on stderr, only for FAIL and SKIP unless verbose."""

    def __init__(self, stream: Optional[TextIO] = None, verbose: bool = False,
                 quiet: bool = False):
        self.stream = stream or sys.stderr
        self.verbose = verbose
        self.quiet = quiet
        self.count = 0

    def __call__(self, result: CheckResult, remaining: int) -> None:
        self.count += 1
        if self.quiet:
            return
        if result.ok and not self.verbose:
            return
        self.stream.write(f"[{self.count}, {remaining} queued] "
                          f"{result.status.value:<7} {result.url}\n")
