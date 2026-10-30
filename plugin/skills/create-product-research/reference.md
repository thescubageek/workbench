# create-product-research — reference

Read this when a step directs you to. Step 3 and Step 5 both depend on the Audience section
below — it is what makes this skill different from `create-research`, so read it before
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

1. **Within the wb pipeline**: After `/wb:create-project` creates the directory structure. The `product-research.md` file will be created alongside `research.md` — they serve different audiences for the same project.

2. **Standalone**: A PM can run this without `/wb:create-project`. If the directory exists but `product-research.md` doesn't, create it fresh. If the directory doesn't exist, create it.

## Important Notes

### Research Practice

- Focus on behaviors, flows, and capabilities over implementation details.
- Make the research document self-contained, with all the context it needs.
- Keep each sub-agent prompt specific, and limit it to read-only work.
- Document how components connect and how systems interact.
- Have sub-agents document examples and usage patterns as they exist, with file:line references
  for every claim.
- Keep the main session on synthesis. The agents do the deep file reading.

### Three-Layer Output

- **Layer 1 (Product Overview)**: Every PM reads this — must be clear and jargon-free
- **Layer 2 (Engineering Approach)**: PMs read this to understand how the team builds — patterns, not details
- **Layer 3 (Technical Appendix)**: PMs reference this when talking to engineers — file paths and snippets

### Validation

- Validation runs after the document is written, and reads it directly from the file
- FAIL results must be fixed (re-check the code, update document, re-validate)
- UNCERTAIN results are noted in the Validation Notes section for human review
- The `validation_status` frontmatter field tracks overall validation state

## Configuration

The command accepts the directory path as a parameter:

```
/wb:create-product-research docs/plans/2025-10-07-my-project
```

Or prompts for it if not provided.
