# tasks.md Template

Write `tasks.md` in this shape. Every bracketed placeholder must be replaced with something
specific and executable before the file is written.

````markdown
---
project: [from existing frontmatter]
ticket: [from existing frontmatter]
created: [from existing frontmatter]
status: not-started
last_updated: [YYYY-MM-DD]
current_phase: 1
total_tasks: [calculated count]
completed_tasks: 0
task_tracking: markdown-checkboxes
depends_on: [research.md, design.md]
---

# Execution Plan: [Feature Name]

## Overview

Implementing [brief summary] as specified in design.md

**Design Approach**: [from design.md]
**Target State**: [from design.md success criteria]

## Task tracking

**Checkbox state in this file is the source of truth.** There is no external tracker. Flip
`[ ]` → `[x]` as work completes and append `(completed YYYY-MM-DD HH:MM)`. The frontmatter
counters are a derived cache with exactly one writer — `/wb:update_status` — and are never
hand-edited. Git is the durable record: one task, one commit.

**One caveat about that, worth knowing before you rely on it.** Git is the durable record *of
the code*. Plan directories are gitignored until promoted with `git add -f`, so until you
promote this one, the checkboxes above — the actual source of truth — exist only on this disk
and in no commit. Promote early if the plan matters, and note that promotion is a **one-time**
act over the files that exist at that moment: `journal.md`, `handoff-*.md` and `thoughts/`
appear afterwards and need adding too. `git status` never lists ignored files, so the omission
is invisible unless asked for directly:

```bash
git ls-files --others --ignored --exclude-standard docs/plans/<this-directory>/
```

Every task carries a stable local ID (`P2-T7`). IDs are the handle to cite from a commit
message, a journal entry, or a handoff — checkbox tracking is otherwise positional, and an ID
costs nothing to add now. Number them in document order and never renumber.

**The ID's shape is a contract, not a style preference.** It must match
`[A-Z0-9-]*[0-9][A-Z0-9-]*` — uppercase letters, digits and hyphens, with **at least one
digit** — and be wrapped in `**bold**` as the first thing after the checkbox. `P2-T7`, `T14`
and `PHASE3-4` all qualify; `**Setup**`, `**API**` and `**one**` do not.

That rule exists because a plan's own success criteria and prerequisites are checkboxes too, so
every counter in the workflow identifies task lines by this pattern. An ID that does not match
is not a style problem — it makes the task **invisible to counting**, so `/wb:update_status`
writes wrong totals and the session-start bootstrap reports the wrong position, with nothing
erroring anywhere.

Which is why every count of this file is scoped to lines carrying an ID. A bare
`grep -c '^- \[x\]'` also counts the success criteria and prerequisites below, and will not
agree with the frontmatter counters:

```bash
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # completed
grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # remaining
```

## Implementation Strategy

### Phase Rationale
[Explain why phases are ordered this way - dependencies from agents, risk mitigation, etc.]

Based on dependency analysis:
- [Key dependency finding from agent]
- [Parallel work opportunity from agent]

### Testing Strategy
[Overall approach to testing throughout implementation, incorporating test coverage agent findings]

## Progress Overview

| Phase | Status | Tasks | Progress |
|-------|--------|-------|----------|
| Phase 1: [Name] | ⏸️ Not Started | 0/[N] | 0% |
| Phase 2: [Name] | ⏸️ Not Started | 0/[N] | 0% |

Counts come from the checkboxes below and are reconciled by `/wb:update_status`.

---

## Phase 1: [Descriptive Name]

### Objective
[Single clear goal for this phase]

### Prerequisites
- [ ] Research validated
- [ ] Design approved
- [ ] Development environment ready
- [ ] [Dependencies from agent analysis]

### Changes Required

#### 1. [Component/Module Name]

**File**: `path/to/file.ext`

**Current State** (from research.md):
- [How it works now]
- [Key function at line X]

**Target State** (from design.md):
- [How it should work]
- [New capability needed]

**Implementation**:
```language
// At line [X], replace:
[old code]

// With:
[new code]
```

**Rationale**: [Why this specific implementation]
**Pattern Reference**: [Similar implementation from agent at file:line]

#### 2. [Another Component]

[Similar structure...]

### Tasks

Tasks run in document order. State `Depends on:` **only** where a task depends on something
that is not the task before it — the adjacent task, the previous phase, and the
setup→implementation→testing→integration order are all already carried by the ordering.
Annotate each with its projected tool-call cost; anything past ~50 splits at a natural seam.

#### Setup

- [ ] **P1-T1** — Create new directory structure at `path/to/new/` (~5 calls)
- [ ] **P1-T2** — Install dependencies: `npm install [package]` (~4 calls)
- [ ] **P1-T3** — Set up configuration in `config/feature.json` (~6 calls)

#### Implementation

- [ ] **P1-T4** — Create [Component] class at `src/component.ts`: constructor with dependency
      injection, [method1] for [purpose], [method2] for [purpose] (~20 calls)
- [ ] **P1-T5** — Modify [ExistingComponent] at `src/existing.ts:45`: integrate the new
      component, update error handling (~15 calls)

#### Testing

(Generated from test coverage agent findings)

- [ ] **P1-T6** — Write unit tests for [Component] at `tests/component.test.ts`:
      [scenario 1 from agent], [edge case from agent], [error condition from agent] (~18 calls)
- [ ] **P1-T7** — Write integration tests at `tests/integration/feature.test.ts`:
      [integration scenario from agent] (~15 calls)

#### Integration

- [ ] **P1-T8** — Connect [Component] to [ExistingSystem] (~12 calls)
- [ ] **P1-T9** — Update API endpoint at `api/routes.ts:78` (~8 calls)
- [ ] **P1-T10** — Add database migration for new table (~10 calls)

### Success Criteria

#### Automated Verification
- [ ] Unit tests pass: `npm test src/component.test.ts`
- [ ] Integration tests pass: `npm test:integration`
- [ ] Linting clean: `npm run lint`
- [ ] Type checking passes: `npm run typecheck`
- [ ] Build succeeds: `npm run build`

#### Manual Verification
(From design.md success criteria)
- [ ] [Specific user action] works correctly
- [ ] Performance meets target: [metric]
- [ ] Error messages are clear and helpful
- [ ] No regression in [related feature]

### Modified Files

Track all files changed in this phase:

#### Code Files
- `src/component.ts` - New component implementation
- `src/existing.ts` - Integration point modified
- `config/feature.json` - Configuration added

#### Test Files
- `tests/component.test.ts` - Unit tests for new component
- `tests/integration/feature.test.ts` - Integration tests

**Quick test command for this phase**:
```bash
npm test src/component.test.ts tests/integration/feature.test.ts
```

### ⛔ CHECKPOINT: Phase 1 Complete

These are the conditions to meet before Phase 2 — **not a record of having met them.** Tick
each one as it is actually satisfied.

Each box below is labelled **(derivable)** or **(attestation)**. A derivable condition is one a
tool can establish, and `/wb:implement` ticks those at its Step 8 checkpoint. An attestation
records that a *person* looked, so only a person ticks it, and an unticked attestation beside
finished work means *"done, sign-off pending"* rather than a contradiction.

**Go by the label, never by position.** An earlier version of this block described them by
position — "the first three" — and the description did not match the order, which would have a
reader tick the human sign-off box and leave `update_status` unticked.

- [ ] **(derivable)** Every Phase 1 checkbox is `[x]`
- [ ] **(derivable)** All automated verification passing
- [ ] **(attestation)** Manual verification confirmed by human
- [ ] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

---

## Phase 2: [Descriptive Name]

### Objective
[Clear goal for phase 2]

### Prerequisites

- [ ] Phase 1 complete and verified
- [ ] Phase 1 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*
- [ ] [Additional prerequisites from dependency agent]

[Continue with similar structure...]

---

## Implementation Discoveries

Things to determine during implementation:
- [Technical detail that needs investigation]
- [Configuration that needs testing]
- [Performance tuning needed]

Note: Update this section with findings as you implement.

---

## 📝 Completed Tasks Archive

Move completed tasks here as phases close, to keep the active list readable.

---

## 🚧 Blockers & Notes

### Current Blockers

Recorded here with the task ID they block and the date raised. Remove a blocker when it is
resolved, leaving a dated line saying how.

- [YYYY-MM-DD]: [What is blocked, and which task ID] — [what would unblock it]

### Implementation Notes
- [Important discovery during implementation]
- [Deviation from plan and why]

---

## 🔗 Quick Reference

### Key Files
- **Research**: [research.md](research.md) - Current state documentation
- **Design**: [design.md](design.md) - Target state specification
- **Main Entry**: `[from design]`
- **Config**: `[from design]`

### Common Commands
```bash
# Run all tests
npm test

# Run phase-specific tests
[phase test command]

# Build
npm run build

# Lint
npm run lint

# Progress (scoped to task lines — criteria checkboxes are not tasks)
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md
```

### Design Decisions Reference
Quick lookup of key design decisions:
- [Decision 1]: [Brief reminder]
- [Decision 2]: [Brief reminder]
````
