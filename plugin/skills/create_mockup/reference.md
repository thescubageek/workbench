# create_mockup — reference

Read this when a step directs you to.

## Purpose

This skill:

- Documents current UI patterns and styles (research phase)
- Asks clarifying questions about the desired feature
- Creates a versioned mockup with rationale
- Sets up iteration tracking for refinement

## Output Files

| File | Purpose |
| ------ | --------- |
| `mockups/mockup-log.md` | Track all versions and running requirements |
| `mockups/v001/mockup.md` | ASCII structure and specifications |
| `mockups/v001/mockup.html` | Working HTML mockup with app's actual styles |
| `mockups/v001/decisions.md` | Rationale for this version |
| `mockups/v001/preview-v001.png` | Visual screenshot of HTML mockup |

## Important Guidelines

### Research First

- ALWAYS research existing UI before proposing
- Reference specific file:line locations
- Follow established patterns unless explicitly breaking them

### Clarifying Questions

- Ask before assuming
- Understand the WHY not just the WHAT
- Identify constraints early

### Versioning

- Never overwrite - always create new version
- Document what changed and why
- Keep decision trail for design.md

### Fidelity

- ASCII mockups for layout structure discussion
- HTML mockups with app's actual styles for visual validation
- Component specs for implementation detail (copied from research)
- Icon system from research (no placeholder icons/emojis)
- State documentation for edge cases
- Visual screenshots for design approval

### Icon handling based on research

- **If Font Awesome found**: Use `<i class="fa-[style] fa-[name]"></i>` pattern
- **If Material Icons found**: Use `<span class="material-icons">[name]</span>` pattern
- **If SVG sprites found**: Use `<svg><use href="#icon-[name]"></use></svg>` pattern
- **If custom icon components**: Document pattern and ask user how to mock
- **If NO icon system found**: use text only, and raise a `UIQ` row if icons are genuinely needed — never invent a library

### Quality checks before presenting the HTML

- [ ] All CSS classes are from research (no placeholder classes)
- [ ] Icon system matches research (or confirmed text-only)
- [ ] Layout structure matches ASCII diagram
- [ ] Can be opened in browser without errors
- [ ] Styling approach matches research (Tailwind/CSS modules/etc)

## Relationship to Other Commands

**Typical workflow:**

1. `/wb:create_research` - Understand the codebase
2. **`/wb:create_mockup`** - Research UI + create initial mockup
3. [Iterate with mockup-iteration skill]
4. `/wb:create_design` - Finalize design from mockup decisions
5. `/wb:create_tasks` - Plan implementation

The mockup process feeds into design.md with validated requirements.
