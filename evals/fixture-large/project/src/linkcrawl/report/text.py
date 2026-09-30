"""Plain-text report for a terminal."""

from __future__ import annotations

from typing import List

from linkcrawl.core.result import CheckResult
from linkcrawl.report.base import Reporter
from linkcrawl.report.summary import Summary

LABELS = {"ok": "OK  ", "broken": "FAIL", "skipped": "SKIP"}


class TextReporter(Reporter):
    name = "text"
    extension = ".txt"

    def render(self, results: List[CheckResult], summary: Summary) -> str:
        lines: List[str] = []
        for result in self.ordered(results):
            if result.ok and not self.verbose:
                continue
            lines.append(self._line(result))
        if lines:
            lines.append("")
        lines.append(summary.headline())
        if summary.skip_reasons and self.verbose:
            lines.append("skipped because:")
            for reason, count in sorted(summary.skip_reasons.items()):
                lines.append(f"  {count:>4}  {reason}")
        return "\n".join(lines) + "\n"

    def _line(self, result: CheckResult) -> str:
        label = LABELS[result.status.value]
        status = f"{result.http_status}" if result.http_status is not None else "---"
        text = f"{label} {status:>3} {result.url}"
        if result.reason:
            text += f"  ({result.reason})"
        if result.from_cache:
            text += "  [cached]"
        if result.parent and self.verbose:
            text += f"\n           found on {result.parent}"
        return text
