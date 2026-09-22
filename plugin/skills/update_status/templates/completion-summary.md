# Completion summary

Step 7 — emitted once, after the updates land.

**Two substitutions branch on the kind of plan.** A remediation plan
([../../../docs/reference/remediation-plan.md](../../../docs/reference/remediation-plan.md)) has only `tasks.md`, and its single `## Tasks`
section carries no phase number — `SKILL.md` Step 1. A summary that hard-codes the upstream
documents reports updates to two files nobody touched, because they do not exist.

| Substitution | Phased plan | Remediation plan |
| ------------ | ----------- | ---------------- |
| `[upstream-document-updates]` | one `[old] → [new]` line per upstream document — `research.md` first, then `design.md` | omit both lines; a round has neither document, and Step 1 says to leave the rows out rather than write "n/a" |
| the `- Phase: [number]` line | keep as written | drop it — a round has one unnumbered phase |

```
✅ Status updated successfully!

📁 Project: [project-name]
📊 Updates Applied:

[upstream-document-updates]
**tasks.md**: [old] → [new]
  - Phase: [number]
  - Progress: [X]/[Y] tasks ([percentage]%), counted from checkboxes
  - Counters reconciled: [none needed | completed_tasks [old] → [new]]

**Metadata Updated**:
- Last updated: [YYYY-MM-DD]
- Git commit: [commit-hash]
- Git branch: [branch-name]

**Next Steps**:
[Contextual suggestions based on new status]
```
