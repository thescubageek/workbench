---
name: tdd-discipline
description: Use when implementing features, fixing bugs, or writing any production code - enforces RED-GREEN-REFACTOR cycle where tests must fail before writing implementation code. Activates before coding begins.
---

# Test-Driven Development

Write the test first. Watch it fail. Write minimal code to pass.

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over.

**No exceptions:**

- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Delete means delete

## Red-Green-Refactor

### RED - Write Failing Test

Write one minimal test showing what should happen. Run it. Watch it fail.

**Verify failure is correct:**

- Test fails (not errors)
- Fails because feature missing (not typos)
- Failure message matches expectation

**Run it fail-fast.** In the RED/GREEN inner loop you care about *one* test, so stop at the first failure: `pytest -x`, `jest --bail`, `go test -failfast`, `cargo test` (stops by default). Fast feedback, less output to read. (This applies to the single-test loop only — at phase verification you run the whole suite and want the *complete* failure picture, so don't fail-fast there; see GREEN.)

### GREEN - Minimal Code

Write simplest code to pass the test. Nothing more.

**Don't:**

- Add features beyond the test
- Refactor other code
- "Improve" beyond what test requires

**Quiet the green runs.** A passing run only needs to convey "it passed" — a 200-line all-green log just burns working context. Pipe the verifying run through the backpressure wrapper so success collapses to a checkmark and only failures show full detail: `scripts/quiet <test command>` (preserves the exit code; see `verification-before-completion`). Use this for the full-suite/regression runs where you can't fail-fast.

### REFACTOR - Clean Up

After green only:

- Remove duplication
- Improve names
- Extract helpers

Keep tests green. Don't add behavior.

## Common Rationalizations

| Excuse | Reality |
| -------- | --------- |
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Already manually tested" | Ad-hoc ≠ systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is debt. |
| "Need to explore first" | Fine. Throw away exploration, start with TDD. |
| "TDD will slow me down" | TDD faster than debugging. |

## Red Flags - STOP and Start Over

- Code before test
- Test passes immediately (didn't see it fail)
- Can't explain why test failed
- "Just this once"
- "This is different because..."

**All of these mean: Delete code. Start over with TDD.**

## Quick Reference

| Phase | Action | Verify |
| ------- | -------- | -------- |
| RED | Write test | Fails for right reason |
| GREEN | Minimal code | Test passes, others still pass |
| REFACTOR | Clean up | All tests still green |

## When Stuck

| Problem | Solution |
| --------- | ---------- |
| Don't know how to test | Write wished-for API first |
| Test too complicated | Design too complicated. Simplify. |
| Must mock everything | Code too coupled. Refactor. |
