# UI research summary

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 2. Combine the findings of the five agents into this shape.

```markdown
## UI Research Summary

### Layout System
- Pattern: [grid/flex/etc]
- Container widths: [values]
- Breakpoints: [mobile/tablet/desktop values]

### Component Library
- Location: [path]
- Key components: [list with file:line]
- Naming convention: [pattern]

### Styling Approach
- Method: [CSS modules/Tailwind/etc]
- Colors: [token location]
- Typography: [scale location]
- Spacing: [system]

### Icon System
- Library: [Font Awesome / Material Icons / Heroicons / SVG sprites / Custom / None]
- Location: [file:line where the icons are imported or defined]
- Usage pattern: [<i class="..."> / <Icon name="..."> / <svg><use href="...">]
- Sizing: [classes or conventions]
- Examples: [file:line references to icon usage]

### Similar Features
- [Feature 1]: [path] - [how it is structured]
- [Feature 2]: [path] - [how it is structured]

### Patterns to Follow
1. [Pattern from research]
2. [Pattern from research]
```
