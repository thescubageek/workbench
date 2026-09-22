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
- [../../docs/reference/journal-entries.md](../../docs/reference/journal-entries.md) — where a journal entry goes (newest first, never appended), its heading contract, and when it opens and closes
- [../../docs/reference/remediation-plan.md](../../docs/reference/remediation-plan.md) — what a review round's remediation plan is, how Step 1 recognises one, and the files it has and deliberately lacks

**If a directed read fails, stop — do not continue from memory.** These files live outside your
project, so a read can be refused. Say which file was refused, that reads outside the working
directory are gated, and that the fix is to allow the read once or to relaunch with
`--add-dir <plugin-path>`. Do not route around a refusal with `cat`.

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
6. **Documentation First**: Read research.md and design.md for context before starting — a
   remediation plan has neither, and Step 1 says what to read instead

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

Take the project directory and the phase from the arguments, prompting for either if it is
missing. Then read `research.md`, `design.md` and `tasks.md` from that directory — **fully**, no
`limit` or `offset`.

**A remediation plan has only `tasks.md`, and that is correct.** Read
[../../docs/reference/remediation-plan.md](../../docs/reference/remediation-plan.md) NOW for how to recognise one
and what it deliberately lacks, then take `tasks.md` alone as the whole plan. Do not stop, and do
not route the user to `/wb:create_project` to manufacture two files that exist only to be empty.

Every later step that reaches for research or design context — the REFACTOR step's patterns, Step
4's edge cases, Step 5's testing patterns, Step 6's manual checks — then has nothing to reach for.
On such a plan the task text and its acceptance criterion are the whole specification; do not go
hunting for the absent file.

1. **Read project structure**:
   - Check that specified directory exists
   - Verify presence of research.md, design.md, tasks.md — for a remediation plan, `tasks.md`
     alone satisfies this

2. **Read research.md FULLY** (a remediation plan has none — skip to step 4):
   - Understand what currently exists in the codebase
   - Note patterns and conventions to follow
   - Identify key file:line references

3. **Read design.md FULLY** (likewise absent from a remediation plan):
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

1. **Find the phase**: `current_phase` in frontmatter, or the phase given as `$2`. A remediation
   plan carries neither: its `## Tasks` section is the single phase, and Step 6's checkpoint
   falls at the end of the round.

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
   tells you which. Finish or supersede that work before starting something new. An open entry
   carrying `[blocked]` is neither — it was left open deliberately and its `Next action` names
   what it waits on, so read that before deciding. On a remediation plan the journal to read is
   the **parent plan's** `docs/plans/<plan>/journal.md`; a round directory has none.

**If `tasks.md` has no phases or no tasks**, stop and say so: the plan has not been decomposed
yet, and `/wb:create_tasks` is what writes it. **A remediation plan is exempt from the phase half
of this check, never from the task half**: no task lines is still a stop, and there the fix is to
re-run the review, not `/wb:create_tasks`.

### Step 3: Implement Phase Tasks

#### For Each Implementation Task

**A. Open a journal entry**

Before touching code, add an entry at the **top** of `journal.md` — never appended to the end —
naming the task ID, what you are about to do, and the exact next action, written **at the start**
of the work, not the end, because a session does not get to choose how it ends. Read
[../../docs/reference/journal-entries.md](../../docs/reference/journal-entries.md) NOW and follow it.

The heading shape is a contract — the session-start hook, `forge`, `daily-digest`, `resume_handoff` and `create_handoff` all match on the trailing `(open)` / `(closed)`, and an entry ending any other way is invisible to them. Timestamp from `date -u +"%Y-%m-%d %H:%M"`, never estimated:

```
## YYYY-MM-DD HH:MM — <task-id or short label> (open)
```

**On a remediation plan, the entry goes in the parent plan's `journal.md`** — a round directory
holds no journal of its own. The rule and its reason are stated once, in `journal-entries.md` →
*Which file, when the plan directory is nested*.

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
   durable audit trail. Stage it as **Staging** below describes.
3. **Close the journal entry** with what landed and its commit.
4. **Add implementation notes** to tasks.md if there was a discovery or a deviation:

   ```markdown
   ## Implementation Notes
   - [YYYY-MM-DD] Completed [task-id]: [brief note about discoveries or deviations]
   ```

**Staging.** Stage the files this task changed **by path** — never `git add -A` or `.`, which
sweeps in generated artifacts (`__pycache__/`, `*.pyc`, build output) that are not the task's
work.

**Stage the plan's own files with `git add -f`, every time.** `docs/plans/` is gitignored, so a
plain `git add [plan-dir]/tasks.md` exits 1 with "The following paths are ignored", stages
nothing, and breaks the `&&` chain — the commit never runs, and the checkbox you just flipped
stays in the working tree instead of the log. The `&&` below is what makes that true: separate
the three commands by newlines and a failed stage lets the commit land **without** the plan
files. Git refuses **already-tracked** plan files too, so "this plan was promoted once" is not a
reason to drop the `-f`. The `-f` overrides gitignore; it
never widens the pathspec, so the by-path rule above still holds.

```bash
git add [files this task changed] &&                     # code — by path, no -f
git add -f [plan-dir]/tasks.md [plan-dir]/journal.md &&  # plan files — always -f
git commit -m "[task-id]: ..."
```

**A failed stage hides.** `git status --short` does not list *untracked* ignored files, so an
unpromoted plan directory's `tasks.md` is invisible there and the tree reads clean over a status
edit that was never committed. (A *tracked* plan file that is merely modified does show, so the
blindness is specific to a directory nothing has promoted.) Confirm what the commit actually
contains with `git show --stat HEAD` rather than inferring it from a clean tree.

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

   If the skill cannot be invoked in this session — headless runs deny mid-conversation skill
   calls unless launched with `--allowedTools=Skill` — say so in the report and leave the
   counters as they are. Do not hand-edit them; drift is expected, and the next
   `/wb:update_status` reconciles it.

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
