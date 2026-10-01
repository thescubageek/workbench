"""Entry point: parse arguments, resolve settings, dispatch to a subcommand."""

from __future__ import annotations

import sys
import traceback
from typing import List, Optional

from linkcrawl.cli.args import UsageError, parse_args
from linkcrawl.cli.cmd_check import run_check
from linkcrawl.cli.cmd_config import run_config
from linkcrawl.cli.cmd_crawl import run_crawl
from linkcrawl.cli.cmd_report import run_report
from linkcrawl.cli.exit_codes import (EXIT_CONFIG_ERROR, EXIT_INTERNAL_ERROR,
                                      EXIT_INTERRUPTED, EXIT_USAGE)
from linkcrawl.cli.overrides import cli_overrides
from linkcrawl.config.settings import resolve_settings
from linkcrawl.core.errors import ConfigError, PluginError, ReportError

DEBUG_ENV = "LINKCRAWL_DEBUG"


def main(argv: Optional[List[str]] = None) -> int:
    try:
        args = parse_args(argv)
    except UsageError as error:
        sys.stderr.write(f"{error}\n")
        return EXIT_USAGE
    try:
        if args.command == "report":
            return run_report(args)
        if args.command == "config":
            return run_config(args)
        settings = resolve_settings(cli_overrides(args), config_path=args.config)
        if args.command == "check":
            return run_check(args, settings)
        if args.command == "crawl":
            return run_crawl(args, settings)
    except (ConfigError, PluginError) as error:
        sys.stderr.write(f"linkcrawl: configuration error: {error}\n")
        return EXIT_CONFIG_ERROR
    except ReportError as error:
        sys.stderr.write(f"linkcrawl: {error}\n")
        return EXIT_USAGE
    except KeyboardInterrupt:
        sys.stderr.write("linkcrawl: interrupted\n")
        return EXIT_INTERRUPTED
    except Exception:
        traceback.print_exc()
        return EXIT_INTERNAL_ERROR
    sys.stderr.write(f"linkcrawl: unknown command {args.command!r}\n")
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
