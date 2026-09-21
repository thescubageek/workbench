# Session Journal: adversarial_loop

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

## 2026-09-21 08:41 — R6-T9 (closed)

- **Task/phase**: Round 6 reopened at the user's direction with three tasks folded in from the
  checkpoint's held list. R6-T9 — R6-T4 left two `Phase ${phase}` interpolations behind, at
  `implement/SKILL.md:543` and `templates/modified-files-fragment.md:6`.
- **Landed**: both swapped to `${phaseLabel}`; the definition at `SKILL.md:459` now names all four
  consumers; `modified-files-fragment.md` gained its own substitution table so a reader who opens
  only that file (which is what Step 7 directs) can substitute for both plan kinds.
- **Commits**: the commit carrying this entry (`R6-T9: ...`)
- **Learned**: the worker's first draft copied the sibling tables verbatim, which would have put
  the literal `Phase ${phase}` into its **own new prose** — the acceptance grep would then have
  passed while matching the fix rather than the defect. It caught that itself and reworded to
  `Phase <n>`. The verifier checked specifically that this was not a contortion to dodge the grep
  and ruled it clearer here, since the file no longer has a `${phase}` variable to refer to.
  A criterion that can be satisfied by the fix's own text is a criterion worth re-reading.

## 2026-09-21 06:57 — R6-T8 (closed)

- **Task/phase**: R6-T8 — `validate_project` errors on every structural check of a round
  directory. Last task of round 6.
- **Landed**: an `isRound` predicate at `validation-rules.md:17-19` (a `reviews:` frontmatter key
  or a `reviews/<date>-round-N/` path), with three `if (!isRound)` guards fencing the phased-only
  regions and a `validateRoundStructure()` at `:262-283` giving the round its **own** contract —
  eight frontmatter keys, `reviews:` resolves (ERROR), `round:` agrees with the directory
  (WARNING), `## Tasks` present (ERROR). Checklist §9 and the report template follow.
- **Commits**: the commit carrying this entry (`R6-T8: ...`)
- **Learned**: the worker found **six more** unexempted assumptions than the finding named, one of
  which would have *thrown* and taken the rest of validation with it. The verifier traced the
  brace depth line by line rather than trusting reported line numbers, and confirmed every §3
  task-tracking check sits at depth 0 outside all guards — so a round still gets checkbox shape,
  ID shape, counter drift and status-vs-boxes. It also ran the predicate against the live round
  directory and its parent plan: true and false respectively, so real projects keep their
  validation. Set-difference of severity calls HEAD vs tree: zero removed, zero changed.
  **The worker's cited line numbers were pre-edit coordinates against post-edit locations** —
  corrected here and in the commit from the verifier's independent trace.

## 2026-09-21 06:46 — R6-T7 (closed)

- **Task/phase**: R6-T7 — `implement_inline` was never widened, so the documented alternative
  execution path refuses the shape `implement` now accepts and names `/wb:create_tasks` as the
  remedy, which is wrong for a round.
- **Landed**: carve-out at `implement_inline/SKILL.md:122-131` (byte-identical to `implement`'s),
  Step 2 companion with the corrected remedy at `:202-205`, Principle 6, Steps 1.1/1.2/1.3 and
  2.1 widened, plus `reference.md`'s resume path and both templates. Journal handling brought in
  line with R6-T6: parent-plan rule, `[blocked]` producer and consumer.
- **Commits**: the commit carrying this entry (`R6-T7: ...`)
- **Learned**: the worker found a defect nobody had listed — `implement_inline` is a **consumer**
  of journals `implement` writes, and its Step 2.4 said to "finish or supersede" an open entry. A
  `[blocked]` entry must be neither. R6-T6's commit one step earlier had therefore left a live
  cross-skill inconsistency, and this was the only task that could land it. The verifier ruled
  scope per file rather than blanket, and settled it on a fact the task text does not state:
  R6-T7 is the **only** task in either round that names `implement_inline`, while R6-T4/T5/T6 all
  scope themselves to `implement/`, so the round allocated the whole sibling here.
- **Blocked by**: nothing. Two notes for the checkpoint — the `[blocked]` *producer* block at
  `implement_inline/reference.md:26-36` is the one edit "follow-ups, not fixes" would arguably
  have routed to a follow-up (it is not remediation-specific), and `implement_inline` still has
  **no `git add -f` analogue** for staging plan files, so an inline run would silently drop
  `tasks.md` and `journal.md` from every commit. That is R6-T2's defect on the sibling, and no
  task in either round covers it.

## 2026-09-21 06:29 — R6-T6 (closed)

- **Task/phase**: R6-T6 — two journal-placement findings in one. (a) Step 6c's deliberately-open
  blocked entry trips `validate_project`'s stale-open-entry ERROR, with the cause misattributed.
  (b) A round's `journal.md` would land below the `docs/plans/*/` glob every reader inherits.
- **Landed**: (a) a `[blocked]` marker in the heading **label**, before the trailing suffix, so
  the five readers that anchor on `(open)`/`(closed)` are undisturbed; validator exemption at
  `validation-rules.md:146-147`, the rule and a marker section in `journal-entries.md:110-146`,
  in-place marking instructions in `implement/SKILL.md` Step 6c. (b) `journal-entries.md:48` —
  "**A remediation plan writes to its parent plan's `journal.md`, not to one of its own**",
  restated at `implement/SKILL.md:280`. No reader and no hook changed.
- **Commits**: the commit carrying this entry (`R6-T6: ...`)
- **Learned**: **the only FAIL of the round, and the diff could not have shown it.** The shipped
  grep exempted `[blocked] (open)` with a literal single space while the validator used `\s*`, so
  `[blocked]  (open)` passed the validator and was flagged by the document describing it — a
  false alarm on a correct file, in a file whose own rule is "match the reader, not the
  convention". Caught only by building fixtures and running both mechanisms side by side; the
  re-verify table now agrees 11/11 across whitespace, case and position variants, with the
  unmarked-stale control still firing in both. Coordinator applied the one-line fix rather than
  electing the `fable` rung, which 6c calls "an explicit election, never automatic".
- **Blocked by**: nothing. Two notes for the checkpoint: `daily-digest/sources.md:85-86` carries a
  comment that is now slightly incomplete (harmless — it reads only the newest entry), and the
  checklist's "unless its label carries `[blocked]`" is a summary looser than the validator's
  positional test, which is why it routes the reader to `journal-entries.md` for the mechanism.

## 2026-09-21 06:25 — R6-T5 (closed)

- **Task/phase**: R6-T5 — `implement/reference.md:55`'s resume path still requires `research.md`
  and `design.md` with no exemption, so `continue` on a round contradicts Step 1 of the same
  skill. The word "remediation" appeared nowhere in `reference.md`.
- **Landed**: exemption at `reference.md:55-58`, in Resume Logic step 4, reusing the recognition
  clause verbatim from `implement/SKILL.md:121` and `update_status/SKILL.md:74`. Three sites, one
  rule. `grep -c remediation` 0 → 1.
- **Commits**: the commit carrying this entry (`R6-T5: ...`)
- **Learned**: ran on **sonnet** rather than opus — a bounded mirror of a carve-out already
  written three times, with the wording fixed by precedent and no design latitude. Worker and
  verifier both finished in about a minute against ~4 for the opus tasks. This is the shape the
  Step 5 ladder means by "the deliberate downshift": a mechanical mirror of settled prose.
  Verifier independently swept all 192 lines and confirmed the file's only other mention of the
  two plan files (`:125`, migration guidance) is not on the resume path.

## 2026-09-21 06:15 — R6-T4 (closed)

- **Task/phase**: R6-T4 — Step 8 and both templates source manual-verification content from
  `design.md`, which Step 1 of the same skill declares absent for a remediation plan, and both
  interpolate `Phase ${phase}` for a plan that has no phase.
- **Landed**: all three surfaces **branched, not replaced**. Two new placeholders —
  `${phaseLabel}` (`Phase <n>` phased, `Round <N>` for a round) and `${closingLine}` — each with
  a substitution table in the templates and `${phaseLabel}` also stated in `SKILL.md` Step 8. A
  round's manual steps now come from each outstanding task's own acceptance criterion, citing
  `SKILL.md:196-199`. New rule: never wait on an empty checklist.
- **Commits**: the commit carrying this entry (`R6-T4: ...`)
- **Learned**: the verifier mechanically byte-compared the phased render at `HEAD` against the
  new one. `phase-completion-report.md` round-trips exactly; `manual-verification-request.md`
  differs by one line (the `from design.md` attribution moved into the substitution table), which
  is unavoidable given the criterion and loses nothing. The worker's "renders byte-identically"
  claim was an overstatement by that one line. **Tooling fact worth keeping**: the wrapped `diff`
  in this shell reported "Files are identical" for two files that demonstrably differ — the
  verifier caught it and re-ran under `cmp` and `/usr/bin/diff`. Do not trust the wrapped `diff`.
- **Blocked by**: nothing. `SKILL.md:522` (Step 9's Implementation Notes template) carries the
  same `Phase ${phase}` defect and **no remaining round-6 or round-7 task covers it** — recorded
  for the checkpoint rather than fixed, since it is outside every task's scope.

## 2026-09-21 06:07 — R6-T3 (closed)

- **Task/phase**: R6-T3 — shape-6 `(attestation)` findings have no mechanical criterion, so a
  TDD worker cannot write a failing test for them and the verifier FAILs a clean tree. The task
  deadlocks, lands on the blocking list, and `adversarial-loop`'s gate never clears.
- **Landed**: Step 4 diverts a no-criterion task to a new checkpoint **attestation list** at
  `implement/SKILL.md:252-264`; 6c never escalates one (`:380-384`); BARRIER 4 (`:426-429`) and
  Step 8.1 (`:437-440`) widened so a legitimately-`[ ]` attestation task does not hold the phase
  open; Step 8.4 (`:468-472`) lets a human's yes flip it and `:484-486` extends the existing
  "no run may tick it on its own authority" rule to cover it. Defensive lines in both agents.
- **Commits**: the commit carrying this entry (`R6-T3: ...`)
- **Learned**: termination was bought by widening the *barrier*, not by widening who may tick the
  box — the verifier traced attended, `--auto`, and both degraded paths and found all four
  terminate, with no path reaching `[x]` except a human at 8.4. Worst case (both Step 4 and the
  verifier miss the recognition) costs one wasted escalation and lands on the blocking list:
  bounded, not a hang. Three recognition sites now carry the same two keys — the verifier was
  keying on the `(attestation)` label alone until the verify pass caught it.
- **Blocked by**: nothing. Two producer-side gaps belong to round 7 and are recorded for the
  checkpoint — `adversarial-review/templates.md` never reserves a slot for the `(attestation)`
  label or for the name of who must look, so the label is an instruction to the producing model
  rather than a template literal.

## 2026-09-21 05:58 — R6-T2 (closed)

- **Task/phase**: R6-T2 — `implement` Step 6b stages plan files by path from a gitignored round
  directory, so `git add` exits 1 and the chained commit never runs. `git add -f` appears nowhere
  in `implement` or `adversarial-review`.
- **Landed**: `git add -f` rule and an executable fenced block at `implement/SKILL.md:335-347`;
  the hiding mechanism named at `:349`; `git add -f` in Step 6c's WIP-commit row at `:388`; and a
  `git ls-files --others --ignored --exclude-standard` probe beside `git status --short` in Step
  8.2. RED (`exit 1`) and GREEN (`exit 0`) both re-derived by the verifier against `HEAD`.
- **Commits**: the commit carrying this entry (`R6-T2: ...`)
- **Learned**: three measured facts, all of which shaped the fix. A *tracked* plan file is still
  refused by plain `git add`, so the `-f` rule had to be unconditional. `git restore` does **not**
  consult `.gitignore`, so Step 6c's restore guidance carried no defect and was left alone. And
  `git status --short` *does* report modifications to tracked files under an ignored path — it is
  blind only to *untracked* ones, which is why Step 8.2 needs both probes and not a replacement.
  The verifier caught the first draft overstating that last point; corrected before commit.
- **Blocked by**: nothing. Step 6a's discriminator was deliberately left reading `git status
  --short` alone — adjudicated a defensible boundary, since its second signal (`grep` for the
  checkbox) reads the disk and is immune to `.gitignore` under any condition.

## 2026-09-21 05:53 — R6-T1 (closed)

- **Task/phase**: R6-T1 — give `update_status` a remediation carve-out so `implement` Step 9
  stops routing a finished review round to `/wb:create_project`.
- **Landed**: carve-out at `update_status/SKILL.md:72`, directly under `⛔ BARRIER 1`, reusing
  `implement`'s recognition rule verbatim (`reviews:` key or `reviews/<date>-round-N/` path) and
  extending it across all seven steps. `reference/error-handling.md:27` now branches on
  `Otherwise,`, so the `Run /wb:create_project first` message is unreachable for a round
  directory. Verifier re-derived the RED against `HEAD` rather than trusting the worker: zero
  hits before, three after.
- **Commits**: the commit carrying this entry (`R6-T1: ...`)
- **Learned**: `update_status/templates/status-update-plan.md` and `templates/completion-summary.md`
  still hardcode research.md and design.md rows. The carve-out handles that in prose only, and no
  round-6 or round-7 task owns those two files — round 7 is entirely `adversarial-review`. Real
  unowned gap; recorded for the checkpoint.

## 2026-09-21 05:32 — PD5-1 and PD5-2 decided: disclose only, work the full backlog (closed)

- **Task/phase**: Phase 5 close-out. Resumed from `handoff-2026-09-21-04-43.md` (handoff and
  tree agreed at 84/85), then `/wb:resolve_questions` over the three open records.
- **Landed**: **PD5-1 → disclose only** — Step 3 states the range-to-fleet ratio and the report
  carries a shortfall line. **PD5-2 → work the full backlog** — all 20 round 6 and 7 tasks under
  `implement`; the handoff's recommended cut (revert R5-T7) is not taken, and R5-T7 is completed
  across `update_status`, `implement_inline` and `validate_project` instead. Q8-5 left partly
  resolved at the user's choice. Both decisions in `design.md` → Resolved Decisions; PD5-1's row
  reconciled and a PD5-2 row added in `tasks.md`.
- **Commits**: e9812a5 (resume entry); the decision edits are uncommitted at close — stage with
  `git add -f`.
- **Learned**: the user's stated priority is fewest defects and limitations, not the smallest
  cut. Round 8 is the accepted risk, gated by the breaker and explicit approval as before.
- **Blocked by**: nothing. **Next**: `/wb:implement docs/plans/2026-09-17-adversarial_loop/reviews/2026-09-21-round-6/`
  then round 7; a PD5-1 disclosure task still needs adding to the plan; P5-T5 last.

## 2026-09-21 04:43 — handoff written: the cut, not the backlog (closed)

- **Task/phase**: handoff into a fresh session to decide what ships as `3.0.0`.
- **Landed**: [handoff-2026-09-21-04-43.md](handoff-2026-09-21-04-43.md), framed as a scoping
  decision with a recommended cut — revert R5-T7, fix R7-T1, make Step 8 advisory — rather than
  as the 22-finding backlog rounds 6 and 7 produced.
- **Learned**:
  - **The framing is the whole point of this handoff.** Handing a fresh session 22 verified
    findings produces round 8; two rounds have now shown the fix-then-review loop is not
    converging on this surface. The handoff opens by saying so and asks for a decision.
  - **Three of the five ship-blockers trace to one commit.** R5-T7 widened `implement` alone —
    measured, `grep -c 'reviews:'` is 1 in `implement/SKILL.md` and **0** in both
    `implement_inline` and `validate_project`, while `update_status` Step 1 hard-requires the two
    files a round directory lacks. Reverting it is cheaper than completing it across four core
    stages, and the capability it adds has never worked: run 6 reached clean on the loop's
    *inline* branch with no plan directory at all.
  - **`design.md` Q8-1 predicted this and we shipped the cheap half** — *"`validate_project` must
    also tolerate a `tasks.md` with no `research.md`/`design.md` beside it; that is a real change,
    not free."* Recorded at the time as a live follow-up, then walked past on the way to a release.
- **Blocked by**: **PD5-1** and the cut are the user's calls. **P5-T5** waits behind them, because
  the three personal skills are the port's source material.

## 2026-09-21 03:51 — P5-T4 run 6: all eight items PASS, and the task is done (closed)

- **Task/phase**: P5-T4, closed. 84 of 85; only P5-T5 remains, and it needs the user.
- **Landed**: run 6's transcript and ledger promoted into `thoughts/`; P5-T4 ticked with
  run-by-run attribution; three manual-verification criteria met across Phases 3 and 5; the
  P1-T2 substitution assessed at the foot of the probe document, as Phase 5 required.
- **Learned**:
  - **The loop reached clean.** Round 1: four legs, 14 candidates → 5 deduped → 5 verified
    (3 CONFIRMED, 2 PLAUSIBLE) → 4 Valid and fixed. Round 2, scoped: zero findings. Gate
    satisfied. Six runs to get here, four of them blocked before measuring anything — twice on
    auto mode, once on a launch that dropped `--plugin-dir`, once on a one-file fixture that made
    the loop's own breaker unsatisfiable.
  - **The corrected `/verify` step worked, and `/verify` earned its place.** It asked instead of
    invoking, the user ran it, and it returned PASS having surfaced four things no static lens
    produced — including `require_admin` authorizing on any truthy value, so `is_admin='no'`
    passes. That is the argument for Q5's delegation, arriving the same day the delegation was
    found to be broken.
  - **The P1-T2 assessment has a real answer now, and it is uncomfortable.** The inline probe was
    adequate for what it claimed; the plan then mispriced what it deferred. P5-T4 was sized at
    "~18 calls" and was in fact the first execution of Steps 4–8 — which happened *after* `3.0.0`
    was cut, and found four shipped defects. A tracer bullet that cannot fire the actual weapon
    tells you the sights line up and nothing about whether the gun cycles. The cheap probe that
    would have caught it — a one-command headless `claude -p --plugin-dir … --allowedTools=Skill`
    — was available from Phase 1 and nobody reached for it, because "behavioural test" was
    imagined as a session a human sits through.
  - **Two things recorded rather than fixed.** Three of four legs ran the test suite against an
    explicit prohibition; that is a decision about whether the rule earns a carve-out, not a
    patch. And the breaker has still never been exercised as evidence — run 6's two-file fix
    surface sits inside the caveat's own range, and round 2's zero findings left the trend test
    correctly unevaluated.
  - **`grep --version` lies here.** It reports BSD grep while the diagnostics come from ugrep, so
    version-sniffing to pick safe flags gives the wrong answer — which is how the blast-radius
    guard got exercised for real, by an ad-hoc `--exclude-dir` that ugrep rejected.
- **Commits**: this one.
- **Blocked by**: **P5-T5** needs the user's go-ahead to delete the three personal skills.
  **PD5-1** remains open.

## 2026-09-21 03:02 — P5-T4 run 5: the loop works, and `/verify` cannot be called (closed)

- **Task/phase**: the `adversarial-loop`-without-`gh` half of P5-T4. Ran properly for the first
  time; six of seven report items PASS; **P5-T4 stays unchecked**.
- **Landed**: `adversarial-loop` Phase 1 step 4 no longer instructs an impossible action;
  `code-review-integration.md`'s invocability claim corrected and its ReportFindings hedge
  upgraded to two observations; `review-ledger.md` records the breaker's single-file blind spot.
- **Learned**:
  - **`/verify` cannot be invoked by the model.** `Skill('verify')` refuses with
    `disable-model-invocation`, and the refusal ends *"Do not replicate this skill's workflow by
    other means."* Phase 1 step 4 said "Invoke `/verify`" — unexecutable since the day it
    shipped. Worse, `code-review-integration.md:12` asserted all three built-ins were
    model-invocable, and the skill was written against that assertion. Measured all three:
    `code-review` loads, `security-review` loads, `verify` refuses. **This is design Q5's
    foundation** — *"fix-verification delegates to the built-in `/verify`; nothing stack-specific
    ships"* — resting on something false. The step now stops and asks the user, and an
    un-run `/verify` must be disclosed rather than papered over with the per-finding criteria,
    which answer a different question: they check each finding's scenario is closed, `/verify`
    checks the change still runs.
  - **The breaker cannot not fire on a single-file change.** `introduced_by` intersects a
    finding's path with the previous round's fix surface, so with one file every later finding is
    "introduced" by construction — including two the session verified byte-identical to base and
    therefore caused by nothing. Rate 0% → 100%, Blocking, at the minimum-N floor. The mechanical
    derivation is still right; path-intersection is just a poor proxy for causation when there
    are few paths. Recorded in `review-ledger.md` as *"the breaker cannot tell"*, not as evidence.
  - **This is also why clean was never reached**, so the honest answer to the item as written is
    that it did not pass — even though every step behaved correctly. A fixture of one file was my
    choice, and it made the loop's own gate unsatisfiable.
  - **Three earlier findings got their second confirmation**, on a different repository:
    `ReportFindings` unavailable inside the fork, the `launched (… running in the background)`
    result line, and `PIPESTATUS` empty under zsh. The integration doc hedged the first as "one
    observation, one build"; it is now two and the hedge is gone.
  - **The blast-radius guard fired for real, by accident.** An ad-hoc call passed
    `--exclude-dir=.git`, which this machine's `grep` (ugrep) rejects with exit 2 — and the guard
    printed `SEARCH FAILED (grep exit 2)` instead of reading the empty output as "no callers".
    That is the `search=$?` fix earning its place in the wild rather than in a fixture.
  - **The substantive outcome is the sort a review is for**: remediating the planted defect
    reverted the commit entirely, because the commit contained nothing but the defect. The branch
    now delivers nothing and nothing on it says so.
- **Commits**: this one.
- **Blocked by**: P5-T4 needs a rerun on a **multi-file** fixture with the corrected `/verify`
  step. **PD5-1** remains the user's decision.

## 2026-09-21 02:31 — P5-T4 run 4: blocked at launch, and the diagnosis was wrong (closed)

- **Task/phase**: the `adversarial-loop`-without-`gh` half of P5-T4. Never ran.
- **Landed**: nothing in `plugin/`. Two `knowledge.md` entries extended, the plan updated,
  P5-T5's rationale sharpened with a measurement. Fixture intact at `c6ff468`.
- **Learned**:
  - **The session reported that `--plugin-dir` "contributed nothing" and that `wb:` was being
    served by the stale installed 2.1.0. It was not.** With the flag, from `/tmp`, headless,
    `wb:adversarial-loop` loads from this checkout; `--add-dir` alongside changes nothing.
    Without the flag, the error is verbatim what the session saw, down to the parenthetical
    naming the bare alternative. **The flag was absent from that launch.** A launch failure that
    presents as a plugin defect, and the report was confident and specific about the wrong cause.
  - **What makes it checkable in one line**: `claude --plugin-dir <p> plugin details wb` printing
    the version and `Source: wb@inline`. Run 4 never ran it, and neither did my handoff ask for
    it — that omission is mine, and the next brief opens with it.
  - **Taking the agent at face value would have cost a day.** "The stale 2.1.0 serves the `wb:`
    namespace" implies a release blocker in the install story. It is not true, and five minutes
    of measurement said so.
  - **One real finding did come out of it, and it sharpens P5-T5.** With the 3.0.0 plugin loaded
    and enumerating, the *bare* name still resolves to the personal copy — 236 lines against the
    shipped 379. The prefix decides, deterministically. Design A3 called this non-deterministic;
    it is not, and a user typing the skill's own name gets the wrong artifact.
  - **The session stopped rather than improvising**, offered three paths, and refused to modify
    `~/.claude/skills` without an explicit go-ahead. That is the behaviour the preconditions are
    for, and it is why the fixture is still clean.
- **Commits**: this one.
- **Blocked by**: P5-T4's last half still needs a correctly launched session. **PD5-1** remains
  the user's decision.

## 2026-09-21 00:03 — round 5 closed, and the mutation backlog that reopened inside it (closed)

- **Task/phase**: round 5 executed elsewhere (10/10, one commit each); results verified here and
  the backlog it reopened closed out.
- **Landed**: three corpus cases and ten argued waivers for shape 4's mutants. Corpus 54 → 86,
  waivers 48 → 58, **305 of 363 killed, 0 surviving**, ratchet 244 → 305. Round 5 verified at
  10/10 with counters reconciled; Implementation Notes record the round and the follow-up.
- **Learned**:
  - **A ratchet on one number cannot see the invariant it was protecting.** Shape 4 added ~60
    lines and the sweep went from 0 survivors to 16 — but `killed` rose the whole time (244 →
    299) because the mutant *total* rose with it, so the gate stayed green while
    every-mutant-killed-or-argued quietly stopped being true. The number to watch is survivors;
    the ratchet watches kills. Recorded rather than fixed — changing the ratchet is a decision.
  - **The new detector was the least-tested code in the tool**, which is exactly what you would
    predict and exactly what nobody checks: a guard written this round, reviewed by nothing,
    carrying 16 of the 16 survivors.
  - **Nine of the sixteen sat on one decision line** — `logical_lines`' gap check. Same signal
    the 94-mutant handoff called out for `L96`: a count of survivors per source line points at
    the under-covered decision better than any reading of the code does.
  - **My own probe was wrong, in the under-reporting direction.** Its `SHAPE_OF` had not learned
    shape 4, so the baseline read 78/83 and five corpus cases would have scored as failures.
    Caught only because the number disagreed with `test-guards`, which is the authority. Fifth
    instance of this class in this plan and the second I have caused; the instrument needs the
    same scepticism as the thing it measures.
  - **R5-T7 was a contract decision and the session did not invent one** — `design.md` Q8-1 had
    already decided that a remediation plan has no research or design stage. Landing the
    tolerance on the `implement` side keeps the review's output shape stable, which matters
    because this round's own `tasks.md` is in that shape. `validate_project` still needs the
    same tolerance; that is a live follow-up, named in the design as *"a real change, not free"*.
  - **Nothing outward-facing ran for two tasks that name pushes and labels.** R5-T2 and R5-T9
    were exercised against a throwaway bare repo and a stubbed `gh`; for R5-T9 the defect is pure
    shell sequencing, so the stub reproduces it exactly, and the session said plainly that it had
    not run against a live PR rather than implying it had.
- **Commits**: the twelve round-5 commits, plus this one.
- **Blocked by**: **PD5-1** is still the user's decision. P5-T4 still needs `wb:adversarial-loop`
  reaching clean without `gh`. The round's `status:` is left `in-progress` — `complete` is the
  judgment-bearing transition `update_status` reserves for a human.

## 2026-09-20 22:05 — P5-T4 run 2: the wrapper works, and running it broke the wrapper (closed)

- **Task/phase**: P5-T4 run 2, scoped to `plugin/skills/adversarial-loop`. Run elsewhere; results
  brought back, verified here, and acted on.
- **Landed**: two zsh defects in `adversarial-review` fixed and verified under zsh; two
  corrections to `code-review-integration.md`; round 5 linked from Implementation Notes;
  `knowledge.md` gains the shell entry and an auto-mode amendment. **P5-T4 stays unchecked** —
  `wb:adversarial-loop` without `gh` has still never run.
- **Learned**:
  - **Steps 5 through 8 ran for the first time.** 5 legs → 23 candidates → 18 after dedupe → 10
    CONFIRMED, 2 PLAUSIBLE, 6 REFUTED, then a remediation plan written. Everything past Step 4 had
    been shipped untested through four review rounds and a release cut.
  - **The verify pass paid for itself twice in one round.** A Monitor finding raised independently
    by *three* legs came back REFUTED against `docs/claude-code-skills-guide.md:302` — agreement
    between reviewers is not evidence, and without the verifier three votes would have carried it.
    And a contested clearance was overturned: security had cleared the `&&` against a *failed*
    push while AI-systems raised a *successful no-op* push, so the clearance answered a claim the
    finding never made. Both are arguments for keeping Step 6 that no amount of prose would have
    produced.
  - **Running the reviewer is what found the reviewer's own defects, and both were silent.**
    `${PIPESTATUS[0]}` is a bash array and the Bash tool runs zsh, so the blast-radius guard
    expanded to nothing and a `grep` exiting 2 passed it without a word — the precise failure the
    block's own prose claims to exist for. And `git diff --stat $range` relied on word-splitting,
    which zsh does not do, so a path target died with `fatal: ambiguous argument`.
  - **Four rounds missed the second one for a reason worth keeping**: only the *path* target form
    puts a space in `$range`, and no round had ever run that form. Reading a fenced block is not
    exercising it. This is the same lesson as the corpus cases that satisfied two rules at once,
    arriving from the other direction.
  - **My predecessor's fix for run 1 was almost wrong the same way.** It proposed
    `grep -v "^\./<file>:"`; this grep emits no leading `./`, so that anchor would have filtered
    nothing. Shipped as `^(\./)?<file>:`, and run 2 confirmed the `(\./)?` is load-bearing.
  - **Two things about the built-in that the integration doc got wrong.** Its result line reads
    `launched (forked execution, running in the background)` on a long review, not
    `completed (forked execution)` — a wrapper matching on `completed` waits forever. And
    `ReportFindings` was unavailable *inside* the fork while available in the calling session, so
    the built-in leg fell back to prose. Both now recorded where the coupling is confined.
  - **Auto mode arrived on in a session started believing it was off — twice.** Both runs stopped
    at the precondition before anything else, which is the prompt working as intended. "Fresh
    session" is not evidence the mode is off.
- **Commits**: this one.
- **Blocked by**: **PD5-1** is still the user's decision. P5-T4 needs the `adversarial-loop`
  half. Round 5's ten tasks are queued and not started.

## 2026-09-20 21:21 — P5-T4 run 1: did not pass, and found the thing it was written to find (closed)

- **Task/phase**: P5-T4, the behavioural smoke session. Run in a separate session; results
  brought back here and acted on.
- **Landed**: transcript promoted and linted
  ([thoughts/2026-09-19-smoke-session.md](thoughts/2026-09-19-smoke-session.md)); the one
  CONFIRMED finding fixed in `adversarial-review/SKILL.md`; **PD5-1** raised as an open decision;
  two `knowledge.md` entries extended. **P5-T4 stays unchecked** — 2 of 5 PASS, 1 FAIL, 2 NOT RUN.
- **Learned**:
  - **The skill has no gate on diff size against fleet size, and would not have disclosed it.**
    On the release branch — 81 files, +11,655 — it sized to tier MAX and five lenses, which over
    ~5,000 lines of runtime surface is sampling, not reviewing. Its only cap is on lenses; its
    disclosure machinery covers a missing built-in leg and dropped lenses, and size overrun routes
    to neither. The stop came from the prompt, not the skill. **That is the answer to the question
    P5-T4 exists to ask**, and it is why a smoke session is not a formality.
  - **The blast-radius measurement was wrong in the safe-looking direction.** Step 3 prescribed
    `grep -rnF -- "<sym>" . | grep -v "<the changed file>"`, which filters by line *content*, so it
    drops every line whose text mentions that path — for a script invoked by path, exactly its
    callers. On `shellcheck-gate`: one hit, a README heading, reading as isolated. Anchored on the
    path field: four, including `plugin/scripts/check:52`, the line that puts it in the release
    gate. Ten lines below prose warning that the error direction is toward believing the change is
    safe. Its three documented safeguards all defend against grep failing *loudly*; none defends
    against grep succeeding while the filter removes the answer.
  - **The proposed fix was itself wrong here, and only running it showed that.** The session
    suggested `grep -v "^\./<file>:"`. On this machine the path field arrives *without* the `./`
    under one invocation and *with* it under another, so that anchor filtered nothing — failing
    safe, but failing. The shipped form is `^(\./)?<file>:`, and the prose now states what was
    measured rather than a GNU-versus-BSD mechanism nobody checked.
  - **My own verification of the fix was unfirable on the first attempt.** I ran the `bash` fence
    under zsh, where `${PIPESTATUS[0]}` is empty — so `search` was blank, the guard could not fire,
    and the negative control printed nothing and looked like a pass. Re-run under `bash -c` it
    behaves: status 0 on the real search, `SEARCH FAILED (grep exit 2)` on a broken one. Fourth
    instance of this class in this plan, first one I caused.
  - **Auto mode was on, so item 2 fails and cannot be rescued by rerunning in the same mode.**
    All four supporting files arrived via `cat`. The manifest's hard-stop rule is addressed to a
    gating behaviour only the Read tool has, so under auto mode it cannot fire in either direction
    — the manifest and the harness conflict and the harness wins silently. Honest mitigation,
    recorded rather than buried: the plugin path was inside the working directory, so `Read` would
    not have been gated either. Exercising that rule needs auto mode off *and* a marketplace
    install.
  - **A cwd recorded once at the top of a session is not a durable fact.** A `cd`-prefixed Bash
    call moved the session's primary working directory mid-run, and the workspace path is a
    symlink, so `pwd` and `pwd -P` disagree and will never compare equal. Both now in
    `knowledge.md`, attached to the entry that already says to state the cwd.
  - **The transcript failed `lint --all` and the hook could not fix it.** MD024 and MD025 are not
    auto-fixable, and MD025 counts a frontmatter `title:` as the document's title. A bulk-generated
    document can pass the PostToolUse hook, look clean, and break the `check` gate later.
- **Commits**: this one.
- **Blocked by**: **PD5-1** is the user's decision and P5-T5 is downstream of a P5-T4 that has not
  passed. A rerun needs auto mode **off** and a **scoped** target — one subsystem, not the release.

## 2026-09-19 16:22 — P5-T2, P5-T3, and two criteria that never ran (closed)

- **Task/phase**: Phase 5 — everything up to the manual steps.
- **Landed**: `3.0.0` in both manifests (`7ed03e5`); all nine release checks green on that
  commit with the output recorded verbatim (`02e43d2`,
  [thoughts/2026-09-19-release-checks.md](thoughts/2026-09-19-release-checks.md)); two Phase 3
  criteria repaired and README's Scripts section re-synced (`ef411c5`); counters reconciled
  81 → 83 of 85. P5-T4 and P5-T5 remain and are both manual.
- **Learned**:
  - **Phase 3's checkpoint ticked "All automated verification passing" over a check that could
    not fail and one that did.** `lint <directory>` answers *"No markdown files to lint"* and
    exits 0, so that criterion linted nothing and reported clean — this plan's own defect class,
    inside this plan's own criteria, found only because someone re-ran the boxes instead of
    reading them. The other counted the literal string `does not create`, returned 0, while the
    skill says *"This skill **never creates one**"* at line 60. **The tempting repair was to
    reword the skill until the grep passed.** Both greps now print what they found, and the
    non-goal pattern was falsified against a file that lacks it.
  - **The docs-accuracy criterion earned its place on its first real run.** It failed:
    `test-phi-patterns` and `lib_mutate.py` were missing from README's Scripts section, both
    added during round 4. The README also still described a 43-case corpus and twelve planted
    mutations against the real 73, 15 and 22 — and claimed 100%/100% for the rewrite where the
    measured figures are 97%/87%. A release that documents a tool it no longer ships is the
    drift this plan has now hit three times.
  - **Re-running a checkbox is not the same as reading it**, and the difference was four real
    defects this morning. The unticked boxes in Phases 3 and 8 looked like bookkeeping; two of
    them were failures and two were checks that could not fire.
  - **The CHANGELOG date is left wrong on purpose.** `## [3.0.0] — 2026-09-18` is the day the
    entry was written, and the release is not cut until P5-T4 and P5-T5 pass. Guessing the date
    now would make it wrong in the direction nobody checks; it gets set when the tag is created.
- **Commits**: `ef411c5`, `7ed03e5`, `02e43d2`, and this one.
- **Blocked by**: P5-T4 needs an interactive session from a recorded cwd outside the plugin
  directory — it cannot be evidenced headless, because auto mode bypasses the read conventions
  the smoke session exists to exercise. P5-T5 waits on P5-T4 and on the user's confirmation.

## 2026-09-19 15:56 — waiver keys and the vestigial chdir (closed)

- **Task/phase**: out-of-plan follow-up to the mutation backlog — the two items the previous
  entry left open, at the user's request.
- **Landed**: `os.chdir(root)` removed from `check-guards`; generated mutants now carry a
  **key** instead of a line number, and waivers match on it. 244/292 killed, 48 waived,
  0 surviving; ratchet holds at 244.
- **Learned**:
  - **The key that works is `scope | enclosing block | statement | operator`.** Statement
    text alone is not unique — `continue` appears in both arms of the same `if` in
    `md_shell_lines`, and `i += 1` twice in `substitutions` — but the enclosing block's
    header separates them and reads better than an index would. Only the `strip_comment`
    comment test needed `#1`/`#2`, because it holds two `BoolOp`s and two `Compare`s in one
    expression; that index orders the collisions inside one statement rather than every line
    in the file.
  - **Uniqueness is enforced, not hoped for.** All 292 keys are distinct after
    disambiguation, and the generator appends `#n` itself — so a waiver can never address
    two mutants and silently excuse one nobody argued about.
  - **The falsification is the whole point and it is cheap**: shift every line in
    `check-guards` down by two and re-run. All 48 waivers still bind. Under the old scheme
    every one of them would have gone stale at once, and the ratchet would not have noticed,
    because moving a mutant from `waived` to `survivors` leaves the kill count unchanged.
  - **Removing the chdir cost one curated mutation its anchor.** `resolve targets after the
    chdir` inverted two lines, one of which no longer exists — it would have reported
    `MUTATION DID NOT APPLY`, which the suite prints but does not fail on. Re-pointed at the
    property that is still real: take the targets raw, which the no-target integrity claim
    catches.
  - **The sweep is what licensed the deletion.** "This call does nothing" was an argument
    until the generated mutant deleting it survived 73 corpus cases and 15 integrity claims.
    That is the same evidence a waiver rests on, used the other way round.
- **Commits**: this one.
- **Blocked by**: nothing. P5-T2..T5 (the release) remain.

## 2026-09-19 06:51 — the 94 surviving generated mutants (closed)

- **Task/phase**: out-of-plan backlog, carried by
  [handoff-2026-09-19-05-39.md](handoff-2026-09-19-05-39.md) — kill or waive each of the 94
  survivors of `test-guards --generated`.
- **Landed**: **244 of 293 killed (was 198), 49 waived, 0 surviving.** 19 new corpus cases
  (54 → 73), 6 new integrity claims (9 → 15), 48 new waivers, and a stale-waiver guard on the
  sweep. Ratchet raised 198 → 244.
- **Learned**:
  - **The largest single cause was pairs of cases that satisfy two rules at once.** Every
    `ok-glob-*` case guarded with `[ -e "$f" ] || continue`, which matches *both* of
    `_is_guard`'s alternatives — so collapsing the alternation and turning the `or` into an
    `and` both changed nothing. Same shape in the status-test cases: all of them used `if`,
    so three of `STATUS_LINE`'s four alternatives were never exercised. A corpus written from
    idiomatic code tests the idiom, not the rule.
  - **`s3-guard-past-window` had no guard in it.** The name describes the case the corpus
    needed; the fixture is an unguarded loop like `s3-bare`, so the end-of-input flush
    reported it either way and `GLOB_WINDOW` was untested at any value. Two cases now pin the
    boundary from both sides. A fixture whose name and content disagree is worse than a
    missing one, because the gap reads as covered.
  - **Every string the tool prints that is not a finding is a claim, and six were unasserted.**
    Deleting the "no such path", "cannot read", "nothing to check" and "unguarded measurements"
    messages left every exit code intact — and so did changing the clean-exit `return 0`, and
    swapping `sys.argv[1:]` for `sys.argv[0:]`, which makes the tool scan *itself* and report
    clean. None of them is reachable from the corpus, which only ever looks at findings.
  - **49 of the 94 were genuinely equivalent, and saying so took longer than killing them.**
    Nine delete a docstring; three drop a `^` from a pattern used with `re.match`; seven sit
    in a branch unreachable from valid shell; four index a fence run of identical characters.
    The waiver is the deliverable for those, and the rule that a waiver carries an argument is
    what stopped the list becoming a shrug.
  - **Three are equivalent only because the scoring compares sets.** The two `break`s and the
    `pending_glob = None` after a window report exist to stop one finding being emitted twice,
    and duplicate output *is* a defect — it is invisible because findings are compared as a
    set of `(line, shape)`. Recorded in the waivers as a gap in the scoring rather than a
    property of the code.
  - **Waivers are anchored on line numbers, so any edit to `check-guards` silently unhooks the
    ones below it** — the mutant reappears as an unexplained survivor and the ratchet cannot
    see it, because moving a mutant from `waived` to `survivors` leaves the kill count
    unchanged. The sweep now fails on a waiver that matches no generated mutant and reports
    (without failing) one that a corpus case has since made redundant. Both branches
    falsified against planted waivers.
  - **`L44` is waived as *disputed*, not as equivalent.** Dropping the word boundaries lets
    `|| echo_warn` count as the whitelisted `|| echo`. But `||` guards the exit status
    whatever follows it, and the exit status is the whole subject of shape 1 — so pinning
    that line MUST-FIRE would encode a contested prior into the corpus, which is the mistake
    the Q8-5 label already recorded once.
- **Commits**: this one.
- **Blocked by**: nothing. P5-T2..T5 (the release) remain and are untouched by this work.

## 2026-09-19 05:39 — handoff written for the mutation backlog (closed)

- **Task/phase**: a scoped handoff for the 94 surviving generated mutants.
- **Landed**: [handoff-2026-09-19-05-39.md](handoff-2026-09-19-05-39.md) — the task, why the apparatus
  exists, a triage of the 94 by operator, the four groups worth opening first, and the five
  rules that keep the exercise honest.
- **Learned**:
  - **The handoff leads with triage, not the list.** 94 raw entries is a number; 57 source
    lines grouped by operator — 41 `int`, 31 `del` (9 of them deleting docstrings), 14 `regex`
    — is a starting point. The regex group is smallest and highest-value, because this tool's
    decisions live in its patterns.
  - **The rule most worth carrying across** is that the survivor list is not a bug list.
    Raising the kill rate with contrived cases would be fitting the corpus to the tool, which
    is the failure the whole apparatus exists to prevent.
  - **The branch is 26 commits ahead of `origin` and unpushed**, so the handoff says to push
    first if it is picked up on another machine. The plan is promoted into git but only locally.
- **Blocked by**: nothing. P5-T2..T5 remain and are independent of the backlog.

## 2026-09-19 05:37 — P8-T1 and P8-T8 (closed)

- **Task/phase**: the thrash evidence into `research.md`; P8-T8 assessed and superseded.
- **Landed**: `research.md` gains a facts-only section — the per-round table, the commit
  shapes re-derived from `git show --name-only`, both mirror-image regressions, the three
  files recurring across rounds, and the measurements of the verification apparatus.
  Parent plan 81 of 85.
- **Learned**:
  - **P8-T8's target no longer existed.** It said "re-plan the 11 open round-3 findings"; by
    the time P8-T3 was written they were closed — six by Phase 9's replacement of
    `check-guards`, the rest by Phase 7 — and round 4 re-raised none of them. Writing a
    retroactive plan for closed findings would have produced a document describing work
    already done. Recorded as a deviation with that reasoning rather than ticked.
  - **The mechanism's first use was round 4, and it ran before the mechanism was written.**
    That ordering is why P8-T3 documents an observed process. What it taught is in `design.md`:
    the per-finding criterion caught four fixes that passed the aggregate gate and failed their
    own finding's scenario, and shape 6 — "no mechanical criterion" — was never needed across
    31 findings.
  - **Every figure in the research section was re-derived rather than recalled**, which
    mattered: the 64% was published as "four of 22" and then "a third" before anyone counted
    it. Both earlier figures are recorded alongside the real one.
  - **The PostToolUse hook rewrote the file between the write and the check** — lint reported
    issues, then reported clean on the next run with no edit from me. The session warning about
    verifying committed content rather than working-tree content is a live effect, not a
    theoretical one.
- **Blocked by**: nothing. P5-T2..T5 (release) remain, plus the 94-mutant backlog.

## 2026-09-19 05:31 — renumber: this release is 3.0.0, aliases move to 4.0.0 (closed)

- **Task/phase**: version decision recorded; forward-looking references renumbered.
- **Landed**: `CHANGELOG.md` heading `[2.2.0]` → `[3.0.0]`; the versioning policy gains the
  clause that justifies it; eleven alias-removal promises across three stubs,
  `CHANGELOG.md` and `docs/commands-reference.md` move `3.0.0` → `4.0.0`, with "through 2.x"
  becoming "through 3.x"; the active plan's forward-looking references follow.
- **Learned**:
  - **The policy did not cover the actual breaking change.** "Major for removed or renamed
    stages" — nothing was renamed, so the letter said minor. But `check` now requires
    `shellcheck` and `python3` and fails without them: a contributor who could run the checks
    at 2.1.0 cannot at this release. The policy is amended to cover *any change to what the
    plugin requires of the environment it runs in*, in the same release that needed it.
  - **Moving the promise, not the release.** The alias stubs promised removal at 3.0.0 in
    eleven places. Honouring that number would have forced an unrelated deprecation into this
    release — the exact concern the original decision raised when it avoided 3.0.0. Moving the
    promise to 4.0.0 resolves it; the superseded reasoning is kept beside the new decision.
  - **Upstream's v3.0.0 is a different project's version.** Twenty references in the
    fork-merge plan are about `gvarela/workbench`; a blanket substitution would have corrupted
    a research record. Renumbering had to be surgical, not textual.
  - **History was left alone deliberately.** The journal, the handoff and the round-4 finding
    record still say 2.2.0, because they describe what was true when written. Rewriting them
    would falsify the record for the sake of tidiness.
- **Blocked by**: nothing. P5-T2 now bumps to 3.0.0.

## 2026-09-19 05:28 — P8-T3, P8-T4, P8-T5 (closed)

- **Task/phase**: the remediation-plan mechanism, the ledger and breaker, and shellcheck.
- **Landed**: `adversarial-review` Step 8 writes the plan; `adversarial-loop` Phase 1 step 3
  runs `implement` against it instead of fixing inline; `plugin/docs/reference/review-ledger.md`
  is the single authority for the ledger and the breaker; `shellcheck` is a required
  dependency with its own scoped gate. 79 of 85.
- **Learned**:
  - **The mechanism was written from something that worked.** Round 4's remediation used the
    shape by hand first, so Step 8 documents an observed process rather than an imagined one.
  - **`shellcheck-gate` failed its own gate on the first run**: a comment beginning
    `# shellcheck` is parsed as a *directive*, and an unparseable directive is an error. It
    also found `cd` without `|| exit` in two scripts — a failed `cd` scans the wrong tree —
    and the two dead assignments in `test-count` that round 4 flagged.
  - **Required, not optional.** `check` fails loudly with the install command when shellcheck
    is missing. Falsified on a PATH without it. A gate that silently skips is indistinguishable
    from one that passed, which is the class this directory exists to catch.
  - **Deliberate suppressions carry their reason.** Three `# shellcheck disable=` entries, each
    with the argument beside it: `ls` in wb-prime is deliberate because the sort key is the
    directory NAME, which survives a fresh clone where mtime does not.
- **Blocked by**: nothing. P5-T2..T5 (release) and P8-T1/P8-T8 remain.

## 2026-09-19 05:14 — round-4 remediation complete, 18/18 (closed)

- **Task/phase**: the generated mutator, the 94-survivor backlog, and R4-T9..T18.
- **Landed**: `350478f`, `9c59791`, `732e6e3`, `dc79479`. All 20 round-4 findings closed.
- **Learned**:
  - **The generated sweep found two defects in itself within an hour.** A `cmp Eq->NotEq`
    mutant inverted `if __name__ == '__main__'`, so that mutant ran `main()` at import with
    the sweep's own argv. Correctly counted as caught; its stderr leaked into the report.
    Diagnosis was slowed by stdout being block-buffered through a pipe while stderr is not,
    so the error appeared first and read as a startup failure.
  - **A sweep that always exits 1 is not a signal.** 94 survivors meant permanent red, so it
    ratchets instead: the kill count is recorded and may not fall.
  - **I escaped the option-shaped test pattern twice**, which is exactly what stops grep
    treating it as an option — the test passed both times while verifying nothing. Only the
    third, unescaped form discriminates. The first fixture also used `-x`, a real grep
    option, so the mutant HUNG rather than failed and stalled a two-minute command.
  - **The first PHI falsification passed for the wrong reason** — dropping `(?i)` from one
    pattern of two still matched via the other. Falsifying a falsification is not paranoia.
  - **Over-redaction is now pinned, not accidental.** The general member-ID shape cannot tell
    a member ID from any `AA-BB-nnnnnn`, so locale ids are redacted too. That is the safe
    direction for a PHI control and it costs a digest item its reference, so both the
    over-matches and the digit floor are test cases.
  - **Three of the curated 22 mutations are caught only via false positives.** Invisible
    while the score was one total; now reported separately.
- **Blocked by**: nothing. The parent plan's Phase 5 release tasks and P8-T3/T4/T5/T8 remain.

## 2026-09-18 21:06 — Phase 9: check-guards rebuilt (closed)

- **Task/phase**: Q8-3/Q8-4 recorded; Phase 9 added and executed, P9-T1 through P9-T5.
- **Landed**: `check-guards` and `test-guards` rebuilt in Python on the probed approach;
  the 43-case corpus shipped at `plugin/scripts/fixtures/guard-corpus.json`. Counters 71 → 76
  of 85.
- **Learned**:
  - **Corpus 43/43, integrity 4/4, mutations 12/12 — the pre-registered bar exactly.** Against
    the bash scanner's 89% corpus and 50% mutation on the same cases.
  - **The corpus caught a real bug in the tool on its first run.** `s1-guard-on-earlier` failed:
    I had written `break` where `continue` belonged, so a guarded capture earlier on a line
    excused an unguarded one after it — the *same* defect, in the *same* direction, that Phase 7
    shipped and round 3 found. Writing the corpus first is what stopped it shipping a third time.
  - **Two mutations survived the first harness, and both were corpus gaps rather than tool
    gaps**: no case used an extensionless script, and none had an unclosed fence as its only
    defect. Both are now cases. This is the mutation score doing precisely its job — telling you
    the corpus has a hole, not that the tool does.
  - **The missing-target refusal could never be caught by the corpus**, because every corpus
    case materialises a real directory. That needed assertions *outside* the corpus, and the
    mutation score had to be computed against corpus **and** integrity together — otherwise the
    integrity guards were themselves deletable, which is the identical hole one level up.
  - **The old dispatch rule was too broad**: `'/scripts/' in path` fed the corpus JSON to the
    shell analyser and reported 24 findings in this tool's own fixtures. Keying on file type
    rather than location fixed that and the scripts-README-parsed-as-shell case together.
  - **Q8-5 is now implemented, not just answered**: the rule is *captured and the status never
    tested*, with next-line lookahead. `shellcheck` was right that a bare assignment masks
    nothing.
- **Commits**: `ab17659`, and this one.
- **Blocked by**: nothing mechanical. P8-T3, P8-T4, P8-T5 and P8-T8 remain; whether to re-run
  the adversarial review is the user's call, and this phase is a rewrite — the
  highest-defect-density shape in the plan.

## 2026-09-18 20:51 — P8-T2, P8-T6, P8-T7: the check-guards spike (closed)

- **Task/phase**: Q8-1/Q8-2 decided and recorded; the spike pre-registered, run, and written up.
- **Landed**: `4ed63e6` (decisions), `6153221` (pre-registration), and this one. Spike artifacts
  under `thoughts/spike/`: a 38-case labelled corpus, a driver, a mutation runner, candidate C.
- **Learned**:
  - **Corpus**: A 89%, shellcheck 71%, C 97%. **Mutation**: A 50%, C 87%. Pre-registered
    outcome "C clearly beats A on both" → rewrite. Read against the pre-registration, not
    around it.
  - **A's four surviving mutations are exactly the four round 3 found by hand.** An independent
    method reproduced that result — the best evidence in the spike that the second score earns
    its cost.
  - **shellcheck is not wrong, it is answering a different question.** SC2312 flags every
    masked return, so it fires on `n=$(count foo f) || exit 2` and on `[ -e "$x" ] || continue`
    alike: 10 false positives on 15 correct files. Filtering it down to our three shapes means
    re-implementing the policy layer, which is the part that keeps breaking. It also missed the
    unquoted `--include` glob entirely.
  - **Q8-5 has an uncomfortable answer.** Shape 1 is well-formed only as "captured and the
    status never tested", which needs lookahead. Neither implementation does it; C's one false
    positive IS that case. And I labelled the disputed case MUST-FIRE, which encodes my own
    prior into the corpus — the label is what a reviewer should argue with, not the numbers.
  - **Stopped at the bound.** C was not built into the shipped tool. The spike establishes the
    approach is better; adopting it is a separate decision and it is the user's.
  - **Sequencing corrected mid-phase**: P8-T5 originally ran before the spike, which would have
    declared shellcheck a hard gate dependency before knowing whether it is used — the
    commit-on-an-untested-assumption this phase exists to stop.
- **Blocked by**: the adoption decision on candidate C, and Q8-3/Q8-4 before P8-T4.

## 2026-09-18 20:30 — round 3, the PHI fix, and Phase 8 (closed)

- **Task/phase**: scoped round-3 review; the PHI fix; Phase 8 opened for the thrash problem.
- **Landed**: `3ce6af9` puts the PHI patterns back where the collectors read them.
  `thoughts/2026-09-18-thrashing-and-remediation-planning.md` records the analysis. Phase 8
  adds 8 tasks and 5 open questions; total 80, 68 done.
- **Learned**:
  - **The loop was thrashing and could not see it.** Introduced-rate by round: — / 64% / 67%,
    with round 3 scoped to ~12% of the surface and a third of the lenses. Normalised, it rose.
    The gate is a *level* test; nothing compares round N to N−1, and there is no record to
    compare against.
  - **Two mirror-image regressions** — the `mktemp` fix for "a fixed path gets reused" shipped
    a literal fixed path; the guard-walk fix for "a later guard excuses an earlier capture"
    shipped its exact inverse. A mirror-image twin is near-proof the fix was pattern-matched
    rather than understood.
  - **Batch-fix, batch-verify is the larger mechanism.** Phase 7 was 22 tasks in **one**
    commit with the gates run once at the end. An aggregate green is compatible with any
    number of offsetting individual failures, and both fix phases contained some.
  - **Every verified finding already carries its own acceptance test** — the
    `failure_scenario` field is a pre-written test case, authored by the reviewer, and
    batch-fixing discards it. That single observation is the design.
  - **The plugin already ships every piece of machinery the fix loop bypassed**:
    `create_tasks`, `implement`, `tdd-discipline`, `verification-before-completion`,
    `task-verifier`. Treating findings as a to-do list instead of a plan skipped all five.
  - **shellcheck does not flag `n=$(grep -c f x)`, and is arguably right** — a bare assignment
    does not mask the status, so `$?` works. That makes `check-guards`' shape-1 rule possibly
    ill-formed rather than merely badly implemented, which is now Q8-5 and is exactly the kind
    of question the spike exists to answer before a fourth patch.
- **Commits**: `3ce6af9`, and this one.
- **Blocked by**: Q8-1 and Q8-2 need the user before P8-T3 can be written.

## 2026-09-18 19:56 — PHI fix + Phase 7, all 22 tasks (closed)

- **Task/phase**: the PHI regression, then P7-T1 through P7-T22 — close round 2.
- **Landed**: two commits. `1e818ea` restores the Member-ID matcher; `1990b40` closes the
  remaining 21 findings. Counters 46 → 68 of 72.
- **Learned**:
  - **Round 2 found 22 findings and 14 of them — 64% — were in surface Phase 6 created or
    rewrote.** I first wrote "four", then "a third"; both were estimates I did not count, and
    both understated it. The itemisation: PHI regression, mktemp, Step 1's three `range=`,
    Step 2 ignoring `$target`, the ungated `gh pr comment`, push/ready unchained, the
    `capture_seg` walk, the GLOB_WINDOW cancel keywords, fence indent tracking, the
    trailing-comment false positive, the `|| true` header/code mismatch, test-guards'
    exit-code-only assertions, STYLE being unemittable, and the CI workflow's missing
    permissions floor. The other 8 were pre-existing, found because round 2 was pointed
    where round 1 had not looked.
    **A fix phase has a higher defect density than the code it repairs** — written fast,
    under the impression the thinking is already done. That is now an attestation in the
    Phase 7 checkpoint rather than a lesson in a journal.
  - **The PHI regression is the shape to remember.** Genericizing an employer name out of a
    de-identification rule also removed the rule's matcher, and the scrub then reported clean
    on a real `BM-CA-12345678`. The edit had a non-safety motive and still needed a safety
    review. The restored rule now *fails closed*: an undeclared repository format widens it
    and can no longer disable it.
  - **`test-guards` earned itself within one commit.** Rewritten to assert *which* finding
    fired rather than just the exit code, it immediately caught a bug the old form could not
    see — the guard-segment walk cut at the first literal `grep`, so `echo "grep || true";
    n=$(grep -c x f)` read as guarded. Verified the new form fails when the fence scanner is
    broken: exit 1, where the old suite stayed 19/19 green.
  - **`check-guards` reported clean on a path that does not exist.** Its own defect class,
    in the script written to catch it, for the fourth time in this plan. It now exits 2 on a
    missing target and refuses to report clean having scanned zero files.
  - **I made the pipe-status mistake twice in this session**, once measuring a regression
    probe through `| tail` and once assuming `$c` word-splits in a `for` loop under zsh. Both
    produced a confident wrong reading in the session that is fixing that exact class.
  - **CI was pinned to a version the tree is not linted with** (0.45.0 against a local
    0.49.0) until I compared them. A pin that differs from the maintainer's version just
    relocates the disagreement into CI.
- **Commits**: `1e818ea`, `1990b40`, and this one.
- **Correction**: this heading first carried an estimated time (20:14) ahead of the
  actual clock. `journal-entries.md` says to read the clock and never estimate — the
  rule this plan ships, broken by the session shipping it. Kept as a record rather
  than quietly rewritten.
- **Blocked by**: nothing. Round 3 is gated on explicit user approval — Phase 7 is exactly the
  kind of surface round 2 proved needs reviewing, and P5-T2 onward follow the review.

## 2026-09-18 18:52 — Phase 6, all 21 tasks (closed)

- **Task/phase**: P6-T1 through P6-T21 — close the findings the dogfood review raised.
- **Landed**: 21 tasks, three commits. Phase 6 added to `tasks.md` before any fix, with the
  three pending decisions recorded and resolved. Counters 25 → 46 of 50.
- **Learned**:
  - **The base-ref fix is verified in both directions.** In a scratch repo with no
    `origin/main` and a hostile `REVIEW.md` staged: the old one-liner printed the malicious
    text and exited 0; the new form prints `REVIEW.md NOT READ` and never reads it.
  - **`check-guards` had a fifth hole nobody had found — its guard test.** `|| echo` was
    matched anywhere on the line, so `$([[ $(… | grep -c .) -le 2 ]] && echo 1 || echo 0)`
    read as guarded. That is why `test-quiet`'s two captures survived every prior run. The
    guard is now anchored to the capture itself, which also cleared a false positive the
    first tightening introduced on `wb-prime.sh:177`.
  - **Fixing the checker surfaced more than it closed, which is the expected direction.**
    Widening the detectors immediately flagged `test-count:66` — the "control" assertion that
    asserted the opposite of its own label. It had been passing since it was written.
  - **`test-guards` now exists because none of this was catchable.** 19 planted cases, both
    directions. `check-guards` has been an instance of its own defect class three times in
    this plan; a contract test is the only thing that changes that.
  - **A regression probe, not just a pass.** Reverting `count`'s `status -ge 2` to `-gt 2`
    now fails `test-count` (exit 1). Before P6-T15 it passed 13/13.
  - **The release's own vocabulary gate could never have passed.** Unanchored, it matched
    `rspec` inside "perspective" and `redis` inside "rediscovering". Now word-anchored, and
    the shipped plugin no longer names an employer anywhere — including the `daily-digest`
    PHI guardrail, which now applies to any covered organization without naming one.
  - **I did not measure my own regression probe correctly the first time**: I read the exit
    status through a `| tail -3` pipe and got `tail`'s. Re-measured directly. Worth recording
    because it is the exact class this phase is about, made by the session fixing it.
- **Commits**: `46b90f4`, `410c908`, and this one.
- **Blocked by**: nothing. P5-T2 through P5-T5 are next and are deliberately unstarted — the
  user gated the re-review on explicit approval, and the release follows the re-review.

## 2026-09-18 18:24 — P5-T1 + dogfood adversarial review (closed)

- **Task/phase**: P5-T1 — the `## [2.2.0]` CHANGELOG entry; plus a full `adversarial-review`
  run against PR #25, which is the PR that ships the skill.
- **Landed**: `CHANGELOG.md` gains `## [2.2.0]` (Added / Fixed / Changed / Migration) in the
  existing bolded-lead-sentence style. P5-T1 ticked; counters reconciled 23 → 25.
- **Learned**: the dogfood run returned **22 findings, 18 CONFIRMED**, against the artifacts
  this release ships. Four of the five deliberately-unproven items resolved on their own:
  the built-in leg really does run forked; all five supporting files were read; every
  relative link in the three new skill directories resolves; the shipped model-tier table
  matches the harness enum. The load-bearing ones:
  - `adversarial-review/SKILL.md:71` — `git show "$(git merge-base HEAD origin/main)":REVIEW.md`
    collapses to `git show :REVIEW.md` when `origin/main` does not resolve. `:path` is git's
    **index** syntax, so it reads the staged file and exits 0. The declared security boundary
    inverts into a read of the least trustworthy copy, and the documented absent-tell never
    fires. Reproduced in a scratch repo.
  - `check-guards` has four holes, and the repo it certifies contains the defect it hunts:
    `test-quiet:33` and `:39` carry unguarded `grep -c` captures and the script still prints
    `✅`. It also misses the last line of any file (`flush_pending` is a no-op whose comment
    claims otherwise), never scans the 17 indented ```bash fences, and scans prose in any
    `.md` under `scripts/`.
  - `$REPO` and `$PR` are used by every `gh` command in `reply-to-claude` and
    `adversarial-loop` and assigned by nothing.
  - `git diff --stat <pr#>` is fatal; no step converts a PR number to a range.
  - P5-T3's own vocabulary grep cannot pass: two real `hellobrightline` hits in
    `daily-digest/sources.md`, plus substring false positives (`rspec` inside "perspective",
    `redis` inside "rediscovering").
- **Blocked by**: P5-T2 and P5-T3 should not run until the CONFIRMED findings are
  dispositioned — the release would ship the defects the release exists to prevent.

## 2026-09-18 17:59 — P5-T6 (closed)

- **Task/phase**: P5-T6 — ship plugin/scripts/count with a contract test
- **Landed**: scripts/count + test-count (13 assertions, incl. a control proving grep -c does not
  distinguish), README entry, and a pointer from verification-before-completion
- **Commits**: 042f7af
- **Learned**: writing count exposed two false positives in check-guards — a comment describing
  the bad pattern, and a capture guarded by \$? on the next line. Both were real checker bugs.
  Three responses to this class have now each found a defect in the previous one.
- **Started at**: 3971331

## 2026-09-18 17:55 — handoff written (closed)

- **Task/phase**: session transfer at Phase 5, before the release is cut
- **Landed**: `handoff-2026-09-18-17-55.md`; draft PR #25 opened; 4 knowledge entries added
- **Next action**: a fresh session runs `/wb:adversarial-review 25` against this PR, then
  Phase 5 — P5-T1 CHANGELOG onward, with P5-T6 (`scripts/count`) required before completion
- **Commits**: fd7089d

## 2026-09-18 17:47 — P4-T4 (closed)

- **Task/phase**: P4-T4 — dangling-reference sweep across the whole plugin, run last so it covers
  the documentation change
- **Landed**: sweep narrowed to skill-meaning contexts; found and fixed `wb:loop` in
  touch-grass, a pre-existing dangling reference to a built-in mistaken for a wb skill
- **Commits**: 376173b
- **Learned**: the first sweep matched every backticked token and produced 39 hits, none real —
  a check too broad is as useless as one that cannot fire, just louder. Narrowing to contexts that
  *mean* "a skill" turned 39 false positives into one true one.
- **Started at**: b41834a

## 2026-09-18 17:47 — P4-T5 (closed)

- **Task/phase**: P4-T5 — re-sync help and README now that all three skills exist
- **Landed**: both skills added to help and README; coverage check clean
- **Commits**: d0564c1
- **Started at**: d6c35eb

## 2026-09-18 17:46 — P4-T3 (closed)

- **Task/phase**: P4-T3 — repoint model-help's calibration anchor and add gate-mode rows
- **Landed**: anchor repointed at adversarial-review; two gate-mode rows added, four columns each
- **Commits**: d48956b
- **Learned**: the right session tier for both new skills is Sonnet/medium, which reads as low
  until the fourth column explains it — the cost lives in forked agents, and paying Opus for a
  session that mostly waits is exactly the over-powering the rubric warns about.
- **Started at**: 40e906b

## 2026-09-18 17:46 — P4-T2 (closed)

- **Task/phase**: P4-T2 — repoint daily-digest's two review-family references
- **Landed**: both daily-digest references repointed; no ghost names remain in the file
- **Commits**: fa52b8a
- **Started at**: 1cc7222

## 2026-09-18 17:45 — P4-T1 (closed)

- **Task/phase**: P4-T1 — add the hand-off line to review-prep
- **Landed**: hand-off line near the top of review-prep, framed as same-subject-opposite-shape
- **Commits**: 331924c
- **Started at**: 273e6aa

## 2026-09-18 17:42 — P3-T2 + P3-T3 (closed)

- **Task/phase**: P3-T2 — write plugin/skills/adversarial-loop/SKILL.md
- **Landed**: adversarial-loop/SKILL.md and reference.md, in one commit — see below. Plugin
  enumerates 39 skills; no broken links anywhere
- **Commits**: 68a12f9
- **Learned**: writing the SKILL.md created a dangling link to a file the next task would produce,
  and the link check caught it before commit. One task one commit had to yield to not shipping a
  broken directed read. Also: the five CI/bot mechanics are all the same failure shape as the
  silent-measurement class — an absence that means "not yet" versus one that means "broken".
- **Started at**: 86e8c76

## 2026-09-18 17:39 — P3-T1 (closed)

- **Task/phase**: P3-T1 — write plugin/skills/reply-to-claude/SKILL.md
- **Landed**: reply-to-claude/SKILL.md; plugin enumerates 38 skills; dispositions linked to
  adversarial-review/reference.md rather than restated
- **Commits**: 888c0d5
- **Learned**: the `claude[bot]` login gotcha is the silent-measurement class wearing an API
  filter — a filter on `claude` matches nothing and returns success, so it reads as "no
  findings". Same failure shape as a grep that errors and reports zero.
- **Started at**: 84a096e

## 2026-09-18 17:27 — help/README accuracy (closed)

- **Task/phase**: out-of-plan, user-requested — bring wb:help and README.md up to date
- **Landed**: help and README now cover every shipped skill and the three reference docs; P4-T5
  filed to re-sync after Phase 3, with a runnable coverage check as a Phase 4 criterion
- **Commits**: bce0774
- **Learned**: help had drifted eight user-invocable skills behind, none of it caused by this
  work. The plan had no task to update it, which is the mechanism: documentation that nothing
  checks and no task owns falls behind silently, exactly like the review-skill references this
  whole effort is fixing.
- **Started at**: c2d8700

## 2026-09-18 17:24 — P2-T7 (closed)

- **Task/phase**: P2-T7 — make Phase 2's invariant checks runnable, and run them
- **Landed**: eight Phase 2 criteria rewritten as listing-based, shell-agnostic checks; all run
  and ticked; P5-T3's duplicate link check replaced with the working form rather than left fragile
- **Commits**: 0f40336
- **Learned**: the criteria I wrote at create_tasks time contained the very defects this session
  then spent hours finding — a pipeline form that parse-errors under zsh, and two counts where a
  zero is indistinguishable from a broken command. Writing checks before having been burned by
  them produces checks that look right.
- **Started at**: c8aeaa6

## 2026-09-18 17:18 — P2-T6 (closed)

- **Task/phase**: P2-T6 — write plugin/skills/adversarial-review/SKILL.md, the skill body
- **Landed**: SKILL.md — seven steps plus verify-only mode; all five supporting links resolve;
  plugin loads with 37 skills at ~180 always-on / ~3.3k on-invoke
- **Commits**: 815955e
- **Learned**: declaring `Skill` in `allowed-tools` is untested territory — no shipped skill had
  done it. Loading is unaffected, so the value is at worst inert; whether it actually pre-approves
  the call is still unproven and only P5-T4's smoke session can settle it.
- **Started at**: 1105065

## 2026-09-18 00:54 — P2-T5 (closed)

- **Task/phase**: P2-T5 — write plugin/skills/adversarial-review/reference.md
- **Landed**: reference.md as the adjudication authority; P3-T3 amended in tasks.md to link to
  it rather than restate the dispositions
- **Commits**: 1f0863f
- **Learned**: my own portability check had an unreachable negative branch — piping grep into sed
  masked its exit status, so `|| echo silent` could never fire. The check was right about the
  file and wrong about itself. Same family as everything else this session, in a new disguise.
- **Started at**: 49e0317

## 2026-09-18 00:51 — P2-T4 (closed)

- **Task/phase**: P2-T4 — write plugin/skills/adversarial-review/templates.md
- **Landed**: templates.md — six output shapes, with the reconnaissance summary emitted before
  any spawn so the cost is arguable before it is paid
- **Commits**: 4f347ea
- **Learned**: writing the Checked-and-clear shape was where the probe's correction actually bit.
  The natural framing is "here is what we covered"; the true framing is "here are claims we are
  making", and only the second one implies each line needs a file:line behind it.
- **Started at**: 6d6e92f

## 2026-09-18 00:45 — silent-measurement checks (closed)

- **Task/phase**: out-of-plan — ship a mechanical guard check (1) and change the documented
  measurement idiom to show-don't-count (2); file scripts/count (3) against Phase 5
- **Landed**: plugin/scripts/check-guards (three patterns, each falsified), scripts/quiet
  guarded, verification-before-completion now prefers listing to counting, scripts/count filed
  as P5-T6
- **Commits**: d291042
- **Learned**: the check I wrote to catch silent failures reported clean while holding a real
  finding — `FOUND=1` inside a pipeline subshell. Third occurrence of that trap in this repo,
  and `scripts/lint` already documents it. The pattern across all of this: the assurance
  machinery fails the same way as the thing it assures, so it needs the same scrutiny rather
  than more trust.
- **Started at**: 40d041e

## 2026-09-18 00:31 — L1 fix (closed)

- **Task/phase**: out-of-plan — close L1, the last unfixed defect from the P1-T3 probe
- **Landed**: indented-heading ERROR in validation-rules.md (before the extraction) and a
  Check it in journal-entries.md, both falsified; limitation recorded rather than engineered around
- **Commits**: c835266
- **Learned**: the silent-measurement class caught me a fourth time, inside the verification of
  the fix for the third — `grep -c` printing 0 and exiting 1 made `|| echo 0` emit a second
  zero, producing a bogus "WOULD FLAG". `wb-prime.sh:55-63` documents exactly this. Knowing a
  trap and not reaching for the guard are different things, which is an argument for the guard
  being in the prompt rather than in anyone's memory.
- **Started at**: 90a05c0

## 2026-09-18 00:26 — P2-T3 (closed)

- **Task/phase**: P2-T3 — write plugin/skills/adversarial-review/prompts.md
- **Landed**: prompts.md — shared evidence-contract preamble, stance agent, lens agent,
  verifier, and the four-value tier table
- **Commits**: 307fff8
- **Learned**: the stance agent's prompt is better written as "review only what a hunk-scoped pass
  cannot see" than as a second sweep — it composes with the built-in's `low` pass instead of
  contradicting its explicit hunk-only instruction, which was the Tier 0 conflict from
  explore_design, resolved in prompt text rather than in the ladder.
- **Deviation**: placed the verifier prompt here though the task did not assign it; recorded in
  tasks.md Implementation Notes.
- **Started at**: fb82f8e

## 2026-09-18 00:23 — P2-T2 (closed)

- **Task/phase**: P2-T2 — write plugin/skills/adversarial-review/lenses.md
- **Landed**: plugin/skills/adversarial-review/lenses.md — ten lens rows stated as behaviour
  rather than framework, four mandatory triggers that raise the tier, signal-ranked category
  recognition, the six-lens guard, and user-named lenses used verbatim
- **Commits**: 868981a
- **Learned**: the hard part of generalising was not removing framework names but replacing them
  with something that still discriminates — "persistence, data models, background jobs" carries
  the same selection power as the original's "models, commands, jobs" without naming a stack.
  Path conventions had to be ranked last as a signal; they are what mislead across ecosystems.
- **Started at**: 15e7dec

## 2026-09-18 00:14 — silent-check root cause (closed)

- **Task/phase**: out-of-plan, user-requested — fix the cause of the recurring
  "measurement fails and reads as success" class rather than more instances
- **Landed**: FALSIFY added as step 2 of verification-before-completion's gate, with the
  mechanism table and authoring red flags; pointers added in create_tasks' template and
  validate_execution Step 3. Stated once, referenced twice.
- **Commits**: 375d5c2
- **Learned**: the old gate could not catch this class by construction — all three failures
  passed IDENTIFY/RUN/READ/VERIFY. Also that the glob defect is shell-dependent: zsh reports 0
  where bash reports the truth, so "it worked when I ran it" is weaker evidence than it reads as.
- **Started at**: 4a01988

## 2026-09-18 00:08 — P2-T1 (closed)

- **Task/phase**: P2-T1 — write plugin/docs/reference/code-review-integration.md
- **Landed**: plugin/docs/reference/code-review-integration.md — rely-on/do-not-rely-on split,
  ReportFindings contract, /verify chaining, and the model-family table demoted to a dated
  observation with a working `Check it`
- **Commits**: bd654e7
- **Learned**: my own `Check it` command was unfirable on first write — `strings` emits the
  em-dash as the literal `\u2014`, so matching it with `.` returned nothing and read as clean.
  Every check in a reference doc needs running before the doc is committed.
- **Started at**: 17e3fba

## 2026-09-17 23:57 — P1-T4 (closed)

- **Task/phase**: P1-T4 — close out the probe document and delete the fixture
- **Landed**: probe document closed out with both commits in its frontmatter; fixture and bare
  origin deleted. Phase 1 complete — 4/4 tasks.
- **Commits**: 83ff352
- **Learned**: nothing new beyond P1-T3's findings; this task was bookkeeping and cleanup.
- **Started at**: 9f3caf1

## 2026-09-17 23:42 — P1-T3 (closed)

- **Task/phase**: P1-T3 — run both halves of the probe and append verbatim results
- **Landed**: both halves run and appended to the probe document; verdict — the wrapper shape
  holds. Pre-registration untouched.
- **Commits**: 9f3caf1
- **Learned**: a leg's *clearance* can be wrong, and only verification catches it. The lens leg
  cleared `daily-digest/sources.md:77`; the built-in flagged it; source settled it as a real
  bug. Also: the recon step's own measurement can fail silently and read as clean.
- **Blocked by**: nothing — B1 is recorded against P4-T2, not blocking.
- **Started at**: ef24356

## 2026-09-17 23:42 — P1-T2 (closed)

- **Task/phase**: P1-T2 — pre-register the wrapper-shape probe before running it
- **Landed**: thoughts/2026-09-17-wrapper-shape-probe.md, pre-registration only — rubric,
  predictions for both branches, and pass/fail conditions for Half A (sizing) and Half B (merge)
- **Commits**: ef24356
- **Learned**: the probe had to split targets. `/code-review` resolves from the current
  repository, so the fixture answers the sizing question and this repository answers the merge
  question. Skill-file loading is not probed here at all; P5-T4 covers it.
- **Started at**: d994b1f

## 2026-09-17 23:35 — P1-T1 (closed)

- **Task/phase**: P1-T1 — build the throwaway fixture repo for the wrapper-shape probe
- **Landed**: fixture at /tmp/wb-adv-probe with bare origin; `trivial` (docs, 4 insertions) and
  `risky` (app/auth.py, 6 changed lines, two planted defects). Build cwd recorded in tasks.md.
- **Commits**: be0d107
- **Learned**: the risky branch came out at 6 lines while carrying a privilege-escalation path —
  a cleaner demonstration of the LOC-is-not-complexity premise than the plan assumed.
- **Started at**: 2f00ea9

## 2026-09-17 23:21 — create_tasks (closed)

- **Task/phase**: P0-T4 — execution plan for 2026-09-17-adversarial_loop
- **Landed**: tasks.md — 6 phases, 27 tasks (4 already complete), 5 checkpoints. Phase 1 is a
  tracer bullet on the wrapper shape; everything after it is contingent on that verdict.
- **Commits**: plan promoted in a1793aa; this revision pending
- **Learned**: A1 proved the built-in is *invocable*, not that the two-leg *shape* holds — recon
  sizing, both legs spawning, two finding sets merging into one verified report. That gap is what
  Phase 1 exists to close before any shipped file is written.
- **Started at**: a1793aa

## 2026-09-17 21:31 — create_design (closed)

- **Task/phase**: P0-T3 — design for 2026-09-17-adversarial_loop
- **Landed**: design.md written and approved (`status: approved`); all 11 open records resolved —
  6 assumptions validated (A1/A2/A4/A5 by probe, A3 dissolved by PD1, A6 from knowledge.md) and
  5 pending decisions decided. Separately fixed the journal-ordering contract across the plugin
  and six defects the built-in review surfaced.
- **Commits**: see the two commits made at close of this entry
- **Learned**: the built-in `/code-review` is invocable from a wb skill via the `Skill` tool and
  runs **forked**, so it does not consume the caller's context — this is what makes the two-leg
  design affordable, and it was the assumption everything else rested on. Running it at `low` and
  `high` on our own tree found six real defects, three of them incomplete applications of my own
  journal fix.
- **Started at**: 46ef587
- **Superseded**: this entry was closed by writing a *second* heading (the 18:00 entry) rather
  than editing this one in place — the failure `journal-entries.md` names. Left in place with its
  state corrected rather than deleted, so the record of the mistake survives.

## 2026-09-17 19:15 — explore_design + resolve_questions (closed)

- **Task/phase**: architecture exploration, then all 11 open questions resolved
- **Landed**: `thoughts/2026-09-17-adversarial-review-architecture.md` (direction B, wrapper +
  lens injection, reconnaissance tiering); 11 decisions in `design.md` →
  `## Technical Decisions` → `### Resolved Decisions`; every `research.md` question row now
  carries a pointer; follow-up research appended on the built-in review machinery
- **Commits**: none yet (plan directory is gitignored until promoted)
- **Learned**: the built-in `/code-review` is a full multi-agent reviewer (8–10 finder angles,
  CONFIRMED/PLAUSIBLE/REFUTED vocabulary, `ReportFindings`), and `/verify` already implements
  prefer-the-repo's-own-skill with a bootstrap fallback. `review-strict` is not a real artifact
  anywhere. Both facts reshaped the design from "port two skills" to "wrap the standard install".

## 2026-09-17 18:00 — create_research (closed)

- **Task/phase**: P0-T2 — research for 2026-09-17-adversarial_loop
- **Landed**: research.md complete — 4 parallel agents, dependency + portability inventory of the two adversarial skills, wb shipping contract, 8 open questions
- **Commits**: none yet (plan directory is gitignored until promoted)
- **Learned**: `review-reef`, `review-security`, `review-strict`, `review-terse` are dangling symlinks into a missing `/Users/scraig/projects/prompts/` tree — adversarial-review's stated rule-catalogue dependency is unreadable. `plugin/skills/daily-digest/SKILL.md:204,278` and `plugin/skills/model-help/SKILL.md:160` already route to that non-existent review-skill family.

## 2026-09-17 17:53 — create_research (superseded, closed)

- **Task/phase**: P0-T2 — research for 2026-09-17-adversarial_loop
- **Next action**: spawn the Step 4 agents, then synthesize into research.md
- **Started at**: 46ef587
