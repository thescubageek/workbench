# Escalation worker prompt

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
