# implement_inline — reference

Read this when a step directs you to.

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

When resuming work (phase = "continue"), the plan document tells you where you are — there is
no separate tracker to reload.

1. **Read `tasks.md` FULLY** and establish position from the checkboxes:

   ```bash
   grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # completed
   grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # remaining
   ```

   Scoped to lines carrying a task ID — the criteria checkboxes are not tasks, and counting
   them manufactures drift against the counters.

   The first `[ ]` task in the current phase is the next task. `current_phase` in frontmatter
   says which phase, and a mismatch between the counters and the checkbox counts means the
   counters are stale, not the checkboxes — run `/wb:update_status` and trust the checkboxes.

2. **Read the journal tail.** `journal.md`'s most recent entry tells you what the previous
   session was attempting. An **open** entry beside uncommitted changes means a task was
   interrupted mid-flight; an open entry beside a clean tree means a session simply moved on.
   The working tree is the authority, never the journal.

3. **Review context**:
   - Read tasks.md "Implementation Notes" for discoveries
   - Read research.md and design.md for context
   - Read `.claude/wb/knowledge.md` if it exists

4. **Verify previous work** (optional):

   ```bash
   # Run tests to ensure previous work is solid
   [test command from tasks.md]
   ```

5. **Continue from the next unchecked task**: implement with the TDD cycle, flip its checkbox
   at completion, and trust completed work (`[x]` tasks with commits behind them) unless tests
   fail.

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
1. Read tasks.md; find the first unchecked task in the current phase
2. Read research.md and design.md for context
3. Open a journal entry naming the task and the next action
4. Implement with the TDD cycle (Red → Green → Refactor)
5. Flip the task's checkbox to [x] and append (completed YYYY-MM-DD HH:MM)
6. Commit — one task, one commit
7. Close the journal entry with what landed and its commit
8. Repeat 1-7 for the next unchecked task
9. Run verification at phase boundaries
10. At a phase checkpoint: confirm every phase checkbox is [x], then run /wb:update_status
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
- ✅ Read `tasks.md` to find the next unchecked task
- ✅ Flip a task's checkbox to `[x]` the moment it is done — that flip **is** the tracking act
- ✅ Commit each task separately, so the log is the audit trail
- ✅ Respect phase boundaries and checkpoints
- ✅ Track modified files for easier testing
- ✅ Generate phase-specific test commands
- ✅ Document any deviations in Implementation Notes
- ✅ Run `/wb:update_status` at phase checkpoints to reconcile the counters

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
- ❌ **NEVER** use TaskCreate/TaskUpdate/TodoWrite for tracking — the checkboxes in `tasks.md` are the tracking surface, and a parallel list only goes stale
- ❌ **NEVER** hand-edit the frontmatter counters — `/wb:update_status` is their only writer
- ❌ **NEVER** leave a finished task unchecked; an unflipped checkbox is indistinguishable from unfinished work

## Configuration

This skill implements tasks from the structured task list following TDD practices. Task status lives in `tasks.md`'s checkboxes, phase status is "every checkbox in the phase is `[x]`", and git is the durable record.
