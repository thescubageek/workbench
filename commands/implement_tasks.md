---
description: Implement tasks following TDD practices with phase boundaries
argument-hint: [project-directory] [phase-number|continue]
---

# Implement Tasks

You are tasked with implementing tasks from a structured task list in `tasks.md`, following Test-Driven Development (TDD) practices and the phased implementation approach defined in the project documentation.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If directory and phase provided** (e.g., `/implement_tasks docs/plans/2025-01-08-my-project/ 1`):
   - Use `$1` as project directory
   - Use `$2` as phase number (or "continue" to resume)
   - Read all documentation immediately
   - Begin implementation

2. **If partial arguments**:
   - Use provided arguments
   - Prompt only for missing ones

3. **If no arguments**:

   ```
   I'll help you implement the tasks from your project. Please provide:
   1. Path to the project documentation directory (e.g., docs/plans/2025-01-08-my-project/)
   2. Which phase to implement (number or "continue" to resume from current phase)
   3. Any specific context or constraints for this implementation session (optional)

   I'll follow TDD practices and implement the tasks systematically.
   ```

## Implementation Philosophy

### Core Principles

1. **TDD Cycle**: Red → Green → Refactor for each task
2. **Phase Boundaries**: Complete phases fully before proceeding
3. **ZERO SCOPE CREEP**: Implement EXACTLY what's in tasks.md - NO additions, NO improvements, NO extras
4. **Progress Tracking**: Use beads for ALL status tracking (`bd update`, `bd close`)
5. **Verification Gates**: Respect ⛔ CHECKPOINT markers between phases
6. **Documentation First**: Read research.md and design.md for context before starting

### CRITICAL: NO SCOPE ADDITIONS - NONE

- **NEVER** add features not in tasks.md
- **NEVER** refactor code beyond what's specified
- **NEVER** make "improvements" or "optimizations" not explicitly asked for
- **NEVER** add extra error handling, validation, or edge cases not in the plan
- **NEVER** create abstractions or utilities not specifically tasked
- **ONLY** implement what is EXPLICITLY written in tasks.md
- If you think something is missing, STOP and ask - DO NOT add it yourself

### TDD Implementation Flow

For each implementation task:

```
1. RED Phase (Write Failing Test First)
   - Write test that defines the expected behavior
   - Run test to confirm it fails
   - Tracked in beads as testing task

2. GREEN Phase (Minimal Implementation)
   - Write just enough code to make test pass
   - No optimization, just make it work
   - Run test to confirm it passes
   - Tracked in beads as implementation task

3. REFACTOR Phase (Improve Without Breaking)
   - Clean up code while tests stay green
   - Run tests after each change
   - Close beads issue: `bd close [task-id]`
```

## Process Steps

### Step 1: Read and Understand Context

**⛔⛔⛔ BARRIER 1: STOP! Read ALL documentation files FULLY - NO SHORTCUTS ⛔⛔⛔**

```javascript
const projectDir = $1 || /* prompt for it */;
const phase = $2 || /* prompt for it */;

// Read all project files
const researchFile = `${projectDir}/research.md`;
const designFile = `${projectDir}/design.md`;
const tasksFile = `${projectDir}/tasks.md`;
```

1. **Read project structure**:
   - Check that specified directory exists
   - Verify presence of research.md, design.md, tasks.md

2. **Read research.md FULLY**:
   - Understand what currently exists in the codebase
   - Note patterns and conventions to follow
   - Identify key file:line references

3. **Read design.md FULLY**:
   - Understand the desired end state
   - Review success criteria for the phase
   - Note both automated and manual verification requirements

4. **Read tasks.md FULLY**:
   - Identify current phase from frontmatter
   - Count completed vs remaining tasks
   - Locate the next unchecked task

**think deeply about implementing ONLY what's specified**

After reading all documentation, synthesize:

- What patterns should I follow from research?
- What's the goal from the design?
- What EXACT tasks are specified in tasks.md?
- REMEMBER: Do NOT add anything not explicitly listed

### Step 2: Set Up Task Tracking with Beads

**CRITICAL**: Use beads for ALL task tracking (phases AND granular tasks). Never use TaskCreate/TaskUpdate or markdown checkboxes.

#### Verify Beads is Initialized

First, check that beads is working:

```bash
bd doctor    # Check beads health
```

**If beads is not initialized or has errors**:

```
⚠️ Beads Not Initialized

Beads is required for task tracking in the wb workflow.

To initialize beads for this project:
```bash
cd [project-root]
bd init
```

Then run `/wb:create_execution` to set up beads issues for all tasks.

```

Stop and wait for user to initialize beads before proceeding.

#### Detect Beads Mode

**Beads mode**: `$BEADS_MODE` (set by the SessionStart hook). Git mode (default) — `.beads/` is committed; after `bd sync`, commit it to persist. Stealth mode — local-only; read `docs/beads-stealth-mode.md`. Both modes track tasks identically within a session.

#### Verify Beads Tracking Configuration

Check that tasks.md frontmatter has beads tracking:

```yaml
# tasks.md frontmatter should have:
beads_epic: [epic-id]
beads_phases:
  phase1_milestone: [phase1-milestone-id]
  phase2_milestone: [phase2-milestone-id]
beads_tasks:
  phase1_setup_1: [task-id]
  phase1_setup_2: [task-id]
  phase1_impl_1: [task-id]
  # ... all tasks
```

**If frontmatter is missing beads tracking**: Tell user "Beads tracking not configured. Run `/wb:create_execution` to set up beads issues for all tasks."

#### Find Available Work

Use beads to find what's ready to work on:

```bash
bd ready    # Show all tasks with no blockers (ready to start)
```

This shows:

- Tasks with no dependencies (can start immediately)
- Tasks whose dependencies are all closed (newly unblocked)
- Both granular tasks and phase milestones

#### Claim and Track Tasks

For each task you work on:

```bash
# Review task details before starting
bd show [task-id]    # See description, dependencies, blockers

# Claim the task
bd update [task-id] --status in_progress

# When complete
bd close [task-id] --reason "Brief description of what was done"

# Check what's now unblocked
bd ready
```

**Workflow**:

1. `bd ready` - Find available work
2. `bd show [id]` - Review task details
3. `bd update [id] --status in_progress` - Claim it
4. Implement with TDD (Red → Green → Refactor)
5. `bd close [id]` - Mark complete
6. `bd ready` - Find next task

**Phase Milestone Tracking**:

- Phase milestones are automatically unblocked when all their task dependencies close
- Close the phase milestone only after ALL phase tasks are done AND manual verification passes
- Use `bd show [phase-milestone-id]` to see which tasks still block the milestone

| Tool     | Use Case                                                |
| -------- | ------------------------------------------------------- |
| Beads    | ALL task tracking (granular tasks AND phase milestones) |
| Markdown | Documentation only (what the plan is, not status)       |

### Step 3: Implement Phase Tasks

#### For Each Implementation Task

**A. Test First (RED)**

```markdown
🔴 Writing test for: [task description]
```

1. Create/update test file
2. Write test that captures the requirement
3. Run test to confirm failure (fail-fast — this is the single-test inner loop):

   ```bash
   # Example commands (adapt to project). Fail-fast keeps feedback fast and output small.
   npm test path/to/test.spec.ts -- --bail
   go test ./path/to/package -run TestName -failfast
   pytest -x tests/test_feature.py::test_name
   ```

4. Confirm test fails for the right reason

**B. Implementation (GREEN)**

```markdown
🟢 Implementing: [task description]
```

1. Write minimal code to pass the test
2. Focus on making it work, not perfect
3. Run test to confirm it passes (fail-fast, single test)
4. Run related tests to ensure no regression — wrap green runs to keep context lean:

   ```bash
   # Success -> a checkmark; only failures dump full output. Exit code preserved.
   scripts/quiet <project test command>
   ```

**C. Refactor (REFACTOR)**

```markdown
♻️ Refactoring: [task description]
```

1. Improve code quality while keeping tests green
2. Consider patterns from research.md
3. Run tests after each change
4. Commit when satisfied

**D. Update Progress**

After completing each task:

1. Close the beads issue:

   ```bash
   bd close [task-id] --reason "Implemented [feature], tests passing"
   ```

2. Check what's newly available:

   ```bash
   bd ready    # See what's now unblocked
   ```

3. Optionally add implementation notes to tasks.md:

   ```markdown
   ## Implementation Notes
   - [YYYY-MM-DD] Completed [task-id]: [brief note about discoveries or deviations]
   ```

**Do NOT**:

- ❌ Update checkboxes in tasks.md (documentation only)
- ❌ Use TaskCreate/TaskUpdate (not persisted)
- ❌ Update frontmatter counts manually (beads is source of truth)

### Step 4: Handle Testing Tasks

For dedicated testing tasks:

1. **Unit Tests**:
   - Test individual functions/methods
   - Mock external dependencies
   - Aim for edge cases identified in design.md

2. **Integration Tests**:
   - Test component interactions
   - Use real implementations where possible
   - Verify data flow matches research findings

Follow project testing patterns identified in research.md.

### Step 5: Run Phase Verification

**⛔ BARRIER 2**: Complete ALL tasks in the phase before verification

#### Automated Verification

Run all automated checks from the phase's "Automated Verification" section.
This is the **full-suite** run — do NOT fail-fast here; you want the complete
failure picture. Instead wrap each check in `scripts/quiet` so a green run
collapses to a checkmark and only failures print in full (exit codes preserved):

```bash
# Adapt these to actual commands from tasks.md. scripts/quiet is optional but
# keeps an all-green phase from flooding context.
scripts/quiet make test        # or npm test, go test ./..., pytest
scripts/quiet make lint        # or npm run lint, golangci-lint run
scripts/quiet make typecheck   # or npm run typecheck, go build ./...
scripts/quiet make build       # or npm run build, go build
```

Fix any issues before proceeding.

#### Update Modified Files Section

After implementation, update the "Modified Files" section in tasks.md:

```markdown
### 📝 Modified Files

#### Code Files
- `path/to/file1.ext` - Implemented [feature]
- `path/to/file2.ext` - Added [functionality]

#### Test Files
- `path/to/test1.spec.ts` - Tests for [feature]
- `path/to/test2.test.ts` - Integration tests for [scenario]

**Quick test commands:**
```bash
# Run tests for this phase only (scope which tests run AND quiet the green output)
scripts/quiet npm test path/to/test1.spec.ts path/to/test2.test.ts
```

```

### Step 6: Phase Checkpoint

**⛔ CHECKPOINT: Phase [N] Complete**

Complete these steps IN ORDER before proceeding to next phase:

#### 1. Verify All Phase Tasks Closed

```bash
# Check the phase milestone to see blocking tasks
bd show [phase-milestone-id]

# Verify all tasks for this phase are closed
bd list --status=closed | grep "phase[N]"

# Verify nothing is still in progress
bd list --status=in_progress
```

**Requirement**: All phase task beads issues must be closed.

#### 2. Run Automated Verification

```bash
# Adapt these to actual commands from tasks.md. Full-suite run: no fail-fast;
# wrap in scripts/quiet so green is a checkmark and failures print in full.
scripts/quiet make test        # or npm test, go test ./..., pytest
scripts/quiet make lint        # or npm run lint, golangci-lint run
scripts/quiet make typecheck   # or npm run typecheck, go build ./...
scripts/quiet make build       # or npm run build, go build
```

**Requirement**: All automated checks must pass.

#### 3. Request Manual Verification

Present manual verification checklist to user:

```
✅ Phase [N] Automated Verification Complete

**Automated checks passed:**
- ✅ All tests passing: [test command]
- ✅ Linting clean: [lint command]
- ✅ Build successful: [build command]

**Beads state:**
- ✅ All Phase [N] tasks closed: [list task IDs]

**Manual verification required:**

Please perform the following manual checks from design.md:

1. [Manual verification item 1]
2. [Manual verification item 2]
3. [Manual verification item 3]

Reply when manual verification is complete and I'll close the phase milestone.
```

**Requirement**: Wait for user confirmation before proceeding.

#### 4. Close Phase Milestone

**ONLY after user confirms manual verification**, close the milestone:

```bash
bd close [phase-milestone-id] --reason "Phase [N] complete: [summary]. All tasks closed, automated verification passed, manual verification confirmed."
bd ready  # Check what's now unblocked (next phase milestone tasks)
```

#### 5. Report Completion

```
✅ Phase [N] Complete

**Beads tracking**:
- ✅ Phase [N] milestone closed: [phase-milestone-id]
- 🔓 Unblocked: [next-phase-milestone-id] and its initial tasks

**Progress Summary:**
- Phase [N]: [X] tasks completed
- Next phase: [Y] tasks available (run `bd ready` to see)
- Files modified: [count] code files, [count] test files

Ready to proceed to Phase [N+1].
```

### Step 7: Update Status

After phase completion and verification:

1. **Verify beads state**:

   ```bash
   bd stats    # Check overall progress
   bd list --status=closed    # See what's complete
   bd ready    # See what's available next
   ```

2. **Optionally update tasks.md frontmatter** (for human reference):

   ```yaml
   current_phase: [N+1 if moving forward]
   last_updated: YYYY-MM-DD
   status: in-progress  # or complete if all phases done
   ```

   Note: Frontmatter is for documentation. Beads is the source of truth.

3. **Add implementation notes** if there were discoveries:

   ```markdown
   ## Implementation Notes
   - [YYYY-MM-DD] Phase [N] complete: [key learnings, deviations from plan]
   ```

4. **Sync beads state**:

   ```bash
   bd sync    # Export beads to .beads/issues.jsonl

   # In git mode, commit the beads state
   if [ "$BEADS_MODE" != "stealth" ]; then
     git add .beads/
     git commit -m "Update beads state after Phase [N]"
   fi
   ```

   **Mode behavior**:
   - **Stealth mode**: bd sync exports locally, .beads/ not committed
   - **Git mode**: bd sync + git commit persists to git for cross-machine sync

## Handling Mismatches

When implementation differs from tasks:

```
⚠️ Implementation Variance Detected

**Task states**: [what the task says to do]
**Reality found**: [actual situation in code]
**Impact**: [why this matters]

**Options**:
1. Adapt implementation to match codebase reality
2. Update task to reflect necessary changes
3. Skip task with documentation of why

How should I proceed?
```

Document any deviations in the "Implementation Notes" section of tasks.md.

## Resume Logic

When resuming work (phase = "continue"):

1. **Check beads state** (source of truth):

   ```bash
   # See overall progress
   bd stats

   # Find what's ready to work on
   bd ready

   # Check what's currently in progress
   bd list --status=in_progress

   # Check what's been completed
   bd list --status=closed
   ```

2. **Review context**:
   - Read tasks.md "Implementation Notes" for discoveries
   - Read research.md and design.md for context
   - Check current_phase in frontmatter (for reference)

3. **Verify previous work** (optional):

   ```bash
   # Run tests to ensure previous work is solid
   [test command from tasks.md]
   ```

4. **Continue from next available task**:
   - `bd ready` shows what's available (no blockers)
   - `bd show [task-id]` to review task details
   - `bd update [task-id] --status in_progress` to claim it
   - Implement with TDD cycle
   - `bd close [task-id]` when complete
   - Trust completed work (closed beads issues) unless tests fail

## TDD Best Practices

### Test Quality

- **Test behavior, not implementation**
- **One assertion per test** (when practical)
- **Descriptive test names**: `should_return_error_when_payment_exceeds_limit`
- **Arrange-Act-Assert** pattern
- **Test edge cases** identified in design.md

### When to Skip TDD

Some tasks may not need test-first approach:

- Configuration changes
- Documentation updates
- Refactoring with existing tests
- Build/deployment scripts

For these, update tasks.md appropriately but skip RED phase.

## Special Considerations

### Modified Files Tracking

Maintain the "Modified Files" section in tasks.md to help with:

- Targeted test running (just phase files)
- Code review focus
- Rollback if needed
- Understanding scope of changes

### Quick Test Commands

Generate phase-specific test commands to avoid running entire suite. Two
independent levers, both reduce context cost: scope *which* tests run, and
quiet the output of green runs.

```bash
# Instead of running all tests
npm test

# Run just this phase's tests (scope) and quiet the green output (backpressure)
scripts/quiet npm test src/feature/*.test.ts tests/integration/feature.test.ts
```

### Daily Progress Pattern

```
1. Check beads state: `bd ready` and `bd list --status=in_progress`
2. Read tasks.md for context (what the plan is)
3. Choose next task from `bd ready` output
4. Claim task: `bd update [task-id] --status in_progress`
5. Implement with TDD cycle (Red → Green → Refactor)
6. Close task: `bd close [task-id] --reason "..."`
7. Check what's unblocked: `bd ready`
8. Repeat steps 3-7 for next task
9. Run verification at phase boundaries
10. If phase milestone complete: close it with `bd close [milestone-id]`
11. Add implementation notes to tasks.md if needed
12. `bd sync` to persist state to git remote
```

## Error Handling

### Test Failures During Implementation

If tests fail unexpectedly:

1. Check if codebase changed since design was written
2. Verify test is testing the right thing
3. Check for environment issues
4. Document any fixes needed in Implementation Notes

### Verification Failures

If automated verification fails after implementation:

1. Fix issues before marking phase complete
2. Re-run full verification suite
3. Update test commands if they've changed
4. Document any special setup needed

## Important Guidelines

### DO

- ✅ Follow TDD cycle: Red → Green → Refactor
- ✅ Read ALL documentation files FULLY first
- ✅ Use `bd ready` to find available work
- ✅ Use `bd update [id] --status in_progress` to claim tasks
- ✅ Use `bd close [id]` when tasks complete
- ✅ Respect phase boundaries and checkpoints
- ✅ Track modified files for easier testing
- ✅ Generate phase-specific test commands
- ✅ Document any deviations in Implementation Notes
- ✅ Run `bd sync` at session end to persist state

### DON'T (ABSOLUTELY FORBIDDEN)

- ❌ **NEVER** skip writing tests first (except for noted exceptions)
- ❌ **NEVER** add ANY scope beyond what's in tasks.md - NO EXCEPTIONS
- ❌ **NEVER** move to next phase without verification
- ❌ **NEVER** close manual verification without user confirmation
- ❌ **NEVER** implement multiple phases without checkpoints (unless explicitly instructed)
- ❌ **NEVER** use limit/offset when reading files
- ❌ **NEVER** add "nice to have" features or improvements
- ❌ **NEVER** refactor code that works unless tasks.md says to
- ❌ **NEVER** add error handling not specified in tasks
- ❌ **NEVER** create helper functions not explicitly required
- ❌ **NEVER** use TaskCreate/TaskUpdate/TodoWrite for tracking (use beads)
- ❌ **NEVER** update markdown checkboxes for status (documentation only)
- ❌ **NEVER** treat markdown as source of truth (beads is source of truth)

## Configuration

This command implements tasks from the structured task list following TDD practices. It uses beads for ALL task tracking (both granular tasks and phase milestones) and provides systematic implementation guidance with TDD discipline.
