---
project: rd-branch-knowledge-loop
ticket: N/A
created: 2026-07-31
status: draft
last_updated: 2026-07-31
last_updated_note: "Phase 0+1 complete; 4 further decisions resolved via /wb:resolve_questions (protected set, code/knowledge branch split, ajv validation, workspace arrangement)"
depends_on: research.md
design_approach: Git-native entry-addressable knowledge store with hook-enforced protected-path boundary
---

# Design: R+D Branch as a Self-Learning Knowledge Base

## Problem Statement

Every wb ticket re-derives its context from scratch. The pipeline is per-ticket by construction
(`commands/forge.md:115` — "one ticket at a time") and every artifact it produces lands in one
timestamped `docs/plans/<date>-<slug>/` directory that nothing else ever reads.

Four separate commands already instruct the agent to capture what it learned
(`commands/validate_execution.md:381`, `commands/create_handoff.md:214-218`,
`commands/implement_tasks.md:494`, `commands/implement_coordinated.md:652`). All four terminate in a
per-ticket file or a one-shot handoff. The read side of the loop is already built and proven
(`commands/resume_handoff.md:158`, "Step 4: Apply Learnings from Handoff") — it simply has no durable
input. The loop is open at exactly one joint: **there is no destination**.

The cost of that gap is already observable in this repo. `docs/beads-integration-learnings.md` is the
one hand-written attempt at durable cross-session knowledge. Three of its items now contradict
`CLAUDE.md` outright (`:66-86`, `:88-113`, `:229-235` — all recommend tracking mechanisms `CLAUDE.md`
forbids), and nothing noticed; the contradiction is visible only by reading both files side by side.
Its final section (`:244-252`) is a backlog captured and then dropped. This is the
capture-without-curation failure the external literature predicts, at small scale, in production.

Solving this matters now because the same joint blocks the harder goal. Improving the harness itself
(the AHE/Self-Harness shape) requires the same machinery as accumulating codebase knowledge: a durable
store, an admission gate, and an invalidation path. Building it once serves both. Not solving it means
every long-horizon effort keeps paying full context-reconstruction cost per ticket, and the harness
keeps improving only when a human happens to notice something.

### Success Metrics

- A knowledge entry produced by one ticket run is readable by a later, unrelated ticket run in a fresh
  context, with no human copying it between directories.
- Entry staleness is decidable **without a model call**: `git diff <verified-sha>..HEAD -- <cited
  paths>` classifies every entry clean-or-suspect deterministically.
- An agent-originated write to any protected path is denied by the enforcement layer, demonstrably, in
  a test — and the denial does not depend on any instruction text the agent could be talked out of.
- Normal maintainer development (editing `commands/`, `skills/`, `agents/` by hand) is never blocked by
  the enforcement layer.
- The `docs/beads-integration-learnings.md` migration surfaces its three `CLAUDE.md` contradictions via
  the invalidation path rather than via a human reading both files.

## Design Approach

A **git-native, entry-addressable knowledge store** living on a long-lived unmerged branch, fed by
**automatic ungated capture** and drained by a **batched, human-gated promotion pass**, with a
**protected-path boundary enforced mechanically at the tool-call layer** rather than in prose.

The four moving parts, and why each exists:

- **The store** is the destination the four capture points never had. It is per-repo, entry-addressable,
  and carries provenance sufficient to make staleness computable.
- **Capture is automatic and ungated** because the write path is the moment an agent is least inclined
  to do bookkeeping; anything requiring the agent to *choose* to record gets skipped.
- **Promotion is batched and gated** because the admission decision is the one component the literature
  unanimously says cannot be skipped, and a gate cheap enough to run per-ticket is a gate too weak to
  prevent bloat.
- **Enforcement is mechanical** because the threat model is injected instruction text, and instruction
  text cannot defend against itself.

### Why This Approach

- **Git supplies, for free, everything the governance literature lists as unsolved.** The Always-On
  Agents survey names provenance tracking, review/approval, conflict resolution, and auditability as
  open problems for shared agent memory. A branch has all four natively. CAAF's argument that the
  harness must be a versioned engineering asset is satisfied by construction rather than by adding a
  layer.
- **Entry-granular addressing solves two problems with one choice.** ACE's reason is context collapse —
  monolithic rewrites progressively lose detail. The concurrency reason is independent and equally
  binding: parallel ticket agents proposing edits to one document conflict, and proposing edits to
  distinct entries do not. Both point the same way.
- **The verification machinery already exists and is reusable as-is.** A candidate knowledge entry is
  structurally the same object as a research claim — a statement about the codebase with file
  references. `agents/research-validator.md` already classifies exactly that into PASS / FAIL / STALE /
  UNCERTAIN (`:96-101`, `:179-181`). `STALE` ("file exists but content has changed") is precisely the
  staleness verdict this design needs. This is the single highest-reuse point in the whole design.
- **The read path has a proven insertion point.** `commands/create_research.md:47-60` (Step 0, Ticket
  Context Bootstrap) already exists to load prior context before decomposing research, already delegates
  to a skill, already treats results as "high-priority scoping input," and is already specified as
  best-effort and never blocking (`:60`). A knowledge read is the same shape as a ticket-context read,
  and inherits the caveat at `:58` unchanged — it shapes *where* you look, not *what* you produce.
- **The precedent for a single authoritative policy artifact is established.** `skills/model-help`
  is one file that owns a cross-cutting rubric which every phase command delegates to rather than
  re-deriving (`:56-79`). The write-policy config follows that shape.
- **The tracer bullet made mechanical enforcement available.** `PreToolUse` hooks can hard-deny a tool
  call (`permissionDecision: "deny"`, or exit code 2). That converts the locked human-in-the-loop
  constraint from an assertion into a control. Without this finding the design would have had to lean
  entirely on review discipline, which is the thing the zombie-agents threat model defeats.

## Technical Decisions

### Architecture

- **The store lives on a long-lived unmerged branch; ticket workspaces read it via fetch or
  `git worktree` from `origin/<kb-branch>`.**
  - Rationale: keeps knowledge out of the shipped plugin, so it never inherits the version-keyed
    marketplace cache and the two-file version bump described in `CLAUDE.md` → "Releasing New
    Commands/Skills/Agents." Knowledge improves continuously; plugin delivery is discrete.
  - Trade-off: an unmerged branch needs an explicit tracking policy against `main`, or entry provenance
    SHAs drift out of meaning. Merging would have been simpler and was rejected for the release-coupling
    reason above.
  - Explicitly provisional — recorded as "for now until we figure out a better mechanism." The delivery
    mechanism must stay swappable; nothing else in the design may assume this specific transport.
  - Source: research.md Open Question 1 · Decided 2026-07-31

- **That branch is `thescubageek/self-learning-loops-research` itself — the existing R+D branch is
  promoted to the permanent store branch rather than a dedicated one being cut.**
  - Rationale: it is already designated do-not-merge, is already pushed, and already carries the plan
    documents and Phase 0 findings that the store's first entries will cite — so its existing history is
    usable provenance from day one instead of starting from an empty root.
  - Trade-off: the branch stops being a disposable investigation branch. Anything landed on it from here
    is permanent store history, and it inherits merge-forward-never-rebase **permanently** — no rebase
    and no force-push on this branch, ever, or every stored provenance SHA silently goes stale.
  - Source: tasks.md Phase 1 Prerequisites / P1-T1 · Decided 2026-07-31

- **Code and knowledge are split across two branches from Phase 2 onward: the loop's *code* is built on a
  normal feature branch off `main` and reaches users through the ordinary release path; only `knowledge/`
  lives on the store branch.**
  - Rationale: the store branch is permanently unmerged outbound, but `hooks/knowledge-guard.sh`, the
    scripts, `commands/curate_knowledge.md`, and the version bump only reach an installed user via
    `main`. The original framing decoupled *knowledge* from the version-keyed release path and silently
    left the *code* stranded on a branch that by definition never ships. Splitting resolves it without
    weakening the store branch's no-outbound-merge rule: code flows feature-branch → `main` → forward-merge
    into the store branch, so the store still ends up holding both code and knowledge and entry
    `file:line` refs still resolve locally. Knowledge never travels the other way.
  - Trade-off: two branches to keep straight, and Phase 1's already-committed code has to be moved rather
    than written in place. Accepted — the alternative is discovering at Phase 6 that nothing built can be
    delivered.
  - Consequence: `.wb-knowledge.json` and `.wb-knowledge.schema.json` belong on the **code** side. They
    are per-repo configuration the shipped hook reads from whatever branch is checked out, not store
    content.
  - **`docs/plans/` stays on the store branch.** It is gitignored as dev-only and must never reach `main`
    (`.gitignore:7`), so it cannot ride the feature branch through the release path. It also already has
    its full history here, and duplicating it across branches would recreate exactly the
    two-sources-of-truth drift this project exists to fix. The feature-branch workspace reads it from the
    store-branch worktree.
  - **Working arrangement**: `kyiv` stays on the store branch; a second Conductor workspace carries the
    feature branch, and Phases 2–5 are implemented there. Git allows one checkout per branch, so the two
    workspaces hold the two branches and `scripts/knowledge-worktree` resolves across them — which is the
    multi-workspace case it was built for, now exercised for real rather than only in tests.
  - Source: tasks.md "What Phase 1 surfaced" · Decided 2026-07-31

- **The store is scoped to the repository it lives in. One mechanism, per-repo instances.**
  - Rationale: wb's codebase *is* its harness, so harness self-improvement is a special case of codebase
    knowledge rather than a separate product. In this repo the branch supplements workbench development
    and its entries are about the harness; when wb is used on another project, that project gets its own
    store scoped to that project's code. No dual schema is required.
  - Trade-off: cross-repo knowledge transfer is given up. That is acceptable and arguably desirable —
    Memory Transfer Learning measures negative transfer as a real degradation, and per-repo scoping is
    the strongest available counter to it.
  - Source: research.md Open Question 2 · Decided 2026-07-31

- **The store branch tracks `main` continuously, merging forward so it always contains recent code;
  provenance is relative to its own history.**
  - Rationale: keeping the code alongside the knowledge means an entry's `file:line` references resolve
    locally in a store-branch worktree, with no second fetch — the read path already needs that worktree,
    so this costs nothing extra. It also keeps the staleness diff comparing against a history that is
    actually current.
  - Trade-off: the branch is never quiet — every `main` commit is potential invalidation churn. The
    consequence is that the invalidation sweep belongs **on sync**, not only on demand, so entries are
    re-classified as the code moves under them rather than at some later moment of remembering.
  - **Merge forward, never rebase.** The option was phrased "merges or rebases," but they are not
    interchangeable here: rebasing rewrites the commits that entry provenance SHAs point at, which would
    silently invalidate every stored reference and destroy the audit trail the whole design rests on.
    Merge is the only variant compatible with stable provenance.
  - Note on direction: this is `main` → store. It does not contradict the decision that the store never
    merges into `main` — the flow is one-way inbound, and the store branch stays permanently unmerged
    outbound.
  - Source: design.md Pending Decisions · Decided 2026-07-31

- **Entries are individually addressable files with a generated index; the store is never a single
  hand-maintained document.**
  - Rationale: concurrent proposals from parallel ticket agents merge without conflict at entry
    granularity and collide at document granularity. It also makes AHE's "revert at file granularity"
    literal rather than approximate, and structurally forbids the monolithic rewrite that produces
    ACE's context collapse.
  - Trade-off: a directory of entries is worse to read than one document, and costs more to load naively.
    The generated index recovers readability; scoped retrieval (below) recovers load cost.
  - Pattern reference: research.md §5.2; `skills/touch-grass/SKILL.md:49-58` is the existing in-repo
    precedent for an append-mostly, provenance-carrying, confidence-tagged artifact.

- **Two stages with different postures: capture is automatic and ungated; promotion is batched and
  gated.**
  - Rationale: separating them resolves the tension the research left open. A gate strict enough to
    prevent skill bloat rejects most candidates, which makes per-ticket gating expensive friction on
    every forge. Making capture free and ungated means nothing is lost while the gate stays strict.
    Matches ACE's "refined and deduplicated periodically" and the FDE model's scheduled
    one-day-a-week platform slot.
  - Trade-off: learnings sit unpromoted between passes, and staging accumulates noise that someone must
    eventually triage. An explicit manual trigger for the pass mitigates the first; curation operations
    (below) mitigate the second.
  - Source: research.md Open Question 3 · Decided 2026-07-31

- **Staging lives on the store branch in a `staging/` area, written through the same worktree the read
  path requires.**
  - Rationale: captures become durable and shared the moment they happen, rather than sitting on one
    machine until someone runs a pass. With parallel workspaces (several Conductor workspaces on the
    same repo), that means a learning captured in one is visible to a curation pass run from another —
    which is the whole point of a shared store rather than a local cache.
  - Trade-off: the worktree becomes a runtime dependency for **capture**, not just for reading. If it is
    absent, capture cannot land. That failure must be **visible, not silent** — a no-op capture is worse
    than no capture, because it looks like the loop is working when nothing is being recorded.
  - **Requirement — the read path must never read `staging/`.** Staged content is ungated,
    auto-captured, and unreviewed. If retrieval could surface it, ungated content would steer future
    tickets, which is precisely the vector the gate exists to close. Promoted entries and staged
    candidates must be separate trees, and retrieval is scoped to promoted entries only.
  - **Requirement — capture filenames must be collision-free across concurrent writers.** Parallel
    workspaces capturing at the same moment must not contend; entry IDs need to carry enough
    distinguishing context (workspace, run, sequence) that two simultaneous captures never target the
    same path. This is the concurrency reason the entry-per-file decision already exists.
  - Source: design.md Pending Decisions · Decided 2026-07-31

- **Capture and propagation of decisions and progress are automatic, not agent-elected.**
  - Rationale: stated requirement. The four existing capture points fail partly because they depend on
    the agent choosing to act at the moment it is finishing and least inclined to. Turn- and
    subagent-boundary events fire regardless of what the agent decides.
  - Trade-off: automatic capture writes lower-signal material than deliberate capture would. Accepted —
    the gate is where signal is enforced, and the literature is unanimous that filtering belongs at
    admission, not at capture.

- **A protected-path boundary is enforced at the tool-call layer, and denial does not depend on any
  instruction text.**
  - Rationale: the threat model is injected instruction that survives into memory and is legitimized as
    a learned pattern (zombie agents). A prompt-layer control is defeated by exactly the class of input
    it exists to stop. `PreToolUse` denial is not, because it is evaluated outside the model's
    influence.
  - Trade-off: silent machinery that can surprise, and a hard dependency on hook events beyond the two
    this repo currently registers (`.claude-plugin/plugin.json:10-45`). The design must degrade
    gracefully where those events are unavailable, following the existing beads graceful-degradation
    precedent.

- **Enforcement is hook-only for v1. The CI and branch-protection layer is designed but not built until
  the loop runs unattended.**
  - Rationale: the hook covers the agent write path, which is the only path that exists while a human is
    driving every run. CI and CODEOWNERS cover human and out-of-band writes, which only become a real
    exposure once the loop operates without someone watching.
  - Trade-off: v1 has a known, named hole — anything not going through the agent's tool layer is
    unguarded. Accepted deliberately, with the closing condition stated: build the CI layer before the
    first unattended run, not after.
  - Source: Fork 1 · Decided 2026-07-31

- **One generic enforcement hook ships in the plugin, opt-in via host-repo detection, with the
  protected-path set declared per-repo by config. This repo declares the workbench-core paths; other
  repos declare their own.**
  - Rationale: the protected set is genuinely two sets with one shape. The workbench-core paths
    (`commands/`, `agents/`, `skills/`, `hooks/`, the eval corpus) are steering machinery only in a
    wb-development repo. The generic paths (a host project's own `CLAUDE.md` and `.claude/` config, and
    the store's write-policy config) carry the same zombie-agent exposure in *any* repo running the
    loop. One mechanism with a per-repo declared path set covers both without shipping a rule that is
    nonsense outside this repo — and it mirrors the per-repo scoping already decided for the store
    itself.
  - Trade-off: a repo with no declared config gets no enforcement at all. Enforcement is therefore
    **fail-open across repos and fail-closed within a configured repo** — an unconfigured repo is
    unprotected rather than protected-by-default. Accepted because the alternative (deny-by-default in
    every installed repo) would block users editing their own identically-named directories, which is
    the worse failure.
  - Consequence: **the config that declares the protected set must declare itself.** It is core
    self-extension by definition, so the loop cannot edit it. That makes the moment the config is first
    created the trust anchor of the whole scheme, and every later change to it a human-only act.
  - Source: design.md Pending Decisions · Decided 2026-07-31

- **This repo's protected set is the fifteen paths committed in `.wb-knowledge.json`, not the six the
  execution plan enumerated.** Added beyond `commands/`, `agents/`, `skills/`, `hooks/`, `CLAUDE.md` and
  the config: `scripts/`, `.claude-plugin/`, `.claude/`, `AGENTS.md`, `.wb-knowledge.schema.json`,
  `knowledge/entries/`, `knowledge/SCHEMA.md`, and — added by P1-T9 — `package.json` and
  `package-lock.json`.
  - Rationale: each is steering machinery under the design's own default-deny rule. `scripts/` holds hook
    implementations, `.claude-plugin/` is where hooks are *registered* (protecting `hooks/` while leaving
    the registration writable would be a gap, not a boundary), `AGENTS.md` and `.claude/` steer sessions,
    `knowledge/entries/` is what retrieval reads, and `SCHEMA.md` defines what a valid entry even is.
    Protecting the config while leaving its schema writable would let the loop relax the rules the config
    is validated against — the same bypass one level up.
  - Trade-off: an armed self-extension run cannot write its own tests or scripts, so any new tooling a
    curation pass wants must come through a human. Accepted; that is the same trade as the rest of the
    boundary. Note this costs nothing during ordinary development, where the hook is inert.
  - `knowledge/staging/` is deliberately **excluded** — capture writes there, and staging is ungated by
    design. Its absence from the set is load-bearing, and `scripts/test-knowledge-config` asserts it.
  - **`package.json` / `package-lock.json` (added 2026-07-31 by P1-T9, pending human confirmation).**
    P1-T9 made `ajv` the enforcement mechanism behind the schema, which made the files pinning `ajv`'s
    version load-bearing. An armed run able to edit them could pin a validator that accepts anything, and
    every enforcement test would still report green — the same bypass as editing the schema, one level
    further up. Asserted in `scripts/test-knowledge-config` rather than required by the schema, because
    it is repo-specific: a host project may have no `package.json`, whereas the config and its schema are
    universal. Noting the general shape: **each time enforcement gains a new mechanical dependency, that
    dependency joins the protected set** — the boundary has to follow the machinery.
  - Source: tasks.md Phase 2 Prerequisites · Decided 2026-07-31, amended 2026-07-31 (P1-T9)

- **The hook is inert during normal development and armed only while a self-extension / curation run is
  active. While armed it is three-state: `ask` when a human is present, hard `deny` when the run is
  full-auto or unattended.**

  | Context | Hook behaviour |
  | --- | --- |
  | Normal development, no loop run active | Inert — never fires |
  | Loop run active, interactive session | `permissionDecision: "ask"` — human approves each write |
  | Loop run active, full-auto / unattended | `permissionDecision: "deny"` — no write, explicitly refused |

  - Rationale: the locked constraint requires a human *in the loop*, not that the human do the typing.
    `ask` forces a permission prompt that auto-accept mode cannot bypass, so no injected instruction can
    self-approve — while still letting the maintainer say "apply proposal 7" and approve it
    consciously. When there is no human to ask, there is no loop to be in, so the only correct answer is
    refusal. Staying inert outside a loop run keeps ordinary plugin development completely unaffected,
    which was a stated success metric.
  - Trade-off: arming state becomes a control surface, and a narrower enforcement window than
    always-armed. Accepted because the threat being defended against is the loop acting on its own; a
    maintainer editing by hand was never the risk.
  - **Why deny rather than letting `ask` time out**: an unanswered prompt stalls, which is
    non-deterministic and reads as a hang. An explicit deny is deterministic, legible in the log
    ("denied: full-auto"), and cannot be resolved by an auto-approver appearing later in the run.
    Full-auto self-extension therefore fails closed and loudly, by design.
  - **Consequence — the arming mechanism is itself core self-extension.** If the loop can set or clear
    its own armed state, it can disarm itself and every other control falls. Arming must be established
    by the human act that initiates the run (the manual trigger, or the scheduler), outside the agent's
    tool layer, and the arm/disarm state must be part of the protected config. The same applies to
    whatever signals "full-auto" — if the loop can claim to be interactive, it can downgrade `deny` to
    `ask` and then auto-approve.
  - Source: design.md Pending Decisions · Decided 2026-07-31, amended same day

- **The interactive half of the `ask` verification is a human-run gate that must pass before Phase 1
  begins — implementation does not start on an unobserved row of the behaviour table.**
  - Rationale: Phase 0 established headlessly that auto-accept never *silently approves* an `ask`, which
    closes the self-approval vector. What it cannot establish is whether an interactive session with
    auto-accept enabled renders a visible prompt — which is exactly what the middle row of the three-state
    table claims. Deferring it to the Phase 2 checkpoint would mean building the whole enforcement layer
    on the one row of its own behaviour table that has never been observed.
  - Trade-off: implementation stalls on a manual step that cannot be automated from inside an agent
    session. Accepted — it is one prompt at a terminal, against the cost of discovering at the Phase 2
    checkpoint that the middle row does not exist.
  - Consequence if it fails: `ask` never prompts interactively, the armed hook collapses to two states
    (inert / `deny`), and the three-state decision above must be re-opened before Phase 2 per the Phase 0
    checkpoint. Note this is a usability failure, not a security one — the collapse direction is toward
    refusal.
  - Source: tasks.md Phase 2 Prerequisites · Decided 2026-07-31

- **All core self-extension requires a human in the loop. Permanently, with no configurable override.**
  - Rationale: a loop that can weaken its own evaluator makes its own tests easier while continuing to
    report success, and every downstream gate silently loses its signal. This is the reward-hacking
    failure mode in research.md §1.5.
  - Trade-off: full autonomy over the harness is given up permanently, not deferred. This is the
    intended trade.
  - **Core self-extension** is: the eval corpus and its rubrics; the harness components (`commands/`,
    `agents/`, `skills/`, `hooks/`, `CLAUDE.md`); and the gate and write-policy configuration itself.
    Ambiguous cases are default-denied into this set. The third item is the one that must be hardest —
    if the loop can edit the policy deciding what needs review, every other control is bypassable in one
    move and the bypass reads as a routine config change.
  - Source: research.md Open Question 4, locked constraint · Decided 2026-07-31

- **Write policy is a per-project configurable preference defaulting to the strictest setting; when
  relaxed, it relaxes along origin.**
  - Rationale: trust posture legitimately differs by repo. Origin — verified tool output versus model
    narration — is the tiering axis that maps to evidence rather than to a self-assessed category the
    model could mislabel.
  - Trade-off: a configuration surface is itself attack surface, which is why it is enumerated as core
    self-extension above.
  - Constraint: the configuration must be **unable to express** "auto-promote core self-extension." That
    is not a setting the surface offers, because a configurable control over the control is the bypass.
  - Source: research.md Open Question 5, as amended · Decided 2026-07-31

- **Evaluation is layered: a fixture corpus as static baseline, plus AHE-style prediction-then-verify
  for periodic feedback. Deferred out of v1.**
  - Rationale: the fixture corpus alone goes stale and under-covers; prediction-then-verify alone has no
    baseline to regress against. Together the corpus becomes a maintained artifact. Discovery from the
    verify loop refills corpus gaps.
  - Trade-off: deferring it means v1 cannot demonstrate that the store improves anything. Accepted for
    v1 only, on the grounds that the entry shape should be proven on real content before a corpus is
    built to measure it.
  - Hard constraint carried forward: corpus changes are additive-only, human-reviewed, and can never
    weaken, relax, or remove an existing failing case.
  - Source: research.md Open Question 4 · Decided 2026-07-31

### Data Model

- **Entry fields.** Every entry carries: a stable **ID**; the **claim** as one dense self-contained
  block; **provenance** (the cited `file:line` refs and the **commit SHA the entry was verified
  against**); **confidence**; **scope tags** (repo / subsystem / ticket class); **kind** (*semantic* —
  how this works; *procedural* — how to do this kind of change here; *episodic* — what happened and
  why); and **origin** (tool-verified versus model-narrated, which is what the write policy tiers on).
  - Rationale: this is the minimum set that makes the other decisions possible — ID enables delta
    addressing, provenance enables computable staleness, scope tags counter negative transfer, origin
    drives the write policy.
  - Trade-off: heavier than prose notes, and the cost lands on the write path. Mitigated by automatic
    capture — the agent is not asked to fill these in deliberately.

- **Staleness is a computed predicate, not a stored flag.** An entry is *suspect* when any cited path
  changed between its verified-at SHA and `HEAD`. Suspect entries are then referred to
  `agents/research-validator.md` for a real verdict.
  - Rationale: keeps the cheap deterministic check separate from the expensive model check, so the
    whole store can be swept for free and only the suspects cost anything.
  - Known limit: this does not detect decay in *procedural* or *episodic* entries that cite no files
    ("we tried X and it didn't work"). Those decay on a different clock, and the literature offers only
    eviction policies, not detection. Handled by curation, not by invalidation.

- **Promoted entries carry a prediction.** Each declares its expected effect, verified against
  subsequent runs, and is reverted at file granularity when the prediction fails.
  - Rationale: AHE's decision-observability pillar — this is what converts promotion from
    trial-and-error into a falsifiable contract.
  - Trade-off: predictions are only as good as the verification substrate, which v1 defers. Until the
    corpus exists the prediction is recorded but weakly checked; that is a stated v1 limitation, not a
    silent one.

- **Curation operations are add / update / merge / deprecate.** Merging is bounded by a diversity rule:
  keep entries that each win on *some* class of ticket rather than collapsing to one canonical best
  practice.
  - Rationale: CODESKILL's lifecycle is the established answer to skill bloat; GEPA's Pareto front is
    the established caution against over-merging. Both apply.

### Integration Points

- **Read** — `commands/create_research.md:47-60` (Step 0) is the primary insertion point, extending the
  existing bootstrap rather than adding a parallel one; it inherits the best-effort/never-blocking
  contract at `:60`. `commands/resume_handoff.md:158` gains a second input source alongside the handoff.
  Retrieval is scoped by tags and bounded in count — never a wholesale load, because retrieval noise and
  negative transfer worsen as the store grows.
- **Capture** — the four existing points (`validate_execution.md:381`, `create_handoff.md:214-218`,
  `implement_tasks.md:494`, `implement_coordinated.md:652`) become sources rather than terminals.
  `validate_execution` is the highest-signal of the four because it is the only phase with ground truth:
  it has already compared plan to reality and classified deviations as justified or unjustified
  (`:279-291`), which is exactly the verifier-grounded failure record Self-Harness's weakness-mining
  stage consumes.
- **Verification** — `agents/research-validator.md` is reused unchanged as the claim verifier. The
  promotion reviewer must be a **fresh-context** agent, per `skills/touch-grass/SKILL.md:88`, which
  already records that a same-context reviewer rubber-stamps its own work.
- **Structure** — `skills/project-structure/SKILL.md` currently declares four categories (research.md /
  design.md / tasks.md / thoughts/). The store is a fifth, cross-ticket category and must be declared
  there, or the existing separation rules will not know where it belongs.
- **Tiering** — the curation pass is high-judgment batch work. `skills/model-help/SKILL.md:79` already
  establishes that the quality floor is inviolable; the pass must be tiered on judgment, not routed to
  the cheapest agent because it runs unattended.
- **Tracking** — **git is the source of truth for promotion proposals; beads is a queryable overlay
  where available.** The proposal artifact *is* a file on the store branch with history behind it, so
  git already carries state, provenance, and revert. Beads adds status querying and dependency tracking
  on top, subject to the fast-fail probe (`hooks/setup-beads-mode.sh`, `docs/beads-fast-fail.md`), and
  the loop runs unchanged without it — this workspace has neither `bd` nor `.beads/`.
  - Rationale: the loop must work in any repo wb is used on, and a hard beads dependency would make the
    store unusable exactly where it is most useful — a fresh project that has not adopted beads yet.
  - Trade-off: **this inverts the repo's normal convention for one subsystem.** `CLAUDE.md` and
    `commands/validate_execution.md:65` establish beads as the authoritative status source, with
    markdown lagging. That rule exists because a task's status lives nowhere else; a proposal's status
    lives in its own file and commit history. The inversion is deliberate and scoped to proposals only —
    everything else in wb keeps beads as the source of truth.
  - Source: design.md Pending Decisions · Decided 2026-07-31

- **`ajv` becomes a hard dependency, and `.wb-knowledge.json` is validated against its schema in the test
  suite.**
  - Rationale: the config is the trust anchor, and P1-T6's "auto-promote core self-extension is
    unexpressible" is currently guaranteed only by 31 structural `jq` assertions — which verify the schema
    *says* the right thing, not that anything rejects a config violating it. A hand-edited config would be
    caught only for the properties those assertions happen to cover. For the one file in the repo whose
    integrity every other control depends on, "probably fine" is the wrong standard.
  - Trade-off: the repo's first hard runtime dependency beyond `markdownlint-cli`, which means a
    `package.json` and an install step where there was none. Accepted deliberately for this file.
  - Consequence: the negative fixtures already described at the bottom of `scripts/test-knowledge-config`
    become real tests — a config with `write_policy.core_self_extension`, one with
    `model_narrated: "auto-promote"`, and one whose `protected_paths` omits itself must each be *rejected*
    by the validator, not merely unmatched by an assertion.
  - **Implemented 2026-07-31 (P1-T9).** `ajv` pinned at 8.20.0 as a devDependency;
    `scripts/validate-json-schema` compiles the schema and validates data files (exit `0` valid / `1`
    invalid / `2` bad input / `3` ajv not installed); `scripts/test-knowledge-config` feeds it thirteen
    jq-mutated copies of the live config plus one **positive control** — relaxing `tool_verified` to
    `auto-promote` must still be accepted, or a validator that refused everything would turn every
    rejection green. 47/47.
  - **Constraint the implementation adds, load-bearing for Phase 2:** the dependency is **dev-time only**.
    A marketplace install is a bare clone with no `node_modules`, so `hooks/knowledge-guard.sh` must read
    `.wb-knowledge.json` with the `scripts/lint-hook` jq-then-grep idiom and must never invoke the
    validator. The validator establishes the config is well-formed at review time; the hook must still
    degrade gracefully when handed one that is not — which is the malformed-config → `deny` row of the
    behaviour table.
  - Source: tasks.md "What Phase 1 surfaced" · Decided 2026-07-31 · Implemented 2026-07-31

- **This project's own implementation is tracked documentation-only. No `bd init`; `tasks.md`'s local
  IDs (`P0-T1` …) are the only task identifiers.**
  - Rationale: adding beads mid-build would mean standing up an epic, 7 milestones, and 37 issues before
    any of them can be worked, and the store being built here is deliberately designed to run without
    beads anyway — so the build is dogfooding its own no-beads path. The plan documents already carry
    the phase structure a fresh session needs.
  - Trade-off: **there is no cross-session status.** A resumed session reads what the plan *is*, not what
    is *done*, and must reconstruct progress from git history and the Phase 0/1 gate markers in
    `tasks.md`. This is the exact failure the plan documents warn about; it is accepted here and must be
    compensated for by keeping the phase gates in `tasks.md` current as each phase lands.
  - Note on convention: `CLAUDE.md` mandates beads for all task tracking, so this is a scoped exception
    for this project, not a general relaxation. The prohibition on substitutes still holds in full — no
    TodoWrite, no TaskCreate, no markdown checkboxes repurposed as progress. The checkboxes in `tasks.md`
    remain verification criteria only.
  - Source: tasks.md Current Blockers · Decided 2026-07-31

## Scope Definition

### In Scope

- The protected-path enforcement boundary, denying agent-originated writes to core self-extension paths.
- The entry format, including provenance sufficient to compute staleness deterministically.
- Automatic capture from turn and subagent boundaries into an ungated staging area.
- A manually-triggerable batched curation and promotion pass, with a fresh-context reviewer.
- The `docs/beads-integration-learnings.md` migration as the single end-to-end test case — converting
  its surviving learnings into entries, catching its three `CLAUDE.md` contradictions through the
  invalidation path, triaging its dropped backlog (`:244-252`), and marking the original superseded.
- Declaring the store as a category in `skills/project-structure`.

### Out of Scope

- **The fixture eval corpus and rubrics** — deferred until the entry shape is proven on real content.
- **The CI / branch-protection / CODEOWNERS layer** — designed here, built before the first unattended
  run.
- **Automated promotion of anything** — every promotion in v1 is a human-reviewed diff.
- **Cross-repo knowledge transfer** — excluded by the per-repo scoping decision.
- **Vector, graph, or embedding-based retrieval** — scoped tag retrieval only. The large-repo memory
  literature shows naive embedding retrieval failing on exactly the staleness axis this design solves
  with git.
- **Changing how `docs/plans/` works** — per-ticket directories stay per-ticket; the store is a sibling.
- **Any relaxation of the write policy** — the strict default ships; the relaxed tiers are designed but
  not exercised.

## Success Criteria

### Functional Requirements

- [ ] An agent-originated write to a core self-extension path is denied, and the denial holds when the
      agent has been instructed to perform the write.
- [ ] A maintainer editing `commands/` or `skills/` by hand is not blocked.
- [ ] A learning captured during one ticket run is present in staging without the agent having chosen
      to record it.
- [ ] A promotion pass can be triggered manually and produces a reviewable diff, not a live mutation.
- [ ] A promoted entry is retrievable by a later ticket run in a fresh context, scoped by tag.
- [ ] Sweeping the store classifies every entry clean or suspect using git alone.
- [ ] The `beads-integration-learnings.md` migration flags its three contradicted items through the
      invalidation path.

### Non-Functional Requirements

- [ ] Read path is best-effort and never blocking — an unavailable store degrades research, never halts
      it, matching the `create_research.md:60` contract.
- [ ] Enforcement failure mode is closed: if the hook cannot determine whether a path is protected, it
      denies.
- [ ] The plugin remains usable in repos with no store and no beads, per the existing graceful-degradation
      precedent.
- [ ] No entry is readable as instruction under the default write policy.

## Risk Analysis

### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- |
| A shipped deny hook fires in **users'** repos, blocking their edits to their own `commands/` or `skills/` | High | High | Resolved 2026-07-31: the hook is inert unless the host repo declares `.wb-knowledge.json`, and inert again unless a run is armed. Fail-open across repos by design. Verified by hand in a scratch repo at the Phase 2 checkpoint. |
| Hook events beyond the two currently registered are unavailable in a user's Claude Code version | Med | Med | Degrade gracefully to the prompt-layer instruction, and surface that enforcement is unavailable rather than silently proceeding as if it were on |
| Staging accumulates noise faster than the batched pass drains it | Med | High | Curation's merge/deprecate operations; the pass is manually triggerable when backlog builds |
| Retrieval noise / negative transfer as the store grows | Med | Med | Per-repo scoping, scope tags, bounded retrieval count; never a wholesale load |
| Promoted entries are unfalsifiable while the corpus is deferred | Med | High | Predictions are recorded from day one so they are checkable retroactively once the corpus exists; the limitation is stated, not hidden |
| Procedural/episodic entries decay undetected | Med | Med | Explicitly out of the invalidation path; handled by curation review, with the gap named |
| The store's provenance SHAs drift as the unmerged branch diverges from `main` | High | Med | Resolved 2026-07-31: `main` merges forward into the store branch continuously — merge, never rebase, since rebasing rewrites the commits provenance points at. Invalidation sweep runs on sync. |

### Assumptions

Beads is unavailable in this workspace, so these carry no IDs. With beads, each becomes
`bd create "Validate: …" --type=task --priority=2`.

| Assumption | Beads ID | Validated? |
| --- | --- | --- |
| `PreToolUse` deny works as documented in the installed Claude Code version | *(no beads)* | **Validated 2026-07-31** — executed against Claude Code 2.1.195; see Phase 0 findings below |
| `PreToolUse` `ask` is not bypassed by auto-accept | *(no beads)* | **Validated 2026-07-31 — fully, interactive included.** Human-run A/B under `accept edits on`: the control file wrote silently, the sentinel prompted. See Phase 0 findings |
| `Stop` / `SubagentStop` can write files reliably enough for automatic capture | *(no beads)* | **Validated 2026-07-31** — both fired and wrote; payloads carry `transcript_path` |
| `agents/research-validator.md` accepts a knowledge entry as-is without schema changes | *(no beads)* | Pending — structural similarity argued, not tested |
| A generated index keeps the store readable at the scale it actually reaches | *(no beads)* | Pending |
| `docs/beads-integration-learnings.md` contains enough surviving content to be a meaningful test case | *(no beads)* | Pending — 10 learnings, 3 known-contradicted |

### Phase 0 Tracer Bullet — Executed Findings (2026-07-31)

Method: the probes were run as **real headless `claude -p` sessions** in a scratch directory
(`/tmp/wb-hook-probe`) with throwaway `--settings` files, not by editing this repo's
`.claude/settings.json`. Hook configuration is snapshotted at session start, so an in-session edit
would not have been exercised; a fresh child session is the only way to actually execute the probe.
Consequence: `.claude/settings.json` was never modified, and the probe cannot ship.
Environment: Claude Code **2.1.195**, macOS (Darwin 25.5.0), probe model `haiku`.

**Control** — with no hook registered and `--permission-mode acceptEdits`, the `Write` lands. Every
"blocked" result below is therefore attributable to the hook, not to the harness refusing anyway.

| Probe | `default` | `acceptEdits` | `auto` | `dontAsk` | `bypassPermissions` |
| --- | --- | --- | --- | --- | --- |
| `permissionDecision: "deny"` | blocked | blocked | blocked | blocked | **blocked** |
| `permissionDecision: "ask"` | blocked | **blocked** | blocked | blocked | **blocked** |

Load-bearing consequences:

- **`deny` is not bypassable by permission mode.** It holds even under `bypassPermissions` (the
  `--dangerously-skip-permissions` posture), which is the mode a full-auto run is most likely to use.
  The enforcement architecture stands; the convention-only alternative stays rejected.
- **`ask` is not auto-approved by auto-accept.** Under `acceptEdits` the write was refused, and the
  refusal reason (`permissionDecisionReason`) was surfaced to the model verbatim. In every
  non-interactive mode, `ask` degrades to refusal — i.e. it **fails closed**, which is the posture the
  full-auto row of the three-state table wants anyway.
- **The interactive middle row is confirmed too** (human-run, 2026-07-31). Run as an A/B inside one
  session started with `--permission-mode acceptEdits`, footer reading `accept edits on`: a control file
  the hook ignores was written with **no prompt**, and `sentinel.txt` — differing only in the filename the
  hook matches — **prompted for approval**. Auto-accept is therefore provably live and the hook's `ask`
  is what interrupts it. The three-state table is now observed in every row rather than argued.
  - An earlier attempt was discarded as inconclusive: it wrote only the sentinel, in default mode, where
    a `Write` prompts regardless. The control file is what makes the result mean anything.
- **`Stop` and `SubagentStop` both fire and write reliably.** Payloads carry `session_id`, `cwd`,
  `permission_mode`, `last_assistant_message`, `transcript_path`, and — for `SubagentStop` —
  `agent_id`, `agent_type`, and `agent_transcript_path`. Capture (Phase 3) has a richer substrate than
  the design assumed: the full transcript is addressable from the hook, not just the last message.
- **Full-auto is *not* reliably detectable from the hook payload** — this answers one of `tasks.md`'s
  Implementation Discoveries, and it answers it negatively. `permission_mode` *is* present in the
  `PreToolUse` payload, but a headless `claude -p` run at default settings reports
  `"permission_mode":"default"`, identical to an interactive session. Attendance is therefore not
  inferable; it must be **asserted by the arming trigger**, exactly as the arming decision above already
  requires. The elevated modes (`acceptEdits` / `auto` / `dontAsk` / `bypassPermissions`) are usable only
  as a one-way signal: they can raise suspicion of unattended operation, never confirm attendance.
  Practical rule for Phase 2: absent a positive interactive assertion from the arming act, treat the run
  as full-auto and `deny`.
- **The path the hook receives is a resolved absolute path, and it is not necessarily the path anyone
  named.** In the interactive run, Claude Code 2.1.195 redirected both writes into a per-session
  scratchpad — `/private/tmp/claude-501/<project-slug>/<uuid>/scratchpad/sentinel.txt` — rather than the
  working directory the prompt asked for, and `/tmp` arrived as its `/private/tmp` realpath. The hook saw
  the real destination and matched correctly, so the probe stands; but two Phase 2 consequences follow.
  **(a)** `hooks/knowledge-guard.sh` must compare *resolved* paths (symlinks and `/tmp` → `/private/tmp`
  included) against the protected set, never the literal string in `tool_input`. **(b)** A naive
  repo-relative prefix match is both bypassable and wrong: an agent write can land somewhere entirely
  outside the repo, which means "not under a protected prefix" cannot be read as "safe" — it must fall
  through to the indeterminate case, which the behaviour table already sends to `deny` inside a
  configured repo.

## Rejected Alternatives

### Option: Convention-only enforcement (prompt-layer)

- **Approach**: express the protected-path rule as instruction text in the commands and rely on human
  review at commit time.
- **Rejected because**: the threat model is injected instruction text. A prompt-layer control is
  defeated by precisely the class of input it exists to stop. The tracer bullet established that a
  mechanical alternative exists at the same cost, making this strictly dominated.
- **Trade-offs**: would have had zero dependency on hook availability and shipped as ordinary plugin
  content.

### Option: Single-file knowledge store

- **Approach**: one growing markdown document, appended to.
- **Rejected because**: reintroduces merge conflicts between concurrent ticket agents, and invites the
  monolithic rewrite that produces ACE's documented context collapse.
- **Trade-offs**: markedly easier to read and cheaper to load. Recovered via the generated index.

### Option: Merge the store into `main`

- **Approach**: knowledge ships as part of the plugin.
- **Rejected because**: couples continuous knowledge improvement to the discrete, version-keyed
  marketplace release path.
- **Trade-offs**: simpler transport, no branch-tracking policy needed. Revisit if the unmerged-branch
  mechanism proves awkward — this decision was explicitly recorded as provisional.

### Option: Per-ticket promotion

- **Approach**: gate and promote at the end of every forge.
- **Rejected because**: a gate strict enough to prevent bloat rejects most candidates, making it
  expensive friction on every ticket.
- **Trade-offs**: learnings would never decay in staging. Mitigated by the manual trigger.

### Option: Separate knowledge repository

- **Approach**: the store lives outside `workbench` entirely, consumed as a data source.
- **Rejected because**: contradicts the per-repo scoping decision, and the governance benefit it buys
  is available from the deferred CI layer without the extra repo.
- **Trade-offs**: strongest isolation and the cleanest audit boundary.

## Pending Decisions

Beads is unavailable, so these carry no IDs. With beads, each becomes
`bd create "Decide: …" --type=task --priority=1`.

| Decision Needed | Beads ID | Blocks |
| --- | --- | --- |
| How enforcement is scoped so a marketplace-installed plugin does not deny writes in users' repos — opt-in marker file, host-repo detection, or ship the hook unregistered | *(no beads)* | — resolved 2026-07-31 |
| Whether the deny hook is always-armed over a fixed path set, or armed only during a self-extension/curation run | *(no beads)* | — resolved 2026-07-31 |
| How the unmerged store branch tracks `main` so entry provenance SHAs stay meaningful | *(no beads)* | — resolved 2026-07-31 |
| Where the staging area physically lives, given `docs/plans/` is gitignored (`.gitignore:7`) and the store branch is unmerged | *(no beads)* | — resolved 2026-07-31 |
| Whether promotion proposals are tracked in beads or as branch commits only, given beads is absent here | *(no beads)* | — resolved 2026-07-31 |

*All 5 pending decisions resolved as of 2026-07-31 via `/wb:resolve_questions`; each is recorded in
`## Technical Decisions` above. The `### Assumptions` table stays open by nature — those are settled by
execution and testing, not by a decision.*

## References

- Research: [research.md](research.md)
- Locked constraint: research.md → Open Questions #4
- Enforcement probe: [Claude Code hooks reference](https://code.claude.com/docs/en/hooks)
- Existing hook precedent: `.claude-plugin/plugin.json:10-45`, `scripts/lint-hook`
- Reused verifier: `agents/research-validator.md`
- Structure authority: `skills/project-structure/SKILL.md`
