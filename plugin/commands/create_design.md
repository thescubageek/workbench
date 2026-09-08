---
description: Create architectural design decisions based on validated research
argument-hint: "[project-directory]"
---

# Create Design Document

Creates architectural and technical design decisions based on validated research. Focuses on WHAT to build and WHY, not HOW to implement.

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

1. **If directory provided** (e.g., `/create_design docs/plans/2025-01-08-my-project/`):
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

Before starting design, check if research left unresolved questions:

```bash
bd list --status=open | grep "Q:"   # Find open questions from research
```

If critical questions block design decisions, resolve them first or document as assumptions.

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

**think deeply about WHAT to build, not HOW to build it**

Synthesize the research into design constraints and opportunities.
Remember: You are deciding WHAT and WHY, not HOW.

### Step 2: Spawn Verification Agents

**Leverage Claude Code's agent capabilities to validate design approach:**

After reading research, spawn specialized agents in parallel to gather additional context:

**Sub-agents are READ-ONLY** — they return findings only; YOU write `design.md` after synthesizing.

```javascript
// Spawn agents concurrently for verification - all are read-only
Task({
  description: "Verify design patterns",
  prompt: `Based on the research findings, identify architectural patterns we should follow.

  From research.md:
  - [Key patterns found in research]
  - [Conventions observed]
  - [Integration points]

  Find:
  - Similar features already implemented
  - Patterns we should follow for consistency
  - Anti-patterns to avoid

  Document what exists, do not evaluate quality.
  Return findings only; write nothing.`,
  subagent_type: "pattern-finder",
  model: "haiku"
})

Task({
  description: "Analyze integration points",
  prompt: `Analyze how our design will integrate with existing systems.

  From research.md:
  - [Current architecture]
  - [Integration patterns]

  Identify:
  - Required integration points
  - API contracts we must respect
  - Dependencies we'll have
  - Potential conflicts

  Return findings only; write nothing.`,
  subagent_type: "codebase-analyzer",
  model: "sonnet"
})

Task({
  description: "Find risk precedents",
  prompt: `Search for similar changes in the codebase history.

  Look for:
  - Previous similar implementations
  - Issues encountered
  - Solutions that worked
  - Patterns that failed

  Return findings only; write nothing.`,
  subagent_type: "pattern-finder",
  model: "haiku"
})
```

**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL agents to complete - NO EXCEPTIONS ⛔⛔⛔**

### Step 3: Problem Definition

**think deeply about the actual problem, not the implementation**

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

**⛔ TRACER BULLET GATE: Before presenting options, ask if one probe would collapse the set**

**think deeply about the single load-bearing uncertainty**

The candidate approaches usually share one assumption you cannot yet evaluate — and the answer changes which paths are even viable. Don't list options on paper and defer that unknown to a "validate later" beads issue. Resolve it now if you cheaply can.

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

1. **Generate design options**:

   ```
   Based on the research and verification agents, I see [2-3] possible approaches:

   **Option A: [Descriptive Name]**
   - Approach: [Brief description]
   - Pros: [Benefits]
   - Cons: [Drawbacks]
   - Risk: [Main risk]
   - Precedent: [Similar implementation from agents]

   **Option B: [Descriptive Name]**
   - Approach: [Brief description]
   - Pros: [Benefits]
   - Cons: [Drawbacks]
   - Risk: [Main risk]
   - Precedent: [Similar implementation from agents]

   Which approach aligns best with your priorities?
   Or should we explore a hybrid approach?
   ```

2. **Discuss trade-offs**:
   - Performance vs simplicity
   - Time to market vs completeness
   - Flexibility vs specificity
   - Consistency vs innovation

3. **Get explicit approval** on the chosen approach before proceeding

### Step 5: Document Design Decisions

Update or create design.md with the following structure:

````markdown
---
project: [from existing frontmatter]
ticket: [from existing frontmatter]
created: [from existing frontmatter]
status: draft
last_updated: [YYYY-MM-DD]
depends_on: research.md
design_approach: [selected option name]
---

# Design: [Feature/Task Name]

## Problem Statement

[Clear articulation of the problem we're solving and why it matters]

### Success Metrics
- [Measurable outcome 1]
- [Measurable outcome 2]
- [Measurable outcome 3]

## Design Approach

[High-level description of the chosen solution approach]

### Why This Approach
- [Rationale for choosing this over alternatives]
- [How it aligns with existing patterns from research]
- [How it addresses the core problem]
- [Precedents from agent findings]

## Technical Decisions

### Architecture
- [Key architectural decision 1]
  - Rationale: [Why this choice]
  - Trade-off: [What we're giving up]
  - Pattern reference: [file:line from research]

### Data Model
- [Data structure/schema decisions]
- [State management approach]
- [Data flow design]

### Integration Points
- [How this integrates with existing systems]
- [API contracts or interfaces]
- [Dependencies on other components]

## Scope Definition

### In Scope
- [Specific feature/capability 1]
- [Specific feature/capability 2]
- [Specific feature/capability 3]

### Out of Scope
- [What we explicitly won't do]
- [Features deferred to later]
- [Problems we're not solving]

## Success Criteria

### Functional Requirements
- [ ] [User-facing capability 1]
- [ ] [User-facing capability 2]
- [ ] [System behavior 1]

### Non-Functional Requirements
- [ ] Performance: [Specific metric]
- [ ] Reliability: [Specific metric]
- [ ] Security: [Specific requirement]

## Risk Analysis

### Technical Risks
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [Strategy] |

### Assumptions

Based on knowledge gaps from research - track in beads to ensure validation:

| Assumption | Beads ID | Validated? |
|------------|----------|------------|
| [gap 1] works as [description] | `[id]` | Pending |
| [gap 2] can be resolved by [approach] | `[id]` | Pending |

```bash
# Create beads issues for assumptions that need validation:
bd create "Validate: [assumption]" --type=task --priority=2 \
  -d "Assumption from design. If wrong: [impact]"
```

## Rejected Alternatives

### Option: [Alternative Approach Name]

- **Approach**: [What it would have done]
- **Rejected because**: [Specific reasons]
- **Trade-offs**: [What we would have gained/lost]

## Pending Decisions

Design decisions that need stakeholder input - track in beads:

| Decision Needed | Beads ID | Blocks |
|-----------------|----------|--------|
| [What needs to be decided] | `[id]` | [phase or "execution start"] |
| [Options and trade-offs] | `[id]` | [what can't proceed] |

```bash
# Create beads issues for pending decisions:
bd create "Decide: [brief decision]" --type=task --priority=1 \
  -d "Options: [A, B, C]. Trade-offs: [summary]. Blocks: [what]"
```

Note: Decisions blocking execution should be resolved before `/create_execution`.

## References

- Research: [research.md](research.md)
- Related designs: [if any]
- External docs: [if any]

````

**⛔⛔⛔ BARRIER 3: STOP! Verify no placeholder values before writing — every decision, rationale, and reference must be concrete, not a `[TODO]`/`[TBD]`/template stub. ⛔⛔⛔**

### Step 6: Review and Iterate

**1. Present the design:**

```
✅ Design document created at: [path]/design.md

Design approach: [selected approach name]

Key decisions made:

- [Major decision 1]
- [Major decision 2]
- [Major decision 3]

Pending decisions: [count]

Agent findings incorporated:

- [Finding 1 from verification agents]
- [Finding 2 from integration analysis]

The design document includes:

- Problem statement and success metrics
- Technical architecture decisions
- Clear scope boundaries
- Risk analysis and mitigation

Please review and provide feedback:

- Are the success criteria appropriate?
- Do the technical decisions align with your vision?
- Are there risks we haven't considered?
- Should any out-of-scope items be included?
```

**2. Iterate based on feedback:**

- Adjust success criteria
- Refine technical decisions
- Add/remove scope items
- Update risk analysis

**3. Get explicit approval:**

```
Once you're satisfied with the design, please confirm approval.
After approval, run `/create_execution` to build the implementation plan.
```

## Important Guidelines

### Design Principles

1. **Separate WHAT from HOW**:
   - Design says WHAT to build and WHY
   - Execution plan says HOW to build it
   - Don't include implementation sequences

2. **Make Decisions Explicit**:
   - Document every significant choice
   - Include rationale and trade-offs
   - Note what was rejected and why

3. **Respect Research Findings**:
   - Build on patterns found in research
   - Respect constraints discovered
   - Don't contradict factual findings

4. **Keep It Disposable**:
   - Design should be complete but changeable
   - If approach is wrong, should be able to start over
   - Research remains valid even if design changes

### What Belongs in Design vs Execution

**Design (THIS document - WHAT and WHY only)**:

- ✅ Architecture decisions (WHAT architecture to use and WHY)
- ✅ Data models (WHAT data structures and WHY)
- ✅ API contracts (WHAT interfaces and WHY)
- ✅ Success criteria (WHAT defines success and WHY)
- ✅ Scope boundaries (WHAT is included/excluded and WHY)
- ✅ Technical approach (WHAT approach and WHY)

**Execution (tasks.md - HOW only - NEVER PUT THESE HERE)**:

- ❌ Phase sequencing (HOW to order implementation)
- ❌ Specific code changes (HOW to modify files)
- ❌ Step-by-step implementation (HOW to build it)
- ❌ Test writing tasks (HOW to test it)
- ❌ File modification lists (HOW to change code)
- ❌ Command sequences (HOW to execute changes)

**REMEMBER: If it describes HOW to do something, it DOES NOT belong in design**

### Handling Knowledge Gaps

When research has knowledge gaps:

1. **Document assumptions**:
   - State what you're assuming
   - Note risk if assumption is wrong
   - Plan for discovery during implementation

2. **Design for flexibility**:
   - Don't over-commit to uncertain areas
   - Build in abstraction where needed
   - Plan for multiple scenarios

3. **Flag for implementation**:
   - Mark decisions that depend on unknowns
   - Note what needs investigation
   - Will be resolved in execution phase

### Leveraging Agent Findings

Use agent findings to strengthen design:

1. **Pattern matching**: Reference similar implementations found by agents
2. **Integration validation**: Use agent findings to validate integration approach
3. **Risk assessment**: Incorporate historical findings from agents
4. **Consistency**: Ensure design follows patterns identified by agents

## Configuration

This command creates design decisions based on validated research. It leverages Claude Code's agent spawning capabilities to verify design approaches and find precedents.
