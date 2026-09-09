---
name: create_project
description: Initialize comprehensive project documentation with research, design, and task files
argument-hint: "[project-name] [base-dir] [ticket-ref]"
allowed-tools: Read
---

# Initialize Project Documentation

Creates a comprehensive documentation structure for a new project or feature, setting up folders and files for research, planning, and task tracking with proper metadata.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- [templates.md](templates.md) — the five initial file templates, under five named sections. Step 4 reads **one section per file it creates**, not the whole file
- [reference.md](reference.md) — argument usage, status progression, error handling

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

Create five foundation files. **Read one template section per file**, at the moment you create
that file — reading `templates.md` whole pulls in four skeletons you do not need.

1. **README.md** — navigation hub. Read the `## README.md Template` section of
   [templates.md](templates.md) NOW and create the file from it, with all metadata filled in.
2. **research.md** — research documentation. Read the `## research.md Template` section NOW
   and create the file from it, with all metadata filled in.
3. **design.md** — design decisions. Read the `## design.md Template` section NOW and create
   the file from it, with all metadata filled in.
4. **tasks.md** — task tracking. Read the `## tasks.md Template` section NOW and create the
   file from it, with all metadata filled in.
5. **journal.md** — the session journal. Read the `## journal.md Template` section NOW and
   create the file from it. It starts with no entries; the implementation stages open the
   first one when work begins.

Two things about the generated `tasks.md` are load-bearing rather than cosmetic:

- **Checkbox state in `tasks.md` is the source of truth.** There is no external tracker. The
  planning checkboxes it ships with are live status from the moment the file exists, not a
  bootstrap convenience to be superseded later.
- **The frontmatter counters are a derived cache with exactly one writer**, `/wb:update_status`.
  The template carries `task_tracking: markdown-checkboxes` to say so in the file itself.

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
├── tasks.md       - Execution plan (1/4 tasks complete)
└── journal.md     - Session journal (no entries yet)

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
   /create_tasks [directory]

4. Implement with TDD:
   /implement [directory]

Ready to begin research phase!
```

## Important Notes

See [reference.md](reference.md) — argument usage, status progression, and error handling.
