---
id: 20260731-maputo-handseed-main-002
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
    - path: scripts/lint-hook
      lines: "9-19"
    - path: .claude-plugin/plugin.json
      lines: "10-45"
---

Every hook script receives its event payload as **JSON on stdin**, not via an environment variable.
`scripts/lint-hook:9-19` is the in-repo reference: it reads stdin into `PAYLOAD`, extracts
`.tool_input.file_path` with `jq`, and falls back to `grep`/`sed` when `jq` is absent.

Copy that idiom including the fallback. The plugin ships through a marketplace clone and cannot assume
`jq` on a user's machine — nor `node_modules`, which is why no runtime component may depend on `ajv`
even though it is a hard dev dependency.

`CLAUDE_TOOL_ARGS` exists only as a legacy fallback for an empty stdin; it is not the channel.
