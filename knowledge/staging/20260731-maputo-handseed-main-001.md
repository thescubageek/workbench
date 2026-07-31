---
id: 20260731-maputo-handseed-main-001
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
    - path: .claude-plugin/plugin.json
      lines: "10-45"
    - path: scripts/lint-hook
      lines: "9-19"
---

Hook configuration in Claude Code is read **once at session start**. Editing a settings file or
`.claude-plugin/plugin.json` mid-session registers nothing, so an in-session edit followed by an
in-session check will appear to pass while having exercised no hook at all.

Consequence for anyone testing a hook here: a contract test that feeds a payload to the script on stdin
tests *the script*, and only a child `claude -p` session started with `--settings` tests *registration
and enforcement*. Both layers are needed and neither substitutes for the other — a contract test cannot
catch a matcher typo or an unregistered event.

Verified by executing hook probes against Claude Code 2.1.195 as headless child sessions, repeatedly,
across Phase 0 and Phase 2 of the knowledge-store work.
