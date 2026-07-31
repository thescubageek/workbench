---
id: 20260731-maputo-handseed-main-004
kind: semantic
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
    - path: .claude-plugin/plugin.json
      lines: "10-45"
---

**A shell redirect through the Bash tool produces no `PreToolUse` event.** `printf 'hello' > d.txt` run
via Bash created the file with no hook invocation logged at all, while a `Write` to a sibling path in the
same session did fire the hook.

Any control registered on `Write`/`Edit` is therefore blind to file changes made through Bash. This is
not fixable at the hook layer: matching paths inside arbitrary shell strings is unreliable, and a control
that fires on `grep -r commands/` trains the operator to disarm it, which is worse than a named hole.

The answer is a layer outside the agent's tool calls — CI, CODEOWNERS, branch protection. Anyone
reasoning about the completeness of a `PreToolUse` boundary needs this fact first.
