# research.md Template

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

Quick reference to key files:
[Specific file:line references - to be added]

## Similar Implementations

[Examples from codebase - to be added]

## Open Questions

Questions that block the next phase live here as a table with local IDs. To be populated by
`/wb:create_research`.

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| — | [none yet] | — | — |

## Next Steps

1. Run `/wb:create_research [directory]` to populate this document
2. Review findings before design

## References

- Design: [design.md](design.md)
- Tasks: [tasks.md](tasks.md)
````
