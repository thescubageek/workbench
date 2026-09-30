# Objective 1 report (P4-T9)

This report checks the design.md targets for Objective 1 (output in WBTE) on the final Phase 4
tree. Every run used the fixture, the model `sonnet`, and 3 repeats.

**Result: every target is met on the final tree, with one small remainder.** The final tree
is card v3 with P4-T9's fixes and the user's two decisions (D8, D9). The 2.1.1 lone-ID count
below is scored with the D9 detector, so it reads 25, not the 27 of the first scoring.

| Tree | Run | Plugin |
| ---- | --- | ------ |
| 2.1.1 | `evals/runs/20260930T013327Z` (the P2-T8 baseline) | `4b32306` |
| P4-T8 | `evals/runs/20260930T063927Z` | `eaf199b` |
| First fixes (rule 15, the Assumptions line) | `evals/runs/20260930T065634Z` | working tree |
| D9 ID rule, card v2b | `evals/runs/20260930T071741Z` | working tree |
| **Final: card v3** | **`evals/runs/20260930T073357Z`** | the P4-T9 commit |

## Targets

| design.md target | 2.1.1 | P4-T8 | First fixes | Card v2b | **Final (v3)** |
| ---------------- | ----- | ----- | ----------- | -------- | -------------- |
| At most 5% of document sentences over 25 words, and fewer than 2.1.1 | 7.0% | 3.3% | 3.2% | 3.1% | **2.9%** |
| No semicolons in document prose | 82 | 13 | 4 | 7 | **9**, all in the shared `tasks.md` boilerplate (D8) |
| No chat ID used alone (D9 rule) | 25 | 2 | 1 | 7 | **2** |
| No lost facts (the within-run judge, D7) | no loss 3/3 | loss 1/3 | no loss 3/3 | loss 1/3 | **no loss 3/3** |
| Parser-token failures (only the known kind) | 8 | 0 | 2 | 6 | **4** |

On the final tree, every stage wrote its document (9 of 9), and the longest document sentence
has 51 to 56 words (2.1.1: 69). Chat has 0.3% of sentences over 25 words and 0 semicolons. Each
repeat cited 5, 4 and 5 of the 6 expected facts (2.1.1: 5, 4, 4). The run cost $4.52.

**The remainder:** 2 chat IDs in one sentence, "I ticked P0-T2 and P0-T3, because research.md
is complete and design.md is approved". The reason implies the meaning, but the IDs are not
paired. The user reviews this at the Phase 4 checkpoint.

## The fixes in P4-T9

1. **The lost fact.**
   - P4-T8, repeat 3: the design wrote "a default run makes no more requests than the current
     code" and dropped the value (3 attempts, `config.py:4`).
   - The cause is a writing rule, so the fix is in the single authority. `technical-english.md`
     gains output rule 15: "Keep specific values. Do not replace a number, a name, or a
     `file:line` from the research with a general phrase."
   - With the fix, the judge found no loss in 3 of 3 repeats.
2. **The chat IDs (first fix).**
   - P4-T8, repeat 1: the `create_tasks` summary wrote "A1 holds, because…".
   - The fix is in `create_tasks/templates/plan-presentation-message.md`, which 3.0.0 does not
     share. It gains an "Assumptions and pending decisions" line with a paired example.

3. **The ID rule (D9).** The user refined it: once per paragraph, nested IDs and ranges are
   fine, and documents need not explain each ID. `technical-english.md`, card rule 1 and
   `wbte_check.py` now state the same rule. Two planted inputs prove the detector:
   `clean-lone-id-paragraph.txt` passes, and `bad-lone-id-new-paragraph.txt` fails. Every run
   is scored again with this detector.
4. **Card v3.** A lost value came back in the v2b run (repeat 1, the 10-second timeout). Rule
   15 lived only in the reference doc, so v3 adds it to the card as rule 2
   (`thoughts/2026-09-30-card-measurement.md`).

## The semicolons (D8)

- **All 9 remaining semicolons are in generated `tasks.md` files**, and each one comes from
  fixed text in `create_tasks/templates/tasks-md-template.md`.
  - They are in the checkpoint block (the sentence after "Go by the label, never by
    position"), the ID-shape rule, the "Tasks run in document order" note, and the
    prerequisites line.
  - The model copies this text into every plan.
- **The template is one of the 48 files shared with 3.0.0.** D-Q3 allows only the link line
  there. The user accepted the gap for 2.2.0 (D8), and the 3.0.0 handoff names it.

## Variance

- **Chat IDs used alone** move a lot between runs of trees with the same rules. On the D9
  detector, the last four runs gave 2, 1, 7 and 2.
- **Parser-token failures** (the missing `git_commit` and `git_branch` keys) move between 0 and
  12.
- **Document sentence length** moved in one direction over the Phase 3 and Phase 4 runs: 10.4%
  and 7.0% (2.1.1), then 4.3%, 3.1%, 3.3%, 3.2%, 3.1% and 2.9%.
- **Semicolons** from the shared `tasks.md` boilerplate vary with how much of that text the
  model copies (4, 7 and 9 in the last three runs). Semicolons outside it are 0 in each of
  those runs.
