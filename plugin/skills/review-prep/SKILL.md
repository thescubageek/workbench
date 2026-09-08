---
name: review-prep
description: Interactive code review walkthrough using tmux and nvim for pair programming style review. Use when user says "review", "walk through changes", "explain this diff", "prep for PR", or wants to understand what changed.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Code Review Prep

Interactive walkthrough of changes as pair programming. Opens files in nvim pane, waits for questions.

## Supporting Script

This skill includes `nvim-helper.sh` for tmux/nvim operations. Add to your permissions to avoid repeated approvals:

```json
{
  "permissions": {
    "allow": [
      "Bash(${CLAUDE_PLUGIN_ROOT}/skills/review-prep/nvim-helper.sh:*)"
    ]
  }
}
```

## Setup

1. Initialize nvim pane:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/review-prep/nvim-helper.sh setup
# Returns: NVIM_PANE=%123
```

1. Get the diff:

```bash
# Default: last commit
git show HEAD --stat

# Or specific range
git diff main..HEAD --stat
```

1. Parse changes into logical groups:
   - Group related hunks that solve same problem
   - Keep test files paired with their implementation

## Start Review

State the problem(s) being solved (1-2 max).

```
This diff addresses:
1. [Problem A] - files: x.ts, y.ts, x.test.ts
2. [Problem B] - files: z.ts

Total: N files, M logical changes
```

If more than 2-3 problems: flag as code smell, suggest splitting.

## For Each Change

1. Open file at line:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/review-prep/nvim-helper.sh open src/auth.ts 42
```

1. Focus nvim for user inspection:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/review-prep/nvim-helper.sh focus
```

1. Give ONE line context: "Change X/N - [Problem]. [brief description]"
2. Wait for questions

## TDD Check

For each production code change, verify:

- [ ] Corresponding test file changed?
- [ ] New code has test coverage?

Flag violations:

```
⚠ TDD: src/auth.ts changed but src/auth.test.ts unchanged
```

Don't block - just note. User decides if intentional.

## Navigation

| Command | Action |
| --------- | -------- |
| `next` | Next logical change |
| `back` | Previous change |
| `skip to [file]` | Jump to specific file |
| `show test` | Open corresponding test file |
| `done` | Wrap up review |

## Conversation Style

- Short responses - one or two lines max
- Wait for questions, don't front-load explanation
- Answer directly, then offer: "want to see the test?"
- Bounce up/down abstraction layers on request

## Wrap-up

When user says "done":

```
## Review Summary

**Changes reviewed**: X/Y
**Problems addressed**: [list]

**TDD Status**:
- ✓ Changes with tests: N
- ⚠ Changes without tests: M [list files if any]

**Notes**: [any flags raised during review]

Ready for PR? [yes/concerns]
```

## Script Reference

```bash
# Check if nvim pane exists
${CLAUDE_PLUGIN_ROOT}/skills/review-prep/nvim-helper.sh status

# Setup (find or create nvim pane)
${CLAUDE_PLUGIN_ROOT}/skills/review-prep/nvim-helper.sh setup

# Open file at specific line
${CLAUDE_PLUGIN_ROOT}/skills/review-prep/nvim-helper.sh open FILE LINE

# Focus nvim pane
${CLAUDE_PLUGIN_ROOT}/skills/review-prep/nvim-helper.sh focus
```

## Code Smell Flags

| Smell | Response |
| ------- | ---------- |
| >2-3 problems per diff | "Consider splitting this PR" |
| Change doesn't map to stated problem | "This seems unrelated - intentional?" |
| Pattern repeated 3+ times | "Extract helper? (your call)" |
| Large file change, no tests | "Missing test coverage?" |
| Commented-out code added | "Dead code - remove?" |
