# state.md — touch-grass checkpoint

Write this output in wb Technical English (WBTE): read [technical-english.md](../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

<!--
Copy this file to your checkpoint directory (the default is `.context/<slug>/state.md`). Fill it
in BEFORE any research. This file holds the whole run. Assume that the session stops between
segments, so a resume must lose nothing and use THIS FILE ALONE. Keep the sections in this order.
-->

## Header

- **Question:** <the one decision or deliverable the whole loop serves>
- **Deliverable spec:** <what "done" looks like — format, length, audience>
- **Operating model:** <triad ranking, e.g. quality > money > time>
- **Deadline:** <absolute datetime, or "none">
- **Checkpoint dir:** <path>
- **Deliverable file:** <path, e.g. .context/<slug>/report.md>

<!-- AMENDMENT blocks: append one VERBATIM when the user changes the scope during the run.
     Never rewrite the history above. Later segments get the changes from the amendments. -->

### AMENDMENT 1 — <date/time>

<what the user changed, in their words, and your restatement>

## Segment plan

<!-- Each segment is ONE sub-question. Size it before you run it. Tick it when its FINDINGS are written. -->

- [ ] S1: <sub-question> — size: <small|medium|large>, est. <N> calls
- [ ] S2: <sub-question> — size: <…>, est. <N> calls
- [ ] S3: <…>

## Budget ledger

| Segment | Estimate | Actual | Notes (record every deliberate cut here. Silent truncation is forbidden) |
| ------- | -------- | ------ | ------------------------------------------------------------------ |
| S1      | <N>      | <N>    | <e.g. "skipped source X because Y">                                |

## Findings

### S1 — <sub-question> — confidence: <high|medium|low>

<short, complete findings. Cite each source by its number in the ledger below.>

<!-- add one FINDINGS block per completed segment -->

## Decision so far

<the current verdict. Update it after EVERY segment. What is the answer if the run stops now?>

## Sources ledger

| # | Source (URL / path) | Takeaway | Confidence |
| - | ------------------- | -------- | ---------- |
| 1 | <url or file>       | <one line> | <h/m/l>  |

## Next action

<Write this so that a model with NO earlier context can do it exactly as written.
Name the segment, the sources, and the depth. The wakeup prompt resumes from this action.>
