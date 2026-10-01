"""Reporter lookup by name."""

from __future__ import annotations

from typing import Dict, Type

from linkcrawl.core.errors import ReportError
from linkcrawl.report.base import Reporter
from linkcrawl.report.json_report import JsonReporter
from linkcrawl.report.junit import JunitReporter
from linkcrawl.report.text import TextReporter

REPORTERS: Dict[str, Type[Reporter]] = {
    TextReporter.name: TextReporter,
    JsonReporter.name: JsonReporter,
    JunitReporter.name: JunitReporter,
}


def get_reporter(name: str, verbose: bool = False) -> Reporter:
    try:
        reporter_class = REPORTERS[name]
    except KeyError as error:
        known = ", ".join(sorted(REPORTERS))
        raise ReportError(f"unknown report format {name!r}; expected one of {known}") from error
    return reporter_class(verbose=verbose)
