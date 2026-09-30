# Rule card measurement (P3-T3)

This record tests assumption A1 in design.md. A1 says that a short rule card at session start
changes the style of chat output in a way the harness can measure.

**Result: A1 is validated with card v2.** Card v1 changed the documents but not the IDs in
chat. Card v2 puts the ID rule first, with examples. It cut chat IDs used alone from 17 to 3.
It also kept the document gains and lost no expected facts.

## Method

- Every run used the fixture, the model `sonnet`, and 3 repeats for each tree.
- The before tree is `4b32306` (2.1.1). The after tree is the working tree: 2.1.1 plus
  `technical-english.md` and the card. No template links to the reference doc yet, so the card
  is the only plugin change that can reach a stage.
- The card reached the model headless. The session transcript of the first after-tree run
  contains the card text, with the path under `CLAUDE_PLUGIN_ROOT` resolved.
- All numbers come from `wbte_check.py`, `token_check.py`, and `judge.mechanical()` over the
  written documents and the chat output of each stage.

| Tree | Runs used |
| ---- | --------- |
| 2.1.1 | `evals/runs/20260930T021922Z`, before repeats 1–3 |
| Card v1 | `evals/runs/20260930T021922Z`, after repeats 1–2, and `evals/runs/20260930T042516Z`, repeat 1 |
| Card v2 | `evals/runs/20260930T043113Z`, repeats 1–3 |

Two runs were lost to network outages (`ENOTFOUND`), and neither counts:

- `evals/runs/20260930T015105Z`: the after-tree design stage failed in repeat 2, and the
  session dropped in repeat 3.
- `evals/runs/20260930T021922Z`: the after tree failed in repeat 3. So a single-tree run of
  card v1 (`20260930T042516Z`) supplied the third card-v1 repeat.

## Results

| Metric | 2.1.1 | Card v1 | Card v2 | design.md target |
| ------ | ----- | ------- | ------- | ---------------- |
| Document sentences | 1017 | 1209 | 1202 | — |
| Document sentences over 25 words | 10.4% | 4.4% | 4.3% | at most 5%, and lower than 2.1.1 |
| Over 25 words, per repeat | 11.1%, 10.1%, 10.1% | 3.5%, 5.0%, 4.8% | 5.1%, 3.3%, 4.5% | — |
| Longest document sentence | 69 words | 69 words | 51 words | — |
| Semicolons in document prose | 120 | 30 | 16 | 0 |
| Noun clusters (heuristic) | 3 | 3 | 7 | — |
| Chat sentences | 315 | 309 | 324 | — |
| Chat sentences over 25 words | 0.95% | 0.0% | 0.0% | — |
| Semicolons in chat | 3 | 3 | 2 | 0 |
| Chat IDs used alone | 17 | 20 | 3 | 0 |
| Expected facts cited, per repeat | 4, 4, 4 | 4, 4, 4 | 4, 4, 4 | no loss |
| Parser-token failures | 8 | 4 | 12 | no new kind |
| Stages written | 9 / 9 | 9 / 9 | 9 / 9 | — |
| Cost | $4.58 | $4.43 | $4.43 | — |

The P2-T8 baseline run gave 7.0% of document sentences over 25 words, with 82 semicolons and
27 lone IDs. The 2.1.1 column above comes from a later run of the same tree. The difference is
run-to-run variance.

## What moved and what did not

- **Document sentence length meets the design target with the card alone.** 4.3% is below
  5% and below both 2.1.1 runs. One card-v2 repeat was at 5.1%, so the margin is small.
- **Semicolons fell by 87%, but they are not at 0.** Most of the remaining semicolons are in
  `tasks.md` and in the fixed `✅ … ; N findings` completion line. The Phase 4 template rewrites
  target both.
- **Chat IDs used alone moved only with card v2.** Card v1 had the ID rule seventh. Card v2
  puts it first, with parenthesized examples, and names lists such as "PD1 and PD2".
  - The 3 remaining hits are `A1`, `A2`, and `A1`. Some card-v1 hits were detector limits,
    for example "A1 says callers depend on…", where the meaning follows in the same sentence.
  - The detector did not change between the measurements.
- **No expected fact was lost.** Each repeat cited 4 of the 6 facts at the exact `file:line`.
- **Parser-token failures rose from 8 to 12, all of one known kind.** They are the missing
  `git_commit` and `git_branch` keys (see the Implementation Discoveries in `tasks.md`). No
  other kind of failure occurred. This count varies between runs of the same tree (P2-T8 had
  8, and the 2.1.1 column here has 8).
- **Noun clusters rose from 3 to 7.** The heuristic has false positives, so this is a trend to
  watch in Phase 4, not a finding.

## Card versions

Card v1 (commit `a733187`, 118 words):

```text
wb Technical English (WBTE) applies to every reply and every document you write:
  1. Give the result first. Then give the reason.
  2. Write one instruction in each sentence. Use the imperative.
  3. Write at most 20 words in an instruction and 25 words in a description.
  4. Do not use semicolons. Write two sentences.
  5. Write complete sentences. Keep articles and verbs. Do not write fragments.
  6. Use the active voice and simple tenses.
  7. In chat, never use an ID alone. Write "P1-T3 (the driver probe) passed", not "P1-T3 passed".
  8. Define a term at its first use, or use a simple word.
Keep code, paths, and exempt tokens exactly as they are.
Full rules: $root/docs/reference/technical-english.md
```

Card v2 (the P3-T3 commit, 149 words). It changes the ID rule and the semicolon rule:

```text
wb Technical English (WBTE) applies to every reply and every document you write:
  1. In chat, never write an ID alone. Put its meaning in parentheses right after it:
     "PD1 (the retry bound)", "P1-T3 (the driver probe)". This applies to every task,
     question, assumption, and decision ID, also in a list such as "PD1 and PD2".
  2. Give the result first. Then give the reason.
  3. Write one instruction in each sentence. Use the imperative.
  4. Write at most 20 words in an instruction and 25 words in a description.
  5. Do not use semicolons, in chat or in documents. Write two sentences.
  6. Write complete sentences. Keep articles and verbs. Do not write fragments.
  7. Use the active voice and simple tenses.
  8. Define a term at its first use, or use a simple word.
Keep code, paths, and exempt tokens exactly as they are.
Full rules: $root/docs/reference/technical-english.md
```

Card v2 is at 149 of the 150 words that `test-prime` allows. A later wording change must
remove a word for each word it adds.

## Card v3 (P4-T9)

P4-T9 changed the card twice more, as the P3-T3 task allows ("at most 2 more times"):

- **v2b** changes only rule 1, to the per-paragraph ID rule that the user chose (D9).
- **v3** adds "Keep exact values and file:line references" (output rule 15) as rule 2.
  - In the v2b run (`evals/runs/20260930T071741Z`), repeat 1 lost the 10-second timeout
    value. Rule 15 was only in the reference doc, and the model reads that doc in about two
    runs of three (P4-T2).
  - To make room, v3 merges "active voice" and "simple tenses" into one rule, and it drops
    "simple tenses". It has 141 words.

| Run | Card | Sentences over 25 words | Within-run judge | Chat IDs used alone |
| --- | ---- | ----------------------- | ---------------- | ------------------- |
| `20260930T071741Z` | v2b | 3.1% | loss in 1 of 3 (F1) | 7, all in repeat 1 |
| `20260930T073357Z` | v3 | 2.9% | no loss in 3 of 3 | 2, in one sentence |

Card v3 is the released card:

```text
wb Technical English (WBTE) applies to every reply and every document you write:
  1. In chat, never write an ID alone. At its first mention in each paragraph, put its
     meaning in parentheses: "PD1 (the retry bound)". A range can stay bare.
  2. Keep exact values and file:line references. Write "3 attempts (config.py:4)",
     not "the default".
  3. Give the result first. Then give the reason.
  4. Write one instruction in each sentence, in the imperative.
  5. Write at most 20 words in an instruction and 25 words in a description.
  6. Do not use semicolons, in chat or in documents. Write two sentences.
  7. Write complete sentences in the active voice. Keep articles and verbs.
  8. Define a term at its first use, or use a simple word.
Keep code, paths, and exempt tokens exactly as they are.
Full rules: $root/docs/reference/technical-english.md
```

## A3: the card after compaction with no active plan

**Result: A3 is validated, 2026-09-30.** The user ran an interactive session with
`claude --plugin-dir /Users/scraig/conductor/workspaces/workbench/houston-v2/plugin`. The cwd
was `/tmp/wb-a3-noplans`, a new git repo with no plans.

1. **Startup.** The model reported the card in its context, from the wb SessionStart hook,
   with the full-rules path resolved.
2. **The first `/compact`.** It did not run ("Not enough messages to compact").
3. **Compaction.** After a few more messages, `/compact` ran. The model reported the card
   in the new context, labelled `SessionStart:compact hook success`. The PreCompact output of
   `wb-prime.sh` appeared only in the `/compact` command's stdout, so the SessionStart copy
   carries the card.
4. **Finding.** After compaction, the card was in the context twice. Both copies had the same
   text and the same `SessionStart:compact` label. So the card's token cost after compaction
   is about double. The cause is not known. It may be the harness, because the plugin
   registers `wb-prime.sh` once for SessionStart (follow-up, not changed).
