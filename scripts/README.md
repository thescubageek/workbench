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
