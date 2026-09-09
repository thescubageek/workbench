# design.md Template

````markdown
---
project: [project-name]
ticket: [ticket-reference or null]
created: [YYYY-MM-DD]
created_timestamp: [ISO-8601 timestamp]
status: draft
last_updated: [YYYY-MM-DD]
designer: [username]
git_commit: [commit-hash or "not-in-git"]
git_branch: [branch-name or "not-in-git"]
repository: [repo-name or "unknown"]
tags: [design, architecture, [project-name]]
depends_on: research.md
---

# Design: [Project Name]

**Created**: [YYYY-MM-DD HH:MM UTC]
**Designer**: [username]
**Ticket**: [ticket-reference or N/A]
**Status**: Draft

## Problem Statement

[What problem we're solving and why - to be filled by /wb:create_design]

### Success Metrics
- [ ] [To be defined]

## Design Approach

[High-level solution approach - to be added]

### Why This Approach
- [To be added from design analysis]

## Technical Decisions

### Architecture
- [To be defined]

### Data Model
- [To be defined]

### Integration Points
- [To be identified]

## Scope Definition

### In Scope
- [To be defined]

### Out of Scope
- [To be defined]

## Success Criteria

### Functional Requirements
- [ ] [To be defined]

### Non-Functional Requirements
- [ ] [To be defined]

## Risk Analysis

[To be evaluated]

### Assumptions

| ID | Assumption | Validated? |
| -- | ---------- | ---------- |
| — | [none yet] | — |

## Rejected Alternatives

[To be documented during design]

## Pending Decisions

| ID | Decision Needed | Blocks |
| -- | --------------- | ------ |
| — | [none yet] | — |

## References

- Research: [research.md](research.md)
- Tasks: [tasks.md](tasks.md)
- Related: [to be added]
````
