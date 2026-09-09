# README.md Template

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
2. ⏳ Research phase (`/wb:create_research [directory]`)
3. ⏳ Design phase (`/wb:create_design [directory]`)
4. ⏳ Execution planning (`/wb:create_tasks [directory]`)
5. ⏳ Implementation (`/wb:implement [directory]`)
6. ⏳ Testing & Verification

## Quick Commands

```bash
# Continue with research (analyzes codebase)
/wb:create_research [this-directory]

# Create design decisions
/wb:create_design [this-directory]

# Generate execution plan with tasks
/wb:create_tasks [this-directory]

# Implement with worker agents (/wb:implement_inline runs it in this session)
/wb:implement [this-directory]

# Update status across all files
/wb:update_status [this-directory]
```

## Git Information

- **Branch**: [branch-name]
- **Commit**: [commit-hash]
- **Repository**: [repo-name]
````
