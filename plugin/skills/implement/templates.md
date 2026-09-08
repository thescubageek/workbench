# implement — templates

Read the **section you need**, when its step directs you to.

Sections: `Modified Files fragment` (Step 7) · `Manual verification request` (Step 8) ·
`Phase completion report` (Step 8) · `Incomplete worker message` (Step 6)

## Modified Files fragment

Step 7 — aggregate every worker's output into this section of `tasks.md`.

````markdown
### 📝 Modified Files (Phase ${phase})

#### Code Files
${aggregatedCodeFiles.map(f => `- \`${f.path}\` - ${f.description}`).join('\n')}

#### Test Files
${aggregatedTestFiles.map(f => `- \`${f.path}\` - ${f.description}`).join('\n')}

**Quick test commands:**

```bash
# Run all tests for this phase
${generatePhaseTestCommand(aggregatedTestFiles)}
```
````

## Manual verification request

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

## Phase completion report

Step 8 — emitted once, after the human confirms manual verification.

```
✅ Phase ${phase} Complete (Coordinated Execution)

**Execution Statistics:**
- Worker agents spawned: ${workerCount}
- Total tasks completed: ${completedCount}
- Escalations: ${escalationCount}
- Execution mode: sequential

**Progress Summary:**
- Phase ${phase}: ${taskCount} tasks, every checkbox [x]
- Next phase: ${nextPhaseTaskCount} tasks
- Files modified: ${codeFileCount} code files, ${testFileCount} test files
- Counters reconciled by /wb:update_status

**Context Efficiency:**
- Main agent context: Constant (no accumulation)
- Worker contexts: Ephemeral (discarded after each task)
- No compaction needed during phase implementation

Ready to proceed to Phase ${phase + 1}.
```

## Incomplete worker message

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
