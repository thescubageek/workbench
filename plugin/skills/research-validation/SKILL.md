---
name: research-validation
description: Validates research documents against the actual codebase. Checks file paths exist, code snippets match, and behavioral claims are accurate. Use when "validate research", "check research accuracy", "verify research", or "is this research still accurate".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(test:*, ls:*)
---

# Research Validation

Research goes stale. Code changes. This skill checks whether documented claims are still true.

## The Rule

```
NO TRUST WITHOUT VERIFICATION
```

If the research document says it, check it against the code. Every path, every snippet, every behavioral claim.

## When to Validate

- Code changed since research was written
- Before a planning session that depends on research
- When anyone says "is this still accurate?"
- After a refactor or major feature change
- Before making product decisions based on research

## How to Validate

### 1. Find the Document

Look for research documents in the specified or current project directory:

- `product-research.md` (PM-focused)
- `research.md` (engineering-focused)

If both exist, validate whichever the user specifies. If unspecified, ask.

### 2. Read It Fully

Read the entire document. No limit/offset. Full context required.

### 3. Check Every Claim

**Paths** — every file path in backticks:

```bash
test -f "path/to/file.ext" && echo "PASS" || echo "FAIL: not found"
```

**Snippets** — every code block with a source reference:

- Read the actual file at the stated location
- Compare quoted content to actual content
- PASS if matches, STALE if changed, FAIL if gone

**Behaviors** — every "when X, system does Y" claim:

- Grep for the handler/route/function
- Read the implementation
- Trace the flow: does the code do what the document says?
- PASS if confirmed, FAIL if wrong, UNCERTAIN if can't fully trace

**Patterns** — every "codebase uses X" claim:

- Search for the pattern across the codebase
- Verify it exists where claimed
- PASS if found, STALE if changed, FAIL if gone

### 4. Update the Document

Update frontmatter:

- `validation_status: passed` | `passed_with_warnings` | `failed`
- `last_validated: [YYYY-MM-DD]`

### 5. Report

```
## Research Validation: [document name]

**Status**: PASS | PASS WITH WARNINGS | FAIL
**Checked**: [date]

Paths: N/M exist
Snippets: N/M match
Behaviors: N/M verified, K uncertain
Patterns: N/M confirmed

### Issues
[List FAIL or STALE items with what changed]

### Action Needed
[What to update, or "none — document is accurate"]
```

## If Validation Fails

Don't silently fix the document. Report:

1. What claims are now wrong
2. What changed in the code (if determinable)
3. Whether it needs a minor update or full re-research
4. Suggest `/wb:create_product_research` or `/wb:create_research` to regenerate if too stale
