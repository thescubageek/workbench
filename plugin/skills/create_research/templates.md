# create_research — output template

Read this when Step 6 directs you to. Write `research.md` in this shape. Never paraphrase the
template from memory; every bracketed placeholder must be replaced with real content from the
codebase before the file is written.

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

Quick reference list:

- `path/to/file1.ext:123` - Main entry point for X
- `path/to/file2.ext:45-67` - Core validation logic
- `path/to/file3.ext:89` - Database queries for Y
- `path/to/file4.ext:200-250` - Error handling implementation

## Similar Implementations

Existing patterns in the codebase that might be relevant:

**Example from `path/to/example.ext:100-120`**:

```language
// Code showing similar pattern already in use
```

This pattern is also used in:

- `other/file.ext:50` - For feature X
- `another/file.ext:75` - For feature Y

## Open Questions

Questions that must be resolved before the next phase live **here**, in this document, with a
short local ID. This section is the record — there is no external tracker.

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| Q1 | [The question, phrased so someone else could answer it] | [What cannot proceed without the answer] | Open |
| Q2 | [Another question] | [What it blocks] | Open |

Rules for this table:

- **IDs are local and stable.** `Q1`, `Q2`, … numbered in the order raised, never renumbered
  when one is resolved. The ID is the handle another document cites.
- **A question is only a question if something is blocked by it.** If nothing is blocked, it is
  a note, not an open question — put it in the findings.
- **Resolving is a two-part act.** `/wb:resolve_questions` sets the State cell to
  `Resolved YYYY-MM-DD → design.md (## Technical Decisions)` and writes the decision, with its
  rationale, into `design.md`. The decision itself does **not** get recorded here: research
  documents facts, and a decision is not a fact about the codebase.
- **Keep resolved rows in place.** The audit trail is the point.

## Next Steps

Based on the research findings:

1. [Suggested next action based on findings]
2. [Another logical next step]
3. Review the research document
4. Run `/create_design` to create design decisions

````
