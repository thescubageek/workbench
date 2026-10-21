---
name: implement_coordinated
description: Deprecated alias of implement — use /wb:implement (removed at 4.0.0)
argument-hint: "[project-directory] [phase-number|continue]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Implement Coordinated (Deprecated Alias)

This command was renamed to `/wb:implement`. The coordinated worker path is the *recommended* execution path, so it now carries the plain verb; the inline path is `/wb:implement_inline`, which names what is actually different about it. The alias remains through 3.x and is removed at 4.0.0.

## Behavior

1. **Tell the user once, up front**:

   ```
   Note: /wb:implement_coordinated is now /wb:implement — same skill, new name.
   This alias works through 3.x and will be removed at 4.0.0.
   ```

2. **Then run the canonical skill**: Read [../implement/SKILL.md](../implement/SKILL.md) NOW and follow it exactly, passing through any arguments unchanged. Its supporting files (`prompts/`, `templates/`, `reference.md`) live in `../implement/` and are read from there — this directory holds the stub and nothing else.

Do not duplicate any behavior here; the canonical skill is the single source of truth.
