---
name: project-structure
description: Enforces project documentation structure in docs/plans/ directories - research.md for facts, design.md for decisions, tasks.md for implementation, thoughts/ for explorations - plus the cross-ticket knowledge store for what outlives a ticket.
---

# Project Structure

## Document Separation

**research.md** - Facts only (internal codebase + external research)

- WHAT EXISTS: Current code, external patterns, options, capabilities
- NO decisions, NO rationale, NO implementation steps

**design.md** - Decisions + rationale only

- WHAT to build, WHY chosen
- Architectural decisions, trade-offs, scope
- NO facts without decisions, NO implementation steps

**tasks.md** - Implementation only

- HOW to implement: specific steps, file changes, tests
- NO rationale, NO alternatives

**thoughts/** - Explorations & refinements

- Questions, experiments, discussions
- Understanding refinements before decisions
- Informal notes, brainstorming
- Anything not ready for formal docs

**knowledge store** - Cross-ticket, not per-ticket

- The four categories above are scoped to one `docs/plans/<date>-<slug>/` directory and stop mattering
  once the ticket closes
- The store (see the `knowledge-store` skill) holds what outlives the ticket — durable facts, gotchas,
  and conventions — read via `./scripts/knowledge-read`
- Anything true only of this ticket stays in the four categories above, not the store

## Quick Check

- Decision? → design.md
- Fact/Option? → research.md
- Step/Code? → tasks.md
- Exploring/Unsure? → thoughts/
- True beyond this ticket? → knowledge store
