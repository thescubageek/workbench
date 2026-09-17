---
name: help
description: Quick reference for wb workflow stages, where status lives, and continuity across sessions
argument-hint: "[topic]"
allowed-tools: Read
---

# Workbench Help

This document is a reference for both the user AND Claude. When invoked:

1. **Read the topic** (if provided) — e.g., `/wb:help status` means focus on where status lives
2. **Explain** the relevant stages, workflow, or concepts conversationally
3. **Answer questions** — help the user understand how to use these tools effectively
4. **Guide Claude too** — this reference helps Claude understand the workflow it should follow

You are a helpful guide to this workflow system, not just dumping text.

## Topics

```
/wb:help              # Overview of everything
/wb:help workflow     # Stage sequence and when to use each
/wb:help status       # Where task status lives and who writes it
/wb:help continuity   # Journal, knowledge file, handoffs, compaction
/wb:help mockup       # Mockup iteration workflow
/wb:help [stage]      # Specific stage (e.g., /wb:help create_design)
```

## Command Workflow

```
/wb:create_project    → Initialize project structure
         ↓
/wb:create_research   → Document what EXISTS (facts only)
         ↓
[/wb:explore_design]  → Optional: air the alternatives before choosing.
         ↓              Only when research found more than one viable approach.
/wb:create_design     → Decide WHAT to build and WHY
         ↓
/wb:create_tasks      → Plan HOW to implement (phased task list)
         ↓
/wb:implement         → Execute with TDD via worker agents (recommended)
   or /wb:implement_inline → the same plan, run inline on this session's model
         ↓
/wb:validate_execution → Verify implementation matches plan
```

**Session Management:**

```
/wb:create_handoff    → Save context for later (or before a second compaction)
/wb:resume_handoff    → Restore context and continue
/wb:update_status     → Reconcile the frontmatter counters against the checkboxes
/wb:resolve_questions → Walk open questions one at a time
```

**UI Mockup Workflow:**

```
/wb:create_mockup     → Research UI patterns + create v001
[iterate with feedback] → Keep/remove/change decisions captured
[mockup-iteration skill] → Creates versioned mockups automatically
finalize              → Compile requirements into design.md
```

## Where status lives

**There is no external tracker.** Nothing to install, nothing to initialize, nothing that can
be unavailable. The plan documents are the record.

| What | Where | Who writes it |
| ---- | ----- | ------------- |
| Task status | The checkbox on the task line in `tasks.md` | whoever finishes the task — flipping it **is** the act of recording it done |
| Phase status | Every checkbox in the phase is `[x]` | — |
| Progress counters | `tasks.md` frontmatter | **`/wb:update_status` only.** Never hand-edit |
| Durable record | Git — one task, one commit, task ID in the message | the coordinator, after the verifier passes |
| Questions, assumptions, pending decisions | The document that raises them, with local IDs (`Q1`, `A1`, `PD1`, `UIQ1`) | `/wb:resolve_questions` closes them |

Three rules that follow from this:

- **The checkboxes win.** Counters are a derived cache; drift between checkpoints is expected,
  not an error. `status-sync` surfaces it, `/wb:update_status` reconciles it, and the counts are
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
| `handoff-*.md` | one transfer | one read | by `/wb:resume_handoff` |

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

### `/wb:create_project [name] [directory] [ticket]`

Creates project structure: README, research.md, design.md, tasks.md, journal.md.

### `/wb:create_research [directory]`

Spawns parallel agents to document codebase. Facts only, no opinions.

### `/wb:explore_design [directory] [topic]`

Optional. Frames a decision, drafts genuinely different directions, runs the trade-off discussion, and converges only on explicit approval — recording the outcome at the top of a `thoughts/` document. Never writes design.md. Suggested by research only when the findings named more than one viable approach.

### `/wb:create_design [directory]`

Interactive design session. Captures WHAT and WHY, not HOW. Formalizes an `explore_design` record when one exists rather than regenerating options.

### `/wb:create_tasks [directory]`

Transforms design into a phased task list. Each task is a checkbox with a local ID and a projected tool-call cost; anything past ~50 calls splits at a natural seam.

### `/wb:implement [directory] [phase|continue]`

The recommended execution path: one worker agent per task in fresh context, verified, then committed by the coordinator. Keeps the main session's context constant.

### `/wb:implement_inline [directory] [phase|continue]`

The same plan, implemented inline on this session's model. Simpler; the context accumulates.

### `/wb:validate_execution [directory]`

Verifies implementation matches plan. Treats the checkboxes as claims to test against the code, in both directions.

### `/wb:update_status [directory]`

Counts the checkboxes and reconciles the frontmatter counters to them. The only writer of those fields.

### `/wb:create_mockup [directory] [feature]`

Researches existing UI patterns, asks clarifying questions, creates versioned mockup. Use mockup-iteration skill to refine.

### `/wb:create_handoff [directory] [reason]`

Captures context for session transfer, reviews the session's knowledge candidates, and adds a journal pointer at the top of `journal.md`. A handoff crossing machines must `git add -f` its plan directory — plan directories are gitignored by default.

### `/wb:resume_handoff [handoff-file]`

Restores context, then **reconciles the handoff against the working tree** — the repository is the authority, the handoff is a report — and names any disagreement.

### `/wb:resolve_questions [directory]`

Walks open questions, assumptions and pending decisions one at a time, recording each answer as a decision with its rationale and marking the source row resolved. Always offers "Skip for now" unless a question is critical.

### `/wb:forge [ticket-or-directory] [stop-at-phase]`

End-to-end sequencer: runs a ticket through research → design → tasks (default stop) → implement → validate, enforcing barriers and confirming before each transition. Re-entrant — detects pipeline state from the documents.

### `/wb:daily-digest [since-date] [project-or-ticket]`

Morning "catch me up + plan my day" orchestrator. Restores active-project context, pulls what changed since yesterday across Jira, wb plans, git/GitHub PRs, Sentry, Notion, Gmail, and Calendar, reconciles the same work item across sources, then produces a prioritized, session-sustainable day plan — with a complexity→(model, effort) tier per task and touch-grass pacing to stay inside the 5-hour window.

### `/wb:model-help [handoff-or-spec]`

Advises which Claude model + reasoning-effort to run a task at (advice only, never implements). Also runs in **gate mode**: the per-phase "model journey" a `forge` should take and whether switching the main model at a gate is worth the context-reload cost.

## Core Principles

1. **Document, Don't Judge** — Research describes what IS, not what should change
2. **Explicit Barriers** — Stop at ⛔ BARRIER markers, wait for completion
3. **Zero Scope Creep** — Only implement what's in tasks.md; report what you find rather than fixing it, but implement what the task asks for *completely*
4. **TDD Discipline** — Red → Green → Refactor for each task
5. **Status lives in the plan** — checkboxes are truth, counters are a cache with one writer, git is the durable record
6. **Right-sized model/effort** — Each gate advises a model + effort tier (via `model-help`); switch the main model only when it pays for the context reload, and never below the phase's quality floor

## Quick Troubleshooting

**"The counters don't match the checkboxes"**
Expected between checkpoints. Run `/wb:update_status` — it counts the boxes and reconciles. The checkboxes are right.

**"A task isn't being counted"**
Its ID probably lacks a digit. Task IDs must match `[A-Z0-9-]*[0-9][A-Z0-9-]*` in bold — `**Setup**` is invisible to every counter, `**P2-T7**` is not. `/wb:validate_project` reports these.

**"The session says the wrong plan is active"**
The hook picks the most recently modified `docs/plans/*/tasks.md` whose status is not `complete`. Set the finished plan's `status: complete`.

**"My plan directory vanished on another machine"**
`docs/plans/` is gitignored by default. Promote it with `git add -f docs/plans/<dir>/` before handing off across machines.

**"A previous session left an open journal entry"**
Check the working tree. Uncommitted changes mean a task was interrupted mid-flight — finish or supersede it. A clean tree means the session simply moved on; close the entry and continue.
