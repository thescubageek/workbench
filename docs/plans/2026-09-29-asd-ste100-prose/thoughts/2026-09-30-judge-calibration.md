# Judge calibration (P2-T7)

This record calibrates `evals/judge.py` on two pairs from the P2-T6 run,
`evals/runs/20260930T010202Z`. In that run, both trees are `4b32306` (2.1.1), with 1 repeat and
the model `sonnet`.

**Result: the judge finds a planted loss in 3 of 3 runs. It also reports a loss between two
runs of the same tree for `design.md`.** So a before/after verdict on `design.md` or `tasks.md`
does not show a real loss yet. The verdict on `research.md` is reliable on this evidence.

## How the judge runs

- The command is `claude -p --tools "" --setting-sources project --strict-mcp-config --model sonnet --output-format json`.
- The cwd is a new temporary directory, so no `CLAUDE.md` loads.
- A probe call with these flags saw 0 skills whose names start with `wb:`. So no plugin
  loaded.
- The mechanical counts beside each verdict come from `judge.mechanical()`: refs, IDs,
  barriers, and the expected facts cited at the exact `file:line`.

## Pair 1: the altered copy (known loss)

The before file is `before/1/plan/research.md`. The after file is
`calibration/research-altered.md`. It is the same file with two changes:

- **Fact F6 removed.** F6 is "the CLI exits with status 2 when a link is broken". The summary
  sentence, the `if broken: return 2` code lines, and the step-4 sentence no longer state it.
- **The `config.py:4` reference removed.** The link on the `MAX_RETRIES` bullet and the
  `src/linkcheck/config.py:4` line in the reference list are gone.

| Run | Verdict | Lost facts | Lost refs |
| --- | ------- | ---------- | --------- |
| 1 | loss | F6 | `src/linkcheck/config.py:4`, `src/linkcheck/cli.py:18` |
| 2 | loss | F6 | none |
| 3 | loss | F6 | `src/linkcheck/config.py:4` |

The judge flags the altered copy in 3 of 3 runs, so the P2-T7 bar holds. It names the lost
fact every time. It names the lost `config.py:4` reference in 2 of 3 runs. The mechanical
count finds that reference loss every time, so the report shows both.

## Pair 2: the real output (same tree, two runs)

The before and after files are `before/1/plan/<doc>` and `after/1/plan/<doc>`. Both come from
2.1.1, so any difference is run-to-run variance.

| Document | Runs | Verdicts | Mechanical: expected facts cited, before and after |
| -------- | ---- | -------- | -------------------------------------------------- |
| `research.md` | 3 | no loss, no loss, no loss | F1–F5, then F1, F2, F3, F5 |
| `design.md` | 1 | loss (F1, F2, two refs) | F1, F2, F3, F5, then F3, F5 |
| `tasks.md` | 1 | no loss | F2, F3, F5, then F5 |

The `design.md` loss is a false positive for this purpose. The two runs chose different
designs, and the second design does not restate the default timeout or the attempt count.
The expected-fact counts also move between runs of the same tree, for all three documents.

## What this means for the gates

- The Phase 4 and Phase 5 gates use "no loss in 3 of 3 repeats". A per-document
  before/after verdict on `design.md` or `tasks.md` can fail that gate with no plugin change.
- The `research.md` verdict held 3 of 3 on the same tree. It is usable as a gate on this
  evidence.
- The metric counts also vary between runs of the same tree. Sentences over 25 words were
  12.0% and 8.4%, and IDs used alone in chat were 6 and 0. A single repeat cannot show a
  change of that size.
- A human decides how the gate uses the judge before P4-T9 and Phase 5. See the
  Implementation Discoveries in `tasks.md`.

## The within-run mode (P4-T10, design.md D7)

D7 changed the gate. The judge now asks whether a run's `design.md` and `tasks.md` carry
forward the facts, `file:line` references and IDs of that run's own `research.md`. For
`tasks.md`, the run's `design.md` is given as context. The command is
`python3 evals/judge.py --run <run> --within`, or `--research <file> --doc <file>` for one
judgment.

The calibration used the 2.1.1 baseline run, `evals/runs/20260930T013327Z` (3 repeats). The
files are in `calibration-within/`.

**The planted loss** is a copy of `before/1/plan/design.md` with fact F2 removed in 5 places:
the default of 3 attempts at `config.py:4`. The copy still says "the existing default" and "the
default number of times".

| Prompt | Planted copy flagged | Real run, no loss |
| ------ | -------------------- | ----------------- |
| v1 | 0 of 3 | 3 of 3 repeats (6 of 6 judgments) |
| v2 | **3 of 3** (F2 each time) | **3 of 3 repeats (6 of 6 judgments)** |

- **Prompt v1** told the judge to ignore research facts that the chosen approach does not need.
  The judge then read "the existing default" as enough, and it missed the loss in all 3 runs.
  The mechanical count did find it: F2 was cited in `research.md` and not in the copy.
- **Prompt v2** adds one rule. If a document mentions a setting, default, limit or behavior
  from research, it must give the research value or its `file:line`. With that rule, the judge
  flags the planted copy every time and still finds no loss in the real run.

**Result: the within-run mode is calibrated (prompt v2).** P4-T9 and Phase 5 use it as the
"no loss" gate. The v1 verdicts are kept in `calibration-within/v1/`.
