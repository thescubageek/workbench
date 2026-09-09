# Manual verification request

Step 8 — emitted at the phase checkpoint, then **stop and wait**.

```
✅ Phase ${phase} Automated Verification Complete

**Automated checks passed:**
- ✅ All tests passing: [test command]
- ✅ Linting clean: [lint command]
- ✅ Build successful: [build command]

**Worker agents completed:**
${workerSummaries.map(w => `- ✅ ${w.title}: ${w.summary}`).join('\n')}

**Phase ${phase} task state:**
- ✅ Every Phase ${phase} checkbox is [x] (${taskCount} of ${taskCount})
- ✅ Each task committed separately

**Blocking issues carried to this checkpoint:**
${blockingIssues.length ? blockingIssues.map(b => `- ⚠️ ${b.taskId}: ${b.summary}`).join('\n') : '- none'}

**Manual verification required:**

Please perform the following manual checks from design.md:

${manualVerificationSteps}

Reply when manual verification is complete.
```
