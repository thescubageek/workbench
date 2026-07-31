# Scripts

Utility scripts for the project.

## Install

```bash
npm install
```

Required once per clone, before running `test-knowledge-config`. It installs `ajv`, the repo's only
node dependency — a **hard** one, because `.wb-knowledge.json` is the trust anchor of the knowledge
loop and a config that violates its schema must be *rejected*, not merely un-asserted.

`node_modules/` is gitignored and is **never** shipped. A marketplace install has no `node_modules`,
so nothing on the runtime path — the guard hook, capture — may depend on `ajv` or on
`validate-json-schema`. Dev-time only.

`markdownlint-cli` is still expected globally (see `lint` below); it is not managed by `package.json`.

## Available Scripts

### `lint`

Lints markdown files using markdownlint.

```bash
# Lint only changed markdown files (default)
./scripts/lint

# Auto-fix issues in changed files
./scripts/lint --fix

# Lint all markdown files in the project
./scripts/lint --all

# Auto-fix all markdown files
./scripts/lint --all --fix

# Show help
./scripts/lint --help
```

**Features:**

- By default, only lints files that have been changed (git diff)
- Excludes common directories (node_modules, .git, vendor, etc.)
- Uses `.markdownlintrc` for configuration if present
- Provides clear output with file status indicators
- Supports auto-fixing with the `--fix` flag

**Requirements:**

- markdownlint-cli (`npm install -g markdownlint-cli` or `brew install markdownlint-cli`)
- git (for detecting changed files)

### `lint-hook`

Hook script used by Claude Code to automatically lint markdown files after they are created or edited.

```bash
# This script is automatically triggered by Claude Code hooks
# It's configured in the plugin manifest: .claude-plugin/plugin.json (hooks block)
```

**Features:**

- Automatically runs after Write or Edit tools modify markdown files
- Attempts to auto-fix issues with markdownlint
- Shows concise output in Claude Code interface
- Non-blocking (won't stop operations if linting fails)

### `quiet`

Runner-agnostic output backpressure for the TDD/verification loop. Wraps any
command: a green run collapses to a single checkmark plus the command's own
summary line; a red run dumps the full captured log so no failure detail is
lost. The wrapped command's exit code is always passed through unchanged.

```bash
# Green run -> one checkmark + summary line; full output suppressed to a tmpfile
./scripts/quiet pytest -q
./scripts/quiet make test

# Red run -> full output is printed verbatim, original exit code preserved
./scripts/quiet go test ./...
```

**Features:**

- Generalizes the `lint-hook` pattern (run → keep a marker line → suppress the rest) to any runner
- Success path keeps the model inside its working-context "smart zone" (a 200-line green run becomes ~2 lines)
- Failure output is never truncated — full log on any non-zero exit
- Exit-code-faithful, so `verification-before-completion` checks keep working
- Opt-in: invoke it explicitly; nothing is wrapped automatically

**Verify the contract:**

```bash
./scripts/test-quiet
```

### `test-quiet`

Contract tests for `quiet` (success collapse, failure dump, exit-code pass-through). Run after changing `quiet`.

### `knowledge-worktree`

Resolves the knowledge store for this repo and prints its root path on stdout. The store lives on a
long-lived branch declared in `.wb-knowledge.json`; git allows a branch to be checked out in only one
worktree at a time, so this **resolves to an existing checkout wherever it already is** — including a
sibling Conductor workspace — rather than competing for one. Only when nothing holds the branch does it
create a worktree.

```bash
STORE="$(./scripts/knowledge-worktree)" || exit 1
ls "$STORE/entries"
```

**Contract:**

- On success, stdout is the store root path and nothing else
- Every failure is non-zero, legible, and on stderr — **never a silent no-op**, because a capture that
  quietly writes nowhere looks like a working loop while recording nothing
- Repeated runs return the identical path and create nothing extra

**Exit codes:** `2` not in a git repo · `3` no `.wb-knowledge.json` · `4` store branch missing ·
`5` checkout has no store root · `6` worktree creation failed

**Environment:** `WB_KNOWLEDGE_WORKTREE` overrides where a worktree is created;
`WB_KNOWLEDGE_NO_JQ=1` forces the jq-free parsing fallback.

### `test-knowledge-worktree`

Contract tests for `knowledge-worktree`. Builds throwaway git repos under a temp dir — never touches the
real repository or its worktrees. Covers the resolve/create/reuse cases, idempotency, the
branch-held-by-another-worktree case, the jq-free fallback, and every loud-failure path.

### `validate-json-schema`

Validates JSON documents against a JSON Schema using `ajv`. Written for one job — proving that
`.wb-knowledge.json` is *enforced* by `.wb-knowledge.schema.json` rather than merely described by it —
but takes any schema and any number of data files.

```bash
./scripts/validate-json-schema .wb-knowledge.schema.json .wb-knowledge.json
```

**Exit codes:** `0` all valid · `1` at least one document invalid (errors on stderr) · `2` usage error,
unreadable file, or a schema that will not compile · `3` `ajv` not installed — run `npm install`.

Dev-time only; see the install note above.

### `test-knowledge-config`

Contract tests for `.wb-knowledge.json` and `.wb-knowledge.schema.json`, in two layers.

**Structural (`jq`)** — the trust anchor holds: the config declares itself protected, the harness paths
and the files pinning the validator are covered, `knowledge/staging/` is *not* covered (capture must be
able to write there), every declared path actually exists, and — the negative assertions that matter
most — core self-extension has no policy surface anywhere in either file.

**Enforcement (`ajv`, via `validate-json-schema`)** — the schema is executed, not just read. Mutated
copies of the live config are fed to a real validator and each must be rejected: one carrying
`write_policy.core_self_extension`, one with `model_narrated: "auto-promote"`, one whose
`protected_paths` omits itself, and nine more. A **positive control** runs alongside them — relaxing
`tool_verified` to `auto-promote`, the one axis the policy may relax, must still be *accepted* — because
without it every rejection would also pass against a validator that simply refuses everything.

Run it after any edit to either file. If the negative assertions start failing, a bypass has been
reintroduced. Requires `npm install` first.

### `test-knowledge-guard`

Contract tests for `hooks/knowledge-guard.sh`, the three-state `PreToolUse` guard. Feeds payloads to
the script on stdin in throwaway git repos and asserts every row of the behaviour table, plus path
resolution (symlinks, `..`, `/tmp` → `/private/tmp`), the jq-free fallback, output hygiene, and the two
cases the boundary actually rests on:

- **arming cannot be set from anything the agent can write** — an in-repo marker file, a fabricated
  payload field, and `tool_input.content` claiming `interactive` all change nothing
- **interactive is asserted, never inferred** — `permission_mode` may *veto* an interactive claim but
  can never establish one, because a headless run reports `"default"` exactly like an interactive one

This tests the script. It cannot test whether Claude Code ever calls it — see the probe below.

### `probe-knowledge-guard`

**Opt-in; spawns real `claude -p` sessions and costs model calls.** Not part of `npm test`.

Tests what the contract test structurally cannot: registration and enforcement. Hook configuration is
read once at session start, so an in-session settings edit registers nothing — only a child session
with `--settings` exercises the real path. Three runs, each an A/B against a control file the guard
ignores:

| Run | Repo | Armed | Expected |
| --- | --- | --- | --- |
| A | configured | `full-auto` | control written, sentinel **refused** |
| B | configured | no | control written, sentinel **written** |
| C | unconfigured | `full-auto` | control written, sentinel **written** |

B is what makes A mean anything — a guard that denied everything would look identical without it. C is
the regression that matters most to users: a marketplace install must never deny writes in a repo that
has not opted in.

```bash
./scripts/probe-knowledge-guard              # uses haiku
WB_PROBE_MODEL=sonnet ./scripts/probe-knowledge-guard
```

Not covered: the interactive `ask` row, which cannot be observed headlessly and needs a human at a
terminal.

## The knowledge guard

`hooks/knowledge-guard.sh` is registered on `PreToolUse` for `Write|Edit|MultiEdit|NotebookEdit` in
`.claude-plugin/plugin.json`. It is inert unless the repo declares `.wb-knowledge.json` **and** the
session was armed:

```bash
WB_SELF_EXTENSION=interactive claude          # armed, human present  -> protected writes ask
WB_SELF_EXTENSION=full-auto  claude -p ...    # armed, unattended     -> protected writes deny
claude                                        # not armed             -> inert
./hooks/knowledge-guard.sh --selfcheck        # is enforcement actually available here?
```

Arming is an environment variable because that is the one channel the agent cannot reach: tool-layer
processes are children of the session and cannot mutate the environment the hook inherits. Verified by
execution — an `export WB_SELF_EXTENSION=full-auto` run by the agent's own Bash tool did not change
what the hook subsequently saw.

**Known hole, stated rather than papered over:** a shell redirect through the Bash tool
(`printf x > commands/help.md`) produces no `PreToolUse` Write event and is not seen. The designed
answer is the CI / CODEOWNERS layer, which must exist before the first unattended run.

## Configuration

The project uses `.markdownlintrc` for markdownlint configuration. Current settings:

- Line length checking disabled (for long code blocks)
- Inline HTML allowed
- Emphasis as heading allowed (for "think deeply" directives)
- Fenced code blocks without language specification allowed

## Claude Code Hooks

The project has automatic markdown linting configured via Claude Code hooks in the plugin manifest `.claude-plugin/plugin.json` (`hooks` block):

- **PostToolUse hooks** for Write and Edit tools
- Automatically runs `${CLAUDE_PLUGIN_ROOT}/scripts/lint-hook` after any markdown file is created or modified
- Attempts to auto-fix common markdown issues
- Shows brief status messages in the Claude Code interface

To disable automatic linting, remove or comment out the `hooks` section in `.claude-plugin/plugin.json`.
