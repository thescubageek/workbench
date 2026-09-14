---
name: implement
description: Implement a plan's tasks with worker agents, keeping the main context clean. The recommended execution path — spawns one focused worker per task in fresh context, verifies each, and commits it. Use /wb:implement_inline instead to run tasks inline on the current session model.
argument-hint: "[project-directory] [phase-number|continue] [--auto]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Implement Tasks (Coordinated)

**The recommended execution path: coordinator + worker agents.**

You coordinate task implementation from `tasks.md` by spawning worker agents sequentially, each with focused context and a fresh context window. This prevents main session context bloat.

The alternative is `/wb:implement_inline`, which runs the same plan **inline on the current session model** — simpler, but the main context accumulates every task.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- `prompts/` — [worker-prompt.md](prompts/worker-prompt.md) (Step 5) · [verifier-prompt.md](prompts/verifier-prompt.md) and [escalation-worker-prompt.md](prompts/escalation-worker-prompt.md) (Step 6)
- `templates/` — [incomplete-worker-message.md](templates/incomplete-worker-message.md) (Step 6) · [modified-files-fragment.md](templates/modified-files-fragment.md) (Step 7) · [manual-verification-request.md](templates/manual-verification-request.md) and [phase-completion-report.md](templates/phase-completion-report.md) (Step 8)
- [reference.md](reference.md) — evolution, resume logic, why the coordinator pattern exists, migration, the DO/DON'T lists, configuration

**If a directed read fails, stop — do not continue from memory.** These files live in the plugin
directory, which is outside your project, so a read of one can be refused. Say which file was
refused, that reads outside the working directory are gated, and that the fix is to allow the
read once or to relaunch with `--add-dir <plugin-path>`. Writing the artifact from this manifest
alone produces a plausible document that was never based on the template — the exact failure the
sentence above exists to prevent. Do not route around a refusal with `cat`.

## Initial Response

When invoked, check for arguments:

**`--auto` is a flag, not a positional argument. Strip it out before positional binding.**
It may appear anywhere in the invocation, so `/wb:implement --auto <dir> continue` must still
bind the *directory* into the first positional slot — putting the flag there loses the project
directory entirely, and that has happened. Match `--auto` by name, remove it, then treat what
remains as the positional list.

*This paragraph deliberately does not write the positional placeholders literally. The harness
substitutes their **values** into skill text, so a sentence that names them reads back as the
values it was meant to explain — "strip the flag before binding `<the correct directory>`" —
which is circular, and legible only when the binding already worked. Measured 2026-09-13.*

Its only effect is that the Step 8 phase checkpoint does not stop to request manual
verification. Per-task verification, the one-task-one-commit rule, the blocking list and every
barrier before Step 8 are unchanged — `--auto` removes a wait, not a check. What it costs is
recorded rather than hidden; see Step 8.

1. **If directory and phase provided** (e.g., `/wb:implement docs/plans/2025-01-08-my-project/ 1`):
   - Use `$1` as project directory
   - Use `$2` as phase number (or "continue" to resume)
   - Read all documentation immediately
   - Begin coordination

2. **If partial arguments**:
   - Use provided arguments
   - Prompt only for missing ones

3. **If no arguments**:

   ```
   I'll coordinate task implementation using worker agents with fresh context. Please provide:
   1. Path to the project documentation directory (e.g., docs/plans/2025-01-08-my-project/)
   2. Which phase to implement (number or "continue" to resume from current phase)
   3. Any specific context or constraints for this implementation session (optional)

   I'll spawn worker agents sequentially to keep the main session context clean.
   ```

## Implementation Philosophy

### Core Principles

All principles from `implement_inline` PLUS:

1. **Coordination Over Direct Implementation**: Main agent orchestrates, doesn't code
2. **Context Extraction**: Build minimal context packages for workers
3. **Sequential Execution**: Simple, predictable, one task at a time
4. **Worker Isolation**: Each worker operates in fresh context
5. **Model Selection**: right tier per task, by judgment over the task's content (Step 5)
6. **Main Session Stays Clean**: No context accumulation in coordinator

### CRITICAL: NO SCOPE ADDITIONS - NONE

Same zero-tolerance policy as original:

- **NEVER** add features not in tasks.md
- **NEVER** refactor beyond what's specified
- **NEVER** make "improvements" not explicitly asked for
- **NEVER** add extra error handling, validation, or edge cases
- **ONLY** implement what is EXPLICITLY written in tasks.md
- If something seems missing, STOP and ask - DO NOT add it

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

These are the worker's constraints too — they live in `agents/task-worker.md`, and the
coordinated path inherits them from there rather than restating them per spawn.

## Process Steps

### Step 1: Read and Understand Context

**⛔⛔⛔ BARRIER 1: STOP! Read ALL documentation files FULLY - NO SHORTCUTS ⛔⛔⛔**

Take the project directory and the phase from the arguments, prompting for either if it is
missing. Then read `research.md`, `design.md` and `tasks.md` from that directory — **fully**, no
`limit` or `offset`.

1. **Read project structure**:
   - Check that specified directory exists
   - Verify presence of research.md, design.md, tasks.md

2. **Read research.md FULLY**:
   - Understand what currently exists in the codebase
   - Note patterns and conventions to follow
   - Identify key file:line references
   - Extract testing framework, file structure, naming conventions

3. **Read design.md FULLY**:
   - Understand the desired end state
   - Review success criteria for the phase
   - Note automated and manual verification requirements
   - Identify architectural constraints

4. **Read tasks.md FULLY**:
   - Identify current phase from frontmatter
   - Count completed vs remaining tasks from the checkboxes
   - Understand task structure, IDs, and any `Depends on:` fields

5. **Read `.claude/wb/knowledge.md` if it exists** — durable repository facts, each with a date
   and a verification hint. Treat entries as dated claims to re-check, not as current truth.

**Work out:**

- What patterns should workers follow from research?
- What's the goal from the design?
- What EXACT tasks are specified in tasks.md?
- What minimal context does each worker need?

After reading all documentation, prepare to spawn workers sequentially.

### Step 2: Establish Position from tasks.md

There is no external tracker to verify or configure. `tasks.md` is both the plan and the
status surface.

1. **Find the phase**: `current_phase` in frontmatter, or the phase given as `$2`.
2. **Confirm the phase has tasks.** If `tasks.md` has no phases or no task lines, stop and say
   so — the plan has not been decomposed, and `/wb:create_tasks` is what writes it.
3. **Check the counters against the checkboxes.** If they disagree, the checkboxes are right;
   note it and let `/wb:update_status` reconcile at the checkpoint.
4. **Inspect the working tree.**

   ```bash
   git status --short
   ```

   It should be clean before the first spawn. Uncommitted changes mean a previous task was
   never committed — diagnose with Step 6 before spawning anything new.

### Step 3: Extract Context Package

**Build a minimal context package for workers.**

From the documentation you've read, extract ONLY what workers need:

```javascript
const contextPackage = {
  // From design.md — why this phase exists. Renders FIRST in the worker prompt.
  design: {
    why: "one or two sentences: what this phase delivers and who it serves",
    phaseGoal: "what this phase achieves",
    successCriteria: ["criterion 1", "criterion 2"],
    constraints: ["constraint 1", "constraint 2"],
    architecturalApproach: "key decisions"
  },

  // From research.md - patterns workers must follow
  patterns: {
    testingFramework: "jest | pytest | go test | ...",
    testFileLocation: "tests/ | __tests__ | *_test.go | ...",
    fileStructure: "src/ layout | pkg/ layout | ...",
    namingConventions: "camelCase | snake_case | ...",
    importPatterns: "how modules are imported",
    errorHandling: "established patterns"
  },

  // Where the worker flips its checkbox
  tasksFile: `${projectDir}/tasks.md`,

  // Test commands
  testCommands: {
    unit: "npm test | pytest | go test ./...",
    specific: "npm test path/to/file | pytest tests/file.py",
    coverage: "npm test -- --coverage | pytest --cov"
  },

  // File references relevant to this phase
  relevantFiles: [
    "src/feature/file1.ts:123 - existing pattern to follow",
    "tests/feature/test1.spec.ts:45 - test structure example"
  ]
};
```

**Minimize context**: Only include what workers actually need to implement tasks.

### Step 4: Take the Next Task

**⛔ BARRIER 2: One task at a time, in document order**

The next task is the **first `- [ ]` line in the current phase**. Phases run in document order
and tasks run in order within a phase, so the plan's ordering is the schedule.

A task carrying a `Depends on:` field is the exception — check its named dependency is already
`[x]` before taking it. Nothing else encodes dependencies.

### Step 5: Spawn a Worker

**Open a journal entry first.** Append to `journal.md` naming the task ID, what the worker is
about to attempt, and the exact next action. Written at the start, not the end — an abrupt
kill then leaves a correct open entry rather than silence.

The heading shape is a contract, because the session-start hook, `forge`, `daily-digest`, `resume_handoff` and `create_handoff` all read it to decide whether work was interrupted:

```
## YYYY-MM-DD HH:MM — <task-id or short label> (open)
```

Ending in a literal `(open)` or `(closed)` is what makes the state detectable. An entry that ends any other way is invisible to every one of those readers, and the failure is silent — a session reads "closed" over interrupted work.

**Choose the tier.** This is the one statement of the worker tier rule; every other mention in
this skill and its supporting files points here rather than restating it.

| Tier | When | Notes |
| ---- | ---- | ----- |
| `haiku` | Mechanical only — config, docs, renames, version bumps, typos | **Never annotate `effort` on a haiku spawn** |
| `sonnet` | Bounded and fully specified — the task names the exact change and leaves no design latitude | The deliberate downshift, not the default |
| **`opus`** | **Default.** Anything with judgment in it | |
| `fable` | **Never a first spawn.** Only as an explicit election after a *verified* failure | Always `effort: high` — never `xhigh` or `max` |

**These four are the only values the spawn tool accepts.** Its `model` parameter is an enum —
`haiku · sonnet · opus · fable` — so a full identifier like `claude-opus-4-8[1m]` cannot be
pinned per spawn, and `opus` resolves to whatever the current Opus is. Full IDs belong to the
*main-session* model, chosen with `/model`; see the `model-help` skill. Do not write one into a
spawn and assume it took.

Judgment over the task's body, not a keyword match on its title: a regex over titles is a proxy
for difficulty, and you have the task itself. And note what the tier does **not** fix: workers
hit a *tool-call* ceiling, not a context limit, so reaching for a bigger model does not change
truncation behaviour. Step 3's context minimisation and the plan's ~50-call task sizing are what
address that.

**Then spawn.** Read [prompts/worker-prompt.md](prompts/worker-prompt.md) NOW and spawn the `task-worker` agent with it.

**Loop**: Spawn → Wait → Verify → Commit → Next task

### Step 6: After Each Worker Returns

**⛔ BARRIER 3: Verify and commit before the next task**

#### 6a. Did the worker finish?

The worker's final act is flipping its task's checkbox to `[x]`. Workers do not commit, so
everything they touched is still in the working tree — which is what makes the answer
observable:

```bash
git status --short          # what changed
grep -n '\*\*${taskId}\*\*' tasks.md   # is the checkbox [x]?
```

| Checkbox | Working tree | Diagnosis |
| -------- | ------------ | --------- |
| `[x]` | has the task's changes | **Finished** — go to 6b |
| `[ ]` | has substantial, coherent changes | **Truncation** — the worker exhausted its tool-call budget and the finishing tail is missing |
| `[ ]` | empty or barely touched | **Genuine failure** — the work did not happen |

**Truncation and genuine failure are different events with opposite remedies.** Do not treat
them alike, and **never retry the whole task with the same context** — same task plus same
context spends the same budget and truncates at the same point, buying nothing.

- **On truncation**: finish the remaining slice yourself, or re-delegate **only what is left**
  with the completed work described as context. Do not re-run the parts that landed.
- **On genuine failure**: go to 6c.

#### 6b. Verify

Read [prompts/verifier-prompt.md](prompts/verifier-prompt.md) NOW and spawn the `task-verifier` agent with it. Scope is checked against the uncommitted working tree — there is no base ref to supply, because the worker did not commit.

Parse the result:

```javascript
// Agent returns text like: "### Status: PASS" or "### Status: FAIL"
const passed = verificationReport.includes("### Status: PASS");
```

**If PASS**: commit the task — one task, one commit, with the task ID in the message. Close the
journal entry with what landed and the commit hash. Aggregate its modified files and test
commands. Return to Step 4.

**Committing here is what makes an unfinished task detectable.** After a passing task the tree
is clean, so any uncommitted work belongs to something that did not finish.

**If FAIL**: go to 6c.

#### 6c. One escalation, then a human

A verified failure gets **exactly one** escalation attempt:

1. **Reset the checkbox to `[ ]` first.** The worker flips it as its *final* act, before
   anything verifies the work — so a task that reaches 6c is almost always sitting at `[x]`
   while being unverified. Set it back before you do anything else. Skip this and the
   escalation worker starts against an already-`[x]` box, which destroys 6a's only signal for
   distinguishing a truncated escalation attempt from a finished one.
2. Escalate **one rung up Step 5's ladder from the tier that failed** — `haiku` → `sonnet`,
   `sonnet` → `opus`, `opus` → `fable` at `effort: high`. Reaching the `fable` rung is an
   explicit election, never automatic. A task that failed at `opus` has one rung left, so if
   `fable` also fails the answer is the checkpoint's blocking list, not a third model.
3. Say which rung you chose and why, in one line.
4. Read [prompts/escalation-worker-prompt.md](prompts/escalation-worker-prompt.md) NOW and spawn with it.
5. Re-verify.

**If re-verification fails**, stop, and leave the repository in the state the next task needs.
A second automatic attempt is the one that reliably wastes a worker; the checkpoint is where a
human sees it.

**The tree must be clean before the next task starts.** 6a and 6b both read the uncommitted
working tree as belonging to the task just spawned. Leave a blocked task's changes lying in it
and the next worker inherits them: a worker that did nothing looks like *"substantial, coherent
changes"* and gets misdiagnosed as truncation, and its verifier fails it for touching files it
never opened. So pick one, and end clean either way:

| The blocked work is | Do this |
| ------------------- | ------- |
| Worth keeping | Commit it **as work in progress, not as the task** — `WIP ${taskId}: blocked, verification failed — not a completion`. Git is the durable record; the checkpoint names the commit |
| Not worth keeping | `git restore` **the paths the worker reported**, never a blanket `git checkout -- .`, which would also revert earlier committed-but-unstaged work |

Then: checkbox stays `[ ]`, task goes on the phase checkpoint's blocking list with the reason
and the WIP commit hash if there is one, journal entry closes as blocked, and you continue to
the next task.

If the diagnosis is a genuine failure with no usable work at all, read the
[templates/incomplete-worker-message.md](templates/incomplete-worker-message.md) and ask.

### Step 7: Aggregate Results

**⛔ BARRIER 4: All phase tasks complete**

Every task in the phase is `[x]` and committed. Read [templates/modified-files-fragment.md](templates/modified-files-fragment.md) NOW and update that section of `tasks.md` from the aggregated worker outputs.

### Step 8: Phase Checkpoint

**⛔ CHECKPOINT: Phase ${phase} Complete**

1. **Verify every Phase ${phase} checkbox is `[x]`.** That is the phase-completion condition —
   there is nothing else to close. Any task on the blocking list keeps its `[ ]` and is named
   at this checkpoint.

2. **Confirm the tree is clean.** Each task was committed after its verifier passed and each
   blocked task was resolved to a WIP commit or restored (6c), so leftover uncommitted work
   means something did not finish and nobody noticed.

3. **Run automated verification** — and note the ordering: `update_status` runs at **Step 9**,
   after this checkpoint. Do not tick its checkpoint box until it has actually run. Ticking it
   here asserts something not yet done, which is the same error in miniature as ticking the
   human attestation.

   Run the checks:

   ```bash
   # Adapt these to actual commands from tasks.md
   make test           # or npm test, go test ./..., pytest
   make lint           # or npm run lint, golangci-lint run
   make typecheck      # or npm run typecheck, go build ./...
   make build          # or npm run build, go build
   ```

4. **Request manual verification — or record that nobody was asked.**

   **Attended (the default).** Read [templates/manual-verification-request.md](templates/manual-verification-request.md) NOW, emit it, and **wait for the user's confirmation**.

   **Under `--auto`.** Do not wait. Tick the checkpoint conditions you actually established —
   every phase checkbox `[x]`, automated verification passing, `update_status` run — and
   **leave "Manual verification confirmed by human" as `[ ]`**, because no human was asked.
   Then add one line under the checkpoint naming the run unattended, with the phase and the
   time, and listing the manual steps from `design.md` that nobody performed.

   **The unticked box is the feature, not an oversight.** `--auto` buys you the wait; it does
   not buy the attestation, because an attestation is a claim about what a person did. A run
   that ticked that box on its own authority would have every finished plan assert a sign-off
   that never happened — the defect `84da251` removed from the template, reintroduced
   systematically rather than once. Leaving it `[]` is what keeps "unattended" and "approved"
   distinguishable later, when the plan is the only witness.

5. **Report completion.** Attended: only after the user confirms. Under `--auto`: immediately.
   Either way read the [templates/phase-completion-report.md](templates/phase-completion-report.md) NOW and emit it,
   and under `--auto` say in it that the phase closed unattended.

   **On the final phase under `--auto`, say plainly that the plan cannot close itself.** Once
   every task is `[x]`, `tasks.md` wants `status: in-progress → complete` — and that is a
   `status:` change, which `/wb:update_status` gates behind its own barrier. `--auto` is scoped
   to this checkpoint and does not reach another skill's gate. So an unattended run ends with
   the counters reconciled, the work committed, and the plan's own status still `in-progress`,
   waiting on a person. Name that in the report rather than leaving the user to discover a plan
   that looks unfinished; it is the one thing `--auto` deliberately cannot finish.

### Step 9: Reconcile Status

After phase completion:

1. **Run `/wb:update_status`.** It is the only writer of the progress frontmatter fields — it
   counts the checkboxes and reconciles the counters to them. Do not edit `current_phase` or
   `completed_tasks` here.

2. **Add implementation notes** with worker insights:

   ```markdown
   ## Implementation Notes
   - [YYYY-MM-DD] Phase ${phase} complete using coordinated workers:
     - ${workerCount} workers spawned (sequential execution)
     - ${escalationCount} escalations, ${truncationCount} truncations recovered
     - Main context kept clean, no compaction needed
     - Key learnings: ${aggregatedLearnings}
   ```

3. **Consider a handoff rather than a second compaction.** A phase that would need to compact
   twice should hand off instead — `/wb:create_handoff` writes what the next session needs.

## Important Guidelines

See [reference.md](reference.md) — how this evolved from `implement_inline`, resume logic, why the coordinator pattern exists, migration, the DO/DON'T lists, and configuration.
