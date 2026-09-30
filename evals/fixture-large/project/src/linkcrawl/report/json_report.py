"""JSON report: the summary and every result."""

from __future__ import annotations

import json
from typing import List

from linkcrawl import __version__
from linkcrawl.core.result import CheckResult
from linkcrawl.report.base import Reporter
from linkcrawl.report.summary import Summary

JSON_REPORT_SCHEMA = "linkcrawl-report/1"


class JsonReporter(Reporter):
    name = "json"
    extension = ".json"

    def render(self, results: List[CheckResult], summary: Summary) -> str:
        payload = {
            "schema": JSON_REPORT_SCHEMA,
            "generator": f"linkcrawl {__version__}",
            "summary": summary.to_dict(),
            "results": [result.to_dict() for result in self.ordered(results)],
        }
        return json.dumps(payload, indent=2, sort_keys=False) + "\n"
