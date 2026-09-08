---
name: status-sync
description: Monitors beads status and reminds about bd sync at session end or when phases complete.
allowed-tools: Read, Glob, Grep, Bash(bd:*)
---

# Status Sync Reminder

Reminds about beads synchronization when completing work or ending sessions.

## When to Activate

- User completes a phase checkpoint
- User says "done", "finished", "complete" about implementation work
- At session end (before saying work is complete)

## Check Current State

```bash
bd stats                        # Overall progress
bd ready                        # What's available
bd list --status=in_progress    # What's claimed
```

## Drift Indicators

**Work done but not synced**:

- Issues closed in session but `bd sync` not run
- End of session approaching

**Phase complete but not closed**:

- All tasks in a phase done, but beads issue still open
- Reminder: `bd close [phase-id] --reason "..."`

## When to Remind

```
📍 Beads sync reminder:
- [X] issues updated this session
- Run `bd sync` before ending session

Or if phase complete:
- Phase [N] appears complete
- Run: bd close [phase-id] --reason "Phase N complete"
```

## When NOT to Remind

- Minor work in progress (mid-phase)
- User explicitly said they'll update later
- Already reminded in this session
- Just starting work (not ending)

## DO NOT

- Update files directly
- Run commands automatically
- Interrupt creative/coding flow unnecessarily
- Remind repeatedly for the same issue
