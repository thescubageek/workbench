# Batch 0 gate — spawn names, models, and effort

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../../../plugin/docs/reference/technical-english.md) and apply it.

**Run**: 2026-10-23 (UTC), Claude Code 2.1.306, at commit `d9ff6a4`. The cwd was `/tmp/batch0probe`
(`/private/tmp/batch0probe`), an empty git repository.
**Result**: PASS. Every agent resolved by its `wb:` name and ran at the model and effort of the
design's Data Model table. The bare name was rejected.
**Cost**: $0.27 (`total_cost_usd` of the session).

## Mechanical checks

`checks/prompt-checks.sh spawn-names prose-spawns spawn-models agent-tiers roster haiku-effort-rule`
printed 0 for all six, and every check PASS.

## Probe

```bash
env -u CLAUDE_CODE_PLUGIN_DIRS claude -p --plugin-dir /Users/scraig/conductor/workspaces/workbench/douala-v1/plugin \
  --model sonnet --effort low --permission-mode acceptEdits --max-budget-usd 0.50 \
  --output-format stream-json --verbose "<prompt>"
```

- The prompt spawned the 7 `wb:` agents in one message, each with a one-word task and no `model`
  or `effort`. `wb:task-worker` also got `model: "sonnet"`, because its agent file sets no model.
  An eighth spawn used the bare name `codebase-locator` as a negative control.
- The main session ran at `low`, which no agent file sets. So an agent that ran at its own level
  read it from its agent file, not from the session.
- The `init` event listed one `wb` plugin: `/Users/scraig/conductor/workspaces/workbench/douala-v1/plugin`,
  `wb@inline`, version 3.0.0.
- Model: the `model` field of the assistant messages in
  `~/.claude/projects/-private-tmp-batch0probe/d13af613-3fdd-42a7-bc7a-5e0f3a61d03d/subagents/agent-*.jsonl`.
  Effort: `"output_config":{"effort":…}` in the same files.

| Agent | Spawn `model` | Model that ran | Effort that ran | Expected |
| ----- | ------------- | -------------- | --------------- | -------- |
| `wb:codebase-locator` | none | `claude-haiku-5-5` | `medium` | haiku, `medium` |
| `wb:pattern-finder` | none | `claude-haiku-5-5` | `medium` | haiku, `medium` |
| `wb:codebase-analyzer` | none | `claude-sonnet-5-5` | `medium` | sonnet, `medium` |
| `wb:product-behavior-analyzer` | none | `claude-sonnet-5-5` | `medium` | sonnet, `medium` |
| `wb:research-validator` | none | `claude-sonnet-5-5` | `high` | sonnet, `high` |
| `wb:task-verifier` | none | `claude-sonnet-5-5` | `high` | sonnet, `high` |
| `wb:task-worker` | `sonnet` | `claude-sonnet-5-5` | `medium` | sonnet, `medium` |
| `codebase-locator` (bare) | — | — | — | rejected |

The bare name returned this error, verbatim:

```text
Agent type 'codebase-locator' not found. Available agents: claude, Explore, general-purpose, Plan, statusline-setup, wb:codebase-analyzer, wb:codebase-locator, wb:pattern-finder, wb:product-behavior-analyzer, wb:research-validator, wb:task-verifier, wb:task-worker
```

## What this validates

- Design assumption A5 (a spawn with no `model` runs the agent file's model) holds for all 6
  agents that set a model.
- The headless probe exercises the working-tree plugin when it runs under
  `env -u CLAUDE_CODE_PLUGIN_DIRS`.

## Limits

- The probe shows that each spawn resolves and runs at its tier. It does not show that a stage
  copies its spawn block correctly. The Phase 2 harness run exercises that.
- `stream.jsonl` in this directory is the session's stream output.
