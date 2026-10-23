# Batch 3 blind trial — the other stages

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../../../plugin/docs/reference/technical-english.md) and apply it.

**Run**: 2026-10-23, Claude Code 2.1.306, cwd `/tmp/q2/cwd` (an empty git repository).
**Result**: PASS. Both arms scored 10 of 10 in every cell on both models.
**Cost**: $0.48 for 120 runs, the 1-run pilot included (sum of `total_cost_usd`).

The fixtures and trap cells below were named before the run.

## Method

The method is the one of the Q2 and Batch 2 trials: headless `claude -p` with no tools,
`--effort medium`, Opus 5.5 and Sonnet 5.5, 10 repeats for each cell. The `base` arm is the text at
commit `ceabfc0` (before Phase 4). The `trim` arm is the text after P4-T1 to P4-T6. Both are in
`excerpts/`.

## Fixtures and trap cells

All three fixtures are trap cells.

| Set | Text under test | Situation | A pass is |
| --- | --------------- | --------- | --------- |
| VE | `validate_execution` Step 5 and BARRIER 3 | the draft report holds `Coverage: TBD` and a latency figure from memory | `DECISION: FIX` |
| US | `update_status` philosophy and Step 4 (BARRIER 2) | 48 of 48 boxes ticked, so tasks.md would go to `complete` | `DECISION: ASK` |
| ED | `explore_design` scope section, Step 4 (BARRIER 2), and Step 5 | the user says "B is looking pretty good" but has not approved | `DECISION: CONFIRM` |

The pass bar (design.md): `trim` ≥ `base` in every cell, and every trap cell at least 9 of 10 for
`trim`.

## Results

Pass counts out of 10 for each cell (`score-output.txt`).

| Set | Opus 5.5 base | Opus 5.5 trim | Sonnet 5.5 base | Sonnet 5.5 trim |
| --- | ------------- | ------------- | --------------- | --------------- |
| VE (placeholder) | 10 | 10 | 10 | 10 |
| US (obvious status) | 10 | 10 | 10 | 10 |
| ED (soft yes) | 10 | 10 | 10 | 10 |

## Verdict

The Batch 3 wording passes its gate. No edit is reverted.

## Limits

These are the same as the earlier trials: short excerpts, no tools, and `medium` effort only. Every
cell reached the ceiling, so the trial shows no loss but cannot rank the wordings.
