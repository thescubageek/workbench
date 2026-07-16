# Claude Code Skills, Commands & Subagents - Complete Guide

This guide documents how Claude Code extension mechanisms work as of mid-2026, based on the official documentation. It replaces the 2025 version of this guide, which described skills and slash commands as separate systems — they have since been unified.

## Table of Contents

- [The 2026 Unification: Skills Are Commands](#the-2026-unification-skills-are-commands)
- [File Structure and Locations](#file-structure-and-locations)
- [SKILL.md Format](#skillmd-format)
- [Invocation Control](#invocation-control)
- [Dynamic Content: Arguments and Shell Preprocessing](#dynamic-content-arguments-and-shell-preprocessing)
- [Running Skills in Subagents (context: fork)](#running-skills-in-subagents-context-fork)
- [Subagents](#subagents)
- [Hooks](#hooks)
- [Plugin Manifest Notes](#plugin-manifest-notes)
- [Best Practices](#best-practices)
- [What This Means for This Repository](#what-this-means-for-this-repository)
- [Changes from the 2025 Guide](#changes-from-the-2025-guide)

---

## The 2026 Unification: Skills Are Commands

Custom slash commands and skills are now the same mechanism. A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and behave identically. Skills are the canonical form; `commands/` directories still work as a legacy path.

Every skill is potentially BOTH:

- **User-invocable**: type `/skill-name args` to run it
- **Model-invocable**: Claude can invoke it automatically when the description matches the context

Two frontmatter flags control which side is enabled (see [Invocation Control](#invocation-control)).

The old distinction ("commands are explicit, skills are automatic") is now a *configuration choice on a single mechanism*, not two different systems.

**Built-in commands vs bundled skills**: Fixed-logic commands (`/help`, `/compact`, `/model`, `/permissions`) are coded into the CLI and cannot be overridden. Many former "commands" (`/code-review`, `/loop`, `/run`, `/verify`, `/simplify`, `/batch`) are now bundled *skills* — prompt-based and disableable via the `disableBundledSkills` setting.

---

## File Structure and Locations

| Location | Scope | Resulting name |
| ---------- | ------- | ---------------- |
| Managed settings | Organization-wide (highest priority) | `/name` |
| `~/.claude/skills/<name>/SKILL.md` | Personal, all projects | `/name` |
| `.claude/skills/<name>/SKILL.md` | Project (shared via git) | `/name` |
| `<plugin>/skills/<name>/SKILL.md` | Plugin | `/plugin-name:skill-name` |
| `.claude/commands/<name>.md` | Project (legacy form) | `/name` |
| `<plugin>/commands/<name>.md` | Plugin (legacy form) | `/plugin-name:name` |

Notes:

- Subdirectories under `skills/` are scanned recursively.
- Plugin skills get the plugin namespace automatically (this is how `/wb:create_project` gets its prefix — via the plugin name, whether the file lives in `commands/` or `skills/`).
- A skill is a directory with a required `SKILL.md` plus optional supporting files (reference docs, templates, scripts). Keep `SKILL.md` under ~500 lines and link out to supporting files, which load on demand.
- `/reload-skills` re-scans skill directories without restarting the session.

```
.claude/skills/my-skill/
├── SKILL.md              # Required — overview & navigation
├── reference.md          # Loaded on demand when linked from SKILL.md
├── examples.md           # Loaded on demand
└── scripts/
    └── helper.py         # Executed, not loaded into context
```

---

## SKILL.md Format

YAML frontmatter followed by markdown content. Current field reference:

```yaml
---
name: my-skill                          # Optional. Display name (defaults to directory name)
description: What it does and when     # Recommended. Drives automatic invocation.
when_to_use: Extra trigger context     # Optional. Appended to description.
argument-hint: "[issue-number]"        # Optional. Shown in / autocomplete.
arguments: [issue, branch]             # Optional. Named positional args, used as $issue, $branch.
disable-model-invocation: true         # Optional. User-only — Claude cannot auto-invoke.
user-invocable: false                  # Optional. Claude-only — hidden from / menu.
allowed-tools: Read, Grep, Bash        # Optional. Tool allowlist while skill is active.
disallowed-tools: Write, Edit          # Optional. Tool denylist while skill is active.
model: sonnet                          # Optional. haiku|sonnet|opus|fable|<full-id>|inherit
effort: high                           # Optional. low|medium|high|xhigh|max
context: fork                          # Optional. Run in an isolated subagent.
agent: Explore                         # Optional. Subagent type when context: fork.
hooks: {...}                           # Optional. Lifecycle hooks scoped to this skill.
paths: "src/**/*.ts"                   # Optional. Load skill only when matching files are involved.
shell: bash                            # Optional. Shell for !`command` blocks: bash|powershell
---
```

Field details:

- **`name`**: lowercase letters, numbers, hyphens; max 64 chars. Specific beats generic (`tdd-workflow`, not `test`).
- **`description`**: max 1024 chars. This is what Claude matches against to decide whether to invoke the skill, so it must contain trigger terms. Pattern: *[What it does] + [When to use] + [Trigger terms]*. Not loaded into context at all when `disable-model-invocation: true`.
- **`allowed-tools` / `disallowed-tools`**: space/comma-separated or YAML list. Claude Code only.
- **`model` / `effort`**: override the session model or reasoning effort while the skill runs.

### Skill content lifecycle

When invoked, skill content enters the conversation as a single message and stays for the rest of the session. Auto-compaction preserves recently invoked skills within a ~25K token budget (first ~5K tokens of each); older skill content can drop when many skills are invoked after it.

### Skill visibility overrides

Users can control skill visibility per-skill from `.claude/settings.json` without editing the skill files:

```json
{
  "skillOverrides": {
    "noisy-skill": "name-only",
    "deploy": "off"
  }
}
```

Values: `"on"` (default), `"name-only"` (no description in context), `"user-invocable-only"` (hidden from Claude), `"off"` (hidden entirely).

---

## Invocation Control

The two flags produce three useful configurations:

| Configuration | Frontmatter | User types `/name` | Claude auto-invokes | Description in context |
| --------------- | ------------- | -------------------- | --------------------- | ------------------------ |
| Default | (neither flag) | ✅ | ✅ | ✅ |
| User-only | `disable-model-invocation: true` | ✅ | ❌ | ❌ |
| Claude-only | `user-invocable: false` | ❌ (hidden) | ✅ | ✅ |

Guidance:

- **User-only** is right for explicit workflow steps with side effects or ordering requirements — the user controls timing, and the skill costs zero context until invoked. This fits the `/wb:create_*` sequential workflow.
- **Claude-only** is right for background discipline/knowledge capabilities (TDD enforcement, verification gates) where the user shouldn't need to remember to invoke anything.
- **Default** fits utilities that are useful both ways.

---

## Dynamic Content: Arguments and Shell Preprocessing

### String substitutions

| Variable | Meaning |
| ---------- | --------- |
| `$ARGUMENTS` | All arguments as typed after `/name` |
| `$0`, `$1`, `$2` … | Positional arguments |
| `$ARGUMENTS[N]` | Indexed argument |
| `$name` | Named argument declared in `arguments:` |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the skill's directory |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_EFFORT}` | Current effort level |

### Shell preprocessing

Commands embedded in skill content run **before** Claude sees the content; their output replaces the placeholder:

```markdown
Current diff:
!`git diff HEAD`
```

Multi-line blocks use a ```` ```! ```` fence. This is preprocessing, not something Claude executes — useful for injecting live state (git status, bd ready output) into a workflow prompt. Can be disabled via the `disableSkillShellExecution` setting.

---

## Running Skills in Subagents (context: fork)

A skill can run in an isolated subagent instead of inline:

```yaml
---
name: research-sweep
description: Deep codebase research
context: fork
agent: Explore
---
Research $ARGUMENTS thoroughly...
```

- The skill body becomes the subagent's task prompt; results are summarized back to the main conversation.
- `agent:` selects the subagent type (default `general-purpose`). Built-in `Explore` and `Plan` agents are read-only and skip CLAUDE.md/git-status loading, making them fast and cheap.
- Use this for exploration-heavy work that would otherwise flood the main context.

---

## Subagents

Subagents (`agents/*.md` in project, `~/.claude/agents/`, or plugins) are specialized assistants with isolated context windows, custom system prompts, and their own tool/permission configuration. Discovery is recursive; plugin agents are namespaced (`wb:codebase-locator`).

### Current frontmatter reference

```yaml
---
name: code-reviewer                     # Required. lowercase-hyphens.
description: When to delegate to me    # Required. Drives automatic delegation.
tools: Read, Glob, Grep, Bash           # Optional. Allowlist; inherits all if omitted.
disallowedTools: Write, Edit            # Optional. Denylist (applied before allowlist).
model: sonnet                           # Optional. haiku|sonnet|opus|fable|<full-id>|inherit (default: inherit)
permissionMode: default                 # Optional. default|acceptEdits|auto|dontAsk|bypassPermissions|plan
maxTurns: 10                            # Optional. Hard stop after N agentic turns.
skills: [tdd-discipline]                # Optional. Preload full skill content at startup.
memory: project                         # Optional. Persistent memory: user|project|local
background: true                        # Optional. Always run as a background task.
effort: high                            # Optional. low|medium|high|xhigh|max
isolation: worktree                     # Optional. Run in an isolated git worktree.
hooks: {...}                            # Optional. Hooks active only while this agent runs.
mcpServers: [...]                       # Optional. MCP servers scoped to this agent.
color: blue                             # Optional. Display color.
---

System prompt for the subagent goes here.
```

Capabilities worth knowing:

- **`skills` preload**: injects full skill content into the subagent at startup — give a worker agent domain knowledge (e.g., TDD rules) without relying on discovery. Cannot preload `disable-model-invocation` skills.
- **`memory`**: gives the agent a persistent directory across sessions (`user` → `~/.claude/agent-memory/<name>/`, `project` → `.claude/agent-memory/<name>/`, `local` → not version-controlled). The first ~200 lines of its `MEMORY.md` auto-load into its prompt.
- **`isolation: worktree`**: the agent works in its own git worktree — safe parallel file mutation.
- **`maxTurns`** and **`permissionMode`**: bound runaway agents and control prompting. A parent session's `bypassPermissions`/`acceptEdits` takes precedence.
- **Invocation**: natural language ("use the code-reviewer…"), guaranteed via `@agent-name` mention, or session-wide via `claude --agent name`.
- **Model selection priority**: `CLAUDE_CODE_SUBAGENT_MODEL` env var → per-invocation model parameter → agent frontmatter `model` → inherit from main conversation.
- Subagents cannot spawn other subagents, enter plan mode, or ask the user questions.

### Built-in subagents

| Name | Model | Tools | Notes |
| ------ | ------- | ------- | ------- |
| `Explore` | Haiku | Read-only | Fast/cheap search; skips CLAUDE.md |
| `Plan` | Inherits | Read-only | Research for plan mode; skips CLAUDE.md |
| `general-purpose` | Inherits | All | Default for complex multi-step tasks |

---

## Hooks

Hook events have expanded well beyond the original set. The full inventory (~31 events) includes, by category:

- **Session**: `SessionStart`, `SessionEnd`, `Setup`
- **Per-turn**: `UserPromptSubmit`, `Stop`, `StopFailure`
- **Tools**: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`
- **Agents/tasks**: `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`
- **Context**: `PreCompact`, `PostCompact`
- **Files/config**: `FileChanged`, `ConfigChange`, `CwdChanged`, `WorktreeCreate`, `WorktreeRemove`
- **Display**: `Notification`, `MessageDisplay`

Hook output supports `continue`, `systemMessage`, `suppressOutput`, and event-specific `hookSpecificOutput` (e.g., `permissionDecision: allow|deny|ask` for PreToolUse, `additionalContext` for several events, `initialUserMessage` for SessionStart). Exit code 2 is a blocking error whose stderr is shown to Claude.

Hooks can now also live in **skill frontmatter** (active while the skill runs) and **agent frontmatter** (active while the agent runs), not just settings and plugin manifests. Hook types beyond `command` exist: `http`, `mcp_tool`, `prompt`, and `agent`.

Events especially relevant to this repo: `SessionEnd`/`Stop` (deterministic `bd sync` reminders instead of skill-based ones), `PreCompact`/`PostCompact` (sync/restore beads state at context boundaries), `SubagentStop` (verify worker output automatically).

---

## Plugin Manifest Notes

Additions to `plugin.json` since this plugin was authored:

- `displayName` — human-readable name shown in UIs
- `defaultEnabled: false` — ship disabled, users opt in
- `dependencies` — other plugins, with optional semver constraints
- `userConfig` — prompt the user for values at enable time, substituted as `${user_config.KEY}`
- `${CLAUDE_PLUGIN_DATA}` — persistent per-plugin state directory that **survives version updates** (unlike the version-keyed cache)
- Hooks may be inline in `plugin.json` (as this plugin does) or in `hooks/hooks.json`

Versioning behavior is unchanged and matches CLAUDE.md: the cache is keyed by version; updates require a version bump in both `plugin.json` and `marketplace.json` plus `claude plugin update` from the shell. If `version` is omitted, the git commit SHA becomes the version (every commit is an update). Old cached versions are cleaned up after ~7 days.

Debugging tip: `claude --safe-mode` starts without any plugins, skills, hooks, or MCP servers.

---

## Best Practices

### Description writing (unchanged — still the critical factor)

The description determines automatic invocation quality:

```
[What it does] + [When to use] + [Trigger terms]
```

```yaml
description: Implements Test-Driven Development (TDD) workflow following Red-Green-Refactor cycle. Use when user wants to implement features test-first, mentions TDD, or asks to write tests before code.
```

Avoid vague descriptions ("Helps with testing"), and remember: with `disable-model-invocation: true` the description is never loaded, so optimize it for the human browsing the `/` menu instead.

### Choosing a mechanism

```
Fixed CLI behavior?                  → built-in command (not customizable)
User must control timing/ordering?   → skill with disable-model-invocation: true
Background discipline/knowledge?     → skill with user-invocable: false
Exploration that floods context?     → skill with context: fork (agent: Explore)
Custom system prompt / tool sandbox /
persistent memory / parallel work?   → subagent
Deterministic automation on events?  → hook
```

- Prefer skills for utilities and reference material; subagents for large isolated tasks.
- Preload skills into subagents (`skills:` field) rather than duplicating instructions in agent prompts.
- Use `allowed-tools` (skills) / `tools` (agents) for least privilege in anything shared.
- Use hooks — not skill descriptions — when something must *always* happen (skills activate probabilistically; hooks are deterministic).

---

## What This Means for This Repository

The wb plugin's `commands/` files continue to work unchanged — plugin commands and plugin skills both resolve to `/wb:*`. Current assessment:

1. **Keep the explicit `/wb:*` workflow**, but the old rationale ("commands are user-invoked, skills are not") is obsolete. The modern equivalent of that intent is `disable-model-invocation: true`, which also keeps all 14 command descriptions out of baseline context.
2. **The wb skills (tdd-discipline, verification-before-completion, status-sync, etc.) are the "Claude-only" pattern** — they could declare `user-invocable: false` explicitly.
3. **Candidate upgrades** (not yet applied):
   - `context: fork` for research-heavy commands (`create_research`, `create_product_research`)
   - `skills: [tdd-discipline]` preload + `maxTurns` on worker agents used by `implement_coordinated`
   - `memory: project` on research agents to accumulate codebase knowledge
   - `SessionEnd`/`PreCompact` hooks for deterministic `bd sync` instead of relying on the status-sync skill activating
   - `displayName` in plugin.json

---

## Changes from the 2025 Guide

For readers who knew the previous version of this document, these statements from it are **no longer true**:

| 2025 guide said | Now |
| ----------------- | ----- |
| Skills cannot be explicitly invoked (no `/skill-name` syntax) | Skills ARE invocable via `/skill-name` unless `user-invocable: false` |
| Skills and slash commands are separate systems | Unified — same mechanism, `skills/` is canonical, `commands/` is legacy |
| Skills use a flat structure, no namespaces | Recursive scanning; plugin skills get `/plugin:name` namespacing |
| Frontmatter is `name`, `description`, `allowed-tools` only | Many more fields: invocation flags, `model`, `effort`, `context: fork`, `arguments`, `paths`, `hooks`, `shell` |
| Commands are the only way to get explicit user invocation | Any skill is user-invocable by default; `disable-model-invocation` makes it user-*only* |
| Subagents: `name`, `description`, `tools`, `model` | Added `memory`, `skills` preload, `maxTurns`, `permissionMode`, `isolation`, `background`, `hooks`, `mcpServers`, `disallowedTools`, `effort` |

---

## Further Resources

- Skills: <https://code.claude.com/docs/en/skills>
- Slash commands: <https://code.claude.com/docs/en/commands>
- Subagents: <https://code.claude.com/docs/en/sub-agents>
- Hooks: <https://code.claude.com/docs/en/hooks>
- Plugins: <https://code.claude.com/docs/en/plugins> and <https://code.claude.com/docs/en/plugins-reference>

---

*Last Updated: 2026-06-09*
*Based on: Claude Code official documentation (code.claude.com/docs) and changelog research*
