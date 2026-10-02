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

### `test-check`

Contract tests for `check`'s `require()`, extracted from the shipped script and run against fake binaries on `PATH` (missing, unparseable version, too old, new enough). Run after changing `check`.

### `check`

**Every gate this repository has, in one command.** This is what CI runs and what a maintainer
runs before cutting a release.

```bash
./plugin/scripts/check
```

Runs, in order: `shellcheck-gate` (shellcheck ≥ 0.9.0 required), `lint --all`, `check-guards`, `test-guards`, `test-count`, `test-phi-patterns`, `test-quiet`, `test-check`, `test-lint`, `test-prime`, `test-pr-template`, `test-wbte-dictionary`, `test-pr-identity`. **Every
gate runs even after one fails** — knowing that something is broken is less useful than knowing
which things are. Exits 0 only if all of them pass.

It exists because the guards below shipped with nothing invoking them, which is its own instance
of the class they hunt: a check that never runs and a check that always passes look the same from
outside. CI runs this on push to `main` and on every pull request
(`.github/workflows/checks.yml`). That workflow is maintainer infrastructure and is **never
shipped** — `marketplace.json` sets `"source": "./plugin"`, so nothing outside `plugin/` reaches
an installer.

### `shellcheck-gate`

Runs `shellcheck` over the plugin's own shell scripts, at **default severity only** — `-o all`
is what produces the noise, and noise is what gets a gate switched off. Scoped by shebang, not
by glob: `plugin/scripts/*` would feed `README.md` to the parser and produce seven spurious
errors.

```bash
./plugin/scripts/shellcheck-gate
```

It earned its place on the first run — `cd` without `|| exit` in two scripts (a failed `cd`
scans the wrong tree), two dead assignments in `test-count`, and an error in its own source,
because a comment beginning `# shellcheck` is parsed as a *directive*.

Deliberate exceptions carry `# shellcheck disable=<code>` **with the reason beside them**, never
a bare suppression.

**It is not the engine for `check-guards`.** That was probed and rejected: `SC2312` flags every
masked return value, so it fires on `n=$(count foo f) || exit 2` and on `[ -e "$x" ] || continue`
alike — 10 false positives against 15 correct files — and it misses the unquoted `--include`
glob entirely.

**`shellcheck` is required, not optional.** `check` fails loudly and prints the install command
when it is missing, because a gate that silently skips is indistinguishable from one that
passed — the defect class this whole directory exists to catch, one level up.

### `check-guards`

Finds measurements whose failure is indistinguishable from a clean result — the class where a
broken command and a genuinely empty result produce the same output, and the error always points
toward believing things are fine. Six shapes:

1. A counting `grep` captured in a substitution **whose exit status is never tested**. grep exits
   1 on no match and 2 on **error**, so a missing file and a clean file both yield something that
   looks like a usable count.
2. An unquoted `--include=` glob. Shell-dependent: `bash` passes an unmatched glob through, `zsh`
   errors and the result is silently zero.
3. A `for` over a glob with no existence test. An unmatched glob runs the body once with the
   literal pattern as the filename.
4. An outward-facing action left as a separate statement after the one it depends on.
   `git push; gh pr ready` un-drafts at a head the push never delivered; an unchained
   `gh pr view --json labels` after a failed `gh pr edit --add-label` prints an array without
   the label, which reads exactly like the label landing. `&&` is the whole remedy, and
   de-chaining is a one-character edit nothing else here can see — `shellcheck-gate` skips
   `*.md`, and `lint` is markdownlint.
5. A bash-only `${PIPESTATUS[0]}` inside a markdown fence. The Bash tool runs zsh, where it expands
   to nothing, so `[ "" -le 1 ]` is true and a grep that exited 2 passes its own guard. Markdown
   only: in a `.sh` file with a bash shebang it is correct.
6. A bare positional token (`$1`, `$ARGUMENTS`) inside a fence of a shipped `SKILL.md`. The harness
   substitutes it with the invocation's arguments, so `awk -F: '$1 != …'` arrives as
   `awk -F: '--plan != …'`. `SKILL.md` only, `clip` is exempt, and `${1:-…}` is not matched.

```bash
./plugin/scripts/check-guards            # defaults to plugin/
./plugin/scripts/check-guards some/dir
```

Exit 0 clean, 1 findings, **2 the scan could not be trusted** — a missing target, or a file it
could not read. That third state matters: a checker that reports clean because it scanned nothing
is the defect it exists to catch.

It scans shell scripts and the fenced shell blocks inside markdown, including **indented** fences
and `sh`/`shell`/`zsh` as well as `bash` — a block nested in a numbered step is still an instruction a
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

- **Corpus** — 131 labelled cases (`jq length fixtures/guard-corpus.json`), each carrying the
  review round that found it. Every shape must fire; every correct form must not.
- **Scan integrity** — properties the corpus structurally cannot test, because every corpus case
  materialises a real directory: a missing target exits 2, an empty directory does not hard-fail,
  a symlinked directory is followed.
- **Mutation survivability** — 25 single-line breaks are planted in `check-guards` and the
  suite asserts each one is caught. This exists because a previous suite reported 31/31 while four
  of the checker's guards could each be deleted with a one-line edit and it stayed green. **A
  corpus proves the detectors fire on what you thought of; mutation proves the corpus would notice
  if one stopped firing at all.** The mutation score is computed against corpus *and* integrity
  together, or the integrity guards would themselves be deletable.

Acceptance bar: 100% of the corpus, all integrity checks, every mutation caught.

```bash
./plugin/scripts/test-guards --generated
```

**The generated sweep** is a separate mode and still not part of `check`. It runs in CI on every
pull request. Locally it takes about four minutes on the maintainer's machine and has been
measured at twelve, against `check`'s ~20 seconds. It parses `check-guards` and mutates it mechanically: every
comparison operator, boolean operator and integer constant, every statement deletion, and a set
of regex weakenings (drop anchors, drop word boundaries, collapse alternations, widen
quantifiers). 421 mutants (recorded in `fixtures/mutation-ratchet.json`). The ratchet was
re-based on the lexer rewrite on 2026-10-01 and now stands at 381 of 421 killed.

**Why both.** The curated list is author-written, and round 4 of this repository's own review
established what that is worth: the same session wrote the tool, the corpus *and* the mutations,
and an independent reviewer's 24 mutations found 20 survivors behind a green 12/12. **A generator
has no blind spot correlated with the author's**, because it is not reasoning about the problem —
it walks the syntax tree and changes one thing.

The sweep scores against the corpus **and** the integrity layer. Corpus-only scoring mis-reports
every mutation the integrity checks cover — `scanned == 0`, the unreadable-file refusal, target
resolution — as a survivor, which inflated the survivor count by 11%.

**It ratchets rather than gating.** Demanding zero survivors would fail forever at 67% and be
ignored within a week; printing a number nobody compares to anything is the same as not running
it. So the kill count is recorded in `fixtures/mutation-ratchet.json` and **may not fall**, and
**no survivor may go unwaived**: a newly surviving mutant must be killed with a corpus case or
waived with an argument, and `--generated` fails on any unwaived survivor or a stale waiver.
Those are the two things the sweep enforces. When the mutant set itself shrinks because
`check-guards` was simplified, the stored count is lowered by a deliberate hand edit of
`fixtures/mutation-ratchet.json`, with the reason in the commit message, and `--generated` prints
the exact values. It never lowers the count by itself.

**Equivalent mutants are the known cost**, waived in `fixtures/mutation-waivers.json`, and a
waiver carries an argument rather than an entry. Treat the survivor list as a queue of corpus
cases worth writing, not as a bug list: many survivors are constants and branches no realistic
input distinguishes.

### `test-phi-patterns`

Contract test for the PHI scrub patterns in `daily-digest/sources.md`. The patterns are
extracted **from the shipped file**, never restated here — a second copy is how the previous
version drifted, and a test carrying its own copy of the thing under test verifies nothing.

Both directions: the variants the prose demands must match (lowercase, missing or extra
separators), and the identifiers a digest is made of must not (Jira keys, PR refs, ISO dates,
SHAs). Known over-matches are pinned as expected, so the trade-off is visible rather than
accidental.

```bash
./plugin/scripts/test-phi-patterns
```

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

### `pr-identity`

Decides how a PR number, branch or path target relates to this checkout. Prints closed-set key=value lines: `relation`, `fix`, `publish`, and push destination. Consumers act on the fields, never a ref name.

### `test-pr-identity`

Contract tests for `pr-identity`. Scenario table over scratch worlds and error paths, using the stub `gh`.

```bash
./plugin/scripts/test-pr-identity
```

### `fixtures/gh-stub`

Stub `gh` for `test-pr-identity`. Reads `$GH_FIXTURE` and logs to `$GH_LOG`.

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
with 200 plans. The card has a limit of 150 words and must name PR descriptions and commit
messages. Run after changing `wb-prime.sh`.

### `pr-template`

Prints the PR template that `/wb:pr-description` fills. It looks where GitHub looks, in
GitHub's order: `.github/`, the repository root, then `docs/`. Each line is
`repo <absolute path>`: the default `pull_request_template.md` (any case) first, then the `.md`
files of a `PULL_REQUEST_TEMPLATE/` directory. With no template, the one line is
`generic <absolute path>`, the template that ships with the skill. It only reads.

```bash
./scripts/pr-template
```

### `test-pr-template`

Contract tests for `pr-template`: each location, GitHub's order, names in any case, a template
directory, no template, a run from a subdirectory, and a run outside a repository. Run after
changing `pr-template`.

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
