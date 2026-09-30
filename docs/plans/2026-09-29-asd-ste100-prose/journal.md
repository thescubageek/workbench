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

## 2026-09-30 00:39 — P2-T3 (closed)

- **Task/phase**: P2-T3 — `evals/wbte_check.py` and its planted-failure inputs with clean siblings
- **Landed**: the checker, with 4 bad inputs and 4 clean siblings in `evals/fixtures/planted/`. Before the checker existed, every input exited 2. Now each bad input exits 1 and each clean sibling exits 0. The reference doc passes. Files that end in `.txt` are chat output. The limits apply to all given files together
- **Commits**: see `P2-T3: add the WBTE metric checker`
- **Learned**: the first noun-cluster heuristic flagged verbs and names in real documents. It now treats words that end in -s as breaks, joins runs of capitalized words, and counts multi-word technical nouns from the reference doc as one word. A few false positives remain ("want lower skill quality"), so cluster counts are a trend signal, not a hard gate

## 2026-09-30 00:36 — P2-T2 (closed)

- **Task/phase**: P2-T2 — ignore rules: `.gitignore` gains `evals/runs/`, `__pycache__/`, `*.pyc`; new `.wblintignore` with `evals/fixtures/planted/`
- **Landed**: before the change, `lint --all` flagged a temporary planted file (MD022). After it, lint skipped the file and `lint --all` was clean. `test-lint` passed 15 of 15. The temporary file was removed
- **Commits**: see `P2-T2: ignore harness runs, bytecode, and planted fixtures`

## 2026-09-30 00:32 — P2-T1 (closed)

- **Task/phase**: P2-T1 — write `plugin/docs/reference/technical-english.md` (nine sections, exempt tokens copied from the parsers)
- **Landed**: the WBTE reference doc. Lint is clean, the prose has no semicolons, and no sentence has more than 20 words
- **Commits**: cdee6d5
- **Learned**: lint `--fix` (MD010) turns a literal tab inside a code block into spaces. The dictionary lookup uses `$'\t'` for that reason

## 2026-09-30 00:24 — P1-T3 (closed)

- **Task/phase**: P1-T3 — run the headless driver probe against the 2.1.1 tree (tests assumption A6)
- **Landed**: probe PASS in 59 s, exit 0. `research.md` reached `status: complete`, 4 of 6 facts are cited at the exact `file:line`, and the `✅ research.md updated` line is in stdout. The record is `thoughts/2026-09-30-harness-probe.md`. A6 is still `Pending` (the plan changes it only on failure). Verifier PASS
- **Commits**: see `P1-T3: record the headless driver probe`
- **Learned**: the stage skipped its sub-agent fan-out, as 2.1.1 allows when the whole surface is already read. So the probe does not show that headless runs can spawn sub-agents. The read boundary was off on this machine

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
