# resolve_questions — templates

Write this output in wb Technical English (WBTE): read [technical-english.md](../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Read this when Step 4d directs you to. These are the **canonical** shapes for every record that
this skill writes. Step 4d points here and does not repeat them, so only one definition must
stay correct.

## Persistence Format Reference

A question from `research.md` changes **two** places when it is resolved. The decision goes into `design.md`. The source question in `research.md` gets a pointer, because research contains facts only.

**① The decision goes into `## Technical Decisions` in `design.md`:**

```markdown
## Technical Decisions

### Data Model
- Partial responses persist server-side via a new `in_progress_responses` column
  - Rationale: it follows the charting-note autosave precedent. The PHI posture for that path is already approved
  - Trade-off: one more write path to keep consistent with final-submit
  - Source: research.md Q1 · Decided 2026-05-18
```

**② The source question in `research.md` becomes a pointer. It contains no decision and no rationale, because research contains facts only:**

```markdown
## Open Questions

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| Q1 | Should partial answers leave the device (PHI posture)? | persistence layer | **Resolved 2026-05-18** → design.md (## Technical Decisions) |
| Q2 | Is multi-device resume in scope, or same-device only? | resume scope | Open |
```

**A question that lives in `design.md` or `execution.md`** is resolved in place, because decisions belong there:

```markdown
- Should branching semantics change for resumed sessions?
  - **Decided 2026-05-18**: No. Resume uses the existing branch, so the state machine keeps one path. (Rationale: it avoids a second code path that nobody asked for.)
```

**Update the tracking tables:**

```markdown
## Pending Decisions

| ID | Decision Needed | Blocks | State |
| -- | --------------- | ------ | ----- |
| PD1 | Persistence layer for partial responses | execution start | Resolved 2026-05-18 → design.md (## Technical Decisions) |

### Assumptions

| ID | Assumption | Validated? |
| -- | ---------- | ---------- |
| A1 | Autosave precedent covers PHI posture | Validated 2026-05-18 |
```
