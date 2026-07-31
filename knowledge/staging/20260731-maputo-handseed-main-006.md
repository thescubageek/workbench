---
id: 20260731-maputo-handseed-main-006
kind: semantic
origin: tool-verified
confidence: high
status: staged
scope:
  - repo:workbench
  - subsystem:hooks
  - ticket-class:hook-development
provenance:
  verified_at: fd8d39a59a3c825b038c19847ef2dbd6e2feae5b
  cites:
    - path: hooks/knowledge-guard.sh
---

**The `file_path` a hook receives is a resolved absolute path, and not necessarily the one anyone typed.**
Claude Code 2.1.195 was observed redirecting `Write` calls into a per-session scratchpad
(`/private/tmp/claude-501/<slug>/<uuid>/scratchpad/`) rather than the working directory the prompt named,
and `/tmp` arrives as its `/private/tmp` realpath.

Two consequences for any hook that matches on paths. Compare **resolved** paths, including symlinks and
the `/tmp` → `/private/tmp` rewrite, never the literal string in `tool_input`. And do not read "outside
my expected prefix" as "irrelevant" — a naive repo-relative prefix match is both bypassable and wrong,
because an agent write can land entirely outside the repo.
