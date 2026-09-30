# PR description — the generic template

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 4. Use this template only when `pr-template` prints `generic`. Fill the fenced block, and
leave out everything outside it. Each comment gives the section's scope and its size. Remove
the comments. Leave out "Notes for reviewers" if it has nothing to say.

```markdown
## Summary

<!-- 1 to 3 sentences. What changes for a user or a developer, then why. -->

## Changes

<!-- At most 5 bullets, one line each. A behaviour or a decision, not a file list. -->

## Testing

<!-- 1 to 3 bullets: how you verified it, with the command or the manual step. -->

## Notes for reviewers

<!-- Optional. At most 3 bullets: a risk, a follow-up, or where to look first. -->

<!-- Links: the ticket, the plan or handoff for detail. One line. -->
```
