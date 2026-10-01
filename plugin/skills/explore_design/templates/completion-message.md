# Completion message

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 7. Emit this once, after the document is written.

```
✅ Exploration recorded: [path]/thoughts/[YYYY-MM-DD]-[topic].md

Decided: [chosen direction]
Because: [one-line rationale]
Rejected: [N] alternatives, with reasons

This stage does not write design.md. Run:
  /wb:create_design [project-dir]

It finds this record, presents the decision for confirmation, and writes it
into design.md. It also carries the rejected alternatives across, so the
reasoning is not generated again.
```
