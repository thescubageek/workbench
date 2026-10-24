# create_tasks — sub-agent prompts

Read this when Step 2 directs you to. All three agents spawn together, in parallel. Read the
file whole. Use the prompts verbatim, and substitute the bracketed placeholders from
research.md and design.md.

## Agent 1: Analyze file dependencies

```javascript
Task({
  description: "Analyze file dependencies",
  prompt: `Analyze dependencies for implementing the design.

  From research.md:
  - Current file structure: [key files]
  - Integration points: [systems]

  From design.md:
  - Target architecture: [approach]
  - Components to build: [list]

  Determine:
  - Build order (what must be done first)
  - Parallel work opportunities
  - Critical path dependencies
  - External dependencies needed

  Return findings only; write nothing.`,
  subagent_type: "wb:codebase-analyzer"
})
```

## Agent 2: Identify test coverage needs

```javascript
Task({
  description: "Identify test coverage needs",
  prompt: `Identify testing requirements for the implementation.

  From design.md:
  - Success criteria: [criteria]
  - Risk areas: [risks]

  From research.md:
  - Existing test patterns: [patterns]
  - Test frameworks in use: [frameworks]

  Determine:
  - Unit tests needed (with file:line for each component)
  - Integration tests required
  - Edge cases from risk analysis
  - Test fixtures needed

  Return findings only; write nothing.`,
  subagent_type: "wb:codebase-analyzer"
})
```

## Agent 3: Find similar implementation patterns

```javascript
Task({
  description: "Find similar implementation patterns",
  prompt: `Find examples of similar implementations in the codebase.

  From design.md:
  - Type of change: [type]
  - Components affected: [components]

  Search for:
  - Similar features already implemented
  - Phased rollout patterns used
  - Testing approaches for similar changes
  - Configuration patterns to follow

  Return findings only; write nothing.`,
  subagent_type: "wb:pattern-finder"
})
```

Spawn all three concurrently.
