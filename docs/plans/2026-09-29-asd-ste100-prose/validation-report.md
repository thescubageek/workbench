# Validation Report: asd-ste100-prose (wb 2.2.0, WBTE)

Generated: 2026-09-30 15:57 UTC
Validated tree: `c13f02b` on `wb-2.2.0/asd_ste100_prose`, against the 2.1.1 baseline `4b32306`

## Executive Summary

**Overall Status**: ⚠️ PASSED WITH ISSUES

- Planned Phases: 8 (Phase 0 to Phase 7)
- Completed Phases: 8. Every task checkbox is `[x]`, and the evidence supports each one
- Task Completion: 40/40 tasks (100%). The frontmatter counters (`total_tasks: 40`, `completed_tasks: 40`) match the checkbox counts
- Automated Tests: PASS, with one known exception. `./plugin/scripts/lint --all` exits 1 on 4 gitignored run outputs. Every tracked file is clean
- Manual Testing Required: YES. The attestations of Phases 2, 4, 5, 6 and 7 are open, and `status: complete` waits for a person

No task is a false completion, and no `[ ]` task has finished work. No checkbox changed in this validation.

## Phase-by-Phase Validation

### Phase 0: Planning

**Status**: ✅ Fully Implemented

- ✅ P0-T1 to P0-T4 (project structure, research, design, tasks) - `research.md` has `status: complete`, `design.md` has `status: approved`, and `tasks.md` exists. These tasks produce plan documents and have no commits of their own. P1-T1 (`ddf975a`) promoted the directory

### Phase 1: Tracer bullet — prove the harness driver

**Status**: ✅ Fully Implemented

#### Completed Tasks

- ✅ P1-T1 (promote the plan) - `ddf975a`. `git ls-files docs/plans/2026-09-29-asd-ste100-prose/` lists `tasks.md` and every other plan file. No plan file is untracked
- ✅ P1-T2 (the fixture) - `b0d0f80`. `evals/fixture/{project,QUESTION.md,expected.json,plan-seed}` exist
- ✅ P1-T3 (the driver probe) - `33cb729`. `thoughts/2026-09-30-harness-probe.md` records PASS with its cwd, command, model and duration

#### Success Criteria Results

**Automated Verification**: all three ticked, and the tracked-markdown lint is clean today.

### Phase 2: Rules authority, harness, and baseline

**Status**: ✅ Fully Implemented

#### Completed Tasks

- ✅ P2-T1 (the reference doc) - `cdee6d5`. `plugin/docs/reference/technical-english.md` opens in the `branch-naming.md` shape (`:3-4`)
- ✅ P2-T2 (ignore rules) - `f231094`. `.gitignore:13` has `evals/runs/`. `.wblintignore` has `evals/fixtures/planted/` only
- ✅ P2-T3 (the metric checker) - `16bf35f`. Its 5 bad planted inputs exit 1, and its 5 clean siblings exit 0
- ✅ P2-T4 (the token registry) - `e2f4b0d`. Its 3 bad inputs exit 1, and its 2 clean inputs exit 0
- ✅ P2-T5 (the link checker) - `98a4f6c`. Its 3 bad case directories exit 1, and `links/clean` exits 0
- ✅ P2-T6, P2-T7, P2-T8 (driver, judge, report, baseline) - `2c19da5`, `c78418c`, `8db0854`. `thoughts/2026-09-30-{judge-calibration,baseline}.md` exist

#### Success Criteria Results

**Automated Verification**:

- ✅ Planted-failure checks: every bad input fires, and every clean sibling passes (the test-coverage agent ran them all)
- ✅ `lint plugin/docs/reference/technical-english.md` is clean
- ⚠️ `grep -ril 'ASD-STE100' plugin/` now lists 3 files, not 1. Phase 6 added `plugin/scripts/wbte-dictionary:3,5,22,88` and `plugin/skills/wbte-dictionary/SKILL.md:3,4,23,24`. These are names, usage text and the free-download link. None is ASD rules text. The criterion was true when it was ticked and is now stale

**Manual Verification Required**:

- [ ] A human reads one judge verdict and one baseline report and confirms they make sense

### Phase 3: Rule card

**Status**: ✅ Fully Implemented

#### Completed Tasks

- ✅ P3-T1 (the contract test, RED) - `f6b7c9e`. `plugin/scripts/test-prime` has 40 cases, and all 40 pass
- ✅ P3-T2 (the card) - `a733187`. `card()` is at `plugin/hooks/wb-prime.sh:57-73`, with guarded calls at `:113` (recovery, before the zero-plan exit) and `:132` (after the `PRIME.md` if/else). `CLAUDE.md` has the `test-prime` line
- ✅ P3-T3 (measure A1) - `77134aa`. `thoughts/2026-09-30-card-measurement.md` exists, and `design.md:513` has A1 `Validated 2026-09-30`

#### Success Criteria Results

**Automated Verification**:

- ✅ `test-prime`: 40 passed, 0 failed. The card has 141 words, below the 150-word limit
- ✅ `test-lint`: 15 passed. `test-quiet`: 9 passed
- ✅ `bash -n plugin/hooks/wb-prime.sh` succeeds

The regression agent ran the hook directly and confirmed the contract:

- With `WB_TECH_ENGLISH=0`, the output is byte-identical to 2.1.1 in all 8 payload combinations.
- `--export` is identical to 2.1.1.
- Every run exits 0.
- 200 plan directories take about 2.5 s, the same as 2.1.1.

Both attestations are ticked.

### Phase 4: Objective 1 — link lines and template rewrites

**Status**: ✅ Fully Implemented (one target has a small remainder, shown below)

#### Completed Tasks

- ✅ P4-T1 (12 shared link lines) - `442e862`. For each of the 12 shared files, `git diff 4b32306..HEAD` shows only the link line and a blank line
- ✅ P4-T2 (measure A2) - `8bc40a6`. `design.md:514` has A2 `Validated 2026-09-30`
- ✅ P4-T3 to P4-T8 (WBTE rewrites) - `bb909bc`, `647ad1c`, `64a4408`, `f9fb225`, `fc112ea`, `eaf199b`. 48 relative links to `technical-english.md` resolve. `link_check.py` passes on 43 templates and 4 inline steps
- ✅ P4-T10 (within-run judge) - `8518bf1`
- ✅ P4-T9 (the Objective 1 report) - `312d135`. `thoughts/2026-09-30-objective-1-report.md` records the final run `20260930T073357Z`

In all 56 modified plugin markdown files, each exempt token and each `BARRIER`/`NOW` directive occurs as often as at `4b32306`. That covers every entry in `evals/tokens.json` plus the checkpoint, journal and report literals. No skill frontmatter changed.

#### Success Criteria Results

**Automated Verification**:

- ✅ `python3 evals/link_check.py`: PASS
- ✅ `python3 evals/token_check.py`: PASS on the registry. On generated documents, only the known missing `git_commit`/`git_branch` keys remain (4 in the final run)
- ⚠️ `wbte_check.py` thresholds:
  - Met: 2.9% of sentences over 25 words (2.1.1: 7.0%), and no lost facts in 3 of 3 repeats.
  - Accepted under D8: 9 semicolons, all from the shared `tasks.md` boilerplate.
  - Open: 2 chat IDs used alone, in one sentence. This waits for the user
- ⚠️ `lint --all` exits 1 (see Issues). The tracked-file lint is clean

**Manual Verification Required**:

- [ ] A human reads one generated `research.md`, `design.md`, `tasks.md` and chat summary from P4-T9, and confirms they are easier to follow than the baseline samples
- [ ] A human confirms that the judge verdicts in the report match a spot check

### Phase 5: Objective 2 — gated "lite" rewrite

**Status**: ✅ Fully Implemented

#### Completed Tasks

- ✅ P5-T5 (large fixture) - `82564d8` (WIP), `3ecd226`. `evals/fixture-large/` has 77 Python files and 19 expected facts. The tracer run `20260930T082028Z` spawned `codebase-locator`, `codebase-analyzer` and `pattern-finder`
- ✅ P5-T1, P5-T2, P5-T3 (kept) - `e51bb10`, `1668bd8`, `445938e`. `thoughts/2026-09-30-lite-verdicts.md` shows no loss in 1 of 1 repeats (D10). In each rewritten file, `⛔` and `NOW` occur as often as at `4b32306`
- ✅ P5-T4 (restored) - `f01180a`. `git diff 4b32306..HEAD -- plugin/agents/` is empty. The token cost is in the verdicts record

#### Success Criteria Results

**Automated Verification**:

- ✅ Each kept rewrite has a "no loss" verdict. The verdict is 1 of 1 repeats, not 3 of 3 (D10)
- ✅ `token_check.py` and `link_check.py` pass
- ⚠️ `lint --all` exits 1 (see Issues)

**Manual Verification Required**:

- [ ] A human reads the verdict table and one kept rewrite, and confirms that the rewrite did not remove meaning

### Phase 6: Dictionary skill

**Status**: ✅ Fully Implemented

#### Completed Tasks

- ✅ P6-T1 (the contract test, RED) - `cd389c7`. `plugin/scripts/test-wbte-dictionary` has 13 checks, and all 13 pass
- ✅ P6-T2 (the extractor and the skill) - `68ac4c3`:
  - `plugin/scripts/wbte-dictionary` writes only to `${HOME}/.claude/wb/wbte-dictionary.tsv` (`:26-27`).
  - It exits 2 when no tool is present, and 3 inside a git work tree (`:16`).
  - `plugin/skills/wbte-dictionary/SKILL.md` has valid frontmatter.

#### Success Criteria Results

**Automated Verification**:

- ✅ `test-wbte-dictionary`: 13 passed, 0 failed
- ✅ `git ls-files | grep -iE '\.pdf$|wbte-dictionary\.tsv'` prints nothing

**Manual Verification Required**:

- [ ] A4: a human runs `/wb:wbte-dictionary <path-to-real-Issue-9.pdf>` in a fresh session and confirms that the entries are usable
- [ ] The skill works from a fresh session, and the plugin still works with no copy present

### Phase 7: Documentation, handoff, and release checks

**Status**: ✅ Fully Implemented

#### Completed Tasks

- ✅ P7-T1 (README and CLAUDE.md) - `097a6f1`. `README.md:266-275` has the WBTE section and the `WB_TECH_ENGLISH` row
- ✅ P7-T2 (the 3.0.0 handoff) - `b80e5a9`. The handoff is tracked. It has these sections: new files, the link line, the `wb-prime.sh` change, expected merge conflicts (including the `knowledge.md` note at `:106`), the post-3.0.0 pass, and running the harness
- ✅ P7-T3 (CHANGELOG and version) - `08c285c`. Both manifests read `2.2.0`, and `claude plugin validate plugin/` passes
- ✅ P7-T4, P7-T5 (release checks and conflicts) - `767016a`, `d0f8441`. `thoughts/2026-09-30-release-checks.md` lists 5 conflicted paths. Each path has an action or a handoff note

#### Success Criteria Results

**Automated Verification**:

- ⚠️ Every P7-T4 command exits 0 except `lint --all` (exit 1, gitignored output) and `git merge-tree` (5 conflicts, as expected)
- ✅ The version is `2.2.0` in both manifests
- ✅ The handoff is tracked

**Manual Verification Required**:

- [ ] A human reads the README section, the CHANGELOG entry and the handoff, and confirms that they describe the release
- [ ] A smoke session with `claude --plugin-dir <repo>/plugin` shows the card, and one stage writes WBTE output

## Code Quality Analysis

### Pattern Compliance

- ✅ `technical-english.md` follows the single-authority shape of `branch-naming.md` (`:3-4`). The rule phrases appear only there and in the card (`wb-prime.sh:67-68`), which is the named exception
- ✅ The link line has the same wording in every template and inline step. Its path depth is correct in each file. `wbte-dictionary/SKILL.md:8` has a deliberate, shorter variant
- ✅ The `WB_TECH_ENGLISH` guard (`wb-prime.sh:113,132`) uses the `:-1` / `= "0"` form of `lint-hook:11`
- ✅ `test-prime` and `test-wbte-dictionary` follow `test-lint`: a `check` helper, `mktemp -d` with `trap … EXIT`, a summary line, and the exit code from the fail count
- ✅ `evals/*.py` import only the standard library. Exit codes are 0 pass, 1 fail and 2 usage in every checker
- ✅ `wbte-dictionary` quotes its variables, stages its output in a trapped temporary directory, and moves it into place (`:37-38,93-94`)
- ⚠️ `plugin/scripts/README.md` does not document `wbte-dictionary`, `test-prime` or `test-wbte-dictionary`. `help/SKILL.md` does not mention the new skill

### Test Coverage

- Contract tests: 40 cases for the hook, and 13 for the dictionary extractor. Every case that the plan requires has a test
- Harness checkers: 11 planted-failure inputs, each with a clean control
- Missing tests (all minor):
  - `test-prime` does not assert exit 0 on the `--export`, `PRIME.md`, resume and `WB_TECH_ENGLISH` runs.
  - The refusal check at `test-wbte-dictionary:94` asserts a non-zero exit, not exit 3.
  - The no-argument usage path, the "no entries found" path (`wbte-dictionary:87-90`) and the pypdf branch have no test.

## Deviations from Plan

### Justified Deviations

1. **Two tasks added during the plan**: P4-T10 (the within-run judge, D7) and P5-T5 (the large fixture, D6)
   - Plan specified: 38 tasks
   - Actual implementation: 40 tasks. Commits `654b441` and `72af3b1` record the replans
   - Justification: the user asked for both. Without them, the "no loss" gate had no valid signal
2. **Phase 5 gates used 1 repeat, not 3** (D10)
   - Plan specified: no loss in 3 of 3 repeats
   - Actual implementation: 1 of 1, after the spend limit was reached
   - Justification: the user chose it, and the verdict table states the limit
3. **The agent rewrite was restored** (P5-T4)
   - Justification: the gate found a loss, and the gate rule is to restore. The draft is kept for the post-3.0.0 pass
4. **Merge conflicts outside design.md's list**: `.gitignore` and `.claude/wb/knowledge.md`
   - Plan specified (`design.md:487-488`): conflicts only in link lines, `wb-prime.sh`, the manifests, `README.md` and `CHANGELOG.md`
   - Actual implementation: 5 conflicts. P7-T5 expected `.gitignore`. `knowledge.md` has a resolution note (keep both entries) at handoff `:106`
   - Justification: both are append-only conflicts, and the handoff tells the 3.0.0 branch how to resolve them
5. **Semicolons in the shared `tasks.md` boilerplate** (D8): accepted for 2.2.0, and named in the handoff

### Unjustified Deviations

None found.

## Issues and Risks

### Critical Issues (Must Fix)

None.

### Non-Critical Issues (Should Fix)

- 🟡 **`lint --all` fails, and the plan explains the cause incorrectly.**
  - `lint --all` exits 1 on 4 untracked files, `evals/runs/*/before/*/plan/tasks.md`, with MD024 duplicate headings.
  - `tasks.md:1327-1332` says that the path is in both `.gitignore` and `.wblintignore`. It is not. `.wblintignore` lists only `evals/fixtures/planted/`.
  - The failure has this cause: `wb_lint_ignored` does not honour `.gitignore`, by design.
  - Adding `evals/runs/` to `.wblintignore` alone would still not work. `git check-ignore -v` reports `.gitignore:13` first, so the ownership check rejects the match. The regression agent reproduced this.
  - The fix is in `plugin/scripts/lint-common.sh`. It is unchanged since `4b32306`, so the bug predates 2.2.0.
  - This keeps the automated boxes of Phases 4, 5 and 7 at `[ ]`.
- 🟡 **The dictionary extractor's git-repo refusal has a gap.**
  - The script probes `$HOME` when `~/.claude/wb` does not exist yet (`plugin/scripts/wbte-dictionary:29-30`).
  - If `~/.claude` is a git repository (a common dotfiles setup), the probe does not see it. The script then writes the dictionary copy into that repository.
  - design.md depends on this guard: "a user-level path means the copy is never committed to any repo by accident".
  - The fix is to probe the nearest existing ancestor of `$out_dir`, and to add a test for that case.
- 🟡 **Some plan records are out of date:**
  - `design.md:518` keeps A6 `Pending`. `thoughts/2026-09-30-lite-verdicts.md` now shows headless stages spawning their agents on the large fixture, which is the condition that D6 set.
  - D6 (`design.md:376-377`) and D7 (`design.md:390-391`) still say that their work "is not a task". P5-T5 and P4-T10 now exist.
  - The Phase 2 ASD-STE100 criterion (`tasks.md:432`) no longer matches the tree (see Phase 2).
  - The design.md Success Criteria checkboxes (`:461-490`) are all `[ ]`.
- 🟡 **2 chat IDs are used alone** in one `create_tasks` summary sentence, in the final P4-T9 run. This waits for the user's decision.
- 🟡 **One semicolon remains in a rewritten, non-shared template**: `create_design/templates/design-md-template.md:125`, in a placeholder cell ("What needs to be decided; options and trade-offs in one line").

### Potential Risks

- ⚠️ **The Objective 2 verdicts rest on 1 repeat each.** Run-to-run variance is large (chat IDs used alone ranged from 1 to 7 on the same rules). A "no loss" in 1 of 1 is weaker evidence than the design asked for
- ⚠️ **The card prints twice after `/compact`** (the A3 follow-up). This doubles the post-compaction cost, to about 380 tokens
- ⚠️ **Many `file:line` citations are hard-coded in `technical-english.md:108-177`**, and no check keeps them current. They will drift when 3.0.0 changes the cited files

## Recommendations

### Immediate Actions Required

1. Close the git-repo probe gap in `plugin/scripts/wbte-dictionary:29-30`, with a test, before the release ships. It is small, and it protects the licence guarantee
2. Correct the `wb_lint_ignored` note at `tasks.md:1327-1332`. Then fix `lint-common.sh` so that `.wblintignore` wins over an earlier `.gitignore` match, or file it as a follow-up issue

### Before Deployment

1. Do the open manual checks of Phases 2, 4, 5, 6 and 7 (the checklist below)
2. Decide on the 2 remaining chat IDs (Phase 4)
3. Set A6 in `design.md`, correct the D6 and D7 wording and the Phase 2 criterion, and tick the design.md Success Criteria that are met
4. Set `status: complete` through `/wb:update_status`, after sign-off

### Future Improvements (Not Blocking)

1. Document the three new scripts in `plugin/scripts/README.md`, and add `wbte-dictionary` to `help/SKILL.md`
2. Add the missing test assertions listed under Test Coverage
3. Gate the Objective 2 rewrites again with 3 repeats in the post-3.0.0 pass
4. Find out why the card prints twice after compaction

## Manual Testing Checklist

### Phase 2

- [ ] Read one judge verdict and `thoughts/2026-09-30-baseline.md`, and confirm they make sense

### Phase 4

- [ ] Read one generated `research.md`, `design.md`, `tasks.md` and chat summary from run `20260930T073357Z`, and compare them with the `20260930T013327Z` baseline
- [ ] Spot-check the judge verdicts in `thoughts/2026-09-30-objective-1-report.md`

### Phase 5

- [ ] Read the verdict table and one kept rewrite (for example `plugin/skills/create_tasks/reference.md` against `4b32306`), and confirm that no meaning was removed

### Phase 6

- [ ] In a fresh session, run `/wb:wbte-dictionary <path-to-Issue-9.pdf>` and confirm that the entries are usable
- [ ] Confirm that the plugin works with no dictionary copy present

### Phase 7

- [ ] Read the README section, the CHANGELOG 2.2.0 entry and the handoff
- [ ] Start `claude --plugin-dir <repo>/plugin`, confirm that the card shows, and run one stage to see WBTE output

## Appendix: Validation Evidence

### Git Changes Summary

```bash
Commits:       58 (4b32306..c13f02b)
Files changed: 220 (61 under plugin/)
Insertions:    +12253 lines (+1214 under plugin/)
Deletions:     -451 lines (-450 under plugin/)
```

Every task from P1-T1 to P7-T5 has a commit with its task ID in the subject.

### Test Execution Logs

```text
test-prime: 40 passed, 0 failed
test-lint: 15 passed, 0 failed
test-quiet: 9 passed, 0 failed
test-wbte-dictionary: 13 passed, 0 failed
link_check.py: PASS (43 templates, 4 inline steps)
token_check.py: PASS
lint $(git ls-files '*.md'): All markdown files are clean
lint --all: exit 1 — 4 files under evals/runs/ (untracked), MD024
claude plugin validate plugin/: Validation passed
bash -n on wb-prime.sh, test-prime, test-wbte-dictionary, wbte-dictionary: OK
shellcheck: info-level notes only. Those in wb-prime.sh predate 2.2.0
```

### Agent Findings

- **Code changes**: this agent stopped at its turn limit, because it has no git access. The validator ran the same checks directly:
  - The name-status diff under `plugin/` matches the plan's file list, with no unexpected files.
  - The 12 shared files changed by the link line only.
  - `plugin/agents/` is unchanged.
  - No exempt token or `BARRIER`/`NOW` directive was lost.
- **Test coverage**: every required case has a test, and every test passes. The gaps are listed under Test Coverage.
- **Regressions**: none found.
  - The hook is byte-identical to 2.1.1 with `WB_TECH_ENGLISH=0`.
  - Parser tokens, frontmatter and links are intact.
  - The agent corrected the `.wblintignore` premise.
- **Patterns**: the new code follows the repository conventions. The agent found the refusal-probe gap and the documentation gaps listed above.

---

## Validation Completed

**Next Steps**:

1. Fix the extractor probe gap, and correct or fix the lint-ignore note
2. Perform the manual checks above
3. Update the stale design.md records, then close the plan with `/wb:update_status`
4. Push and open the PR, after your go-ahead

**Validator Notes**: the implementation is complete and matches the plan. The records are careful and honest about what was not attested. All open items are small, or are human sign-offs that the full-auto run could not give.
