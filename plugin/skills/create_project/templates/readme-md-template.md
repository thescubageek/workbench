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

## Documentation Structure

- **[research.md](research.md)** - Codebase research and findings
- **[design.md](design.md)** - Architectural design decisions
- **[tasks.md](tasks.md)** - Execution plan and task tracking
- **[journal.md](journal.md)** - Session journal. An entry opens when work starts

## Workflow

1. ✅ Project structure created
2. ⏳ Research phase (`/wb:create_research [directory]`)
3. ⏳ Design phase (`/wb:create_design [directory]`)
4. ⏳ Execution planning (`/wb:create_tasks [directory]`)
5. ⏳ Implementation (`/wb:implement [directory]`)
6. ⏳ Testing & Verification

## Quick Commands

```bash
# Research the codebase
/wb:create_research [this-directory]

# Write the design decisions
/wb:create_design [this-directory]

# Write the execution plan and its tasks
/wb:create_tasks [this-directory]

# Implement the plan with worker agents. /wb:implement_inline runs it in this session instead
/wb:implement [this-directory]

# Update the status in all files
/wb:update_status [this-directory]
```

## Git Information

- **Branch**: [branch-name]
- **Commit**: [commit-hash]
- **Repository**: [repo-name]
````
