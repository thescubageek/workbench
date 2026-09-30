"""Built-in hooks registered on every run."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from linkcrawl.core.result import CheckResult, ResultSource
from linkcrawl.plugins.hooks import AFTER_CHECK, BUILTIN_PRIORITY
from linkcrawl.plugins.registry import HookRegistry

if TYPE_CHECKING:
    from linkcrawl.config.settings import Settings

SLOW_SUFFIX = "slow response"


def annotate_slow(result: CheckResult, settings: "Settings") -> Optional[CheckResult]:
    """Add a note to OK network results slower than slow_threshold. Status is unchanged."""
    if result.source is not ResultSource.NETWORK or not result.ok:
        return None
    if result.elapsed_seconds <= settings.slow_threshold:
        return None
    note = f"{SLOW_SUFFIX} ({result.elapsed_seconds:.1f}s)"
    reason = f"{result.reason}; {note}" if result.reason else note
    return result.with_reason(reason)


def register_builtins(registry: HookRegistry, settings: "Settings") -> None:
    registry.register(AFTER_CHECK, annotate_slow, priority=BUILTIN_PRIORITY,
                      owner="linkcrawl.builtin.annotate_slow")
