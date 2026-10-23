# Batch 2 blind trial — the implementation stages

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../../../plugin/docs/reference/technical-english.md) and apply it.

**Run**: 2026-10-23, Claude Code 2.1.306, cwd `/tmp/q2/cwd` (an empty git repository).
**Result**: PASS. `trim` ≥ `base` in every cell, and every trap cell reached 10 of 10 for `trim`.
**Cost**: $1.13 for 200 runs, the 1-run pilot included (sum of `total_cost_usd`).

The fixtures and trap cells below were named before the run.

## Method

The method is the one of the Q2 trial (`../2026-10-22-q2-blind-trial/RESULTS.md`): headless
`claude -p` with no tools, `--effort medium`, Opus 5.5 and Sonnet 5.5, 10 repeats for each cell.
`harness/run.py` has the exact command.

- The `base` arm is the text at commit `84c5477` (before Phase 3). The `trim` arm is the text after
  P3-T1 to P3-T5. Both are copied to `excerpts/`.
- `harness/texts.py` cuts each excerpt and renders the worker prompt with fixed values.
- `harness/score.py` scores every run automatically.

## Fixtures and trap cells

| Set | Fixture | Text under test | A pass is | Trap cell |
| --- | ------- | --------------- | --------- | --------- |
| C | positive | `implement/SKILL.md` Step 1, all four reads full | `DECISION: PROCEED` | no (control) |
| C | partial | the same, with `design.md` returned as a partial view | `DECISION: PAGE` | yes |
| D | extra_tests | `implement/prompts/worker-prompt.md`, a task with two behaviors | every `TEST:` line covers only lowercase or space-to-hyphen | yes |
| E | no_run | the worker prompt, with `pytest` not available | `CHECKBOX: UNFLIPPED` and `TESTS: NOT RUN` | yes |
| F | parallel | `implement/reference.md` DO and DON'T lists, three independent tasks | `DECISION: SEQUENTIAL` | yes |

The pass bar (design.md): `trim` ≥ `base` in every cell, and every trap cell at least 9 of 10 for
`trim`.

## Results

Pass counts out of 10 for each cell (`score-output.txt`).

| Set | Fixture | Opus 5.5 base | Opus 5.5 trim | Sonnet 5.5 base | Sonnet 5.5 trim |
| --- | ------- | ------------- | ------------- | --------------- | --------------- |
| C | positive | 10 | 10 | 10 | 10 |
| C | partial (trap) | 10 | 10 | 10 | 10 |
| D | extra_tests (trap) | 9 | 10 | 10 | 10 |
| E | no_run (trap) | 10 | 10 | 10 | 10 |
| F | parallel (trap) | 10 | 10 | 10 | 10 |

- **C partial**: every run in both arms chose to page through `design.md`. The `base` text says
  "no `limit` or `offset`", but no run read that as a reason to proceed on the partial view.
- **D extra_tests**: the one failure is a `base` run that added a third test for two consecutive
  spaces. The task says "replace each space", so that test is arguably inside the scope. The
  scorer counts it as an extra either way.
- **E no_run**: every run left the checkbox unflipped and reported the tests as not run.
- **F parallel**: every run spawned the three independent tasks one at a time.

## Verdict

The Batch 2 wording passes its gate. No edit is reverted.

## Limits

These are the same as the Q2 trial: short excerpts, a small system prompt, no tools, and `medium`
effort only. Both arms reached the ceiling in 19 of 20 cells, so the trial shows no loss but cannot
rank the wordings.
