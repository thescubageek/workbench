# Error Handling

## Invalid Transitions

If user requests invalid transition:

```
⚠️ Invalid Status Transition

Cannot transition design.md from 'draft' to 'approved' because:
- research.md is still in 'draft' status

Valid next steps:
1. Complete research first (/wb:create_research)
2. Confirm the design at /wb:create_design Step 6 — approval is a human act, and that
   confirmation is what writes 'approved'
```

## Missing Files

**Check for a remediation plan before reporting anything missing.** A directory that
`../../../docs/reference/remediation-plan.md` recognises as a round means `tasks.md` alone *is* the
whole plan — research.md and design.md are not missing, they were never written, and this message must
not fire. Reconcile the counters from the checkboxes and carry on; `/wb:create_project` would
manufacture two files that exist only to be empty.

Otherwise, if files don't exist:

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
- design.md: draft
- tasks.md: in-progress (7 of 24 tasks [x])

This is inconsistent. Suggesting correction:
- Set design.md back to 'draft' OR
- Confirm implementation has started and flip the tasks that are done

Which would you prefer?
```
