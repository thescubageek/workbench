# Frontmatter fragments

Step 5 — apply after confirmation.

**Which fragments apply branches on the kind of plan.** A remediation plan
([../../../docs/reference/remediation-plan.md](../../../docs/reference/remediation-plan.md)) has only `tasks.md`, and its single `## Tasks`
section carries no phase number — `SKILL.md` Step 1. Applying every fragment to a round means
writing frontmatter into two files that do not exist.

| Fragment | Phased plan | Remediation plan |
| -------- | ----------- | ---------------- |
| the `research.md` and `design.md` fragments below | apply both | skip both — a round has neither document, and Step 1 says to leave them out rather than record them as "n/a" |
| `current_phase` in the `tasks.md` fragment | write the counted phase number | omit the key — do not invent a phase number for a plan that has none |

## research.md — phased plans only

```yaml
status: [new-status]
last_updated: [YYYY-MM-DD]
git_commit: [current-commit]
git_branch: [current-branch]
```

## design.md — phased plans only

```yaml
status: [new-status]
last_updated: [YYYY-MM-DD]
git_commit: [current-commit]
git_branch: [current-branch]
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

When `tasks.md` first moves to `in-progress`, add implementation notes:

```markdown
## Implementation Notes

Started: [YYYY-MM-DD]
- Implementation began on phase [N]
- [Any relevant context about starting implementation]
```

Then update the Progress Overview table to match those counts, and add a note if the status
changed:

```markdown
### Implementation Notes
- Status updated to [new-status] on [YYYY-MM-DD]
- [Reason for status change]
```
