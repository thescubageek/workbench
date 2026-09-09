---
name: status-sync
description: Surfaces drift between a plan's frontmatter counters and its actual checkbox state at phase end and session end, and points at /wb:update_status to reconcile.
user-invocable: false
allowed-tools: Read, Glob, Grep, Bash(grep:*)
---

# Status Sync Reminder

Checkbox state in `tasks.md` is the source of truth for task and phase status. The frontmatter
counters are a **derived cache** with exactly one writer, `/wb:update_status`.

A cache is allowed to be stale — the implementation stages flip checkboxes and defer the
counters deliberately, so drift between checkpoints is normal, not an error. What is *not*
acceptable is drift nobody notices, because a stale counter reads as fact. This skill makes it
visible and points at the one command that fixes it.

## When to Activate

- User completes a phase checkpoint
- User says "done", "finished", "complete" about implementation work
- At session end (before saying work is complete)

## Check Current State

Count the checkboxes and compare them with what the frontmatter claims:

```bash
# Scope to lines carrying a task ID — a plan's success criteria and prerequisites
# are checkboxes too, and counting them inflates progress.
grep -cE '^- \[x\] \*\*[A-Z0-9-]+\*\*' tasks.md    # actually done
grep -cE '^- \[ \] \*\*[A-Z0-9-]+\*\*' tasks.md    # actually remaining
grep -E '^(status|current_phase|total_tasks|completed_tasks):' tasks.md
```

## Drift Indicators

**Counters disagree with the checkboxes**:

- `completed_tasks` or `total_tasks` differs from the counts above
- The checkboxes are right; the counters are stale

**Phase appears complete but status doesn't say so**:

- Every checkbox in the current phase is `[x]`, but `current_phase` has not moved
- Or `status:` is still `not-started` while tasks are `[x]`

**Finished work is uncommitted**:

- Tasks are `[x]` but `git status --short` is dirty — under one-task-one-commit that means
  something did not finish, and it is the signal a cold session reads as "interrupted"

## When to Remind

```
📍 Status drift:
- Checkboxes: [A]/[B] tasks done
- Frontmatter: [X]/[Y]
- Run `/wb:update_status [project-dir]` to reconcile (it is the only writer of those fields)

Or if a phase looks complete:
- Every Phase [N] checkbox is [x], but current_phase is still [N]
- Run `/wb:update_status` after the checkpoint's manual verification
```

## When NOT to Remind

- Minor work in progress (mid-phase) — drift is expected here and reporting it is noise
- User explicitly said they'll update later
- Already reminded in this session
- Just starting work (not ending)

## DO NOT

- Update files directly
- **Rewrite the counters yourself** — `/wb:update_status` is their single writer, and a second
  writer reintroduces exactly the drift this skill exists to report
- Run commands automatically
- Interrupt creative/coding flow unnecessarily
- Remind repeatedly for the same issue
- Treat drift as an error — it is the expected state between checkpoints
