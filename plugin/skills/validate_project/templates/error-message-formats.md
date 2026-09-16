# Error message formats

Step 3 — use these shapes so findings are consistent and greppable.

## Critical errors

```
❌ Missing Required File: tasks.md
   Location: [project-dir]/tasks.md
   Cause: File does not exist
   Impact: Cannot track implementation work
   Fix: Run /wb:create_tasks to generate tasks.md
```

```
❌ Duplicate Task IDs: P2-T7
   Location: tasks.md, lines 214 and 288
   Cause: two tasks share one local ID
   Impact: an ID is the handle a commit, journal entry or handoff cites — a duplicate makes those citations ambiguous
   Fix: renumber the later task; never renumber one that has already been cited
```

```
❌ Stale Tracking Guidance
   File: tasks.md, line 343
   Text: "these checkboxes are documentation only"
   Cause: plan predates 2.0.0, when status moved into these checkboxes
   Impact: a reader following it will not record status anywhere
   Fix: delete the note; the checkboxes are the record
```

```
❌ Status Progression Violation
   Files: design.md (approved), research.md (draft)
   Cause: Design approved but research not complete
   Impact: Violates workflow: research must complete before design
   Fix: Complete research OR set design back to draft
```

## Warnings

```
⚠️ Missing Git Metadata
   File: research.md
   Fields: git_commit, git_branch
   Impact: Cannot track code state when research was done
   Fix: Run /wb:update_status to populate metadata
```

```
⚠️ Placeholder Content Found
   File: design.md, line 45
   Text: "[To be added]"
   Impact: Incomplete documentation
   Fix: Document the design decision or remove placeholder
```

```
⚠️ Counter Drift
   File: tasks.md frontmatter
   Cause: completed_tasks: 13, but 18 task lines are [x]
   Impact: none to correctness — the checkboxes are authoritative
   Fix: Run /wb:update_status; it is the only writer of these fields
```

```
⚠️ Resolved Record Without a Pointer
   File: research.md, Open Questions row Q3
   Cause: state is "Resolved 2026-09-08" but names no destination
   Impact: the decision cannot be found from the question it answered
   Fix: point the row at where the decision was recorded (design.md → Technical Decisions)
```
