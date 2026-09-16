# resolve_questions — templates

Read this when Step 4d directs you to. These are the **canonical** shapes for every record this
skill writes; Step 4d points here rather than restating them, so there is one definition to
keep correct.

## Persistence Format Reference

Resolving one question raised in `research.md` touches **two** places: the decision lands in `design.md`, and the source question in `research.md` gets a pointer (research stays facts-only).

**① Decision lands in `design.md` `## Technical Decisions`:**

```markdown
## Technical Decisions

### Data Model
- Partial responses persist server-side via a new `in_progress_responses` column
  - Rationale: aligns with the charting-note autosave precedent; PHI posture already approved for that path
  - Trade-off: one more write path to keep consistent with final-submit
  - Source: research.md Q1 · Decided 2026-05-18
```

**② Source question in `research.md` becomes a pointer (no decision/rationale embedded — facts-only):**

```markdown
## Open Questions

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| Q1 | Should partial answers leave the device (PHI posture)? | persistence layer | **Resolved 2026-05-18** → design.md (## Technical Decisions) |
| Q2 | Is multi-device resume in scope, or same-device only? | resume scope | Open |
```

**Resolving a question that lives in `design.md`/`execution.md`** (decisions belong there, so record in place):

```markdown
- Should branching semantics change for resumed sessions?
  - **Decided 2026-05-18**: No — resume reuses the existing branch; keeps the state machine single-path. (Rationale: avoids a second code path no one asked for.)
```

**Reconciling tracking tables:**

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
