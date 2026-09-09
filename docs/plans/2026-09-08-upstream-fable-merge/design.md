---
project: upstream-fable-merge
ticket: N/A
created: 2026-09-08
status: implementing
last_updated: 2026-09-08
git_commit: a6de084d1cb89e81ca344e88c39b4f72d9ba19e2
git_branch: thescubageek/gabe-fable-merge-research
repository: thescubageek/workbench
designer: wolfpacksteve@gmail.com
depends_on: research.md
design_approach: tracker-free-modernization
task_tracking: markdown-checkboxes
status_note: "Decisions D1–D17 set by the user 2026-09-08; D8 expanded and PD1 resolved on the user's cross-session-bootstrap requirement; D19 added on the user's obsolete-docs question; D18 proposed as a rider; D20 added 2026-09-08 on the user's go-ahead to close the guardrail gap. Approved 2026-09-08 by the user invoking /wb:create_execution; PD2, PD3, PD4 and assumption A1 all resolved 2026-09-08 via /wb:resolve_questions — see Technical Decisions → Resolved Decisions. Assumptions A4 and A5 validated 2026-09-08 by the Phase 0 layout probe and its smoke session. D21 added 2026-09-08 (plan persistence), with the lint-scope and commit-cadence resolutions, via /wb:resolve_questions. Nothing gates execution."
---

# Design: Tracker-Free Modernization (wb 2.0.0)

## Implementation Notes

Started 2026-09-08 (status `approved` → `implementing`; the approval record lives in
`status_note`). Phase 0 landed: the layout probe returned **proceed with D1/D2 as designed**,
so nothing in this document needs re-planning. D16's lint fix is in. Assumptions A4 and A5
moved from Pending to Validated on probe evidence, which means D2's on-demand reads and D9/PD4's
alias stubs rest on a measurement rather than on upstream's report, and D19's
"a shipped skill may link only into `plugin/docs/reference/`" rule has a verified read path
behind it. Per-phase execution notes live in `tasks.md` → Implementation Notes; this section
records only what changed for the *design*.

## Problem Statement

Our fork carries the pre-modernization shape of a plugin whose upstream has since been
rebuilt: monolithic `commands/*.md` files loaded whole at invocation, a shipped tree with no
boundary between runtime and maintainer docs, no optional architecture stage, no defense
against compaction drift, a worker failure path that retries with identical context, and a
prompt-scaffolding root that mandates directives the current model generation does not need.

Two problems are ours alone rather than inherited. First, the plugin **hard-requires a task
tracker that is not present**: `bd` is not installed, there is no `.beads/` directory in this
repository, and the beads plugin whose 20 `/beads:*` commands our help documents is not in
the marketplace cache. Six commands (`create_execution`, `implement_tasks`,
`implement_coordinated`, `forge`, `validate_project`, `validate_execution`) reach a
stop-and-prompt gate on a dependency that cannot resolve. Second, the tracker never earned
its cost: of 363 `bd` invocation lines across 31 files, the dependency graph that
`create_execution` builds with `bd dep add` is a **derived index** of ordering already fixed
in tasks.md, and the commands that consume it explicitly instruct ignoring the markdown
status surface that already exists beside it.

Meanwhile the model generation the scaffolding was written for is gone. Fable 5.1 is
available as a deliberate upshift, but nothing in our tree routes to it, and the escalation
path we do have spends two identical-context retries on failures that upstream's evidence
says truncate at the same point every time.

### Success Metrics

- A session in a repository with no tracker installed runs the full pipeline end to end with
  no stop-and-prompt gate and no degraded path
- `grep -rn "bd \|beads\|BEADS_MODE"` over the shipped tree returns nothing outside a
  migration note
- Task and phase status is readable from `tasks.md` alone — checkbox state plus frontmatter
  counters — and one command is the only writer of those counters
- Invocation-time context for the workflow stages drops by roughly a third against v1.12.5,
  with no stage losing content
- A compacted session receives, in its first post-compaction context, an instruction to
  re-read the active plan documents before asserting what they say
- A session whose predecessor was killed abruptly — no handoff, no clean shutdown, nothing
  appended on the way out — can state from its first context alone which plan is active, what
  the previous session was attempting, what the next action is, and what is left uncommitted
- Every knowledge entry carries a date and a way to check whether it is still true, and no
  task outcome appears in the knowledge file
- A verified task failure produces exactly one escalation attempt at a named higher tier,
  then stops at the phase checkpoint — never a same-context retry
- Fable appears in no default path; every route to it is an explicit upshift the user or the
  coordinator elects
- `./scripts/lint --fix` exits non-zero when findings remain, in every mode
- One statement of the worker tier rule exists in the shipped tree

## Design Approach

**Tracker-free modernization**: adopt upstream's structural and discipline work, and replace
its tracking substrate with the markdown-native one our sibling workflow already runs, rather
than porting upstream's beads realignment.

The port is organized around a single observation from research: our command bodies and
upstream's skill bodies share the same Step 1–8 skeletons and heading structure, so the
modernization is a **mechanical re-shaping of files we already have**, and the prose
improvements land in the same edit. Removing beads is not a separate subtraction — it is what
makes the re-shaping cheap, because roughly 110 lines of `bd create` / `bd dep add`
choreography in the largest command file disappear instead of being carried across.

### Why This Approach

- **The tracker's capability is already duplicated in markdown.** `tasks.md` carries
  frontmatter counters (`status`, `current_phase`, `total_tasks`, `completed_tasks`,
  `commands/create_execution.md:192-196`), per-task checkboxes (`:247-250`, `:317-328`),
  phase checkpoints (`:348-359`), a completed-tasks archive (`:388-393`), and
  blockers/notes/modified-files sections (`:397-412`) that have **no** beads equivalent. The
  commands' own text is what makes it inert: `create_execution.md:284` ("Task status is
  tracked ONLY in beads"), `implement_tasks.md:685-686` ("NEVER treat markdown as source of
  truth"). Removing beads is largely deleting the instruction to ignore what is already
  written.
- **A working precedent exists in this environment, by this author.** The CaseSmith
  (`/law:*`) workflow — source at `/Users/thescubageek/projects/casesmith/claude-code/`,
  installed at `~/.claude/commands/law/` — is the same pipeline shape running tracker-free:
  `create_workplan.md:168` declares `task_tracking: markdown-checkboxes` as an explicit
  frontmatter schema field; `:217` states "**No beads, no external tracker.** Run
  `/law:update_matter_status` to reconcile counters"; `:252` gives the mutation rule ("Flip
  `[ ]` → `[x]` as work completes; update `completed_tasks` in frontmatter");
  `draft_tasks.md:32,143-147,317` gives the execution-side protocol and the phase-completion
  check ("Every checkbox must be `[x]`"), with a DO-NOT list that is the exact mirror of ours
  (`:149-154`: "❌ use beads (`bd` CLI) — CaseSmith does not use it", "❌ skip updating the
  checkbox after completion"); `update_matter_status.md:69-73,365` gives the reconciliation
  mechanism and the doctrine ("Markdown checkboxes are the ONLY source of truth"); and
  `skills/matter-structure/SKILL.md:171-173` carries a dedicated "No Beads" section — the
  precedent for where the doctrine statement belongs, whose analogue here is
  `project-structure`. It is also running in a live matter, not just specified. This design
  adopts that convention rather than inventing one.
- **Our version is the precedent plus a durable record it lacks.** CaseSmith's matters are
  gitignored by default (`update_matter_status.md:461`), so checkbox-plus-counter is its
  *entire* state surface with nothing corroborating it. Our plans live in a git repository,
  so D14's one-task-one-commit rule gives us an independent audit trail the precedent has
  been running without.
- **The dependency graph is not load-bearing.** Execution is strictly sequential
  (`commands/implement_coordinated.md:2,10,124,605,650`); `bd ready` only names the next task
  in an order the document already fixes; the edges are generated mechanically from the fixed
  Setup→Implementation→Testing→Integration and Phase-N→Phase-N+1 sequence
  (`create_execution.md:576-582`); only two sites ever inspect a milestone's `blockedBy`
  (`implement_coordinated.md:527,539`), and the sequential command approximates the same
  answer with a title grep (`implement_tasks.md:393`); and no epic parent-child relationship
  is traversed anywhere at runtime.
- **The planning records carry no unique information.** `resolve_questions.md` already
  duplicates every resolution into the markdown decision log (`:184-189`, `:219-226`) and
  states that "the canonical resolution lives in the file or the bead" (`:316`); it already
  degrades silently when beads is absent (`:323`). The tracker holds only an ID and an
  open/closed bit used as a gate.
- **Upstream's own evidence bounds what to change.** Phase 1 of its Fable work was additive
  and needed no behavioral gate; its Phase 2 trims were blind-trialled and *rejected* for
  barriers and scope blocks. So this design adds guardrails and leaves barrier and
  scope-block volume alone.

## Technical Decisions

### D1: The shipped runtime moves under `plugin/`

- **Decision**: the runtime installers receive lives in `plugin/`; the marketplace manifest
  stays at the repository root pointing at `./plugin`; maintainer documentation and plan
  directories stay in a root `docs/` that is never shipped. A shipped
  `plugin/docs/reference/` holds cross-cutting docs that skills link to at runtime.
- **Rationale**: today every file is shipped, so maintainer material, plan artifacts, and
  research notes are part of the installed payload, and there is no place to put a shared
  runtime reference that several skills can cite instead of restating. The split is also the
  precondition for D2 — progressive disclosure needs a stable relative-link root.
- **Trade-off**: every path in our own tooling, the local-dev instruction, and the install
  identity changes once. `--plugin-dir` must point at the subdirectory, which is a documented
  upstream gotcha for sessions that forget.
- **Pattern reference**: research.md §7; `.context/upstream/CLAUDE.md` layout section;
  `.claude-plugin/marketplace.json` `source` field.

### D2: Workflow stages become skills with progressive disclosure

- **Decision**: each `commands/<name>.md` becomes `plugin/skills/<name>/SKILL.md` carrying
  the judgment and control flow, with output templates, sub-agent prompts, and reference
  material moved to sibling files read on demand. Workflow skills declare
  `allowed-tools: Read` so those reads do not prompt mid-skill; background discipline skills
  declare `user-invocable: false`.
- **Rationale**: measured on our own files, this cuts invocation-time context from 7,465 to
  roughly 4,700 lines (−37%) across the fourteen stages while *increasing* total content —
  the material is not lost, it is deferred until the step that needs it. Our step skeletons
  already match upstream's, so the split is a re-shaping rather than a rewrite. The
  `allowed-tools` line is not cosmetic: upstream found in release testing that without it,
  on-demand reads prompt for permission when the session is in another project.
- **Trade-off**: a supporting file can drift from the SKILL.md that cites it, which a single
  monolith cannot. Mitigated by the explicit "read each when its step directs you to — never
  paraphrase from memory" instruction upstream uses.
- **Pattern reference**: research.md §7 table;
  `.context/upstream/plugin/skills/create_research/SKILL.md:5,12-15`.

### D3: Sub-agents get frontmatter tiers; the main session keeps `model-help`

- **Decision**: agent definitions carry explicit `model:`, `effort:`, and `maxTurns:`
  frontmatter. Main-session model and effort selection stays exclusively with the
  `model-help` skill in gate mode. Neither mechanism restates the other.
- **Rationale**: this follows `model-help`'s own economics — "sub-agent model + effort is
  free… main-session model/effort costs a context reload" (`skills/model-help/SKILL.md:55-56`).
  Free choices belong pinned where they are used; the expensive choice belongs behind the
  switch-cost rule. Upstream pins both per skill and has no central authority; we have the
  authority and should not fragment it. `maxTurns` also gives the search agents a bound we
  currently lack entirely.
- **Trade-off**: two places name models, so the boundary must be stated or it will blur. The
  rule is: anything spawned is pinned at its definition; anything the session itself runs is
  advised by `model-help`.

### D4: Beads is removed; markdown is the status surface

- **Decision**: beads is removed from the shipped tree in its entirety — every `bd`
  invocation, the `BEADS_MODE`/`BEADS_AVAILABLE` machinery and the hook that sets it, the
  "Beads Required" principle, the fast-fail gates, the `/beads:*` command reference, and the
  beads-specific documents. Replacing it:
  - **Task and phase status**: checkbox state in `tasks.md`, mutated as work completes, plus
    frontmatter counters. Checkboxes are the source of truth; counters are a derived
    convenience.
  - **Phase completion**: every checkbox in the phase section is `[x]`.
  - **Durable record**: git. One task, one commit (see D14), so the commit log is the audit
    trail the tracker used to hold.
  - **Planning records** (`Q:` / `Decide:` / `Validate:` / `UI Q:`): markdown sections in the
    document that owns them, with short stable local IDs.
- **Rationale**: the capability inventory shows the tracker's use is overwhelmingly flat
  status write and read, both of which a checkbox expresses; its dependency graph is a derived
  index of document order; its planning records already duplicate into markdown by design;
  and its one unique capability — cross-session persistence — is documented as not working in
  the stealth configuration this repository uses anyway
  (`docs/beads-stealth-mode.md:26`, `commands/create_handoff.md:141-144`). Against that, the
  cost is a hard dependency that is absent from the environment today and six commands that
  halt on it. The user's stated rationale — that a modern model holds plan state across a
  session without an external index — is consistent with what the inventory found: the index
  was never read deeply enough to matter.
- **Trade-off**: we lose queryable cross-plan state and ready-work computation over a real
  graph. Accepted because neither is consumed today; if a future plan genuinely needs
  parallel task scheduling, that is the moment to reconsider, not now.
- **Pattern reference**: `~/.claude/commands/law/create_workplan.md:168,206,217,252`;
  `~/.claude/commands/law/draft_tasks.md:115,143-147,317`;
  `~/.claude/commands/law/update_matter_status.md:69-71,155-157,365`.

### D5: `update_status` is the sole writer of progress frontmatter

- **Decision**: the frontmatter progress fields have exactly one writer, `update_status`.
  Implementation stages flip checkboxes and defer counter reconciliation to it; the
  `status-sync` skill gains a drift indicator that compares counter values against actual
  checkbox counts and surfaces a mismatch instead of trusting either.
- **Rationale**: with checkboxes as the source of truth, counters are a cache, and a cache
  with many writers and no owner is exactly how the fields rotted before. We have at least
  two writers today and no stated rule — `create_execution.md:355` edits `current_phase`
  inline at the phase checkpoint while `update_status.md:227-238` also rewrites it; upstream
  already replaced that same checkpoint step with a delegation to its sole writer
  (`create_tasks/templates.md:175`) and states the rule in its `CLAUDE.md`. The drift report
  has a working shape to copy: CaseSmith's `update_matter_status.md:434-443` renders counter
  drift as actual grep counts against the stale frontmatter values and reconciles to the
  counts.
- **Trade-off**: counters can be stale between reconciliations. Accepted — the drift
  indicator makes staleness visible, and the checkboxes are always current.

### D6: Planning records become markdown-native, and the gates read markdown

- **Decision**: questions, decisions, assumptions, and UI questions live as tables or
  sections in the document that raises them, each with a short local ID (`Q1`, `PD1`, `A1`,
  `UIQ1`) and an explicit open/resolved state. `forge`'s barrier checks and
  `create_design`'s cold-start check read those sections. `resolve_questions` drops its beads
  branch and keeps the markdown walk it already has.
- **Rationale**: `resolve_questions` already treats markdown as canonical and beads as a
  supplementary index, and already degrades silently without it — so this decision mostly
  deletes the redundant half. A local ID preserves the one thing the tracker contributed: a
  stable handle to cite from another document.
- **Trade-off**: no cross-plan query for open questions. Accepted; the plan directory is the
  unit of work.

### D7: Ordering is document order; dependencies are stated only where they branch

- **Decision**: phases run in document order and tasks run in order within a phase. A task
  that genuinely depends on a non-adjacent task states it in one field; nothing else encodes
  dependencies. `create_tasks` writes no dependency graph.
- **Rationale**: this is what the current system already does behind the graph — the edges
  are derived from the fixed category and phase sequence, and execution is sequential, so the
  graph's only runtime job is to name the next task in a linear order. Stating the exception
  where it occurs is strictly less machinery than deriving a graph and querying it back.
- **Trade-off**: no automatic detection of an ordering mistake. Accepted; the phase
  checkpoint is where a human reads the plan anyway.

### D8: Cross-session continuity is two artifacts with different lifetimes, delivered at session start

Replaces `bd remember`, which leaves with beads. A new session must be able to resume without
a deliberate handoff having been written, and without relearning what earlier plans already
established.

**Why two artifacts and not one.** The two needs have different lifetimes, write triggers, and
read patterns: *what the last session did* is chronological, plan-scoped, and read as a tail;
*what this repository is like* is curated, repo-scoped, and read whole. Merging them produces a
diary in which the durable facts are buried among stale ones — and we have the cautionary
example in-repo. `docs/beads-integration-learnings.md` (as of `b902566`; D19 deletes it) is
exactly that merge: a 252-line session log whose entries now read as current rules and
contradict them, telling a session to "Always use TodoWrite" (`:233`) against
`commands/implement_tasks.md:684`'s "NEVER use … TodoWrite", and that checkboxes "work well
for within-phase tracking" (`:74`) against the prohibition this plan is only now reversing.
One file would reproduce that failure by construction — which is why D19 removes that
document rather than annotating it, and why this decision keeps the two lifetimes apart.

#### D8a: A session journal, per plan, whose entries are opened at the start of work and closed at the end

- **Decision**: each plan directory carries a `journal.md`: an append-only,
  reverse-chronological record. Entries are **opened when work begins, not written when it
  ends**. On starting a task or phase, the stage appends an open entry naming what it is about
  to do and the exact next action; on completing it, the same entry is closed with what landed
  and its commit range. An entry also carries anything learned that changes how the remaining
  work should proceed, and anything blocking. `create_handoff` appends a pointer to the handoff
  it wrote. `update_status` does not write it — it owns counters (D5).
- **Rationale**: **a session cannot be relied on to get a chance to write anything.** Token
  limits, context exhaustion, a closed laptop, a dead battery, a crashed harness — none of
  these run a shutdown step, and a journal written only at boundaries is silent in exactly the
  cases it exists for. Worse than silent: its tail would still show the *previous* completed
  phase, so a cold session would read a confident, stale "last known good" and never learn
  that work stopped mid-task. Inverting the write — record intent on entry, outcome on exit —
  means an abrupt kill leaves an **open entry**, which is both correct and the most useful
  thing the next session could find: what was being attempted and what came next. An
  append-only file is also safe under multiple writers in a way counters are not, so it needs
  no single-writer rule.
- **The one termination mode we get warning of** is context exhaustion: PreCompact fires
  before it. D11's hook is already registered there, so it refreshes the open entry's
  mechanical fields (timestamp, working-tree state, checkbox counts) on that trigger — no
  judgment, just the facts that would otherwise be lost.
- **Trade-off**: an entry can be left open by a session that simply moved on without closing
  it, so an open entry means "unfinished or interrupted", not "interrupted". D8c's
  reconciliation is what distinguishes them. One more file per plan, bounded by the plan's own
  lifetime — plans complete, and the read path only ever consumes the tail.

#### D8b: A repository knowledge file, curated, committed, one fact per entry

- **Decision**: `.claude/wb/knowledge.md` holds durable facts about the repository — a
  constraint, a convention, a tool quirk — one per entry, each carrying the fact, why it
  matters, the date, the plan it came from, and a **verification hint**: how a future session
  can check whether it is still true. It is committed. Qualification: it qualifies only if it
  would change how the *next* session works. It does not qualify if it is a task outcome (the
  journal has those), a plan deviation (Implementation Notes has those), or true of only one
  task. A session that finds an entry false corrects or deletes it in the same session.
- **Rationale**: this is `bd remember`'s role, which upstream reports a notable uplift from and
  which nothing in our tree currently fills. The verification hint is the part `bd remember`
  lacked: upstream recorded the recency trap — memory is workspace-wide, so one session's
  stumble becomes a permanent rule — and dating an entry beside a way to re-check it is what
  makes staleness detectable instead of authoritative. `.claude/wb/` is the namespace upstream
  already established for the plugin's per-repository, agent-facing material, and unlike
  `docs/plans/` it is not gitignored here, so the knowledge travels with the repository.
- **Trade-off**: curation is manual, so the file is only as good as the discipline applied to
  it. The qualification rule, the one-fact shape, and the correction obligation are what keep
  it from becoming the diary D8's preamble warns about.

#### D8c: The bootstrap arrives in the first context unasked, and is reconciled against the working tree

- **Decision**: the D11 hook does the delivering. On a fresh session start it prints, after the
  orientation: the active plan and its position from checkbox counts and frontmatter, the
  journal's most recent entry verbatim (bounded, tail only), whether that entry is **open or
  closed**, and one line naming the knowledge file and its entry count. Where the journal's
  tail disagrees with the repository — an open entry, or a closed entry sitting beside
  uncommitted changes — the block says so explicitly and names the working-tree state, rather
  than reporting the journal as fact. The knowledge file is read on demand by the stages that
  benefit — the research stages, `create_design`, both implementation stages, and
  `resume_handoff` — rather than printed at start. `resume_handoff` reads the journal tail
  alongside the handoff it was given.
- **Rationale**: "quickly" is the requirement, and any mechanism that needs a command to be
  remembered will not be. The hook is the only thing that runs at exactly the moment a new
  session begins, and it is already scanning plan directories for D11, so the marginal cost is
  one file's tail. Printing the last entry rather than a summary means the first context
  contains the literal next action.
  The reconciliation is what makes the whole scheme survive an abrupt kill. **The one thing
  that always survives is the repository itself** — the working tree, the index, and the commit
  log — so it is the authority the journal is checked against, never the reverse. This composes
  with two decisions already made rather than adding machinery: D14 moves the commit to the
  coordinator after verification, so uncommitted work in the tree is a reliable marker of
  something that did not finish; and D4 makes checkbox state authoritative, so counts are
  current even when nothing was written to the journal. An open entry plus a dirty tree is an
  interrupted task; a closed entry plus a clean tree is a genuine stopping point; the two
  mixed cases are exactly what a cold session needs told rather than guessed.
- **Trade-off**: a bounded amount of baseline context in every session in every repository with
  the plugin installed, on top of D11's orientation. Bounded by printing one entry and by the
  hook's existing no-subprocess, size-capped contract. The tree check is a status read, not an
  analysis — the hook reports the discrepancy and leaves the judgment to the session.

### D9: `create_execution` becomes `create_tasks` — and it is a rewrite, not a rename

- **Decision**: the stage is renamed to `create_tasks`, matching the `create_*`-names-its-
  artifact convention (it writes `tasks.md`). The old name remains as a deprecated alias that
  announces the rename once and then runs the canonical skill, to be removed at the next
  major. The rename and the beads removal are executed as one change, because the file's beads
  choreography is what is being replaced by the markdown task table.
- **Rationale**: the rename alone is cosmetic; the same file holds the `bd create` / `bd dep
  add` block (`commands/create_execution.md:478-600`) and the frontmatter beads-ID block
  (`:596-615`) that D4 and D7 delete, plus the "tracked ONLY in beads" annotations that D4
  reverses. Doing them separately would mean editing the same regions twice. The alias
  follows upstream's proven precedent, whose one recorded gotcha — a session holding a stale
  cached skill body — is what its pointer files exist to absorb.
  *(Amended 2026-09-08: the stubs ship; the pointer files do not. See Resolved Decisions.)*
- **Trade-off**: an extra directory in the menu until removal.

### D10: `explore_design` is added as an optional stage

- **Decision**: an optional facilitated architecture stage sits between research and design:
  frame the decision space, diverge, discuss, converge only on explicit approval, and record
  the outcome as a `thoughts/` exploration document whose **top section is the decision
  record** — chosen direction, rationale, and rejected alternatives. It never writes
  `design.md`; `create_design` is what promotes the record into `## Technical Decisions`.
  *(Clarified 2026-09-08: this sentence originally read "plus a decision record in the design
  decisions log", which contradicted "never writes `design.md`" because the decisions log is
  `design.md`. Resolved in Resolved Decisions below; the behaviour is unchanged from what
  `P2-T4` shipped.)* `create_design` consumes a recorded decision at
  its cold start and formalizes it rather than regenerating options; with no record, its
  behavior is unchanged. The research stages suggest it only when findings show more than one
  viable approach.
- **Rationale**: the pipeline currently jumps from facts to a locked decision with no stage
  where alternatives are aired, so the reasoning behind an architecture choice survives only
  as design.md's Rejected Alternatives section — written by the same pass that chose. The
  conditional suggestion matters: upstream found and fixed a 0/3 false positive in exactly
  that nudge, so it fires on evidence, not by default.
- **Trade-off**: another optional stage to explain. Its decision record is also the natural
  consumer of D6's markdown records, so the two land together.

### D11: Drift hardening, with the freed hook slot

- **Decision**: adopt the compaction defenses, using the SessionStart slot that D4 vacates:
  - a single hook, registered on SessionStart for every trigger and on PreCompact, that
    prints a session orientation on a fresh start (the stage chain, the plan-directory
    convention, where status lives, that checkpoints stop for a human, the active plans in
    the repository) and compaction-recovery text on a compact trigger (that summarized
    document contents are paraphrase and the plan documents must be re-read before being
    asserted). It replaces `setup-beads-mode.sh`, which D4 makes dead.
  - a `doc-adherence` background skill whose rule is that a claim about what a plan document
    says requires a read of that document in the current context window.
  - handoff-over-compact guidance where the choice is actually made: a phase that would need
    a second compaction hands off instead.
- **Rationale**: hooks are the only mechanism that survives a compaction boundary
  deterministically; skill text does not. The orientation half becomes more valuable once
  beads is gone, not less: `bd prime` used to be what told a session where it was, and
  nothing else in an installed session names the stage order or where plans live. Our
  `CLAUDE.md` does, but it is not shipped.
- **Trade-off**: a few hundred tokens of baseline context in every session in every
  repository with the plugin installed. Bounded by keeping the orientation short and the hook
  free of subprocess calls.

### D12: Fable is an upshift, never a default

- **Decision**: Fable appears in no default path. Concretely:
  - `model-help` remains the single authority and gains explicit **upshift ladder** semantics:
    a named next-tier-up per phase, elected by the user or by the coordinator at a defined
    trigger, never entered automatically by a stage's baseline.
  - the decomposition stage recommends Opus at its self-check, with Fable named as the
    available upshift — not, as upstream has it, Fable recommended with Opus as the floor.
  - on a verified task failure the coordinator escalates **one rung from the tier that
    failed** and says which rung it chose and why; reaching the Fable rung is an explicit
    election, consistent with our standing "advise, never auto-switch" policy.
  - wherever Fable is used, effort is `high`, never `xhigh` or `max`.
- **Rationale**: the user's position is that Fable is a deliberate upshift, and our existing
  architecture already encodes exactly that discipline — `model-help` advises and never
  switches, and its roster names Fable as available rather than default
  (`skills/model-help/SKILL.md:22`). Adopting upstream's routing verbatim would contradict
  both. The `effort: high` cap is kept on its own evidence: at higher settings on long
  deliverables the model drafts in thinking and writes again, roughly doubling output for a
  patch-plus-report shaped task.
- **Trade-off**: we forgo the automatic quality ceiling upstream buys on its two Fable
  stages. Accepted deliberately; the ladder makes the upshift one step away rather than
  absent.

### D13: One statement of the worker tier rule

- **Decision**: the worker tier rule is stated once, in the coordinated execution skill at
  the point of spawn. The keyword-regex `determineModel()` function is retired in favor of
  coordinator judgment over the task's content, and every other restatement of the tiers
  becomes a pointer to the single statement.
- **Rationale**: our tree states the rule in prose (`commands/implement_coordinated.md:264-267`)
  *and* implements it as a regex (`:672-710`) whose fallthrough is the most expensive tier —
  so any task whose title does not match a hand-written pattern is charged at the ceiling.
  Upstream retired the same function for the same reason. A regex over task titles is a proxy
  for difficulty; the coordinator has the task body.
- **Trade-off**: judgment is less predictable than a regex. That is the point — and the
  verify-then-escalate loop is the safety net.

### D14: The failure path discriminates truncation from failure, and never retries the whole task

- **Decision**: on a worker that returns without completing, the coordinator first determines
  which of two distinct events occurred — **truncation** (the worker exhausted its tool-call
  budget; the finishing tail is missing) or **genuine failure** (the work is wrong) — by
  inspecting the working tree, and applies opposite remedies: finish or re-delegate the
  remaining slice for truncation, escalate one tier for failure. A task is never retried whole
  with the same context. A verified failure gets exactly one escalation attempt; if
  re-verification fails, the task goes to the phase checkpoint's blocking list for a human.
  Workers do not commit; the coordinator commits each task after its verifier passes, which
  is what makes an incomplete task detectable.
- **Rationale**: our current path treats every failure identically and retries twice with the
  same context (`commands/implement_coordinated.md:435-456`) — which upstream's measurement
  says truncates at the same point every time, spending two workers to learn nothing. The
  ~70-call ceiling was measured across 129 transcripts with context exhaustion ruled out, so
  budget, not difficulty, is the variable. Moving the commit to the coordinator is what turns
  "uncommitted work present" into a reliable truncation signal.
- **Trade-off**: one fewer automatic attempt before a human is involved. That is a feature —
  the second attempt was the one that reliably wasted a worker.

### D15: Tasks are sized by tool-call cost

- **Decision**: `create_tasks` sizes tasks by projected tool calls rather than wall-clock
  time, and splits a task projecting past roughly half the observed ceiling at a natural seam
  before it is ever spawned.
- **Rationale**: truncation is a function of call count, so the estimate that predicts it is
  the one the decomposition stage should carry. Sizing in hours predicts nothing about it.
- **Trade-off**: the number is empirical and machine-dependent, so it is stated as an
  observation with its provenance rather than a constant.

### D16: The lint gate reports findings in its exit code

- **Decision**: `scripts/lint` exits non-zero whenever markdownlint reported an error, in
  every mode including `--fix` when findings remain, and says so when issues could not be
  auto-fixed. The PostToolUse hook continues to exit zero so an edit is never blocked by a
  lint finding.
- **Rationale**: verified empirically — plain mode exits 1, `--fix` exits 0 with findings
  remaining, because the `exit 1` is nested inside the non-`--fix` branch
  (`scripts/lint:220-225`). A gate that reports success on failure is worse than no gate,
  because the release process cites it.
- **Trade-off**: any pre-existing backlog surfaces immediately. Our `.markdownlintrc` already
  disables the two rules that produced upstream's backlog, so this is expected to be small.

### D17: This is 2.0.0, with a changelog and a migration note

- **Decision**: the release is a major — 1.12.5 → 2.0.0 — carrying a changelog entry with a
  Breaking section and a Migration section. The migration tells an installer with existing
  plans that beads IDs in old plan frontmatter no longer resolve, that checkbox state is now
  authoritative, and that `--plugin-dir` must point at the subdirectory.
- **Rationale**: removed commands, a renamed stage, a relocated tree, and a removed tracking
  dependency are each individually breaking. Our repository currently has no changelog at
  all, so a major that changes the workflow contract with no written migration path would
  leave the user's own older plan directories silently broken.
- **Trade-off**: one more document to maintain. Scoped to a changelog only; a full release
  process document is out of scope.

### D18: The scaffolding root is rewritten and the thinking directives are converted

- **Decision**: rewrite `CLAUDE.md`'s "Working with Commands" list and its barrier example so
  each synchronization point is marked once with its reason stated, and so decision points
  name what the decision is about instead of instructing thinking depth. Convert the 25
  `think deeply` / `ultrathink` sites to the directive each one introduces, and delete the two
  bare ones. Leave barrier volume and scope-block volume untouched.
- **Rationale**: this is the one upstream trim that survived its evidence gate, and it rides
  the D2 migration at near-zero marginal cost since every one of those files is being reshaped
  anyway. The root list matters more than the sites: it is what regenerates the pattern in the
  next stage anyone writes, which is why upstream rewrote it *before* trimming. Thinking depth
  is a session effort setting now, not prompt text. The two trims upstream *rejected* — barrier
  volume and scope-block CAPS — are explicitly not in scope: its blind trials returned
  equal-or-worse on both, and our volume is already at parity with what it kept.
- **Trade-off**: touches every stage file. Since D2 touches them all regardless, the marginal
  risk is the wording change alone.
- **Approved 2026-09-08** (PD3). Proposed as a rider because it was not among the originally
  requested items; now in scope in full.

### D19: Obsolete rule-bearing documents are deleted, and where rules may live becomes a rule

- **Decision**: two parts.

  **Delete** the documents whose subject this plan removes, rather than annotating them as
  historical: `docs/beads-fast-fail.md`, `docs/beads-stealth-mode.md`,
  `docs/beads-integration-learnings.md`, and root `AGENTS.md`. `CLAUDE.md` becomes the single
  root for session protocol, absorbing anything in `AGENTS.md` worth keeping.

  **Then state the rule that keeps it from recurring**: a shipped skill may link only into
  `plugin/docs/reference/`; everything under `docs/` is maintainer-facing and is never a
  runtime rules source; and anything we deliberately keep as history is marked non-normative
  at its top rather than left to read as current guidance.

- **Rationale**: these files do not merely describe a removed subsystem, they *instruct* — and
  a stale instruction is worse than a stale description, because it reads as authority. Three
  specifics:

  `AGENTS.md` is the sharpest case. It is 42 lines of which every operative one is beads
  (`bd onboard`, `bd ready`, `bd update --status in_progress`, `bd sync`), it duplicates
  `CLAUDE.md`'s session protocol, and its "Landing the Plane" block issues absolute
  directives ("Work is NOT complete until `git push` succeeds", "NEVER stop before pushing").
  It is also a **conventionally auto-loaded filename** — agent harnesses read `AGENTS.md` the
  way Claude Code reads `CLAUDE.md` — so it can enter a session's context with nothing
  pointing at it. Upstream removed its own copy on 2026-09-05 for the same reason: it
  "duplicated CLAUDE.md's session protocol with a stale pre-1.0.2 step."

  `docs/beads-integration-learnings.md` is already **orphaned** — the only reference to it in
  our tree is inside itself (`:195`) — which is precisely why annotation would not protect
  us. Nothing links to it, so nothing warns a session before a grep surfaces
  `:233` "Always use TodoWrite" against `commands/implement_tasks.md:684`'s "NEVER use …
  TodoWrite", or `:74` "Markdown checkboxes work well for within-phase tracking" against a
  prohibition this plan is only now reversing. It is also 252 lines about a subsystem that
  will not exist.

  The two `beads-*` doctrine docs carry fifteen inbound links between them from seven command
  files; all of those links disappear under D4 regardless, so keeping the targets would leave
  two unreferenced rule sources behind.

  Upstream's choice to keep its learnings document as dated history was right *for upstream* —
  it still has beads, so the history has a current subject and a maintainer guide to hang it
  from. Neither condition holds here.

  The second half matters more than the deletions. Removing four files is a one-time fix;
  stating where rules may live is what stops the fifth. D1 already draws the shipped/maintainer
  boundary, so this decision only names the consequence that boundary implies.

- **Trade-off**: we lose the migration narrative in `beads-integration-learnings.md` — the
  SQLite-to-Dolt pain, the five-week-stale export discovery. Accepted: git preserves the file,
  research.md records what it contained at `b902566`, and its one durable lesson (a merged
  journal-and-rules file decays into stale authority) is now load-bearing rationale in D8
  rather than a line in a document nobody links to.
- **Pattern reference**: `docs/beads-integration-learnings.md:74,233` (the contradictions);
  `AGENTS.md:1-42`; `CLAUDE.md:241` and `docs/workbench-workflow-guide.md:893` (the two
  inbound `AGENTS.md` references to repoint).

### D20: The two implementation guardrails that guard against the failure modes of every strong model

- **Decision**: add upstream's two Fable Phase-1 implementation guardrails, in the shape it
  ships them:
  - a **surgical-edit** rule — when it will not affect the end result, edit a file in place
    rather than rewriting it;
  - a **follow-ups, not fixes** rule — a pre-existing bug, a performance concern, or behavior
    the task does not mention is *reported*, not fixed, unless the requested behavior cannot
    work without it — closing with the completeness clause: this is about extras only,
    implement every behavior the task asks for, completely.

  They live beside the existing scope block, as a `### Extras and edits` section, and in
  `agents/task-worker.md`'s constraints, from which the coordinated path inherits them.

- **Rationale**: research.md §5 found all seven of upstream's Phase-1 guardrails absent from
  our tree. This plan adopted two of them for other reasons — the memory surface became D8,
  and the `task-worker` agent became a Phase 2 task — leaving these two unadopted for no
  stated reason. That gap matters more than it looks:
  - The scope block we have is a **dead end**: five `NEVER` bullets ending in "STOP and ask"
    (`commands/implement_tasks.md:50-58`), immediately followed by the TDD flow. It says what
    not to *add* and says nothing about what to do when a worker *discovers* something. So the
    common case — a worker finds a real bug in the function it is editing — has no rule at all.
  - It is also the only place our tree lacks a **completeness counter-clause**. A prohibition
    list without one invites the opposite failure, under-delivery, which
    `agents/task-verifier.md` checks for but no instruction guards against.
  - The failure modes these guard against are documented for the current model generation
    ("rewrites whole files where a targeted edit would do", "fixes nearby code, writes extra
    tests"), and they are not Fable-specific — they are the shape strong models fail in on
    long multi-file runs. This plan is a 60-task multi-file run.
- **Trade-off**: the follow-ups rule could suppress a fix that was genuinely required. The
  completeness clause and the "unless the requested behavior cannot work without it" escape
  are what bound it, and `task-verifier` already checks scope adherence in both directions.
- **Not a Fable concession**: this is worth doing at any tier, which is why it is a decision
  rather than a condition on D12's upshift ladder.
- **Pattern reference**: `.context/upstream/plugin/agents/task-worker.md:30-31`;
  `.context/upstream/plugin/skills/implement_inline/SKILL.md:62-66`.

### D21: Plans are transient by default and promoted into git on a trigger

- **Decision**: `docs/plans/` stays gitignored, so every plan directory starts local to the
  worktree that created it. A plan is promoted into git (`git add -f docs/plans/<dir>/`) when
  **either** trigger fires: the work needs to cross a session or a machine, or the branch is
  about to merge. Anything that must survive a branch being *abandoned* goes in
  `.claude/wb/knowledge.md` (D8b) instead of being preserved as a plan directory.
- **Rationale**: whether a plan deserves permanence is usually only knowable at the end, when
  the branch either lands or is discarded, so any scheme that classifies at creation will
  classify wrongly. Both triggers sit at moments when the answer *is* known, and neither
  requires foresight. The first is forced by physics rather than preference — a plan that is
  not in git cannot travel to another machine, and the branch push is the transport. The second
  follows from D4: if git is the durable record of how the code got this way, a plan whose work
  landed is part of that record, and a plan whose work did not is not.
  The load-bearing half is D8b. Its qualification rule — an entry qualifies only if it would
  change how the *next* session works — is already the definition of "permanent", and the file
  is already committed and repo-scoped. That is what makes transient-by-default safe: an
  abandoned branch still leaves behind what it taught, so hygiene is decoupled from
  durability. **You do not have to keep a plan to keep what it taught you.**
- **No new machinery**: `tasks.md` frontmatter already carries `status:`, so "complete" is
  already expressible, and force-add is one-way — once a path is tracked, `.gitignore` stops
  applying to it — so promotion is a single command with no ongoing bookkeeping.
- **Trade-off**: a plan abandoned *mid-flight* on one machine after being promoted stays in
  history as an unfinished record, and a plan not yet promoted is invisible to every other
  machine. Accepted: the first is cheap noise with a `status:` field to explain it, and the
  second is the definition of transient rather than a defect.
- **Where it is written**: `project-structure` (already D4's doctrine home, opened by `P2-T24`)
  and `create_handoff` (the cross-machine trigger is its business, opened by `P2-T18`). Folded
  into those two tasks rather than added as a new one.
- **Decided 2026-09-08** via `/wb:resolve_questions`, on the user's question about managing
  transient versus permanent plans. This plan itself was force-added on the same date: both
  triggers fire for it.

### Resolved Decisions

Decisions made after the design was approved, recorded here by `/wb:resolve_questions`.

- **The coordinated worker default tier is Opus 4.8 (1M), with Opus 5 as the first upshift
  rung** (resolves PD2, and D13's open default). The default is the **1M-context variant** —
  model ID `claude-opus-4-8[1m]`, following the harness's `[1m]` suffix convention — not the
  base `claude-opus-4-8`. The full ladder becomes: haiku for mechanical work only ·
  **Opus 4.8 1M default** · Opus 5 on coordinator judgment for architectural or cross-cutting
  tasks · Fable only as an explicit election after a verified failure (D12).
  - **Consequence for `model-help`**: its roster (`skills/model-help/SKILL.md:22`) currently
    names four models with **no 1M variants**, so as written the authority would not contain
    the model the ladder names. `P2-T17` must add the 1M variants to the roster and state
    which tier's 1M form is the default, or the ladder and the roster disagree.
  - Rationale: keeps Opus-class reasoning on worker tasks while taking the cheaper of the two
    Opus tiers, which is exactly what `model-help:24` already prescribes ("Opus 4.8 is the
    default Opus… Downshift 5 → 4.8 whenever 5 would be overkill"). It also preserves D12's
    ladder shape — every rung above the default is entered by election, not by baseline.
  - On the 1M choice specifically: it buys headroom for cross-cutting tasks rather than fixing
    a known failure. Worth stating plainly so nobody later mistakes it for a truncation fix —
    D14/D15 established that workers hit a **tool-call** ceiling, not a context limit
    (upstream measured a truncated worker holding only 92K tokens), so the wider window does
    not change truncation behaviour.
  - Trade-off: costlier per task than upstream's Sonnet default, so we decline the cost win
    upstream took in July. Accepted: the regex being retired (D13) had opus as its
    *fallthrough*, so this is not a cost regression against today's behaviour — it is the same
    tier one step cheaper.
  - Note: this is the one place our tiering deliberately diverges from upstream, and the
    reason is our two-Opus roster, which upstream does not have.
  - Source: design.md PD2 · research.md Open Questions · Decided 2026-09-08

- **D18 ships in this release, in full** (resolves PD3). `P1-T6` rewrites the `CLAUDE.md`
  "Working with Commands" list and its barrier example at the start of Phase 1; the 25
  `think deeply` / `ultrathink` sites convert during Phase 2's per-file pass, and the two bare
  ones are deleted.
  - Rationale: it is the only one of upstream's three deferred trims that passed its
    blind-trial gate, and it rides the D2 reshape at near-zero marginal cost since every
    affected file is being restructured anyway. Sequencing the root first is upstream's own
    reasoning — the list is what regenerates the pattern in the next stage anyone writes, so
    trimming sites while the root still mandates them guarantees regression.
  - Trade-off: touches every stage file, but D2 touches them all regardless, so the marginal
    risk is the wording change alone and revert is one commit.
  - Explicitly still out of scope: barrier volume and scope-block CAPS. Upstream's trials
    returned equal-or-worse on both, and our volume is already at parity with what it kept.
  - Source: design.md PD3 · Decided 2026-09-08

- **All three renames ship in this release** (resolves PD4, and widens D9).
  `implement_coordinated` → **`implement`** and `implement_tasks` → **`implement_inline`**
  join `create_execution` → `create_tasks`. Each old name remains a deprecated alias in the
  same shape — a stub that announces the rename once then runs the canonical skill, plus one
  pointer file per supporting file — removed at the next major.
  - Rationale: 2.0.0 is already a breaking release and the alias mechanism is already being
    built for `create_execution`, so the marginal cost of two more is one task. Doing them
    separately would mean a second major with a second migration note for a change whose
    reasoning is already settled: the recommended execution path should carry the plain verb
    rather than reading as the special case, and `implement_inline` names what is actually
    different about the other path (it runs inline, on the session model).
  - Trade-off: the `/wb:` menu carries three deprecated aliases until the next major instead
    of one, and `implement` becomes the most generic trigger word in the menu — its
    description has to carry the discrimination ("worker agents, main context kept clean"
    versus "inline on the current session model"). This reverses the reasoning that deferred
    it, which was alias-surface cost; the user's call is that one migration beats two.
  - Sequencing: the renames execute inside Phase 2's per-file pass, not as a separate sweep —
    same reasoning as D9, since the files are being reshaped and de-beaded in that pass
    anyway and a rename is a directory move plus a frontmatter `name:` change.
  - Source: design.md PD4 · Decided 2026-09-08

- **The migration note is written for a single operator across multiple machines** (resolves
  A1). No other people or repositories install `wb`, but the user has it installed on other
  machines and workspaces that hold existing plan directories, so 2.0.0's Migration section is
  written per-machine rather than per-person: update the plugin and restart on each machine;
  point `--plugin-dir` at `plugin/`; and expect existing plan directories' beads IDs to stop
  resolving, with checkbox state becoming authoritative.
  - Rationale: the blast radius is real but bounded — one operator means no coordination
    problem and no deprecation window to negotiate, but multiple installs means the note
    cannot assume the reader is in this repository looking at this plan.
  - Trade-off: none. A briefer note would have been wrong for the second and third machine.
  - Source: design.md A1 · Decided 2026-09-08

- **A phase-exit criterion tests what that phase owns; the tree-wide assertion belongs at the
  cut** (resolves Phase 2's unmeetable beads criterion). Phase 2's
  `grep … plugin/ → no hits` is scoped to exclude three files with named later owners —
  `commands/help.md` (`P4-T2`), `hooks/setup-beads-mode.sh` (`P3-T4`), `commands/forge.md`
  (`P4-T1`) — and Phase 4's existing whole-tree criterion is left untouched as the real gate.
  - Rationale: as written, Phase 2 could execute perfectly and still fail its own headline
    check, because 43 of the 78 hits at the time of the decision were in files it is not
    allowed to touch. A criterion that cannot pass teaches the reader to discount it, and this
    one guards D4 — the phase's whole point.
  - Why not pull the files forward instead: `P4-T1` and `P4-T2` are ordered last deliberately,
    because `forge` and `help` describe the pipeline's final shape and that shape is not final
    until Phase 3 adds `explore_design`. `P3-T4` is worse to split — it deletes the hook *and*
    registers `wb-prime.sh` in the same manifest slot, so taking only the deletion leaves
    `plugin.json` pointing at a hook that no longer exists.
  - Why the assertion is not weakened: the identical whole-tree check already exists as a
    Phase 4 criterion, covering `plugin/`, `README.md`, `CLAUDE.md` and `docs/`. Nothing is
    dropped; the check simply runs where every owner has had its turn.
  - Trade-off: the exclusion list is a hardcoded set of three paths, so it rots if a file is
    renamed. Bounded by naming the owning task beside each path — a reader who finds the
    exclusion stale can see immediately which task should have removed it.
  - **Generalizes**: this is the third criterion in this plan written against a scope wider than
    its phase (after Phase 1's `AGENTS.md` grep and the two tier-rule rewordings). The pattern
    is worth stating — **write a phase's exit check against the phase's own Modified Files
    list**, and keep tree-wide assertions for the release phase.
  - Source: tasks.md Phase 2 Automated Verification · Decided 2026-09-08

- **A2 is validated, and the one finding worth carrying is that checkbox counting must be
  ID-scoped** (resolves A2). Checkbox-plus-counter status held at this plan's scale — 64 tasks,
  five phases, 30 tracked live, position recoverable at every boundary and every commit citing
  a task ID.
  - Rationale: A2 is the assumption D4 rests on, and it was recorded as proven only in the
    sibling workflow. This plan is now the larger test case, so the evidence exists rather than
    being deferred indefinitely.
  - The predicted strain was real but bounded. Task identity is positional, and that cost:
    an edit whose text match broke when a completion stamp shifted the line; a `total_tasks`
    bump that an ID-keyed count would not have needed; and — the one that would have silently
    corrupted every counter — a naïve `grep -c '^- \[x\]'` reading **38** against 30 real
    tasks, because a plan's own success criteria and prerequisites are checkboxes too.
  - **Consequence already shipped**: `update_status` and `validate_project` both scope their
    counts to lines carrying a task ID, and both say why. A future reader reaching for the
    obvious grep gets the wrong number by exactly the count of criteria in the file, which on a
    criteria-heavy plan is a ~25% over-count.
  - Trade-off: none new. The mitigation is a stricter grep, not more machinery. If plans ever
    reach several hundred tasks, an ID-keyed index is the escalation — but nothing in this
    run pointed at needing one.
  - Source: design.md A2 · evidenced by this plan's own execution · Decided 2026-09-08

- **The worker tier rule stays a table; Phase 2's criterion is reworded to match it**
  (resolves the criterion/implementation mismatch `P2-T15` surfaced). The check becomes
  `grep -rln 'claude-opus-4-8[1m]' plugin/skills/` → exactly one file.
  - Rationale: the old criterion, `grep -rln "Haiku:.*Sonnet:.*Opus:" plugin/`, was written
    against the one-line prose shape D13 was *replacing*. PD2's ladder has four rungs, and two
    carry conditions that prose had nowhere to put — "never annotate `effort` on a haiku spawn"
    and "Fable only after a verified failure, always at `effort: high`". A table states them
    once and legibly; rewriting it back to prose to satisfy a grep would be the tail wagging the
    dog, and would have to name Sonnet, which is not in our ladder at all.
  - Rejected: keeping both forms. A prose summary beside the table is a *second* statement of
    the tier rule in the same file — precisely what D13 exists to prevent, and the two would
    drift.
  - **Corrected the same day, and the correction is the more useful record.** The model-ID form
    broke within the hour: `P2-T17` added the 1M variants to `model-help`'s roster, exactly as
    PD2's consequence note had said it would, so `claude-opus-4-8[1m]` appeared in two files.
    A criterion keyed to a *value* named in two places was never going to hold. The check is now
    keyed to a **self-describing marker of the invariant** — the sentence in `implement`'s Step 5
    declaring itself the single statement — so it survives model renames, roster additions and
    reformatting. General lesson worth keeping: verify a criterion against a value the plan
    already predicts will recur, before adopting it.
  - Source: tasks.md Phase 2 Automated Verification · surfaced by `P2-T15` · Decided 2026-09-08

- **The renames' dangling callers are repointed in one sweep at the end of Phase 2, as new
  task `P2-T30`** (closes the gap `P2-T6` raised). Every already-reshaped skill that names
  `create_execution`, `implement_tasks` or `implement_coordinated` is repointed once, after all
  three canonical names exist.
  - Rationale: the timing is the whole decision. Fixing `create_execution`'s seven callers when
    that rename landed would mean editing `create_project` and `create_design` a second time,
    then a third when `implement_tasks` → `implement_inline` lands — those same files reference
    both. One sweep after all three renames exist touches each file exactly once, which is what
    the edit-once rule is actually protecting.
  - Why Phase 2 and not Phase 4: the breakage is created here, and Phase 2's own exit greps can
    verify the fix. Deferring it would carry eleven references to deprecated commands through
    two human checkpoints, where a reader would reasonably read them as current.
  - Scope: eleven references at the time of the decision — `create_project` (×8),
    `create_design` (×2), `create_tasks` (×1). `model-help`'s three are excluded; `P2-T17`
    owns them. The list stops growing because the nine stages still to be reshaped will be
    written with the new names directly.
  - Trade-off: for the rest of Phase 2 the tree contains references to deprecated names. They
    resolve through the stubs, so nothing is broken — but anyone reading a generated template in
    that window sees the old name. Accepted as the cheaper of two imperfect windows.
  - Source: tasks.md Current Blockers (raised by `P2-T6`) · Decided 2026-09-08

- **The three renames ship as stub skills only — no pointer files** (amends D9, narrows
  `P2-T8` and `P2-T29`). Each deprecated name keeps a `SKILL.md` that announces the rename once
  and reads the canonical skill. The per-supporting-file pointer stubs are dropped, and the four
  already written for `create_execution` are deleted.
  - Rationale: A1's resolution removed most of D9's basis. A deprecation window exists to give
    *other people* time to migrate, and A1 established there are none — one operator, a few
    machines. What survives is narrower and real: muscle memory, and the fact that plan
    directories already written on other machines have `/create_execution` and
    `/implement_tasks` baked into their generated Quick Commands blocks. Those documents cannot
    be retroactively updated, so a stub turns a dead command into a one-line redirect. That is
    worth keeping.
  - Why the pointer files are not: they guard exactly one case — a session already running when
    the plugin updates, still holding the *old* skill body, whose relative reads then miss.
    A stale body never routes through the stub, so stubs and pointers cover different failures.
    That one is transient and self-healing, and its remedy (restart the session) is already the
    first line of the migration note.
  - Cost, stated precisely: dropping the pointers saves **no tokens** — only `SKILL.md` loads at
    invocation. It removes ~10 files, a directory's worth of clutter per alias, and a removal
    chore at 3.0.0. The stubs themselves cost ~320 on-invoke and ~30 always-on each, so ~1k and
    ~90 for three; that surcharge is accepted and is not captured by the fourteen-stage metric.
  - Trade-off: a session that updates mid-flight and then invokes a stale supporting-file path
    gets a read error instead of a redirect. Accepted — it is one session, the message is
    legible, and restarting is already prescribed.
  - Note on PD4: it is sometimes read as an argument *for* aliases; it is not. It argues that if
    the mechanism is being built anyway, all three renames should ride it at once rather than
    splitting into two migrations. That reasoning is untouched by this amendment.
  - Source: user question, 2026-09-08 · amends D9 · Decided 2026-09-08

- **A multi-line message block a skill emits verbatim is a template, and lives in
  `templates.md`** (resolves the message-template question, and sets the convention for the
  nine stages still to be reshaped). `create_design`'s three blocks — the Mode A
  recorded-decision confirmation, the Mode B design-options message, and the Step 6
  presentation — moved to named sections, each read by section at the point of use.
  - Rationale: `P2-T14`'s own spec already treats exactly this content as `templates.md`
    material ("the message and fragment set … the success summary, and the three Error
    Handling message templates"), so leaving `create_design`'s inline would have shipped two
    stages treating the same kind of block differently. The value is the rule, not the tokens:
    nine stages remain, and one stated convention beats nine case-by-case judgment calls.
  - Bound: this applies to multi-line blocks the skill emits **verbatim**. A three-line report
    shape inline with the discipline that fires it — `create_design`'s tracer-bullet cull
    report, for instance — stays put; moving it would cost more in indirection than it saves.
  - Measured: `create_design` 4.5k → **4.1k** (−29.3% against its 5.8k baseline), and the
    running fourteen-stage tally improves from −34.3% to **−36.1%**.
  - Trade-off: one more read mid-conversation, which A4 confirmed is prompt-free; and a
    second re-edit of a committed file, accepted for the same reason as the `P2-T1` amendment
    — the alternative is discovering the inconsistency at the Phase 2 checkpoint.
  - Related fragility, worth stating once: a `templates.md` section holding a fenced document
    skeleton contains `##` headings of its own, so a section-scoped read must respect fence
    boundaries rather than stopping at the next `##`. Mitigated by listing the real section
    names in each `templates.md` header.
  - Source: tasks.md Implementation Notes (design-cluster boundary) · Decided 2026-09-08

- **`explore_design`'s decision record lives at the top of its `thoughts/` exploration
  document, and nowhere else** (resolves D10's internal contradiction). `create_design` scans
  `[project-dir]/thoughts/` for an exploration document carrying a decision-record section,
  reads it fully, and formalizes it into `design.md`'s `## Technical Decisions`.
  `explore_design` never writes `design.md`.
  - Rationale: D10 as written said both "a decision record in the design decisions log" and
    "never writes `design.md`" — and the decisions log *is* `design.md`, so the two clauses
    could not both hold. This reading keeps the second clause literal, needs no new artifact,
    and puts the decision where a reader of the exploration is already looking. It also keeps
    the stage boundary intact: `design.md` has exactly one writer, `create_design`.
  - Why it needed deciding now rather than at `P3-T10`: `P2-T4` shipped `create_design`'s
    cold-start check today and had to consume *something*. A producing stage and a consuming
    stage that disagree about the location do not fail loudly — the consumer finds nothing,
    silently takes its no-record path, and the whole feature never fires.
  - Trade-off: the decision is not in the decisions log until `create_design` runs, so a plan
    that explores and then stalls has its decision recorded only in `thoughts/`. Accepted: the
    thoughts document is committed like everything else, and D8's continuity artifacts cover
    the interrupted case.
  - Source: design.md D10 · surfaced writing `P2-T4` · Decided 2026-09-08

- **A skill's supporting file is read by named section, not whole, when it holds several
  independent blocks** (resolves the `create_project` templates question). `create_project`
  keeps **one** `templates.md` holding all four artifact skeletons under named headings, and
  each of Step 4's four creation sub-steps directs a read of *its* section by name.
  - Rationale: no skeleton is an outlier — README 51 lines, research 75, design 82, tasks 81,
    289 total — so none earns its own file on size. Upstream ships the identical shape at
    nearly the identical size (one `templates.md` at 321 lines) and points at named sections
    per step, so this is a proven layout rather than a guess. Four separate files would add
    four supporting-file links to keep in sync for no measured gain.
  - The section-scoped read is the load-bearing half. A single whole-file pointer would pull
    all ~300 lines of skeletons in to write one document, and again on every re-read after a
    context loss. Naming the section is what makes progressive disclosure actually progressive
    inside a supporting file, not just between them.
  - Generalizes beyond this stage: any supporting file holding several independent blocks gets
    named sections and section-scoped reads. `create_mockup`'s ~300-line templates (`P2-T20`)
    and `create_tasks`' supporting set (`P2-T7`) are the other candidates.
  - Trade-off: a section-scoped read depends on the section heading staying stable, so renaming
    a heading in a supporting file silently breaks the pointer that names it. Cheap to catch —
    the headings are in the same repository as the pointers — and the alternative costs tokens
    on every read.
  - Source: tasks.md Implementation Discoveries · Decided 2026-09-08

- **`## Important Notes` is tail reference material and moves to `reference.md` in every stage
  that has one — `P2-T1` amended to match** (closes the reference-scope question the research
  cluster raised). `create_research`'s Important Notes now sits in its `reference.md` with a
  pointer left in `SKILL.md`, exactly as `P2-T2` does it.
  - Rationale: the phase recipe's own step 4 already says to move tail reference material and
    names `## Important Guidelines`; `## Important Notes` is the same kind of section under a
    different name. A survey of all 29 Phase 2 tasks found every other stage carrying such a
    section already names it in that task's reference scope — `create_research` was the single
    omission. So this is applying the stated recipe, not amending it, and "fix this stage" and
    "make it a phase-wide rule" are the same act because there is nothing else to fix.
  - Evidence it mattered: `create_research` measured **−22.6%** on-invoke tokens against the
    −30% bar while `create_product_research` — same recipe, same cluster, Important Notes moved
    — measured **−38.5%**. After the move: **~5.3k → ~3.7k = −30.2%**, and the cluster goes
    from −31.4% to **−34.7%**.
  - Trade-off: it re-opens a file one commit after the plan's edit-once rule closed it. Accepted
    because the alternative is re-opening it at the Phase 2 checkpoint instead, which is what
    that rule exists to prevent — and the cost of deciding now is one small follow-up commit.
  - Source: tasks.md Implementation Notes (research-cluster measurement) · Decided 2026-09-08

- **Plan directories are transient by default and promoted on a trigger** — recorded as a
  full decision at **D21** above, because it is a convention the shipped skills carry rather
  than a one-off resolution. Source: the user's transient-versus-permanent question ·
  Decided 2026-09-08.

- **Commit cadence is one commit per task, except in Phase 2, where it is one commit per
  cluster** (refines D14's "one task, one commit"). Phases 0, 1, 3 and 4 commit per task ID,
  with the ID leading the commit message. Phase 2's eight clusters — research, design,
  execution-planning, implementation, validation-and-status, execution-path decisions, handoff,
  and remaining stages — commit once each.
  - Rationale: Phase 2 is 28 tasks that each move a file's prose between four new files, so
    per-task commits there produce a log of 28 near-identical "reshape one stage" entries while
    the reviewable unit is the cluster. Everywhere else a task is a distinct change and the
    per-task commit is the audit trail D4 relies on to replace the tracker.
  - Trade-off: inside a Phase 2 cluster, D8c's "uncommitted work in the tree means a task did
    not finish" signal degrades from task granularity to cluster granularity — an interrupted
    session mid-cluster leaves several finished tasks uncommitted alongside the unfinished one.
    Accepted because checkbox state stays per-task and current regardless, so the journal entry
    plus the checkboxes still localize the interruption; git is losing resolution, not the
    answer.
  - Consequence for `P2-T*`: the recipe's step 8 ("commit. One task, one commit") is amended in
    place, and the per-file lint gate still runs per task — only the commit is batched.
  - Source: tasks.md Phase 2 recipe step 8 · design.md D14 · Decided 2026-09-08

- **`lint --all` excludes `.context/`, and that is an authorized scope addition to Phase 0**
  (resolves the plan defect `P0-T4` surfaced). One line — `-not -path "./.context/*"` — joins
  the existing exclusion list in `scripts/lint`, and Phase 0 gains task `P0-T6` to carry it.
  - Rationale: D16's whole premise is that a gate which misreports is worse than no gate, and
    that cuts both ways. `--all` returns 84 findings, **all** of them inside the gitignored
    `.context/upstream/` export and **none** in anything we author, so the four phase criteria
    that assert "clean" would sit red from Phase 1 through Phase 4 — long enough to train the
    reader to ignore them, which is exactly where a real regression hides. `.context/` is also
    the same category as entries the list already names (`vendor/`, `node_modules/`): vendored,
    read-only, not ours.
  - Trade-off: it fixes the instance, not the class — `--all` still does not consult
    `.gitignore`, so a future vendored directory reintroduces the same noise until it is named
    too. Accepted deliberately over the general fix, because rebuilding the list from
    `git ls-files` would silently drop `docs/plans/` — gitignored in this repository — and with
    it every plan document this workflow produces, trading a cosmetic problem for real lost
    coverage.
  - Scope note: no pre-existing task authorized touching `--all`'s file list, so this is
    recorded as a decision with its own task ID rather than folded into `P0-T4`.
  - Source: tasks.md Current Blockers (raised by `P0-T4`) · Decided 2026-09-08

- **A4 and A5 are validated, and the shipped-reference-directory convention has evidence behind
  it** (resolves both assumptions). `allowed-tools: Read` suppresses the permission prompt for
  on-demand supporting files in **both** shapes the design relies on — a sibling file inside the
  skill directory, and a file reached by climbing out of it into `plugin/docs/reference/`. The
  deprecated-alias stub shape works: it announces the rename once, then reads and follows the
  canonical skill.
  - Rationale: the Phase 0 layout probe (`P0-T1`/`P0-T3`) was built to exercise exactly these two
    read shapes and the alias stub, and the human smoke session reported no prompt on either read
    plus a single rename announcement. The cross-directory half was the one design.md flagged as
    uncertain, and it is the half D19's "a shipped skill may link only into
    `plugin/docs/reference/`" rule depends on — that rule now rests on a measurement rather than
    on upstream's report.
  - Consequence: `P1-T3` (create `plugin/docs/reference/`) and the three alias stubs (`P2-T8`,
    `P2-T29`) proceed as designed, with no fallback needed. The `--plugin-dir` smoke session at the
    Phase 2 and Phase 4 checkpoints is now a regression check rather than a first proof.
  - Trade-off: none. The one residual gap is narrow — alias *invocation* was observed under
    `--plugin-dir` rather than under a marketplace install, so the Phase 4 checkpoint's
    marketplace-install alias check stays worth running.
  - Source: design.md A4, A5 · tasks.md Phase 0 Manual Verification · Decided 2026-09-08

## Scope Definition

### In Scope

- D1–D2: the `plugin/` relocation and the skills/progressive-disclosure migration, including
  `allowed-tools` and `user-invocable` frontmatter and a shipped reference directory
- D3: sub-agent frontmatter tiers and turn caps; the `model-help` boundary statement
- D4–D7: beads removal and the markdown status surface, sole-writer reconciliation, markdown
  planning records, and document-order execution
- D8: cross-session continuity — the per-plan session journal, the committed repository
  knowledge file with its qualification and verification rules, and the session-start
  bootstrap that delivers both
- D9 + PD4: all three renames — `create_execution` → `create_tasks`,
  `implement_coordinated` → `implement`, `implement_tasks` → `implement_inline` — each with a
  deprecated alias, executed together with the beads removal in those files
- D10: `explore_design`
- D11: the orientation/recovery hook, `doc-adherence`, and handoff-over-compact guidance
- D12: Fable as an upshift-only tier and the `model-help` upshift ladder
- D13–D15: one tier-rule statement, the truncation/failure split, one escalation, coordinator
  commits, and tool-call-based task sizing
- D16: the lint exit code
- D17: the 2.0.0 cut, changelog, and migration note
- Rewriting the surfaces that beads removal and the rename invalidate: the workflow guide, the
  commands reference, `help`, `forge`'s state detection and barriers, `AGENTS.md`, `README.md`,
  and `CLAUDE.md`'s tracking principles
- Reversing the instructions that make the existing markdown surface inert — among them
  `commands/create_execution.md:284,648,702`, `commands/implement_tasks.md:315-317,684-686`,
  `commands/update_status.md:110,371,403`, `commands/validate_execution.md:63,203,379`,
  `commands/resume_handoff.md:248`, `commands/create_project.md:343`, and `CLAUDE.md:124` —
  and resolving the contradictions they already produce with
  `docs/commands-reference.md:408` ("Update task checkboxes as you complete work") and
  `docs/beads-integration-learnings.md:74,86,208,233` (which says checkboxes work well and to
  "Always use TodoWrite", against `implement_tasks.md:684`'s "NEVER use … TodoWrite"). The
  removal resolves a live inconsistency rather than only subtracting.
- D19: deleting `docs/beads-fast-fail.md`, `docs/beads-stealth-mode.md`,
  `docs/beads-integration-learnings.md`, and root `AGENTS.md`; folding anything worth keeping
  from `AGENTS.md` into `CLAUDE.md`; repointing its two inbound references
  (`CLAUDE.md:241`, `docs/workbench-workflow-guide.md:893`); and stating the
  where-rules-may-live rule that D1's shipped/maintainer boundary implies
- D20: the surgical-edit and follow-ups-not-fixes guardrails, with the completeness clause,
  beside the existing scope block and in the `task-worker` agent's constraints
- D18 in full (PD3 approved 2026-09-08)
- D21: the transient-by-default plan-persistence convention and its two promotion triggers,
  written into `project-structure` and `create_handoff` (added 2026-09-08)

### Out of Scope

- Upstream's plan **Intent** section and its per-stage obligations, and the full
  human-input map. `help` is rewritten only as far as beads removal forces.
- A release-process document beyond the changelog.
- Building or merging the `knowledge-store` subsystem from
  `origin/thescubageek/knowledge-store-v1` (4,770 lines: two hooks, nine scripts with test
  harnesses, a curation proposal linter, git-based invalidation sweeps, three-state PreToolUse
  enforcement). D8 solves the stated bootstrap problem with two markdown files and hook
  wiring; that branch solves a larger problem — automatic capture with enforcement and
  programmatic invalidation — which is worth revisiting only if manual curation proves
  insufficient in practice. Recorded so the prior work is not lost.
- Every upstream decision whose subject is beads: the persistence tiers, stealth setup rule,
  session-start sanity check, version floor, hygiene command wiring, and the maintainer
  contract inventory. All moot under D4.
- Barrier-volume and scope-block-volume trims — rejected upstream on evidence.
- Retrofitting existing plan directories under `docs/plans/`; the migration note covers them.

## Success Criteria

### Functional Requirements

- [ ] The full pipeline runs end to end in a repository with no tracker installed, with no
      stop-and-prompt gate
- [ ] `tasks.md` alone answers "what is done, what phase are we in, what is next"
- [ ] Exactly one command writes the progress frontmatter fields; `status-sync` reports drift
      between counters and checkbox counts
- [ ] `create_tasks`, `implement`, and `implement_inline` exist; `create_execution`,
      `implement_coordinated`, and `implement_tasks` each print a deprecation notice once and
      then behave identically to their canonical skill
- [ ] `explore_design` produces a `thoughts/` record plus a decision-log entry, and
      `create_design` formalizes a recorded decision instead of regenerating options
- [ ] A compacted session's first context contains the re-read instruction and names the
      active plan directory
- [ ] Killing a session mid-task without any shutdown step leaves an open journal entry naming
      the attempted work and next action; the next session's first context reports it as
      interrupted and names the uncommitted changes
- [ ] Every knowledge entry carries a date, its source plan, and a verification hint; the
      qualification rule is stated where entries are written
- [ ] A verified failure produces one escalation at a named tier, then the checkpoint's
      blocking list; an incomplete worker is diagnosed as truncation or failure before any
      remedy
- [ ] No default path selects Fable; the upshift ladder names it as an election
- [ ] Both implementation paths carry the surgical-edit and follow-ups-not-fixes rules with
      the completeness clause; the scope block is no longer a dead end
- [ ] `./scripts/lint --fix` exits non-zero with findings remaining
- [ ] Both manifests read 2.0.0 and the changelog has Breaking and Migration sections

### Non-Functional Requirements

- [ ] Invocation-time context across the workflow stages is at least 30% below v1.12.5, with
      no stage's content removed
- [ ] The shipped tree contains no `bd`, `beads`, or `BEADS_MODE` reference outside the
      migration note
- [ ] The orientation hook makes no subprocess calls and stays well under its time budget
- [ ] One statement of the worker tier rule exists in the shipped tree
- [ ] `./scripts/lint` is clean on every file this plan touches

## Risk Analysis

### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
| ---- | ------ | ---------- | ---------- |
| Losing durable cross-session status with the tracker | Med | Low | Checkboxes are in-repo and versioned; git is the audit trail via one-task-one-commit; the handoff already carries context and is the documented path in stealth mode today |
| Counters drift from checkbox reality | Med | Med | Single writer (D5) plus an explicit drift indicator; checkboxes remain authoritative so drift is cosmetic |
| The migration's blast radius — 31 files touch beads, every stage file is reshaped | High | Med | The two changes coincide per file, so each file is edited once; phase the work by file cluster with the lint gate (D16) as the per-file check |
| A stale cached skill body resolves old supporting-file paths after the rename | Med | Med | Alias directories keep pointer files (D9); the migration note names the session restart |
| `--plugin-dir` pointed at the repository root silently serves nothing after D1 | Med | Med | Called out in the migration note and the local-dev instruction |
| Removing beads breaks `forge`'s state detection, which infers pipeline position from issue state | Med | High | In scope explicitly; `forge` re-derives position from document existence, frontmatter status, and checkbox counts |
| Coordinator judgment replacing the regex picks a worse tier than the regex did | Low | Low | The regex's fallthrough was the most expensive tier, so the floor it set was cost not quality; the verify-then-escalate loop catches under-powering |
| D18's wording changes regress discipline on the weaker models the stages run on | Med | Low | Only the trim upstream's trials passed is in scope; the two they rejected are excluded; revert is one commit |
| A session dies before appending anything, leaving the journal's tail stale and confidently wrong | High | High | Entries open at the start of work, not the end (D8a), so the default residue of an abrupt kill is a correct open entry; the bootstrap reconciles against the working tree and never reports the journal as fact when the two disagree (D8c) |
| The knowledge file degrades into a diary whose stale entries read as current rules | High | Med | Exactly what `docs/beads-integration-learnings.md` became (D19 deletes it), which is why journal and knowledge are separate files; plus the qualification rule, one-fact entries, dated entries with verification hints, and the correct-on-discovery obligation |
| A future document accumulates stale rules the same way, after this cleanup | Med | Med | D19's second half is the durable fix: shipped skills link only into `plugin/docs/reference/`, `docs/` is never a runtime rules source, and retained history is marked non-normative at its top |
| Knowledge entries accumulate faster than they are curated | Med | Med | The qualification rule excludes task outcomes and single-task facts, which is most of the volume; the verification hint makes a stale entry cheap to disprove rather than requiring judgment |
| The follow-ups rule suppresses a fix that was genuinely required | Med | Low | The "unless the requested behavior cannot work without it" escape, the completeness clause, and `task-verifier`'s existing two-way scope check |
| An entry left open by a session that simply moved on is misread as an interruption | Low | Med | The working-tree check distinguishes them (D8c); a clean tree beside an open entry is a stale marker, not lost work |

### Assumptions

Tracked here rather than in a tracker — which is this design's own convention (D6).

| ID | Assumption | Validated? |
| -- | ---------- | ---------- |
| A1 | No consumer outside this repository depends on `wb`'s beads integration | **Validated 2026-09-08** — no other people or repos; but the user has `wb` installed on other machines/workspaces holding existing plan directories, so the migration note is written per-machine (see Resolved Decisions) |
| A2 | Checkbox-plus-counter status is sufficient at our plan sizes, as it is for CaseSmith's | **Validated 2026-09-08** — tested by this plan itself at 64 tasks across five phases, 30 of them tracked live. Position was recoverable at every boundary, every commit cites a task ID, and the plan survived being re-scoped twice without losing its place. The predicted positional-identity limitation did strain, in three concrete ways, all now handled: **(1)** a text match against a task line failed because a completion stamp had shifted it, so edits must anchor on the ID, not the surrounding prose; **(2)** `total_tasks` needed a manual bump when a task was added mid-phase, which an ID-keyed count would not have; **(3) the important one** — a naïve `grep -c '^- \[x\]'` read **38** against 30 real tasks, because a plan's success criteria and prerequisites are checkboxes too. Counting must be **ID-scoped** (`grep -cE '^- \[[ x]\] \*\*[A-Z0-9-]+\*\*'`) or every counter is systematically wrong by the number of criteria in the file. `update_status` and `validate_project` both carry that scoping explicitly |
| A3 | The ~70-call truncation ceiling generalizes to this environment | Pending — measured upstream on one machine/model; D15 states it as provenance-bearing, not constant |
| A4 | `allowed-tools: Read` behaves as upstream describes for on-demand supporting files | **Validated 2026-09-08** — Phase 0 probe smoke session: **both** halves. The sibling `templates.md` and the cross-directory `../../docs/reference/probe-ref.md` each read with **no permission prompt**, and the marker `PROBE-REF-RESOLVED` was echoed verbatim (so the read resolved rather than being paraphrased) |
| A5 | Deprecated-alias skills resolve correctly in our marketplace install, not just upstream's | **Validated 2026-09-08** — two-part evidence: a marketplace install from a `./plugin` source enumerated both skills (`Skills (2) probe, probe_old`, `Source: wbprobe@wb-probe`), and a `--plugin-dir` session invoked `probe_old`, which announced the rename **once** and then ran `probe`, reading both supporting files. Caveat: install/enumeration was observed under the marketplace identity; alias *invocation* was observed under `--plugin-dir` |

## Rejected Alternatives

### Replace beads with a graph-capable substitute (sidecar database, JSON dependency file, or the harness task tools)

- **Approach**: keep the epic/milestone/task graph and its ready-work computation, backed by
  something lighter than beads.
- **Rejected because**: the tracer-bullet probe showed the graph is write-heavy and
  read-shallow — built elaborately, consumed only to name the next task in an order the
  document already fixes and to check whether a phase's tasks are all closed. Reproducing a
  graph nobody queries would carry the cost that motivated the removal.

### Keep beads and adopt upstream's realignment instead

- **Approach**: port upstream's three persistence tiers, stealth setup rule, sanity check,
  and version floor, and require bd 1.1.0.
- **Rejected because**: it raises a hard dependency that is currently absent from the
  environment — no binary, no database, no plugin — in exchange for an index the inventory
  shows is not read deeply. It is also the largest single block of upstream work, and all of
  it becomes moot under D4.

### Rename `create_execution` and remove beads as separate changes

- **Approach**: do the cosmetic rename first, then strip beads later.
- **Rejected because**: the beads choreography and the frontmatter ID block live in the file
  being renamed, and the "tracked ONLY in beads" annotations are what D4 reverses — the two
  changes edit the same regions, so separating them means editing twice and shipping an
  intermediate state that is neither.

### Adopt upstream's Fable routing as written

- **Approach**: Fable recommended for decomposition with Opus as the floor, and Fable as the
  automatic first escalation on a verified failure.
- **Rejected because**: it contradicts the stated position that Fable is a deliberate
  upshift, and it contradicts our own advise-never-auto-switch policy. D12 keeps the
  capability one explicit step away instead.

### One merged continuity file instead of two

- **Approach**: a single `notes.md` per plan holding both session history and durable
  repository facts.
- **Rejected because**: we have the experiment's result in-repo.
  `docs/beads-integration-learnings.md` merged a session log with durable guidance, and its
  stale entries now read as current rules and contradict the shipped ones (`:233` "Always use
  TodoWrite" against `implement_tasks.md:684`'s "NEVER"). Different lifetimes need different
  files, or the durable half inherits the chronological half's decay.

### Rely on the handoff, and require sessions to end cleanly

- **Approach**: keep `create_handoff` as the sole continuity mechanism and treat a missing
  handoff as user error.
- **Rejected because**: a session does not choose how it ends. Token limits, context
  exhaustion, power loss, and harness crashes all terminate without running anything, so a
  scheme that depends on a shutdown step is absent precisely when it is needed. The handoff
  remains the right artifact for a *planned* transfer; D8 covers the unplanned case beneath it.

### Write journal entries at completion rather than opening them at the start

- **Approach**: append one entry per session summarizing what was accomplished, at the end.
- **Rejected because**: it produces silence on abrupt termination, and silence is not the worst
  of it — the tail would still show the last *completed* phase, so a cold session would read a
  confident stale entry and never learn that work stopped mid-task. Opening on entry makes the
  default residue of a kill correct rather than misleading.

### Adopt the `knowledge-store` branch as the memory surface

- **Approach**: merge the existing 4,770-line subsystem — capture hooks at turn and subagent
  boundaries, nine scripts, a proposal linter, git-based invalidation, PreToolUse enforcement.
- **Rejected because**: it answers a larger question (automatic capture with enforcement and
  programmatic invalidation) than the one asked, and its blast radius would dominate this
  plan's. D8 meets the bootstrap requirement with two markdown files and wiring into a hook
  this plan already adds. If manual curation proves insufficient in practice, that branch is
  the escalation path and its reasoning is already written.

### Trim barrier and scope-block volume along with the thinking directives

- **Approach**: complete upstream's full Phase 2 trim set.
- **Rejected because**: upstream's blind trials returned equal-or-worse for both — the
  barrier trap fixture failed under both wordings, and the trimmed scope block regressed the
  trap's reporting half. Our volume is already at parity with what upstream kept, so there is
  nothing to do and evidence against doing it.

## Pending Decisions

| ID | Decision Needed | Blocks |
| -- | --------------- | ------ |
| PD2 | Whether the coordinated worker default tier stays Opus or moves to Sonnet with Opus as the first upshift rung (D12/D13). Our current default is the ceiling by regex fallthrough; upstream deliberately moved away from it | — resolved 2026-09-08 (Opus 4.8 default, Opus 5 upshift; see Resolved Decisions) |
| PD3 | Whether D18 is approved as part of this release or deferred | — resolved 2026-09-08 (approved in full; see Resolved Decisions) |
| PD4 | Whether the `implement_*` renames follow in a later cut or are dropped | — resolved 2026-09-08 (folded into this release; see Resolved Decisions) |

## References

- Research: [research.md](research.md)
- Upstream Fable plan: `.context/upstream/docs/plans/2026-09-01-fable-5-1-rebaseline/`
  (design D1–D10, `trials/2026-09-05-blind-trials.md`)
- Upstream 3.0.0 plan: `.context/upstream/docs/plans/2026-09-05-prompts-h7c-implement-rename-3.0/`
- Upstream compaction plan: `.context/upstream/docs/plans/2026-08-21-prompts-8bj-compaction-drift-hardening/`
- Upstream truncation evidence: `.context/upstream/docs/subagent-tool-call-ceiling.md`
- Tracker-free precedent: `~/.claude/commands/law/{create_workplan,draft_tasks,update_matter_status}.md`
