# Spike: which implementation should `check-guards` be?

**Status**: pre-registration written 2026-09-18 **before** any candidate was built or run.
Results appended below it, unedited above the line.

## The load-bearing assumption

Three fix rounds have patched `check-guards` and each closed real holes while opening comparable
ones. Every remediation option on the table assumes **the implementation stays a line-oriented
bash regex scanner**. If that assumption is wrong, patching it a fourth time is wasted work.

## What is being probed

One corpus, three candidate implementations, two scores.

**The corpus** is the asset three review rounds already bought: every `MUST-FIRE` and
`MUST-NOT-FIRE` case in `test-guards`, plus the six shapes round 3 found, plus the shape the
`shellcheck` observation raised (Q8-5). Each case carries its provenance — which round found it —
so the corpus doubles as the regression record.

**The candidates**:

| | Implementation |
| - | -------------- |
| **A** | current `check-guards`, unchanged — the baseline |
| **B** | `shellcheck -o all` plus a fence extractor |
| **C** | a throwaway implementation using a real CommonMark fence parse and shell tokenisation |

**The scores**, both required — round 3 established that the first alone is not enough:

1. **Corpus score** — MUST-FIRE caught, MUST-NOT-FIRE false positives.
2. **Mutation survivability** — plant single-line breaks and count how many the corpus catches.
   Phase 7 scored 100% on its corpus while four of its new guards were deletable with the suite
   green, so an implementation that wins on (1) and loses on (2) has not actually won.

## Pre-registered outcomes

Written before running, so the verdict is read *against* them rather than around them.

- **B wins** — `shellcheck` catches the shapes at an acceptable false-positive rate → delete the
  hand-rolled detectors, keep only fence extraction, depend on a maintained parser. Kills every
  patching option, and makes the dependency question in P8-T5 a yes.
- **C clearly beats A** on **both** scores → rewrite. The 11 open round-3 findings in
  `check-guards` become moot rather than fixed, and P8-T8 plans only the non-`check-guards` ones.
- **C matches A** (within noise on both scores) → the problem is intrinsically hard rather than
  badly implemented. Narrow the tool's claims, document its false-positive and false-negative
  rate, stop calling it a gate, and fix the 11 findings as ordinary remediation.
- **Nothing beats A** → strongest possible evidence for narrowing; stop spending on the
  implementation question entirely.

**Regardless of which wins**: the corpus and the mutation runner ship. They are the direct answer
to round 3's finding that every scan-verifiability guard was deletable without the suite noticing,
and they are independent of the implementation question.

## Bounds

Stop when the two scores are in. Do **not** build the winner into the real implementation inside
this spike — the point of escalating out of the fix loop is that a design decision gets decided
deliberately, and adopting it here would be the same collapse of design into execution the phase
was opened to stop.

---

## Results

*(appended after the run)*
