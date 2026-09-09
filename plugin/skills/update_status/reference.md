# update_status — reference

Read the **section you need**, when its step directs you to.

Sections: `Status Transition Logic` (Step 3) · `Smart Status Detection` (Step 2) ·
`Error Handling` (any step) · `Important Notes` · `Configuration`

## Status Transition Logic

### Research Status Transitions

```
draft → in-progress
  Trigger: User starts researching, some sections have content

in-progress → complete
  Trigger: All sections populated with real findings
  Requires: No placeholder text like "[To be added]"
```

### Plan Status Transitions

```
draft → ready
  Trigger: All phases defined with success criteria
  Requires: research.md is complete

ready → implementing
  Trigger: The first task checkbox is flipped to [x]

implementing → complete
  Trigger: Every task checkbox in every phase is [x], and the work is committed
```

### Tasks Status Transitions

```
not-started → in-progress
  Trigger: At least one task checkbox is [x]
  Updates: current_phase to the phase holding the first unchecked task

in-progress → complete
  Trigger: Every task checkbox is [x]
  Requires: each phase's manual verification confirmed at its checkpoint
```

## Smart Status Detection

Detect status from actual content, not from what the frontmatter currently claims.

**The checkboxes in `tasks.md` are the source of truth** for task and phase status. Count them.
The frontmatter counters are a derived cache — this skill is their only writer, so when the two
disagree, the counters are what changes.

For research and design status, which are not expressed as checkboxes, use content analysis.

### Research Detection

- Count sections with real content vs placeholders
- Check for file:line references (indicates real research)
- Look for code snippets and detailed findings
- If >80% complete → suggest "complete"
- If >20% complete → suggest "in-progress"
- Otherwise → keep as "draft"

### Plan Detection

- Check if all phases have detailed "Changes Required"
- Verify success criteria are specific (not "[To be defined]")
- Cross-check with tasks.md for implementation progress
- If any task is `[x]` → suggest "implementing"
- If fully defined but nothing started → suggest "ready"
- Otherwise → keep as "draft"

### Tasks Detection

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

## Error Handling

### Invalid Transitions

If user requests invalid transition:

```
⚠️ Invalid Status Transition

Cannot transition design.md from 'draft' to 'implementing' because:
- research.md is still in 'draft' status
- No task checkbox in tasks.md is [x]

Valid next steps:
1. Complete research first (/wb:create_research)
2. Move design to 'ready' status once research is complete
3. Flip a task checkbox in tasks.md to begin implementing
```

### Missing Files

If files don't exist:

```
❌ Missing Documentation Files

Expected files in [directory]:
- research.md [✓/✗]
- design.md [✓/✗]
- tasks.md [✓/✗]

Run /wb:create_project first to initialize the documentation structure.
```

### Inconsistent State

If files have conflicting status:

```
⚠️ Inconsistent Status Detected

Current state:
- design.md: implementing
- tasks.md: not-started (0 of 24 tasks [x])

This is inconsistent. Suggesting correction:
- Set design.md back to 'ready' OR
- Confirm implementation has started and flip the tasks that are done

Which would you prefer?
```

## Important Notes

### Read-Only Analysis

- **NEVER modify files** without explicit user confirmation
- **ALWAYS present the update plan** before applying changes
- **VERIFY actual progress** by reading file contents and counting checkboxes, not by trusting frontmatter

### Sole Writer

This skill is the **only** writer of the progress frontmatter fields — `status`,
`current_phase`, `total_tasks`, `completed_tasks`. The implementation stages flip checkboxes
and defer these fields to it.

That rule is the whole mechanism. Counters are a cache, and a cache with several writers and no
owner is exactly how these fields rotted before: two commands rewriting `current_phase` from
different beliefs about progress, neither wrong at the moment it wrote. One writer, deriving
from one source, cannot disagree with itself.

When the counters and the checkboxes disagree, **the checkboxes win, always**. Drift is expected
between checkpoints and is not an error — reconcile silently and report the delta.

### Atomic Updates

- Update all files in the same operation
- Don't leave files in inconsistent states
- If any update fails, report error and don't partial-update

### Git Metadata

- Capture current git state when updating
- This provides audit trail of when status changed
- Update timestamp reflects when status was updated, not when work was done

### Backward Transitions

- Only allow with explicit confirmation
- Warn user about regression
- Require reason for moving backward

### Phase Progression

- Detect current phase from the first unchecked task
- Don't skip phases - must complete in order

## Configuration

The skill accepts the directory path as a parameter:

```
/wb:update_status docs/plans/2025-10-07-my-project
```

Or prompts for it if not provided.
