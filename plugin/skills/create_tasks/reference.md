# create_tasks — reference

Read this when a step directs you to.

## Important Guidelines

### Execution Planning Principles

1. **Bridge Current to Target**:
   - Start from research (current state)
   - End at design (target state)
   - Plan the transformation path

2. **Phase by Risk and Dependencies**:
   - Use agent findings to order phases
   - Riskiest changes early (fail fast)
   - Dependencies before dependents
   - Infrastructure before features

3. **Make Tasks Executable**:
   - Specific file and line references
   - Exact code to add/change
   - Clear test scenarios from agent
   - Runnable commands

4. **Enable Incremental Progress**:
   - Each phase independently valuable
   - Checkpoints prevent cascading issues

### What Belongs in Execution vs Design

**Execution (THIS document)**:

- ✅ Phase sequencing and dependencies
- ✅ Specific code changes
- ✅ File modifications with line numbers
- ✅ Test writing tasks
- ✅ Command sequences

**Design (design.md)**:

- ❌ Architecture decisions (already made)
- ❌ Success criteria (reference them)
- ❌ Scope decisions (already defined)
- ❌ Technical approach (already chosen)

### Handling Implementation Discoveries

Some things can only be determined during coding:

1. **Document in "Implementation Discoveries"**:
   - Note what needs investigation
   - Update with findings as discovered
   - Adjust tasks if needed

2. **Don't Block on Minor Unknowns**:
   - Make reasonable assumptions for low-stakes details
   - Plan to test and adjust
   - Document the uncertainty
   - **But**: if an unknown is *load-bearing* (its failure invalidates whole phases), don't assume — resolve it with a Phase 0 tracer bullet first (see Step 3)

3. **Update During Implementation**:
   - Add discovered constraints
   - Note performance findings
   - Record configuration needs

### Leveraging Agent Findings

Use agent findings throughout execution plan:

1. **Dependencies**: Order phases based on dependency agent analysis
2. **Testing**: Incorporate test coverage agent recommendations
3. **Patterns**: Reference similar implementations found by pattern agent
4. **Risk mitigation**: Address risks identified by agents

## Task Granularity

Tasks should be:

- **Specific**: "Create PaymentRetry class at src/retry/PaymentRetry.ts"
- **Sized by projected tool calls** — see below
- **Testable**: Clear completion criteria
- **Independent**: Minimal blocking between tasks

### Size by tool calls, not by hours

Wall-clock time predicts nothing about whether a task can be finished. **Tool calls do.** A
one-hour task touching 3 files is ~20 calls; a one-hour task touching 12 files is ~80.

A delegated worker hard-stops when it exhausts its tool-call budget — observed near **~70
calls**, which is measured evidence from one machine and one model, not a guaranteed constant.
The failure is worse than it sounds because truncation always eats the **finishing tail**: the
last edits, the verification run, the status update. What is left behind looks like work in
progress, not like a failure.

**A task projecting past ~50 calls is split at its natural seam before it is ever spawned.**
Half the observed ceiling is the budget, because the estimate is an estimate.

Annotate each task with its rough projection — `(~30 calls)` — so the number that predicts
truncation is the number the plan carries. `examples.md` works through a projection and a
split.

## Configuration

This skill creates an execution plan from approved research and design documents. It leverages Claude Code's agent spawning capabilities to analyze dependencies, test coverage, and similar patterns.
