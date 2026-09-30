# Objective 2 verdicts: the gated "lite" rewrite (Phase 5)

This record holds the Phase 5 gate for each "lite" rewrite of instruction prose. A rewrite is
kept only if the within-run judge (D7) finds no loss and `token_check.py` finds no new kind of
failure. Because of D10, each gate has 1 repeat, not 3.

## The large fixture (P5-T5)

On the small fixture (`evals/fixture/`), no stage spawned an agent in 12 sessions. So 5 of the 9
Phase 5 files could not show "no loss". P5-T5 built `evals/fixture-large/`:

- `linkcrawl`, a synthetic link crawler and checker written for the fixture. It has 77 Python
  files (65 in `src/`, 12 in `tests/`) and 4,178 lines, in 9 subpackages. It also has
  `README.md`, `pyproject.toml`, and 3 docs.
- A research question that spans several subsystems, and 19 expected facts across 13 files. The
  plan seed is identical to the small fixture's.
- `--fixture` on `evals/run.py`, `evals/judge.py`, and (through the run manifest)
  `evals/report.py`.

**Spawn evidence.** The tracer (`evals/runs/20260930T082028Z`, `create_research` only, Phase 4
tree `f2c78e8`) spawned `codebase-locator`, `codebase-analyzer`, and `pattern-finder`. In every
later run, all three stages spawned agents, and each stage read its own `reference.md` and
`sub-agent-prompts.md` (and `examples.md` for `create_tasks`).

**The before-run** is `evals/runs/20260930T082432Z`, repeat 1, on the Phase 4 tree `f2c78e8`.
All 3 stages wrote their documents, at a cost of $4.88 over 714 s. It cited 5 of the 19 facts.
The within-run judge found no loss in `design.md` or `tasks.md`.

**Budget (D10).** At about 01:38, four parallel runs on the large fixture hit the user's
individual spend limit. Repeats 2 and 3 of the first four runs failed with no output. The user
chose 1 repeat for each gate. Every verdict below is "1 of 1".

## Method for each gate

- The gate tree is the Phase 4 plugin (`git archive f2c78e8 plugin`) with only that task's
  rewritten files copied over it. Trees built this way are not affected by later commits.
- Each rewrite was drafted in `.context/lite/`. A mechanical check confirmed that every line
  with ⛔, "NOW", or a capitalized scope word is kept, and that the headings, code blocks, and
  frontmatter are unchanged. `token_check.py` and `link_check.py` pass on the overlaid tree.
- The run is `evals/run.py --before <gate tree> --repeats 1 --fixture evals/fixture-large`.
- The judge is `judge.py --fixture evals/fixture-large --research <run>/research.md --doc
  <run>/design.md`, then the same call for `tasks.md` with `--context design.md`.
- **Exercise evidence** comes from the transcripts. It lists each rewritten file that a stage
  read, and each agent that a stage spawned.

## Verdicts

| Task | Files | Run | Exercised | Judge (design, tasks) | Token failures | Facts cited | Cost | Kept? |
| ---- | ----- | --- | --------- | --------------------- | -------------- | ----------- | ---- | ----- |
| P5-T1 | `create_research/reference.md`, `create_research/sub-agent-prompts.md` | `20260930T082512Z` | both files read by `create_research`, 4 agents spawned | no loss, no loss | only the known git keys | 5 of 19 | $4.52 | **kept** |
| P5-T2 | `create_design/reference.md`, `create_design/sub-agent-prompts.md` | `20260930T082458Z` | both files read by `create_design`, 6 agents spawned | no loss, no loss | only the known git keys | 6 of 19 | $6.37 | **kept** |
| P5-T3 | `create_tasks/reference.md`, `create_tasks/examples.md`, `create_tasks/sub-agent-prompts.md` | `20260930T120839Z` | all three files read by `create_tasks`, 3 agents spawned | no loss, no loss | only the known git keys | 6 of 19 | $5.61 | **kept** |
| P5-T4 | `agents/codebase-analyzer.md`, `agents/codebase-locator.md` | `20260930T122037Z` | spawned in all three stages (`codebase-analyzer` 9 times, `codebase-locator` once) | **loss**, no loss | only the known git keys | 5 of 19 | $5.34 | **restored** |

**P5-T4 is restored.** Its `design.md` cites `src/linkcrawl/core/classify.py:81-83` for the
429-to-skipped rule. That file has 40 lines, and research gives the rule at `classify.py:29`. With
1 repeat, the cause could be the agent rewrite or run-to-run variance. The gate rule keeps a
rewrite only when it shows no loss, so the two agent files stay as they are in 2.1.1. The draft
is kept in `.context/lite/plugin/agents/` for the post-3.0.0 pass, which can gate it again with 3
repeats.

## Token cost

`claude --plugin-dir <tree>/plugin plugin details wb`:

| Item | 2.1.1 (`4b32306`) | Final tree (P5-T4) |
| ---- | ----------------- | ------------------ |
| Always-on, every session | ~3,251 | ~3,412 (the new `wbte-dictionary` skill adds ~130) |
| `create_research` on invoke | ~5.2k | ~5.2k |
| `create_design` on invoke | ~5.4k | ~5.4k |
| `create_tasks` on invoke | ~3.8k | ~3.8k |
| `codebase-analyzer`, `codebase-locator` on invoke | ~1.2k, ~1k | ~1.2k, ~1k |

`plugin details` does not count hook output or runtime reads. Two more costs apply:

- **The rule card** is 141 words (about 190 tokens) at every session start, and again after each
  compaction.
- **The reference doc** is read when a stage follows a link line. It has 1,571 words, so about
  2,100 tokens. The model followed the link in about two of three linked stage runs
  (P4-T2).

## Summary

| Result | Tasks |
| ------ | ----- |
| Kept (no loss, 1 of 1) | P5-T1, P5-T2, P5-T3: 7 skill files |
| Restored (loss in `design.md`) | P5-T4: the 2 agent files |
