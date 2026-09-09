# design.md Template

Write `design.md` in this shape; every bracketed placeholder must be replaced before the file
is written.

Two tables in it carry local IDs rather than tracker references — there is no external
tracker, so these tables **are** the record. See the rules under each.

````markdown
---
project: [from existing frontmatter]
ticket: [from existing frontmatter]
created: [from existing frontmatter]
status: draft
last_updated: [YYYY-MM-DD]
depends_on: research.md
design_approach: [selected option name]
---

# Design: [Feature/Task Name]

## Problem Statement

[Clear articulation of the problem we're solving and why it matters]

### Success Metrics
- [Measurable outcome 1]
- [Measurable outcome 2]
- [Measurable outcome 3]

## Design Approach

[High-level description of the chosen solution approach]

### Why This Approach
- [Rationale for choosing this over alternatives]
- [How it aligns with existing patterns from research]
- [How it addresses the core problem]
- [Precedents from agent findings]

## Technical Decisions

### Architecture
- [Key architectural decision 1]
  - Rationale: [Why this choice]
  - Trade-off: [What we're giving up]
  - Pattern reference: [file:line from research]

### Data Model
- [Data structure/schema decisions]
- [State management approach]
- [Data flow design]

### Integration Points
- [How this integrates with existing systems]
- [API contracts or interfaces]
- [Dependencies on other components]

## Scope Definition

### In Scope
- [Specific feature/capability 1]
- [Specific feature/capability 2]
- [Specific feature/capability 3]

### Out of Scope
- [What we explicitly won't do]
- [Features deferred to later]
- [Problems we're not solving]

## Success Criteria

### Functional Requirements
- [ ] [User-facing capability 1]
- [ ] [User-facing capability 2]
- [ ] [System behavior 1]

### Non-Functional Requirements
- [ ] Performance: [Specific metric]
- [ ] Reliability: [Specific metric]
- [ ] Security: [Specific requirement]

## Risk Analysis

### Technical Risks
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [Strategy] |

### Assumptions

Assumptions this design rests on, usually from research's knowledge gaps. This table is the
record — there is no external tracker.

| ID | Assumption | Validated? |
| -- | ---------- | ---------- |
| A1 | [gap 1] works as [description] | Pending |
| A2 | [gap 2] can be resolved by [approach] | Pending |

- **IDs are local and stable**: `A1`, `A2`, … in the order raised, never renumbered.
- **State the consequence.** An assumption worth a row is one where being wrong changes the
  design; if being wrong changes nothing, it is background, not an assumption.
- **Validating is an edit, not a new record.** `/wb:resolve_questions` flips the cell to
  `Validated YYYY-MM-DD`, or to `Invalid — [note]` with what the answer forces to change.
  Rows are never deleted.

## Rejected Alternatives

### Option: [Alternative Approach Name]

- **Approach**: [What it would have done]
- **Rejected because**: [Specific reasons]
- **Trade-offs**: [What we would have gained/lost]

## Pending Decisions

Design decisions that need stakeholder input before execution can start. This table is the
record — there is no external tracker.

| ID | Decision Needed | Blocks | State |
| -- | --------------- | ------ | ----- |
| PD1 | [What needs to be decided; options and trade-offs in one line] | [phase or "execution start"] | Open |
| PD2 | [Another decision] | [what can't proceed] | Open |

- **IDs are local and stable**: `PD1`, `PD2`, … in the order raised, never renumbered.
- **Resolution goes in `State`, never in `Blocks`.** `/wb:resolve_questions` sets State to
  `Resolved YYYY-MM-DD → design.md (## Technical Decisions)`. `Blocks` keeps saying what the
  decision blocked — overwriting it destroys the record of why the row mattered, which is the
  half of the audit trail that is hard to reconstruct later.
- **A row needs a real blockee.** If nothing is blocked, it is a preference, not a pending
  decision — decide it here and record it under Technical Decisions.
- **Resolving writes two places.** `/wb:resolve_questions` records the decision with its
  rationale and trade-off under `## Technical Decisions` (in a `### Resolved Decisions`
  subsection if none fits), then sets this row's `Blocks` cell to `— resolved YYYY-MM-DD`.
  The row stays.

Note: Decisions blocking execution should be resolved before `/wb:create_tasks`.

## References

- Research: [research.md](research.md)
- Exploration: [thoughts/[date]-[topic].md](thoughts/) — if `/wb:explore_design` ran
- Related designs: [if any]
- External docs: [if any]

````
