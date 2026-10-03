# First PR-phase run of `/wb:adversarial-loop` — PR #25

Run 2026-09-27 (local, PDT) / 2026-09-28 (UTC). Invocation: `/wb:adversarial-loop 25`.
Stopped after Phase 1 adjudication and prune, as instructed. `implement` was not invoked.

## Preconditions

| Check | Result |
| ----- | ------ |
| "While auto mode is active" block in context | absent |
| `claude --plugin-dir plugin plugin details wb` | `wb 3.0.0` · `Source: wb@inline` |
| `pwd` | `/Users/scraig/conductor/workspaces/workbench/ankara` |
| `pwd -P` | `/Users/scraig/conductor/workspaces/workbench/ankara` |
| `git status --short` | empty (the rtk proxy printed `ok`; `rtk proxy git status --short \| wc -l` → `0`) |
| HEAD | `adversarial-loop-skill-research` at `5c74e60`, descendant of `95ffdb4` |

## Phase 0 binding

`target=25`. `gh pr view 25` → head `adversarial-loop-skill-research` (the checked-out branch),
base `main`, `isDraft: false`, head OID `95ffdb4`. The target names the current checkout, so the
PR phases stayed in scope. Local HEAD `5c74e60` was one commit ahead of the PR head. That commit
touches only plan documents.

## Review reconnaissance, verbatim

```text
🔎 Reconnaissance — PR #25 (origin/main...origin/adversarial-loop-skill-research @ 95ffdb4), 107 files
   Paths           high     skill/agent definitions (executed prose), hooks, release scripts, a new CI workflow
   Behaviour       high     new adversarial-loop skill directs git push, gh pr ready, @claude comments, labels; CI now executes repo scripts on pull_request
   Blast radius    medium   measured: callers outside the diff — scripts/quiet → tdd-discipline/SKILL.md, implement_inline/templates/modified-files-fragment.md; scripts/lint, lint-hook → CLAUDE.md; wb-prime.sh → doc-adherence/SKILL.md + 2 maintainer docs; branch-naming.md → create_project, jira-context, CLAUDE.md; count, review-ledger.md, remediation-plan.md → none (control symbol → 0, search confirmed live)
   Coupling        high     6 subsystems: skills, agents, hooks, scripts, CI, maintainer docs/plans
   Reversibility   medium   3.0.0 version bump — marketplace cache is keyed on version, so a shipped 3.0.0 cannot be re-cut under the same number
   Test evidence   medium   scripts have contract tests (test-guards, test-count, test-quiet, test-phi-patterns, mutation ratchet); skill prose has only check-guards' fenced-block scan

   Tier: top, set by Behaviour (outward-facing git/gh actions directed by prose)
   Lenses: AI-systems (skill/agent prose, mandatory), security (outbound gh calls + bot-relayed text reaching a comment body, mandatory), cross-file tracer (callers outside the diff above, mandatory), release engineer (checks.yml, plugin.json/marketplace.json, check gate), test-quality (test-guards/mutation fixtures), SRE (Phase 3 bounded wait on CI + claude[bot])  ·  dropped: backend (no persistence), frontend (no rendering), data (no schema), localization (no locale files)
   Effort: high — coverage at the top tier; round 9 over a range eight rounds have already swept, so recall over precision
   Coverage: 107 files / +17,166 −211 resolved  ·  6 lenses + the built-in leg
```

- **Tier:** top.
- **Deciding axis:** Behaviour.
- **`Coverage:` line:** emitted, **with a shortfall**:

```text
⚠️ Coverage shortfall — 107 files / +17,166 lines, 6 lenses + the built-in leg: the lens triggers
   matched 74 files (6,966 lines), and the other 33 (10,411 lines — docs/plans/**, CHANGELOG.md,
   README.md, .claude/wb/knowledge.md, docs/commands-reference.md) were reached by the built-in leg alone
```

Other lines the review emitted:

- `REVIEW.md` was read from `origin/main` (merge-base `46ef587`) and is absent on the base:
  `fatal: path 'REVIEW.md' does not exist in '46ef587…'`.
- `🔍 Built-in leg: /code-review high → 10 findings`. The call returned
  `launched (forked execution, running in the background)`, and the findings came back as prose.

## Pool, verify, report

- **Candidates:** 31 (built-in 10, security 4, AI-systems 5, release 2, cross-file 3,
  test-quality 2, SRE 5).
- **Dedupe:** 4 pairs collapsed, leaving 27.
- **Verification:** 27 verifiers returned 24 CONFIRMED, 1 PLAUSIBLE and 2 REFUTED.
  - REFUTED: `check-guards:434` zero-scan exit, and Step 8's `git add -f` publishing silently.
  - One clearance conflict (release leg vs built-in on the zero-scan exit) was resolved by its
    verifier for the clearance.
- `ReportFindings` was called with 25 findings at `level: high`.

## Step 8

- **Round directory written:** yes. `docs/plans/2026-09-17-adversarial_loop/reviews/2026-09-28-round-9/tasks.md`.
- **Staged:** yes. `git add -f` exit 0 (`A  …/2026-09-28-round-9/tasks.md`). Not committed.
- **`<plan>`** = `docs/plans/2026-09-17-adversarial_loop`, named by the loop.
- **`<N>`** = `9`, one more than the highest existing (`2026-09-26-round-8`).
- **`<date>`** = `2026-09-28`, from `date -u +%F`. The local date was `2026-09-27`, and the run
  crossed UTC midnight at 17:00 PDT.
- **Against the expectation:** the expected path was `reviews/2026-09-27-round-9/`. The actual path
  is `reviews/2026-09-28-round-9/`. Findings survived, so a round directory was written; the
  divergence is the date component only, by the UTC rule in `remediation-plan.md`.

## Adjudication and prune

Adjudicated 25:

- **Valid:** 21.
- **Real but disproportionate:** 1 (R9-T20; the remedy was rewritten to a comment fix).
- **Over-fitted:** 3 (R9-T16, R9-T18, R9-T25), deleted from `## Tasks`.

**Pruned task list (22):**

| ID | Location | Finding |
| -- | -------- | ------- |
| R9-T1 | `adversarial-review/SKILL.md:297` | awk `$1` in a fenced block is harness-substituted |
| R9-T2 | `adversarial-review/SKILL.md:116` | PR target reviews the origin head, never local fix commits |
| R9-T3 | `adversarial-loop/SKILL.md:135` | plan dir passed to the review has no slot; bound as path target |
| R9-T4 | `reply-to-claude/SKILL.md:33` | `<pr#>` argument ignored by every snippet |
| R9-T5 | `adversarial-review/SKILL.md:234` | REVIEW.md false-positive entries are suppression (attestation) |
| R9-T6 | `daily-digest/sources.md:227` | PHI ID patterns miss `_`-adjacent, doubled, dot separators |
| R9-T7 | `adversarial-loop/SKILL.md:283` | unguarded `isDraft` capture skips the un-draft |
| R9-T8 | `adversarial-loop/SKILL.md:402` | Phase 5 bot-SHA comparison has no data source (attestation) |
| R9-T9 | `review-ledger.md:21` | ledger gitignored and never staged |
| R9-T10 | `adversarial-loop/SKILL.md:382` | bot rounds bypass the ledger and breaker |
| R9-T11 | `adversarial-loop/SKILL.md:346` | Phase 3 treats a failed gh poll as "nothing arrived" |
| R9-T12 | `adversarial-review/SKILL.md:211` | branch target reads REVIEW.md from the current checkout |
| R9-T13 | `implement_inline/SKILL.md:368` | no attestation-task diversion |
| R9-T14 | `check-guards:52` | misses `grep -cE` / `-ci` / `-cv` |
| R9-T15 | `check-guards:151` | skips double-quoted `$( )` |
| R9-T17 | `check-guards:92` | unclosed text fence hides later bash blocks |
| R9-T19 | `test-guards:593` | mutation ratchet masks regressions via absolute count |
| R9-T20 | `checks.yml:36` | "Pinned" comment on an unpinned install — correct the comment |
| R9-T21 | `.gitignore:14` | two `.pyc` files stay tracked |
| R9-T22 | `README.md:311` | mutation-test figures stale (and a third set in `plugin/scripts/README.md`) |
| R9-T23 | `plugin/scripts/README.md:100` | `check` gate list omits two gates |
| R9-T24 | `adversarial-loop/SKILL.md:417` | self-citations point at wrong lines |

Frontmatter `total_tasks: 25` was left as written. `/wb:update_status` owns the counters.

**Ledger:** `docs/plans/2026-09-17-adversarial_loop/review-log.md`, created by this run. No ledger
existed for rounds 1–8. It is staged with `git add -f`; that step is not in the skill, and its
absence is R9-T9. It holds 25 rows. The first row, verbatim:

```text
| 9 | `plugin/skills/adversarial-review/SKILL.md:297` | positional-token-in-fence | CONFIRMED | Valid | this run received `--plan != ENVIRON[…]`; awk probes exit 0 keeping all lines for a numeric arg; introduced by R7-T1 `4face1f` | prev-fix |
```

**Breaker:**

- **Introduced-rate trend:** 4 of 25 findings are `prev-fix` (16%). With no N−1 row, the trend
  cannot be evaluated.
- **Mirror-image candidate, surfaced not decided:** R7-T1 introduced the `:297` awk `$1` and
  reintroduced the 2.0.1 positional-substitution class. If it counts as a mirror image, the
  breaker is Blocking.
- **Same-file advisory:** it fires for `adversarial-review/SKILL.md` (rounds 7, 8, 9).

**`/verify`:** not asked. No fix was made, so there is nothing for it to exercise yet.

## PR phases

**None engaged.** The Phase 1 gate holds: 21 findings are adjudicated Valid and one more is Real
but disproportionate. So Phases 2–5 were never entered.

- **No confirmation gate was reached.** Nothing was pushed, un-drafted, commented or labelled.
- **No dependency-missing line was printed**, because no PR phase checked its dependencies.
- **No bounded-wait line was printed**, because Phase 3 was not entered.
- **Q4 remains unexercised:** the `claude[bot]`-installed test did not run.

Observed, not tested by the loop:

- `.github/workflows/` holds only `checks.yml`, on this branch and on `origin/main`.
- Two verifiers found zero `claude[bot]` activity across PRs 1–25.
- A future Phase 3 on this repository is therefore likely to hit the missing-dependency stop.
  That is a prediction, not a result.

## Observed during the run

- **The harness substituted `$1` in the received `adversarial-review` body** with `--plan`, the
  second word of the argument string `25 --plan docs/plans/…`. This is the direct evidence for
  R9-T1 and R9-T3. The session used the unsubstituted `$1` by hand and bound `target=25` from the
  loop, not from the body.
- The first `resolve_range` call printed `resolve_range:7: command not found:` and then
  `could not resolve PR 25 via gh — NOT reviewing the current branch`. The cause was a
  transcription artifact after a line-continuation backslash in the session's copy, not gh.
  Re-run on one line, it resolved `origin/main...origin/adversarial-loop-skill-research`.
- The session's first blast-radius attempt printed zero for every symbol. It had used
  `--exclude-dir=docs`, which also excludes `plugin/docs`, and zsh did not split the argument
  pairs. Both were fixed, a negative control was added, and the rerun measured.
- Three lens and verifier agents modified the worktree to probe: a ref checkout, a corpus edit,
  and a `.pyc` touch. Each reported restoring it, and `git status --porcelain` was re-checked
  empty after each.
- The markdown lint hook's `--fix` rewrote a failure scenario in the round plan (a code span with
  inner triple backticks lost a space). The session reworded that line.
