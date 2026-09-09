---
name: validate_project
description: Validate project documentation follows wb workflow correctly
argument-hint: "[project-directory]"
allowed-tools: Read
---

# Validate Project

Validates that a project's documentation structure follows the wb workflow correctly. Identifies gaps, disconnects, and inconsistencies across the plan documents.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- [reference.md](reference.md) — the eight-category **Validation Checklist**, the per-check **Validation Rules**, the DO/DON'T lists, and configuration
- [templates.md](templates.md) — the validation report and the canonical error-message formats

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

```javascript
const projectDir = $1 || /* prompt for it */;

const files = {
  research: `${projectDir}/research.md`,
  design: `${projectDir}/design.md`,
  tasks: `${projectDir}/tasks.md`,
  journal: `${projectDir}/journal.md`,  // optional
  handoff: `${projectDir}/handoff.md`   // optional
};
```

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
grep -c '^- \[x\]' ${projectDir}/tasks.md    # tasks done
grep -c '^- \[ \]' ${projectDir}/tasks.md    # tasks remaining
grep -cE '^- \[[ x]\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' ${projectDir}/tasks.md   # tasks carrying a local ID
```

Note where a plan's own success criteria and prerequisites are also checkboxes: a raw
`grep -c '^- \[x\]'` counts those too, so scope the count to task lines when comparing against
`total_tasks`. Getting this wrong makes every counter look drifted.

Hold these numbers; the checklist compares the frontmatter counters against them.

### Step 3: Run Validation Checks

Read [reference.md](reference.md) NOW — the `## Validation Checklist` section for what to check, and `## Validation Rules` for how each check is evaluated.

Track:

- ✅ **Pass**: Check succeeded
- ⚠️ **Warning**: Non-critical issue, should fix
- ❌ **Error**: Critical issue, must fix

Organize findings by category:

1. Critical Errors (must fix)
2. Warnings (should fix)
3. Passed Checks (all good)

For each finding, use the shapes in the `## Error message formats` section of [templates.md](templates.md), so findings stay consistent and greppable.

### Step 4: Report Findings

Read the `## Validation report` section of [templates.md](templates.md) NOW and present the report in that shape.

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

See [reference.md](reference.md) — the DO/DON'T lists and configuration.
