---
name: create_tasks
description: Transform design into detailed phased execution plan with embedded tasks
argument-hint: "[project-directory]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Create Execution Plan

Transforms design decisions into a detailed, phased execution plan with embedded tasks. Focuses on HOW to implement what was designed.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- [sub-agent-prompts.md](sub-agent-prompts.md) — the three Step 2 analysis agents
- `templates/` — [tasks-md-template.md](templates/tasks-md-template.md) (Step 4) · [plan-presentation-message.md](templates/plan-presentation-message.md) (Step 6)
- [examples.md](examples.md) — worked examples of sizing a task by tool calls, splitting at a natural seam, and when a task needs an explicit `Depends on:`
- [reference.md](reference.md) — planning principles, execution vs design, implementation discoveries, task granularity, configuration

**If a directed read fails, stop — do not continue from memory.** These files live outside your
project, so a read can be refused. Say which file was refused, that reads outside the working
directory are gated, and that the fix is to allow the read once or to relaunch with
`--add-dir <plugin-path>`. Do not route around a refusal with `cat`.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

**Model & effort (gate check)**: on entry, consult the `model-help` skill (gate mode) for the model + effort this phase warrants; surface its one-line verdict and — only if a switch clears the switch-cost bar — the `/model` action. Baseline is Sonnet/medium — the design decisions are already made; this phase structures them into phased tasks. Best-effort and non-blocking: stay silent and proceed when the current tier is already right. See CLAUDE.md → "Model & effort at gates."

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:create_tasks docs/plans/2025-01-08-my-project/`):
   - Use `$1` as the project directory
   - Read research.md, design.md, and tasks.md immediately
   - Begin execution planning

2. **If no arguments**:

   ```
   I'll help you create an execution plan from the approved design. Please provide:
   1. Path to the project documentation directory (e.g., docs/plans/2025-01-08-my-project/)

   I'll read the research and design documents to create a detailed implementation plan with tasks.
   ```

## Prerequisites

- **MUST** have research.md (validated)
- **MUST** have design.md (approved)
- Both documents should be in the specified project directory

## Process Steps

### Step 1: Read Foundation Documents

**⛔⛔⛔ BARRIER 1: STOP! Read ALL documents FULLY - research.md, design.md, tasks.md ⛔⛔⛔**

**Open a journal entry before you begin reading** — appended to `journal.md` in the plan
directory. The heading shape is a contract — the session-start hook, `forge`, `daily-digest`,
`resume_handoff` and `create_handoff` all match on the trailing `(open)` / `(closed)`:

```text
## 2026-09-11 14:02 — create_tasks (open)

- **Task/phase**: P0-T4 — execution plan for <plan>
- **Next action**: generate the phased plan, then present it at Step 6
- **Started at**: <commit hash, or `no-commits-yet`>
```

**Read the clock for the timestamp** — `date -u +"%Y-%m-%d %H:%M"`. Never estimate it or copy a
time from elsewhere in the file.

```javascript
const projectDir = $1 || /* prompt for it */;

// Read all project files
const researchFile = `${projectDir}/research.md`;
const designFile = `${projectDir}/design.md`;
const tasksFile = `${projectDir}/tasks.md`;
```

1. **Read research.md completely**:
   - Current implementation details
   - File locations and patterns
   - Constraints to respect
   - Knowledge gaps identified

2. **Read design.md completely**:
   - Design decisions made
   - Success criteria defined
   - Scope boundaries set
   - Technical specifications
   - Any unresolved rows in its Assumptions and Pending Decisions tables — a `PD` row that
     blocks execution start must be resolved before this plan is written, not planned around

3. **Read existing tasks.md if present**:
   - Check current status
   - Note any existing progress

**Decide HOW to bridge from current state to target state**

Synthesize research (current state) and design (target state) to determine the implementation path.
Remember: Now you're planning HOW to build what was designed.

### Step 2: Spawn Analysis Agents

**Leverage Claude Code's agent capabilities for implementation analysis:**

After reading all documents, read [sub-agent-prompts.md](sub-agent-prompts.md) NOW and spawn the three agents it defines, concurrently.

**Skip the fan-out only if you have already read the entire relevant surface in this context** —
every file the agents would open, not a sample. Having read *some* of it, a cross-cutting change,
or uncertainty about which files are relevant are each a reason to spawn, not to skip. **If you
skip, say so in your output and say why**, naming what you read instead.

**Sub-agents are READ-ONLY** — they return findings only; YOU write `tasks.md` after synthesizing.

**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL agents - dependency, test, pattern agents ⛔⛔⛔**

This barrier governs *waiting*, not spawning — synthesis on a partial set misses what the missing
report would have changed. A fan-out skipped under the rule above satisfies it trivially.

### Step 3: Determine Implementation Strategy

**Decide the safest, most logical implementation sequence**

Based on the gap between current and target state, and agent findings:

1. **Identify dependencies** (from dependency agent):
   - What must be built first?
   - What can be done in parallel?
   - What requires prerequisites?

2. **Assess risk** (from test coverage agent):
   - What changes are highest risk?
   - What needs extra testing?

3. **Plan phases** (synthesize all findings):
   - Group related changes
   - Minimize risk per phase
   - Enable incremental validation
   - Follow patterns from similar implementations

4. **Order for document order.** Phases run in the order they appear, and tasks run in order
   within a phase — so the sequence you choose here *is* the dependency graph. Write no
   separate graph. A task that genuinely depends on something other than the task before it
   states that in one `Depends on:` field; if many tasks need one, the phase is ordered wrong,
   so reorder it. See [examples.md](examples.md) → "When a task needs a Depends on field".

5. **Size every task by projected tool calls, not hours.** A task projecting past ~50 calls
   splits at its natural seam *before* it is ever spawned — usually source change, then test
   conversion, which are separately verifiable anyway. Truncation eats the finishing tail, so
   what a too-big task leaves behind looks like progress rather than failure. See
   [reference.md](reference.md) → "Task Granularity" for the rule and
   [examples.md](examples.md) for a worked projection and split.

**⛔ TRACER BULLET CHECK: Does the whole plan rest on one unverified assumption?**

**Identify the single load-bearing unknown**

A multi-phase plan built on "assuming X works..." is a gamble — if X is false, every phase after it is wasted. Before finalizing phases, ask: is there one assumption whose failure would invalidate large parts of the plan, and would one bounded probe resolve it?

If so, make it **Phase 0: Tracer Bullet** — a single bounded spike (a thin end-to-end slice, one query, one throwaway prototype) that resolves the unknown before the real build. Phase 1+ then plan against a known answer, not a guess. Keep it bounded: one assumption, stop the moment it resolves, then plan the rest. If there is no single decisive unknown, skip Phase 0 — don't manufacture one.

This is distinct from minor discoveries you make as you code (see reference.md → "Handling Implementation Discoveries"): a tracer bullet is for the *decisive* unknown that reorders the plan. See the `tracer-bullet` skill for the full discipline.

### Step 4: Generate Execution Plan

Read [templates/tasks-md-template.md](templates/tasks-md-template.md) NOW and write `tasks.md` in the shape it gives.

Three things about that template are load-bearing rather than cosmetic:

- **Checkbox state in `tasks.md` is the source of truth.** There is no external tracker to
  create, and no issue IDs to mint. The plan you write *is* the tracking surface.
- **The frontmatter counters are a derived cache with exactly one writer**, `/wb:update_status`.
  Phase checkpoints delegate to it rather than editing `current_phase` inline, which is how
  those fields stay consistent with the checkboxes.
- **Every task carries a stable local ID and a tool-call projection.** The ID is what a commit
  message, a journal entry, or a handoff cites; the projection is the number that predicts
  truncation. The ID's **shape is a contract**: `[A-Z0-9-]*[0-9][A-Z0-9-]*` in bold, with at
  least one digit, because that pattern is what every counter in the workflow uses to tell a
  task line from a bold criterion label. An ID without a digit is invisible to counting.

**⛔⛔⛔ BARRIER 3: STOP! Verify NO placeholder values - ALL tasks MUST be specific and executable ⛔⛔⛔**

### Step 5: Validate Completeness

Verify with agent findings:

1. **All success criteria** from design.md have corresponding tasks
2. **All scope items** from design.md are addressed
3. **Knowledge gaps** from research.md are handled
4. **Risk mitigations** from design.md are incorporated
5. **Every task is specific and executable**
6. **Test coverage** matches test agent recommendations
7. **Dependencies** follow agent-identified order
8. **Every task carries an ID and a tool-call projection**, and nothing projects past ~50

### Step 6: Present the Plan

**Close the journal entry first**, naming the phase and task counts the plan landed with.

Read [templates/plan-presentation-message.md](templates/plan-presentation-message.md) NOW and present it in that shape.

## Important Guidelines

See [reference.md](reference.md) — execution planning principles, what belongs in execution vs design, handling implementation discoveries, leveraging agent findings, task granularity, and configuration.
