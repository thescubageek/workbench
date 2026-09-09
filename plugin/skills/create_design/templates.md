# create_design — templates

Read the **section you need**, when its step directs you to — not the whole file. Never
paraphrase a template from memory.

Sections: `design.md Template` (Step 5) · `Recorded-decision confirmation message` (Step 4,
Mode A) · `Design options message` (Step 4, Mode B) · `Design presentation message` (Step 6)

## design.md Template

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

| ID | Decision Needed | Blocks |
| -- | --------------- | ------ |
| PD1 | [What needs to be decided; options and trade-offs in one line] | [phase or "execution start"] |
| PD2 | [Another decision] | [what can't proceed] |

- **IDs are local and stable**: `PD1`, `PD2`, … in the order raised, never renumbered.
- **A row needs a real blockee.** If nothing is blocked, it is a preference, not a pending
  decision — decide it here and record it under Technical Decisions.
- **Resolving writes two places.** `/wb:resolve_questions` records the decision with its
  rationale and trade-off under `## Technical Decisions` (in a `### Resolved Decisions`
  subsection if none fits), then sets this row's `Blocks` cell to `— resolved YYYY-MM-DD`.
  The row stays.

Note: Decisions blocking execution should be resolved before `/create_tasks`.

## References

- Research: [research.md](research.md)
- Exploration: [thoughts/[date]-[topic].md](thoughts/) — if `/wb:explore_design` ran
- Related designs: [if any]
- External docs: [if any]

````

## Recorded-decision confirmation message

Step 4, Mode A — a decision record exists, so it is confirmed rather than re-derived.

```
Research and exploration already converged on a recorded decision:

**Chosen direction**: [name from the decision record]
**Rationale**: [rationale from the record]
**Exploration record**: [thoughts doc path]

I'll formalize this into design.md. Confirm, or tell me if the decision
should be revisited.
```

## Design options message

Step 4, Mode B — no decision record, so options are generated here.

```
Based on the research and verification agents, I see [2-3] possible approaches:

**Option A: [Descriptive Name]**
- Approach: [Brief description]
- Pros: [Benefits]
- Cons: [Drawbacks]
- Risk: [Main risk]
- Precedent: [Similar implementation from agents]

**Option B: [Descriptive Name]**
- Approach: [Brief description]
- Pros: [Benefits]
- Cons: [Drawbacks]
- Risk: [Main risk]
- Precedent: [Similar implementation from agents]

Which approach aligns best with your priorities?
Or should we explore a hybrid approach?
```

## Design presentation message

Step 6 — emitted once, after `design.md` is written.

```
✅ Design document created at: [path]/design.md

Design approach: [selected approach name]

Key decisions made:

- [Major decision 1]
- [Major decision 2]
- [Major decision 3]

Pending decisions: [count]

Agent findings incorporated:

- [Finding 1 from verification agents]
- [Finding 2 from integration analysis]

The design document includes:

- Problem statement and success metrics
- Technical architecture decisions
- Clear scope boundaries
- Risk analysis and mitigation

Please review and provide feedback:

- Are the success criteria appropriate?
- Do the technical decisions align with your vision?
- Are there risks we haven't considered?
- Should any out-of-scope items be included?
```
