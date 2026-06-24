---
description: Transform design into detailed phased execution plan with embedded tasks
argument-hint: [project-directory]
---

# Create Execution Plan

Transforms design decisions into a detailed, phased execution plan with embedded tasks. Focuses on HOW to implement what was designed.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/create_execution docs/plans/2025-01-08-my-project/`):
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

3. **Read existing tasks.md if present**:
   - Check current status
   - Note any existing progress

**think deeply about HOW to bridge from current state to target state**

Synthesize research (current state) and design (target state) to determine the implementation path.
Remember: Now you're planning HOW to build what was designed.

### Step 2: Spawn Analysis Agents

**Leverage Claude Code's agent capabilities for implementation analysis:**

After reading all documents, spawn specialized agents in parallel:

**Sub-agents are READ-ONLY** — they return findings only; YOU write `tasks.md` after synthesizing.

```javascript
// Spawn analysis agents in parallel - all are read-only
Task({
  description: "Analyze file dependencies",
  prompt: `Analyze dependencies for implementing the design.

  From research.md:
  - Current file structure: [key files]
  - Integration points: [systems]

  From design.md:
  - Target architecture: [approach]
  - Components to build: [list]

  Determine:
  - Build order (what must be done first)
  - Parallel work opportunities
  - Critical path dependencies
  - External dependencies needed

  Return findings only; write nothing.`,
  subagent_type: "codebase-analyzer",
  model: "sonnet"
})

Task({
  description: "Identify test coverage needs",
  prompt: `Identify testing requirements for the implementation.

  From design.md:
  - Success criteria: [criteria]
  - Risk areas: [risks]

  From research.md:
  - Existing test patterns: [patterns]
  - Test frameworks in use: [frameworks]

  Determine:
  - Unit tests needed (with file:line for each component)
  - Integration tests required
  - Edge cases from risk analysis
  - Test fixtures needed

  Return findings only; write nothing.`,
  subagent_type: "codebase-analyzer",
  model: "sonnet"
})

Task({
  description: "Find similar implementation patterns",
  prompt: `Find examples of similar implementations in the codebase.

  From design.md:
  - Type of change: [type]
  - Components affected: [components]

  Search for:
  - Similar features already implemented
  - Phased rollout patterns used
  - Testing approaches for similar changes
  - Configuration patterns to follow

  Return findings only; write nothing.`,
  subagent_type: "pattern-finder",
  model: "haiku"
})
```

**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL agents - dependency, test, pattern agents ⛔⛔⛔**

### Step 3: Determine Implementation Strategy

**think deeply about the safest, most logical implementation sequence**

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

### Step 4: Generate Execution Plan

Update or create tasks.md with the following structure:

````markdown
---
project: [from existing frontmatter]
ticket: [from existing frontmatter]
created: [from existing frontmatter]
status: not-started
last_updated: [YYYY-MM-DD]
current_phase: 1
total_tasks: [calculated count]
completed_tasks: 0
depends_on: [research.md, design.md]
---

# Execution Plan: [Feature Name]

## Overview

Implementing [brief summary] as specified in design.md

**Design Approach**: [from design.md]
**Target State**: [from design.md success criteria]

## Implementation Strategy

### Phase Rationale
[Explain why phases are ordered this way - dependencies from agents, risk mitigation, etc.]

Based on dependency analysis:
- [Key dependency finding from agent]
- [Parallel work opportunity from agent]

### Testing Strategy
[Overall approach to testing throughout implementation, incorporating test coverage agent findings]

## Progress Overview

Progress is tracked in beads. To check current status:

```bash
bd stats                    # Overall project statistics
bd list --status=closed     # See completed tasks
bd list --status=in_progress # See active work
bd ready                    # See available work
```

**Phase status**:
- Phase 1: See beads milestone `[phase1-milestone-id]` - depends on [X] tasks
- Phase 2: See beads milestone `[phase2-milestone-id]` - depends on [Y] tasks
- Phase 3: See beads milestone `[phase3-milestone-id]` - depends on [Z] tasks

Use `bd show [milestone-id]` to see which tasks block each phase milestone.

---

## Phase 1: [Descriptive Name]

### Objective
[Single clear goal for this phase]

### Prerequisites
- [ ] Research validated
- [ ] Design approved
- [ ] Development environment ready
- [ ] [Dependencies from agent analysis]

### Changes Required

#### 1. [Component/Module Name]

**File**: `path/to/file.ext`

**Current State** (from research.md):
- [How it works now]
- [Key function at line X]

**Target State** (from design.md):
- [How it should work]
- [New capability needed]

**Implementation**:
```language
// At line [X], replace:
[old code]

// With:
[new code]
```

**Rationale**: [Why this specific implementation]
**Pattern Reference**: [Similar implementation from agent at file:line]

#### 2. [Another Component]

[Similar structure...]

### Tasks

**Note**: Task status is tracked ONLY in beads. The tasks below document WHAT needs to be done (the PLAN). For task STATUS, run `bd list` or check frontmatter `beads_tasks` for IDs.

#### Setup Tasks
- Create new directory structure at `path/to/new/` → `[beads:phase1_setup_1]`
- Install dependencies: `npm install [package]` → `[beads:phase1_setup_2]`
- Set up configuration in `config/feature.json` → `[beads:phase1_setup_3]`

#### Implementation Tasks
- Create [Component] class at `src/component.ts` → `[beads:phase1_impl_1]`
  - Implement constructor with dependency injection
  - Add [method1] for [purpose]
  - Add [method2] for [purpose]
- Modify [ExistingComponent] at `src/existing.ts:45` → `[beads:phase1_impl_2]`
  - Add integration with new component
  - Update error handling

#### Testing Tasks
(Generated from test coverage agent findings)
- Write unit tests for [Component] at `tests/component.test.ts` → `[beads:phase1_test_1]`
  - Test [scenario 1 from agent]
  - Test [edge case from agent]
  - Test [error condition from agent]
- Write integration tests at `tests/integration/feature.test.ts` → `[beads:phase1_test_2]`
  - Test [integration scenario from agent]

#### Integration Tasks
- Connect [Component] to [ExistingSystem] → `[beads:phase1_integration_1]`
- Update API endpoint at `api/routes.ts:78` → `[beads:phase1_integration_2]`
- Add database migration for new table → `[beads:phase1_integration_3]`

### Success Criteria

#### Automated Verification
- [ ] Unit tests pass: `npm test src/component.test.ts`
- [ ] Integration tests pass: `npm test:integration`
- [ ] Linting clean: `npm run lint`
- [ ] Type checking passes: `npm run typecheck`
- [ ] Build succeeds: `npm run build`

#### Manual Verification
(From design.md success criteria)
- [ ] [Specific user action] works correctly
- [ ] Performance meets target: [metric]
- [ ] Error messages are clear and helpful
- [ ] No regression in [related feature]

### Modified Files

Track all files changed in this phase:

#### Code Files
- `src/component.ts` - New component implementation
- `src/existing.ts` - Integration point modified
- `config/feature.json` - Configuration added

#### Test Files
- `tests/component.test.ts` - Unit tests for new component
- `tests/integration/feature.test.ts` - Integration tests

**Quick test command for this phase**:
```bash
npm test src/component.test.ts tests/integration/feature.test.ts
```

### ⛔ CHECKPOINT: Phase 1 Complete

Before proceeding to Phase 2:
1. ✅ All Phase 1 task beads issues closed (`bd list --status=closed`)
2. ✅ Phase 1 milestone beads issue closed
3. ✅ All automated verification passing
4. ✅ Manual verification confirmed by human
5. ✅ Update frontmatter: `current_phase: 2`

**Verification**: Run `bd show [phase1-milestone-id]` to confirm all blocking tasks are closed.

**Do not proceed without human confirmation of manual tests.**

---

## Phase 2: [Descriptive Name]

### Objective
[Clear goal for phase 2]

### Prerequisites
- [ ] Phase 1 complete and verified
- [ ] Phase 1 manual testing confirmed
- [ ] [Additional prerequisites from dependency agent]

[Continue with similar structure...]

---

## Implementation Discoveries

Things to determine during implementation:
- [Technical detail that needs investigation]
- [Configuration that needs testing]
- [Performance tuning needed]

Note: Update this section with findings as you implement.

---

## 📝 Completed Tasks Archive

Move completed tasks here weekly to keep active list focused.

### Week of [YYYY-MM-DD]
- [x] Task description (completed YYYY-MM-DD HH:MM)

---

## 🚧 Blockers & Notes

### Current Blockers

Blockers are tracked in beads. To see current blockers:

```bash
bd blocked    # Show all blocked issues and what blocks them
```

For reference, recently resolved blockers can be noted here:
- [Date]: [Brief description] - resolved by [solution]

### Implementation Notes
- [Important discovery during implementation]
- [Deviation from plan and why]

---

## 🔗 Quick Reference

### Key Files
- **Research**: [research.md](research.md) - Current state documentation
- **Design**: [design.md](design.md) - Target state specification
- **Main Entry**: `[from design]`
- **Config**: `[from design]`

### Common Commands
```bash
# Run all tests
npm test

# Run phase-specific tests
[phase test command]

# Build
npm run build

# Lint
npm run lint
```

### Design Decisions Reference
Quick lookup of key design decisions:
- [Decision 1]: [Brief reminder]
- [Decision 2]: [Brief reminder]
````

**⛔⛔⛔ BARRIER 3: STOP! Verify NO placeholder values - ALL tasks MUST be specific and executable ⛔⛔⛔**

### Step 5: Create Beads Issues

Create beads issues to track ALL work (phases AND granular tasks) across sessions.

**Critical**: Beads is the source of truth for status. Every task checkbox in tasks.md gets a corresponding beads issue.

#### 5a. Verify Beads is Initialized

```bash
bd doctor    # Check beads is working
```

If beads is not initialized, prompt user: "Run `bd init` to initialize beads tracking for this project."

#### 5a1. Beads Mode

**Beads mode**: `$BEADS_MODE` (set by the SessionStart hook). Git mode (default) — `.beads/` is committed for cross-session persistence; proceed normally. Stealth mode — `.beads/` is local-only; read `docs/beads-stealth-mode.md` and follow it. Both modes track tasks identically within a session.

#### 5b. Create Epic for the Project

```bash
bd create "[Project Name] Implementation" \
  --type=epic \
  --priority=2 \
  -d "Implementation tracking for [project]. See tasks.md for detailed plan."
```

**Capture the epic ID** from the output (e.g., `Created prompts-abc`). You'll need it for task references.

#### 5c. Create Phase Milestone Issues

For each phase in the execution plan, create a milestone issue:

```bash
# Phase 1 - capture the ID from output
bd create "Phase 1 Milestone: [Phase Name]" \
  --type=task \
  --priority=2 \
  -d "All Phase 1 tasks complete. Objective: [phase objective]. See tasks.md Phase 1 for details."
# → Created prompts-xyz (save this as PHASE1_MILESTONE_ID)

# Phase 2 - capture the ID from output
bd create "Phase 2 Milestone: [Phase Name]" \
  --type=task \
  --priority=2 \
  -d "All Phase 2 tasks complete. Objective: [phase objective]. See tasks.md Phase 2 for details."
# → Created prompts-abc (save this as PHASE2_MILESTONE_ID)

# Set up dependency: Phase 2 milestone depends on Phase 1 milestone
bd dep add [PHASE2_MILESTONE_ID] [PHASE1_MILESTONE_ID]
```

**Important**: Capture each ID as it's created. You'll need them for dependencies.

#### 5d. Create Task Issues for Each Task

**CRITICAL**: Create a beads issue for EVERY task checkbox in the execution plan.

For each task in each phase:

```bash
# Setup task example
bd create "Create new directory structure at path/to/new/" \
  --type=task \
  --priority=2 \
  -d "Phase 1 setup task. Create directory structure for new component."
# → Created prompts-def (save as TASK1_ID)

# Implementation task example
bd create "Create [Component] class at src/component.ts" \
  --type=task \
  --priority=2 \
  -d "Phase 1 implementation. Create component with constructor, method1 for [purpose], method2 for [purpose]."
# → Created prompts-ghi (save as TASK2_ID)

# Testing task example
bd create "Write unit tests for [Component] at tests/component.test.ts" \
  --type=task \
  --priority=2 \
  -d "Phase 1 testing. Test scenario 1, edge case X, error condition Y."
# → Created prompts-jkl (save as TASK3_ID)

# Integration task example
bd create "Connect [Component] to [ExistingSystem]" \
  --type=task \
  --priority=2 \
  -d "Phase 1 integration. Update API endpoint at api/routes.ts:78."
# → Created prompts-mno (save as TASK4_ID)
```

**Task Creation Guidelines**:
- Title should match the task description from tasks.md
- Description includes phase, task type (setup/implementation/testing/integration), and key details
- All tasks start with priority 2 (medium)
- Use --type=task for all granular tasks

#### 5e. Set Up Task Dependencies

Link tasks to their phase milestone and to each other:

```bash
# All Phase 1 tasks block the Phase 1 milestone
bd dep add [PHASE1_MILESTONE_ID] [TASK1_ID]
bd dep add [PHASE1_MILESTONE_ID] [TASK2_ID]
bd dep add [PHASE1_MILESTONE_ID] [TASK3_ID]
bd dep add [PHASE1_MILESTONE_ID] [TASK4_ID]

# Implementation tasks depend on setup tasks being done
bd dep add [TASK2_ID] [TASK1_ID]

# Testing tasks depend on implementation
bd dep add [TASK3_ID] [TASK2_ID]

# Integration depends on both implementation and testing
bd dep add [TASK4_ID] [TASK2_ID]
bd dep add [TASK4_ID] [TASK3_ID]
```

**Dependency Principles**:
- Setup tasks have no dependencies (start immediately)
- Implementation depends on setup
- Testing depends on implementation
- Integration depends on implementation and testing
- Phase milestone depends on ALL phase tasks
- Next phase milestone depends on previous phase milestone

**Tip**: Use parallel task creation for efficiency:
- Spawn multiple `bd create` commands using parallel agents
- Capture all IDs, then set up dependencies in a second pass

**Important**: Capture ALL task IDs. You'll need them for frontmatter tracking.

#### 5f. Update tasks.md with Issue References

Add beads tracking to tasks.md frontmatter for ALL issues:

```yaml
beads_epic: [epic-id]
beads_phases:
  phase1_milestone: [phase1-milestone-id]
  phase2_milestone: [phase2-milestone-id]
  phase3_milestone: [phase3-milestone-id]
beads_tasks:
  # Phase 1 tasks
  phase1_setup_1: [task-id]
  phase1_setup_2: [task-id]
  phase1_impl_1: [task-id]
  phase1_impl_2: [task-id]
  phase1_test_1: [task-id]
  phase1_test_2: [task-id]
  phase1_integration_1: [task-id]
  # Phase 2 tasks
  phase2_setup_1: [task-id]
  phase2_impl_1: [task-id]
  # ... etc for all tasks
```

**Frontmatter Guidelines**:
- Use descriptive keys that match the task structure
- Format: `phaseN_category_number` (e.g., `phase1_setup_1`, `phase2_impl_3`)
- Keep the same order as tasks appear in the plan
- This enables easy lookup: "What's the beads ID for Phase 2 implementation task 1?"

Add a quick reference section with key commands:

```markdown
## Beads Issue Tracking

This project uses beads for ALL task tracking across sessions.

**Epic**: [epic-id]

**Phase Milestones**:
- Phase 1: [phase1-milestone-id] (all Phase 1 tasks must complete)
- Phase 2: [phase2-milestone-id] (all Phase 2 tasks must complete)
- Phase 3: [phase3-milestone-id] (all Phase 3 tasks must complete)

**Granular Tasks**: See frontmatter `beads_tasks` section for all task IDs.

**Essential Commands**:
- `bd ready` - See what's ready to work on (no blockers)
- `bd show [id]` - View task details and dependencies
- `bd update [id] --status in_progress` - Claim a task
- `bd close [id]` - Complete a task
- `bd blocked` - See what's currently blocked
- `bd list --status=in_progress` - See your active work

**Status Source**: Beads is the source of truth for all task status. Do NOT use markdown checkboxes for tracking.
```

### Step 6: Validate Completeness

Verify with agent findings:

1. **All success criteria** from design.md have corresponding tasks
2. **All scope items** from design.md are addressed
3. **Knowledge gaps** from research.md are handled
4. **Risk mitigations** from design.md are incorporated
5. **Every task is specific and executable**
6. **Test coverage** matches test agent recommendations
7. **Dependencies** follow agent-identified order

### Step 7: Present the Plan

```
✅ Execution plan created at: [path]/tasks.md

Implementation structure:
- Phase 1: [Name] - [X] tasks
- Phase 2: [Name] - [Y] tasks
- Phase 3: [Name] - [Z] tasks

Total tasks: [total count]

Agent findings incorporated:
- Dependency order: [key dependency from agent]
- Test coverage: [X] unit tests, [Y] integration tests
- Similar patterns: [reference to pattern agent findings]

Beads tracking:
- Epic: [epic-id]
- Phase milestone issues created with dependencies
- ALL granular tasks created as beads issues
- Task dependencies set up (setup → impl → test → integration)
- Use `bd ready` to find available work
- Total beads issues: [count] ([X] phase milestones + [Y] granular tasks)

Key features of the plan:
- Clear implementation sequence based on dependency analysis
- Specific code changes with before/after context
- Comprehensive test coverage from agent analysis
- Automated and manual verification per phase
- Quick test commands to avoid running full suite
- Complete beads integration for ALL task tracking (no markdown checkboxes)
- Survives session boundaries and context compaction

Next steps:
1. Review the execution plan in tasks.md (documentation)
2. Run `bd ready` to see available work (first tasks with no dependencies)
3. Run `/implement_tasks` to begin implementation with TDD
4. Track ALL progress with beads (`bd update [id] --status in_progress`, `bd close [id]`)
5. Never use markdown checkboxes for status - beads is source of truth
```

## Important Guidelines

### Execution Planning Principles

1. **Bridge Current to Target**:
   - Start from research (current state)
   - End at design (target state)
   - Plan the transformation path

2. **Phase by Risk and Dependencies**:
   - Use agent findings to order phases
   - Riskiest changes early (fail fast)
   - Dependencies before dependents
   - Infrastructure before features

3. **Make Tasks Executable**:
   - Specific file and line references
   - Exact code to add/change
   - Clear test scenarios from agent
   - Runnable commands

4. **Enable Incremental Progress**:
   - Each phase independently valuable
   - Checkpoints prevent cascading issues

### What Belongs in Execution vs Design

**Execution (THIS document)**:

- ✅ Phase sequencing and dependencies
- ✅ Specific code changes
- ✅ File modifications with line numbers
- ✅ Test writing tasks
- ✅ Command sequences

**Design (design.md)**:

- ❌ Architecture decisions (already made)
- ❌ Success criteria (reference them)
- ❌ Scope decisions (already defined)
- ❌ Technical approach (already chosen)

### Handling Implementation Discoveries

Some things can only be determined during coding:

1. **Document in "Implementation Discoveries"**:
   - Note what needs investigation
   - Update with findings as discovered
   - Adjust tasks if needed

2. **Don't Block on Unknowns**:
   - Make reasonable assumptions
   - Plan to test and adjust
   - Document the uncertainty

3. **Update During Implementation**:
   - Add discovered constraints
   - Note performance findings
   - Record configuration needs

### Leveraging Agent Findings

Use agent findings throughout execution plan:

1. **Dependencies**: Order phases based on dependency agent analysis
2. **Testing**: Incorporate test coverage agent recommendations
3. **Patterns**: Reference similar implementations found by pattern agent
4. **Risk mitigation**: Address risks identified by agents

## Task Granularity

Tasks should be:

- **Specific**: "Create PaymentRetry class at src/retry/PaymentRetry.ts"
- **Sized**: 1-4 hours of work typically
- **Testable**: Clear completion criteria
- **Independent**: Minimal blocking between tasks

## Configuration

This command creates an execution plan from approved research and design documents. It leverages Claude Code's agent spawning capabilities to analyze dependencies, test coverage, and similar patterns.
