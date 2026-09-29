---
created: 2026-09-28
type: tracer-bullet
project: guard_lexer_and_pr_identity
topic: does resolving a PR by headRefOid refuse the same-name fork case that name matching accepts, and does the pull-ref fetch work
status: run
git_commit: 2eaa15f
git_branch: adversarial-loop-skill-research
---

# Tracer bullet: PR identity by commit

**Pre-registered** in `2026-09-28-lexer-and-pr-identity.md` → Decision Record — PR identity:
construct a fork PR whose branch name matches the local checkout, show the OID test refuses
where the name test proceeds, and show the fetch spelling works in a fresh clone.

**Predicted**: the shipped name test rewrites the range to `...HEAD` and reviews the
maintainer's own commits under the PR's number; the OID test refuses with a named reason; the
fetch lands `refs/remotes/origin/pr/<N>` at `headRefOid` and touches no worktree.

## Fixture

cwd `/tmp/wb-identity-probe/origin-src` (`pwd -P` the same; not a Conductor path). Built and
deleted in one session, 2026-09-28. A repository with `main` at `720753f`, a **local** branch
`patch-1` at `9a3b1c5` ("maintainer's own patch-1"), and a **fork** commit `8460be3`
("contributor's patch-1 (fork)") that is a sibling of `patch-1` off `main` and exists locally
only as `refs/pull/57/head`, then pushed to a bare origin as `refs/pull/57/head` — the ref
GitHub serves for every PR. A stub `gh` on `PATH` answered `gh pr view 57` with
`headRefName: patch-1`, `isCrossRepository: true`, `headRefOid: 8460be3…`, `baseRefName: main`.

## Run 1 — name test versus OID test (verbatim)

```text
local patch-1 HEAD=9a3b1c5f629778c97285a9c84d19455abd649ea5  fork headRefOid=8460be3b249c2d0787b8d63e957cb56ebb1a9934  base=720753f469e610bdc898a311e55082827e0e533a

=== NAME TEST (shipped Step 1 logic, verbatim shape) ===
name test resolves range: origin/main...HEAD   (right endpoint 9a3b1c5)
=== OID TEST (candidate I-A) ===
REFUSE: PR 57 is cross-repository; local branch 'patch-1' is not its head (headRefOid 8460be3) — fetch refs/pull/57/head to review it
HEAD does NOT descend from headRefOid 8460be3: local patch-1 is a different commit
```

The name test — `[ "${range##*...origin/}" = "$(git branch --show-current)" ]` from
`adversarial-review/SKILL.md:125` — matched `patch-1` to `patch-1` and rewrote the range to end
at local `HEAD`, `9a3b1c5`, the maintainer's commit. It would have reported that as a review of
PR 57. The OID test read `isCrossRepository` and refused by name, and `git merge-base
--is-ancestor 8460be3 HEAD` confirmed local `HEAD` does not descend from the PR's head.
**R10-T3's scenario, reproduced; prediction held.**

## Run 2 — the fetch spelling

First attempt failed on the fixture, not the design: `git clone --bare` copies branches and
tags only, so `refs/pull/57/head` was absent from the fake origin
(`fatal: couldn't find remote ref refs/pull/57/head`). After
`git push origin refs/pull/57/head:refs/pull/57/head`:

```text
pull ref now on the fake origin: 8460be3
=== FETCH SPELLING, fake origin ===
fetched origin/pr/57 = 8460be3
worktree changes: 0; branch: patch-1
=== review range the resolver would use ===
origin/main...origin/pr/57 ->  1 file changed, 1 insertion(+), 1 deletion(-)
```

`git fetch origin refs/pull/57/head:refs/remotes/origin/pr/57` wrote one remote-tracking ref
equal to `headRefOid`, changed nothing in the worktree, and left the branch on `patch-1`. The
range `origin/main...origin/pr/57` then diffs the contributor's change, not the maintainer's.

Against the real remote, in a fresh clone of `thescubageek/workbench` under `/tmp` (deleted
afterwards):

```text
=== FETCH SPELLING, real GitHub remote ===
origin/pr/25 = 3b4e04b; headRefOid from gh = 3b4e04b
```

**Prediction held.** The fixture lesson is itself a finding for the design: a test origin
built with `git clone --bare` does not carry pull refs, so any fixture for this resolver must
push them explicitly.

## What this settles for the design

- The resolver reads `headRefOid` and `isCrossRepository` from `gh pr view`; both fields are
  present in `gh` 2.x's `--json` surface (measured in research and here).
- On the PR's own checkout, "own" is `git merge-base --is-ancestor "$headRefOid" HEAD`, not a
  branch-name comparison. A descendant reviews to `HEAD` and discloses the delta; a non-descendant
  or a cross-repository PR refuses by name and offers the fetch.
- The fetch spelling is `git fetch origin "refs/pull/$N/head:refs/remotes/origin/pr/$N"`; it
  writes exactly one ref and is named in the report.
- The refusal and the fetch both `return`, never `exit`, per the Step 1 discipline.

## Not measured

A same-repository PR whose branch name matches but whose head is ahead of `origin/<head>` after
a push from another machine (R10-T4's stale-remote case). The OID comparison covers it by
construction — `headRefOid` is the source of truth, not `origin/<head>` — but no fixture here
exercised it.
