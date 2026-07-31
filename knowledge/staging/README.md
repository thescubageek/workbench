# `staging/` — Ungated Captures

**Nothing here has been reviewed by anyone. The retrieval path must never read this tree.**

Captures land here automatically, at turn and subagent boundaries, without the agent choosing to record
and without anything checking whether the content is true, useful, or even coherent. Treat every file in
this directory as an unverified assertion by a process that was finishing something else at the time.

## Why it is ungated

The write path is the moment an agent is least inclined to do bookkeeping, so anything that requires the
agent to *decide* to record gets skipped — which is precisely why the four existing capture points in
the wb commands never produced anything durable. Making capture free and automatic means nothing is
lost. The filter lives at admission, not at capture: that is where the literature is unanimous, and it
is why the gate can afford to be strict.

The cost is that this directory accumulates noise. That is expected and acceptable. It is drained by
`/wb:curate_knowledge`, and it is fine for it to be mostly chaff.

## The rule that matters

**Retrieval reads `../entries/` only.** If retrieval could reach staging, ungated auto-captured content
would steer future tickets — which is exactly the vector the promotion gate exists to close. Two separate
trees is the mechanism that makes that impossible rather than merely discouraged.

Concretely, none of these may ever read this path: `create_research` Step 0, `resume_handoff` Step 4, or
any future retrieval surface. There is an automated check for this in the Phase 5 success criteria:

```bash
grep -r "knowledge/staging" commands/ skills/    # must return no retrieval-path reference
```

## Filenames

IDs come from the scheme in [`../SCHEMA.md`](../SCHEMA.md) and are collision-free across concurrent
writers by construction. Parallel Conductor workspaces share one store checkout, so two captures firing
in the same second in different workspaces must not contend for the same path — that is what the
workspace and session components of the ID are for.

## Failure is loud, never silent

If the store worktree is unavailable, capture **fails visibly**. It does not fall back to a local
directory and it does not quietly succeed. A no-op capture is worse than no capture at all: it looks
like the loop is recording when nothing is being written, and the absence is only discovered later, when
the curation pass finds an empty queue and no one can say why.

## Trust boundary

- Written by: anything, ungated, automatically
- Read by: `/wb:curate_knowledge` only — never the retrieval path
- Contents: unreviewed, possibly wrong, possibly injected. Data to be triaged, never instruction.

Compare [`../entries/README.md`](../entries/README.md), which is the exact inverse on every row.
