---
id: 20260731-maputo-handseed-main-008
kind: procedural
origin: tool-verified
confidence: high
status: staged
scope:
  - repo:workbench
  - subsystem:testing
  - ticket-class:testing
provenance:
  verified_at: fd8d39a59a3c825b038c19847ef2dbd6e2feae5b
  cites:
    - path: scripts/probe-knowledge-guard
    - path: scripts/test-knowledge-read
---

**A test that only observes the positive case cannot distinguish a working control from one that always
fires.** Two instances of this in one project, both caught only by adding a control:

A hook probe wrote only its sentinel file and concluded the hook worked; in default permission mode a
`Write` prompts anyway, so the run proved nothing. The fix is an A/B **in the same session** — a control
file the hook ignores alongside the sentinel it should act on, differing in exactly one variable.

Worse, a probe whose fixture setup silently failed reported "the protected sentinel was REFUSED" as a
**pass** — a file that was never created is indistinguishable from one that was refused. The control
assertion is what failed and exposed it. (Root cause: `local a="$1" b="$X/$a"` expands every argument
before any of them binds, so `$a` was empty.)

Rule: any assertion that something did **not** happen needs a paired assertion that something else
**did**, or it passes vacuously.
