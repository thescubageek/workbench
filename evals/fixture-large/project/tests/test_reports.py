import json
import xml.etree.ElementTree as ElementTree

import pytest

from linkcrawl.core.errors import ReportError
from linkcrawl.core.result import ResultSource, broken_result, ok_result, skipped_result
from linkcrawl.report.registry import get_reporter
from linkcrawl.report.summary import Summary
from linkcrawl.store.results_file import load_results, save_results

RESULTS = [
    ok_result("https://example.com/", 200, attempts=1),
    ok_result("https://example.com/c", 200, source=ResultSource.CACHE),
    broken_result("https://example.com/missing", "HTTP 404", 404, attempts=1,
                  parent="https://example.com/"),
    skipped_result("https://example.com/private", "disallowed by robots.txt"),
]


def test_summary_counts():
    summary = Summary.from_results(RESULTS)
    assert (summary.total, summary.ok, summary.broken, summary.skipped) == (4, 2, 1, 1)
    assert summary.from_cache == 1
    assert summary.skip_reasons == {"disallowed by robots.txt": 1}
    assert summary.headline() == "4 checked, 2 ok, 1 broken, 1 skipped, 1 from cache"


def test_text_report_lists_failures_first():
    text = get_reporter("text").render(RESULTS, Summary.from_results(RESULTS))
    lines = text.splitlines()
    assert lines[0].startswith("FAIL 404 https://example.com/missing")
    assert lines[1].startswith("SKIP --- https://example.com/private")
    assert lines[-1].startswith("4 checked")


def test_json_report_round_trips_results():
    payload = json.loads(get_reporter("json").render(RESULTS, Summary.from_results(RESULTS)))
    assert payload["summary"]["broken"] == 1
    assert payload["results"][0]["status"] == "broken"


def test_junit_marks_failures_and_skips():
    xml = get_reporter("junit").render(RESULTS, Summary.from_results(RESULTS))
    root = ElementTree.fromstring(xml.split("\n", 1)[1])
    suite = root.find("testsuite")
    assert suite.get("failures") == "1"
    assert suite.get("skipped") == "1"
    assert len(suite.findall("testcase/failure")) == 1
    assert len(suite.findall("testcase/skipped")) == 1


def test_unknown_reporter():
    with pytest.raises(ReportError):
        get_reporter("html")


def test_results_file_round_trip(tmp_path):
    path = str(tmp_path / "results.json")
    save_results(path, RESULTS, meta={"command": "check"})
    loaded, meta = load_results(path)
    assert loaded == RESULTS
    assert meta == {"command": "check"}


def test_results_file_rejects_other_json(tmp_path):
    path = tmp_path / "other.json"
    path.write_text("{}")
    with pytest.raises(ReportError):
        load_results(str(path))
