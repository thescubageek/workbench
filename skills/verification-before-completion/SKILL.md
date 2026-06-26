---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, passing, or done - requires running verification commands and confirming output before making any success claims. Evidence before assertions.
---

# Verification Before Completion

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this response, you cannot claim it passes.

## The Gate

Before claiming ANY success:

1. **IDENTIFY**: What command proves this claim?
2. **RUN**: Execute the command (fresh, complete)
3. **READ**: Check output and exit code
4. **VERIFY**: Does output confirm the claim?
5. **ONLY THEN**: Make the claim with evidence

Skip any step = not verified.

## What Requires Verification

| Claim | Requires | NOT Sufficient |
| ------- | ---------- | ---------------- |
| "Tests pass" | Test output: 0 failures | Previous run, "should pass" |
| "Build succeeds" | Build command: exit 0 | Linter passing |
| "Bug fixed" | Regression test passes | "Code changed" |
| "Task complete" | All acceptance criteria checked | "Looks done" |
| "Phase complete" | All tasks verified | Some tasks done |

## Common Rationalizations

| Excuse | Reality |
| -------- | --------- |
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ tests ≠ build |
| "I'm tired" | Exhaustion ≠ excuse |
| "Already checked earlier" | Fresh verification required |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Saying "Done!" before running tests
- About to commit without verification
- Relying on partial checks
- Expressing satisfaction before evidence

**All of these mean: STOP. Run verification. Then claim.**

## Correct Pattern

```
[Run: npm test]
[Output: 34/34 passing]

All tests pass.
```

**Quieting verification without losing evidence.** A green run only needs to
prove "it passed" — the full log just burns context. `scripts/quiet <command>`
is exit-code-faithful: on success it prints a checkmark plus the runner's
summary line (your evidence — e.g. `34 passed in 1.2s`); on failure it dumps the
full output and preserves the non-zero exit code. So you still RUN fresh, still
READ exit code and a real output line, and still VERIFY — you just don't drown in
200 lines of green. Failures are never suppressed, which is exactly when you need
the detail.

```
[Run: scripts/quiet npm test]
[✓ npm test (181 lines suppressed → /tmp/wb-quiet.ab12cd)]
[  34 passed in 1.2s]

All tests pass.
```

## Incorrect Pattern

```
I've fixed the bug. Tests should pass now.
```

No output = no evidence = not verified.

## Integration with Status Updates

Before running `/wb:update_status` to mark phases complete:

- Run all phase verification commands
- Confirm all tasks actually done
- Check automated criteria pass
- Then update status with evidence
