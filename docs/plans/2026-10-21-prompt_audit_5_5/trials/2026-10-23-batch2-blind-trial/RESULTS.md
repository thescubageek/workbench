# Batch 2 blind trial — the implementation stages

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../../../plugin/docs/reference/technical-english.md) and apply it.

**Status**: fixtures and trap cells named before the run (2026-10-23). Results follow below.

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
