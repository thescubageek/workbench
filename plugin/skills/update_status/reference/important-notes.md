# Important Notes

## Read-Only Analysis

- **NEVER modify files** without explicit user confirmation
- **ALWAYS present the update plan** before applying changes
- **VERIFY actual progress** by reading file contents and counting checkboxes, not by trusting frontmatter

## Sole Writer

This skill is the **only** writer of the progress frontmatter fields — `status`,
`current_phase`, `total_tasks`, `completed_tasks`. The implementation stages flip checkboxes
and defer these fields to it.

That rule is the whole mechanism. Counters are a cache, and a cache with several writers and no
owner is exactly how these fields rotted before: two commands rewriting `current_phase` from
different beliefs about progress, neither wrong at the moment it wrote. One writer, deriving
from one source, cannot disagree with itself.

When the counters and the checkboxes disagree, **the checkboxes win, always**. Drift is expected
between checkpoints and is not an error — reconcile silently and report the delta.

## Atomic Updates

- Update all files in the same operation
- Don't leave files in inconsistent states
- If any update fails, report error and don't partial-update

## Git Metadata

- Capture current git state when updating
- This provides audit trail of when status changed
- Update timestamp reflects when status was updated, not when work was done

## Backward Transitions

- Only allow with explicit confirmation
- Warn user about regression
- Require reason for moving backward

## Phase Progression

- Detect current phase from the first unchecked task
- Don't skip phases - must complete in order
