## Summary

The HTTP client now retries a failed request at most 3 times, with backoff and jitter. Before,
it retried without a limit, so one outage multiplied the load on the server.

## Changes

- The retry limit and the backoff are settings in `src/retry/config.py:4-9`.
- The backoff starts at 200 ms, doubles on each attempt, and adds up to 20% jitter.
- The old unlimited path is gone. `docs/retry.md` says how to raise the limit.

## Testing

- All unit and integration tests pass.
- A fake server that fails every second request gets 3 attempts, then a clear error.

Closes #42

🤖 Generated with [Claude Code](https://claude.com/claude-code)
