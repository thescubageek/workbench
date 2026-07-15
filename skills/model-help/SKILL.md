---
name: model-help
description: Given a handoff file, task spec, ticket, or pasted work description, recommend which Claude model + reasoning-effort level to run it at (and whether to split it into tiers). Use when the user asks "what model/effort should I use", "which effort level", "tier this task", "model advice for this handoff", or hands over a task/handoff and asks how to run it. Advice only — it does not do the work.
---

# /model-help — pick the model + effort for a task

Read a handoff / task spec / ticket and return a **model + effort** recommendation with a one-paragraph rationale. Advice only — never start the implementation.

## Input

- A file path (e.g. a `/tmp/*-handoff.md`, a `docs/plans/**/tasks.md`, a ticket export) — read it fully.
- Or pasted content in a handoff-ish shape (scope, file refs, decisions, open questions).
- If nothing is provided, ask for the handoff/spec (one line) and stop.

## The two axes (pick each independently)

**Model = capability ceiling.** How much raw reasoning the hardest part of the task needs.
**Effort = how much thinking to spend** at that ceiling. A cheap model at high effort ≠ a strong model at low effort — match model to the ceiling, effort to the depth.

Current roster (most → least capable): **`claude-opus-4-8` (Opus 4.8)** · **`claude-sonnet-5` (Sonnet 5)** · **`claude-haiku-4-5` (Haiku 4.5)**. `claude-fable-5` (Fable 5) also exists (fast Claude‑5 tier); default to the three above unless the user prefers Fable. Effort levels: `low` · `medium` · `high` · `xhigh` · `max`.

## Assess the task on these dimensions

Score the task HIGH/MED/LOW on each — the **highest** dimension drives the tier (a task is only as cheap as its riskiest part):

1. **Blast radius** — how many call sites / subsystems does it touch? Is it a hot path (a widely-called model method, a shared concern)? Isolated file = LOW; ~hundreds of call sites = HIGH.
2. **Correctness sensitivity** — compliance / PHI / security / billing / auth / data-integrity / irreversible migration? A silent bug that ships is expensive = HIGH. Easily caught in review/tests = LOW.
3. **Novelty / ambiguity** — is the approach already decided (mechanical execution) or does it need design judgment, trade-offs, or resolving open questions? "Decision LOCKED, just build X" = LOW; "figure out the approach" = HIGH.
4. **Cross-file reasoning** — must you hold many files/interactions in context at once (audits, reviews, refactors, tracing data flow)? One file = LOW; whole-subsystem = HIGH.
5. **Verification cost** — can the result be exercised/tested cheaply, or does a mistake hide until prod? Cheap to verify = LOW; hard-to-observe = HIGH.

## Mapping (highest dimension wins)

| Task shape | Model | Effort |
| --- | --- | --- |
| Trivial, isolated, easily verified — copy tweaks, config bumps, a rename, doc edits, a single obvious factory/spec | Haiku 4.5 (or Sonnet 5) | low |
| Bounded eng change, mechanical but touches a hot path or needs edge/nil-safety reasoning + real specs | Sonnet 5 | medium |
| Multi-file feature, non-trivial logic, moderate correctness sensitivity, some design latitude | Sonnet 5 (Opus 4.8 if reasoning-dense) | high |
| Compliance / PHI / security / billing critical · wide blast radius · novel design · hard-to-reverse migration · adversarial review of sensitive code | Opus 4.8 | high → max |

Effort guidance: **medium is the default for real eng work.** Drop to **low** only when genuinely mechanical. Reserve **high** for hard reasoning / review; **xhigh/max** for the thorniest multi-constraint problems or adversarial verification — they cost real time/tokens with diminishing returns, so don't reach for them by default.

## Splitting

If the handoff has parts with different ceilings, **recommend splitting** and tier each part — e.g. "migration alone → Sonnet/low; the hot-path resolver change + specs → Sonnet/medium." Don't average a spiky task down to one tier.

## What raises / lowers a tier

- **Lowers:** the decision is already made/LOCKED · isolated file · strong test coverage exists · reversible.
- **Raises:** PHI/clinical/billing/security · edits a load-bearing shared method · open design questions in the handoff · cross-repo or migration · "be thorough / exhaustive / audit."

## Output format

Lead with the call, then justify in ~2–4 sentences, then note bump-conditions:

```
**<Model>, <effort> effort.**
- Why not higher: <the ceiling isn't needed because …>
- Why not lower: <the riskiest dimension — e.g. hot path / PHI — needs it>
- Split (if any): <part → tier>
- Bump to <higher> if: <condition>
```

Keep it tight. No preamble, no restating the whole handoff.

## Calibration anchors

- **Reef `review-reef` on a clinical notes-fan-out PR** → Opus 4.8 / high (compliance-critical, cross-file, adversarial). Bump to max for a focused pass on the sign-and-lock core.
- **Add a nullable column + a one-line resolver change on a ~140-call-site hot path + form field** (e.g. TB-2936 Zoom `zoom_url`) → Sonnet 5 / medium; the migration alone would be Sonnet/low.
- **Copy change / locale tweak / config bump** → Haiku 4.5 / low.
