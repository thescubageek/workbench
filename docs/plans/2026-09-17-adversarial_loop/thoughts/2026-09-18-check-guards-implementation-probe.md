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

Corpus: **38 cases** — 23 MUST-FIRE, 15 MUST-NOT-FIRE — assembled from every case in
`test-guards`, the six shapes round 3 found, and three cases for Q8-5. Each case carries its
provenance, so the corpus doubles as the regression record.

### Score 1 — corpus

| Candidate | Must-fire caught | False positives | Total |
| --------- | ---------------- | --------------- | ----- |
| **A** current `check-guards` | 20/23 | 1/15 | **34/38 = 89%** |
| **B** `shellcheck -o all` + fence extractor | 22/23 | **10/15** | **27/38 = 71%** |
| **C** fence parse + substitution spans | **23/23** | 1/15 | **37/38 = 97%** |

A missed exactly the three round-3 findings still open (`guard-on-earlier`, `hash-in-string`,
`tilde-fence`) and false-positived on `ortrue-comment` — the corpus reproduces round 3's findings
independently, which is a useful cross-check that it has teeth.

### Score 2 — mutation survivability

Eight single-line breaks per candidate; how many does the corpus catch?

| Candidate | Caught | Survived |
| --------- | ------ | -------- |
| **A** | **4/8 = 50%** | stop scanning extensionless scripts · delete the 0-file refusal · delete the find-stderr refusal · delete the missing-target check |
| **C** | **7/8 = 87%** | break the fence closer |

**A's four survivors are exactly the four round 3 found by hand.** An independent method
reproduced that result, which is the strongest evidence in this spike that the second score is
worth taking.

C's single survivor is a **corpus gap, not an implementation gap**: no case yet requires a fence
to close correctly for the outcome to differ. That case should be added whichever candidate wins.

### Verdict, read against the pre-registration

Pre-registered: *"C clearly beats A on both scores → rewrite."* **That is the outcome.**
97% vs 89% on corpus, 87% vs 50% on mutation.

**B is dead**, and for a reason worth recording: `shellcheck` is not wrong, it is answering a
different question. `SC2312` flags every masked return value, so it fires on `n=$(count foo f)
|| exit 2` and on `[ -e "$x" ] || continue` guards alike — **10 false positives on 15 correct
files**. Nothing filters that down to our three shapes without re-implementing the policy layer,
which is the part that keeps breaking. It also missed the unquoted `--include` glob entirely.
Adopting it as the *engine* is out; adopting it as an *independent linter for our own scripts* is
a separate and still-open question, and a default-severity run already found real defects
(`cd` without `|| exit` in `check:17` and `check-guards:35`; two dead assignments in
`test-count:68`).

### Q8-5 — is shape 1 even well-formed?

Partly answered, and the answer is uncomfortable. The corpus distinguishes
`n=$(grep -c foo f)` followed by `echo` (MUST-FIRE) from the same capture followed by
`if [ $? -ge 2 ]` (MUST-NOT-FIRE) — so the rule is well-formed only if stated as **"captured and
the status never tested"**, which needs lookahead. Neither A nor C does this: C's single false
positive is exactly that case. `shellcheck` declines to flag the bare assignment at all, and on
the narrow question of whether the status is *masked*, it is right.

**Methodological caveat, stated rather than buried**: I labelled the disputed case MUST-FIRE,
which encodes my prior into the corpus. A reviewer who thinks a bare assignment is fine would
score every candidate differently. The label is the thing to argue with, not the numbers.

### What this did not decide

Per the pre-registered bound, **C was not built into the real implementation** and must not be
adopted on this evidence alone. C is a ~130-line spike with no tests of its own, one known false
positive, and one uncovered mutation. What the spike establishes is that the *approach* — real
fence parsing plus substitution-span analysis instead of line regexes — is materially better on
both axes. Turning that into a shipped tool is a separate decision, and the decision is the
user's.
