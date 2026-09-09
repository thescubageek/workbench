# Incomplete worker message

Step 6 — only after the working-tree inspection shows this is a **genuine failure with no
usable work**, not a truncation. Truncation is finished or re-delegated without asking; see
SKILL.md Step 6.

```
⚠️ Worker Did Not Complete Task

Task ${taskId}: checkbox still [ ], and the working tree shows ${treeState}.
Worker reported: ${workerError}

Diagnosis: ${diagnosis}

**Options**:
1. Re-delegate the remaining slice with the failure report as context
2. Escalate one tier (${escalationTier}) — one attempt
3. Mark blocked and carry to the phase checkpoint
4. Manual intervention

How should I proceed?
```
