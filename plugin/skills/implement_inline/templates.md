# implement_inline — templates

Read the **section you need**, when its step directs you to.

Sections: `Modified Files fragment` (Step 5) · `Manual verification request` (Step 6) ·
`Phase completion report` (Step 6)

## Modified Files fragment

Step 5 — append or update this section in `tasks.md` after implementation.

````markdown
### 📝 Modified Files

#### Code Files
- `path/to/file1.ext` - Implemented [feature]
- `path/to/file2.ext` - Added [functionality]

#### Test Files
- `path/to/test1.spec.ts` - Tests for [feature]
- `path/to/test2.test.ts` - Integration tests for [scenario]

**Quick test commands:**

```bash
# Run tests for this phase only (scope which tests run AND quiet the green output)
scripts/quiet npm test path/to/test1.spec.ts path/to/test2.test.ts
```
````

## Manual verification request

Step 6 — emitted at the phase checkpoint, then **stop and wait**.

```
✅ Phase [N] Automated Verification Complete

**Automated checks passed:**
- ✅ All tests passing: [test command]
- ✅ Linting clean: [lint command]
- ✅ Build successful: [build command]

**Phase [N] task state:**
- ✅ Every Phase [N] checkbox is [x] ([X] of [X])

**Manual verification required:**

Please perform the following manual checks from design.md:

1. [Manual verification item 1]
2. [Manual verification item 2]
3. [Manual verification item 3]

Reply when manual verification is complete and I'll close out the phase.
```

## Phase completion report

Step 6 — emitted once, after the human confirms manual verification.

```
✅ Phase [N] Complete

**Progress Summary:**
- Phase [N]: [X] tasks completed, every checkbox [x]
- Next phase: [Y] tasks
- Files modified: [count] code files, [count] test files
- Counters reconciled by /wb:update_status

Ready to proceed to Phase [N+1].
```
