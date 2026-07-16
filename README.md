# Workbench (wb)

A Claude Code plugin for structured software development workflows: project planning, research, design, execution, and validation with TDD enforcement and beads integration.

## Overview

A personal workbench of tools and workflows for Claude Code. Streamlines software development through structured planning, research, and persistent task tracking with [beads](https://github.com/steveyegge/beads).

**[Complete Workflow Guide](docs/workbench-workflow-guide.md)**

## Quick Start

### Installation

```bash
# Add the marketplace and install the plugin
claude plugin marketplace add thescubageek/workbench
claude plugin install wb@thescubageek-workbench
```

For local development:

```bash
# Clone and test locally (changes take effect immediately)
git clone git@github.com:thescubageek/workbench.git
claude --plugin-dir /path/to/workbench
```

### Updating

To release new commands/skills/agents:

1. Bump `version` in **both** `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (must match)
2. Commit and push to GitHub
3. Users run from their shell (not a slash command):

   ```bash
   claude plugin update wb@thescubageek-workbench
   ```

4. Restart Claude (or `/reload-plugins`) to apply

Note: `/reload-plugins` alone does NOT pull updates — the cache is keyed by version and only `claude plugin update` invalidates it.

### Using Commands

```bash
# Initialize -> Research -> Design -> Implement -> Validate
/wb:create_project my-feature docs/plans TICKET-123
/wb:create_research docs/plans/2025-01-15-TICKET-123-my-feature
/wb:create_mockup docs/plans/... "UI component"  # Optional for UI
/wb:create_design docs/plans/...
/wb:create_execution docs/plans/...
/wb:implement_tasks docs/plans/...
/wb:validate_execution docs/plans/...
```

**Skills** (auto-activated): `project-structure`, `mockup-iteration`, `tdd-discipline`, `verification-before-completion`, `status-sync`, `review-prep`, `jira-context`, `clip`, `eli5-clip`

**[Full Commands Reference](docs/commands-reference.md)**

## What's Inside

### Commands (`/wb:*`)

Slash commands for project documentation and task management:

- **`/wb:create_project`** - Initialize structured documentation with rich metadata
- **`/wb:create_research`** - Document codebase using parallel research agents
- **`/wb:create_product_research`** - Document codebase from a product perspective (features, user flows, behaviors)
- **`/wb:create_mockup`** - Research UI patterns and create HTML mockups with visual validation
- **`/wb:create_design`** - Create architectural design decisions (WHAT and WHY)
- **`/wb:create_execution`** - Transform design into phased execution plan (HOW)
- **`/wb:implement_tasks`** - Implement with TDD (Red-Green-Refactor)
- **`/wb:implement_coordinated`** - Coordinate implementation with worker agents
- **`/wb:validate_execution`** - Validate implementation matches plan
- **`/wb:validate_project`** - Validate project documentation structure
- **`/wb:create_handoff`** - Create session handoff for work continuity
- **`/wb:resume_handoff`** - Resume from handoff document
- **`/wb:resolve_questions`** - Walk through open questions one at a time and record answers
- **`/wb:forge`** - Run a ticket through the full pipeline (research → validate); end-to-end sequencer
- **`/wb:update_status`** - Intelligently sync status across all documentation files
- **`/wb:help`** - Quick reference for all commands

### Agents

Specialized agents for codebase analysis:

- **`codebase-locator`** - Find specific components and files
- **`codebase-analyzer`** - Analyze implementation details with file:line references
- **`pattern-finder`** - Find similar patterns and implementations
- **`product-behavior-analyzer`** - Analyze the codebase as user-visible behaviors and product capabilities
- **`research-validator`** - Validate research docs against the codebase (paths, snippets, behavioral claims)
- **`task-verifier`** - Verify task completion against requirements

### Skills (auto-activated)

Background capabilities that Claude automatically invokes:

- **`project-structure`** - Enforces document separation (research.md, design.md, tasks.md)
- **`mockup-iteration`** - Iterate on UI mockups with KEEP/REMOVE/CHANGE tracking
- **`tdd-discipline`** - Enforces RED-GREEN-REFACTOR cycle before writing production code
- **`verification-before-completion`** - Requires running verification before claiming work is done
- **`status-sync`** - Monitors for status drift and reminds to sync
- **`review-prep`** - Interactive code review walkthrough using tmux and nvim
- **`jira-context`** - Loads context from a Jira ticket's "Agents" section (hivemind bootstrap); runs standalone or inside `create_research`/`forge`
- **`research-validation`** - Validates research docs against the actual codebase (paths, snippets, behavioral claims)
- **`model-help`** - Recommends the Claude model + reasoning-effort for a task/handoff; also the gate-mode authority for the workflow commands
- **`tracer-bullet`** - Fires one cheap probe at the riskiest assumption before fanning out into speculative work
- **`touch-grass`** - Paces long-horizon research/audits across checkpointed segments with self-scheduled resumes
- **`fetch-issues`** - Triages open GitHub issues into per-issue, session-ready handoffs
- **`daily-digest`** - Morning "catch me up + plan my day" orchestrator across Jira, beads, git, and more
- **`clip`** - Runs an instruction, then copies the result to the clipboard (cross-platform) instead of printing it
- **`eli5-clip`** - Summarizes recent work as a warm, plain-language message for a non-technical reader and copies it to the clipboard, tailored to a named recipient

### Hooks

- **SessionStart** - Auto-detects beads mode (stealth/git)
- **PostToolUse** - Lints markdown files after Write/Edit operations

## Plugin Structure

```
workbench/
├── .claude-plugin/     # Plugin manifest + marketplace
│   ├── plugin.json
│   └── marketplace.json
├── commands/           # Slash commands (/wb:*)
├── agents/             # Specialized subagents
├── skills/             # Auto-activated capabilities
├── hooks/              # Event handlers
├── scripts/            # Utility scripts (lint)
└── docs/               # Guides and documentation
```

## Beads Integration

Requires [beads](https://github.com/steveyegge/beads) for persistent task tracking:

```bash
bd init --stealth   # Stealth: .beads/ not committed (work repos)
bd init             # Git: .beads/ in git (personal projects)
```

Commands create/track beads issues for phases, tasks, and UI questions. SessionStart hook detects mode automatically.

## Core Philosophy

- **Document, Don't Judge**: Research describes what EXISTS, not what should change
- **Explicit Barriers**: Synchronization points prevent rushing ahead
- **Dual Verification**: Automated (tests, CI) + Manual (UX, edge cases)
- **Zero Scope Creep**: Tasks only from plans - no ad-hoc additions

## Output Discipline (optional opt-in)

The `/wb:*` commands already keep narration terse (act on barriers silently, emit a one-line completion summary instead of recapping the written document). To enforce the same discipline **globally** across all your Claude Code work — not just wb — add this to your own `~/.claude/CLAUDE.md` (user-wide) or a project `CLAUDE.md`:

```markdown
## Output Discipline
- Act on barriers/checkpoints silently; don't restate the plan between steps.
- After writing a file, don't reproduce its contents in chat — emit a one-line summary.
- Surface only blockers, decisions awaiting input, and errors.
```

The plugin cannot (and does not) write to your personal config — this rule is opt-in by design.

## Development

### Linting

```bash
./scripts/lint           # Lint changed files
./scripts/lint --fix     # Auto-fix issues
./scripts/lint --all     # Lint all markdown files
```

### Testing Changes

```bash
# Run with local plugin
claude --plugin-dir /path/to/this/repo

# Reload after changes (inside Claude Code)
/reload-plugins
```

## License

MIT
