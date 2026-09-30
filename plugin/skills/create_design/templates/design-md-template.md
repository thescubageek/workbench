# design.md Template

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Write `design.md` in this shape. Replace every bracketed placeholder before you write the
file.

Two tables in it use local IDs, not tracker references. There is no external tracker, so these
tables **are** the record. Each table has its rules below it.

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

[The problem that this design solves, and why it matters]

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
  - Trade-off: [What this choice gives up]
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
- [What this design does not do]
- [Features deferred to later]
- [Problems that this design does not solve]

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

This table lists the assumptions that the design depends on. They usually come from gaps in
the research. This table is the record, because there is no external tracker.

| ID | Assumption | Validated? |
| -- | ---------- | ---------- |
| A1 | [gap 1] works as [description] | Pending |
| A2 | [gap 2] can be resolved by [approach] | Pending |

- **IDs are local and stable.** Number them `A1`, `A2`, and so on, in the order you raise them.
  Never renumber them.
- **State the consequence.** Give an assumption a row only if a wrong assumption changes the
  design. If it changes nothing, it is background and not an assumption.
- **Validation is an edit, not a new record.** `/wb:resolve_questions` changes the cell to
  `Validated YYYY-MM-DD`. If the answer refutes the assumption, it writes `Invalid — [note]`,
  and the note says what must change. Never delete a row.

## Rejected Alternatives

### Option: [Alternative Approach Name]

- **Approach**: [What it would have done]
- **Rejected because**: [Specific reasons]
- **Trade-offs**: [What it gains and what it loses]

## Pending Decisions

This table lists the design decisions that need stakeholder input before execution starts.
This table is the record, because there is no external tracker.

| ID | Decision Needed | Blocks | State |
| -- | --------------- | ------ | ----- |
| PD1 | [What needs to be decided; options and trade-offs in one line] | [phase or "execution start"] | Open |
| PD2 | [Another decision] | [what cannot proceed] | Open |

- **IDs are local and stable.** Number them `PD1`, `PD2`, and so on, in the order you raise
  them. Never renumber them.
- **Write the resolution in `State`, never in `Blocks`.** `/wb:resolve_questions` sets State to
  `Resolved YYYY-MM-DD → design.md (## Technical Decisions)`. `Blocks` continues to say what the
  decision blocked. If you overwrite it, you lose the reason that the row mattered. That half
  of the audit trail is hard to rebuild later.
- **A row needs something that it blocks.** If it blocks nothing, it is a preference and not a
  pending decision. Decide it here, and record it under Technical Decisions.
- **Resolving writes in two places.** First, `/wb:resolve_questions` records the decision, its
  rationale and its trade-off under `## Technical Decisions`. It uses a
  `### Resolved Decisions` subsection if no other subsection fits. Then it sets this row's
  `State` cell to `Resolved YYYY-MM-DD → design.md (## Technical Decisions)`. The row stays, and
  `Blocks` does not change.

Note: resolve every decision that blocks execution before you run `/wb:create_tasks`.

## References

- Research: [research.md](research.md)
- Exploration: [thoughts/[date]-[topic].md](thoughts/), if `/wb:explore_design` ran
- Related designs: [if any]
- External docs: [if any]

````
