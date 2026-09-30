# validate_execution — templates

Write this output in wb Technical English (WBTE): read [technical-english.md](../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Read the **section you need**, when its step directs you to.

Sections: `Validation report` (Step 5)

## Validation report

Step 5. This is the document that the skill writes. Every file:line, metric, test result and
status in it must come from real tool output. If a value has no source, omit it or mark it
`unverified`. Do not invent a value.

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
⚠️ [Task description] - Partly complete (X is missing)

#### Success Criteria Results

**Automated Verification**:
- ✅ Tests pass: `make test` (45 of 45 tests pass)
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
   - Justification: [why it is better]

### Unjustified Deviations
1. **[Description]** at `file:line`
   - Should be: [per plan]
   - Actually is: [current state]
   - Impact: [consequences]

## Issues and Risks

### Critical Issues (Must Fix)
- 🔴 [Issue description] - It blocks a function
- 🔴 [Issue description] - It is a security concern

### Non-Critical Issues (Should Fix)
- 🟡 [Issue description] - It affects performance
- 🟡 [Issue description] - It makes maintenance harder

### Potential Risks
- ⚠️ [Risk description] - Monitor it in production
- ⚠️ [Risk description] - May affect [component]

## Recommendations

### Immediate Actions Required
1. Fix build error at `file:line`
2. Add missing test for [scenario]
3. Complete [incomplete task]

### Before Deployment
1. Do the manual testing checklist below
2. Review the change with the team lead
3. Update the documentation

### Future Improvements (Not Blocking)
1. Consider refactoring [component] for clarity
2. Add error handling at [location]

## Manual Testing Checklist

Copy this checklist for the manual verification:

### User Interface
- [ ] The feature appears correctly in the UI
- [ ] All user interactions work as expected
- [ ] Error states display correctly
- [ ] The performance is acceptable

### Integration
- [ ] It works with the existing [component]
- [ ] Data flows correctly through the system
- [ ] Related features show no regressions

### Edge Cases
- [ ] It handles empty or null inputs
- [ ] It works with the maximum data size
- [ ] It degrades safely when an error occurs

## Appendix: Validation Evidence

### Git Changes Summary
```bash
Files changed: [X]
Insertions: +[Y] lines
Deletions: -[Z] lines
```

### Test Execution Logs

[Include the key excerpts from the test runs]

### Agent Findings

[Include the relevant findings from the validation agents]

---

## Validation Completed

**Next Steps**:

1. Fix each critical issue found above
2. Do the manual testing with the checklist above
3. Get approval from a reviewer
4. Deploy the change

**Validator Notes**:
[Other context or observations about the implementation]

````
