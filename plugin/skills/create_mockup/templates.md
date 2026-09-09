# create_mockup — templates

Read the **section you need**, when its step directs you to — not the whole file. Each block
below is independent, and this file is large.

Sections: `UI research summary` (Step 2) · `Clarifying questions` (Step 3) ·
`mockup.md` (Step 5) · `decisions.md` (Step 5) · `mockup.html` (Step 6) ·
`mockup-log.md` (Step 8) · `Presentation message` (Step 9)

## UI research summary

Step 2 — synthesize the five agents' findings into this shape.

```markdown
## UI Research Summary

### Layout System
- Pattern: [grid/flex/etc]
- Container widths: [values]
- Breakpoints: [mobile/tablet/desktop values]

### Component Library
- Location: [path]
- Key components: [list with file:line]
- Naming convention: [pattern]

### Styling Approach
- Method: [CSS modules/Tailwind/etc]
- Colors: [token location]
- Typography: [scale location]
- Spacing: [system]

### Icon System
- Library: [Font Awesome / Material Icons / Heroicons / SVG sprites / Custom / None]
- Location: [file:line where icons imported/defined]
- Usage pattern: [<i class="..."> / <Icon name="..."> / <svg><use href="...">]
- Sizing: [classes or conventions]
- Examples: [file:line references to icon usage]

### Similar Features
- [Feature 1]: [path] - [how it's structured]
- [Feature 2]: [path] - [how it's structured]

### Patterns to Follow
1. [Pattern from research]
2. [Pattern from research]
```

## Clarifying questions

Step 3 — ask these, then **wait** for answers before creating anything.

```
Based on my research of the existing UI, I have some questions:

**Scope & Purpose**
1. What problem does this [feature] solve for users?
2. Who is the primary user of this feature?

**Content & Data**
3. What information needs to be displayed?
4. What actions can users take?
5. Are there states to handle? (empty, loading, error, success)

**Placement & Flow**
6. Where does this fit in the navigation?
7. What triggers this UI to appear?
8. Where does the user go after completing this?

**Constraints**
9. Any technical constraints I should know about?
10. Mobile support required?

Please answer what you can - we can iterate on unknowns.
```

## mockup.md

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

## decisions.md

Step 5 — `mockups/v00N/decisions.md`.

```markdown
---
version: 1
created: [YYYY-MM-DD]
---

# v001 Decisions

## Choices Made

### Layout Choice
- **Decision**: [what was chosen]
- **Rationale**: [why, referencing research]
- **Alternative considered**: [what else could work]

### Component Choices
- **Decision**: Use [component] for [purpose]
- **Rationale**: Matches existing pattern at [file:line]

## Based On Research

- Layout follows pattern from [similar feature]
- Components reused from [library location]
- Styling matches [existing page]

## Assumptions

1. [Assumption made due to unclear requirement]
2. [Assumption about user behavior]

## Needs Validation

- [ ] [Thing to verify with user/stakeholder]
- [ ] [Technical feasibility question]
```

## mockup.html

Step 6 — `mockups/v00N/mockup.html`. Every class must come from research; no placeholders.

`````html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mockup: [Feature Name] v001</title>

  <!-- Import app's styles based on research -->
  <!-- If using Tailwind: -->
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- If using app's CSS files (adjust paths): -->
  <!-- <link rel="stylesheet" href="../../src/styles/main.css"> -->

  <!-- If using icon library from research: -->
  <!-- Font Awesome example: -->
  <!-- <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"> -->

  <!-- Material Icons example: -->
  <!-- <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons"> -->

  <style>
    /* Add any custom styles needed to match app exactly */
    /* Copy from discovered theme/color tokens */
  </style>
</head>
<body class="[discovered body classes from research]">

  <!-- Header/Navigation - copy structure from research file:line -->
  <header class="[actual header classes from app]">
    <!-- Use actual nav structure from research -->
  </header>

  <!-- Main content area -->
  <main class="[layout classes from research]">

    <!-- Feature mockup using real component HTML -->
    <div class="[container classes from research]">

      <h1 class="[heading classes from research]">
        <!-- Icon if system found: -->
        <!-- <i class="fa-solid fa-[icon-name]"></i> -->
        [Feature Title]
      </h1>

      <!-- Content sections matching ASCII diagram -->

      <!-- Buttons using app's actual button HTML -->
      <div class="[button container classes]">
        <button class="[primary button classes from research]">
          <!-- Icon if used in app: -->
          <!-- <i class="fa-solid fa-save"></i> -->
          Primary Action
        </button>
        <button class="[secondary button classes from research]">
          Secondary Action
        </button>
      </div>

    </div>

  </main>

  <!-- Footer if app has one -->

</body>
</html>
`````

## mockup-log.md

Step 8 — `mockups/mockup-log.md`, created once and updated by each iteration.

```markdown
---
feature: [feature name]
created: [YYYY-MM-DD]
current_version: 1
status: iterating
project_directory: [full path to project directory]
last_updated: [YYYY-MM-DD]
---

# Mockup Iteration Log

## Feature: [Name]

**Goal**: [From clarifying questions]

## Version History

### v001 - [YYYY-MM-DD] - Initial Draft
- **Status**: In Review
- **Key decisions**: [brief summary]
- **Feedback needed**: [what to validate]

## UI Research Reference

_From initial research - apply to all versions:_

- **Layout pattern**: [pattern from research]
- **Component library**: [location]
- **Styling system**: [approach]
- **Icon system**: [library and usage pattern, or "None - text only"]
- **Similar features**: [references]

## Running Requirements

### Confirmed (KEEP)
_Requirements confirmed through iteration_

### Rejected (REMOVE)
_Ideas explored and rejected with rationale_

### Open (DECIDING)
_Still being discussed. Cite the `UIQ` IDs from the current version's mockup.md rather than
restating the questions._

## Design Principles Emerging

1. [Principle discovered through iteration]
```

## Presentation message

Step 9 — emitted once, after the package is complete.

```
Initial mockup created!

Location: [project-dir]/mockups/v001/

**What I created based on research:**
- Layout following [pattern] from [similar feature]
- Using components: [list with file:line]
- Styling: [CSS approach from research]
- Icons: [icon system from research, or text-only]

**Files created:**
- mockup.md - ASCII structure and specifications
- mockup.html - Working HTML with app's actual styles
- decisions.md - Rationale for design choices
- preview-v001.png - Visual screenshot

**Key decisions made:**
1. [Decision 1] - because [rationale from research]
2. [Decision 2] - because [rationale from research]

**Open questions:**
[UIQ IDs and one line each, from mockup.md's Open Questions table — or "none"]

**Next steps:**
- Review the visual preview above
- Open mockups/v001/mockup.html in browser to interact
- Review mockups/v001/mockup.md for structure details
- Provide feedback - just discuss what to keep, change, or remove
- Each iteration will update both ASCII and HTML with decisions captured

Ready to iterate? Just tell me what to keep, change, or remove.
```
