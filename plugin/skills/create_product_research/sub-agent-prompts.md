# create_product_research — sub-agent prompts

Read this when Step 4 or Step 7 directs you to. Use these prompts verbatim, substituting the
bracketed placeholders. Never paraphrase them from memory.

**Sub-agents are READ-ONLY** — they return findings only; YOU write `product-research.md`
after synthesizing.

## Parallel Research Strategy

Announce the fan-out in this shape:

```
## Parallel Research Strategy

Based on the research question "[research-question]", I'll spawn specialized agents to investigate:

1. **Locating Components** - Finding where features are implemented
2. **Analyzing Product Behaviors** - Understanding what the software does
3. **Finding Patterns** - Identifying conventions and engineering approach
```

### Agent 1: Component Locator

```javascript
Task({
  description: "Find [feature] components",
  prompt: `Find all files related to [feature].

  Search for:
  - Source files implementing [feature]
  - Test files for [feature]
  - Configuration files
  - UI components, routes, API endpoints
  - Related documentation

  Focus on [specific directories if known].
  Return findings only; write nothing.`,
  subagent_type: "codebase-locator",
  model: "haiku"
})
```

### Agent 2: Product Behavior Analyzer

```javascript
Task({
  description: "Analyze [feature] product behaviors",
  prompt: `Document the codebase as it exists, for a product manager — explain as
  PRODUCT BEHAVIORS, not code; document what IS, not what SHOULD BE; no
  improvements or issue-spotting. Include file:line references for EVERY
  behavioral claim; trace actual code, do not guess. Return findings only; write nothing.

  Understand what [feature] does from a product perspective. Analyze:
  - What user-visible behaviors does this feature provide?
  - What are the user flows (step by step, in plain language)?
  - What data does the user provide, and what do they see?
  - What happens when things go wrong (error states)?
  - What configuration controls this feature's behavior?

  Start with [specific files if known].`,
  subagent_type: "product-behavior-analyzer",
  model: "sonnet"
})
```

### Agent 3: Pattern Finder

```javascript
Task({
  description: "Find engineering patterns and conventions",
  prompt: `Identify coding patterns and engineering conventions in the codebase.

  Find:
  - Naming conventions used
  - Architecture patterns (MVC, microservices, etc.)
  - How similar features are typically built
  - Testing approach and coverage patterns
  - Error handling conventions
  - Configuration management approach

  Summarize at a HIGH LEVEL suitable for a product manager to understand the engineering approach, not the engineering details.

  REMEMBER: Document what IS, not what SHOULD BE. No recommendations.

  Return findings only; write nothing.`,
  subagent_type: "pattern-finder",
  model: "haiku"
})
```

**Additional specialized agents** based on research focus:

- API endpoint analysis (what endpoints exist, what they do)
- Database/data model investigation (what data is stored)
- Frontend component exploration (what the user sees)
- Integration/third-party service analysis

The three typed agents above carry their constraints in their own definitions. An ad-hoc
`general-purpose` agent does **not** — so when you spawn a one-off researcher, the
documentarian constraint and the file:line requirement go in the spawning prompt explicitly.

### Parallel Execution

Spawn all agents concurrently for efficiency. Each returns a report; none write files.

## The validation agent (Step 7)

Spawn this **after** `product-research.md` is written. The validator reads the written file
directly — no need to pass findings in context.

```javascript
Task({
  description: "Validate product research document",
  prompt: `Validate the research document at [project-dir]/product-research.md against the actual codebase.

  Read the document fully, then check:
  1. All file paths mentioned exist
  2. All code snippets match actual file content
  3. All behavioral claims ("when X, system does Y") can be traced through code
  4. All pattern claims are accurate

  Return a structured validation report with PASS/FAIL/UNCERTAIN per claim.
  DO NOT modify the document. Only report findings.`,
  subagent_type: "research-validator",
  model: "sonnet"
})
```
