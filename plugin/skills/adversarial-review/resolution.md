# Resolving the target

**Read this when Step 1 directs you to**, after the block runs. It says what each outcome of the
block means and what to report, and why the block is shaped as it is.

## What the block printed

**The relation between the target and this checkout is decided in
[`pr-identity`](../../scripts/pr-identity), not in the Step 1 block.** The script's header and its
`relation` cases are the conditions. The block reads the `review_head`, `review_base` and
`pathspec` fields by key and does not re-derive them. For a PR target whose `relation` is not
`own`, the script fetches the PR's head into `refs/remotes/<base remote>/pr/<N>` and the range
ends there. The `identity:` line names the result. Copy that line into the report as it is
printed.

**An empty range and an unresolvable one are different, and only one of them is a stop.** Five
outcomes, and the last is dangerous precisely because it wears the first one's clothes:

- **Resolved, and empty** — the range parsed and the stat is blank. If that is genuinely the
  change, or is plainly not what was asked for, stop and say so rather than reviewing nothing.
- **Fetched** — the target is a PR number and `relation` is not `own`. The `identity:` line
  reads `<base remote>/pr/<N> = <oid> (<relation>: <reason>)`. The fetch writes that one
  remote-tracking ref and nothing else. Disclose it in the report. It needs no confirmation.
- **Refused** — `pr-identity` exited non-zero: `gh` could not answer for the PR, no remote points
  at the PR's base repository, or the fetch of `refs/pull/<N>/head` failed. The script names the
  cause on stderr and the block returns 1. The review did not run. Say that in the report, and do
  not review the current branch in its place.
- **Not resolved** — an endpoint is not a revision here. The block says which, on stderr, and
  returns. Say that in the report; do not report it as a change with no content.
- **Resolved to something git cannot parse** — the outcome with no error to show for it. Measured
  in this repository: `git diff --stat "origin/main...plugin/skills/adversarial-review/*.md"`
  exits **0 printing nothing**, indistinguishable from an empty diff, because git takes a
  wildcard-bearing argument as a *pathspec* rather than a revision and that pathspec matches no
  file. Drop the wildcard and the same mistake is `fatal: ambiguous argument`, exit 128, written
  to stderr with nothing reading it. The `git rev-parse --verify` pass over both endpoints is what
  turns both into the second outcome before any stat is printed.

**The base is asked for, not assumed.** `origin/main` is this repository's default, not every
repository's, and an earlier version of the Step 1 block hardcoded it in three of its four branches
while `git diff --stat origin/nonexistent...HEAD` exits 128 onto stderr — measured, and nothing in
the old block read it. `pr-identity` now asks `gh` for the target's base branch. When no PR
answers, it uses the default branch of the repository: `gh`'s `defaultBranchRef`, then
`<remote>/HEAD`, then `main`. Step 2 reads `REVIEW.md` from the same base. What breaks a hardcoded base —
`master`, `develop`, a shallow or single-branch clone, a fork checkout — is enumerated once, in
Step 2's ⛔ note; it is not restated here.

## Why the block is shaped this way

⛔ **The skill's blocks run under zsh, not bash.** The Bash tool's shell is `/bin/zsh`, so a fenced
`bash` block in SKILL.md is executed by a shell that does **not** word-split unquoted expansions and
does **not** define `PIPESTATUS`. Both bit SKILL.md: `git diff --stat $range` died with
`fatal: ambiguous argument` the first time anyone passed a path target, and the blast-radius
guard in Step 3 could never fire. Quote every expansion, keep a pathspec in its own variable,
and take an exit status from `$?` on the line after the command rather than from a pipeline.

⛔ **A failure in the Step 1 block `return`s; it must never `exit`.** The Bash tool runs an entire call in one
shell, so `exit 1` inside a fenced block ends that shell and not just the block: measured, a call
of `false || { echo "failing" >&2; exit 1; }` followed by `echo "THIS SHOULD NOT PRINT"` printed
only `failing`, and everything queued after it silently never ran. That is why the resolution is a
function — `return 1` stops the resolution, leaves the rest of the call alive, and still prints
the loud line, which is the part that must survive: "could not resolve PR N — NOT reviewing the
current branch" must never be followed by a review of the current branch.

⛔ **One branch runs, and the branch is real.** An earlier version of Step 1 listed the three
forms as three consecutive `range=` assignments separated only by comments. A fenced `bash` block
in SKILL.md is executed — `plugin/scripts/check-guards` scans these blocks for exactly that reason — so
all three ran, the last won, and a PR-number target silently became the current branch while the
report still named the PR.
