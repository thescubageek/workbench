# tasks.md Template

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

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

**The checkboxes in this file are the source of truth.** There is no external tracker. When a
task is done, change its `[ ]` to `[x]` and add `(completed YYYY-MM-DD HH:MM)`. The
frontmatter counters are a derived cache. Only `/wb:update_status` writes them, so never edit
them by hand. Git is the durable record.

Every task line has a bold local ID with at least one digit, for example `P1-T3`. Every count
uses that shape. The success criteria and prerequisites in this file are checkboxes too, so a
bare `grep -c '^- \[x\]'` counts them as tasks:

```bash
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # completed
grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # remaining
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
- [x] **P0-T1** — Create project structure (completed [YYYY-MM-DD HH:MM])
- [ ] **P0-T2** — Complete research using `/wb:create_research [directory]`
- [ ] **P0-T3** — Create design document using `/wb:create_design [directory]`
- [ ] **P0-T4** — Generate execution plan using `/wb:create_tasks [directory]`

---

## Implementation Phases

[To be populated by /wb:create_tasks after design is approved]

---

## 📝 Completed Tasks Archive

- [x] Create project structure - [YYYY-MM-DD HH:MM]

---

## 🚧 Blockers & Notes

### Current Blockers
| Blocker | Impact | Action | Owner | Due Date |
|---------|--------|--------|-------|----------|
| Research is needed | The design cannot start | Run /wb:create_research | [username] | [date] |

### Implementation Notes
- The project was created on [YYYY-MM-DD].

---

## 🔗 Quick Reference

### Key Files
- **Research**: [research.md](research.md)
- **Design**: [design.md](design.md)

### Next Action
**Run**: `/wb:create_research [this-directory]`
````
