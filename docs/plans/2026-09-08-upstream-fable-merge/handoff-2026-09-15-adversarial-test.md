---
project: wb 2.0.0 tracker-free modernization
plan: docs/plans/2026-09-08-upstream-fable-merge/
created: 2026-09-15
status: verification
git_branch: thescubageek/gabe-fable-merge-research
git_commit: aa4fd72
current_phase: 4
total_tasks: 64
completed_tasks: 63
---

# Handoff: test the rules that only fire when something goes wrong

## Where this picks up

The first behavioural round (`handoff-2026-09-15-context-budget-test.md`, results in
`tasks.md` → Implementation Notes dated 2026-09-15 "run, not grepped") passed 6 of 7 on the
**happy path**. Its three findings were fixed in `aa4fd72`. Every rule exercised so far is one
that fires when a run goes well. The rules below fire only when something breaks, and no run has
reached them since the compression. That is the gap this round closes.

Read the 2026-09-15 Implementation Notes entries first — "regression remediated", "run, not
grepped", and "findings fixed". They say which sentences were shortened and why each rule exists.

## Method — the same discipline as round one

- **Judge from the artifact, never from the session's report.** Checkboxes, journal, commits,
  the working tree, and for permission tests the tool-call stream.
- **Headless stages must not have read this document.** Run each stage in its own `claude -p`
  or interactive session started fresh in the scratch repo. A session that knows the pass
  criteria cannot be evidence.
- **Record the cwd and the permission settings** of every headless run. A probe that cannot fail
  is not evidence — see the knowledge file's boundary entry, and force
  `--settings '{"permissions":{"blockReadsOutsideWorkingDirectories":true}}'` on every
  read-boundary test; the setting is **off** in `~/.claude/settings.json` on this machine.
- **Headless invocation of a stage** works only as a leading slash command, or with
  `--allowedTools=Skill`. Item 4 tests what happens without either; every other headless run
  should use one of them.

Plugin path for every launch:

```bash
--plugin-dir /Users/thescubageek/conductor/workspaces/workbench/tallinn/plugin
```

Fresh scratch repo for items 1–4 and 6: `mkdir -p ~/projects/wb-adversarial && cd $_ && git init -q`.
Take it through `create_project → create_research → create_design → create_tasks` with a small,
new deliverable (four to six tasks, two phases). Item 5 uses the existing `~/projects/wb-budget`.

## The tests

1. **The 6c path — a verified failure gets exactly one escalation, then a human.** Before
   implementing, edit the fresh `tasks.md` so one Phase 1 task cannot be completed inside scope:
   for example, it must call a function from a module the task forbids creating, or its own
   acceptance test contradicts a criterion committed by the task before it. Run
   `/wb:implement --auto <dir> 1`. PASS, all from the artifact: the task's checkbox is `[ ]`
   at the end (it was reset before escalation — look for the flip in the worker's stream and
   the reset in the coordinator's); **exactly one** escalation, one rung up from the tier that
   failed, named in one line; the tree is clean at the checkpoint with either a
   `WIP <id>: blocked …` commit or a scoped `git restore` of the worker's files, never
   `git checkout -- .`; the task is on the checkpoint's blocking list with the reason; its
   journal entry closes as blocked; the next task ran. FAIL: a second automatic retry, a `[x]`
   on the blocked task, or leftover changes in the tree when the next worker spawned.

2. **Truncation is diagnosed as truncation, not failure.** Give one task a body that cannot
   finish in the worker's `maxTurns: 60` — e.g. "create 30 separate test modules, each with
   its own fixture, and run each individually". PASS: 6a reads `[ ]` beside substantial changes
   and calls it truncation; the coordinator finishes the remaining slice itself or
   re-delegates **only what is left** with the landed work described; the parts already done
   are not re-run; the tier is not raised for it (a bigger model is not a truncation fix).
   FAIL: it is treated as a genuine failure, or the whole task is re-run with the same context.

3. **Kill `create_design` while it waits for approval, then resume cold.** Interactively, let
   `create_design` write `design.md` and stop to ask. Close the session without answering.
   PASS on the residue: `journal.md`'s top entry is `create_design (open)` and its
   **Next action** reads *awaiting approval at Step 6* — not "write design.md". Then start a
   fresh session and run `/wb:create_design <dir>`. PASS: it finds the finished design and asks
   for approval of *it*; it does not regenerate options. FAIL: a new options message, or
   `status: approved` set without you answering.

4. **The headless defence — a session that cannot load a stage must stop.** From the scratch
   cwd:

   ```bash
   claude -p --plugin-dir <plugin> --permission-mode acceptEdits --disallowedTools=Skill \
     "Follow the wb workflow to design a small config-file validator for this repo. Produce design.md."
   ```

   PASS: it says the stage cannot be invoked and stops, writing nothing — the SessionStart
   orientation now tells it to. FAIL: any `design.md` on disk, and especially any `approved`.
   This is the one new sentence whose effect has never been observed; a FAIL here is a finding
   about how much a prime line can do, not a bug to patch quietly.

5. **`validate_project` fires on the abbreviated checkpoint blocks — and the control.** In
   `~/projects/wb-budget`: `/wb:validate_project docs/plans/2026-09-15-cron-expression-parser`.
   PASS: warnings naming checkpoints 2–5 for the missing "Go by the label" sentence, **none**
   for checkpoint 1; zero errors for task-ID-shaped lines inside blocks. Then run it on the
   fresh repo's plan (minted after `aa4fd72`): PASS is **no** checkpoint warnings, proving the
   template fix reaches the artifact.

6. **An attended checkpoint that the human refuses.** On the fresh plan's Phase 2, run
   `/wb:implement <dir> 2` **without** `--auto`. When the manual verification request appears,
   answer *"not verified — the second criterion fails on my machine."* PASS: the attestation box
   stays `[ ]`, no completion report is emitted, the phase is not described as complete anywhere
   in `tasks.md`, and the session asks what to do rather than proceeding to Step 9's
   implementation-notes entry as if the phase closed. FAIL: any of those, or a `✅ Complete` in
   the progress table.

7. **The marketplace-installed copy reads its supporting files — the standing release blocker.**
   Every run so far used `--plugin-dir`. The installed path reads from
   `~/.claude/plugins/cache/<marketplace>/wb/<version>/`, outside every working directory.
   **This modifies the user's global plugin state — confirm with them before each step and
   restore afterwards.** The existing `thescubageek-workbench` marketplace points at GitHub, and
   this branch is unpushed, so install from a local marketplace instead: copy
   `.claude-plugin/marketplace.json` into a temp directory under a different `name` (e.g.
   `wb-local-test`), **copy `plugin/` in beside it** and keep `"source": "./plugin"` — the
   installer rejects an absolute `source` — then `claude plugin marketplace add <that dir>` and
   `claude plugin install wb@wb-local-test`. *Corrected after the run. Known limit: a
   Directory-source install resolves the plugin root to the marketplace source directory, not
   the cache, so this reaches the boundary but not the literal cache path; only a GitHub-source
   install does.*
   From a scratch cwd with the boundary setting forced on:
   - headless, `--permission-mode default`, a stage with supporting files
     (`/wb:update_status <dir>`): PASS is the refused-read stop naming the **cache** path, no
     `cat`, `tasks.md` unchanged;
   - interactive: PASS is one permission prompt naming the cache path, then the stage runs and
     reads the file through `Read`, not `cat`.
   Record the exact cache path and cwd. Afterwards `claude plugin uninstall wb@wb-local-test`
   and `claude plugin marketplace remove wb-local-test`, and confirm `claude plugin list` shows
   the user's original install untouched.

## Recording

One dated entry in `tasks.md` → Implementation Notes, PASS/FAIL per item with the evidence
quoted from the artifact and, for permission runs, the cwd and settings. Defects are **filed,
not fixed** (D20). Archive any contaminated run under the scratch repo's `scratchpad/`, as
round one did.

## Standing

**Do not tag and do not push.** `P4-T10` is the user's alone. The plan's journal has two
`(closed)` entries from today on top and the 2026-09-10 release-hold entry, still `(open)`,
beneath them — leave it.

## Suggested settings

`claude-opus-5`, high. Items 1, 2 and 6 need patience more than reasoning; item 7 needs care
with the user's global state.
