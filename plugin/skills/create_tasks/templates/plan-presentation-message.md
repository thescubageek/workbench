# Plan presentation message

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 6. Emit this once, after `tasks.md` is written.

```
✅ The execution plan is written: [path]/tasks.md

Implementation structure:
- Phase 1: [Name] - [X] tasks
- Phase 2: [Name] - [Y] tasks
- Phase 3: [Name] - [Z] tasks

Total tasks: [total count]

Agent findings used in the plan:
- Dependency order: [key dependency from agent]
- Test coverage: [X] unit tests, [Y] integration tests
- Similar patterns: [reference to pattern agent findings]

Assumptions and pending decisions:
- [Each ID with its meaning in parentheses, for example "A1 (only checker.py reads MAX_RETRIES)", and its state. Or "none"]

The plan has these features:
- An implementation order from the dependency analysis
- Specific code changes, with the state before and after each change
- Test coverage from the agent analysis
- Automated and manual verification for each phase
- Quick test commands, so that the full suite does not need to run each time
- A size for each task in projected tool calls. A task larger than about 50 calls is split

Where status lives:
- The checkboxes in tasks.md are the source of truth
- The frontmatter counters are a derived cache. /wb:update_status is their only writer
- Git is the durable record, with one commit for each task

Next steps:
1. Review the execution plan in tasks.md
2. Run `/wb:implement` to start the implementation with TDD and worker agents. `/wb:implement_inline` runs it in this session instead
3. Tick each checkbox when its work is done. Run /wb:update_status at each phase checkpoint
```
