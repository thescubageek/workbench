---
project: upstream-fable-merge
created: 2026-09-08
last_updated: 2026-09-08
handoff_reason: Planning and decision-resolution complete; implementation starts in a fresh session
git_commit: b9025662a57fd8ef3000454c7f4e2cabae4db427
git_branch: thescubageek/gabe-fable-merge-research
repository: thescubageek/workbench
author: wolfpacksteve@gmail.com
next_command: "/wb:implement_tasks docs/plans/2026-09-08-upstream-fable-merge/ 0"
session_model: claude-opus-5
session_effort: high
worker_default_model: claude-opus-4-8[1m]
open_decisions: none
---

# Handoff: wb 2.0.0 tracker-free modernization — ready to implement

## Quick Start

```bash
cd /Users/thescubageek/conductor/workspaces/workbench/tallinn
# The plan is self-contained. Read in this order; this handoff is only orientation:
#   docs/plans/2026-09-08-upstream-fable-merge/README.md   (map)
#   docs/plans/2026-09-08-upstream-fable-merge/design.md   (D1–D20 + Resolved Decisions)
#   docs/plans/2026-09-08-upstream-fable-merge/tasks.md    (62 tasks, 5 phases)
/wb:implement_tasks docs/plans/2026-09-08-upstream-fable-merge/ 0
```

**No open decisions.** PD2, PD3, PD4 and assumption A1 were all resolved 2026-09-08 via
`/wb:resolve_questions`; every gate in `tasks.md` is cleared. Start at Phase 0.

## Model

| Role | Setting | Notes |
| ---- | ------- | ----- |
| **This session** | **Opus 5 / high** | Elect **xhigh** on `P3-T1`–`P3-T3`, `P3-T10`, `P4-T1` only. Not `max`. Do not churn tiers between phases. |
| **Coordinated worker default** | **Opus 4.8 1M — `claude-opus-4-8[1m]`** | The **1M variant**, not base `claude-opus-4-8`. This is a plan *output* (PD2), written into the tier rule by `P2-T15`. |
| Worker upshift rung | Opus 5 | Coordinator judgment, for architectural or cross-cutting tasks |
| Worker mechanical tier | Haiku | Mechanical only; never annotate `effort` on a haiku spawn |
| Fable | Election only | Never a first spawn. Only after a verified failure, always at `effort: high`. |

**Do not run this session on Fable.** Reasoning, in short: Fable's documented tendency is to
answer from memory rather than read, and Phase 2's whole recipe is "read this file fully,
split at these headings, never paraphrase from memory"; task decomposition already spent the
ceiling's value at ~30 calls per task; and it is 2× Opus 5 per token. Full reasoning in
design.md D12 and the Resolved Decisions entry for PD2.

**One trap worth naming**: the 1M default buys headroom, it does **not** fix truncation.
D14/D15 established that workers hit a *tool-call* ceiling, not a context limit — upstream
measured a truncated worker holding only 92K tokens. If a worker truncates, the remedy is
`P2-T16`'s discrimination logic, not a bigger window.

## Current State

Nothing is implemented. No source file has been touched — `git status --short` is empty. The
only working-tree changes are the five plan documents under
`docs/plans/2026-09-08-upstream-fable-merge/` (gitignored) and an added `upstream` git remote.

| Document | State |
| -------- | ----- |
| `research.md` | Complete; **all 7 Open Questions closed** with pointers to where each was decided |
| `design.md` | **Approved** — D1–D20, plus a `### Resolved Decisions` subsection holding PD2/PD3/PD4/A1 |
| `tasks.md` | Complete — **62 tasks, 5 phases**, `status: not-started`, `current_phase: 0`, no gates |
| `journal.md` | Does not exist — `P3-T7` creates the convention; this plan predates it |

## What this project is

Port the applicable parts of `gvarela/workbench` (our fork parent, v3.0.0) into our tree and
**remove beads entirely**, reaching wb 2.0.0. The load-bearing decisions:

- **D4** — no external tracker. Checkbox state in `tasks.md` is truth, frontmatter counters
  are a derived cache, git is the durable record.
- **D8** — continuity: a per-plan `journal.md` whose entries **open when work starts** (so an
  abrupt kill leaves a correct open entry, not silence), a committed
  `.claude/wb/knowledge.md` with dated entries carrying verification hints, and a
  session-start bootstrap **reconciled against the working tree** — the repository is the
  authority, never the journal.
- **D12** — Fable is an upshift, never a default.
- **D14** — truncation and genuine failure are different events with opposite remedies; never
  retry a whole task with the same context.
- **D19/D20** — delete the stale rule-bearing docs, then constrain where rules may live; and
  add the two implementation guardrails whose absence was a real gap.

## Decisions resolved 2026-09-08 — what changed since the plan was first written

Full records with rationale and trade-offs are in design.md → Technical Decisions →
**Resolved Decisions**. Summary, because three of these changed the plan's shape:

1. **PD2 — worker ladder.** Haiku (mechanical only) · **Opus 4.8 1M default** · Opus 5 upshift
   on coordinator judgment · Fable by election after a verified failure. This is the one place
   our tiering deliberately diverges from upstream, and the reason is our two-Opus roster,
   which upstream does not have. **Knock-on**: `model-help`'s roster at `:22` lists four
   models with *no* 1M variants, so `P2-T17` must add them or the ladder names a model its own
   authority doesn't contain.
2. **PD3 — D18 approved in full.** No longer a rider. `P1-T6` is unconditional and rewrites
   the `CLAUDE.md` scaffolding root at the **start** of Phase 1 — before any stage file is
   trimmed, because the root regenerates the pattern in the next stage anyone writes. The 25
   `think deeply` / `ultrathink` sites convert during Phase 2. Barrier volume and scope-block
   CAPS remain **out** of scope: upstream's blind trials returned equal-or-worse on both.
3. **PD4 — all three renames ship.** `create_execution` → `create_tasks`,
   `implement_coordinated` → **`implement`**, `implement_tasks` → **`implement_inline`**, each
   with a deprecated alias removed at the next major. This *reversed* the earlier deferral —
   the reasoning is that 2.0.0 is already breaking and the alias mechanism is already being
   built, so one migration beats two. Cost: three aliases in the menu until the next major,
   and `implement` becomes the most generic trigger word, so its description must carry the
   discrimination against `implement_inline`. Added `P2-T29` for the two new alias stubs.
4. **A1 — validated, with a caveat.** No other people or repositories install `wb`, but the
   user has it installed on **other machines and workspaces holding existing plan
   directories**. So `P4-T7`'s Migration section is written **per-machine** and must not
   assume the reader is in this repository looking at this plan.

## Critical Discoveries

Things this session learned that the documents don't make obvious and that would cost real
time to rediscover. **Candidates for `.claude/wb/knowledge.md` once `P3-T8` creates it** —
each carries the verification hint D8b requires.

1. **`claude plugin details <name>` reports projected token cost per component.** This is the
   direct measurement of D2's headline metric, replacing the line-count proxy the design was
   originally written against. `P0-T2` captures the baseline.
   *Verify: `claude plugin details wb` shows a "Projected token cost" block.*
2. **`claude plugin tag --dry-run <path>` validates that `plugin.json` and the enclosing
   marketplace entry agree**, and warns when a `CLAUDE.md` sits at the plugin root where it
   will not be loaded. That warning is present today, and its disappearance is the
   verification that D1 landed. Tag convention is `wb--v<version>`, **not** upstream's
   `v<version>`.
   *Verify: `claude plugin tag --dry-run .` at the repo root emits the CLAUDE.md warning.*
3. **`./scripts/lint --fix` exits 0 with findings remaining** — the `exit 1` is nested inside
   the non-`--fix` branch. Confirmed empirically. `P0-T4` fixes it, and every later phase's
   per-file gate depends on that fix.
   *Verify: lint a file with an unfixable finding; plain mode exits 1, `--fix` exits 0.*
4. **The beads dependency graph was never load-bearing.** Execution is strictly sequential;
   `bd ready` only named the next task in an order the document already fixed; edges were
   derived from the fixed phase/category sequence; only two sites ever inspected a milestone's
   `blockedBy`. This is *why* D4 is safe and why no graph-capable replacement is needed.
5. **The tracker is absent from this environment anyway** — no `bd` binary, no `.beads/`, and
   the beads plugin is not in the marketplace cache. Six commands currently reach a
   stop-and-prompt gate on a dependency that cannot resolve.
6. **CaseSmith (`/law:*`) is the working tracker-free precedent, by the same author.** Source
   at `/Users/thescubageek/projects/casesmith/claude-code/`. It runs
   `task_tracking: markdown-checkboxes`, states "No beads, no external tracker", and
   reconciles counters with `grep -c '^- \[x\]'` via `/law:update_matter_status`. D4 adopts
   that convention rather than inventing one — read those three files if a status-surface
   question arises.
7. **Split boundaries in `tasks.md` are headings, never line numbers.** Line numbers decay
   after the first edit in a sequential multi-file refactor. Two agents produced line-range
   maps during planning; they are corroboration, not input.
8. **`implement_coordinated` (now `implement`) is the deepest-coupled file in the tree** — its
   tracker gates recur across Steps 2, 4, 6, 7, 8, and 9 rather than sitting in one section.
   That is why `P2-T10` (rename + structure) and `P2-T28` (gates) are separate tasks.
9. **`help.md:245-246` already points users at the `v1.0.0` tag for a "markdown-only
   workflow".** This release restores that as the only mode — say so in the changelog rather
   than presenting tracker-free operation as new.

## Current Blockers

None.

## Uncommitted Changes

- `docs/plans/2026-09-08-upstream-fable-merge/{README,research,design,tasks}.md` and this
  handoff — gitignored; force-add if you want them in history
- Added git remote `upstream` → `https://github.com/gvarela/workbench.git`
- `.context/upstream/` — the exported upstream tree (gitignored; refresh recipe in README)

No source file has been modified.

## Next Steps

1. **Phase 0** (`P0-T1`–`P0-T5`): the layout probe and the lint fix. **Phase 0 can invalidate
   Phases 1–2** — if the throwaway `plugin/` probe does not load under our marketplace
   identity, D1 and D2 are dead and the plan needs re-planning. Its checkpoint says to stop
   rather than push through.
2. **Phase 1**: relocation, sub-agent tiers, `AGENTS.md` deletion, `P1-T7`'s guardrails, and
   `P1-T6`'s scaffolding-root rewrite (now unconditional).
3. **Phases 2–4** in order. Stop at every ⛔ CHECKPOINT — they are human gates by design.

## Things that will bite

- **`--plugin-dir` must point at `plugin/`** after Phase 1, not the repo root. A session
  started against the root silently serves nothing.
- **The installed plugin is 1.12.4 while the repo is 1.12.5** — the marketplace cache lags.
  Working-tree changes are invisible to a session that did not start with `--plugin-dir`.
- **Phase 3's checkpoint needs a real interrupt.** The D8 acceptance test is: open a journal
  entry, make an uncommitted edit, then kill the session with no shutdown step, and confirm
  the next session's first context reports the entry as open and names the uncommitted work.
  That cannot be automated — it needs an actual plug-pull.
- **`docs/plans/` is gitignored here.** Plan artifacts are local unless force-added.
- **This plan predates its own conventions.** There is no `journal.md` for it, and its
  decisions live in markdown tables rather than a tracker — which is the convention D6 makes
  permanent, so nothing needs migrating.
- **Until `P3-T8` runs, this handoff is the only carrier** for the nine discoveries above. If
  a session dies before Phase 3, re-read this file rather than assuming the knowledge file
  holds them.

## Artifacts and References

- Plan: `docs/plans/2026-09-08-upstream-fable-merge/`
- Upstream tree: `.context/upstream/` at `upstream/main` = `19e98ee` (v3.0.0)
- Upstream's Fable plan (source for D12–D15 and the *rejected* trims):
  `.context/upstream/docs/plans/2026-09-01-fable-5-1-rebaseline/` — note
  `trials/2026-09-05-blind-trials.md`, which is why barrier and scope-block volume are not in
  scope
- Upstream's truncation evidence (D14, D15):
  `.context/upstream/docs/subagent-tool-call-ceiling.md`
- Tracker-free precedent:
  `/Users/thescubageek/projects/casesmith/claude-code/commands/law/{create_workplan,draft_tasks,update_matter_status}.md`
