# Phase completion report

Step 8 — emitted once. **Attended:** after the human confirms manual verification. **Under
`--auto`:** immediately, with two additions that are part of the report and not optional extras.

1. **Say the phase closed unattended**, naming the manual steps nobody performed — from
   `design.md` on a phased plan, and from the outstanding tasks' own acceptance criteria on a
   remediation plan, which has no `design.md` (`SKILL.md:196-199`).
2. **On the final phase, say the plan cannot close itself** — every task `[x]` leaves `tasks.md`
   wanting `complete`, which is a judgment-bearing `status:` change behind `/wb:update_status`'s
   own barrier that `--auto` does not reach.

Both are mandated in prose by `SKILL.md` Step 8. They are restated here because a coordinator
that renders this template faithfully and stops would otherwise emit neither — and silence at
the final phase is exactly the defect.

**Three substitutions branch on the kind of plan.** A remediation plan
([../../../docs/reference/remediation-plan.md](../../../docs/reference/remediation-plan.md)) has no numbered phase — `SKILL.md` Step 2 — so
there is no `${phase}` to name and nothing after it to proceed to.

| Placeholder | Phased plan | Remediation plan |
| ----------- | ----------- | ---------------- |
| `${phaseLabel}` | `Phase ${phase}` | `Round N`, taken from the round's directory name |
| `Next phase:` line | the next phase's task count | omit the line — the round is the whole plan |
| closing line | `Ready to proceed to Phase ${phase + 1}.` | name what actually comes next: the review's next round if one is planned, otherwise the plan's owner |

On the **final** phase of a phased plan the closing line is wrong for the same reason: there is
no phase after it. Say the plan is out of phases and awaits `/wb:update_status`. A report that
points at a phase nobody wrote sends the next session looking for it.

```
✅ ${phaseLabel} Complete (Coordinated Execution)

**Execution Statistics:**
- Worker agents spawned: ${workerCount}
- Total tasks completed: ${completedCount}
- Escalations: ${escalationCount}
- Execution mode: sequential

**Progress Summary:**
- ${phaseLabel}: ${taskCount} tasks, every checkbox [x]
- Next phase: ${nextPhaseTaskCount} tasks
- Files modified: ${codeFileCount} code files, ${testFileCount} test files
- Counters reconciled by /wb:update_status

**Context Efficiency:**
- Main agent context: Constant (no accumulation)
- Worker contexts: Ephemeral (discarded after each task)
- No compaction needed during phase implementation

${closingLine}
```
