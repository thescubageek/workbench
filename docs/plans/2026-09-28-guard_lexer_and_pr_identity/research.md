---
project: guard_lexer_and_pr_identity
ticket: null
created: 2026-09-28
created_timestamp: 2026-09-28T20:05:58Z
status: complete
last_updated: 2026-09-28
researcher: scraig
git_commit: 662d93b30fe5cbb06ab8d9073b7d75f4128cc4c3
git_branch: adversarial-loop-skill-research
repository: thescubageek/workbench
tags: [research, codebase, guard_lexer_and_pr_identity]
---

# Research: guard_lexer_and_pr_identity

**Created**: 2026-09-28 20:05 UTC
**Last Updated**: 2026-09-28
**Ticket**: N/A

## Research Question

How does `plugin/scripts/check-guards` lex fenced shell today (quotes, escapes, nested
substitutions, fence classes, the guard regex), and how does `adversarial-review` resolve a PR,
branch or path target into a range and a `REVIEW.md` base (Steps 1 and 2)? Facts needed for the
round-10 escalation: the ten held findings, the round-3 spike's method and scores, and what `gh`
and `git` expose for fork-safe PR identity.

## Summary

`check-guards` is a 479-line Python 3 scanner with no tokenizer library (`import os, re, sys`
only, `check-guards:53-55`). It splits markdown into fenced blocks with one regex
(`check-guards:57`) and a state machine (`:82-108`), then lexes each shell line with three
separate hand-written quote trackers — `strip_comment` (`:111-131`), `_quote_spans` (`:134-147`)
and `substitutions` (`:150-194`) — none of which handles a backslash escape. `substitutions()`
returns only the outermost span per `$(`; nested `$( )` are walked over to find the matching
`)` and never recorded. Six detector shapes hang off that lexing, each a regex
(`COUNTING :59`, `GUARD :62`, `PUBLISH :68`, `BASHISM :75`, `POSITIONAL :76`). It has been
patched in rounds 4, 7, 9 and 10 — 21 tasks across 14 commits — after one rebuild on the
round-3 spike's verdict, whose two-score method (corpus pass rate, mutation survivability) is
what `test-guards` now runs: 114 corpus cases, 15 integrity claims, 25 curated mutations, and a
`--generated` sweep of 395 AST mutants gated by 51 waivers and a ratchet at 344.

`adversarial-review` resolves a target in Step 1's `resolve_range()`
(`adversarial-review/SKILL.md:111-149`) and again, independently, in Step 2
(`:209-229`). Both identify a PR's head **by branch name only**: the `headRefName` from
`gh pr view` is compared against `git branch --show-current` (`:125`, `:221`), and on a match
the range is rewritten to end at local `HEAD` (R9-T2, R9-T26). No shipped file reads
`headRefOid`, `isCrossRepository`, `headRepository`, or `refs/pull/`, and nothing fetches. Both
fields are available: `gh pr view 25 --json` returns them, `refs/pull/25/head` exists on the
remote at the same SHA as `headRefOid`, and a scratch clone fetched it into a remote-tracking ref
cleanly. The local worktree's fetch refspec covers `refs/heads/*` only, so the pull ref does not
resolve locally today.

The ten round-10 findings held for this design sit exactly on those two seams. Every mechanism
they describe was reproduced by measurement during this research: `read -r path` empties zsh's
lookup path (`command -v sed` prints nothing afterwards); `filter=$?` after a command
substitution tracks the loop body's last command, not the loop; a backslash-escaped `\$(` in
double quotes stays literal in the shell but is opened as a substitution by the lexer.

## Detailed Findings

### The `check-guards` lexer

**Location**: `plugin/scripts/check-guards` (479 lines, Python 3.14 here)

**What exists**:

- A module docstring (`:1-52`) naming six shapes and the exit contract: 0 clean, 1 findings,
  2 the scan could not be trusted (`:51`). Two files are exempt by basename
  (`EXEMPT = {'check-guards', 'test-guards'}`, `:79`); `/node_modules/` paths are skipped (`:413`).
- File dispatch by extension and path, never by shebang (`:419-421`): `.md` files are fence-scanned;
  `.sh` files and extensionless files whose path contains `/scripts/` are scanned whole
  (`is_sh = ext == '.sh' or (ext == '' and f'{os.sep}scripts{os.sep}' in path)`).
- `SHELL_INFO = {'bash', 'sh', 'shell'}` (`:58`): a fence's info string, lowercased, must equal
  one of these three words to count as shell. `zsh` is not in the set.

**Key code — fence detection** (`:57`, `:90-108`):

```python
FENCE = re.compile(r'^(?P<ind>[ ]{0,3})(?P<f>`{3,}|~{3,})[ \t]*(?P<info>\S*)')
```

Opener: any 3+ backticks or tildes with up to 3 spaces of indent; the info string is one
whitespace-delimited token. Closer: same fence character, run length `>=` the opener's
(`:103`), and **no** info string. Indent is not compared. Every fence is tracked regardless of
language, so a ` ```bash ` nested inside a ` ````text ` wrapper is content, not live shell
(`:96-98`). A block still open at end of file returns `unclosed_at`, and `collect()` reports it
as `'unclosed shell fence'` (`:430-433`) whatever the fence's language was.

**Key code — the three quote trackers**:

- `strip_comment` (`:111-131`): per-character loop with one `quote` variable; `#` at column 0
  or after whitespace, outside quotes, ends the line. No backslash handling.
- `_quote_spans` (`:134-147`): a per-character boolean list, `True` inside `'…'` or `"…"`. No
  backslash handling.
- `substitutions(line)` (`:150-194`): returns `[(inner_start, close_index)]` for `$( )` and
  backtick spans. Single quotes suppress recognition of `$(`; double quotes do not (`:156-157`,
  `:166-169`). On `$(`, a fresh `_quote_spans` is computed for the substring after it (`:170`)
  and a depth counter walks to the matching `)` (`:173-179`); the result appended is the
  **outermost** inner span only (`:180`). Nested `$( )` inside it are consumed, not returned. A
  backtick with no partner is skipped one character (`:182-191`). There is no check for a
  preceding backslash anywhere in the function: `\$(` opens a span (`:169`).

**Key code — the shape regexes**:

```python
COUNTING = re.compile(r'\bgrep\b[^|;)`]*?\s(?:-[A-Za-z]*c[A-Za-z]*|--count)\b')   # :59
GUARD    = re.compile(r'\|\|\s*(?:true\b|:(?!\w)|echo\b)')                          # :62
STATUS_TEST = re.compile(r'\$\?')                                                   # :63
STATUS_LINE = re.compile(r'^\s*(?:if\s|\[\[?|test\s|[A-Za-z_]\w*=\$\?\s*$)')        # :200
PUBLISH  = re.compile(r'^\s*(?:git\s+push|gh\s+pr\s+(?:ready|edit|comment|merge|view|close|reopen))\b')  # :68-69
BASHISM  = re.compile(r'\$\{?PIPESTATUS\b')                                         # :75
POSITIONAL = re.compile(r'\$(?:\d|ARGUMENTS)')                                      # :76
POSITIONAL_OK = {'clip'}                                                            # :77
```

**How the six shapes work**:

1. **Shape 1, counting capture** (`:302-326`): for each span from `substitutions()`, if
   `COUNTING` matches the inner text and neither `GUARD.search(inner)` nor a `GUARD.match` on
   the text immediately after the closing delimiter matches, and `_status_tested()` (`:203-213`,
   next-line lookahead for a `$?` test via `STATUS_LINE`) finds nothing, emit
   `'grep -c captured without a status guard'`. `GUARD` accepts `|| true`, `|| :` and
   `|| echo`; `${n:-0}` appears in the docstring's prose (`:11`) and in no regex.
2. **Shape 2** (`:328-332`): `--include=(\S+)` whose value does not start with a quote.
3. **Shape 3** (`:334-353`): `for <var> in <glob>` with no `[ -e/-f/-s/-r ]` test or `continue`
   within `GLOB_WINDOW = 4` lines (`:64`, `_is_guard :216-219`).
4. **Shape 4** (`:264-284`, `:371-373`): two `PUBLISH`-class statements in sequence not joined
   by `&&`, over logical lines with continuations joined and top-level `;` split.
5. **Shape 5** (`:355-361`): `BASHISM` in a markdown-fenced line only (`md=True`).
6. **Shape 6** (`:363-366`): `POSITIONAL` in a fenced line of a `SKILL.md` whose directory is
   not in `POSITIONAL_OK` (`skill` computed at `:440-441`).

**The FIXES table** (`:378-393`) carries one hint per shape. The shape-6 hint (`:388-390`) reads:
`'use no positional token at all —`cut -d: -f1`,`while IFS=: read -r path _`, or describe the argument slot in prose'`.
The unclosed-fence hint (`:391-392`): `'close the fence; a later ```bash opener is otherwise read as its content and never scanned'`.

**Invocation**: `plugin/scripts/check:55` runs `check-guards` with no arguments (default target
`plugin/`); `check:56` runs `test-guards` with no arguments. Any non-zero exit fails the gate;
exit 2 is not distinguished from 1 (`check:21-30`).

### The test apparatus around it

**Location**: `plugin/scripts/test-guards` (625 lines), `plugin/scripts/lib_mutate.py`
(233 lines), `plugin/scripts/fixtures/`

**What exists**:

- **Corpus** — `fixtures/guard-corpus.json`, 114 cases, schema `id`, `shape`, `expect` (1/0),
  `path`, `content`, `provenance`, optional `expect_at` (`[[line, shape], …]`). `run_corpus`
  (`test-guards:149-182`) materializes each case under a temp dir and runs the candidate
  implementation by **subprocess**; for `expect == 1` the parsed `(line, shape)` set must equal
  `expect_at` exactly, not merely be non-empty (`:165-167`).
- **Integrity claims** — 15, in `run_integrity` (`:185-338`): missing target exits 2 and names
  the path; empty directory exits 0; a tree with no scannable files exits 0 and says "nothing to
  check" on stderr; the scanned-file count is exact; a relative target resolves against the
  caller's cwd; findings say why on stderr; a by-name-exempt file is not reported while the same
  content elsewhere is; a nested symlink is followed; an unreadable file exits 2 and is named;
  no argument defaults to the `plugin` tree beside the script.
- **Curated mutations** — 25 `(label, old, new)` tuples (`:51-120`), each applied to a temp copy
  (`:538-553`) and counted caught when misses rise, integrity drops, or false positives rise
  (`:558-563`). `check-guards`' SHA-256 is asserted unchanged afterwards (`:578-583`).
- **`--generated`** — `lib_mutate.generate()` parses `check-guards` with `ast`, and for every
  node applies comparison swaps, `and`/`or` flips, integer `±1`, seven regex weakenings
  (`lib_mutate.py:29-41`), and statement deletion (`:134-231`). Each mutant is keyed
  `<scope> | <block> | <statement> | <operator>` with `#n` on collisions (`:67-116`), and
  labelled `L<line> <op>` for display only. Mutants run **in-process** under a 5-second alarm
  (`test-guards:395-412`); the docstring at `:342-344` gives the reason: subprocess spawning
  at ~30 ms across ~16k runs is nine minutes of `fork()`. A survivor is re-scored against the
  integrity claims via the CLI (`:435-439`) before it counts. Current state, from the fixtures:
  395 mutants, 344 killed, 51 waived (`mutation-waivers.json`, each `{"match": <key>, "reason":
  <prose>}`), 0 unwaived, ratchet `{"killed": 344, "of": 395}`.
- **`ratchet_verdict(killed, prev, survivors, stale)`** (`:502-517`): fails on any stale waiver,
  any unwaived survivor, or `killed < prev`; a rise rewrites the ratchet file (`:619-621`). The
  plain suite self-tests it once, asserting an unwaived survivor fails even when the count rose
  (`:585-587`).
- **A candidate implementation** can be scored with `test-guards <path>` (`:12, 28-29`): every
  subprocess and the mutant source both point at that path.
- **Runtime as documented**: `plugin/scripts/README.md:211-212` says `--generated` takes
  "~80 seconds"; the round-9 and round-10 sessions recorded about 4 minutes and, earlier,
  12 minutes 22 seconds. `--generated` is run by neither `check` nor CI
  (`.github/workflows/checks.yml:34` runs `check` only); the README calls it "a separate mode
  and deliberately not part of `check`" (`:211`).

**Precedent for adding a shape**, from `git show --stat`:

| Commit | Shape | `check-guards` | Corpus | Waivers | Sweep after |
| ------ | ----- | -------------- | ------ | ------- | ----------- |
| `5d77fe0` R7-T7 | 5, `PIPESTATUS` | +33 lines | 86 → 96 | 58 → 58 (one reworded) | 309/367, 0 survived |
| `9255fb2` R9-T0 | 6, positional | +26 lines | 96 → 105 | 58 → 58 | 318/376, 0 survived |

R9-T17 then took the corpus to 114 (`4de2701`).

### The history of patches to the lexer

Every task against `plugin/scripts/check-guards` since the rebuild, from the round plans:

| Round | Task | Finding | Shape |
| ----- | ---- | ------- | ----- |
| 4 | R4-T1 | tracked-file mutation leaves a disarmed checker on disk | 2 + 1 |
| 4 | R4-T2 | relative path resolves against the wrong tree via `chdir` | 1 |
| 4 | R4-T3 | paren counting ignores quotes | 2 |
| 4 | R4-T4 | unpaired backtick breaks the span scan | 2 |
| 4 | R4-T5 | `$?` lookahead unsound in both directions | 2 |
| 4 | R4-T6 | `GUARD`'s trailing `\b` after `:` never matches | 2 |
| 4 | R4-T7 | a correctly guarded one-line `for` glob reported | 2 |
| 4 | R4-T8 | bash fence nested in a text fence entered as live shell | 2 |
| 7 | R7-T7 | no detector for the `PIPESTATUS` bashism | 2 |
| 9 | R9-T0 | no detector for `$1`/`$ARGUMENTS` in a fence | 2 |
| 9 | R9-T14 | `COUNTING` misses `-cE`, `-ci`, `-cv` | 2 |
| 9 | R9-T15 | double-quoted `$( )` never scanned | 2 |
| 9 | R9-T17 | unclosed non-shell fence swallows later shell blocks | 2 |
| 10 | R10-T5 | shape-6 hint's `read -r path` ties to `PATH` under zsh | 3 |
| 10 | R10-T7 | shape 6 does not scan `zsh` fences | 2 |
| 10 | R10-T10 | `\$(` in double quotes scanned as a substitution (from R9-T15) | 2 |
| 10 | R10-T11 | only the outermost `$( )` span is returned | 2 |
| 10 | R10-T12 | `GUARD` accepts `\|\| echo` inside the substitution | 2 |
| 10 | R10-T21 | any unclosed fence is labelled "unclosed shell fence" | 2 |

Fourteen commits touch the file; four rounds patched it. The round-10 ledger marks R10-T10 as
caused by R9-T15 and R10-T5 by R9-T0
(`docs/plans/2026-09-17-adversarial_loop/review-log.md`, round 10 breaker section).

### The round-3 spike

**Location**: `docs/plans/2026-09-17-adversarial_loop/thoughts/2026-09-18-check-guards-implementation-probe.md`,
`thoughts/spike/`

**What exists**: a pre-registered probe, written before it ran, scoring three implementations
against one 38-case corpus (23 must-fire, 15 must-not-fire) on two numbers.

| Candidate | What | Corpus | Mutation survivability |
| --------- | ---- | ------ | ---------------------- |
| A | the then-shipped bash scanner | 34/38 (89%) | 4/8 caught (50%) |
| B | `shellcheck -o all` plus a fence extractor | 27/38 (71%), 10 false positives | not scored; rejected as engine |
| C | ~130-line probe: CommonMark fence parse plus substitution-span analysis | 37/38 (97%) | 7/8 caught (87%) |

The verdict, recorded in `design.md` of that plan, was to rebuild on C. The caveat recorded
with it, verbatim: *"candidate C is a ~130-line probe with no tests of its own, one known false
positive (`ok-status-next-line`, which needs next-line lookahead for `$?`) and one uncovered
mutation (the fence closer — a corpus gap, not an implementation gap). The rebuild is a phase
with the corpus as its acceptance criteria, not a copy of the spike."*

Q8-5 in that plan, verbatim: *"Is `check-guards`' shape-1 rule even well-formed? `shellcheck`
does not flag `n=$(grep -c f x)` and is arguably right: a bare assignment does not mask the
status, so `$?` works. The real defect is 'nobody checks it' — a dataflow property, not a
syntax pattern."* Its state: *"Partly resolved 2026-09-18: well-formed only as 'captured and
the status never tested', which needs lookahead."*

### `adversarial-review` target resolution

**Location**: `plugin/skills/adversarial-review/SKILL.md` — Arguments (`:50-90`), Step 1
(`:68-202`), Step 2 (`:203-284`), Step 3's blast-radius block (`:308-388`)

**What exists — Arguments**: `argument-hint:
"[<pr#>|<branch>|<path>] [--effort=<low|medium|high|xhigh|max>] [--plan=<dir>]"` (`:4`). The
positional is sniffed: digits are a PR, a path that exists on disk is a path, anything else is a
branch (`:54-55`). `--effort` and `--plan` (both `--plan=<dir>` and `--plan <dir>`) are
stripped before binding (`:56-62`). The bare-`$1` warning at `:87-90` carries a literal `$1` in
prose; the round-10 run received it substituted.

**Key code — Step 1** (`:105-149`):

```bash
base_ref() {
  b=$(gh pr view "$@" --json baseRefName --jq .baseRefName 2>/dev/null)
  printf 'origin/%s' "${b:-main}"
}

resolve_range() {
  if [ -z "${target:-}" ]; then
    range="$(base_ref)...HEAD"
  elif [ -e "$target" ]; then
    range="$(base_ref)...HEAD"
    pathspec="$target"
  elif printf '%s' "$target" | grep -qE '^[0-9]+$'; then
    range=$(gh pr view "$target" --json baseRefName,headRefName \
              --jq '"origin/" + .baseRefName + "...origin/" + .headRefName') \
      || { echo "could not resolve PR $target via gh — NOT reviewing the current branch" >&2; return 1; }
    if [ "${range##*...origin/}" = "$(git branch --show-current)" ]; then
      range="${range%...*}...HEAD"
    fi
  else
    range="$(base_ref "$target")...$target"
  fi

  left="${range%%...*}"
  right="${range##*...}"
  for ref in "$left" "$right"; do
    git rev-parse --verify --quiet "$ref^{commit}" >/dev/null && continue
    echo "range did not resolve: '$ref' is not a revision here — NOT reviewing" >&2
    return 1
  done
  ...
}
```

**How it works**:

1. No target or a path target: the current branch against its own base, `base...HEAD`. A path
   adds a pathspec (`:112-118`).
2. A PR number: `gh pr view` supplies `baseRefName` and `headRefName`; the range is
   `origin/<base>...origin/<head>`. If `<head>` equals `git branch --show-current`, the right
   endpoint becomes `HEAD` (`:125-127`, from R9-T2). No fetch precedes this, and `headRefOid`
   is not read.
3. A branch name: `base_ref "$target"...<target>` (`:128-130`).
4. Both endpoints must pass `git rev-parse --verify --quiet "$ref^{commit}"` (`:133-140`).
5. Failure `return`s, never `exit`s (`:160-166`): the Bash tool runs a whole call in one shell.

**Key code — Step 2** (`:209-240`): a second, independent resolution.

```bash
if [ -z "${target:-}" ] || [ -e "$target" ]; then
  base_branch=$(gh pr view --json baseRefName --jq .baseRefName 2>/dev/null)
  head_ref="HEAD"
elif printf '%s' "$target" | grep -qE '^[0-9]+$'; then
  base_branch=$(gh pr view "$target" --json baseRefName --jq .baseRefName 2>/dev/null)
  head_ref=$(gh pr view "$target" --json headRefName --jq .headRefName 2>/dev/null)
  if [ "$head_ref" = "$(git branch --show-current)" ]; then
    head_ref="HEAD"
  else
    head_ref="origin/${head_ref:-}"
  fi
else
  base_branch=$(gh pr view "$target" --json baseRefName --jq .baseRefName 2>/dev/null)
  head_ref="$target"
fi
[ -n "$base_branch" ] && base_branch="origin/$base_branch"
base_branch=${base_branch:-origin/main}
base=$(git merge-base "$head_ref" "$base_branch" 2>/dev/null)
```

Then `git show "$base:REVIEW.md"`, with four documented outcomes (`:250-264`): Present; Absent
(`does not exist in`, the normal case); Base ref unresolved (`REVIEW.md NOT READ`); read from
the wrong branch, "the one with no error to show for it". Every `gh` call and the `merge-base`
carry `2>/dev/null`.

**Key code — Step 3's blast-radius filter** (`:313-323`):

```bash
hits=$(command grep -rnF --exclude-dir=.context -- "<changed symbol>" .)
search=$?
[ "$search" -le 1 ] || echo "SEARCH FAILED (grep exit $search) — NOT an isolated change" >&2
changed="<the changed file>"
callers=$(printf '%s\n' "$hits" | while IFS= read -r hit; do
  file=${hit%%:*}
  [ "$file" = "$changed" ] || [ "$file" = "./$changed" ] || printf '%s\n' "$hit"
done)
filter=$?
[ "$filter" -eq 0 ] || echo "FILTER FAILED (exit $filter) — NOT an isolated change" >&2
```

`--exclude-dir` matches basenames, so `.git` is not excluded; the round-10 run measured
`./.git/logs/HEAD`, `./.git/COMMIT_EDITMSG` and a binary-index match landing in `callers`.

**Consumers of the same identity test**:

- `adversarial-loop/SKILL.md:125`: *"If `target` does not name the current checkout, the
  pull-request phases do not run."* Prose only; the Phase 2 block (`:289-303`) pushes the
  checked-out branch and un-drafts `$PR` with no comparison of the PR's head to the checkout.
- `reply-to-claude/SKILL.md:45-48`: binds `PR` from `gh pr view ${target:+"$target"}` and never
  compares it to the checkout; the precondition at `:20` requires "a pull request for the current
  branch".
- `adversarial-loop/SKILL.md:424-426`: Phase 5 reads `gh api "repos/$REPO/commits/<head sha>/check-runs"`;
  `$REPO` is bound nowhere in that skill.

### What `gh` and `git` expose for PR identity

Measured 2026-09-28 from this worktree (`pwd` and `pwd -P` both
`/Users/scraig/conductor/workspaces/workbench/ankara`), read-only:

- `gh pr view 25 --json headRefOid,baseRefOid,isCrossRepository,headRepository,headRepositoryOwner`
  returns `headRefOid: 3b4e04bf…`, `baseRefOid: 46ef587b…`, `isCrossRepository: false`,
  `headRepositoryOwner.login: thescubageek`. `gh api repos/thescubageek/workbench/pulls/25`
  agrees on every field and adds `head.repo.full_name`.
- `git ls-remote origin 'refs/pull/25/*'` lists `refs/pull/25/head` at `3b4e04bf…` — equal to
  `headRefOid` — and `refs/pull/25/merge` at a different SHA.
- Locally, `git rev-parse --verify --quiet 'refs/pull/25/head^{commit}'` exits 1: the pull ref
  is absent. `remote.origin.fetch` is `+refs/heads/*:refs/remotes/origin/*` only.
- In a scratch clone under `/tmp` (deleted afterwards),
  `git fetch origin 'refs/pull/25/head:refs/remotes/origin/pr/25'` succeeded and
  `origin/pr/25` resolved to `3b4e04bf…`.
- `git merge-base HEAD origin/main` and `git merge-base 3b4e04b origin/main` both return
  `46ef587b…`, equal to `baseRefOid`.
- No file under `plugin/` uses `headRefOid`, `isCrossRepository`, `headRepository`,
  `refs/pull/`, or `git fetch`. `headRefName` is read at `adversarial-review/SKILL.md:121,220`
  and `fetch-issues/SKILL.md:74`.

### Shell facts behind the held findings

Measured through the Bash tool (zsh 5.9), each in a fresh call:

- `while IFS=: read -r path rest; do :; done` then `command -v sed` prints nothing and exits 1;
  `${#path}` is 1 afterwards against 31 in a fresh shell. With `file` as the variable,
  `command -v sed` prints `/usr/bin/sed`. (R10-T5's mechanism.)
- `callers=$(… | while … done); filter=$?` gives `filter=0` whether or not `set -o pipefail` is
  on; it gives `filter=1` only when the loop body's last command is `false`. (R10-T13's
  mechanism: `$?` reports the substitution's last command.)
- `f="cost \$(command grep -c q /dev/null)"; echo "$f"` prints the literal `$(` text; the shell
  does not substitute. (R10-T10's mechanism: the shell and the lexer disagree on `\$(`.)
- `type grep` and `type diff` both name a shell function from `~/.claude/shell-snapshots/`.
- Python 3.14.0 with stdlib `shlex` available; `bashlex` not installed. ShellCheck 0.11.0
  installed. The plugin's `check` requires `shellcheck` and `python3` (design decision PD2 of the
  parent plan made that a major-version dependency change).

## Architecture Documentation

**Current patterns found**:

- Pattern: a spike scored on two numbers before a rebuild — `thoughts/2026-09-18-check-guards-implementation-probe.md`,
  pre-registered outcomes, corpus pass rate plus mutation survivability; adopted as design in
  the parent plan and shipped as `test-guards`' permanent shape.
- Pattern: one task one commit, criterion RED before the fix — every row in the patch table
  above.
- Pattern: identity by name — `git branch --show-current` compared to `headRefName` in two
  places (`adversarial-review/SKILL.md:125`, `:221`); the loop's Phase 0 rule at
  `adversarial-loop/SKILL.md:125` is stated in prose and enforced by no block.
- Pattern: `return`, never `exit`, inside a fenced block (`adversarial-review/SKILL.md:160-166`).

**Component connections**:

- `check` → `check-guards` (gate 3) and `test-guards` (gate 4), `plugin/scripts/check:55-56`.
- `test-guards` → `lib_mutate.py` (`--generated` only) → `fixtures/mutation-{waivers,ratchet,survivors}`.
- `adversarial-loop` Phase 0 → `adversarial-review` Step 1 (`--plan=`, `target`) → Step 2 →
  Step 3; Phase 2 and Phase 5 re-resolve the PR from `target` independently.

**Conventions observed**:

- Scripts under `plugin/scripts/` are extensionless Python or bash; fixtures are JSON beside
  them; every script has a contract test named `test-<script>`.
- A detector shape lands as: regex constant, `analyse()` branch, `FIXES` entry, corpus cases
  with `provenance`, `SHAPE_OF` entry in `test-guards`, and a ratchet raise.

## Code References

- `plugin/scripts/check-guards:57-58` — `FENCE` regex and `SHELL_INFO`
- `plugin/scripts/check-guards:59-77` — every shape regex and `POSITIONAL_OK`
- `plugin/scripts/check-guards:82-108` — `md_shell_lines`, the fence state machine
- `plugin/scripts/check-guards:111-194` — the three quote trackers and `substitutions()`
- `plugin/scripts/check-guards:200-213` — `STATUS_LINE` and `_status_tested()` lookahead
- `plugin/scripts/check-guards:302-373` — `analyse()`, shapes 1–6
- `plugin/scripts/check-guards:378-393` — `FIXES`
- `plugin/scripts/check-guards:396-444` — `collect()`, dispatch and exemptions
- `plugin/scripts/test-guards:51-120` — the 25 curated mutations
- `plugin/scripts/test-guards:149-182` — `run_corpus`, exact `expect_at` matching
- `plugin/scripts/test-guards:371-465` — `run_generated`
- `plugin/scripts/test-guards:502-517` — `ratchet_verdict`
- `plugin/scripts/lib_mutate.py:29-41` — the seven regex weakenings
- `plugin/scripts/lib_mutate.py:67-116` — mutant keys and disambiguation
- `plugin/skills/adversarial-review/SKILL.md:105-149` — `base_ref`, `resolve_range`
- `plugin/skills/adversarial-review/SKILL.md:209-240` — Step 2's head/base resolution
- `plugin/skills/adversarial-review/SKILL.md:313-323` — the blast-radius filter
- `plugin/skills/adversarial-loop/SKILL.md:125` — the prose-only own-checkout rule
- `plugin/skills/adversarial-loop/SKILL.md:289-303` — Phase 2's push/un-draft block
- `plugin/skills/reply-to-claude/SKILL.md:45-48` — PR binding without a checkout check
- `docs/plans/2026-09-17-adversarial_loop/reviews/2026-09-28-round-10/tasks.md` — the ten
  held tasks: T3, T4, T13, T29; T5, T7, T10, T11, T12, T21

## Similar Implementations

**The spike itself** is the closest precedent for what this plan must do next: a bounded probe,
pre-registered, scoring candidates on the existing corpus and mutation suite. `test-guards <path>`
already accepts a candidate implementation and runs the same corpus and integrity claims against
it (`test-guards:12, 28-29`), so a new lexer can be scored without touching the shipped file.

**Python's `shlex`** is present in the stdlib (measured) and is not used anywhere in the
plugin. It tokenizes POSIX shell words with quote and backslash handling; it does not parse
`$( )` nesting.

**`git rev-parse --verify --quiet "$ref^{commit}"`** at `adversarial-review/SKILL.md:137` is
the plugin's one existing idiom for "is this a real commit", and `git merge-base` at `:233` its
one idiom for a base.

## Open Questions

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| Q1 | May the lexer take a dependency beyond the Python stdlib (`bashlex` is not installed; `shlex` is), or must a rebuilt lexer stay stdlib-only? The parent plan treated adding `shellcheck` and `python3` as a major-version change to what the plugin requires of its environment. | the candidate set for the lexer tracer bullet | Open |
| Q2 | May `adversarial-review` fetch `refs/pull/<N>/head` into a remote-tracking ref? The skill's stance is that checking a target out is "a state change nobody asked for"; a fetch writes a ref but touches no worktree. Without it, a PR not on the current checkout can only be reviewed at whatever `origin/<head>` last fetched. | the identity resolver's design | Open |
| Q3 | When a PR target's head branch is the current checkout, is the reviewed range the local `HEAD` (today, R9-T2), the PR's `headRefOid`, or both with the difference disclosed? This is the axis both mirror-image regressions (R9-T2/R9-T26 → R10-T3) sit on, and a fork PR with the same branch name makes name matching wrong in either direction. | the identity resolver's design, and R10-T3/T4/T13 | Open |
| Q4 | Does `--generated` join `check` and CI, given that after R9-T19 it is the only gate that fails on an unwaived survivor and it runs in minutes rather than the README's 80 seconds? | the tracer bullet's acceptance bar and R10-T17/T18's scope | Open |

## Next Steps

1. Resolve Q1–Q4 with `/wb:resolve_questions docs/plans/2026-09-28-guard_lexer_and_pr_identity`
   — Q1 and Q2 decide what the two tracer bullets may test.
2. Fire the two tracer bullets the breaker requires, pre-registered in `thoughts/`: score a
   tokenizer-based lexer against the 114-case corpus and the mutation sweep via
   `test-guards <path>`; and resolve PR #25's identity by `headRefOid` and `refs/pull/25/head`
   in a scratch clone, on a same-name fork if one can be constructed.
3. Review the research document.
4. Run `/wb:create_design docs/plans/2026-09-28-guard_lexer_and_pr_identity` to create design decisions.

## References

- Design: [design.md](design.md)
- Tasks: [tasks.md](tasks.md)
- Origin: `docs/plans/2026-09-17-adversarial_loop/review-log.md` → *Breaker, after round 10*
- Spike: `docs/plans/2026-09-17-adversarial_loop/thoughts/2026-09-18-check-guards-implementation-probe.md`
