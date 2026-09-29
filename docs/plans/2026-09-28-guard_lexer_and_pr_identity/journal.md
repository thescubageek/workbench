# Session Journal: guard_lexer_and_pr_identity

Append-only, reverse-chronological — newest entry at the top. **No entries yet.**

**Entries open when work starts, not when it ends.** A session does not get to choose how it
ends: a token limit, a closed laptop, or a crashed harness runs no shutdown step. An entry
written only at completion would be silent in exactly those cases, and worse than silent — its
tail would still show the last *finished* phase, so the next session would read a confident,
stale record and never learn that work stopped mid-task. Opening on entry makes the default
residue of an abrupt kill correct: an open entry naming what was being attempted and what came
next.

An open entry beside uncommitted changes means an interrupted task. An open entry beside a
**clean** tree is ambiguous and the tree cannot resolve it: the session may have finished without
closing out, or be **blocked waiting on a human** — a design awaiting approval is exactly this,
and it is the correct residue rather than a fault — or still be running in another session, which
this repository cannot observe at all.

**So read the entry's `Next action` before concluding anything.** The working tree is the
authority on whether work is *in flight*; only the entry says what the work was and what it is
waiting for.

**A heading must end in a literal `(open)` or `(closed)`.** That suffix is what every reader
matches on — the session-start hook, `forge`, `daily-digest`, `resume_handoff`,
`create_handoff`. A heading ending any other way is invisible to all of them, and the failure
is silent: the next session is told "closed" over work that was interrupted.

Entries take these two shapes. **Keep the dates as the literal placeholder `YYYY-MM-DD`.** The
session-start hook finds the newest entry with `grep -E '^## '` and then discards headings whose
date is still a placeholder — so the placeholder is what stops these examples being read as a
real entry. The fence is for readability and is *not* the protection: the hook is not
fence-aware, and these headings still begin at column zero inside it. An example rewritten with
a realistic-looking date would be reported as an interrupted task in every plan generated from
this template, silently, from the moment of creation.

```text
## YYYY-MM-DD HH:MM — <task-id or short label> (open)

- **Task/phase**: <ID and one-line description>
- **Next action**: <the literal next thing to do, specific enough to act on cold>
- **Started at**: <commit hash>

## YYYY-MM-DD HH:MM — <task-id or short label> (closed)

- **Task/phase**: <ID and one-line description>
- **Landed**: <what actually changed>
- **Commits**: <range or hashes>
- **Learned**: <anything that changes how the remaining work should proceed — omit if nothing>
- **Blocked by**: <anything blocking — omit if nothing>
```

<!-- Real entries begin below this line, newest first. -->

## 2026-09-29 02:34 — P1-T2 (closed)

- **Task/phase**: P1-T2 — close the generated mutation sweep after the lexer rewrite.
- **Landed**: sweep reconciled against `lex()`. 13 stale waivers (the exact prediction) —
  8 deleted, 5 re-keyed. 6 corpus cases added (120 to 126), each the sole killer of a named
  survivor. 3 waivers added, then 2 of them deleted again (see below) and a 3rd deleted by the
  coordinator, leaving 43. Ratchet re-based once, by the harness itself, 344/395 to 377/420.
  Final: 377/420 killed, 43 waived, **0 survived**, 0 stale.
- **Commits**: this commit.
- **Learned**: three things, and the first is the important one.
  1. **An equivalence argument backed by a probe set is only as good as the probe set's
     variety.** Two waivers claimed `stack[0][1]` and `stack[-1][1]` were indistinguishable,
     on ten probes that all put `|| true` *inside* the substitution. With the guard **outside**,
     valid bash tells them apart — `n=$(`grep -c foo f`; echo z) || true` — and the mutant's
     end-of-line flush swallows the outside guard, so an unguarded capture reads as guarded.
     Both became corpus cases. A third waiver (`$( | del Continue`) fell to the same idea and
     was deleted too. The failure mode is not "wrong argument" but "probes that share a hidden
     assumption and so cannot fail" — the same shape as the knowledge file's "a probe that
     cannot fail is not evidence".
  2. **`redundant` and `stale` are different waiver states and only one is fatal.**
     `test-guards:451-457` partitions idle waivers: `stale` (the statement is gone) fails the
     run; `redundant` (the mutant lives and a corpus case now kills it) prints an informational
     line and does not. A waiver can therefore be harmless to the gate and still carry a false
     argument, which is what the deleted third one was.
  3. **`lex()` added 25 mutants, not the ~6 the bullet's arithmetic implied.** Its stack
     discipline — the tick/paren kinds, the `dq` save-restore — is state the old flat scanner
     did not have, so removing `depth` did not shrink the population as much as predicted.
- **Blocked by**: nothing. The run was interrupted once by a spend limit and resumed with its
  context intact; the failure was external, not a defect in the work.

## 2026-09-29 01:51 — P1-T1 (closed)

- **Task/phase**: P1-T1 — land `lex()` in `plugin/scripts/check-guards` and the six corpus
  cases that pin it; rewrite the three curated mutations whose anchors vanish.
- **Landed**: one `lex(line)` returning per-character `(in_single, in_double, escaped)` and
  every span in close order; `strip_comment`, `_quote_spans` and `substitutions()` are thin
  readers of it and `statements()` reads the same flags, so the four consumers cannot disagree.
  `depth` dropped everywhere; close-paren branch guarded by `not dq`; the eight shell rules in
  the docstring. `'zsh'` added to `SHELL_INFO`. Corpus 114 to 120. Three curated mutations
  re-anchored on `lex()`, total held at 25.
- **Commits**: this commit.
- **Learned**: two things worth carrying into P1-T2.
  1. **RED was 117/120, not the 114/120 the plan predicted.** Only the tracer bullet's three
     cases fail against the shipped checker; the three sweep-gap cases pass against the old
     trackers because they pin mutants of the *new* `lex()`, not defects of the old ones. The
     verifier reproduced 117/120 against `HEAD:plugin/scripts/check-guards` independently.
  2. **A2 held, and the check caught a real defect in the work itself.** Planting each
     rewritten mutation in a scratch copy scored 119/120 for all three. The first draft of
     `gen-sweep-dq-across-subst` put the guarded capture first and the planted `dq` mutant
     scored 120/120 — the case was inverted so the unguarded capture leads. Trusting the case
     without planting the mutant would have shipped a curated mutation protecting nothing.
- **Blocked by**: nothing.

## 2026-09-29 01:37 — create_tasks (closed)

- **Task/phase**: P0-T4 — execution plan for 2026-09-28-guard_lexer_and_pr_identity
- **Landed**: tasks.md — 3 phases, 14 implementation tasks (P1 ×5 lexer, P2 ×5 resolver,
  P3 ×4 CI and close-out), no Phase 0 tracer bullet because both bullets already ran; every
  task sized under 50 calls; the resolver block written into the plan and scanned clean by
  `check-guards`. Step 2 fan-out skipped: the research fan-out this session read the whole
  surface; three small facts read directly.
- **Commits**: this commit.
- **Learned**: nothing that changes the plan. Next: `/wb:implement` in a fresh session on
  Opus 4.8 / high, `--plugin-dir plugin`, Phase 1 first.

## 2026-09-29 01:22 — create_design (closed)

- **Task/phase**: P0-T3 — design for 2026-09-28-guard_lexer_and_pr_identity
- **Landed**: design.md written and approved (`status: approved`) — one lexer, one resolver;
  Mode A from the exploration record and both tracer bullets; Q1–Q4 carried in as Resolved
  Decisions; 4 rejected alternatives carried across; 0 pending decisions, 3 assumptions.
  Step 2 fan-out skipped: the research fan-out this session had already read the entire
  surface.
- **Commits**: 0177b1a (draft), this commit (approval).
- **Learned**: nothing that changes the remaining work. Next: `/wb:create_tasks`.

## 2026-09-29 00:51 — tracer bullets: lexer L-B, identity I-A (closed)

- **Task/phase**: the two bullets the breaker required before any fix.
- **Landed**: lexer — baseline 114/117, L-B 117/117 on the second attempt (one real bug found
  by the corpus: `)` inside double quotes), L-C 89/117; sweep 338/425 with 49 survivors, 26 in
  new code and mostly a dead `depth` field. Verdict L-B, recorded in the exploration document.
  Identity — name test proceeds, OID test refuses, pull-ref fetch works on a fake origin and on
  GitHub. Harness, candidates and raw results kept under `thoughts/spike/`.
- **Commits**: this commit.
- **Learned**: prediction 3 was right on verdict, wrong on mechanism (must-fire, not
  must-not-fire); prediction 2's survivor count was under by the cost of one unread field.
  Next: `/wb:resolve_questions` (Q1, Q4; Q2/Q3 already answered by I-A), then
  `/wb:create_design`.

## 2026-09-28 23:55 — explore_design (closed)

- **Task/phase**: between P0-T2 and P0-T3 — architecture exploration for both components.
- **Landed**: `thoughts/2026-09-28-lexer-and-pr-identity.md`. PR identity decided (I-A: resolve
  by `headRefOid`, fetch `refs/pull/<N>/head` as a named step, one resolver for Steps 1–2);
  answers research Q2 and Q3. Lexer narrowed to L-B vs L-C, L-A rejected; the user asked for a
  tracer bullet before choosing. Measured after the discussion: ShellCheck 0.11 has no token or
  AST output, so L-C can only be findings-as-detector — the spike's rejected candidate B.
- **Commits**: this commit.
- **Learned**: next is the two tracer bullets (pre-registrations are in the thoughts doc), then
  `/wb:resolve_questions` for Q1/Q4 and the lexer choice, then `/wb:create_design`.

## 2026-09-28 20:24 — create_research (closed)

- **Task/phase**: P0-T2 — research for 2026-09-28-guard_lexer_and_pr_identity
- **Landed**: research.md complete — 6 parallel agents (2 analyzers, test apparatus, pattern
  finder, locator, environment measurements); the lexer, its test apparatus, the target
  resolver, the spike precedent, and gh/git identity facts documented; 4 open questions.
- **Commits**: this commit.
- **Learned**: `refs/pull/25/head` exists on the remote at `headRefOid` and fetches cleanly,
  but the local refspec never brings it in; `shlex` is present, `bashlex` is not. Every held
  finding's mechanism reproduced by measurement. Next: `/wb:resolve_questions`, then the two
  tracer bullets, then `/wb:create_design`.
