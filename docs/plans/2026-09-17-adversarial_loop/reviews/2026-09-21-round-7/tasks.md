---
project: adversarial_loop
reviews: docs/plans/2026-09-17-adversarial_loop
round: 7
created: 2026-09-21
status: in-progress
total_tasks: 12
completed_tasks: 0
task_tracking: markdown-checkboxes
---

# Remediation — adversarial review round 7

Target: `plugin/skills/adversarial-review` — **delta-scoped to `1990b40..HEAD`** (+137/−10 across
`SKILL.md` and `templates.md`), not the path target the skill's Step 1 would have resolved
(`origin/main...HEAD -- <path>` = +948/−0, the whole feature). The narrowing was a user decision;
the skill has no way to express it. That is R7-T13's absent sibling — see Implementation notes.

Reviewed by `/code-review high` plus AI-systems, cross-file-tracer and release-engineer lenses.
One candidate (Step 8 never reports the plan path) was REFUTED and dropped: the loop invokes the
review in-session, so the path is retained.

**The shape of this round.** Six of the twelve tasks are in the three executable-block edits this
delta was written to make — the regex-injectable exclusion, the un-validated range, the
non-persisting `target`, the miscounted bullet list, the uncovered release gates, the unfiltered
blast-radius search. The fixes were each verified once, individually, by their author, with a
negative control. That caught the defect each was aimed at and none of the defects each
introduced.

## How each task is verified

Every task carries its finding's `failure_scenario` as its acceptance criterion, and **the
criterion is run before the fix**. A criterion that passes before the change is not a criterion.

## Tasks

- [x] **R7-T1** — `plugin/skills/adversarial-review/SKILL.md:224` — the newly-anchored exclusion
      interpolates the changed file's path raw into an ERE, so a path with regex metacharacters
      silently changes or invalidates the filter — and it fails toward "isolated", which the
      surrounding prose claims cannot happen.
      **Fails when:** for `app/[id].tsx` the `[id]` becomes a character class and the changed
      file's own lines stop being excluded. Unbalanced: `printf 'a/b.txt:1:x\n' | grep -vE
      "^(\./)?app/[id.tsx:"` → `ugrep: error: … mismatched [ ]`, **exit 2, no output**, piped
      into `sed` and read as "no callers". Meanwhile `SKILL.md:247` asserts "the errors this
      block guards against all point toward believing the change is safe".
      **Acceptance (shape 1)**: execute both commands above as written; assert exit 2 / empty
      today (RED), and after the fix assert the metacharacter path is matched literally and a
      pattern failure is announced rather than swallowed. (~4 calls) (completed 2026-09-22 18:29)

- [x] **R7-T2** — `plugin/skills/adversarial-review/SKILL.md:314` — Step 8 writes every
      verification-surviving finding into an executable plan, but adjudication happens afterwards
      and nothing prunes the rejected findings before `implement` runs.
      **Fails when:** `adversarial-loop/SKILL.md:38-49` orders it review → adjudicate → fix. Step
      8 writes all survivors; Phase 1 step 2 (`:133-137`) assigns dispositions; step 3
      (`:138-140`) runs `implement` on the already-written file. `grep -rn
      'prune|rewrite tasks|filter.*task'` across both skills returns nothing; templates.md's task
      shape has no disposition field. Only `Valid` says "Fix it"; `Over-fitted` says "Note it; do
      not build for it". `implement/SKILL.md:86-87` is "ONLY implement what is EXPLICITLY written
      in tasks.md". A round with 2 Valid and 4 rejected commits six fixes, and the gate
      (`adversarial-loop:193`) passes because it only checks Valid findings were resolved.
      **Acceptance (shape 3)**: dual grep — a pruning/annotation step present at a named
      `file:line` between adjudication and `implement`, *and* the current unconditional "runs
      `implement` against what you wrote" phrasing absent. (~3 calls) (completed 2026-09-22 18:42)

- [x] **R7-T3** — `plugin/skills/adversarial-review/SKILL.md:312` — Step 8 has no zero-findings
      branch, so a clean round (the loop's success state) makes `implement` stop and the loop
      misreports it as skill drift.
      **Fails when:** round 3 returns zero survivors with the plan directory present. Step 8's
      only skip is "no plan directory" — unlike Step 7, whose `templates.md:37-38` explicitly
      names "an empty array if nothing survived". The loop's gate sits at `:191-193`, **after**
      all six steps, so step 3 runs `implement` unconditionally; `implement/SKILL.md:167-170`
      stops on "no task lines"; the loop's drift clause (`:148-150`) enumerates only "a missing
      file" and "no phases", so the only categorization available is "the two skills have drifted
      apart: say so and stop" — emitted exactly when it should flip to Phase 2.
      **Acceptance (shape 3)**: dual grep — a zero-findings branch present in Step 8 at a named
      `file:line`, *and* a matching clean-round branch in `adversarial-loop`'s step 3 so the stop
      is not read as drift. (~3 calls) (completed 2026-09-22 18:52)

- [x] **R7-T4** — `plugin/skills/adversarial-review/SKILL.md:315` — `<plan>`, `<N>` and `<date>`
      are never defined, so two sessions diverge on where to write, which round number to use,
      and which timezone dates the directory.
      **Fails when:** `grep -rn '<plan>|<date>|round-N' plugin/skills/adversarial-review/`
      returns only the two lines that *use* them. (a) Two plan directories exist here and the
      target is a PR/branch/path with no mapping to either; Step 8's only escape is "no plan
      directory". (b) The review is stateless — the loop passes only target and `--effort` — so
      round 2 writes `round-1` and clobbers round 1's `[x]` checkboxes. (c) Local vs UTC is
      unspecified while `implement:260` mandates `date -u`. **Already in the tree:** following
      Step 8 as written this session produced `2026-09-21-round-6` beside existing
      `2026-09-18-round-4` and `2026-09-20-round-5`, which are local-dated.
      **Acceptance (shape 4 + negative control)**: grep for a stated resolution rule for each of
      the three placeholders; today all three greps return nothing (RED). Negative control: the
      same greps against an unmodified copy must still return nothing. (~4 calls)
      (completed 2026-09-22 19:03)

- [x] **R7-T5** — `plugin/skills/adversarial-review/SKILL.md:60` — the new binding note says to
      export `target` "in the same shell you run the block in", but shell state does not survive
      between Bash tool calls and Step 2 is a separate block.
      **Fails when:** measured — `export target=X` in one Bash call, `${target:-UNSET}` in the
      next prints **UNSET**. On `/wb:adversarial-review 42`, Step 2's `printf '%s' "${target:-}"
      | grep -qE '^[0-9]+$'` is false in the new shell, the else branch runs `gh pr view` bare,
      `head_ref` becomes `HEAD`, and REVIEW.md resolves from whatever branch is checked out —
      precisely the fourth outcome `SKILL.md:170-174` calls "the one with no error to show for
      it", with the wrong base then echoed as legitimate.
      **Acceptance (shape 1)**: run `export target=42` and `echo "${target:-UNSET}"` in two
      separate Bash tool calls; assert UNSET today (RED). After the fix, assert Step 2 either
      re-derives `target` in its own block or the note says so explicitly. (~3 calls) (completed 2026-09-22 23:25)

- [x] **R7-T6** — `plugin/skills/adversarial-review/SKILL.md:81,88` — the Step 1 block never
      checks that the range it printed is real, and its `exit 1` kills the whole tool-call shell.
      Two findings, one file, one class (Step 1 resolution robustness).
      **Fails when:** (a) a glob or mistyped path fails `[ -e "$target" ]` (zsh does not glob
      inside a quoted test), falls to the branch case, and `git diff --stat
      "origin/main...plugin/skills/adversarial-review/*.md"` **exits 0 with no output** — a third
      outcome `SKILL.md:118-121` does not cover. (b) `origin/main` is hardcoded in three of four
      branches while Step 2 enumerates `master`/`develop`/shallow/fork as real conditions;
      `git diff --stat origin/nonexistent...HEAD` writes `fatal: ambiguous argument` to stderr
      with nothing detecting it. (c) On a `gh` failure the `exit 1` terminates the entire shell —
      measured; everything queued after it in the same call silently never ran, and `check-guards`
      has no detector for `exit`.
      **Acceptance (shape 1)**: execute all three cases as written; assert the measured wrong
      outcomes today (RED), then assert the fixed block reports a non-empty stat or says
      explicitly that the range did not resolve, and returns rather than exits. (~6 calls) (completed 2026-09-22 23:39)

- [ ] **R7-T7** — `plugin/skills/adversarial-review/SKILL.md:112` — the file names `check-guards`
      as what protects its fenced blocks; neither release gate scans markdown at all.
      **Fails when:** measured — `shellcheck-gate` builds its list from `find plugin/scripts
      plugin/hooks -type f` filtered on a bash/sh shebang, reports "9 shell scripts clean", and
      never touches a SKILL.md. `check-guards` has exactly four detector shapes, none matching
      these blocks, and ran clean over all five adversarial-review files. Reverting `search=$?`
      to the `search=${PIPESTATUS[0]}` this delta fixed and re-running both gates: **both exit 0,
      clean**. The protection the file cites does not cover the defect that bit it.
      **Acceptance (shape 2)**: a test case that fails before and passes after — reintroduce
      `${PIPESTATUS[0]}` into a fenced block and assert the gate now flags it, having first
      asserted it does not today. (~5 calls)

- [ ] **R7-T8** — `plugin/skills/adversarial-review/SKILL.md:227` — "Four details in that command"
      is followed by five bullets.
      **Fails when:** `awk` between that heading and the next section counts **5** bullets (`-F`,
      `--`, status-from-`$?`, guard-runs-before-print, path-anchored exclusion); the delta changed
      the count Three → Four while adding two. A reader reconciling prose against block concludes
      an edit stranded one, and the two likeliest deletions are the two newest — the
      `$?`-not-`PIPESTATUS` rule and the path anchor — which are exactly the two the same delta
      documents as fixes for measured defects.
      **Acceptance (shape 1)**: run the bullet count; assert 5 against a heading saying "Four"
      today (RED), and equality after. (~2 calls)

- [ ] **R7-T9** — `plugin/skills/adversarial-review/SKILL.md:17` — `review-ledger.md` is listed
      as "the findings ledger a round appends to" and no step reads or writes it.
      **Fails when:** `grep -rn 'ledger|review-log' plugin/skills/adversarial-review/` returns
      exactly one hit — that header line. The ledger at `docs/plans/<plan>/review-log.md` is
      written only by `adversarial-loop` Phase 1 step 5. The skill advertises standalone use, so
      standalone rounds leave no ledger, and `review-ledger.md:24-25` states the consequence: "a
      file that was never created reads exactly like a clean one" — the thrash breaker cannot
      fire, on exactly the runs nobody is watching.
      **Acceptance (shape 5)**: a reference resolver — every file listed in the header block must
      have at least one step that directs its read. Today `review-ledger.md` has zero (RED).
      After the fix either a step appends, or the bullet says the file is the loop's. (~3 calls)

- [ ] **R7-T10** — `plugin/skills/adversarial-review/SKILL.md:5` — `allowed-tools` declares a
      read-only surface while Step 8 writes a file.
      **Fails when:** the frontmatter is `Read, Glob, Grep, Bash, Task, Skill, ReportFindings` —
      no `Write`, no `Edit` — while Step 8 writes `docs/plans/<plan>/reviews/<date>-round-N/
      tasks.md`, and `SKILL.md:39` reinforces it with "It does **not** fix anything." Every
      sibling that writes declares it: `adversarial-loop:5`, `implement:5`, `create_tasks:5` all
      carry `Write, Edit`; `update_status:5` carries `Edit`. An operator reading the frontmatter
      to decide whether the skill mutates the tree concludes it does not, and runs it unattended.
      **Acceptance (shape 3)**: dual grep — `Write` present in `adversarial-review/SKILL.md:5`,
      and the "does not fix anything" sentence reconciled so it no longer implies no writes.
      (~2 calls)

- [ ] **R7-T11** — `plugin/skills/adversarial-review/SKILL.md:220` — the blast-radius search
      recurses the whole working directory with no exclusion, so most "measured" call sites can
      be transcript prose.
      **Fails when:** measured twice here — for `review-ledger.md`, 15 hits of which **11 (73%)**
      are `.context/attachments/*.txt` session transcripts and 4 are real; for `check-guards`, 23
      of 58 (~40%). The reconnaissance summary then reports an inflated blast radius, and
      `lenses.md` sets the tier as the **maximum** of six axes, so transcript noise can raise the
      tier and the fleet cost.
      **Acceptance (shape 1)**: run the block as written for `review-ledger.md` and count
      transcript hits — 11 of 15 today (RED); after the fix assert 0. Note for the implementer:
      the standing environment note says ugrep rejects `--exclude-dir`, but it was measured
      **working** here (`--include=` is the one that is rejected, exit 2) — verify before
      choosing the mechanism. (~4 calls)

- [ ] **R7-T12** — `plugin/skills/adversarial-review/templates.md:111` — Step 8 writes into
      gitignored `docs/plans/` and nothing promotes the file.
      **Fails when:** `.gitignore:7` is `docs/plans/`; `git add` on the Step 8 path exits 1 with
      "The following paths are ignored … hint: Use -f", staging nothing. `git add -f` appears
      nowhere in either skill. The round's only durable artifact never reaches a commit, is lost
      on `git clean -fdx` or a worktree teardown, and — because ignored paths never appear in
      `git status --short` — every downstream "confirm the tree is clean" reads clean over it.
      **Acceptance (shape 1)**: `git add` the Step 8 path; assert exit 1 today (RED), and after
      the fix assert Step 8 (or the loop) promotes it with `-f` and the file appears in
      `git status --short`. (~3 calls)

- [ ] **R7-T13** — `plugin/skills/adversarial-review/SKILL.md` Step 3 and `templates.md` (the
      reconnaissance summary) — PD5-1, decided 2026-09-20 as **disclose only**: the skill has no
      disclosure when the fleet it sized cannot cover the range it resolved.
      **Fails when:** on `origin/main...HEAD` at 81 files / +11,655 the skill sized tier MAX and
      five lenses over ~5,000 runtime lines and would have reported findings indistinguishable
      from a full pass; round 7's own path target expanded 137 delta lines to 948 with no line in
      the output saying so. The existing disclosure machinery fires only for a missing built-in
      leg and for dropped lenses — neither path covers this.
      **Acceptance (shape 4 + negative control)**: the reconnaissance summary states the resolved
      range's size beside the fleet it sized, and the report carries a shortfall line whenever a
      lens is covering more than it can read — in the voice the built-in uses to disclose a
      single-pass run. Grep for the shortfall line's template in `templates.md` and its trigger
      in Step 3; today both greps return nothing (RED). Negative control: the same greps against
      an unmodified copy still return nothing. No threshold, no stop, no `--since` — PD5-1
      rejected both and `--since`/`--range` is 3.1 work. (~6 calls)
- [ ] **R7-T14** — `plugin/skills/adversarial-review/templates.md:137-139,153` — shape 6 tells the
      producing model to "Label `(attestation)`, name who must look", but the task-line template
      reserves no slot for either, so the label is an instruction rather than a template literal
      and the consumer that now keys off it may never see it.
      **Fails when:** round 6's R6-T3 taught `implement` to divert a no-criterion task to the Step
      8 checkpoint instead of deadlocking a TDD worker against it. Its Step 4 recognition
      (`implement/SKILL.md:252-264`) matches the `(attestation)` label **or** an acceptance line
      saying outright that no mechanical criterion exists. But `templates.md:139` emits
      `**Acceptance (shape <n>)**: <the check, from the taxonomy below>`, and `<n>` is a digit —
      nothing in the emitted line carries the word. A producer may write `**Acceptance (shape
      6)**: Steve must judge whether …` with the token absent, leaving only the prose key.
      Shape 6 also says to name who must look, but no field holds the name, so `implement` Step
      8.4's request can only say "someone must look".
      **Acceptance (shape 3)**: dual grep — the token `(attestation)` and a named person/role
      field must be reachable from the **emitted** task line, not only from the taxonomy table
      prose; today `grep -n 'attestation' plugin/skills/adversarial-review/templates.md` hits
      only the table row at `:153` and nothing in the template block at `:137-139` (the RED).
      After the fix the emitted form pins both at a named `file:line`, and `implement`'s Step 4
      recognition matches it literally. (~3 calls)

## Implementation notes

- **Blocking set**: R7-T1, R7-T2, R7-T3. The first corrupts the measurement the whole tier
  decision rests on; the second lands fixes for findings the loop rejected; the third turns the
  loop's success state into a reported failure.
- **R7-T13 is now the PD5-1 disclosure task** (filled 2026-09-22). PD5-1 fired for real this
  round: a path target expands to the entire feature (948 lines) with no way to say "the delta
  since round N", and the narrowing was applied by hand. PD5-1 was decided 2026-09-20 as
  *disclose only* — see `design.md` → Resolved Decisions — so the task states the ratio and adds
  a shortfall line. A `--since=<ref>` / `--range=<a..b>` argument and any refusing gate are
  deferred to 3.1, recorded here so the idea is not lost.
- **R7-T4 resolves by linking, not by inventing.** `plugin/docs/reference/remediation-plan.md`
  (P5-T7, 2026-09-22) states the resolution rules for `<plan>`, `<N>` and `<date>`. R7-T4's fix
  is to direct Step 8's read of that document and make the loop pass the plan directory it
  resolved; it must not restate the rules in `SKILL.md`, which would recreate the drift P5-T7
  removed. Round 6's consumers already link to it.
- **Out of delta, recorded so it is not lost.** Real, but in surface rounds 1–2 already reviewed,
  so not tasked here: Step 2 does not handle branch targets at all (base and head both resolve
  from the current checkout); Step 2's `REVIEW.md NOT READ` diagnostic names `origin/main` when
  the operand that actually failed is a malformed `head_ref`; Step 2's `2>/dev/null` contradicts
  the no-suppressed-stderr rule Step 3 states two screens later; Step 4's BARRIER has no handling
  for the `launched (forked execution, running in the background)` result shape — **both built-in
  legs returned exactly that shape this session**; Step 4's stance-agent condition encodes a
  `/code-review` internal that `code-review-integration.md` lists under "do not rely on these";
  Step 6's verifier fan-out is uncapped and absent from the pre-spend summary (this run spawned 7
  verifiers behind a 6-lens cap); the prose sniff order at `SKILL.md:45` says digits-then-path
  while the block tests `-e` first; `lenses.md:95` gives no resolution when mandatory plus
  user-named lenses exceed six.
- **Contamination note for whoever reads the agent transcripts**: two lens agents cited
  `reviews/2026-09-21-round-6/tasks.md` as independent corroboration. It is not — it is round 6's
  own output, written earlier in the same session. Their own re-run reproductions stand; the
  citation does not.

- **R7-T14 is numbered around a reserved slot.** The note below reserves `R7-T13` for the absent
  `--since` / `--range` control, so the task folded in from round 6's checkpoint takes `R7-T14`
  rather than colliding with it.
- **Folded in from round 6's checkpoint (2026-09-21).** R7-T14 above. Round 6's R6-T3 built the
  consumer side of the attestation contract; the producer side lives in this round's file, so the
  two halves must land together or the label remains unenforceable.
- **Recorded for round 7 planning, explicitly NOT to be done in round 6** (user decision,
  2026-09-21): the remediation-plan recognition rule — "a `reviews:` key in frontmatter or a
  `reviews/<date>-round-N/` path" — is now restated in **17 shipped files**. The house pattern is
  one authority under `plugin/docs/reference/` linked from each site. The intent is to write
  `plugin/docs/reference/remediation-plan.md` before round 7 starts and repoint all 17, which
  also gives R7-T4's undefined `<plan>`, `<N>` and `<date>` a home.
- **Noted at round 6's checkpoint, not blocking, no task yet**: the attestation list R6-T3
  introduced lives only in session memory until Step 8.4. A session that dies mid-phase leaves the
  diverted task at `[ ]` with nothing recording *why* it was diverted — the checkbox is
  indistinguishable from a task never reached. Durable placement (the journal, or a line in
  `tasks.md`) is the obvious fix and belongs to whichever round takes it up.
