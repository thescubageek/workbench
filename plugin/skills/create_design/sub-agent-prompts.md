# create_design — sub-agent prompts

Read this when Step 2 directs you to. All three spawn together, in parallel — read the file
whole. Use the prompts verbatim, substituting the bracketed placeholders from research.md.

**Sub-agents are READ-ONLY** — they return findings only; YOU write `design.md` after
synthesizing.

## Agent 1: Verify design patterns

```javascript
Task({
  description: "Verify design patterns",
  prompt: `Based on the research findings, identify architectural patterns we should follow.

  From research.md:
  - [Key patterns found in research]
  - [Conventions observed]
  - [Integration points]

  Find:
  - Similar features already implemented
  - Patterns we should follow for consistency
  - Anti-patterns to avoid

  Document what exists, do not evaluate quality.
  Return findings only; write nothing.`,
  subagent_type: "pattern-finder",
  model: "haiku"
})
```

## Agent 2: Analyze integration points

```javascript
Task({
  description: "Analyze integration points",
  prompt: `Analyze how our design will integrate with existing systems.

  From research.md:
  - [Current architecture]
  - [Integration patterns]

  Identify:
  - Required integration points
  - API contracts we must respect
  - Dependencies we'll have
  - Potential conflicts

  Return findings only; write nothing.`,
  subagent_type: "codebase-analyzer",
  model: "sonnet"
})
```

## Agent 3: Find risk precedents

```javascript
Task({
  description: "Find risk precedents",
  prompt: `Search for similar changes in the codebase history.

  Look for:
  - Previous similar implementations
  - Issues encountered
  - Solutions that worked
  - Patterns that failed

  Return findings only; write nothing.`,
  subagent_type: "pattern-finder",
  model: "haiku"
})
```

Spawn all three concurrently.
