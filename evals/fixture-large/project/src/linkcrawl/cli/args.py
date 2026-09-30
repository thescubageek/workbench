"""Argument parsing for the linkcrawl command."""

from __future__ import annotations

import argparse
from typing import List, Optional

from linkcrawl import __version__
from linkcrawl.config.validation import REPORT_FORMATS

PROG = "linkcrawl"


class UsageError(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise UsageError(f"{self.prog}: {message}")


def _add_common(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group("settings")
    group.add_argument("--config", metavar="PATH", help="read settings from this file")
    group.add_argument("--timeout", type=float, metavar="SECONDS",
                       help="read timeout per attempt")
    group.add_argument("--connect-timeout", type=float, metavar="SECONDS")
    group.add_argument("--max-attempts", type=int, metavar="N",
                       help="attempts per link, including the first")
    group.add_argument("--backoff-base", type=float, metavar="SECONDS")
    group.add_argument("--rate-limit", type=float, metavar="PER_SECOND",
                       help="requests per second per host; 0 disables")
    robots = group.add_mutually_exclusive_group()
    robots.add_argument("--respect-robots", dest="respect_robots", action="store_true",
                        default=None)
    robots.add_argument("--ignore-robots", dest="respect_robots", action="store_false")
    group.add_argument("--cache-ttl", type=int, metavar="SECONDS",
                       help="seconds an OK result stays cached; 0 disables")
    group.add_argument("--no-cache", action="store_true",
                       help="same as --cache-ttl 0")
    group.add_argument("--cache-path", metavar="PATH")
    group.add_argument("--exclude", action="append", metavar="GLOB", dest="exclude_patterns")
    group.add_argument("--include", action="append", metavar="GLOB", dest="include_patterns")
    group.add_argument("--accept-status", action="append", type=int, metavar="CODE",
                       dest="accepted_statuses")
    group.add_argument("--plugin", action="append", metavar="MODULE:FUNC", dest="plugins")
    out = parser.add_argument_group("output")
    out.add_argument("--format", choices=REPORT_FORMATS, dest="report_format")
    out.add_argument("--output", "-o", metavar="PATH", help="write the report to a file")
    out.add_argument("--save", metavar="PATH", help="save raw results for `linkcrawl report`")
    out.add_argument("--fail-on-skipped", action="store_true", default=None)
    out.add_argument("--verbose", "-v", action="store_true")
    out.add_argument("--quiet", "-q", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog=PROG, description="Crawl a site and check its links.")
    parser.add_argument("--version", action="version", version=f"{PROG} {__version__}")
    commands = parser.add_subparsers(dest="command", metavar="COMMAND")
    commands.required = True

    check = commands.add_parser("check", help="check a list of URLs")
    check.add_argument("urls", nargs="*", metavar="URL")
    check.add_argument("--file", "-f", metavar="PATH",
                       help="read URLs from a file, one per line ('-' for stdin)")
    _add_common(check)

    crawl = commands.add_parser("crawl", help="crawl from start URLs and check every link")
    crawl.add_argument("urls", nargs="*", metavar="START_URL")
    crawl.add_argument("--sitemap", metavar="URL", help="seed the crawl from a sitemap")
    crawl.add_argument("--max-depth", type=int, metavar="N")
    crawl.add_argument("--max-pages", type=int, metavar="N")
    crawl.add_argument("--internal-only", dest="check_external", action="store_false",
                       default=None, help="skip links to other hosts")
    _add_common(crawl)

    config = commands.add_parser("config", help="show resolved settings and their origin")
    config.add_argument("--json", action="store_true", help="print as JSON")
    _add_common(config)

    report = commands.add_parser("report", help="render a saved results file")
    report.add_argument("results", metavar="RESULTS_JSON")
    report.add_argument("--format", choices=REPORT_FORMATS, default="text",
                        dest="report_format")
    report.add_argument("--output", "-o", metavar="PATH")
    report.add_argument("--verbose", "-v", action="store_true")
    report.add_argument("--fail-on-skipped", action="store_true", default=False)
    return parser


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)
