---
name: forge
description: Forge a ticket through the full wb pipeline — research → design → tasks → implementation. End-to-end sequencer for the wb workflow.
argument-hint: "[ticket-or-directory] [stop-at-phase?]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Forge — wb pipeline orchestrator

"Forge" / "forging" is the user's shorthand for running a ticket through the full wb pipeline. This skill is the sequencer — it does not implement new logic; it invokes the existing `/wb:*` stages in order, enforces the barriers between phases, and tracks where the ticket is in the pipeline.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- `templates/` — [output-style.md](templates/output-style.md) (the per-phase report shape) · [model-plan.md](templates/model-plan.md) (the model-plan table)
- [examples.md](examples.md) — invocation examples, and the evidence behind each detected state

**If a directed read fails, stop — do not continue from memory.** These files live in the plugin
directory, which is outside your project, so a read of one can be refused. Say which file was
refused, that reads outside the working directory are gated, and that the fix is to allow the
read once or to relaunch with `--add-dir <plugin-path>`. Writing the artifact from this manifest
alone produces a plausible document that was never based on the template — the exact failure the
sentence above exists to prevent. Do not route around a refusal with `cat`.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## When to use

- User says **"forge this ticket"**, **"run X through forge"**, **"forge it"**, or **"start forging"**
- User invokes `/wb:forge` directly
- The user wants the end-to-end project workflow rather than a single `wb:` step

## What it does NOT do

- Does not skip steps or merge phases
- Does not run implementation without explicit go-ahead from the user (implementation is a heavier commitment than planning)
- Does not bypass barriers or stakeholder questions

## Pipeline sequence

```
[optional] /wb:create_project   → if no project directory exists yet
         ↓
/wb:create_research             → document what EXISTS (facts only, parallel agents)
         ↓ ⛔ BARRIER: open questions resolved
[optional] /wb:explore_design   → only when research surfaced more than one viable approach
         ↓
/wb:create_design               → decide WHAT to build and WHY
         ↓ ⛔ BARRIER: no pending decisions blocking execution
/wb:create_tasks                → plan HOW; writes the phased task list
         ↓ ⛔ BARRIER: user confirms ready to implement
/wb:implement                   → TDD per phase via worker agents
         ↓
/wb:validate_execution          → verify implementation matches plan
```

## Arguments

- `$1` — project directory **OR** ticket reference (e.g., `docs/plans/2026-05-12-project-roar/` or `TB-2421`). If a ticket ref is given and no project dir exists, the pipeline starts at `/wb:create_project`.
- `$2` — optional stop phase: one of `research`, `design`, `tasks`, `implement`, `validate`. If omitted, default is **stop after `create_tasks`** (i.e., plan-only forge — does not auto-run implementation).

## Initial response

When invoked:

1. **Parse arguments.** If `$1` looks like a path (`docs/plans/...`), treat as project directory. If it looks like a ticket ID (`[A-Z]+-\d+`), treat as ticket reference. If empty, prompt.

2. **Detect current pipeline state — from the documents.** There is no tracker to query; the plan directory *is* the state. Read it:

   - **No directory** → start at `create_project`
   - **No `research.md`, or `status: draft` with placeholder sections** → start at `create_research`
   - **`research.md` `status: complete`, `design.md` missing or `draft`** → start at `create_design`
   - **`design.md` approved, `tasks.md` has no task lines** → start at `create_tasks`
   - **`tasks.md` has task lines and at least one is `[ ]`** → ready for `implement`
   - **Every task checkbox is `[x]`** → ready for `validate_execution`

   ```bash
   grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md   # done
   grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md   # remaining
   ```

   Scope the counts to lines carrying a task ID — a plan's own success criteria and
   prerequisites are checkboxes too. And treat `current_phase` as a **cache, not evidence**: if
   it disagrees with the checkboxes, the checkboxes win. [examples.md](examples.md) tabulates
   the states and the evidence for each.

3. **Read the journal tail if `journal.md` exists.** An **open** entry means the last stretch of
   work was interrupted; that is more informative about where the ticket really is than any
   status field, and it belongs in the state report.

4. **Report current state to the user** in 1–2 sentences. Example: "Project at `docs/plans/2026-05-12-project-roar/` has research + design complete, 0 of 18 tasks done. Next step is `/wb:implement`. Stop-after default is `create_tasks` — confirm to proceed."

5. **Emit a one-time model plan.** Consult the `model-help` skill in **gate mode** (pass the ticket/design difficulty and the remaining phases) and print a compact per-phase tier table for the phases still ahead — the "model journey" for this forge. This is advisory: it shows where a main-model switch is worth the reload and, by clustering same-tier phases, keeps the whole run to ~1–2 switches. Read [templates/model-plan.md](templates/model-plan.md) for the shape.

6. **Confirm with the user before each phase transition.** Forge does not auto-advance silently; the user must see what's about to run — and, at that moment, the model advisory for the phase about to run.

## Per-phase behavior

### Phase: create_project

- Only runs if no project directory exists.
- Invoke `/wb:create_project` semantics (read `../create_project/SKILL.md`); collect project name, base dir, ticket ref.
- Output: timestamped project directory with README, research, design, tasks and journal files.

### Phase: create_research

- Invoke `/wb:create_research` semantics.
- **Pass the ticket ref through.** If forge was given a Jira ticket ref (`$1`) or the project has a `ticket:` frontmatter field, ensure create_research receives it so its **Ticket Context Bootstrap** (Step 0) runs the `jira-context` skill: fetch the ticket via the Atlassian MCP and, if the description has an **Agents** section, follow those instructions to shortcut context lookup ("hivemind" off the ticket).
- ⛔ BARRIER on completion: read research.md's `## Open Questions` table. If any row's state is still `Open`, **stop and surface them to the user** before advancing. Forge does not skip blockers.

### Phase: explore_design (optional)

- Runs only if `create_research` suggested it — which it does only when the findings named two
  or more viable approaches with nothing deciding between them. Do not run it by default; an
  optional stage invoked unconditionally is just a slower pipeline.
- Invoke `/wb:explore_design` semantics. It records a decision at the top of a `thoughts/`
  document, which `create_design` then formalizes.

### Phase: create_design

- Invoke `/wb:create_design` semantics.
- ⛔ BARRIER on completion: read design.md's `## Pending Decisions` table. If any row is unresolved and its `Blocks` names execution start, **stop and surface it**.

### Phase: create_tasks

- Invoke `/wb:create_tasks` semantics.
- Writes the phased task list, each task a checkbox with a local ID.
- ⛔ BARRIER: explicitly ask the user "ready to implement?" before advancing. Default stop-after value is here.

### Phase: implement

- Loop per phase: take the first unchecked task in the current phase → invoke `/wb:implement`
  for that phase → at its ⛔ CHECKPOINT, wait for the human → advance to the next phase in
  **document order**.
- Phases run in the order they appear in `tasks.md`. There is no dependency graph to query; the
  document's ordering is the schedule.
- Stop the loop if any phase fails verification, or if a task lands on the checkpoint's blocking list.
- Surface failed task IDs to the user.
- `/wb:implement_inline` is the alternative if the user wants the work done in this session
  rather than by workers.

### Phase: validate_execution

- Invoke `/wb:validate_execution` semantics.
- Surface diff between plan and actual implementation.

## Cross-cutting rules

1. **Do not skip barriers.** If a phase has unresolved `Q`, `PD`, `A`, or `UIQ` records in the document that raises them, forge stops. `/wb:resolve_questions` is what walks them.
2. **Status sync at each transition** — run `/wb:update_status` so the frontmatter counters follow the checkboxes. It is their only writer.
3. **Surface, don't hide.** Forge reports what it's about to do, what it just did, and what's blocked. The user should never have to ask "where are we?"
4. **Re-entrant.** Forge can be invoked mid-pipeline. It picks up from the detected state — which is why state detection reads documents rather than remembering anything.
5. **One ticket at a time.** Forge sequences a single ticket end-to-end; it does not parallelize across tickets.
6. **Model/effort advisory at every gate.** At each transition confirmation, delegate to the `model-help` skill (gate mode) for the phase about to run and surface its one-line verdict. Advise a main-model switch **only** when it clears the switch-cost bar (≥1 tier delta *and* a substantial phase); otherwise say "stay." Never advise below the phase's quality floor, and never switch on the user's behalf — they run `/model`. This is advisory and non-blocking; it must not delay or gate the actual work.

## Output style

See [templates/output-style.md](templates/output-style.md) for the per-phase report shape.

## Examples

See [examples.md](examples.md).

## Notes for Claude

- This skill is **a sequencer, not a re-implementation** of the underlying `wb:*` stages. Always invoke the existing stages rather than duplicating their logic.
- When you would normally output "I'll run X next" between phases, instead pause for user confirmation if the next step is `implement` (heavier commitment).
- Honor `wb:help` semantics — if user asks "what's forge?", direct them to `/wb:help` for the underlying workflow and explain forge is the orchestrator over it.
- "Forge" is project-personal vocabulary; when speaking to the user, use it naturally. When invoking underlying tooling, the formal names are `wb:create_research` etc.
