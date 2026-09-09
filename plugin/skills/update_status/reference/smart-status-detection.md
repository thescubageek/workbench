# Smart Status Detection

Detect status from actual content, not from what the frontmatter currently claims.

**The checkboxes in `tasks.md` are the source of truth** for task and phase status. Count them.
The frontmatter counters are a derived cache — this skill is their only writer, so when the two
disagree, the counters are what changes.

For research and design status, which are not expressed as checkboxes, use content analysis.

## Research Detection

- Count sections with real content vs placeholders
- Check for file:line references (indicates real research)
- Look for code snippets and detailed findings
- If >80% complete → suggest "complete"
- If >20% complete → suggest "in-progress"
- Otherwise → keep as "draft"

## Plan Detection

- Check if all phases have detailed "Changes Required"
- Verify success criteria are specific (not "[To be defined]")
- Cross-check with tasks.md for implementation progress
- If any task is `[x]` → suggest "implementing"
- If fully defined but nothing started → suggest "ready"
- Otherwise → keep as "draft"

## Tasks Detection

Count, don't assume:

```bash
# Task lines only — scope to lines carrying a task ID, so that a plan's own
# success criteria and prerequisites (also checkboxes) are not counted as tasks.
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # completed
grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # remaining
```

- All task lines `[x]` → suggest "complete"
- Any task line `[x]`, some `[ ]` → suggest "in-progress"
- No task line `[x]` → "not-started"
- `current_phase` is the phase containing the **first unchecked task**
- Percentage is completed ÷ total from those counts

**If a plan does not use task IDs**, fall back to counting every `^- \[[ x]\]` line inside
phase task sections, and say in the report that the count is approximate because task lines
could not be distinguished from criteria.
