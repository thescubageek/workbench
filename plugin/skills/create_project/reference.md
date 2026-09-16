# create_project — reference

Read this when a step directs you to.

## Important Notes

### Argument Usage

- `$1` - Project name (required if using arguments)
- `$2` - Base directory (optional, defaults to docs/plans)
- `$3` - Ticket reference (optional)
- `$ARGUMENTS` - All arguments as a single string

### Status Progression

Files progress through defined states:

- `research.md`: draft → in-progress → complete
- `design.md`: draft → approved *(approval is a human act at `/wb:create_design` Step 6)*
- `tasks.md`: not-started → in-progress → complete

## Error Handling

Check for and handle:

- Directory already exists → Suggest different name or confirm overwrite
- Invalid project name → Request kebab-case format
- Git not available → Use placeholder values
- No write permissions → Suggest different location
- Prose where a project name was expected → ask; never bind words one, two and three to
  name, directory and ticket. Silently accepting a sentence produced a wrongly-named plan
  directory and a ticket reference that was a stray English word, and nothing downstream
  noticed (reported twice, 2026-09-10 and 2026-09-13)
