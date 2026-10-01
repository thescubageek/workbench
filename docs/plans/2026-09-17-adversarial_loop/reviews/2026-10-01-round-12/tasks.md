---
project: adversarial_loop
reviews: docs/plans/2026-09-17-adversarial_loop
round: 12
created: 2026-10-01
status: in-progress
total_tasks: 7
completed_tasks: 0
task_tracking: markdown-checkboxes
---

# Remediation — adversarial review round 12

Target: PR #25 on its own checkout, `origin/main...HEAD` at `6cd1d71`. A re-review of round 11's
fixes, run by `/wb:adversarial-loop 25 --plan=docs/plans/2026-09-17-adversarial_loop`. Four
lenses plus the built-in leg returned 21 candidates. Ten survived verification (6 confirmed, 4
plausible, and one merged finding), and seven are tasks after adjudication.

## How each task is verified

Every task carries its finding's `failure_scenario` as its acceptance criterion, and **the
criterion is run before the fix**. A criterion that passes before the change is not a criterion.

## Tasks

- [x] **R12-T1** — `plugin/skills/adversarial-loop/SKILL.md:136` — for a PR target that resolves
      to the fetch path, Phase 0 stops only at "the end of Phase 1", and Phase 1 steps 3 to 6 still
      fix, commit the ledger and re-review on the current checkout.
      **Fails when:** on feature-B stacked on PR 42's head, `/wb:adversarial-loop 42` now resolves to
      `origin/pr/42 = ..., fetched` (round 11's branch-name test), so Phases 2, 4 and 5 are skipped;
      Phase 1 step 3 runs `implement`, which commits fixes onto feature-B, step 5 commits the ledger
      onto feature-B, and step 6 re-resolves 42 to the same unchanged `headRefOid` and reviews
      `origin/pr/42` again, so the same Valid findings return and the gate never clears; every
      round adds duplicate fix and ledger commits to the wrong branch. No line in Phase 1 reads
      `review_provenance`.
      **Acceptance (shape 4)**: grep Phase 0 for a sentence that when the identity line does not
      start with `HEAD` the loop stops after the first review's report, with no step 3 to 6 (no
      fixes, no ledger commit, no re-review), and Phase 1 step 3 for a back-reference to it;
      negative control: neither exists today (`command grep -n 'stop at the end of Phase 1'` finds
      only the old sentence). (~4 calls) (completed 2026-10-01 14:18)

- [ ] **R12-T2** — `plugin/skills/adversarial-loop/SKILL.md:253` — the scoped ledger block exits
      128 when `review-log.md` does not exist, which contradicts the sentence that a round with no
      rows commits nothing and exits 0.
      **Fails when:** round 1 of a run verifies zero findings: Step 8 writes no `tasks.md`, the
      ledger is one row per finding so none is written, and `review-log.md` is never created;
      `git add -f` of the missing path prints `fatal: pathspec ... did not match any files` and
      exits 128 (reproduced under zsh in a throwaway repo), against the prose and the instruction to
      run the block on every round. From round 2 on the file exists.
      **Acceptance (shape 1)**: execute the block in a scratch repo with `docs/plans/` ignored and
      no ledger file; assert exit 0 and no new commit; then with a ledger row present assert it
      still commits only the ledger. RED today: exit 128. (~5 calls)

- [ ] **R12-T3** — `plugin/docs/reference/technical-english.md:109` — the "Task lines" citation
      points at implement Step 6a, which holds no task-ID parser or line pattern.
      **Fails when:** a maintainer changing the task-line contract follows "`implement/SKILL.md`,
      Step 6a, the checkbox check" to find the ID shape and the `- [ ]` and `- [x]` patterns; Step 6a
      holds only a grep of one task ID and a checkbox table, and the first-unchecked-line rule is in
      Step 4's BARRIER 2, so the parser is never found. Introduced by R11-T11's rewrite of the old
      line citation.
      **Acceptance (shape 3)**: dual grep — "Step 6a, the checkbox check" absent from the file, and
      the citation names Step 4's BARRIER 2 rule (the first `- [ ]` line in the current phase) at a
      cited line. (~3 calls)

- [ ] **R12-T4** — `plugin/skills/reply-to-claude/SKILL.md:20` (also `:58`) — the Preconditions
      bullet still states the old ancestry-only test, and the refusal's remedy "check out its
      branch" points at the wrong branch after a local rename.
      **Fails when:** a checkout that descends from the PR head but is on another branch satisfies
      the Preconditions bullet ("`HEAD` at or descended from the PR's head commit") and is refused
      by Step 1 (the branch name must equal `headRefName`). After a local `git branch -m` of a
      published branch, the refusal says "check out its branch", and `git checkout foo` creates a
      tracking branch from `origin/foo` without the unpushed local commits. The smaller change is
      to this skill only: the loop's refusal has no remedy text and stays as it is.
      **Acceptance (shape 3)**: dual grep — "at or descended from the PR's head commit" absent, and
      the bullet says "on the PR's own branch" at a cited line; execute Step 1's block in a scratch
      repo on a renamed branch with a stub `gh` and assert the refusal text names both branches and
      says to push the renamed branch or switch back. (~5 calls)

- [ ] **R12-T5** — `plugin/skills/reply-to-claude/SKILL.md:92` — Step 2's inline-comment jq prints
      `path:null` for an outdated comment, and nothing scopes the collected findings to those new
      since the last reply.
      **Fails when:** GitHub sets `.line` to null on outdated inline comments; the filter prints
      `a.py:null` for a comment with `line` null and `original_line` 12 (reproduced with jq on a
      synthetic sample), so Step 3's `file:line` adjudication loses the line and a Rejected entry
      may cite a guessed line under the maintainer's identity; every `claude[bot]` review and
      comment from earlier rounds is also collected.
      **Acceptance (shape 1)**: run the Step 2 inline-comment filter with `/opt/homebrew/bin/jq` on
      a synthetic two-comment array (one with `"line": null, "original_line": 12`); assert the
      first prints `a.py:12`. RED today: `a.py:null`. Add one sentence to Step 2 that the reply
      covers only findings raised since the last `@claude` reply, and grep for it. (~4 calls)

- [ ] **R12-T6** — `plugin/scripts/test-phi-patterns:44` — the two `+` cases match both patterns,
      so dropping `+` from either pattern alone leaves the suite green.
      **Fails when:** `+` is deleted from the separator class of only the general pattern, or only
      the member-ID pattern, in `sources.md`; `BM+CA+12345678` and `bm+ca+12345678` still match
      through the other pattern, so `test-phi-patterns` stays 33/33 PASS. `BM+CA+1234567` matches
      only the general pattern and `BMCA+12345678` only the member-ID pattern.
      **Acceptance (shape 2)**: add those two synthetic cases as must-scrub; plant each deletion in
      a scratch copy of `sources.md` and show the matching new case goes red while the old suite
      stays green. (~5 calls)

- [ ] **R12-T7** — `CHANGELOG.md:175` — the 2.1.0 section was inserted above the released 2.2.0
      and 2.1.1, the 3.0.0 section never mentions WBTE, and a parenthetical says 3.0.0 was "then
      numbered 2.2.0".
      **Fails when:** the section order reads 3.0.0, 2.1.0, 2.2.0, 2.1.1, 2.0.1 (2.1.0 is not on
      `origin/main` and was added by this PR); a reader of 3.0.0 does not learn that WBTE (merged in
      from 2.2.0, byte-identical to main's section) is in it; the line 178 parenthetical reads as a
      contradiction beside a real 2.2.0. The smaller change is to move the 2.1.0 section, add one
      sentence to 3.0.0, and reword the parenthetical.
      **Acceptance (shape 3)**: dual grep — the `^## \[` headings read 3.0.0, 2.2.0, 2.1.1, 2.1.0,
      2.0.1 in that order and "then numbered 2.2.0" is absent, and the 3.0.0 section contains
      "WBTE" at a cited line. (~4 calls)

## Implementation notes

- **[2026-10-01] Adjudicated before writing.** The plan carries only the adjudicated tasks. Three
  findings are not tasks: the in-progress bot edit at `adversarial-loop/SKILL.md:410` (Over-fitted,
  unobserved bot behaviour), the push destination at `adversarial-loop/SKILL.md:354`
  (Pre-existing, older than round 11) and the zero-file count at `plugin/scripts/check:60`
  (Over-fitted, needs a regression that also passes two fixtures). The ledger carries all ten.
- **[2026-10-01] Task 4 absorbs the rename-remedy finding.** It is the same file and the same
  identity prose as the Preconditions finding, so one task holds both.
