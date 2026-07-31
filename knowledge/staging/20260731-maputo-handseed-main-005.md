---
id: 20260731-maputo-handseed-main-005
kind: semantic
origin: tool-verified
confidence: high
status: staged
scope:
  - repo:workbench
  - subsystem:hooks
  - ticket-class:enforcement
provenance:
  verified_at: fd8d39a59a3c825b038c19847ef2dbd6e2feae5b
  cites:
    - path: hooks/knowledge-guard.sh
---

**`permission_mode` in a hook payload cannot confirm that a human is present.** A headless `claude -p`
run at default settings reports `"permission_mode":"default"` — byte-identical to an interactive session.

So attendance is not inferable from inside a hook and must be asserted by whatever starts the run. The
elevated modes (`acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`) are usable in one direction only:
they can raise suspicion of unattended operation, never confirm attendance. Any logic that treats an
elevated mode as evidence *for* something has the arrow backwards.

Separately verified: `permissionDecision: "deny"` holds in all five permission modes including
`bypassPermissions`, and `ask` is never silently auto-approved — under `acceptEdits` it degrades to
refusal headlessly, and prompts interactively.
