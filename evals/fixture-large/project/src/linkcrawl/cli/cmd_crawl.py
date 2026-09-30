"""`linkcrawl crawl START_URL...`: crawl internal pages and check every link found."""

from __future__ import annotations

import argparse
import sys

from linkcrawl.cli.exit_codes import EXIT_INTERRUPTED, EXIT_NOTHING_CHECKED, exit_code_for
from linkcrawl.cli.output import Progress, maybe_save, render_report, write_report
from linkcrawl.config.settings import Settings
from linkcrawl.core.errors import CrawlAborted
from linkcrawl.core.pipeline import build_components
from linkcrawl.crawl.crawler import crawl


def run_crawl(args: argparse.Namespace, settings: Settings) -> int:
    if not args.urls and not args.sitemap:
        sys.stderr.write("linkcrawl crawl: give at least one START_URL or --sitemap\n")
        return EXIT_NOTHING_CHECKED
    components = build_components(settings, start_urls=args.urls)
    progress = Progress(verbose=args.verbose, quiet=args.quiet)
    interrupted = False
    try:
        results = crawl(settings, components, args.urls, sitemap=args.sitemap,
                        progress=progress)
    except CrawlAborted as aborted:
        results = aborted.results
        interrupted = True
    finally:
        components.close()
    text, summary = render_report(results, settings.report_format, args.verbose,
                                  hooks=components.hooks)
    write_report(text, args.output)
    maybe_save(results, args.save, "crawl")
    if interrupted:
        return EXIT_INTERRUPTED
    return exit_code_for(summary, settings.fail_on_skipped)
