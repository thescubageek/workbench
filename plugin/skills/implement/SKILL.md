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
- [../../docs/reference/branch-naming.md](../../docs/reference/branch-naming.md) — the branch-name rule Step 2 applies as a backstop, shared with `create_project`, `jira-context` and `forge`
- [../../docs/reference/journal-entries.md](../../docs/reference/journal-entries.md) — where a journal entry goes (newest first, never appended), its heading contract, and when it opens and closes
- [../../docs/reference/remediation-plan.md](../../docs/reference/remediation-plan.md) — what a review round's remediation plan is, how Step 1 recognises one, and the files it has and deliberately lacks

**If a directed read fails, stop — do not continue from memory.** These files live outside your
project, so a read can be refused. Say which file was refused, that reads outside the working
directory are gated, and that the fix is to allow the read once or to relaunch with
`--add-dir <plugin-path>`. Do not route around a refusal with `cat`.

## Initial Response

When invoked, check for arguments:

**`--auto` is a flag, not a positional argument. Strip it out before positional binding.**
It may appear anywhere in the invocation, so `/wb:implement --auto <dir> continue` must still
bind the *directory* into the first positional slot. Match `--auto` by name, remove it, then
treat what remains as the positional list. *(This paragraph names no positional placeholder
literally: the harness substitutes their values, and the sentence goes circular.)*

Its only effect is that the Step 8 phase checkpoint does not stop to request manual
verification. Per-task verification, the one-task-one-commit rule, the blocking list and every
barrier before Step 8 are unchanged — `--auto` removes a wait, not a check. It is phase-scoped:
the run still ends after Step 9, so a multi-phase plan takes one `continue` invocation per phase.

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

**A remediation plan has only `tasks.md`, and that is correct.** Read
[../../docs/reference/remediation-plan.md](../../docs/reference/remediation-plan.md) NOW for how to recognise one
and what it deliberately lacks, then take `tasks.md` alone as the whole plan. Do not stop, and do
not route the user to `/wb:create_project` to manufacture two files that exist only to be empty.

1. **Read project structure**:
   - Check that specified directory exists
   - Verify presence of research.md, design.md, tasks.md — for a remediation plan, `tasks.md`
     alone satisfies this

2. **Read research.md FULLY** (a remediation plan has none — skip to step 4):
   - Understand what currently exists in the codebase
   - Note patterns and conventions to follow
   - Identify key file:line references
   - Extract testing framework, file structure, naming conventions

3. **Read design.md FULLY** (likewise absent from a remediation plan):
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

1. **Find the phase**: `current_phase` in frontmatter, or the phase given as `$2`. A remediation
   plan carries neither: its `## Tasks` section is the single phase, and Step 8's checkpoint falls
   at the end of the round.
2. **Confirm the phase has tasks.** If `tasks.md` has no phases or no task lines, stop and say
   so — the plan has not been decomposed, and `/wb:create_tasks` is what writes it. **A
   remediation plan is exempt from the phase half of this check, never from the task half**: no
   task lines is still a stop, and there the fix is to re-run the review, not `/wb:create_tasks`.
3. **Check the counters against the checkboxes.** If they disagree, the checkboxes are right;
   note it and let `/wb:update_status` reconcile at the checkpoint.
4. **Inspect the working tree.**

   ```bash
   git status --short
   ```

   It should be clean before the first spawn. Uncommitted changes mean a previous task was
   never committed — diagnose with Step 6 before spawning anything new.

5. **Check the branch name — the last backstop before code lands on it.** Every commit this
   stage makes is stamped with the current branch, and after the first push the name is
   expensive to change. Read
   [../../docs/reference/branch-naming.md](../../docs/reference/branch-naming.md) NOW and apply
   it, taking the scope from the plan's `ticket:` frontmatter or from a release version the plan
   targets, and the description from the plan's directory name.

   If an earlier stage already named the branch, this check finds it correct and costs nothing.
   Non-blocking: a declined rename does not hold up the phase.

### Step 3: Extract Context Package

**Build a minimal context package for workers.**

From the documentation you've read, extract ONLY what workers need. For a remediation plan there
is no `design.md` or `research.md` to extract from: each task carries its own `**Fails when:**`
scenario and acceptance criterion, and those *are* the worker's context — pass the task line
verbatim and fill `design`/`patterns` from the reviewed code itself.

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

**A task with no mechanical acceptance criterion is not worker work — divert it here.** An
`adversarial-review` remediation plan emits these deliberately: the acceptance line is labelled
`(attestation)` and names who must look, because the finding is a judgement call with no check
to run. Recognise one by that label, or by an acceptance line saying outright that no mechanical
criterion exists, and do **not** spawn a worker for it. There is nothing to implement, so a
worker under TDD has no failing test to write, and the verifier reads the clean tree it
correctly leaves behind as a FAIL — two workers and an escalation spent to arrive back at an
unfinished task.

Instead: leave the checkbox `[ ]`, add the task to the phase checkpoint's **attestation list**
with its `file:line` and the person or role the task names, and move on to the next task. Step
8.4 is where a human is asked, and a human's answer there is the only thing that may flip that
box.

### Step 5: Spawn a Worker

**Open a journal entry first**, naming the task ID, what the worker is about to attempt, and the
exact next action. Written at the start, not the end — an abrupt kill then leaves a correct open
entry rather than silence. It goes at the **top** of `journal.md`, never appended to the end:
read [../../docs/reference/journal-entries.md](../../docs/reference/journal-entries.md) NOW and
follow it.

The heading shape is a contract — the session-start hook, `forge`, `daily-digest`, `resume_handoff` and `create_handoff` all match on the trailing `(open)` / `(closed)`, and an entry ending any other way is invisible to them. Timestamp from `date -u +"%Y-%m-%d %H:%M"`, never estimated:

```
## YYYY-MM-DD HH:MM — <task-id or short label> (open)
```

**On a remediation plan, the entry goes in the parent plan's `journal.md`** — a round directory
holds no journal of its own. The rule and its reason are stated once, in `journal-entries.md` →
*Which file, when the plan directory is nested*.

**Choose the tier.** This is the one statement of the worker tier rule; every other mention in
this skill and its supporting files points here rather than restating it.

| Tier | When | Notes |
| ---- | ---- | ----- |
| `haiku` | Mechanical only — config, docs, renames, version bumps, typos | **Never annotate `effort` on a haiku spawn** |
| `sonnet` | Bounded and fully specified — the task names the exact change and leaves no design latitude | The deliberate downshift, not the default |
| **`opus`** | **Default.** Anything with judgment in it | |
| `fable` | **Never a first spawn.** Only as an explicit election after a *verified* failure | Always `effort: high` — never `xhigh` or `max` |

**These four are the only values the spawn tool accepts** — its `model` parameter is an enum, so
a full identifier like `claude-opus-4-8[1m]` cannot be pinned per spawn, and `opus` resolves to
the current Opus. Full IDs belong to the *main-session* model (`/model`; see `model-help`).

Judge the task's body, not a keyword match on its title. The tier does **not** fix truncation:
workers hit a *tool-call* ceiling, not a context limit — Step 3's context minimisation and the
plan's ~50-call task sizing are what address that.

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

**If PASS**: commit the task — one task, one commit, with the task ID in the message. Stage the
files the worker reported plus `tasks.md` and `journal.md`, **by path** — never `git add -A` or
`.`. Generated artifacts (`__pycache__/`, `*.pyc`, build output) are not the task's work: leave
them unstaged and name the missing `.gitignore` entry at the checkpoint. Close the journal entry
with what landed and the commit hash. Aggregate its modified files and test commands. Return to
Step 4.

**Stage the plan's own files with `git add -f`, every time.** `docs/plans/` is gitignored, so a
plain `git add <plan-dir>/tasks.md` exits 1 with "The following paths are ignored", stages
nothing, and breaks the `&&` chain — the commit never runs, and one task, one commit fails on the
first passing task of the plan. The `&&` below is what makes that true: separate the three
commands by newlines and a failed stage lets the commit land **without** the plan files. A plain
`git add` exits 1 even on an already-tracked plan file — staging it and failing anyway, which
breaks the `&&` chain just the same — so "this plan was promoted once" is not a reason to drop
the `-f`. The `-f` overrides gitignore; it never widens the pathspec, so the by-path rule above
still holds.

```bash
git add ${workerReportedFiles} &&                        # code — by path, no -f
git add -f ${planDir}/tasks.md ${planDir}/journal.md &&  # plan files — always -f
git commit -m "${taskId}: ..."
```

**A failed stage hides.** `git status --short` does not list *untracked* ignored files, so an
unpromoted plan directory's `tasks.md` is invisible there — 6a's discriminator, 6c's "end clean
either way" and Step 8.2's clean check all read clean over a plan file that was never committed.
(A *tracked* plan file that is merely modified does show, so the blindness is specific to a
directory nothing has promoted.) Confirm what the
commit actually contains (`git show --stat HEAD`) rather than inferring it from a clean tree.

**Committing here is what makes an unfinished task detectable.** After a passing task the tree
is clean, so any uncommitted work belongs to something that did not finish.

A PASS that carries a `### Baseline failures` section still commits, but the failure goes on the
checkpoint's notes and the automated-verification box stays `[ ]` until the suite is actually
green — a substituted bar is reported, never silently adopted.

**If FAIL**: go to 6c.

#### 6c. One escalation, then a human

**A FAIL that names the task as an attestation task is the one failure that is never
escalated.** No rung of the ladder can produce a diff for a judgement call, so a second attempt
buys nothing but another clean tree. Reset the checkbox to `[ ]`, restore anything the worker
touched, and move the task to the checkpoint's attestation list — the diversion Step 4 should
have made, made late.

Any other verified failure gets **exactly one** escalation attempt:

1. **Reset the checkbox to `[ ]` first.** The worker flips it as its *final* act, before
   anything verifies the work, so a task reaching 6c is usually at `[x]` while unverified. An
   escalation started against an `[x]` box leaves 6a no signal to tell truncation from
   completion.
2. Escalate **one rung up Step 5's ladder from the tier that failed** — `haiku` → `sonnet`,
   `sonnet` → `opus`, `opus` → `fable` at `effort: high`. The `fable` rung is an explicit
   election, never automatic; if `fable` also fails, the answer is the checkpoint's blocking
   list, not a third model.
3. Say which rung you chose and why, in one line.
4. Read [prompts/escalation-worker-prompt.md](prompts/escalation-worker-prompt.md) NOW and spawn with it.
5. Re-verify.

**If re-verification fails**, stop, and leave the repository in the state the next task needs.
A second automatic attempt is the one that reliably wastes a worker; the checkpoint is where a
human sees it.

**The tree must be clean before the next task starts.** 6a and 6b read the uncommitted working
tree as the current task's, so a blocked task's leftovers would be misdiagnosed as the next
worker's truncation and fail its verifier. Pick one, and end clean either way:

| The blocked work is | Do this |
| ------------------- | ------- |
| Worth keeping | Commit it **as work in progress, not as the task** — `WIP ${taskId}: blocked, verification failed — not a completion`. Stage the plan's files with `git add -f`, as in 6b. Git is the durable record; the checkpoint names the commit |
| Not worth keeping | `git restore` **the paths the worker reported**, never a blanket `git checkout -- .`, which would also revert earlier committed-but-unstaged work |

Then: checkbox stays `[ ]`, task goes on the phase checkpoint's blocking list with the reason
and the WIP commit hash if there is one, and you continue to the next task. The journal entry
stays **`(open)`**, with its Next action naming the checkpoint it waits on — an open entry beside
a clean tree is the journal's blocked-on-a-human state, and closing it would report the task
finished.

**Edit its heading in place to add `[blocked]`, immediately before the suffix:**

```
## 2026-09-20 14:02 — P1-T2 [blocked] (open)
```

The next task's Step 5 writes its entry above this one, which leaves an `(open)` entry below the
newest — exactly the shape a second-heading close leaves behind. The marker is what tells the
stale-entry check in
[../validate_project/reference/validation-rules.md](../validate_project/reference/validation-rules.md)
that this one is deliberate; without it, validation ERRORs on a state this step created on purpose
and blames the wrong cause. The line still ends in `(open)`, so the suffix contract every reader
depends on is untouched. Remove the marker when the entry finally closes.

If the diagnosis is a genuine failure with no usable work at all, read the
[templates/incomplete-worker-message.md](templates/incomplete-worker-message.md) and ask.

### Step 7: Aggregate Results

**⛔ BARRIER 4: All phase tasks complete, or on a list that says why not — waiting on a task no
worker can close would deadlock the phase**

Every task in the phase is `[x]` and committed, except tasks on the blocking list (6c) and tasks
on the attestation list (Step 4). Those keep their `[ ]` and are named at the checkpoint. Do not
hold the barrier open for an attestation task: nothing before Step 8.4 is permitted to tick it,
so waiting for it to go `[x]` is waiting forever.

Read [templates/modified-files-fragment.md](templates/modified-files-fragment.md) NOW and update that section of `tasks.md` from the aggregated worker outputs.

### Step 8: Phase Checkpoint

**⛔ CHECKPOINT: ${phaseLabel} Complete**

`${phaseLabel}` is `Phase <n>` on a phased plan and `Round <N>`, from the round's directory name,
on a remediation plan — which carries no numbered phase (Step 2). Substitute it here, in both
Step 8 templates, in Step 7's `modified-files-fragment.md`, and in Step 9's Implementation Notes.
A checkpoint headed `Phase undefined` reads as a run that lost its place.

1. **Verify every ${phaseLabel} checkbox is `[x]`, apart from the two lists that account for a
   `[ ]`.** That is the phase-completion condition — there is nothing else to close. A task on
   the blocking list (6c) or the attestation list (Step 4) keeps its `[ ]` and is named here
   with its reason; every other task must be `[x]`.

2. **Confirm the tree is clean.** Every task was committed after its verifier passed or resolved
   under 6c, so leftover uncommitted work means something did not finish. `git status --short`
   cannot tell you this alone: `docs/plans/` is gitignored, so an uncommitted plan file never
   appears there and a phase that lost its `tasks.md` reads clean. Check both.

   ```bash
   git status --short
   git ls-files --others --ignored --exclude-standard docs/plans/<this-plan>/
   ```

3. **Run automated verification.** `update_status` runs at **Step 9**, after this checkpoint —
   do not tick its checkpoint box until it has actually run.

   ```bash
   # Adapt these to actual commands from tasks.md
   make test           # or npm test, go test ./..., pytest
   make lint           # or npm run lint, golangci-lint run
   make typecheck      # or npm run typecheck, go build ./...
   make build          # or npm run build, go build
   ```

4. **Request manual verification — or record that nobody was asked.**

   **Attended (the default).** Read [templates/manual-verification-request.md](templates/manual-verification-request.md) NOW, emit it, and **wait for the user's confirmation**.

   **Put the attestation list in that same request, one line each** — the task's `file:line`,
   the judgement being asked for, and who the task names. This is the authority those tasks were
   diverted here to wait for: on a clear yes, flip the task's checkbox to `[x]`, record in one
   line who attested and when, and commit it as you would any other task. On anything else it
   stays `[ ]` and moves to the blocking list with what the human said.

   **Under `--auto`.** Do not wait. Tick the checkpoint conditions you actually established —
   every phase checkbox `[x]`, automated verification passing, and the `update_status` box once
   Step 9 has run it — and **leave "Manual verification confirmed by human" as `[ ]`**, because
   no human was asked. Then add one line under the checkpoint naming the run unattended, with
   `${phaseLabel}`, the time, and the manual steps nobody performed — from `design.md` on a
   phased plan, and on a remediation plan from the outstanding tasks' own acceptance criteria in
   the round's `tasks.md`, which is where a round's manual steps live because it has no
   `design.md` (Step 3).
   **Attestation tasks stay `[ ]`** and are listed there too — the phase still closes,
   unattended, so the run terminates instead of stalling, and the report tells a person exactly
   which judgements are outstanding.

   **The unticked box is the feature, not an oversight.** `--auto` buys the wait, not the
   attestation: that box records what a person did, and no run may tick it on its own authority.
   An attestation task's checkbox is that same box under another name, and the same rule holds
   for it.

5. **Report completion.** Attended: only after the user confirms. Under `--auto`: immediately.
   Either way read the [templates/phase-completion-report.md](templates/phase-completion-report.md) NOW and emit it,
   and under `--auto` say in it that the phase closed unattended.

   **On the final phase under `--auto`, say plainly that the plan cannot close itself.**
   `status: in-progress → complete` is a `status:` change gated by `/wb:update_status`'s own
   barrier, which `--auto` does not reach — so the run ends with the work committed, the
   counters reconciled, and the plan still `in-progress`, waiting on a person. Name that in the
   report.

### Step 9: Reconcile Status

After phase completion:

1. **Run `/wb:update_status`.** It is the only writer of the progress frontmatter fields — it
   counts the checkboxes and reconciles the counters to them. Do not edit `current_phase` or
   `completed_tasks` here.

   If the skill cannot be invoked in this session — headless runs deny mid-conversation skill
   calls unless launched with `--allowedTools=Skill` — say so in the report and leave the
   counters as they are. Do not hand-edit them; drift is expected, and the next
   `/wb:update_status` reconciles it.

2. **Add implementation notes** with worker insights:

   ```markdown
   ## Implementation Notes
   - [YYYY-MM-DD] ${phaseLabel} complete using coordinated workers:
     - ${workerCount} workers spawned (sequential execution)
     - ${escalationCount} escalations, ${truncationCount} truncations recovered
     - Main context kept clean, no compaction needed
     - Key learnings: ${aggregatedLearnings}
   ```

3. **Consider a handoff rather than a second compaction.** A phase that would need to compact
   twice should hand off instead — `/wb:create_handoff` writes what the next session needs.

## Important Guidelines

See [reference.md](reference.md) — how this evolved from `implement_inline`, resume logic, why the coordinator pattern exists, migration, the DO/DON'T lists, and configuration.
