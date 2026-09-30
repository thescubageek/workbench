"""JUnit XML report, so CI systems show each link as a test case.

A broken link is a <failure>; a skipped link is <skipped>; an OK link passes.
"""

from __future__ import annotations

import xml.etree.ElementTree as ElementTree
from typing import List

from linkcrawl.core.result import CheckResult
from linkcrawl.crawl.normalize import host
from linkcrawl.report.base import Reporter
from linkcrawl.report.summary import Summary

SUITE_NAME = "linkcrawl"


class JunitReporter(Reporter):
    name = "junit"
    extension = ".xml"

    def render(self, results: List[CheckResult], summary: Summary) -> str:
        suites = ElementTree.Element("testsuites", {
            "name": SUITE_NAME,
            "tests": str(summary.total),
            "failures": str(summary.broken),
            "skipped": str(summary.skipped),
        })
        suite = ElementTree.SubElement(suites, "testsuite", {
            "name": SUITE_NAME,
            "tests": str(summary.total),
            "failures": str(summary.broken),
            "skipped": str(summary.skipped),
            "errors": "0",
            "time": f"{sum(r.elapsed_seconds for r in results):.3f}",
        })
        for result in self.ordered(results):
            self._case(suite, result)
        ElementTree.indent(suites)
        body = ElementTree.tostring(suites, encoding="unicode")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n"

    def _case(self, suite: ElementTree.Element, result: CheckResult) -> None:
        case = ElementTree.SubElement(suite, "testcase", {
            "classname": host(result.url) or "unknown",
            "name": result.url,
            "time": f"{result.elapsed_seconds:.3f}",
        })
        if result.broken:
            failure = ElementTree.SubElement(case, "failure", {
                "message": result.reason or "broken",
                "type": f"HTTP {result.http_status}" if result.http_status else "network",
            })
            failure.text = self._details(result)
        elif result.skipped:
            ElementTree.SubElement(case, "skipped", {"message": result.reason})

    @staticmethod
    def _details(result: CheckResult) -> str:
        lines = [f"url: {result.url}", f"attempts: {result.attempts}"]
        if result.parent:
            lines.append(f"found on: {result.parent}")
        return "\n".join(lines)
