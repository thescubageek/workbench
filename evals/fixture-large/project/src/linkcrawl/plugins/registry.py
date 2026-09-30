"""The hook registry: register callables by hook name and call them in priority order."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from linkcrawl.core.errors import PluginError
from linkcrawl.plugins.hooks import DEFAULT_PRIORITY, HOOK_NAMES

Hook = Callable[..., Any]


@dataclass(frozen=True)
class Registration:
    name: str
    function: Hook
    priority: int
    owner: str


class HookRegistry:
    def __init__(self):
        self._hooks: Dict[str, List[Registration]] = {name: [] for name in HOOK_NAMES}

    def register(self, name: str, function: Hook, priority: int = DEFAULT_PRIORITY,
                 owner: str = "") -> None:
        if name not in self._hooks:
            raise PluginError(f"unknown hook {name!r}; expected one of {', '.join(HOOK_NAMES)}")
        entry = Registration(name, function, priority, owner or _qualname(function))
        self._hooks[name].append(entry)
        self._hooks[name].sort(key=lambda item: item.priority)

    def registrations(self, name: str) -> List[Registration]:
        return list(self._hooks.get(name, []))

    def call(self, name: str, **kwargs: Any) -> List[Any]:
        return [self._invoke(entry, kwargs) for entry in self.registrations(name)]

    def first(self, name: str, **kwargs: Any) -> Any:
        """Call hooks in order and return the first non-None value."""
        for entry in self.registrations(name):
            value = self._invoke(entry, kwargs)
            if value is not None:
                return value
        return None

    def transform(self, name: str, value: Any, **kwargs: Any) -> Any:
        """Pass value through each hook; a hook returning None leaves it unchanged."""
        current = value
        for entry in self.registrations(name):
            changed = entry.function(current, **kwargs)
            if changed is not None:
                current = changed
        return current

    def _invoke(self, entry: Registration, kwargs: Dict[str, Any]) -> Any:
        try:
            return entry.function(**kwargs)
        except TypeError as error:
            raise PluginError(f"hook {entry.owner} for {entry.name}: {error}") from error

    def __len__(self) -> int:
        return sum(len(items) for items in self._hooks.values())


def _qualname(function: Hook) -> str:
    module = getattr(function, "__module__", "?")
    name = getattr(function, "__qualname__", repr(function))
    return f"{module}.{name}"
