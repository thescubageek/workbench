# decisions.md

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 5. Write `mockups/v00N/decisions.md`.

```markdown
---
version: 1
created: [YYYY-MM-DD]
---

# v001 Decisions

## Choices Made

### Layout Choice
- **Decision**: [what was chosen]
- **Rationale**: [why, with a reference to the research]
- **Alternative considered**: [what else could work]

### Component Choices
- **Decision**: Use [component] for [purpose]
- **Rationale**: It matches the existing pattern at [file:line]

## Based On Research

- The layout follows the pattern from [similar feature]
- The components come from [library location]
- The styling matches [existing page]

## Assumptions

1. [An assumption made because a requirement is not clear]
2. [Assumption about user behavior]

## Needs Validation

- [ ] [Thing to verify with user/stakeholder]
- [ ] [Technical feasibility question]
```
