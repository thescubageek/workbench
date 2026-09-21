# Status update plan

Step 4 — present this and **wait** for confirmation before writing anything.

**Two substitutions branch on the kind of plan.** A remediation plan
(`docs/plans/<plan>/reviews/<date>-round-N/`) has only `tasks.md`, and its single `## Tasks`
section carries no phase number — `SKILL.md` Step 1. A template that hard-codes the upstream
documents therefore asks the user to confirm a status transition for two files that do not
exist, under a phase the round never had.

| Substitution | Phased plan | Remediation plan |
| ------------ | ----------- | ---------------- |
| `[upstream-document-blocks]` | one block per upstream document — `research.md` first, then `design.md` — each with its Current, Proposed and Reason lines | omit both blocks; a round has neither document, and Step 1 says to leave the rows out rather than write "n/a" |
| the `Current Phase` and `Proposed Phase` lines | keep as written | drop both lines — do not invent a phase number for a plan that has none |

```
📊 Current Status Analysis:

[upstream-document-blocks]

**tasks.md**
- Current: [current-status]
- Current Phase: [phase-number]
- Counters say: [X]/[Y] tasks
- Checkboxes say: [A]/[B] tasks ([percentage]%)
- Proposed: [new-status]
- Proposed Phase: [phase-number] (holds the first unchecked task)
- Reason: [why this transition is appropriate]

**Counter reconciliation**:
- completed_tasks: [old] → [new]
- total_tasks: [old] → [new]
- Drift found: [none | N tasks, expected between checkpoints]

**Git Metadata Update**:
- New git_commit: [current commit hash]
- New git_branch: [current branch]

Do you want to proceed with these updates? (yes/no)
```
