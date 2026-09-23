# Manual verification request

Step 8 — emitted at the phase checkpoint, then **stop and wait**.

**Attended runs only.** Under `--auto` this request is not emitted and nothing waits: the
checkpoint ticks the conditions it established, leaves "Manual verification confirmed by human"
`[ ]`, and records the phase as having closed unattended.

**Two substitutions branch on the kind of plan.** A remediation plan
([../../../docs/reference/remediation-plan.md](../../../docs/reference/remediation-plan.md)) has no numbered phase and no `design.md` —
`SKILL.md` Step 1 and Step 2 — so a template that hard-codes either waits on a checklist drawn
from a file that does not exist, under a heading reading `Phase undefined`.

| Placeholder | Phased plan | Remediation plan |
| ----------- | ----------- | ---------------- |
| `${phaseLabel}` | `Phase ${phase}` | `Round N`, taken from the round's directory name |
| `${manualVerificationSteps}` | the phase's manual checks from `design.md` | each outstanding task's own acceptance criterion, quoted from the round's `tasks.md` with the `file:line` it names — a round's manual steps live in its acceptance criteria, not in a design document (`SKILL.md:196-199`) |

**Never wait on an empty list.** If a round yields no acceptance criterion a human must run or
judge, and no attestation task (Step 8.4), write "no manual steps for this round" and skip the
wait. A confirmation of nothing is a confirmation that never arrives.

```
✅ ${phaseLabel} Automated Verification Complete

**Automated checks passed:**
- ✅ All tests passing: [test command]
- ✅ Linting clean: [lint command]
- ✅ Build successful: [build command]

**Worker agents completed:**
${workerSummaries.map(w => `- ✅ ${w.title}: ${w.summary}`).join('\n')}

**${phaseLabel} task state:**
- ✅ Every ${phaseLabel} checkbox is [x] (${taskCount} of ${taskCount})
- ✅ Each task committed separately

**Blocking issues carried to this checkpoint:**
${blockingIssues.length ? blockingIssues.map(b => `- ⚠️ ${b.taskId}: ${b.summary}`).join('\n') : '- none'}

**Manual verification required:**

Please perform the following manual checks:

${manualVerificationSteps}

Reply when manual verification is complete.
```
