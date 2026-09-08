---
description: Validate that execution plan was correctly implemented and verify all success criteria
argument-hint: "[project-directory]"
---

# Validate Execution

Validates that an execution plan was correctly implemented, verifying all success criteria and identifying any deviations, gaps, or issues.

**Model & effort (gate check)**: on entry, consult the `model-help` skill (gate mode) for the model + effort this phase warrants; surface its one-line verdict and — only if a switch clears the switch-cost bar — the `/model` action. Baseline is Sonnet/medium, rising to Opus/high when the change has wide blast radius, is compliance/security-sensitive, or is hard to verify (mistakes hide until prod) — adversarial checking of sensitive code earns the higher tier. Best-effort and non-blocking: stay silent and proceed when the current tier is already right. See CLAUDE.md → "Model & effort at gates."

## Purpose

This command provides an objective assessment of implementation completeness by:

- Verifying claimed completions match actual code changes
- Running all automated verification checks
- Identifying deviations from the plan
- Documenting gaps or issues found
- Providing clear manual testing requirements

Run this AFTER implementation to ensure quality before merging or deployment.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/validate_execution docs/plans/2025-01-08-my-project/`):
   - Use `$1` as the project directory
   - Read all documentation immediately
   - Begin validation process

2. **If no arguments**:

   ```
   I'll validate the execution of your implementation plan. Please provide:
   1. Path to the project documentation directory (e.g., docs/plans/2025-01-08-my-project/)

   I'll verify that the implementation matches the plan and all success criteria are met.
   ```

## Process Steps

### Step 1: Context Discovery

**⛔⛔⛔ BARRIER 1: STOP! Read ALL documentation FULLY - research.md, design.md, tasks.md ⛔⛔⛔**

```javascript
const projectDir = $1 || /* prompt for it */;

// Read all project documentation
const researchFile = `${projectDir}/research.md`;
const designFile = `${projectDir}/design.md`;
const tasksFile = `${projectDir}/tasks.md`;
```

1. **Read tasks.md completely** to understand:
   - What phases were planned
   - Success criteria for each phase
   - Modified files listed
   - NOTE: tasks.md checkboxes are **documentation only** — they are NOT the status source (`implement_tasks`/`resume_handoff` do not update them). Read completion from beads instead (next item).

2. **Read task completion status from beads** (the source of truth):
   - Verify beads is available with a fast, filesystem-only probe — do NOT use `bd doctor` (it can hang; see docs/beads-fast-fail.md):

     ```bash
     if [ "$BEADS_AVAILABLE" = "yes" ] || { command -v bd >/dev/null 2>&1 && [ -d .beads ]; }; then
       bd list --status closed   # tasks/phases actually completed
       bd list --status open     # remaining work
       bd stats                  # completion counts for the executive summary
     else
       echo "⚠️ Beads unavailable — fall back to tasks.md checkboxes, but flag that status is unverified."
     fi
     ```

   - Use the beads issue IDs in tasks.md frontmatter (`beads_epic`, `beads_phases`, `beads_tasks`) to map each phase/task to its issue and read its real status.

3. **Read design.md** to understand:
   - Original design decisions
   - Success metrics defined
   - Scope boundaries

4. **Read research.md** to understand:
   - Original state of the codebase
   - Patterns that should be followed

**think deeply about what was supposed to be built vs what exists**

### Step 2: Spawn Validation Agents

**Use parallel agents to verify implementation comprehensively:**

**CRITICAL: Sub-agents gather information and return findings. They do NOT write files. YOU (the main agent) will write the validation report after synthesizing their findings.**

```javascript
// Spawn validation agents concurrently
Task({
  description: "Verify code changes",
  prompt: `Analyze all code changes to verify they match the execution plan.

  From tasks.md, these files should be modified:
  [List files from tasks.md]

  Check:
  - Were all listed files actually modified?
  - Do modifications match specified changes?
  - Are there unexpected modifications?
  - Were any planned changes missed?

  Use git diff to compare changes if needed.
  Return findings only; write nothing.`,
  subagent_type: "codebase-analyzer",
  model: "haiku"
})

Task({
  description: "Verify test coverage",
  prompt: `Verify that all tests specified in the plan were implemented.

  From tasks.md, these tests were required:
  [List test requirements]

  Check:
  - Do all specified tests exist?
  - Do they test the right scenarios?
  - Are there gaps in coverage?
  - Do all tests pass?

  Run test commands and analyze coverage.
  Return findings only; write nothing.`,
  subagent_type: "general-purpose",
  model: "sonnet"
})

Task({
  description: "Check for regressions",
  prompt: `Verify no existing functionality was broken.

  Run comprehensive checks:
  - All existing tests still pass
  - Build succeeds without warnings
  - No performance degradation
  - No breaking changes to APIs

  Return findings only; write nothing.`,
  subagent_type: "general-purpose",
  model: "sonnet"
})

Task({
  description: "Analyze patterns and quality",
  prompt: `Verify implementation follows established patterns.

  From research.md, these patterns should be followed:
  [List patterns from research]

  Check:
  - Does new code follow existing patterns?
  - Are conventions maintained?
  - Is error handling consistent?
  - Are there any anti-patterns?

  Return findings only; write nothing.`,
  subagent_type: "pattern-finder",
  model: "sonnet"
})
```

**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL validation agents to complete ⛔⛔⛔**

### Step 3: Run Automated Verification

For each phase in tasks.md, run ALL automated verification commands:

```bash
# Common verification commands (adapt based on project)
make check      # Linting and formatting
make test       # Unit tests
make integration # Integration tests
make build      # Build verification

# Project-specific commands from tasks.md
[Run any specific commands listed in success criteria]
```

Document the results:

- ✅ Pass: Command succeeded
- ❌ Fail: Command failed (include error)
- ⚠️ Partial: Some issues but not blocking

### Step 4: Analyze Implementation Completeness

**think deeply about gaps between plan and reality**

For each phase in tasks.md:

1. **Check task completion** (against beads, not checkboxes):
   - For each task/phase issue reported `closed` in beads, verify it was actually done — look for evidence in code changes
   - Flag any beads issue closed without corresponding code (false completion), and any open issue whose work appears done (unclosed completion)
   - Ignore tasks.md `[x]` marks as a status signal — they are documentation only and routinely stale

2. **Verify success criteria**:
   - Were all automated criteria met?
   - Are manual criteria ready for testing?
   - Any criteria impossible to verify?

3. **Identify deviations**:
   - Changes made differently than planned
   - Additional changes not in plan
   - Planned changes not implemented

4. **Assess impact**:
   - Are deviations improvements or problems?
   - Do they affect the overall solution?
   - Should they be documented or reverted?

### Step 5: Generate Validation Report

**⛔⛔⛔ BARRIER 3: STOP! No placeholders in the report — every file:line, metric, test result, and status must come from real tool output (agent findings, `bd` status, verification runs). Omit or mark `unverified` rather than inventing a value. ⛔⛔⛔**

Create a comprehensive validation report:

```markdown
# Validation Report: [Project Name]
Generated: [YYYY-MM-DD HH:MM]

## Executive Summary

**Overall Status**: ✅ PASSED | ⚠️ PASSED WITH ISSUES | ❌ FAILED

- Planned Phases: [X]
- Completed Phases: [Y]
- Task Completion: [X]/[Y] tasks ([percentage]%)
- Automated Tests: [PASS/FAIL]
- Manual Testing Required: YES/NO

## Phase-by-Phase Validation

### Phase 1: [Name]
**Status**: ✅ Fully Implemented | ⚠️ Partially Implemented | ❌ Not Implemented

#### Completed Tasks
✅ [Task description] - Verified at `file:line`
✅ [Task description] - Verified at `file:line`

#### Incomplete/Missing Tasks
❌ [Task description] - Not found in code
⚠️ [Task description] - Partially complete (missing X)

#### Success Criteria Results

**Automated Verification**:
- ✅ Tests pass: `make test` (all 45 tests passing)
- ✅ Linting clean: `make lint` (no issues)
- ❌ Build fails: `make build` (error: [specific error])

**Manual Verification Required**:
- [ ] [Manual test 1 from plan]
- [ ] [Manual test 2 from plan]

### Phase 2: [Name]
[Similar structure...]

## Code Quality Analysis

### Pattern Compliance
- ✅ Follows existing error handling patterns
- ✅ Uses established naming conventions
- ⚠️ Inconsistent with logging pattern at `file:line`

### Test Coverage
- Unit Tests: [X]% coverage ([Y] new tests added)
- Integration Tests: [X] scenarios covered
- Missing Tests: [List any gaps]

## Deviations from Plan

### Justified Deviations
1. **[Description]** at `file:line`
   - Plan specified: [what plan said]
   - Actual implementation: [what was done]
   - Justification: [why it's better]

### Unjustified Deviations
1. **[Description]** at `file:line`
   - Should be: [per plan]
   - Actually is: [current state]
   - Impact: [consequences]

## Issues and Risks

### Critical Issues (Must Fix)
- 🔴 [Issue description] - Blocks functionality
- 🔴 [Issue description] - Security concern

### Non-Critical Issues (Should Fix)
- 🟡 [Issue description] - Performance impact
- 🟡 [Issue description] - Maintainability concern

### Potential Risks
- ⚠️ [Risk description] - Monitor in production
- ⚠️ [Risk description] - May affect [component]

## Recommendations

### Immediate Actions Required
1. Fix build error at `file:line`
2. Add missing test for [scenario]
3. Complete [incomplete task]

### Before Deployment
1. Perform manual testing checklist below
2. Review with team lead
3. Update documentation

### Future Improvements (Not Blocking)
1. Consider refactoring [component] for clarity
2. Add additional error handling at [location]

## Manual Testing Checklist

Copy this checklist for manual verification:

### User Interface
- [ ] Feature appears correctly in UI
- [ ] All user interactions work as expected
- [ ] Error states display properly
- [ ] Performance is acceptable

### Integration
- [ ] Works with existing [component]
- [ ] Data flows correctly through system
- [ ] No regressions in related features

### Edge Cases
- [ ] Handles empty/null inputs
- [ ] Works with maximum data size
- [ ] Graceful degradation on errors

## Appendix: Validation Evidence

### Git Changes Summary
```bash
Files changed: [X]
Insertions: +[Y] lines
Deletions: -[Z] lines
```

### Test Execution Logs

[Include key excerpts from test runs]

### Agent Findings

[Include relevant findings from validation agents]

---

## Validation Completed

**Next Steps**:

1. Address any critical issues identified
2. Perform manual testing using checklist above
3. Get approval from reviewer
4. Deploy with confidence

**Validator Notes**:
[Any additional context or observations about the implementation]

```

### Step 6: Update Documentation

If validation passes with minor issues:
1. Reconcile status in **beads** (`bd close`/`bd update`) to reflect actual completion — beads is the source of truth; only ever update tasks.md checkboxes *from* beads, never the reverse
2. Document any approved deviations
3. Note lessons learned for future projects

If validation fails:
1. Clearly mark which tasks need completion
2. Provide specific guidance for fixes
3. Re-run validation after fixes

## Important Guidelines

### Validation Philosophy

1. **Be Objective**: Assess what IS, not what SHOULD BE
2. **Be Thorough**: Check everything, assume nothing
3. **Be Constructive**: Identify issues with solutions
4. **Be Precise**: Use file:line references for all claims
5. **Be Practical**: Focus on what matters for deployment

### What Makes a PASS vs FAIL

**✅ PASS**:
- All critical functionality implemented
- All automated tests pass
- No blocking issues
- Ready for manual testing

**⚠️ PASS WITH ISSUES**:
- Core functionality works
- Some non-critical issues exist
- Can be deployed with known limitations
- Issues documented for future work

**❌ FAIL**:
- Critical functionality missing
- Tests failing
- Blocking issues present
- Not safe to deploy

### Common Validation Checks

Always verify:
- [ ] All phases/tasks closed in beads actually are complete (with corresponding code)
- [ ] No completed work is left open in beads, and no closed issue lacks code
- [ ] All tests pass consistently
- [ ] No regressions introduced
- [ ] Build succeeds cleanly
- [ ] Error handling is robust
- [ ] Patterns are followed
- [ ] Documentation updated if needed

## Relationship to Other Commands

Recommended workflow:
1. `/create_research` - Document current state
2. `/create_design` - Decide what to build
3. `/create_execution` - Plan how to build
4. `/implement_tasks` - Build it with TDD
5. **`/validate_execution`** - Verify it was built correctly ← YOU ARE HERE
6. `/create_handoff` - Document for next session (if needed)

## Configuration

This command performs comprehensive validation of implemented plans. It can be run by the implementer for self-check or by another person/agent for objective validation.

Best used:
- After implementation before merge
- When resuming work to verify state
- Before deployment to production
- For quality assurance checks
