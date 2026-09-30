# create_research — output template

Write this output in wb Technical English (WBTE): read [technical-english.md](../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Read this when Step 6 directs you to. Write `research.md` in this shape. Do not paraphrase the
template from memory. Replace every bracketed placeholder with real content from the codebase
before you write the file.

````markdown
---
project: [from existing frontmatter]
ticket: [from existing frontmatter]
created: [from existing frontmatter]
status: complete
last_updated: [YYYY-MM-DD]
---

# Research: [Project Name]

**Created**: [original date]
**Last Updated**: [YYYY-MM-DD]
**Ticket**: [ticket-reference or N/A]

## Research Question

[Original user query]

## Summary

[High-level documentation of what was found, answering the user's question by describing what exists - 2-3 paragraphs]

## Detailed Findings

### [Component/Area 1]

**Location**: `path/to/component/`

**What exists**:
- Description of current implementation ([`file.ext:123`](link))
- How it connects to other components
- Current implementation details (without evaluation)

**Key code**:
```language
// Actual code snippet from file.ext:123-145
// Showing how it currently works
```

**How it works**:

1. [Step-by-step explanation of current flow]
2. [With specific file:line references]
3. [Describing actual behavior]

### [Component/Area 2]

[Continue pattern...]

## Architecture Documentation

**Current patterns found**:

- Pattern 1: [Description of pattern and where used]
  - Example: `src/auth/validator.ts:45-67`
  - Example: `src/api/middleware.ts:23-30`

**Component connections**:

- [Component A] → [Component B]: [How they interact]
  - Entry point: `file1.ext:123`
  - Exit point: `file2.ext:456`

**Conventions observed**:

- Files are organized by [observed pattern]
- Naming follows [observed convention]
- Testing uses [observed approach]

## Code References

These are the key references:

- `path/to/file1.ext:123` - Main entry point for X
- `path/to/file2.ext:45-67` - Core validation logic
- `path/to/file3.ext:89` - Database queries for Y
- `path/to/file4.ext:200-250` - Error handling implementation

## Similar Implementations

These existing patterns in the codebase may be relevant:

**Example from `path/to/example.ext:100-120`**:

```language
// Code showing similar pattern already in use
```

This pattern is also used in:

- `other/file.ext:50` - For feature X
- `another/file.ext:75` - For feature Y

## Open Questions

This table lists the questions to resolve before the next phase. Each question has a short
local ID. This section is the record, because there is no external tracker.

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| Q1 | [The question, phrased so someone else could answer it] | [What cannot proceed without the answer] | Open |
| Q2 | [Another question] | [What it blocks] | Open |

Rules for this table:

- **IDs are local and stable.** Number them `Q1`, `Q2`, and so on, in the order you raise them.
  Do not renumber them when a question is resolved. Other documents cite the ID.
- **A question needs something that it blocks.** If it blocks nothing, it is a note and not an
  open question. Put it in the findings.
- **Resolving has two parts.** `/wb:resolve_questions` sets the State cell to
  `Resolved YYYY-MM-DD → design.md (## Technical Decisions)`. It also writes the decision and
  its rationale into `design.md`. Do **not** record the decision here. Research records facts,
  and a decision is not a fact about the codebase.
- **Keep resolved rows in place.** They are the audit trail.

## Next Steps

These steps follow from the findings:

1. [Suggested next action based on findings]
2. [Another logical next step]
3. Review the research document
4. Run `/wb:create_design` to write the design decisions

````
