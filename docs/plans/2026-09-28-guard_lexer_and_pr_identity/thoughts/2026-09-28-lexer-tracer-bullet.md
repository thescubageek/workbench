---
created: 2026-09-28
type: tracer-bullet
project: guard_lexer_and_pr_identity
topic: L-B (one stdlib state machine) versus L-C (ShellCheck findings as detector) for check-guards
status: run — verdict L-B
git_commit: 2eaa15f
git_branch: adversarial-loop-skill-research
---

# Tracer bullet: which lexer

**Written before any candidate exists.** The round-3 spike's rule: pre-register the bar and the
predicted outcome, then run, then read the result against the prediction — never around it.

## What is being tested

The assumption L-B and L-C share: that the existing corpus plus the mutation sweep is a
sufficient acceptance bar for replacing the lexer — that a candidate reaching the bar is one the
next review round will not thrash on. If L-B reaches the bar and the held findings' cases pass,
the class is retired by construction. If neither reaches it, the corpus is what needs redesign,
not the lexer.

## Harness

`thoughts/spike/harness/` is a copy of `plugin/scripts/test-guards`, `lib_mutate.py` and
`fixtures/` taken at `2eaa15f`, with **three corpus cases added** (below). Candidates live in
`thoughts/spike/candidates/<name>/check-guards`. A candidate is scored by
`python3 harness/test-guards candidates/<name>/check-guards` (corpus + 15 integrity claims +
25 curated mutations) and by `--generated` (395 AST mutants, in the background). The shipped
file is never touched; `A/` is the shipped checker copied in as the baseline.

**Known harness offsets, measured on the baseline before any candidate**: the copied harness
scores the shipped checker below its in-tree numbers on integrity and curated mutations because
some claims and anchors refer to the plugin tree's layout, not the file's content. The baseline's
numbers on this harness are the comparison point; the in-tree numbers are not.

## The three cases added (must-fire / must-not-fire)

Each pins one held finding. Written before the candidates so the bar cannot be fitted to them.

| id | pins | expect | content (one fenced `bash` block in a `SKILL.md` unless noted) |
| -- | ---- | ------ | ------- |
| `r10-t10-escaped-dollar-paren` | R10-T10 | 0 | `f="cost \$(grep -c q f)"` — a backslash-escaped `$(` inside double quotes is literal text; no substitution, no finding |
| `r10-t11-nested-guard-inner` | R10-T11 | 1 at the line, `capture` | `n=$(echo "$(grep -c a f \|\| true) $(grep -c b g)")` — the second inner substitution is unguarded; the outer-only scan sees the first guard and clears it |
| `r10-t7-zsh-fence-positional` | R10-T7 | 1 at the line, `positional` | a ` ```zsh ` fence in a `SKILL.md` holding `t=$1` — shape 6 must scan `zsh` fences |

R10-T21 (the unclosed-fence label) is a message-text change, not a lexing behaviour, and is
not scored here. R10-T12 (`GUARD` accepting `|| echo`) and R10-T5 (the fix hint) are regex and
prose edits that apply to either candidate and are not scored here.

## Candidates

- **L-B** — `candidates/B/check-guards`: the shipped file with `strip_comment`, `_quote_spans`
  and `substitutions()` replaced by one state machine, `lex(line)`, that walks the line once and
  records for each index whether it is inside single quotes, inside double quotes, escaped by a
  preceding backslash, or at what `$( )` depth. `substitutions()` returns every span, nested
  included, innermost last. `SHELL_INFO` gains `zsh`. Nothing else changes: same regexes, same
  `analyse()`, same `collect()`.
- **L-C** — `candidates/C/check-guards`: the shipped fence scanner kept; for each fenced
  block, `shellcheck -s bash -f json1` is run and its findings are mapped onto the six shapes
  where a ShellCheck code exists for the shape (SC2312 for a masked return in a substitution
  covers shape 1's territory; no code exists for shapes 2, 5 or 6, which keep the shipped
  regexes). Measured before this was written: ShellCheck 0.11 has no token or AST output, so
  this is findings-as-detector, the round-3 spike's candidate B shape.

## Pre-registered bar and predictions

**Bar, either candidate**: corpus 117/117 (114 + 3) including all three new cases; integrity
at or above the baseline's harness number; curated mutations at or above the baseline's; zero
unwaived survivors on `--generated` after argued waivers, with stale waivers expected because
the mutant keys change with the source.

**Predictions, written now**:

1. **Baseline A** fails exactly the three new cases (114/117), by construction.
2. **L-B** reaches 117/117 on the corpus at the first or second attempt. Its `--generated`
   sweep regrows survivors by 10–20, in the new `lex()` function, and every one is closable by
   a corpus case or an argued waiver — the pattern shapes 4, 5 and 6 each showed.
3. **L-C** fails the must-not-fire half of the corpus: SC2312 fires on `n=$(count foo f) || exit 2`
   and on `[ -e "$x" ] || continue`, the exact false positives the round-3 spike recorded (10 of
   15 clean files), and no mapping of ShellCheck codes reaches 117/117 without re-implementing
   the policy layer in Python — which is L-B by another route.
4. **Decision rule**: if prediction 2 holds and 3 holds, L-B. If L-B cannot reach 117/117
   without encoding a behaviour the corpus pins that no reasonable lexer produces, name the
   case and stop — the corpus is the defect. If L-C reaches the bar, the spike's 2026-09-18
   verdict was wrong and this document says so.

## Results

Run 2026-09-28 from `thoughts/spike/harness/` (cwd
`/Users/scraig/conductor/workspaces/workbench/ankara/docs/plans/2026-09-28-guard_lexer_and_pr_identity/thoughts/spike/harness`,
`pwd -P` the same), one `test-guards` at a time, each backgrounded. Full outputs in
`thoughts/spike/results-*.txt`.

### Baseline A — the shipped checker on the 117-case harness

```text
== corpus ==
  114/117 (58 of 60 must-fire caught, 1 false positives)
  ✗ MISSED  r10-t11-nested-guard-inner (want [(4, 'capture')], got [])
  ✗ MISSED  r10-t7-zsh-fence-positional (want [(4, 'positional')], got [])
  ✗ FALSE+  r10-t10-escaped-dollar-paren (got [(4, 'capture')])
test-guards: corpus 114/117, integrity 13/15, mutations 19/25 — FAIL
```

**Prediction 1 held exactly**: the three new cases and nothing else. Integrity 13/15 and
mutations 19/25 are the harness offsets named above (claims and anchors that refer to the
plugin tree's layout); the same numbers came out of an earlier run on the unmodified copy.
These are the comparison point for both candidates.

### L-B — one state machine, first attempt

```text
== corpus ==
  116/117 (60 of 60 must-fire caught, 1 false positives)
  ✗ FALSE+  r4-ok-paren-pattern (got [(2, 'capture')])
test-guards: corpus 116/117, integrity 13/15, mutations 16/25 — FAIL
```

All three new cases passed. The one false positive was a real lexer bug: on
`n=$(grep -c ")" f.txt || true)` the machine closed the substitution at the `)` inside the
double-quoted pattern, so the span ended at `grep -c "` and the guard fell outside it. The shell
rule is that `)` inside double quotes is literal. One-line fix: the close-paren branch gates on
`not dq`. Recorded here because it is exactly the class of disagreement the rewrite exists to
end, found by the corpus on the first run — the round-4 case `r4-ok-paren-pattern` was written
for the old tracker's mirror of this bug.

### L-B — second attempt, after the fix

```text
== corpus ==
  117/117 (60 of 60 must-fire caught, 0 false positives)
== scan integrity (outside the corpus) ==
== mutation survivability ==
  ?? break the quote-aware comment strip: anchor not found — MUTATION DID NOT APPLY
  ?? stop scanning sh/shell fences: anchor not found — MUTATION DID NOT APPLY
  ?? make the span finder quote-blind again: anchor not found — MUTATION DID NOT APPLY
  16/25 mutations caught
test-guards: corpus 117/117, integrity 13/15, mutations 16/25 — FAIL
```

**Corpus bar met.** Integrity equals the baseline's harness number. Of the 25 curated
mutations, three anchor on text that no longer exists (`strip_comment`'s loop, the
`SHELL_INFO` literal, `substitutions()`'s quote branch); the 22 that applied caught 16, and the
six survivors are the same six layout-offset survivors the baseline shows. The `FAIL` verdict
is the harness's `caught == 25` rule reading three non-applying mutations as misses. **For the
real implementation, those three curated mutations need equivalents written against `lex()`**
— a mutation that no longer applies is a mutation that no longer protects anything.

### L-C — ShellCheck SC2312 as the shape-1 detector

```text
== corpus ==
  89/117 (32 of 60 must-fire caught, 0 false positives)
test-guards: corpus 89/117, integrity 10/15, mutations 16/25 — FAIL
```

28 must-fire cases missed, including `s1-lastline`, `s1-backtick`, `s1-spaced`, `s1-longflag`,
`s1-guard-on-later`, `s1-guard-on-earlier`. **Prediction 3 held on the verdict and was wrong
on the mechanism**: the failure is on the must-fire half, not must-not-fire. SC2312 does not
flag a bare assignment `n=$(grep -c foo f)` — ShellCheck's position, recorded as Q8-5 in the
parent plan, is that a bare assignment does not mask the status. Shape 1's rule is "captured
and the status never tested", which is a dataflow property ShellCheck declines to judge. So
L-C cannot reach the bar by mapping codes; it would need the lookahead and the capture scan
re-implemented in Python, which is L-B with an extra process per fence.

### L-B — generated mutation sweep

```text
== generated mutation sweep ==
  killed   338/425
  waived   38 (equivalent mutants, reasons in fixtures/mutation-waivers.json)
generated: 338/425 killed (79%), 38 waived, 49 survived
❌ 13 waiver(s) match no generated mutant.
❌ 49 unwaived survivor(s).
❌ ratchet: killed fell from 344 to 338.
```

The mutant population grew from 395 to 425 because `lex()` adds nodes. Of the 51 shipped
waivers, 38 still match and 13 went stale: their keys named statements in the three replaced
functions. The 49 unwaived survivors, grouped by enclosing function from
`thoughts/spike/harness/fixtures/mutation-survivors.txt`:

| Function | Survivors | Reading |
| -------- | --------- | ------- |
| `collect` | 13 | unchanged code — the exit-2 and node_modules branches the shipped tree waives; stale-key artefacts of the harness copy, not new survivors |
| `main` | 9 | unchanged code, same class |
| `<module>` | 1 | `sys.exit(main(...))` int mutation, same class |
| `lex` | 20 | mostly `d + 1` / `int 1-1` on the **`depth` tuple field, which nothing reads** (`strip_comment` reads `escd`, `_quote_spans` reads `c[0]`/`c[1]`; `depth` is dead) — equivalent mutants by construction; plus `dq = False` on `$(` open (`del Assign`) and `i += 2` (`int 2-1`), which are corpus gaps |
| `_quote_spans` | 5 | `c[0] or c[1]` → `and`, and `int 0±1`/`1±1` on the indices — no corpus case has a `;` inside a *single-quoted* string in a shape-4 chain, so `statements()` never distinguishes the two flags |
| `strip_comment` | 1 | docstring deletion |

So: 23 are the shipped tree's own waived class re-surfacing under new keys, and 26 are in the
new code. Of those 26, roughly 20 vanish by deleting the unread `depth` field from the tuple
(dead state is what an equivalent mutant is), and the rest need two or three corpus cases: a
double-quoted string spanning a `$(` boundary, a `;` inside single quotes in a chained
publish line, and a backtick opened inside double quotes.

**Prediction 2, read honestly**: the corpus half held on the second attempt; the survivor
half held *in kind* — every survivor is closable by a corpus case, a waiver, or removal of dead
state — but the count was 26 in the new code against a predicted 10–20. The excess is the
`depth` field: I recorded it "for completeness" and the sweep priced the completeness at
twenty mutants. The implementation should carry only what a consumer reads.

## Verdict

**L-B.** Decision rule line 4 applied: prediction 2 held on the bar (117/117, integrity at
baseline, all three held findings' cases passing) and on closability; prediction 3 held on the
verdict (L-C at 89/117) with the mechanism corrected — the miss is on must-fire, because
ShellCheck will not judge a bare assignment, which is Q8-5 verbatim. L-C is not "L-B by another
route"; it is short of the bar by 28 cases with no mapping that closes them.

**What the implementation inherits from this bullet**:

- `candidates/B/check-guards` is the seed, with the `not dq` fix on the close-paren branch and
  the docstring rule that a `)` inside double quotes is literal.
- Drop the `depth` field from `ctx`; carry `(in_single, in_double, escaped)`.
- Replace the three curated mutations that no longer apply with equivalents against `lex()`:
  break the backslash handling, break single-quote suppression of `$(`, break the
  save-and-restore of `dq` across a substitution.
- Corpus cases for the three real gaps above, written RED first.
- Rewrite the 13 stale waivers against the new keys, or delete the ones whose statements are
  gone; expect the ratchet to be re-based, not raised, on the first landing.
- R10-T12 (`GUARD` and `|| echo`), R10-T5 (the fix hint), and R10-T21 (the fence label) are
  unchanged regex and text edits on top of this, not part of the lexer.
