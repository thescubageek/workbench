---
name: help
description: Reference for the wb workflow, and in a repository with an active plan, where you are and what's next — each document's status, the phase and task position, open questions and pending decisions, what the next stage needs from you, and what the previous stage left undone against the plan's Intent. Use when the user asks where they are, what's next, what a stage needs, or how wb works. Takes an optional topic.
argument-hint: "[topic]"
allowed-tools: Read, Glob, Grep, Bash
---

# Workbench Help

This document is a reference for both the user AND Claude. When invoked:

1. **Establish state** (the State section) — which case you are in, and the position report if
   there is an active plan
2. **Read the topic** (if provided) — e.g., `/wb:help status` means focus on where status lives
3. **Explain** the relevant stages, workflow, or concepts conversationally
4. **Answer questions** — help the user understand how to use these tools effectively
5. **Guide Claude too** — this reference helps Claude understand the workflow it should follow

You are a helpful guide to this workflow system, not just dumping text.

## State

Run this first, before any topic. It decides which of three cases you are in. Read every file
it names in full, in this session. Do not answer from the session-start summary or from memory.

1. **Find the active plans.** Use the scan the session-start hook uses: each
   `docs/plans/<dir>/tasks.md` whose frontmatter `status:` is not `complete`, newest directory
   name first. No `docs/plans` directory, or no active plan, is **case A**.
2. **Pick the plan**: the one the request or topic names, otherwise the newest active one. Name
   the others in one line.
3. **Read the evidence** for that plan:
   - `README.md` — the `## Intent` section: the Goal, the statements with any `→ PASS`,
     `→ FAIL` or `→ DEFERRED` suffix, the Non-goals and the Amendments. No section is
     **case B**. A section is **case C**. The rules are in
     [../../docs/reference/plan-intent.md](../../docs/reference/plan-intent.md).
   - `research.md`, `design.md`, `tasks.md` — the frontmatter `status:` of each.
   - `research.md` — the `## Intent Coverage` lists, and the `## Open Questions` rows whose
     State is `Open`.
   - `design.md` — the Success Metrics with their `(refines: S<n>)` markers, the
     `**Deferred**:` line, the Assumptions rows still `Pending`, and the Pending Decisions rows
     still `Open`.
   - `tasks.md` — `current_phase`, and the task checkboxes. Count only task lines:
     `^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*` for done and the same with `\[ \]` for open.
     The counters in the frontmatter are a cache, so do not report them as the position.
   - `journal.md` — the first level-2 heading, and whether it ends in `(open)` or `(closed)`.
   - `git status --short` — whether the tree is clean.
4. **Report**, in this order, before any requested topic:

   ```
   📍 Plan: docs/plans/<dir> (others active: <list, or none>)
   Documents: research.md <status>, design.md <status>, tasks.md <status>, phase <n>, <done>/<total> tasks
   Open items: <Q, A and PD IDs, each with its meaning in parentheses, or none>
   Journal: <latest heading>, <open or closed>, tree <clean or N changed files>
   Next stage: /wb:<stage> — needs from you: <that stage's cells from the table below>
   Left undone by the previous stage: <gaps, or none>
   ```

   **The next stage** is the first that applies: `create-research` when research.md is not
   `complete`. `create-design` when design.md is not `approved`. `create-tasks` when tasks.md
   has no task lines. `implement` (phase n) when a task line is open. `validate-execution` when
   every task is done and no statement carries a verdict. Otherwise the plan is finished. Set
   its `status: complete`.

   **The gaps** come only from the evidence: a statement research lists under "No findings
   touch". A statement with no `(refines:)` metric and no Deferred entry. A metric whose
   `(refines:)` names no statement. A statement without a verdict after validation ran. An open
   question, assumption or pending decision. An `(open)` journal entry beside a clean tree.
5. **The three cases**:
   - **Case A, no active plan**: print `No active plan here (no docs/plans, or every plan is
     complete).` Then render the requested topic, or Topics and Command Workflow.
   - **Case B, an active plan without an Intent section**: print the report, with
     `Left undone by the previous stage: not measurable, no Intent section (plan predates 3.2.0)`.
     Report the other gaps as usual. Then render the requested topic.
   - **Case C, an active plan with an Intent section**: the full report, then the requested
     topic.

**Which output a request gets.** "Where am I", "what's next", "what does the next stage need",
or a bare `/wb:help` in a repository with an active plan gets the full report. A question
about what wb or a stage does gets the topic, after one `📍 Plan:` line.

## Topics

```
/wb:help              # Where you are and what's next (with an active plan), else the overview
/wb:help needs        # What each stage needs from you
/wb:help intent       # The plan's Intent: Goal, success statements, verdicts
/wb:help workflow     # Stage sequence and when to use each
/wb:help status       # Where task status lives and who writes it
/wb:help continuity   # Journal, knowledge file, handoffs, compaction
/wb:help mockup       # Mockup iteration workflow
/wb:help review       # Reviewing a change adversarially
/wb:help reference    # The shipped reference docs and what each governs
/wb:help [stage]      # Specific stage (e.g., /wb:help create-design)
```

## Command Workflow

```
/wb:create-project    → Initialize project structure
         ↓
/wb:create-research   → Document what EXISTS (facts only)
         ↓
[/wb:explore-design]  → Optional: air the alternatives before choosing.
         ↓              Only when research found more than one viable approach.
/wb:create-design     → Decide WHAT to build and WHY
         ↓
/wb:create-tasks      → Plan HOW to implement (phased task list)
         ↓
/wb:implement         → Execute with TDD via worker agents (recommended)
   or /wb:implement-inline → the same plan, run inline on this session's model
         ↓
/wb:validate-execution → Verify implementation matches plan
```

**Session Management:**

```
/wb:create-handoff    → Save context for later (or before a second compaction)
/wb:resume-handoff    → Restore context and continue
/wb:update-status     → Reconcile the frontmatter counters against the checkboxes
/wb:resolve-questions → Walk open questions one at a time
```

**UI Mockup Workflow:**

```
/wb:create-mockup     → Research UI patterns + create v001
[iterate with feedback] → Keep/remove/change decisions captured
[mockup-iteration skill] → Creates versioned mockups automatically
finalize              → Compile requirements into design.md
```

## What each stage needs from you

One row per stage. Each stage opens with a one-line summary of its row. "Did enough" names the
evidence the stage leaves behind. The State section reads that evidence.

| Stage | You provide | You decide | You confirm | How you know it did enough |
| ----- | ----------- | ---------- | ----------- | -------------------------- |
| `create-project` | the goal, what success looks like, the non-goals, or prose that carries them. Name, base directory, ticket | — | the Intent as read back to you | README has an Intent: a Goal, two to four statements with IDs, the Non-goals. No file was written before you confirmed |
| `create-research` | the question, or confirmation of the one derived from the Goal. Files to read first | whether to run `explore-design` | — | research.md's Intent Coverage lists every statement once. Findings carry `file:line` references |
| `explore-design` | reactions to each direction as it is drafted | the direction, by explicit approval only | the framing of the decision | a `thoughts/` document whose Decision Record quotes the Goal. A Goal change has an Amendments line |
| `create-design` | the approach, when no decision record exists | the approach, and the success metrics | the recorded decision, when one exists | every statement is refined by a `(refines:)` metric or deferred with a reason. design.md is `approved` |
| `create-tasks` | — | — | that the phases and checkpoints match how you want to review | every task has an ID and a projection. Target State lists the Intent metrics, each checked in a phase |
| `implement` / `implement-inline` | the phase to run | what to do after a verified failure or a plan defect | each phase checkpoint | every task in the phase is `[x]`, verified, and one commit. The checkpoint closed on your go-ahead |
| `validate-execution` | the manual checks only you can run | whether each deviation stands | your reading of each statement's verdict | a report with a verdict per statement. Each README statement ends `→ PASS`, `→ FAIL` or `→ DEFERRED` with a date |
| `update-status` | — | any backward status change, with a reason | the proposed changes | the frontmatter counters match the checkboxes |
| `resolve-questions` | an answer to each question, or "Skip for now" | each answer | — | each resolved row points to its decision in design.md |
| `create-handoff` / `resume-handoff` | the reason for handing off, or the handoff path | — | the resumption summary | the handoff carries decisions, discoveries and next steps. Resume reconciled it against the tree |
| `validate-project` | — | which findings to fix | — | every check is reported, with a fix for each finding |
| `create-mockup` / mockup-iteration | the feature, and keep, remove or change feedback on each version | the open `UIQ` questions | each version | the decision log records each choice |
| `create-product-research` | the product question, or confirmation of the one derived from the Goal | — | — | product-research.md answers in user-visible behavior, with Intent Coverage |
| `forge` | the ticket or plan directory | everything the stages above ask you to decide | the Intent, the design, and each phase transition | the stages above, in order |

## The plan's Intent

`create-project` writes an `## Intent` section in the plan's README: a Goal, two to four "Success
looks like" statements (`S1`, `S2`, …), the Non-goals, and a dated Amendments list. Every later
stage answers to it. Research reports which statements its findings bear on. Design refines each
statement into metrics marked `(refines: S<n>)`, or defers it with a reason. Tasks carry those
metrics into the Target State. Validation writes a verdict back onto each statement. A change to
the Goal or the Non-goals needs your explicit approval and an Amendments line.

Plans created before 3.2.0 have no Intent section, and no stage asks them for one. The rules are
in `docs/reference/plan-intent.md`.

## Where status lives

**There is no external tracker.** Nothing to install, nothing to initialize, nothing that can
be unavailable. The plan documents are the record.

| What | Where | Who writes it |
| ---- | ----- | ------------- |
| Task status | The checkbox on the task line in `tasks.md` | whoever finishes the task — flipping it **is** the act of recording it done |
| Phase status | Every checkbox in the phase is `[x]` | — |
| Progress counters | `tasks.md` frontmatter | **`/wb:update-status` only.** Never hand-edit |
| Durable record | Git — one task, one commit, task ID in the message | the coordinator, after the verifier passes |
| Questions, assumptions, pending decisions | The document that raises them, with local IDs (`Q1`, `A1`, `PD1`, `UIQ1`) | `/wb:resolve-questions` closes them |

Three rules that follow from this:

- **The checkboxes win.** Counters are a derived cache; drift between checkpoints is expected,
  not an error. `status-sync` surfaces it, `/wb:update-status` reconciles it, and the counts are
  always what's right.
- **Every task line carries a bold local ID with at least one digit** (`P2-T7`). That is a
  contract, not a style: every counter identifies task lines by that shape, so an ID without a
  digit makes the task invisible to counting.
- **An unflipped checkbox is indistinguishable from unfinished work.** Flip it when the task is
  done, not later.

## Continuity across sessions

Three artifacts, different lifetimes:

| Artifact | Scope | Lifetime | Read when |
| -------- | ----- | -------- | --------- |
| `journal.md` | one plan | the plan's | at session start (the tail), and on resume |
| `.claude/wb/knowledge.md` | the repository | indefinite, curated | before research, design, or implementation |
| `handoff-*.md` | one transfer | one read | by `/wb:resume-handoff` |

**The journal's entries open when work starts, not when it ends.** A session does not choose
how it ends — a token limit, a closed laptop, a crashed harness run no shutdown step. An entry
written only at completion is silent in exactly those cases, and worse than silent: its tail
would still show the last *finished* phase, so the next session reads a confident, stale record.
Opening on entry makes the default residue of an abrupt kill correct.

**The repository is always the authority.** An open entry beside uncommitted changes means an
interrupted task; an open entry beside a clean tree means a session that simply moved on. The
session-start hook reports both, and never presents the journal as fact when the two disagree.

**On compaction**: the hook prints recovery text saying the summaries above are paraphrase.
A phase that would need a **second** compaction should hand off instead — what degrades first is
exactly what a handoff captures deliberately.

## Command Details

### `/wb:create-project [name] [directory] [ticket]`

Settles the plan's Intent with you first, then creates the project structure: README (with the Intent), research.md, design.md, tasks.md, journal.md.

### `/wb:create-research [directory]`

Spawns parallel agents to document codebase. Facts only, no opinions.

### `/wb:explore-design [directory] [topic]`

Optional. Frames a decision, drafts genuinely different directions, runs the trade-off discussion, and converges only on explicit approval — recording the outcome at the top of a `thoughts/` document. Never writes design.md. Suggested by research only when the findings named more than one viable approach.

### `/wb:create-design [directory]`

Interactive design session. Captures WHAT and WHY, not HOW. Formalizes an `explore-design` record when one exists rather than regenerating options.

### `/wb:create-tasks [directory]`

Transforms design into a phased task list. Each task is a checkbox with a local ID and a projected tool-call cost; anything past ~50 calls splits at a natural seam.

### `/wb:implement [directory] [phase|continue]`

The recommended execution path: one worker agent per task in fresh context, verified, then committed by the coordinator. Keeps the main session's context constant.

### `/wb:implement-inline [directory] [phase|continue]`

The same plan, implemented inline on this session's model. Simpler; the context accumulates.

### `/wb:validate-execution [directory]`

Verifies implementation matches plan. Treats the checkboxes as claims to test against the code, in both directions, and writes a verdict back onto each Intent statement.

### `/wb:update-status [directory]`

Counts the checkboxes and reconciles the frontmatter counters to them. The only writer of those fields.

### `/wb:create-mockup [directory] [feature]`

Researches existing UI patterns, asks clarifying questions, creates versioned mockup. Use mockup-iteration skill to refine.

### `/wb:create-handoff [directory] [reason]`

Captures context for session transfer, reviews the session's knowledge candidates, and adds a journal pointer at the top of `journal.md`. A handoff crossing machines must `git add -f` its plan directory — plan directories are gitignored by default.

### `/wb:resume-handoff [handoff-file]`

Restores context, then **reconciles the handoff against the working tree** — the repository is the authority, the handoff is a report — and names any disagreement.

### `/wb:resolve-questions [directory]`

Walks open questions, assumptions and pending decisions one at a time, recording each answer as a decision with its rationale and marking the source row resolved. Always offers "Skip for now" unless a question is critical.

### `/wb:forge [ticket-or-directory] [stop-at-phase]`

End-to-end sequencer: runs a ticket through research → design → tasks (default stop) → implement → validate, enforcing barriers and confirming before each transition. Re-entrant — detects pipeline state from the documents.

### `/wb:daily-digest [since-date] [project-or-ticket]`

Morning "catch me up + plan my day" orchestrator. Restores active-project context, pulls what changed since yesterday across Jira, wb plans, git/GitHub PRs, Sentry, Notion, Gmail, and Calendar, reconciles the same work item across sources, then produces a prioritized, session-sustainable day plan — with a complexity→(model, effort) tier per task and touch-grass pacing to stay inside the 5-hour window.

### `/wb:model-help [handoff-or-spec]`

Advises which Claude model + reasoning-effort to run a task at (advice only, never implements). Also runs in **gate mode**: the per-phase "model journey" a `forge` should take and whether switching the main model at a gate is worth the context-reload cost.

### `/wb:pr-description [base-branch] [--update]`

Drafts a short PR title and body in WBTE from the branch's commits and diff. It fills the repository's own PR template, or a generic one, scopes each section to what a reviewer needs, and aims for about one screen. It runs `gh pr create` or `gh pr edit` only after you confirm.

### `/wb:wbte-dictionary [path-to-ASD-STE100-Issue-9.pdf]`

Makes a private copy of the ASD-STE100 approved-word dictionary from your own copy of the free Issue 9 PDF. The copy is `~/.claude/wb/wbte-dictionary.tsv`, outside every repository. It is optional. With the copy, the model can look up one word when it is not sure the word is approved in wb Technical English (WBTE). The WBTE rules are in `docs/reference/technical-english.md`, and a short rule card prints at every session start. `WB_TECH_ENGLISH=0` turns the card off.

## Other skills

Not pipeline stages — invoke them directly when you want them.

| Skill | What it does |
| ----- | ------------ |
| `/wb:adversarial-review [<pr#>\|<branch>\|<path>] [--effort=<level>]` | Assumes the change is broken and hunts for how. Sizes its own fan-out from what the diff touches, wraps the built-in `/code-review`, injects domain-expert lenses, and verifies every finding before reporting. Serves any PR, branch or path, and writes a round plan only for the current checkout |
| `/wb:adversarial-loop [<this checkout's pr#>\|<current branch>\|<path in this tree>] [--effort=<level>]` | Drives the current checkout's change to reviewable: review, adjudicate, fix, re-verify until a pass is clean. Serves only the current checkout's PR, and refuses any other target with `/wb:adversarial-review <target>`. If this checkout's pull request exists, it also flips to ready, waits on CI and `claude[bot]`, and replies until resolved |
| `/wb:reply-to-claude [<pr#>]` | Answers a `claude[bot]` review with a comment mapping one-to-one to its findings — what was fixed, what was rejected and why |
| `/wb:review-prep [target]` | Interactive diff walkthrough in tmux and nvim — paced for a human, where `adversarial-review` is a batch hunt |
| `/wb:research-validation [directory]` | Re-checks a research document against the code: do the paths exist, do the snippets match, are the behavioral claims still true |
| `/wb:jira-context <TICKET>` | Loads a ticket's Agents section and the files it points at. Runs standalone, or as `create-research`'s Step 0 |
| `/wb:fetch-issues [repo]` | Triages open GitHub issues into per-issue, session-ready handoffs |
| `/wb:create-product-research [directory]` | Research from a product angle — user-visible behavior and flows rather than implementation |
| `/wb:tracer-bullet` | Fires one cheap probe at the riskiest assumption before fanning out into speculative work |
| `/wb:clip <instruction>` | Runs an instruction and copies the result to the clipboard instead of printing it |
| `/wb:eli5-clip` | Summarizes recent work in plain language for a non-technical reader, and clips it |

Background skills activate on their own and are not invoked: `doc-adherence`,
`project-structure`, `tdd-discipline`, `verification-before-completion`, `status-sync`,
`mockup-iteration`.

## Shipped reference docs

Each is the single authority for one rule. Stages link to them rather than restating, so the rule
changes in one place.

| Doc | Governs |
| --- | ------- |
| `docs/reference/technical-english.md` | How wb writes plans, reports, chat, PRs and commit messages: wb Technical English (WBTE) |
| `docs/reference/plan-intent.md` | The plan's `## Intent` section: its shape, which stage writes what, the `(refines:)` marker, and the verdicts |
| `docs/reference/branch-naming.md` | What the working branch is called, and when to rename it |
| `docs/reference/journal-entries.md` | Where a journal entry goes — newest at the top, never appended — its `(open)`/`(closed)` contract, and when it opens and closes |
| `docs/reference/code-review-integration.md` | What Claude Code's built-in review commands provide, and which parts of that a skill may rely on |
| `docs/reference/review-ledger.md` | The findings ledger a review loop appends to between rounds, and the thrash breaker computed from it |
| `docs/reference/remediation-plan.md` | What a review round's remediation plan is — where it lives, how a consumer recognizes one, what it has and deliberately lacks, and how Step 8's placeholders resolve |

## Core Principles

1. **Document, Don't Judge** — Research describes what IS, not what should change
2. **Explicit Barriers** — Stop at ⛔ BARRIER markers, wait for completion
3. **Zero Scope Creep** — Only implement what's in tasks.md; report what you find rather than fixing it, but implement what the task asks for *completely*
4. **TDD Discipline** — Red → Green → Refactor for each task
5. **Status lives in the plan** — checkboxes are truth, counters are a cache with one writer, git is the durable record
6. **Right-sized model/effort** — Each gate advises a model + effort tier (via `model-help`); switch the main model only when it pays for the context reload, and never below the phase's quality floor

## Quick Troubleshooting

**"The counters don't match the checkboxes"**
Expected between checkpoints. Run `/wb:update-status` — it counts the boxes and reconciles. The checkboxes are right.

**"A task isn't being counted"**
Its ID probably lacks a digit. Task IDs must match `[A-Z0-9-]*[0-9][A-Z0-9-]*` in bold — `**Setup**` is invisible to every counter, `**P2-T7**` is not. `/wb:validate-project` reports these.

**"The session says the wrong plan is active"**
The hook picks the most recently modified `docs/plans/*/tasks.md` whose status is not `complete`. Set the finished plan's `status: complete`.

**"My plan directory vanished on another machine"**
`docs/plans/` is gitignored by default. Promote it with `git add -f docs/plans/<dir>/` before handing off across machines.

**"A previous session left an open journal entry"**
Check the working tree. Uncommitted changes mean a task was interrupted mid-flight — finish or supersede it. A clean tree means the session simply moved on; close the entry and continue.
