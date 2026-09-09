# validate_execution — templates

Read the **section you need**, when its step directs you to.

Sections: `Validation report` (Step 5)

## Validation report

Step 5 — the document this skill produces. Every file:line, metric, test result and status in
it must come from real tool output; omit a value or mark it `unverified` rather than inventing
one.

````markdown
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

````
