# Session Journal: asd-ste100-prose

Append-only, reverse-chronological — newest entry at the top. **No entries yet.**

**Entries open when work starts, not when it ends.** A session does not get to choose how it
ends: a token limit, a closed laptop, or a crashed harness runs no shutdown step. An entry
written only at completion would be silent in exactly those cases, and worse than silent — its
tail would still show the last *finished* phase, so the next session would read a confident,
stale record and never learn that work stopped mid-task. Opening on entry makes the default
residue of an abrupt kill correct: an open entry naming what was being attempted and what came
next.

An open entry beside uncommitted changes means an interrupted task. An open entry beside a
**clean** tree is ambiguous and the tree cannot resolve it: the session may have finished without
closing out, or be **blocked waiting on a human** — a design awaiting approval is exactly this,
and it is the correct residue rather than a fault — or still be running in another session, which
this repository cannot observe at all.

**So read the entry's `Next action` before concluding anything.** The working tree is the
authority on whether work is *in flight*; only the entry says what the work was and what it is
waiting for.

**A heading must end in a literal `(open)` or `(closed)`.** That suffix is what every reader
matches on — the session-start hook, `forge`, `daily-digest`, `resume_handoff`,
`create_handoff`. A heading ending any other way is invisible to all of them, and the failure
is silent: the next session is told "closed" over work that was interrupted.

Entries take these two shapes. **Keep the dates as the literal placeholder `YYYY-MM-DD`.** The
session-start hook finds the newest entry with `grep -E '^## '` and then discards headings whose
date is still a placeholder — so the placeholder is what stops these examples being read as a
real entry. The fence is for readability and is *not* the protection: the hook is not
fence-aware, and these headings still begin at column zero inside it. An example rewritten with
a realistic-looking date would be reported as an interrupted task in every plan generated from
this template, silently, from the moment of creation.

```text
## YYYY-MM-DD HH:MM — <task-id or short label> (open)

- **Task/phase**: <ID and one-line description>
- **Next action**: <the literal next thing to do, specific enough to act on cold>
- **Started at**: <commit hash>

## YYYY-MM-DD HH:MM — <task-id or short label> (closed)

- **Task/phase**: <ID and one-line description>
- **Landed**: <what actually changed>
- **Commits**: <range or hashes>
- **Learned**: <anything that changes how the remaining work should proceed — omit if nothing>
- **Blocked by**: <anything blocking — omit if nothing>
```

<!-- Real entries begin below this line, newest first. -->

## 2026-09-30 12:37 — P7-T4 (closed)

- **Task/phase**: P7-T4 — the release checks, recorded in `thoughts/2026-09-30-release-checks.md`
- **Landed**: every command exits 0, except `lint --all` (only gitignored `evals/runs/` output, because of the `wb_lint_ignored` follow-up) and `git merge-tree` (5 conflicted paths). Every tracked file lints clean, and the four test scripts, both checkers and `claude plugin validate` pass
- **Commits**: see `P7-T4: record the release checks`

## 2026-09-30 12:37 — P7-T3 (closed)

- **Task/phase**: P7-T3 — the CHANGELOG 2.2.0 entry, and both manifests bumped to 2.2.0
- **Landed**: `## [2.2.0] — 2026-09-30` in the 2.1.1 shape (a prose intro, a results table, Added, Changed, "Not changed, deliberately", Migration). `plugin.json` and `marketplace.json` both say `2.2.0`. `claude plugin validate plugin/` passes
- **Commits**: see `wb 2.2.0: CHANGELOG entry and version bump (P7-T3)`

## 2026-09-30 12:35 — P7-T2 (closed)

- **Task/phase**: P7-T2 — `handoff-2026-09-30-wbte-for-3.0.0.md` for the `adversarial-loop-skill-research` branch
- **Landed**: the handoff lists the new files, the link-line text and its 12 shared locations, the three `wb-prime.sh` hunks, the expected merge conflicts (5 paths, confirmed with `git merge-tree` at `2fff76c`), the post-3.0.0 work (the other 35 shared files, the D8 boilerplate, the agent draft, and 36 non-shared files), and how to run the harness and the gate
- **Commits**: see `P7-T2: add the WBTE handoff for the 3.0.0 branch`

## 2026-09-30 12:34 — P5-T4 (closed)

- **Task/phase**: P5-T4 — the gated lite rewrite of `agents/codebase-analyzer.md` and `agents/codebase-locator.md`, then the token cost of the final tree
- **Landed**: restored. In the gate run `20260930T122037Z` (1 repeat, D10), `design.md` cited `classify.py:81-83` for a rule at `classify.py:29`, and that file has 40 lines. The within-run judge flagged the loss. The agent files stay as they are in 2.1.1, and the draft stays in `.context/lite/`. The always-on cost is ~3,412 tokens (2.1.1: ~3,251), and the per-stage cost is unchanged. The record is `thoughts/2026-09-30-lite-verdicts.md`
- **Commits**: see `P5-T4: restore the agent files (the gate found a loss), and record the token cost`
- **Learned**: with 1 repeat, a loss cannot be told apart from run-to-run variance. The post-3.0.0 pass should gate the agent draft again with 3 repeats

## 2026-09-30 12:22 — P5-T3 (closed)

- **Task/phase**: P5-T3 — the gated lite rewrite of `create_tasks/reference.md`, `create_tasks/examples.md`, `create_tasks/sub-agent-prompts.md`
- **Landed**: kept. The gate run is `20260930T120839Z`, 1 repeat (D10). Every rewritten file was exercised (all three files read by `create_tasks`, 3 agents spawned). The within-run judge found no loss in `design.md` or `tasks.md`. `token_check.py` found only the known missing git keys. The run cited 6 of the 19 facts (the before-run cited 5). Cost $5.61
- **Commits**: see `P5-T3: keep the lite rewrite of create_tasks/reference.md, create_tasks/examples.md, create_tasks/sub-agent-prompts.md`
- **Learned**: the gate ran before this entry was written, in the overnight batch. This entry was opened and closed in one step

## 2026-09-30 12:22 — P5-T2 (closed)

- **Task/phase**: P5-T2 — the gated lite rewrite of `create_design/reference.md`, `create_design/sub-agent-prompts.md`
- **Landed**: kept. The gate run is `20260930T082458Z`, 1 repeat (D10). Every rewritten file was exercised (both files read by `create_design`, 6 agents spawned). The within-run judge found no loss in `design.md` or `tasks.md`. `token_check.py` found only the known missing git keys. The run cited 6 of the 19 facts (the before-run cited 5). Cost $6.37
- **Commits**: see `P5-T2: keep the lite rewrite of create_design/reference.md, create_design/sub-agent-prompts.md`
- **Learned**: the gate ran before this entry was written, in the overnight batch. This entry was opened and closed in one step

## 2026-09-30 12:22 — P5-T1 (closed)

- **Task/phase**: P5-T1 — the gated lite rewrite of `create_research/reference.md`, `create_research/sub-agent-prompts.md`
- **Landed**: kept. The gate run is `20260930T082512Z`, 1 repeat (D10). Every rewritten file was exercised (both files read by `create_research`, 4 agents spawned). The within-run judge found no loss in `design.md` or `tasks.md`. `token_check.py` found only the known missing git keys. The run cited 5 of the 19 facts (the before-run cited 5). Cost $4.52
- **Commits**: see `P5-T1: keep the lite rewrite of create_research/reference.md, create_research/sub-agent-prompts.md`
- **Learned**: the gate ran before this entry was written, in the overnight batch. This entry was opened and closed in one step

## 2026-09-30 08:11 — P7-T1 (closed)

- **Task/phase**: P7-T1 — the README section on WBTE, and the two `CLAUDE.md` lines. This runs ahead of the Phase 5 gates (the user's full-auto instruction), because it does not depend on their results
- **Landed**: the README section "wb Technical English (WBTE)": what WBTE is, the credit line, the card, repository terms, the dictionary skill, and a `Variable | Effect` table for `WB_TECH_ENGLISH=0`. `CLAUDE.md` gains item 8 under Working with Commands and an Eval harness line under Development Tools. Both files lint clean, and `link_check.py` passes. The README section has no sentence over 25 words
- **Commits**: see `P7-T1: document WBTE in README and CLAUDE.md`

## 2026-09-30 08:10 — P6-T2 (closed)

- **Task/phase**: P6-T2 — the `wbte-dictionary` extractor script, the `/wb:wbte-dictionary` skill, and the pointer in `technical-english.md`
- **Landed**: `test-wbte-dictionary` passes 13 of 13. On the user's own PDF, with a temporary HOME outside every repo, it wrote 1,975 entries (652 approved), and 1,114 of the 1,323 unapproved words have alternatives. The development copy was deleted. The always-on cost is ~3,412 tokens, up from ~3,251 (the new skill adds ~130)
- **Commits**: see `P6-T2: add the wbte-dictionary extractor and skill`
- **Learned**: the entry was opened and closed in the same step. The commit that closes P6-T1 marks the start

## 2026-09-30 08:08 — P6-T1 (closed)

- **Task/phase**: P6-T1 — `plugin/scripts/test-wbte-dictionary`, RED. It runs in parallel with P5-T5 (the user's full-auto instruction), because Phase 6 depends only on P2-T1
- **Landed**: 13 checks over the four cases in the task. With no extractor, the 9 positive checks fail with exit 127, and the 4 "nothing written" checks pass trivially
- **Commits**: see `P6-T1: add the wbte-dictionary contract test (RED)`

## 2026-09-30 08:06 — P5-T5 (closed)

- **Task/phase**: P5-T5 — a larger fixture, `evals/fixture-large/`, that makes the stages spawn sub-agents, plus `--fixture` support and the Phase 4 before-run on it
- **Landed**: `evals/fixture-large/` (77 Python files, 4,178 lines, 19 facts) and `--fixture` support. The tracer `20260930T082028Z` spawned all three agent types. The before-run is `20260930T082432Z`, repeat 1 (Phase 4 tree `f2c78e8`, $4.88, within-run judge: no loss). The record is `thoughts/2026-09-30-lite-verdicts.md`
- **Commits**: 82564d8 (WIP), then `P5-T5: record the large fixture and the Phase 5 before-run`
- **Learned**: four parallel runs on the large fixture hit the individual spend limit. Run them one at a time. The user chose 1 repeat per gate (D10)

## 2026-09-30 06:39 — P4-T9 (closed)

- **Task/phase**: P4-T9 — the Objective 1 measurement: 2.1.1 against the P4-T8 tree, 3 repeats, with the design.md targets and the within-run judge
- **Landed**: the final tree (card v3, run `20260930T073357Z`) against 2.1.1 (`20260930T013327Z`). Sentences over 25 words: 7.0% to 2.9%. The within-run judge found no loss in 3 of 3 repeats. Document semicolons: 82 to 9, all in the shared `tasks.md` boilerplate (D8). Chat IDs used alone: 25 to 2 (D9 rule). Fixes: rule 15, the Assumptions line, the D9 ID rule, and card v3
- **Commits**: 91bebc8 (WIP), then `P4-T9: meet the Objective 1 targets on the final tree`
- **Learned**: a rule that lives only in the reference doc applies in about two runs of three. A rule that must always hold belongs on the card. Metrics that come from chat vary a lot between repeats

## 2026-09-30 06:35 — P4-T10 (closed)

- **Task/phase**: P4-T10 — the within-run judge mode (D7), with calibration on the 2.1.1 baseline run
- **Landed**: `judge.py --within` and `--research/--doc/--context`. With prompt v2, the planted copy (F2 and `config.py:4` removed) is flagged in 3 of 3 runs, and the real 2.1.1 baseline run shows no loss in 3 of 3 repeats (6 of 6 judgments). The record is `thoughts/2026-09-30-judge-calibration.md`
- **Commits**: see `P4-T10: add and calibrate the within-run judge mode (D7)`
- **Learned**: prompt v1 ("ignore facts that the approach does not need") missed the planted loss in 0 of 3 runs. The fix is a rule that a mention of a research setting must give its value or its `file:line`

## 2026-09-30 05:28 — P4-T8 (closed)

- **Task/phase**: P4-T8 — WBTE rewrite, with the link line, of the two `forge` templates, the `daily-digest`, `touch-grass`, `implement` and `implement_inline` templates, and the end-of-turn summary in `resolve_questions/SKILL.md`
- **Landed**: `link_check.py` now passes on all 43 templates and all 4 inline output steps (exit 0). The registry passes, lint is clean, and the added lines have no semicolons. `incomplete-worker-message.md` now pairs the task ID with `${task.title}`, following the ID rule
- **Commits**: see `P4-T8: rewrite the forge, digest, touch-grass and implement templates in WBTE`
- **Learned**: `daily-digest/digest-template.md` and `touch-grass/state-template.md` sit directly in the skill directory, so their link path is `../../`, not `../../../`

## 2026-09-30 05:27 — P4-T7 (closed)

- **Task/phase**: P4-T7 — WBTE rewrite, with the link line, of the seven `create_mockup` templates, `create_product_research/templates.md`, and the completion line in `create_product_research/SKILL.md`
- **Landed**: `link_check.py` failed on 9 of 9 before the change and on 0 after it. The registry passes, lint is clean, and the added lines have no semicolons. The semicolon in the fixed completion line became a full stop. `UIQ` IDs, both `Resolved` state strings, the HTML and the ASCII layout did not change
- **Commits**: see `P4-T7: rewrite the create_mockup and create_product_research templates in WBTE`

## 2026-09-30 05:25 — P4-T6 (closed)

- **Task/phase**: P4-T6 — WBTE rewrite, with the link line, of `validate_execution/templates.md`, `validate_project/templates/error-message-formats.md`, `resolve_questions/templates.md`, and `create_tasks/templates/plan-presentation-message.md`
- **Landed**: `link_check.py` failed on 4 of 4 before the change and on 0 after it. The registry passes (including `[To be added]` and the three tracking-table headings), lint is clean, and the added lines have no semicolons. The report status words and the error titles did not change
- **Commits**: see `P4-T6: rewrite the validation, resolve_questions and plan-presentation templates in WBTE`

## 2026-09-30 05:24 — P4-T5 (closed)

- **Task/phase**: P4-T5 — WBTE rewrite, with the link line, of the `create_handoff` templates, `resume_handoff/templates.md`, and the `explore_design` templates
- **Landed**: `link_check.py` failed on 5 of 5 before the change and on 0 after it. The registry passes, lint is clean, and the added prose has 0 semicolons. `## Decision Record`, the `OPEN`/`CLOSED` journal words and `UIQ[n]` did not change
- **Commits**: see `P4-T5: rewrite the handoff and explore_design templates in WBTE`

## 2026-09-30 05:22 — P4-T4 (closed)

- **Task/phase**: P4-T4 — WBTE rewrite, with the link line, of `create_research/templates.md` and the four `create_design` templates
- **Landed**: `link_check.py` failed on 5 of 5 before the change and on 0 after it. The registry passes, lint is clean, and the added prose has 0 semicolons and a longest sentence of 25 words. A `design.md` and a `research.md` filled from the new templates pass `token_check.py`
- **Commits**: see `P4-T4: rewrite the create_research and create_design templates in WBTE`

## 2026-09-30 05:17 — P4-T3 (closed)

- **Task/phase**: P4-T3 — WBTE rewrite, with the link line, of the four `create_project` document templates and the Step 5 output block in `create_project/SKILL.md`
- **Landed**: `link_check.py` failed on the 5 `create_project` locations before the change and passes on all 5 after it. The prose changed and the placeholders did not. The token registry passes. The new prose has 0 semicolons and no sentence over 25 words. A `tasks.md`, `research.md` and `design.md` filled from the new templates pass `token_check.py`
- **Commits**: see `P4-T3: rewrite the create_project templates in WBTE`

## 2026-09-30 05:17 — P4-T2 (closed)

- **Task/phase**: P4-T2 — measure A2: does the model follow the link line? The Phase 3 tree against the P4-T1 tree, 3 repeats
- **Landed**: A2 validated with a limit. The model read `technical-english.md` in 4 of the 6 stage runs whose output has a link line. `tasks.md` sentences over 25 words fell from 7.1% to 5.8%, and document semicolons fell from 16 to 9. The record is `thoughts/2026-09-30-link-measurement.md`
- **Commits**: see `P4-T2: measure the link line (A2 validated, followed in 4 of 6 linked runs)`
- **Learned**: chat IDs used alone rose from 3 to 8, probably run-to-run variance. P4-T9 measures chat again on the final tree

## 2026-09-30 05:16 — P4-T1 (closed)

- **Task/phase**: P4-T1 — add the link line to the 12 locations shared with 3.0.0 (11 templates and the `create_research` Step 8 completion line)
- **Landed**: `link_check.py` failed on 12 of 12 before the change and fails on 0 of 12 after it. Each file gained exactly 2 lines (the link line and a blank line) and lost none. Lint is clean, and the token registry passes
- **Commits**: see `P4-T1: link the 12 shared output locations to technical-english.md`

## 2026-09-30 01:58 — P3-T3 (closed)

- **Task/phase**: P3-T3 — measure A1: does the rule card change chat output? 3 repeats, `4b32306` against the working tree
- **Landed**: A1 validated with card v2. Across 3 repeats, 4.3% of document sentences had more than 25 words (2.1.1: 10.4%). Document semicolons fell from 120 to 16, and chat IDs used alone fell from 17 to 3. No expected fact was lost. The record is `thoughts/2026-09-30-card-measurement.md`
- **Commits**: see `P3-T3: measure the rule card (A1 validated with card v2)`
- **Learned**: card v1 did not move the chat IDs. Putting the ID rule first, with examples, did. Two runs were lost to network outages, and the driver does not retry on `API Error`

## 2026-09-30 01:49 — P3-T2 (closed)

- **Task/phase**: P3-T2 — `card()` and two guarded calls in `plugin/hooks/wb-prime.sh`, a header bullet, and a `CLAUDE.md` line for `test-prime`
- **Landed**: the card (8 imperatives, the ID rule, and the path, 118 words). `test-prime` passes 40 of 40, `test-lint` passes 15 of 15, and `test-quiet` passes 9 of 9. With `WB_TECH_ENGLISH=0`, the output is byte-identical to the 2.1.1 hook for startup, compact and PreCompact
- **Commits**: see `P3-T2: print the WBTE rule card at every session start`
- **Learned**: the orientation path prints one blank line before the card, inside the guard. So the test's `strip_card` also removes that line

## 2026-09-30 01:49 — P3-T1 (closed)

- **Task/phase**: P3-T1 — `plugin/scripts/test-prime`, the contract test for `wb-prime.sh`, RED against the current hook
- **Landed**: 40 cases. Against the current hook, the 15 card cases fail and the 25 others pass
- **Commits**: see `P3-T1: add the wb-prime contract test (RED)`
- **Learned**: macOS `seq 1 0` counts down, so it prints 1 and 0. The first draft's "0 plans" repository had 2 plans. The test uses a C-style loop

## 2026-09-30 01:20 — P2-T8 (closed)

- **Task/phase**: P2-T8 — the 2.1.1 baseline: 3 repeats of `4b32306`, `wbte_check.py` and `token_check.py` on every output, and the token cost from `plugin details`
- **Landed**: the baseline, run `evals/runs/20260930T013327Z`, recorded in `thoughts/2026-09-30-baseline.md`. 7.0% of document sentences have more than 25 words. Documents have 82 semicolons in prose, and chat has 27 IDs used alone. The always-on cost is about 3,251 tokens
- **Commits**: see `P2-T8: record the 2.1.1 baseline`
- **Learned**: the first baseline run failed in repeat 3, because a resumed call could not read the stage's templates. The driver now passes `--add-dir` and skips `create_tasks` after an unwritten design. The rerun wrote 9 of 9 documents

## 2026-09-30 01:14 — P2-T7 (closed)

- **Task/phase**: P2-T7 — `evals/judge.py`, `evals/report.py`, `evals/README.md`, and calibration of the judge on two pairs from the P2-T6 run
- **Landed**: the judge, the report, and the harness README. The judge flagged the altered copy (F6 and one `file:line` removed) in 3 of 3 runs. It found no loss in the real `research.md` pair in 3 of 3 runs. The record is `thoughts/2026-09-30-judge-calibration.md`
- **Commits**: see `P2-T7: add the fidelity judge, the report, and the harness README`
- **Learned**: the judge reports a loss on `design.md` between two runs of the same tree. A human must decide how the Phase 4 and Phase 5 gates use it. See the Implementation Discoveries in tasks.md

## 2026-09-30 00:58 — P2-T6 (closed)

- **Task/phase**: P2-T6 — `evals/run.py`, the before/after driver (two trees, fresh fixture per repeat, three stages, headless approval step)
- **Landed**: the driver. It ran 1 repeat of `4b32306` against itself (`evals/runs/20260930T010202Z`), and all 6 stages wrote their document. Wall time was about 11 min and cost was $3.06. `--after` is optional for a one-tree baseline
- **Commits**: see `P2-T6: add the before/after stage driver`
- **Learned**: `create_design` stops at Step 4 to ask which option to design, because the fixture plan names no goal. One fixed follow-up reply ("take the option you recommend") gets it to write `design.md`. `create_tasks` accepted the driver-set `status: approved` and did not wait for input. The stages skipped their sub-agent fan-out, because the fixture is small. The session was interrupted once (a change of location), and the tree held only the open journal entry.

## 2026-09-30 00:39 — P2-T5 (closed)

- **Task/phase**: P2-T5 — `evals/link_check.py` with planted inputs (template without a link line, a file that restates a rule, a tracked `.pdf`)
- **Landed**: the checker and 4 planted case directories. The 3 bad cases exit 1 and the clean case exits 0. The RED state on the repo is exit 1: 43 of 43 templates and 4 of 4 inline steps have no link line. No file restates a rule, and no PDF or dictionary is tracked
- **Commits**: see `P2-T5: add the link-line and single-authority checker`
- **Learned**: the planted PDF case is simulated with a `.tracked` list, so no `.pdf` is committed. A committed `.pdf` would break the Phase 6 check that `git ls-files` lists none

## 2026-09-30 00:37 — P2-T4 (closed)

- **Task/phase**: P2-T4 — `evals/tokens.json` and `evals/token_check.py`, with planted inputs (task ID with no digit, journal heading with no suffix, checkpoint without the label sentence)
- **Landed**: the registry and the checker. With no arguments, it checks that every exempt token is still in each template listed for it. With file arguments, it runs the parser patterns on generated documents. Before the checker existed, every planted input exited 2. Now the 3 bad inputs exit 1 and the 2 clean ones exit 0. A temporary tree with one token removed made the registry check exit 1
- **Commits**: see `P2-T4: add the exempt-token registry and checker`
- **Learned**: the task-ID check uses the validator's own pattern, `[A-Z0-9-]+`. So a mixed-case bold lead-in such as `**Setup**` is not seen as a task line, which matches how the validator behaves

## 2026-09-30 00:34 — P2-T3 (closed)

- **Task/phase**: P2-T3 — `evals/wbte_check.py` and its planted-failure inputs with clean siblings
- **Landed**: the checker, with 4 bad inputs and 4 clean siblings in `evals/fixtures/planted/`. Before the checker existed, every input exited 2. Now each bad input exits 1 and each clean sibling exits 0. The reference doc passes. Files that end in `.txt` are chat output. The limits apply to all given files together
- **Commits**: see `P2-T3: add the WBTE metric checker`
- **Learned**: the first noun-cluster heuristic flagged verbs and names in real documents. It now treats words that end in -s as breaks, joins runs of capitalized words, and counts multi-word technical nouns from the reference doc as one word. A few false positives remain ("want lower skill quality"), so cluster counts are a trend signal, not a hard gate

## 2026-09-30 00:33 — P2-T2 (closed)

- **Task/phase**: P2-T2 — ignore rules: `.gitignore` gains `evals/runs/`, `__pycache__/`, `*.pyc`; new `.wblintignore` with `evals/fixtures/planted/`
- **Landed**: before the change, `lint --all` flagged a temporary planted file (MD022). After it, lint skipped the file and `lint --all` was clean. `test-lint` passed 15 of 15. The temporary file was removed
- **Commits**: see `P2-T2: ignore harness runs, bytecode, and planted fixtures`

## 2026-09-30 00:32 — P2-T1 (closed)

- **Task/phase**: P2-T1 — write `plugin/docs/reference/technical-english.md` (nine sections, exempt tokens copied from the parsers)
- **Landed**: the WBTE reference doc. Lint is clean, the prose has no semicolons, and no sentence has more than 20 words
- **Commits**: cdee6d5
- **Learned**: lint `--fix` (MD010) turns a literal tab inside a code block into spaces. The dictionary lookup uses `$'\t'` for that reason

## 2026-09-30 00:24 — P1-T3 (closed)

- **Task/phase**: P1-T3 — run the headless driver probe against the 2.1.1 tree (tests assumption A6)
- **Landed**: probe PASS in 59 s, exit 0. `research.md` reached `status: complete`, 4 of 6 facts are cited at the exact `file:line`, and the `✅ research.md updated` line is in stdout. The record is `thoughts/2026-09-30-harness-probe.md`. A6 is still `Pending` (the plan changes it only on failure). Verifier PASS
- **Commits**: see `P1-T3: record the headless driver probe`
- **Learned**: the stage skipped its sub-agent fan-out, as 2.1.1 allows when the whole surface is already read. So the probe does not show that headless runs can spawn sub-agents. The read boundary was off on this machine

## 2026-09-30 00:17 — P1-T2 (closed)

- **Task/phase**: P1-T2 — build `evals/fixture/` (project, QUESTION.md, expected.json, plan-seed)
- **Landed**: `linkcheck` fixture project (4 Python files and a README, 6 facts F1–F6), `QUESTION.md`, `expected.json` (id, fact, ref, contains), `plan-seed/` from the 2.1.1 `create_project` templates. Verifier PASS
- **Commits**: see `P1-T2: build the evals fixture`
- **Learned**: the 2.1.1 `research`, `design` and `tasks` templates fail markdownlint as written (no blank lines around headings and lists). The seeds were lint-fixed. The templates under `plugin/` were not changed (follow-up)

## 2026-09-30 00:16 — P1-T1 (closed)

- **Task/phase**: P1-T1 — promote the plan directory into git
- **Landed**: `git add -f docs/plans/2026-09-29-asd-ste100-prose/` (README, research, design, tasks, journal)
- **Commits**: see `P1-T1: promote the asd-ste100-prose plan`

## 2026-09-30 00:03 — create_tasks (closed)

- **Task/phase**: P0-T4 — execution plan for asd-ste100-prose
- **Landed**: tasks.md — 7 implementation phases, 34 tasks (38 with Phase 0), Phase 1 is a tracer bullet for the headless harness driver (A6)
- **Commits**: none (plan files uncommitted; P1-T1 promotes them)
- **Learned**: Objective 2 in 2.2.0 is limited to files the harness exercises; other non-shared skill files move to the post-3.0.0 pass

## 2026-09-29 23:56 — create_tasks (open)

- **Task/phase**: P0-T4 — execution plan for asd-ste100-prose
- **Next action**: generate the phased plan, then present it at Step 6
- **Started at**: 4b32306

## 2026-09-29 23:55 — create_design (closed)

- **Task/phase**: P0-T3 — design for asd-ste100-prose
- **Landed**: design.md `status: approved` — Option A (reference doc + always-on rule card), name wb Technical English (WBTE), eval harness under `evals/`, A1–A6 pending
- **Commits**: none (plan files uncommitted)

## 2026-09-29 23:33 — create_design (open)

- **Task/phase**: P0-T3 — design for asd-ste100-prose
- **Next action**: awaiting approval at Step 6 — design.md written (Option A, wb Technical English); on approval set `status: approved` and close this entry
- **Started at**: 4b32306

## 2026-09-29 17:45 — create_research (closed)

- **Task/phase**: P0-T2 — research for asd-ste100-prose
- **Landed**: research.md (status: complete) — prose surfaces, existing rules and enforcement, cross-skill rule mechanisms, STE metrics, ASD-STE100 facts and licence, 3.0.0 overlap; Q1–Q5 open
- **Commits**: none (plan files uncommitted)
- **Learned**: local `main` ref is stale at 2a6fa62; compare against `origin/main`. 3.0.0 was once numbered 2.2.0

## 2026-09-29 17:36 — create_research (open)

- **Task/phase**: P0-T2 — research for asd-ste100-prose
- **Next action**: spawn the Step 4 agents, then synthesize into research.md
- **Started at**: 46ef587b084ea4d84a8a9b4e5b0770778903ba9b
