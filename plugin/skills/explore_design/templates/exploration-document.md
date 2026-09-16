# Exploration document

Step 6 — `[project-dir]/thoughts/YYYY-MM-DD-<topic>.md`.

**The decision record is the top section, and that placement is load-bearing**: `create_design`
scans `thoughts/` for exactly this section and formalizes it into `design.md`'s Technical
Decisions. A record buried below the exploration is a record the consuming stage will not find.

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

**Rationale**: [why this one — the reasoning the user actually gave, not a reconstruction]

**Rejected**:

- **[Option B]** — [why not. The specific reason, not "less good"]
- **[Option C]** — [why not]

**Revisit if**: [the condition that would reopen this — a constraint that might change, an
assumption that might fail. Omit only if there genuinely isn't one.]

**Decided**: [YYYY-MM-DD], with [user], after [N] rounds of discussion.

---

## The Decision Space

**What is actually being decided**: [one sentence — the question, not the options]

**What is NOT being decided here**: [adjacent questions deliberately held out of scope]

**Constraints that bound any answer**:

- [From research.md: what exists that we must work with — file:line]
- [From the user: a stated requirement or preference]

**What would make this decision wrong**: [the thing that, if true, invalidates the choice]

## Directions Considered

### [Direction A — descriptive name]

- **Shape**: [what this actually looks like, concretely]
- **Precedent**: [where something like this already exists — file:line, or "none in this codebase"]
- **Buys**: [what it gets you]
- **Costs**: [what it gives up — be specific; "more complex" is not a cost]
- **Fails if**: [the condition under which this is the wrong choice]

### [Direction B]

[Same shape.]

## Discussion

[The actual trade-off conversation, in enough detail that the reasoning survives. This is the
part that a Rejected Alternatives section in design.md cannot carry, because design.md is
written by the pass that already chose. Quote the user where their words settled something.]

## Open Threads

[Anything raised and deliberately left unresolved, with why. Not everything has to close.]
````
