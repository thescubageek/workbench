---
name: create_execution
description: Deprecated alias of create_tasks — use /wb:create_tasks (removed at 3.0.0)
argument-hint: "[project-directory]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Create Execution (Deprecated Alias)

This command was renamed to `/wb:create_tasks`, matching the convention that a `create_*` stage is named for the artifact it writes — and this one writes `tasks.md`. The alias remains through 2.x and is removed at 3.0.0.

## Behavior

1. **Tell the user once, up front**:

   ```
   Note: /wb:create_execution is now /wb:create_tasks — same skill, new name.
   This alias works through 2.x and will be removed at 3.0.0.
   ```

2. **Then run the canonical skill**: Read [../create_tasks/SKILL.md](../create_tasks/SKILL.md) NOW and follow it exactly, passing through any arguments unchanged. Its supporting files (`templates/`, `sub-agent-prompts.md`, `examples.md`, `reference.md`) live in `../create_tasks/` and are read from there — this directory holds the stub and nothing else.

Do not duplicate any behavior here; the canonical skill is the single source of truth.
