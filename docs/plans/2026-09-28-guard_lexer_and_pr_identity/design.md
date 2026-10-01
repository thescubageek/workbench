---
project: guard_lexer_and_pr_identity
ticket: null
created: 2026-09-28
created_timestamp: 2026-09-28T20:05:58Z
status: approved
last_updated: 2026-09-28
designer: scraig
git_commit: 41a7a3a
git_branch: adversarial-loop-skill-research
repository: thescubageek/workbench
tags: [design, architecture, guard_lexer_and_pr_identity]
depends_on: research.md
design_approach: One lexer, one resolver — retire two classes the review loop kept re-finding
---

# Design: guard_lexer_and_pr_identity

**Created**: 2026-09-28 20:05 UTC
**Designer**: scraig
**Ticket**: N/A

<!-- Status lives in frontmatter `status:` only. Do not restate it here: it is the field
     /wb:create_tasks and forge gate on, it changes, and a second copy goes stale the moment
     the design is approved. `created` and `ticket` are repeated above because they never
     change after creation. -->

## Problem Statement

The `adversarial_loop` plan's thrash breaker tripped Blocking after round 10: 29 of 31 findings
sat in the previous round's fix surface, and two were mirror images of round-9 fixes. Both
mirror pairs live in the same two components, and each has been patched in four or more rounds
without the class closing.

**The lexer.** `plugin/scripts/check-guards` decides "is this character inside quotes" in three
separate hand-written trackers — `strip_comment`, `_quote_spans` and `substitutions()` — none
of which handles a backslash escape, and the third of which records only the outermost `$( )`
span. R9-T15 taught one tracker about double quotes; the other two did not learn, and R10-T10
was the result. Four of the six held lexer findings (R10-T7, T10, T11, T21) are consequences of
three definitions where one belongs.

**PR identity.** `adversarial-review` decides which commit a PR target refers to by comparing
its `headRefName` to `git branch --show-current`, in two independent copies (Step 1 and Step
2). R9-T2 and R9-T26 rewrote that comparison so a PR on its own checkout reviews local
commits; R10-T3 is the same comparison accepting a fork PR whose branch happens to share the
name, and reviewing the maintainer's commits under the contributor's PR number. R10-T4 is the
same comparison trusting `origin/<head>` at whatever the last fetch was.

**Why now**: 3.0.0 ships on this branch, and PD5-2 chose fewest defects over smallest cut. The
breaker's own rule says a loop cannot fix a design defect by construction; it keeps finding the
symptoms. Ten round-10 tasks are held behind this design.

**If we do not solve it**: round 11 finds the fifth quoting case and the third identity case,
and the loop's introduced-rate stays where round 10 measured it.

### Success Metrics

- `check-guards` has exactly one definition of quoting context, read by every consumer; the
  three held lexing findings' corpus cases pass and every prior case still passes (117/117 on
  the harness that decided the lexer).
- A PR target is resolved once, by commit: a same-name fork PR is refused by name, a PR ahead
  of the last fetch is reviewed at its real head, and a PR on its own checkout reviews local
  `HEAD` only when `HEAD` descends from the PR's head.
- The generated mutation sweep reports zero unwaived survivors on the shipped tree, and runs
  in CI.
- No new dependency: the lexer imports only the Python standard library.

## Design Approach

Two independent replacements, each decided by a pre-registered tracer bullet and each retiring
a class rather than an instance.

**One lexer.** `check-guards` gains a single function that walks a shell line once and records,
per character, whether it is inside single quotes, inside double quotes, or escaped, and emits
every `$( )` and backtick span, nested included. `strip_comment`, `_quote_spans`,
`substitutions()` and `statements()` all read that one pass. `zsh` joins the set of fence info
strings scanned as shell. Nothing about the six detector shapes changes; they consume the same
spans and the same comment-stripped line they always did, now from one source.

**One resolver.** `adversarial-review` gains a single identity step, run before Step 1's range
and Step 2's `REVIEW.md` base, that reads the PR's `headRefOid`, `baseRefName` and
`isCrossRepository` from `gh` and produces one answer both steps use: the commit under review
and the base to compare against. "The PR's own checkout" means `HEAD` descends from
`headRefOid`; otherwise the resolver fetches `refs/pull/<N>/head` into a remote-tracking ref,
says so, and reviews that. A cross-repository PR whose branch name matches the checkout is
refused by name. Branch and path targets keep their current spellings, fed through the same
step.

### Why This Approach

- **The breaker's evidence points at definitions, not lines.** Three quote trackers disagreeing
  and two name comparisons drifting are the same shape: a fact stated in more than one place.
  Both replacements reduce the count to one. The house rule for shipped prose is the same —
  one authority, linked, because copies drift (`plugin/docs/reference/README.md`).
- **Both were decided by measurement.** The lexer bullet scored three candidates on a
  117-case corpus and a 425-mutant sweep: the shipped checker 114/117, the single state machine
  117/117, ShellCheck-as-detector 89/117. The identity bullet reproduced R10-T3's same-name fork
  case and showed the name test proceeding where the commit test refuses, then showed the fetch
  landing a remote-tracking ref at `headRefOid` on a fake origin and on GitHub.
- **It follows the round-3 precedent.** The last time `check-guards` tripped the breaker, a
  pre-registered spike chose rebuild over a fourth patch, and the rebuild retired six findings
  at once (`docs/plans/2026-09-17-adversarial_loop/design.md` → check-guards rebuilt on
  candidate C). This design reuses that method and that acceptance apparatus.
- **It respects the skill's own limits.** The resolver writes exactly one remote-tracking ref
  and touches no worktree, which stays on the right side of "checking a target out is a state
  change nobody asked for" (`adversarial-loop/SKILL.md:125`); and it `return`s, never `exit`s
  (`adversarial-review/SKILL.md:160-166`).

## Technical Decisions

### Architecture

- **`check-guards` lexes each line with one state machine, `lex(line)`, and every consumer
  reads it.** It returns a per-character context of `(in_single, in_double, escaped)` and a
  list of every substitution span, nested included, appended as each closes. `strip_comment`
  cuts at a `#` that is outside quotes and unescaped; `_quote_spans` is the disjunction of the
  two quote flags; `substitutions()` returns the span list; `statements()` splits on `;` using
  the same flags.
  - Rationale: the held findings are disagreements between trackers (R9-T15 → R10-T10), a
    missing escape rule (R10-T10), and an outermost-only span list (R10-T11); one pass removes
    the seam all three sit on. The tracer bullet's first attempt found one real bug in it — a
    `)` inside double quotes closing the substitution — and the corpus caught it on the first
    run, which is the acceptance apparatus doing what it was built for.
  - Trade-off: about 90 lines rewritten; the three curated mutations whose anchors were in the
    replaced code must be rewritten against `lex()` or they protect nothing; 13 generated-sweep
    waivers go stale and are rewritten or deleted; the ratchet is re-based, not raised, on the
    first landing.
  - Pattern reference: `plugin/scripts/check-guards:150-194` (the function being replaced);
    `thoughts/spike/candidates/B/check-guards` (the seed, with the close-paren fix).

- **The context tuple carries only what a consumer reads.** `(in_single, in_double, escaped)`;
  no substitution depth, no token kinds.
  - Rationale: the bullet's sweep priced an unread `depth` field at about twenty equivalent
    mutants. Dead state is what an equivalent mutant is, and each one needs an argued waiver.
  - Trade-off: a future shape that needs depth adds it then, with its consumer.

- **The shell rules the lexer encodes are the shell's, stated in its docstring.** A backslash
  escapes the next character outside single quotes; single quotes are literal until the next
  single quote; double quotes toggle; `$( )` and backticks open a fresh quoting context and
  restore the outer one on close; single quotes suppress a substitution and double quotes do
  not; a `)` inside double quotes closes nothing; an unclosed `$( )` runs to end of line; an
  unclosed backtick is a stray and yields no span.
  - Rationale: every one of those is a corpus case or a held finding; stating them in one place
    is what lets the next review round check the lexer against a rule instead of against a
    previous fix.
  - Trade-off: the docstring is normative and must be edited with the code.

- **`zsh` is a shell fence.** `SHELL_INFO` gains `zsh`; prose stays unscanned.
  - Rationale: the Bash tool runs fences under zsh (`.claude/wb/knowledge.md`), so a `zsh`
    fence in a `SKILL.md` is executed by the same harness that substitutes `$1` (R10-T7).
  - Trade-off: none found; no shipped file carries a `zsh` fence today.

- **`adversarial-review` resolves a target's identity once, in one function, before any
  range or base is computed.** The function binds: the commit under review, the base ref, and
  a one-line provenance statement the report carries (`origin/pr/57 = 8460be3, fetched` or
  `HEAD, 2 commits ahead of headRefOid 3b4e04b`). Step 1 derives its range from those two
  refs; Step 2 derives its `REVIEW.md` merge-base from the same two refs. Neither step
  re-reads `gh`.
  - Rationale: the mirror-image pair R9-T2/R9-T26 → R10-T3 came from two copies of one test.
    A single function is the only shape in which they cannot drift.
  - Trade-off: the resolver is the one place the review can fail before it starts; every
    failure there `return`s with a named reason and the report says the review did not run.
  - Pattern reference: `adversarial-review/SKILL.md:105-149` (Step 1's `resolve_range`, which
    becomes the consumer of the resolver rather than the resolver) and `:209-240` (Step 2's
    duplicate, which is removed).

- **Where the resolver lives: a fenced block in `SKILL.md`, not a shipped script.**
  - Rationale: it needs `target`, which is bound in prose and re-stated per block (the
    `$1` rule); a script would need the argument passed and would re-introduce the positional
    surface shape 6 now forbids in fences and the harness substitutes in prose. Every other
    resolution in the skill is a fenced block, and `check-guards` scans fences.
  - Trade-off: one more block a session must run as written. The four `gh` fields are read in
    one call, so the block is no longer than Step 1's today.

- **The resolved decisions below are architecture too**, landed by `/wb:resolve_questions`
  before this document was written and kept in their own subsection so the audit trail reads
  in the order the decisions were made.

### Data Model

- **The lexer's output**: `ctx`, a list of `(in_single: bool, in_double: bool, escaped: bool)`
  with one entry per character of the line; and `spans`, a list of `(inner_start, close_index)`
  in close order, so an inner substitution precedes the outer one that contains it. A span's
  `close_index` is `len(line)` for an unclosed `$( )`.
- **The resolver's output**, three shell variables every later step reads and none rebinds:
  `review_head` (a ref that resolves to a commit — `HEAD`, `origin/pr/<N>`, `origin/<branch>`),
  `review_base` (`origin/<baseRefName>`), and `review_provenance` (one line for the report).
  The range is `$review_base...$review_head`; the `REVIEW.md` base is
  `git merge-base "$review_head" "$review_base"`.
- **The identity facts read from `gh`**, in one call: `headRefOid`, `headRefName`,
  `baseRefName`, `isCrossRepository`. `headRepository` is not read; `isCrossRepository` is the
  one bit the decision needs.
- **The fetch's only write**: `refs/remotes/origin/pr/<N>`. Never a local branch, never a
  worktree change, never `refs/pull/<N>/merge`.

### Integration Points

- **`test-guards` and its fixtures** are the acceptance apparatus: the 114-case corpus gains
  the three cases the bullet wrote and two or three more for the sweep's real gaps; the 25
  curated mutations lose three anchors and gain three equivalents against `lex()`; the waiver
  file loses its stale keys; the ratchet is re-based. `test-guards <path>` scored the candidate
  without touching the shipped file and is how the implementation is verified before it lands.
- **`plugin/scripts/check`** is unchanged: seven gates, ~20 seconds. **`.github/workflows/checks.yml`**
  gains a job for `test-guards --generated` (Q4).
- **`adversarial-loop`** Phase 0 already binds `target` and passes `--plan=`; its prose rule
  that the PR phases do not run when `target` is not the current checkout
  (`adversarial-loop/SKILL.md:125`) reads the resolver's `review_provenance` instead of a name
  comparison. Phase 2's push block and `reply-to-claude`'s PR binding are round-10 cluster-3
  tasks (R10-T25, R10-T9) and are out of scope here; they consume the same resolver once it
  exists.
- **The stop table** in `adversarial-loop` gains one row: the fetch, named, with what it may
  write. It is not a confirmation gate — it is disclosed, not asked — because it is the same
  class of write as any `git fetch`.
- **The six held lexer findings map onto this design as follows**: R10-T7, T10, T11 are closed
  by the lexer and pinned by the bullet's three corpus cases; R10-T21 (the unclosed-fence
  label) is a message change on the fence scanner, which this design does not alter; R10-T12
  (`GUARD` and `|| echo`) and R10-T5 (the fix hint) are regex and text edits with no lexing
  content. The four held identity findings: R10-T3, T4 are closed by the resolver; R10-T13
  (the dead `filter=$?`) and R10-T29 (`.git` in the blast-radius search) are Step 3 changes
  that ride with the same skill edit.

### Resolved Decisions

- **The `check-guards` lexer stays stdlib-only.** `import os, re, sys` today; a rebuilt lexer
  adds nothing outside the Python standard library (`shlex` is available and unused; `bashlex`
  is not installed).
  - Rationale: the parent plan's PD2 made adding `shellcheck` and `python3` to what `check`
    requires a major-version change; a third-party parser is the same class of change. The
    tracer bullet's winning candidate needs none.
  - Trade-off: `$( )` nesting and backslash escapes are hand-written rather than borrowed.
  - Source: research.md Q1 · Decided 2026-09-28

- **`adversarial-review` may fetch a PR's head ref, as a named and disclosed step.** When a PR
  target's head is not the current checkout (a cross-repository PR, or a same-repository PR
  whose head is not an ancestor of `HEAD`), the resolver runs
  `git fetch origin "refs/pull/$N/head:refs/remotes/origin/pr/$N"`, reports the ref it wrote,
  and reviews `origin/pr/$N`. Nothing else is written; no checkout, no branch, no worktree
  change.
  - Rationale: the skill's rule is that checking a target out is a state change nobody asked
    for; a remote-tracking ref is the same class of write any `git fetch` performs and is the
    only way the loop reviews a PR the user is not on, which the parent plan's Q4 requires.
    Measured in the identity tracer bullet: one ref written, worktree and branch untouched, on
    a fake origin and on GitHub.
  - Trade-off: a test origin must carry pull refs explicitly — `git clone --bare` does not copy
    them.
  - Source: research.md Q2 · thoughts/2026-09-28-lexer-and-pr-identity.md (I-A) · Decided 2026-09-28

- **A PR target's head is its commit, not its branch name, and "own checkout" means descent.**
  The resolver reads `headRefOid` and `isCrossRepository` from `gh pr view`. If
  `git merge-base --is-ancestor "$headRefOid" HEAD` holds and the PR is not cross-repository,
  the reviewed range ends at local `HEAD` and the report discloses the commits ahead of the
  PR's head. Otherwise the resolver refuses by name and offers the fetch above. Steps 1 and 2
  resolve once, in one function Step 2 reads from.
  - Rationale: the mirror-image pair R9-T2/R9-T26 → R10-T3 came from two copies of a
    branch-name comparison; a same-name fork PR made it review the maintainer's own commits
    under the PR's number (reproduced in the identity tracer bullet). Descent by OID is the
    test the name comparison was standing in for.
  - Trade-off: a same-repository PR whose head moved on another machine reviews the fetched
    OID, not `origin/<head>` at the last fetch — R10-T4 closed by construction, unmeasured.
  - Source: research.md Q3 · thoughts/2026-09-28-lexer-and-pr-identity.md (I-A) · Decided 2026-09-28

- **The generated mutation sweep joins CI, not `check`.** `.github/workflows/checks.yml` gains a
  job that runs `./plugin/scripts/test-guards --generated` on every pull request; `check` keeps
  its seven gates and its ~20-second runtime. The README's "~80 seconds" figure is corrected to
  what the sweep measures (about 4 minutes on this machine, 12 once).
  - Rationale: after R9-T19 the sweep is the only gate that fails on an unwaived survivor.
    Left manual, that invariant depends on memory, and this plan measured the result — shape 4
    regrew 16 survivors while the kill-count ratchet stayed green. CI runs on every PR anyway;
    the sweep is deterministic (in-process AST mutants under an alarm) and its ratchet file is
    already committed, so CI needs no new state.
  - Trade-off: a slower CI run; a survivor found only in CI is fixed after the push, not before.
  - Source: research.md Q4 · Decided 2026-09-28

## Scope Definition

### In Scope

- Replacing `check-guards`' three quote trackers with one lexer; adding `zsh` to the shell
  fence set; the corpus cases, curated-mutation equivalents, waiver rewrites and ratchet re-base
  that land with it.
- A single identity resolver in `adversarial-review` feeding Steps 1 and 2, with the fetch step
  and its disclosure; removal of Step 2's duplicate resolution; the stop-table row.
- The Step 3 changes that ride with the same skill edit: the dead `filter=$?` (R10-T13) and the
  `.git` exclusion (R10-T29).
- The three regex and text edits that are not lexing but sit in the same file: `GUARD` and
  `|| echo` (R10-T12), the shape-6 fix hint (R10-T5), the unclosed-fence label (R10-T21).
- A CI job for the generated sweep and the README runtime correction (Q4).
- Landing on `adversarial-loop-skill-research` before PR #25 merges, so 3.0.0 ships with it
  (the round-10 escalation decision, 2026-09-28).

### Out of Scope

- **The six detector shapes and what they flag.** This design changes what feeds them, not
  what they detect.
- **Round 10's cluster 3**: `adversarial-loop` publishing and ledger mechanics (R10-T2, T8,
  T16, T23, T25) and `reply-to-claude` (R10-T9, T24). Ordinary tasks, worked after this lands.
- **The eight standalone round-10 findings** (PHI scrub, prose `$1`, `check`'s `require`, the
  ratchet's message and unit coverage, READMEs, `implement_inline` BARRIER 2).
- **GitLab or any host without a `refs/pull/<N>/head`-style ref.** Out of scope by the parent
  plan; the resolver's fetch spelling is GitHub's.
- **A per-host or per-repository override of the fetch.** Not asked for; the stop table's row
  is the disclosure.

## Success Criteria

### Functional Requirements

- [ ] `check-guards` passes the 117-case corpus (the shipped 114 plus the three bullet cases)
      with zero false positives, and the three held lexing findings' cases are among them.
- [ ] `test-guards` reports the curated mutations all caught, with the three replaced anchors'
      equivalents present, and `--generated` reports zero unwaived survivors and no stale
      waivers.
- [ ] On PR #25's own checkout, `adversarial-review 25` resolves to `HEAD` and discloses the
      commits ahead of `headRefOid`; on a checkout that is not the PR's head, it fetches
      `refs/pull/25/head` and reviews `origin/pr/25`, naming the ref it wrote.
- [ ] Against the identity bullet's fixture (a same-name fork PR), the resolver refuses by
      name; against a stubbed `gh` returning a `headRefOid` not present locally, it fetches.
- [ ] Step 2's `REVIEW.md` base is derived from the resolver's refs; no second `gh` read of
      `headRefName` exists in the skill.
- [ ] `.github/workflows/checks.yml` runs `test-guards --generated` on every PR.

### Non-Functional Requirements

- [ ] **No new dependency**: `check-guards` imports only the standard library.
- [ ] **No worktree write**: the resolver's only write is one remote-tracking ref, and the
      report names it.
- [ ] **Local `check` stays at its current runtime**; the sweep's cost lands in CI only.
- [ ] **Every fenced block in the edited skill passes `check-guards`**: no bare `$1`, no
      `PIPESTATUS`, no unchained publish.
- [ ] **The lexer's rules are stated in one docstring**, and every rule has a corpus case.

## Risk Analysis

### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
| ---- | ------ | ---------- | ---------- |
| The lexer encodes a behaviour the corpus pins that the shell does not have | Med | Low | The bullet found one (the double-quoted `)`); the docstring states the shell rule per case, and the next review round checks the rule, not the previous fix |
| The sweep regrows more survivors than the bullet's 26 once curated-mutation equivalents land | Low | Med | Each is a corpus case or an argued waiver; the ratchet is re-based once, with provenance, not raised |
| The stale-waiver rewrite silently drops a waiver that still mattered | Med | Low | `ratchet_verdict` fails on a stale key, so a dropped waiver is loud; deletions are listed in the commit |
| `gh pr view --json` field names change | Low | Low | Four fields, read in one call, named in the resolver's diagnostic on failure |
| The fetch is refused by a repository policy or an offline environment | Low | Low | The resolver `return`s with the named reason; the report says the review did not run |
| A same-repository PR whose head moved elsewhere is reviewed at the fetched OID rather than the branch the user expects | Low | Low | `review_provenance` states which ref was reviewed and why, every time |

### Assumptions

Assumptions this design rests on, usually from research's knowledge gaps. This table is the
record — there is no external tracker.

| ID | Assumption | Validated? |
| -- | ---------- | ---------- |
| A1 | `git merge-base --is-ancestor <headRefOid> HEAD` is the right "own checkout" test on a repository where the PR head branch is checked out with local commits ahead of it. If false, a legitimate local-fix review is refused. | Validated 2026-10-01 — on PR #25 own checkout the resolver printed `identity: HEAD, 4 commit(s) ahead of headRefOid 149f233 (PR 25, own checkout)`, N equal to `git rev-list --count 149f233..HEAD`, no fetch ran. The PR head had moved from 3b4e04b since planning, so the plan's literal SHA and count were stale; the descendant case held. |
| A2 | The three curated-mutation equivalents written against `lex()` are as strong as the three they replace. If false, the curated suite protects less than before while reporting 25/25. | Pending — checked by planting each break in a scratch copy and watching the corpus fail, the round-4 discipline |
| A3 | The generated sweep is deterministic across machines, so a CI job and a local run agree. If false, CI fails on a survivor the author cannot reproduce. | Validated 2026-10-01 — first CI run (run 36813275478, commit c6451ff) reported `killed 378/421`, 43 waived, 0 survived, ratchet held at 378: the local re-based numbers, on a different machine. |

- **IDs are local and stable**: `A1`, `A2`, … in the order raised, never renumbered.
- **State the consequence.** An assumption worth a row is one where being wrong changes the
  design; if being wrong changes nothing, it is background, not an assumption.
- **Validating is an edit, not a new record.** `/wb:resolve_questions` flips the cell to
  `Validated YYYY-MM-DD`, or to `Invalid — [note]` with what the answer forces to change.
  Rows are never deleted.

## Rejected Alternatives

Carried across from `thoughts/2026-09-28-lexer-and-pr-identity.md` and the two tracer bullets,
where each was argued or measured rather than invented here.

### Option: L-A — fix the three trackers in place

- **Approach**: add backslash handling to each tracker, make `substitutions()` return every
  span, add `zsh`, relabel the unclosed-fence finding.
- **Rejected because**: it keeps three definitions of "inside quotes". The breaker fired on
  exactly that: R9-T15 changed one tracker's view of double quotes and produced R10-T10 because
  the other two never learned about backslashes. A fourth pass is the third instance, not the
  class.
- **Trade-offs**: the smallest diff; no new abstraction.

### Option: L-C — ShellCheck as the engine

- **Approach**: run ShellCheck over each fence and map its findings onto the shapes.
- **Rejected because**: measured at 89/117 on the harness. ShellCheck 0.11 has no token or AST
  output, and its SC2312 does not fire on a bare assignment, so shape 1's rule ("captured and
  the status never tested") cannot be expressed as a code mapping — Q8-5 verbatim. Reaching
  the bar means re-implementing the capture scan and the lookahead in Python: L-B plus a
  process per fence.
- **Trade-offs**: a real parser behind the findings, which nothing here can consume.

### Option: I-B — resolve by commit, refuse rather than fetch

- **Approach**: the same OID test; when the head is not present locally, stop with a named
  reason.
- **Rejected because**: the loop then stops at Phase 1 on every off-checkout target — a
  narrower loop reported as the same thing, which the parent plan's Q4 decision rejected.
- **Trade-offs**: no writes at all.

### Option: I-C — keep name matching, add a fork check

- **Approach**: leave Steps 1 and 2; refuse when `isCrossRepository` is true or the name
  matches but `headRefOid` is not an ancestor of `HEAD`.
- **Rejected because**: it keeps two independent resolutions that already drifted once, and
  still reviews `origin/<head>` at the last fetch (R10-T4 unfixed).
- **Trade-offs**: the smallest change.

## Pending Decisions

Design decisions that need stakeholder input before execution can start. This table is the
record — there is no external tracker.

| ID | Decision Needed | Blocks | State |
| -- | --------------- | ------ | ----- |
| — | none — every decision this design rests on was taken in `/wb:explore_design`, by the two tracer bullets, or by `/wb:resolve_questions` (Q1–Q4), and is recorded above | — | — |

- **IDs are local and stable**: `PD1`, `PD2`, … in the order raised, never renumbered.
- **Resolution goes in `State`, never in `Blocks`.**
- **A row needs a real blockee.** If nothing is blocked, it is a preference, not a pending
  decision — decide it here and record it under Technical Decisions.

## References

- Research: [research.md](research.md)
- Exploration: [thoughts/2026-09-28-lexer-and-pr-identity.md](thoughts/2026-09-28-lexer-and-pr-identity.md)
- Tracer bullets: [thoughts/2026-09-28-lexer-tracer-bullet.md](thoughts/2026-09-28-lexer-tracer-bullet.md),
  [thoughts/2026-09-28-identity-tracer-bullet.md](thoughts/2026-09-28-identity-tracer-bullet.md);
  harness, candidates and raw results under `thoughts/spike/`
- Origin: `docs/plans/2026-09-17-adversarial_loop/review-log.md` → *Breaker, after round 10*;
  the ten held tasks in `reviews/2026-09-28-round-10/tasks.md`
- Precedent: `docs/plans/2026-09-17-adversarial_loop/thoughts/2026-09-18-check-guards-implementation-probe.md`
- Tasks: [tasks.md](tasks.md)
