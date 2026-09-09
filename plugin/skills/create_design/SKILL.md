---
name: create_design
description: Create architectural design decisions based on validated research
argument-hint: "[project-directory]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Create Design Document

Creates architectural and technical design decisions based on validated research. Focuses on WHAT to build and WHY, not HOW to implement.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- [sub-agent-prompts.md](sub-agent-prompts.md) — the three Step 2 verification agents
- `templates/` — one file per output shape: [design-md-template.md](templates/design-md-template.md) (Step 5, includes the Assumptions and Pending Decisions tables) · [recorded-decision-confirmation-message.md](templates/recorded-decision-confirmation-message.md) (Step 4, Mode A) · [design-options-message.md](templates/design-options-message.md) (Step 4, Mode B) · [design-presentation-message.md](templates/design-presentation-message.md) (Step 6)
- [reference.md](reference.md) — design principles, what belongs in design vs execution, handling knowledge gaps, leveraging agent findings, configuration

**If a directed read fails, stop — do not continue from memory.** These files live in the plugin
directory, which is outside your project, so a read of one can be refused. Say which file was
refused, that reads outside the working directory are gated, and that the fix is to allow the
read once or to relaunch with `--add-dir <plugin-path>`. Writing the artifact from this manifest
alone produces a plausible document that was never based on the template — the exact failure the
sentence above exists to prevent. Do not route around a refusal with `cat`.

**Model & effort (gate check)**: on entry, consult the `model-help` skill (gate mode) for the model + effort this phase warrants; surface its one-line verdict and — only if a switch clears the switch-cost bar — the `/model` action. Design is the reasoning-dense phase and usually the pipeline's ceiling: baseline **Opus/high**, rising to `max` for novel / one-way-door / compliance-critical / high-blast-radius decisions. This is the gate most likely to justify switching *up*. Best-effort and non-blocking: stay silent and proceed when the current tier is already right. See CLAUDE.md → "Model & effort at gates."

## CRITICAL: This Document is About WHAT and WHY - NEVER HOW

- **DO NOT** include implementation sequences or step-by-step procedures
- **DO NOT** specify HOW to code solutions
- **DO NOT** create task lists or phase breakdowns
- **DO NOT** detail file modifications or code changes
- **ONLY** document WHAT needs to be built and WHY those choices were made
- **ONLY** architectural decisions and technical approach
- The HOW comes later in the execution plan - NOT HERE

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:create_design docs/plans/2025-01-08-my-project/`):
   - Use `$1` as the project directory
   - Read research.md and design.md immediately
   - Begin design process

2. **If no arguments**:

   ```
   I'll help you create a design document based on the research. Please provide:
   1. Path to the project documentation directory (e.g., docs/plans/2025-01-08-my-project/)
   2. Any specific constraints or requirements for the design (optional)
   3. Any architectural preferences or patterns to follow (optional)

   I'll analyze the research findings and work with you to make design decisions.
   ```

## Prerequisites

- **MUST** have completed research.md in the project directory
- Research should be validated (facts confirmed accurate)
- Knowledge gaps from research should be reviewed

### Check for Blocking Questions

Before starting design, check whether research left unresolved questions. They live in
research.md's `## Open Questions` table — read it and look for rows whose **State** is `Open`.
There is no external tracker to query; the table is the record.

If a critical question blocks a design decision, resolve it first — `/wb:resolve_questions`
walks them one at a time — or carry it forward deliberately as a row in the design's
Assumptions table, which states what being wrong would cost.

## Process Steps

### Step 1: Read and Analyze Research

**⛔⛔⛔ BARRIER 1: STOP! Read research.md and existing design.md FULLY - NO SKIMMING ⛔⛔⛔**

```javascript
const projectDir = $1 || /* prompt for it */;

// Read all project files
const researchFile = `${projectDir}/research.md`;
const designFile = `${projectDir}/design.md`;
```

1. **Read research.md completely**:
   - Understand current implementation
   - Note all patterns and conventions found
   - Identify constraints that must be respected
   - Review knowledge gaps section

2. **Read existing design.md** (if present):
   - Check current status
   - Note any existing design decisions
   - Identify what needs updating

3. **Extract key design inputs**:
   - What exists that we must work with
   - What patterns should we follow
   - What constraints limit our options
   - What gaps might affect our design

4. **Check for a recorded decision** (from `/wb:explore_design`):

   Look in `[project-dir]/thoughts/` for an exploration document carrying a decision record —
   a section stating the chosen direction and its rationale. If `design.md` already exists,
   also check its `## Technical Decisions` for a record naming an exploration document.

   If one exists, read the exploration document **FULLY**, including its rejected
   alternatives. The architectural decision has already been made and argued; Step 4 will
   formalize it rather than regenerate options. If none exists, Step 4 runs its normal
   interactive path — this check simply finds nothing and costs nothing.

5. **Read `.claude/wb/knowledge.md` if it exists** — durable repository facts, each with a
   date and a verification hint. Treat entries as dated claims to re-check, not as current
   truth; correct or delete one you find false in this session. Absent file, fall through.

**Decide WHAT to build, not HOW to build it**

Synthesize the research into design constraints and opportunities.
Remember: You are deciding WHAT and WHY, not HOW.

### Step 2: Spawn Verification Agents

**Leverage Claude Code's agent capabilities to validate design approach:**

After reading research, read [sub-agent-prompts.md](sub-agent-prompts.md) NOW and spawn the three agents it defines, concurrently.

**When the fan-out is skippable, and when it is not.** Spawn unless you have **already read the
entire relevant surface** in this context — every file the agents would open, not a sample. That
is a real case: a repository of three files, or a change confined to one module you have read
whole. Then the agents can only return what you already hold, and spawning them spends tokens to
learn nothing.

Anything else, spawn. In particular, spawn when you have read *some* of the surface and are
inferring the rest, when the change is cross-cutting, or when you are unsure which files are
relevant — that uncertainty is the thing the fan-out resolves, so treating it as a reason to skip
inverts the purpose.

**If you skip, say so in your output and say why**, naming what you read instead. A silent skip
is indistinguishable from forgetting, and the next reader cannot tell which happened.

**Sub-agents are READ-ONLY** — they return findings only; YOU write `design.md` after synthesizing.

**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL agents to complete - NO EXCEPTIONS ⛔⛔⛔**

This barrier governs *waiting*, not spawning — synthesis on a
partial set misses what the missing report would have changed. If you skipped the fan-out under
the rule above, there is nothing to wait for and the barrier is satisfied trivially; it is not a
reason to spawn agents you just established would return nothing.

### Step 3: Problem Definition

**Define the actual problem, not the implementation**

Based on research and agent findings, clearly articulate:

1. **The Problem**:
   - What specific problem are we solving?
   - Why does it need to be solved now?
   - What happens if we don't solve it?

2. **Success Metrics**:
   - How will we measure success?
   - What are the acceptance criteria?
   - What are the performance requirements?

3. **Constraints**:
   - Technical constraints from research
   - Business constraints
   - Time/resource constraints

### Step 4: Solution Exploration

This step runs in one of two modes, set by Step 1's decision-record check.

#### Mode A — a recorded decision exists: formalize, do not regenerate

The architectural decision was already made and argued in `/wb:explore_design`. **Do NOT
generate options.** Presenting a fresh option set here would re-litigate a decision the user
already reached, and would discard the reasoning the exploration produced.

Read [templates/recorded-decision-confirmation-message.md](templates/recorded-decision-confirmation-message.md) NOW and present the recorded decision for confirmation in that
shape.

- **On confirmation**: treat the recorded direction as the approved approach and go to Step 5.
  The exploration document supplies the Rejected Alternatives and their rationale — carry them
  across rather than inventing new ones.
- **If the user wants to revisit**: suggest re-running `/wb:explore_design [project-dir]`.
  Do not re-litigate the decision here with freshly generated options.

#### Mode B — no recorded decision: explore here

**⛔ TRACER BULLET GATE: Before presenting options, ask if one probe would collapse the set**

**Identify the single load-bearing uncertainty**

The candidate approaches usually share one assumption you cannot yet evaluate — and the answer changes which paths are even viable. Don't list options on paper and defer that unknown to a "validate later" row in the Assumptions table. Resolve it now if you cheaply can.

Fire a tracer bullet when **ALL** hold:

1. The viability of multiple approaches hinges on the same unverified assumption.
2. One bounded action would resolve it — read the one file end-to-end, run a minimal end-to-end slice, make the one API call, run the one query, write one throwaway spike.
3. Resolving it eliminates options or reorders significant downstream work.

If so, run that single bounded probe **before** generating options, then **report the cull**:

```
Tracer bullet: [what was probed] → [evidence found].
This kills Option [X] / confirms [assumption].
Surviving options: [...]
```

Keep it bounded: one assumption (the highest-leverage one), throwaway or thin, stop the moment it resolves. If there is no single decisive unknown, skip the probe and proceed — don't manufacture one.

See the `tracer-bullet` skill for the full discipline.

**Interactive Design Discussion**

1. **Generate design options**: read the [templates/design-options-message.md](templates/design-options-message.md) NOW and present them in that shape.

2. **Discuss trade-offs**:
   - Performance vs simplicity
   - Time to market vs completeness
   - Flexibility vs specificity
   - Consistency vs innovation

3. **Get explicit approval** on the chosen approach before proceeding

### Step 5: Document Design Decisions

Read [templates/design-md-template.md](templates/design-md-template.md) NOW and update or create `design.md` in the shape it gives.

Two of its tables are the project's own record, because there is no external tracker:

- **Assumptions** carry local IDs (`A1`, `A2`, …) and a `Validated?` state. An assumption
  earns a row when being wrong would change the design.
- **Pending Decisions** carry local IDs (`PD1`, `PD2`, …) and name what they block. A row needs
  a real blockee; if nothing is blocked, decide it here and record it under Technical Decisions.

Both are edited in place when resolved — `/wb:resolve_questions` flips the state cell and,
for a pending decision, writes the decision with its rationale and trade-off under
`## Technical Decisions`. Rows are never deleted; the audit trail is the point.

**⛔⛔⛔ BARRIER 3: STOP! Verify no placeholder values before writing — every decision, rationale, and reference must be concrete, not a `[TODO]`/`[TBD]`/template stub. ⛔⛔⛔**

### Step 6: Review and Iterate

**1. Present the design:** read the [templates/design-presentation-message.md](templates/design-presentation-message.md) NOW and present it in that shape.

**2. Iterate based on feedback:**

- Adjust success criteria
- Refine technical decisions
- Add/remove scope items
- Update risk analysis

**3. Get explicit approval — and record it:**

```
Once you're satisfied with the design, please confirm approval.
After approval, run `/wb:create_tasks` to build the implementation plan.
```

**On confirmation, set `status: approved` in `design.md`'s frontmatter** and refresh
`last_updated`. Until then it stays `draft`.

That edit is the gate, not a formality: `/wb:create_tasks` requires `approved`, and `forge`
routes on it. A design left at `draft` stops the pipeline with no explanation, because the next
stage can only see the field, not the conversation in which you approved it. Equally, never set
it without the confirmation — writing `approved` on your own judgment removes the one review
step between a design and the tasks built on it.

## Important Guidelines

See [reference.md](reference.md) — design principles, what belongs in design vs execution, handling knowledge gaps, leveraging agent findings, and configuration.
