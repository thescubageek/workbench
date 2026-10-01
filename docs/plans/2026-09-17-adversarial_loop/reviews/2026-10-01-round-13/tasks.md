---
project: adversarial_loop
reviews: docs/plans/2026-09-17-adversarial_loop
round: 13
created: 2026-10-01
status: in-progress
total_tasks: 7
completed_tasks: 0
task_tracking: markdown-checkboxes
---

# Remediation — adversarial review round 13

Target: PR #25 on its own checkout, `origin/main...HEAD` at `72f8210`. A re-review of round 12's
fixes. **HELD: the breaker tripped (see the Implementation notes). No task here is worked until
the user decides.**

## How each task is verified

Every task carries its finding's `failure_scenario` as its acceptance criterion, and **the
criterion is run before the fix**. A criterion that passes before the change is not a criterion.

## Tasks

- [ ] **R13-T1** — `plugin/skills/adversarial-loop/SKILL.md:136` (also
      `plugin/skills/adversarial-review/SKILL.md:131`) — Phase 0's stop rule keys on the identity
      line starting with `HEAD`, which a branch target named like `HEAD-fix` satisfies, while a
      branch target naming the current branch does not.
      **Fails when:** on feature-B, `/wb:adversarial-loop HEAD-fix` prints `identity: HEAD-fix
      (branch; base origin/main)`, the rule does not fire, and steps 3 to 6 commit another
      branch's fixes onto feature-B; `/wb:adversarial-loop feature-B` on feature-B stops after step
      2 and never fixes the branch you are on.
      **Acceptance (shape 1)**: run `resolve_identity` in a scratch repo for targets `HEAD-fix`,
      the current branch and a PR number; assert only own-checkout lines match the rule's test
      (a leading `HEAD (`), and a branch target equal to the current branch gets HEAD provenance.
      RED today: `HEAD-fix` matches, the current-branch target does not. (~8 calls)

- [ ] **R13-T2** — `plugin/skills/adversarial-loop/SKILL.md:139` (also
      `plugin/skills/adversarial-review/SKILL.md:514`) — a run that Phase 0 stops still has the
      review stage an unpruned round plan under the current checkout's plan, and its dispositions
      are recorded nowhere.
      **Fails when:** on feature-B, `/wb:adversarial-loop 42` stops after step 2; Step 8 wrote and
      staged `reviews/<date>-round-N/tasks.md` with a task for every finding of PR 42, so the next
      unscoped commit or a later `implement` carries them onto feature-B; the dispositions reach no
      ledger and the report does not say so.
      **Acceptance (shape 4)**: grep adversarial-review Step 8 for a rule that a review whose
      `review_head` is not `HEAD` writes and stages no plan, and Phase 0 for a sentence that the
      report is the only record and no ledger row exists for that target; negative control: both
      absent today. (~5 calls)

- [ ] **R13-T3** — `plugin/skills/adversarial-loop/SKILL.md:258` (also
      `plugin/docs/reference/review-ledger.md:30`) — the `[ -f ]` guard added in round 12 turns a
      missing or mistyped ledger path into a silent exit 0.
      **Fails when:** a round verifies findings, step 2 rejects them all, and the rows land at
      another path; the guard is false, nothing is committed, Phase 2 pushes, and the breaker reads
      a file that never existed as clean.
      **Acceptance (shape 1)**: restore the unguarded block and make a clean round write a
      `clean-round` row so the ledger always exists; execute the block in a scratch repo: a missing
      ledger exits non-zero, a clean round's ledger commits alone, a changed ledger commits only
      itself. RED today: a missing ledger exits 0. (~8 calls)

- [ ] **R13-T4** — `plugin/skills/reply-to-claude/SKILL.md:58` (also `:62`) — the branch refusal
      tells the model to push and reopen the PR, and the ancestry refusal says "check out its
      branch" after the branch already matched.
      **Fails when:** on `main`, `/wb:reply-to-claude 57` prints a remedy to `git push -u origin`
      and "reopen the PR", both outward-facing and unconfirmed here, with a contributor-controlled
      branch name inside the quotes; the second refusal is reachable only after the names matched.
      **Acceptance (shape 1)**: execute Step 1 in a scratch repo for a mismatched branch, a renamed
      branch and a behind branch; assert neither message contains `push` or `check out its branch`,
      each names both branches or the oid, and each ends `NOT replying`. RED today: both do. (~6 calls)

- [ ] **R13-T5** — `plugin/skills/reply-to-claude/SKILL.md:92` — Step 2 prints no dates and shows
      an outdated comment's `original_line` unmarked.
      **Fails when:** a comment at `foo.sh:40` becomes outdated, prints `foo.sh:40`, and the model
      reads today's line 40; round-1 review bodies cannot be told from round-2 ones.
      **Acceptance (shape 1)**: run the Step 2 filters with jq on a synthetic array; assert an
      outdated comment prints `(outdated)`, and every printed line carries its date. RED today:
      neither. (~5 calls)

- [ ] **R13-T6** — `plugin/scripts/test-phi-patterns:44` — deleting any separator member from one
      pattern alone, or widening the bounds, passes all 35 cases.
      **Fails when:** `_`, space, `.`, `:`, `/`, en dash, em dash or NBSP is deleted from only the
      first or only the second pattern; 17 such deletions pass today and the em dash has no case.
      **Acceptance (shape 2)**: a loop test that, for each member, requires a member-ID-only input
      and a general-only input to match the right pattern alone, plus a four-separator negative;
      each single-pattern deletion in a scratch copy then fails a case. RED today: none fails. (~8 calls)

- [ ] **R13-T7** — `plugin/docs/reference/technical-english.md:110` — the task-lines citation to
      implement Step 4, BARRIER 2 does not contain the ID shape or the line patterns.
      **Fails when:** a maintainer follows it to confirm the exempt-token shape and finds nothing.
      **Acceptance (shape 3)**: dual grep — "Step 4, BARRIER 2" absent from the file, and the list
      names only citations that contain the patterns. (~3 calls)

## Implementation notes

- **[2026-10-01] HELD behind the breaker.** The introduced-rate did not fall from round 12 (80%)
  to round 13 (83%), so `review-ledger.md` says to stop fixing and not run another round. The
  seven tasks are the Valid findings, kept for the decision. The ledger carries all twelve rows
  and the breaker section.
- **[2026-10-01] Five candidates are ledger-only.** Over-fitted: the shrink-excuse heuristic, the
  three-copies preference, the `found:` header match, the unreleased 3.0.0 date, and the untested
  blocks.
