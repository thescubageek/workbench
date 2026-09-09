# Handoff document

Step 4 — write the handoff in this shape. Omit any section with nothing real to put in it;
never fill one with placeholders.

````markdown
---
created: [YYYY-MM-DDTHH:MM:SS+TZ]
type: handoff
project: [project-name]
phase: [current phase number]
handoff_reason: [reason]
last_task: [description of last task worked on]
git_commit: [current HEAD commit]
git_branch: [current branch]
repository: [repository name]
---

# Handoff: [Project Name] - [Brief Status]

**Created**: [YYYY-MM-DD HH:MM TZ]
**Reason**: [handoff reason]
**Current Phase**: Phase [N] of [Total]
**Overall Progress**: [from tasks.md's checkboxes — e.g. 30/64 tasks; count ID-scoped task lines, not every checkbox]

## Quick Start

Same machine? Prefer native `claude --resume` — it restores the full prior session (including tool results) more reliably than any doc. This handoff exists for **cross-machine / cross-agent / teammate** transfer: resume with `/wb:resume_handoff [this file path]`.

## Current State Summary

**What we're building**: [Brief description from design.md]

**Where we are**: [Current status - e.g., "Implementing Phase 2, task 3 of 5"]

**Last completed action**: [What was just finished]

**Next immediate task**: [What to do next]

## Work Completed This Session

### Code Changes
[Each entry derived from `git diff` / `git status` — `<file:line>` — what changed. Omit if none.]

### Tasks Completed
[Task IDs flipped to [x] this session, with titles. Omit if none.]

### Verification Run
[Only commands actually run this session, with their real output. Omit anything you did not run — do not assume pass/fail.]

### Plan State

```
Phase [N] of [M] — [X]/[Y] tasks [x]
Next unchecked task: [ID] — [title]
Blocked (from tasks.md Current Blockers): [ID + one line, or "none"]
Journal: [most recent entry, and whether it is OPEN or CLOSED]
```

## Critical Learnings

### Discoveries Not in Documentation

[Non-obvious findings worth carrying forward — patterns, hidden dependencies, gotchas, required workarounds — each with a real `file:line`. Omit if none. Durable codebase facts belong in CLAUDE.md, not a one-shot handoff.]

### Problems Solved

**Problem 1**: [Description]
- **Symptom**: [What went wrong]
- **Root Cause**: [Why it happened]
- **Solution**: [How it was fixed]
- **Location**: `file:line`

**Problem 2**: [Description]
[Similar structure...]

### Decisions Made

1. **Decision**: Chose [approach A] over [approach B]
   - **Why**: [Reasoning]
   - **Trade-off**: [What we gave up]
   - **Impact**: [Consequences]

## Current Blockers

### Active Blockers

1. **Blocker**: [Description]
   - **Impact**: Cannot proceed with [task]
   - **Attempted Solutions**:
     - Tried [approach 1] - failed because [reason]
     - Tried [approach 2] - partial success but [issue]
   - **Potential Solutions**:
     - Could try [approach 3]
     - Might need to [alternative]
   - **Files Involved**: `file1.ts`, `file2.ts`

### Resolved Blockers (For Reference)

1. **Was Blocked**: [Previous blocker]
   - **Resolution**: [How it was solved]
   - **Key Insight**: [What unlocked it]

## Implementation Notes

### Deviations from Plan

1. **Deviation**: [What's different from tasks.md]
   - **Location**: Phase [N], Task [M]
   - **Original Plan**: [What tasks.md said]
   - **Actual Implementation**: [What was done]
   - **Reason**: [Why the change]
   - **Impact**: [None/Minor/Needs Plan Update]

### Edge Cases Discovered

1. **Edge Case**: [Description]
   - **Scenario**: [When it occurs]
   - **Handling**: [How it's handled]
   - **Test**: [Test coverage at `file:line`]

### Technical Debt Noted

1. **Debt**: [Description]
   - **Location**: `file:line`
   - **Impact**: [Current limitation]
   - **Future Fix**: [What should be done]

## Uncommitted Changes

```bash
# Git status
[Output of git status]

# Files modified but not staged:
[List files]

# Purpose of uncommitted changes:
[Explain what the changes do and why not committed]
```

## Next Steps

### Immediate Next Tasks

1. **Complete current task**: [Specific task from tasks.md]
   - Start at: `file:line`
   - Implement: [What to add/change]
   - Verify with: [Test command]

2. **Fix blocker**: [If any]
   - Try approach: [Specific suggestion]
   - If that fails: [Alternative]

3. **Continue phase**: Complete remaining [N] tasks in Phase [M]

### Recommended Approach

```bash
# 1. Resume from handoff
/wb:resume_handoff [this file]

# 2. Check git status
git status

# 3. Run tests to verify state
npm test

# 4. Continue with next task
# [Specific guidance for next task]
```

### Watch Out For

- ⚠️ [Gotcha 1]: [What to be careful about]
- ⚠️ [Gotcha 2]: [Another thing to watch]
- ⚠️ [Gotcha 3]: [Performance/security concern]

## Mockup State (if applicable)

_Include this section if mockups/ directory exists:_

- **Current version**: v00[N]
- **Mockup log**: `mockups/mockup-log.md`
- **Pending feedback** (not yet versioned):
  - [feedback 1]
  - [feedback 2]
- **Open UI questions** (from the mockup log's records):
  - `UIQ[n]`: [question]

## Artifacts and References

### Project Documents
- Research: `[path]/research.md` - Original analysis
- Design: `[path]/design.md` - Architecture decisions
- Tasks: `[path]/tasks.md` - Execution plan (currently on Phase [N])
- This Handoff: `[path]/handoff-YYYY-MM-DD-HH-MM.md`

### Key Code Locations
[Real paths central to the in-flight work. Stable, project-wide paths belong in CLAUDE.md, not each handoff.]

### External References
- [Any documentation consulted]
- [Stack Overflow solutions found]
- [Design patterns referenced]

## Session Metadata

[Only what's measurable from tooling — omit the rest. Lines changed from `git diff --stat`; tasks completed from the checkboxes flipped this session. Do NOT estimate session duration or any count you can't derive from a command.]

## Handoff Verification

Before using this handoff, verify:
- [ ] Project directory exists at specified path
- [ ] Git repository is at mentioned commit
- [ ] Tests pass as indicated
- [ ] No merge conflicts if branch changed

---

**Handoff Complete**: Ready for resumption using `/wb:resume_handoff [path]`
````
