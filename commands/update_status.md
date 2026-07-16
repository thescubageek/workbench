---
description: Update status across all project documentation files based on progress
argument-hint: "[project-directory]"
---

# Update Project Status

Intelligently updates status across all project documentation files (research.md, design.md, tasks.md) based on actual progress, ensuring consistency and proper state transitions.

## CRITICAL: Status Update Philosophy

- **READ BEFORE WRITE**: Always read ALL documentation files FULLY before making any updates
- **VERIFY STATE**: Confirm current state matches actual progress before transitioning
- **CASCADING UPDATES**: Status changes may trigger updates across multiple files
- **MAINTAIN CONSISTENCY**: Ensure all files reflect the same project reality
- **NO REGRESSION**: Never move status backward without explicit user confirmation
- **ATOMIC UPDATES**: Update all affected files together, not one at a time

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

#### Check Beads State

```bash
bd stats                        # Overall counts
bd list                         # All issues with status
bd list --status=in_progress    # Active work
bd list --status=closed         # Completed work
```

**Beads mode** (see `docs/beads-stealth-mode.md`) does not affect status updates — both modes hold the same beads state, differing only in persistence.

Check tasks.md for beads phase IDs:

```yaml
# Look for these in frontmatter:
beads_epic: [epic-id]
beads_phases:
  phase1: [phase1-id]
  phase2: [phase2-id]
```

#### Read Documentation Files

Read all documentation files to understand current state:

1. **Read research.md FULLY** - Check status, completion, findings
2. **Read design.md FULLY** - Check status, phase progress, implementation state
3. **Read tasks.md FULLY** - Check current_phase, beads_tasks frontmatter (for reference only)

**IMPORTANT**: Use Read tool WITHOUT limit/offset parameters

Record current state:

- Research status: [draft/in-progress/complete]
- Design status: [draft/ready/implementing/complete]
- Tasks status: [not-started/in-progress/complete]
- Current phase: [number]
- Completed tasks: [count]
- Total tasks: [count]
- Beads phase issues status (open/in_progress/closed)

### Step 2: Analyze Actual Progress

**think deeply**

Examine the files to determine actual state:

1. **Research Analysis**:
   - Are all required sections populated with real content?
   - Does it have detailed findings with file:line references?
   - Are there still placeholder sections like "[To be added]"?
   - Determine: draft | in-progress | complete

2. **Design Analysis**:
   - Are design decisions documented with rationale?
   - Are success criteria measurable and complete?
   - Is implementation started (check tasks.md)?
   - Are all design aspects complete?
   - Determine: draft | ready | implementing | complete

3. **Tasks Analysis** (beads is ONLY source of truth):
   - Check beads issues: `bd stats`, `bd list --status=closed`, `bd list --status=in_progress`
   - Check phase milestones: `bd show [phase-milestone-id]` for each phase
   - Check all task issues: `bd list` to see task status
   - Closed phase milestone = all phase tasks complete
   - In-progress tasks = active work
   - Open tasks with no blockers = ready to start
   - DO NOT check markdown checkboxes (documentation only, not tracking)

   Determine: not-started | in-progress | complete

4. **Progress Calculation**:
   - Count closed task issues: `bd list --status=closed | wc -l`
   - Count total task issues from tasks.md frontmatter `beads_tasks`
   - Identify active phase: check which phase milestone has open tasks
   - Check current work: `bd list --status=in_progress`
   - Check blockers: `bd blocked`
   - Calculate percentage: (closed_tasks / total_tasks) * 100

### Step 3: Determine Status Transitions

Based on analysis, determine appropriate status for each file:

**Status Progression Rules**:

1. **research.md**:
   - `draft` → Has frontmatter but minimal/placeholder content
   - `in-progress` → Has some findings but incomplete sections
   - `complete` → All sections populated with real findings, no placeholders

2. **design.md**:
   - `draft` → Template structure, no real design decisions made
   - `ready` → All design decisions documented, ready for execution planning
   - `implementing` → Tasks have started (tasks.md shows progress)
   - `complete` → All design implemented and verified

3. **tasks.md**:
   - `not-started` → No beads task issues closed, current_phase: 0
   - `in-progress` → Some beads task issues closed or in_progress
   - `complete` → All beads task issues AND phase milestones closed

**Validation Rules**:

- Cannot mark design as `ready` if research is still `draft`
- Cannot mark tasks as `in-progress` if design is still `draft`
- Cannot mark design as `complete` if tasks is not `complete`
- `implementing` requires at least one beads task issue in_progress or closed

### Step 4: Present Status Update Plan

Show user what will change:

```
📊 Current Status Analysis:

**research.md**
- Current: [current-status]
- Proposed: [new-status]
- Reason: [why this transition is appropriate]

**design.md**
- Current: [current-status]
- Proposed: [new-status]
- Reason: [why this transition is appropriate]

**tasks.md**
- Current: [current-status]
- Current Phase: [phase-number]
- Completed: [X]/[Y] tasks ([percentage]%)
- Proposed: [new-status]
- Proposed Phase: [phase-number]
- Reason: [why this transition is appropriate]

**Beads Status**:
- Epic: [epic-id] - [status]
- Phase 1: [phase1-id] - [open/in_progress/closed]
- Phase 2: [phase2-id] - [open/in_progress/closed]
- ...

**Git Metadata Update**:
- New git_commit: [current commit hash]
- New git_branch: [current branch]

Do you want to proceed with these updates? (yes/no)
```

### Step 5: Apply Updates

**⛔ BARRIER 2**: Wait for user confirmation before proceeding

After user confirms, update all files:

#### Update research.md

Update frontmatter:

```yaml
status: [new-status]
last_updated: [YYYY-MM-DD]
git_commit: [current-commit]
git_branch: [current-branch]
```

#### Update design.md

Update frontmatter:

```yaml
status: [new-status]
last_updated: [YYYY-MM-DD]
git_commit: [current-commit]
git_branch: [current-branch]
```

If transitioning to `implementing`, add implementation notes:

```markdown
## Implementation Notes

Started: [YYYY-MM-DD]
- Implementation began on phase [N]
- [Any relevant context about starting implementation]
```

#### Update tasks.md

Update frontmatter:

```yaml
status: [new-status]
last_updated: [YYYY-MM-DD]
current_phase: [calculated-phase-number]
completed_tasks: [actual-count]
git_commit: [current-commit]
git_branch: [current-branch]
```

Update Progress Overview table to reflect actual counts.

Add implementation notes if status changes:

```markdown
### Implementation Notes
- Status updated to [new-status] on [YYYY-MM-DD]
- [Reason for status change]
```

#### Reconcile Beads State

If markdown shows phases complete that beads shows open, sync them:

```bash
# For each phase marked complete in markdown but open in beads:
bd close [phase-id] --reason "Reconciliation: marked complete in tasks.md"
```

### Step 6: Verify Consistency

**⛔ BARRIER 3**: Verify all updates were applied correctly

After all updates:

1. **Read each file back** to verify changes were applied
2. **Check consistency**:
   - All files have same `last_updated` date
   - All files have same git metadata
   - Status transitions are valid across all files
3. **Validate no regressions**:
   - Status didn't move backward unexpectedly
   - Task counts are accurate
   - Phase numbers make sense

### Step 7: Confirm Completion

Present summary:

```
✅ Status updated successfully!

📁 Project: [project-name]
📊 Updates Applied:

**research.md**: [old] → [new]
**design.md**: [old] → [new]
**tasks.md**: [old] → [new]
  - Phase: [number]
  - Progress: [X]/[Y] tasks ([percentage]%)

**Metadata Updated**:
- Last updated: [YYYY-MM-DD]
- Git commit: [commit-hash]
- Git branch: [branch-name]

**Next Steps**:
[Contextual suggestions based on new status]
```

### Step 8: Sync Beads State

After updating status, sync beads state:

```bash
bd sync    # Export beads to .beads/issues.jsonl

# In git mode, commit the beads state if needed
if [ "$BEADS_MODE" != "stealth" ]; then
  if git diff --quiet .beads/ 2>/dev/null; then
    echo "No beads changes to commit"
  else
    git add .beads/
    git commit -m "Sync beads state after status update"
  fi
fi
```

**Why this matters**:

- **Stealth mode**: Keeps local beads database in sync with .beads/ files
- **Git mode**: Persists beads state to git for cross-machine sync
- Both modes: Ensures beads database is up-to-date

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
  Trigger: First beads task issue in_progress or closed
  Requires: At least one beads task issue has status != open

implementing → complete
  Trigger: All beads tasks complete and verified
  Requires: All beads task issues AND phase milestones closed
```

### Tasks Status Transitions

```
not-started → in-progress
  Trigger: First beads task issue in_progress or closed
  Updates: current_phase to active phase number

in-progress → complete
  Trigger: All beads task issues closed, all phase milestone issues closed
  Requires: All phases verified via beads
```

## Smart Status Detection

The command should intelligently detect status based on actual content.

**Beads is the ONLY source of truth** for task/phase status. Use `bd list`, `bd show [id]`, `bd stats` to get authoritative status.

**NEVER check markdown checkboxes** - they are documentation only and do not reflect actual status.

For research and design status (not tracked in beads), use content analysis:

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
- If tasks have progress → suggest "implementing"
- If fully defined but no tasks started → suggest "ready"
- Otherwise → keep as "draft"

### Tasks Detection

**Use beads only**:

- Count closed issues: `bd list --status=closed | grep -v milestone | wc -l`
- Count total task issues from frontmatter `beads_tasks`
- Identify active phase: check which phase milestone has open blocking tasks
- If all task issues closed AND all phase milestones closed → suggest "complete"
- If any task issue in_progress OR closed → suggest "in-progress" and update current_phase
- Calculate accurate percentage from beads counts
- DO NOT count markdown checkboxes

## Error Handling

### Invalid Transitions

If user requests invalid transition:

```
⚠️ Invalid Status Transition

Cannot transition design.md from 'draft' to 'implementing' because:
- research.md is still in 'draft' status
- No beads task issues have been claimed or completed

Valid next steps:
1. Complete research first (/create_research)
2. Move design to 'ready' status once research is complete
3. Claim a task in beads (`bd update [task-id] --status in_progress`) to begin implementing
```

### Missing Files

If files don't exist:

```
❌ Missing Documentation Files

Expected files in [directory]:
- research.md [✓/✗]
- design.md [✓/✗]
- tasks.md [✓/✗]

Run /create_project first to initialize the documentation structure.
```

### Inconsistent State

If files have conflicting status:

```
⚠️ Inconsistent Status Detected

Current state:
- design.md: implementing
- tasks.md: not-started (0 tasks completed)

This is inconsistent. Suggesting correction:
- Set design.md back to 'ready' OR
- Start checking off tasks in tasks.md

Which would you prefer?
```

## Important Notes

### Read-Only Analysis

- **NEVER modify files** without explicit user confirmation
- **ALWAYS present the update plan** before applying changes
- **VERIFY actual progress** by reading file contents, not just frontmatter

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

- Automatically detect current phase from tasks.md
- Update current_phase based on which phase has active work
- Don't skip phases - must complete in order

## Configuration

The command accepts the directory path as a parameter:

```
/update_status docs/plans/2025-10-07-my-project
```

Or prompts for it if not provided.
