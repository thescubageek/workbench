# resume_handoff — templates

Read the **section you need**, when its step directs you to.

Sections: `Resume confirmation` (Step 6)

## Resume confirmation

Step 6 — emitted once, when context has been restored and work is about to continue.

```
✅ Successfully resumed from handoff

Handoff Summary:
- Created: [date/time from handoff]
- Previous Session: ran on [model]
- Tasks Completed: [X]/[Y] (counted from tasks.md checkboxes, not from the handoff's claim)
- Current Phase: [N] - [name]

Key Context Restored:
- [Critical learning 1]
- [Critical learning 2]
- [Active blocker if any]

Current State:
- Git: [branch] at [commit]
- Uncommitted changes: [YES — what they are / NO]
- Tests: [PASSING/FAILING]
- Plan: [X]/[Y] tasks [x]; next unchecked is [ID] — [title]
- Journal: last entry [OPEN since <time> / CLOSED]

Reconciliation:
[Only if the handoff and the working tree disagree — say which is which and which
 one you are trusting. Omit entirely when they agree.]

Ready to continue with:
[Next immediate task from tasks.md]

Using approach:
[Recommended approach from handoff]

Watching for:
- [Gotcha 1 from handoff]
- [Gotcha 2 from handoff]
```
