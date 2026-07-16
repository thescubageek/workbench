---
description: Resume work from a handoff document created in a previous session
argument-hint: [handoff-file-path]
---

# Resume Handoff

Resumes work from a handoff document, restoring context and continuing implementation where the previous session left off.

## Purpose

**Same machine? Use native `claude --resume` instead** — it restores the full prior session (messages + tool results) more reliably than any document. This command is for **cross-machine / cross-agent / teammate** resumption, where the live session isn't available.

This command:

- Restores full context from handoff document
- Reads all referenced project files
- Understands problems solved and blockers
- Continues work without repeating discoveries
- Maintains consistency with previous decisions

## Initial Response

When invoked, check for arguments:

1. **If handoff path provided** (e.g., `/resume_handoff docs/plans/2025-01-08-auth/handoff-2025-01-08-14-30.md`):
   - Use `$1` as handoff file path
   - Begin resumption process immediately

2. **If no arguments**:

   ```
   I'll resume work from a handoff document. Please provide:
   1. Path to the handoff document (e.g., docs/plans/project/handoff-YYYY-MM-DD-HH-MM.md)

   I'll restore the context and continue where the previous session left off.
   ```

## Process Steps

### Step 1: Read and Validate Handoff

**⛔⛔⛔ BARRIER 1: STOP! Read handoff document COMPLETELY - every section matters ⛔⛔⛔**

```javascript
const handoffPath = $1 || /* prompt for it */;
```

1. **Read handoff document fully** to understand:
   - Current state and progress
   - Critical learnings and discoveries
   - Problems already solved
   - Active blockers
   - Next steps planned

2. **Extract key information**:
   - Project directory path
   - Current phase and task
   - Git commit reference
   - Uncommitted changes status

3. **Pull latest from remote**:

   ```bash
   git pull    # Get latest commits (and beads state if in git mode)
   ```

4. **Sync and check beads state**:

   ```bash
   # Beads mode (see docs/beads-stealth-mode.md). Git mode (default): sync from git.
   # Stealth: handoff is document-based only (no git beads state).
   if [ "$BEADS_MODE" != "stealth" ]; then
     bd sync    # Pull beads database from .beads/ in git
   fi

   # Check beads state regardless of mode
   bd stats                        # Current beads statistics
   bd list --status=in_progress    # Check active work
   bd ready                        # See what's available
   ```

   Compare with handoff's `beads_in_progress`:
   - **Git mode**: Should match if no work done since handoff
   - **Stealth mode**: May differ (beads is local, handoff is document-based)

**think deeply about the context and discoveries documented**

### Step 2: Read Project Documentation

Based on handoff references, read the project files:

```javascript
// Extract project directory from handoff
const projectDir = /* extracted from handoff */;

// Read all project documentation
const researchFile = `${projectDir}/research.md`;
const designFile = `${projectDir}/design.md`;
const tasksFile = `${projectDir}/tasks.md`;
```

1. **Read research.md** to understand:
   - Original codebase state
   - Patterns to follow
   - Integration points

2. **Read design.md** to understand:
   - What we're building
   - Design decisions made
   - Success criteria

3. **Read tasks.md** to understand:
   - Current phase details
   - Specific tasks to complete
   - Success verification steps

### Step 3: Restore Working Context

**Restore beads tracking state:**

```bash
# If handoff shows an in_progress phase, verify it's still claimed
bd show [phase-id-from-handoff]

# If phase was released (no longer in_progress), reclaim it
bd update [phase-id] --status in_progress

# If phase was completed by another session, find next work
bd ready
```

**Review beads issues for next steps:**

The handoff document may reference specific beads issue IDs. Check them:

```bash
# Review next tasks mentioned in handoff
bd show [issue-id-from-handoff]

# See what's ready to work on
bd ready

# Claim the next task
bd update [task-id] --status in_progress
```

**Check for uncommitted changes** mentioned in handoff:

```bash
# Check current git status
git status

# If uncommitted changes exist, understand their purpose from handoff
git diff
```

### Step 4: Apply Learnings from Handoff

Before starting work, internalize the critical learnings:

1. **Patterns and Conventions**:
   - Note any discovered patterns mentioned
   - Remember consistency requirements
   - Apply same approaches used previously

2. **Problems Already Solved**:
   - Don't re-solve issues documented in handoff
   - Use the solutions already found
   - Apply workarounds mentioned

3. **Decisions Made**:
   - Maintain consistency with prior decisions
   - Don't revisit settled trade-offs
   - Follow the chosen approach

4. **Known Gotchas**:
   - Be aware of performance issues found
   - Watch for edge cases discovered
   - Avoid pitfalls documented

### Step 5: Address Active Blockers

If handoff documents active blockers:

1. **Review attempted solutions**:
   - Don't repeat failed attempts
   - Understand why previous approaches failed

2. **Try suggested solutions**:
   - Start with potential solutions from handoff
   - Apply insights from previous attempts

3. **Escalate if still blocked**:
   - Document additional attempts
   - Consider if different expertise needed
   - Create new handoff if switching approach

### ⛔ Model/Effort Gate — advise before continuing

**Before resuming work, pause once and advise on the model + effort for the remaining work.** A resume is the cheapest possible moment to switch: you've *just* reloaded the full context, so the switch tax is already paid — landing on the right tier now avoids a mid-phase reload later.

1. From the handoff and beads state, identify the phase being resumed (`implement` / `validate` / etc.) and how gnarly the remaining tasks are.
2. Consult the `model-help` skill in **gate mode** with that phase + the project docs + the model the handoff recorded (Output Format's "Previous Session … with [model]").
3. Surface its one-line verdict, e.g.:

   ```
   Model gate — implement (resume): recommend Sonnet 5 / medium. Handoff ran on Opus 4.8.
   → Switch down (plan is locked; remaining tasks are mechanical — Opus is overkill for the rest).
   ```

   Or, if the remaining work is the hard part, recommend staying/going up — the floor is inviolable, never advise below what the remaining tasks need.

**Advisory and non-blocking.** State the recommendation and the concrete action (`/model <name>`, set effort); the user decides. Never switch on their behalf. If the current tier is already right, say so in one line and continue.

### Step 6: Continue Implementation

**Resume from exact point indicated in handoff:**

```
Resuming work from handoff dated [YYYY-MM-DD HH:MM]

Current Status:
- Phase: [N] of [Total]
- Last Completed: [task description]
- Now Working On: [next task]

Applying learnings:
- [Key learning 1 from handoff]
- [Key learning 2 from handoff]

Continuing implementation...
```

Follow the "Next Steps" section from handoff:

1. Complete the immediate next task specified
2. Apply recommended approach documented
3. Watch for gotchas mentioned
4. Verify work as indicated

### Step 7: Maintain Continuity

As you work:

1. **Stay consistent** with patterns discovered in handoff
2. **Reference solutions** to problems already solved
3. **Track status in beads** (`bd update [id] --status in_progress`, `bd close [id]`) as you complete work — NEVER markdown checkboxes (tasks.md is documentation only)
4. **Document new discoveries** for potential future handoff
5. **Run verification** commands from handoff

## Validation Steps

After resuming, verify continuity:

1. **Code State Verification**:

   ```bash
   # Run tests to ensure starting state is good
   npm test  # or appropriate test command

   # Check build still works
   npm run build
   ```

2. **Progress Verification**:
   - Confirm phase matches handoff
   - Check task completion matches
   - Verify no work was lost

3. **Context Verification**:
   - Apply a learning from handoff
   - Reference a solved problem
   - Use a discovered pattern

## Output Format

When successfully resumed:

```
✅ Successfully resumed from handoff

Handoff Summary:
- Created: [date/time from handoff]
- Previous Session: [duration] with [model]
- Tasks Completed: [X]/[Y]
- Current Phase: [N] - [name]

Key Context Restored:
- [Critical learning 1]
- [Critical learning 2]
- [Active blocker if any]

Current State:
- Git: [branch] at [commit]
- Uncommitted changes: [YES/NO]
- Tests: [PASSING/FAILING]
- Beads: [N] open, [M] in_progress, [X] closed
- Active phase: [phase-id] or "none"

Ready to continue with:
[Next immediate task from handoff]

Using approach:
[Recommended approach from handoff]

Watching for:
- [Gotcha 1 from handoff]
- [Gotcha 2 from handoff]
```

## Important Guidelines

### Resume Best Practices

1. **Trust the Handoff**: Previous session did the discovery work
2. **Don't Repeat**: Avoid re-solving problems documented
3. **Stay Consistent**: Follow patterns and decisions made
4. **Build on Learnings**: Apply insights discovered
5. **Continue Momentum**: Pick up where left off, don't restart

### When Handoff Conflicts with Code

If handoff says one thing but code shows another:

1. **Trust the code** for current state
2. **Trust the handoff** for learnings and context
3. **Document the discrepancy**
4. **Proceed with caution**
5. **Consider validation** via `/validate_execution`

### Quality Indicators

A successful resume shows:

- Immediate understanding of context
- No repeated discovery work
- Consistent approach with previous session
- Forward progress from exact stopping point
- Application of documented learnings

## Relationship to Other Commands

Common workflows:

**Simple Resume**:

1. **`/resume_handoff`** - Load context
2. `/implement_tasks` - Continue implementation
3. `/validate_execution` - Verify when phase complete

**Complex Resume with Validation**:

1. **`/resume_handoff`** - Load context
2. `/validate_execution` - Check actual state
3. Resolve any discrepancies
4. `/implement_tasks` - Continue work

**Chain of Handoffs**:

1. **`/resume_handoff`** - Session 2 resumes from Session 1
2. Work on implementation
3. `/create_handoff` - Session 2 creates new handoff
4. [New session]
5. **`/resume_handoff`** - Session 3 continues chain

## Error Handling

### Handoff File Not Found

```
❌ Error: Handoff file not found at [path]

Please check:
1. File path is correct
2. You're in the right repository
3. File wasn't moved or deleted

You may need to:
- Search for handoff files: find . -name "handoff-*.md"
- Start fresh with project documentation
```

### Invalid Handoff Format

```
❌ Error: Handoff document missing critical sections

Required sections not found:
- [Missing section]

This may not be a valid handoff document.
Check the file path or create a new handoff.
```

## Configuration

This command restores complete context from handoff documents. It's essential for maintaining continuity across sessions and preventing loss of discovered knowledge.

Best used:

- When resuming incomplete work
- After session timeout or limit
- When switching between models
- For collaborative handoffs between team members

The resume process ensures no context is lost and work continues efficiently without repeating discoveries or solving already-solved problems.
