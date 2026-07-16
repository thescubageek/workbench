---
description: Initialize comprehensive project documentation with research, design, and task files
argument-hint: "[project-name] [base-dir] [ticket-ref]"
---

# Initialize Project Documentation

Creates a comprehensive documentation structure for a new project or feature, setting up folders and files for research, planning, and task tracking with proper metadata.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If arguments provided** (e.g., `/create_project auth-refactor docs/plans LINEAR-456`):
   - Parse: `$1` = project-name, `$2` = base-dir, `$3` = ticket-ref
   - Skip prompting and proceed directly to Step 2

2. **If partial arguments** (e.g., `/create_project auth-refactor`):
   - Use provided arguments and prompt only for missing ones

3. **If no arguments**:
   - Prompt for all required information:

   ```
   I'll help you set up comprehensive project documentation. Please provide:
   1. Project name (short, kebab-case preferred, e.g., auth-refactor)
   2. Base directory (default: docs/plans)
   3. Ticket/issue reference (optional, e.g., GH-123, JIRA-456, LINEAR-789)

   I'll create a timestamped project directory with research, design, and task tracking files.
   ```

## Process Steps

### Step 1: Parse Arguments

```javascript
// Parse provided arguments
const projectName = $1;  // First argument
const baseDir = $2 || 'docs/plans';  // Second argument with default
const ticketRef = $3 || null;  // Third argument (optional)

// If any required args missing, prompt for them
```

### Step 2: Gather Metadata

**think deeply**

Collect system metadata for proper tracking:

```bash
# Git metadata (if in a git repository)
git_commit=$(git rev-parse HEAD 2>/dev/null || echo "not-in-git")
git_branch=$(git branch --show-current 2>/dev/null || echo "not-in-git")
git_remote=$(git remote get-url origin 2>/dev/null || echo "no-remote")

# Extract repository name from remote URL
repo_name=$(echo $git_remote | sed 's/.*[:/]\([^/]*\/[^.]*\).*/\1/')

# System metadata
current_date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
current_date_simple=$(date +"%Y-%m-%d")
username=$(whoami)
```

### Step 3: Create Directory Structure

Create the project directory with format:

```
[base-directory]/[YYYY-MM-DD]-[TICKET-][project-name]/
```

Examples:

- `docs/plans/2025-01-08-auth-refactor/`
- `docs/plans/2025-01-08-LINEAR-789-api-migration/`

### Step 4: Create Initial Files with Rich Metadata

Create four foundation files:

**1. README.md** - Navigation hub

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

## Workflow

1. ✅ Project structure created
2. ⏳ Research phase (`/create_research [directory]`)
3. ⏳ Design phase (`/create_design [directory]`)
4. ⏳ Execution planning (`/create_execution [directory]`)
5. ⏳ Implementation (`/implement_tasks [directory]`)
6. ⏳ Testing & Verification

## Quick Commands

```bash
# Continue with research (analyzes codebase)
/create_research [this-directory]

# Create design decisions
/create_design [this-directory]

# Generate execution plan with tasks
/create_execution [this-directory]

# Implement tasks with TDD
/implement_tasks [this-directory]

# Update status across all files
/update_status [this-directory]
```

## Git Information

- **Branch**: [branch-name]
- **Commit**: [commit-hash]
- **Repository**: [repo-name]
````

**2. research.md** - Research documentation

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

[Areas needing further investigation - to be added]

## Next Steps

1. Run `/create_research [directory]` to populate this document
2. Review findings before design

## References

- Design: [design.md](design.md)
- Tasks: [tasks.md](tasks.md)
````

**3. design.md** - Design decisions

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

## Rejected Alternatives

[To be documented during design]

## Pending Decisions

[Design decisions needing input - to be identified]

## References

- Research: [research.md](research.md)
- Tasks: [tasks.md](tasks.md)
- Related: [to be added]
````

**4. tasks.md** - Task tracking

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
- [ ] Generate execution plan using `/create_execution [directory]`

---

## Implementation Phases

[To be populated by /create_execution after design is approved]

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

**⛔ BARRIER 1**: Ensure all files are created with proper frontmatter before proceeding

### Step 5: Confirm Creation

Present the created structure:

```
✅ Project documentation initialized successfully!

📁 Created at: [full-path-to-directory]

📄 Files created:
├── README.md      - Project overview and navigation
├── research.md    - Research documentation (status: draft)
├── design.md      - Design decisions (status: draft)
└── tasks.md       - Execution plan (1/4 tasks complete)

📊 Metadata captured:
- Git commit: [commit-hash]
- Branch: [branch-name]
- Repository: [repo-name]
- Created by: [username]
- Timestamp: [ISO-8601]

🔄 Next Steps:

1. Research the codebase:
   /create_research [directory]

2. After research, create design:
   /create_design [directory]

3. Then generate execution plan:
   /create_execution [directory]

4. Implement with TDD:
   /implement_tasks [directory]

Ready to begin research phase!
```

## Important Notes

### Argument Usage

- `$1` - Project name (required if using arguments)
- `$2` - Base directory (optional, defaults to docs/plans)
- `$3` - Ticket reference (optional)
- `$ARGUMENTS` - All arguments as a single string

### Status Progression

Files progress through defined states:

- `research.md`: draft → in-progress → complete
- `design.md`: draft → ready → implementing → complete
- `tasks.md`: not-started → in-progress → complete

## Error Handling

Check for and handle:

- Directory already exists → Suggest different name or confirm overwrite
- Invalid project name → Request kebab-case format
- Git not available → Use placeholder values
- No write permissions → Suggest different location
