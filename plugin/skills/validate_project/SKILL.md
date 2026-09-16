---
name: validate_project
description: Validate project documentation follows wb workflow correctly
argument-hint: "[project-directory]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Validate Project

Validates that a project's documentation structure follows the wb workflow correctly. Identifies gaps, disconnects, and inconsistencies across the plan documents.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- `reference/` — [validation-checklist.md](reference/validation-checklist.md) and [validation-rules.md](reference/validation-rules.md) (Step 3) · [important-guidelines.md](reference/important-guidelines.md) · [configuration.md](reference/configuration.md)
- `templates/` — [error-message-formats.md](templates/error-message-formats.md) (Step 3) · [validation-report.md](templates/validation-report.md) (Step 4)

**If a directed read fails, stop — do not continue from memory.** These files live outside your
project, so a read can be refused. Say which file was refused, that reads outside the working
directory are gated, and that the fix is to allow the read once or to relaunch with
`--add-dir <plugin-path>`. Do not route around a refusal with `cat`.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:validate_project docs/plans/2025-01-08-my-project/`):
   - Use `$1` as the project directory
   - Begin validation immediately

2. **If no arguments**:

   ```
   I'll validate your project documentation. Please provide:
   1. Path to the project documentation directory (e.g., docs/plans/2025-01-08-my-project/)

   I'll check for:
   - File structure completeness
   - Frontmatter validity
   - Task-tracking integrity
   - Status consistency
   - Content gaps and placeholders
   ```

## What this skill is checking against

There is no external tracker to cross-check the plan against. `tasks.md` **is** the record —
checkbox state is the truth, the frontmatter counters are a derived cache with one writer
(`/wb:update_status`), and git is the durable trail.

That changes the shape of validation rather than removing it. Instead of asking "do two systems
agree?", ask **"can this document actually carry the role it claims?"** — are the tasks
checkboxes rather than prose, do they have stable unique IDs, does the declared status
contradict the boxes, and is there stale guidance telling a reader that status lives somewhere
else. Counter drift is a **warning**, never an error: it is expected between checkpoints, and
the counts win.

## Validation Process

### Step 1: Read All Documentation

**⛔ BARRIER 1: Read ALL files FULLY - no shortcuts**

Take the project directory from the arguments, prompting for it if it is missing. Then read
every document it holds — **fully**, no `limit` or `offset`: `research.md`, `design.md` and
`tasks.md` are required; `journal.md` and any `handoff*.md` are optional and validated only when
present.

1. **Check directory exists**:

   ```bash
   ls ${projectDir}
   ```

2. **Read all required files**:
   - Read research.md FULLY
   - Read design.md FULLY
   - Read tasks.md FULLY
   - Read journal.md and handoff.md if they exist

3. **Parse frontmatter** from each file

**Establish what the documents claim, before checking whether it holds**

### Step 2: Count the Task Surface

Before running the checklist, get the facts that most other checks depend on:

```bash
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' ${projectDir}/tasks.md   # tasks done
grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' ${projectDir}/tasks.md   # tasks remaining
grep -c  '^- \[[ x]\]' ${projectDir}/tasks.md                                  # ALL checkboxes
```

The first two are the counts every other check compares against, and they are scoped to lines
carrying a local ID. The third is deliberately unscoped: a plan's own success criteria and
prerequisites are checkboxes too, so **the gap between the third number and the first two is
expected**, and is not drift. Comparing a raw `grep -c '^- \[x\]'` against `total_tasks` is the
mistake that makes every counter look drifted — flag it if you find it written into a plan.

Hold these numbers; the checklist compares the frontmatter counters against them.

### Step 3: Run Validation Checks

Read [reference/validation-checklist.md](reference/validation-checklist.md) NOW for what to check, and [reference/validation-rules.md](reference/validation-rules.md) for how each check is evaluated.

Track:

- ✅ **Pass**: Check succeeded
- ⚠️ **Warning**: Non-critical issue, should fix
- ❌ **Error**: Critical issue, must fix

Organize findings by category:

1. Critical Errors (must fix)
2. Warnings (should fix)
3. Passed Checks (all good)

For each finding, use the shapes in the [templates/error-message-formats.md](templates/error-message-formats.md), so findings stay consistent and greppable.

### Step 4: Report Findings

Read [templates/validation-report.md](templates/validation-report.md) NOW and present the report in that shape.

### Step 5: Offer Fixes

After presenting the report, offer to help fix issues:

```
Would you like me to:
1. Fix critical errors automatically (where possible)
2. Generate a plan to address all issues
3. Re-run validation after you make changes
4. Continue to next step in workflow
```

**One exception to "fix where possible"**: never rewrite the frontmatter counters here.
`/wb:update_status` is their only writer — that single-writer rule is what keeps them
consistent, and a second writer reintroduces exactly the drift this check reports.

## Important Guidelines

See [reference/important-guidelines.md](reference/important-guidelines.md) for the DO/DON'T lists and [reference/configuration.md](reference/configuration.md).
