---
project: adversarial_loop
reviews: docs/plans/2026-09-17-adversarial_loop
round: 6
created: 2026-09-21
status: in-progress
total_tasks: 11
completed_tasks: 11
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

- [x] **R6-T6** — `plugin/skills/implement/SKILL.md:254-257` — the new top-insert journal rule
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
      remediation plan writes; grep must find that sentence. (~5 calls) (completed 2026-09-21 06:33)

- [x] **R6-T7** — `plugin/skills/implement_inline/SKILL.md:123` — the sibling execution path was
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
      `file:line`, mirroring `implement/SKILL.md:118-128`. (~2 calls) (completed 2026-09-21 06:51)

- [x] **R6-T8** — `plugin/skills/validate_project/SKILL.md:66` — `validate_project` errors on
      every structural check of a round directory.
      **Fails when:** `/wb:validate_project docs/plans/<plan>/reviews/<date>-round-N/` runs.
      `SKILL.md:66-68` states "research.md, design.md and tasks.md are required";
      `reference/validation-checklist.md:7-8` checks both exist; lines 95-96 require `depends_on`
      links between them. A remediation plan's frontmatter
      (`adversarial-review/templates.md:118-127`) has no `depends_on` and neither file. Every one
      of those checks reports a critical error against a shape `implement` now treats as valid.
      **Acceptance (shape 3)**: dual grep — the unconditional requirement absent from
      `validate_project/SKILL.md:66` and `validation-checklist.md:7-8,95-96`, and a round-shape
      branch present at a named `file:line`. (~3 calls) (completed 2026-09-21 07:03)

- [x] **R6-T9** — `plugin/skills/implement/SKILL.md:543` and
      `templates/modified-files-fragment.md:6` — R6-T4 branched Step 8 and its two templates for
      a phaseless round but left two further `Phase ${phase}` interpolations behind, so the round
      that fixed the defect still emits it twice.
      **Fails when:** `implement` finishes a round and reaches Step 9. `SKILL.md:543` writes
      `- [YYYY-MM-DD] Phase ${phase} complete using coordinated workers:` into Implementation
      Notes, and Step 7 emits `templates/modified-files-fragment.md:6`,
      `### 📝 Modified Files (Phase ${phase})`. A remediation plan has no phase
      (`SKILL.md:459`), so both render `Phase undefined`. Observed in this very round: the
      coordinator substituted `Round 6` by hand in `a66205f` because the template said `Phase`.
      `${phaseLabel}` already exists and is defined at `SKILL.md:459`; neither site uses it.
      **Acceptance (shape 3)**: dual grep — `grep -n 'Phase \${phase' plugin/skills/implement/
      SKILL.md plugin/skills/implement/templates/modified-files-fragment.md` returns both hits
      today (the RED); after the fix it returns nothing, *and* `${phaseLabel}` is present at both
      sites with its substitution rule reachable from each. (~3 calls) (completed 2026-09-21 15:43)

- [x] **R6-T10** — `plugin/skills/implement_inline/SKILL.md` Step 3E — the sibling execution path
      has no `git add -f`, and no `git add` at all, so it inherits the gitignore refusal
      wholesale: an inline run drops `tasks.md` and `journal.md` from every commit, silently.
      **Fails when:** `/wb:implement_inline` reaches its commit step on any plan under
      `docs/plans/`, which `.gitignore:7` ignores. R6-T2 fixed exactly this on `implement`
      (`SKILL.md:335-347`): plain `git add <plan-dir>/tasks.md` exits 1 with "The following paths
      are ignored", the `&&` chain breaks, and the failure **hides**, because `git status
      --short` does not list untracked ignored files. Confirmed by the reviewer:
      `grep -rn 'git add' plugin/skills/implement_inline/` returns nothing, so the path has no
      staging instruction to correct — it has none at all. Status edits are therefore never
      committed and the plan's record is lost.
      **Acceptance (shape 1 + shape 3)**: execute `git add --dry-run <a round tasks.md>` and
      assert exit 1 (the RED), then `git add --dry-run -f` and assert exit 0; *and* grep must
      find `git add -f` in `plugin/skills/implement_inline/` at a named `file:line`, which
      returns nothing today. The by-path rule and the prohibition on `git add -A` / `.` must be
      stated alongside it, as they are in `implement`. (~4 calls) (completed 2026-09-21 15:48)

- [x] **R6-T11** — `plugin/skills/update_status/templates/` — R6-T1's carve-out tells the skill
      to omit research and design rows for a round, but all three templates hardcode them, so the
      instruction and the artifact disagree.
      **Fails when:** `update_status` runs on a round and reaches its output.
      `templates/status-update-plan.md:8,13`, `templates/completion-summary.md:11,12` and
      `templates/frontmatter-fragments.md:5,14` each carry a **research.md** and a **design.md**
      section with no branch. R6-T1 conditioned the skill's prose at `SKILL.md:72` but left the
      templates unconditioned, and the round-6 verifier recorded the gap as real and unowned. A
      round therefore gets a status report listing two files that do not exist, or the "n/a" rows
      `SKILL.md:72`'s carve-out explicitly says not to write.
      **Acceptance (shape 3)**: dual grep — `grep -rn 'research\.md\|design\.md'
      plugin/skills/update_status/templates/` returns six unconditioned hits today (the RED);
      after the fix every surviving hit is on the phased branch, and a round branch is present at
      a named `file:line` in each of the three templates. The phased output must be unchanged.
      (~3 calls) (completed 2026-09-21 15:54)

## Implementation notes

- **R6-T1 and R6-T4 are the two that fire on every single round**; R6-T2 fires on every round
  that reaches a first passing task. Treat those three as the blocking set.
- R6-T3 is the one that makes the loop non-terminating rather than merely noisy: an
  un-fixable finding keeps `adversarial-loop`'s gate from ever clearing.
- **Out of scope for this round, recorded so it is not lost**: the built-in `/code-review` leg
  resolved its base as the local `main` (`2a6fa62`), eleven commits behind `origin/main`
  (`46ef587`), and attributed the Step 2 branch-naming backstop to this diff. That is a defect in
  `adversarial-review` Step 4, not in `implement`, and belongs to the target-2 review.

- [x] **R6-T12** — `plugin/skills/update_status/SKILL.md:174` — Step 5 applies the frontmatter
      fragments unconditionally to `research.md`, `design.md` and `tasks.md`, so on a round it
      instructs writing frontmatter into two files that do not exist — and R6-T11's templates now
      say the opposite.
      **Fails when:** `update_status` runs on a round and a confirmation carries it past Step 4.
      `SKILL.md:174` reads "apply them to research.md, design.md and tasks.md" with no branch,
      while `templates/frontmatter-fragments.md:12` — added by R6-T11 minutes earlier — says to
      skip both fragments for a round. One skill, two instructions, opposite directions; R6-T1
      conditioned the carve-out at `:72` but never Step 5. Separately, Step 4's trigger list at
      `:157-170` names "any `research.md` or `design.md` transition" and "`design.md` would reach
      `approved`" with no round branch. Those are disjunctive conditions that simply never fire
      on a round, so they misdirect no action — but they read as though the documents exist.
      **Acceptance (shape 3)**: dual grep — the unconditional "research.md, design.md and
      tasks.md" phrasing absent from Step 5, and a round branch present at a named `file:line`;
      the `:157-170` triggers conditioned so they cannot name a file a round lacks. The phased
      path must be unchanged. (~3 calls) (completed 2026-09-21 16:58)

- [ ] **R6-T13** — `plugin/skills/implement/SKILL.md:363-367` and the matching block at
      `implement_inline/SKILL.md:304-308` — the prose says a failed stage "breaks the `&&` chain"
      and the commit never runs, but the fenced block separates the three commands with
      newlines, so a failed `-f` stage lets `git commit` run anyway and commit **without** the
      plan files. One task, both files — same class, inherited verbatim from R6-T2.
      **Fails when:** any run reaches the commit step and the `git add -f` fails for any reason
      (a path typo, a removed file, a permissions error). Under newline separation the shell
      runs the next command regardless, so the commit lands carrying the code changes and
      missing `tasks.md` and `journal.md` — the checkbox flip and the journal entry are left in
      the working tree while the commit reports success. That is a **quieter** failure than the
      one the prose describes, and the prose's promise that "the commit never runs" is what
      stops a reader from checking.
      **Acceptance (shape 1)**: execute the block **as written** in a scratch repo with an
      ignored plan path and a stage engineered to fail; assert that today a commit is created
      without the plan files (the RED), and that after the fix no commit is created at all.
      (~4 calls)

### 📝 Modified Files (Round 6)

This round changed prompt documents, not code — there are no test files, and the gate is
`./plugin/scripts/lint` plus `./plugin/scripts/check`.

#### Skill and reference files

- `plugin/skills/update_status/SKILL.md` — R6-T1: remediation carve-out under BARRIER 1
- `plugin/skills/update_status/reference/error-handling.md` — R6-T1: `create_project` routing gated
- `plugin/skills/implement/SKILL.md` — R6-T2, R6-T3, R6-T4, R6-T6: `git add -f` staging, the
  attestation list, the Step 8 phase/`design.md` branch, the `[blocked]` marker and parent-journal rule
- `plugin/skills/implement/reference.md` — R6-T5: resume-path exemption
- `plugin/skills/implement/templates/manual-verification-request.md` — R6-T4: round branch
- `plugin/skills/implement/templates/phase-completion-report.md` — R6-T4: round branch
- `plugin/agents/task-worker.md` — R6-T3: declines an attestation task
- `plugin/agents/task-verifier.md` — R6-T3: routes an attestation FAIL to the checkpoint
- `plugin/docs/reference/journal-entries.md` — R6-T6: `[blocked]` marker, parent-journal rule
- `plugin/skills/implement_inline/SKILL.md` — R6-T7: carve-out, corrected remedy, journal handling
- `plugin/skills/implement_inline/reference.md` — R6-T7: resume path, `[blocked]` producer/consumer
- `plugin/skills/implement_inline/templates/manual-verification-request.md` — R6-T7: round branch
- `plugin/skills/implement_inline/templates/phase-completion-report.md` — R6-T7: round branch
- `plugin/skills/validate_project/SKILL.md` — R6-T8: phased-only qualifier on the required files
- `plugin/skills/validate_project/reference/validation-rules.md` — R6-T6, R6-T8: `[blocked]`
  exemption; `isRound` predicate and `validateRoundStructure()`
- `plugin/skills/validate_project/reference/validation-checklist.md` — R6-T6, R6-T8: `[blocked]`
  exception; two-shapes scoping and §9
- `plugin/skills/validate_project/templates/validation-report.md` — R6-T8: round row handling

**Quick verification commands:**

```bash
./plugin/scripts/lint --all
./plugin/scripts/check
```
