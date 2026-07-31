---
name: knowledge-store
description: Conventions for writing durable learnings into the repo's knowledge store (knowledge/staging/) — entry shape, the origin field, and what belongs there versus in a per-ticket document. Use when a wb command reaches a capture point, when asked to "record this learning", "capture what we found", or "write this to the knowledge store", or when deciding whether a finding is durable enough to outlive its ticket.
allowed-tools: Read, Glob, Grep, Bash(git:*), Bash(./scripts/knowledge-worktree:*)
---

# Knowledge Store — Capture Conventions

The single authority on how a learning is written down, so four commands do not each carry their own
copy of the rule and drift apart. This file covers **capture**; promotion and curation are a separate
concern with a separate gate.

## Where it goes

```bash
STORE="$(./scripts/knowledge-worktree)" || STORE=""   # non-zero = no store here
```

- **Empty or non-zero → skip silently.** Not every repo declares a store. This is best-effort and must
  never block the command that called it.
- **Writes go to `$STORE/staging/` only.** Never to `entries/`. That tree is promoted, reviewed content
  and the retrieval path reads it; anything ungated landing there would steer future tickets, which is
  precisely what the promotion gate exists to prevent.

One file per claim, named for its `id`, in the shape defined by `knowledge/SCHEMA.md`. Read that file
for the full field list rather than reproducing it here.

## What is worth writing

A `Stop` hook already captures every turn automatically, so the automatic record exists whether or not
you add anything. Write a deliberate entry only for a claim that **stands on its own in six months, to
someone who never saw this ticket.**

| Write an entry | Don't |
| --- | --- |
| A non-obvious fact about how this codebase behaves | A summary of what you just did |
| A gotcha that cost real time, with the `file:line` that proves it | Anything already in `CLAUDE.md` |
| "We tried X here; it failed because Y" | Restating the plan or the task list |
| A convention a future change must respect | Anything true only of this ticket |

Ticket-scoped narrative belongs in `docs/plans/<ticket>/`. The store is for what outlives the ticket.

## `origin` — the field that actually matters

Two values, and the write policy tiers on this axis. **Mislabelling it defeats the policy**, so the rule
is worth stating precisely:

- **`tool-verified`** — a tool produced an observation you did not author: a test result, a diff, a
  validator verdict, an executed probe.
- **`model-narrated`** — everything else, including anything you concluded, summarised, or inferred.

**Reading a file and reporting what it says is narration, not verification.** Reading is not a test.
When unsure, it is `model-narrated` — that is the strictly safe direction, because `model-narrated` is
pinned to `propose-only` and can never be auto-promoted.

Automatic hook capture is *structurally* `model-narrated`: a turn boundary sees your summary, never a
tool's output. `tool-verified` is reachable only from a capture point where a verdict actually exists —
which is why `/wb:validate_execution` is the highest-signal source in the pipeline.

## Provenance

`provenance.verified_at` is the full SHA the claim was checked against (`git rev-parse HEAD`), and
`cites` lists the `file:line` refs it rests on. This is what makes staleness computable without a model
call — `git diff <verified_at>..HEAD -- <cited paths>` classifies the entry clean or suspect.

An entry that cites nothing is not wrong, but it is **undecidable** by that sweep and decays on a clock
nothing observes. Cite files whenever the claim rests on them.

## Health

```bash
./hooks/knowledge-capture.sh --selfcheck
```

Reports whether capture is actually working here. Worth running when you expect entries and see none:
silence is exactly what a correctly inert capture looks like, so it cannot tell you the difference
between "this repo has no store" and "capture is broken."
