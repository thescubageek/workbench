---
name: update_status
description: Update status across all project documentation files based on progress
argument-hint: "[project-directory]"
allowed-tools: Read
---

# Update Project Status

Reconciles status across all project documentation files (research.md, design.md, tasks.md) against actual progress, ensuring consistency and proper state transitions.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- [templates.md](templates.md) — the status update plan, the per-file frontmatter fragments, and the completion summary, under named sections
- [reference.md](reference.md) — status transition logic, detection rules, error-handling messages, the sole-writer rule, configuration

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## CRITICAL: Status Update Philosophy

- **READ BEFORE WRITE**: Always read ALL documentation files FULLY before making any updates
- **COUNT, DON'T ASSUME**: progress comes from counting checkboxes, never from the counters you are about to rewrite
- **CASCADING UPDATES**: Status changes may trigger updates across multiple files
- **MAINTAIN CONSISTENCY**: Ensure all files reflect the same project reality
- **NO REGRESSION**: Never move status backward without explicit user confirmation
- **ATOMIC UPDATES**: Update all affected files together, not one at a time

### This skill is the sole writer of the progress frontmatter

`status`, `current_phase`, `total_tasks`, `completed_tasks` have exactly one writer: this
skill. Every other stage flips checkboxes and defers these fields here.

**Checkbox state in `tasks.md` is the source of truth.** The counters are a derived cache of
it. When they disagree — which is normal between checkpoints, not an error — **the checkboxes
win**, and the counters are what change. Reconcile, report the delta, and move on.

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:update_status docs/plans/2025-01-08-auth/`):
   - Use `$1` as the project directory
   - Read all documentation files immediately
   - Analyze and propose status updates

2. **If no arguments**:

   ```
   I'll help you update the project status. Please provide:
   1. Path to the project documentation directory

   Example: /wb:update_status docs/plans/2025-01-08-auth/
   ```

## Steps to Execute

### Step 1: Read Current State (CRITICAL)

**⛔ BARRIER 1**: Read ALL files FULLY before proceeding

1. **Read research.md FULLY** - Check status, completion, findings
2. **Read design.md FULLY** - Check status, phase progress, implementation state
3. **Read tasks.md FULLY** - Check current_phase, counters, and every task checkbox

**IMPORTANT**: Use Read tool WITHOUT limit/offset parameters

Record current state as *claimed*: the status of each file, `current_phase`, and the counter
values. These are the numbers you will test, not the numbers you will trust.

### Step 2: Count Actual Progress

This is the measurement step. Everything downstream derives from it.

```bash
# Task lines only — scope to lines carrying a task ID, so that a plan's own success
# criteria and prerequisites (also checkboxes) are not miscounted as tasks.
grep -cE '^- \[x\] \*\*[A-Z0-9-]+\*\*' tasks.md    # completed
grep -cE '^- \[ \] \*\*[A-Z0-9-]+\*\*' tasks.md    # remaining
```

Then:

1. **Locate the current phase** — the phase containing the **first unchecked task**.
2. **Compute the delta** between the counters and the counts. Drift is expected; record its
   size for the report.
3. **Analyze research.md and design.md by content**, since their status is not expressed as
   checkboxes. Read the `## Smart Status Detection` section of [reference.md](reference.md) for
   how each is judged.

**Examine the files to determine actual state.**

### Step 3: Determine Status Transitions

Read the `## Status Transition Logic` section of [reference.md](reference.md) NOW and determine the appropriate status for each file.

Validation rules that constrain the result:

- Cannot mark design as `ready` if research is still `draft`
- Cannot mark tasks as `in-progress` if design is still `draft`
- Cannot mark design as `complete` if tasks is not `complete`
- Cannot mark tasks `complete` while any task checkbox is `[ ]`
- `implementing` requires at least one task checkbox `[x]`

### Step 4: Present Status Update Plan

Read the `## Status update plan` section of [templates.md](templates.md) NOW and present it.

**⛔ BARRIER 2**: Wait for user confirmation before proceeding

### Step 5: Apply Updates

After the user confirms, read the `## Frontmatter fragments` section of [templates.md](templates.md) NOW and apply them to research.md, design.md and tasks.md.

The counters written are the **counted** values from Step 2 — not the previous values adjusted,
and not an estimate. If the count and the old counter disagree, the count is what lands.

### Step 6: Verify Consistency

**⛔ BARRIER 3**: Verify all updates were applied correctly

1. **Read each file back** to verify changes were applied
2. **Re-count the checkboxes** and confirm the written counters now match
3. **Check consistency**:
   - All files have same `last_updated` date
   - All files have same git metadata
   - Status transitions are valid across all files
4. **Validate no regressions**: status didn't move backward unexpectedly, phase numbers make sense

### Step 7: Confirm Completion

Read the `## Completion summary` section of [templates.md](templates.md) NOW and present it.

## Important Notes

See [reference.md](reference.md) — status transition logic, smart status detection, error-handling messages, the sole-writer rule, and configuration.
