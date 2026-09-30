# Exploration document

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 6. Write `[project-dir]/thoughts/YYYY-MM-DD-<topic>.md`.

**The decision record is the top section, and its position matters.** `create_design` looks in
`thoughts/` for exactly this section. It writes the record into the Technical Decisions of
`design.md`. If the record is below the exploration, `create_design` does not find it.

````markdown
---
created: [YYYY-MM-DD]
type: exploration
project: [project-name]
topic: [what was being decided]
status: decided | abandoned
---

# Exploration: [what was being decided]

## Decision Record

**Chosen direction**: [the approach, in one line]

**Rationale**: [why this direction. Use the reasons that the user gave, not a reconstruction]

**Rejected**:

- **[Option B]** — [why not. The specific reason, not "less good"]
- **[Option C]** — [why not]

**Revisit if**: [the condition that reopens this decision, for example a constraint that can
change or an assumption that can fail. Omit this only if there is no such condition.]

**Decided**: [YYYY-MM-DD], with [user], after [N] rounds of discussion.

---

## The Decision Space

**What is actually being decided**: [one sentence. State the question, not the options]

**What is NOT being decided here**: [related questions that are kept out of scope on purpose]

**Constraints that bound any answer**:

- [From research.md: what exists and must be used, with file:line]
- [From the user: a stated requirement or preference]

**What would make this decision wrong**: [the thing that, if true, invalidates the choice]

## Directions Considered

### [Direction A — descriptive name]

- **Shape**: [what this actually looks like, concretely]
- **Precedent**: [where something similar already exists: file:line, or "none in this codebase"]
- **Buys**: [what it gets you]
- **Costs**: [what it gives up. Be specific. "More complex" is not a cost]
- **Fails if**: [the condition under which this is the wrong choice]

### [Direction B]

[Same shape.]

## Discussion

[The trade-off discussion, in enough detail to keep the reasoning. The Rejected Alternatives
section in design.md cannot hold this, because the stage that writes design.md has already
chosen. Quote the user where their words decided something.]

## Open Threads

[Each point that was raised and left open on purpose, with the reason. Not every point must close.]
````
