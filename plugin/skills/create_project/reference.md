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
- `design.md`: draft → ready → implementing → complete
- `tasks.md`: not-started → in-progress → complete

## Error Handling

Check for and handle:

- Directory already exists → Suggest different name or confirm overwrite
- Invalid project name → Request kebab-case format
- Git not available → Use placeholder values
- No write permissions → Suggest different location
