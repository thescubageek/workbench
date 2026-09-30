"""`linkcrawl report RESULTS_JSON`: re-render saved results in another format."""

from __future__ import annotations

import argparse

from linkcrawl.cli.exit_codes import exit_code_for
from linkcrawl.cli.output import render_report, write_report
from linkcrawl.store.results_file import load_results


def run_report(args: argparse.Namespace) -> int:
    results, _meta = load_results(args.results)
    text, summary = render_report(results, args.report_format, args.verbose)
    write_report(text, args.output)
    return exit_code_for(summary, args.fail_on_skipped)
