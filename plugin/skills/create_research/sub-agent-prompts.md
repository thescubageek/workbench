# create_research — sub-agent prompts

Read this when Step 4 directs you to. Use these prompts verbatim. Substitute the bracketed
placeholders. Never paraphrase them from memory.

## Parallel Research Strategy

Announce the fan-out in this shape:

```
## Parallel Research Strategy

Based on the research question "[research-question]", I'll spawn specialized agents to investigate:

1. **Locating Components** - Finding where features are implemented
2. **Analyzing Implementation** - Understanding how code works
3. **Finding Patterns** - Identifying conventions and similar implementations
```

## Agent Spawning Examples

**Agent 1: Component Locator**

```javascript
Task({
  description: "Find [feature] components",
  prompt: `Find all files related to [feature].

  Search for:
  - Source files implementing [feature]
  - Test files for [feature]
  - Configuration files
  - Related documentation

  Focus on [specific directories if known].
  Return findings only; write nothing.`,
  subagent_type: "wb:codebase-locator"
})
```

**Agent 2: Implementation Analyzer**

```javascript
Task({
  description: "Analyze [feature] implementation",
  prompt: `Document the codebase as it exists, with file:line references. Describe how
  it currently works, with no improvements and no issue-spotting. Return findings only;
  write nothing.

  Understand how [feature] works. Analyze:
  - Entry points and main functions
  - Data flow through the system
  - Key algorithms and logic
  - Error handling approaches

  Start with [specific files if known].`,
  subagent_type: "wb:codebase-analyzer"
})
```

**Agent 3: Pattern Finder**

```javascript
Task({
  description: "Find [pattern] examples",
  prompt: `Identify [pattern type] in the codebase.

  Find:
  - Similar implementations to [feature]
  - Naming conventions for [component type]
  - Common patterns for [functionality]
  - Testing approaches for [feature type]

  Return findings only; write nothing.`,
  subagent_type: "wb:pattern-finder"
})
```

**Additional specialized agents** based on research focus:

- Database schema investigation
- API endpoint analysis
- Frontend component exploration
- Configuration and environment analysis
- Testing pattern discovery

The three typed agents above carry the documentarian constraint in their own definitions.
An ad-hoc `general-purpose` agent does **not** carry it. So when you spawn a one-off researcher,
put the documentarian constraint in the spawning prompt explicitly.

## Parallel Execution

```javascript
// Spawn multiple agents concurrently:
const agents = [
  componentLocator,
  implementationAnalyzer,
  patternFinder,
  // Add more as needed
];

// All agents work in parallel for efficiency
```
