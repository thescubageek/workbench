# Session Journal: asd-ste100-prose

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

## 2026-09-30 00:17 — P1-T2 (closed)

- **Task/phase**: P1-T2 — build `evals/fixture/` (project, QUESTION.md, expected.json, plan-seed)
- **Landed**: `linkcheck` fixture project (4 Python files and a README, 6 facts F1–F6), `QUESTION.md`, `expected.json` (id, fact, ref, contains), `plan-seed/` from the 2.1.1 `create_project` templates. Verifier PASS
- **Commits**: see `P1-T2: build the evals fixture`
- **Learned**: the 2.1.1 `research`, `design` and `tasks` templates fail markdownlint as written (no blank lines around headings and lists). The seeds were lint-fixed. The templates under `plugin/` were not changed (follow-up)

## 2026-09-30 00:16 — P1-T1 (closed)

- **Task/phase**: P1-T1 — promote the plan directory into git
- **Landed**: `git add -f docs/plans/2026-09-29-asd-ste100-prose/` (README, research, design, tasks, journal)
- **Commits**: see `P1-T1: promote the asd-ste100-prose plan`

## 2026-09-30 00:03 — create_tasks (closed)

- **Task/phase**: P0-T4 — execution plan for asd-ste100-prose
- **Landed**: tasks.md — 7 implementation phases, 34 tasks (38 with Phase 0), Phase 1 is a tracer bullet for the headless harness driver (A6)
- **Commits**: none (plan files uncommitted; P1-T1 promotes them)
- **Learned**: Objective 2 in 2.2.0 is limited to files the harness exercises; other non-shared skill files move to the post-3.0.0 pass

## 2026-09-29 23:56 — create_tasks (open)

- **Task/phase**: P0-T4 — execution plan for asd-ste100-prose
- **Next action**: generate the phased plan, then present it at Step 6
- **Started at**: 4b32306

## 2026-09-29 23:55 — create_design (closed)

- **Task/phase**: P0-T3 — design for asd-ste100-prose
- **Landed**: design.md `status: approved` — Option A (reference doc + always-on rule card), name wb Technical English (WBTE), eval harness under `evals/`, A1–A6 pending
- **Commits**: none (plan files uncommitted)

## 2026-09-29 23:33 — create_design (open)

- **Task/phase**: P0-T3 — design for asd-ste100-prose
- **Next action**: awaiting approval at Step 6 — design.md written (Option A, wb Technical English); on approval set `status: approved` and close this entry
- **Started at**: 4b32306

## 2026-09-29 17:45 — create_research (closed)

- **Task/phase**: P0-T2 — research for asd-ste100-prose
- **Landed**: research.md (status: complete) — prose surfaces, existing rules and enforcement, cross-skill rule mechanisms, STE metrics, ASD-STE100 facts and licence, 3.0.0 overlap; Q1–Q5 open
- **Commits**: none (plan files uncommitted)
- **Learned**: local `main` ref is stale at 2a6fa62; compare against `origin/main`. 3.0.0 was once numbered 2.2.0

## 2026-09-29 17:36 — create_research (open)

- **Task/phase**: P0-T2 — research for asd-ste100-prose
- **Next action**: spawn the Step 4 agents, then synthesize into research.md
- **Started at**: 46ef587b084ea4d84a8a9b4e5b0770778903ba9b
