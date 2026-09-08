---
description: Research UI patterns and create initial mockup with clarifying questions
argument-hint: "[project-directory] [feature-description]"
---

# Create Mockup

Researches existing UI patterns, styles, and layouts, then creates an initial mockup iteration through interactive discussion. Follows the "research what EXISTS" philosophy before proposing changes.

## Purpose

This command:

- Documents current UI patterns and styles (research phase)
- Asks clarifying questions about the desired feature
- Creates a versioned mockup with rationale
- Sets up iteration tracking for refinement

## Initial Response

When invoked, check for arguments:

1. **If directory and feature provided** (e.g., `/create_mockup docs/plans/2025-01-08-dashboard/ "user settings panel"`):
   - Use `$1` as project directory
   - Use `$2+` as feature description
   - Begin research immediately

2. **If no arguments**:

   ```
   I'll help you create a UI mockup. Please provide:
   1. Path to the project documentation directory
   2. Brief description of what you want to mockup

   I'll research existing patterns first, then we'll discuss the design together.
   ```

## Process Steps

### Step 1: Research Existing UI

**⛔⛔⛔ BARRIER 1: STOP! Research current UI patterns before proposing anything ⛔⛔⛔**

Spawn parallel agents to document what EXISTS:

```javascript
// Agent 1: Layout Patterns
Task({
  description: "Research UI layouts",
  prompt: `You are documenting the codebase UI as it exists.

Find and document:
- Page layout patterns (grid, flex, containers)
- Navigation structure
- Content area organization
- Responsive breakpoints

Return with file:line references. DO NOT suggest improvements.`,
  subagent_type: "codebase-analyzer",
  model: "haiku"
})

// Agent 2: Component Library
Task({
  description: "Research UI components",
  prompt: `You are documenting the codebase UI as it exists.

Find and document:
- Existing component library (buttons, forms, cards, modals)
- Component naming conventions
- Props/API patterns
- Where components are defined

Return with file:line references. DO NOT suggest improvements.`,
  subagent_type: "codebase-analyzer",
  model: "haiku"
})

// Agent 3: Styling Patterns
Task({
  description: "Research styling approach",
  prompt: `You are documenting the codebase styling as it exists.

Find and document:
- CSS approach (CSS modules, Tailwind, styled-components, etc.)
- Color tokens/variables
- Typography scale
- Spacing system
- Theme configuration

Return with file:line references. DO NOT suggest improvements.`,
  subagent_type: "codebase-analyzer",
  model: "haiku"
})

// Agent 4: Similar Features
Task({
  description: "Find similar UI features",
  prompt: `You are documenting similar features in the codebase.

Find examples of:
- Similar panels/modals/pages to [feature description]
- How similar features are structured
- Patterns for [feature type] in this codebase

Return with file:line references. DO NOT suggest improvements.`,
  subagent_type: "pattern-finder",
  model: "haiku"
})

// Agent 5: Icon System
Task({
  description: "Research icon system",
  prompt: `You are documenting the icon system as it exists.

Find and document:
- Icon library used (Font Awesome, Material Icons, Heroicons, SVG sprites, custom, etc.)
- Where icons are defined/imported (file:line references)
- How icons are referenced in components (class names, components, imports)
- Icon sizing and color conventions
- Examples of icon usage with file:line references
- Pattern for icons in buttons, headers, navigation

Return exact patterns found. If NO icon system exists, state that clearly.
DO NOT suggest adding an icon library if none exists.`,
  subagent_type: "codebase-analyzer",
  model: "haiku"
})
```

**⛔ BARRIER 2**: Wait for ALL agents to complete before proceeding.

### Step 2: Synthesize Research

Create a UI research summary:

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

### Step 3: Clarifying Questions

**think deeply about what information is needed**

Before creating mockup, ask clarifying questions:

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

Wait for user responses before proceeding.

### Step 4: Create Mockup Directory

Set up versioned mockup structure:

```
[project-dir]/mockups/
├── mockup-log.md          # Decision log across versions
├── v001/
│   ├── mockup.md          # ASCII structure and specs
│   ├── mockup.html        # Working HTML with app styles
│   ├── preview-v001.png   # Visual screenshot
│   └── decisions.md       # Rationale for this version
├── v002/
│   ├── mockup.md
│   ├── mockup.html
│   ├── preview-v002.png
│   └── decisions.md
└── ...
```

### Step 5: Create Initial Mockup (v001)

**⛔ BARRIER 3**: No placeholders - all content must be specific based on research + answers.

Create `mockups/v001/mockup.md`:

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

**If no icon system found but icons needed:**
Create beads issue: `bd create "UI Q: Icon system?" --type=task --priority=2 -d "Mockup needs icons but no system found. Options: add library, use text only, custom SVG"`

## Open Questions

UI questions are tracked in beads, NOT in this document.

**To add a UI question**:

```bash
bd create "UI Q: [your question]" --type=task --priority=2 \
  -d "From mockup v[version]. Blocks: [what can't proceed without answer]"
# → Returns issue ID (e.g., prompts-abc)
```

**Active questions** (reference only, beads is source of truth):

Use `bd list --status=open | grep "UI Q:"` to see all open UI questions, or reference by ID:
- `[id]`: [Brief question summary] - blocks finalization
- `[id]`: [Brief question summary] - blocks [what it blocks]

To see full question details: `bd show [id]`
````

Create `mockups/v001/decisions.md`:

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

### Step 6: Create HTML Mockup with App Styles

**⛔ BARRIER 4**: After ASCII mockup created, generate working HTML mockup with real app styles.

Create `mockups/v001/mockup.html`:

**Critical requirements:**

1. **Import app's actual stylesheets** based on research
2. **Use discovered component HTML patterns** (copy structure from file:line references)
3. **Apply actual CSS classes/tokens** from research (no placeholder classes)
4. **Follow icon system** from research (Font Awesome, Material Icons, etc.) or text-only if none
5. **Match layout structure** from ASCII diagram
6. **Standalone file** - can be opened directly in browser

**Template structure:**

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

**Icon handling based on research:**

- **If Font Awesome found**: Use `<i class="fa-[style] fa-[name]"></i>` pattern
- **If Material Icons found**: Use `<span class="material-icons">[name]</span>` pattern
- **If SVG sprites found**: Use `<svg><use href="#icon-[name]"></use></svg>` pattern
- **If custom icon components**: Document pattern and ask user how to mock
- **If NO icon system found**: Use text only, create beads issue if icons needed

**Quality checks before proceeding:**

- [ ] All CSS classes are from research (no placeholder classes)
- [ ] Icon system matches research (or confirmed text-only)
- [ ] Layout structure matches ASCII diagram
- [ ] Can be opened in browser without errors
- [ ] Styling approach matches research (Tailwind/CSS modules/etc)

### Step 7: Visual Validation with Playwright

**⛔ BARRIER 5**: Validate HTML mockup visually before presenting to user.

Use Playwright to preview the mockup:

1. **Navigate to mockup**:
   - Get absolute path to mockup.html
   - Open in browser: `file:///[absolute-path]/mockups/v001/mockup.html`

2. **Take full page screenshot**:
   - Capture entire mockup
   - Save as `mockups/v001/preview-v001.png`

3. **Present visual preview to user**:

```
Visual preview of mockup v001:

[Show preview-v001.png]

Does this match your app's visual style?
- Colors match app theme? [Y/N]
- Spacing looks consistent? [Y/N]
- Typography matches app? [Y/N]
- Icons follow app pattern? [Y/N] (or text-only confirmed)
- Layout structure correct? [Y/N]

If anything looks off, let me know and I'll adjust.
```

1. **If similar feature found in research**:
   - Offer to navigate to similar page for comparison
   - Take screenshot of existing feature
   - Show side-by-side comparison

**Wait for user feedback before proceeding to Step 8.**

### Step 8: Initialize Mockup Log

Create `mockups/mockup-log.md`:

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
_Still being discussed_

## Design Principles Emerging

1. [Principle discovered through iteration]
```

### Step 9: Present for Iteration

Present the complete mockup package to user:

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
[List any beads issues created for UI questions]

**Next steps:**
- Review the visual preview above
- Open mockups/v001/mockup.html in browser to interact
- Review mockups/v001/mockup.md for structure details
- Provide feedback - just discuss what to keep, change, or remove
- Each iteration will update both ASCII and HTML with decisions captured

Ready to iterate? Just tell me what to keep, change, or remove.
```

## Output Files

| File | Purpose |
| ------ | --------- |
| `mockups/mockup-log.md` | Track all versions and running requirements |
| `mockups/v001/mockup.md` | ASCII structure and specifications |
| `mockups/v001/mockup.html` | Working HTML mockup with app's actual styles |
| `mockups/v001/decisions.md` | Rationale for this version |
| `mockups/v001/preview-v001.png` | Visual screenshot of HTML mockup |

## Important Guidelines

### Research First

- ALWAYS research existing UI before proposing
- Reference specific file:line locations
- Follow established patterns unless explicitly breaking them

### Clarifying Questions

- Ask before assuming
- Understand the WHY not just the WHAT
- Identify constraints early

### Versioning

- Never overwrite - always create new version
- Document what changed and why
- Keep decision trail for design.md

### Fidelity

- ASCII mockups for layout structure discussion
- HTML mockups with app's actual styles for visual validation
- Component specs for implementation detail (copied from research)
- Icon system from research (no placeholder icons/emojis)
- State documentation for edge cases
- Visual screenshots for design approval

## Relationship to Other Commands

**Typical workflow:**

1. `/wb:create_research` - Understand the codebase
2. **`/wb:create_mockup`** - Research UI + create initial mockup
3. [Iterate with mockup-iteration skill]
4. `/wb:create_design` - Finalize design from mockup decisions
5. `/wb:create_execution` - Plan implementation

The mockup process feeds into design.md with validated requirements.
