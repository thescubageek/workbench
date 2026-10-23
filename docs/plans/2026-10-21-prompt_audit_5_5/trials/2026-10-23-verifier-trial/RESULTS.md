# Verifier trial — Sonnet 5.5 against Opus 5.5 for task-verifier

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../../../plugin/docs/reference/technical-english.md) and apply it.

**Question** (design.md, Resolved Decisions): should `task-verifier` and `research-validator` move
from Sonnet 5.5 to Opus 5.5? They move only if Opus finds more planted defects with no more false
failures.

## Method

- `harness/fixtures.py` builds one scratch git repository for each run under `/tmp/vtrial/`. Each
  repository is a small Python project (`calc.py`, `tests/test_calc.py`) with a seed commit, a plan
  file `docs/plans/demo/tasks.md`, and the worker's change left uncommitted. The task is P1-T2: add
  `subtract(a, b)` with a unit test. The test command is `python3 -m unittest discover -s tests -v`,
  because `pytest` is not installed on this machine.
- `harness/run.py` runs the verifier directly as the session agent:
  `claude -p --plugin-dir <repo>/plugin --agent wb:task-verifier --model <sonnet|opus> --effort high`
  with `Bash,Read,Grep,Glob` allowed, under no `CLAUDE_CODE_PLUGIN_DIRS`. The prompt carries the
  fields of `implement/prompts/verifier-prompt.md`. The worker summary always claims success.
- `harness/score.py` reads the one `### Status: PASS` or `### Status: FAIL` heading. A run with no
  status line or with two counts as wrong.

## Cells

| Cell | The worker's change | Expected |
| ---- | ------------------- | -------- |
| clean | `subtract` and its test, checkbox flipped | PASS |
| baseline_fail | the clean change, and a test that already failed in the seed commit | PASS, with `### Baseline failures` |
| broken_test | `subtract` returns `a + b`, so its test fails | FAIL |
| scope_creep | the clean change, plus an unrequested `multiply` | FAIL |
| clean_tree | no change at all | FAIL |
| unchecked | the clean change, with the checkbox left `[ ]` | FAIL |
| tautological | the test asserts `subtract(5, 3) == subtract(5, 3)` | FAIL |
| no_test | `subtract` with no test | FAIL |

## Pilot (1 run for each cell and model)

Cost $0.73 (Sonnet $0.23, Opus $0.50, with the 2 cost-measurement runs). Both models were right in
all 8 cells: 6 of 6 defects found and 0 of 2 false failures on the controls.

## Results (3 runs for each cell and model)

Total cost $1.98, the pilot included (Sonnet $0.62, Opus $1.36). `score-output.txt` has the counts.

| Cell | Sonnet 5.5 right | Opus 5.5 right |
| ---- | ---------------- | -------------- |
| clean | 3 of 3 | 3 of 3 |
| baseline_fail | 3 of 3 | 3 of 3 |
| broken_test | 3 of 3 | 3 of 3 |
| scope_creep | 3 of 3 | 3 of 3 |
| clean_tree | 3 of 3 | 3 of 3 |
| unchecked | 3 of 3 | 3 of 3 |
| tautological | 3 of 3 | 3 of 3 |
| no_test | 3 of 3 | 3 of 3 |

- Defects found: Sonnet 18 of 18, Opus 18 of 18.
- False FAIL or missing status on the controls: Sonnet 0 of 6, Opus 0 of 6.
- Every `baseline_fail` report, on both models, had a `### Baseline failures` section that named
  `test_halve`.
- An Opus run cost about twice a Sonnet run ($0.11 against $0.06 for the clean cell).

## Verdict

Opus 5.5 found no more defects than Sonnet 5.5 and had no fewer false failures. By the design's
rule, `task-verifier` and `research-validator` stay on Sonnet 5.5 at `high`.

## Limits

- The defects are planted and plain. A subtle defect could separate the models where these did not.
- The runner makes the verifier the session agent with `--agent`. It does not go through a spawn,
  so it does not test a spawn `model` override.
- `research-validator` was not run. The design ties its tier to this trial.
