# Phase completion report

Step 6 — emitted once, after the human confirms manual verification.

**Three substitutions branch on the kind of plan.** A remediation plan ([../../../docs/reference/remediation-plan.md](../../../docs/reference/remediation-plan.md))
has no numbered phase — SKILL.md Step 2 — so there is no `[N]` to name and nothing after it to proceed to.

| Placeholder | Phased plan | Remediation plan |
| ----------- | ----------- | ---------------- |
| `Phase [N]` | the phase number | `Round N`, taken from the round's directory name |
| `Next phase:` line | the next phase's task count | omit the line — the round is the whole plan |
| closing line | `Ready to proceed to Phase [N+1].` | name what actually comes next: the review's next round if one is planned, otherwise the plan's owner |

On the **final** phase of a phased plan the closing line is wrong for the same reason: there is no
phase after it. Say the plan is out of phases and awaits `/wb:update_status`, rather than pointing
the next session at a phase nobody wrote.

```
✅ Phase [N] Complete

**Progress Summary:**
- Phase [N]: [X] tasks completed, every checkbox [x]
- Next phase: [Y] tasks
- Files modified: [count] code files, [count] test files
- Counters reconciled by /wb:update_status

Ready to proceed to Phase [N+1].
```
