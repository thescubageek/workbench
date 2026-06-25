---
description: Forge a ticket through the full wb pipeline — research → design → execution → implementation. End-to-end sequencer for the wb workflow.
argument-hint: [ticket-or-directory] [stop-at-phase?]
---

# Forge — wb pipeline orchestrator

"Forge" / "forging" is the user's shorthand for running a ticket through the full wb pipeline. This command is the sequencer — it does not implement new logic; it invokes the existing `/wb:*` commands in order, enforces the barriers between phases, and tracks where the ticket is in the pipeline.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## When to use

- User says **"forge this ticket"**, **"run X through forge"**, **"forge it"**, or **"start forging"**
- User invokes `/wb:forge` directly
- The user wants the end-to-end project workflow rather than a single `wb:` step

## What it does NOT do

- Does not skip steps or merge phases
- Does not run `wb:implement_tasks` without explicit go-ahead from the user (implementation is a heavier commitment than planning)
- Does not bypass beads tracking, barriers, or stakeholder questions

## Pipeline sequence

```
[optional] /wb:create_project   → if no project directory exists yet
         ↓
/wb:create_research             → document what EXISTS (facts only, parallel agents)
         ↓ ⛔ BARRIER: stakeholder Qs resolved
/wb:create_design               → decide WHAT to build and WHY
         ↓ ⛔ BARRIER: decisions made, no open Decide: items
/wb:create_execution            → plan HOW; creates beads issues
         ↓ ⛔ BARRIER: user confirms ready to implement
/wb:implement_tasks             → TDD per phase (loop per phase via beads ready/close)
         ↓
/wb:validate_execution          → verify implementation matches plan
```

## Arguments

- `$1` — project directory **OR** ticket reference (e.g., `docs/plans/2026-05-12-project-roar/` or `TB-2421`). If a ticket ref is given and no project dir exists, the pipeline starts at `/wb:create_project`.
- `$2` — optional stop phase: one of `research`, `design`, `execution`, `implement`, `validate`. If omitted, default is **stop after `execution`** (i.e., plan-only forge — does not auto-run implementation).

## Initial response

When invoked:

1. **Parse arguments.** If `$1` looks like a path (`docs/plans/...`), treat as project directory. If it looks like a ticket ID (`[A-Z]+-\d+`), treat as ticket reference. If empty, prompt.

2. **Detect current pipeline state.** Read the project directory if it exists:
   - No directory → start at `create_project`
   - No `research.md` or only empty stubs → start at `create_research`
   - `research.md` complete, no `design.md` or empty → start at `create_design`
   - `design.md` complete, no `tasks.md` or no beads issues → start at `create_execution`
   - `tasks.md` complete with beads phases → ready for `implement_tasks`
   - All phases closed in beads → ready for `validate_execution`

3. **Report current state to the user** in 1–2 sentences. Example: "Project at `docs/plans/2026-05-12-project-roar/` has research + design complete. Next step is `/wb:create_execution`. Stop-after default is `execution` — confirm to proceed."

4. **Confirm with the user before each phase transition.** Forge does not auto-advance silently; the user must see what's about to run.

## Per-phase behavior

### Phase: create_project
- Only runs if no project directory exists.
- Invoke `/wb:create_project` semantics (read `commands/create_project.md`); collect project name, base dir, ticket ref.
- Output: timestamped project directory with stub research/design/tasks files.

### Phase: create_research
- Invoke `/wb:create_research` semantics.
- ⛔ BARRIER on completion: list any `Q:` items in beads. If any are unresolved, **stop and surface them to the user** before advancing. Forge does not skip blockers.

### Phase: create_design
- Invoke `/wb:create_design` semantics.
- ⛔ BARRIER on completion: list any `Decide:` items in beads. If any are unresolved, **stop and surface them**.

### Phase: create_execution
- Invoke `/wb:create_execution` semantics.
- Creates beads phases.
- ⛔ BARRIER: explicitly ask the user "ready to implement?" before advancing. Default stop-after value is here.

### Phase: implement_tasks
- Loop: `bd ready` → claim phase → invoke `/wb:implement_tasks` for that phase → close → next.
- Stop the loop if any phase fails verification.
- Surface failed task IDs to the user.

### Phase: validate_execution
- Invoke `/wb:validate_execution` semantics.
- Surface diff between plan and actual implementation.

## Cross-cutting rules

1. **Beads is required** — if `bd init` hasn't run in the project, run it before `create_execution`.
2. **Do not skip barriers.** If a phase has open `Q:`, `Decide:`, `Validate:`, or `UI Q:` items, forge stops.
3. **Status sync at each transition** — run `/wb:update_status` (or equivalent) so frontmatter / README stays accurate.
4. **Surface, don't hide.** Forge reports what it's about to do, what it just did, and what's blocked. The user should never have to ask "where are we?"
5. **Re-entrant.** Forge can be invoked mid-pipeline. It picks up from the detected state.
6. **One ticket at a time.** Forge sequences a single ticket end-to-end; it does not parallelize across tickets.

## Output style

After each phase:

```
✅ <phase> complete
   <2-3 bullets of what was produced>

⛔ Barriers before <next phase>:
   - <blocker 1>
   - <blocker 2>

Next: /wb:<next-phase>  (forge will invoke unless you say stop)
```

If everything is clear, advance. If anything is blocked, stop and report.

## Examples

- `/wb:forge docs/plans/2026-05-12-project-roar/` — pick up the in-flight Roar project at its current pipeline phase
- `/wb:forge TB-2421` — start a new forge for ticket TB-2421 (will run `create_project` first)
- `/wb:forge TB-2421 design` — forge stops after design phase, doesn't enter execution
- `/wb:forge` (no args) — prompt for ticket or directory

## Notes for Claude

- This command is **a sequencer, not a re-implementation** of the underlying `wb:*` commands. Always invoke the existing commands rather than duplicating their logic.
- When you would normally output "I'll run X next" between phases, instead pause for user confirmation if the next step is `implement_tasks` (heavier commitment).
- Honor `wb:help` semantics — if user asks "what's forge?", direct them to `/wb:help` for the underlying workflow and explain forge is the orchestrator over it.
- "Forge" is project-personal vocabulary; when speaking to the user, use it naturally. When invoking underlying tooling, the formal names are `wb:create_research` etc.
