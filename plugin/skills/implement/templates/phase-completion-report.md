# Phase completion report

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
