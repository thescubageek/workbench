# create_product_research — output template

Write this output in wb Technical English (WBTE): read [technical-english.md](../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Read this when Step 6 directs you to. Write `product-research.md` in this shape. Do not
paraphrase the template from memory. Replace every bracketed placeholder with real content
from the codebase before you write the file.

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

[A 2-3 paragraph description, in plain language, of what this feature or area does. A PM must understand the product capability without reading code.]

## User Flows

### [Flow Name] (e.g., "User Creates an Account")

1. User [action in plain language]
2. System [validates/processes/responds]
3. If [condition], then [outcome A]. Otherwise, [outcome B]
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
- **System stores**: [what the system keeps, and why]
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

[Each UNCERTAIN claim from the validation that a human must review]

- [Claim]: [What was verified, what needs manual check]

## Open Questions

This table lists the questions to resolve before the next phase. Each question has a short
local ID. This section is the record, because there is no external tracker.

| ID | Question | Affects | State |
| -- | -------- | ------- | ----- |
| Q1 | [The question, in product terms] | [What product decision it affects] | Open |
| Q2 | [Another question] | [What it affects] | Open |

Rules for this table:

- **IDs are local and stable.** Number them `Q1`, `Q2`, and so on, in the order you raise them.
  Do not renumber them when a question is resolved. Other documents cite the ID.
- **A question gets a row only if a decision waits on it.** Otherwise it is a finding.
- **Resolving has two parts.** `/wb:resolve_questions` sets the State cell to
  `Resolved YYYY-MM-DD → design.md (## Technical Decisions)`. It also writes the decision and
  its rationale into `design.md`. Do not copy the decision back here. This document records
  what the software does, and a decision is not a fact about the software.
- **Keep resolved rows in place.** They are the audit trail.

## Next Steps

These steps follow from the findings:

1. [Suggested next action based on findings]
2. [Another logical next step]
3. Ask the engineering team to review the document for accuracy
4. Run `/wb:create_design` when you are ready to make the design decisions
````
