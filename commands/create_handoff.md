---
description: Create a handoff document to transfer work context to another session or agent
argument-hint: "[project-directory] [handoff-reason]"
---

# Create Handoff

Creates a comprehensive handoff document to transfer your work context to another agent or resume in a new session. Captures critical context, learnings, and next steps that aren't in the formal documentation.

## Purpose

Handoff documents preserve:

- Work in progress and current status
- Critical learnings and discoveries
- Context not captured in formal docs
- Exact state for seamless resumption
- Blockers and their solutions
- Next steps with specific guidance

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/create_handoff docs/plans/2025-01-08-my-project/ "switching to opus for complex logic"`):
   - Use `$1` as project directory
   - Use `$2+` as handoff reason (optional)
   - Begin handoff creation

2. **If no arguments**:

   ```
   I'll create a handoff document for your current work. Please provide:
   1. Path to the project documentation directory (e.g., docs/plans/2025-01-08-my-project/)
   2. Reason for handoff (optional, e.g., "session ending", "need different model", "blocked on approval")

   I'll document the current state for seamless continuation.
   ```

## Process Steps

### Step 1: Gather Current State

**⛔⛔⛔ BARRIER 1: STOP! Read ALL project docs AND review conversation history ⛔⛔⛔**

```javascript
const projectDir = $1 || /* prompt for it */;
const handoffReason = $2 || "session transfer";

// Read all project documentation
const researchFile = `${projectDir}/research.md`;
const designFile = `${projectDir}/design.md`;
const tasksFile = `${projectDir}/tasks.md`;
```

1. **Read all project documentation** to understand:
   - Project goals and current status
   - What's been completed
   - What's in progress

2. **Review conversation history** to capture:
   - Recent changes made
   - Problems encountered and solutions
   - Decisions made during implementation
   - Any deviations from plan

3. **Check beads state** to capture:

   ```bash
   bd stats                        # Overall project progress
   bd list --status=in_progress    # Active work
   bd list --status=closed         # Completed work
   bd blocked                      # Any blocked issues
   bd ready                        # What's available next
   ```

   This shows:
   - What tasks were completed
   - What's currently in progress
   - What's ready to work on next

4. **Check for mockup state** (if mockups/ exists):

   ```bash
   ls mockups/                     # Check for mockup directory
   # If exists, read mockups/mockup-log.md for current version and pending feedback
   ```

**think deeply about what context would be lost if starting fresh**

### Step 2: Analyze Work State

Determine the current implementation state:

1. **Implementation Progress**:
   - Which phase are we in?
   - Which tasks are complete/in-progress/blocked?
   - Any partial implementations?

2. **Critical Discoveries**:
   - Unexpected patterns found
   - Gotchas encountered
   - Solutions to tricky problems
   - Performance considerations discovered

3. **Deviations and Decisions**:
   - Where we deviated from plan and why
   - Judgment calls made
   - Trade-offs accepted

4. **Current Blockers**:
   - What's preventing progress
   - What's been tried
   - Potential solutions identified

### Step 3: Sync Beads and Check Git State

```bash
# Sync beads state
bd sync    # Exports to .beads/issues.jsonl

# Beads mode (see docs/beads-stealth-mode.md). Stealth → document next steps
# manually in the handoff doc (beads won't travel via git). Git mode (default):
if [ "$BEADS_MODE" != "stealth" ]; then
  git status                                  # .beads/issues.jsonl should be modified
  git add .beads/ && git commit -m "Sync beads state before handoff"
fi

# Check for uncommitted code changes
git diff

# Note any staged changes
git diff --staged

# Capture current HEAD for frontmatter
git rev-parse HEAD
```

Document any uncommitted work and its purpose.

**Beads persistence**:

- **Git mode** (personal projects): Beads state committed to git, persists across sessions
- **Stealth mode** (work repos): Beads state local-only, document next steps manually for handoff

**⛔⛔⛔ BARRIER 2: STOP! Ground every claim before writing. Every file:line, metric, test result, and progress figure MUST come from actual tool output (`git diff` / `git log` / `git diff --stat`, `bd`, a real test run) — never from memory or the template's example values. If a value isn't verified, omit it or mark it `unverified`. Omit empty sections entirely; never fill them with placeholders. Mark genuinely unknown fields `unknown`. ⛔⛔⛔**

### Step 4: Create Handoff Document

Create handoff in the project directory:

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
beads_epic: [epic-id from tasks.md]
beads_active_phase: [phase-id if in_progress]
---

# Handoff: [Project Name] - [Brief Status]

**Created**: [YYYY-MM-DD HH:MM TZ]
**Reason**: [handoff reason]
**Current Phase**: Phase [N] of [Total]
**Overall Progress**: [from `bd stats` — e.g. closed/total; omit if not derivable]

## Quick Start

Same machine? Prefer native `claude --resume` — it restores the full prior session (including tool results) more reliably than any doc. This handoff exists for **cross-machine / cross-agent / teammate** transfer: resume with `/resume_handoff [this file path]`.

## Current State Summary

**What we're building**: [Brief description from design.md]

**Where we are**: [Current status - e.g., "Implementing Phase 2, task 3 of 5"]

**Last completed action**: [What was just finished]

**Next immediate task**: [What to do next]

## Work Completed This Session

### Code Changes
[Each entry derived from `git diff` / `git status` — `<file:line>` — what changed. Omit if none.]

### Tasks Completed
[From `bd list --status=closed` this session — IDs + titles. Omit if none.]

### Verification Run
[Only commands actually run this session, with their real output. Omit anything you did not run — do not assume pass/fail.]

### Beads Tracking State
```bash
# bd stats output
[total] open, [n] in_progress, [m] closed, [b] blocked

# Active phases (in_progress)
[phase-id]: [description]

# Blocked phases (if any)
[phase-id]: blocked by [blocker-id]

# Ready to work (next available)
[phase-id]: [description]
```

## Critical Learnings

### Discoveries Not in Documentation

[Non-obvious findings worth carrying forward — patterns, hidden dependencies, gotchas, required workarounds — each with a real `file:line`. Omit if none. Durable codebase facts belong in CLAUDE.md, not a one-shot handoff.]

**Also write the durable ones to `knowledge/staging/`**, per `skills/knowledge-store`. A handoff is read once by the next session and then goes stale; the store is read by every later ticket. Anything in this section that would still be true after this work ships belongs in both. Best-effort — if `./scripts/knowledge-worktree` exits non-zero, skip silently. Mark `origin: model-narrated` unless a tool produced the observation.

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
/resume_handoff [this file]

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
- **Open UI questions** (beads):
  - `[id]`: [question]

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

[Only what's measurable from tooling — omit the rest. Lines changed from `git diff --stat`; tasks closed from `bd list --status=closed`. Do NOT estimate session duration or any count you can't derive from a command.]

## Handoff Verification

Before using this handoff, verify:
- [ ] Project directory exists at specified path
- [ ] Git repository is at mentioned commit
- [ ] Tests pass as indicated
- [ ] No merge conflicts if branch changed

---

**Handoff Complete**: Ready for resumption using `/resume_handoff [path]`
````

### Step 5: Save and Confirm

Save the handoff document as:

```
[project-dir]/handoff-YYYY-MM-DD-HH-MM.md
```

Where:

- YYYY-MM-DD is current date
- HH-MM is current time (24-hour)

Present to user:

```
✅ Handoff document created successfully!

Saved to: [full path]/handoff-YYYY-MM-DD-HH-MM.md

This handoff captures:
- Current progress: Phase [N], [X]% complete
- Critical learnings: [count] discoveries
- Active blockers: [count] issues
- Next steps: [count] specific tasks

To resume this work in a new session:
/resume_handoff [full path to handoff file]

The handoff includes all context needed for seamless continuation.
```

## Important Guidelines

### What to Include

**ALWAYS Include**:

- Current phase and task status
- Recent code changes (file:line)
- Problems solved and how
- Active blockers and attempted solutions
- Critical discoveries about codebase
- Next immediate steps

**Include When Relevant**:

- Uncommitted changes and why
- Deviations from plan
- Performance considerations found
- Security issues discovered
- Architectural insights

**Don't Include**:

- Large code blocks (use file:line references)
- Obvious information from project docs
- Generic advice
- Completed and verified work from previous phases

### Handoff Quality

A good handoff should allow someone to:

1. Understand exactly where you left off
2. Know what problems you solved
3. Avoid repeating failed attempts
4. Continue without re-discovering context
5. Make the same decisions you made

### When to Create Handoffs

Create a handoff when:

- Session is ending with work incomplete
- Switching to different model for complex work
- Blocked and need different expertise
- Completed significant milestone
- Made important discoveries

## Relationship to Other Commands

Typical workflows:

**Mid-Implementation Handoff**:

1. `/implement_tasks` - Working on implementation
2. [Hit blocker or session limit]
3. **`/create_handoff`** - Document current state
4. [New session]
5. `/resume_handoff` - Continue where left off

**Phase Completion Handoff**:

1. Complete Phase N
2. `/validate_execution` - Verify work
3. **`/create_handoff`** - Document for next phase
4. [New session]
5. `/resume_handoff` - Start Phase N+1

## Configuration

This command creates rich context documents for work continuity. Best used when work spans multiple sessions or needs transfer between different agents/models.

The handoff document is self-contained and includes everything needed to resume work without loss of context or discovered knowledge.
