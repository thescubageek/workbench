"""Saved result files: what `linkcrawl check --save` writes and `linkcrawl report` reads."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Tuple

from linkcrawl import __version__
from linkcrawl.core.errors import ReportError
from linkcrawl.core.result import CheckResult
from linkcrawl.store.json_store import JsonStore

RESULTS_FORMAT = "linkcrawl-results"
RESULTS_VERSION = 1


def save_results(path: str, results: List[CheckResult], meta: Dict[str, Any] = None) -> None:
    payload = {
        "format": RESULTS_FORMAT,
        "version": RESULTS_VERSION,
        "generator": f"linkcrawl {__version__}",
        "saved_at": time.time(),
        "meta": dict(meta or {}),
        "results": [result.to_dict() for result in results],
    }
    JsonStore(path).save(payload)


def load_results(path: str) -> Tuple[List[CheckResult], Dict[str, Any]]:
    store = JsonStore(path)
    if not store.exists():
        raise ReportError(f"{path}: no such results file")
    data = store.load()
    if data.get("format") != RESULTS_FORMAT:
        raise ReportError(f"{path}: not a linkcrawl results file")
    if data.get("version") != RESULTS_VERSION:
        raise ReportError(f"{path}: unsupported results version {data.get('version')!r}")
    try:
        results = [CheckResult.from_dict(item) for item in data.get("results", [])]
    except (KeyError, ValueError, TypeError) as error:
        raise ReportError(f"{path}: malformed result: {error}") from error
    return results, dict(data.get("meta", {}))
