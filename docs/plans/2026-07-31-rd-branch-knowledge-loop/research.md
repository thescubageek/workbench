---
project: rd-branch-knowledge-loop
ticket: N/A
created: 2026-07-31
status: complete
last_updated: 2026-07-31
last_updated_note: "Resolved all 6 open questions via /wb:resolve_questions (interim; promote in create_design)"
researcher: Steve Craig
git_commit: 5b027235be6a6bd898dd8fc6578de254018d50d8
git_branch: thescubageek/self-learning-loops-research
repository: thescubageek/workbench
research_type: external-literature + codebase
---

# Research: R+D Branch as a Self-Learning Knowledge Base

**Created**: 2026-07-31
**Last Updated**: 2026-07-31
**Ticket**: N/A

## Research Question

What is the current (mid-2026) state of the art in **self-learning loops** and **forward deployed
engineering**, and what do those two bodies of practice say about the specific architecture the user
described: a **centralized R+D branch that acts as a common knowledge base** which other
tickets/tasks/agents read from and write back to, used for **long-horizon SWE project management**?

## Scope and Method

This document has two kinds of content and keeps them separated on purpose:

- **Parts 1–4 are facts.** Part 1–2 document what the external literature and industry practice
  actually say, with sources. Part 3 is a synthesis *of those sources* — the mapping is labeled where
  it is inference rather than citation. Part 4 documents what exists in this repository today, with
  `file:line` references, per the Documentarian Rule (`commands/create_research.md:13`).
- **Part 5 is design input, not decisions.** The user asked how this *could* be implemented. Part 5
  enumerates the surfaces and mechanisms available, with the trade-off each carries. Nothing in Part 5
  is a decision; decisions belong in `design.md` via `/wb:create_design`.

Verification notes:

- All external claims are attributed. Quantitative results are attributed to the specific paper or
  post that reported them; none were independently reproduced.
- `bd` is **not** installed in this workspace and there is no `.beads/` directory, so open questions
  are listed in this document rather than filed as beads issues. Per `docs/beads-fast-fail.md`
  semantics, the correct next step is `bd init` before running the pipeline commands that assume beads.

## Summary

The industry has converged, over roughly the last twelve months, on the position that the improvable
unit of an AI coding system is **the harness, not the model weights** — the system prompt, tool
descriptions and implementations, skills, sub-agent configuration, middleware, and long-term memory
that surround the model. Lilian Weng's July 2026 survey frames this as "harness engineering," and the
concrete systems under it (ACE, GEPA, Self-Harness, AHE, CODESKILL, DGM) all share the same shape:
run the agent, capture the trajectory, mine failures into candidate edits to the harness, and **accept
an edit only if it survives a validation gate**. The reported gains are large and reproducible enough
to take seriously — Self-Harness moved MiniMax M2.5 from 40.5% to 61.9% on Terminal-Bench 2.0 with no
weight updates, and AHE moved a coding harness from 69.7% to 77.0% pass@1 over ten iterations. Just as
consistent across the literature is *how these loops fail*: context collapse from full-prompt rewrites,
reward hacking against weak evaluators, skill bloat, negative transfer, and — most relevant to a shared
knowledge base — persistence of injected content once the agent is allowed to write its own memory.

Forward deployed engineering is the organizational half of the same loop. Palantir's model, now being
copied by Anthropic, OpenAI, Google, Databricks and Cohere, is not "consultants who code": the
load-bearing mechanic is that **the engineer embedded in the field is also the primary input channel
to the platform**. Reported practice is an explicit split — roughly 30–40 hours embedded with operators
plus one day a week on platform engineering — and an explicit routing rule: product feedback goes
through the FDE rather than around them. The documented critique is equally instructive: Anaplan's CEO
argues FDE is "a good selling model… not a great model for running the software," because without the
generalization step it produces permanent vendor dependency instead of a better platform. In other
words, **the write-back is the whole thing**. An FDE loop with no productization step is just
consulting, and a self-learning loop with no promotion gate is just log accumulation.

Mapped onto the user's architecture, the R+D branch is the **platform** and each ticket is a
**deployment**. That framing is what makes the two literatures actionable together: the branch holds
itemized, provenance-stamped, independently-verifiable knowledge (ACE's playbook, CODESKILL's skill
library, FederatedSkill's shared repository); each ticket reads from it at bootstrap and proposes deltas
back; and a promotion gate decides what generalizes (Self-Harness's validation stage, FDE's
productization step, FederatedSkill's quality filter). The workbench today already has most of the
*read* path and most of the *verification* machinery — `create_research` has a bootstrap hook point at
`commands/create_research.md:47-60`, `resume_handoff` has an explicit "Apply Learnings" step at
`commands/resume_handoff.md:158`, `agents/research-validator.md` already emits a `STALE` verdict that is
precisely a staleness detector, and `skills/touch-grass/SKILL.md:47-58` already specifies a durable
cold-resume state contract. What it does not have is a **destination**: four separate commands tell the
agent to capture learnings (`commands/validate_execution.md:381`,
`commands/create_handoff.md:214`, `commands/implement_tasks.md:494`,
`commands/implement_coordinated.md:652`) and every one of them terminates in a per-ticket file or a
one-shot handoff. The observable consequence is already in the repo:
`docs/beads-integration-learnings.md` is a hand-written learnings artifact from 2026-01-31 whose
Learning 5 recommends `TodoWrite`, which `CLAUDE.md` now explicitly forbids — a captured learning that
went stale with no mechanism to notice.

---

## Part 1 — Self-Learning Loops: External State of the Art

### 1.1 The improvable unit moved from weights to the harness

[Lilian Weng's "Harness Engineering for Self-Improvement"](https://lilianweng.github.io/posts/2026-07-04-harness/)
(2026-07-04) defines a harness as "the system surrounding a base model that orchestrates execution and
decides how the model thinks and plans, calls tools and acts, perceives and manages context, stores
artifacts, and evaluates results." The survey's organizing claim is that optimizing this layer is a
distinct and currently under-exploited axis from training better weights.

Three design patterns recur across the systems it surveys:

- **Goal-oriented loops** — plan → execute → observe/test → improve, where the agent analyzes its own
  trajectories rather than being re-prompted by a human.
- **File system as persistent memory** — long-horizon agents store artifacts (experiment logs, diffs,
  error traces) as durable files rather than carrying them in context. This is called out as
  deliberately simple and generic, aligned with existing software-engineering practice.
- **Sub-agents and background jobs** — explicit, inspectable parallelism, with sub-agent outputs
  written to files so a run is recoverable after interruption and reasoning over execution history is
  possible.

The [bdtechtalks primer on self-improving harnesses](https://bdtechtalks.substack.com/p/a-primer-on-self-improving-agent)
makes the same point from the practitioner side: these frameworks update prompts, executable rules,
tool-calling logic, retry discipline, memory and context-assembly — **without touching model weights**
— and the practical advice to engineers is to stop hand-tweaking prompts and instead build "infrastructure,
trace logging, and evaluation datasets that make agent self-improvement possible."

### 1.2 What specifically gets written back

[Agentic Harness Engineering (AHE)](https://arxiv.org/abs/2604.25850) (Lin et al., arXiv:2604.25850,
April 2026) gives the most useful enumeration for our purposes. It names **seven editable harness
components**, each with a file-level representation so the action space is explicit and revertible:

1. System prompt
2. Tool description
3. Tool implementation
4. Middleware
5. Skill
6. Sub-agent configuration
7. Long-term memory

That list maps almost one-to-one onto a Claude Code plugin's directory layout, which is why this
literature is unusually directly applicable to the workbench (see Part 4).

### 1.3 The three invariants of loops that actually work

Across the systems surveyed, three mechanisms separate loops that improve from loops that drift. Each
comes from a different paper and each addresses a different failure.

**Invariant 1 — Update by itemized delta, never by rewriting the whole artifact.**
[ACE (Agentic Context Engineering)](https://arxiv.org/html/2510.04618v1) (arXiv:2510.04618) treats
context as "an evolving playbook rather than an increasingly lengthening prompt," structured as
itemized `(identifier, description)` bullets. Its three roles are **Generator** (runs the task, records
the trajectory), **Reflector** (distills insight from success/failure), and **Curator** (emits compact
delta updates — new or changed bullets — merged in by deterministic logic, with periodic dedup). The
stated reason for the delta discipline is to prevent **context collapse and brevity bias**: monolithic
rewrites progressively lose accumulated detail. Reported result: ReAct + ACE outperforms the selected
baselines by 10.6% on average, and works even without ground-truth labels. An open-source
implementation exists ([ace-agent/ace](https://github.com/ace-agent/ace)).

**Invariant 2 — Pair every edit with a falsifiable prediction, and revert at file granularity.**
AHE's contribution is three "matched observability pillars": *component observability* (every editable
component is a file, so edits are explicit and revertible), *experience observability* (millions of raw
trajectory tokens distilled into a layered, drill-down evidence corpus an evolving agent can actually
consume), and *decision observability* (**every proposed edit carries a self-declared prediction, which
the next round verifies against task-level outcomes; failures are reverted per-file**). The paper
frames this as converting harness evolution from trial-and-error into falsifiable contracts. Reported
result: 69.7% → 77.0% pass@1 after ten iterations, outperforming hand-built harnesses (OpenCode,
Terminus-2) on Terminal-Bench-2 and transferring to SWE-bench-verified without further evolution.

**Invariant 3 — Accept a proposed edit only after regression on a held-out split.**
[Self-Harness](https://arxiv.org/abs/2606.09498) (arXiv:2606.09498, Shanghai AI Laboratory, June 2026)
runs a three-stage loop: **weakness mining** (cluster failures from execution traces into
verifier-grounded, model-specific patterns), **harness proposal** (generate diverse but *minimal* edits
tied to those specific patterns), and **proposal validation** (accept only after regression testing on
held-in / held-out splits). Reported results on Terminal-Bench 2.0, with no weight updates:

| Base model | Seed harness | After Self-Harness | Relative gain |
| --- | --- | --- | --- |
| MiniMax M2.5 | 40.5% | 61.9% | +52.6% |
| Qwen3.5-35B-A3B | 23.8% | 38.1% | +60.1% |
| GLM-5 | 42.9% | 57.1% | +33.1% |

The paper's stated key insight is that it does not add generic instructions — it turns *model-specific
weaknesses* into concrete, executable harness changes.

### 1.4 Adjacent mechanisms worth knowing

- **[GEPA](https://arxiv.org/abs/2507.19457)** (arXiv:2507.19457, ICLR 2026 Oral) — reflective prompt
  evolution: mutate prompts using natural-language feedback from rollouts, and maintain a **Pareto
  front** across problem instances rather than a single best candidate, to avoid local optima. Reported:
  beats GRPO by 6% on average and up to 20% while using **up to 35× fewer rollouts**; beats MIPROv2 by
  >10%. The relevant lesson for a knowledge base is the Pareto-front idea: keep the diverse set of
  entries that each win on *some* instance rather than collapsing to one "best practice."
- **[CODESKILL](https://arxiv.org/pdf/2605.25430)** (arXiv:2605.25430) — self-evolving skills for
  coding agents, managed through four lifecycle operations: **add / update / merge / deprecate**, driven
  by downstream task success. Named failure modes: **skill bloat** (unbounded repository growth degrades
  retrieval), **retrieval noise** (irrelevant skills rank high and mislead), and **overfitting** (skills
  too specialized to generalize).
- **Meta Context Engineering (MCE)** (via Weng) — bi-level optimization that separates the *mechanism*
  of context management from the *content* of the artifact, so the two can be improved independently.
- **Darwin Gödel Machine (DGM)** (via Weng) — agents modifying their own harness codebase, with new
  candidates admitted only if sufficiently high-performing. Reported 20–50% improvement on SWE-bench
  Verified and 14.2–30.7% on Polyglot versus hand-built agents.
- **HarnessX / AEGIS** (via bdtechtalks) — modular harness components plus harness-model co-evolution
  via GRPO, reported at +4.7% beyond harness-only optimization.
- **[Memory Transfer Learning](https://arxiv.org/pdf/2604.14004)** (arXiv:2604.14004) — measures what
  transfers across coding domains. **Transfers:** general problem-solving and debugging strategies, code
  patterns and implementation templates, cross-cutting domain knowledge. **Does not transfer:**
  task-specific implementation details, domain-unique APIs and syntax, highly specialized problem
  structures. Failure modes: **negative transfer** (a wrong prior strategy actively degrades a
  dissimilar task), **staleness**, **over-specificity**.
- **[FederatedSkill](https://arxiv.org/pdf/2606.03143)** (arXiv:2606.03143) — many independent agents
  keep local skill libraries and *selectively* contribute to a shared one. Contributions are validated
  before integration; low-performing or poorly-generalized ones are rejected; conflicting
  implementations are arbitrated on demonstrated performance. Only finalized skills are shared, not raw
  experience.
- **[Always-On Agents survey](https://arxiv.org/pdf/2606.30306)** (arXiv:2606.30306) — the governance
  vocabulary for persistent memory: **write policies** (what may enter), **provenance tracking**
  (origin and modification history), **review/approval** before memory updates, **decay/eviction**, and
  **conflict resolution** across distributed memory. Its named open problems are exactly the multi-agent
  shared-memory ones: coordination, poisoning, access control, consistency, conflicting updates.

### 1.5 Documented failure modes

Consolidated from Weng's survey unless otherwise attributed. These are the constraints any design has
to answer to.

| Failure mode | Mechanism | Source |
| --- | --- | --- |
| **Context collapse / brevity bias** | Monolithic rewrites of a growing artifact progressively lose detail | ACE |
| **Reward hacking** | The loop optimizes whatever signal it is given — overfits unit tests, exploits benchmark artifacts. Mitigation: held-out tests, trace audits, human review | Weng |
| **Weak/fuzzy evaluators** | Loops need measurable, objective signal. Research taste, novelty, and long-term value resist quantification | Weng |
| **Diversity collapse** | Evolutionary/RL loops exploit known patterns and converge to local optima | Weng; GEPA's Pareto front is the counter |
| **Capability threshold** | STOP improved with GPT-4 but *degraded* with GPT-3.5 and Mixtral — self-improvement requires a sufficiently capable base model | Weng (STOP) |
| **Implementation drift** | Under complexity pressure models regress toward simpler solutions than the ones they proposed | Weng (Trehan & Chopra 2026 replication) |
| **Over-optimism / p-hacking** | Models declare success on noisy or failed experiments and add "numerical duct tape" absent real signal | Weng |
| **Negative-results bias** | Trained on success-biased literature, models are bad at abandoning hypotheses and reporting failure | Weng |
| **Long-horizon blindness** | Short-term task completion does not capture maintainability, ownership, migration cost, backward compatibility, debugging burden | Weng |
| **Skill bloat / retrieval noise / overfitting** | Unbounded library growth degrades retrieval; irrelevant entries mislead; narrow entries don't generalize | CODESKILL |
| **Negative transfer** | A retrieved prior strategy makes a dissimilar task *worse* than no memory | Memory Transfer Learning |
| **Stale retrieval** | Vector indexes don't update when code changes; agents retrieve deleted logic and outdated signatures | [supermemory](https://supermemory.ai/blog/memory-bottleneck-large-repo-coding-agents/) |
| **Self-reinforcing injection ("zombie agents")** | Injected payloads written into memory survive and propagate through self-evolution, masquerading as learned patterns; the refinement process *legitimizes* them; standard defenses are inadequate | [arXiv:2602.15654](https://arxiv.org/pdf/2602.15654) |
| **Uncontrolled drift / loss of auditability** | Agents freely modifying their own constraints drift incrementally, lose auditability, and can circumvent safety mechanisms through undocumented changes | [CAAF, arXiv:2604.17025](https://arxiv.org/pdf/2604.17025) |

Two further calibration points from Weng worth holding onto for a *long-horizon* system specifically:

- On **RE-Bench**, the best AI scored roughly 4× human experts at a 2-hour budget, but **human experts
  exceeded agents at 8-hour and 32-hour budgets**. Agent advantage is currently concentrated at short
  horizons; long horizons are where the harness has to carry the weight.
- The survey's explicit stance: *"Humans should move up the stack, not be removed from the loop."*
  Good design creates oversight touchpoints at the right abstraction level.

---

## Part 2 — Forward Deployed Engineering: External State of the Art

### 2.1 What the role is

Per [MarkTechPost's 2026-05-20 overview](https://www.marktechpost.com/2026/05/20/what-is-a-forward-deployed-engineer-the-ai-role-openai-anthropic-and-google-are-hiring-in-2026/),
an FDE "works embedded with the customer's technical and operational environment," writing and
iterating production code inside client infrastructure and staying engaged until the system runs
reliably in production. The article's role contrasts are the crisp part:

| Role | Distinction drawn |
| --- | --- |
| Consultant | "Consultants write reports and recommendations; an FDE builds the actual system and stays until it runs in production" |
| Solutions architect | Handles planning/design; the FDE owns implementation delivery |
| Product engineer | Product engineers ship features; FDEs ship customer *outcomes* |

Named artifacts of the practice include **custom evaluation suites** built from real-world examples —
the cited OpenAI/John Deere engagement involved "reviewing hundreds of real-world examples, building
custom evaluation systems to measure accuracy, and iterating."

### 2.2 The mechanic that matters here: field → platform

The load-bearing claim, and the reason this belongs in the same document as self-learning loops:
**"FDE field work feeds the product roadmap; every deployment pattern you find shapes future platform
features."**

The [Perspective AI writeup of Palantir's playbook](https://getperspective.ai/blog/palantir-forward-deployed-engineering-playbook-anthropic-openai-copying)
describes the operating mechanics:

- **An explicit time split.** Roughly 30–40 hours embedded with analysts and operators, plus **one day
  per week on platform engineering**. The generalization work is scheduled, not incidental.
- **Ontology-first.** FDEs model the customer domain into a Foundry ontology — entities, properties,
  relationships. That artifact is simultaneously the deployment foundation *and* the translation
  mechanism for platform generalization. One artifact serves both the local job and the shared layer.
- **Discovery is engineering, not a separate research function.** 5–10 deep conversations per week are
  treated as core engineering work; unstructured data shapes both the customer ontology and the next
  platform release. (MarkTechPost separately reports AI FDEs spending 30–40% of the week on
  conversational discovery.)
- **A routing rule: "Route product feedback through the FDE."** The embedded engineer is the *primary*
  product-management input channel, not a secondary voice.
- **No handoff seam.** FDEs "own the entire data-to-decision loop," so customer-specific work feeds back
  as generalizable patterns without a handoff boundary to lose fidelity across.

Adoption is broad as of mid-2026: [MindStudio](https://www.mindstudio.ai/blog/palantir-forward-deployed-engineer-model-anthropic-openai)
reports Anthropic, OpenAI, Google DeepMind, Databricks and Cohere copying the model directly.

### 2.3 The internal analogue

The same loop, run on yourself, is the documented
[dogfooding-with-rapid-iteration pattern](https://www.agentic-patterns.com/patterns/dogfooding-with-rapid-iteration-for-agent-improvement/):
the team building an agent uses it as their primary daily tool. Signals collected are direct
observation of strengths and weaknesses during real work, real-world complexity that test environments
miss, usage patterns across the team, and honest assessment of feature utility. What makes it work is
loop *tightness* — pain points are felt immediately and iterated within hours. Named cost: it requires
high internal adoption, and internal users may not represent all segments. This is the closest published
analogue to a single engineer running an R+D branch that improves the tooling they use on every ticket.

### 2.4 The documented critique

The critique is important because it names the exact failure a knowledge base is supposed to prevent.
In [Forbes (2026-07-10)](https://www.forbes.com/sites/stevebanker/2026/07/10/palantir-and-forward-deployed-engineering-what-should-we-believe/),
Anaplan CEO Charlie Gottdiener argues FDE excels at "showing up and doing a POC" with a "nice-looking
dashboard," but creates perpetual reliance on vendor engineers, limited functionality, and lock-in —
concluding "It's a good selling model… It's not a great model for running the software. Not at all."
The article also cites a 2025 MIT Media Lab finding that 95% of generative-AI pilots fail to deliver
business value, and notes successful exceptions (CH Robinson's automated quoting) plus Kinaxis's
position that FDE works when executed with domain expertise rather than engineering talent alone.

**The synthesis:** an FDE loop whose field work never generalizes back into the platform degenerates
into permanent bespoke maintenance. That is structurally the same failure as a self-learning loop that
accumulates trajectories but never promotes anything into the harness. In both cases the missing
component is the **promotion gate** — the step that decides what generalizes and admits only that.

---

## Part 3 — The Convergence: R+D Branch as Platform, Ticket as Deployment

This part is synthesis across the sources in Parts 1–2. The correspondence below is inference, not a
claim any single source makes.

The user's architecture — a centralized R+D branch acting as a common knowledge base for other
tickets/tasks/agents — has a direct analogue in both literatures, and the analogues agree on structure:

| Concept | Self-learning-loop term | FDE term | R+D-branch term |
| --- | --- | --- | --- |
| The shared, improvable artifact | Playbook (ACE) / skill library (CODESKILL) / shared repository (FederatedSkill) | The platform; the ontology | The R+D branch |
| The local unit of work | A rollout / trajectory | A customer deployment | A ticket / task / agent run |
| Reading shared knowledge in | Context assembly / retrieval | Reusing platform primitives | Bootstrap at research time |
| Writing local learning out | Curator delta / skill add-update | Productization; "route feedback through the FDE" | Promotion proposal |
| The admission decision | Proposal validation on held-out split (Self-Harness); quality filter (FederatedSkill) | The one-day-a-week platform slot | The promotion gate |
| Detecting that knowledge went bad | Staleness / negative transfer | Deployment regression | Re-validation against HEAD |
| Preventing unbounded growth | Merge/deprecate (CODESKILL); dedup (ACE) | Deprecating bespoke forks | Curation pass |

Four structural properties fall out of this that are specific to the *long-horizon* case and are worth
stating explicitly, because they are what distinguishes this from "just write good docs":

1. **Knowledge must be addressable at entry granularity, not document granularity.** ACE's reason is
   context collapse; the R+D-branch reason is additionally mechanical — N concurrent ticket agents
   proposing edits to one shared artifact will conflict at document granularity and will not conflict at
   itemized-entry granularity. The same design choice solves both problems.
2. **Every entry needs provenance, and provenance is what makes staleness computable.** The
   [supermemory analysis](https://supermemory.ai/blog/memory-bottleneck-large-repo-coding-agents/) names
   stale retrieval as a primary large-repo failure: indexes don't update when code changes, so agents
   retrieve outdated signatures and deleted logic. The multi-scope pattern reported in the
   [mem0 2026 memory review](https://mem0.ai/blog/state-of-ai-agent-memory-2026) tags each write with
   identity scopes (user / agent / session / org) with documented precedence rules for conflicts. In a
   git-native knowledge base the strongest available provenance is free: the commit SHA the entry was
   verified against, plus the files it cites. An entry is *suspect* exactly when those files changed
   since that SHA — which is a computable predicate, not a judgment call.
3. **The admission gate is the component that cannot be skipped.** This is the one point where
   Self-Harness, FederatedSkill, DGM, and the FDE critique all independently agree. Self-Harness accepts
   only after held-out regression; FederatedSkill rejects low-performing or poorly-generalized
   contributions and arbitrates conflicts on demonstrated performance; DGM admits new candidates only if
   sufficiently high-performing; the FDE critique says the model rots without the productization step.
4. **Write access to shared memory is a security boundary, not just a quality one.** The zombie-agents
   result ([arXiv:2602.15654](https://arxiv.org/pdf/2602.15654)) is that injected content written into
   agent memory *survives and propagates* through self-evolution and is legitimized by the refinement
   process — it stops looking like an attack and starts looking like a learned pattern. A shared R+D
   branch read by every subsequent ticket is, by construction, a supply chain. Anything that can write
   to it can influence every future run.

And one honest counterweight, from CAAF ([arXiv:2604.17025](https://arxiv.org/pdf/2604.17025)): the
harness should be treated as a **versioned engineering asset** subject to normal engineering discipline
— version control, testing, validation — precisely because unconstrained self-modification produces
uncontrolled drift, loss of auditability, and cascading failures. For a plugin whose entire content is
prompts that steer other work, this argues for the loop's *output* being a reviewable diff on a branch
rather than a live-mutating store. Which is, conveniently, what a git branch already is.

---

## Part 4 — What Exists in the Workbench Today

### 4.1 Inventory

At `5b02723` on `thescubageek/self-learning-loops-research` (93 commits), plugin version **1.12.3**
(`.claude-plugin/plugin.json:3`):

- **16 commands** in `commands/` — the pipeline (`create_project`, `create_research`,
  `create_product_research`, `create_mockup`, `create_design`, `create_execution`, `implement_tasks`,
  `implement_coordinated`, `validate_execution`, `validate_project`), continuity
  (`create_handoff`, `resume_handoff`, `update_status`, `resolve_questions`), orchestration (`forge`),
  and `help`.
- **6 agents** in `agents/` — `codebase-locator`, `codebase-analyzer`, `pattern-finder`,
  `product-behavior-analyzer`, `research-validator`, `task-verifier`.
- **15 skills** in `skills/` — `clip`, `daily-digest`, `eli5-clip`, `fetch-issues`, `jira-context`,
  `mockup-iteration`, `model-help`, `project-structure`, `research-validation`, `review-prep`,
  `status-sync`, `tdd-discipline`, `touch-grass`, `tracer-bullet`, `verification-before-completion`.
- **2 hook events** (`.claude-plugin/plugin.json:10-45`) — `SessionStart` →
  `hooks/setup-beads-mode.sh` (timeout 5); `PostToolUse` matching `Write` and `Edit` →
  `scripts/lint-hook` (timeout 5). No `Stop`, `SubagentStop`, `PreCompact`, `UserPromptSubmit`, or
  `PreToolUse` hooks are registered.
- **Automated gates** — `scripts/lint` / `scripts/lint-hook` (markdown lint only) and
  `scripts/test-quiet`, which is a contract test for `scripts/quiet`'s output behavior. There is no
  automated check of any kind over the *prompts* — the actual product.
- `.claude/settings.json` is an empty object (`{}`).
- No `.beads/` directory and no `bd` binary in this workspace.

### 4.2 The pipeline is per-ticket and it terminates

`commands/forge.md:26-38` defines the sequence:

```text
[optional] /wb:create_project
         ↓
/wb:create_research      → document what EXISTS
         ↓ ⛔ BARRIER: stakeholder Qs resolved
/wb:create_design        → decide WHAT and WHY
         ↓ ⛔ BARRIER: decisions made
/wb:create_execution     → plan HOW; creates beads issues
         ↓ ⛔ BARRIER: user confirms ready to implement
/wb:implement_tasks      → TDD per phase
         ↓
/wb:validate_execution   → verify implementation matches plan
```

Forge is explicitly re-entrant and state-detecting (`commands/forge.md:51-58`: it reads the project
directory and infers which phase to resume at) and explicitly **one ticket at a time**
(`commands/forge.md:115`: "Forge sequences a single ticket end-to-end; it does not parallelize across
tickets"). Every artifact it produces lives under one timestamped `docs/plans/<date>-<slug>/` directory.
Nothing in the pipeline reads from, or writes to, anything shared across ticket directories.

### 4.3 Learning-capture points that already exist and have no destination

This is the most directly relevant finding. Four separate commands instruct the agent to capture
learnings, and all four terminate locally:

| Location | What it says | Where it goes |
| --- | --- | --- |
| `commands/validate_execution.md:381` | "Note lessons learned for future projects" | **Nowhere.** No destination file, format, or consumer is specified. |
| `commands/create_handoff.md:214-218` | `## Critical Learnings` → "Discoveries Not in Documentation… each with a real `file:line`. **Durable codebase facts belong in CLAUDE.md, not a one-shot handoff.**" | Names the right promotion target (`CLAUDE.md`) but specifies no mechanism, gate, or trigger. The handoff itself is explicitly one-shot. |
| `commands/implement_tasks.md:494` | `## Implementation Notes` → `[YYYY-MM-DD] Phase [N] complete: [key learnings, deviations from plan]` | The ticket's own `tasks.md`. |
| `commands/implement_coordinated.md:652` | `Key learnings: ${aggregatedLearnings}` — aggregated across sequential worker agents | The ticket's own `tasks.md`. Aggregation exists *within* a run and stops there. |

There is also a **read** path already built, for exactly one source: `commands/resume_handoff.md:158`
("Step 4: Apply Learnings from Handoff") and `:319-327` ("Build on Learnings: apply insights
discovered"; "Trust the handoff for learnings and context"). The read side of the loop is therefore
proven in this codebase — it just currently has a single-session artifact as its only input.

### 4.4 Mechanisms already present that do half of what a knowledge loop needs

| Need (from Part 3) | Existing mechanism | Notes |
| --- | --- | --- |
| Bootstrap shared context before research | `commands/create_research.md:47-60` — Step 0 "Ticket Context Bootstrap" delegates to the `jira-context` skill and treats what it finds as "high-priority scoping input"; explicitly best-effort and non-blocking (`:60`) | This is a working, tested hook point for an external knowledge source. The pattern generalizes. |
| Detect that stored knowledge went stale | `agents/research-validator.md` — validates paths, snippets, behavioral claims and pattern claims against the codebase, emitting **PASS / FAIL / STALE / UNCERTAIN** per claim (`:96-101`, `:118-181`) | `STALE` ("file exists but content has changed") is precisely the staleness predicate a knowledge base needs. Also exposed as the `research-validation` skill. |
| Durable state that survives context loss | `skills/touch-grass/SKILL.md:12` — "A long task survives interruption only if its entire state lives in a file a cold-context model could resume from"; `:49-58` specifies the `state.md` contract: Header + numbered AMENDMENT blocks (never rewrite history), Segment plan, Budget ledger, **Findings** (one dense self-contained block per segment with confidence), **Decision so far**, **Sources ledger** (source / takeaway / confidence), **Next action** | An append-mostly, provenance-carrying, confidence-tagged, cold-resumable artifact already specified in this repo. It is a per-run version of the structure a shared knowledge base needs. |
| Independent critique before accepting work | `skills/touch-grass/SKILL.md:88` — fresh-**context** critic subagent given only spec + deliverable + checkpoint, returning BLOCKER/MAJOR/MINOR; explicitly notes same-session wakeups "rubber-stamp your own work" | The repo already encodes the insight that a validator must not share the author's context. |
| Verify before claiming | `skills/verification-before-completion/SKILL.md`; `agents/task-verifier.md` | Evidence-before-assertion is already a first-class discipline. |
| Cull before fanning out | `skills/tracer-bullet/SKILL.md` | Probe the load-bearing assumption first; "culling is the deliverable." |
| Cost-aware routing of work | `skills/model-help/SKILL.md:56-67` per-phase model/effort baseline table; `:68-79` the switch-cost rule (sub-agent tiering is free; main-session switches cost a context reload; the quality floor is inviolable) | An existing, centralized policy artifact that already governs the whole pipeline — and a precedent for "one file is the authority, commands delegate to it." |
| Cross-ticket intake | `skills/fetch-issues/SKILL.md` (open GitHub issues → per-issue session-ready handoffs); `skills/daily-digest/SKILL.md` (cross-source catch-up and day plan) | The only two skills that already operate across multiple work items rather than within one. |

### 4.5 What has no mechanism at all

| Missing capability | Current state |
| --- | --- |
| A shared, cross-ticket knowledge artifact | None. All knowledge is scoped to one `docs/plans/<date>-<slug>/` directory or one handoff file. |
| A trace/experience corpus | None. Nothing persists sub-agent trajectories, tool-call sequences, or failure records. AHE's "experience observability" pillar has no substrate here. |
| A promotion gate (ticket-local → shared) | None. `create_handoff.md:218` names `CLAUDE.md` as the target for durable facts; nothing implements the move. |
| Staleness detection over stored knowledge | The *detector* exists (`research-validator`'s `STALE`) but nothing invokes it on a schedule or against a shared store — only on a single research document on request. |
| An eval corpus for the prompts themselves | None. `scripts/test-quiet` tests one shell script's output contract. No fixture tickets, no regression suite, no way to tell whether a change to `create_design.md` made designs better or worse. |
| A revert unit for a bad knowledge/harness edit | Git commits, used manually. Nothing pairs an edit with a prediction (AHE) or a regression check (Self-Harness). |
| Curation (dedup / merge / deprecate) | None. Nothing bounds growth of any accumulated artifact. |
| Write-policy or provenance on captured knowledge | None. No entry IDs, no verified-at SHA, no confidence, no scope tags. |

### 4.6 Observed drift, as evidence that the gap is real

`docs/beads-integration-learnings.md` is the repo's one genuine attempt at a durable, cross-session
learnings artifact — a hand-written document dated "Session 2026-01-31" with ten numbered learnings.
Two things about it are load-bearing evidence for this research:

- **It has gone stale with no mechanism to notice.** Learning 5 (`:88-113`, "TodoWrite + Beads Serve
  Different Purposes") and the post-review clarification (`:229-235`, "**Always use TodoWrite** for
  session tracking") directly contradict the current `CLAUDE.md`, which states: "Do NOT use TaskCreate,
  TaskUpdate, TodoWrite, or markdown checkboxes for tracking." The same document's Learning 4
  (`:66-86`) recommends markdown checkboxes for within-phase tracking, which `CLAUDE.md` also now
  forbids and which `commands/validate_execution.md:63` explicitly demotes to "documentation only."
  Nothing flagged the contradiction; it is only visible by reading both files.
- **Its own final section is an unactioned backlog.** `:244-252` ("Remaining Token Optimization") lists
  four known duplications from an earlier review that were never addressed — captured, then dropped.

This is a small, concrete instance of exactly the failure the external literature predicts for
capture-without-curation: an artifact that accumulates, is never re-validated against the current state
of the system, and silently becomes a source of wrong guidance.

A second, structural constraint worth recording: per `CLAUDE.md` → "Releasing New
Commands/Skills/Agents", the marketplace plugin cache is **keyed by version**, so any self-improvement
the loop produces does not reach an installed user until `version` is bumped in both
`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, pushed, and pulled via
`claude plugin update`. Local `--plugin-dir` development takes effect immediately. Any autonomy design
has to account for that release boundary — the loop can improve the branch continuously, but delivery
is discrete and versioned.

---

## Part 5 — Design Input: Surfaces Available for an R+D Knowledge Branch

**Not decisions.** This part enumerates the concrete surfaces this repo already exposes and what each
mechanism from Parts 1–3 would require if built on them, with the trade-off it carries. Decisions
belong in `design.md`.

### 5.1 The entry shape

The convergent recommendation from ACE (itemized `(identifier, description)` bullets, delta updates),
Always-On Agents (provenance, write policy, conflict resolution), mem0's multi-scope tagging, and this
repo's own `state.md` contract (`skills/touch-grass/SKILL.md:49-58` — findings with confidence, sources
ledger with confidence) is a single entry format carrying, at minimum:

- a stable **ID** (so deltas address entries, not documents — this is what makes concurrent proposals
  non-conflicting);
- the **claim**, one dense self-contained block;
- **provenance**: the repo, the `file:line` refs it rests on, and the **commit SHA it was verified
  against** (this is the computable staleness predicate from Part 3.2);
- **confidence**, per the existing `state.md` and sources-ledger convention;
- **scope tags** — which repo / subsystem / ticket class it applies to (the counter to negative
  transfer, per Memory Transfer Learning);
- **kind** — the Always-On Agents taxonomy is directly usable: *semantic* (how this subsystem works),
  *procedural* (how to do this kind of change here), *episodic* (what happened on ticket X and why).

Trade-off: this is heavier than prose notes, and the cost lands on the write path — the moment where the
agent is finishing a ticket and least inclined to do bookkeeping. Anything requiring more than a couple
of fields at capture time will be skipped or filled with mush.

### 5.2 Branch mechanics

The user's "R+D branch" framing has a real advantage the literature doesn't get for free: **git already
provides provenance, auditability, review, atomic revert, and merge machinery**, which is exactly what
CAAF argues a harness needs and what the Always-On Agents survey lists as unsolved governance problems.
Specific choices this raises:

- **Entry-per-file vs entries-in-one-file.** One file per entry (e.g. `knowledge/<kind>/<id>.md`) makes
  concurrent proposals from parallel ticket agents merge without conflict, and makes AHE's "revert at
  file granularity" literal. One large file is easier to read and cheaper to load, but reintroduces
  conflicts and invites the monolithic rewrite ACE warns about. An index file that is *generated* from
  the entries gets both.
- **Direction of merge.** If the R+D branch merges into `main`, knowledge becomes part of the shipped
  plugin and inherits the version-bump release constraint from §4.6. If it stays long-lived and
  unmerged, it needs an explicit read mechanism from ticket workspaces (fetch + read from
  `origin/<kb-branch>`, a `git worktree`, or a sparse checkout) and a policy for how it tracks `main`
  so its provenance SHAs stay meaningful.
- **This repo's own layout is a fit.** `docs/plans/<date>-<slug>/` is per-ticket by design and should
  stay that way; a shared store is a sibling, not a replacement. `project-structure` (the skill that
  enforces the research/design/tasks separation) is where a fourth category would need to be declared.

### 5.3 Read path — where it plugs in

Three existing insertion points, in order of how well-proven they are:

1. **`commands/create_research.md:47-60`, Step 0.** This step already exists to load pre-existing
   context before decomposing research, already delegates to a skill (`jira-context`), already treats
   the result as "high-priority scoping input," and is already specified as **best-effort and never
   blocking** (`:60`). A knowledge-base read is the same shape as a ticket-context read. The existing
   caveat at `:58` also transfers exactly: it shapes *where* you look, not *what* you produce — the
   Documentarian Rule still holds.
2. **`commands/resume_handoff.md:158`, Step 4 "Apply Learnings."** Already the consumer of captured
   learnings; would gain a second input source.
3. **`commands/forge.md:51-58`.** Forge already detects pipeline state before acting; a knowledge-base
   read at forge entry would apply to every phase downstream in one place.

Trade-off to design against: **retrieval noise and negative transfer are the measured failure modes**
(CODESKILL, Memory Transfer Learning), and they get worse as the store grows. Loading "the knowledge
base" wholesale is the naive version and will degrade research quality on tickets it doesn't apply to.
Scope tags plus a bounded number of entries is the counter; `model-help`'s precedent is relevant —
a policy artifact that is *consulted for a specific decision*, not preloaded.

### 5.4 Write path — where it plugs in

The four capture points from §4.3 are already written and already positioned correctly; what they lack
is a destination. In increasing order of signal quality:

- **`commands/validate_execution.md:381`** is the highest-value point in the pipeline, because
  validation is the only phase that has *ground truth* — it has just compared plan to reality, run the
  automated checks, and classified deviations as justified or unjustified (`:279-291`). That is a
  verifier-grounded failure record, which is precisely what Self-Harness's weakness-mining stage
  consumes. It is currently the weakest-specified capture instruction in the repo.
- **`commands/create_handoff.md:214-218`** already demands `file:line` evidence per learning and
  already names the promotion target. It is the closest existing thing to a promotion proposal.
- **`commands/implement_coordinated.md:652`** already aggregates learnings across multiple worker
  agents — the fan-in shape a multi-agent contribution needs (compare FederatedSkill: local libraries,
  selective contribution).
- **`commands/implement_tasks.md:494`** per-phase notes are the highest-volume, lowest-signal source.

Trade-off: the literature is unanimous that **volume is not the goal**. Self-Harness generates
"diverse yet *minimal*" edits tied to specific mined failures; FederatedSkill shares only *finalized*
skills, not raw experience; ACE's Curator emits *compact* deltas and dedups periodically. A write path
that promotes every per-phase note produces the skill-bloat failure directly.

### 5.5 The promotion gate

The component Part 3.3 identifies as unskippable, and the one this repo has no analogue for. Available
building blocks:

- **A fresh-context critic** is already specified and already argued for in this repo
  (`skills/touch-grass/SKILL.md:88`) — including the crucial detail that a same-context reviewer
  rubber-stamps. A promotion reviewer must be a clean-context subagent given the candidate entry and
  nothing else.
- **Adversarial verification of the claim** is what `agents/research-validator.md` already does for
  research documents: paths, snippets, behavioral claims, pattern claims → PASS/FAIL/STALE/UNCERTAIN. A
  candidate knowledge entry is structurally the same object as a research claim. This is the single
  highest-reuse opportunity identified in this research.
- **The scheduled generalization slot** is the FDE model's answer, and it is a human-process answer
  rather than a mechanism: one day a week on platform work. The workbench analogue would be a recurring
  curation pass rather than an inline-with-every-ticket promotion — which also matches ACE's "refined
  and deduplicated *periodically*."
- **Human review as the default**, per Weng's "humans move up the stack, not out of the loop" and CAAF's
  versioned-asset argument. A promotion proposal that lands as a reviewable diff on a branch is already
  the natural artifact here.

Open trade-off: a gate strict enough to prevent bloat is a gate that rejects most candidates, and every
rejected candidate is capture effort spent for nothing. Whether the gate runs per-ticket (immediate,
expensive, high friction) or as a batched periodic pass (cheaper, but learnings decay between passes)
is a genuine design fork.

### 5.6 Invalidation

The mechanism is available and cheap in a git-native store: an entry records the SHA it was verified
against and the files it cites; `git diff <verified-sha>..HEAD -- <cited paths>` answers "is this entry
suspect?" without any model call. Suspect entries then go to `agents/research-validator.md` for a real
verdict. The [Cognee approach reported in 2026 practice](https://www.cognee.ai/blog/guides/ai-coding-agent-persistent-codebase-memory)
is the same idea via content hashing with re-ingestion as a CI step on merge; the git-native version is
strictly cheaper here because the repo already has the history.

Note what this does *not* solve: staleness of *procedural* and *episodic* knowledge that doesn't cite
specific files ("we tried X and it didn't work"). Those decay on a different clock and the survey
literature offers only decay/eviction policies, not detection.

### 5.7 Curation

CODESKILL's four operations (**add / update / merge / deprecate**) plus ACE's periodic dedup are the
established answer to bloat, and GEPA's Pareto front is the caution against over-merging: keep entries
that each win on *some* class of ticket rather than collapsing to one canonical "best practice."
Concretely, this is a batched pass over the store, not an inline operation.

### 5.8 Measuring whether it helps

This is the weakest-supported part of the whole design space, and the literature says so.
[OSS Insight's 2026 memory-architecture comparison](https://ossinsight.io/blog/agent-memory-race-2026)
names measuring "longitudinal value (actual performance over months) versus benchmark scores" as
explicitly unresolved, alongside "which layer should own memory." Weng names weak/fuzzy evaluators as
the primary limiter on self-improvement loops generally, and reward hacking as what happens when you
optimize a weak signal anyway.

What the repo has to work with today: nothing. There is no eval corpus over the prompts (§4.5), so any
claim that a knowledge base or a harness edit *helped* is currently unfalsifiable. The mechanisms in
the literature that would make it falsifiable all require an eval substrate first — Self-Harness's
held-out regression split, AHE's prediction-then-verify, DGM's admission threshold. This suggests the
eval corpus is a prerequisite for the loop rather than a later refinement, and is the most likely
candidate for a `tracer-bullet` probe before any larger build.

### 5.9 The FDE analogue in workbench terms

Mapping §2.2's mechanics onto a single-maintainer plugin used on real tickets:

| FDE mechanic | Workbench analogue |
| --- | --- |
| Embedded in the field, 30–40h/week | Every real ticket forged with `/wb:forge` is a deployment of the harness against real complexity. |
| One day/week on platform engineering | A scheduled curation/promotion pass, distinct from ticket work. Currently absent — improvements happen when someone notices. |
| Ontology-first: one artifact serves both the local job and the platform | The candidate is the knowledge entry: written to serve *this* ticket, structured so it generalizes. |
| "Route product feedback through the FDE" | The agent that just did the work is the primary input channel to the harness — which is exactly what §4.3's four capture points already assume, and what §4.5's missing destination defeats. |
| Discovery as engineering | `create_research` already is this. |
| The critique: no generalization → permanent bespoke maintenance | The current state: every ticket re-derives context from scratch; `docs/beads-integration-learnings.md` is the one generalization attempt and it drifted (§4.6). |

### 5.10 What the sources argue against automating

- **Self-editing without a gate.** CAAF: unconstrained self-modification produces uncontrolled drift,
  loss of auditability, and cascading failures. AHE's answer is not "don't edit" but "every edit is a
  file, carries a prediction, and reverts on failure."
- **Trusting a self-improvement loop below a capability threshold.** STOP improved with GPT-4 and
  *degraded* with weaker models. `skills/model-help/SKILL.md:79` already encodes the matching principle
  for this repo ("the floor is inviolable") — a promotion/curation pass is high-judgment work and should
  be tiered accordingly, not pushed to the cheapest agent because it is batch work.
- **Letting anything writable be read as instruction.** Zombie agents: content written into memory
  survives self-evolution and is legitimized as a learned pattern. A shared knowledge base read by every
  future ticket needs its trust boundary stated explicitly — what may write, what is treated as data
  versus directive, and what a human must sign off on.
- **Optimizing a weak signal.** Weng: reward hacking, over-optimism, p-hacking. Without §5.8's eval
  substrate, a loop that "improves" the harness is measuring nothing.

---

## Part 6 — Risks Specific to This Repository

| Risk | Why it is sharper here | Anchor |
| --- | --- | --- |
| **Shared KB as supply chain** | This plugin's entire content is *instructions that steer other work*. A poisoned or merely wrong entry doesn't produce one bad answer; it silently steers every future ticket's research and design. | [arXiv:2602.15654](https://arxiv.org/pdf/2602.15654) |
| **No falsifiability today** | With no eval corpus over prompts (§4.5), every claimed improvement to the harness is currently an assertion. This repo's own `verification-before-completion` skill forbids exactly that pattern. | §4.5, §5.8 |
| **Drift is already demonstrated** | `docs/beads-integration-learnings.md` contradicts `CLAUDE.md` today and nothing noticed. A larger store fails the same way, faster. | §4.6 |
| **Documentarian Rule tension** | `create_research.md:13` forbids recommendations in research. A knowledge base that accumulates *procedural* guidance ("do it this way here") is closer to design than research, so where it lives and which command may write it is a real structural question, not a formatting one. | `commands/create_research.md:13`, `skills/project-structure` |
| **Release boundary** | Version-keyed marketplace cache means continuous self-improvement + discrete versioned delivery. A loop that edits the plugin must also manage the two-file version bump and the user-run `claude plugin update`. | `CLAUDE.md` → Releasing |
| **Beads assumption unmet here** | `CLAUDE.md` requires beads for all task tracking; this workspace has neither `bd` nor `.beads/`. Any KB design that leans on beads for promotion-proposal tracking inherits that dependency and its fast-fail requirements. | §4.1, `docs/beads-fast-fail.md` |
| **Long-horizon is where agents are weakest** | RE-Bench: humans exceeded agents at 8h and 32h budgets while agents led 4× at 2h. A long-horizon project-management system is being built precisely in the regime where the model needs the most scaffolding — which is the argument *for* the durable artifact and *against* expecting the agent to hold it. | Weng |

---

## Open Questions

*All 6 questions resolved as of 2026-07-31 via `/wb:resolve_questions`. These are **interim** records:
`design.md` does not exist yet, so `/wb:create_design` should promote each into
`## Technical Decisions` with explicit rationale and trade-offs.*

Beads is unavailable in this workspace, so these are recorded here. With beads, each becomes
`bd create "Q: …" --type=task --priority=2`.

1. **Does the R+D branch merge into `main` or stay long-lived and unmerged?** This determines whether
   knowledge ships with the plugin (and inherits the version-bump release path) or is fetched from
   `origin/<branch>` by ticket workspaces. Blocks all of §5.2.
   - **Resolved 2026-07-31**: Long-lived unmerged branch — ticket workspaces read it via fetch or
     `git worktree` from `origin/<kb-branch>`; it does not merge into `main`. Explicitly provisional
     ("for now until we figure out a better mechanism"), so the design must keep the delivery mechanism
     swappable rather than assuming this is permanent. Consequence to carry into design: entry
     provenance SHAs need a stated policy for how the branch tracks `main` (§5.1, §5.6), and the
     version-keyed release path in §4.6 does **not** apply to knowledge entries under this choice.
2. **Is the knowledge base scoped to this plugin's own improvement, or to the codebases the plugin is
   used on?** These are different products. "Improve the workbench harness" (AHE/Self-Harness shape) and
   "accumulate knowledge about the repo being worked on" (CODESKILL/memory shape) share machinery but
   have different consumers, different staleness clocks, and different trust boundaries. Blocks §5.1
   and §5.3.
   - **Resolved 2026-07-31**: Dual purpose, resolved by scoping the store to **the repo it lives in**
     rather than choosing between the two shapes. In *this* repo the R+D branch is a parallel
     do-not-merge branch supplementing workbench development, so its entries are about the harness. When
     wb is used on another project, that project gets its own KB scoped to that project's code — not to
     workbench. Rationale: wb's codebase *is* its harness, so harness self-improvement is a special case
     of codebase knowledge and one mechanism covers both; no dual schema is required. Consequences to
     carry into design: (a) the store is per-repo, not global, so cross-repo transfer is explicitly out
     of scope for v1 (this is also the counter to the negative-transfer risk in §5.3); (b) the trust
     boundary still differs by host repo — in workbench, entries steer the harness and are effectively
     directive, elsewhere they are descriptive — which is input to Q5.
3. **Per-ticket promotion or batched periodic curation?** Immediate-and-expensive versus
   cheap-but-decaying. Blocks §5.5.
   - **Resolved 2026-07-31**: Batched periodic curation pass — the FDE-style scheduled slot is the
     gate — **plus an explicit manual trigger** so a pass can be run on demand rather than only on
     schedule. Rationale: keeps per-forge friction at zero and matches ACE's "refined and deduplicated
     periodically," while the manual trigger covers the case where a ticket produced something worth
     promoting immediately. Added requirement stated by the user, which the design must treat as
     first-class: **capture and propagation of decisions and progress should be automatic**, not manual
     as it is today. That splits §5.5 into two mechanisms — automatic, ungated capture into a staging
     area (wiring up the four orphaned capture points in §4.3), and a batched, gated promotion pass out
     of it. The gate stays batched; only the capture is continuous.
4. **What is the eval corpus?** Without one, §5.8 says the loop is unfalsifiable. Candidate cheap
   substrate: a small set of fixture tickets against a fixture repo, with a rubric per phase. This is
   the highest-value `tracer-bullet` probe available and arguably gates everything else.
   - **Resolved 2026-07-31**: Both, layered. A **fixture corpus** (fixture tickets against a fixture
     repo, per-phase rubric) provides the static baseline and the held-out regression split that
     Self-Harness's validation stage needs. On top of it, **AHE-style prediction-then-verify** provides
     periodic feedback: each promoted entry declares an expected effect, verified against subsequent
     real runs, reverted at file granularity on failure. Discovery from the verify loop feeds back into
     the fixture corpus when a real failure turns out to have no coverage. Rationale: the fixture corpus
     alone goes stale and under-covers; prediction-then-verify alone has no baseline to regress against;
     together the corpus becomes a maintained artifact rather than a one-time investment.
   - **⛔ LOCKED CONSTRAINT — human-in-the-loop on all core self-extension (2026-07-31).** Self-extension
     is wanted: the loop *should* be able to grow its own eval corpus from discovered coverage gaps.
     But **every core self-extension requires a human in the loop** — no exceptions, no
     configurable override, no earned-autonomy path. Rationale (user, verbatim framing): "otherwise we
     have a huge vector." Mechanically this is the reward-hacking failure in §1.5 (Weng): a loop that
     can weaken its own evaluator makes its own tests easier and every downstream gate silently loses
     its signal, while continuing to report success.

     **Core self-extension** means any change to the machinery that evaluates or steers the system
     — the design must enumerate this set explicitly and default-deny anything ambiguous into it:

     - the **eval corpus and its rubrics** — additive-only, human-reviewed, and never able to weaken,
       relax, or remove an existing failing case;
     - the **harness components themselves** — `commands/`, `agents/`, `skills/`, `hooks/`, `CLAUDE.md`
       (the seven AHE components in §1.2 map onto these directories);
     - the **gate and write-policy configuration itself** — this is the one that must be hardest. If the
       loop can edit the policy that decides what needs human review, every other control here is
       bypassable in one move, and the bypass looks like a routine config change.

     **This narrows Q5.** Q5's "defined path to removal" for the human gate applies only to ordinary
     knowledge entries tiered by origin. It does **not** apply to core self-extension, where the human
     gate is permanent by decision rather than provisional pending hardening.
5. **Who or what may write to the shared store, and is any of it treated as directive rather than
   data?** The zombie-agents result makes this a security question, not a workflow preference.
   - **Resolved 2026-07-31**: Make it a **configurable per-project preference**, defaulting to the
     strictest setting — agents propose only, every promotion is a human-reviewed diff, and entries are
     read as data rather than as instruction. When a project relaxes the default, the axis it relaxes
     along is **origin**: entries derived from verified tool output (test results, diffs, validator
     verdicts) may promote automatically; entries derived from model narration always require human
     review. Rationale: the trust posture legitimately differs by repo (per Q2, workbench's own entries
     are directive and warrant the strict default), and origin is the tiering axis that maps to
     evidence rather than to self-assessed category. Stated long-term goal to design toward, not away
     from: **harden the supply chain enough that full-auto becomes safe** — so the design should treat
     the human gate as a currently-required control with a defined path to removal (what would have to
     be true), not as a permanent fixture.
   - **Amended 2026-07-31 — scope narrowed by Q4's locked constraint.** The path-to-removal above
     applies **only to ordinary knowledge entries**. It does not apply to core self-extension (the eval
     corpus and rubrics, the harness components under `commands/`/`agents/`/`skills/`/`hooks/` and
     `CLAUDE.md`, and the gate/write-policy configuration itself), where the human gate is permanent by
     decision. The per-project preference must therefore be unable to express "auto-promote core
     self-extension" at all — that is not a setting the configuration surface should offer, since a
     configurable control over the control is the bypass.
6. **Does `docs/beads-integration-learnings.md` get migrated, re-validated, or deprecated?** It is the
   existing instance of the artifact being designed, and it currently contains guidance `CLAUDE.md`
   forbids. Whatever the answer, it is the natural first test case for the invalidation mechanism in
   §5.6.
   - **Resolved 2026-07-31**: **Migrate, then deprecate.** Convert its surviving learnings into entries
     in the new store, re-validated against HEAD — dropping or correcting the three items that
     contradict `CLAUDE.md` (`:66-86`, `:88-113`, `:229-235`) — and then mark the original superseded
     and historical rather than maintaining it in parallel. Rationale: it is the only real corpus of
     pre-existing entries available, so it doubles as the first end-to-end test of the §5.6 invalidation
     path and the §5.7 curation operations; leaving it live afterward would recreate the exact
     two-sources-of-truth drift documented in §4.6. Its unactioned backlog at `:244-252` should be
     triaged during migration rather than carried over silently.

## Code References

- `.claude-plugin/plugin.json:3` — plugin version 1.12.3
- `.claude-plugin/plugin.json:10-45` — the only two registered hook events
- `commands/forge.md:26-38` — pipeline sequence
- `commands/forge.md:51-58` — re-entrant pipeline-state detection
- `commands/forge.md:115` — one ticket at a time
- `commands/create_research.md:13` — the Documentarian Rule
- `commands/create_research.md:47-60` — Step 0 Ticket Context Bootstrap (the existing read-path hook)
- `commands/validate_execution.md:63` — tasks.md checkboxes are documentation only
- `commands/validate_execution.md:279-291` — justified vs unjustified deviations
- `commands/validate_execution.md:381` — "Note lessons learned for future projects" (no destination)
- `commands/create_handoff.md:214-218` — Critical Learnings; names CLAUDE.md as promotion target
- `commands/implement_tasks.md:494` — per-phase Implementation Notes
- `commands/implement_coordinated.md:652` — aggregated worker learnings
- `commands/resume_handoff.md:158` — Step 4 Apply Learnings (the existing consumer)
- `commands/resume_handoff.md:319-327` — Build on Learnings / trust the handoff
- `agents/research-validator.md:96-101` — PASS/FAIL/UNCERTAIN classification
- `agents/research-validator.md:179-181` — overall status determination including STALE
- `skills/touch-grass/SKILL.md:12` — durable-state core principle
- `skills/touch-grass/SKILL.md:49-58` — the `state.md` contract
- `skills/touch-grass/SKILL.md:88` — fresh-context critic
- `skills/model-help/SKILL.md:56-67` — per-phase model/effort baselines
- `skills/model-help/SKILL.md:68-79` — switch-cost rule and inviolable floor
- `hooks/setup-beads-mode.sh` — fast-fail availability probe, sets `BEADS_AVAILABLE` / `BEADS_MODE`
- `docs/beads-integration-learnings.md:66-86` — Learning 4, markdown checkboxes (now contradicted)
- `docs/beads-integration-learnings.md:88-113` — Learning 5, TodoWrite (now contradicted)
- `docs/beads-integration-learnings.md:229-235` — "Always use TodoWrite" (now contradicted)
- `docs/beads-integration-learnings.md:244-252` — unactioned token-optimization backlog
- `scripts/test-quiet` — the repo's only executable test (covers `scripts/quiet`, not the prompts)

## Sources

Self-learning loops and harness engineering:

- [Harness Engineering for Self-Improvement — Lilian Weng, Lil'Log, 2026-07-04](https://lilianweng.github.io/posts/2026-07-04-harness/)
- [A primer on self-improving agent harnesses — Ben Dickson, bdtechtalks](https://bdtechtalks.substack.com/p/a-primer-on-self-improving-agent)
- [Agentic Context Engineering (ACE) — arXiv:2510.04618](https://arxiv.org/html/2510.04618v1) · [reference implementation](https://github.com/ace-agent/ace)
- [Agentic Harness Engineering (AHE) — arXiv:2604.25850](https://arxiv.org/abs/2604.25850)
- [Self-Harness: Harnesses That Improve Themselves — arXiv:2606.09498](https://arxiv.org/abs/2606.09498)
- [GEPA: Reflective Prompt Evolution — arXiv:2507.19457 (ICLR 2026 Oral)](https://arxiv.org/abs/2507.19457)
- [CODESKILL: Learning Self-Evolving Skills for Coding Agents — arXiv:2605.25430](https://arxiv.org/pdf/2605.25430)
- [Memory Transfer Learning in Coding Agents — arXiv:2604.14004](https://arxiv.org/pdf/2604.14004)
- [FederatedSkill: Federated Learning for Agentic Skill Evolution — arXiv:2606.03143](https://arxiv.org/pdf/2606.03143)
- [Always-On Agents: Persistent Memory, State, and Governance — arXiv:2606.30306](https://arxiv.org/pdf/2606.30306)
- [Zombie Agents: Persistent Control of Self-Evolving LLM Agents — arXiv:2602.15654](https://arxiv.org/pdf/2602.15654)
- [Harness as an Asset: CAAF — arXiv:2604.17025](https://arxiv.org/pdf/2604.17025)

Agent memory in practice:

- [The Agent Memory Race of 2026: 5 Repos, 4 Architectures, 1 Unsolved Problem — OSS Insight](https://ossinsight.io/blog/agent-memory-race-2026)
- [Large-Repo Coding Agent Memory Bottleneck — supermemory, June 2026](https://supermemory.ai/blog/memory-bottleneck-large-repo-coding-agents/)
- [State of AI Agent Memory 2026 — mem0](https://mem0.ai/blog/state-of-ai-agent-memory-2026)
- [Persistent Codebase Memory for Coding Agents — Cognee](https://www.cognee.ai/blog/guides/ai-coding-agent-persistent-codebase-memory)

Forward deployed engineering:

- [What is a Forward Deployed Engineer — MarkTechPost, 2026-05-20](https://www.marktechpost.com/2026/05/20/what-is-a-forward-deployed-engineer-the-ai-role-openai-anthropic-and-google-are-hiring-in-2026/)
- [Palantir's Forward-Deployed Engineering Playbook — Perspective AI](https://getperspective.ai/blog/palantir-forward-deployed-engineering-playbook-anthropic-openai-copying)
- [Palantir's FDE Model — MindStudio](https://www.mindstudio.ai/blog/palantir-forward-deployed-engineer-model-anthropic-openai)
- [Palantir And Forward Deployed Engineering: What Should We Believe? — Forbes, 2026-07-10](https://www.forbes.com/sites/stevebanker/2026/07/10/palantir-and-forward-deployed-engineering-what-should-we-believe/)
- [Dogfooding with Rapid Iteration for Agent Improvement — Agentic Patterns](https://www.agentic-patterns.com/patterns/dogfooding-with-rapid-iteration-for-agent-improvement/)

## Next Steps

All 6 open questions were resolved on 2026-07-31 (see the interim records under Open Questions).

1. Run `/wb:create_design` on this research. Its first job is to promote the six interim resolutions
   into `## Technical Decisions` with explicit rationale and trade-offs, since research stays
   facts-only.
2. Build the fixture corpus first (Q4). It is still the `tracer-bullet` probe: every admission gate in
   the literature needs a baseline, and the prediction-then-verify layer has nothing to regress against
   without it.
3. Carry the **locked constraint** into design as a first-class invariant, not a footnote: all core
   self-extension is permanently human-gated (Q4) — eval corpus and rubrics, harness components, and
   the gate/write-policy config itself, with ambiguous cases default-denied into that set. Design must
   also enumerate that set explicitly and make "auto-promote core self-extension" unexpressible in the
   configuration surface. The earned-autonomy path from Q5 applies only to ordinary knowledge entries.
4. `bd init` before running pipeline commands, since this workspace currently has no beads.
