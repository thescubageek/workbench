# Completion message

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 5. Emit this once, after the handoff is saved.

```
✅ The handoff document is saved.

Saved to: [full path]/handoff-YYYY-MM-DD-HH-MM.md

This handoff records:
- Current progress: Phase [N], [X]/[Y] tasks complete
- Critical learnings: [count] discoveries
- Active blockers: [count] issues
- Next steps: [count] specific tasks
- Knowledge entries added: [count, or "none. Nothing met the bar"]

To resume this work in a new session:
/wb:resume_handoff [full path to handoff file]

The handoff contains the context that the next session needs.
```
