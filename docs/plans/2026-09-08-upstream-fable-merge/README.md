# upstream-fable-merge

**Created**: 2026-09-08
**Ticket**: N/A
**Status**: Planned — 62 tasks across 5 phases, not started — no open decisions

## Overview

Assess what `gvarela/workbench` (our fork parent, now at v3.0.0) has landed since our
merge-base at `cb693fb`, and map each change onto the current architecture of
`thescubageek/workbench` (v1.12.5) — with particular attention to the Fable 5.1
re-baseline work Gabe called out.

Research is documentarian: it records what exists on each side and the structural
relationship (present / absent / divergent). Adopt/adapt/skip dispositions belong to the
design stage.

## Documentation Structure

- **[research.md](research.md)** — What exists on both sides and how it maps: divergence
  topology, upstream's release inventory, the Fable plan (including which trims the blind
  trials rejected), model/effort architecture, implementation guardrails, scaffolding
  inventory, layout and context economy, hooks, beads vocabulary, the subagent tool-call
  ceiling, release mechanics, and a two-way capability inventory
- **[design.md](design.md)** — Decisions D1–D21 and why: the `plugin/` relocation and
  progressive-disclosure migration, beads removal with markdown as the status surface,
  cross-session continuity (D8: a per-plan session journal whose entries open at the start of
  work, a committed repository knowledge file, and a session-start bootstrap reconciled
  against the working tree), `create_tasks`, `explore_design`, drift hardening, Fable as an
  upshift-only tier, the de-duplicated failure path, the lint fix, the 2.0.0 cut, and D19's
  removal of the obsolete rule-bearing documents plus the rule for where rules may live.
  All pending decisions (PD2–PD4) and assumption A1 resolved 2026-09-08; nothing gates execution
- **[tasks.md](tasks.md)** — 62 tasks in 5 phases: Phase 0 resolves the layout unknown and
  repairs the lint gate; Phase 1 relocates the tree; Phase 2 is the per-file pass (reshape +
  de-beads + content, one edit per file); Phase 3 adds the capabilities that did not exist
  (continuity, drift hardening, `explore_design`); Phase 4 rewrites the consumers and cuts
  2.0.0. Written in the markdown-checkbox convention it establishes
- **[journal.md](journal.md)** — the session journal: one entry per unit of work, newest first,
  each ending in `(open)` or `(closed)`. The Implementation Notes at the bottom of `tasks.md`
  carry every finding, deviation and test round; the six session handoffs that once lived here
  were removed 2026-09-15 once their content was in those notes (see git history)
- **thoughts/** — `2026-09-08-baseline-measurements.md` is written by task `P0-T2` and holds
  the before-measurements Phase 2's exit compares against

## Upstream reference

The upstream tree is exported to `.context/upstream/` (gitignored) at
`upstream/main` = `19e98ee` (v3.0.0). To refresh:

```bash
git fetch upstream
rm -rf .context/upstream && mkdir -p .context/upstream
git archive upstream/main | tar -x -C .context/upstream
```

Upstream's own plan documents are the primary sources for the Fable work:

- `.context/upstream/docs/plans/2026-09-01-fable-5-1-rebaseline/` — research, design (D1–D10),
  the effort-curve/routing thoughts doc, and `trials/2026-09-05-blind-trials.md`
- `.context/upstream/docs/plans/2026-09-05-prompts-h7c-implement-rename-3.0/` — the 3.0.0
  plan (D1–D20: renames, plan Intent, stateful help, beads realignment, wb-prime)
- `.context/upstream/docs/plans/2026-08-21-prompts-8bj-compaction-drift-hardening/` — the
  compaction/drift work (D1–D4)
- `.context/upstream/CHANGELOG.md` — the full 1.0.0 → 3.0.0 log

## Quick Commands

```bash
/wb:implement_tasks docs/plans/2026-09-08-upstream-fable-merge/ 0   # start at Phase 0
/wb:update_status     docs/plans/2026-09-08-upstream-fable-merge/
```

## Git Information

- **Branch**: `thescubageek/gabe-fable-merge-research`
- **Commit**: `b902566` (all `file:line` references in this project are at this commit for
  our tree, and at `19e98ee` for upstream)
- **Repository**: thescubageek/workbench (fork of gvarela/workbench)
- **Merge-base with upstream**: `cb693fb` (2026-04-28)

## Notes

- `bd` is not installed in this workspace. Open questions live in research.md's Open Questions
  section and pending decisions in design.md's table — which is the convention this plan makes
  permanent (design.md D6), so there is nothing to migrate later.
- All decisions resolved 2026-09-08: **PD2** worker ladder is **Opus 4.8 1M** (`claude-opus-4-8[1m]`)
  default / Opus 5 upshift / Fable by election; **PD3** D18 approved in full; **PD4** all three renames ship;
  **A1** migration note is written per-machine. Records with rationale live in design.md
  → Technical Decisions → Resolved Decisions.
- `docs/plans/` is gitignored in this repository (dev-only artifacts, per `.gitignore`), so
  plan documents are local unless deliberately force-added. **This plan was force-added
  2026-09-08** under D21: plans are transient by default and promoted into git when the work
  must cross a session or machine, or when the branch is about to merge — both of which fire
  for a 62-task, 5-phase plan ending in a release.
