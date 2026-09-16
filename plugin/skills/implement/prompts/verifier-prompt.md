# Verifier prompt

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
