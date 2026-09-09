# Frontmatter fragments

Step 5 — apply after confirmation.

## research.md

```yaml
status: [new-status]
last_updated: [YYYY-MM-DD]
git_commit: [current-commit]
git_branch: [current-branch]
```

## design.md

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

## tasks.md

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
