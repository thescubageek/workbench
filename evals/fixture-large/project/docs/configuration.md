# Configuration

Each setting comes from one of four layers. A later layer overrides an earlier layer.

1. Built-in defaults
2. A config file: `linkcrawl.ini`, `.linkcrawl.json`, or a `[linkcrawl]` section in
   `setup.cfg`
3. Environment variables that start with `LINKCRAWL_`
4. Command-line options

Run `linkcrawl config` to see each value and the layer that set it.

## Example `linkcrawl.ini`

```ini
[linkcrawl]
timeout = 5
max_attempts = 3
rate_limit = 1
exclude_patterns = */logout, */admin/*
```

Unknown keys in a config file are errors. Unknown `LINKCRAWL_` variables are not errors, but
`linkcrawl config` shows a warning for each one.
