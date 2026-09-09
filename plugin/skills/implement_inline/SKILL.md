---
name: implement_inline
description: Implement tasks following TDD practices with phase boundaries, inline on the current session model
argument-hint: "[project-directory] [phase-number|continue]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Implement Tasks (inline)

You are tasked with implementing tasks from a structured task list in `tasks.md`, following Test-Driven Development (TDD) practices and the phased implementation approach defined in the project documentation.

This runs **inline, on the current session model**. For the coordinated path — worker agents, main context kept clean — use `/wb:implement`.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- `templates/` — [modified-files-fragment.md](templates/modified-files-fragment.md) (Step 5) · [manual-verification-request.md](templates/manual-verification-request.md) and [phase-completion-report.md](templates/phase-completion-report.md) (Step 6)
- [reference.md](reference.md) — handling mismatches, resume logic, TDD best practices, special considerations, error handling, the DO/DON'T lists, configuration

**If a directed read fails, stop — do not continue from memory.** These files live in the plugin
directory, which is outside your project, so a read of one can be refused. Say which file was
refused, that reads outside the working directory are gated, and that the fix is to allow the
read once or to relaunch with `--add-dir <plugin-path>`. Writing the artifact from this manifest
alone produces a plausible document that was never based on the template — the exact failure the
sentence above exists to prevent. Do not route around a refusal with `cat`.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

**Model & effort (gate check)**: on entry, consult the `model-help` skill (gate mode) for the model + effort this phase warrants; surface its one-line verdict and — only if a switch clears the switch-cost bar — the `/model` action. Baseline is Sonnet/medium (the plan is locked; most tasks are mechanical-to-moderate), bumping genuinely gnarly tasks to Opus/high. Best-effort and non-blocking: stay silent and proceed when the current tier is already right. See CLAUDE.md → "Model & effort at gates."

## Initial Response

When invoked, check for arguments:

1. **If directory and phase provided** (e.g., `/wb:implement_inline docs/plans/2025-01-08-my-project/ 1`):
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
4. **Progress Tracking**: checkbox state in `tasks.md` is the source of truth — flipping a task's checkbox **is** the act of recording it done
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

### Extras and edits

The scope rules above say what not to **add**. They say nothing about what to do with what you
**find**, which is the common case: a worker editing a function notices a real bug in it. That
has a rule too.

- **Edit in place rather than rewriting.** When a targeted edit and a whole-file rewrite reach
  the same end result, make the targeted edit — fewer tokens, same outcome, and a diff a
  reviewer can read.
- **Follow-ups, not fixes.** A pre-existing bug, a performance concern, or any behavior the
  task does not mention is **reported, not fixed** — record it under "issues encountered" and
  move on. The one exception: fix it if the behavior the task asks for cannot work without it.
- **This is about extras only.** Implement every behavior the task asks for, **completely**.
  The rules above bound what you add; none of them licenses delivering less than the task
  specifies. Under-delivery is the failure this clause exists to prevent.

### TDD Implementation Flow

For each implementation task:

```
1. RED Phase (Write Failing Test First)
   - Write test that defines the expected behavior
   - Run test to confirm it fails

2. GREEN Phase (Minimal Implementation)
   - Write just enough code to make test pass
   - No optimization, just make it work
   - Run test to confirm it passes

3. REFACTOR Phase (Improve Without Breaking)
   - Clean up code while tests stay green
   - Run tests after each change
   - Flip the task's checkbox to [x], then commit
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

5. **Read `.claude/wb/knowledge.md` if it exists** — durable repository facts, each with a date
   and a verification hint. Treat entries as dated claims to re-check, not as current truth.
   Absent file, fall through.

**Implement ONLY what's specified**

After reading all documentation, synthesize:

- What patterns should I follow from research?
- What's the goal from the design?
- What EXACT tasks are specified in tasks.md?
- REMEMBER: Do NOT add anything not explicitly listed

### Step 2: Establish Position from tasks.md

There is no external tracker. `tasks.md` is both the plan and the status surface, so
establishing position is a read, not a setup step.

1. **Find the phase**: `current_phase` in frontmatter, or the phase given as `$2`.

2. **Find the next task**: the first `- [ ]` line in that phase's task list. Tasks run in
   document order; a task carrying a `Depends on:` field is the exception, so check that its
   named dependency is already `[x]`.

3. **Check the counters against reality**:

   ```bash
   grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # completed
   grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # remaining
   ```

   **Scope the counts to lines carrying a task ID.** A plan's success criteria and
   prerequisites are checkboxes too; an unscoped count includes them, disagrees with what
   `/wb:update_status` wrote, and reports drift that is not there.

   If the frontmatter counters disagree with these counts, **the checkboxes are right and the
   counters are stale**. Note it and run `/wb:update_status` at the next checkpoint — do not
   hand-edit the counters, and do not let a stale counter change which task you pick.

4. **Read the journal tail**: `journal.md`'s most recent entry. An **open** entry means the
   previous session was interrupted mid-task or simply moved on — an uncommitted working tree
   tells you which. Finish or supersede that work before starting something new.

**If `tasks.md` has no phases or no tasks**, stop and say so: the plan has not been decomposed
yet, and `/wb:create_tasks` is what writes it.

### Step 3: Implement Phase Tasks

#### For Each Implementation Task

**A. Open a journal entry**

Before touching code, append an entry to `journal.md` naming the task ID, what you are about
to do, and the exact next action. This is written **at the start**, not the end: a session
does not get to choose how it ends, and an entry written only on completion is silent in
exactly the cases it exists for.

The heading shape is a contract, because the session-start hook, `forge`, `daily-digest`, `resume_handoff` and `create_handoff` all read it to decide whether work was interrupted:

```
## YYYY-MM-DD HH:MM — <task-id or short label> (open)
```

Ending in a literal `(open)` or `(closed)` is what makes the state detectable. An entry that ends any other way is invisible to every one of those readers, and the failure is silent — a session reads "closed" over interrupted work.

**B. Test First (RED)**

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

**C. Implementation (GREEN)**

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

**D. Refactor (REFACTOR)**

```markdown
♻️ Refactoring: [task description]
```

1. Improve code quality while keeping tests green
2. Consider patterns from research.md
3. Run tests after each change

**E. Record it done**

In this order:

1. **Flip the checkbox.** `- [ ]` → `- [x]`, and append `(completed YYYY-MM-DD HH:MM)`. This
   is the tracking act — not a note about the tracking act. A finished task with an unflipped
   checkbox is indistinguishable from unfinished work to the next session.
2. **Commit.** One task, one commit, with the task ID in the message. The commit log is the
   durable audit trail.
3. **Close the journal entry** with what landed and its commit.
4. **Add implementation notes** to tasks.md if there was a discovery or a deviation:

   ```markdown
   ## Implementation Notes
   - [YYYY-MM-DD] Completed [task-id]: [brief note about discoveries or deviations]
   ```

**Do NOT**:

- ❌ Keep a parallel task list in TaskCreate/TaskUpdate/TodoWrite — it only goes stale beside the checkboxes
- ❌ Hand-edit the frontmatter counters; `/wb:update_status` is their only writer
- ❌ Batch several tasks into one commit, which destroys the per-task audit trail

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

Read [templates/modified-files-fragment.md](templates/modified-files-fragment.md) NOW and update that section in `tasks.md`.

### Step 6: Phase Checkpoint

**⛔ CHECKPOINT: Phase [N] Complete**

Complete these steps IN ORDER before proceeding to next phase:

1. **Verify every Phase [N] checkbox is `[x]`.** Read the phase section and check. This is the
   phase-completion condition — there is nothing else to close. A task left `[ ]` means the
   phase is not done, even if you believe the work happened.

2. **Run automated verification** (the block in Step 5). All checks must pass.

3. **Request manual verification.** Read [templates/manual-verification-request.md](templates/manual-verification-request.md) NOW, emit it, and **wait for the user's confirmation**.

4. **Report completion.** Only after the user confirms: read the
   [templates/phase-completion-report.md](templates/phase-completion-report.md) NOW and emit it.

### Step 7: Reconcile Status

After phase completion and verification:

1. **Run `/wb:update_status`.** It is the only writer of the progress frontmatter fields
   (`status`, `current_phase`, `total_tasks`, `completed_tasks`) — it counts the checkboxes and
   reconciles the counters to them. Do not edit those fields here; two writers and no owner is
   how they rotted before.

2. **Add implementation notes** if there were discoveries:

   ```markdown
   ## Implementation Notes
   - [YYYY-MM-DD] Phase [N] complete: [key learnings, deviations from plan]
   ```

3. **Confirm the phase's work is committed.** Git is the durable record; a phase whose tasks
   are `[x]` but whose work is uncommitted is exactly the state that reads as "interrupted" to
   the next session.

## Important Guidelines

See [reference.md](reference.md) — handling mismatches, resume logic, TDD best practices, special considerations, error handling, the DO/DON'T lists, and configuration.
