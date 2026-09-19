# Scripts

Utility scripts for the project.

## Available Scripts

### `lint`

Lints markdown files using markdownlint.

```bash
# Lint only changed markdown files (default)
./plugin/scripts/lint

# Auto-fix issues in changed files
./plugin/scripts/lint --fix

# Lint all markdown files in the project
./plugin/scripts/lint --all

# Auto-fix all markdown files
./plugin/scripts/lint --all --fix

# Show help
./plugin/scripts/lint --help
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
./plugin/scripts/quiet pytest -q
./plugin/scripts/quiet make test

# Red run -> full output is printed verbatim, original exit code preserved
./plugin/scripts/quiet go test ./...
```

**Features:**

- Generalizes the `lint-hook` pattern (run → keep a marker line → suppress the rest) to any runner
- Success path keeps the model inside its working-context "smart zone" (a 200-line green run becomes ~2 lines)
- Failure output is never truncated — full log on any non-zero exit
- Exit-code-faithful, so `verification-before-completion` checks keep working
- Opt-in: invoke it explicitly; nothing is wrapped automatically

**Verify the contract:**

```bash
./plugin/scripts/test-quiet
```

### `test-quiet`

Contract tests for `quiet` (success collapse, failure dump, exit-code pass-through). Run after changing `quiet`.

### `check`

**Every gate this repository has, in one command.** This is what CI runs and what a maintainer
runs before cutting a release.

```bash
./plugin/scripts/check
```

Runs, in order: `lint --all`, `check-guards`, `test-guards`, `test-count`, `test-quiet`. **Every
gate runs even after one fails** — knowing that something is broken is less useful than knowing
which things are. Exits 0 only if all of them pass.

It exists because the guards below shipped with nothing invoking them, which is its own instance
of the class they hunt: a check that never runs and a check that always passes look the same from
outside. CI runs this on push to `main` and on every pull request
(`.github/workflows/checks.yml`). That workflow is maintainer infrastructure and is **never
shipped** — `marketplace.json` sets `"source": "./plugin"`, so nothing outside `plugin/` reaches
an installer.

### `check-guards`

Finds measurements whose failure is indistinguishable from a clean result — the class where a
broken command and a genuinely empty result produce the same output, and the error always points
toward believing things are fine. Three shapes:

1. A counting `grep` captured in a substitution **whose exit status is never tested**. grep exits
   1 on no match and 2 on **error**, so a missing file and a clean file both yield something that
   looks like a usable count.
2. An unquoted `--include=` glob. Shell-dependent: `bash` passes an unmatched glob through, `zsh`
   errors and the result is silently zero.
3. A `for` over a glob with no existence test. An unmatched glob runs the body once with the
   literal pattern as the filename.

```bash
./plugin/scripts/check-guards            # defaults to plugin/
./plugin/scripts/check-guards some/dir
```

Exit 0 clean, 1 findings, **2 the scan could not be trusted** — a missing target, or a file it
could not read. That third state matters: a checker that reports clean because it scanned nothing
is the defect it exists to catch.

It scans shell scripts and the fenced shell blocks inside markdown, including **indented** fences
and `sh`/`shell` as well as `bash` — a block nested in a numbered step is still an instruction a
model executes. Prose and tables are not scanned, so a document may describe a bad pattern freely.
**A deliberate counter-example belongs in a `text` fence rather than a `bash` one**; that is the
convention instead of a suppression marker, because a marker can silence a real finding and a
fence language cannot. Two files are exempt by name — `check-guards` and `test-guards` — because
their content *is* the fixtures.

**Note on shape 1**: the rule is *captured and the status never tested*, not merely *captured*. A
bare `n=$(grep -c x f)` does not mask `$?` — the assignment's status is the substitution's — so a
following `$?` test is accepted. `shellcheck` is right to decline to flag the bare form, which is
why it was rejected as the engine for this check.

**Requires `python3`.** It was a bash regex scanner through three review rounds, each of which
patched real holes and opened comparable ones; the rewrite parses fences properly and locates a
capture by finding the substitution containing it. Measured on the same corpus, the bash version
scored 89% with 50% mutation survivability; this one scores 100% and 100%.

### `test-guards`

Contract tests for `check-guards`, in **three** parts — and the third is the one that matters:

```bash
./plugin/scripts/test-guards
```

- **Corpus** — 43 labelled cases in `fixtures/guard-corpus.json`, each carrying the review round
  that found it. Every shape must fire; every correct form must not.
- **Scan integrity** — properties the corpus structurally cannot test, because every corpus case
  materialises a real directory: a missing target exits 2, an empty directory does not hard-fail,
  a symlinked directory is followed.
- **Mutation survivability** — twelve single-line breaks are planted in `check-guards` and the
  suite asserts each one is caught. This exists because a previous suite reported 31/31 while four
  of the checker's guards could each be deleted with a one-line edit and it stayed green. **A
  corpus proves the detectors fire on what you thought of; mutation proves the corpus would notice
  if one stopped firing at all.** The mutation score is computed against corpus *and* integrity
  together, or the integrity guards would themselves be deletable.

Acceptance bar: 100% of the corpus, all integrity checks, every mutation caught.

```bash
./plugin/scripts/test-guards --generated
```

**The generated sweep** is a separate mode and deliberately not part of `check` — it takes ~80
seconds against `check`'s ~20. It parses `check-guards` and mutates it mechanically: every
comparison operator, boolean operator and integer constant, every statement deletion, and a set
of regex weakenings (drop anchors, drop word boundaries, collapse alternations, widen
quantifiers). ~294 mutants.

**Why both.** The curated list is author-written, and round 4 of this repository's own review
established what that is worth: the same session wrote the tool, the corpus *and* the mutations,
and an independent reviewer's 24 mutations found 20 survivors behind a green 12/12. **A generator
has no blind spot correlated with the author's**, because it is not reasoning about the problem —
it walks the syntax tree and changes one thing.

The sweep scores against the corpus **and** the integrity layer. Corpus-only scoring mis-reports
every mutation the integrity checks cover — `scanned == 0`, the unreadable-file refusal, target
resolution — as a survivor, which inflated the survivor count by 11%.

**Equivalent mutants are the known cost**, waived in `fixtures/mutation-waivers.json`, and a
waiver carries an argument rather than an entry. Treat the survivor list as a queue of corpus
cases worth writing, not as a bug list: many survivors are constants and branches no realistic
input distinguishes.

### `lib_mutate.py`

The mutation operators used by `test-guards --generated`. Not a script — imported, not run.

### `fixtures/guard-corpus.json`

The labelled corpus. Not a test on its own — it is the asset three adversarial review rounds
bought, and every case records which round found it, so it doubles as the regression record.
Add a case here when a new shape is found; that is cheaper than adding a detector.

### `count`

A match count whose failure is distinguishable from zero.

```bash
n=$(./plugin/scripts/count 'pattern' file.txt) || handle_failure
n=$(./plugin/scripts/count --lines file.txt)   || handle_failure
```

Inside a shipped skill, reference it as `${CLAUDE_PLUGIN_ROOT}/scripts/count`. It is not on
`PATH`: written as a bare `count`, the command is not found, the substitution fails, and the
`|| handle_failure` branch is taken every time — which would make the one script whose purpose
is a trustworthy count always report failure.

- **exit 0** — the count is on stdout and is trustworthy, including `0`
- **exit 2** — the count could not be taken; stdout is empty, reason on stderr

Because the failure is loud, `n=$(count ...) || handle` is safe in a way that
`n=$(grep -c ...)` is not.

### `test-count`

Contract tests for `count`. The contract is one thing: **a count of zero and a failure to count
must be distinguishable.** Covers a real count, zero matches, a missing file, an unreadable file,
a directory, a grep error on a readable file, `--lines`, and bad usage — plus a control showing
that `grep -c` collapses the two once defaulted the way a careful author would default them.

```bash
./plugin/scripts/test-count
```

A skip is reported as a skip, never as a pass.

## Configuration

The project uses `.markdownlintrc` for markdownlint configuration. Current settings:

- Line length checking disabled (for long code blocks)
- Inline HTML allowed
- Emphasis as heading allowed (bold lines used as step directives, e.g. `**Decide WHAT to build**`)
- Fenced code blocks without language specification allowed

## Claude Code Hooks

The project has automatic markdown linting configured via Claude Code hooks in the plugin manifest `.claude-plugin/plugin.json` (`hooks` block):

- **PostToolUse hooks** for Write and Edit tools
- Automatically runs `${CLAUDE_PLUGIN_ROOT}/scripts/lint-hook` after any markdown file is created or modified
- Attempts to auto-fix common markdown issues
- Shows brief status messages in the Claude Code interface

To disable automatic linting, remove or comment out the `hooks` section in `.claude-plugin/plugin.json`.
