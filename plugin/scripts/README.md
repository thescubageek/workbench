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
- Excludes `vendor/`, `node_modules/`, `.git/`, `.context/`, `tmp/`, `.next/`, `dist/` and
  `build/` **at any depth**, on every route — including explicitly named file arguments
- Honours `.wblintignore` and `.markdownlintignore` at the repository root
- Does **not** honour `.gitignore`: wb plan directories under `docs/plans/` are gitignored
  until promoted, and are exactly what the hook exists to lint
- Uses `.markdownlintrc` for configuration if present; otherwise a default config written to
  a private temp dir and removed on exit
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

- Runs after Write, Edit and Bash tool calls that touch markdown
- **Write / Edit auto-fix.** `tool_input.file_path` names the file the tool just wrote, so
  the path is unambiguous and rewriting it is safe
- **Bash reports only.** A Bash command's text cannot distinguish a write from a read, and a
  `PostToolUse` hook has no pre-state to compare against. `find -mmin -1` answers "was this
  modified recently?", never "did *this command* modify it?" — and those diverge exactly when
  an earlier step wrote a batch of markdown and a later command reads one of them
- Shares `wb_lint_ignored()` with `lint`, so ignored paths are skipped before `lint` is spawned
- Shows concise output in Claude Code interface
- Non-blocking (won't stop operations if linting fails)

**Environment:**

| Variable | Effect |
| -------- | ------ |
| `WB_LINT_HOOK=0` | Hook is a no-op. One-line escape hatch, no manifest edit needed |
| `WB_LINT_FIX_ON_BASH=1` | Opt back into auto-fixing on the Bash route, accepting that a read-only command can then silently rewrite content this session did not author |

**Verify the contract:**

```bash
./scripts/test-lint
```

### `lint-common.sh`

Sourced by `lint` and `lint-hook`; never executed directly. Defines `wb_lint_ignored()` — the
single answer to "may lint touch this path?" — so the two agree and neither can acquire a
private exclusion list.

### `test-lint`

Contract tests for `lint` and `lint-hook`: read-only Bash does not mutate, exclusions apply on
the explicit-path route at any depth, ignore files are honoured, a gitignored path is still
linted, a path in both `.gitignore` and `.wblintignore` is skipped, Write/Edit still fixes, and
both env vars do what they say. Run after changing either
script.

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

### `wbte-dictionary`

Makes a private copy of the ASD-STE100 approved-word dictionary from your own copy of the Issue
9 PDF. The `/wb:wbte-dictionary` skill runs it. The plugin works without the copy.

```bash
./scripts/wbte-dictionary ~/Downloads/ASD-STE100_ISSUE9.pdf
```

**Features:**

- Writes `~/.claude/wb/wbte-dictionary.tsv` with the columns word, part of speech, status, and
  alternatives. The alternatives are best-effort.
- Refuses to write inside a git work tree, also when only `~/.claude` is one (exit 3). ASD does
  not permit redistribution, so the copy stays out of every repository.
- Uses `pdftotext -layout` if present, otherwise python3 with `pypdf`. If neither is present, it
  says what to install and exits 2.

### `test-wbte-dictionary`

Contract tests for `wbte-dictionary`, with invented words only. They cover the expected rows,
the missing-tool message, output under `$HOME` only, and both git work-tree refusals. Run after
changing `wbte-dictionary`.

### `test-prime`

Contract tests for `hooks/wb-prime.sh`. They cover the WBTE rule card on each SessionStart
source, with 0, 1 and 2 active plans and with `.claude/wb/PRIME.md`. They also cover no card on
PreCompact, `WB_TECH_ENGLISH=0`, `--export`, exit 0, no file changes, and the 5-second limit
with 200 plans. The card has a limit of 150 words. Run after changing `wb-prime.sh`.

## Configuration

The project uses `.markdownlintrc` for markdownlint configuration. Current settings:

- Line length checking disabled (for long code blocks)
- Inline HTML allowed
- Emphasis as heading allowed (bold lines used as step directives, e.g. `**Decide WHAT to build**`)
- Fenced code blocks without language specification allowed

## Claude Code Hooks

The project has automatic markdown linting configured via Claude Code hooks in the plugin manifest `.claude-plugin/plugin.json` (`hooks` block):

- **PostToolUse hooks** for the Write, Edit and Bash tools
- Runs `${CLAUDE_PLUGIN_ROOT}/scripts/lint-hook` after a tool call that touches markdown
- Auto-fixes on Write/Edit; reports without rewriting on Bash
- Shows brief status messages in the Claude Code interface
- `WB_LINT_HOOK=0` disables it without editing the manifest

To disable automatic linting, remove or comment out the `hooks` section in `.claude-plugin/plugin.json`.
