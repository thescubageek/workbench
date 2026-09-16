# create_product_research — output template

Read this when Step 6 directs you to. Write `product-research.md` in this shape. Never
paraphrase the template from memory; every bracketed placeholder must be replaced with real
content from the codebase before the file is written.

````markdown
---
project: [from existing frontmatter or research question]
created: [YYYY-MM-DD]
status: complete
audience: product
last_updated: [YYYY-MM-DD]
validation_status: not-yet-run
---

# Product Research: [Feature/Area Name]

**Created**: [YYYY-MM-DD]
**Last Updated**: [YYYY-MM-DD]
**Audience**: Product Management

## Feature Overview

[2-3 paragraph plain-language description of what this feature/area does. Written so a PM can understand the product capability without reading code.]

## User Flows

### [Flow Name] (e.g., "User Creates an Account")

1. User [action in plain language]
2. System [validates/processes/responds]
3. If [condition], then [outcome A]; otherwise [outcome B]
4. User sees [result]

**Success outcome**: [what the user experiences when everything works]
**Error outcomes**:

- [Error condition]: [what the user sees]
- [Error condition]: [what the user sees]

### [Additional flows...]

## Product Behaviors

### [Behavior Area]

| Trigger | What Happens | Configurable? |
|---------|-------------|---------------|
| [user action or event] | [system behavior in plain language] | [yes — setting name / no] |

### [Additional behavior areas...]

## Data & Integration

### What Data Is Involved

- **User provides**: [input data in business terms]
- **System stores**: [what's persisted and why]
- **User sees**: [output/display data]

### How It Connects to Other Features

- **[Feature/Service]**: [what the integration enables]
- **[External System]**: [what data flows between them]

### Configuration That Affects Behavior

| Setting | What It Controls | Default |
|---------|-----------------|---------|
| [setting name] | [plain-language description] | [value] |

## Engineering Approach

### Coding Patterns

- **[Pattern name]**: [1-sentence description of the convention]
  - Used in: [where this pattern appears]

### Architecture Style

- [High-level observation about how the codebase is organized]
- [Technology choices relevant to product decisions]

### Testing Approach

- [How this feature is tested — unit, integration, e2e]
- [Coverage level observation]

## Technical Appendix

### File References

**[Feature Area 1]**:

- `path/to/main/implementation/` — [what it handles in product terms]
- `path/to/tests/` — [test coverage for this area]

**[Feature Area 2]**:

- `path/to/files/` — [what it handles]

### Key Code (for engineering discussions)

```language
// From path/to/file.ext:NN-MM
// [Brief description of what this code does in product terms]
[actual code snippet]
```

### Validation Notes

[Any UNCERTAIN claims from validation that need human review]

- [Claim]: [What was verified, what needs manual check]

## Open Questions

Questions that must be resolved before the next phase live **here**, in this document, with a
short local ID. This section is the record — there is no external tracker.

| ID | Question | Affects | State |
| -- | -------- | ------- | ----- |
| Q1 | [The question, in product terms] | [What product decision it affects] | Open |
| Q2 | [Another question] | [What it affects] | Open |

Rules for this table:

- **IDs are local and stable.** `Q1`, `Q2`, … numbered in the order raised, never renumbered
  when one is resolved. The ID is the handle another document cites.
- **A question earns a row only if a decision waits on it.** Otherwise it is a finding.
- **Resolving is a two-part act.** `/wb:resolve_questions` sets the State cell to
  `Resolved YYYY-MM-DD → design.md (## Technical Decisions)` and writes the decision, with its
  rationale, into `design.md`. The decision itself is not copied back here: this document
  records what the software does, and a decision is not a fact about the software.
- **Keep resolved rows in place.** The audit trail is the point.

## Next Steps

Based on the research findings:

1. [Suggested next action based on findings]
2. [Another logical next step]
3. Review with engineering team for accuracy
4. Run `/wb:create_design` when ready to make design decisions
````
