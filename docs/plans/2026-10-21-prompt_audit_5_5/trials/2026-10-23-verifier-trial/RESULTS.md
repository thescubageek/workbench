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
