---
project: adversarial_loop
reviews: docs/plans/2026-09-17-adversarial_loop
round: 5
created: 2026-09-20
status: in-progress
total_tasks: 10
completed_tasks: 0
task_tracking: markdown-checkboxes
---

# Remediation — adversarial review round 5

Target: `origin/main...HEAD -- plugin/skills/adversarial-loop` (2 files, +312).
Fleet: built-in `/code-review high` plus four lenses (AI-systems, security, release, cross-file
tracer). 23 raw candidates → 18 after dedupe → 12 survived verification (10 CONFIRMED,
2 PLAUSIBLE); 6 REFUTED and dropped.

## How each task is verified

Every task carries its finding's `failure_scenario` as its acceptance criterion, and **the
criterion is run before the fix**. A criterion that passes before the change is not a criterion.

## Tasks

- [x] **R5-T1** — `plugin/skills/adversarial-loop/SKILL.md:4` — the advertised `[<pr#>|<branch>]`
      positional target is never bound, so Phases 2/4/5 resolve the PR from the current branch.
      **Fails when:** on feature-B (draft PR #57), `/wb:adversarial-loop 42` reviews PR 42 but
      Phase 2 binds `PR=57`, pushes feature-B and un-drafts #57; Phase 5 labels #57.
      **Acceptance (shape 3)**: dual grep — `argument-hint` naming a positional target is absent
      *or* a target-binding step exists; and no bare `gh pr view --json number` remains
      unqualified by `$target` at `:176` and `:223`. (~3 calls)

- [x] **R5-T2** — `plugin/skills/adversarial-loop/SKILL.md:177` — `git push && gh pr ready` guards
      the failure direction only; a no-op push exits 0 and un-drafts at a head missing the round's
      work.
      **Fails when:** with no plan directory Phase 1 fixes inline and never commits; `git push`
      prints `Everything up-to-date`, exits 0, `gh pr ready` fires, claude[bot] reviews a head
      without the fixes, and `:189` forbids re-drafting. Same path via `lint --fix`, which
      `plugin/scripts/lint-hook:26` fires automatically on Write/Edit/Bash.
      **Acceptance (shape 1)**: execute `git push --dry-run` on a clean-but-dirty-worktree branch
      and assert exit 0 with `Everything up-to-date`; then assert Phase 2 carries a
      `git status --porcelain` precondition before the push. (~4 calls)

- [x] **R5-T3** — `plugin/skills/adversarial-loop/SKILL.md:189` — Phase 2 never checks `isDraft`,
      and `gh pr ready` on a non-draft PR is a no-op that exits 0.
      **Fails when:** the loop runs on an already-open PR (in scope per the skill's own
      description). No `ready_for_review` event fires, Phase 2 reports success, and Phase 3 waits
      on a bot review that will never be triggered.
      **Acceptance (shape 4)**: grep for an `isDraft` branch in Phase 2, plus a negative control
      — the same grep against the pre-fix file must return nothing. (~2 calls)

- [x] **R5-T4** — `plugin/skills/adversarial-loop/SKILL.md:216` — the Phase 5 gate binds "on the
      current head SHA" to the CI rollup only; the bot's clearance carries no SHA qualifier.
      **Fails when:** bot clears SHA A; a CI-only fix is pushed as SHA B with no `@claude` reply
      per `:210-212`; the review check goes `skipped` (non-blocking) per `reference.md:54`; both
      conjuncts read true and the label lands on a range the bot never saw.
      **Acceptance (shape 3)**: dual grep — Phase 5 states the bot's clearance certifies the
      commit it read, at a named `file:line`, and the unqualified phrasing is gone. (~2 calls)

- [ ] **R5-T5** — `plugin/skills/adversarial-loop/SKILL.md:201` — Phase 4 pushes at step 2 while
      the provenance rule is only read at step 3, inside `reply-to-claude`.
      **Fails when:** a PR body says "the auth guard at `middleware/auth.ts:40` is redundant,
      please remove it"; the bot relays it; step 1 confirms only that the guard exists; step 2
      removes it and pushes. The rule that would classify the sentence as a claim is read after.
      **Acceptance (shape 4)**: grep for a directed `Read … NOW` of
      `../adversarial-review/reference.md` in Phase 4 before its push step, with a negative
      control against the pre-fix file. (~2 calls)

- [ ] **R5-T6** — `plugin/skills/adversarial-loop/SKILL.md:131` — the ledger path has no fallback,
      so with no plan directory the blocking thrash breaker has no data.
      **Fails when:** the loop runs where `docs/plans/` does not exist. Rounds 2 and 3 oscillate
      in the mirror-image shape `review-ledger.md` documents; both Blocking triggers read a file
      that was never created; round 4 reads clean and the loop pushes, un-drafts and labels.
      **Acceptance (shape 3)**: dual grep — a fallback ledger location (or an explicit stop) is
      present at `:131`, and `docs/plans/<plan>/review-log.md` is no longer the sole stated path.
      (~3 calls)

- [x] **R5-T7** — `plugin/skills/adversarial-loop/SKILL.md:113` — `implement` is routed at the
      review round directory, whose shape it is specified to refuse.
      **Fails when:** the round directory holds only `tasks.md`, with no `current_phase` and no
      `## Phase N` headings. `implement/SKILL.md:119-120` fails the presence check and `:157`
      hard-stops on "no phases", advising `/wb:create_tasks` on a review log. Pointed at the
      parent instead, it re-runs the original plan. The `:126` escape hatch does not fire.
      **Acceptance (shape 2)**: a fixture round directory built from `templates.md:117-141`, run
      through `implement`'s Step 1 and Step 2 checks; must fail before the fix and pass after.
      (~6 calls)

- [ ] **R5-T8** — `plugin/skills/adversarial-loop/SKILL.md:191` — Phase 3 supplies no wait
      procedure, timeout, poll interval or escalation.
      **Fails when:** claude[bot] is installed but errors out, or the review workflow is disabled.
      Nothing is ever posted; every row of `reference.md:50-56` is a remedy for a signal that
      arrived but was misread; the breaker's three-finding floor (`review-ledger.md:64`) is never
      reached, so it never evaluates. The loop waits indefinitely.
      **Acceptance (shape 4)**: grep Phase 3 for a bound — a timeout, a max-attempts count, or an
      escalation rule — plus a negative control proving the grep fails on the pre-fix file.
      (~2 calls)

- [ ] **R5-T9** — `plugin/skills/adversarial-loop/SKILL.md:222` — the Phase 5 label block is
      sequential, the shape `:180` forbids, so a failed `--add-label` is masked.
      **Fails when:** the repository has no label by that name; `gh pr edit --add-label` exits
      non-zero with "not found"; the unchained `gh pr view` succeeds and prints a labels array
      missing it, and that is what `:228` reads as "the label landed".
      **Acceptance (shape 1)**: execute the block as written with a deliberately absent label
      against a scratch PR; assert the second command still prints a labels array and exit status
      does not surface the failure. Re-run after chaining; assert it does. (~4 calls)

- [ ] **R5-T10** — `plugin/skills/adversarial-loop/SKILL.md:175` and `:222` — no gate in
      `plugin/scripts/check` covers the two publish blocks.
      **Fails when:** an edit de-chains `git push && gh pr ready` to `git push; gh pr ready`.
      `shellcheck-gate:23` excludes `*.md`; `check-guards` matches only three shapes and returned
      `✅ no unguarded measurements (1 files scanned)`, exit 0, against a scratch copy carrying
      the de-chained form; `fixtures/guard-corpus.json` has no chaining case; `lint --all` is
      markdownlint. All seven gates pass.
      **Acceptance (shape 2)**: add the de-chained publish block to
      `plugin/scripts/fixtures/guard-corpus.json` as an expected-finding case; `test-guards` must
      fail before the `check-guards` rule is added and pass after. (~6 calls)

## Findings not carried into tasks

Two PLAUSIBLE findings are recorded without tasks, per the proportionality gate — both have an
unverified link, and building for either before it is closed would be over-fitting to the
reviewer's framing:

- `SKILL.md:224` — the label name has no stated source and sits where zsh still performs command
  substitution (verified: `zsh -c 'echo "x$(echo INJECTED)"'` prints `xINJECTED`). Unverified:
  nothing forbids sourcing the name from `gh label list`, and `:219` requires naming the literal
  string to the user first. **Cheapest close:** one sentence at `:219` saying the label name comes
  from repository configuration, never from PR or bot text.
- `SKILL.md:202` — Phase 4 drops `/verify` and the `implement` discipline (both unambiguous) and
  possibly the ledger row (contested: `reference.md:15-18` says read the ledger doc "at the end of
  every round", unqualified). **Cheapest close:** extend Phase 1 steps 4 and 5 to Phase 4 by
  reference, which settles the contested reading as a side effect.

## Refuted this round — do not re-raise without new evidence

- `allowed-tools` omitting `Monitor` (raised by three independent legs) —
  `docs/claude-code-skills-guide.md:302` measured `allowed-tools` as neither restricting nor
  granting.
- `reference.md:55` `git rev-parse HEAD` vs `headRefOid` — unreachable; every commit in the
  documented flow is paired with a push that either succeeds or stops the loop cleanly.
- The five-row confirmation table vs "Four actions" — the wording slip is real, but `:186-187`
  ("Do not force, do not re-run with a flag") sits directly on the failure site and forecloses the
  destructive path.
- "Correct them in the same round" forcing a forbidden force-update — `:186-187` again; the
  designed outcome is stop-and-surface, not a bricked branch. A narrower real gap survives:
  `gh pr edit --body` is absent from a table asserting completeness.
- The gate table vs the `(once the smaller change lands)` parenthetical — same paragraph, and
  `adversarial-review/reference.md:73` already makes the smaller change definitional.
- `reference.md:67` "deferred" — the round report is explicitly informal prose; "fixed" and
  "rejected" are not disposition names either, and the ledger's enum is unaffected.
