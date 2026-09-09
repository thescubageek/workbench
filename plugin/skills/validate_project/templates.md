# validate_project — templates

Read the **section you need**, when its step directs you to.

Sections: `Validation report` (Step 4) · `Error message formats` (Step 3)

## Validation report

Step 4 — the report this skill emits.

````markdown
# Project Validation Report

**Project**: [project-name]
**Location**: [project-dir]
**Validated**: [YYYY-MM-DD HH:MM]

## Summary

- ✅ [X] checks passed
- ⚠️ [Y] warnings found
- ❌ [Z] critical errors found

**Overall Status**: [PASS / PASS WITH WARNINGS / FAIL]

---

## Critical Errors ❌

These MUST be fixed for the project to follow wb workflow correctly:

### 1. Status Contradicts Its Own Checkboxes
**File**: tasks.md
**Issue**: status is `complete` but 4 tasks are still `[ ]`
**Impact**: the plan claims done work that its own record says is outstanding
**Fix**: finish the tasks, or correct the status

### 2. Status Inconsistency
**Files**: design.md (status: ready), research.md (status: draft)
**Issue**: Design cannot be ready if research is still draft
**Impact**: Violates workflow progression rules
**Fix**: Complete research first OR set design back to draft

[... more critical errors ...]

---

## Warnings ⚠️

These should be fixed but don't block workflow:

### 1. Counter Drift
**File**: tasks.md frontmatter
**Issue**: `completed_tasks: 13` but 18 tasks are `[x]`
**Impact**: none to correctness — the checkboxes are authoritative — but the summary understates progress
**Fix**: Run `/wb:update_status`

### 2. Placeholder Content
**File**: design.md, line 45
**Issue**: Contains "[To be added]" placeholder text
**Impact**: Incomplete design documentation
**Fix**: Document the design decision or remove the section

[... more warnings ...]

---

## Passed Checks ✅

These aspects are correctly configured:

- ✅ All required files exist
- ✅ Frontmatter is valid YAML
- ✅ Required frontmatter fields present
- ✅ Every task is a checkbox with a unique local ID
- ✅ Status progression is logical
- ✅ Planning records carry IDs and states
- ✅ Dependencies are documented
- ✅ Project names are consistent

---

## Recommendations

Based on the validation results:

1. **Immediate Actions** (critical errors):
   - [Specific action 1]
   - [Specific action 2]

2. **Soon** (warnings):
   - [Specific action 1]
   - [Specific action 2]

3. **Optional Improvements**:
   - Add `ticket` field to frontmatter for issue tracking
   - Add `repository` field for GitHub integration
   - Run `/wb:update_status` to sync all metadata

---

## Validation Details

**Files Checked**:
- research.md: [status] (last_updated: [date])
- design.md: [status] (last_updated: [date])
- tasks.md: [status] (last_updated: [date])

**Task State**:
- Tasks: [X] of [Y] `[x]` ([percentage]%)
- Frontmatter counters: [agree / drifted by N]
- Current phase: [N]

**Planning Records**:
- Open questions: [count] open, [count] resolved
- Assumptions: [count] pending, [count] validated
- Pending decisions: [count] open, [count] resolved

**Next Command Suggestions**:
- If critical errors: Fix them manually or re-run workflow commands
- If warnings only: Run `/wb:update_status` to sync metadata
- If all passed: Run `/wb:implement` to continue work
````

## Error message formats

Step 3 — use these shapes so findings are consistent and greppable.

### Critical errors

```
❌ Missing Required File: tasks.md
   Location: [project-dir]/tasks.md
   Cause: File does not exist
   Impact: Cannot track implementation work
   Fix: Run /wb:create_tasks to generate tasks.md
```

```
❌ Duplicate Task IDs: P2-T7
   Location: tasks.md, lines 214 and 288
   Cause: two tasks share one local ID
   Impact: an ID is the handle a commit, journal entry or handoff cites — a duplicate makes those citations ambiguous
   Fix: renumber the later task; never renumber one that has already been cited
```

```
❌ Stale Tracking Guidance
   File: tasks.md, line 343
   Text: "these checkboxes are documentation only"
   Cause: plan predates 2.0.0, when status moved into these checkboxes
   Impact: a reader following it will not record status anywhere
   Fix: delete the note; the checkboxes are the record
```

```
❌ Status Progression Violation
   Files: design.md (implementing), research.md (draft)
   Cause: Design implementing but research not complete
   Impact: Violates workflow: research must complete before design
   Fix: Complete research OR set design back to draft
```

### Warnings

```
⚠️ Missing Git Metadata
   File: research.md
   Fields: git_commit, git_branch
   Impact: Cannot track code state when research was done
   Fix: Run /wb:update_status to populate metadata
```

```
⚠️ Placeholder Content Found
   File: design.md, line 45
   Text: "[To be added]"
   Impact: Incomplete documentation
   Fix: Document the design decision or remove placeholder
```

```
⚠️ Counter Drift
   File: tasks.md frontmatter
   Cause: completed_tasks: 13, but 18 task lines are [x]
   Impact: none to correctness — the checkboxes are authoritative
   Fix: Run /wb:update_status; it is the only writer of these fields
```

```
⚠️ Resolved Record Without a Pointer
   File: research.md, Open Questions row Q3
   Cause: state is "Resolved 2026-09-08" but names no destination
   Impact: the decision cannot be found from the question it answered
   Fix: point the row at where the decision was recorded (design.md → Technical Decisions)
```
