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
- **Same file three consecutive rounds (advisory):**
  - It fires for `plugin/skills/adversarial-review/SKILL.md`, which was touched by rounds 8 (R8-T2) and 9 and carries findings in round 10.
  - `plugin/skills/adversarial-loop/SKILL.md` and `plugin/scripts/check-guards` do **not** meet it. `git log` shows fix commits from R4, R5, R7 and R9 on each, and none from R8, so rounds 9 and 10 are only two consecutive.
