# create_mockup — sub-agent prompts

Read this when Step 1 directs you to. All five spawn together, in parallel — read the file
whole. Every one of them documents what **exists**; none proposes changes.

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

**Sub-agents are READ-ONLY** — they return findings only; YOU write the research summary and
the mockup after synthesizing.
