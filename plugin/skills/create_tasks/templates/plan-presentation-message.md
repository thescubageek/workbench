# Plan presentation message

Step 6 — emitted once, after `tasks.md` is written.

```
✅ Execution plan created at: [path]/tasks.md

Implementation structure:
- Phase 1: [Name] - [X] tasks
- Phase 2: [Name] - [Y] tasks
- Phase 3: [Name] - [Z] tasks

Total tasks: [total count]

Agent findings incorporated:
- Dependency order: [key dependency from agent]
- Test coverage: [X] unit tests, [Y] integration tests
- Similar patterns: [reference to pattern agent findings]

Key features of the plan:
- Clear implementation sequence based on dependency analysis
- Specific code changes with before/after context
- Comprehensive test coverage from agent analysis
- Automated and manual verification per phase
- Quick test commands to avoid running full suite
- Every task sized by projected tool calls, split past ~50

Where status lives:
- Checkbox state in tasks.md is the source of truth
- Frontmatter counters are a derived cache; /wb:update_status is their only writer
- Git is the durable record — one task, one commit

Next steps:
1. Review the execution plan in tasks.md
2. Run `/wb:implement` to begin implementation with TDD via worker agents (`/wb:implement_inline` runs it in this session)
3. Flip checkboxes as work completes; run /wb:update_status at each phase checkpoint
```
