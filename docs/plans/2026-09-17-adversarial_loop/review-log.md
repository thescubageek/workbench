# Review ledger — adversarial_loop

One row per finding per round, per `plugin/docs/reference/review-ledger.md`. Rounds 1–8 ran
outside `/wb:adversarial-loop` and left no ledger; round 9 is the first row set, so the
introduced-rate trend has no N−1 to compare against.

`introduced_by` is derived: a finding whose path is in
`git diff --name-only 150949a^..origin/adversarial-loop-skill-research` (round 8's fix surface:
`CHANGELOG.md`, `plugin/skills/adversarial-review/SKILL.md`,
`plugin/skills/update_status/templates/frontmatter-fragments.md`, plan documents) is `prev-fix`.

## Round 9 — 2026-09-28 — PR #25 at `95ffdb4`

| round | file:line | class | verdict | disposition | evidence | introduced_by |
| ----- | --------- | ----- | ------- | ----------- | -------- | ------------- |
| 9 | `plugin/skills/adversarial-review/SKILL.md:297` | positional-token-in-fence | CONFIRMED | Valid | this run received `--plan != ENVIRON[…]`; awk probes exit 0 keeping all lines for a numeric arg; introduced by R7-T1 `4face1f` | prev-fix |
| 9 | `plugin/skills/adversarial-review/SKILL.md:116` | stale-remote-range | CONFIRMED | Valid | range is `origin/<base>...origin/<head>`; no push between Phase 1 rounds | prev-fix |
| 9 | `plugin/skills/adversarial-loop/SKILL.md:135` | undefined-arg-slot | CONFIRMED | Valid | review Arguments define target and `--effort` only; `-e` sniffs a plan dir as path target | pre-existing |
| 9 | `plugin/skills/reply-to-claude/SKILL.md:33` | ignored-pr-arg | CONFIRMED | Valid | `:33`, `:48`, `:90`, `:105` all `gh pr view --json number` with no argument | pre-existing |
| 9 | `plugin/skills/adversarial-review/SKILL.md:234` | review-md-suppression | CONFIRMED | Valid | `:234` allows false-positive entries; `:248-251` concedes author-controlled base; verifier prompt never re-checks them | prev-fix |
| 9 | `plugin/skills/daily-digest/sources.md:227` | phi-pattern-gap | CONFIRMED | Valid | patterns widened in this PR; synthetic `_`-adjacent, doubled and dot-separated IDs unmatched | pre-existing |
| 9 | `plugin/skills/adversarial-loop/SKILL.md:283` | unguarded-capture | CONFIRMED | Valid | `DRAFT=$(…)` has no `\|\|`; `DRAFT=$(false)` → empty → else branch | pre-existing |
| 9 | `plugin/skills/adversarial-loop/SKILL.md:402` | unobservable-gate-signal | CONFIRMED | Valid | review `commit_id` immutable on edit; issue comments have no commit field | pre-existing |
| 9 | `plugin/docs/reference/review-ledger.md:21` | ledger-unstaged | CONFIRMED | Valid | path ignored by `.gitignore:7`; no `git add -f` of `review-log.md` in any shipped file | pre-existing |
| 9 | `plugin/skills/adversarial-loop/SKILL.md:382` | bot-round-unledgered | CONFIRMED | Valid | zero "ledger" hits in Phase 4; step 1 imports dispositions and provenance only | pre-existing |
| 9 | `plugin/skills/adversarial-loop/SKILL.md:346` | poll-error-indistinct | CONFIRMED | Valid | step 3 covers semantic empty results only; step 4 names two causes, neither a failed poll | pre-existing |
| 9 | `plugin/skills/adversarial-review/SKILL.md:211` | wrong-base-for-branch | CONFIRMED | Valid | Step 2 `else` arm serves both no-target and branch-target; Step 1 `:121` handles branches | prev-fix |
| 9 | `plugin/skills/implement_inline/SKILL.md:368` | missing-attestation-path | CONFIRMED | Valid | 0 hits for "attestation" in implement_inline; `implement/SKILL.md:250-263` diverts | pre-existing |
| 9 | `plugin/scripts/check-guards:52` | detector-false-negative | CONFIRMED | Valid | `n=$(grep -cE foo f)` scans clean; `-c` control flagged | pre-existing |
| 9 | `plugin/scripts/check-guards:151` | detector-false-negative | CONFIRMED | Valid | `n="$(grep -c foo f)"` scans clean; unquoted control flagged | pre-existing |
| 9 | `plugin/scripts/check-guards:333` | detector-false-negative | CONFIRMED | Over-fitted | needs an unguarded outer glob loop with a guarded inner glob loop inside the 4-line window; no instance in the tree | pre-existing |
| 9 | `plugin/scripts/check-guards:92` | detector-false-negative | CONFIRMED | Valid | unclosed `text` fence disables scanning of the rest of the file silently; markdownlint passes it | pre-existing |
| 9 | `plugin/scripts/test-guards:561` | corpus-floor-missing | CONFIRMED | Over-fitted | trigger is a deliberate deletion from the test fixture, visible in any diff | pre-existing |
| 9 | `plugin/scripts/test-guards:593` | ratchet-count-only | CONFIRMED | Valid | `killed` is a count; new unwaived survivors are written to survivors.txt and never asserted | pre-existing |
| 9 | `.github/workflows/checks.yml:36` | comment-contradicts-code | CONFIRMED | Real but disproportionate | apt install unpinned; `check` enforces a 0.9.0 floor — remedy is to correct the comment, not pin apt | pre-existing |
| 9 | `.gitignore:14` | tracked-bytecode | CONFIRMED | Valid | two `.pyc` under `thoughts/spike/__pycache__/` tracked since `52828f6` | pre-existing |
| 9 | `README.md:311` | stale-doc-figures | CONFIRMED | Valid | README 73/22/244-of-292/48 vs fixtures 96/23/309-of-367/58 | pre-existing |
| 9 | `plugin/scripts/README.md:100` | stale-doc-figures | CONFIRMED | Valid | omits shellcheck-gate and test-phi-patterns vs `check:51-59` | pre-existing |
| 9 | `plugin/skills/adversarial-loop/SKILL.md:417` | dangling-self-citation | CONFIRMED | Valid | `:394`→`:191` (text at `:264`), `:417`→`:242` (rule at `:303`) | pre-existing |
| 9 | `plugin/skills/adversarial-loop/reference.md:53` | unobservable-gate-signal | PLAUSIBLE | Over-fitted | trigger unobservable: zero claude[bot] activity across PRs 1–25; R9-T8's attestation settles the surface | pre-existing |

Dropped by verification (REFUTED, not ledgered as findings): `plugin/scripts/check-guards:434`
zero-scan exit 0 — deliberate and tested at `test-guards:201-220`, unreachable from `check:55`;
Step 8 `git add -f` staging published silently — `adversarial-review/SKILL.md:463-468` requires
reporting the plan as staged.

### Breaker, after round 9

- **Introduced-rate trend:** 4 of 25 `prev-fix` (16%). No round-8 ledger row exists, so the trend
  cannot be evaluated. Not a clean result: there is no N−1.
- **Mirror-image regression — candidate, surfaced for a decision:** the `:297` awk `$1` was
  introduced by R7-T1 (`4face1f`), the fix that made the blast-radius exclusion literal. It
  reintroduces the positional-substitution class the 2.0.1 release removed ("Do not write
  `target=$1` in a fenced block"). If that counts as a mirror image, the breaker is **Blocking**:
  stop fixing, escalate `adversarial-review` Step 3 to research/design, and fire a tracer bullet
  before another attempt.
  **Decided 2026-09-27: it counts. Blocking, resolved by tracer bullet — R9-T0 adds the
  `check-guards` shape, R9-T1 rewrites without a positional token; both land before the rest.**
- **Same file three consecutive rounds (advisory):** `plugin/skills/adversarial-review/SKILL.md`
  was touched by round 7 (R7-T1) and round 8 (R8-T2) and carries findings in round 9.

## Round 10 — 2026-09-28 — PR #25 at `3b4e04b` (own checkout, `origin/main...HEAD`)

`introduced_by` derived from `git diff --name-only 95ffdb4..HEAD` (round 9's fix surface, 33
files). Every path below is in it except `plugin/scripts/check` and
`plugin/skills/implement/SKILL.md`.

| round | file:line | class | verdict | disposition | evidence | introduced_by |
| ----- | --------- | ----- | ------- | ----------- | -------- | ------------- |
| 10 | `plugin/skills/daily-digest/sources.md:227` | phi-pattern-gap | CONFIRMED | Valid | python probe: `%3A`/`%2F`/`%20`-adjacent, `/`, `:`, 3-char, en-dash, NBSP separators unmatched; `:223-224` promises extra separators | prev-fix |
| 10 | `plugin/skills/adversarial-loop/SKILL.md:234` | ledger-unstaged | CONFIRMED | Valid | step 5 stages after step 3's commit and implement's commits; Phase 2 `:295` porcelain guard exits 1 | prev-fix |
| 10 | `plugin/skills/adversarial-loop/SKILL.md:392` | ledger-unstaged | CONFIRMED | Valid | Phase 4 step 3 stages; no commit when all rejected or breaker stops; no porcelain check in Phases 4–5 | prev-fix |
| 10 | `plugin/skills/adversarial-review/SKILL.md:125` | fork-pr-name-match | CONFIRMED | Valid | `:125`, `:221` compare `headRefName` to branch name only; 0 hits for `isCrossRepository` | prev-fix |
| 10 | `plugin/skills/adversarial-review/SKILL.md:121` | stale-remote-range | CONFIRMED | Valid | off-checkout PR range is `origin/<head>` with no fetch or `headRefOid` compare | prev-fix |
| 10 | `plugin/scripts/check-guards:389` | zsh-path-clobber | CONFIRMED | Valid | FIXES says `read -r path _`; zsh probe printed NO_SED; contradicts `adversarial-review/SKILL.md:376` | prev-fix |
| 10 | `plugin/skills/adversarial-review/SKILL.md:87` | positional-token-in-prose | CONFIRMED | Valid | this run received `target=--plan=docs/plans/2026-09-17-adversarial_loop` in both bodies | prev-fix |
| 10 | `plugin/scripts/check-guards:58` | detector-false-negative | CONFIRMED | Real but disproportionate | `SHELL_INFO` = bash/sh/shell; zsh `t=$1` unflagged — add `zsh`, keep prose unscanned (implement's `$1` is intended) | prev-fix |
| 10 | `plugin/skills/adversarial-loop/SKILL.md:353` | poll-no-baseline | CONFIRMED | Valid | no pre-summons id/`updated_at` capture anywhere in SKILL.md or reference.md | prev-fix |
| 10 | `plugin/skills/reply-to-claude/SKILL.md:20` | target-not-checkout | CONFIRMED | Valid | Step 1 reads no `headRefName`/`headRefOid`; Step 3 reads the working tree | prev-fix |
| 10 | `plugin/scripts/check-guards:174` | detector-false-positive | CONFIRMED | Valid | `f="cost \$(grep -c q f)"` exits 1; `475e656^` exits 0 — regression from R9-T15 | prev-fix |
| 10 | `plugin/scripts/check-guards:180` | detector-false-negative | CONFIRMED | Valid | nested-span probe exits 0; control without `\|\| true` flagged | prev-fix |
| 10 | `plugin/scripts/check-guards:62` | detector-false-negative | CONFIRMED | Valid | GUARD `\|\|\s*(?:true\b\|:(?!\w)\|echo\b)`; `\|\| echo 0` scans clean, yields "0\n0" | prev-fix |
| 10 | `plugin/skills/adversarial-review/SKILL.md:321` | dead-guard | CONFIRMED | Valid | six probed inputs incl. `pipefail` all give `filter=0` | prev-fix |
| 10 | `plugin/scripts/check:42` | version-check-skipped | CONFIRMED | Valid | fake shellcheck printing `garbage`, exit 3 → `require` rc 0 | pre-existing |
| 10 | `plugin/skills/adversarial-review/SKILL.md:220` | empty-equals-empty | CONFIRMED | Over-fitted | needs detached HEAD plus a gh failure in Step 2 after Step 1's gh call succeeded in the same run (`:123` returns first) | prev-fix |
| 10 | `plugin/skills/adversarial-loop/SKILL.md:425` | phase5-lookup | CONFIRMED | Valid | no `--paginate`/`per_page`; endpoint pages at 30; `reply-to-claude/SKILL.md:69` calls it mandatory | prev-fix |
| 10 | `plugin/scripts/test-guards:515` | ratchet-cannot-fall | CONFIRMED | Real but disproportionate | only `killed` compared, `of` never read, written only on rise — fix the message and README, not the design | prev-fix |
| 10 | `plugin/scripts/test-guards:585` | test-coverage-gap | CONFIRMED | Valid | single call `ratchet_verdict(318, 309, [survivor], [])`; stale and `killed < prev` branches never entered | prev-fix |
| 10 | `README.md:305` | stale-doc-figures | CONFIRMED | Valid | "three shapes" / `plugin/scripts/README.md:142` "Four shapes" vs `check-guards:4` "Six shapes" | prev-fix |
| 10 | `plugin/scripts/check-guards:160` | detector-false-negative | CONFIRMED | Over-fitted | needs `'\''` on the same line as an unguarded capture; pre-R9-T15 identical; no instance in the tree | prev-fix |
| 10 | `plugin/scripts/check-guards:430` | wrong-label | CONFIRMED | Valid | lone unclosed `text` fence reported as "unclosed shell fence"; fails closed, label and advice wrong | prev-fix |
| 10 | `plugin/skills/adversarial-loop/SKILL.md:422` | unobservable-gate-signal | PLAUSIBLE | Over-fitted | `:428-431` offers an exit ("say that the label covers a range the bot did not read"); check-run shape unobserved, `:434` provisional; Q4 | prev-fix |
| 10 | `plugin/skills/adversarial-loop/SKILL.md:393` | round-number-collision | PLAUSIBLE | Valid | bot round writes no `reviews/` dir; `remediation-plan.md:142` derives `<N>` from dirs; this run ledgers round 10 = dir N | prev-fix |
| 10 | `plugin/skills/reply-to-claude/SKILL.md:131` | untrusted-text-relay | PLAUSIBLE | Valid | body rules at `:131-150` never require paraphrase or `@` defanging; `:87` concedes relayed text | prev-fix |
| 10 | `plugin/skills/adversarial-loop/SKILL.md:290` | prose-only-precondition | PLAUSIBLE | Valid | block never compares PR head to the checkout; Phase 0 `:125` is prose only | prev-fix |
| 10 | `plugin/skills/implement_inline/SKILL.md:347` | missing-attestation-path | PLAUSIBLE | Valid | BARRIER 2 unqualified; `349e471` added no barrier hunk; `implement/SKILL.md:449-450` has the carve-out | prev-fix |
| 10 | `plugin/skills/adversarial-loop/SKILL.md:425` | phase5-lookup | PLAUSIBLE | Valid | `$REPO` has one hit, `:425`, never bound; `gh api` accepts `{owner}/{repo}` | prev-fix |
| 10 | `plugin/skills/implement/SKILL.md:46` | positional-token-in-prose | PLAUSIBLE | Pre-existing | same tokens on `origin/main` at `:44-45`, `:155`; this PR moved them, did not add them; index mapping unverified | pre-existing |
| 10 | `plugin/scripts/test-phi-patterns:35` | test-coverage-gap | PLAUSIBLE | Valid | BM-only first pattern passes 18/18; revert of R9-T6 fails 14/18 (that half refuted) | prev-fix |
| 10 | `plugin/skills/adversarial-review/SKILL.md:313` | blast-radius-noise | PLAUSIBLE | Valid | clone probe after a commit naming `shellcheck-gate`: 3 `.git` text hits + binary index match; not in a worktree | prev-fix |

Dropped by verification (REFUTED, not ledgered as findings):

- Phase 5 "completed" admits a skipped run. `adversarial-loop/SKILL.md:427-428` already excludes skipped.
- Phase 2/5 read an unbound `target`. The Phase 0 guard at `:125` makes the current-branch PR the target PR.
- The mutation ratchet is absent from `check`/CI. That is documented at `plugin/scripts/README.md:211` and `README.md:319`.
- `/wb:help` lacks `--plan`. Help abbreviates every hint (`--auto` appears nowhere in it).

### Breaker, after round 10

- **Introduced-rate trend: Blocking.** 29 of 31 `prev-fix` (94%), against round 9's 4 of 25 (16%). The rate did not fall; it rose. Both rounds are above the three-finding floor.
  - **Caveat, per `review-ledger.md`:** round 9's fix surface is 33 files and covers every path carrying a round-10 finding except `plugin/scripts/check` and `plugin/skills/implement/SKILL.md`. Path intersection approaches the one-file limitation that document names. Read the rise partly as "the breaker cannot tell" rather than as clean evidence of causation.
  - It is not wholly noise. R10-T10 is caused by R9-T15, and R10-T5 by R9-T0.
- **Mirror-image regression — candidates, surfaced for a decision:**
  - `adversarial-review/SKILL.md:125` (fork PR resolved to local HEAD) is the inverse of R9-T2/R9-T26. That fix was for "a PR target reviews the origin head, not the local commits"; this finding is "a PR target reviews the local HEAD, not the PR".
  - `check-guards:174` (`\$(` false positive) is the inverse of R9-T15. R9-T15 fixed "double-quoted `$(` never scanned"; this is "a literal `\$(` in double quotes is scanned".
  - If either counts, the breaker is Blocking on that trigger too.
  - **Decided 2026-09-28: both count.** Each is the round-9 fix's own axis flipped — which head a
    PR target reviews (R9-T2/R9-T26 → R10-T3), what counts as a substitution inside double quotes
    (R9-T15 → R10-T10) — and each names a component the introduced-rate trend already points at.
    Blocking on the mirror-image trigger for `adversarial-review` Steps 1–2 and for
    `check-guards`' lexer.
- **Escalation, decided 2026-09-28 (user):** `create_research` then `create_design` on two
  components — the `check-guards` lexer (T5, T7, T10, T11, T12, T21) and `adversarial-review`
  target resolution (T3, T4, T13, T29) — in a **new plan directory** —
  `docs/plans/2026-09-28-guard_lexer_and_pr_identity/` — folded into 3.0.0 on this branch
  before PR #25 merges. One tracer bullet per component before any fix. Cluster 3
  (`adversarial-loop` publishing and ledger mechanics, `reply-to-claude`) and the eight standalone
  findings stay in round 10 as ordinary tasks, worked after the escalation lands.
- **Same file three consecutive rounds (advisory):**
  - It fires for `plugin/skills/adversarial-review/SKILL.md`, which was touched by rounds 8 (R8-T2) and 9 and carries findings in round 10.
  - `plugin/skills/adversarial-loop/SKILL.md` and `plugin/scripts/check-guards` do **not** meet it. `git log` shows fix commits from R4, R5, R7 and R9 on each, and none from R8, so rounds 9 and 10 are only two consecutive.
- **Escalation landed, 2026-10-01:** `docs/plans/2026-09-28-guard_lexer_and_pr_identity/` (design: `design.md` there) closed the ten held round-10 tasks (T3, T4, T5, T7, T10, T11, T12, T13, T21, T29), each recorded by pointer in the round's `tasks.md`. R10-T3 is resolved by commit, not refusal: a cross-repository PR is fetched and reviewed at its own head with disclosed provenance. The fifteen ordinary tasks are now unblocked.

## Round 11 — 2026-10-01 — PR #25 at `cc331f8` (own checkout, `origin/main...HEAD`)

`introduced_by` derived from `git log --first-parent --no-merges --name-only 3b4e04b..HEAD` (round 10's
fix surface plus the guard_lexer_and_pr_identity plan, 45 files). Three of nineteen paths are outside it:
`plugin/skills/implement/SKILL.md`, `plugin/docs/reference/technical-english.md` and `plugin/scripts/test-quiet`.

| round | file:line | class | verdict | disposition | evidence | introduced_by |
| ----- | --------- | ----- | ------- | ----------- | -------- | ------------- |
| 11 | `plugin/skills/adversarial-loop/SKILL.md:323` | stacked-branch-identity | CONFIRMED | Valid | scratch repo: is-ancestor passes on a stacked branch; push went to feature-B, origin/feature-A unchanged; `@{push}` would catch it | prev-fix |
| 11 | `plugin/skills/implement/SKILL.md:365` | round-journal-staging | CONFIRMED | Valid | throwaway repo: `git add -f r/tasks.md r/journal.md` exits 128 and stages nothing, so the commit is skipped | pre-existing |
| 11 | `plugin/skills/adversarial-loop/SKILL.md:318` | target-not-restated | CONFIRMED | Valid | Phase 2 and 5 blocks carry no `target=` and Phase 0 has no re-state sentence; adversarial-review `:77` and reply-to-claude `:36` do | prev-fix |
| 11 | `plugin/skills/adversarial-loop/SKILL.md:301` | baseline-not-rerecorded | CONFIRMED | Valid | `baseline` appears only in Phase 2 and Phase 3; Phase 4 never re-records before a re-summon | prev-fix |
| 11 | `plugin/skills/daily-digest/sources.md:227` | phi-separator-gap | CONFIRMED | Valid | `BM+CA+12345678` matches neither pattern (Python re.search); the `%20` form is pinned and scrubbed | prev-fix |
| 11 | `plugin/skills/adversarial-loop/SKILL.md:244` | ledger-commit-pathspec | PLAUSIBLE | Valid | commit has no pathspec so it commits the whole index; Phase 1 has no clean-tree precondition | prev-fix |
| 11 | `plugin/scripts/fixtures/mutation-waivers.json:99` | non-equivalent-waivers | CONFIRMED | Valid | scratch checker: two captures on one line reported twice with the break deleted, a glob loop seven times; parse_findings is a set | prev-fix |
| 11 | `plugin/scripts/test-guards:528` | ratchet-boundary-untested | CONFIRMED | Valid | `<=` mutant leaves all four verdict checks green; probe with equal totals returns the shrunk message | prev-fix |
| 11 | `plugin/scripts/check-guards:206` | strip-comment-backtick | CONFIRMED | Pre-existing | known follow-up since P1-T2; valid only for a `#` after whitespace inside a backtick span followed by a second capture; reachability unchanged by this round | prev-fix |
| 11 | `plugin/skills/adversarial-loop/SKILL.md:458` | stale-citations | CONFIRMED | Valid | `SKILL.md:273` is blank-adjacent prose (text at 289); `:299` should be 349; hook sentence contradicts CLAUDE.md | prev-fix |
| 11 | `plugin/docs/reference/technical-english.md:133` | stale-citations | CONFIRMED | Valid | `implement/SKILL.md:242-245` is now BARRIER 2; Status headings at 342-343 | pre-existing |
| 11 | `plugin/scripts/README.md:241` | readme-counts | CONFIRMED | Valid | `jq length fixtures/guard-corpus.json` returns 128; READMEs say 114 and 15 | prev-fix |
| 11 | `plugin/scripts/test-guards:171` | negatives-hide-crash | CONFIRMED | Valid | wrapper that exits 1 with a traceback on clean input scores tn=60 fp=0 | prev-fix |
| 11 | `plugin/scripts/test-quiet:1` | test-quiet-gaps | CONFIRMED | Valid | `lines=99` and delete-log-on-success mutants both leave 9 passed | pre-existing |
| 11 | `plugin/scripts/test-guards:528` | shrunk-branch-drop-size | PLAUSIBLE | Valid | branch fires on any killed fall with a smaller total; needs an idle waiver to absorb the lost kill | prev-fix |
| 11 | `plugin/skills/reply-to-claude/SKILL.md:54` | identity-polarity-drift | PLAUSIBLE | Real but disproportionate | review `:115` uses `!= true`, reply `:54` and loop `:323` use `= false`; no realistic trigger; fix the prose, not the blocks | prev-fix |
| 11 | `plugin/skills/adversarial-loop/SKILL.md:466` | phase5-gate-unmeetable | PLAUSIBLE | Over-fitted | depends on an unobserved workflow trigger; the skill marks it provisional and gives the explicit exit at `:476-478` | prev-fix |
| 11 | `plugin/scripts/test-guards:665` | stored-total-stale | PLAUSIBLE | Over-fitted | pass or fail depends only on `killed < prev`; a stale `of` changes the message wording only | prev-fix |
| 11 | `.github/workflows/checks.yml:57` | sweep-timeout | PLAUSIBLE | Real but disproportionate | no hang input found; add `timeout-minutes` only, skip the subprocess timeout | prev-fix |

Dropped by verification (REFUTED, not ledgered as findings):

- `{owner}/{repo}` in the Phase 5 lookup. `gh api` resolves it with the same base-repo logic as `gh repo view`; this checkout agrees (`thescubageek/workbench`).
- Refusal when `headRefOid` is not fetched. `--is-ancestor` exits 128 and the refusal is the correct fail-closed outcome; only the message is thin.
- Ledger and plan commits after a clean pass. The gate text is about reviewable content, and Phase 1 step 3 already says the pass still certifies the tree.
- An attestation task pinning `current_phase`. Checkpoint boxes are not ID'd task lines, and a round has no phase.
- No PHI rule in the review path. A policy preference, and the operator layer already applies; the plugin creates no PHI.
- CI Python version drift. CI ran 3.12.3 and reproduced 378/421, 43 waived, 0 survived.
- The `test-count` pre-checks. Only the exit status and empty stdout are a documented contract.

Two further candidates were preferences, not defects: the comment-density rule for `test-check`, and force-adding plan files against the plan-promotion convention.

### Breaker, after round 11

- **Introduced-rate trend: not Blocking.** 16 of 19 `prev-fix` (84%), against round 10's 29 of 31 (94%). The rate fell. Both rounds are above the three-finding floor.
  - **Caveat, per `review-ledger.md`:** the fix surface is 45 files and covers 16 of 19 finding paths, so path intersection is a weak proxy here. Read the fall as modest.
- **Mirror-image regression: none.** R11-T1 tightens the ancestry test R10-T3 introduced, and R11-T3 and R11-T4 extend R10-T8 and R10-T25; none is the inverse of an earlier fix.
- **Same file three consecutive rounds (advisory):** `plugin/skills/adversarial-loop/SKILL.md` carries findings in rounds 9, 10 and 11. Treat further Phase edits there as one change set.

## Round 12 — 2026-10-01 — PR #25 at `6cd1d71` (own checkout, `origin/main...HEAD`)

`introduced_by` derived from `git log --first-parent --no-merges --name-only cc331f8..HEAD` (round 11's
fix surface, 20 files). Two of ten paths are outside it: `plugin/scripts/check` and `CHANGELOG.md`.

| round | file:line | class | verdict | disposition | evidence | introduced_by |
| ----- | --------- | ----- | ------- | ----------- | -------- | ------------- |
| 12 | `plugin/skills/adversarial-loop/SKILL.md:136` | fetched-target-fixes-here | CONFIRMED | Valid | Phase 0 stops at 'the end of Phase 1' and Phase 1 steps 3-6 run implement, commit the ledger and re-review on the current checkout; nothing there reads review_provenance | prev-fix |
| 12 | `plugin/skills/adversarial-loop/SKILL.md:253` | ledger-missing-exit-128 | CONFIRMED | Valid | block run under zsh with no review-log.md exits 128; the ledger is one row per finding so a zero-finding first round never creates it | prev-fix |
| 12 | `plugin/docs/reference/technical-english.md:109` | task-lines-citation | CONFIRMED | Valid | Step 6a holds no `[A-Z0-9-]*[0-9][A-Z0-9-]*` parser; the first-unchecked rule is Step 4 BARRIER 2 | prev-fix |
| 12 | `plugin/skills/reply-to-claude/SKILL.md:20` | preconditions-stale-remedy | CONFIRMED | Valid | bullet says 'at or descended from' while Step 1 requires the PR's own branch; remedy 'check out its branch' is wrong after a rename (smaller change: this skill only) | prev-fix |
| 12 | `plugin/skills/reply-to-claude/SKILL.md:92` | inline-line-null | PLAUSIBLE | Valid | jq on a synthetic sample prints `a.py:null` for line null; no round scoping in Step 2 | prev-fix |
| 12 | `plugin/skills/adversarial-loop/SKILL.md:410` | in-progress-arrival | PLAUSIBLE | Over-fitted | depends on unobserved bot behaviour; the skill marks the check-run provisional and Phase 5 requires a completed check-run | prev-fix |
| 12 | `plugin/scripts/test-phi-patterns:44` | plus-cases-not-discriminating | CONFIRMED | Valid | both + cases match both patterns (re.search per pattern); BM+CA+1234567 and BMCA+12345678 each match one | prev-fix |
| 12 | `plugin/skills/adversarial-loop/SKILL.md:354` | push-destination | PLAUSIBLE | Pre-existing | bare git push predates round 11; needs two remotes with a same-repo PR in the parent; gh remote ranking unverified | prev-fix |
| 12 | `plugin/scripts/check:60` | zero-files-floor | PLAUSIBLE | Over-fitted | exit 0 on zero files is documented and tested; dispatch and default-target wiring are covered by fixtures | pre-existing |
| 12 | `CHANGELOG.md:175` | changelog-order | CONFIRMED | Valid | 2.1.0 section added by this PR sits above released 2.2.0 and 2.1.1; 3.0.0 section never mentions WBTE | pre-existing |

Dropped by verification (REFUTED or out of range, not ledgered as findings):

- The literal `target=""` re-statement. Phase 0 only lets Phases 2 and 5 run when the identity line starts with `HEAD`, and then the current-branch PR is the target PR.
- `lint-common.sh`, `evals/judge.py`, `evals/wbte_check.py` and `evals/run.py`. None is in `origin/main...HEAD`.
- `plugin/scripts/check` omitting the 2.2.0 tests. Known; the user has not decided.
- The PHI digit-group variants. Already adjudicated in round 11.

### Breaker, after round 12

- **Introduced-rate trend: not Blocking.** 8 of 10 `prev-fix` (80%), against round 11's 16 of 19 (84%). The rate fell. Both rounds are above the three-finding floor.
  - **Caveat, per `review-ledger.md`:** round 11's fix surface is 20 files and covers 8 of 10 finding paths, so path intersection is a weak proxy. Read the fall as modest.
- **Mirror-image regression: none.** R12-T1 follows from R11-T1's added branch-name test sending more targets down the fetch path. Fixing it adds a stop rule and does not invert R11-T1.
- **Same file three consecutive rounds (advisory):** `plugin/skills/adversarial-loop/SKILL.md` carries findings in rounds 9, 10, 11 and 12, and `plugin/skills/reply-to-claude/SKILL.md` in rounds 10, 11 and 12. Treat further edits to either as one change set.

## Round 13 — 2026-10-01 — PR #25 at `72f8210` (own checkout, `origin/main...HEAD`)

`introduced_by` derived from `git log --first-parent --no-merges --name-only 6cd1d71..HEAD` (round 12's
fix surface, 11 commits and 5 files). Two of twelve paths are outside it: `plugin/skills/adversarial-review/SKILL.md` (no finding) and `plugin/scripts/test-guards`.

| round | file:line | class | verdict | disposition | evidence | introduced_by |
| ----- | --------- | ----- | ------- | ----------- | -------- | ------------- |
| 13 | `plugin/skills/adversarial-loop/SKILL.md:136` | stop-rule-head-prefix | CONFIRMED | Valid | scratch run: a branch target HEAD-fix prints `identity: HEAD-fix (branch; …)` and passes a starts-with-HEAD test; a branch target naming the current branch prints `<branch> (branch; …)` and stops the loop | prev-fix |
| 13 | `plugin/skills/adversarial-loop/SKILL.md:139` | stopped-run-staged-plan | CONFIRMED | Valid | Step 8 stages the round plan under --plan before the stop rule applies; step 3's pruning is skipped; step-2 dispositions reach no ledger | prev-fix |
| 13 | `plugin/skills/adversarial-loop/SKILL.md:258` | ledger-guard-silent-skip | CONFIRMED | Valid | the [ -f ] guard checks nothing about a zero-finding round, so a mistyped or unwritten ledger exits 0 where the old block exited 128 | prev-fix |
| 13 | `plugin/skills/reply-to-claude/SKILL.md:58` | refusal-remedies | CONFIRMED | Valid | branch refusal tells the model to push and reopen the PR with no confirmation; ancestry refusal says check out its branch after the branch already matched | prev-fix |
| 13 | `plugin/skills/reply-to-claude/SKILL.md:92` | step2-dates-outdated | PLAUSIBLE | Valid | filter prints no dates and shows an outdated comment's original_line unmarked | prev-fix |
| 13 | `plugin/scripts/test-phi-patterns:44` | separator-members-unpinned | CONFIRMED | Valid | in-process: 17 single-pattern separator deletions and the {0,3}/{1,3} bounds pass all 35 cases; em dash has no case | prev-fix |
| 13 | `plugin/docs/reference/technical-english.md:110` | task-lines-citation | CONFIRMED | Valid | BARRIER 2 has no ID shape or [x] pattern; the other three citations name the real homes | prev-fix |
| 13 | `plugin/scripts/test-guards:544` | shrink-excuse-heuristic | PLAUSIBLE | Over-fitted | the verdict still fails and the maintainer lowers the count by hand; only the message wording is at stake | pre-existing |
| 13 | `plugin/skills/adversarial-loop/SKILL.md:175` | identity-guard-copies | PLAUSIBLE | Over-fitted | three copies of one guard is a maintainability preference; the asymmetry is already documented and no wrong outcome was shown | prev-fix |
| 13 | `plugin/scripts/test-guards:142` | found-line-header-match | PLAUSIBLE | Over-fitted | needs a finding whose raw statement ends in colon and digits while containing a slash; a capture statement ends in a closing parenthesis | pre-existing |
| 13 | `CHANGELOG.md:14` | unreleased-date | PLAUSIBLE | Over-fitted | 3.0.0 is untagged, so its date is the planned release date and is set at release | prev-fix |
| 13 | `plugin/skills/adversarial-loop/SKILL.md:258` | changed-blocks-untested | PLAUSIBLE | Over-fitted | check-guards flags only publish-class commands, which the ledger block has none of; the blocks were executed in scratch repos each round | prev-fix |

Dropped (REFUTED or already adjudicated, not ledgered as findings):

- The PHI separator variants (digit groups, tab, U+2011). Adjudicated Over-fitted in round 11.
- The literal `target=""` re-statement. Refuted in round 12.
- The stale `of` in the ratchet file. Adjudicated Over-fitted in round 11.
- Deleted waivers justified only by the ratchet number. The three corpus cases (`s1-two-captures-one-line`, `s2-two-includes-one-line`, `s3-unguarded-loop-long-body`) exist, and each mutant was shown to fail one in a scratch copy.

### Breaker, after round 13

- **Introduced-rate trend: Blocking.** 10 of 12 `prev-fix` (83%), against round 12's 8 of 10 (80%) and round 11's 16 of 19 (84%). The rate did not fall from round 12 to round 13. Both rounds are above the three-finding floor.
  - **Caveat, per `review-ledger.md`:** round 12's fix surface is 5 files and every confirmed finding sits in three of them (`adversarial-loop/SKILL.md`, `reply-to-claude/SKILL.md`, `test-phi-patterns`). Path intersection is a weak proxy on a surface this small. Read the trip as "the breaker cannot tell", but the ledger rule is mechanical and does not wait for that judgement.
- **Mirror-image regression: candidate, surfaced for a decision.** `stop-rule-head-prefix` follows from R12-T1: the stop rule it added keys on the same `HEAD` prefix that already misread a branch target naming the current branch, and now also misreads a branch named `HEAD-fix`. It is the same axis (which identity lines count as the current checkout) fixed in round 12 and broken both ways in round 13. If it counts, the breaker is Blocking on that trigger too.
- **Same file three consecutive rounds (advisory):** `plugin/skills/adversarial-loop/SKILL.md` carries findings in rounds 9, 10, 11, 12 and 13, and `plugin/skills/reply-to-claude/SKILL.md` in rounds 10 to 13.
- **Held 2026-10-01 (surfaced to the user):** no round-13 task is worked and no round 14 runs. The seven Valid findings are in `reviews/2026-10-01-round-13/tasks.md`, held for the decision.
- **Escalation landed, 2026-10-02:** `docs/plans/2026-10-01-pr_identity_contract` (design.md decisions PD5 to PD8, with `plugin/scripts/pr-identity` and `plugin/scripts/test-pr-identity` in `check`) closed R13-T1 to R13-T4 by P2-T4, P2-T3, P2-T6 and P2-T7. R13-T5 to R13-T7 are unheld.
