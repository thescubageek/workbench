---
project: linkcrawl link classification
status: complete
---

# Research: how linkcrawl classifies a link

| ID | Claim | Source |
| -- | ----- | ------ |
| C01 | The default read timeout per attempt is 8 seconds. | `src/linkcrawl/config/defaults.py:7` |
| C02 | A link gets at most 3 attempts by default, including the first. | `src/linkcrawl/config/defaults.py:10` |
| C03 | The `LINKCRAWL_TIMEOUT` environment variable overrides the timeout setting. | `src/linkcrawl/config/env.py:18` |
| C04 | Settings are merged so that the environment overrides the command line. | `src/linkcrawl/config/settings.py:17` |
| C05 | The timeout passed to `urlopen` is the larger of the connect and read timeouts. | `src/linkcrawl/net/timeouts.py:28` |
| C06 | HTTP 502 is not retried. Only 429, 500, 503 and 504 are retried. | `src/linkcrawl/net/retry.py:14` |
| C07 | The backoff delay grows exponentially from the base and is capped at `backoff_max`. | `src/linkcrawl/net/backoff.py:35` |
| C08 | The per-host rate limit is 5 requests per second by default. | `src/linkcrawl/config/defaults.py:17` |
| C09 | A rate limit of 0 disables the per-host rate limiter. | `src/linkcrawl/net/rate_limit.py:70` |
| C10 | When robots.txt returns a 5xx status, every URL on that origin is allowed. | `src/linkcrawl/crawl/robots.py:43` |
| C11 | Only OK results are cached, so broken and skipped links are checked again on every run. | `src/linkcrawl/store/cache.py:21` |
| C12 | An HTTP status of 429 after all retries makes a link broken. | `src/linkcrawl/core/classify.py:29` |
| C13 | The command exits with status 1 when any link is broken. | `src/linkcrawl/cli/exit_codes.py:33` |
| C14 | The JUnit report writes a broken link as a failure element. | `src/linkcrawl/report/junit_xml.py:51` |

## Snippet

From `src/linkcrawl/config/defaults.py:17`:

```python
DEFAULT_RATE_LIMIT_PER_HOST = 5.0
```
