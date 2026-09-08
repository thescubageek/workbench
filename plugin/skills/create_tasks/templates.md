# create_tasks — templates

Read the **section you need**, when its step directs you to — not the whole file.

Sections: `tasks.md Template` (Step 4) · `Plan presentation message` (Step 6)

## tasks.md Template

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

```bash
grep -c '^- \[x\]' tasks.md    # completed
grep -c '^- \[ \]' tasks.md    # remaining
```

Every task carries a stable local ID (`P2-T7`). IDs are the handle to cite from a commit
message, a journal entry, or a handoff — checkbox tracking is otherwise positional, and an ID
costs nothing to add now. Number them in document order and never renumber.

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

Before proceeding to Phase 2:

1. ✅ Every Phase 1 checkbox is `[x]`
2. ✅ All automated verification passing
3. ✅ Manual verification confirmed by human
4. ✅ Run `/wb:update_status` to reconcile the frontmatter counters — it is the only writer of
   those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests.**

---

## Phase 2: [Descriptive Name]

### Objective
[Clear goal for phase 2]

### Prerequisites
- [ ] Phase 1 complete and verified
- [ ] Phase 1 manual testing confirmed
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

# Progress
grep -c '^- \[x\]' tasks.md
```

### Design Decisions Reference
Quick lookup of key design decisions:
- [Decision 1]: [Brief reminder]
- [Decision 2]: [Brief reminder]
````

## Plan presentation message

Step 6 — emitted once, after `tasks.md` is written.

```
✅ Execution plan created at: [path]/tasks.md

Implementation structure:
- Phase 1: [Name] - [X] tasks
- Phase 2: [Name] - [Y] tasks
- Phase 3: [Name] - [Z] tasks

Total tasks: [total count]

Agent findings incorporated:
- Dependency order: [key dependency from agent]
- Test coverage: [X] unit tests, [Y] integration tests
- Similar patterns: [reference to pattern agent findings]

Key features of the plan:
- Clear implementation sequence based on dependency analysis
- Specific code changes with before/after context
- Comprehensive test coverage from agent analysis
- Automated and manual verification per phase
- Quick test commands to avoid running full suite
- Every task sized by projected tool calls, split past ~50

Where status lives:
- Checkbox state in tasks.md is the source of truth
- Frontmatter counters are a derived cache; /wb:update_status is their only writer
- Git is the durable record — one task, one commit

Next steps:
1. Review the execution plan in tasks.md
2. Run `/implement_tasks` to begin implementation with TDD
3. Flip checkboxes as work completes; run /wb:update_status at each phase checkpoint
```
