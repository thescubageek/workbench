# implement — sub-agent prompts

Read the **section you need**, when its step directs you to.

Sections: `Worker prompt` (Step 5) · `Verifier prompt` (Step 6) · `Escalation worker prompt`
(Step 6, after a verified failure)

## Worker prompt

Step 5 — spawn the `task-worker` agent with this prompt. The agent definition
(`agents/task-worker.md`) already carries its tools, its preloaded `tdd-discipline` skill, its
turn cap, and the constraints below; this prompt supplies only what changes per task.

```markdown
function buildWorkerPrompt(task, contextPackage) {
  return `You are a focused implementation worker for a single task.

## Why this phase exists

${contextPackage.design.why}

## Your Task
**ID**: ${task.id}
**Title**: ${task.title}
**Description**: ${task.description}

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

### 1. RED Phase - Write Failing Test First
- Create/update test file following patterns above
- Write test that captures the requirement EXACTLY as specified
- NO additional test cases not specified in the task
- Run test to confirm it fails: ${contextPackage.testCommands.specific}
- Confirm test fails for the RIGHT reason

### 2. GREEN Phase - Minimal Implementation
- Write ONLY enough code to make the test pass
- Focus on making it work, not making it perfect
- NO extra features, NO "improvements", NO scope additions
- Run test to confirm it passes
- Run related tests to ensure no regression

### 3. REFACTOR Phase - Clean Up While Tests Stay Green
- Improve code quality while keeping tests green
- Follow patterns from context above
- Run tests after each change
- Stop when code is clean and tests pass

### 4. Flip the checkbox — your final act
In \`${contextPackage.tasksFile}\`, change this task's \`- [ ]\` to \`- [x]\` and append
\`(completed YYYY-MM-DD HH:MM)\`.

**Do this last, and do not commit.** The coordinator commits after verification. The flipped
checkbox sitting in an uncommitted tree is how the coordinator knows you finished rather than
ran out of budget — so flipping it early, or committing yourself, destroys the only signal
that distinguishes a truncated worker from a failed one.

## CRITICAL Constraints

- **ZERO SCOPE CREEP**: Implement ONLY what's in the task description above
- **NO ADDITIONS**: No extra features, error handling, or validation
- **FOLLOW PATTERNS**: Use patterns from context, don't invent new ones
- **TEST FIRST**: Always RED → GREEN → REFACTOR
- **ONE TASK ONLY**: Complete this task and return
- **DO NOT COMMIT**: the coordinator commits after the verifier passes

## Expected Output

Return a summary including:
1. What you implemented
2. Files created/modified
3. Tests added/modified
4. Test commands to verify
5. Any issues encountered — including anything you found and deliberately did *not* fix
6. Confirmation that the task's checkbox is now [x]

If you encounter errors or blockers:
- Document them clearly
- Leave the checkbox unflipped
- Return detailed error information
`;
}
```

## Verifier prompt

Step 6 — spawn the `task-verifier` agent after the worker returns.

```
Use the task-verifier agent to verify task completion.

Provide the agent with:
- Task ID: ${taskId}
- Task Description: ${task.description}
- Test Command: ${workerOutput.testCommand}
- Files Changed: ${workerOutput.filesChanged}
- Tests Modified: ${workerOutput.testsModified}
- Worker Summary: ${workerOutput.summary}

Scope is checked against the **uncommitted working tree** (`git status --short`,
`git diff`) — workers do not commit, so everything the worker touched is still
unstaged. There is no base ref to supply.

The agent will run tests, check scope adherence in both directions (nothing added
beyond the task, nothing the task asked for left out), and return a structured
markdown report with Status: PASS or FAIL.
```

## Escalation worker prompt

Step 6 — spawn **once**, only after a verified failure, and only at one tier above the tier
that failed.

```
Use the task-worker agent to fix a verified failure.

Model: ${escalationTier}   # one rung above the tier that failed — see SKILL.md Step 5
Effort: ${escalationTier == "fable" ? "high" : "<tier default>"}

Provide:
- Task ID: ${taskId}
- Original Task: ${task.description}
- Verification Report: ${verificationReport}
- What the previous worker produced: ${workerOutput.summary}
- Instructions: Fix the specific issues the report identifies. Do not re-do the parts
  that passed. Same constraints as the original worker — no scope additions, TDD cycle,
  flip the checkbox as your final act, do not commit.
```
