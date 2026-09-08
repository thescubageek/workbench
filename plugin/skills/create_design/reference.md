# create_design — reference

Read this when a step directs you to.

## Important Guidelines

### Design Principles

1. **Separate WHAT from HOW**:
   - Design says WHAT to build and WHY
   - Execution plan says HOW to build it
   - Don't include implementation sequences

2. **Make Decisions Explicit**:
   - Document every significant choice
   - Include rationale and trade-offs
   - Note what was rejected and why

3. **Respect Research Findings**:
   - Build on patterns found in research
   - Respect constraints discovered
   - Don't contradict factual findings

4. **Keep It Disposable**:
   - Design should be complete but changeable
   - If approach is wrong, should be able to start over
   - Research remains valid even if design changes

### What Belongs in Design vs Execution

**Design (THIS document - WHAT and WHY only)**:

- ✅ Architecture decisions (WHAT architecture to use and WHY)
- ✅ Data models (WHAT data structures and WHY)
- ✅ API contracts (WHAT interfaces and WHY)
- ✅ Success criteria (WHAT defines success and WHY)
- ✅ Scope boundaries (WHAT is included/excluded and WHY)
- ✅ Technical approach (WHAT approach and WHY)

**Execution (tasks.md - HOW only - NEVER PUT THESE HERE)**:

- ❌ Phase sequencing (HOW to order implementation)
- ❌ Specific code changes (HOW to modify files)
- ❌ Step-by-step implementation (HOW to build it)
- ❌ Test writing tasks (HOW to test it)
- ❌ File modification lists (HOW to change code)
- ❌ Command sequences (HOW to execute changes)

**REMEMBER: If it describes HOW to do something, it DOES NOT belong in design**

### Handling Knowledge Gaps

When research has knowledge gaps:

1. **Document assumptions**:
   - State what you're assuming
   - Note risk if assumption is wrong
   - Plan for discovery during implementation

2. **Design for flexibility**:
   - Don't over-commit to uncertain areas
   - Build in abstraction where needed
   - Plan for multiple scenarios

3. **Flag for implementation**:
   - Mark decisions that depend on unknowns
   - Note what needs investigation
   - Will be resolved in execution phase

### Leveraging Agent Findings

Use agent findings to strengthen design:

1. **Pattern matching**: Reference similar implementations found by agents
2. **Integration validation**: Use agent findings to validate integration approach
3. **Risk assessment**: Incorporate historical findings from agents
4. **Consistency**: Ensure design follows patterns identified by agents

## Configuration

This skill creates design decisions based on validated research. It leverages Claude Code's agent spawning capabilities to verify design approaches and find precedents.
