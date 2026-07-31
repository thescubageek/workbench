---
id: 20260731-maputo-handseed-main-010
kind: semantic
origin: model-narrated
confidence: low
status: staged
scope:
  - repo:workbench
  - subsystem:hooks
  - ticket-class:hook-development
provenance:
  verified_at: fd8d39a59a3c825b038c19847ef2dbd6e2feae5b
  cites:
    - path: hooks/knowledge-capture.sh
---

A `Stop` hook should never exit non-zero to signal a problem: exit code 2 on `Stop` is documented to
block the stop and feed stderr back to the model, which risks a stop → continue → stop loop.
`hooks/knowledge-capture.sh` therefore always exits 0 and surfaces failure on stderr plus a
`systemMessage`, with `--selfcheck` as the deterministic health channel.

**This is `model-narrated` on purpose, and the label is the point.** The design decision was made and
implemented, but the loop itself was never provoked — no probe ever returned exit 2 from a `Stop` hook
to see what actually happens. The claim rests on documentation and reasoning, not on an observation a
tool produced. Reading a doc and concluding something is narration; `knowledge/SCHEMA.md` is explicit
that when unsure it is `model-narrated`, and that mislabelling this axis defeats the write policy.

What *was* verified by execution: the `systemMessage` reaches the session transcript verbatim as an
`attachment` record, carrying both the hook's message and the underlying `knowledge-worktree`
diagnostic. So the loud-failure channel demonstrably works. Whether exit 2 would loop remains untested.
