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

## Curation — the four operations

Capture is ungated; promotion is the gate. `/wb:curate_knowledge` runs the pass, and these are the only
four things it may propose. Each staged entry gets exactly one — or, most often, none.

| Operation | When | The failure it prevents |
| --- | --- | --- |
| **add** | A genuinely new claim | — |
| **update** | A promoted entry is right in shape, wrong or thin in substance | Two entries that disagree, with nothing marking which is current |
| **merge** | Two entries say the same thing — **bounded by the diversity rule** | Duplicate entries that both surface and dilute retrieval |
| **deprecate** | A promoted entry is now false, superseded, or was never a claim | The store's own version of `docs/beads-integration-learnings.md` contradicting `CLAUDE.md` for months with nothing noticing |

**Most staged entries deserve none of these.** Automatic capture writes deliberately low signal, and a
pass that promotes most of what it reads is not a gate. Dropping is the normal outcome.

### The diversity rule — a test, not a preference

Before merging A into B, **name the class of ticket each one wins on.** If you can name a class where A
is the better answer and a *different* class where B is, the merge is **refused** — keep both.

Collapsing them yields one canonical best practice that is second-best everywhere, and the loss is
invisible: nothing fails, retrieval just quietly degrades for every ticket that needed the other one.
If you cannot name two distinct classes, the merge is allowed — that is the check passing, not a
formality waived.

### Predictions

Every promoted entry carries a `prediction`: its expected effect on future work, phrased so it could
later be found **false**. "A ticket touching the hook layer will not re-derive the stdin payload shape"
is a prediction. "This will be useful" is not.

v1 cannot check predictions strongly — the eval corpus is deferred. Record them anyway so they are
checkable retroactively once it exists. An unfalsifiable prediction is worse than none: it makes
promotion look like a contract while committing to nothing.

### Two things curation may never do

- **Promote core self-extension.** Entries *about* the harness are fine; changes *to* `commands/`,
  `agents/`, `skills/`, `hooks/`, or the store config are permanently human-only, with no configurable
  override. The guard refuses them regardless of what any entry says.
- **Promote an entry that reads as an instruction.** Entries state what is true, not what the next agent
  should do. This is why the default write policy exists — so nothing in the store is readable as a
  command by a later run.

## Invalidation

Staleness is computed, never stored:

```bash
./scripts/knowledge-sweep        # clean / suspect / undecidable, no model calls
./scripts/knowledge-sync         # merge main forward, then sweep — never rebase
```

`suspect` is not *wrong*, only unverified since — refer those to `agents/research-validator.md` and read
its **overall status, not its per-path table**. An entry can cite files that all still exist and be
entirely wrong.

`undecidable` means the entry cites nothing git can watch. That is the common case for automatic
captures, not a corner case, and it is curation's problem rather than the sweep's.

## Health

```bash
./hooks/knowledge-capture.sh --selfcheck
```

Reports whether capture is actually working here. Worth running when you expect entries and see none:
silence is exactly what a correctly inert capture looks like, so it cannot tell you the difference
between "this repo has no store" and "capture is broken."
