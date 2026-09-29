---
project: guard_lexer_and_pr_identity
ticket: null
created: 2026-09-28
created_timestamp: 2026-09-28T20:05:58Z
status: draft
last_updated: 2026-09-28
designer: scraig
git_commit: 662d93b30fe5cbb06ab8d9073b7d75f4128cc4c3
git_branch: adversarial-loop-skill-research
repository: thescubageek/workbench
tags: [design, architecture, guard_lexer_and_pr_identity]
depends_on: research.md
---

# Design: guard_lexer_and_pr_identity

**Created**: 2026-09-28 20:05 UTC
**Designer**: scraig
**Ticket**: N/A

<!-- Status lives in frontmatter `status:` only. Do not restate it here: it is the field
     /wb:create_tasks and forge gate on, it changes, and a second copy goes stale the moment
     the design is approved. `created` and `ticket` are repeated above because they never
     change after creation. -->

## Problem Statement

[What problem we're solving and why - to be filled by /wb:create_design]

### Success Metrics

- [ ] [To be defined]

## Design Approach

[High-level solution approach - to be added]

### Why This Approach

- [To be added from design analysis]

## Technical Decisions

### Architecture

- [To be defined]

### Data Model

- [To be defined]

### Integration Points

- [To be identified]

### Resolved Decisions

- **The `check-guards` lexer stays stdlib-only.** `import os, re, sys` today; a rebuilt lexer
  adds nothing outside the Python standard library (`shlex` is available and unused; `bashlex`
  is not installed).
  - Rationale: the parent plan's PD2 made adding `shellcheck` and `python3` to what `check`
    requires a major-version change; a third-party parser is the same class of change. The
    tracer bullet's winning candidate needs none.
  - Trade-off: `$( )` nesting and backslash escapes are hand-written rather than borrowed.
  - Source: research.md Q1 · Decided 2026-09-28

- **`adversarial-review` may fetch a PR's head ref, as a named and disclosed step.** When a PR
  target's head is not the current checkout (a cross-repository PR, or a same-repository PR
  whose head is not an ancestor of `HEAD`), the resolver runs
  `git fetch origin "refs/pull/$N/head:refs/remotes/origin/pr/$N"`, reports the ref it wrote,
  and reviews `origin/pr/$N`. Nothing else is written; no checkout, no branch, no worktree
  change.
  - Rationale: the skill's rule is that checking a target out is a state change nobody asked
    for; a remote-tracking ref is the same class of write any `git fetch` performs and is the
    only way the loop reviews a PR the user is not on, which the parent plan's Q4 requires.
    Measured in the identity tracer bullet: one ref written, worktree and branch untouched, on
    a fake origin and on GitHub.
  - Trade-off: a test origin must carry pull refs explicitly — `git clone --bare` does not copy
    them.
  - Source: research.md Q2 · thoughts/2026-09-28-lexer-and-pr-identity.md (I-A) · Decided 2026-09-28

- **A PR target's head is its commit, not its branch name, and "own checkout" means descent.**
  The resolver reads `headRefOid` and `isCrossRepository` from `gh pr view`. If
  `git merge-base --is-ancestor "$headRefOid" HEAD` holds and the PR is not cross-repository,
  the reviewed range ends at local `HEAD` and the report discloses the commits ahead of the
  PR's head. Otherwise the resolver refuses by name and offers the fetch above. Steps 1 and 2
  resolve once, in one function Step 2 reads from.
  - Rationale: the mirror-image pair R9-T2/R9-T26 → R10-T3 came from two copies of a
    branch-name comparison; a same-name fork PR made it review the maintainer's own commits
    under the PR's number (reproduced in the identity tracer bullet). Descent by OID is the
    test the name comparison was standing in for.
  - Trade-off: a same-repository PR whose head moved on another machine reviews the fetched
    OID, not `origin/<head>` at the last fetch — R10-T4 closed by construction, unmeasured.
  - Source: research.md Q3 · thoughts/2026-09-28-lexer-and-pr-identity.md (I-A) · Decided 2026-09-28

- **The generated mutation sweep joins CI, not `check`.** `.github/workflows/checks.yml` gains a
  job that runs `./plugin/scripts/test-guards --generated` on every pull request; `check` keeps
  its seven gates and its ~20-second runtime. The README's "~80 seconds" figure is corrected to
  what the sweep measures (about 4 minutes on this machine, 12 once).
  - Rationale: after R9-T19 the sweep is the only gate that fails on an unwaived survivor.
    Left manual, that invariant depends on memory, and this plan measured the result — shape 4
    regrew 16 survivors while the kill-count ratchet stayed green. CI runs on every PR anyway;
    the sweep is deterministic (in-process AST mutants under an alarm) and its ratchet file is
    already committed, so CI needs no new state.
  - Trade-off: a slower CI run; a survivor found only in CI is fixed after the push, not before.
  - Source: research.md Q4 · Decided 2026-09-28

## Scope Definition

### In Scope

- [To be defined]

### Out of Scope

- [To be defined]

## Success Criteria

### Functional Requirements

- [ ] [To be defined]

### Non-Functional Requirements

- [ ] [To be defined]

## Risk Analysis

[To be evaluated]

### Assumptions

| ID | Assumption | Validated? |
| -- | ---------- | ---------- |
| — | [none yet] | — |

## Rejected Alternatives

[To be documented during design]

## Pending Decisions

| ID | Decision Needed | Blocks |
| -- | --------------- | ------ |
| — | [none yet] | — |

## References

- Research: [research.md](research.md)
- Tasks: [tasks.md](tasks.md)
- Related: `docs/plans/2026-09-17-adversarial_loop/review-log.md` (Breaker, after round 10)
