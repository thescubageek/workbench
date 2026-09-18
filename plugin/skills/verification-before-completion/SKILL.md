---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, passing, or done - requires running verification commands and confirming output before making any success claims. Evidence before assertions.
user-invocable: false
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
2. **FALSIFY**: What would this command print if the claim were false? If you cannot answer,
   you do not yet have a check — you have a ritual.
3. **RUN**: Execute the command (fresh, complete)
4. **READ**: Check output and exit code
5. **VERIFY**: Does output confirm the claim?
6. **ONLY THEN**: Make the claim with evidence

Skip any step = not verified.

## Step 2 is the one that gets skipped

A check that cannot fail is not evidence. It is the *shape* of evidence, and it passes every
other step in this gate — you identified a command, ran it, read its output, and the output said
clean. Nothing in steps 3–5 catches it, because the command really did run and really did say
that.

**Silence is ambiguous, and that is where this hides.** "No output" means *either* "nothing
matched" *or* "the command never worked". A check that treats those alike reports a broken
measurement as a clean result — and the error is always in the same direction: toward believing
things are fine.

**For a new check, see it fail once.** Plant the failure it is meant to catch, confirm it fires,
remove the plant. A check verified only against a passing case is a check you have never tested.

### Mechanisms that produce a check which cannot fail

| Mechanism | Why the silence lies | Guard |
| --------- | -------------------- | ----- |
| Counting instead of listing | `0` and "the command failed" are the same output; a listing makes the difference visible | Print the matches; count only what you have already seen |
| `grep` exit status discarded | `0` matched, `1` no match, `2` **error**. `$( )` and pipes throw it away, so a missing file and a clean file look identical | Test the status, or `[ -e "$f" ] \|\| continue` first |
| Unquoted glob in an argument | **Shell-dependent**: `bash` passes an unmatched glob through literally and the command works; `zsh` errors and the result is silently zero. A check that passed in one shell can be broken in another | Quote it: `--include='*.py'` |
| Unmatched glob in a `for` | The body runs once with the literal pattern as the filename | `[ -e "$x" ] \|\| continue` as the body's first line |
| Pattern cannot match the real encoding | Non-ASCII arrives escaped — `strings` emits an em-dash as the literal `\u2014` — so a pattern written with the character matches nothing | Match an ASCII-only substring, and run the check once before trusting it |
| A probe whose environment cannot trigger the condition | The thing under test was never reachable from where it ran | Record the working directory and environment alongside the result |

### Prefer showing the evidence to counting it

Every instance of this failure observed so far was a **count**. That is not a coincidence:
a count destroys the information that would have caught it.

`grep -c` returning `0` is indistinguishable from a command that never ran. The same search
printing its matches is not — an empty list *where you expected two file paths* is visibly wrong,
because you already know what should be there.

```text
# Fragile: 0 and "broken" look identical
n=$(grep -c "$sym" --include='*.py' -r .)
```

```bash
# Better: you see what was found, and notice when it is nothing
grep -rn "$sym" --include='*.py' . | sed 's/^/  /'
```

So: **say what you expect the command to print, then run it.** "This should list two call sites"
turns a zero into an obvious error instead of a clean result. That is the FALSIFY step moved from
claim-time to command-time, which is where the mistake is actually made.

Use a count only when you have already seen the listing, or when the count is guarded and its
failure is distinguishable from zero.

### Red flags when *writing* a check

- It has only ever been observed passing.
- It has only ever been observed passing **in one shell**. Glob and quoting behaviour differ
  between `bash` and `zsh`, and the difference shows up as a wrong number, not an error.
- You cannot say in one sentence what makes it print something.
- It checks for the **absence** of a string — absence passes for every reason, including wrong
  path, wrong pattern, and wrong encoding.
- Its result is a count, and nothing distinguishes "counted zero" from "could not count".
- It is a count at all, when a listing would have shown you what was found.

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
| "The check came back clean" | Can it come back dirty? Show it doing so |
| "No output, so nothing's wrong" | No output is not a result until the check can produce one |

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

```
[Run: grep -rn "$sym" --include=*.py .]
[Output: (nothing)]

No callers outside the diff — safe to change the signature.
```

The glob was unquoted, every `grep` errored, and the loop reported zero callers. There were two.
The command ran, the output was read, and the conclusion was still wrong — which is why
**FALSIFY** is a step and not a footnote.

## Integration with Status Updates

Before running `/wb:update_status` to mark phases complete:

- Run all phase verification commands
- Confirm all tasks actually done
- Check automated criteria pass
- Then update status with evidence
