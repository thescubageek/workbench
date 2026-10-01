"""Reporters: text, JSON and JUnit XML renderings of a run's results."""

from linkcrawl.report.registry import get_reporter
from linkcrawl.report.summary import Summary

__all__ = ["Summary", "get_reporter"]
