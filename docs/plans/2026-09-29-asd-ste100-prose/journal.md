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

## 2026-09-30 01:58 — P3-T3 (closed)

- **Task/phase**: P3-T3 — measure A1: does the rule card change chat output? 3 repeats, `4b32306` against the working tree
- **Landed**: A1 validated with card v2. Across 3 repeats, 4.3% of document sentences had more than 25 words (2.1.1: 10.4%). Document semicolons fell from 120 to 16, and chat IDs used alone fell from 17 to 3. No expected fact was lost. The record is `thoughts/2026-09-30-card-measurement.md`
- **Commits**: see `P3-T3: measure the rule card (A1 validated with card v2)`
- **Learned**: card v1 did not move the chat IDs. Putting the ID rule first, with examples, did. Two runs were lost to network outages, and the driver does not retry on `API Error`
## 2026-09-30 01:55 — P3-T2 (closed)

- **Task/phase**: P3-T2 — `card()` and two guarded calls in `plugin/hooks/wb-prime.sh`, a header bullet, and a `CLAUDE.md` line for `test-prime`
- **Landed**: the card (8 imperatives, the ID rule, and the path, 118 words). `test-prime` passes 40 of 40, `test-lint` passes 15 of 15, and `test-quiet` passes 9 of 9. With `WB_TECH_ENGLISH=0`, the output is byte-identical to the 2.1.1 hook for startup, compact and PreCompact
- **Commits**: see `P3-T2: print the WBTE rule card at every session start`
- **Learned**: the orientation path prints one blank line before the card, inside the guard. So the test's `strip_card` also removes that line

## 2026-09-30 01:53 — P3-T1 (closed)

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

## 2026-09-30 00:53 — P2-T5 (closed)

- **Task/phase**: P2-T5 — `evals/link_check.py` with planted inputs (template without a link line, a file that restates a rule, a tracked `.pdf`)
- **Landed**: the checker and 4 planted case directories. The 3 bad cases exit 1 and the clean case exits 0. The RED state on the repo is exit 1: 43 of 43 templates and 4 of 4 inline steps have no link line. No file restates a rule, and no PDF or dictionary is tracked
- **Commits**: see `P2-T5: add the link-line and single-authority checker`
- **Learned**: the planted PDF case is simulated with a `.tracked` list, so no `.pdf` is committed. A committed `.pdf` would break the Phase 6 check that `git ls-files` lists none

## 2026-09-30 00:47 — P2-T4 (closed)

- **Task/phase**: P2-T4 — `evals/tokens.json` and `evals/token_check.py`, with planted inputs (task ID with no digit, journal heading with no suffix, checkpoint without the label sentence)
- **Landed**: the registry and the checker. With no arguments, it checks that every exempt token is still in each template listed for it. With file arguments, it runs the parser patterns on generated documents. Before the checker existed, every planted input exited 2. Now the 3 bad inputs exit 1 and the 2 clean ones exit 0. A temporary tree with one token removed made the registry check exit 1
- **Commits**: see `P2-T4: add the exempt-token registry and checker`
- **Learned**: the task-ID check uses the validator's own pattern, `[A-Z0-9-]+`. So a mixed-case bold lead-in such as `**Setup**` is not seen as a task line, which matches how the validator behaves

## 2026-09-30 00:39 — P2-T3 (closed)

- **Task/phase**: P2-T3 — `evals/wbte_check.py` and its planted-failure inputs with clean siblings
- **Landed**: the checker, with 4 bad inputs and 4 clean siblings in `evals/fixtures/planted/`. Before the checker existed, every input exited 2. Now each bad input exits 1 and each clean sibling exits 0. The reference doc passes. Files that end in `.txt` are chat output. The limits apply to all given files together
- **Commits**: see `P2-T3: add the WBTE metric checker`
- **Learned**: the first noun-cluster heuristic flagged verbs and names in real documents. It now treats words that end in -s as breaks, joins runs of capitalized words, and counts multi-word technical nouns from the reference doc as one word. A few false positives remain ("want lower skill quality"), so cluster counts are a trend signal, not a hard gate

## 2026-09-30 00:36 — P2-T2 (closed)

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
