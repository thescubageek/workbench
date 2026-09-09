# Error Handling

## Invalid Transitions

If user requests invalid transition:

```
⚠️ Invalid Status Transition

Cannot transition design.md from 'draft' to 'implementing' because:
- research.md is still in 'draft' status
- No task checkbox in tasks.md is [x]

Valid next steps:
1. Complete research first (/wb:create_research)
2. Move design to 'ready' status once research is complete
3. Flip a task checkbox in tasks.md to begin implementing
```

## Missing Files

If files don't exist:

```
❌ Missing Documentation Files

Expected files in [directory]:
- research.md [✓/✗]
- design.md [✓/✗]
- tasks.md [✓/✗]

Run /wb:create_project first to initialize the documentation structure.
```

## Inconsistent State

If files have conflicting status:

```
⚠️ Inconsistent Status Detected

Current state:
- design.md: implementing
- tasks.md: not-started (0 of 24 tasks [x])

This is inconsistent. Suggesting correction:
- Set design.md back to 'ready' OR
- Confirm implementation has started and flip the tasks that are done

Which would you prefer?
```
