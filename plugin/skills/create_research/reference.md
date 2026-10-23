# create_research — reference

Read this when a step directs you to.

## Research practice

- Find concrete file paths and line numbers for developer reference.
- Make the research document self-contained, with all the context it needs.
- Keep each sub-agent prompt specific, and limit it to read-only documentation work.
- Document how components connect and how systems interact.
- Have sub-agents document examples and usage patterns as they exist.
- Keep the main session on synthesis. The agents do the deep file reading.

## Configuration

The command accepts the directory path as a parameter:

```
/wb:create_research docs/plans/2025-10-07-my-project
```

If the directory path is not given, the command prompts for it.
