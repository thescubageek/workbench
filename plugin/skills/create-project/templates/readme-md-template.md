# README.md Template

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

````markdown
# [Project Name]

**Created**: [YYYY-MM-DD]
**Ticket**: [ticket-reference or N/A]

<!-- The status is not repeated here. Each document has its own `status:` field in its
     frontmatter. A summary copy in this file is the copy that nobody updates. -->

## Overview

This directory contains the documentation for [project-name].

## Intent

<!-- The plan's contract. Rules: plugin docs/reference/plan-intent.md. Change the Goal,
     a statement or a Non-goal only with the user's approval, and add an Amendments line. -->

**Goal**: [one sentence: what the project is for]

**Success looks like**:

- **S1**: [an observable statement a person could see or check]
- **S2**: [another]

**Non-goals**:

- [what this project will not do, or "none stated"]

**Amendments**:

- none

## Documentation Structure

- **[research.md](research.md)** - Codebase research and findings
- **[design.md](design.md)** - Architectural design decisions
- **[tasks.md](tasks.md)** - Execution plan and task tracking
- **[journal.md](journal.md)** - Session journal. An entry opens when work starts

## Workflow

1. ✅ Project structure created
2. ⏳ Research phase (`/wb:create-research [directory]`)
3. ⏳ Design phase (`/wb:create-design [directory]`)
4. ⏳ Execution planning (`/wb:create-tasks [directory]`)
5. ⏳ Implementation (`/wb:implement [directory]`)
6. ⏳ Testing & Verification

## Quick Commands

```bash
# Research the codebase
/wb:create-research [this-directory]

# Write the design decisions
/wb:create-design [this-directory]

# Write the execution plan and its tasks
/wb:create-tasks [this-directory]

# Implement the plan with worker agents. /wb:implement-inline runs it in this session instead
/wb:implement [this-directory]

# Update the status in all files
/wb:update-status [this-directory]
```

## Git Information

- **Branch**: [branch-name]
- **Commit**: [commit-hash]
- **Repository**: [repo-name]
````
