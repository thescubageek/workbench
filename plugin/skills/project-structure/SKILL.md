---
name: project-structure
description: Enforces project documentation structure in docs/plans/ directories - research.md for facts, design.md for decisions, tasks.md for implementation, thoughts/ for explorations.
user-invocable: false
---

# Project Structure

## Document Separation

**research.md** - Facts only (internal codebase + external research)

- WHAT EXISTS: Current code, external patterns, options, capabilities
- NO decisions, NO rationale, NO implementation steps

**design.md** - Decisions + rationale only

- WHAT to build, WHY chosen
- Architectural decisions, trade-offs, scope
- NO facts without decisions, NO implementation steps

**tasks.md** - Implementation only

- HOW to implement: specific steps, file changes, tests
- NO rationale, NO alternatives

**thoughts/** - Explorations & refinements

- Questions, experiments, discussions
- Understanding refinements before decisions
- Informal notes, brainstorming
- Anything not ready for formal docs

**journal.md** - Session continuity

- Reverse-chronological — **newest entry at the top, never appended to the end**. Entries
  **open when work starts**, close when it ends. See `plugin/docs/reference/journal-entries.md`
- An open entry beside uncommitted changes means an interrupted task

## No external tracker

**Status lives in `tasks.md`.** No external database, no issue tracker, no parallel task list —
and nothing to install before the workflow runs.

- **Checkbox state is the source of truth.** Flipping `- [ ]` → `- [x]` *is* the act of
  recording a task done. A finished task with an unflipped checkbox is indistinguishable from
  unfinished work.
- **Every task line carries a bold local ID matching `[A-Z0-9-]*[0-9][A-Z0-9-]*`** — uppercase,
  hyphens, at least one digit (`P2-T7`, `T14`). This is a contract, not a style: a plan's
  success criteria and prerequisites are checkboxes too, so counters identify task lines by this
  pattern. An ID without a digit makes its task invisible to counting, silently.
- **Frontmatter counters are a derived cache**, with exactly one writer: `/wb:update_status`.
  Never hand-edit them. Drift between checkpoints is expected; `status-sync` surfaces it.
- **Git is the durable record.** One task, one commit, with the task ID in the message — so the
  log is the audit trail a tracker used to hold, and uncommitted work is a reliable signal that
  something did not finish.
- **Planning records live in the document that raises them**: questions in research.md,
  assumptions and pending decisions in design.md, UI questions in a mockup — each with a short
  local ID (`Q1`, `A1`, `PD1`, `UIQ1`) and an explicit state. Resolving one edits its row; rows
  are never deleted.

## Plan persistence: transient by default

Plan directories under `docs/plans/` are **gitignored by default**. Not every branch's plan
deserves to outlive the branch, and deciding at creation time gets it wrong — you only know at
the end.

Promote a plan into git (`git add -f docs/plans/<dir>/`) when **either** trigger fires:

- the work needs to cross a session or a machine — a plan that is not in git cannot travel
- the branch is about to merge — if the work landed, the plan is part of how the code got there

Anything that must survive a branch being **abandoned** belongs in `.claude/wb/knowledge.md`
instead, which is committed. Its qualification rule — an entry only counts if it would change
how the *next* session works — is the definition of durable. **You do not have to keep a plan
to keep what it taught you.**

## Quick Check

- Decision? → design.md
- Fact/Option? → research.md
- Step/Code? → tasks.md
- Exploring/Unsure? → thoughts/
- Status of a task? → its checkbox in tasks.md
- Durable fact about this repo? → .claude/wb/knowledge.md
