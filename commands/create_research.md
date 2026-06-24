---
description: Research codebase using parallel agents to document how things work
argument-hint: [project-directory] [research-question]
---

# Generate Research Document

Conducts comprehensive codebase research and documents findings by spawning specialized agents to work in parallel, gathering detailed information about existing implementation.

## Documentarian Rule

```
DOCUMENT WHAT EXISTS — NEVER SUGGEST, CRITIQUE, OR IMPROVE
```

Describe the code as it is: no recommendations, issue-spotting, enhancements,
critiques, or root-cause analysis unless explicitly asked. You are a
documentarian, not an evaluator.

**Output discipline**: act on barriers silently; don't restate the plan between
steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:create_research docs/plans/2025-01-08-auth/`):
   - Use `$1` as the project directory
   - If `$2+` exists, use as research question
   - Otherwise, prompt for research focus

2. **If no arguments**:

   ```
   I'm ready to research the codebase and document findings. Please provide:
   1. Path to the project documentation directory
   2. Your research question or area of interest

   Example: /wb:create_research docs/plans/2025-01-08-auth/
   Then: "Research how authentication and session management work"
   ```

## Steps to Execute After Receiving the Research Query

### Step 1: Read Any Directly Mentioned Files First (CRITICAL)

- If the user mentions specific files (docs, JSON, configs), read them FULLY first
- **IMPORTANT**: Use the Read tool WITHOUT limit/offset parameters to read entire files
- **CRITICAL**: Read these files yourself in the main context before spawning any sub-tasks
- This ensures you have full context before decomposing the research

**⛔⛔⛔ BARRIER 1: STOP! Do NOT proceed to Step 2 until ALL mentioned files are FULLY read ⛔⛔⛔**

### Step 2: Validate Project Structure

- Check that the specified directory exists
- Verify research.md file exists (created by `/create_project`)
- Read the current research.md FULLY to see what's already documented
- Check frontmatter status field

### Step 3: Analyze and Decompose the Research Question

**think deeply about what EXISTS in the codebase**

1. **Break down the user's query into composable research areas**
2. **Take time to ultrathink about:**
   - Underlying patterns and connections that EXIST
   - Architectural implementations CURRENTLY IN PLACE
   - Which directories, files, or patterns are ACTUALLY PRESENT

3. **Identify research areas** to investigate:
   - Authentication flow (if relevant)
   - User validation points (if relevant)
   - API endpoints (if relevant)
   - Database schema (if relevant)
   - [Other areas specific to the research question]

4. **Consider which specific components** to investigate

### Step 4: Spawn Parallel Research Agents

Create multiple Task agents to research different aspects concurrently using our specialized agents:

**Sub-agents are READ-ONLY** — they return findings only; YOU write `research.md` after synthesizing.

```
## Parallel Research Strategy

Based on the research question "[research-question]", I'll spawn specialized agents to investigate:

1. **Locating Components** - Finding where features are implemented
2. **Analyzing Implementation** - Understanding how code works
3. **Finding Patterns** - Identifying conventions and similar implementations
```

#### Agent Spawning Examples

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
  subagent_type: "codebase-locator",
  model: "haiku"
})
```

**Agent 2: Implementation Analyzer**

```javascript
Task({
  description: "Analyze [feature] implementation",
  prompt: `Document the codebase as it exists, with file:line references — describe
  HOW IT CURRENTLY WORKS; no improvements or issue-spotting (document what IS,
  not what SHOULD BE). Return findings only; write nothing.

  Understand how [feature] works. Analyze:
  - Entry points and main functions
  - Data flow through the system
  - Key algorithms and logic
  - Error handling approaches

  Start with [specific files if known].`,
  subagent_type: "codebase-analyzer",
  model: "sonnet"
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
  subagent_type: "pattern-finder",
  model: "haiku"
})
```

**Additional specialized agents** based on research focus:

- Database schema investigation
- API endpoint analysis
- Frontend component exploration
- Configuration and environment analysis
- Testing pattern discovery

#### Parallel Execution

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

**CRITICAL Agent Instructions (MUST follow exactly):**

- **Each agent is a documentarian, NOT a critic or consultant**
- **Agents MUST describe what exists without ANY judgment**
- **Use specific agent types for their strengths**
- **Run multiple agents in parallel for speed**
- **ALWAYS wait for ALL agents before synthesizing**
- **Remind EVERY agent: You are documenting the codebase AS IT EXISTS**

**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL sub-agents to complete - DO NOT proceed until EVERY agent returns ⛔⛔⛔**

### Step 5: Synthesize Findings

**think deeply about documenting ONLY what EXISTS**

**IMPORTANT**: Wait for ALL sub-agent tasks to complete before proceeding

1. **Compile all sub-agent results**
2. **Prioritize live codebase findings** as primary source of truth
3. **Connect findings across different components**
4. **Include specific file paths and line numbers** for reference
5. **Highlight patterns, connections, and architectural decisions THAT EXIST**
6. **Answer the user's specific questions** with concrete evidence FROM THE CURRENT CODE
7. **DO NOT add recommendations or improvements unless explicitly requested**

### Step 6: Document Findings

Update the research.md file with:

````markdown
---
project: [from existing frontmatter]
ticket: [from existing frontmatter]
created: [from existing frontmatter]
status: complete
last_updated: [YYYY-MM-DD]
---

# Research: [Project Name]

**Created**: [original date]
**Last Updated**: [YYYY-MM-DD]
**Ticket**: [ticket-reference or N/A]

## Research Question

[Original user query]

## Summary

[High-level documentation of what was found, answering the user's question by describing what exists - 2-3 paragraphs]

## Detailed Findings

### [Component/Area 1]

**Location**: `path/to/component/`

**What exists**:
- Description of current implementation ([`file.ext:123`](link))
- How it connects to other components
- Current implementation details (without evaluation)

**Key code**:
```language
// Actual code snippet from file.ext:123-145
// Showing how it currently works
```

**How it works**:

1. [Step-by-step explanation of current flow]
2. [With specific file:line references]
3. [Describing actual behavior]

### [Component/Area 2]

[Continue pattern...]

## Architecture Documentation

**Current patterns found**:

- Pattern 1: [Description of pattern and where used]
  - Example: `src/auth/validator.ts:45-67`
  - Example: `src/api/middleware.ts:23-30`

**Component connections**:

- [Component A] → [Component B]: [How they interact]
  - Entry point: `file1.ext:123`
  - Exit point: `file2.ext:456`

**Conventions observed**:

- Files are organized by [observed pattern]
- Naming follows [observed convention]
- Testing uses [observed approach]

## Code References

Quick reference list:

- `path/to/file1.ext:123` - Main entry point for X
- `path/to/file2.ext:45-67` - Core validation logic
- `path/to/file3.ext:89` - Database queries for Y
- `path/to/file4.ext:200-250` - Error handling implementation

## Similar Implementations

Existing patterns in the codebase that might be relevant:

**Example from `path/to/example.ext:100-120`**:

```language
// Code showing similar pattern already in use
```

This pattern is also used in:

- `other/file.ext:50` - For feature X
- `another/file.ext:75` - For feature Y

## Open Questions

Questions that require resolution before proceeding are tracked in beads, NOT in this document.

**To add a question**:

```bash
bd create "Q: [your question]" --type=task --priority=2 \
  -d "Research question. Blocks: [what can't proceed without this answer]"
# → Returns issue ID (e.g., prompts-abc)
```

**Active questions** (reference only, beads is source of truth):

Use `bd list --status=open` to see all open questions, or reference by ID:
- `[id]`: [Brief question summary] - blocks design decisions about [area]
- `[id]`: [Brief question summary] - blocks [what it blocks]

To see full question details: `bd show [id]`

## Next Steps

Based on the research findings:

1. [Suggested next action based on findings]
2. [Another logical next step]
3. Review the research document
4. Run `/create_design` to create design decisions

````

**⛔⛔⛔ BARRIER 3: STOP! Verify NO placeholder values - ALL data MUST be from ACTUAL codebase ⛔⛔⛔**

Before writing:

- **NO** "[To be added]" or similar placeholders
- **NO** generic examples - use REAL code from THIS codebase
- **NO** assumptions - only documented FACTS

### Step 7: Handle Follow-Up Questions

If the user has follow-up questions:

1. **DO NOT create a new research file**
2. **Append to the existing research.md**
3. **Add new section**: `## Follow-up Research [YYYY-MM-DD HH:MM]`
4. **Update frontmatter**:
   - `last_updated: [YYYY-MM-DD]`
   - Add: `last_updated_note: "Added research on [topic]"`
5. **Spawn new sub-agents** for additional investigation
6. **Continue building** on previous findings

### Step 8: Confirm Completion

Emit a one-line summary, not a recap:

```
✅ research.md updated — [topic]; [N] findings, [M] code refs. Next: /create_design
```

## Important Notes

### Critical Ordering

- **ALWAYS** read mentioned files first before spawning sub-tasks (Step 1)
- **ALWAYS** wait for all sub-agents to complete before synthesizing (Step 4)
- **NEVER** write the research document with placeholder values

### Documentation Philosophy

- **CRITICAL**: You and all sub-agents are documentarians, not evaluators
- **NO RECOMMENDATIONS**: Only describe the current state of the codebase
- Focus on finding concrete file paths and line numbers for developer reference
- Research documents should be self-contained with all necessary context
- Each sub-agent prompt should be specific and focused on read-only documentation operations
- Document cross-component connections and how systems interact

### File Reading

- **File reading**: Always read mentioned files FULLY (no limit/offset) before spawning sub-tasks
- Have sub-agents document examples and usage patterns as they exist
- Keep the main agent focused on synthesis, not deep file reading

## Configuration

The command accepts the directory path as a parameter:

```

/create_research docs/plans/2025-10-07-my-project

```

Or prompts for it if not provided.
