"""`linkcrawl config`: print every resolved setting and the layer that set it."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, TextIO

from linkcrawl.cli.exit_codes import EXIT_OK
from linkcrawl.cli.overrides import cli_overrides
from linkcrawl.config.env import unknown_env_vars
from linkcrawl.config.schema import FIELDS
from linkcrawl.config.settings import resolve_with_origins


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value) or "(none)"
    return str(value)


def settings_table(values: Dict[str, Any], origins: Dict[str, str]) -> List[str]:
    width = max(len(spec.name) for spec in FIELDS)
    lines = []
    for spec in FIELDS:
        value = _format_value(values[spec.name])
        lines.append(f"{spec.name:<{width}}  {value:<28}  [{origins.get(spec.name, '?')}]")
    return lines


def run_config(args: argparse.Namespace, stream: Optional[TextIO] = None) -> int:
    out = stream or sys.stdout
    resolved = resolve_with_origins(cli_overrides(args), config_path=args.config)
    values = resolved.settings.as_dict()
    if args.json:
        payload = {"config_file": resolved.config_path,
                   "settings": {name: {"value": values[name], "from": resolved.origins[name]}
                                for name in values}}
        out.write(json.dumps(payload, indent=2, default=list) + "\n")
        return EXIT_OK
    out.write(f"config file: {resolved.config_path or '(none found)'}\n")
    for line in settings_table(values, resolved.origins):
        out.write(line + "\n")
    for name in sorted(unknown_env_vars()):
        out.write(f"warning: {name} is set but no setting reads it\n")
    return EXIT_OK
