---
project: adversarial_loop
reviews: docs/plans/2026-09-17-adversarial_loop
round: 9
created: 2026-09-28
status: in-progress
total_tasks: 25
completed_tasks: 0
task_tracking: markdown-checkboxes
---

# Remediation — adversarial review round 9

Target: PR #25, `origin/main...origin/adversarial-loop-skill-research` at `95ffdb4`. First run of
`/wb:adversarial-loop` against a real pull request.

## How each task is verified

Every task carries its finding's `failure_scenario` as its acceptance criterion, and **the
criterion is run before the fix**. A criterion that passes before the change is not a criterion.

## Tasks

- [x] **R9-T0** — `plugin/scripts/check-guards` — no detector shape sees a positional token
      (`$<digit>`, `$ARGUMENTS`) inside a fenced block of a shipped `SKILL.md`, the class 2.0.1
      removed across eight stages and R7-T1 reintroduced at `adversarial-review/SKILL.md:297`.
      **Fails when:** `/wb:adversarial-review 25 --plan <dir>` — the harness substitutes the awk
      `$1` with `--plan` before the block reaches the session; measured in the round-9 run.
      `check-guards plugin/` exits 0 over the file today. Every other `$1` under
      `plugin/skills/` is prose ("Use `$1` as the project directory") and `clip`'s
      `$ARGUMENTS` is deliberate, so the shape scans fenced blocks only and allowlists `clip`.
      **Acceptance (shape 2)**: a must-fire corpus case with `$1` inside a `bash` fence and a
      must-not-fire case with `$1` in prose; RED today (the gate passes both); GREEN after the
      shape lands, with `check-guards plugin/` now flagging `:297` and nothing else. Model it on
      shape 5 (R7-T7, the `PIPESTATUS` bashism). **Lands first, as its own commit, before
      R9-T1** — the breaker fired Blocking on R9-T1 and this is the tracer bullet that retires
      the class rather than the fourth instance. (~8 calls) (completed 2026-09-28 12:38)

- [x] **R9-T1** — `plugin/skills/adversarial-review/SKILL.md:297` — the blast-radius awk filter
      uses the awk field `$1`, which the harness substitutes with an invocation argument.
      **Fails when:** `/wb:adversarial-review 25` → the block arrives as
      `awk -F: '25 != ENVIRON["changed"] && …'`, which exits 0 and keeps every line, so the
      changed file's own lines count as callers and inflate the tier silently; this run received
      `--plan != …`, and a path or `feature/foo` substitution makes awk exit 2 so every such target
      prints FILTER FAILED.
      **Acceptance (shape 1)**: invoke the skill with an argument and execute the Step 3 block as
      received against a two-line input where one line is the changed file; assert only the other
      line prints. RED today: both print. Rewrite with **no positional token at all** —
      `cut -d: -f1` or `while IFS=: read -r path _` — so R9-T0's shape passes it; do not escape or
      quote `$1` around the harness. · Depends on: R9-T0 (~6 calls) (completed 2026-09-28 13:26)

- [x] **R9-T2** — `plugin/skills/adversarial-review/SKILL.md:116` — a PR-number target resolves
      to the pushed origin head, so loop re-reviews never see local fix commits.
      **Fails when:** `/wb:adversarial-loop 25` on PR 25's checkout: round 1's fixes are committed
      locally by implement; round 2's re-review diffs the unchanged origin head, so fixed findings
      recur or the gate clears from the record, and Phase 2 pushes commits no pass ever read.
      **Acceptance (shape 1)**: with a local commit ahead of `origin/<head>`, run Step 1's block
      for a same-checkout PR target; assert the printed range's right endpoint is `HEAD` (or that
      the block refuses and names the gap). RED today: prints `origin/<head>`. (~5 calls) (completed 2026-09-28 13:47)

- [x] **R9-T3** — `plugin/skills/adversarial-loop/SKILL.md:135` — the plan directory the loop is
      told to pass has no slot in adversarial-review's argument grammar and is bound as a path
      target.
      **Fails when:** No loop argument → review invoked with `docs/plans/<plan>`; Step 1 binds
      target, `-e` is true, pathspec becomes the gitignored plan directory, and the review covers
      that directory instead of the branch's change.
      **Acceptance (shape 3)**: dual grep — adversarial-review's Arguments section names the plan
      slot (its spelling and that it is stripped before binding target), and
      `adversarial-loop/SKILL.md:135` uses that same spelling. RED today: no slot defined. (~4 calls) (completed 2026-09-28 13:59)

- [x] **R9-T4** — `plugin/skills/reply-to-claude/SKILL.md:33` — every snippet runs `gh pr view`
      with no argument, so `<pr#>` is never used.
      **Fails when:** On a branch whose PR is #42, `/wb:reply-to-claude 57` collects #42's bot
      findings and, after confirmation, posts the public @claude reply to #42 while reporting it as
      the reply for #57.
      **Acceptance (shape 3)**: dual grep — each of the four `gh pr view` snippets (`:33`, `:48`,
      `:90`, `:105`) carries the `${target:+"$target"}` form, and a binding step like
      adversarial-loop Phase 0 is present. RED today: zero snippets pass the argument. (~4 calls)
      (completed 2026-09-28 14:09)

- [ ] **R9-T5** — `plugin/skills/adversarial-review/SKILL.md:234` — REVIEW.md may add "known
      false positives", which is finding-level suppression from a base that can be
      author-controlled.
      **Fails when:** PR B stacked on the same author's PR A; A's REVIEW.md says guard removal in
      middleware/ is a known false positive; reviewing B reads it from the merge-base as Present and
      B's guard-removal finding is dropped with no lens disabled and no tier lowered.
      **Decided 2026-09-27 by the maintainer**: keep the entries, demote them to a hint the
      verifier must still check, and disclose in the report every finding a REVIEW.md entry
      touched.
      **Acceptance (shape 3)**: dual grep — `adversarial-review/SKILL.md` Step 2 no longer says an
      entry drops a finding; `prompts.md`'s verifier prompt names the entry as a hint to re-check,
      not a verdict; `templates.md` carries a one-line disclosure per touched finding. RED today:
      the verifier prompt never mentions REVIEW.md. (~6 calls)

- [ ] **R9-T6** — `plugin/skills/daily-digest/sources.md:227` — the member-ID scrub patterns miss
      IDs adjacent to `_`, with doubled separators, or dot-separated.
      **Fails when:** Synthetic `BM-CA-12345678_intake.pdf`, `member_BM-CA-12345678`,
      `BM--CA--12345678`, `BM.CA.12345678` match neither pattern, so such an ID in an email subject
      or attachment name reaches the digest and .context/ unscrubbed; test-phi-patterns only pins
      passing variants.
      **Acceptance (shape 2)**: add those four synthetic cases to `plugin/scripts/test-phi-patterns`
      as must-match; RED today: 4 fail; GREEN after the pattern change, with the existing
      must-not-match cases (Jira, PR, date, SHA) still passing. (~5 calls)

- [ ] **R9-T7** — `plugin/skills/adversarial-loop/SKILL.md:283` — `DRAFT=$(gh pr view … isDraft)`
      has no failure guard.
      **Fails when:** The isDraft query fails transiently while the PR is a draft → DRAFT="" → the
      else branch pushes, prints 'already open', never runs `gh pr ready`, and Phase 3 waits on a
      bot review that was never summoned.
      **Acceptance (shape 1)**: execute the Phase 2 block with `gh` shimmed to fail only the
      isDraft call; assert it exits non-zero before any `git push`. RED today: reaches the else
      branch. (~5 calls)

- [ ] **R9-T8** — `plugin/skills/adversarial-loop/SKILL.md:402` — Phase 5 requires "the SHA the
      bot's newest comment was written against", which no surface the bot edits carries.
      **Fails when:** Bot reviews commit A, B is pushed, bot edits its comment for B: a review's
      commit_id still reads A and an issue comment has no commit field, so the gate cannot clear
      mechanically and the session must improvise.
      **Decided 2026-09-27 by the maintainer**: compare the review check-run's `head_sha` for
      the current head, not a SHA on the comment. Provisional until a real `claude[bot]` run
      exists on some repository; recorded as such in the skill.
      **Acceptance (shape 3)**: dual grep — Phase 5 no longer asks for "the SHA the bot's newest
      comment was written against"; it names the check-run `head_sha` comparison and says the
      rule is provisional pending a real bot run. RED today. (~4 calls)

- [ ] **R9-T9** — `plugin/docs/reference/review-ledger.md:21` — the ledger path is gitignored and
      no step stages it.
      **Fails when:** Rounds 1–2 run in one worktree; work resumes in a fresh worktree or after
      `git clean -fdx`; the round directories survive but review-log.md does not, and both Blocking
      breaker triggers read the missing file as a clean trend.
      **Acceptance (shape 4)**: grep for a `git add -f` of `review-log.md` in
      `adversarial-loop/SKILL.md` step 5 (presence), with a negative control that the same grep
      against `origin/main`'s copy returns nothing. (~3 calls)

- [ ] **R9-T10** — `plugin/skills/adversarial-loop/SKILL.md:382` — Phase 4 bot rounds are never
      written to the ledger and repeat without a bound.
      **Fails when:** Bot round 1 flags capture A; the fix guards B in a way that excuses A; bot
      round 2 flags B; no ledger rows exist, so the mirror-image trigger never evaluates and the
      loop repeats unboundedly, re-summoning @claude each round.
      **Acceptance (shape 4)**: grep Phase 4's line range for a ledger-record step and a breaker
      check (presence), with a negative control showing the range has zero "ledger" hits today.
      (~3 calls)

- [ ] **R9-T11** — `plugin/skills/adversarial-loop/SKILL.md:346` — the Phase 3 wait does not
      distinguish a poll whose gh call errored from one that found nothing.
      **Fails when:** The gh token hits a rate limit or expires mid-wait; 15 polls error; the bound
      report reads 'no claude[bot] comment' and names only 'bot erroring / workflow disabled' as
      causes, indistinguishable from a slow bot.
      **Acceptance (shape 4)**: grep Phase 3 step 3 for an instruction that a poll whose command
      exited non-zero is a failed poll to be reported, not a wait (presence), negative control on
      the current text. (~3 calls)

- [ ] **R9-T12** — `plugin/skills/adversarial-review/SKILL.md:211` — Step 2 resolves REVIEW.md's
      base only for numeric targets; a branch target uses the current checkout.
      **Fails when:** On feature-A, `adversarial-review feature-B` (PR base `release`) reads
      REVIEW.md from merge-base(HEAD, feature-A's base), contradicting 'Resolve the base OF THE
      TARGET', and the review runs under another change's rules.
      **Acceptance (shape 1)**: run Step 2's block with `target=<a local branch other than HEAD>`;
      assert the echoed `head_ref` is that branch. RED today: echoes HEAD. (~4 calls)

- [ ] **R9-T13** — `plugin/skills/implement_inline/SKILL.md:368` — no handling for
      attestation-shaped tasks.
      **Fails when:** A round with an `**Acceptance (attestation)**:` task run via
      /wb:implement_inline: Step 3 attempts TDD on an unfalsifiable judgement, and Step 6 requires
      every box `[x]` with no carve-out, so the round can never close.
      **Acceptance (shape 3)**: dual grep — `implement_inline/SKILL.md` Step 3 names
      `Acceptance (attestation)` and Step 6 carves out the attestation list, matching
      `implement/SKILL.md:250-263`. RED today: 0 hits for "attestation". (~3 calls)

- [ ] **R9-T14** — `plugin/scripts/check-guards:52` — COUNTING misses `grep -cE`, `-ci`, `-cv`.
      **Fails when:** A fenced block `n=$(grep -cE foo f)` with no guard scans '✅ no unguarded
      measurements' (exit 0); the `-c` control on the same line is flagged.
      **Acceptance (shape 2)**: add must-fire corpus cases for `-cE`, `-ci`, `-cv` to
      `fixtures/guard-corpus.json`; RED today; GREEN after the regex change. (~4 calls)

- [ ] **R9-T15** — `plugin/scripts/check-guards:151` — substitutions() skips double-quoted `$( )`.
      **Fails when:** `n="$(grep -c foo f)"` with no guard scans clean (exit 0) while the unquoted
      form is flagged.
      **Acceptance (shape 2)**: must-fire corpus case for `n="$(grep -c foo f)"` and
      `echo "found $(grep -c x f)"`; RED today; GREEN after. (~4 calls)

- [ ] **R9-T17** — `plugin/scripts/check-guards:92` — an unclosed non-shell fence swallows later
      shell blocks.
      **Fails when:** An unclosed `text`-tagged fence followed by a `bash`-tagged fence containing
      `n=$(grep -c foo f)` exits 0 clean with no unclosed-fence finding; markdownlint in the same
      gate also passes it.
      **Acceptance (shape 2)**: must-fire corpus case with that document; RED today; GREEN after.
      (~4 calls)

- [ ] **R9-T19** — `plugin/scripts/test-guards:593` — the --generated ratchet compares an absolute
      kill count.
      **Fails when:** An edit adds ~10 trivially killed mutants while one previously killed detector
      mutant survives; killed rises 309→318, the ratchet reports 'raised', and the regression shows
      only as an unasserted line in mutation-survivors.txt.
      **Acceptance (shape 2)**: a test-guards integrity case where a new unwaived survivor appears
      alongside a higher kill count; assert --generated fails. RED today. (~5 calls)

- [ ] **R9-T20** — `.github/workflows/checks.yml:36` — the shellcheck install is unpinned despite
      its comment.
      **Fails when:** ubuntu-latest rolls to a newer shellcheck; shellcheck-gate reports new
      findings and CI goes red on a PR that changed nothing — the case the comment claims to
      prevent.
      **Remedy (smallest change):** correct the comment to state the 0.9.0 floor
      `plugin/scripts/check` enforces; do not pin an apt package on `ubuntu-latest`.
      **Acceptance (shape 3)**: dual grep — "Pinned like markdownlint" absent from
      `checks.yml`, and the comment names the same minimum as `require shellcheck` in
      `plugin/scripts/check`. (~3 calls)

- [ ] **R9-T21** — `.gitignore:14` — two `.pyc` files stay tracked despite the new ignore rules.
      **Fails when:** Re-running the spike rewrites the bytecode; `git status` shows both tracked
      .pyc files modified, the churn the new comment says is fixed.
      **Acceptance (shape 4)**: `git ls-files '*.pyc'` prints nothing, with a negative control that
      it prints both paths today. (~2 calls)

- [ ] **R9-T22** — `README.md:311` — the mutation-test numbers match no shipped fixture;
      `plugin/scripts/README.md:193-215` carries a third set.
      **Fails when:** A reader judging check-guards' strength reads 73 cases / 244 of 292 in present
      tense while the fixtures hold 96 cases, 23 mutations, 309 of 367, 58 waivers.
      **Acceptance (shape 3)**: dual grep — the stale figures absent from both READMEs, and the
      figures present match `jq length` on guard-corpus.json and mutation-waivers.json and the
      contents of mutation-ratchet.json. (~4 calls)

- [ ] **R9-T23** — `plugin/scripts/README.md:100` — the `check` gate list omits shellcheck-gate and
      test-phi-patterns.
      **Fails when:** A reader relying on that line concludes shell lint and the PHI scrub patterns
      are not gated by check/CI.
      **Acceptance (shape 3)**: dual grep — line 100 names all seven gates in `check`'s order, and
      `plugin/scripts/check:51-59` is unchanged. (~2 calls)

- [ ] **R9-T24** — `plugin/skills/adversarial-loop/SKILL.md:417` — two self-citations point at
      wrong lines (`:394` → `:191`, `:417` → `:242`).
      **Fails when:** Following `SKILL.md:242` from Phase 5 to check the chaining rule lands on
      unrelated between-rounds text with nothing inline to correct it.
      **Acceptance (shape 5)**: a resolver — for each `SKILL.md:<n>` self-citation in the file,
      the cited line contains the quoted or named text. RED today: 2 of them fail. (~3 calls)

## Implementation notes

- **Decisions taken 2026-09-27 before any task ran** (user, in the release-close session):
  - **Breaker: Blocking.** R9-T1 is a mirror-image regression of the 2.0.1 positional-substitution
    fix. Resolved by a tracer bullet, not full escalation: R9-T0 (a `check-guards` shape) and
    R9-T1 land first, as their own commits, then the rest under `implement`.
  - **R9-T5 and R9-T8** converted from attestations to mechanical tasks with the decisions
    written into them.
  - **Q4:** the missing `claude[bot]` dependency is accepted as the PR-phase test. The stop with
    a clear message is the recorded result; installing the app is a separate repository
    decision.
- **Ordering**: R9-T0, then R9-T1, then loop-correctness (T2, T3, T7, T9, T10, T11, T12), then
  publishing/compliance (T4, T5, T6, T8, T13), then detector gaps (T14, T15, T17, T19), then docs
  (T20–T24). `implement` runs in document order; the IDs are left as filed.
- **Round 9 is post-close.** The parent plan reached `complete` at 86 of 86 on 2026-09-27; this
  round exists because the first PR-loop run was also the first review over the round 6–8 fix
  surface. R9-T2 must land before any re-review of a PR target, or the re-review reads the
  pushed head and misses local fixes — until then, re-review with no target argument.
