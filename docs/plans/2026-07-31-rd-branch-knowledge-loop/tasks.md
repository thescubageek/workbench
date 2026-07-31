---
project: rd-branch-knowledge-loop
ticket: N/A
created: 2026-07-31
status: in-progress
last_updated: 2026-07-31
current_phase: 0
total_tasks: 41
completed_tasks: 4
depends_on: [research.md, design.md]
beads_epic: none — decided 2026-07-31 to run this project documentation-only; no bd init
beads_phases: none — see beads_epic
beads_tasks: none — see beads_epic; local IDs (P0-T1 …) are the only task identifiers
---

# Execution Plan: R+D Branch Knowledge Store

## Overview

Implementing the git-native, entry-addressable knowledge store from design.md: automatic ungated
capture into staging, a batched human-gated promotion pass, and a protected-path boundary enforced at
the tool-call layer.

**Design Approach**: Git-native entry-addressable knowledge store with hook-enforced protected-path
boundary
**Target State**: design.md → Success Criteria (7 functional, 4 non-functional)

## Implementation Strategy

### Phase Rationale

Ordering is driven by three things: the decisive unknown, the enforcement-before-loop rule, and the
thin-slice scope decision.

- **Phase 0 comes first because the whole plan rests on one unverified assumption.** design.md's
  Assumptions table records that `PreToolUse` deny/ask behaviour was verified *from documentation
  only, not executed*. Three architecture decisions depend on it. If the installed Claude Code does
  not honour `permissionDecision` as documented, Phases 2–6 are built on sand and the enforcement
  architecture has to be redesigned. One bounded probe resolves it.
- **Enforcement lands before capture and promotion (Phase 2 before 3–4).** Building the loop before
  the boundary exists means running an ungated self-extension loop, however briefly. The design's
  entire threat model argues against that ordering, so the boundary is built first even though it
  produces no user-visible value on its own.
- **The migration is last because it is the acceptance test, not a feature.** Fork 2 chose "enforcement
  - thin slice," which means every phase is scoped to *the minimum that makes the migration work* —
  not a general system that is later migrated onto. Phase 6 is where the slice is proven end to end.

Read path (Phase 5) follows promotion (Phase 4) because until entries are promoted there is nothing to
retrieve — building retrieval earlier would be untestable.

**Dependency analysis** (done in the main session rather than by spawned agents, per the standing
instruction not to use the Agent tool; research.md Part 4 already contains the pattern and integration
findings those agents would re-derive):

- The protected-path config (P1) must exist before the hook (P2) — the hook reads it, and it declares
  itself as protected, so it is the trust anchor and cannot be created by the loop later.
- The entry schema (P1) blocks capture (P3), promotion (P4), and retrieval (P5) — everything writes or
  reads that shape.
- The worktree (P1) blocks both capture and read, because staging lives on the store branch.
- `agents/research-validator.md` is reused unchanged; nothing blocks on building a verifier.
- Version bump + marketplace sync is the last task before anything reaches an installed user, because
  the cache is keyed by version (`CLAUDE.md` → Releasing).

**Parallel opportunity**: Phase 3 (capture) and Phase 5 (read path) touch disjoint command files and
could run concurrently once Phase 1 lands, if Phase 4's promoted entries are stubbed for testing.

### Testing Strategy

This repo has one executable test — `scripts/test-quiet`, a bash contract test for `scripts/quiet` —
and `scripts/lint` for markdown. That is the whole automated surface, so the strategy is:

- **Shell components (hooks, sweep script) get contract tests in the exact `scripts/test-quiet` idiom**:
  a `check "description" "$condition"` helper, PASS/FAIL counters, non-zero exit when any check fails.
  These are real automated tests and the TDD cycle applies (`skills/tdd-discipline` — RED before GREEN).
  The hook payload shape to feed on stdin is documented by the existing `scripts/lint-hook`, which
  parses `{"tool_input":{"file_path":"..."}}` with a `jq`-then-`grep` fallback.
- **Markdown components (commands, skills) have no automated correctness test.** `./scripts/lint` checks
  formatting only. This is the gap the deferred eval corpus would close, so manual verification carries
  the weight in Phases 5–6 and each phase states its manual checks explicitly rather than implying
  coverage that does not exist.
- **Phase 6 is the integration test** — the migration exercises capture → gate → invalidation →
  curation on real content.

### Note on the enforcement hook during development

The hook is inert unless a self-extension run is armed (design.md → Technical Decisions). Building this
by hand therefore does **not** trip the boundary being built, and Phase 2's tests must arm it explicitly
to exercise the deny/ask paths.

## Progress Overview

**Beads is not used for this project — decided 2026-07-31.** `bd` is not on `PATH`, there is no
`.beads/`, and the decision was to proceed documentation-only rather than run `bd init` (rationale and
trade-off in `design.md` → Technical Decisions → Integration Points). The local IDs (`P0-T1` …) are the
only task identifiers.

The consequence to work around: **there is no cross-session status.** Progress lives in this file's phase
gates and in git history, so a phase that lands must be reflected here or a resumed session cannot tell.
Per `CLAUDE.md`, markdown checkboxes are still not a status mechanism — the checkboxes in this document
are verification criteria, and the substitutes `CLAUDE.md` forbids (TodoWrite, TaskCreate) stay
forbidden.

| Phase | Name | Tasks |
| --- | --- | --- |
| 0 | Tracer bullet — verify hook primitives | 4 |
| 1 | Store foundation | 8 |
| 2 | Enforcement boundary | 7 |
| 3 | Automatic capture | 6 |
| 4 | Curation, promotion, invalidation | 8 |
| 5 | Read path | 4 |
| 6 | Migration and end-to-end validation | 4 |

---

## Phase 0: Tracer Bullet — Verify Hook Primitives

### Objective

Resolve the one unverified assumption the rest of the plan depends on: that the installed Claude Code
honours `PreToolUse` `permissionDecision` and that `Stop`/`SubagentStop` hooks can reliably write files.
Stop the moment both are answered.

### Prerequisites

- [ ] research.md validated, design.md approved
- [ ] A scratch branch or worktree where a throwaway hook can be registered without disturbing `main`

### Changes Required

Throwaway only. Nothing from this phase is kept except the recorded answer.

**File**: `.claude/settings.json` (currently `{}`) — temporary local hook registration, reverted at
phase end. Local settings are the right place because the probe must not ship
(`.claude/settings.local.json` is gitignored; `.claude/settings.json` is tracked, so revert is
mandatory).

### Tasks

- **P0-T1** — Register a throwaway `PreToolUse` hook in `.claude/settings.json` matching `Write` that
  emits `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny",
  "permissionDecisionReason":"probe"}}` for a single sentinel path, and confirm the write is actually
  blocked.
- **P0-T2** — Change the same hook to `permissionDecision: "ask"` and confirm it forces a permission
  prompt **even with auto-accept enabled**. This is the specific behaviour the three-state design rests
  on; documented but unverified.
- **P0-T3** — Register a throwaway `Stop` hook that appends a line to a scratch file, and confirm it
  fires and the write lands. Repeat for `SubagentStop` with a trivial spawned agent.
- **P0-T4** — Revert `.claude/settings.json` to `{}`, and record the verdict for each of the three
  primitives in design.md's Assumptions table (`Validated 2026-07-31` or `Invalid — <what actually
  happened>`).

### Success Criteria

**Automated Verification**

- [x] `git diff --exit-code .claude/settings.json` is clean after P0-T4 (probe fully reverted) —
      trivially clean; the probe ran in `/tmp/wb-hook-probe` and never touched the tracked file
- [x] `./scripts/lint docs/plans/2026-07-31-rd-branch-knowledge-loop/design.md` passes after the
      Assumptions table update

**Manual Verification**

- [x] A `Write` to the sentinel path was visibly refused under `deny` — in all five permission modes,
      including `bypassPermissions`
- [~] A `Write` to the sentinel path visibly prompted under `ask` **with auto-accept on** — **partial.**
      Verified that `acceptEdits` does not silently approve an `ask` (the write was refused). Whether an
      *interactive* session renders a visible prompt cannot be established headlessly; it needs a human
      at a terminal. Fails closed either way, so the three-state design is not invalidated.
- [x] The `Stop` hook's scratch line is present on disk
- [x] The `SubagentStop` hook's scratch line is present on disk

### Deviation from the written method

P0-T1–T3 were specified as edits to `.claude/settings.json` in this session. Hook configuration is
snapshotted at session start, so an in-session edit would have registered nothing and the probe would
have "passed" without executing. The probes were instead run as real headless `claude -p` child sessions
against throwaway `--settings` files in `/tmp/wb-hook-probe`. Stronger, not weaker: it actually executes,
and it makes P0-T4's revert unnecessary because the tracked file was never modified.

### Modified Files

- `.claude/settings.json` — **not modified** (see deviation note above)
- `docs/plans/2026-07-31-rd-branch-knowledge-loop/design.md` — Assumptions table updated with verdicts,
  plus a "Phase 0 Tracer Bullet — Executed Findings" subsection

### Interactive `ask` check — human-run, blocks Phase 1

The one probe an agent session cannot run. The scaffolding is live at `/tmp/wb-hook-probe`; the hook
denies-or-asks only for a path ending in `sentinel.txt`, and `PROBE_DECISION` in the settings file
selects which.

```bash
rm -f /tmp/wb-hook-probe/work/sentinel.txt /tmp/wb-hook-probe/pretool.log
cd /tmp/wb-hook-probe/work
claude --settings /tmp/wb-hook-probe/settings-ask.json --model haiku
```

In the session: press **Shift+Tab** until the footer shows **accept edits**, then send:

```text
Use the Write tool to create sentinel.txt in the current directory containing exactly: hello
```

Reading the result:

| Observed | Meaning | Action |
| --- | --- | --- |
| A permission prompt appears citing `probe: protected path`, despite accept-edits | **PASS** — the three-state design holds as written | Tick the Phase 1 gate; proceed |
| The write lands silently, no prompt, `sentinel.txt` exists | **FAIL, and the bad one** — accept-edits bypasses `ask`, so an armed interactive run could self-approve | Stop; re-open the three-state decision. `ask` cannot be the interactive state |
| Refused outright with no prompt | Partial — fails closed, so no security hole, but `ask` buys nothing over `deny` | Collapse the armed hook to two states (inert / `deny`) and simplify Phase 2 |

Afterwards: `cat /tmp/wb-hook-probe/pretool.log` should show one `decision=ask` line per attempt — if it
is empty the hook never fired and the run proved nothing. Record the verdict in design.md's Assumptions
table and in the Phase 0 findings subsection.

### ⛔ CHECKPOINT: Phase 0 Complete

**If `ask` does not survive auto-accept**, the three-state hook collapses to two states and the design
decision must be revisited before Phase 2 — stop and re-open that decision rather than proceeding.

**If `PreToolUse` deny does not work at all**, the enforcement architecture is invalid. Stop. The
convention-only option was rejected as strictly dominated *because* a mechanical alternative existed;
if it does not, that rejection has to be reconsidered and the design revised.

**If `Stop`/`SubagentStop` cannot write reliably**, automatic capture moves back into command prose and
Phase 3 is redesigned — but Phases 1, 2, 4–6 survive unchanged.

Do not proceed without a human confirming the three verdicts.

---

## Phase 1: Store Foundation

### Objective

Establish the store branch, the worktree access path, the entry schema, and the protected-path config —
the trust anchor everything else reads.

### Prerequisites

- [x] Phase 0 complete, all three primitives verified
- [x] Decision on whether `thescubageek/self-learning-loops-research` becomes the store branch or a
      dedicated branch is created
  - **Decided 2026-07-31** → reuse `thescubageek/self-learning-loops-research`; decision recorded in
    `design.md` (## Technical Decisions → Architecture)
- [ ] **Human-run gate (decided 2026-07-31): the interactive auto-accept `ask` check has passed.** Phase 0
      verified `ask` only in non-interactive modes; the middle row of the three-state table is still
      unobserved. See "Interactive `ask` check" below for the procedure. Phase 1 does not start until this
      is confirmed.

### Changes Required

#### 1. Store branch and layout

**Target State** (from design.md): a long-lived branch that merges `main` forward continuously, never
merges outbound, and holds knowledge alongside code so `file:line` refs resolve locally.

Layout to establish on that branch:

- `knowledge/entries/<kind>/<id>.md` — promoted entries, one file each
- `knowledge/staging/<id>.md` — ungated captures, a separate tree so retrieval can never reach it
- `knowledge/INDEX.md` — generated, never hand-edited

#### 2. Protected-path config

**File**: `.wb-knowledge.json` (repo root, tracked)

Declares the protected path set and the write policy for *this* repo. Must list itself — it is core
self-extension by definition, and the moment it is created is the trust anchor of the whole scheme.

### Tasks

- **P1-T1** — Decide and establish the store branch: designate the current R+D branch or create a
  dedicated one; document the choice and the `main`-forward-merge policy (merge, never rebase) in the
  store's own README.
- **P1-T2** — Create the `knowledge/entries/`, `knowledge/staging/` split on the store branch with a
  README in each explaining the trust distinction between them.
- **P1-T3** — Write the entry schema doc defining the seven fields from design.md → Data Model (ID,
  claim, provenance with cited paths + verified-at SHA, confidence, scope tags, kind, origin) with one
  filled-in real example, not a template stub.
- **P1-T4** — Define the collision-free ID scheme for concurrent writers across parallel workspaces
  (workspace + run + sequence components), and document why each component is needed.
- **P1-T5** — Create `.wb-knowledge.json` declaring this repo's protected paths (`commands/`,
  `agents/`, `skills/`, `hooks/`, `CLAUDE.md`, `.wb-knowledge.json` itself) and the strict default write
  policy.
- **P1-T6** — Write the schema for `.wb-knowledge.json` such that "auto-promote core self-extension" is
  **not expressible** — the absence of that setting is a design requirement, not an omission.
- **P1-T7** — Write `scripts/knowledge-worktree` to create or attach the store-branch worktree, and to
  fail loudly (non-zero, clear message) when it cannot — a silent no-op is worse than no capture.
- **P1-T8** — Write `scripts/test-knowledge-worktree` contract test in the `scripts/test-quiet` idiom,
  covering: attaches cleanly, is idempotent on re-run, exits non-zero with a readable message when the
  branch is missing.

### Success Criteria

**Automated Verification**

- [ ] `./scripts/test-knowledge-worktree` passes
- [ ] `./scripts/lint --all` clean
- [ ] `jq . .wb-knowledge.json` parses
- [ ] `git worktree list` shows the store worktree after running `scripts/knowledge-worktree`

**Manual Verification**

- [ ] The entry schema example is a real entry about this codebase, with paths that resolve
- [ ] `.wb-knowledge.json` lists itself in the protected set
- [ ] The staging/entries README pair makes the trust distinction unmistakable to a reader who has not
      read design.md

### Modified Files

- `knowledge/entries/README.md`, `knowledge/staging/README.md`, `knowledge/SCHEMA.md` — new, store branch
- `.wb-knowledge.json` — new
- `scripts/knowledge-worktree`, `scripts/test-knowledge-worktree` — new
- `scripts/README.md` — document the new scripts

### ⛔ CHECKPOINT: Phase 1 Complete

Do not proceed until `.wb-knowledge.json` exists and is human-reviewed. It is the trust anchor — every
later control reads it, and after Phase 2 the loop can no longer modify it.

---

## Phase 2: Enforcement Boundary

### Objective

Build the three-state `PreToolUse` guard: inert during normal development, `ask` in an armed
interactive run, hard `deny` in an armed full-auto run.

### Prerequisites

- [ ] Phase 1 complete, `.wb-knowledge.json` reviewed and committed
- [ ] Phase 0 verdicts confirm `deny` and `ask` both behave as documented
  - **Decided 2026-07-31**: `deny` is confirmed in all five permission modes including
    `bypassPermissions`. `ask` is confirmed non-bypassable only in non-interactive modes; the interactive
    half was promoted to a human-run gate on **Phase 1** rather than deferred to here, so by the time this
    prerequisite is read it is either satisfied or the three-state decision has already been re-opened.
    Recorded in `design.md` (## Technical Decisions → Architecture).

### Changes Required

**File**: `hooks/knowledge-guard.sh` (new)

Reads the `PreToolUse` payload on stdin (same shape `scripts/lint-hook` already parses), resolves the
target path, consults `.wb-knowledge.json`, and emits a `permissionDecision`.

Behaviour table from design.md:

| Context | Decision |
| --- | --- |
| No `.wb-knowledge.json` in host repo | inert (fail-open across repos) |
| Config present, no run armed | inert |
| Armed, interactive | `ask` |
| Armed, full-auto/unattended | `deny` |
| Config present, path indeterminate | `deny` (fail-closed within a configured repo) |

### Tasks

- **P2-T1** — Write `scripts/test-knowledge-guard` FIRST (RED), covering every row of the table above
  plus: path outside the protected set passes through, arming signal absent means inert, malformed
  config means deny.
- **P2-T2** — Implement `hooks/knowledge-guard.sh` to make the tests pass (GREEN), following the
  stdin-JSON parsing idiom in `scripts/lint-hook` including the `jq`-absent fallback.
- **P2-T3** — Implement host-repo detection: the hook is inert when the host repo has no
  `.wb-knowledge.json`, so a marketplace install never denies in someone else's repo.
- **P2-T4** — Implement the arming mechanism so that arm state is established outside the agent's tool
  layer and cannot be set by the loop; add a test asserting an agent-writable path cannot flip it.
- **P2-T5** — Implement the full-auto detection and add a test asserting that a run which *claims*
  interactive without evidence is treated as full-auto (deny), not as interactive.
- **P2-T6** — Register the hook on `PreToolUse` matching `Write` and `Edit` in
  `.claude-plugin/plugin.json`, alongside the existing lint hook.
- **P2-T7** — Add a graceful-degradation path: when the hook cannot run at all, surface that enforcement
  is unavailable rather than proceeding silently as if it were on.

### Success Criteria

**Automated Verification**

- [ ] `./scripts/test-knowledge-guard` passes, covering all five behaviour rows
- [ ] `./scripts/test-quiet` still passes (no regression in the existing script contract)
- [ ] `jq . .claude-plugin/plugin.json` parses after hook registration
- [ ] `./scripts/lint --all` clean

**Manual Verification**

- [ ] With no run armed, editing `commands/help.md` by hand and via the agent both succeed
- [ ] With a run armed interactively, an agent edit to `commands/help.md` prompts for approval, and the
      prompt appears **with auto-accept enabled**
- [ ] With a run armed full-auto, the same edit is refused with a legible reason
- [ ] In a scratch repo with no `.wb-knowledge.json`, the hook never fires

### Modified Files

- `hooks/knowledge-guard.sh` — new
- `scripts/test-knowledge-guard` — new
- `.claude-plugin/plugin.json` — `PreToolUse` registration

### ⛔ CHECKPOINT: Phase 2 Complete

Verify by hand in a scratch repo that a marketplace-shaped install does **not** deny writes. This is the
highest-impact risk in design.md's risk table; a regression here breaks other people's repositories, not
just this one.

---

## Phase 3: Automatic Capture

### Objective

Capture learnings into `knowledge/staging/` at turn and subagent boundaries, without the agent choosing
to record.

### Prerequisites

- [ ] Phase 2 complete — the boundary exists before the loop that writes
- [ ] Phase 0 confirmed `Stop`/`SubagentStop` can write reliably

### Tasks

- **P3-T1** — Write `scripts/test-knowledge-capture` FIRST (RED): writes a well-formed entry to
  `staging/`, never to `entries/`; fails loudly when the worktree is absent; two concurrent invocations
  produce two distinct files.
- **P3-T2** — Implement `hooks/knowledge-capture.sh` emitting a staging entry with the Phase 1 schema
  and the Phase 1 ID scheme.
- **P3-T3** — Register it on `Stop` and `SubagentStop` in `.claude-plugin/plugin.json`.
- **P3-T4** — Wire `commands/validate_execution.md:381` ("Note lessons learned for future projects") to
  name `knowledge/staging/` as its destination — the highest-signal source, since validation is the only
  phase with ground truth (`:279-291`).
- **P3-T5** — Wire the remaining three capture points to the same destination:
  `commands/create_handoff.md:214-218`, `commands/implement_tasks.md:494`,
  `commands/implement_coordinated.md:652`.
- **P3-T6** — Add the origin field discipline: captures derived from tool output (test results, diffs,
  validator verdicts) are marked tool-verified; everything else is model-narrated. The write policy
  tiers on this, so mislabelling defeats it.

### Success Criteria

**Automated Verification**

- [ ] `./scripts/test-knowledge-capture` passes including the concurrency case
- [ ] `jq . .claude-plugin/plugin.json` parses
- [ ] `./scripts/lint --all` clean

**Manual Verification**

- [ ] Running any `/wb:*` command to completion leaves at least one staging entry, with no explicit
      instruction to record
- [ ] Removing the worktree causes a visible, legible failure rather than a silent no-op
- [ ] No capture ever lands in `knowledge/entries/`

### Modified Files

- `hooks/knowledge-capture.sh`, `scripts/test-knowledge-capture` — new
- `.claude-plugin/plugin.json` — `Stop` / `SubagentStop` registration
- `commands/validate_execution.md`, `commands/create_handoff.md`, `commands/implement_tasks.md`,
  `commands/implement_coordinated.md` — capture destination named

### ⛔ CHECKPOINT: Phase 3 Complete

Confirm staging is accumulating from real work before building the drain. A pass with nothing to curate
cannot be tested meaningfully.

---

## Phase 4: Curation, Promotion, and Invalidation

### Objective

Build the manually-triggerable batched pass that drains staging through a fresh-context reviewer into
promoted entries, plus the git-only staleness sweep.

### Prerequisites

- [ ] Phase 3 complete, staging has real captured content

### Tasks

- **P4-T1** — Write `scripts/test-knowledge-sweep` FIRST (RED): an entry whose cited paths are unchanged
  since its verified-at SHA classifies clean; one whose paths changed classifies suspect; an entry citing
  no paths is reported as undecidable rather than clean.
- **P4-T2** — Implement `scripts/knowledge-sweep` using `git diff <verified-sha>..HEAD -- <cited paths>`
  and no model call.
- **P4-T3** — Create `commands/curate_knowledge.md` — the manual-trigger pass. It arms the guard, reads
  staging, and produces a reviewable diff; it never mutates `entries/` live.
- **P4-T4** — Specify the fresh-context reviewer in that command per `skills/touch-grass/SKILL.md:88` —
  a clean-context subagent given the candidate and nothing else, because a same-context reviewer
  rubber-stamps.
- **P4-T5** — Wire `agents/research-validator.md` in as the claim verifier for suspect and candidate
  entries, unchanged. If it turns out to need schema changes, that invalidates an Assumption and should
  be recorded, not patched over.
- **P4-T6** — Implement the four curation operations (add / update / merge / deprecate) with the
  diversity rule bounding merge: keep entries that each win on some class of ticket rather than
  collapsing to one canonical best practice.
- **P4-T7** — Record a prediction on every promoted entry, per design.md → Data Model, even though v1
  cannot strongly check it yet — so predictions are checkable retroactively once the corpus exists.
- **P4-T8** — Add the on-sync invalidation trigger so the sweep runs when the store branch merges `main`
  forward, not only on demand.

### Success Criteria

**Automated Verification**

- [ ] `./scripts/test-knowledge-sweep` passes, including the undecidable case
- [ ] `./scripts/lint --all` clean
- [ ] A sweep over the whole store completes with no model calls (verifiable — the script makes none)

**Manual Verification**

- [ ] `/wb:curate_knowledge` produces a diff for review, and nothing is written to `entries/` until it
      is approved
- [ ] The reviewer subagent receives only the candidate, not the authoring context
- [ ] A deliberately stale entry (cite a path, then change it) is caught by the sweep
- [ ] Merging two entries that win on different ticket classes is refused by the diversity rule

### Modified Files

- `scripts/knowledge-sweep`, `scripts/test-knowledge-sweep` — new
- `commands/curate_knowledge.md` — new
- `skills/knowledge-store/SKILL.md` — new; store conventions and the curation operations

### ⛔ CHECKPOINT: Phase 4 Complete

Confirm by hand that no path exists from staging to `entries/` that skips the reviewer.

---

## Phase 5: Read Path

### Objective

Make promoted entries retrievable at research and resume time, scoped by tag, bounded in count, and
never reaching staging.

### Prerequisites

- [ ] Phase 4 complete, at least a few promoted entries exist

### Tasks

- **P5-T1** — Extend `commands/create_research.md:47-60` (Step 0) to consult the store alongside
  `jira-context`, inheriting the existing best-effort/never-blocking contract at `:60` and the
  scope-not-substance caveat at `:58`.
- **P5-T2** — Add the store as a second input source to `commands/resume_handoff.md:158` (Step 4, Apply
  Learnings), which is already the proven consumer of captured learnings.
- **P5-T3** — Implement scoped, count-bounded retrieval reading `knowledge/entries/` only — never
  `knowledge/staging/`. Retrieval noise and negative transfer are the measured failure modes and both
  worsen with store size, so a wholesale load is explicitly wrong.
- **P5-T4** — Declare the store as a fifth category in `skills/project-structure/SKILL.md`, whose Quick
  Check currently routes only to research.md / design.md / tasks.md / thoughts/.

### Success Criteria

**Automated Verification**

- [ ] `./scripts/lint --all` clean
- [ ] `grep -r "knowledge/staging" commands/ skills/` returns no retrieval-path reference

**Manual Verification**

- [ ] A fresh-context run of `/wb:create_research` surfaces a relevant promoted entry
- [ ] The same run with the worktree removed still completes — degraded, not halted
- [ ] An irrelevant entry (wrong scope tag) is not surfaced
- [ ] No staging content ever appears in a research document

### Modified Files

- `commands/create_research.md`, `commands/resume_handoff.md` — read path
- `skills/project-structure/SKILL.md` — fifth category
- `skills/knowledge-store/SKILL.md` — retrieval rules

---

## Phase 6: Migration and End-to-End Validation

### Objective

Prove the slice on real content by migrating `docs/beads-integration-learnings.md`, then release.

### Prerequisites

- [ ] Phases 1–5 complete

### Tasks

- **P6-T1** — Migrate the surviving learnings from `docs/beads-integration-learnings.md` into entries,
  re-validated against HEAD. The three known-contradicted items (`:66-86`, `:88-113`, `:229-235` — all
  recommend tracking mechanisms `CLAUDE.md` forbids) must be **caught by the invalidation path**, not by
  a human reading both files. If the sweep misses them, that is a real finding about the sweep, not a
  reason to hand-correct and move on.
- **P6-T2** — Triage the dropped backlog at `:244-252` (four known duplications from an earlier review,
  never actioned) — each either becomes an entry or is explicitly dropped with a reason. Carrying it
  over silently would recreate the original failure.
- **P6-T3** — Mark `docs/beads-integration-learnings.md` superseded and historical, leaving a pointer to
  the store. Two live sources of truth is the drift documented in research.md §4.6.
- **P6-T4** — Bump `version` to `1.13.0` in **both** `.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json` (currently `1.12.3` in both; new commands/skills/hooks make this a
  feature bump), and document the new surface in `README.md` and `CLAUDE.md`.

### Success Criteria

**Automated Verification**

- [ ] `./scripts/lint --all` clean
- [ ] `./scripts/test-quiet`, `./scripts/test-knowledge-guard`, `./scripts/test-knowledge-capture`,
      `./scripts/test-knowledge-sweep` all pass
- [ ] Versions match: `jq -r '.version' .claude-plugin/plugin.json` equals
      `jq -r '.plugins[0].version' .claude-plugin/marketplace.json`

**Manual Verification**

- [ ] All seven functional requirements in design.md → Success Criteria demonstrably hold
- [ ] The three contradicted items were surfaced by the sweep, not by hand
- [ ] `claude plugin update wb@thescubageek-workbench` in a test install picks up 1.13.0 and the plugin
      still works in a repo with no store and no beads

### Modified Files

- `docs/beads-integration-learnings.md` — marked superseded
- `knowledge/entries/**` — migrated entries
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — version bump
- `README.md`, `CLAUDE.md` — document the new surface

### ⛔ CHECKPOINT: v1 Complete

Run `/wb:validate_execution` before considering this done.

---

## Implementation Discoveries

To determine during implementation:

- Whether the arming signal can be made genuinely unreachable from the agent's tool layer, or whether it
  is only *inconvenient* to reach. If only inconvenient, say so plainly — the design's threat model
  depends on the stronger claim.
- Whether `agents/research-validator.md` really accepts a knowledge entry unchanged, or needs a schema
  shim. Recorded as an Assumption; the answer belongs back in design.md either way.
- How large `knowledge/INDEX.md` gets before generation cost or read cost matters.
- ~~Whether full-auto is reliably detectable from within a hook, or whether it must be asserted by the
  invoking trigger.~~ **Answered 2026-07-31 (Phase 0): it must be asserted.** `permission_mode` is in the
  `PreToolUse` payload, but a headless `claude -p` run reports `"default"` — indistinguishable from an
  interactive session. Elevated modes are a one-way suspicion signal only. Phase 2 rule: absent a
  positive interactive assertion from the arming act, treat the run as full-auto and `deny`.

## Blockers and Notes

### Current Blockers

- ~~**Beads unavailable** — no `bd` binary, no `.beads/`. Status tracking is unavailable until
  `bd init`.~~ **Decided 2026-07-31**: proceed documentation-only — no `bd init` for this project;
  `P0-T1`-style local IDs are the only task identifiers. Decision and its trade-off recorded in
  `design.md` (## Technical Decisions → Integration Points). Consequence to respect: cross-session status
  lives in the phase gates in this file plus git history, so keep them current as each phase lands.

### Implementation Notes

- The enforcement hook is inert during ordinary development, so building it does not obstruct building
  it. Phase 2's tests must arm it deliberately.
- `docs/plans/` is gitignored (`.gitignore:7`); this project's documents are tracked only because they
  were force-added onto the R+D branch.
- **Hook probes must run as child `claude -p` sessions.** Hook config is read at session start, so
  editing `.claude/settings.json` mid-session tests nothing. Phase 2 and Phase 3 hook tests inherit this:
  a contract test that feeds a payload to the script on stdin tests the script, and a `claude -p` child
  session with `--settings` tests the *registration and enforcement*. Both are needed; only the first is
  covered by the `scripts/test-quiet` idiom.
- **Phase 3 capture has more to work with than assumed.** `Stop`/`SubagentStop` payloads carry
  `transcript_path` (and `agent_transcript_path` / `agent_id` / `agent_type` for subagents), so capture
  can read the run's actual trajectory rather than only `last_assistant_message`.

## Quick Reference

### Key Files

- **Research**: [research.md](research.md)
- **Design**: [design.md](design.md)
- **Hook payload idiom**: `scripts/lint-hook`
- **Contract test idiom**: `scripts/test-quiet`
- **Reused verifier**: `agents/research-validator.md`
- **Fresh-context critic rationale**: `skills/touch-grass/SKILL.md:88`

### Common Commands

```bash
./scripts/lint --all                 # Markdown lint
./scripts/test-quiet                 # Existing contract test (regression check)
./scripts/test-knowledge-guard       # Phase 2
./scripts/test-knowledge-capture     # Phase 3
./scripts/test-knowledge-sweep       # Phase 4
```

### Design Decisions Reference

- Store branch is long-lived and unmerged outbound; `main` merges **forward into it**, never rebased
- Store is scoped per-repo; cross-repo transfer is out of scope
- Capture is automatic and ungated; promotion is batched and human-gated
- Enforcement: inert / `ask` interactive / `deny` full-auto, opt-in by host-repo config
- All core self-extension is permanently human-gated, with no configurable override
- Git is source of truth for proposals; beads is a queryable overlay
