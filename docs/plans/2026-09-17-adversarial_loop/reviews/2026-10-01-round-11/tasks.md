---
project: adversarial_loop
reviews: docs/plans/2026-09-17-adversarial_loop
round: 11
created: 2026-10-01
status: in-progress
total_tasks: 19
completed_tasks: 0
task_tracking: markdown-checkboxes
---

# Remediation — adversarial review round 11

Target: PR #25 on its own checkout, `origin/main...HEAD` at `cc331f8`. Round-11 review after the
`guard_lexer_and_pr_identity` escalation and round 10's fifteen ordinary tasks, run by
`/wb:adversarial-loop 25 --plan=docs/plans/2026-09-17-adversarial_loop`. Five lenses plus the
built-in leg returned 32 candidates. Nineteen survived verification (13 confirmed, 6 plausible).

## How each task is verified

Every task carries its finding's `failure_scenario` as its acceptance criterion, and **the
criterion is run before the fix**. A criterion that passes before the change is not a criterion.

## Tasks

- [x] **R11-T1** — `plugin/skills/adversarial-loop/SKILL.md:323` (also
      `plugin/skills/reply-to-claude/SKILL.md:54`, `plugin/skills/adversarial-review/SKILL.md:115`) —
      the own-checkout test (same-repository and `headRefOid` is an ancestor of `HEAD`) also passes
      for a branch stacked on the PR's head.
      **Fails when:** on feature-B (draft PR 57) stacked on feature-A (PR 42),
      `/wb:adversarial-loop 42` resolves identity as `HEAD`, Phase 0 passes, Phase 2's ancestor
      check passes, `git push` pushes feature-B and `gh pr ready 42` un-drafts PR 42 at A1, which
      has none of the round's fixes; the phase forbids re-drafting. Reproduced in a scratch repo:
      `is-ancestor` passed, bare push went to feature-B, `origin/feature-A` stayed at A1, and
      `git rev-parse --abbrev-ref @{push}` returned `origin/feature-B`.
      **Acceptance (shape 1)**: execute the Phase 2 block in a scratch repo with a local bare
      origin and a stub `gh` (feature-B stacked on feature-A, PR head A1); assert it exits before
      `git push` with a named reason and the origin is unchanged. RED today: it pushes feature-B
      and logs `gh pr ready 42`. Apply the same check to reply-to-claude Step 1 and to
      adversarial-review's own-checkout branch, and re-run the six R10-T25 cases. (~10 calls) (completed 2026-10-01 13:07)

- [x] **R11-T2** — `plugin/skills/implement/SKILL.md:365` (also
      `plugin/skills/implement_inline/SKILL.md:313`) — the per-task staging chain names
      `${planDir}/journal.md`, which a remediation round never has.
      **Fails when:** `adversarial-loop` Phase 1 step 3 points `implement` at
      `docs/plans/<plan>/reviews/<date>-round-N/`, which holds only `tasks.md`;
      `git add -f r/tasks.md r/journal.md` exits 128 (`fatal: pathspec ... did not match any
      files`), stages nothing (not even `tasks.md`), the `&&` skips `git commit`, so no
      remediation task gets its commit and the flipped checkbox stays uncommitted and invisible to
      `git status`. Reproduced in a throwaway repo.
      **Acceptance (shape 1)**: execute the staging chain in a scratch repo whose ignored plan
      directory is a round (`tasks.md` only, journal in the parent); assert it exits 0 and creates
      one commit holding `tasks.md` and the parent's `journal.md`. RED today: exit 128, no commit.
      State the round variant once in each skill. (~8 calls) (completed 2026-10-01 13:09)

- [x] **R11-T3** — `plugin/skills/adversarial-loop/SKILL.md:318` (also `:488`) — the Phase 2 and
      Phase 5 blocks read `${target:+"$target"}` but nothing re-states `target`, and Phase 0 does
      not say to.
      **Fails when:** run as written in a fresh shell, `target` is unset, so `gh pr view` resolves
      the current branch's PR: with feature-B on draft PR 57 and target 42 the block un-drafts or
      labels 57, or fails "no PR for the current branch" when the current branch has none.
      `adversarial-review/SKILL.md:77` and `reply-to-claude/SKILL.md:36` both say to re-state it.
      **Acceptance (shape 4)**: grep Phase 0 for a sentence that the binding lives in the session
      and is re-typed as the first line of every block that reads `$target`, and Phases 2 and 5 for
      a comment or line that does so; negative control: both absent today. (~4 calls) (completed 2026-10-01 13:10)

- [x] **R11-T4** — `plugin/skills/adversarial-loop/SKILL.md:301` — the review baseline is recorded
      once, in Phase 2, and never again before a Phase 4 re-summon.
      **Fails when:** the round-1 bot review arrives (id B1, `updated_at` T1 later than the Phase 2
      baseline); Phase 4 fixes, pushes and re-summons `@claude`; Phase 3 reruns against the same
      baseline, T1 already exceeds it, so the poll declares round 2 arrived on the first poll and
      adjudicates stale findings. The bot edits in place, so only `updated_at` distinguishes
      rounds.
      **Acceptance (shape 4)**: grep Phase 4 for an instruction to re-record the newest
      `claude[bot]` comment id and `updated_at` immediately before each re-summon and to compare
      Phase 3 arrivals against the latest one; negative control: `baseline` appears nowhere in
      Phase 4 today. (~3 calls) (completed 2026-10-01 13:10)

- [x] **R11-T5** — `plugin/skills/daily-digest/sources.md:227` — the member-ID scrub patterns do
      not match a form-encoded space.
      **Fails when:** a Sentry, Jira or Gmail URL containing the synthetic `?q=BM+CA+12345678`
      matches neither pattern (Python `re.search`, both False), so the ID is written into the
      digest unscrubbed, while the same URL with `%20` is scrubbed and pinned.
      **Acceptance (shape 2)**: add `BM+CA+12345678` and `bm+ca+12345678` as must-scrub cases to
      `plugin/scripts/test-phi-patterns`; RED today (unmatched); GREEN after the separator class
      gains `+`, with every existing case (including the glued-prefix and glued-suffix must-not
      cases) still passing. Tabs, wrapped lines and U+2011 or U+2212 hyphens stay out of scope.
      (~5 calls) (completed 2026-10-01 13:11)

- [x] **R11-T6** — `plugin/skills/adversarial-loop/SKILL.md:244` (also `:411`) — the ledger commit
      is `git add -f <ledger> && git commit -m ...` with no pathspec.
      **Fails when:** unrelated files are staged when Phase 1 step 5 or Phase 4 step 3 runs;
      `git commit` with no pathspec commits the whole index under "ledger: round N dispositions".
      **Acceptance (shape 1)**: execute the block in a scratch repo with an unrelated staged file;
      assert the resulting commit holds only the ledger path. RED today: it holds both. A round
      with no new rows must still end with a clean tree, without a failing exit. (~5 calls) (completed 2026-10-01 13:12)

- [x] **R11-T7** — `plugin/scripts/fixtures/mutation-waivers.json:99` (also `:107`, `:111`) —
      three waivers (`del Break` in the shape-1 loop, `del Break` in the shape-2 loop, and the
      `pending_glob = None` reset) claim equivalence that holds only because findings are compared
      as a set.
      **Fails when:** a line holds two unguarded captures, `a=$(grep -c x f); b=$(grep -c y g)`;
      the shipped checker reports it once, with the shape-1 `break` deleted it reports it twice,
      and an unguarded glob loop followed by more than four lines is re-reported on each following
      line (seven times measured), yet every corpus case stays green. The waiver text admits a
      multiset comparison would kill all three.
      **Acceptance (shape 2)**: make `parse_findings` return a multiset and add a corpus case
      with two captures on one line (`expect_at` lists the line twice) and a glob-loop case; show
      in a scratch copy of `check-guards` that each of the three mutants now fails a case; delete
      the three waivers and run `./plugin/scripts/test-guards --generated` once in the background:
      0 unwaived, 0 stale, ratchet re-based with provenance. (~25 calls, one background sweep) (completed 2026-10-01 13:23)

- [x] **R11-T8** — `plugin/scripts/test-guards:528` — no unit case pins the equal-size boundary of
      the shrunk-set guard.
      **Fails when:** changing `total < prev_total` to `<=` keeps all four verdict checks green;
      `ratchet_verdict(330, 344, [], [], total=395, prev_total=395)` then returns "the mutant set
      shrank" and tells the maintainer to lower the stored count, instead of "add a corpus case".
      A shrunk set with a survivor is also unpinned.
      **Acceptance (shape 2)**: add an equal-total case asserting the corpus-case message and a
      shrunk-with-survivor case asserting it fails with the survivor message; plant `<=` in a
      scratch copy and show the equal-total case goes red while the old suite stays green. (~6 calls) (completed 2026-10-01 13:26)

- [x] **R11-T10** — `plugin/skills/adversarial-loop/SKILL.md:458` (also `:494`, `:346`) — three
      citations point at the wrong text and one rationale contradicts `CLAUDE.md`.
      **Fails when:** line 458 cites `SKILL.md:273` for "a clean pass certifies the commit it read"
      (that text is at 289; 273 is "Only when a pull request exists"); line 494 cites
      `SKILL.md:299` for the chained rule (it is at 349); line 346 cites
      `plugin/scripts/lint-hook:26` and says the hook runs `lint --fix` after Bash, but
      `CLAUDE.md` says the Bash route only reports and `:26` is a comment. A session following a
      citation lands on unrelated text.
      **Acceptance (shape 3)**: dual grep — `SKILL.md:273`, `SKILL.md:299` and `lint-hook:26`
      absent from the file, and the replacements name the text itself (a heading or a quoted
      phrase) rather than a line number; the hook sentence says Write and Edit fix and Bash
      reports. (~4 calls) (completed 2026-10-01 13:27)

- [x] **R11-T11** — `plugin/docs/reference/technical-english.md:133` (also `:169`) — citations
      into `plugin/skills/implement/SKILL.md` point at lines that moved.
      **Fails when:** line 133 cites `implement/SKILL.md:242-245` for the journal headings (now
      the BARRIER 2 text) and line 169 cites `:307,320` for the `### Status: PASS` headings (now
      at 342-343), so a WBTE reviewer lands on unrelated prose. Line 110 (`:282`) lands on the
      intended text only by coincidence.
      **Acceptance (shape 3)**: dual grep — `implement/SKILL.md:242-245` and `:307,320` absent,
      and each citation names the heading or phrase instead of a line. (~3 calls) (completed 2026-10-01 13:28)

- [ ] **R11-T12** — `plugin/scripts/README.md:241` (also `README.md:360-361`) — both READMEs state
      a 114-case corpus and 15 integrity checks.
      **Fails when:** a maintainer runs the command the README prints, `jq length
      fixtures/guard-corpus.json`, and gets 128; `test-guards` reports integrity 16/16.
      **Acceptance (shape 3)**: dual grep — "114" and "15 scan-integrity" absent from both
      READMEs, and 128 and 16 present at a cited line each. (~3 calls)

- [ ] **R11-T13** — `plugin/scripts/test-guards:171` — the must-not-fire branch passes whenever
      `parse_findings` is empty, ignoring exit code, stderr and unmapped labels.
      **Fails when:** a checker that wraps the real one and exits 1 with a traceback whenever the
      real result is clean scores `tp=68 fn=0 fp=0 tn=60` while every negative crashes; a finding
      under a renamed label is dropped by `parse_findings` and also reads as a correct negative.
      **Acceptance (shape 2)**: assert `returncode == 0` and empty stderr for `expect == 0` and
      `returncode == 1` for `expect == 1`, and fail on a finding line that maps to no `SHAPE_OF`
      key; show in a scratch copy that the crash-on-clean wrapper now fails the suite. (~8 calls)

- [ ] **R11-T14** — `plugin/scripts/test-quiet:1` — no case asserts the suppressed-line count or
      log retention that `quiet` documents.
      **Fails when:** in a scratch copy, replacing the count capture with `lines=99`, and
      separately deleting the log on success, both leave `test-quiet` at 9 passed, 0 failed.
      **Acceptance (shape 2)**: a case asserting "3 lines suppressed" for a three-line run and that
      the printed log path exists; show both scratch mutations now fail, and remove the test's own
      leaked temp logs. (~6 calls)

- [ ] **R11-T15** — `plugin/scripts/test-guards:528` — the shrunk-set branch ignores how far
      `killed` fell compared with the total.
      **Fails when:** an idle waiver matches a newly unkilled mutant (survivors empty), so killed
      344 to 342 with total 395 to 394 gets "the mutant set shrank, lower the stored count by
      hand" instead of "add a corpus case", and a real regression is ratcheted down.
      **Acceptance (shape 2)**: `ratchet_verdict(342, 344, [], [], total=394, prev_total=395)`
      returns the corpus-case message; `(300, 344, [], [], total=380, prev_total=395)` where the
      drop exceeds what the shrink explains also returns it; RED today; the existing shrunk case
      (330, 344, 380, 395 with a drop explained by the shrink) still returns the lowering message
      only when `prev - killed <= prev_total - total`. (~5 calls)

- [ ] **R11-T16** — `plugin/skills/reply-to-claude/SKILL.md:54` (also
      `plugin/skills/adversarial-loop/SKILL.md:311`) — the prose says all three identity blocks run
      one test, but adversarial-review proceeds unless `cross` is exactly `true` and the other two
      refuse unless it is exactly `false`.
      **Fails when:** `gh` exits 0 with an empty or null `isCrossRepository`: adversarial-review
      takes the own-checkout path while reply-to-claude and loop Phase 2 refuse for the same PR.
      No realistic trigger was found. The smaller change is to state the difference, not to change
      the blocks.
      **Acceptance (shape 3)**: dual grep — "is the one ../adversarial-review/SKILL.md Step 1 uses"
      and "the same test as" absent from the two files, and a sentence present at a cited line that
      says the publishing sites require `isCrossRepository` to be exactly `false` and
      adversarial-review fails open because it only chooses what to review. (~3 calls)

- [ ] **R11-T19** — `.github/workflows/checks.yml:57` — the `mutation-sweep` job has no
      `timeout-minutes`.
      **Fails when:** a mutant that survives the corpus loops on one of the integrity inputs; the
      in-process 5-second alarm does not cover that subprocess, so the job runs to GitHub's
      360-minute default. No such mutant was found, and the current sweep passes in about twelve
      minutes. The smaller change is the job timeout only.
      **Acceptance (shape 4)**: grep `checks.yml` for `timeout-minutes` inside the `mutation-sweep`
      job (30); negative control: absent today. (~3 calls)

## Implementation notes

- **[2026-10-01] Adjudicated before pruning.** T9 (`strip_comment` after a `#` in backticks) is
  Pre-existing. T17 (Phase 5 gate) and T18 (stored `of`) are Over-fitted. T5, T16 and T19 are Real
  but disproportionate or narrowed. Their task lines were deleted or rewritten. The ledger
  carries the dispositions.

- **[2026-10-01] Findings carried, not fixed.** The two preference candidates (the comment-density
  rule for `test-check`, and force-adding plan files against the plan-promotion convention) are
  not tasks. The seven refuted candidates are in the review report.
- **[2026-10-01] Tasks 1, 3 and 16 edit the same three identity blocks.** Work them in that order
  and re-run the six R10-T25 cases after the last.
