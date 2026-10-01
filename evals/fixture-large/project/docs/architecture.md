# Architecture

`linkcrawl` has one composition root, `core/pipeline.py`. It builds every component from one
`Settings` object: the rate limiter, the HTTP client, the robots.txt policy, the scope, the
result cache and the hook registry. The per-link checker, `core/checker.py`, uses these
components.

## Data flow

1. The CLI parses its arguments and resolves the settings.
2. The `check` command sends each URL to the checker. The `crawl` command puts the start
   URLs into a frontier, and then adds the links that it finds on internal pages.
3. The checker returns a `CheckResult` for each URL.
4. The results become a `Summary`. A reporter renders the summary and the results.
5. The summary gives the exit status.

## Subpackages

| Package   | Responsibility |
| --------- | -------------- |
| `config`  | defaults, config files, environment variables, validation |
| `net`     | urllib wrapper, retries, backoff, rate limits, timeouts |
| `crawl`   | frontier, URL normalization, scope, robots.txt, sitemaps, depth |
| `parse`   | link extraction |
| `core`    | results, classification, the checker |
| `store`   | result cache, JSON files |
| `report`  | reporters and the summary |
| `cli`     | subcommands and exit statuses |
| `plugins` | hooks that can change results |
