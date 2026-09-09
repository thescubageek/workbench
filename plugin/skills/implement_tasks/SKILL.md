---
name: implement_tasks
description: Deprecated alias of implement_inline — use /wb:implement_inline (removed at 3.0.0)
argument-hint: "[project-directory] [phase-number|continue]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Implement Tasks (Deprecated Alias)

This command was renamed to `/wb:implement_inline`: it runs the plan inline on the session model, so the name now says what is different about it. The recommended coordinated path — worker agents, main context kept clean — is `/wb:implement`. The alias remains through 2.x and is removed at 3.0.0.

## Behavior

1. **Tell the user once, up front**:

   ```
   Note: /wb:implement_tasks is now /wb:implement_inline — same skill, new name.
   If you wanted worker agents rather than inline execution, use /wb:implement.
   This alias works through 2.x and will be removed at 3.0.0.
   ```

2. **Then run the canonical skill**: Read [../implement_inline/SKILL.md](../implement_inline/SKILL.md) NOW and follow it exactly, passing through any arguments unchanged. Its supporting files (`templates.md`, `reference.md`) live in `../implement_inline/` and are read from there — this directory holds the stub and nothing else.

Do not duplicate any behavior here; the canonical skill is the single source of truth.
