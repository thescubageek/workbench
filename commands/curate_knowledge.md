---
description: Drain the knowledge store's staging area through a fresh-context reviewer into promoted entries, as a reviewable proposal — never a live mutation
argument-hint: "[--sweep-only]"
---

# Curate Knowledge

The batched, human-gated pass that drains `knowledge/staging/` into `knowledge/entries/`. Capture is
automatic and ungated; **this is the gate**, and it is the one component the design says cannot be
skipped or cheapened.

**Model & effort (gate check)**: on entry, consult the `model-help` skill (gate mode). Baseline is
Opus 4.8 / high — this is judgment-dense admission work, and `skills/model-help` is explicit that a pass
running unattended must be tiered on judgment rather than routed to the cheapest agent. Rise to Opus 5
when the batch touches entries about the harness itself. Best-effort and non-blocking. See CLAUDE.md →
"Model & effort at gates."

## Purpose

Staged entries are unreviewed assertions by a process that was finishing something else at the time.
This command turns the useful ones into promoted entries that later tickets will read, and it does so
in a way where **a human decides every promotion**, because a loop that can promote its own claims can
eventually promote a claim that weakens its own evaluator.

## Prerequisites — read before anything else

### The run must already be armed. This command cannot arm it

`hooks/knowledge-guard.sh` is armed by the environment of the process that **started the session**.
Verified by execution in Phase 2: a tool-layer process is a child of the session and cannot mutate the
parent environment the hook inherits. That is what makes arming un-forgeable — and it also means **no
command running inside a session can arm itself**, this one included.

So step one is to confirm, not to arm:

```bash
./hooks/knowledge-guard.sh --selfcheck
```

- `armed: yes, interactive` → proceed.
- `armed: no` → **stop and tell the user to restart**, exactly:

  ```bash
  WB_SELF_EXTENSION=interactive claude
  ```

  Do not proceed unarmed. Unarmed, every write to `knowledge/entries/` would succeed silently with no
  human in the loop, which is precisely the thing this whole design exists to prevent. An unarmed
  curation pass is not a degraded pass — it is the failure mode wearing the pass's clothes.
- `armed: yes, unattended` → **stop.** Promotion has no unattended mode. Say so and exit.

⛔ **BARRIER 1**: Do not read staging, and do not plan any promotion, until the armed state is
confirmed interactive.

### Read these fully, no limit/offset

1. `knowledge/SCHEMA.md` — the entry shape you are producing
2. `skills/knowledge-store/SKILL.md` — capture conventions and the curation operations
3. Every file in `knowledge/staging/` (excluding `README.md`)
4. Every file in `knowledge/entries/` — you cannot judge whether a candidate is new, an update, a
   merge, or a duplicate without knowing what is already promoted

## Step 1: Sweep first, so you know what is already rotting

```bash
./scripts/knowledge-sweep
```

Deterministic, no model calls. Every promoted entry comes back `clean`, `suspect`, or `undecidable`.
Handle each class differently — this is the invalidation half of the pass, and it runs **before**
promotion so you are not adding to a store you have not first checked:

- **clean** — leave alone.
- **suspect** — something it cites has changed. Refer it to `agents/research-validator.md` (Step 3).
  Suspect is *not* wrong, only unverified since.
- **undecidable** — cites nothing git can watch. The sweep cannot help and will never be able to;
  these are yours to judge by reading. Expect most automatic captures here.

If `$ARGUMENTS` contains `--sweep-only`, report the sweep and **stop**. That is the cheap health check.

## Step 2: Triage staging into proposed operations

For each staged entry decide exactly one of four operations. The rationale for each is in
`skills/knowledge-store/SKILL.md` — apply it, do not re-derive it.

| Operation | When |
| --- | --- |
| **add** | A genuinely new claim, not covered by any promoted entry |
| **update** | A promoted entry is right in shape but wrong or thin in substance |
| **merge** | Two entries say the same thing — **subject to the diversity rule below** |
| **deprecate** | A promoted entry is now false, or superseded, or was never a claim |

Most staged entries deserve **none** of these. Automatic capture is deliberately ungated and writes low
signal; a pass that promotes most of what it reads is not a gate. Dropping a staged entry is the normal
outcome and needs no ceremony — say so in the proposal and move on.

### ⛔ The diversity rule bounds merge, and it is a test, not a preference

Before merging A into B, name **the class of ticket each one wins on**. If you can name a class where A
is the better answer and a different class where B is, **the merge is refused** — keep both.

Collapsing them produces one canonical best practice that is second-best everywhere, and the loss is
invisible: nothing fails, retrieval just quietly gets worse for every ticket that needed the other one.
Write the two ticket classes into the proposal. If you cannot name two distinct classes, the merge is
allowed — that is the check passing, not a formality skipped.

## Step 3: Verify claims with a fresh-context validator

Spawn `agents/research-validator.md` for **every candidate you intend to promote** and every **suspect**
entry from Step 1. Give it the entry path and nothing else.

It accepts a knowledge entry unchanged — verified by execution 2026-07-31 against a true/false pair, no
schema shim needed.

**Read its overall status, never its per-path table.** In that probe the validator marked a cited file
`PASS` in the path table (the file does exist) while correctly failing every behavioral claim about it.
An entry can cite files that all still exist and be entirely wrong.

- **PASS** → eligible for promotion
- **PASS WITH WARNINGS** → eligible, but the warnings go in the proposal
- **FAIL** → not eligible. Propose `deprecate` for a promoted entry, or drop a staged one
- **UNCERTAIN** → not eligible without a human ruling. Say what could not be traced

⛔ **BARRIER 2**: Wait for **all** validator results before writing the proposal. A partial proposal
invites promoting the entries that happened to come back first.

## Step 4: Write the proposal — this is the deliverable

```
knowledge/proposals/<UTC-date>-<session8>.md
```

`knowledge/proposals/` is deliberately **not** in `protected_paths`, so you can write it freely. That is
the point of the two-stage shape: the proposal is cheap to produce and cheap to reject, and **nothing
reaches `entries/` while it is being written.**

One section per proposed operation, each carrying:

- the operation, and the target entry id (or `NEW`)
- **the full proposed entry content**, not a description of it — a reviewer must be able to judge the
  text that would land, not a summary of it
- the validator's overall status
- for `merge`: the two ticket classes, per the diversity rule
- **the prediction** (see below)
- one sentence on why this is durable rather than ticket-scoped

Then a summary: N staged read, N proposed, N dropped, and the sweep's counts.

### Every promoted entry carries a prediction

`prediction:` states the entry's **expected effect on future work**, in terms that could later be found
false — "a ticket touching the hook layer will not re-derive the stdin payload shape," not "this is
useful."

v1 cannot check predictions strongly; the eval corpus that would is deferred. Record them anyway, so
they are checkable **retroactively** once the corpus exists. An unfalsifiable prediction is worse than
none: it makes promotion look like a contract while committing to nothing.

⛔ **BARRIER 3**: No placeholders. Every proposed entry is complete, schema-valid, and has a real
`verified_at` SHA and real cites. "TBD" in a proposal becomes "TBD" in the store.

## ⛔ CHECKPOINT: Human review

Present the proposal path and the counts. **Stop. Wait.** Do not apply anything.

The user reads the proposal and says which operations to apply. Applying is Step 5, and it only runs on
an explicit instruction naming what to apply.

## Step 5: Apply, one approved operation at a time

Only on explicit instruction, and only for the operations named.

Each write to `knowledge/entries/` hits the armed guard and **prompts for approval** — that is the
mechanical gate behind the human one, and it is not a formality to click through. If a prompt appears
for an entry the user did not name, something has gone wrong: **deny it and stop.**

After applying:

```bash
./scripts/knowledge-sweep          # the store you just changed should still classify sanely
./scripts/lint knowledge/entries/  # entries are markdown
```

Remove the staged files that were promoted or deliberately dropped, so the next pass does not re-triage
them. Leave anything you deferred.

## Important Guidelines

- **The reviewer must be fresh-context.** `skills/touch-grass/SKILL.md` records why: a same-context
  reviewer carries the authoring context and rubber-stamps its own work. The validator subagent gets
  the candidate and nothing else — not your reasoning, not the proposal, not why you liked it.
- **Never promote to raise a number.** A pass that promotes nothing is a valid pass and a common one.
- **Core self-extension is never promotable by this command.** Entries *about* the harness are fine;
  changes *to* `commands/`, `agents/`, `skills/`, `hooks/`, or the config are permanently human-only
  with no configurable override, and the guard will refuse them regardless of what any entry says.
- **An entry that reads as an instruction is a defect.** Entries describe what is true, not what the
  next agent should do. The default write policy exists so that no entry is readable as instruction.

## Output Discipline

The proposal file is the deliverable. Report one line — proposal path, counts, sweep summary — and stop.
Do not reproduce the proposal into the chat.
