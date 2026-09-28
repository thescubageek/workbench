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
