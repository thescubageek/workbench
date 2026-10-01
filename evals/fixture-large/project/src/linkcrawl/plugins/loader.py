"""Load plugins named as 'package.module:setup' and call setup(registry)."""

from __future__ import annotations

import importlib
from typing import Iterable, List

from linkcrawl.core.errors import PluginError
from linkcrawl.plugins.registry import HookRegistry


def resolve(spec: str):
    module_name, _, attribute = spec.partition(":")
    if not module_name or not attribute:
        raise PluginError(f"plugin {spec!r} must be written as module:function")
    try:
        module = importlib.import_module(module_name)
    except ImportError as error:
        raise PluginError(f"cannot import plugin module {module_name!r}: {error}") from error
    try:
        return getattr(module, attribute)
    except AttributeError as error:
        raise PluginError(f"{module_name} has no attribute {attribute!r}") from error


def load_plugins(registry: HookRegistry, specs: Iterable[str]) -> List[str]:
    loaded: List[str] = []
    for spec in specs:
        setup = resolve(spec)
        if not callable(setup):
            raise PluginError(f"plugin {spec!r} is not callable")
        try:
            setup(registry)
        except PluginError:
            raise
        except Exception as error:
            raise PluginError(f"plugin {spec!r} failed during setup: {error}") from error
        loaded.append(spec)
    return loaded
