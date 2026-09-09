# create_handoff — reference

Read this when a step directs you to.

## Purpose

Handoff documents preserve:

- Work in progress and current status
- Critical learnings and discoveries
- Context not captured in formal docs
- Exact state for seamless resumption
- Blockers and their solutions
- Next steps with specific guidance

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
- **A phase would need a second compaction — hand off instead.** One compaction is survivable:
  the recovery text fires and the plan documents get re-read. A second means the session is
  running on a paraphrase of a paraphrase, and the things that degrade first are exactly the
  ones a handoff captures deliberately — what was tried and abandoned, why a decision went the
  way it did, which gotcha bit. Handing off costs one document; the alternative costs the
  reasoning that made the work correct.

## Relationship to Other Commands

Typical workflows:

**Mid-Implementation Handoff**:

1. `/wb:implement` - Working on implementation
2. [Hit blocker or session limit]
3. **`/wb:create_handoff`** - Document current state
4. [New session]
5. `/wb:resume_handoff` - Continue where left off

**Phase Completion Handoff**:

1. Complete Phase N
2. `/wb:validate_execution` - Verify work
3. **`/wb:create_handoff`** - Document for next phase
4. [New session]
5. `/wb:resume_handoff` - Start Phase N+1

## Configuration

This skill creates rich context documents for work continuity. Best used when work spans multiple sessions or needs transfer between different agents/models.

The handoff document is self-contained and includes everything needed to resume work without loss of context or discovered knowledge.
