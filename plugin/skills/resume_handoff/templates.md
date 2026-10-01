# resume_handoff — templates

Write this output in wb Technical English (WBTE): read [technical-english.md](../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Read the **section you need**, when its step directs you to.

Sections: `Resume confirmation` (Step 6)

## Resume confirmation

Step 6. Emit this once, when the context is restored and work is about to continue.

```
✅ Work resumed from the handoff.

Handoff Summary:
- Created: [date/time from handoff]
- Previous Session: ran on [model]
- Tasks Completed: [X]/[Y] (counted from the tasks.md checkboxes, not taken from the handoff)
- Current Phase: [N] - [name]

Key Context Restored:
- [Critical learning 1]
- [Critical learning 2]
- [Active blocker if any]

Current State:
- Git: [branch] at [commit]
- Uncommitted changes: [YES, and what they are / NO]
- Tests: [PASSING/FAILING]
- Plan: [X]/[Y] tasks [x]. The next unchecked task is [ID] — [title]
- Journal: last entry [OPEN since <time> / CLOSED]

Reconciliation:
[Only if the handoff and the working tree disagree. Say what each one says, and
 which one you trust. Omit this section when they agree.]

Next task:
[Next immediate task from tasks.md]

Approach:
[Recommended approach from handoff]

Watch for:
- [Gotcha 1 from handoff]
- [Gotcha 2 from handoff]
```
