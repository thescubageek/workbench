# Important Notes

## Read-Only Analysis

- **NEVER change a judgment-bearing `status:` value** without explicit user confirmation
- **ALWAYS present the update plan** before applying a change behind Barrier 2 — the silent
  side (counters, git metadata, `not-started → in-progress`) applies without one
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

## Why Barrier 2 Is Scoped to Judgment

Counter reconciliation is deterministic — Step 2 counts, and the counted value lands — so asking
a human to approve it is ceremony, and a barrier that fires on trivia gets clicked through,
training the same reflex on the barrier that matters. Both times it fired during testing, the
entire proposal was `completed_tasks: 1 → 2`.

Git metadata is on the silent side because it is read from the repository, not judged. Leaving
it out stranded `git_commit` at the plan's creation commit — a stale fact that looked current.

`not-started → in-progress` is on the silent side because gating it was measured to break the
feature: the first checkpoint of every plan hit the barrier, and in a two-phase plan the
`complete` gate caught the second, so no checkpoint could ever be silent. A fully implemented
six-task plan ended up reading `status: not-started` with `completed_tasks: 6`.

The Phase 0 exemption in Step 3 exists because planning tasks are ticked while `design.md` is
still a draft; without it, the implementation-task guard and the `not-started → in-progress`
trigger contradict each other for every plan still in planning.

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
