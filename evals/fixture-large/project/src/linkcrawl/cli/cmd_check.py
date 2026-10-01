"""`linkcrawl check URL...`: check each URL once, without crawling."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable, List, TextIO

from linkcrawl.cli.exit_codes import EXIT_NOTHING_CHECKED, exit_code_for
from linkcrawl.cli.output import Progress, maybe_save, render_report, write_report
from linkcrawl.config.settings import Settings
from linkcrawl.core.pipeline import build_components
from linkcrawl.core.result import CheckResult


def read_url_file(path: str, stdin: TextIO = sys.stdin) -> List[str]:
    handle = stdin if path == "-" else open(path, encoding="utf-8")
    try:
        lines = handle.read().splitlines()
    finally:
        if handle is not stdin:
            handle.close()
    return [line.strip() for line in lines
            if line.strip() and not line.lstrip().startswith("#")]


def gather_urls(args: argparse.Namespace) -> List[str]:
    urls = list(args.urls)
    if getattr(args, "file", None):
        urls.extend(read_url_file(args.file))
    return urls


def check_all(urls: Iterable[str], components, progress=None) -> List[CheckResult]:
    results: List[CheckResult] = []
    for url in urls:
        result = components.checker.check(url)
        results.append(result)
        if progress is not None:
            progress(result, 0)
    return results


def run_check(args: argparse.Namespace, settings: Settings) -> int:
    urls = gather_urls(args)
    if not urls:
        sys.stderr.write("linkcrawl check: no URLs given\n")
        return EXIT_NOTHING_CHECKED
    components = build_components(settings, start_urls=urls)
    progress = Progress(verbose=args.verbose, quiet=args.quiet)
    try:
        results = check_all(urls, components, progress)
    finally:
        components.close()
    text, summary = render_report(results, settings.report_format, args.verbose,
                                  hooks=components.hooks)
    write_report(text, args.output)
    maybe_save(results, args.save, "check")
    return exit_code_for(summary, settings.fail_on_skipped)
