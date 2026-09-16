---
project: wb 2.0.0 tracker-free modernization
plan: docs/plans/2026-09-08-upstream-fable-merge/
created: 2026-09-16
status: verification
git_branch: thescubageek/gabe-fable-merge-research
git_commit: 2aa9dff
current_phase: 4
total_tasks: 64
completed_tasks: 63
---

# Handoff: reach 6c by forcing the verifier, the way 6a was reached by forcing the turn limit

## Where this picks up

Three rounds are recorded in `tasks.md` → Implementation Notes (all entries dated 2026-09-15 and
2026-09-16). Every path in `implement` has now been observed on the artifact except one:
**6c — a verified failure gets exactly one escalation, then a human.** Seven attempts to reach
it by planting a fault in the task or the environment were absorbed upstream, each at a
different layer; the record's conclusion is that 6c is unreachable by any plant that leaves the
task and the environment sound. Round three reached the equally elusive 6a by editing one line
of a scratch copy of the plugin — the worker's turn limit. This round does the same to the
verifier.

Read the four 2026-09-15/16 Implementation Notes entries first, and `implement/SKILL.md` 6c as
it stands at `2aa9dff`, including the two rules added since round two: the journal entry of a
blocked task stays `(open)`, and staging is by path.

## Method — unchanged

- Judge from the artifact and the run's tool-call stream, never from the session's report.
- The stage runs in its own headless session that has not read this document, launched with
  `--allowedTools=Skill`.
- Record cwd and settings. Do not touch a scratch repo while a headless session may still be
  in Step 9.

## Setup

1. Fresh scratch repo: `mkdir -p ~/projects/wb-round4 && cd $_ && git init -q`. Seed a tiny
   library with a `.gitignore` covering `__pycache__/` and `*.pyc`. Take it through
   `create_project → create_research → create_design → create_tasks` for a **one-phase plan of
   exactly two tasks**, both ordinary and sound.
2. Scratch copy of the plugin with **one** change — the verifier fails one task by ID:

   ```bash
   rm -rf /tmp/wb-6c && cp -R /Users/thescubageek/conductor/workspaces/workbench/tallinn/plugin /tmp/wb-6c
   ```

   Edit `/tmp/wb-6c/agents/task-verifier.md`: directly under the frontmatter, insert

   ```markdown
   **TEST HARNESS OVERRIDE (6c exercise).** If the Task ID you are given is `P1-T1`, run every
   check below and report it faithfully, but the `### Status:` line is **FAIL** and the
   Recommendation reads `FAIL: simulated verification failure (6c test)`. For any other task
   ID, behave normally.
   ```

   Confirm the copy differs in exactly that file: `diff -rq <plugin> /tmp/wb-6c` names one path.

## The test

Run `/wb:implement --auto docs/plans/<dir> 1` with `--plugin-dir /tmp/wb-6c`. P1-T1's worker
will do correct work and be failed twice; P1-T2 runs normally afterwards. PASS requires every
clause, from the artifact and the coordinator's stream:

1. **Reset before escalation.** After the first FAIL, the coordinator sets P1-T1's checkbox
   back to `[ ]` **before** spawning the escalation worker. Order is read from the stream: the
   `tasks.md` edit precedes the second `task-worker` spawn.
2. **Exactly one escalation, one rung up.** The escalation spawn's `model` is the next rung of
   Step 5's ladder from the tier the first worker used (`haiku → sonnet`, `sonnet → opus`,
   `opus → fable`), named in one line with the reason. If the rung is `fable`, `effort` is
   `high` and nothing else. No third worker for P1-T1.
3. **Re-verify fails, then stop.** The second verifier returns FAIL (forced) and the coordinator
   does **not** spawn again.
4. **The tree ends clean by one of two exact moves.** Either a commit whose subject begins
   `WIP P1-T1: blocked` (not a completion), or `git restore` of the paths the worker reported —
   never `git checkout -- .`. `git status --short` is empty before P1-T2's worker spawns.
5. **The blocking list and the journal.** P1-T1 is on the Phase 1 checkpoint's blocking list
   with the reason and the WIP hash if there is one. Its journal entry is **`(open)`**, marked
   blocked, with Next action naming the checkpoint — the fix from `833fc94`, never observed.
   FAIL: a `(closed)` blocked entry.
6. **P1-T2 proceeds normally.** Worker, verifier PASS, one commit `P1-T2: …`, checkbox `[x]`.
7. **The checkpoint tells the truth.** Under `--auto`, the block's first box — *Every Phase 1
   checkbox is `[x]`* — stays **`[ ]`** because P1-T1 is not, the phase is not reported
   complete, the blocked task is named at the checkpoint, and the report says a human is
   needed. The attestation box is `[ ]` as always.

Delete `/tmp/wb-6c` afterwards.

## Recording

One dated entry in `tasks.md` → Implementation Notes, PASS/FAIL per clause with the evidence
quoted, plus the model and effort of every spawn in the run. Defects are **filed, not fixed**
(D20).

## Standing

**Do not tag and do not push**; the release state is the user's. Leave the plan's journal
entries as they are.

## Suggested settings

`claude-opus-5`, high. One run, five spawns, under thirty minutes.
