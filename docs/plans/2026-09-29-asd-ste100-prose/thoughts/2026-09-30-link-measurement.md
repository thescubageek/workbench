# Link-line measurement (P4-T2)

This record tests assumption A2 in design.md. A2 says that the model follows a link line at
the top of a template when it writes the document.

**Result: A2 is validated, with a limit.** The model read `technical-english.md` in 4 of the 6
stage runs where the output had a link line. The linked `tasks.md` also moved towards the
design targets. In one repeat, the model did not follow either link. The card is present in
every session, so it covers that case.

## Method

- Every run used the fixture, the model `sonnet`, and 3 repeats for each tree.
- **The Phase 3 tree** is run `evals/runs/20260930T043113Z`. Its plugin is identical to
  `32912a2`: 2.1.1 with the reference doc and card v2 (`git diff 77134aa 32912a2 -- plugin` is
  empty).
- **The P4-T1 tree** is run `evals/runs/20260930T051751Z`, a single-tree run of `442e862`. It
  adds the link line in the 12 locations shared with 3.0.0. For these stages, that means
  `create_research` Step 8 and the `create_tasks` template. `create_design` has no link line
  in this tree, because its template changes in P4-T4.
- The P4-T1 run read the frozen tree `442e862`. The P4-T3 to P4-T8 edits in the working tree
  did not reach it.
- **Direct evidence** comes from the session transcripts. Each transcript was searched for a
  `Read` call on `technical-english.md`.
- **Output evidence** comes from `wbte_check.py`, `token_check.py`, and `judge.mechanical()`.

## Did the model read the reference doc?

| Tree | Stage | Link line in its output path | Repeats that read `technical-english.md` |
| ---- | ----- | ---------------------------- | ---------------------------------------- |
| Phase 3 | research, design, tasks | no | 0 of 3 each |
| P4-T1 | research | yes (Step 8 completion line) | 2 of 3 |
| P4-T1 | design | no | 0 of 3 |
| P4-T1 | tasks | yes (the `tasks.md` template) | 2 of 3 |

In repeat 3 of the P4-T1 tree, neither linked stage read the file.

## Did the output move?

| Metric | Phase 3 tree | P4-T1 tree | design.md target |
| ------ | ------------ | ---------- | ---------------- |
| Document sentences over 25 words | 4.3% | 3.1% | at most 5% |
| `tasks.md` sentences over 25 words | 7.1% | 5.8% | — |
| Semicolons in document prose | 16 | 9 | 0 |
| Semicolons in chat | 2 | 0 | 0 |
| Chat IDs used alone | 3 | 8 | 0 |
| Expected facts cited, per repeat | 4, 4, 4 | 5, 5, 5 | no loss |
| Parser-token failures | 12 | 4 | no new kind |
| Stages written | 9 / 9 | 9 / 9 | — |
| Cost | $4.43 | $4.35 | — |

- **`tasks.md` moved the most**, and its template gained only the link line. All 9 of the
  remaining document semicolons are in `tasks.md`.
- **Chat IDs used alone rose from 3 to 8.** The link lines do not target chat, and card v2 did
  not change. This is probably run-to-run variance, as the card-v1 measurement showed (17, then
  20, for two runs with the same chat rules). P4-T9 measures the chat again on the final tree.
- **No expected fact was lost.** Each repeat cited 5 of the 6 facts, against 4 for the Phase 3
  tree.
- **All 4 parser-token failures are the known missing `git_commit` and `git_branch` keys.**

## What this means

- The link line works in most runs, so the P4-T3 to P4-T8 template rewrites keep it.
- A link line alone is not enough, because one repeat in three did not follow it. The P4-T3 to
  P4-T8 rewrites also put WBTE prose into the non-shared templates, and the card stays.
- The 48 files shared with 3.0.0 keep only the link line until the post-3.0.0 pass (D-Q3).
  Their output then depends on the card and on a link that the model follows in about two runs
  of three.
