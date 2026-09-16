# Phase completion report

Step 8 — emitted once. **Attended:** after the human confirms manual verification. **Under
`--auto`:** immediately, with two additions that are part of the report and not optional extras.

1. **Say the phase closed unattended**, naming the manual steps from `design.md` that nobody
   performed.
2. **On the final phase, say the plan cannot close itself** — every task `[x]` leaves `tasks.md`
   wanting `complete`, which is a judgment-bearing `status:` change behind `/wb:update_status`'s
   own barrier that `--auto` does not reach.

Both are mandated in prose by `SKILL.md` Step 8. They are restated here because a coordinator
that renders this template faithfully and stops would otherwise emit neither — and silence at
the final phase is exactly the defect.

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
