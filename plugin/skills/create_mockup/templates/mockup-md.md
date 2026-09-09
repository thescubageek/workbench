# mockup.md

Step 5 — `mockups/v00N/mockup.md`. Note the Open Questions table: UI questions live in this
document with local `UIQ` IDs.

````markdown
---
version: 1
created: [YYYY-MM-DD]
status: draft
feature: [feature name]
based_on: [similar feature from research]
---

# Mockup: [Feature Name] v001

## Overview

**Purpose**: [From clarifying questions]
**User**: [From clarifying questions]
**Trigger**: [How user gets here]

## Layout

```
┌─────────────────────────────────────────────────┐
│ [Header/Navigation - per existing pattern]       │
├─────────────────────────────────────────────────┤
│                                                 │
│   ┌─────────────────────────────────────────┐   │
│   │ [Component Area]                        │   │
│   │                                         │   │
│   │  [Content structure using ASCII]        │   │
│   │                                         │   │
│   │  ┌──────────┐  ┌──────────┐            │   │
│   │  │ Button 1 │  │ Button 2 │            │   │
│   │  └──────────┘  └──────────┘            │   │
│   │                                         │   │
│   └─────────────────────────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Components Used

| Component | From Library | Purpose |
|-----------|--------------|---------|
| [Component] | [file:line] | [what it does here] |

## Content Specifications

### [Section 1]
- **Data**: [what's displayed]
- **Source**: [where data comes from]
- **Empty state**: [what shows when no data]

### [Section 2]
...

## Interactions

1. **[Action]**: User clicks [element] → [result]
2. **[Action]**: User types in [field] → [validation/result]

## States

| State | Trigger | Display |
|-------|---------|---------|
| Loading | Initial load | [skeleton/spinner] |
| Empty | No data | [message + CTA] |
| Error | API failure | [error message] |
| Success | Action complete | [confirmation] |

## Styling Notes

- Uses [color tokens] from [file]
- Follows [spacing system]
- Typography: [heading/body styles]

## Icons

- System: [icon library/approach from research, or "None - text only"]
- Usage: [how icons are applied, with examples]
- Locations: [where icons appear in this mockup]

**If no icon system found but icons needed:** raise it as a `UIQ` row in Open Questions below —
"no icon system found; options are add a library, text only, or custom SVG" — rather than
inventing one.

## Open Questions

UI questions that block finalization live **here**, with a short local ID. This table is the
record — there is no external tracker.

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| UIQ1 | [The question, specific enough for the user to answer] | [What can't proceed] | Open |
| UIQ2 | [Another question] | [What it blocks] | Open |

- **IDs are local and stable.** `UIQ1`, `UIQ2`, … numbered in the order raised, never
  renumbered — later versions and `mockup-log.md` cite them.
- **IDs carry across versions.** A question raised in v001 and still open in v003 keeps `UIQ1`;
  the point is to see how long it stayed open.
- **A question earns a row only if it blocks.** Otherwise it is a note for `decisions.md`.
- **Resolving is an edit, not a deletion**: set State to `Resolved YYYY-MM-DD — [the answer]`
  and move the decision into that version's `decisions.md`. The row stays.
````
