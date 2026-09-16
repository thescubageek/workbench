# create_product_research — reference

Read this when a step directs you to. Step 3 and Step 5 both depend on the Audience section
below — it is what makes this skill different from `create_research`, so read it before
decomposing and again before synthesizing.

## Audience: Product Managers

Your output is for someone who manages the product, not someone who writes the code. This means:

- Explain features as user-visible behaviors, not implementation details
- Describe flows as user journeys, not code paths
- Group findings by product capability, not by file or module
- Use plain language — no engineering jargon unless it's a user-facing term
- Include technical references as backing evidence in an appendix, not inline

## Workflow Position

This skill can be used in two ways:

1. **Within the wb pipeline**: After `/wb:create_project` creates the directory structure. The `product-research.md` file will be created alongside `research.md` — they serve different audiences for the same project.

2. **Standalone**: A PM can run this without `/wb:create_project`. If the directory exists but `product-research.md` doesn't, create it fresh. If the directory doesn't exist, create it.

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
