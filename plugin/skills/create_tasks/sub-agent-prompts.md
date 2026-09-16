# create_tasks — sub-agent prompts

Read this when Step 2 directs you to. All three spawn together, in parallel — read the file
whole. Use the prompts verbatim, substituting the bracketed placeholders from research.md and
design.md.

**Sub-agents are READ-ONLY** — they return findings only; YOU write `tasks.md` after
synthesizing.

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
  subagent_type: "codebase-analyzer",
  model: "sonnet"
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
  subagent_type: "codebase-analyzer",
  model: "sonnet"
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
  subagent_type: "pattern-finder",
  model: "haiku"
})
```

Spawn all three concurrently.
