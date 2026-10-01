# research.md Template

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

````markdown
---
project: [project-name]
ticket: [ticket-reference or null]
created: [YYYY-MM-DD]
created_timestamp: [ISO-8601 timestamp]
status: draft
last_updated: [YYYY-MM-DD]
researcher: [username]
git_commit: [commit-hash or "not-in-git"]
git_branch: [branch-name or "not-in-git"]
repository: [repo-name or "unknown"]
tags: [research, codebase, [project-name]]
---

# Research: [Project Name]

**Created**: [YYYY-MM-DD HH:MM UTC]
**Researcher**: [username]
**Ticket**: [ticket-reference or N/A]
**Git Commit**: [commit-hash]
**Branch**: [branch-name]

## Research Question

[What are we trying to understand? To be filled by /wb:create_research]

## Summary

[High-level findings - to be added]

## Detailed Findings

[Research findings will be documented here by /wb:create_research]

### Component Analysis
[How components work - to be added]

### Data Flow
[How data moves through system - to be added]

### Dependencies
[External dependencies and integrations - to be added]

## Architecture Documentation

### Patterns Found
[Patterns and conventions discovered - to be added]

### File Structure
[Relevant directory structure - to be added]

## Code References

These are the key files:
[Specific file:line references - to be added]

## Similar Implementations

[Examples from codebase - to be added]

## Open Questions

This table lists the questions that block the next phase. Each question has a local ID.
`/wb:create_research` fills the table.

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| — | [none yet] | — | — |

## Next Steps

1. Run `/wb:create_research [directory]` to fill this document.
2. Review the findings before the design starts.

## References

- Design: [design.md](design.md)
- Tasks: [tasks.md](tasks.md)
````
