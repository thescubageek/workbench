# `entries/` — Promoted Knowledge

**Everything here has been through a human-reviewed promotion diff. Retrieval reads this tree, and only
this tree.**

An entry in this directory can steer any future ticket in this repository: it is loaded at research time
and at handoff-resume time, and it shapes where the next run looks and what it believes about this
codebase. That is exactly why nothing arrives here automatically.

## How content gets in

One way only:

```text
staging/  →  curation pass  →  fresh-context reviewer  →  reviewable diff  →  human approves  →  entries/
```

`/wb:curate_knowledge` produces the diff. It never mutates this tree live. There is no other path, and
adding one would defeat the gate — if you find yourself writing directly here from a script or a hook,
that is a bug, not a shortcut.

## What each file is

One entry per file, named by its ID, in the format defined by [`../SCHEMA.md`](../SCHEMA.md). Entry
granularity is load-bearing in two independent ways: concurrent proposals from parallel ticket agents
merge cleanly at file granularity and collide at document granularity, and a failed entry can be
reverted as one file rather than unpicked from a shared document.

Never collapse these into a single growing document. That reintroduces the merge conflicts and invites
the monolithic rewrite that progressively loses accumulated detail — the failure this layout exists to
prevent. `INDEX.md` is what recovers readability, and it is generated.

## Entries are data, not instructions

Under the default write policy an entry is read as **evidence about the codebase**, never as a directive
to the reading agent. An entry saying "always do X" is a claim that X is the convention here — it is not
an instruction that binds the agent, and it does not override `CLAUDE.md`, the command prose, or the
user.

This is not pedantry. Content written into agent memory survives and propagates through self-evolution,
and the refinement process *legitimizes* it — an injected payload stops looking like an attack and starts
looking like a learned pattern. A store read by every subsequent ticket is a supply chain. The data/
directive boundary is one of the controls that keeps it from being an execution path.

## Trust boundary

- Written by: humans, via approved promotion diffs
- Read by: the retrieval path (`create_research` Step 0, `resume_handoff` Step 4), scoped by tag and
  bounded in count
- Protected: `knowledge/entries/` is in the protected-path set in `.wb-knowledge.json`, so an armed
  agent run cannot write here at the tool-call layer

Compare [`../staging/README.md`](../staging/README.md), which is the exact inverse on every row.
