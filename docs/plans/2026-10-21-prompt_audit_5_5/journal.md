# Session Journal: prompt_audit_5_5

Reverse-chronological — **newest entry at the top. No entries yet.**

**Where a new entry goes: directly under the marker comment at the bottom of this preamble,
above every existing entry. Never appended to the end of the file.** This is not a style
preference. The session-start hook picks the most recent entry with
`grep -E '^## ' journal.md | grep -vE '\[YYYY|<YYYY|YYYY-MM-DD' | head -1` — the *first* heading
in the file. An entry written at the bottom is invisible to it, and the failure is silent and
inverted: the hook reports the oldest entry as current, so a resuming session is told the plan is
mid-research when design has already finished, or that an entry is `(open)` when its own
`(closed)` entry sits further down. `forge`, `daily-digest`, `resume_handoff` and
`create_handoff` inherit the same first-heading assumption. For the same reason, "the journal
tail" means the newest entry — which is at the top.

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

## 2026-10-23 05:00 — P4-T5 (closed)

- **Task/phase**: P4-T5 — the wording rules in create_project, resolve_questions, fetch-issues, daily-digest, and forge
- **Landed**: 9 barriers with reasons. 1 kept CAPS line, the daily-digest Iron Law (the PHI rule)
- **Commits**: the P4-T5 commit

## 2026-10-23 04:59 — P4-T4 (closed)

- **Task/phase**: P4-T4 — the wording rules in explore_design, create_mockup, and mockup-iteration
- **Landed**: 7 barriers with reasons, plain scope section and agent prompts. 0 CAPS lines
- **Commits**: the P4-T4 commit

## 2026-10-23 04:59 — P4-T3 (closed)

- **Task/phase**: P4-T3 — the wording rules in create_handoff and resume_handoff
- **Landed**: 3 barriers with reasons and the read-fully wording. 0 CAPS lines
- **Commits**: the P4-T3 commit

## 2026-10-23 04:58 — P4-T2 (closed)

- **Task/phase**: P4-T2 — the wording rules in update_status
- **Landed**: plain philosophy list, 2 barrier reasons, and the read-fully wording. 0 CAPS lines
- **Commits**: the P4-T2 commit

## 2026-10-23 04:58 — P4-T1 (closed)

- **Task/phase**: P4-T1 — the wording rules in the validation skills
- **Landed**: 4 barriers with reasons, the read-fully wording, and 0 CAPS lines in the four files
- **Commits**: the P4-T1 commit

## 2026-10-23 04:36 — P3-T9 (closed)

- **Task/phase**: P3-T9 — run the verifier trial to 3 repeats, apply the decision rule
- **Landed**: 18 of 18 defects on both models, 0 false failures. The verifiers stay on Sonnet 5.5. Ledger about $19.05
- **Commits**: the P3-T9 commit

## 2026-10-23 04:35 — P3-T8 (closed)

- **Task/phase**: P3-T8 — build the planted-defect verifier trial and run a pilot
- **Landed**: 8 cells, harness, and a pilot where both models are right in every cell. $0.73, ledger about $17.80
- **Commits**: the P3-T8 commit

## 2026-10-23 04:31 — P3-T7 (closed)

- **Task/phase**: P3-T7 — run the Batch 2 blind trial
- **Landed**: PASS in every cell, 200 runs, $1.13. Ledger about $17.07
- **Commits**: the P3-T7 commit

## 2026-10-23 04:30 — P3-T6 (closed)

- **Task/phase**: P3-T6 — build the Batch 2 blind trial
- **Landed**: 5 fixtures, 4 named trap cells, harness and scorer. Not yet run
- **Commits**: the P3-T6 commit

## 2026-10-23 04:29 — P3-T5 (closed)

- **Task/phase**: P3-T5 — the wording rules in tdd-discipline and verification-before-completion
- **Landed**: 4 lines plain. 0 CAPS lines in either skill
- **Commits**: the P3-T5 commit

## 2026-10-23 04:29 — P3-T4 (closed)

- **Task/phase**: P3-T4 — the wording rules in implement_inline/reference.md
- **Landed**: a plain DON'T list without the restated scope items, and the paging rule. 0 CAPS lines
- **Commits**: the P3-T4 commit

## 2026-10-23 04:28 — P3-T3 (closed)

- **Task/phase**: P3-T3 — the wording rules in implement_inline/SKILL.md
- **Landed**: the Q2-measured Scope list, single-marker BARRIER 1, and the read-fully wording. 0 CAPS lines
- **Commits**: the P3-T3 commit

## 2026-10-23 04:27 — P3-T2 (closed)

- **Task/phase**: P3-T2 — the wording rules in implement/reference.md and implement/prompts/worker-prompt.md
- **Landed**: plain DON'T list and plain worker constraints. 0 CAPS lines in `implement/`
- **Commits**: the P3-T2 commit

## 2026-10-23 04:27 — P3-T1 (closed)

- **Task/phase**: P3-T1 — the wording rules in implement/SKILL.md
- **Landed**: plain Scope list, single-marker BARRIER 1, reasons on BARRIER 2 and 3, and the read-fully wording. 0 CAPS lines
- **Commits**: the P3-T1 commit

## 2026-10-23 03:38 — P2-T6 (closed)

- **Task/phase**: P2-T6 — act on the Batch 1 verdict
- **Landed**: repeat 3 no loss. P2-T4 kept, and the repeat-2 loss is recorded as variance. Ledger about $15.94
- **Commits**: the P2-T6 commit

## 2026-10-23 02:40 — P2-T5 (closed)

- **Task/phase**: P2-T5 — Batch 1 harness gate on evals/fixture-large
- **Landed**: 2 repeats ($3.80, $4.45). Judge: repeat 1 no loss. Repeat 2 tasks.md lost design assumption A2. Ledger about $12.37
- **Commits**: the P2-T5 commit
- **Learned**: the P2-T4 diff does not touch assumption handling, so the loss is likely run-to-run variance. P2-T6 needs the user's decision

## 2026-10-23 02:39 — P2-T4 (closed)

- **Task/phase**: P2-T4 — the wording rules in create_tasks
- **Landed**: 3 single-marker barriers and plain prerequisites. 0 CAPS lines remain
- **Commits**: the P2-T4 commit

## 2026-10-23 02:38 — P2-T3 (closed)

- **Task/phase**: P2-T3 — the wording rules in create_design
- **Landed**: the scope section with its reason, 3 single-marker barriers, and the restatements removed. 0 CAPS lines remain
- **Commits**: the P2-T3 commit

## 2026-10-23 02:37 — P2-T2 (closed)

- **Task/phase**: P2-T2 — the wording rules in create_product_research
- **Landed**: 4 single-marker barriers, 1 kept CAPS line (the Documentarian Rule fence), and the restatements removed. 43 lines added, 76 removed
- **Commits**: the P2-T2 commit

## 2026-10-23 02:36 — P2-T1 (closed)

- **Task/phase**: P2-T1 — the wording rules in create_research
- **Landed**: 3 single-marker barriers, 1 kept CAPS line (the Documentarian Rule fence), and the restatements removed. 39 lines added, 73 removed
- **Commits**: the P2-T1 commit

## 2026-10-23 01:49 — P1-T10 (closed)

- **Task/phase**: P1-T10 — release 3.0.1: CHANGELOG entry and both manifests
- **Landed**: the [3.0.1] entry and version 3.0.1 in both manifests. ./plugin/scripts/check passed every gate. Not tagged and not pushed, pending the user
- **Commits**: the P1-T10 commit

## 2026-10-23 01:47 — P1-T9 (closed)

- **Task/phase**: P1-T9 — Batch 0 gate: mechanical checks and a headless spawn probe
- **Landed**: trials/2026-10-23-batch0-probe/RESULTS.md. The six mechanical checks PASS, all 7 agents ran at their tier, and the bare name was rejected. Cost $0.27, ledger $3.92
- **Commits**: the P1-T9 commit

## 2026-10-23 01:46 — P1-T8 (closed)

- **Task/phase**: P1-T8 — gate lines delegate to model-help, and the other tier text names the 5.5 models
- **Landed**: 7 gate lines, explore_design's self-check, resume_handoff's example, the forge model plan, and 2 daily-digest lines. All six Phase 1 mechanical checks PASS
- **Commits**: the P1-T8 commit

## 2026-10-23 01:46 — P1-T7 (closed)

- **Task/phase**: P1-T7 — model-help roster, ladder, mapping, baselines, and anchors for the 5.5 models
- **Landed**: the 5.5 roster and prices, one Opus, the ladder Haiku 5.5 → Sonnet 5.5 → Opus 5.5 → Fable 5.1, Opus 5.5 baselines, and new anchors. `model-help` has 0 roster hits
- **Commits**: the P1-T7 commit
- **Learned**: a fact that compares with an old model ("Opus 5 at high") trips the roster check, so it now says "the previous Opus"

## 2026-10-23 01:44 — P1-T6 (closed)

- **Task/phase**: P1-T6 — effort for each rung of the `implement` tier ladder, and remove the haiku-effort rule
- **Landed**: the tier table with an Effort column, the escalation step and prompt at the rung's effort, and the `claude-opus-5-5[1m]` example. `haiku-effort-rule` 0 PASS
- **Commits**: the P1-T6 commit

## 2026-10-23 01:43 — P1-T5 (closed)

- **Task/phase**: P1-T5 — agent frontmatter to the design's Data Model table
- **Landed**: `effort: medium` in codebase-locator, pattern-finder, and task-worker. The other 4 agents already matched. `agent-tiers` 0 PASS
- **Commits**: the P1-T5 commit

## 2026-10-23 01:43 — P1-T4 (closed)

- **Task/phase**: P1-T4 — `wb:` names in the prose spawns of `implement`
- **Landed**: 6 spawn lines in `implement/SKILL.md` and `implement/prompts/`. `prose-spawns` 0 PASS
- **Commits**: the P1-T4 commit

## 2026-10-23 01:43 — P1-T3 (closed)

- **Task/phase**: P1-T3 — `wb:` spawn names and no spawn `model` in the 6 sub-agent-prompts.md files
- **Landed**: 20 spawn blocks now read `subagent_type: "wb:<name>"` with no `model`. The 2 general-purpose spawns are unchanged. `spawn-names` 0 and `spawn-models` 0 PASS
- **Commits**: the P1-T3 commit

## 2026-10-23 01:41 — P1-T2 (closed)

- **Task/phase**: P1-T2 — write checks/prompt-checks.sh and its planted-failure test
- **Landed**: the 9 checks and a 42-case contract test. The baselines are in tasks.md Implementation Notes
- **Commits**: the P1-T2 commit
- **Learned**: the haiku-effort line in `adversarial-review/prompts.md:165` backticks `haiku`, so the first regex missed it. The contract test now plants both forms

## 2026-10-23 01:40 — P1-T1 (closed)

- **Task/phase**: P1-T1 — capture the token baseline before any Phase 1 edit
- **Landed**: baseline-tokens-3.0.0.txt (wb@inline 3.0.0). The 14-stage on-invoke sum is ~64.1k, recorded in tasks.md Implementation Notes
- **Commits**: the P1-T1 commit

## 2026-10-22 20:48 — create_tasks (closed)

- **Task/phase**: P0-T4 — execution plan for prompt_audit_5_5
- **Landed**: tasks.md with 6 phases and 44 implementation tasks (48 with P0), one phase per design batch, each with its own gate and a full checkpoint. inventory-2026-10-22.txt holds the line numbers at d2ba6ab
- **Commits**: none (plan files are gitignored and not yet promoted)
- **Learned**: CLAUDE_CODE_PLUGIN_DIRS on this machine loads the ankara plugin into headless runs, so every harness and probe command uses `env -u CLAUDE_CODE_PLUGIN_DIRS`. `judge.py --within` judges nothing on a research-only run, so Phase 5 uses the before/after mode. Spend so far $3.65. Next stage: /wb:implement

## 2026-10-22 20:25 — create_design (closed)

- **Task/phase**: P0-T3 — design for prompt_audit_5_5
- **Landed**: design.md approved by the user on 2026-10-22 (status: approved). Option B in six batches (0 to 5), each with its own gate. Batch 0 ships as 3.0.1, Batches 1 to 5 as 3.1.0
- **Commits**: none (plan files are gitignored and not yet promoted)
- **Learned**: the harness supports `--stages` and a one-tree run without `--after`, which can lower gate cost. Next stage: /wb:create_tasks

## 2026-10-22 19:58 — create_research follow-up: Q1 and Q2 probes (closed)

- **Task/phase**: P0-T2 follow-up — Q1 (per-spawn effort) and Q2 (WBTE lite rule 6) probes, Q3 and Q4 recorded
- **Landed**: research.md Follow-up Research section. Q1–Q4 resolved, with decisions in design.md (## Technical Decisions, Resolved Decisions). Trial record in trials/2026-10-22-q2-blind-trial/. Two knowledge entries added
- **Commits**: none (plan files are gitignored; knowledge.md is changed in the working tree only)
- **Learned**: a spawn `effort` reaches the API. Plain barrier and scope wording showed no loss on Opus 5.5 and Sonnet 5.5 (320 runs, $3.62). About $26 of the $30 eval budget remains. Next stage: /wb:create_design

## 2026-10-21 18:47 — create_research (closed)

- **Task/phase**: P0-T2 — research for prompt_audit_5_5
- **Landed**: research.md (status complete), from 6 read-only agents and one live probe. Bare `subagent_type` names fail in Claude Code 2.1.303. 4 open questions (Q1–Q4) block the design.
- **Commits**: none (plan files are gitignored and not yet promoted)
- **Learned**: Claude Code 2.1.303 documents a per-spawn `effort` parameter, which contradicts Gabe's 2.1.285 measurement. WBTE lite rule 6 constrains barrier and caps changes. Next stage: /wb:create_design
