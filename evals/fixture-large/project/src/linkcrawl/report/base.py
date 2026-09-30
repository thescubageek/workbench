"""The reporter interface."""

from __future__ import annotations

import abc
from typing import List

from linkcrawl.core.result import CheckResult, LinkStatus
from linkcrawl.report.summary import Summary

STATUS_ORDER = {LinkStatus.BROKEN: 0, LinkStatus.SKIPPED: 1, LinkStatus.OK: 2}


class Reporter(abc.ABC):
    name = "base"
    extension = ".txt"

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    @abc.abstractmethod
    def render(self, results: List[CheckResult], summary: Summary) -> str:
        """Return the whole report as one string."""

    @staticmethod
    def ordered(results: List[CheckResult]) -> List[CheckResult]:
        return sorted(results, key=lambda r: (STATUS_ORDER[r.status], r.url))
