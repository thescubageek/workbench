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
