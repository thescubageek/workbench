# Thrashing, and why a review round's output is a plan rather than a patch

**Status**: exploration, 2026-09-18. Feeds a design decision; decides nothing on its own.

Three adversarial review rounds against this branch produced a result none of them was looking
for: **the fixes were introducing defects at roughly the rate the reviews were removing them.**
This document records the evidence, names the mechanism, and proposes the change. It exists
because the loop had no way to notice, and a human had to.

## The evidence

| Round | Findings | In the previous fix's surface | Scope reviewed |
| ----- | -------- | ----------------------------- | -------------- |
| 1 | 22 | — (first pass) | full diff, 6 legs |
| 2 | 22 | 14 (64%) | full diff, 6 legs |
| 3 | 12 | ~8 (67%), 6 in `check-guards` alone | **scoped** — ~12% of the surface, 2 legs |

**The introduced-rate did not decay, and normalised for scope it rose.** Round 3 examined an
eighth of the surface with a third of the lenses and still found two thirds of its findings in
code the previous round's fixes had written.

Two specific shapes, both observed, both near-proof that a fix was pattern-matched rather than
understood:

- **Mirror-image regressions.** The `mktemp` fix for *"a fixed path gets reused across runs"*
  shipped a template whose `X`s were not trailing — a literal fixed path. The guard-walk fix for
  *"a guard on a later capture excuses an earlier one"* shipped *"a guard on an earlier capture
  excuses a later one."* In both cases the fix addressed the single instance it was shown and
  recreated the class from the other side.
- **Same-file recurrence.** `check-guards`, `adversarial-review/SKILL.md` and
  `reply-to-claude/SKILL.md` each produced findings in all three rounds.
  `adversarial-review/reference.md` already says *"one defect in a region is evidence of a
  second, not of a region now cleared"* — it just never turned that observation into a rule that
  stops anything.

## Mechanism 1 — the gate is a level test, so it cannot see oscillation

The loop stops when a pass returns no finding adjudicated `Valid`. That is a measurement of the
*current* round. It is not a measurement of the *trend*, and the two are different questions: a
loop can oscillate indefinitely while every individual round looks like progress, because every
individual round **is** progress on the findings it was handed.

Nothing in the loop compares round N to round N−1. There is no record to compare against — which
is the same gap round 3 found independently: `adversarial-loop` says *"Record the disposition and
its evidence"* and names no destination, so the gate is self-certified and unauditable.

## Mechanism 2 — batch-fix, batch-verify

This is the larger one, and it is a property of how the fix phases were actually executed:

```
Phase 6:  22 tasks -> 3 commits.  Gates run once, at the end.
Phase 7:  22 tasks -> 1 commit.   Gates run once, at the end.
```

**An aggregate green is compatible with any number of offsetting individual failures.** Running
`check` after twenty-two changes establishes that the tree passes the gates. It establishes
nothing about whether change #14 did what it was supposed to do, and nothing at all about whether
change #14 broke something change #9 had just fixed. Both of those happened.

The deeper loss is subtler. **Every verified finding already contains its own acceptance test.**
The evidence contract requires a `failure_scenario`: *concrete inputs or state → the specific
wrong outcome*. That is a test case, pre-written, by the reviewer, in the finding. Batch-fixing
throws it away — nobody re-runs the original failure scenario against the fix, so "fixed" means
"I edited the thing the finding pointed at."

## Mechanism 3 — a fix phase is design work wearing execution clothes

A remediation task feels like execution: the analysis is done, the defect is named, the change is
small. So it receives execution-level care. But choosing *how* to close a finding is a design
decision, made fast, usually without research, and — as rounds 2 and 3 show — frequently at the
wrong altitude. Every `check-guards` fix patched a regex; none asked whether a line-oriented
regex scanner over shell and CommonMark is the right shape at all.

That is the generalisation: **thrashing is often a design defect being treated as a series of
implementation defects.** A review loop reviews diffs. A design defect is not in the diff. So the
loop cannot fix one by construction — it will keep finding its symptoms, forever, and each fix
will be locally reasonable.

## What this implies

**Remediation is implementation, so it should get implementation discipline.** The plugin already
ships every piece of the machinery and the review loop bypassed all of it:

| Already shipped | What the review loop did instead |
| --------------- | -------------------------------- |
| `create_tasks` — phased plan, one checkbox per unit | an unordered list of findings |
| `implement` — one worker per task, fresh context, verified, committed | 22 edits in one session, one commit |
| `tdd-discipline` — RED before GREEN | edit, then run the aggregate gate |
| `verification-before-completion` — FALSIFY, then claim | claimed per-finding, verified in aggregate |
| `task-verifier` agent — per-task pass/fail | none |

Treating findings as a to-do list rather than a plan is what skipped all five.

### Why per-finding verification specifically kills the mirror-image regression

A mirror-image twin is created by generalising from the single input you were shown. If the
finding's `failure_scenario` must be **reproduced before the fix** — the RED step — you are
forced to characterise the class rather than the instance, and the mirror case is the obvious
second case to write. `tdd-discipline` already requires this. It was never pointed at fixes.

## Options considered

1. **Keep batch-fixing, add a stricter final gate.** Rejected: round 3 showed the final gate is
   exactly what cannot see offsetting failures, and mutation testing showed four of Phase 7's new
   guards were deletable with the suite still green. A stronger aggregate gate is more of the
   thing that did not work.
2. **One commit per finding, verified in place, no plan document.** Better, and insufficient:
   it fixes the verification granularity but still has no cross-round memory, so thrashing stays
   invisible and dispositions stay unrecorded.
3. **A review round emits a remediation plan, executed by `implement`, with a findings ledger
   spanning rounds.** Proposed. It reuses machinery that exists, closes round 3's
   "no durable disposition record" finding with the same artifact, and makes the trend measurable.

## Proposed shape

**A review round's output is a plan, not a patch.**

- `adversarial-review` emits findings, as now.
- Findings become a **remediation `tasks.md`** — real task IDs, ordered, with dependencies.
  Findings in one file and one class group into one task; findings in one file and different
  classes stay separate, and the task that touches a file re-verifies every finding against it.
- Each task carries its finding's `failure_scenario` as its **acceptance criterion**, so the
  verification step is written before the fix and is specific to that finding.
- `implement` executes it: one worker per task, fresh context, `task-verifier`, one commit each.
- A **findings ledger** (`review-log.md`) records every finding across rounds — file, class,
  verdict, disposition, evidence, and whether it lands in surface the previous fix touched
  (mechanically derivable by intersecting finding paths with
  `git diff <last-fix-base>..HEAD --name-only`).

### The circuit breaker

The ledger makes thrashing measurable, so the loop can stop on it. Candidate thresholds, to be
settled in design rather than here:

- a **mirror-image regression** — a new finding that is the inverse of one already fixed;
- the **introduced-rate failing to decay** across two consecutive rounds;
- the **same file** producing findings in three consecutive rounds.

On trip: **stop fixing.** Do not run another round. Escalate out of the loop and back into the
pipeline — `create_research` then `create_design` on the component that tripped it — and require
a tracer bullet before the next attempt.

`check-guards` trips all three thresholds, which is why the spike now queued against it is the
first instance of this path rather than a one-off.

## Open questions for design

- **Q**: Does the remediation plan live in the existing plan directory as a new phase, or in its
  own directory? A new phase keeps one status surface; a separate directory keeps the review's
  record from inflating the original plan's counters.
- **Q**: What is the verification step for a finding in **prose** — a misleading instruction has
  a failure scenario but no runnable test? Candidate: the acceptance criterion is that the
  instruction's own fenced command, executed as written, produces the stated outcome.
- **Q**: Should the circuit breaker be advisory or blocking? The plugin's model-advisory
  precedent is non-blocking; this one arguably should not be.
- **Q**: Do the thresholds hold outside this repository, where a review round may legitimately
  revisit a file for unrelated reasons?
