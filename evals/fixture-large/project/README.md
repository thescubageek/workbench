# linkcrawl

A command-line link crawler and checker. It crawls the pages of a site, checks every link it
finds, and writes a report. It uses the Python standard library only.

## Usage

```bash
PYTHONPATH=src python3 -m linkcrawl check https://example.com/a https://example.com/b
PYTHONPATH=src python3 -m linkcrawl crawl https://example.com/ --max-depth 2
PYTHONPATH=src python3 -m linkcrawl report results.json --format junit
PYTHONPATH=src python3 -m linkcrawl config
```

Each link gets one of three statuses: `ok`, `broken` or `skipped`.

## Layout

- `src/linkcrawl/config/` — settings, their defaults and their overrides
- `src/linkcrawl/net/` — the HTTP client
- `src/linkcrawl/crawl/` — the crawl frontier, robots.txt and sitemaps
- `src/linkcrawl/parse/` — link extraction from HTML, Markdown and CSS
- `src/linkcrawl/core/` — the result model and the per-link checker
- `src/linkcrawl/store/` — the result cache and saved result files
- `src/linkcrawl/report/` — text, JSON and JUnit reports
- `src/linkcrawl/cli/` — the `linkcrawl` command
- `src/linkcrawl/plugins/` — the hook registry

More detail is in `docs/`.

## Tests

```bash
python3 -m pytest
```
