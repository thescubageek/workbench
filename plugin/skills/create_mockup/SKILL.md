---
name: create_mockup
description: Research UI patterns and create initial mockup with clarifying questions
argument-hint: "[project-directory] [feature-description]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Create Mockup

Researches existing UI patterns, styles, and layouts, then creates an initial mockup iteration through interactive discussion. Follows the "research what EXISTS" philosophy before proposing changes.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- [sub-agent-prompts.md](sub-agent-prompts.md) — the five Step 1 UI research agents
- `templates/` — one file per output shape: [ui-research-summary.md](templates/ui-research-summary.md) (Step 2) · [clarifying-questions.md](templates/clarifying-questions.md) (Step 3) · [mockup-md.md](templates/mockup-md.md) and [decisions-md.md](templates/decisions-md.md) (Step 5) · [mockup-html.md](templates/mockup-html.md) (Step 6) · [mockup-log-md.md](templates/mockup-log-md.md) (Step 8) · [presentation-message.md](templates/presentation-message.md) (Step 9)
- [reference.md](reference.md) — purpose, output files, guidelines, icon handling, HTML quality checks, workflow position

**If a directed read fails, stop — do not continue from memory.** These files live outside your
project, so a read can be refused. Say which file was refused, that reads outside the working
directory are gated, and that the fix is to allow the read once or to relaunch with
`--add-dir <plugin-path>`. Do not route around a refusal with `cat`.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If directory and feature provided** (e.g., `/wb:create_mockup docs/plans/2025-01-08-dashboard/ "user settings panel"`):
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

Read [sub-agent-prompts.md](sub-agent-prompts.md) NOW and spawn the five agents it defines, concurrently. They document layout, components, styling, similar features, and the icon system — all as they exist.

**Skip the fan-out only if you have already read the entire relevant surface in this context** —
every file the agents would open, not a sample. Having read *some* of it, a cross-cutting change,
or uncertainty about which files are relevant are each a reason to spawn, not to skip. **If you
skip, say so in your output and say why**, naming what you read instead.

**⛔ BARRIER 2**: Wait for ALL agents to complete before proceeding.

This barrier governs *waiting*, not spawning — synthesis on a partial set misses what the missing
report would have changed. A fan-out skipped under the rule above satisfies it trivially.

### Step 2: Synthesize Research

Read [templates/ui-research-summary.md](templates/ui-research-summary.md) NOW and write the summary in that shape.

### Step 3: Clarifying Questions

**Identify what information is missing before anything is drawn**

Read [templates/clarifying-questions.md](templates/clarifying-questions.md) NOW and ask them.

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

Read [templates/mockup-md.md](templates/mockup-md.md) NOW and create `mockups/v001/mockup.md`. Then read [templates/decisions-md.md](templates/decisions-md.md) and create `mockups/v001/decisions.md`.

One thing in the mockup template is load-bearing rather than cosmetic: **UI questions live in
that document, as a table with local `UIQ` IDs**. There is no external tracker. A question earns
a row only if it blocks finalization, the IDs carry across versions so you can see how long one
stayed open, and resolving a question edits its row rather than deleting it.

### Step 6: Create HTML Mockup with App Styles

**⛔ BARRIER 4**: After ASCII mockup created, generate working HTML mockup with real app styles.

Read [templates/mockup-html.md](templates/mockup-html.md) NOW and create `mockups/v001/mockup.html`.

**Critical requirements:**

1. **Import app's actual stylesheets** based on research
2. **Use discovered component HTML patterns** (copy structure from file:line references)
3. **Apply actual CSS classes/tokens** from research (no placeholder classes)
4. **Follow icon system** from research, or text-only if none — see [reference.md](reference.md) → Icon handling
5. **Match layout structure** from ASCII diagram
6. **Standalone file** - can be opened directly in browser

Run the quality checks in [reference.md](reference.md) before proceeding.

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

Read [templates/mockup-log-md.md](templates/mockup-log-md.md) NOW and create `mockups/mockup-log.md`.

### Step 9: Present for Iteration

Read [templates/presentation-message.md](templates/presentation-message.md) NOW and present it.

## Important Guidelines

See [reference.md](reference.md) — purpose, output files, research-first discipline, versioning, fidelity, icon handling, the HTML quality checks, and this skill's place in the workflow.
