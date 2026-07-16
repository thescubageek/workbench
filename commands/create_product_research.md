---
description: Research codebase from a product perspective - features, user flows, behaviors, and patterns
argument-hint: "[project-directory] [research-question]"
---

# Generate Product Research Document

Conducts comprehensive codebase research and documents findings from a **product manager's perspective** by spawning specialized agents to work in parallel. Produces a three-layer document: product overview, engineering approach, and technical appendix.

## Documentarian Rule

```
DOCUMENT WHAT EXISTS — NEVER SUGGEST, CRITIQUE, OR IMPROVE
```

Describe the code as it is: no recommendations, issue-spotting, enhancements,
critiques, or root-cause analysis unless explicitly asked. You are a
documentarian, not an evaluator.

**Output discipline**: act on barriers silently; don't restate the plan between
steps; emit only the artifact and a one-line completion summary.

## Audience: Product Managers

Your output is for someone who manages the product, not someone who writes the code. This means:

- Explain features as user-visible behaviors, not implementation details
- Describe flows as user journeys, not code paths
- Group findings by product capability, not by file or module
- Use plain language — no engineering jargon unless it's a user-facing term
- Include technical references as backing evidence in an appendix, not inline

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:create_product_research docs/plans/2025-01-08-auth/`):
   - Use `$1` as the project directory
   - If `$2+` exists, use as research question
   - Otherwise, prompt for research focus

2. **If no arguments**:

   ```
   I'm ready to research the codebase from a product perspective. Please provide:
   1. Path to the project documentation directory
   2. Your research question or area of interest

   Example: /wb:create_product_research docs/plans/2025-01-08-auth/
   Then: "Research how user authentication works from a product perspective"
   ```

## Workflow Position

This command can be used in two ways:

1. **Within the wb pipeline**: After `/create_project` creates the directory structure. The `product-research.md` file will be created alongside `research.md` — they serve different audiences for the same project.

2. **Standalone**: A PM can run this without `/create_project`. If the directory exists but `product-research.md` doesn't, create it fresh. If the directory doesn't exist, create it.

## Steps to Execute After Receiving the Research Query

### Step 1: Read Any Directly Mentioned Files First (CRITICAL)

- If the user mentions specific files (docs, JSON, configs), read them FULLY first
- **IMPORTANT**: Use the Read tool WITHOUT limit/offset parameters to read entire files
- **CRITICAL**: Read these files yourself in the main context before spawning any sub-tasks
- This ensures you have full context before decomposing the research

**⛔⛔⛔ BARRIER 1: STOP! Do NOT proceed to Step 2 until ALL mentioned files are FULLY read ⛔⛔⛔**

### Step 2: Validate Project Structure

- Check that the specified directory exists; if not, create it
- Check if product-research.md exists (may be a follow-up)
- If it exists, read it FULLY to see what's already documented
- Check frontmatter status field

### Step 3: Decompose Research Question in Product Terms

**ultrathink about what the SOFTWARE DOES from the user's perspective**

1. **Break down the user's query into product areas**, not code modules:
   - What features are involved? What does the user see and do?
   - What user flows touch this area? What's the happy path? Error paths?
   - What data moves through the system? What does the user provide and receive?
   - What integrations or external services are involved?
   - What configuration controls behavior? What can be changed without code?

2. **ultrathink about:**
   - The user-visible surface of this feature — screens, APIs, messages, states
   - How this feature connects to adjacent features the user also touches
   - What a PM needs to know to make decisions about this area
   - Which parts of the codebase actually implement user-facing behavior

3. **Identify research areas** to investigate:
   - User-facing features and capabilities
   - User flows (happy path and error paths)
   - Data involved (what's collected, stored, displayed)
   - Configuration that affects product behavior
   - Integration points with other systems
   - Error states and recovery paths

4. **Consider which specific components** to investigate

### Step 4: Spawn Parallel Research Agents

Create multiple agents to research different aspects concurrently:

**Sub-agents are READ-ONLY** — they return findings only; YOU write `product-research.md` after synthesizing.

```
## Parallel Research Strategy

Based on the research question "[research-question]", I'll spawn specialized agents to investigate:

1. **Locating Components** - Finding where features are implemented
2. **Analyzing Product Behaviors** - Understanding what the software does
3. **Finding Patterns** - Identifying conventions and engineering approach
```

#### Agent 1: Component Locator

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

#### Agent 2: Product Behavior Analyzer

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

#### Agent 3: Pattern Finder

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

#### Parallel Execution

Spawn all agents concurrently for efficiency. Each returns a report; none write files.

**CRITICAL Agent Instructions (MUST follow exactly):**

- **Each agent describes what the software does, NOT how the code works**
- **Agents MUST describe what exists without ANY judgment**
- **Agents MUST include file:line references for every claim**
- **Use specific agent types for their strengths**
- **Run multiple agents in parallel for speed**
- **ALWAYS wait for ALL agents before synthesizing**
- **Remind EVERY agent: You are documenting the codebase AS IT EXISTS**

**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL sub-agents to complete — DO NOT proceed until EVERY agent returns ⛔⛔⛔**

### Step 5: Synthesize Findings into Three Layers

**ultrathink about documenting ONLY what EXISTS, in product language**

**IMPORTANT**: Wait for ALL sub-agent tasks to complete before proceeding

1. **Compile all sub-agent results**
2. **Prioritize live codebase findings** as primary source of truth
3. **Connect findings across different components**
4. **Answer the user's specific questions** with concrete evidence FROM THE CURRENT CODE
5. **DO NOT add recommendations or improvements unless explicitly requested**
6. **Organize into three layers**:

**Layer 1 — Product Overview** (the PM reads this):

- Feature overview in plain language
- User flows as numbered narratives
- Product behaviors: "when X, system does Y"
- Data involvement: what data, where it flows
- Error states as user-visible outcomes
- Integration points as capabilities

**Layer 2 — Engineering Approach** (pattern tracking):

- Coding patterns observed (naming, structure, organization)
- Architecture style notes
- Testing approach characterization
- Technology choices relevant to product decisions

**Layer 3 — Technical Appendix** (credibility backing):

- File references grouped by feature area
- Key code snippets for engineering conversations
- Configuration values that affect behavior

### Step 6: Write Product Research Document

Write the product-research.md file. **Keep the main agent focused on synthesis — sub-agents already did the deep file reading.**

````markdown
---
project: [from existing frontmatter or research question]
created: [YYYY-MM-DD]
status: complete
audience: product
last_updated: [YYYY-MM-DD]
validation_status: not-yet-run
---

# Product Research: [Feature/Area Name]

**Created**: [YYYY-MM-DD]
**Last Updated**: [YYYY-MM-DD]
**Audience**: Product Management

## Feature Overview

[2-3 paragraph plain-language description of what this feature/area does. Written so a PM can understand the product capability without reading code.]

## User Flows

### [Flow Name] (e.g., "User Creates an Account")

1. User [action in plain language]
2. System [validates/processes/responds]
3. If [condition], then [outcome A]; otherwise [outcome B]
4. User sees [result]

**Success outcome**: [what the user experiences when everything works]
**Error outcomes**:

- [Error condition]: [what the user sees]
- [Error condition]: [what the user sees]

### [Additional flows...]

## Product Behaviors

### [Behavior Area]

| Trigger | What Happens | Configurable? |
|---------|-------------|---------------|
| [user action or event] | [system behavior in plain language] | [yes — setting name / no] |

### [Additional behavior areas...]

## Data & Integration

### What Data Is Involved

- **User provides**: [input data in business terms]
- **System stores**: [what's persisted and why]
- **User sees**: [output/display data]

### How It Connects to Other Features

- **[Feature/Service]**: [what the integration enables]
- **[External System]**: [what data flows between them]

### Configuration That Affects Behavior

| Setting | What It Controls | Default |
|---------|-----------------|---------|
| [setting name] | [plain-language description] | [value] |

## Engineering Approach

### Coding Patterns

- **[Pattern name]**: [1-sentence description of the convention]
  - Used in: [where this pattern appears]

### Architecture Style

- [High-level observation about how the codebase is organized]
- [Technology choices relevant to product decisions]

### Testing Approach

- [How this feature is tested — unit, integration, e2e]
- [Coverage level observation]

## Technical Appendix

### File References

**[Feature Area 1]**:

- `path/to/main/implementation/` — [what it handles in product terms]
- `path/to/tests/` — [test coverage for this area]

**[Feature Area 2]**:

- `path/to/files/` — [what it handles]

### Key Code (for engineering discussions)

```language
// From path/to/file.ext:NN-MM
// [Brief description of what this code does in product terms]
[actual code snippet]
```

### Validation Notes

[Any UNCERTAIN claims from validation that need human review]

- [Claim]: [What was verified, what needs manual check]

## Open Questions

Questions requiring resolution are tracked in beads:

```bash
bd create "Q: [your question]" --type=task --priority=2 \
  -d "Product research question. Context: [what this affects]"
```

**Active questions** — use `bd list --status=open` for current list.

## Next Steps

Based on the research findings:

1. [Suggested next action based on findings]
2. [Another logical next step]
3. Review with engineering team for accuracy
4. Run `/wb:create_design` when ready to make design decisions
````

**⛔⛔⛔ BARRIER 3: STOP! Verify NO placeholder values — ALL data MUST be from ACTUAL codebase ⛔⛔⛔**

Before writing:

- **NO** "[To be added]" or similar placeholders
- **NO** generic examples — use REAL data from THIS codebase
- **NO** assumptions — only documented FACTS

### Step 7: Validate the Written Document

**After writing product-research.md, validate it against the codebase.**

The validator reads the written file directly — no need to pass findings in context.

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

**⛔⛔⛔ BARRIER 4: STOP! Wait for validation agent to complete before proceeding ⛔⛔⛔**

After validation returns:

- If **PASS**: Update frontmatter `validation_status: passed`
- If **PASS WITH WARNINGS**: Update frontmatter `validation_status: passed_with_warnings`, add UNCERTAIN items to Validation Notes section
- If **FAIL**: Fix the failing claims by re-checking the code, update the document, re-validate

### Step 8: Handle Follow-Up Questions

If the user has follow-up questions:

1. **DO NOT create a new research file**
2. **Append to the existing product-research.md**
3. **Add new section**: `## Follow-up Research [YYYY-MM-DD HH:MM]`
4. **Update frontmatter**:
   - `last_updated: [YYYY-MM-DD]`
   - Add: `last_updated_note: "Added research on [topic]"`
5. **Spawn new sub-agents** for additional investigation
6. **Re-validate** the new claims after writing
7. **Continue building** on previous findings

### Step 9: Confirm Completion

Emit a one-line summary, not a recap:

```
✅ product-research.md updated — [topic]; validation [PASS/WARN]. Next: /wb:create_design
```

## Important Notes

### Critical Ordering

- **ALWAYS** read mentioned files first before spawning sub-tasks (Step 1)
- **ALWAYS** wait for all sub-agents to complete before synthesizing (Step 4)
- **ALWAYS** write the document before validating (Step 6 before Step 7)
- **ALWAYS** wait for validation before confirming completion (Step 7)
- **NEVER** write the research document with placeholder values

### Documentation Philosophy

- **CRITICAL**: You and all sub-agents are documentarians, not evaluators
- **AUDIENCE**: Product managers — write for them, not for engineers
- **NO RECOMMENDATIONS**: Only describe the current state of the software
- Focus on behaviors, flows, and capabilities over implementation details
- Research documents should be self-contained with all necessary context
- Each sub-agent prompt should be specific and focused on read-only operations
- Document cross-component connections and how systems interact

### File Reading

- **File reading**: Always read mentioned files FULLY (no limit/offset) before spawning sub-tasks
- Have sub-agents document examples and usage patterns as they exist
- Keep the main agent focused on synthesis, not deep file reading
- Sub-agents must include file:line references for all claims

### Three-Layer Output

- **Layer 1 (Product Overview)**: Every PM reads this — must be clear and jargon-free
- **Layer 2 (Engineering Approach)**: PMs read this to understand HOW the team builds — patterns, not details
- **Layer 3 (Technical Appendix)**: PMs reference this when talking to engineers — file paths and snippets

### Validation

- Validation runs AFTER writing the document, reading it directly from file
- FAIL results must be fixed (re-check the code, update document, re-validate)
- UNCERTAIN results are noted in the Validation Notes section for human review
- The `validation_status` frontmatter field tracks overall validation state

## Configuration

The command accepts the directory path as a parameter:

```
/wb:create_product_research docs/plans/2025-10-07-my-project
```

Or prompts for it if not provided.
