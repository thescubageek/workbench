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
