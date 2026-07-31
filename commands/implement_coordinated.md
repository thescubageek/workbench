---
description: Coordinate task implementation using sequential worker agents with fresh context
argument-hint: "[project-directory] [phase-number|continue]"
---

# Implement Tasks (Coordinated)

**Next-generation task implementation using coordinator + worker agent pattern.**

You coordinate task implementation from `tasks.md` by spawning worker agents sequentially, each with focused context and fresh context window. This prevents main session context bloat.

## Evolution from implement_tasks

This command evolves the original `implement_tasks` with one key improvement:

- **Coordinator Pattern**: Main agent orchestrates, workers implement in fresh context
- **Context Efficiency**: Main window stays clean, workers are ephemeral
- **Sequential Execution**: Simple, predictable, no coordination complexity
- **Fresh Context**: Each task starts with clean slate, no accumulation

**All learnings preserved:**

- ⛔ BARRIER synchronization points
- TDD cycle enforcement (Red → Green → Refactor)
- Beads for ALL tracking (phases + tasks)
- ZERO SCOPE CREEP discipline
- Phase boundary verification
- Manual verification checkpoints

## Initial Response

When invoked, check for arguments:

1. **If directory and phase provided** (e.g., `/implement_coordinated docs/plans/2025-01-08-my-project/ 1`):
   - Use `$1` as project directory
   - Use `$2` as phase number (or "continue" to resume)
   - Read all documentation immediately
   - Begin coordination

2. **If partial arguments**:
   - Use provided arguments
   - Prompt only for missing ones

3. **If no arguments**:

   ```
   I'll coordinate task implementation using worker agents with fresh context. Please provide:
   1. Path to the project documentation directory (e.g., docs/plans/2025-01-08-my-project/)
   2. Which phase to implement (number or "continue" to resume from current phase)
   3. Any specific context or constraints for this implementation session (optional)

   I'll spawn worker agents sequentially to keep the main session context clean.
   ```

## Implementation Philosophy

### Core Principles

All principles from `implement_tasks` PLUS:

1. **Coordination Over Direct Implementation**: Main agent orchestrates, doesn't code
2. **Context Extraction**: Build minimal context packages for workers
3. **Sequential Execution**: Simple, predictable, one task at a time
4. **Worker Isolation**: Each worker operates in fresh context
5. **Model Selection**: Right model for task complexity (haiku/sonnet/opus)
6. **Main Session Stays Clean**: No context accumulation in coordinator

### CRITICAL: NO SCOPE ADDITIONS - NONE

Same zero-tolerance policy as original:

- **NEVER** add features not in tasks.md
- **NEVER** refactor beyond what's specified
- **NEVER** make "improvements" not explicitly asked for
- **NEVER** add extra error handling, validation, or edge cases
- **ONLY** implement what is EXPLICITLY written in tasks.md
- If something seems missing, STOP and ask - DO NOT add it

## Process Steps

### Step 1: Read and Understand Context

**⛔⛔⛔ BARRIER 1: STOP! Read ALL documentation files FULLY - NO SHORTCUTS ⛔⛔⛔**

```javascript
const projectDir = $1 || /* prompt for it */;
const phase = $2 || /* prompt for it */;

// Read all project files FULLY
const researchFile = `${projectDir}/research.md`;
const designFile = `${projectDir}/design.md`;
const tasksFile = `${projectDir}/tasks.md`;
```

1. **Read project structure**:
   - Check that specified directory exists
   - Verify presence of research.md, design.md, tasks.md

2. **Read research.md FULLY**:
   - Understand what currently exists in the codebase
   - Note patterns and conventions to follow
   - Identify key file:line references
   - Extract testing framework, file structure, naming conventions

3. **Read design.md FULLY**:
   - Understand the desired end state
   - Review success criteria for the phase
   - Note automated and manual verification requirements
   - Identify architectural constraints

4. **Read tasks.md FULLY**:
   - Identify current phase from frontmatter
   - Count completed vs remaining tasks
   - Read beads tracking configuration
   - Understand task structure and dependencies

**think deeply about:**

- What patterns should workers follow from research?
- What's the goal from the design?
- What EXACT tasks are specified in tasks.md?
- What minimal context does each worker need?

After reading all documentation, prepare to spawn workers sequentially.

### Step 2: Verify Beads Configuration

**CRITICAL**: Use beads for ALL task tracking (phases AND granular tasks).

#### Verify Beads is Available (fast-fail)

Check availability with a **fast, filesystem-only** probe — do NOT use `bd doctor`
(it spawns a slow Dolt process and can hang). See
[docs/beads-fast-fail.md](../docs/beads-fast-fail.md).

```bash
# Prefer the SessionStart-computed flag; fall back to a filesystem probe.
if [ "$BEADS_AVAILABLE" = "yes" ] || { command -v bd >/dev/null 2>&1 && [ -d .beads ]; }; then
  : # beads usable — proceed
else
  echo "⚠️ Beads unavailable — see below."
fi
```

**If beads is unavailable** (bd not installed, or `.beads/` not initialized), say
this **once** and move on — do not loop or re-probe:

```
⚠️ Beads Not Initialized

Beads is required for task tracking in the wb workflow.

To initialize beads for this project:
```bash
cd [project-root]
bd init
```

Then run `/wb:create_execution` to set up beads issues for all tasks.

```

Stop and wait for user to initialize beads before proceeding.

#### Beads Mode

**Beads mode**: `$BEADS_MODE` (set by the SessionStart hook). Git mode (default) — `.beads/` committed for cross-session persistence; proceed normally. Stealth mode — local-only; read `docs/beads-stealth-mode.md`.

#### Verify Beads Tracking Configuration

Check that tasks.md frontmatter has beads tracking:

```yaml
beads_epic: [epic-id]
beads_phases:
  phase1_milestone: [milestone-id]
beads_tasks:
  phase1_setup_1: [task-id]
  phase1_impl_1: [task-id]
  # ... all tasks
```

**If frontmatter is missing**: Tell user "Run `/wb:create_execution` to configure beads tracking."

### Step 3: Extract Context Package

**NEW: Build minimal context package for workers**

From the documentation you've read, extract ONLY what workers need:

```javascript
const contextPackage = {
  // From research.md - patterns workers must follow
  patterns: {
    testingFramework: "jest | pytest | go test | ...",
    testFileLocation: "tests/ | __tests__ | *_test.go | ...",
    fileStructure: "src/ layout | pkg/ layout | ...",
    namingConventions: "camelCase | snake_case | ...",
    importPatterns: "how modules are imported",
    errorHandling: "established patterns"
  },

  // From design.md - relevant to this phase
  design: {
    phaseGoal: "what this phase achieves",
    successCriteria: ["criterion 1", "criterion 2"],
    constraints: ["constraint 1", "constraint 2"],
    architecturalApproach: "key decisions"
  },

  // From tasks.md frontmatter
  beads: {
    epicId: "beads-xxx",
    phaseMilestoneId: "beads-yyy",
    mode: "$BEADS_MODE"
  },

  // Test commands
  testCommands: {
    unit: "npm test | pytest | go test ./...",
    specific: "npm test path/to/file | pytest tests/file.py",
    coverage: "npm test -- --coverage | pytest --cov"
  },

  // File references relevant to this phase
  relevantFiles: [
    "src/feature/file1.ts:123 - existing pattern to follow",
    "tests/feature/test1.spec.ts:45 - test structure example"
  ]
};
```

**Minimize context**: Only include what workers actually need to implement tasks.

### Step 4: Find Available Work

**⛔ BARRIER 2: Get ready tasks from beads**

Query beads to find what's ready to work on:

```bash
# Get ready tasks (no blockers)
bd ready

# This shows tasks that:
# - Have no dependencies, OR
# - All dependencies are closed
```

**Start with the first ready task**. After each worker completes, `bd ready` will show newly unblocked tasks.

### Step 5: Spawn Worker Agents Sequentially

**For each ready task in the phase**, I'll spawn a focused worker agent:

1. **Get next task**: Run `bd ready` to find available work
2. **Check task details**: Run `bd show [task-id]` for requirements
3. **Capture the base ref** (for scope verification): record the current HEAD/working-tree state BEFORE the worker starts, so the verifier can diff exactly this task's changes rather than assuming `HEAD~1`:

   ```bash
   TASK_BASE_REF=$(git rev-parse HEAD)   # pass to the verifier as Base Ref in Step 6
   ```

4. **Determine model**:
   - Haiku: Simple tasks (config, docs, renames)
   - Sonnet: Standard implementation (tests, new functions, integrations)
   - Opus: Everything else (bugs, refactoring, architecture) - DEFAULT
5. **Spawn worker agent**:

   ```
   Use the general-purpose agent to implement this task.

   Provide the agent with:
   - Task ID: ${taskId}
   - Task Title: ${taskTitle}
   - Task Description: ${taskDescription}
   - Context Package: ${patterns, design, file references}
   - Beads Commands: bd update [id] --status in_progress, bd close [id]

   The worker must follow TDD:
   1. RED: Write failing test
   2. GREEN: Minimal implementation
   3. REFACTOR: Clean up
   4. Close beads issue when complete

   Worker should return: files changed, tests modified, test command, summary.
   ```

6. **Collect worker output** when complete
7. **Proceed to verification** (Step 6)

**Loop**: Spawn → Wait → Verify → Next task

#### Worker Prompt Template

```markdown
function buildWorkerPrompt(task, taskDetails, contextPackage) {
  return `You are a focused implementation worker for a single task.

## Your Task
**ID**: ${task.id}
**Title**: ${task.title}
**Description**: ${taskDetails.description}

## Context You Need

### Patterns to Follow
${formatPatterns(contextPackage.patterns)}

### Design Context
**Phase Goal**: ${contextPackage.design.phaseGoal}
**Success Criteria**: ${contextPackage.design.successCriteria}
**Constraints**: ${contextPackage.design.constraints}

### Relevant File References
${formatFileReferences(contextPackage.relevantFiles, task)}

### Test Commands
${formatTestCommands(contextPackage.testCommands)}

## Your Process (TDD Cycle)

**⛔ CRITICAL: Follow this EXACT process**

### 1. Claim the Task
\`\`\`bash
bd update ${task.id} --status in_progress
\`\`\`

### 2. RED Phase - Write Failing Test First
- Create/update test file following patterns above
- Write test that captures the requirement EXACTLY as specified
- NO additional test cases not specified in the task
- Run test to confirm it fails: ${contextPackage.testCommands.specific}
- Confirm test fails for the RIGHT reason

### 3. GREEN Phase - Minimal Implementation
- Write ONLY enough code to make the test pass
- Focus on making it work, not making it perfect
- NO extra features, NO "improvements", NO scope additions
- Run test to confirm it passes
- Run related tests to ensure no regression

### 4. REFACTOR Phase - Clean Up While Tests Stay Green
- Improve code quality while keeping tests green
- Follow patterns from context above
- Run tests after each change
- Stop when code is clean and tests pass

### 5. Close the Task
\`\`\`bash
bd close ${task.id} --reason "Implemented ${task.title}, tests passing"
\`\`\`

## CRITICAL Constraints

- **ZERO SCOPE CREEP**: Implement ONLY what's in the task description above
- **NO ADDITIONS**: No extra features, error handling, or validation
- **FOLLOW PATTERNS**: Use patterns from context, don't invent new ones
- **TEST FIRST**: Always RED → GREEN → REFACTOR
- **ONE TASK ONLY**: Complete this task and return

## Expected Output

Return a summary including:
1. What you implemented
2. Files created/modified
3. Tests added/modified
4. Test commands to verify
5. Any issues encountered
6. Task beads status (should be closed)

If you encounter errors or blockers:
- Document them clearly
- Leave task in in_progress state
- Return detailed error information
`;
}
```

### Step 6: After Each Worker Completes

**⛔ BARRIER 3: Collect output and verify before next task**

After each worker completes:

1. **Verify task was closed**:

   ```bash
   bd show ${taskId}  # Should show status: closed
   ```

2. **Collect worker output**:
   - Files created/modified
   - Tests added/modified
   - Test commands to verify
   - Any issues encountered

3. **Verify task completion**:

   Spawn the task-verifier agent to validate the worker's implementation:

   ```
   Use the task-verifier agent to verify task completion.

   Provide the agent with:
   - Task ID: ${taskId}
   - Task Description: ${taskDetails.description}
   - Base Ref: ${TASK_BASE_REF}  (captured before the worker started, for scope diffing)
   - Test Command: ${workerOutput.testCommand}
   - Files Changed: ${workerOutput.filesChanged}
   - Tests Modified: ${workerOutput.testsModified}
   - Worker Summary: ${workerOutput.summary}

   The agent will run tests, check scope adherence, and return a structured
   markdown report with Status: PASS or FAIL.
   ```

4. **Parse verification result autonomously**:

   Extract pass/fail from agent's markdown report:

   ```javascript
   // Agent returns text like: "### Status: PASS" or "### Status: FAIL"
   const passed = verificationReport.includes("### Status: PASS");
   const failed = verificationReport.includes("### Status: FAIL");
   ```

   **If PASS**:
   - Add to success log
   - Collect modified files for aggregation
   - Proceed to step 5 (next task)

   **If FAIL**:
   - Attempt automatic fix (up to 2 retries):

   **Retry 1:**

   ```
   Verification failed. Spawn a fix worker using the general-purpose agent with opus model.

   Provide:
   - Task ID: ${taskId}
   - Original Task: ${taskDetails.description}
   - Verification Report: ${verificationReport}
   - Instructions: Fix the specific issues identified. Close beads issue when done.
   ```

   **Re-verify** using task-verifier agent with same context.

   **Retry 2** (if still failing): Repeat process with additional context.

   **After 2 failed retries**:
   - Add to blocking issues list for phase checkpoint review
   - Continue to next task (will surface issues at phase boundary)
   - Don't block autonomous flow on individual task failures

5. **Add to aggregated lists** (after pass):
   - Modified files (for final reporting)
   - Test commands (for phase verification)
   - Implementation notes (if worker found issues)

6. **Check for newly ready tasks**:

   ```bash
   bd ready  # See what's now unblocked
   ```

7. **Spawn next worker** (repeat Step 5)

**Handle worker failures** (rare - worker didn't finish):

If worker leaves task in `in_progress` (didn't close beads issue):

```
⚠️ Worker Did Not Complete Task

Task ${taskId} status: in_progress (should be closed)
Worker reported: ${workerError}

This means the worker crashed or couldn't complete the task.
Verification agent is NOT run if worker didn't finish.

**Options**:
1. Retry worker with same context
2. Retry worker with additional context
3. Mark task as blocked, investigate
4. Manual intervention required

How should I proceed?
```

Note: This is different from verification failure. Verification runs AFTER worker successfully completes and closes the beads issue.

### Step 7: Aggregate Results

**⛔ BARRIER 4: All phase tasks complete**

After all workers for the phase complete, aggregate their outputs:

#### Update Modified Files Section

Collect modified files from all workers:

```markdown
### 📝 Modified Files (Phase ${phase})

#### Code Files
${aggregatedCodeFiles.map(f => `- \`${f.path}\` - ${f.description}`).join('\n')}

#### Test Files
${aggregatedTestFiles.map(f => `- \`${f.path}\` - ${f.description}`).join('\n')}

**Quick test commands:**
\`\`\`bash
# Run all tests for this phase
${generatePhaseTestCommand(aggregatedTestFiles)}
\`\`\`
```

#### Check Phase Completion

```bash
# Verify all phase tasks are closed
bd show ${phaseMilestoneId}

# Should show: blockedBy: [] (no remaining dependencies)
```

### Step 8: Run Phase Verification

**⛔ CHECKPOINT: Phase ${phase} Complete**

Same verification process as original `implement_tasks`:

#### 1. Verify All Phase Tasks Closed

```bash
bd show ${phaseMilestoneId}  # Should have no blockers
bd list --status=closed | grep "phase${phase}"
bd list --status=in_progress  # Should be empty for this phase
```

**Requirement**: All phase task beads issues must be closed.

#### 2. Run Automated Verification

```bash
# Adapt these to actual commands from tasks.md
make test           # or npm test, go test ./..., pytest
make lint           # or npm run lint, golangci-lint run
make typecheck      # or npm run typecheck, go build ./...
make build          # or npm run build, go build
```

**Requirement**: All automated checks must pass.

#### 3. Request Manual Verification

Present manual verification checklist to user:

```
✅ Phase ${phase} Automated Verification Complete

**Automated checks passed:**
- ✅ All tests passing: [test command]
- ✅ Linting clean: [lint command]
- ✅ Build successful: [build command]

**Worker agents completed:**
${workerSummaries.map(w => `- ✅ ${w.title}: ${w.summary}`).join('\n')}

**Beads state:**
- ✅ All Phase ${phase} tasks closed: [list task IDs]
- 🔓 Phase milestone ready to close: ${phaseMilestoneId}

**Manual verification required:**

Please perform the following manual checks from design.md:

${manualVerificationSteps}

Reply when manual verification is complete and I'll close the phase milestone.
```

**Requirement**: Wait for user confirmation before proceeding.

#### 4. Close Phase Milestone

**ONLY after user confirms manual verification**:

```bash
bd close ${phaseMilestoneId} --reason "Phase ${phase} complete: ${summary}. All ${taskCount} tasks closed via worker agents, automated verification passed, manual verification confirmed."
bd ready  # Check what's now unblocked (next phase tasks)
```

#### 5. Report Completion

```
✅ Phase ${phase} Complete (Coordinated Execution)

**Execution Statistics:**
- Worker agents spawned: ${workerCount}
- Total tasks completed: ${completedCount}
- Execution mode: sequential

**Beads tracking:**
- ✅ Phase ${phase} milestone closed: ${phaseMilestoneId}
- 🔓 Unblocked: ${nextPhaseMilestoneId} and its initial tasks

**Progress Summary:**
- Phase ${phase}: ${taskCount} tasks completed via workers
- Next phase: ${nextPhaseTaskCount} tasks available (run \`bd ready\`)
- Files modified: ${codeFileCount} code files, ${testFileCount} test files

**Context Efficiency:**
- Main agent context: Constant (no accumulation)
- Worker contexts: Ephemeral (discarded after each task)
- No compaction needed during phase implementation

Ready to proceed to Phase ${phase + 1}.
```

### Step 9: Update Status

After phase completion:

1. **Verify beads state**:

   ```bash
   bd stats    # Check overall progress
   bd list --status=closed    # See what's complete
   bd ready    # See what's available next
   ```

2. **Optionally update tasks.md frontmatter** (for human reference):

   ```yaml
   current_phase: ${phase + 1}
   last_updated: YYYY-MM-DD
   status: in-progress
   execution_mode: coordinated  # Note the new pattern
   ```

3. **Add implementation notes** with worker insights:

   ```markdown
   ## Implementation Notes
   - [YYYY-MM-DD] Phase ${phase} complete using coordinated workers:
     - ${workerCount} workers spawned (sequential execution)
     - Main context kept clean, no compaction needed
     - Key learnings: ${aggregatedLearnings}
   ```

   Then write the durable items from `${aggregatedLearnings}` to **`knowledge/staging/`**, per `skills/knowledge-store`. This matters more here than anywhere else: each worker's context is discarded when it finishes, so a learning not written down is genuinely gone. Best-effort; skip silently if `./scripts/knowledge-worktree` exits non-zero. Worker output you are relaying is `origin: model-narrated` — you did not observe it, a worker reported it.

4. **Sync beads state**:

   ```bash
   bd sync    # Export beads to .beads/issues.jsonl

   # In git mode, commit the beads state
   if [ "$BEADS_MODE" != "stealth" ]; then
     git add .beads/
     git commit -m "Update beads state after Phase ${phase} (coordinated execution)"
   fi
   ```

## Helper Functions

### Determine Worker Model

```javascript
function determineModel(taskDetails) {
  // Extract complexity indicators from task
  const description = taskDetails.description.toLowerCase();
  const title = taskDetails.title.toLowerCase();
  const combined = `${title} ${description}`;

  // Haiku for simple tasks (config, docs, renames)
  const haikuPatterns = [
    /\b(config|configuration|env|environment variable)/,
    /\b(documentation|readme|comment|doc string)/,
    /\b(rename|move|delete)\s+(file|directory|folder)/,
    /\b(update|change)\s+(version|dependency)/,
    /\btypo\b/
  ];

  for (const pattern of haikuPatterns) {
    if (pattern.test(combined)) {
      return 'haiku';
    }
  }

  // Sonnet for straightforward implementation tasks
  const sonnetPatterns = [
    /\b(implement|add|create|build|write)\s+(test|unit test)/,
    /\b(add|create)\s+(function|method|class|component)/,
    /\b(wire up|integrate|connect)\b/,
    /\b(update|modify)\s+(existing|current)/
  ];

  for (const pattern of sonnetPatterns) {
    if (pattern.test(combined)) {
      return 'sonnet';
    }
  }

  // Default → opus (conservative, better at complex tasks)
  // This includes: bug fixing, refactoring, architecture, algorithms, security
  return 'opus';
}
```

## Resume Logic

When resuming work (phase = "continue"):

1. **Check beads state** (source of truth):

   ```bash
   bd stats           # Overall progress
   bd ready           # Available work
   bd list --status=in_progress  # Any workers that didn't finish?
   bd list --status=closed        # Completed work
   ```

2. **Review context**:
   - Read tasks.md "Implementation Notes" for worker insights
   - Read research.md and design.md for context
   - Check current_phase in frontmatter

3. **Handle incomplete workers**:
   - If tasks are stuck in `in_progress`, investigate why
   - Review worker outputs for errors
   - Retry failed tasks with adjusted context

4. **Continue coordination**:
   - Extract context package
   - Run `bd ready` to find next task
   - Spawn worker for next available task
   - Repeat until phase complete

## Advantages Over Sequential Implementation

### Context Efficiency (PRIMARY BENEFIT)

**Sequential** (`implement_tasks`):

```
Main context grows: Research + Design + Task1 + Task2 + Task3 + ...
Token usage: Linear growth, can exhaust window, requires compaction
```

**Coordinated** (`implement_coordinated`):

```
Main context: Research + Design + Coordination logic (stays constant)
Worker contexts: Minimal context per task (ephemeral, discarded after completion)
Token usage: Main stays constant, workers are isolated
```

**Result**: No context accumulation in main session, no need for compaction

#### Why this matters: the ~75k "smart zone"

Models do their best work inside a bounded working context — empirically a
"smart zone" of roughly **75k tokens**. Past that, recall and reasoning degrade
well before the hard context limit is reached. The coordinator/fresh-worker
split exists to keep the main session inside that zone: the coordinator holds
only research + design + coordination logic (constant), and each worker starts
fresh and is discarded, so neither accumulates toward the degradation cliff.

This is the same backpressure principle that governs runtime tool output
(see `scripts/quiet` and the `tdd-discipline` GREEN step): every token that
conveys nothing — a 200-line all-green test run, a finished task's transcript —
is a token stolen from the smart zone. Architecture (fresh workers) handles the
*accumulated* context; output backpressure handles the *per-iteration* context.
Both serve the same budget.

> Source: humanlayer, "context-efficient backpressure" —
> <https://www.humanlayer.dev/blog/context-efficient-backpressure>.
> The article's own thesis (human time costs ~10x tokens; over-conservative
> models waste more via re-runs) is why this reduces cost without trading away
> reliability — failures still surface in full.

### Error Isolation

**Sequential**: Error in Task 3 pollutes context for Tasks 4, 5, 6...

**Coordinated**: Error in Worker 3 isolated, doesn't affect Workers 4, 5, 6

- Fresh start for each task
- Failures are localized

### Model Selection

**Sequential**: All tasks use same model (usually sonnet)

**Coordinated**: Right model for each task

- Simple config/docs: haiku (cheaper, faster)
- Standard implementation: sonnet (tests, new functions, integrations)
- Everything else: opus (default - bugs, refactoring, architecture)
- Cost optimization per task

## Migration from implement_tasks

To migrate existing projects:

1. **No changes needed to documentation structure** (research.md, design.md, tasks.md)
2. **No changes needed to beads configuration** (epic, milestones, tasks)
3. **Switch command**: Use `/wb:implement_coordinated` instead of `/wb:implement_tasks`

Both commands produce identical results. Coordinated version just keeps main session context clean.

## Important Guidelines

### DO

- ✅ Extract minimal context packages for workers
- ✅ Spawn workers sequentially (one at a time)
- ✅ Use appropriate model for task complexity
- ✅ Wait for each worker to complete before next
- ✅ Aggregate worker outputs thoroughly
- ✅ Handle worker failures gracefully
- ✅ All original `implement_tasks` best practices

### DON'T (ABSOLUTELY FORBIDDEN)

- ❌ All prohibitions from original `implement_tasks`
- ❌ **NEVER** spawn multiple workers in parallel (keep it simple)
- ❌ **NEVER** allow workers to add scope
- ❌ **NEVER** pass entire docs to workers (extract context)
- ❌ **NEVER** proceed without waiting for worker completion
- ❌ **NEVER** skip worker output aggregation
- ❌ **NEVER** close phase milestone before manual verification

## Configuration

This command coordinates task implementation using sequential worker agents with focused context. It preserves all disciplines from `implement_tasks` while keeping the main session context clean.

**Recommended for**: Long phases with many tasks, sessions where context compaction would be disruptive, or when you want the main window available for monitoring/debugging.
