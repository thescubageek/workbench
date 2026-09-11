# Workbench (wb)

A Claude Code plugin for structured software development workflows: project planning, research, design, execution, and validation with TDD enforcement.

## Overview

A personal workbench of tools and workflows for Claude Code. Streamlines software development through structured planning, research, and phased execution — with status tracked in the plan documents themselves, no external tracker required.

**[Complete Workflow Guide](docs/workbench-workflow-guide.md)**

## Quick Start

### Installation

```bash
# Add the marketplace and install the plugin
claude plugin marketplace add thescubageek/workbench
claude plugin install wb@thescubageek-workbench
```

The first time you run a stage, Claude asks once for permission to read the plugin's own
templates and prompts out of `~/.claude/plugins/cache/`. Approve it — choose the persistent
option and the grant applies to every project, so you answer it once per machine. If you run
Claude headless or in CI, see [Reading the plugin's supporting
files](#reading-the-plugins-supporting-files) — nothing can answer a prompt there.

For local development:

```bash
# Clone and test locally (changes take effect immediately)
git clone git@github.com:thescubageek/workbench.git
claude --plugin-dir /path/to/workbench/plugin --add-dir /path/to/workbench/plugin
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
/wb:create_tasks docs/plans/...
/wb:implement docs/plans/...
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
- **`/wb:explore_design`** - *(optional)* Air the alternatives before choosing; records the decision in `thoughts/`
- **`/wb:create_tasks`** - Transform design into phased execution plan (HOW)
- **`/wb:implement`** - Implement with TDD via worker agents, main context kept clean *(recommended)*
- **`/wb:implement_inline`** - The same plan, implemented inline on the session model
- **`/wb:validate_execution`** - Validate implementation matches plan
- **`/wb:validate_project`** - Validate project documentation structure
- **`/wb:create_handoff`** - Create session handoff for work continuity
- **`/wb:resume_handoff`** - Resume from handoff document
- **`/wb:resolve_questions`** - Walk through open questions one at a time and record answers
- **`/wb:forge`** - Run a ticket through the full pipeline (research → validate); end-to-end sequencer
- **`/wb:update_status`** - Intelligently sync status across all documentation files
- **`/wb:help`** - Quick reference for all commands

#### Running unattended

`/wb:implement` and `/wb:forge` accept **`--auto`**, which skips the wait at each phase
checkpoint. It removes a wait, not a check: per-task verification, one-task-one-commit, and
every earlier barrier are unchanged.

What `--auto` will **not** do is claim a sign-off nobody gave. At an unattended checkpoint the
three derivable conditions get ticked — phase checkboxes `[x]`, automated verification passing,
counters reconciled — while **"Manual verification confirmed by human" stays `[ ]`** and the
phase is recorded as having closed unattended, naming the manual steps nobody performed. That
unticked box is the point: it is what keeps "ran unattended" and "a person approved this"
distinguishable months later, when the plan is the only witness.

Two gates still stop even under `--auto`, because neither is a wait you can pre-authorise:
`create_design` never writes `status: approved` on its own judgment, and `/wb:update_status`
still presents a plan when a `status:` value would change or move backward. Counter
reconciliation — arithmetic over checkboxes you already control — applies silently either way,
so you never have to remember to run it.

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
- **`daily-digest`** - Morning "catch me up + plan my day" orchestrator across Jira, wb plans, git, and more
- **`clip`** - Runs an instruction, then copies the result to the clipboard (cross-platform) instead of printing it
- **`eli5-clip`** - Summarizes recent work as a warm, plain-language message for a non-technical reader and copies it to the clipboard, tailored to a named recipient

### Hooks

- **SessionStart** - Session orientation, plan position, and the journal/working-tree reconciliation (`hooks/wb-prime.sh`)
- **PreCompact** - Compaction recovery: says the summaries are paraphrase and the plan documents must be re-read
- **PostToolUse** - Lints markdown files after Write/Edit operations

## Plugin Structure

```
workbench/
├── .claude-plugin/
│   └── marketplace.json    # marketplace entry; "source": "./plugin"
├── plugin/                 # everything an installer receives
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── skills/             # workflow stages (/wb:*) and background skills
│   ├── agents/             # specialized subagents
│   ├── hooks/              # event handlers
│   ├── scripts/            # utility scripts (lint)
│   └── docs/reference/     # shipped, runtime-referenced docs
└── docs/                   # maintainer-facing; never shipped
```

**Local development points at `plugin/`, not the repository root:**

```bash
claude --plugin-dir /path/to/workbench/plugin
```

Pointing it at the root does not error — it silently serves the *installed* copy, so
working-tree changes are invisible.

### Reading the plugin's supporting files

Each stage reads its templates and prompts from the plugin directory, which sits outside your
project. That read needs permission, and how you grant it depends on how you run Claude.

**Interactive — you are prompted once.** Approve it and the stage continues; choose the
persistent option and the grant covers every project on the machine. Nothing to configure in
advance. This is the ordinary permission-grant flow, *not* the
`permissions.blockReadsOutsideWorkingDirectories` setting — that setting governs a different
boundary and does not fire on the plugin cache.

**Headless, CI, or `claude -p` — pre-grant it, because nothing can answer a prompt there.**
Under `default` and `acceptEdits` alike the read is denied and the stage stops. Either grant the
path in `permissions.allow`:

```json
{ "permissions": { "allow": ["Read(//Users/<you>/.claude/plugins/cache/**)"] } }
```

or pass the plugin directory as a working directory:

```bash
claude --plugin-dir /path/to/workbench/plugin --add-dir /path/to/workbench/plugin
```

`--add-dir` is the one to use for local development, where the plugin is your working tree
rather than the cache. Both work, and they target different things: `--add-dir` puts the path in
scope, the `allow` rule grants the read directly.

When the read is refused, a stage names the file it could not read and stops, rather than
improvising a document from a template it never saw. That is deliberate — see
`docs/claude-code-skills-guide.md` → House conventions.

## Where status lives

No external tracker. Nothing to install, nothing to initialize.

- **Checkbox state in `tasks.md` is the source of truth.** Flipping `- [ ]` to `- [x]` is the
  act of recording a task done.
- **Frontmatter counters are a derived cache** with exactly one writer, `/wb:update_status`.
  Drift between checkpoints is expected; `status-sync` surfaces it.
- **Git is the durable record** — one task, one commit, task ID in the message.
- **Questions, assumptions and decisions** live in the document that raises them, with local
  IDs (`Q1`, `A1`, `PD1`) and an explicit state.

Continuity across sessions comes from three artifacts with different lifetimes: a per-plan
`journal.md` whose entries **open when work starts** (so an abrupt kill leaves a correct open
entry rather than silence), a committed `.claude/wb/knowledge.md` of durable repository facts,
and handoffs for planned transfers. The session-start hook reports all three, reconciled against
the working tree — the repository is always the authority.

## Core Philosophy

- **Document, Don't Judge**: Research describes what EXISTS, not what should change
- **Explicit Barriers**: Synchronization points prevent rushing ahead
- **Dual Verification**: Automated (tests, CI) + Manual (UX, edge cases)
- **Zero Scope Creep**: Tasks only from plans - no ad-hoc additions, but implement what the task asks for *completely*
- **Status Lives in the Plan**: Checkboxes are truth, counters are a cache with one writer, git is the durable record

## Output discipline (optional opt-in)

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
./plugin/scripts/lint           # Lint changed files
./plugin/scripts/lint --fix     # Auto-fix issues
./plugin/scripts/lint --all     # Lint all markdown files
```

### Testing Changes

```bash
# Run with local plugin (--add-dir lets stages read their own templates)
claude --plugin-dir /path/to/this/repo/plugin --add-dir /path/to/this/repo/plugin

# Reload after changes (inside Claude Code)
/reload-plugins
```

## License

MIT
