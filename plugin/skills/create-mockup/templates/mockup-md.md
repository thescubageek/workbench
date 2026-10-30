# mockup.md

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 5. Write `mockups/v00N/mockup.md`. Note the Open Questions table. UI questions live in
this document, with local `UIQ` IDs.

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
**Trigger**: [How the user gets here]

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
- **Data**: [what the section displays]
- **Source**: [where the data comes from]
- **Empty state**: [what shows when there is no data]

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

- It uses [color tokens] from [file]
- It follows [spacing system]
- Typography: [heading/body styles]

## Icons

- System: [icon library/approach from research, or "None - text only"]
- Usage: [how icons are applied, with examples]
- Locations: [where icons appear in this mockup]

**If no icon system exists but the mockup needs icons:** add a `UIQ` row in Open Questions below.
For example: "No icon system exists. The options are a new library, text only, or custom SVG."
Do not invent an icon system.

## Open Questions

This table lists the UI questions that block the final version. Each question has a short local
ID. This table is the record, because there is no external tracker.

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| UIQ1 | [The question, specific enough for the user to answer] | [What cannot proceed] | Open |
| UIQ2 | [Another question] | [What it blocks] | Open |

- **IDs are local and stable.** Number them `UIQ1`, `UIQ2`, and so on, in the order you raise
  them. Never renumber them, because later versions and `mockup-log.md` cite them.
- **IDs carry across versions.** A question from v001 that is still open in v003 keeps `UIQ1`.
  This shows how long the question stayed open.
- **A question gets a row only if it blocks something.** Otherwise it is a note for `decisions.md`.
- **Resolving is an edit, not a deletion.** Set State to `Resolved YYYY-MM-DD — [the answer]`,
  and move the decision into the `decisions.md` of that version. The row stays.
````
