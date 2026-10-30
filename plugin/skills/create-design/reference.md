# create-design — reference

Read this when a step directs you to.

## Important Guidelines

### Design Principles

1. **Make Decisions Explicit**:
   - Document every significant choice
   - Include rationale and trade-offs
   - Note what was rejected and why

2. **Respect Research Findings**:
   - Build on patterns found in research
   - Respect constraints discovered
   - Do not contradict factual findings

3. **Keep It Disposable**:
   - Design should be complete but changeable
   - If the approach is wrong, you should be able to start over
   - Research remains valid even if design changes

### What Belongs in Design vs Execution

**Design (`design.md`: what and why)**:

- ✅ Architecture decisions (what architecture to use, and why)
- ✅ Data models (what data structures, and why)
- ✅ API contracts (what interfaces, and why)
- ✅ Success criteria (what defines success, and why)
- ✅ Scope boundaries (what is included or excluded, and why)
- ✅ Technical approach (what approach, and why)

**Execution (`tasks.md`: how). These do not go in the design**:

- ❌ Phase sequencing (how to order the implementation)
- ❌ Specific code changes (how to modify files)
- ❌ Step-by-step implementation (how to build it)
- ❌ Test writing tasks (how to test it)
- ❌ File modification lists (how to change code)
- ❌ Command sequences (how to run the changes)

### Handling Knowledge Gaps

When research has knowledge gaps:

1. **Document assumptions**:
   - State what you are assuming
   - Note the risk if the assumption is wrong
   - Plan for discovery during implementation

2. **Design for flexibility**:
   - Do not over-commit to uncertain areas
   - Build in abstraction where needed
   - Plan for multiple scenarios

3. **Flag for implementation**:
   - Mark decisions that depend on unknowns
   - Note what needs investigation
   - The execution phase resolves them

### Leveraging Agent Findings

Use agent findings to strengthen design:

1. **Pattern matching**: Reference similar implementations found by agents
2. **Integration validation**: Use agent findings to validate integration approach
3. **Risk assessment**: Incorporate historical findings from agents
4. **Consistency**: Ensure design follows patterns identified by agents

## Why the approval and journal rules are shaped this way

`SKILL.md` carries the instruction. The reason lives here.

- **Approval cannot predate the artifact.** Three separate sessions independently concluded
  that "run the plan" or a `forge` invocation issued before `design.md` existed is not approval
  of it. Two of them reached that conclusion only after they first conflated the two. Step 6
  states it so the next session does not have to derive it.
- **`approved` is set only on confirmation** because it is the gate `create-tasks` and `forge`
  read. A design left at `draft` stops the pipeline with no explanation. A design advanced on
  the session's own judgment removes the only review step between a design and its tasks. A body
  `**Status**:` line is deleted because two copies of status is how they come to disagree.
- **The journal entry closes on approval, not on writing.** On 2026-09-11 a machine restart
  killed a session that had written a complete design and was waiting for approval. With no open
  entry, the resuming session would have re-run the stage and regenerated options the user had
  already chosen. Design is the longest-running planning stage, so it is the one most likely to
  be interrupted. That is also why the entry is opened before reading, not after writing.
- **Timestamps come from the clock** because guessed timestamps produced entries dated in the
  future and out of order. Those entries corrupted the one thing a journal records: what
  happened, in what sequence.

## Configuration

This skill creates design decisions based on validated research. It leverages Claude Code's agent spawning capabilities to verify design approaches and find precedents.
