---
name: doc-adherence
description: Use when about to state what a plan document says (per the design, the plan calls for, research shows, as documented) or when resuming work after context compaction - requires the claim to come from a read of that file in the current context window, not from a summary or memory.
user-invocable: false
allowed-tools: Read, Glob, Grep
---

# Doc Adherence

Claiming what a plan document says based on a compacted summary is guessing dressed up as citation. A summary is a paraphrase of what a doc said at compaction time — it does not track edits and nothing marks it stale.

## The Iron Law

```
NO ASSERTIONS ABOUT PLAN DOC CONTENTS WITHOUT A READ IN THE CURRENT CONTEXT WINDOW
```

If the full read isn't visible in this context window, you cannot cite it.

## Why Summaries Lie

Compaction replaces the doc's actual text with a model-generated paraphrase. The paraphrase can drop caveats, merge sections, or simply misremember a detail — and nothing in the transcript flags it as degraded. It reads exactly as confidently as a real quote, so the drift is invisible unless you go check.

**Status is where this bites hardest.** `tasks.md`'s checkboxes are the only record of what is done. A summary that says "Phase 2 is complete" is a claim about 30 checkbox characters it no longer has in front of it — and unlike a prose paraphrase, that one is directly actionable and wrong in a way that compounds: work gets skipped, or redone.

## The Gate

Before stating what a plan document says:

1. **IDENTIFY**: Which doc backs this claim — research.md, design.md, tasks.md, journal.md, or a thoughts doc under `docs/plans/`?
2. **CHECK**: Is a full read of that file present in the current context window (not before a compaction)?
3. **IF NOT**: Read it now, fully — no offset/limit shortcuts on a doc you're about to cite.
4. **ASSERT**: State the claim, citing file:line.

Skip step 3 = the claim is unverified.

## Common Rationalizations

| Excuse | Reality |
| -------- | --------- |
| "I read it before the compaction" | Compaction replaced that read with a paraphrase. It no longer counts. |
| "The summary captured the key points" | Summaries drop caveats and merge sections silently. You can't tell what it dropped without re-reading. |
| "It's a small detail, re-reading is wasteful" | A `Read` is cheap; a wrong claim about the plan is not. |
| "I wrote that doc myself earlier" | Authorship isn't a read in this window. Docs get edited between sessions too. |
| "I flipped that checkbox myself, so I know it's done" | You know you *intended* to. A file write can fail, and an edit can land in the wrong place. Status claims come from the file. |

## Red Flags - STOP

- Saying "per the design" or "the plan says" with no read of that file in this window
- Describing `tasks.md` progress from memory — count the checkboxes instead
- Reporting a task as done without the checkbox in front of you
- Proposing work that the checkboxes or git state may already record as done — check state before proposing
- Treating a compaction summary's description of a doc as if it were the doc

**All of these mean: STOP. Read the file. Then assert.**

## When NOT to Apply

- The doc was fully read earlier in the SAME uncompacted window (no compaction has happened since)
- The file in question isn't a plan document (research.md / design.md / tasks.md / journal.md / thoughts docs under `docs/plans/`)
- The user just pasted the exact text you're quoting

## Relationship to the Recovery Hook

The deterministic boundary signal — knowing a compaction just happened — is handled by `hooks/wb-prime.sh`, which prints recovery text on a compact trigger and on PreCompact. Hooks are the only mechanism that survives a compaction boundary reliably; skill text does not.

This skill covers the judgment call *between* those boundaries: recognizing when a claim needs a fresh read versus when a prior read still counts. The hook tells you the ground shifted; this tells you what to do about it every time thereafter.

The same hook's session-start bootstrap prints plan position from the checkbox counts. Treat that as a **pointer, not a citation** — it is accurate at the moment it ran, and the same rule applies: cite the file, not the banner.
