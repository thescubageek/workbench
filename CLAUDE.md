# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Claude Code plugin (`wb`) providing structured software development workflows: project planning, research, design, execution, and validation with TDD enforcement and beads integration.

## Output Discipline

When running `/wb:*` commands, keep narration minimal — the artifact is the deliverable, not the chat:

- Act on barriers and checkpoints **silently** — do not announce "BARRIER 2 satisfied", "all agents returned", or restate the plan between steps.
- After writing a document, **do not reproduce its contents back into the chat**. Emit a single one-line completion summary (e.g. `✅ research.md — <topic>; N findings. Next: /wb:create_design`).
- Surface only what the user must act on: blockers, decisions awaiting their input, and errors. Everything else lives in the artifact.

This is the global reinforcement of each command's inline output-discipline directive. (End users: see README "Output discipline" to opt this rule into your own `CLAUDE.md`.)

## Repository Structure (Plugin Layout)

- `.claude-plugin/` - Plugin manifest
- `commands/` - Slash commands (`/wb:*`)
- `agents/` - Specialized subagent definitions
- `skills/` - Auto-activated background capabilities
- `hooks/` - Event handlers (SessionStart, PostToolUse)
- `scripts/` - Utility scripts (lint, lint-hook)
- `docs/` - Documentation and guides
- `general/` - General-purpose prompts and templates
- `.claude/` - Local development configuration

## Development Tools

### Markdown Linting

```bash
# Lint changed markdown files
./scripts/lint

# Auto-fix markdown issues
./scripts/lint --fix

# Lint specific files
./scripts/lint file1.md file2.md

# Lint all markdown files
./scripts/lint --all
```

**Automatic Linting**: PostToolUse hooks automatically lint markdown files after Write/Edit operations.

### Configuration

**Markdown Lint Rules** (`.markdownlintrc`):

- Line length checking disabled (MD013)
- Inline HTML allowed (MD033)
- Emphasis as heading allowed (MD036)
- Fenced code blocks without language allowed (MD040)

### Testing the Plugin

```bash
# Test locally
claude --plugin-dir /path/to/this/repo

# Reload after changes
/reload-plugins
```

### Releasing New Commands/Skills/Agents

**CRITICAL**: When the plugin is installed via marketplace (not `--plugin-dir`), the plugin system caches files at `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. The cache is keyed by version — adding new files will NOT show up until the version bumps AND the user runs an update.

When adding new commands, skills, or agents:

1. Bump `version` in `.claude-plugin/plugin.json` (e.g., 1.0.0 → 1.1.0 for features, 1.0.0 → 1.0.1 for fixes)
2. Bump matching `version` in `.claude-plugin/marketplace.json` (must match plugin.json)
3. Commit and push
4. Users run `claude plugin update wb@gvarela-workbench` from the **shell** (not a slash command — it's a CLI command, run with `!` prefix or in a separate terminal)
5. After update, restart Claude (or `/reload-plugins`) to apply

**What does NOT work alone**:

- `/reload-plugins` — only re-reads the existing cache, doesn't pull updates
- Pushing to git — the marketplace clone at `~/.claude/plugins/marketplaces/<name>/` doesn't auto-pull
- Bumping version without `claude plugin update` — the cache stays at the old version

For local dev (`--plugin-dir` install), changes take effect immediately without a version bump.

## Command Workflow

The commands follow a strict sequential workflow:

```
/wb:create_project → /wb:create_research → /wb:create_design → /wb:create_execution → /wb:implement_tasks → /wb:validate_execution
```

For multi-session work:

```
[Session 1] → /wb:create_handoff → [Session 2] → /wb:resume_handoff → [Continue work]
```

Each command builds upon the previous one's output, creating structured documentation in timestamped directories under `docs/plans/`.

## Workflow Philosophy

The workflow separates three distinct concerns:

1. **Research** (`research.md`) - Document what EXISTS (facts only, no recommendations)
2. **Design** (`design.md`) - Document WHAT to build and WHY (architectural decisions)
3. **Execution** (`tasks.md`) - Document HOW to build it (phased implementation plan)

## Core Command Philosophy

### Critical Principles

1. **Document, Don't Judge**: Research describes what EXISTS, not what should be changed
2. **Explicit Barriers**: Commands implement synchronization points (⛔ BARRIER) to ensure complete context
3. **File Reading Protocol**: ALWAYS read files FULLY (no limit/offset) before analysis
4. **Dual Verification**: Separate automated checks from manual verification
5. **Zero Scope Creep**: Tasks only come from plans, no additions
6. **Beads Required**: These commands require beads for ALL task tracking (`bd init`)
   - Use beads for phases AND granular tasks
   - Do NOT use TaskCreate, TaskUpdate, TodoWrite, or markdown checkboxes for tracking
   - Markdown files document the PLAN, beads tracks the STATUS

### Beads Error Handling

If any `bd` command fails:

1. **Diagnose**: Run `bd doctor` to check for issues
2. **Report**: Tell the user the specific error and suggest fixes
3. **Fix**: Common fixes:
   - "beads not initialized" → `bd init`
   - "issue not found" → `bd list` to find correct ID
   - "database locked" → wait and retry
4. **Retry**: After fixing, re-run the failed command

### Task Tracking Philosophy

**Beads for STATUS, Markdown for PLAN**:

- **Beads issues** (`bd create`, `bd update`, `bd close`): Track live status of ALL work
- **Markdown files** (tasks.md, research.md, design.md): Document the PLAN and rationale

### Command Structure Patterns

When modifying commands, maintain these patterns:

```markdown
⛔ BARRIER 1: After file reading - full context required
⛔ BARRIER 2: After agent spawning - wait for ALL
⛔ BARRIER 3: Before writing - no placeholders allowed
⛔ CHECKPOINT: Between phases - human verification required
```

### Frontmatter Standards

All generated documentation files use consistent YAML frontmatter:

- Basic: `project`, `ticket`, `created`, `status`, `last_updated`
- Git metadata: `git_commit`, `git_branch`, `repository`
- User tracking: `researcher`, `planner`, `assignee`
- Progress: `current_phase`, `total_tasks`, `completed_tasks`

## Agent Spawning with Model Selection

Commands support model hints when spawning agents:

- `haiku`: File searches, pattern matching, simple tasks
- `sonnet`: Code analysis, integration planning, test design
- `opus`: Complex reasoning, critical decisions

## Working with Commands

When creating or modifying commands:

1. Follow existing command patterns
2. Include all three barriers and checkpoints
3. Use "think deeply" directives at critical decision points
4. Maintain the documentarian philosophy for research
5. Separate automated from manual verification
6. Always read files FULLY before processing
7. Use parallel agents for efficiency but wait for ALL to complete

## Best Practices

When creating new prompts or commands:

1. Use clear, unambiguous language
2. Include examples where helpful
3. Document any special requirements or dependencies
4. Test thoroughly before committing
5. Keep prompts focused on a single purpose

## Git Workflow

- The main branch is `main`
- Commit messages should be descriptive
- Run `./scripts/lint` before committing markdown files
- Keep the repository organized by category

## Beads Issue Tracking

This repository uses [beads](https://github.com/steveyegge/beads) for task tracking across sessions.

### Quick Reference

```bash
bd ready              # Find available work (no blockers)
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git (run at session end)
```

### Session Protocol

See [AGENTS.md](AGENTS.md) for the full session close protocol. Key points:

1. **Before ending**: Close completed issues with `bd close`
2. **Sync**: Run `bd sync` to persist changes
3. **Push**: Commit and push to remote

### Integration with wb Commands

The workbench commands (`/wb:*`) automatically detect beads and use it for phase tracking. See [docs/commands-reference.md](docs/commands-reference.md) for details.
