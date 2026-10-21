---
project: pr_identity_contract
ticket: null
created: 2026-10-01
created_timestamp: 2026-10-01T17:39:07Z
status: approved
last_updated: 2026-10-02
designer: scraig
git_commit: b0ef6c0
git_branch: adversarial-loop-skill-research
repository: thescubageek/workbench
tags: [design, architecture, pr_identity_contract]
depends_on: research.md
design_approach: "C3 — one shipped predicate; the loop serves only its own checkout"
---

# Design: one contract for "the target, relative to this checkout"

> **Kept in the repository without its sibling records.** This design cites `research.md`,
> `tasks.md` and `thoughts/` records of the same plan. They are not in the repository. Each
> decision below is complete without them.
>
> Writing rules: [wb Technical English](../../../plugin/docs/reference/technical-english.md).

## Problem Statement

Three skills decide separately whether the PR or branch under review is the current checkout:
`resolve_identity` in `adversarial-review` Step 1, the Phase 0 rule and the Phase 2 block in
`adversarial-loop`, and the Step 1 block in `reply-to-claude` (research findings 1, 4, 5 and 6).
Phase 0 decides by testing whether free text starts with `HEAD` (research finding 2). Thirteen
review rounds patched these copies one at a time. Each patch moved the failure to a scenario that
the patch did not run, and the round-13 breaker tripped (research finding 9).

The tracer bullet ran the shipped code against 13 pre-registered scenarios. It scored 8 UNSAFE
cells: plans staged for targets the loop does not fix, a fix committed onto the wrong branch, a
push to the user's fork followed by an un-draft of the parent PR, and a silent exit over a missing
ledger (`thoughts/2026-10-01-identity-tracer-bullet.md`, Results). Until this is fixed, the loop
can publish a head that nobody reviewed, and the next review round will find the next copy.

### Success Metrics

- The committed scenario test scores 0 UNSAFE cells on the shipped skills. Today it would score 8.
- One file computes the relation between the target and the checkout. Today three blocks and one
  prose rule compute it.
- No consumer reads a ref name or a prefix to decide whether to fix, stage, publish or reply.

## Design Approach

One shipped script, `plugin/scripts/pr-identity`, is the only place the relation is computed. It
takes the target as an argument and prints closed-set `key=value` lines. Every consumer calls it
by `${CLAUDE_PLUGIN_ROOT}/scripts/pr-identity` and acts on the fields `fix` and `publish`, never on
a name.

`adversarial-loop` serves only a target that is this checkout. Phase 0 runs the script before
anything else. When `fix=no`, the loop refuses and names `/wb:adversarial-review <target>` as the
entry for that target. The loop's stop-after-step-2 rule is deleted, not repaired.

### Which skill serves which target

This is a rule of the contract, stated by the user on 2026-10-01:

- **`adversarial-loop` runs only on the current checkout's PR.** It fixes, commits and publishes,
  so its target must be this checkout. It accepts no target, or a target that resolves to this
  checkout (the current PR's number, the current branch's name, or a path in this tree). Any
  other target is refused before the review runs.
- **`adversarial-review` runs against any target**: a different PR, a different branch, or a
  path. It reads, reports and fetches at most one remote-tracking ref. For a target that is not
  this checkout, it writes and stages no round plan, so its report is the whole output.
- **The loop's refusal names the review.** For example: `PR 57 is not this checkout (cross) —
  NOT running the loop. To review it, run /wb:adversarial-review 57.`
- The skills' `argument-hint` lines and descriptions say the same.

### Why This Approach

- **It is the candidate that passed.** The predicate scored 0 UNSAFE cells. A structured field
  over three copies (C1) scored 1, and the shipped code 8 (exploration, Decision Record).
- **It removes the shared weakness.** Every C0 failure except two traced to a consumer that read a
  name or a prefix (bullet, "What this settles").
- **It follows a precedent.** A skill already calls a plugin script by
  `${CLAUDE_PLUGIN_ROOT}/skills/review-prep/nvim-helper.sh` (`plugin/skills/review-prep/SKILL.md:35`).
  The braced form is substituted at load under both install modes (research finding 8a).
- **It ends the copy problem by construction.** The breaker's rule is to stop patching and
  escalate (`plugin/docs/reference/review-ledger.md:102-116`). A single file cannot drift from
  itself.

## Technical Decisions

### Architecture

- **The predicate is a shipped script, not prose.**
  - Rationale: a block in one skill cannot be sourced by another, so prose forces copies. A
    script is executable, testable and named once.
  - Trade-off: `plugin/scripts/` gains a runtime dependency that skills call. Until now it held
    only maintainer tools and hooks.
  - Pattern reference: `plugin/skills/review-prep/SKILL.md:35`, `plugin/.claude-plugin/plugin.json:21-64`.
- **The script reads only facts it can check, and it decides once.** The facts are the target's
  kind, the PR's `headRefOid`, `headRefName`, `isCrossRepository` and head repository, and the
  current branch with its upstream remote and ref. The decision is the `relation` row in the
  table below.
  - Rationale: the 2026-09-28 design used descent only, and round 11 added the branch name. The
    bullet showed that neither is enough without the push destination (S11).
  - Trade-off: a branch with no upstream is never `own`. It reviews and fixes as the current
    checkout and does not publish.
- **"Own" means the push would land on the PR's head.** The PR is not cross-repository, `HEAD`
  descends from `headRefOid`, the push URL of the current branch's upstream remote is on the
  allow-list and names the PR's head repository, and its upstream ref is `refs/heads/<headRefName>`.
  - Rationale: this clears S3 (renamed), S11 (two remotes) and S2 (stacked) with one test
    (bullet, Results).
  - Trade-off: a renamed branch that tracks the PR head publishes. Today it is refused.
- **Publishing pushes to the place the predicate checked.** Phase 2 and Phase 4 push with an
  explicit `<push_remote> HEAD:<push_ref>` taken from the script. A bare `git push` is removed.
  - Rationale: bare `git push` follows the branch's upstream, which no guard checked
    (research finding 8).
  - Trade-off: none found. The refspec names the only branch the guard approved.
- **The loop serves only its own checkout (C3).** Phase 0 refuses any target with `fix=no` before
  the review runs.
  - Rationale: the review run on a non-own target had no owner for its plan or its dispositions
    (R13-T2). With no such run, the stop rule and the orphan plan both go.
  - Trade-off: `/wb:adversarial-loop <other PR>` stops working as a review-only command. The
    refusal names the standalone review instead.
- **Staging follows fixing.** `adversarial-review` Step 8 writes and stages a round plan only when
  the script printed `fix=yes`. Otherwise the report is the whole output, and the report says so.
- **A clean round writes a ledger row, and the ledger commit has no existence guard.** A missing
  ledger then exits non-zero.
  - Rationale: S12 and S12b (bullet). A ledger that was never written reads as clean
    (`plugin/docs/reference/review-ledger.md:24-25`).
  - Trade-off: the ledger gains one `clean-round` row per clean round.
- **Remote URLs are compared by host, owner and name. A URL the script cannot read goes to `gh`.**
  `pr-identity` reads each remote URL into host, owner and name, and compares the host with the base repository's host from `gh repo view --json nameWithOwner,url`. A remote on another host, such as `gitlab.com` or GitHub Enterprise, is never the PR's head repository, so it gives `elsewhere` and `publish=no`. A URL the script cannot read is resolved with `gh repo view <url>` only when it looks for the base remote. It never decides `own` (see the allow-list decision below).
  - Rationale: `publish=yes` must mean a push to `push_remote` `push_ref` lands on the PR's head. The first P1-T3 version compared owner and name only, so a same-name remote on another host gave `own`.
  - Trade-off: each URL that the base-remote search cannot read costs one `gh` call (see the call-budget decision).
  - Source: tasks.md Current Blockers, P1-T3 item 1 · Decided 2026-10-01
- **The call budget counts allow-listed URLs, and each other URL the base-remote search reads adds one cached call.**
  One `pr-identity` call makes at most three `gh` calls when every remote URL is on the allow-list, and two for hosted GitHub URLs. Each distinct other URL that the base-remote search reads adds at most one `gh repo view <url>` call, cached for the run. The own test makes no `gh` call. The fetch limit stays at one.
  - Rationale: the base-remote search keeps the `gh` fallback, and a file-path or user-less scp remote cannot be read locally. A hard cap would refuse a correct review for an odd URL.
  - Trade-off: the budget is not a fixed ceiling. S6 and S11 make 4 calls because their remotes are file paths. Measured after PD4: P1 and the H and I rows make 3. A test counts the calls in a hosted-URL world and asserts 2.
  - Source: tasks.md Current Blockers, P1-T3 item 2 · Decided 2026-10-01
- **The `gh repo set-default` case is measured against real `gh`, then pinned by a committed scenario.**
  A new assumption, A5, records what `gh repo view` and `gh pr view` return in a scratch `git clone` after `gh repo set-default`. The stub then honours `remote.<name>.gh-resolved` the same way. A scenario makes name-ranking and repository-matching disagree, and expects the repository-matched remote.
  - Rationale: the stub ranks remotes by name, so no test can tell the two rules apart. The first reproduction of the failure used a `gh-resolved` behaviour that nobody measured.
  - Trade-off: this edits `plugin/scripts/fixtures/gh-stub`, which P1-T2 promoted unchanged. The stub change stays as small as the measurement allows.
  - Source: tasks.md Current Blockers, P1-T3 item 3 · Decided 2026-10-01
- **`publish=yes` needs a URL from a strict allow-list. The `gh` fallback only reads.**
  A remote URL can make `publish=yes` only if it matches one exact grammar: `https://` with optional credentials and port, `ssh://` with optional user and port, or `user@host:owner/name`. Host uses `[A-Za-z0-9.-]`, owner and name use `[A-Za-z0-9._-]`, userinfo uses `[A-Za-z0-9._~-]`, and no `%` appears anywhere in the authority. Any other URL is never `own`, so it gives `elsewhere` and `publish=no`. The `gh repo view <url>` fallback stays for finding the base remote to fetch and review from. It never decides `own` or `publish`.
  - Rationale: git and a hand-written parser read some URLs differently. Four verification rounds found `@` in a path, then `%` in `ssh://` userinfo, each giving `publish=yes` for a push to another host. An allow-list fails closed. The fallback trusts the host that `gh` reports, which nothing checks against where `git push` goes.
  - Trade-off: a remote written in any other form can review and fix but cannot publish, for example `ssh.github.com:443`, an ssh-config alias, `git://`, and a local path. This narrows the PD1 decision on the publish side only, because a URL the script cannot read no longer reaches `gh` for the own test.
  - Source: tasks.md Current Blockers, P1-T3 fourth attempt · Decided 2026-10-01
- **A missing block fails every scenario that needs it. The baseline does not model the old prose rules.**
  `test-pr-identity --skills-at b0ef6c0` exits non-zero. S11 and S12b score UNSAFE through their extracted blocks. S2 to S8 fail because the Phase 0 or Step 8 block they need is missing.
  - Rationale: 6 of the bullet's 8 UNSAFE cells (S2 to S6, S8) came from prose rules that the spike modelled by hand (`thoughts/spike/harness.sh:150`, `:180`). A test that models them again keeps a hand-written copy of the rules this plan removes.
  - Trade-off: the baseline shows 2 UNSAFE cells and 6 missing-block failures, not 8 UNSAFE cells.
  - Source: design.md PD5 · Decided 2026-10-01
- **The consumer-level scorer takes its expected rows from the relation table in Data Model, not from the pre-registered tracer-bullet table.**
  The test header lists each place where the two differ: S3 is `own`, S11 reviews the fetched PR head, S2, S4, S5, S6 and S8 refuse before the review because `fix=no`, and S12 expects a committed `clean-round` row.
  - Rationale: the design is approved and it is what the skills implement. A literal port of `thoughts/spike/score.py` reports false MISS cells where the design decided a cell the table left open or scored differently.
  - Trade-off: the pre-registered table stays as it was run, so it no longer matches the committed test row for row.
  - Source: design.md PD6 · Decided 2026-10-01
- **`reply-to-claude` Step 4c re-runs `pr-identity` before it posts. Steps 2 and 4a only re-state `target`.**
  Step 4c refuses unless `pr` equals the number that Step 1 printed, which the model re-types into the block, and Step 1's proceed rule (`relation=own`, or `HEAD` equals `head_oid`) still holds. Steps 2 and 4a get a `target=""` re-statement line and no identity check.
  - Rationale: Step 4c's `gh pr comment` (`reply-to-claude/SKILL.md:149`) is the skill's only outward action, so it gets the same check as the loop's Phase 5. Steps 2 and 4a only read.
  - Trade-off: one more `pr-identity` call per reply. A read-only step that resolves a different PR is caught at Step 4c, not where it happens.
  - Source: design.md PD7 · Decided 2026-10-01
- **The loop never fetches. `pr-identity --no-fetch` classifies a PR target without writing a ref.**
  `adversarial-loop` Phase 0 and the Phase 2, 4 and 5 re-runs pass `--no-fetch`. With the flag, a PR target that is not `own` still gets its `relation`, `fix=no`, `publish=no` and `reason`, and the script prints `review_head=-` and writes no ref. `adversarial-review` does not pass the flag and keeps the one disclosed fetch.
  - Rationale: the loop serves only branches developed in this checkout. It must not pull a remote branch and then refuse it. The user stated the rule on 2026-10-01: a review of a remote branch is fine, and the loop is for local development only.
  - Trade-off: the script gains one flag and the predicate test gains rows for it. The review and the loop still share one predicate, and only the fetch differs.
  - Source: design.md PD8 · Decided 2026-10-01

### Data Model

The script's output contract. Each line is `key=value`. The values of `relation`, `fix` and
`publish` are a closed set. The other values are refs, oids and numbers that consumers pass on
and never compare as text.

| Key | Values | Meaning |
| --- | ------ | ------- |
| `relation` | `own`, `none`, `branch`, `stacked`, `elsewhere`, `detached`, `cross`, `other` | see the relation table |
| `fix` | `yes`, `no` | the reviewed tree is this checkout, so fixes may be committed here |
| `publish` | `yes`, `no` | a push to `push_remote` `push_ref` lands on the PR's head |
| `pr` | a number, or `-` | the PR the target resolved to |
| `head_oid` | an oid, or `-` | the PR's `headRefOid` |
| `review_head`, `review_base` | refs | the range endpoints for `adversarial-review` |
| `pathspec` | a path, or empty | set for a path target |
| `push_remote`, `push_ref` | a remote and `refs/heads/<name>`, or `-` | set only when `publish=yes` |
| `reason` | prose | why `relation` is not `own`, for the report |

It also prints one `identity:` line for the report. No consumer tests that line.

The relation table. The kind of the target is decided first:

- no target, a path that exists, or a name equal to the current branch → the current checkout
- all digits → a PR
- anything else → a branch

| `relation` | When | `fix` | `publish` | `review_head` |
| ---------- | ---- | ----- | --------- | ------------- |
| `own` | a PR, as "own" is defined above | `yes` | `yes` | `HEAD` |
| `none` | the current checkout, and `gh` finds no PR for it | `yes` | `no` | `HEAD` |
| `branch` | a branch target that is not the current branch | `no` | `no` | the branch |
| `stacked`, `elsewhere` | descends from `headRefOid`, but the upstream is not the PR's head | `yes` for the current checkout, else `no` | `no` | `HEAD`, else the fetched PR head |
| `detached` | descends from `headRefOid`, and `HEAD` is detached | as above | `no` | as above |
| `cross` | `isCrossRepository` is not exactly `false` | as above | `no` | as above |
| `other` | `HEAD` does not contain `headRefOid` | as above | `no` | as above |

"As above" means: when the target is the current checkout, `fix=yes` and `review_head=HEAD`.
When the target is a PR number, `fix=no` and the review reads the fetched PR head.

**Exit status**: 0 when resolved. 1 when refused: `gh` could not answer, no remote points at the
PR's base repository, the fetch failed, or a ref did not resolve. 2 on bad usage. A refusal names
its cause on stderr with the existing `— NOT reviewing` wording.

**The one write**: unless `--no-fetch` is given (PD8), for a PR target whose relation is not `own`, the script fetches
`refs/pull/<N>/head` into `refs/remotes/<base remote>/pr/<N>`. The base remote is the remote
whose URL resolves to the PR's base repository, not `origin` by name. The write stays disclosed,
not confirmed (`plugin/skills/adversarial-loop/SKILL.md:84-89`).

### Integration Points

- **`adversarial-review` Step 1** calls the script in place of `resolve_identity`. It keeps the
  `rev-parse --verify` check, the `identity:` and `range:` lines, and Step 2's re-statement from
  the `range:` line.
- **`adversarial-review` Step 8** writes and stages a plan only on `fix=yes`.
- **`adversarial-loop` Phase 0** calls the script first. `fix=no` refuses. `fix=yes, publish=no`
  runs Phase 1 and skips Phases 2 to 5 with `reason`. `fix=yes, publish=yes` runs every phase.
- **`adversarial-loop` Phases 2, 4 and 5** call the script again in the block that acts. Each
  requires `publish=yes` and the same `pr`. Phases 2 and 4 push with the explicit refspec.
- **`adversarial-loop` Phase 1 step 5** writes a `clean-round` row on a clean round and commits
  the ledger with no `[ -f ]` guard.
- **`reply-to-claude` Step 1** calls the script. It proceeds when `relation=own`, or when `HEAD`
  equals `head_oid`. Step 4c re-runs it before `gh pr comment` and requires the same `pr` (PD7). Its refusals name both refs and the relation. They do not tell the user to
  push, reopen a PR, or check out a branch the checkout is already on (R13-T4).
- **`plugin/scripts/check`** runs a new `test-pr-identity`.
- **`review-ledger.md`** documents the `clean-round` row.

## Scope Definition

### In Scope

- `plugin/scripts/pr-identity`, its output contract and its exit codes.
- The consumers listed under Integration Points, in all three skills.
- `plugin/scripts/test-pr-identity`. It is promoted from `thoughts/spike/` and runs the 13
  scenarios against the shipped script, with the Phase 2, reply and ledger blocks extracted from
  the shipped `SKILL.md` files. It joins `plugin/scripts/check`.
- R13-T1, R13-T2, R13-T3 and R13-T4. Each closes by pointer to this plan's task.
- A non-normative notice at the top of the identity sections of
  `docs/plans/2026-09-28-guard_lexer_and_pr_identity/design.md` that points here.
- The 3.0.0 `CHANGELOG.md` entry, and `plugin/scripts/README.md` for the new script and test.
- The `adversarial-loop` and `adversarial-review` `argument-hint` lines, descriptions and README rows, so they state which skill serves another PR.

### Out of Scope

- R13-T5, R13-T6 and R13-T7. They stay ordinary round-13 tasks.
- Pushing to a cross-repository PR's fork, even where `maintainerCanModify` allows it.
- Phase 3 polling and the Phase 5 check-run gate, apart from the PR resolution.
- Changing how the review chooses lenses, verifies findings or assigns dispositions.

## Success Criteria

### Functional Requirements

- [ ] `test-pr-identity` scores 0 UNSAFE cells over S1 to S12b on the shipped skills. It fails
      when the shipped skills at `b0ef6c0` are substituted.
- [ ] `/wb:adversarial-loop 57` on a checkout that is not PR 57 refuses before any review, fetch or write, and names `/wb:adversarial-review 57`. The loop passes `--no-fetch`, so no ref is written (PD8). `/wb:adversarial-review 57` on the same checkout reviews PR 57's fetched head and stages no plan.
- [ ] `/wb:adversarial-loop HEAD-fix` on `feature-B` refuses before the review and names
      `/wb:adversarial-review HEAD-fix` (S8, R13-T1).
- [ ] `/wb:adversarial-loop feature-A` on `feature-A` reviews, fixes and publishes PR 42 (S7, R13-T1).
- [ ] No run on a target with `fix=no` writes or stages a round plan (S2 to S6, R13-T2).
- [ ] In a clone whose `origin` is the user's fork and `upstream` the parent, Phase 2 refuses to
      publish the parent's PR from a branch that tracks the fork (S11).
- [ ] A path target on a PR's own branch publishes that PR (S10).
- [ ] A ledger missing at commit time exits non-zero, and a clean round leaves a committed
      `clean-round` row (S12, S12b, R13-T3).
- [ ] No `reply-to-claude` refusal contains `push` or `check out its branch` (S4, S6, R13-T4).
- [ ] `grep` finds no `--is-ancestor`, `isCrossRepository` or `git branch --show-current` in the
      three `SKILL.md` files. The test lives only in `pr-identity`.

### Non-Functional Requirements

- [ ] Performance: one `pr-identity` call makes at most three `gh` calls when every remote URL is on the allow-list (two for hosted GitHub URLs), plus one cached call for each other URL that the base-remote search reads, and at most one fetch. The own test makes no `gh` call.
- [ ] Reliability: `./plugin/scripts/check` passes, including `shellcheck-gate` on the new script.
- [ ] Security: the script never pushes, never checks out, and never writes a ref other than
      `refs/remotes/<base remote>/pr/<N>`.

## Risk Analysis

### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| The real `gh pr view` with no argument resolves a PR the stub did not model | Med | Med | A1. For the current-checkout kind, the script classes a PR whose `headRefName` differs from the current branch as not `own`, so it does not publish |
| A model types the target into the call wrongly, as with `target=""` | Med | Low | The call takes the target as one quoted argument. `check-guards` shape 6 keeps positional tokens out |
| A user relied on the loop as a review-only command for other PRs | Low | Low | The refusal names the standalone command |
| `shellcheck` or `check-guards` flags the new script | Low | Med | Both run in `check` |

### Assumptions

| ID | Assumption | Validated? |
| -- | ---------- | ---------- |
| A1 | With no argument, the real `gh pr view` resolves the current branch's PR by its head branch, as the stub did. A branch made by `gh pr checkout` resolves to the same PR | Validated 2026-10-01 (On this branch `gh pr view --json number,headRefName` returns number 25 and headRefName `adversarial-loop-skill-research`. In a scratch clone `gh pr checkout 25` made a branch of that name and the same call returned 25 with that name. `branch.adversarial-loop-skill-research.remote` is `origin` and `.merge` is `refs/heads/adversarial-loop-skill-research` in both. A first attempt with a `gh repo clone` scratch failed with a missing remote ref for another branch, so the clone was redone with plain `git clone`) |
| A2 | `git for-each-ref` `%(upstream:remotename)` and `%(upstream:remoteref)` exist in every git the plugin supports | Validated 2026-10-01 (Minimum is git 2.16.0. Its release notes, `Documentation/RelNotes/2.16.0.adoc` in git/git, say `for-each-ref` learned to show the remote name and ref for `upstream` and `push`. The merge `093048b229` is in v2.16.0 and not in v2.15.0. Also present in git 2.54.0 here) |
| A3 | `gh repo view <remote URL>` returns `nameWithOwner` for both `https://` and `git@` remote URLs | Validated 2026-10-01 (`gh repo view git@github.com:thescubageek/workbench.git --json nameWithOwner` and the `https://github.com/thescubageek/workbench.git` form both exit 0 and return `{"nameWithOwner":"thescubageek/workbench"}`) |
| A4 | `${CLAUDE_PLUGIN_ROOT}` in a skill body is substituted at load under `--plugin-dir` and under a marketplace install | Validated 2026-10-01 (research finding 8a) |
| A5 | After `gh repo set-default <repo>` in a clone, `gh repo view` and `gh pr view` answer for the `remote.<name>.gh-resolved=base` remote, not the name-ranked one | Validated 2026-10-01 (gh 2.86.0. Scratch `git clone https://github.com/thescubageek/workbench.git` plus `upstream` = `https://github.com/cli/cli.git`. Without a default, `git config --get-regexp 'remote\..*gh-resolved'` prints nothing, `gh repo view --json nameWithOwner,url` returns `cli/cli` and `gh pr view 25 --json number,url` returns `https://github.com/cli/cli/pull/25`. After `gh repo set-default thescubageek/workbench` the config holds `remote.origin.gh-resolved base`, and the same calls return `thescubageek/workbench` and `https://github.com/thescubageek/workbench/pull/25`). Re-measured 2026-10-01 by the user, in an interactive terminal, with the same two remotes. The "after" half holds: `gh repo view` returns `thescubageek/workbench`. The "before" half differs: `gh repo view` and `gh pr view 25` both fail with `No default remote repository has been set` and `please run gh repo set-default`, instead of answering for `cli/cli`. So the name ranking is what a non-interactive `gh` does, as in the headless measurement and in the stub, and an interactive `gh` refuses when two remotes resolve to different repositories and no default is set. `pr-identity` runs non-interactively and treats a `gh` failure as a refusal, so both behaviours are safe) |

## Rejected Alternatives

### Option: C2 — one script, the loop reviews any target and stops

- **Approach**: the same script, with the loop still reviewing a `fix=no` target and stopping
  after step 2.
- **Rejected because**: its cells are C3's, and it keeps a stop rule and a review run whose plan
  and dispositions have no owner (R13-T2).
- **Trade-offs**: it keeps the loop as a review entry for any target.

### Option: C1 — a structured field over three copies

- **Approach**: `resolve_identity` prints `checkout: own|other`. Phase 2 and reply keep their
  guards, and Phase 2 gains a push check.
- **Rejected because**: it failed S11 as tested, and the fix is one more patch to one copy.
- **Trade-offs**: the smallest diff.

### Option: the predicate inline in `adversarial-review`

- **Approach**: one function in Step 1. The loop and reply copy it.
- **Rejected because**: another skill cannot source a block, so the copies remain.
- **Trade-offs**: no new shipped script.

### Option: keep the harness as a spike

- **Approach**: re-run `thoughts/spike/harness.sh` by hand each round.
- **Rejected because**: rounds 11 to 13 found every defect by hand, and a committed test is what
  makes the class fail early.
- **Trade-offs**: no new gate in `check`.

### Option: absorb all seven held round-13 tasks

- **Rejected because**: R13-T5, R13-T6 and R13-T7 are not about identity.

## Pending Decisions

| ID | Decision Needed | Blocks | State |
| -- | --------------- | ------ | ----- |
| PD1 | How `pr-identity` compares hosts for the own test | P1-T3 | Resolved 2026-10-01 → design.md (## Technical Decisions) |
| PD2 | The `gh` call budget when a remote URL is unreadable | P1-T3 | Resolved 2026-10-01 → design.md (## Technical Decisions) |
| PD3 | Whether a committed test pins the `gh repo set-default` base-remote case | P1-T3 | Resolved 2026-10-01 → design.md (## Technical Decisions) |
| PD4 | Which remote URLs may give `publish=yes`, and whether the `gh` fallback may decide it | P1-T3 | Resolved 2026-10-01 → design.md (## Technical Decisions). Narrows PD1 on the publish side |
| PD5 | What `test-pr-identity --skills-at b0ef6c0` must show, when 6 of the bullet's 8 UNSAFE cells came from prose rules the harness modelled by hand (`spike/harness.sh:150`, `:180`) | P2-T1, Phase 2 success criteria | Resolved 2026-10-01 → design.md (## Technical Decisions) |
| PD6 | Which expected table the consumer-level scorer follows, where the design and the pre-registered table differ (S3, S11, and `fix=no` refusals) | P2-T1 | Resolved 2026-10-01 → design.md (## Technical Decisions) |
| PD7 | Whether `reply-to-claude` Steps 2, 4a and 4c (`SKILL.md:89`, `:133`, `:148`) must check that they resolved the same `pr` as Step 1 | P2-T7 | Resolved 2026-10-01 → design.md (## Technical Decisions) |
| PD8 | Whether `adversarial-loop` may fetch a PR head before it refuses, given that the script fetches for any non-own PR target | P2-T8 | Resolved 2026-10-01 → design.md (## Technical Decisions). The loop never fetches |

## References

- Research: [research.md](research.md)
- Exploration: [thoughts/2026-10-01-pr-identity-contract.md](thoughts/2026-10-01-pr-identity-contract.md)
- Tracer bullet: [thoughts/2026-10-01-identity-tracer-bullet.md](thoughts/2026-10-01-identity-tracer-bullet.md), harness in `thoughts/spike/`
- Superseded: `../2026-09-28-guard_lexer_and_pr_identity/design.md` (its identity sections)
- Inputs: `../2026-09-17-adversarial_loop/handoff-2026-10-01-10-34.md`, `../2026-09-17-adversarial_loop/reviews/2026-10-01-round-13/tasks.md`
