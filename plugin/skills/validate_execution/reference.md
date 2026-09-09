# validate_execution — reference

Read this when a step directs you to.

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

- [ ] Every task marked `[x]` in tasks.md has corresponding code — a checkbox is a claim, and this is where the claim is tested
- [ ] No task left `[ ]` is actually complete in the code — an unflipped checkbox on finished work is as wrong as the reverse
- [ ] The frontmatter counters match the checkbox counts (if not, `/wb:update_status` has not run — note it, do not fix it here)
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
3. `/create_tasks` - Plan how to build
4. `/implement` - Build it with TDD via worker agents (`/implement_inline` runs it in this session)
5. **`/validate_execution`** - Verify it was built correctly ← YOU ARE HERE
6. `/create_handoff` - Document for next session (if needed)

## Configuration

This skill performs comprehensive validation of implemented plans. It can be run by the implementer for self-check or by another person/agent for objective validation.

Best used:

- After implementation before merge
- When resuming work to verify state
- Before deployment to production
- For quality assurance checks
