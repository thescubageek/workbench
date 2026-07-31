---
id: 20260731-maputo-handseed-main-003
kind: procedural
origin: tool-verified
confidence: high
status: staged
scope:
  - repo:workbench
  - subsystem:hooks
  - ticket-class:enforcement
  - ticket-class:security
provenance:
  verified_at: fd8d39a59a3c825b038c19847ef2dbd6e2feae5b
  cites:
    - path: hooks/knowledge-guard.sh
---

An environment variable set on the command line that launches a session **reaches that session's
`PreToolUse` hooks, and the agent cannot change what the hook sees.** A tool-layer process is a child of
the session; it cannot mutate the parent environment the hook inherits.

Verified as an A/B in one session: launched with `WB_SELF_EXTENSION=interactive`, the hook saw
`interactive`; a control run with no variable set saw it unset, so the value genuinely came from the
launch environment. In the same run the agent's own Bash tool executed `export
WB_SELF_EXTENSION=full-auto` **successfully** — it echoed `now full-auto` — and the hook still saw
`interactive` on the next `Write`.

This is what makes an env var the right channel for any signal the agent must not be able to forge.

The honest limit: unreachable for the **running** session, influenceable for a **later** one, because
`.claude/settings.json` has an `env` block applied at session start. Protect `.claude/` if the signal
matters.
