# Session Journal: upstream-fable-merge

Append-only, reverse-chronological — newest entry at the top.

**Entries open when work starts, not when it ends.** A session does not get to choose how it
ends: a token limit, a closed laptop, or a crashed harness runs no shutdown step. An entry
written only at completion would be silent in exactly those cases, and worse than silent — its
tail would still show the last *finished* phase, so the next session would read a confident,
stale record and never learn that work stopped mid-task. Opening on entry makes the default
residue of an abrupt kill correct: an open entry naming what was being attempted and what came
next.

An open entry beside uncommitted changes means an interrupted task. An open entry beside a
clean tree means a session that simply moved on. The working tree is the authority, never this
file.

> Headings end in a literal `(open)` or `(closed)` — that suffix is what the session-start
> hook and the other readers match on. Converted from the earlier `— OPEN —` shape 2026-09-09,
> after Test D found the two disagreed.
>
> **This file starts at 2026-09-08 19:20**, after `P4-T9`. Phases 0–4 ran without it — the
> `P3-T7`/`P3-T8` wiring shipped but was never exercised, which is itself one of the review
> findings below. There is no earlier history to reconstruct and none is invented here.

## 2026-09-15 16:46 — context-budget recovery (closed)

- **Task/phase**: phase 4; 63 of 64, unchanged. Not a task — remediation of the 2026-09-15
  measured regression (fourteen-stage on-invoke 58.4k), run from a handoff.
- **Next action**: `P4-T10` stays held — see the 2026-09-10 entry below, which remains open by
  design. Nothing tagged, nothing pushed.
- **Started at**: `a7e9c64`
- **Landed**: 58.4k → 54.0k with every one of the eight protected rules verified by grep; lint
  clean, tag dry-run clean, hook reporting position. Full record, per-stage table and filed
  findings in `tasks.md` → Implementation Notes, 2026-09-15 "regression remediated". Written at
  close: this session did not open an entry when it started, a lapse of the convention it spent
  the afternoon editing.

## 2026-09-10 15:05 — release held on the installed-plugin read test (open)

- **Task/phase**: phase 4; 63 of 64. `P4-T10` (tag `wb--v2.0.0`) is the only unchecked task and
  is deliberately held.
- **Next action**: evaluate the results of the follow-up handed to a separate Claude testing
  session. Item 1 is the release blocker — whether a *marketplace-installed* 2.0.0 can read its
  own supporting files out of `~/.claude/plugins/cache/...` with
  `blockReadsOutsideWorkingDirectories: true`. Every prior read test used `--add-dir` or a
  `--plugin-dir` checkout, so none of them exercised the installed path.
- **Started at**: `7d155de`

**Why the hold.** D2's progressive disclosure has each skill read supporting files on demand.
Under `--plugin-dir` those sit inside the working directory. Installed from the marketplace they
sit in the version-keyed cache, outside every working directory. If that read is blocked, the
skills degrade to whatever `SKILL.md` alone carries — silently, and only for installed copies,
which is every copy but this one. Tagging before knowing that would ship the break.

**If it comes back clean**: tag and push (both need the user's explicit go-ahead).
**If it comes back blocked**: this is a design problem, not a packaging one. The candidate fixes
— inline the supporting content back into `SKILL.md`, ship a postinstall that copies into the
project, or document an `additionalDirectories` requirement — differ enough that the answer
should decide it, and the −44.9% context result is what is at stake.

## 2026-09-09 16:10 — Test E, end-to-end, paused mid-implement (closed)

- **Task/phase**: post-`P4-T9` live testing; `P4-T10` (tag) still `[ ]`
- **Next action**: decide how Step 5's worker-tier ladder should read, given the Task tool's
  `model` enum is `sonnet | opus | haiku | fable` and cannot express `claude-opus-4-8[1m]` or
  `claude-opus-5`. Then finish Test E: `/wb:implement` Phase 1 checkpoint → Phase 2 →
  `/wb:validate_execution`, in `/tmp/wbe`.
- **Started at**: `bb49770`

**Tests A–D pass.** A: split reads prompt-free with `--add-dir`. B: all three aliases announce
once and load the right canonical. C: with reads blocked, `create_tasks` stopped and named the
fix instead of writing a plan from memory. D: abrupt kill leaves a correct open entry, and
`implement_inline` wrote the canonical `(open)` shape unprompted once the skill stated it.

**Test E in progress** and already worth its cost — it found the design-status vocabulary break
(four values across five skills, nothing advancing `draft`), the Pending Decisions table's
missing `State` column, the duplicated body `**Status**` line, and the Task-tool model enum.

**Open decision, blocking nothing else**: Step 5 names two Opus rungs the spawn tool cannot
distinguish. Options — collapse the ladder to `haiku → opus → fable`; keep the generations but
express the upshift as `effort` rather than `model`; or pin a generation in
`agents/task-worker.md` and drop the per-spawn claim. The third contradicts D13, which is the
whole reason the worker carries no `model:`.

**Closed 2026-09-10.** The blocking decision resolved in `ac950ed`: the ladder is now stated
in values the spawn tool actually accepts, so no rung names a model the Task tool cannot
express. `cb8a9af` fixed the design-status vocabulary this entry found; `5fb7025` fenced the
journal template's example entries after they were found to be live headings.

**Test E itself did not finish here.** It moved to a separate Claude testing session, which was
hard-closed mid-run, resumed from this journal, and landed `P2-T2` as `3fa7e24` before stopping
at the Phase 2 checkpoint. That run is the D8 acceptance test — recovery passed, bootstrap still
needs a re-run against a journal created after `5fb7025`. Recorded in `tasks.md` Phase 3 as
`[~]`. The remaining Test E steps in `/tmp/wbe` are outstanding and tracked as follow-up item 3.

This entry closes with a clean tree because its work is committed, not because the test passed.

## 2026-09-09 12:20 — live testing of the Phase 2 criteria, and the redesign it forced (closed)

- **Task/phase**: post-`P4-T9`; `P4-T10` (tag the release) still `[ ]`
- **Next action**: run the three remaining live tests — alias 3 (`/wb:implement_tasks`), Phase 3's
  abrupt-kill acceptance test, and Phase 4's end-to-end scratch-repo run. Then `/wb:update_status`
  and `P4-T10`.
- **Started at**: `45e849c` (working tree, uncommitted)

**Testing falsified A4 and took the progressive-disclosure read mechanism with it.** Five headless
probes, each with its cwd recorded: a Read of a supporting file is denied under `--plugin-dir`,
denied for a marketplace install reading its own root, passes only with `--add-dir`, and
path-scoped `Read(<plugin-root>/**)` does not cross the boundary either — a plugin cannot
self-grant. The Phase 0 probe that recorded *Validated* never wrote down its working directory,
which is the only field that decides the result.

Separately: the Read tool has no section parameter, so the 33 "read the `## X` section"
instructions had no correct implementation. Observed live — asked for a section starting at
line 291, a model read 180–239.

**What landed**: 14 supporting files split into 48 single-purpose ones under `templates/`,
`prompts/` and `reference/`, so a whole-file read *is* the scoped read (zero section-scoped
instructions remain); `allowed-tools` set to each skill's real surface, which pre-approves
mutations and is called out as Breaking; a hard-stop rule in all 16 manifests so a refused read
reports instead of improvising; A4 corrected to false across design.md, tasks.md, the baseline
thoughts doc and the skills guide, with all five probe runs and their cwds recorded; the boundary
documented in README and the migration notes; two `wb-prime.sh` fixes (name-ordered plans, word-
boundary elision); two new knowledge entries.

**Cost, honestly**: fourteen-stage invocation went 46.8k → 51.1k (+9.2%), still −39.8% on
baseline and 8.3k inside the bar. Per-run cost moves the other way and is the number the split
was for.

**Upstream does not solve any of this** — same defect at a third the surface, and its
`CHANGELOG.md:176` makes the claim these probes disprove. Divergence is deliberate.

## 2026-09-08 19:20 — adversarial review of Phases 1–4, and the fixes it produced (closed)

- **Task/phase**: post-`P4-T9` review; `P4-T10` (tag the release) still `[ ]`
- **Next action**: run the deferred live checks — Phase 2's `--plugin-dir` alias/prompt-free
  read, Phase 3's abrupt-kill acceptance test, Phase 4's end-to-end scratch-repo run — then
  `/wb:update_status` and `P4-T10`
- **Started at**: `45e849c`

**Ten findings; eight fixed in the tree, two need a live session.** Detail in the
Implementation Note dated 2026-09-08 below.

Fixed: `wb-prime.sh`'s `|| echo 0` arithmetic crash and its `[ -d .git ]` worktree blindness;
twelve unscoped checkbox counts; `implement` 6c's clean-tree and checkbox-reset holes; the
generated plan skeleton's ID-less task lines; stale/garbled maintainer docs; the deprecated
name in `commands-reference`'s pipeline diagram; the Fable model ID; 70 unprefixed `/wb:`
commands.

Still open: the three unrun manual criteria, and this plan's own `status:` / `git_commit`
frontmatter, which `/wb:update_status` reconciles once `P4-T10` lands.
