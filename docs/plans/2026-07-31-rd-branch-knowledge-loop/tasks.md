---
project: rd-branch-knowledge-loop
ticket: N/A
created: 2026-07-31
status: in-progress
last_updated: 2026-07-31
current_phase: 4
total_tasks: 42
completed_tasks: 35
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

**The test must be an A/B within one session, not a single write.** A first attempt (2026-07-31) asked
only for the `sentinel.txt` write after a manual Shift+Tab; a prompt appeared, but the dialog offered
"Yes, allow all edits during this session (shift+tab)" — an option only shown when accept-edits is *not*
already active. In default mode a `Write` prompts anyway, so that run could not distinguish the hook's
effect from ordinary behaviour. **Inconclusive, not a pass.** The procedure below fixes both holes: the
mode is set on the command line instead of by keystroke, and a control file the hook ignores runs in the
same turn as the sentinel.

```bash
rm -f /tmp/wb-hook-probe/work/sentinel.txt /tmp/wb-hook-probe/work/control.txt \
      /tmp/wb-hook-probe/pretool.log
cd /tmp/wb-hook-probe/work
claude --settings /tmp/wb-hook-probe/settings-ask.json --permission-mode acceptEdits --model haiku
```

Send exactly one message:

```text
Use the Write tool to create control.txt containing hello, then use the Write tool to
create sentinel.txt containing hello.
```

The hook only matches paths ending in `sentinel.txt`; `control.txt` passes through untouched. So the two
writes differ in exactly one variable, and the comparison reads itself:

| `control.txt` | `sentinel.txt` | Meaning | Action |
| --- | --- | --- | --- |
| silent | **prompts** | **PASS** — accept-edits is provably active, and only the hook's `ask` interrupts it | Tick the Phase 1 gate; proceed |
| silent | silent, file written | **FAIL, and the bad one** — accept-edits bypasses `ask`; an armed interactive run could self-approve | Stop; re-open the three-state decision. `ask` cannot be the interactive state |
| silent | refused, no prompt | Partial — fails closed, no security hole, but `ask` buys nothing over `deny` | Collapse the armed hook to two states (inert / `deny`); simplify Phase 2 |
| **prompts** | either | Void — accept-edits was not active, same confound as attempt 1 | Re-run; check the footer reads `accept edits` |

Afterwards `cat /tmp/wb-hook-probe/pretool.log` should show a line for **both** files — the probe logs
every invocation before it checks the filename, and `decision=` echoes `PROBE_DECISION`, not what was
returned. Two lines is correct and proves the hook ran on both writes; an *empty* log means it never
fired and the run proved nothing.

**VERDICT 2026-07-31 — PASS.** Footer read `accept edits on`; `control.txt` was written with no prompt
and `sentinel.txt` prompted for approval. Recorded in design.md's Assumptions table and Phase 0 findings.
Two incidental findings from the same run, both carried into Phase 2:

- Claude Code redirected the writes into a per-session scratchpad
  (`/private/tmp/claude-501/<slug>/<uuid>/scratchpad/`) rather than the cwd, and `/tmp` arrived as
  `/private/tmp`. The guard must match on **resolved** paths, and must not treat "outside every protected
  prefix" as "safe" — that is the indeterminate case, which fails closed to `deny`.
- The first attempt at this check was inconclusive because it lacked a control. Any future hook-behaviour
  probe needs an A/B in the same session; a single observation cannot separate the hook from the
  harness's own default.

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
- [x] **Human-run gate (decided 2026-07-31): the interactive auto-accept `ask` check has passed.**
      **PASSED 2026-07-31** — A/B under `accept edits on`: control file silent, sentinel prompted. All
      three rows of the behaviour table are now observed. Procedure and verdict below.

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
- **P1-T9** *(added 2026-07-31, decided during review; **done 2026-07-31**)* — Add `ajv` as a hard
  dependency and validate
  `.wb-knowledge.json` against `.wb-knowledge.schema.json` in the test suite. Requires a `package.json`
  (the repo has none) and an install note in `scripts/README.md`. Turn the three negative fixtures
  described at the foot of `scripts/test-knowledge-config` into real rejection tests — a config carrying
  `write_policy.core_self_extension`, one with `model_narrated: "auto-promote"`, and one whose
  `protected_paths` omits itself must each be **rejected by the validator**, which is what upgrades
  P1-T6's guarantee from "the schema says so" to "nothing else validates."

### Success Criteria

**Automated Verification**

- [x] `./scripts/test-knowledge-worktree` passes — 26/26
- [x] `./scripts/lint --all` clean
- [x] `jq . .wb-knowledge.json` parses
- [x] `git worktree list` shows the store worktree after running `scripts/knowledge-worktree` — the
      store branch is checked out in *this* workspace, so the script resolves to it rather than creating
      a second one; the create path is covered by the contract test instead
- [x] `./scripts/test-knowledge-config` passes — 47/47 (added; see below). Was 31/31 structural; P1-T9
      added the ajv enforcement layer plus two protected-path assertions
- [x] `./scripts/validate-json-schema .wb-knowledge.schema.json .wb-knowledge.json` exits 0 (P1-T9)
- [x] `npm test` runs all three suites green

**Manual Verification**

- [x] The entry schema example is a real entry about this codebase, with paths that resolve —
      `.claude-plugin/plugin.json:10-45` and `scripts/lint-hook:9-19`, both checked
- [x] `.wb-knowledge.json` lists itself in the protected set — and the schema *requires* it to, so a
      config that omitted itself is invalid rather than merely wrong
- [x] The staging/entries README pair makes the trust distinction unmistakable to a reader who has not
      read design.md

### Modified Files

- `knowledge/README.md` — new; store branch policy, merge-forward-never-rebase (**added**, P1-T1 needed
  a home for the branch policy)
- `knowledge/entries/README.md`, `knowledge/staging/README.md`, `knowledge/SCHEMA.md` — new, store branch
- `.wb-knowledge.json` — new
- `.wb-knowledge.schema.json` — new (**added**; P1-T6 asked for a schema, which needs its own file)
- `scripts/knowledge-worktree`, `scripts/test-knowledge-worktree` — new
- `scripts/test-knowledge-config` — new (**added**; the only way to actually assert P1-T6's
  "unexpressible" requirement, since the toolchain has no JSON Schema validator)
- `scripts/README.md` — document the new scripts
- `package.json`, `package-lock.json` — new (**added**, P1-T9); `ajv` pinned at 8.20.0 as the repo's
  first node dependency
- `scripts/validate-json-schema` — new (**added**, P1-T9); ajv-backed validator, dev-time only
- `.gitignore` — `node_modules/`
- `CLAUDE.md` — Development Tools gains a Setup section for `npm install`

### What Phase 1 surfaced

- **Parallel Conductor workspaces are git worktrees of one shared repository**, not independent clones
  (`git rev-parse --git-common-dir` → `/Users/thescubageek/projects/workbench/.git`, three worktrees
  registered). Git permits a branch to be checked out in exactly one worktree, so a second workspace
  *cannot* create its own store worktree while this one holds the branch. `knowledge-worktree` therefore
  **resolves to whichever checkout already holds the branch** instead of competing for it. This turns out
  to be what the design wanted anyway: all workspaces share one store directory, so a capture made in one
  is immediately visible to a curation pass run from another. Phase 3 inherits the consequence — concurrent
  captures land in the same directory, which is exactly what the collision-free ID scheme is for.
- **P1-T6's guarantee was structural; P1-T9 closed it. Done 2026-07-31.** The schema makes "auto-promote
  core self-extension" unexpressible — no such property, `additionalProperties: false` at every level,
  `model_narrated` pinned to a `const` rather than an enum — but until P1-T9 **no JSON Schema validator
  ran anywhere in this repo's toolchain**, so nothing mechanically rejected a config that violated it.
  `ajv` is now a hard dev dependency (`package.json`, pinned 8.20.0), `scripts/validate-json-schema`
  executes the schema, and `scripts/test-knowledge-config` feeds it thirteen jq-mutated copies of the
  live config. The three fixtures P1-T9 named are real rejection tests now, alongside ten more
  (unknown keys at each level, absolute protected path, empty `protected_paths`, `version: 2`, …).
  47/47.
  - **The positive control is what makes the rejections mean anything.** A fourteenth mutation relaxes
    `tool_verified` to `auto-promote` — the one axis the policy may relax — and must still be *accepted*.
    Without it, a validator that refused everything would turn every rejection test green. Same lesson as
    the Phase 0 A/B; applied deliberately this time rather than learned again.
  - Each rejection was additionally traced to the schema construct responsible: deleting the
    `protected_paths.allOf` makes the omits-itself config validate, and loosening `model_narrated` from
    `const` to `type: string` makes the auto-promote config validate. The tests fail for the right reason.
  - **Constraint that lands on Phase 2**: `ajv` and `node_modules/` are **dev-time only**. A marketplace
    install is a bare clone with no `node_modules`, so `hooks/knowledge-guard.sh` must keep reading
    `.wb-knowledge.json` with the `scripts/lint-hook` jq-then-grep idiom and **must never** shell out to
    `validate-json-schema`. The validator proves the config is well-formed in CI and at review time; the
    hook must still degrade gracefully when handed one that is not.

- **Introducing `package.json` opened a hole in the trust anchor, so the protected set grew from thirteen
  paths to fifteen** — `package.json` and `package-lock.json` added 2026-07-31. Reason: they pin the ajv
  version `scripts/validate-json-schema` runs. An armed run able to edit them could pin a validator that
  accepts anything, and every enforcement test above would still report green — the same bypass as
  editing the schema, one level further up, and the design's own default-deny rule for ambiguous cases
  points the same way. Asserted in `scripts/test-knowledge-config` rather than required by
  `.wb-knowledge.schema.json`, because it is repo-specific: a host project may legitimately have no
  `package.json`, whereas the config and its schema are universal. **Confirmed by the maintainer
  2026-07-31** — the protected set is the trust anchor and changing it is specified as a human-only act,
  so the join was raised for a decision rather than taken. The set now stands at fifteen paths.
- **The ID scheme needs an atomic allocator, not just distinguishing components.** Documented in
  `knowledge/SCHEMA.md`: the date/workspace/session/agent components make collisions unlikely, but two
  subagents can finish in the same millisecond, so the sequence must be allocated by atomic create
  (`set -C` / `O_EXCL`) with retry. Counting existing files is a read-then-write race. Phase 3 must
  implement it that way; P3-T1's concurrency test is the check.
- **How code built on this branch ships — resolved 2026-07-31 by splitting the branches.** The store
  branch is permanently unmerged outbound, but `hooks/`, `scripts/`, `commands/` and P6-T4's version bump
  only reach an installed user via `main`. **Decision: Phases 2–5 code is built on a normal feature branch
  off `main`; only `knowledge/` stays on the store branch.** Code then flows feature-branch → `main` →
  forward-merge into the store branch, so the store still holds both and entry `file:line` refs still
  resolve. Recorded in `design.md` (## Technical Decisions → Architecture). Phase 1's already-committed
  code must be moved to the feature branch as part of the split.

  **Split executed 2026-07-31.** Feature branch `thescubageek/knowledge-store-v1` cut from `origin/main`
  at `1535d8a`, carrying the Phase 1 code as commit `79c8e59`; the store branch keeps `knowledge/` and
  `docs/plans/`. All tests green on both sides. Two notes: **`main` has moved to v1.12.4**, so P6-T4's
  bump is `1.12.4 → 1.13.0`, not `1.12.3 → 1.13.0`; and the split surfaced two genuine test bugs, fixed
  on the feature branch — the store branch may exist only as a remote-tracking ref in a fresh clone, and
  protected paths under the store root are legitimately absent from a code branch (protecting a path that
  does not exist still prevents its creation, so existence was never the right requirement).

  **The split, concretely** — moves to the feature branch (cut from `origin/main`):
  `.wb-knowledge.json`, `.wb-knowledge.schema.json`, `scripts/knowledge-worktree`,
  `scripts/test-knowledge-worktree`, `scripts/test-knowledge-config`, and the `scripts/README.md` edits.
  Stays on the store branch: `knowledge/**` and `docs/plans/**` — the latter because it is gitignored
  dev-only content that must never reach `main`. No force-push and no rebase: the store branch gets an
  ordinary commit removing the code, and its history stays intact so provenance SHAs keep pointing at
  real commits. Workspace arrangement: `kyiv` keeps the store branch, a second Conductor workspace
  carries the feature branch, and Phases 2–5 are implemented there.

### ⛔ CHECKPOINT: Phase 1 Complete

Do not proceed until `.wb-knowledge.json` exists and is human-reviewed. It is the trust anchor — every
later control reads it, and after Phase 2 the loop can no longer modify it.

---

## Phase 2: Enforcement Boundary

### Objective

Build the three-state `PreToolUse` guard: inert during normal development, `ask` in an armed
interactive run, hard `deny` in an armed full-auto run.

### Prerequisites

- [x] Phase 1 complete, `.wb-knowledge.json` reviewed and committed
  - **Reviewed 2026-07-31**: the thirteen-path set stands as committed, including the seven added beyond
    P1-T5's enumeration. Decision and rationale in `design.md` (## Technical Decisions → Architecture).
- [x] Phase 0 verdicts confirm `deny` and `ask` both behave as documented
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

- [x] `./scripts/test-knowledge-guard` passes, covering all five behaviour rows — **69/69**
- [x] `./scripts/test-quiet` still passes (no regression in the existing script contract) — 9/9
- [x] `jq . .claude-plugin/plugin.json` parses after hook registration
- [x] `./scripts/lint --all` clean
- [x] `./scripts/probe-knowledge-guard` passes — **6/6**, three real `claude -p` sessions (added; the
      registration layer a contract test structurally cannot reach)
- [x] Whole suite re-run under **bash 3.2** (`/bin/bash`, macOS's default) with clean stderr — the hook
      ships to every install and cannot assume bash 5

**Manual Verification**

- [x] With no run armed, editing `commands/help.md` by hand and via the agent both succeed — probe
      Run B wrote the sentinel with the guard registered and unarmed; by-hand edits never reach a
      `PreToolUse` hook at all
- [ ] With a run armed interactively, an agent edit to `commands/help.md` prompts for approval, and the
      prompt appears **with auto-accept enabled** — **human-run, still owed.** Cannot be observed
      headlessly. Phase 0 settled the underlying primitive by human A/B (control silent, sentinel
      prompted under `accept edits on`); this re-runs it against the real guard. Fails closed either
      way, so it gates the *claim*, not the code
- [x] With a run armed full-auto, the same edit is refused with a legible reason — probe Run A; the
      model reported "refused because that path is protected as core system extension machinery"
- [x] In a scratch repo with no `.wb-knowledge.json`, the hook never fires — probe Run C

### Modified Files

- `hooks/knowledge-guard.sh` — new
- `scripts/test-knowledge-guard` — new
- `scripts/probe-knowledge-guard` — new (**added**; the second test layer, opt-in because it spawns
  real sessions)
- `.claude-plugin/plugin.json` — `PreToolUse` registration, matcher `Write|Edit|MultiEdit|NotebookEdit`
- `scripts/README.md`, `README.md` — the guard, its arming contract, and the named Bash hole
- `package.json` — `npm test` gains `test-knowledge-guard`

### What Phase 2 surfaced

- **Arming is an environment variable, and that answers an Implementation Discovery.** The question was
  whether the arming signal can be made *genuinely* unreachable from the agent's tool layer or is only
  *inconvenient* to reach. Answer, by execution (probe at `/tmp/wb-arm-probe`, Claude Code 2.1.195, A/B
  in one session): **a launch-time env var reaches the `PreToolUse` hook, and the agent cannot change
  it.** An `export WB_SELF_EXTENSION=full-auto` run by the agent's own Bash tool executed successfully
  (`now full-auto`) and the hook still saw `interactive` on the next Write — tool-layer processes are
  children and cannot mutate the parent environment the hook inherits. A control run with no variable
  set saw it unset, so the value is genuinely the launch environment's.
  - **The honest limit, since the design's threat model depends on the stronger claim:** unreachable for
    the *running* session, influenceable for a *later* one. `.claude/settings.json` has an `env` block
    applied at session start, so an agent able to write it could arm a future session. Two things bound
    the damage: `.claude/` is in the protected set, and the influence only runs in the safe direction —
    arming a run that was not armed adds friction, it never removes any. The dangerous claim is
    "interactive", and Phase 0 established `ask` degrades to outright refusal in every non-interactive
    mode, so a headless run that successfully claimed interactive would still be refused.

- **The indeterminate case is NOT three-state, and the first implementation got this wrong.** Routing an
  unresolvable path through the same decision as a protected one produced `ask` when armed
  interactively. `design.md`'s non-functional requirement is explicit — "if the hook cannot determine
  whether a path is protected, it denies" — and the reason is substantive: prompting there asks a human
  to approve a write the system itself cannot characterise, which is a rubber stamp wearing a gate's
  clothing. Split into `refuse()` (three-state, protected paths only) and `deny_hard()` (indeterminate,
  no interactive override). The tests caught it.

- **Path matching needs two normalisations composed, not one chosen.** Lexical normalisation catches a
  `..` traversal through a directory that does not exist yet, which no amount of symlink resolution can
  see; symlink resolution catches a link into a protected tree and macOS's `/tmp` → `/private/tmp`.
  Resolving a lexically-normalised path and resolving the raw path can legitimately differ when a
  symlink is followed by `..`, so both results are kept as candidates: protected if *any* candidate
  lands in the set, indeterminate if *any* lands outside the root. Both rules are monotone toward deny,
  so adding a candidate can only make the answer stricter.
  - Found the hard way: the first version required *every* candidate to be inside the root, which broke
    on macOS temp dirs (`/var` → `/private/var`) and denied ordinary unprotected writes. Containment is
    a fact about the resolved path; the lexical form exists for matching, not for containment.

- **A Bash redirect bypasses the guard entirely, confirmed by execution.** `printf 'hello' > d.txt` ran
  through the Bash tool created the file with **no `PreToolUse` Write event** — no log line at all.
  Matching paths inside arbitrary shell strings is unreliable, and a control that fired on
  `grep -r commands/` would train the operator to disarm, which is worse than a named hole. This is the
  same class the deferred CI / CODEOWNERS layer already exists to close, and it moves that layer from
  "before the first unattended run" to "before any armed run is trusted to be bounded". Named in
  `hooks/knowledge-guard.sh`, `scripts/README.md`, and here.

- **A hook timeout fails open.** `.claude-plugin/plugin.json` gives the guard a 10s timeout; a hook that
  produces no output is treated as no opinion, so a timeout reads as inert. The guard makes ~4 `jq`
  calls and no network access, so this is remote — but it is a fail-open in a boundary that is otherwise
  fail-closed, and it should be on the CI layer's list.

- **The probe's own first run was a false green, which is the argument for controls in miniature.** A
  `local name="$1" d="$TMPROOT/$name"` bug (a single `local` expands all its arguments before any of
  them binds) meant the repos were never built — and "the protected sentinel was REFUSED" passed
  *vacuously*, because a file that was never created is indistinguishable from one that was refused.
  The control assertion is what failed and exposed it.

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

- [x] Phase 2 complete — the boundary exists before the loop that writes
- [x] Phase 0 confirmed `Stop`/`SubagentStop` can write reliably

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

- [x] `./scripts/test-knowledge-capture` passes including the concurrency case — **55/55**, and the
      concurrency case runs 8 simultaneous captures and asserts 8 distinct files
- [x] `jq . .claude-plugin/plugin.json` parses
- [x] `./scripts/lint --all` clean
- [x] Re-run under **bash 3.2** with clean stderr, as with the guard

**Manual Verification**

- [x] Running any `/wb:*` command to completion leaves at least one staging entry, with no explicit
      instruction to record — **verified live 2026-07-31 as an A/B.** A child `claude -p` session in a
      configured scratch repo was asked only "What is 2+2?"; a staged entry appeared. The same settings
      in an *unconfigured* repo wrote nothing. The prompt never mentioned recording, which is the whole
      claim: capture does not depend on the agent choosing to record
- [~] Removing the worktree causes a visible, legible failure rather than a silent no-op — **partial.**
      The contract test asserts the hook writes a legible message to stderr AND emits a `systemMessage`
      naming the missing branch. Run live, the failure path executed, but `systemMessage` was not
      observed in `claude -p` output, so whether Claude Code *surfaces* it to a user is unverified.
      This is exactly why `--selfcheck` exists as the deterministic channel; stated rather than assumed
- [x] No capture ever lands in `knowledge/entries/` — asserted in the contract test on every path,
      including under 8-way concurrency, and confirmed in the live run

### Modified Files

- `hooks/knowledge-capture.sh`, `scripts/test-knowledge-capture` — new
- `.claude-plugin/plugin.json` — `Stop` / `SubagentStop` registration
- `commands/validate_execution.md`, `commands/create_handoff.md`, `commands/implement_tasks.md`,
  `commands/implement_coordinated.md` — capture destination named
- `skills/knowledge-store/SKILL.md` — new (**brought forward from Phase 4**; see below)
- `scripts/README.md`, `README.md`, `package.json` — document and wire the new suite

### What Phase 3 surfaced

- **`origin` is enforceable by construction here, not by discipline.** A hook at a turn boundary sees the
  model's *summary*, never a tool's observation, so automatic capture can only ever emit
  `model-narrated` — which the write policy pins to `propose-only`. `hooks/knowledge-capture.sh` contains
  no code path that can emit `tool-verified`, and a test asserts the string does not appear outside
  comments. P3-T6 asked for "origin field discipline"; this is stronger than discipline. `tool-verified`
  is reachable only from the command-level capture points where a verdict actually exists, which is why
  `validate_execution` is the highest-signal of the four.

- **Inert-vs-loud is the same asymmetry Phase 2 used for arming, and it resolves a real tension in the
  design.** design.md requires capture failure to be *visible* ("a no-op capture is worse than no
  capture"), while the risk table requires the plugin never to intrude on repos that have not opted in.
  Both hold once the split is by opt-in: no `.wb-knowledge.json` → completely silent, because there is
  nothing to capture into and a marketplace install must not shout at every user every turn; config
  present but store unreachable → loud, because that repo opted in and its loop is now recording nothing
  while looking like it works.

- **A `Stop` hook must never exit non-zero to signal a problem.** Exit 2 on `Stop` blocks the stop and
  feeds stderr back to the model, which risks a stop-continue-stop loop. Capture always exits 0 and
  surfaces failure on stderr plus a `systemMessage`, with `--selfcheck` as the deterministic channel.
  This constrains Phase 4 too: nothing on the `Stop` path may use exit codes to communicate.

- **Two real bugs, both found by running against the real store rather than only against fixtures.**
  (a) `STORE_ERR="$( { STORE="$(...)"; } 2>&1 )"` runs the inner assignment in a subshell, so `STORE`
  never reached the parent and *every* capture reported the store unreachable — the fixtures passed
  because they exercised the same broken path symmetrically. (b) `--selfcheck` counted
  `staging/README.md` as a captured entry, so an empty store reported as a working one; now counted by
  ID shape, with a regression test. Worth generalising: a health check that counts `*.md` in a directory
  that also holds documentation will lie in the reassuring direction.

- **`skills/knowledge-store/SKILL.md` was brought forward from Phase 4.** P3-T4/T5 would otherwise have
  copied the same ten-line `origin` rule into four command files, and duplicated policy drifting apart is
  the exact failure this project exists to fix — `docs/beads-integration-learnings.md` contradicting
  `CLAUDE.md` is the same shape. design.md already names `skills/model-help` as the precedent for one
  authoritative artifact every command delegates to. The skill currently carries capture conventions
  only; Phase 4 extends it with the curation operations as originally planned.

- **The multi-workspace store resolution works for real, not just in tests.** Running
  `hooks/knowledge-capture.sh --selfcheck` from the `maputo` code-branch workspace resolves the store to
  `kyiv`'s checkout of the store branch. That is the arrangement design.md predicted when it split the
  branches, now exercised end to end rather than argued.

### ⛔ CHECKPOINT: Phase 3 Complete

Confirm staging is accumulating from real work before building the drain. A pass with nothing to curate
cannot be tested meaningfully.

---

## Phase 4: Curation, Promotion, and Invalidation

### Objective

Build the manually-triggerable batched pass that drains staging through a fresh-context reviewer into
promoted entries, plus the git-only staleness sweep.

### Prerequisites

- [x] Phase 3 complete
- [~] staging has real captured content — **NOT met; the maintainer chose to proceed anyway
      2026-07-31.** Consequence, stated rather than glossed: the build and its contract tests are
      fixture-driven, and the checkpoint's end-to-end verification of a real curation pass over real
      captured content is still owed. Nothing about the build depends on it; the *proof that the pass
      discriminates well* does

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

- [x] `./scripts/test-knowledge-sweep` passes, including the undecidable case — **28/28**, covering all
      three routes to undecidable (no cites, no SHA, unknown SHA)
- [x] `./scripts/lint --all` clean
- [x] A sweep over the whole store completes with no model calls — asserted, though see the honesty note
      below about what that assertion is worth
- [x] Re-run under bash 3.2 with clean stderr
- [x] `npm test` green across all six suites — **234 checks**

**Manual Verification**

- [x] A deliberately stale entry (cite a path, then change it) is caught by the sweep — the contract
      test's `suspect-changed`, `suspect-deleted` and `suspect-mixed` fixtures do exactly this
- [ ] `/wb:curate_knowledge` produces a diff for review, and nothing is written to `entries/` until it
      is approved — **owed.** Needs an armed interactive session and real staged content, neither of
      which exists yet
- [ ] The reviewer subagent receives only the candidate, not the authoring context — **owed**, same
      reason. The command specifies it; nothing has executed it
- [ ] Merging two entries that win on different ticket classes is refused by the diversity rule —
      **owed.** This one cannot be automated: it is a judgment the pass makes, and the only test is
      watching a real pass refuse a real merge

### Modified Files

- `scripts/knowledge-sweep`, `scripts/test-knowledge-sweep` — new
- `scripts/knowledge-sync` — new (**added**; P4-T8 needed a home for the on-sync trigger)
- `commands/curate_knowledge.md` — new
- `skills/knowledge-store/SKILL.md` — **extended** (created in Phase 3) with the four curation
  operations, the diversity rule, predictions, and the invalidation commands
- `README.md`, `scripts/README.md`, `package.json` — document and wire the new suite

### What Phase 4 surfaced

- **P4-T3's own wording was wrong, and the collision is load-bearing.** The task says the command "arms
  the guard." It cannot. Phase 2 established by execution that arming lives in the environment of the
  process that *started the session*, precisely so a tool-layer process cannot forge it — and a slash
  command runs inside a session that has already started. So `/wb:curate_knowledge` **verifies** the arm
  and refuses to proceed without it, telling the user to restart with
  `WB_SELF_EXTENSION=interactive claude`. Had this been implemented as written, the command would have
  "armed" itself in a way that either did nothing or, worse, appeared to work — a curation pass that
  believes it is gated and is not.

- **The two-stage proposal shape falls out of the protected set.** `knowledge/entries/` is protected, so
  an armed run's every write there prompts. Twenty prompts in a row is click-through fatigue, which is
  rubber-stamping with extra steps. So the pass writes one **proposal document** to
  `knowledge/proposals/` — deliberately *not* protected, exactly like `staging/` — the human reads it as
  a batch, and only then are named operations applied one prompt at a time. The unprotected proposals
  tree is load-bearing in the same way staging's absence from the set is.

- **The validator assumption holds, with a caveat that changes how it must be used.** Probed by
  execution with a true/false pair citing the same files: the true entry returned PASS 4/4, the false
  one FAIL 0/4 with correct specific corrections. No schema shim needed. **But** on the false entry it
  marked a cited file `PASS` in its *path* table while failing every behavioral claim about it — correct
  per its own rubric, since path existence is not claim accuracy. Curation must therefore read the
  **overall status**, never the per-path table. An entry can cite files that all still exist and be
  entirely wrong.

- **The sweep's `undecidable` verdict is the common case, not the corner case.** Every automatic capture
  from Phase 3 cites nothing, so it lands there. Reporting those `clean` would have been the easy bug —
  nothing cited changed, after all — and it would have laundered "I cannot tell" into "I checked" across
  the majority of the store.

- **`--rebase` is refused rather than merely absent.** `scripts/knowledge-sync` errors on the flag with
  an explanation, because rebasing the store branch rewrites the commits provenance SHAs point at and
  does so *silently, with no error at the moment of damage*. An undocumented option someone reaches for
  anyway is not protection; a refusal that explains itself is.

- **Honesty note on two of the 28 checks.** "Makes no model calls" and "needs no jq" are *negative*
  assertions — verified by execution that they also pass on an empty file. They catch a future
  regression; they do not prove the script works. The other twenty-odd behavioural checks do. Recording
  this because a suite that counts vacuous assertions among its passes overstates its own coverage.

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
  - **Done 2026-07-31, as a SCRIPT rather than as prose in a command.** See "Retrieval moved out of
    markdown" below. `scripts/knowledge-read` + `scripts/test-knowledge-read` (29 checks).
- **P5-T4** — Declare the store as a fifth category in `skills/project-structure/SKILL.md`, whose Quick
  Check currently routes only to research.md / design.md / tasks.md / thoughts/.

### Success Criteria

**Automated Verification**

- [ ] `./scripts/lint --all` clean
- [x] `./scripts/test-knowledge-read` passes — **29/29** (added by the move below)
- [x] ~~`grep -r "knowledge/staging" commands/ skills/` returns no retrieval-path reference~~ —
      **this criterion was wrong and is replaced.** Six files legitimately reference staging today: the
      four Phase 3 capture points *write* there, `curate_knowledge` *drains* it, and the skill documents
      both. As written it fails spuriously, and a criterion that gets waived is worse than none. The
      precise form is the read-path files only:
      `grep -n "knowledge/staging" commands/create_research.md commands/resume_handoff.md` → must be
      empty. The invariant it was reaching for is now enforced mechanically instead — see below.

**Manual Verification** — four of these became automated when retrieval moved into a script

- [x] ~~An irrelevant entry (wrong scope tag) is not surfaced~~ → `test-knowledge-read` asserts it
- [x] ~~No staging content ever appears~~ → asserted three ways: a decoy staged entry matching every
      filter, a source check that no path into the tree is built, and a refused `--staging` flag
- [x] ~~The same run with the worktree removed still completes — degraded, not halted~~ → asserted as
      exit non-zero with empty stdout, plus the caller contract stated
- [ ] A fresh-context run of `/wb:create_research` surfaces a relevant promoted entry — **still owed**,
      and irreducibly so: it needs promoted entries and a real run. What is now testable is that the
      *retrieval* is correct; what is not is that the *command remembers to call it*, which is a grep
      once P5-T1 lands

### Modified Files

- `scripts/knowledge-read`, `scripts/test-knowledge-read` — new (**added**; P5-T3 as a script)
- `commands/create_research.md`, `commands/resume_handoff.md` — read path
- `skills/project-structure/SKILL.md` — fifth category
- `skills/knowledge-store/SKILL.md` — retrieval rules

### Retrieval moved out of markdown — and why that was the point

P5-T3 as written would have put the retrieval rules in `commands/create_research.md` as prose. That
would have made every property of retrieval unverifiable, because **this repo has no way to test
markdown** — the Testing Strategy above says so plainly, and `./scripts/lint` checks formatting only.

Retrieval's failure modes are silent ones: the wrong entries surface, or too many, or ungated ones. A
silent failure with no test is a failure that hides until someone notices research quality quietly got
worse — and negative transfer is *measured* to worsen with store size, so it would look fine at five
entries and rot at two hundred.

So retrieval moved into `scripts/knowledge-read` with a contract test, the same way enforcement, capture
and invalidation already had. This is the general lesson rather than a one-off: **the way to stop
deferring proof in this project is to put less in markdown.** Every property that lives in a script is
testable today; every property that lives in a command is owed until someone runs it by hand.

What is left in markdown shrinks to "does the command call the script", which is a grep. Three of Phase
5's four manual criteria became automated assertions as a direct result, and the fourth is honest about
being irreducible.

Bounding is enforced rather than advised: default limit 5, hard ceiling 25, and the default scope is
`repo:<this repo>` rather than "everything". `--staging` is an **error with an explanation**, not an
absent option — the same shape as `knowledge-sync --rebase`, because an undocumented option someone
reaches for anyway is not protection.

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

- ~~Whether the arming signal can be made genuinely unreachable from the agent's tool layer, or whether
  it is only *inconvenient* to reach.~~ **Answered 2026-07-31 (Phase 2): unreachable for the running
  session, influenceable for a later one.** An env var set at launch reaches the hook and the agent's own
  Bash `export` provably cannot change it, but `.claude/settings.json`'s `env` block could arm a *future*
  session. Bounded by `.claude/` being protected and by the influence only running toward more friction,
  never less. Full detail in "What Phase 2 surfaced".
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
npm install                          # Once per clone — installs ajv (hard dep, dev-time only)
npm test                             # quiet + knowledge-worktree + knowledge-config
./scripts/lint --all                 # Markdown lint
./scripts/test-quiet                 # Existing contract test (regression check)
./scripts/test-knowledge-worktree    # Phase 1
./scripts/test-knowledge-config      # Phase 1 (+ P1-T9 ajv enforcement layer)
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
