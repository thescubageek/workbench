# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Claude Code plugin (`wb`) providing structured software development workflows: project planning, research, design, execution, and validation with TDD enforcement. Status lives in the plan documents; there is no external tracker.

## Output Discipline

When running `/wb:*` commands, keep narration minimal — the artifact is the deliverable, not the chat:

- Act on barriers and checkpoints **silently** — do not announce "BARRIER 2 satisfied", "all agents returned", or restate the plan between steps.
- After writing a document, **do not reproduce its contents back into the chat**. Emit a single one-line completion summary (e.g. `✅ research.md — <topic>; N findings. Next: /wb:create_design`).
- Surface only what the user must act on: blockers, decisions awaiting their input, and errors. Everything else lives in the artifact.

This is the global reinforcement of each command's inline output-discipline directive. (End users: see README "Output discipline" to opt this rule into your own `CLAUDE.md`.)

## Repository Structure (Plugin Layout)

**Everything an installer receives lives under `plugin/`.** The root holds the marketplace
entry and maintainer material that is never shipped.

- `.claude-plugin/marketplace.json` - marketplace entry; `"source": "./plugin"`
- `plugin/.claude-plugin/plugin.json` - the plugin manifest
- `plugin/skills/` - workflow stages (`/wb:*`) and background skills
- `plugin/agents/` - specialized subagent definitions
- `plugin/hooks/` - event handlers (SessionStart, PreCompact, PostToolUse)
- `plugin/scripts/` - utility scripts (lint, lint-hook)
- `plugin/docs/reference/` - shipped, runtime-referenced docs a skill may link into
- `docs/` - **maintainer-facing; never shipped.** Not a runtime rules source
- `.claude/` - local development config, plus `wb/knowledge.md` (committed)

**Where rules may live** (this is a rule, not a preference): a shipped skill may link only into
`plugin/docs/reference/`. Nothing under root `docs/` is read at runtime. Anything kept as
history is marked non-normative at its top, so it cannot be read as current guidance.

## Development Tools

### Markdown Linting

```bash
# Lint changed markdown files
./plugin/scripts/lint

# Auto-fix markdown issues
./plugin/scripts/lint --fix

# Lint specific files
./plugin/scripts/lint file1.md file2.md

# Lint all markdown files
./plugin/scripts/lint --all
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
4. Users run `claude plugin update wb@thescubageek-workbench` from the **shell** (not a slash command — it's a CLI command, run with `!` prefix or in a separate terminal)
5. After update, restart Claude (or `/reload-plugins`) to apply

**What does NOT work alone**:

- `/reload-plugins` — only re-reads the existing cache, doesn't pull updates
- Pushing to git — the marketplace clone at `~/.claude/plugins/marketplaces/<name>/` doesn't auto-pull
- Bumping version without `claude plugin update` — the cache stays at the old version

For local dev (`--plugin-dir` install), changes take effect immediately without a version bump.

## Command Workflow

The commands follow a strict sequential workflow:

```
/wb:create_project → /wb:create_research → [/wb:explore_design] → /wb:create_design → /wb:create_tasks → /wb:implement → /wb:validate_execution
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
6. **Status Lives in the Plan**: checkbox state in `tasks.md` is the source of truth
   - Flipping `- [ ]` → `- [x]` **is** the act of recording a task done
   - Frontmatter counters are a derived cache with exactly one writer, `/wb:update_status`
   - Git is the durable record — one task, one commit, task ID in the message
   - No TaskCreate, TaskUpdate, or TodoWrite: a parallel list only goes stale beside the checkboxes

### Task Tracking

**The plan documents are the record.** There is no external tracker to install, initialize, or
recover.

| Surface | Holds | Written by |
| ------- | ----- | ---------- |
| Checkboxes in `tasks.md` | task and phase status | whoever finishes the task |
| Frontmatter counters | a derived cache of the counts | `/wb:update_status`, and nothing else |
| Git | the durable audit trail | one task, one commit |
| `journal.md` | what a session was attempting | opened at start of work, closed at completion |
| `.claude/wb/knowledge.md` | durable repository facts | curated, committed, each entry dated with a verification hint |

Counter drift between checkpoints is **expected, not an error** — `status-sync` surfaces it and
`/wb:update_status` reconciles it. The checkboxes are always what's right.

**Task IDs are a contract**: every task line carries a bold ID matching
`[A-Z0-9-]*[0-9][A-Z0-9-]*` — at least one digit. Every counter identifies task lines by that
shape, so an ID without a digit makes the task invisible to counting, silently.

### Command Structure Patterns

Mark each real synchronization point **once**, and state the reason in the marker. A marker
whose text only restates the rule ("full context required") tells a session nothing it did not
already know; the reason is what makes it hold when the session is under pressure to proceed.

```markdown
⛔ BARRIER 1: full context read — analysis on partial context produces placeholders
⛔ BARRIER 2: every spawned agent has returned — synthesis on a partial set misses what the
   missing report would have changed
⛔ BARRIER 3: no placeholder values — a placeholder that ships becomes a task nobody can
   execute
⛔ CHECKPOINT: human verification between phases — the next phase builds on what a human has
   accepted
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

## Model & effort at gates

The `model-help` skill is the plugin's single authority on **which Claude model + reasoning-effort** to run at. Its **gate mode** carries per-phase baselines and the switch-cost rule; `forge`, `resume_handoff`, and the `create_*` / `implement` / `implement_inline` / `validate_execution` stages delegate to it rather than re-deriving the rubric. Keep model IDs and effort levels consistent with `plugin/skills/model-help/SKILL.md` (and the `daily-digest` rubric) as they change.

The policy these commands enforce:

1. **Two levers, different costs.** Sub-agent model/effort is **free** (fresh context per agent) — push cheap, parallelizable work there. Switching the **main-session** model reloads the whole conversation (tokens + latency) — advise it only when it pays for that tax.
2. **Advise, never auto-switch.** Commands surface a one-line advisory and the concrete `/model` action; the user decides. Model advisories are best-effort and **non-blocking** — they must never delay or gate the actual work.
3. **The quality floor is inviolable.** Never advise below the tier a phase needs at its hardest sub-problem. Savings come from not over-powering cheap phases and from sub-agent tiering — never from under-powering a hard one.
4. **Minimize switches.** Cluster same-tier phases; a whole forge should cost ~1–2 main-model switches, not one per phase.

## Working with Commands

When creating or modifying commands:

1. Follow existing command patterns
2. Mark each real synchronization point once — `⛔ BARRIER` for "do not proceed until X",
   `⛔ CHECKPOINT` for human confirmation — and state the reason in a plain sentence
3. At decision points, say what the decision is **about**; do not instruct the model how hard
   to think. Thinking depth is the session's effort setting, not prompt text
4. Maintain the documentarian philosophy for research
5. Separate automated from manual verification
6. Read files fully before processing
7. Spawn independent agents in parallel; synthesize only after all have returned

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
- Run `./plugin/scripts/lint` before committing markdown files
- Keep the repository organized by category

### Branch naming

`plugin/docs/reference/branch-naming.md` is the shipped, runtime-read authority. `create_project`, `jira-context`, `forge` and `implement` each link into it rather than restating it; keep it as the one place the rule changes.

The convention is `<scope>/<snake_case_description>`, where `<scope>` is a **ticket key** if one is known (`TB-2421/combobox_aria_pattern`), otherwise a **release version** if the work targets one (`wb-2.1.0/branch_naming_policy`), otherwise nothing (bare description, no slash). A ticket outranks a version; they are never concatenated.

Two things the rule exists to prevent, both observed:

- **A name derived from the user's last message.** A Conductor auto-rename produced `commit-and-push` from the instruction that triggered it. The description names the *change*, never the prompt.
- **Waiting for the commit to name the branch.** The name is applied at the first moment it is knowable — ticket resolved, plan directory created, version decided — not when code is ready to land.

Rename **in place** (`git branch -m`), never by cutting a second branch. Branch create/rename is a git state change: **confirm with the user before running it**, and it is non-blocking — if declined, proceed on the current branch. A branch that has already been pushed is a separate decision: the local rename leaves the remote branch and any open PR behind, so surface that and let the user choose. Never delete a remote branch or force-push without explicit go-ahead.

## Session Conventions

### Session Protocol

`CLAUDE.md` is the single root for session protocol. Before ending a work session:

1. **File follow-ups** — anything discovered but out of scope becomes an issue or a line in
   the plan's Implementation Notes. An intention that exists only in the transcript is lost
   when the session ends.
2. **Run the quality gates** if anything changed — tests, linters, build.
3. **Reconcile status**: flip every finished task's checkbox, then run `/wb:update_status` so
   the counters follow.
4. **Commit, and confirm the push with the user.** Work that ends in the working tree is
   stranded on one machine. Pushing is an outward-facing state change, so it is confirmed
   rather than assumed — do not claim work is complete on the user's behalf, and do not treat
   an unpushed branch as a failure state that licenses pushing without asking.
5. **Clean up** — clear stashes, prune stale remote branches.
6. **Hand off** — leave enough context for the next session to resume without you
   (`/wb:create_handoff`).

### Integration with wb Stages

The workbench stages (`/wb:*`) read and write status directly in the plan documents. See [docs/commands-reference.md](docs/commands-reference.md) for details.
