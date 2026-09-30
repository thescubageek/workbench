# Command line

```text
linkcrawl check URL... [--file PATH] [options]
linkcrawl crawl START_URL... [--sitemap URL] [--max-depth N] [--max-pages N] [options]
linkcrawl report RESULTS_JSON [--format text|json|junit]
linkcrawl config [--json] [options]
```

## Common options

- `--timeout`, `--connect-timeout`, `--max-attempts`, `--backoff-base`, `--rate-limit`
- `--respect-robots` and `--ignore-robots`
- `--cache-ttl`, `--no-cache`, `--cache-path`
- `--include`, `--exclude`, `--accept-status`, `--plugin`
- `--format`, `--output`, `--save`, `--fail-on-skipped`

## Output

The report goes to standard output, or to the file that `--output` names. Progress lines go to
standard error. `--save` writes the raw results, and `linkcrawl report` can render them again
later.

The exit status tells you the result of the run. The values are in `cli/exit_codes.py`.
