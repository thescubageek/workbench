# Error message formats

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 3. Use these shapes, so that findings are consistent and easy to find with grep.

## Critical errors

```
❌ Missing Required File: tasks.md
   Location: [project-dir]/tasks.md
   Cause: The file does not exist
   Impact: Implementation work cannot be tracked
   Fix: Run /wb:create_tasks to write tasks.md
```

```
❌ Duplicate Task IDs: P2-T7
   Location: tasks.md, lines 214 and 288
   Cause: Two tasks share one local ID
   Impact: A commit, a journal entry or a handoff cites a task by its ID. A duplicate ID makes those citations ambiguous
   Fix: Renumber the later task. Never renumber a task that is already cited
```

```
❌ Stale Tracking Guidance
   File: tasks.md, line 343
   Text: "these checkboxes are documentation only"
   Cause: The plan is older than 2.0.0, when status moved into these checkboxes
   Impact: A reader who follows it records status nowhere
   Fix: Delete the note. The checkboxes are the record
```

```
❌ Status Progression Violation
   Files: design.md (approved), research.md (draft)
   Cause: The design is approved, but the research is not complete
   Impact: The workflow requires research to complete before design
   Fix: Complete the research, OR set the design back to draft
```

## Warnings

```
⚠️ Missing Git Metadata
   File: research.md
   Fields: git_commit, git_branch
   Impact: The code state at the time of the research is not recorded
   Fix: Run /wb:update_status to fill the metadata
```

```
⚠️ Placeholder Content Found
   File: design.md, line 45
   Text: "[To be added]"
   Impact: The documentation is incomplete
   Fix: Write the design decision, or remove the placeholder
```

```
⚠️ Counter Drift
   File: tasks.md frontmatter
   Cause: completed_tasks: 13, but 18 task lines are [x]
   Impact: None to correctness. The checkboxes are the authority
   Fix: Run /wb:update_status. It is the only writer of these fields
```

```
⚠️ Resolved Record Without a Pointer
   File: research.md, Open Questions row Q3
   Cause: The state is "Resolved 2026-09-08", but it names no destination
   Impact: The decision cannot be found from the question that it answered
   Fix: Point the row at the place where the decision is recorded (design.md → Technical Decisions)
```
