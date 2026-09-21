---
project: adversarial_loop
reviews: docs/plans/2026-09-17-adversarial_loop
round: 6
created: 2026-09-21
status: in-progress
total_tasks: 8
completed_tasks: 0
task_tracking: markdown-checkboxes
---

# Remediation — adversarial review round 6

Target: `plugin/skills/implement/SKILL.md` at `origin/main...HEAD` (+27/−9). Reviewed by the
built-in `/code-review high` leg plus AI-systems, cross-file-tracer and security lenses; every
candidate verified. Two security-lens candidates were REFUTED and dropped; three built-in
candidates were out of range (that leg resolved a stale local `main`) and one of those was also
REFUTED on the merits.

**The shape of this round.** All nine findings are consequences of one root cause: R5-T7 widened
`implement`'s *entry* check to accept a `tasks.md`-only remediation plan, and nothing downstream
of Step 3 was widened with it. Steps 6–9, the two templates, `reference.md`, and four sibling
skills all still assume `research.md`, `design.md`, a numbered phase, or a committable plan
directory. Fix them as one coherent change or the round will re-raise them.

## How each task is verified

Every task carries its finding's `failure_scenario` as its acceptance criterion, and **the
criterion is run before the fix**. A criterion that passes before the change is not a criterion.

## Tasks

- [x] **R6-T1** — `plugin/skills/update_status/SKILL.md:65` — `update_status` has no remediation
      carve-out, so Step 9 of `implement` closes every round by routing the user to
      `/wb:create_project`, which `implement/SKILL.md:122` forbids.
      **Fails when:** `implement` finishes a round at `docs/plans/<plan>/reviews/<date>-round-N/`
      and reaches Step 9 (`SKILL.md:437`). `update_status/SKILL.md:65-67` is `⛔ BARRIER 1` over
      `research.md` and `design.md`; `update_status/reference/error-handling.md:20-30` then emits
      "❌ Missing Documentation Files … Run /wb:create_project first". Counters
      (`completed_tasks: 0`, `status: in-progress`) are never reconciled, permanently, because
      `update_status` is their only writer.
      **Acceptance (shape 3)**: dual grep — `grep -rniE 'remediation|reviews:'
      plugin/skills/update_status/` returns nothing today (exit 1, the RED state); after the fix
      it names a carve-out at a stated `file:line`, *and* the `create_project` routing in
      `error-handling.md` is conditioned so it cannot fire for a round directory. (~3 calls)
      (completed 2026-09-21 05:55)

- [x] **R6-T2** — `plugin/skills/implement/SKILL.md:328` — Step 6b stages `tasks.md` and
      `journal.md` **by path** from a round directory that `.gitignore:7` (`docs/plans/`) ignores
      and nothing promotes, so `git add` exits 1 and the chained commit does not run.
      **Fails when:** measured in this repository — `git add
      docs/plans/2026-09-17-adversarial_loop/reviews/2026-09-20-round-5/tasks.md` prints "The
      following paths are ignored by one of your .gitignore files" and **exits 1**, staging
      nothing. `git add -f` appears nowhere in `implement` or `adversarial-review`. One task, one
      commit breaks on task 1 — and hides, because ignored paths never appear in
      `git status --short`, so Step 6a's discriminator, Step 6c's "end clean either way" and Step
      8.2's "confirm the tree is clean" all read clean over an uncommitted plan file.
      **Acceptance (shape 1)**: execute the staging command as Step 6b writes it against a round
      directory and assert exit 0 with the file staged. Today it exits 1 — that is the RED.
      Re-run after the fix. (~4 calls) (completed 2026-09-21 06:02)

- [x] **R6-T3** — `plugin/skills/implement/SKILL.md:196` — Step 3 asserts every remediation task
      carries an acceptance criterion that *is* the worker's context; the producer deliberately
      emits shape-6 `(attestation)` tasks with no mechanical criterion, which deadlock the
      worker/verifier loop.
      **Fails when:** `adversarial-review/templates.md:154` defines shape 6 as "**No mechanical
      criterion.** Label `(attestation)`, name who must look". `implement` Step 4 selects it with
      no shape carve-out; `task-worker.md:20` is "TDD, always. RED → GREEN → REFACTOR" and cannot
      write a failing test for "a human must look at this"; `task-verifier.md:104` — "If the tree
      is unexpectedly clean, the worker changed nothing — that is a FAIL". 6c escalates one rung,
      fails again, task goes to the blocking list, the finding is never fixed, and
      `adversarial-loop`'s gate never clears — so the next round re-raises it.
      **Acceptance (shape 4 + negative control)**: grep `implement/SKILL.md` and
      `plugin/agents/task-{worker,verifier}.md` for `attestation`; today the only hits are the
      unrelated phase-checkpoint box in `SKILL.md` and **zero** hits in both agent files — that
      is the RED. After the fix, a named `file:line` routes a no-criterion task to the Step 8
      checkpoint instead of a worker. Negative control: the same grep against an unmodified copy
      must still return the RED result, proving the grep can fail. (~4 calls) (completed 2026-09-21 06:10)

- [x] **R6-T4** — `plugin/skills/implement/SKILL.md:418` — Step 8 and both templates source
      manual-verification content from `design.md`, which Step 1 of the same change declares
      absent for a remediation plan.
      **Fails when:** `adversarial-loop` Phase 1 step 3 invokes `implement` with no `--auto`, so
      Step 8.4 emits `templates/manual-verification-request.md` — body "Please perform the
      following manual checks from design.md:" (line 29) — and **waits** for a confirmation of an
      empty checklist. The `--auto` branch instead lists "the manual steps from `design.md` that
      nobody performed" from a nonexistent file. Both templates also interpolate `Phase ${phase}`
      and close with "Ready to proceed to Phase ${phase + 1}" while `SKILL.md:164-166` says a
      remediation plan has no phase.
      **Acceptance (shape 3)**: dual grep — `design.md` and `Phase ${phase` must be absent from
      the remediation path of `SKILL.md:410-425`,
      `templates/manual-verification-request.md` and `templates/phase-completion-report.md`, and
      a replacement source for a round's manual steps must be present at a named`file:line`.
      (~3 calls) (completed 2026-09-21 06:19)

- [x] **R6-T5** — `plugin/skills/implement/reference.md:55` — the resume path still requires
      `research.md` and `design.md` with no exemption, so `continue` on a round contradicts Step 1
      of the same skill.
      **Fails when:** a round is interrupted (context limit, a 6c block, a declined confirmation)
      and the user runs `/wb:implement docs/plans/<plan>/reviews/<date>-round-N/ continue`. Step 1
      routes `continue` through `reference.md`'s Resume Logic, whose step 4 reads "Review context:
      tasks.md Implementation Notes, research.md, design.md, and `.claude/wb/knowledge.md` if
      present" — the two plan files carry no "if present", unlike `knowledge.md`. The word
      "remediation" appears nowhere in `reference.md`. One skill, two documents, two behaviours.
      **Acceptance (shape 3)**: dual grep — `grep -c remediation plugin/skills/implement/
      reference.md` is 0 today (RED); after the fix it is ≥1 *and* `reference.md:55` carries an
      "if present" or an explicit round exemption. (~2 calls) (completed 2026-09-21 06:26)

- [ ] **R6-T6** — `plugin/skills/implement/SKILL.md:254-257` — the new top-insert journal rule
      collides with Step 6c's deliberately-open blocked entry, and a round's `journal.md` lands
      one level below every reader's glob. Two findings, one file, one class (journal placement).
      **Fails when:** (a) task P1-T2 blocks, Step 6c leaves its entry `(open)` and the coordinator
      continues; P1-T3's Step 5 entry is written *above* it; `validate_project/reference/
      validation-rules.md:142-147` runs `realHeadings.slice(1).filter(h => /\(open\)\s*$/i)` and
      ERRORs "journal.md has 1 stale open entr(y|ies) below the newest … closed by writing a
      second heading instead of editing in place" — for a state `implement` deliberately created,
      with the cause misattributed. (b) The round's `journal.md` is created at
      `docs/plans/<plan>/reviews/<date>-round-N/journal.md`, below the `docs/plans/*/` glob at
      `plugin/hooks/wb-prime.sh:83` that `forge`, `daily-digest`, `resume_handoff` and
      `create_handoff` inherit, so the blocked `(open)` entry is invisible while the parent's
      journal still reads `(closed)`.
      **Acceptance (shape 1 + shape 3)**: construct a journal with a newest `(open)` entry above
      an older blocked `(open)` entry and run the `validation-rules.md` check — it must ERROR
      today (RED) and pass after 6c gains a distinct blocked marker or the validator gains the
      exemption. Separately, the fix must state at a named `file:line` **which** `journal.md` a
      remediation plan writes; grep must find that sentence. (~5 calls)

- [ ] **R6-T7** — `plugin/skills/implement_inline/SKILL.md:123` — the sibling execution path was
      not widened, so the documented alternative refuses the shape `implement` now accepts and
      names the wrong remedy.
      **Fails when:** `implement_inline/SKILL.md:123` still reads "Verify presence of research.md,
      design.md, tasks.md" with no exception, and steps 1.2/1.3 are unconditional full reads.
      `CLAUDE.md`'s workflow table and `implement/SKILL.md:14` advertise `/wb:implement_inline` as
      a legitimate substitute on any project directory; pointed at a round it stops on the missing
      reads, and its Step 2 "no phases" stop still names `/wb:create_tasks` as the fix, which is
      wrong for a round.
      **Acceptance (shape 3)**: dual grep — the unwidened phrasing at
      `implement_inline/SKILL.md:123` absent, and the remediation carve-out present at a named
      `file:line`, mirroring `implement/SKILL.md:118-128`. (~2 calls)

- [ ] **R6-T8** — `plugin/skills/validate_project/SKILL.md:66` — `validate_project` errors on
      every structural check of a round directory.
      **Fails when:** `/wb:validate_project docs/plans/<plan>/reviews/<date>-round-N/` runs.
      `SKILL.md:66-68` states "research.md, design.md and tasks.md are required";
      `reference/validation-checklist.md:7-8` checks both exist; lines 95-96 require `depends_on`
      links between them. A remediation plan's frontmatter
      (`adversarial-review/templates.md:118-127`) has no `depends_on` and neither file. Every one
      of those checks reports a critical error against a shape `implement` now treats as valid.
      **Acceptance (shape 3)**: dual grep — the unconditional requirement absent from
      `validate_project/SKILL.md:66` and `validation-checklist.md:7-8,95-96`, and a round-shape
      branch present at a named `file:line`. (~3 calls)

## Implementation notes

- **R6-T1 and R6-T4 are the two that fire on every single round**; R6-T2 fires on every round
  that reaches a first passing task. Treat those three as the blocking set.
- R6-T3 is the one that makes the loop non-terminating rather than merely noisy: an
  un-fixable finding keeps `adversarial-loop`'s gate from ever clearing.
- **Out of scope for this round, recorded so it is not lost**: the built-in `/code-review` leg
  resolved its base as the local `main` (`2a6fa62`), eleven commits behind `origin/main`
  (`46ef587`), and attributed the Step 2 branch-naming backstop to this diff. That is a defect in
  `adversarial-review` Step 4, not in `implement`, and belongs to the target-2 review.
