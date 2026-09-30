# Objective 1 report (P4-T9)

This report checks the design.md targets for Objective 1 (output in WBTE) on the final Phase 4
tree. Every run used the fixture, the model `sonnet`, and 3 repeats.

**Result: 3 of the 5 targets are met. 2 are close but not met, and each needs a user decision.**

| Tree | Run | Plugin |
| ---- | --- | ------ |
| 2.1.1 | `evals/runs/20260930T013327Z` (the P2-T8 baseline) | `4b32306` |
| P4-T8 | `evals/runs/20260930T063927Z` | `eaf199b` |
| P4-T8 with the P4-T9 fixes | `evals/runs/20260930T065634Z` | the working tree after P4-T9's two fixes |

## Targets

| design.md target | 2.1.1 | P4-T8 | With the fixes | Met? |
| ---------------- | ----- | ----- | -------------- | ---- |
| At most 5% of document sentences over 25 words, and fewer than 2.1.1 | 7.0% | 3.3% | **3.2%** (3.0%, 3.6%, 3.1%) | yes |
| No semicolons in document prose | 82 | 13 | **4** | no (see below) |
| No chat ID used alone | 27 | 2 | **5** (see below) | no (see below) |
| No lost facts (the within-run judge, D7) | 3 of 3 no loss | loss in 1 of 3 | **no loss in 3 of 3** | yes |
| Documents pass the parser patterns | 8 failures | 0 | 2 | yes (only the known kind) |

Other numbers for the tree with the fixes: every stage wrote its document (9 of 9), and the
longest document sentence has 51 words (2.1.1: 69). Chat has 0.3% of sentences over 25 words,
and 1 semicolon. Each repeat cited 4 of the 6 expected facts, the same as 2.1.1 (5, 4, 4). The
run cost $4.44.

## The two fixes in P4-T9

1. **The lost fact.**
   - P4-T8, repeat 3: the design wrote "a default run makes no more requests than the current
     code" and dropped the value (3 attempts, `config.py:4`).
   - The cause is a writing rule, so the fix is in the single authority. `technical-english.md`
     gains output rule 15: "Keep specific values. Do not replace a number, a name, or a
     `file:line` from the research with a general phrase."
   - With the fix, the judge found no loss in 3 of 3 repeats.
2. **The chat IDs.**
   - P4-T8, repeat 1: the `create_tasks` summary wrote "A1 holds, because…".
   - The fix is in `create_tasks/templates/plan-presentation-message.md`, which 3.0.0 does not
     share. It gains an "Assumptions and pending decisions" line with a paired example.

## Target not met: semicolons in documents

- **All 4 semicolons are in generated `tasks.md` files**, and each one comes from fixed text
  in `create_tasks/templates/tasks-md-template.md`.
  - They are in the checkpoint block (the sentence after "Go by the label, never by
    position"), the ID-shape rule, the "Tasks run in document order" note, and the
    prerequisites line.
  - The model copies this text into every plan.
- **The template is one of the 48 files shared with 3.0.0.** D-Q3 allows only the link line
  there in 2.2.0.
- **A user decision is needed.** One option accepts the gap and names it in the 3.0.0
  handoff. The other rewrites the template prose now, which is an exception to D-Q3.

## Target not met: chat IDs used alone

The detector flags 5 IDs in the three `create_tasks` summaries:

| Repeat | Flagged | Context |
| ------ | ------- | ------- |
| 1 | P0-T4 | a range: "(P0-T1 to P0-T4)" |
| 2 | A1, A2 | inside a meaning: "P1-T2 (the A1 check)", "P1-T1 (the A2 probe)" |
| 3 | A2, A2 | a second mention: "confirm A2", after the message already gave A2's meaning |

- **No ID appeared alone at its first mention.** 2.1.1 had 27 lone IDs.
- **Three hits are limits of the detector,** which does not read an ID as paired inside
  another ID's parenthetical meaning or in a range. The detector did not change between the
  runs, so the comparison with 2.1.1 is fair.
- **The strict rule is still broken.** The card says "never write an ID alone", and a second
  mention is also a mention.
- **A user decision is needed.** One option accepts the result. The other adds "every mention"
  wording and measures again (about 15 minutes and $4.50). The card is at 149 of 150 words, so
  that wording must go in the chat templates or in the reference doc.

## Variance

- Chat IDs used alone move a lot between runs of trees with the same card: 3, 8, 2 and 5 in
  the P3-T3, P4-T2, P4-T8 and P4-T9 runs.
- Parser-token failures (the missing `git_commit` and `git_branch` keys) move from 0 to 12.
- Document sentence length and semicolons move less, and they moved in one direction across
  all the Phase 3 and Phase 4 runs.
