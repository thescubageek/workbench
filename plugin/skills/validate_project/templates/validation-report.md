# Validation report

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
**Files**: design.md (status: approved), research.md (status: draft)
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
