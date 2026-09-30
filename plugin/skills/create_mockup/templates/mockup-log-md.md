# mockup-log.md

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 8. Write `mockups/mockup-log.md`. Create it once, and update it in each iteration.

```markdown
---
feature: [feature name]
created: [YYYY-MM-DD]
current_version: 1
status: iterating
project_directory: [full path to project directory]
last_updated: [YYYY-MM-DD]
---

# Mockup Iteration Log

## Feature: [Name]

**Goal**: [From clarifying questions]

## Version History

### v001 - [YYYY-MM-DD] - Initial Draft
- **Status**: In Review
- **Key decisions**: [brief summary]
- **Feedback needed**: [what to validate]

## UI Research Reference

_From the first research. Apply it to all versions._

- **Layout pattern**: [pattern from research]
- **Component library**: [location]
- **Styling system**: [approach]
- **Icon system**: [library and usage pattern, or "None - text only"]
- **Similar features**: [references]

## Running Requirements

### Confirmed (KEEP)
_Requirements that the iterations confirmed_

### Rejected (REMOVE)
_Ideas that were explored and rejected, each with its rationale_

### Open (DECIDING)
_Still under discussion. Cite the `UIQ` IDs from the mockup.md of the current version. Do not
repeat the questions._

## Design Principles Emerging

1. [Principle discovered through iteration]
```
