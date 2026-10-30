---
name: model-help
description: Given a handoff file, task spec, ticket, or pasted work description, recommend which Claude model + reasoning-effort level to run it at (and whether to split it into tiers). Use when the user asks "what model/effort should I use", "which effort level", "tier this task", "model advice for this handoff", or hands over a task/handoff and asks how to run it. Also runs in "gate mode" inside the wb workflow — forge, resume_handoff, and the create_*/implement/validate phase skills consult it to pick the model + effort for the phase about to run and to decide whether switching the main model is worth the context-reload cost. Advice only — it does not do the work.
allowed-tools: Read, Glob, Grep
---

# /wb:model-help — pick the model + effort for a task

Read a handoff / task spec / ticket and return a **model + effort** recommendation with a one-paragraph rationale. Advice only — never start the implementation.

## Input

- A file path (e.g. a `/tmp/*-handoff.md`, a `docs/plans/**/tasks.md`, a ticket export) — read it fully.
- Or pasted content in a handoff-ish shape (scope, file refs, decisions, open questions).
- Or a **gate call from the wb workflow**: a phase name (`research` / `design` / `execution` / `implement` / `validate`) plus the project docs (or handoff) and, if known, the model the session is currently on. Advise the tier for *that phase* and whether to switch — see [Gate mode](#gate-mode--advising-a-wb-workflow-phase) below.
- If nothing is provided, ask for the handoff/spec (one line) and stop.

## The two axes (pick each independently)

**Model = capability ceiling.** How much raw reasoning the hardest part of the task needs.
**Effort = how much thinking to spend** at that ceiling. A cheap model at high effort ≠ a strong model at low effort — match model to the ceiling, effort to the depth.

Current roster (most → least capable): **`claude-fable-5-1` (Fable 5.1)** · **`claude-opus-5-5` (Opus 5.5)** · **`claude-sonnet-5-5` (Sonnet 5.5)** · **`claude-haiku-5-5` (Haiku 5.5)**. **Opus 5.5 is the default main-session model.** Fable 5.1 is the top rung and never a default. Effort levels: `low` · `medium` · `high` · `xhigh` · `max`, and all four models support every level. Price per million input / output tokens: Fable 5.1 $10 / $50, Opus 5.5 $4 / $20, Sonnet 5.5 $2 / $10, Haiku 5.5 from $0.10 / $0.50.

**1M-context variants.** Append `[1m]` to a model ID for the wide-context form, for example
`claude-opus-5-5[1m]`. Reach for one when the
task must hold a lot at once — a whole-subsystem audit, a cross-file refactor, a long plan —
not as a general upgrade: a wider window costs more per token and does nothing for a task that
fits comfortably.

**This roster is for the *main session*, set with `/model`.** Sub-agent spawns are a different
mechanism with a narrower vocabulary: the spawn tool's `model` parameter is an enum of
`haiku · sonnet · opus · fable`, so no full identifier and no `[1m]` variant can be pinned per
spawn. A spawn can also pass `effort`, which overrides the agent file's `effort`.
`/wb:implement`'s Step 5 states the worker ladder in those four values, and is the single
statement of it. Advising a worker tier by full model ID would name something the spawner cannot
select.

**One Opus, and effort before Fable.** Opus 5.5 is the one current Opus. At `medium` it matches or exceeds the previous Opus at `high` on coding and knowledge work (Anthropic's Opus 5.5 prompting guide), so raise its effort before you reach for Fable 5.1. Reserve Fable 5.1 for the genuinely hardest work: novel design, one-way doors, compliance / PHI / security-critical changes, and the escalation after a verified failure.

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
| Trivial, isolated, easily verified — copy tweaks, config bumps, a rename, doc edits, a single obvious factory/spec | Haiku 5.5 (or Sonnet 5.5) | low |
| Bounded eng change, mechanical but touches a hot path or needs edge/nil-safety reasoning + real specs | Sonnet 5.5 | medium |
| Multi-file feature, non-trivial logic, moderate correctness sensitivity, some design latitude | Opus 5.5 | medium |
| Compliance / PHI / security / billing critical · wide blast radius · novel design · hard-to-reverse migration · adversarial review of sensitive code | Opus 5.5 (Fable 5.1 for novel or one-way-door work) | high |

### The upshift ladder (D12 — election, never baseline)

Every tier above a phase's baseline is reached by **explicit election**, never by a stage
choosing it automatically. The ladder, from any starting point:

```
Haiku 5.5  →  Sonnet 5.5  →  Opus 5.5  →  Fable 5.1
```

Two rules make it a ladder rather than a menu:

- **One rung at a time, and say which rung and why.** Jumping two rungs on a failure tells you
  nothing about which rung would have sufficed.
- **Fable is the top rung and is never a default.** It is available — for architecture-critical
  discussion, for decomposition, and as the escalation after a *verified* failure — but nothing
  in the pipeline routes to it on its own. Wherever Fable is used, effort is **`high`**, never
  `xhigh` or `max`: on long deliverables at higher settings it drafts in thinking and then
  writes again, roughly doubling output for a patch-plus-report shaped task.

This skill **advises** the election; it never makes it. That is the same advise-never-auto-switch
policy the switch-cost rule below enforces.

Effort guidance: **medium is the default for real eng work**, and it is the Claude Code default for Opus 5.5, Sonnet 5.5, and Haiku 5.5. Drop to **low** only when genuinely mechanical. Reserve **high** for hard reasoning / review; **xhigh/max** for the thorniest multi-constraint problems or adversarial verification — they cost real time/tokens with diminishing returns, so don't reach for them by default.

## Splitting

If the handoff has parts with different ceilings, **recommend splitting** and tier each part — e.g. "migration alone → Sonnet/low; the hot-path resolver change + specs → Sonnet/medium." Don't average a spiky task down to one tier.

## Gate mode — advising a wb workflow phase

The wb pipeline (`forge`, `resume_handoff`, and the `create_*` / `implement` / `implement_inline` / `validate_execution` skills) consults this skill at phase boundaries. Not every phase needs the same tier, but **switching the main-session model reloads the whole conversation** — so the goal is to spend the right amount per phase *without* churning the model. Two levers, very different costs:

- **Sub-agent model + effort is free** — each spawned agent is fresh context. Push cheap, parallelizable work down to cheap agents aggressively (each agent file in `agents/*.md` sets its own model and effort). This is where most cost optimization lives, and it never touches the main session.
- **Main-session model/effort costs a context reload** on every switch (tokens + latency). An effort change also invalidates the prompt cache, so treat it as a smaller switch. Advise a main-session switch only when it pays for that tax.

### Per-phase baseline (then modulate by the ticket's difficulty via the dimensions above)

| wb phase | Main-session baseline | Why | Cheap work → sub-agents |
| --- | --- | --- | --- |
| `create_research` | Opus 5.5 / medium | Main session decomposes + synthesizes; the heavy lifting is in parallel read-only agents | the agent files set the tiers: locator → haiku, analyzer → sonnet, pattern-finder → haiku |
| `create_design` | **Opus 5.5 / high** (→ Fable 5.1 / high for novel / one-way-door / compliance-critical / high-blast-radius) | Reasoning-dense: trade-offs, architecture, locked decisions. Usually the pipeline's ceiling | little to delegate — the judgment is main-session |
| `create_tasks` | Opus 5.5 / medium (upshift: Opus 5.5 / high) | Decompose an already-decided design into phased tasks — structuring, not deciding. Upshift when decomposition quality sets the ceiling for cheap workers | analysis agents, at their agent-file tiers |
| `implement` | Opus 5.5 / medium | Coordination, not coding: extract context, spawn, verify, commit. The main session holds little | **workers carry the cost, and their tiers are pinned at the point of spawn** — see `implement`'s Step 5, the single statement of the worker ladder. The verifier runs at its agent file's tier unless the [Verifier tier](#verifier-tier) rule upshifts it |
| `implement_inline` | Opus 5.5 / medium (bump gnarly tasks to Opus 5.5 / high) | TDD execution of a locked plan **on the session model**; most tasks mechanical-to-moderate. Nothing is delegated, so the session tier *is* the execution tier | nothing — use `/wb:implement` if you want work pushed to workers |
| `validate_execution` | Opus 5.5 / high (→ Fable 5.1 / high for compliance-critical / hard-to-verify) | Adversarial check vs plan; raise for wide blast radius / compliance / hard-to-verify | validation agents, at their agent-file tiers |
| `adversarial-review` | Opus 5.5 / high (→ Fable 5.1 / high for compliance-sensitive, wide-blast-radius or hard-to-verify diffs) | The session resolves the target, sizes the pass and synthesizes; the reading is done by forked agents and a forked built-in review | **the legs carry the cost** — lens agents at `sonnet`, security and AI-systems at `opus`, verifiers at `sonnet`; see `adversarial-review`'s prompts.md |
| `adversarial-loop` | Opus 5.5 / medium | A sequencer: it orders rounds and holds gates, and contains no review logic of its own | everything — the review it invokes carries its own tier, and `/verify` carries its own |
| `update_status`, `validate_project` | Sonnet 5.5 / medium (upshift: Opus 5.5 / medium) | Mechanical: count checkboxes, compare documents to rules | nothing |

### Where this skill's authority ends

**Anything spawned is pinned at its definition; anything the session itself runs is advised
here.** Sub-agent tiers live in `agents/*.md` frontmatter, and the coordinated worker ladder
lives in `implement`'s Step 5 — this skill does not restate either, because two statements of a
tier rule drift. What it does own is the **main-session** tier for every phase, the
switch-cost judgment about whether changing it is worth the reload, and the one per-spawn
exception below: the verifier upshift.

### Verifier tier

`implement`'s Step 6b reads this section before each `wb:task-verifier` spawn. The agent file
pins `sonnet` at `high`, and that pin is the default. Most tasks verify well at it, and a
verifier runs once for every task. Spending Opus on every check doubles the cost of the
cheapest gate in the loop.

**Upshift one rung, to `opus`, when any of these holds.** Effort stays `high`.

| Condition | Why Sonnet is not enough |
| --------- | ------------------------ |
| The task scores HIGH on **correctness sensitivity**: PHI, security, auth, billing, data integrity, or an irreversible migration | A defect the verifier misses ships, and it is expensive |
| The task scores HIGH on **verification cost**: the mistake hides until production, and the tests cannot show it | The verifier must reason past the green suite, not read it |
| The task scores HIGH on **blast radius**: it edits a shared hot path or a load-bearing method | A scope check must hold every caller in mind |
| This is the **re-verification after a Step 6c escalation** | The task already failed once. This check is the last one before the commit |

Score the task's body against the dimensions at the top of this skill. Do not match keywords
in its title. When none of the conditions holds, pass no `model` on the spawn, so the agent
file's pin applies.

- **Never `fable`.** A verifier checks a diff against a stated task. It does not design, and the
  top rung buys nothing for that.
- **Say which rung and why, in one line**, as the upshift ladder requires. For example:
  `Verifier: opus — P2-T3 edits the session token check (correctness sensitivity HIGH).`
- **The upshift is per task.** The next task starts again at the default.

Bump a phase above its baseline whenever the ticket's own dimensions (blast radius, correctness sensitivity, novelty, cross-file reasoning, verification cost) say so — a research pass over an ambiguous cross-subsystem area is Opus 5.5 / high, not Opus 5.5 / medium.

### The switch-cost rule (this is what keeps it from being noisy)

Advise a **main-session** switch only when **both** hold:

1. the recommended tier differs from the current session by **≥ 1 model step**, and
2. the phase is **substantial** (long reasoning or many tool calls — e.g. design, or a large implement phase), so the reload pays off.

Then:

- **Cluster same-tier phases.** Most phases sit on Opus 5.5, so a forge usually needs no model switch: design and validation raise the effort to `high`, and the other phases stay at `medium`. Switch **up** to Fable 5.1 only for a novel or one-way-door design gate, then back down. A whole forge should cost 0–2 switches, not 5.
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

- **`adversarial-review` on a compliance-sensitive, cross-file change** → Opus 5.5 / high. The review's own reconnaissance sizes its fan-out; this is the *session* tier, and it is what the mandatory security and AI-systems lenses are judged at. Bump to Fable 5.1 / high for a focused pass on the part that cannot be taken back.
- **Add a nullable column + a one-line resolver change on a ~140-call-site hot path + form field** (e.g. TB-2936 Zoom `zoom_url`) → Sonnet 5.5 / medium; the migration alone would be Sonnet 5.5 / low.
- **Copy change / locale tweak / config bump** → Haiku 5.5 / low.
- **Gate mode, a moderate forge** (bounded feature, decisions still open) → research Opus 5.5 / medium → design Opus 5.5 / high → `create_tasks` + `implement` Opus 5.5 / medium → validate Opus 5.5 / high. No model switch, and two effort changes.
- **Gate mode, `resume_handoff` into an implement phase** → Opus 5.5 / medium (plan is locked, tasks are mechanical-to-moderate). The resume already reloaded context, so if the remaining work is gnarly it's a cheap moment to land on Opus 5.5 / high (or Fable 5.1 / high if it's genuinely the hardest part) instead — the reload tax is already paid.
