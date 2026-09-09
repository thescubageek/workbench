# Important Guidelines

## DO

- ✅ Read ALL files fully before reporting
- ✅ Count the checkboxes rather than trusting the counters — the counts are the fact
- ✅ Report both errors and warnings with clear severity
- ✅ Provide specific, actionable fix suggestions
- ✅ Check that task IDs are present and unique; they are cited from outside the file
- ✅ Check for consistency across all files
- ✅ Offer to help fix issues after reporting

## DON'T

- ❌ Make assumptions about what "should" be there
- ❌ Automatically fix issues without user confirmation
- ❌ Skip checks if some files are missing
- ❌ Report vague problems without specific locations
- ❌ Treat counter drift as an error — it is expected between checkpoints, and `/wb:update_status` is what resolves it
- ❌ Rewrite counters yourself; `/wb:update_status` is their only writer
- ❌ Use limit/offset when reading files
