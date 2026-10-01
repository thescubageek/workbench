# Incomplete worker message

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 6. Use this only when the working-tree inspection shows a **genuine failure with no
usable work**, not a truncation. A truncated task is finished or delegated again without a
question. See SKILL.md Step 6.

```
⚠️ The worker did not complete the task

Task ${taskId} (${task.title}): the checkbox is still [ ], and the working tree shows ${treeState}.
The worker reported: ${workerError}

Diagnosis: ${diagnosis}

**Options**:
1. Delegate the remaining work again, with the failure report as context
2. Escalate one tier (${escalationTier}), for one attempt
3. Mark the task blocked, and carry it to the phase checkpoint
4. Fix it by hand

Which option do you choose?
```
