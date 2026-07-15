---
name: model-help
description: Given a handoff file, task spec, ticket, or pasted work description, recommend which Claude model + reasoning-effort level to run it at (and whether to split it into tiers). Use when the user asks "what model/effort should I use", "which effort level", "tier this task", "model advice for this handoff", or hands over a task/handoff and asks how to run it. Also runs in "gate mode" inside the wb workflow — forge, resume_handoff, and the create_*/implement/validate phase commands consult it to pick the model + effort for the phase about to run and to decide whether switching the main model is worth the context-reload cost. Advice only — it does not do the work.
---

# /model-help — pick the model + effort for a task

Read a handoff / task spec / ticket and return a **model + effort** recommendation with a one-paragraph rationale. Advice only — never start the implementation.

## Input

- A file path (e.g. a `/tmp/*-handoff.md`, a `docs/plans/**/tasks.md`, a ticket export) — read it fully.
- Or pasted content in a handoff-ish shape (scope, file refs, decisions, open questions).
- Or a **gate call from the wb workflow**: a phase name (`research` / `design` / `execution` / `implement` / `validate`) plus the project docs (or handoff) and, if known, the model the session is currently on. Advise the tier for *that phase* and whether to switch — see [Gate mode](#gate-mode--advising-a-wb-workflow-phase) below.
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

## Gate mode — advising a wb workflow phase

The wb pipeline (`forge`, `resume_handoff`, and the `create_*` / `implement_tasks` / `validate_execution` commands) consults this skill at phase boundaries. Not every phase needs the same tier, but **switching the main-session model reloads the whole conversation** — so the goal is to spend the right amount per phase *without* churning the model. Two levers, very different costs:

- **Sub-agent model + effort is free** — each spawned agent is fresh context. Push cheap, parallelizable work down to cheap agents aggressively (the phase commands already set `model:` hints on their `Task(...)` spawns). This is where most cost optimization lives, and it never touches the main session.
- **Main-session model/effort costs a context reload** on every switch (tokens + latency). Advise a main-session switch only when it pays for that tax.

### Per-phase baseline (then modulate by the ticket's difficulty via the dimensions above)

| wb phase | Main-session baseline | Why | Cheap work → sub-agents |
| --- | --- | --- | --- |
| `create_research` | Sonnet 5 / medium | Main session decomposes + synthesizes; the heavy lifting is in parallel READ-ONLY agents | locator → haiku, analyzer → sonnet, pattern-finder → haiku |
| `create_design` | **Opus 4.8 / high** (→ max for novel / one-way-door / compliance-critical / high-blast-radius) | Reasoning-dense: trade-offs, architecture, locked decisions. Usually the pipeline's ceiling | little to delegate — the judgment is main-session |
| `create_execution` | Sonnet 5 / medium | Decompose an already-decided design into phased tasks — structuring, not deciding | execution agents → sonnet / haiku |
| `implement_tasks` | Sonnet 5 / medium (bump gnarly tasks to Opus 4.8 / high) | TDD execution of a locked plan; most tasks mechanical-to-moderate | `implement_coordinated` already picks per-task worker models |
| `validate_execution` | Sonnet 5 / medium → Opus 4.8 / high | Adversarial check vs plan; raise for wide blast radius / compliance / hard-to-verify | validation agents → sonnet / haiku |

Bump a phase above its baseline whenever the ticket's own dimensions (blast radius, correctness sensitivity, novelty, cross-file reasoning, verification cost) say so — a research pass over an ambiguous cross-subsystem area is Opus/high, not Sonnet/medium.

### The switch-cost rule (this is what keeps it from being noisy)

Advise a **main-session** switch only when **both** hold:

1. the recommended tier differs from the current session by **≥ 1 model step**, and
2. the phase is **substantial** (long reasoning or many tool calls — e.g. design, or a large implement phase), so the reload pays off.

Then:

- **Cluster same-tier phases.** research + execution + implement typically sit at Sonnet; switch **up** to Opus only for the design gate (and validate if sensitive), then back down. A whole forge should cost ~1–2 switches, not 5.
- **Never switch down if you'll likely switch back up soon** — the double round-trip loses. Only drop a tier when you'll stay dropped for ≥ 2 phases. Sitting one tier *high* for a short phase is cheaper than a round-trip and never costs quality.
- **The floor is inviolable.** Never advise below the tier a phase needs at its hardest sub-problem. Savings come from not *over*-powering cheap phases and from sub-agent tiering — never from under-powering a hard one.

### Gate output format

One line, silent when no switch is warranted (just confirm the tier):

```
Model gate — <phase>: recommend **<Model> / <effort>**. Current: <model or "unknown">.
→ <Switch (worth the reload: <reason>) | Stay (delta too small / phase too short / already sufficient)>.
```

If recommending a switch, tell the user the concrete action (`/model <name>` and set effort), then let them decide — never switch on their behalf, never block on it.

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
- **Gate mode, a moderate forge** (bounded feature, decisions still open) → research Sonnet/medium → **switch up** to Opus/high for the design gate → **switch back down** to Sonnet/medium for execution + implement → validate Sonnet/medium. Two main-model switches total; research/execution/implement never leave Sonnet.
- **Gate mode, `resume_handoff` into an implement phase** → Sonnet/medium (plan is locked, tasks are mechanical-to-moderate). The resume already reloaded context, so if the remaining work is gnarly it's a cheap moment to land on Opus/high instead — the reload tax is already paid.
