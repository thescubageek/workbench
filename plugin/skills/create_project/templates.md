# create_project — initial file templates

Read the **section you need**, when its Step 4 sub-step directs you to — not the whole file.
Each section below is an independent template, and reading one to write another's file costs
tokens for nothing. Never paraphrase a template from memory.

Sections: `README.md Template` · `research.md Template` · `design.md Template` ·
`tasks.md Template` · `journal.md Template`

## README.md Template

````markdown
# [Project Name]

**Created**: [YYYY-MM-DD]
**Ticket**: [ticket-reference or N/A]
**Status**: Planning

## Overview

This directory contains documentation for [project-name].

## Documentation Structure

- **[research.md](research.md)** - Codebase research and findings
- **[design.md](design.md)** - Architectural design decisions
- **[tasks.md](tasks.md)** - Execution plan and task tracking
- **[journal.md](journal.md)** - Session journal; entries open when work starts

## Workflow

1. ✅ Project structure created
2. ⏳ Research phase (`/create_research [directory]`)
3. ⏳ Design phase (`/create_design [directory]`)
4. ⏳ Execution planning (`/create_tasks [directory]`)
5. ⏳ Implementation (`/implement [directory]`)
6. ⏳ Testing & Verification

## Quick Commands

```bash
# Continue with research (analyzes codebase)
/create_research [this-directory]

# Create design decisions
/create_design [this-directory]

# Generate execution plan with tasks
/create_tasks [this-directory]

# Implement with worker agents (/wb:implement_inline runs it in this session)
/implement [this-directory]

# Update status across all files
/update_status [this-directory]
```

## Git Information

- **Branch**: [branch-name]
- **Commit**: [commit-hash]
- **Repository**: [repo-name]
````

## research.md Template

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

[What are we trying to understand? To be filled by /create_research]

## Summary

[High-level findings - to be added]

## Detailed Findings

[Research findings will be documented here by /create_research]

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
`/create_research`.

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| — | [none yet] | — | — |

## Next Steps

1. Run `/create_research [directory]` to populate this document
2. Review findings before design

## References

- Design: [design.md](design.md)
- Tasks: [tasks.md](tasks.md)
````

## design.md Template

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

[What problem we're solving and why - to be filled by /create_design]

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

## tasks.md Template

````markdown
---
project: [project-name]
ticket: [ticket-reference or null]
created: [YYYY-MM-DD]
created_timestamp: [ISO-8601 timestamp]
status: not-started
last_updated: [YYYY-MM-DD]
assignee: [username]
current_phase: 0
total_tasks: 4
completed_tasks: 1
task_tracking: markdown-checkboxes
git_commit: [commit-hash or "not-in-git"]
git_branch: [branch-name or "not-in-git"]
repository: [repo-name or "unknown"]
tags: [tasks, tracking, [project-name]]
---

# Tasks: [Project Name]

**Created**: [YYYY-MM-DD HH:MM UTC]
**Assignee**: [username]
**Ticket**: [ticket-reference or N/A]
**Current Phase**: Planning

## Task tracking

**Checkbox state in this file is the source of truth.** There is no external tracker. Flip
`[ ]` → `[x]` as work completes and append `(completed YYYY-MM-DD HH:MM)`. The frontmatter
counters are a derived cache with exactly one writer — `/wb:update_status` — and are never
hand-edited. Git is the durable record.

```bash
grep -c '^- \[x\]' tasks.md    # completed
grep -c '^- \[ \]' tasks.md    # remaining
```

## Progress Overview

| Phase | Status | Tasks | Progress |
|-------|--------|-------|----------|
| Planning | 🔄 In Progress | 1/4 | 25% |
| Implementation | ⏸️ Not Started | 0/0 | 0% |

**Overall Progress**: 1/4 planning tasks (25%)

---

## Planning Phase

### 📋 Documentation Setup
- [x] Create project structure (completed [YYYY-MM-DD HH:MM])
- [ ] Complete research using `/create_research [directory]`
- [ ] Create design document using `/create_design [directory]`
- [ ] Generate execution plan using `/create_tasks [directory]`

---

## Implementation Phases

[To be populated by /create_tasks after design is approved]

---

## 📝 Completed Tasks Archive

- [x] Create project structure - [YYYY-MM-DD HH:MM]

---

## 🚧 Blockers & Notes

### Current Blockers
| Blocker | Impact | Action | Owner | Due Date |
|---------|--------|--------|-------|----------|
| Research needed | Can't design | Run /create_research | [username] | [date] |

### Implementation Notes
- Project initialized on [YYYY-MM-DD]

---

## 🔗 Quick Reference

### Key Files
- **Research**: [research.md](research.md)
- **Design**: [design.md](design.md)

### Next Action
**Run**: `/create_research [this-directory]`
````

## journal.md Template

````markdown
# Session Journal: [Project Name]

Append-only, reverse-chronological — newest entry at the top.

**Entries open when work starts, not when it ends.** A session does not get to choose how it
ends: a token limit, a closed laptop, or a crashed harness runs no shutdown step. An entry
written only at completion would be silent in exactly those cases, and worse than silent — its
tail would still show the last *finished* phase, so the next session would read a confident,
stale record and never learn that work stopped mid-task. Opening on entry makes the default
residue of an abrupt kill correct: an open entry naming what was being attempted and what came
next.

An open entry beside uncommitted changes means an interrupted task. An open entry beside a
clean tree means a session that simply moved on. The working tree is the authority, never this
file.

## [YYYY-MM-DD HH:MM] — OPEN — [what is being attempted]

- **Task/phase**: [ID and one-line description]
- **Next action**: [the literal next thing to do, specific enough to act on cold]
- **Started at**: [commit hash]

## [YYYY-MM-DD HH:MM] — CLOSED — [what was attempted]

- **Task/phase**: [ID and one-line description]
- **Landed**: [what actually changed]
- **Commits**: [range or hashes]
- **Learned**: [anything that changes how the remaining work should proceed — omit if nothing]
- **Blocked by**: [anything blocking — omit if nothing]
````
