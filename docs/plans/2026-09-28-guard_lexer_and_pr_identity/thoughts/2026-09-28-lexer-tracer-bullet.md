---
created: 2026-09-28
type: tracer-bullet
project: guard_lexer_and_pr_identity
topic: L-B (one stdlib state machine) versus L-C (ShellCheck findings as detector) for check-guards
status: pre-registered
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

*(filled in after the run — verbatim output, never paraphrased)*
