# update_status — templates

Read the **section you need**, when its step directs you to.

Sections: `Status update plan` (Step 4) · `Frontmatter fragments` (Step 5) ·
`Completion summary` (Step 7)

## Status update plan

Step 4 — present this and **wait** for confirmation before writing anything.

```
📊 Current Status Analysis:

**research.md**
- Current: [current-status]
- Proposed: [new-status]
- Reason: [why this transition is appropriate]

**design.md**
- Current: [current-status]
- Proposed: [new-status]
- Reason: [why this transition is appropriate]

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

## Frontmatter fragments

Step 5 — apply after confirmation.

### research.md

```yaml
status: [new-status]
last_updated: [YYYY-MM-DD]
git_commit: [current-commit]
git_branch: [current-branch]
```

### design.md

```yaml
status: [new-status]
last_updated: [YYYY-MM-DD]
git_commit: [current-commit]
git_branch: [current-branch]
```

If transitioning to `implementing`, add implementation notes:

```markdown
## Implementation Notes

Started: [YYYY-MM-DD]
- Implementation began on phase [N]
- [Any relevant context about starting implementation]
```

### tasks.md

```yaml
status: [new-status]
last_updated: [YYYY-MM-DD]
current_phase: [calculated-phase-number]
total_tasks: [counted from task checkboxes]
completed_tasks: [counted from task checkboxes]
git_commit: [current-commit]
git_branch: [current-branch]
```

Then update the Progress Overview table to match those counts, and add a note if the status
changed:

```markdown
### Implementation Notes
- Status updated to [new-status] on [YYYY-MM-DD]
- [Reason for status change]
```

## Completion summary

Step 7 — emitted once, after the updates land.

```
✅ Status updated successfully!

📁 Project: [project-name]
📊 Updates Applied:

**research.md**: [old] → [new]
**design.md**: [old] → [new]
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
