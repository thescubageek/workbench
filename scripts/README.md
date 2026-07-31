# Scripts

Utility scripts for the project.

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

### `test-knowledge-config`

Contract tests for `.wb-knowledge.json` and `.wb-knowledge.schema.json`. Asserts the trust anchor holds:
the config declares itself protected, the harness paths are covered, `knowledge/staging/` is *not*
covered (capture must be able to write there), every declared path actually exists, and — the negative
assertions that matter most — core self-extension has no policy surface anywhere in either file.

Run it after any edit to either file. If the negative assertions start failing, a bypass has been
reintroduced.

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
