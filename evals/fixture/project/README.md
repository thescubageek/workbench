# linkcheck

A small command-line tool that checks whether URLs respond.

## Usage

```bash
PYTHONPATH=src python3 -m linkcheck.cli https://example.com https://example.org
```

Each URL gets an HTTP `HEAD` request. The tool prints `BROKEN <url>` for each link that fails.

## Layout

- `src/linkcheck/config.py` — settings
- `src/linkcheck/checker.py` — checks one URL
- `src/linkcheck/cli.py` — the command-line entry point
