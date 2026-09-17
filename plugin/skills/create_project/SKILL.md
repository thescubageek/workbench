---
name: create_project
description: Initialize comprehensive project documentation with research, design, and task files
argument-hint: "[project-name] [base-dir] [ticket-ref]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Initialize Project Documentation

Creates a comprehensive documentation structure for a new project or feature, setting up folders and files for research, planning, and task tracking with proper metadata.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- `templates/` — the five initial file templates, one per file: [readme-md-template.md](templates/readme-md-template.md) · [research-md-template.md](templates/research-md-template.md) · [design-md-template.md](templates/design-md-template.md) · [tasks-md-template.md](templates/tasks-md-template.md) · [journal-md-template.md](templates/journal-md-template.md). Step 4 reads **one per file it creates**
- [reference.md](reference.md) — argument usage, status progression, error handling
- [../../docs/reference/branch-naming.md](../../docs/reference/branch-naming.md) — the branch-name
  rule Step 3 applies, shared with `jira-context`, `forge` and `implement`

**If a directed read fails, stop — do not continue from memory.** These files live outside your
project, so a read can be refused. Say which file was refused, that reads outside the working
directory are gated, and that the fix is to allow the read once or to relaunch with
`--add-dir <plugin-path>`. Do not route around a refusal with `cat`.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If arguments provided** (e.g., `/wb:create_project auth-refactor docs/plans LINEAR-456`):
   - Read them in order as **project-name**, then **base-dir**, then **ticket-ref**
   - Skip prompting and proceed directly to Step 2

   **Do not split a sentence into these three slots.** If the first argument contains spaces, or
   reads as a description rather than a slug — "a small parser for duration strings" — the user
   typed a description, not three positional values: **ask** for the project name instead of
   binding word one, two and three. *(This step names the slots, not their positional
   placeholders — the harness substitutes those values into skill text.)*

2. **If partial arguments** (e.g., `/wb:create_project auth-refactor`):
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

Bind three slots, in order: the **project name**, then the **base directory** (default
`docs/plans`), then an optional **ticket reference**. Prompt for any that is missing.

**Refuse prose.** If the first argument contains spaces or reads as a description of the work
rather than a name, do not split it across the slots — ask for the three values by name instead.
Splitting a sentence positionally produces a wrongly-named plan directory with no error.

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

**Then align the working branch, before any file is written.** Naming the plan directory is the
moment the work acquires a name — the project name and the ticket ref are both in hand, and
nothing later in the pipeline knows more than you do right now. Waiting until the first commit
is how a session ends up shipping a branch named after a Conductor codeword or the user's last
message.

Read [../../docs/reference/branch-naming.md](../../docs/reference/branch-naming.md) NOW and
apply it. Two inputs it needs, both already parsed in Step 1:

- The **ticket reference**, if one was given — it is the highest-precedence scope.
- The **project name** — the source of the snake_case description when there is no ticket
  summary to draw from.

If no ticket was given, check whether this work targets a **known release version** (a version
bump this plan will make, or a plan named for a release) before concluding there is no scope.

Propose, don't run: the reference doc requires the user's go-ahead, and a declined or
unavailable rename is non-blocking — carry on and create the directory either way. Record the
branch you end up on in Step 2's `git_branch`, re-reading it after any rename so the frontmatter
does not capture the old name.

### Step 4: Create Initial Files with Rich Metadata

Create five foundation files. **Read one template file per file you create**, at the moment you
create it.

1. **README.md** — navigation hub. Read [templates/readme-md-template.md](templates/readme-md-template.md) NOW and create the file from it, with all metadata filled in.
2. **research.md** — research documentation. Read [templates/research-md-template.md](templates/research-md-template.md) NOW
   and create the file from it, with all metadata filled in.
3. **design.md** — design decisions. Read [templates/design-md-template.md](templates/design-md-template.md) NOW and create
   the file from it, with all metadata filled in.
4. **tasks.md** — task tracking. Read [templates/tasks-md-template.md](templates/tasks-md-template.md) NOW and create the
   file from it, with all metadata filled in.
5. **journal.md** — the session journal. Read [templates/journal-md-template.md](templates/journal-md-template.md) NOW and
   create the file from it. It starts with no entries; the implementation stages open the
   first one when work begins.

Two things about the generated `tasks.md` are load-bearing rather than cosmetic:

- **Checkbox state in `tasks.md` is the source of truth.** There is no external tracker. The
  planning checkboxes it ships with are live status from the moment the file exists, not a
  bootstrap convenience to be superseded later.
- **The frontmatter counters are a derived cache with exactly one writer**, `/wb:update_status`.
  The template carries `task_tracking: markdown-checkboxes` to say so in the file itself.

**`thoughts/` is deliberately not provisioned here.** `/wb:explore_design` writes
`[project-dir]/thoughts/<date>-<topic>.md`, and a write to a nested path creates its parent
directories — so the directory appears on first use. Git does not track an empty directory, so
creating one now buys nothing without also planting a `.gitkeep`. Do not add a sixth file or a
`mkdir` for it.

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

📂 thoughts/ — explorations; created on first use by /wb:explore_design

📊 Metadata captured:
- Git commit: [commit-hash]
- Branch: [branch-name]
- Repository: [repo-name]
- Created by: [username]
- Timestamp: [ISO-8601]

🔄 Next Steps:

1. Research the codebase:
   /wb:create_research [directory]

2. Optional — if research surfaces more than one viable approach,
   air the trade-off before design locks it in:
   /wb:explore_design [directory]      (writes to thoughts/)

3. After research, create design:
   /wb:create_design [directory]

4. Then generate execution plan:
   /wb:create_tasks [directory]

5. Implement with TDD:
   /wb:implement [directory]

Ready to begin research phase!
```

## Important Notes

See [reference.md](reference.md) — argument usage, status progression, and error handling.
