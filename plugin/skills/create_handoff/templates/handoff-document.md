# Handoff document

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 4. Write the handoff in this shape. Omit a section that has no real content. Never fill a
section with placeholders.

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
**Overall Progress**: [from the checkboxes in tasks.md, for example 30/64 tasks. Count only task lines with an ID, not every checkbox]

## Quick Start

On the same machine, use `claude --resume` instead. It restores the full earlier session, with the tool results, more reliably than a document can. This handoff is for a transfer to **another machine, another agent, or a teammate**. To resume from it, run `/wb:resume_handoff [this file path]`.

## Current State Summary

**What the project builds**: [Brief description from design.md]

**Where the work is**: [The current status, for example "Implementing Phase 2, task 3 of 5"]

**Last completed action**: [What was just finished]

**Next immediate task**: [What to do next]

## Work Completed This Session

### Code Changes
[One entry for each change, from `git diff` or `git status`: `<file:line>`, then what changed. Omit the section if there is none.]

### Tasks Completed
[The task IDs changed to [x] in this session, each with its title. Omit the section if there is none.]

### Verification Run
[Only the commands that ran in this session, with their real output. Omit a command that did not run. Do not assume a pass or a fail.]

### Plan State

```
Phase [N] of [M] — [X]/[Y] tasks [x]
Next unchecked task: [ID] — [title]
Blocked (from tasks.md Current Blockers): [ID and one line, or "none"]
Journal: [the most recent entry, and whether it is OPEN or CLOSED]
```

## Critical Learnings

### Discoveries Not in Documentation

[Findings that are not obvious and that the next session needs: patterns, hidden dependencies, traps, and required workarounds. Give each one a real `file:line`. Omit the section if there is none. Put durable facts about the codebase in CLAUDE.md, not in a handoff that is read once.]

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
   - **Trade-off**: [What the choice gave up]
   - **Impact**: [Consequences]

## Current Blockers

### Active Blockers

1. **Blocker**: [Description]
   - **Impact**: Cannot proceed with [task]
   - **Attempted Solutions**:
     - Tried [approach 1] - failed because [reason]
     - Tried [approach 2] - it partly worked, but [issue]
   - **Potential Solutions**:
     - Try [approach 3]
     - If that fails, [alternative]
   - **Files Involved**: `file1.ts`, `file2.ts`

### Resolved Blockers (For Reference)

1. **Was Blocked**: [Previous blocker]
   - **Resolution**: [How it was solved]
   - **Key Insight**: [What unlocked it]

## Implementation Notes

### Deviations from Plan

1. **Deviation**: [What is different from tasks.md]
   - **Location**: Phase [N], Task [M]
   - **Original Plan**: [What tasks.md said]
   - **Actual Implementation**: [What was done]
   - **Reason**: [Why the change]
   - **Impact**: [None/Minor/Needs Plan Update]

### Edge Cases Discovered

1. **Edge Case**: [Description]
   - **Scenario**: [When it occurs]
   - **Handling**: [How the code handles it]
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
[What the changes do, and why they are not committed]
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

3. **Continue phase**: Complete the remaining [N] tasks in Phase [M]

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

_Include this section if a mockups/ directory exists._

- **Current version**: v00[N]
- **Mockup log**: `mockups/mockup-log.md`
- **Pending feedback** (not yet versioned):
  - [feedback 1]
  - [feedback 2]
- **Open UI questions** (from the records in the mockup log):
  - `UIQ[n]`: [question]

## Artifacts and References

### Project Documents
- Research: `[path]/research.md` - Original analysis
- Design: `[path]/design.md` - Architecture decisions
- Tasks: `[path]/tasks.md` - Execution plan (currently on Phase [N])
- This Handoff: `[path]/handoff-YYYY-MM-DD-HH-MM.md`

### Key Code Locations
[Real paths that the current work depends on. Put stable paths for the whole project in CLAUDE.md, not in each handoff.]

### External References
- [Any documentation consulted]
- [Stack Overflow solutions found]
- [Design patterns referenced]

## Session Metadata

[Only what a tool can measure. Omit the rest. Take the lines changed from `git diff --stat`. Take the tasks completed from the checkboxes changed in this session. Do NOT estimate the session duration, or any count that a command cannot give.]

## Handoff Verification

Before you use this handoff, check these items:
- [ ] The project directory exists at the path above
- [ ] The git repository is at the commit above
- [ ] The tests pass, as the handoff says
- [ ] If the branch changed, it has no merge conflicts

---

**Handoff complete.** To resume, run `/wb:resume_handoff [path]`.
````
