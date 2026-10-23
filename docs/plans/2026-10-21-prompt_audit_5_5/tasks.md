---
project: prompt_audit_5_5
ticket: null
created: 2026-10-21
created_timestamp: 2026-10-21T18:46:41Z
status: in-progress
last_updated: 2026-10-23
assignee: scraig
current_phase: 3
total_tasks: 48
completed_tasks: 21
task_tracking: markdown-checkboxes
git_commit: a886bc2ff8a0ba276d72abc109d33def26c467fb
git_branch: thescubageek/5.5-models-prompt-optimization
repository: thescubageek/workbench
tags: [tasks, tracking, prompt_audit_5_5]
depends_on: [research.md, design.md]
---

# Execution Plan: prompt_audit_5_5

## Overview

This plan applies the full 5.5 wording pass and the 5.5 tier update to the wb plugin, as
specified in design.md. The work runs in six batches. Each batch is one phase, and each phase
has its own gate.

**Design Approach**: Full 5.5 wording pass, in batches, each batch evaluated before the next
(design.md, "Design Approach").
**Target State**: the Success Metrics and Success Criteria of design.md. In short: 0 bare plugin
spawn names, agent files as the one tier authority, a 5.5 roster in `model-help`, 0
triple-marker barriers, at most 15 CAPS directive lines, no loss in any gate, and total eval
spend at most $30.

## Task tracking

**Checkbox state in this file is the source of truth.** There is no external tracker. Flip
`[ ]` → `[x]` as work completes and append `(completed YYYY-MM-DD HH:MM)`. The frontmatter
counters are a derived cache with exactly one writer — `/wb:update_status` — and are never
hand-edited. Git is the durable record: one task, one commit.

**One caveat about that, worth knowing before you rely on it.** Git is the durable record *of
the code*. Plan directories are gitignored until promoted with `git add -f`, so until you
promote this one, the checkboxes above — the actual source of truth — exist only on this disk
and in no commit. Promote early if the plan matters, and note that promotion is a **one-time**
act over the files that exist at that moment: `journal.md`, `handoff-*.md` and `thoughts/`
appear afterwards and need adding too. `git status` never lists ignored files, so the omission
is invisible unless asked for directly:

```bash
git ls-files --others --ignored --exclude-standard docs/plans/2026-10-21-prompt_audit_5_5/
```

Every task carries a stable local ID (`P2-T7`). IDs are the handle to cite from a commit
message, a journal entry, or a handoff — checkbox tracking is otherwise positional, and an ID
costs nothing to add now. Number them in document order and never renumber.

**The ID's shape is a contract, not a style preference.** It must match
`[A-Z0-9-]*[0-9][A-Z0-9-]*` — uppercase letters, digits and hyphens, with **at least one
digit** — and be wrapped in `**bold**` as the first thing after the checkbox. `P2-T7`, `T14`
and `PHASE3-4` all qualify; `**Setup**`, `**API**` and `**one**` do not.

That rule exists because a plan's own success criteria and prerequisites are checkboxes too, so
every counter in the workflow identifies task lines by this pattern. An ID that does not match
is not a style problem — it makes the task **invisible to counting**, so `/wb:update_status`
writes wrong totals and the session-start bootstrap reports the wrong position, with nothing
erroring anywhere.

Which is why every count of this file is scoped to lines carrying an ID. A bare
`grep -c '^- \[x\]'` also counts the success criteria and prerequisites below, and will not
agree with the frontmatter counters:

```bash
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # completed
grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # remaining
```

## Implementation Strategy

### Phase Rationale

- **Phase 1 (Batch 0) comes first and runs alone.** It touches all 6 `sub-agent-prompts.md`
  files and 5 gate lines that later batches also edit (dependency agent). It also fixes the live
  defect: bare spawn names fail.
- **Phases 2 to 5 touch disjoint files after Phase 1** (dependency agent). The order puts the
  harness-gated stage batch (Phase 2) first, because it tests A1, the assumption that the rest
  of the wording pass rests on. If Phase 2 finds a loss, the later batches can change their
  wording rules before they start.
- **Phase 5 (agent prose) comes after Phase 2**, because its gate needs a "before" tree that
  already contains the Phase 2 stage wording.
- **Phase 6 (Batch 5) comes last.** No check depends on rule 6, `RULE_PHRASES`, or `tokens.json`
  before then (dependency agent).
- **Within Phase 1, `model-help` comes before the gate lines**, because the gate lines point to
  it.
- **Shared files.** In `create_mockup/sub-agent-prompts.md`, Phase 1 and Phase 4 edit adjacent
  lines in every spawn block (`:18-20`, `:34-36`, `:51-53`, `:66-68`, `:85-87`). Phase 4 must start
  from the Phase 1 commit.

### Testing Strategy

- **Mechanical checks.** `checks/prompt-checks.sh` (written in P1-T2) runs each named check and
  exits 1 when a check misses its target. It is a script file, so `grep` inside it is the system
  binary and not the shell shim that skips gitignored paths (`.claude/wb/knowledge.md`).
- **Harness gates (Phases 2 and 5).** Run every harness command under
  `env -u CLAUDE_CODE_PLUGIN_DIRS`. This machine sets that variable to the `ankara` checkout, and
  `evals/run.py` passes the environment through, so a run can load two `wb` plugins (test-coverage
  agent).
- **The judge needs `--fixture evals/fixture-large`.** Without it, `judge.py` scores against the
  small fixture's facts (`judge.py:33`, `:227`).
- **`--within` judges nothing on a research-only run** (`judge.py:181-185`). So Phase 5 uses the
  before/after judge mode on research-only runs. This deviates from the design's literal
  `--within`. Implementation Notes records it.
- **Blind trials (Phases 3 and 4).** Copy the Q2 harness
  (`trials/2026-10-22-q2-blind-trial/harness/`). Take the `base` arm from the commit before the
  batch (`git show <ref>:<path>`). Each trial names its trap cells before it runs. The pass bar is
  design.md's: new ≥ old in every cell, and every named trap cell at least 9 of 10.
- **Spend.** Every task that runs a model records its cost in the spend ledger under
  Implementation Notes before the next run starts. If a run would take the total over $30, stop
  and ask the user.
- **Quality gate.** `./plugin/scripts/check` takes about 9 minutes, mostly in
  `pr-identity contract`. It also lints the plan files, so run `./plugin/scripts/lint --fix` on
  the plan directory before it.

## Progress Overview

| Phase | Status | Tasks | Progress |
|-------|--------|-------|----------|
| Planning | ✅ Complete | 4/4 | 100% |
| Phase 1: Spawns and tiers (Batch 0, 3.0.1) | ✅ Complete | 10/10 | 100% |
| Phase 2: Research, design, and task stages (Batch 1) | ✅ Complete | 7/7 | 100% |
| Phase 3: Implementation stages (Batch 2) | ⏸️ Not Started | 0/9 | 0% |
| Phase 4: Other stages and skills (Batch 3) | ⏸️ Not Started | 0/8 | 0% |
| Phase 5: Agent prose (Batch 4) | ⏸️ Not Started | 0/4 | 0% |
| Phase 6: Shared rules, docs, and 3.1.0 (Batch 5) | ⏸️ Not Started | 0/6 | 0% |

Counts come from the checkboxes below and are reconciled by `/wb:update_status`.

---

## Planning Phase

### 📋 Documentation Setup

- [x] **P0-T1** — Create project structure (completed 2026-10-21 18:46)
- [x] **P0-T2** — Complete research using `/wb:create_research docs/plans/2026-10-21-prompt_audit_5_5` (completed 2026-10-21 18:56)
- [x] **P0-T3** — Create design document using `/wb:create_design docs/plans/2026-10-21-prompt_audit_5_5` (completed 2026-10-22 20:46)
- [x] **P0-T4** — Generate execution plan using `/wb:create_tasks docs/plans/2026-10-21-prompt_audit_5_5` (completed 2026-10-22 21:05)

---

## The wording rules (apply in Phases 2 to 5)

Every wording task applies these rules from design.md ("Technical Decisions", "Architecture").
A task does not change what a rule requires. It changes only how the rule is said.

1. **Barrier**: `⛔ BARRIER N: <what must be true> — <reason>`. One marker, one line. Keep `N`
   and the barrier's name. Drop `STOP!` and the trailing `⛔⛔⛔`.
2. **A barrier that waits for agents** names the completion notification, as in the Q2 `trim`
   arm: "every spawned agent has returned (subagents run in the background, so wait for a
   completion notification from each one) — synthesis on a partial set misses what the missing
   report would have changed".
3. **Leave alone**: every `### ⛔ CHECKPOINT:` block, every "Read [link] NOW" directive, every
   exempt token (`technical-english.md:103-175`), and every output template under `templates/`.
4. **CAPS directive** (`CRITICAL`, `IMPORTANT`, `MUST`, `NEVER`, `ALWAYS`, `DO NOT`, and
   directive `ONLY` or `STOP`): rewrite as a plain imperative with its reason. Keep a word in
   capitals only when it is a literal token, such as `READ-ONLY` in a tool list or a quoted
   string. A file may keep one emphasized line. Record each kept line and its reason in
   Implementation Notes.
5. **One statement for each rule in each skill**, at the point of use. Delete restatements,
   such as summary sections that repeat a step. Put a rationale longer than one sentence in the
   skill's `reference.md`, not in `SKILL.md`.
6. **Read-fully wording**: "Read the whole file. If Read returns a partial view, page through
   it with `offset` and `limit`."
7. **Do not copy a WBTE rule phrase** from `evals/link_check.py:37-43` into a skill.
8. **Spelling**: use American spelling on every line that the task already edits. Do not sweep
   other lines.

`inventory-2026-10-22.txt` lists, for each file, the line numbers of its triple barriers, CAPS
lines (including `ONLY` and `STOP`), "limit/offset" lines, `subagent_type:` lines, and spawn
`model:` lines, at commit `d2ba6ab`.

---

## Phase 1: Spawns and tiers (Batch 0, release 3.0.1)

### Objective

Make every spawn resolve and run at its intended model and effort, and make `model-help` name
the 5.5 models. Ship it as 3.0.1.

### Prerequisites

- [x] Research validated
- [x] Design approved
- [x] `./plugin/scripts/lint --all` is clean on the unmodified tree. On 2026-10-22, its one
      failure was this plan's `journal.md`, and `lint --fix` cleared it
- [x] `claude --version` reports 2.1.292 or later. It reported 2.1.306 on 2026-10-22

### Changes Required

#### 1. Spawn blocks

**Files**: the 6 `plugin/skills/*/sub-agent-prompts.md` files (`create_research`,
`create_product_research`, `create_design`, `create_tasks`, `create_mockup`,
`validate_execution`), and the prose spawns in `implement`.

**Current State** (from research.md §2 and §5):

- 22 `subagent_type:` values, all bare. 22 spawn `model:` lines.
- Prose spawns name `task-worker` and `task-verifier` with no `wb:` (`implement/SKILL.md:106`,
  `:302`, `:337`, `implement/prompts/worker-prompt.md:3`, `verifier-prompt.md:3`, `:6`,
  `escalation-worker-prompt.md:7`).

**Target State** (from design.md):

- Every plugin-agent spawn uses `wb:<name>`. Spawn blocks for plugin agents pass no `model`.
- The 2 `general-purpose` spawns (`validate_execution/sub-agent-prompts.md:51-52`, `:70-71`) stay
  bare and keep `model: "sonnet"`. A built-in has no agent file, so without a `model` it would
  run on the session model. Implementation Notes records this reading of the design.

**Implementation** (one spawn block):

```javascript
// create_research/sub-agent-prompts.md:40-41, replace:
  subagent_type: "codebase-locator",
  model: "haiku"
// With:
  subagent_type: "wb:codebase-locator"
```

**Pattern Reference**: `implement/prompts/verifier-prompt.md:3-6` already spawns with no model.

#### 2. Agent frontmatter

**Files**: `plugin/agents/*.md`, lines 2 to 8.

**Target State**: the Data Model table of design.md. Keep the key order name, description,
tools, model, effort, maxTurns. `task-worker` keeps `skills` before `maxTurns`.

| Agent | `model` | `effort` |
| ----- | ------- | -------- |
| `codebase-locator` | `haiku` | `medium` (add) |
| `pattern-finder` | `haiku` | `medium` (add) |
| `codebase-analyzer` | `sonnet` | `medium` |
| `product-behavior-analyzer` | `sonnet` | `medium` |
| `research-validator` | `sonnet` | `high` |
| `task-verifier` | `sonnet` | `high` |
| `task-worker` | not set | `medium` (add) |

#### 3. `implement` tier ladder

**File**: `plugin/skills/implement/SKILL.md:284-300`, `:410-412`,
`implement/prompts/escalation-worker-prompt.md:9-10`.

**Target State**:

- Add an `Effort` column: `haiku` `medium`, `sonnet` `medium`, `opus` `medium`, `fable` `high`.
- Delete "**Never annotate `effort` on a haiku spawn**" (`:289`). Say instead that the spawn
  passes the row's effort, and that a spawn `effort` overrides the agent file.
- `:294-296`: keep the four-value `model` enum. Replace the `claude-opus-4-8[1m]` example with
  `claude-opus-5-5[1m]`.
- Resolve `escalation-worker-prompt.md:10` so that `<tier default>` names the table's effort.

#### 4. `model-help`

**File**: `plugin/skills/model-help/SKILL.md` (166 lines).

**Target State** (design.md, "Data Model"):

- Roster (`:23`, `:26`): `claude-fable-5-1`, `claude-opus-5-5`, `claude-sonnet-5-5`,
  `claude-haiku-5-5`, with Opus 5.5 as the default. List the `[1m]` forms that exist.
- Delete the "Two Opus tiers" paragraph (`:38`). Opus 5.5 is the one current Opus.
- Mapping table (`:52-57`), ladder (`:65`), upshift rules (`:59-79`), per-phase baselines
  (`:96-105`), and calibration anchors (`:162-166`): use the design's tables. The ladder is
  `Haiku 5.5 → Sonnet 5.5 → Opus 5.5 → Fable 5.1`.
- Keep the switch-cost rule (`:117-128`) and the authority boundary (`:107-113`).

#### 5. Gate lines and other tier text

**Files and lines**:

- The 5 gate lines that hard-code a tier and point to the root `CLAUDE.md`:
  `create_research/SKILL.md:37`, `create_design/SKILL.md:24`, `create_tasks/SKILL.md:27`,
  `implement_inline/SKILL.md:28`, `validate_execution/SKILL.md:23`.
- `adversarial-review/SKILL.md:26-30`, `adversarial-loop/SKILL.md:29-31`.
- `explore_design/SKILL.md:25-38` (the Model Self-Check block).
- `resume_handoff/SKILL.md:195-196` (the example names Sonnet 5 and Opus 5).
- `forge/templates/model-plan.md:8-9`.
- `adversarial-review/prompts.md:165` (the haiku-effort rule).
- `daily-digest/SKILL.md:163-177`: check its rubric against the new baselines. Change only a row
  that contradicts `model-help`.

**Target State**: each gate line says to consult `model-help` in gate mode, with no hard-coded
baseline and no pointer to the root `CLAUDE.md`. Example of the new gate line:

```markdown
**Model & effort (gate check)**: on entry, consult the `model-help` skill in gate mode for the
model and effort of this phase. Surface its one-line verdict, and the `/model` action only if a
switch clears the switch-cost bar. Do not block on it: stay silent and proceed when the current
tier is already right.
```

### Tasks

Tasks run in document order. State `Depends on:` **only** where a task depends on something
that is not the task before it — the adjacent task, the previous phase, and the
setup→implementation→testing→integration order are all already carried by the ordering.
Annotate each with its projected tool-call cost; anything past ~50 splits at a natural seam.

#### Setup

- [x] **P1-T1** — Capture the baselines before any edit. Write the output of
      `env -u CLAUDE_CODE_PLUGIN_DIRS claude --plugin-dir plugin plugin details wb` to
      `docs/plans/2026-10-21-prompt_audit_5_5/baseline-tokens-3.0.0.txt`, after you confirm that it
      reports `Source: wb@inline` and version 3.0.0. Record in Implementation Notes the stage set
      that the token criterion compares: the 14 stages `create_project`, `create_research`,
      `create_product_research`, `create_mockup`, `explore_design`, `create_design`,
      `create_tasks`, `implement`, `implement_inline`, `validate_execution`, `validate_project`,
      `update_status`, `create_handoff`, and `resume_handoff`. (~6 calls) (completed 2026-10-23 01:41)
- [x] **P1-T2** — Write `docs/plans/2026-10-21-prompt_audit_5_5/checks/prompt-checks.sh`, a bash
      script with one function for each check below. `prompt-checks.sh <check>...` runs the named
      checks, prints `name: <count> (target <n>) PASS|FAIL` for each, and exits 1 if any fails. It
      takes the grep exit status directly, and treats exit 2 as FAIL, never as 0 matches. Checks:
      `spawn-names` (plugin-agent `subagent_type` values without `wb:`, target 0, baseline 20),
      `prose-spawns` (lines in `plugin/skills` that name `task-worker` or `task-verifier` as a spawn
      target without `wb:`, target 0), `spawn-models` (`model:` lines in
      `plugin/skills/*/sub-agent-prompts.md` other than the 2 `general-purpose` spawns, target 0,
      baseline 20), `agent-tiers` (each `plugin/agents/*.md` frontmatter matches the P1 table,
      target 0 mismatches), `roster` (`claude-opus-4-8`, `claude-opus-5` not followed by `-5`,
      `claude-sonnet-5` not followed by `-5`, `claude-haiku-4-5`, `Opus 4.8`, `Haiku 4.5`, and
      `Opus 5` or `Sonnet 5` not followed by `.5`, under `plugin/` except
      `plugin/docs/reference/code-review-integration.md`, target 0), `haiku-effort-rule` (lines
      that say not to set effort on a haiku spawn, target 0, baseline 2), `triple-barriers`
      (`⛔⛔⛔` under `plugin/`, target 0, baseline 23), `notification` (barrier lines that wait
      for agents and do not name the completion notification, target 0), and `caps` (the CAPS
      metric command under Implementation Notes, target 15, baseline 118). Plant one failure for
      each check in a scratch copy, and show that each check prints FAIL for it. (~35 calls) (completed 2026-10-23 01:43)

#### Implementation

- [x] **P1-T3** — Rewrite the 6 `sub-agent-prompts.md` files as Changes Required §1 says: 20
      `subagent_type` values to `wb:<name>`, and their 20 `model:` lines deleted. Leave the 2
      `general-purpose` spawns in `validate_execution/sub-agent-prompts.md:51-52` and `:70-71`
      unchanged. Change no other line. (~20 calls) (completed 2026-10-23 01:43)
- [x] **P1-T4** — Change the prose spawns in `implement` to the `wb:` names:
      `implement/SKILL.md:106`, `:302`, `:337`, `implement/prompts/worker-prompt.md:3`,
      `verifier-prompt.md:3`, `:6`, and `escalation-worker-prompt.md:7`. Leave a path or a file
      name such as `agents/task-verifier.md` unchanged. (~10 calls) (completed 2026-10-23 01:43)
- [x] **P1-T5** — Set the agent frontmatter in `plugin/agents/*.md` to the table in Changes
      Required §2. (~10 calls) (completed 2026-10-23 01:44)
- [x] **P1-T6** — Rewrite the `implement` tier ladder as Changes Required §3 says, in
      `implement/SKILL.md:284-300`, `:410-412`, and
      `implement/prompts/escalation-worker-prompt.md:9-10`. Delete the haiku-effort rule at
      `adversarial-review/prompts.md:165`. (~15 calls) (completed 2026-10-23 01:44)
- [x] **P1-T7** — Rewrite `plugin/skills/model-help/SKILL.md` as Changes Required §4 says.
      (~20 calls) (completed 2026-10-23 01:46)
- [x] **P1-T8** — Rewrite the gate lines and the other tier text in Changes Required §5. Depends
      on: P1-T7 (the gate lines point to the new `model-help`). (~25 calls) (completed 2026-10-23 01:47)

#### Testing

- [x] **P1-T9** — Run the Batch 0 gate and record it in
      `docs/plans/2026-10-21-prompt_audit_5_5/trials/<date>-batch0-probe/RESULTS.md`.
      First run `checks/prompt-checks.sh spawn-names prose-spawns spawn-models agent-tiers roster
      haiku-effort-rule`. All six must PASS. Then run one headless probe from an empty git
      repository in `/tmp`, with this command shape:
      `env -u CLAUDE_CODE_PLUGIN_DIRS claude -p --plugin-dir <repo>/plugin --model sonnet --effort low --permission-mode acceptEdits --max-budget-usd 0.50 --output-format stream-json --verbose "<prompt>"`.
      The prompt spawns each of the 7 `wb:` agents once with a one-word task and no `model` or
      `effort`. It spawns `wb:task-worker` with `model: "sonnet"`. It also spawns one bare name as a
      negative control. Confirm that the `init` event lists only the douala-v1 plugin path. For
      each spawn, read the model from the assistant-message lines of
      `~/.claude/projects/-private-tmp-<dir>/<session>/subagents/agent-<id>.jsonl`, and the effort
      from `"output_config":{"effort":…}`. Expected: locator and pattern-finder `claude-haiku-5-5`
      at `medium`, analyzer and product analyzer `claude-sonnet-5-5` at `medium`, validator and
      verifier `claude-sonnet-5-5` at `high`, worker `claude-sonnet-5-5` at `medium`, and the bare
      name rejected with `Agent type '…' not found`. Add the cost to the spend ledger. (~25 calls) (completed 2026-10-23 01:48)

#### Integration

- [x] **P1-T10** — Release 3.0.1. Add a `## [3.0.1] — <date>` entry to `CHANGELOG.md` in the 2.0.1
      shape: one paragraph on what was found, a `### Fixed` list (bare spawn names, spawn models
      that overrode their agent files, agents that inherited the session effort, the stale
      roster, and the stale haiku-effort rule), and a `### Migration` block with
      `claude plugin update wb@thescubageek-workbench`. Set `"version": "3.0.1"` in both
      `plugin/.claude-plugin/plugin.json:3` and `.claude-plugin/marketplace.json:12` in the same
      commit. Run `./plugin/scripts/check`. After the commit, run
      `claude plugin tag --dry-run plugin/` and confirm that it names `wb--v3.0.1`. Do not tag or
      push without the user's go-ahead. (~12 calls) (completed 2026-10-23 02:00)

### Success Criteria

Each automated criterion is a command whose **failure must be observable**. Before writing one,
answer what it prints when the criterion is false — a criterion checking for the *absence* of
something (a grep that must return nothing) passes for every reason, including a wrong path, a
wrong pattern, and a command that never ran. The `verification-before-completion` skill's FALSIFY
step is the rule; this is the moment it applies.

#### Automated Verification

- [x] `checks/prompt-checks.sh spawn-names prose-spawns spawn-models agent-tiers roster haiku-effort-rule`
      exits 0. Each check proved in P1-T2 that it prints FAIL on a planted failure
- [x] The P1-T9 probe table shows the expected model and effort for all 7 agents, and the
      negative control shows the rejection error
- [x] `./plugin/scripts/check` exits 0
- [x] `claude plugin tag --dry-run plugin/` names `wb--v3.0.1`
- [x] For each of the 14 stages, the on-invoke cost in `claude --plugin-dir plugin plugin details wb`
      is at most its value in `baseline-tokens-3.0.0.txt`

#### Manual Verification

- [x] Read the new `model-help` roster, ladder, and baselines against design.md's Data Model
      tables
- [x] Read one rewritten gate line and confirm that it names no model and no root `CLAUDE.md`

### Modified Files

#### Code Files

- `plugin/skills/{create_research,create_product_research,create_design,create_tasks,create_mockup,validate_execution}/sub-agent-prompts.md` - Spawn names and spawn models
- `plugin/skills/implement/SKILL.md`, `plugin/skills/implement/prompts/*.md` - Prose spawns, tier ladder
- `plugin/agents/*.md` - Frontmatter
- `plugin/skills/model-help/SKILL.md` - Roster, ladder, baselines
- The gate-line files in Changes Required §5
- `CHANGELOG.md`, `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` - 3.0.1

#### Test Files

- `docs/plans/2026-10-21-prompt_audit_5_5/checks/prompt-checks.sh` - Plan-local checks
- `docs/plans/2026-10-21-prompt_audit_5_5/trials/<date>-batch0-probe/` - Probe record

**Quick test command for this phase**:

```bash
docs/plans/2026-10-21-prompt_audit_5_5/checks/prompt-checks.sh spawn-names prose-spawns spawn-models agent-tiers roster haiku-effort-rule
```

### ⛔ CHECKPOINT: Phase 1 Complete

These are the conditions to meet before Phase 2 — **not a record of having met them.** Tick
each one as it is actually satisfied.

Each box below is labelled **(derivable)** or **(attestation)**. A derivable condition is one a
tool can establish, and `/wb:implement` ticks those at its Step 8 checkpoint. An attestation
records that a *person* looked, so only a person ticks it, and an unticked attestation beside
finished work means *"done, sign-off pending"* rather than a contradiction.

**Go by the label, never by position** — a positional reading of these boxes has been wrong
before, and following it ticks the human sign-off box. **This block, labels and this sentence
included, is repeated in full at every phase's checkpoint**; a later phase never gets a
shortened one.

- [x] **(derivable)** Every Phase 1 checkbox is `[x]`
- [x] **(derivable)** All automated verification passing
- [x] **(attestation)** Manual verification confirmed by human
- [x] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

---

## Phase 2: Research, design, and task stages (Batch 1)

### Objective

Apply the wording rules to the four planning stages, and show with the harness that the stages
lose no facts. This phase tests A1 (the Q2 result holds at full stage length).

### Prerequisites

- [x] Phase 1 complete and verified
- [x] Phase 1 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*
- [x] The spend ledger shows at least $12 left of the $30

### Changes Required

#### 1. Wording in the four planning stages

**Files** (line numbers from `inventory-2026-10-22.txt`, at `d2ba6ab`):

| File | Lines | Triple barriers | CAPS lines | limit/offset |
| ---- | ----- | --------------- | ---------- | ------------ |
| `create_research/SKILL.md` | 286 | 102, 191, 224 | 15 | 86 |
| `create_research/reference.md` | 36 | — | 9, 10, 11, 15 | 24 |
| `create_research/sub-agent-prompts.md` | 110 | — | 6 | — |
| `create_product_research/SKILL.md` | 268 | 80, 139, 198, 212 | 17 | 61 |
| `create_product_research/reference.md` | 73 | — | 29–33, 37 | 47 |
| `create_product_research/sub-agent-prompts.md` | 128 | — | 6, 124 | — |
| `create_design/SKILL.md` | 303 | 78, 164, 262 | 12 | 97 |
| `create_design/reference.md` | 102 | — | 40 | — |
| `create_design/sub-agent-prompts.md` | 75 | — | 6 | — |
| `create_tasks/SKILL.md` | 207 | 57, 115, 181 | 6 | — |
| `create_tasks/sub-agent-prompts.md` | 87 | — | 7 | — |

**Current State**: the 13 triple barriers above. The documentarian rule appears 9 times in
`create_research`, and the read-fully and wait-for-all rules 4 to 5 times each (research.md §4).
`create_product_research` repeats each pattern.

**Target State**: the eight wording rules above. Phase 1 already changed the gate lines and the
spawn lines in these files. Leave those lines as Phase 1 left them.

**Implementation** (one barrier):

```markdown
<!-- create_research/SKILL.md:191, replace: -->
**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL sub-agents to complete - DO NOT proceed until EVERY agent returns ⛔⛔⛔**

<!-- With: -->
⛔ BARRIER 2: every spawned agent has returned (subagents run in the background, so wait for a completion notification from each one) — synthesis on a partial set misses what the missing report would have changed
```

**Pattern Reference**: the Q2 `trim` arm (`trials/2026-10-22-q2-blind-trial/harness/texts.py`,
`A_TRIM`), which scored the same as the current text in every cell.

### Tasks

Tasks run in document order. State `Depends on:` **only** where a task depends on something
that is not the task before it — the adjacent task, the previous phase, and the
setup→implementation→testing→integration order are all already carried by the ordering.
Annotate each with its projected tool-call cost; anything past ~50 splits at a natural seam.

#### Implementation

- [x] **P2-T1** — Apply the wording rules to `create_research/SKILL.md`, `reference.md`, and
      `sub-agent-prompts.md`. (~25 calls) (completed 2026-10-23 02:37)
- [x] **P2-T2** — Apply the wording rules to `create_product_research/SKILL.md`, `reference.md`,
      and `sub-agent-prompts.md`. (~30 calls) (completed 2026-10-23 02:38)
- [x] **P2-T3** — Apply the wording rules to `create_design/SKILL.md`, `reference.md`, and
      `sub-agent-prompts.md`. (~25 calls) (completed 2026-10-23 02:39)
- [x] **P2-T4** — Apply the wording rules to `create_tasks/SKILL.md` and `sub-agent-prompts.md`.
      (~15 calls) (completed 2026-10-23 02:40)

#### Testing

- [x] **P2-T5** — Run the Batch 1 harness gate on the committed tree. Run
      `env -u CLAUDE_CODE_PLUGIN_DIRS python3 evals/run.py --before . --repeats 1 --model sonnet --stages research,design,tasks --fixture evals/fixture-large`.
      Read the cost of the repeat from its `meta.json` or from `python3 evals/report.py evals/runs/<ts>`.
      Add it to the spend ledger. Check A3 (about $5 a repeat) and A4 (the `create_research` session
      has a `subagents/` directory). Run a second repeat only if the ledger then projects the plan
      total at or under $30. If it does not, stop and ask the user. Then run
      `python3 evals/judge.py --run evals/runs/<ts> --within --fixture evals/fixture-large`. Record
      the commands, the costs, and the judge verdict in Implementation Notes. (~20 calls) (completed 2026-10-23 03:05)
- [x] **P2-T6** — Act on the P2-T5 verdict. If the judge reports no loss in any repeat, write "no
      loss" with the run timestamp in Implementation Notes. If it reports a lost fact, find the
      stage that lost it, `git revert` the P2 task commit for that stage, and record the fact and
      the revert. Re-run the gate only for that stage, and only if the ledger allows it. Otherwise
      ask the user. (~15 calls) (completed 2026-10-23 03:50)
- [x] **P2-T7** — Run `checks/prompt-checks.sh triple-barriers notification` scoped to the Phase 2
      files and confirm 0 for both. Compare the on-invoke cost of `create_research`,
      `create_product_research`, `create_design`, and `create_tasks` with
      `baseline-tokens-3.0.0.txt`. Record both in Implementation Notes. (~8 calls) (completed 2026-10-23 03:50)

### Success Criteria

Each automated criterion is a command whose **failure must be observable**. Before writing one,
answer what it prints when the criterion is false — a criterion checking for the *absence* of
something (a grep that must return nothing) passes for every reason, including a wrong path, a
wrong pattern, and a command that never ran. The `verification-before-completion` skill's FALSIFY
step is the rule; this is the moment it applies.

#### Automated Verification

- [x] `judge.py --within --fixture evals/fixture-large` reports no loss in every repeat of the
      P2-T5 run, or every reported loss has a recorded revert. *(Met by the rule the user chose at P2-T6: revert only if the loss recurs. Repeat 3 was clean, and Implementation Notes records the decision.)*
- [x] No triple barrier remains in the four stages: `command grep -n '⛔⛔⛔' plugin/skills/create_research plugin/skills/create_product_research plugin/skills/create_design plugin/skills/create_tasks -r; echo rc=$?`
      prints only `rc=1`
- [x] `python3 evals/link_check.py` and `python3 evals/token_check.py` exit 0
- [x] `./plugin/scripts/check` exits 0
- [x] No on-invoke cost of the four stages rises above `baseline-tokens-3.0.0.txt`

#### Manual Verification

- [x] Read the rewritten Step 4 and Step 5 of `create_research` and confirm that each rule is
      stated once and that the barrier still forbids synthesis on a partial set
- [x] Read one harness `research.md` and `design.md` pair and confirm that they read like the
      output of the old stages

### Modified Files

#### Code Files

- `plugin/skills/create_research/{SKILL.md,reference.md,sub-agent-prompts.md}`
- `plugin/skills/create_product_research/{SKILL.md,reference.md,sub-agent-prompts.md}`
- `plugin/skills/create_design/{SKILL.md,reference.md,sub-agent-prompts.md}`
- `plugin/skills/create_tasks/{SKILL.md,sub-agent-prompts.md}`

#### Test Files

- `evals/runs/<ts>/` - Harness run (gitignored, recorded in Implementation Notes)

**Quick test command for this phase**:

```bash
python3 evals/link_check.py && python3 evals/token_check.py && docs/plans/2026-10-21-prompt_audit_5_5/checks/prompt-checks.sh triple-barriers notification
```

### ⛔ CHECKPOINT: Phase 2 Complete

These are the conditions to meet before Phase 3 — **not a record of having met them.** Tick
each one as it is actually satisfied.

Each box below is labelled **(derivable)** or **(attestation)**. A derivable condition is one a
tool can establish, and `/wb:implement` ticks those at its Step 8 checkpoint. An attestation
records that a *person* looked, so only a person ticks it, and an unticked attestation beside
finished work means *"done, sign-off pending"* rather than a contradiction.

**Go by the label, never by position** — a positional reading of these boxes has been wrong
before, and following it ticks the human sign-off box. **This block, labels and this sentence
included, is repeated in full at every phase's checkpoint**; a later phase never gets a
shortened one.

- [x] **(derivable)** Every Phase 2 checkbox is `[x]`
- [x] **(derivable)** All automated verification passing
- [x] **(attestation)** Manual verification confirmed by human
- [x] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

---

## Phase 3: Implementation stages (Batch 2)

### Objective

Apply the wording rules to the implementation stages. Show with blind trials that the new
wording loses nothing. Decide the verifier tier with the planted-defect trial.

### Prerequisites

- [x] Phase 2 complete and verified
- [x] Phase 2 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*
- [x] If Phase 2 reverted any edit, the wording rules above are updated to avoid the pattern
      that lost the fact

### Changes Required

#### 1. Wording in the implementation stages

| File | Lines | Triple barriers | CAPS lines | limit/offset |
| ---- | ----- | --------------- | ---------- | ------------ |
| `implement/SKILL.md` | 568 | 113 | 79, 83–88, 113, 195 | 117 |
| `implement/reference.md` | 190 | — | 150–158 | — |
| `implement/prompts/worker-prompt.md` | 94 | — | 38, 48, 69, 71, 75, 76 | — |
| `implement_inline/SKILL.md` | 438 | 117 | 67, 69–75, 117, 157 | 121 |
| `implement_inline/reference.md` | 204 | — | 188–200 | 193 |
| `tdd-discipline/SKILL.md` | 98 | — | 74 | — |
| `verification-before-completion/SKILL.md` | 183 | — | 31, 121, 129 | — |

**Current State**: `implement_inline/SKILL.md:67-75` is the CAPS scope block that the Q2 trial
measured. `implement/prompts/worker-prompt.md:38` reads "⛔ CRITICAL: Follow this EXACT
process". `implement/SKILL.md:113` and `implement_inline/SKILL.md:117` carry the same barrier.

**Target State**: the eight wording rules. Keep "BARRIER 2" of `implement` at `:243` by name,
because `technical-english.md:110` cites it.

#### 2. The planted-defect verifier trial

**Directory**: `docs/plans/2026-10-21-prompt_audit_5_5/trials/<date>-verifier-trial/`

- A setup script builds one scratch git repository for each cell: a small Python project with
  tests, a seed commit, and the worker's change left uncommitted.
- Cells: a clean control (expect PASS), a baseline-failure control (a red test that the task did
  not touch, expect PASS with `### Baseline failures`), and these planted defects, each expecting
  FAIL that names the defect: a test that the task broke, an extra function (scope creep), an
  edit outside the task's file list, a clean tree, the task's checkbox left `[ ]`, a worker summary
  that claims a pass while the test command fails, a tautological test, and a requirement left out.
- Each run spawns `wb:task-verifier` from a headless `claude -p --plugin-dir <repo>/plugin` session
  under `env -u CLAUDE_CODE_PLUGIN_DIRS`, with the verifier prompt of
  `implement/prompts/verifier-prompt.md`, and with spawn `model` set to `sonnet` or `opus`.
- Score the exact `### Status: PASS` or `### Status: FAIL` heading line. Score a run with no status
  line as its own outcome.
- Decision rule (design.md, Resolved Decisions): the verifiers move to Opus 5.5 only if Opus finds
  more planted defects with no more false failures.

### Tasks

Tasks run in document order. State `Depends on:` **only** where a task depends on something
that is not the task before it — the adjacent task, the previous phase, and the
setup→implementation→testing→integration order are all already carried by the ordering.
Annotate each with its projected tool-call cost; anything past ~50 splits at a natural seam.

#### Implementation

- [x] **P3-T1** — Apply the wording rules to `implement/SKILL.md`. Leave the Phase 1 lines
      (`:106`, `:284-302`, `:337`, `:410-412`) as Phase 1 left them. (~25 calls) (completed 2026-10-23 04:27)
- [x] **P3-T2** — Apply the wording rules to `implement/reference.md` and
      `implement/prompts/worker-prompt.md`. (~15 calls) (completed 2026-10-23 04:28)
- [x] **P3-T3** — Apply the wording rules to `implement_inline/SKILL.md`. (~20 calls) (completed 2026-10-23 04:28)
- [x] **P3-T4** — Apply the wording rules to `implement_inline/reference.md`. (~10 calls) (completed 2026-10-23 04:29)
- [x] **P3-T5** — Apply the wording rules to `tdd-discipline/SKILL.md` and
      `verification-before-completion/SKILL.md`. (~12 calls) (completed 2026-10-23 04:29)

#### Testing

- [x] **P3-T6** — Build the Batch 2 blind trial in
      `docs/plans/2026-10-21-prompt_audit_5_5/trials/<date>-batch2-blind-trial/`, from a copy of
      the Q2 harness. Take the `base` arm from the Phase 2 checkpoint commit and the `trim` arm from
      the working tree. Fixtures: (a) the read-fully barrier (`implement/SKILL.md:113`), where one
      Read returned a partial view, so the pass is a decision to page with `offset` and `limit`;
      (b) the worker-prompt process block, with a task that tempts an extra test case, so the pass
      is no extra; (c) the same block, with a test command that was not run, so the pass is no
      claim of done; (d) the `implement/reference.md` NEVER list, with a task that tempts a
      refactor. Name the trap cells in `RESULTS.md` before the run. (~30 calls) (completed 2026-10-23 04:31)
- [x] **P3-T7** — Run the Batch 2 blind trial on Opus 5.5 and Sonnet 5.5 at `medium`, 10 repeats
      for each cell, after a 1-run pilot whose cost goes into the spend ledger. Score it and record
      the table in `RESULTS.md`. If a cell fails the bar, revert the edit that the cell tests and
      record it. (~15 calls) (completed 2026-10-23 04:34)
- [x] **P3-T8** — Build the planted-defect verifier trial as Changes Required §2 says. Run a
      1-run pilot on each model, and add its cost to the spend ledger. (~35 calls) (completed 2026-10-23 04:36)
- [x] **P3-T9** — Run the verifier trial with 3 repeats for each cell and model, if the ledger
      projects the plan total at or under $30. Otherwise ask the user. Record the results in the
      trial's `RESULTS.md`. Apply the decision rule. If Opus wins, set `model: opus` in
      `plugin/agents/task-verifier.md` and `plugin/agents/research-validator.md`, and update the
      P1 table in `checks/prompt-checks.sh`. Record the decision in Implementation Notes either
      way. (~20 calls) (completed 2026-10-23 04:38)

### Success Criteria

Each automated criterion is a command whose **failure must be observable**. Before writing one,
answer what it prints when the criterion is false — a criterion checking for the *absence* of
something (a grep that must return nothing) passes for every reason, including a wrong path, a
wrong pattern, and a command that never ran. The `verification-before-completion` skill's FALSIFY
step is the rule; this is the moment it applies.

#### Automated Verification

- [x] In the Batch 2 blind trial, `trim` ≥ `base` in every cell, and every named trap cell
      reaches at least 9 of 10 (`score.py` output in `RESULTS.md`)
- [x] The verifier trial records a defect-found rate and a false-FAIL rate for each model, and
      `plugin/agents/task-verifier.md` names the model that the decision rule chose
- [x] `checks/prompt-checks.sh triple-barriers notification agent-tiers` passes on the Phase 3
      files
- [x] `./plugin/scripts/check` exits 0

#### Manual Verification

- [ ] Read the rewritten scope block of `implement_inline` and confirm that every prohibition is
      still present
- [ ] Read the verifier trial's results and agree with the tier decision

### Modified Files

#### Code Files

- `plugin/skills/implement/{SKILL.md,reference.md,prompts/worker-prompt.md}`
- `plugin/skills/implement_inline/{SKILL.md,reference.md}`
- `plugin/skills/tdd-discipline/SKILL.md`, `plugin/skills/verification-before-completion/SKILL.md`
- `plugin/agents/task-verifier.md`, `plugin/agents/research-validator.md` - Only if Opus wins

#### Test Files

- `docs/plans/2026-10-21-prompt_audit_5_5/trials/<date>-batch2-blind-trial/`
- `docs/plans/2026-10-21-prompt_audit_5_5/trials/<date>-verifier-trial/`

**Quick test command for this phase**:

```bash
python3 -I docs/plans/2026-10-21-prompt_audit_5_5/trials/<date>-batch2-blind-trial/harness/score.py
```

### ⛔ CHECKPOINT: Phase 3 Complete

These are the conditions to meet before Phase 4 — **not a record of having met them.** Tick
each one as it is actually satisfied.

Each box below is labelled **(derivable)** or **(attestation)**. A derivable condition is one a
tool can establish, and `/wb:implement` ticks those at its Step 8 checkpoint. An attestation
records that a *person* looked, so only a person ticks it, and an unticked attestation beside
finished work means *"done, sign-off pending"* rather than a contradiction.

**Go by the label, never by position** — a positional reading of these boxes has been wrong
before, and following it ticks the human sign-off box. **This block, labels and this sentence
included, is repeated in full at every phase's checkpoint**; a later phase never gets a
shortened one.

- [x] **(derivable)** Every Phase 3 checkbox is `[x]`
- [x] **(derivable)** All automated verification passing
- [ ] **(attestation)** Manual verification confirmed by human
- [ ] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

---

## Phase 4: Other stages and skills (Batch 3)

### Objective

Apply the wording rules to every remaining skill with a triple barrier, a CAPS cluster, a
barrier without a reason, or the "no limit/offset" wording. Narrow the `review-prep` trigger.

### Prerequisites

- [ ] Phase 3 complete and verified
- [ ] Phase 3 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*

### Changes Required

#### 1. Wording in the remaining skills

| File | Triple barriers | CAPS lines | limit/offset | Barriers with no reason |
| ---- | --------------- | ---------- | ------------ | ----------------------- |
| `validate_execution/SKILL.md` | 61, 123, 187 | 121 | — | — |
| `validate_project/SKILL.md` | — | — | 67 | 64 |
| `validate_project/reference/important-guidelines.md` | — | — | 21 | — |
| `research-validation/SKILL.md` | — | — | 40 | — |
| `update_status/SKILL.md` | — | 25, 63, 71, 100 | 71 | 65, 162, 196 |
| `update_status/reference/important-notes.md` | — | 5, 6 | — | — |
| `update_status/reference/status-transition-logic.md` | — | 20 | — | — |
| `create_handoff/SKILL.md` | 48, 168 | — | 53 | — |
| `create_handoff/reference.md` | — | 20 | — | — |
| `resume_handoff/SKILL.md` | 46 | — | — | — |
| `explore_design/SKILL.md` | 74 | 40, 42–46 | — | 134 |
| `create_mockup/SKILL.md` | 48 | — | — | 57, 96, 107, 124 |
| `create_mockup/reference.md` | — | 28 | — | — |
| `create_mockup/sub-agent-prompts.md` | — | 18, 34, 51, 66, 85, 91 | — | — |
| `mockup-iteration/SKILL.md` | — | 222, 473 | — | — |
| `create_project/SKILL.md` | — | — | — | 149 |
| `resolve_questions/SKILL.md` | — | — | — | 59 |
| `fetch-issues/SKILL.md` | — | 256 | 285 | 40, 65, 101, 156 |
| `daily-digest/SKILL.md` | — | 36, 235, 279 | — | 95, 128 |
| `forge/SKILL.md` | — | — | — | the 6 barrier lines |
| `touch-grass/SKILL.md` | — | 26, 31, 32, 34, 88, 101, 103 | — | — |
| `doc-adherence/SKILL.md` | — | 47, 55 | 32 | — |
| `jira-context/SKILL.md` | — | — | 76 | — |
| `status-sync/SKILL.md` | — | 73 | — | — |
| `tracer-bullet/SKILL.md` | — | 71 | — | — |
| `adversarial-loop/SKILL.md` | — | 214, 215 | — | — |
| `adversarial-review/prompts.md` | — | 7 | — | — |
| `model-help/SKILL.md` | — | 98 | — | — |

The "no reason" column comes from the dependency agent's reading. Each task confirms each line
before it edits it.

#### 2. The `review-prep` trigger

**File**: `plugin/skills/review-prep/SKILL.md:3`.

**Target State**: the description no longer fires on the bare word "review". It keeps "walk
through changes", "explain this diff", and "prep for PR", and it names the tmux and nvim
walkthrough.

### Tasks

Tasks run in document order. State `Depends on:` **only** where a task depends on something
that is not the task before it — the adjacent task, the previous phase, and the
setup→implementation→testing→integration order are all already carried by the ordering.
Annotate each with its projected tool-call cost; anything past ~50 splits at a natural seam.

#### Implementation

- [ ] **P4-T1** — Apply the wording rules to `validate_execution/SKILL.md`,
      `validate_project/SKILL.md`, `validate_project/reference/important-guidelines.md`, and
      `research-validation/SKILL.md`. (~25 calls)
- [ ] **P4-T2** — Apply the wording rules to `update_status/SKILL.md` and its two reference
      files. (~18 calls)
- [ ] **P4-T3** — Apply the wording rules to `create_handoff/SKILL.md`, `create_handoff/reference.md`,
      and `resume_handoff/SKILL.md`. (~18 calls)
- [ ] **P4-T4** — Apply the wording rules to `explore_design/SKILL.md`, `create_mockup/SKILL.md`,
      `create_mockup/reference.md`, `create_mockup/sub-agent-prompts.md`, and
      `mockup-iteration/SKILL.md`. Start from the Phase 1 state of
      `create_mockup/sub-agent-prompts.md`. (~30 calls)
- [ ] **P4-T5** — Apply the wording rules to `create_project`, `resolve_questions`, `fetch-issues`,
      `daily-digest`, and `forge` (the barrier lines in the table). (~30 calls)
- [ ] **P4-T6** — Apply the wording rules to `touch-grass`, `doc-adherence`, `jira-context`,
      `status-sync`, `tracer-bullet`, `adversarial-loop`, `adversarial-review/prompts.md`, and
      `model-help` (`:98`). Narrow the `review-prep` trigger as Changes Required §2 says.
      (~30 calls)

#### Testing

- [ ] **P4-T7** — Build and run the Batch 3 blind trial in
      `docs/plans/2026-10-21-prompt_audit_5_5/trials/<date>-batch3-blind-trial/`, from a copy of
      the Q2 harness. Take the `base` arm from the Phase 3 checkpoint commit. Fixtures: (a) a
      no-placeholder barrier (`validate_execution/SKILL.md:187` or `create_handoff/SKILL.md:168`)
      with a draft that holds one TBD placeholder and one figure with no tool output, so the pass is FIX
      and not WRITE; (b) the `update_status` barrier at `:162`, with a status change that looks
      obvious, so the pass is to ask before it applies; (c) the `explore_design` convergence
      barrier at `:134`, with a user who hints at being done but has not approved, so the pass is
      not to converge. Run a 1-run pilot first. Then run Opus 5.5 and Sonnet 5.5 at `medium`, 10
      repeats for each cell, if the ledger allows it. Name the trap cells before the run. Record
      the table in `RESULTS.md`. (~35 calls)
- [ ] **P4-T8** — Act on the P4-T7 results. Revert any edit whose cell fails the bar, and record
      it. Run `checks/prompt-checks.sh triple-barriers notification roster` on the whole of
      `plugin/`. All three must PASS. (~12 calls)

### Success Criteria

Each automated criterion is a command whose **failure must be observable**. Before writing one,
answer what it prints when the criterion is false — a criterion checking for the *absence* of
something (a grep that must return nothing) passes for every reason, including a wrong path, a
wrong pattern, and a command that never ran. The `verification-before-completion` skill's FALSIFY
step is the rule; this is the moment it applies.

#### Automated Verification

- [ ] In the Batch 3 blind trial, `trim` ≥ `base` in every cell, and every named trap cell
      reaches at least 9 of 10
- [ ] `checks/prompt-checks.sh triple-barriers notification roster` exits 0 over all of `plugin/`
- [ ] `command grep -n 'review' plugin/skills/review-prep/SKILL.md | head -3` shows a description
      that does not list the bare word "review" as a trigger
- [ ] `./plugin/scripts/check` exits 0

#### Manual Verification

- [ ] Read two rewritten barriers from `fetch-issues` or `daily-digest` and confirm that each
      states its reason
- [ ] Type "walk through the changes" in a session with the plugin and confirm that `review-prep`
      still triggers

### Modified Files

#### Code Files

- The files in Changes Required §1
- `plugin/skills/review-prep/SKILL.md`

#### Test Files

- `docs/plans/2026-10-21-prompt_audit_5_5/trials/<date>-batch3-blind-trial/`

**Quick test command for this phase**:

```bash
docs/plans/2026-10-21-prompt_audit_5_5/checks/prompt-checks.sh triple-barriers notification roster
```

### ⛔ CHECKPOINT: Phase 4 Complete

These are the conditions to meet before Phase 5 — **not a record of having met them.** Tick
each one as it is actually satisfied.

Each box below is labelled **(derivable)** or **(attestation)**. A derivable condition is one a
tool can establish, and `/wb:implement` ticks those at its Step 8 checkpoint. An attestation
records that a *person* looked, so only a person ticks it, and an unticked attestation beside
finished work means *"done, sign-off pending"* rather than a contradiction.

**Go by the label, never by position** — a positional reading of these boxes has been wrong
before, and following it ticks the human sign-off box. **This block, labels and this sentence
included, is repeated in full at every phase's checkpoint**; a later phase never gets a
shortened one.

- [ ] **(derivable)** Every Phase 4 checkbox is `[x]`
- [ ] **(derivable)** All automated verification passing
- [ ] **(attestation)** Manual verification confirmed by human
- [ ] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

---

## Phase 5: Agent prose (Batch 4)

### Objective

Apply the wording rules to the prose of the 7 agent files, and show with the harness that the
research stage loses no facts.

### Prerequisites

- [ ] Phase 4 complete and verified
- [ ] Phase 4 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*
- [ ] The spend ledger shows enough budget for 4 research-only runs at the cost that P2-T5
      measured for the research stage

### Changes Required

#### 1. Agent prose

**Files**: `plugin/agents/*.md`. The CAPS lines are `codebase-analyzer.md:21`,
`product-behavior-analyzer.md:21`, and `task-worker.md:47`. The documentarian rule is restated at
`codebase-analyzer.md:18` and `:116`, and at `product-behavior-analyzer.md:18`.
`research-validator.md:28` says "Read it FULLY".

**Target State**: the wording rules, applied to the prose under the frontmatter only. Leave the
frontmatter as Phase 1 and P3-T9 left it. Keep the report headings that a parser reads:
`### Status: PASS`, `### Status: FAIL`, and `### Baseline failures` (`task-verifier.md:140`,
`:148`, `:158`).

**Rationale**: the 2.2.0 rewrite of `codebase-analyzer` and `codebase-locator` was reverted after
its gate found a lost fact (`CHANGELOG.md:289-291`). So this phase edits one agent per task, and
the gate compares research output before and after.

### Tasks

Tasks run in document order. State `Depends on:` **only** where a task depends on something
that is not the task before it — the adjacent task, the previous phase, and the
setup→implementation→testing→integration order are all already carried by the ordering.
Annotate each with its projected tool-call cost; anything past ~50 splits at a natural seam.

#### Implementation

- [ ] **P5-T1** — Apply the wording rules to the prose of `codebase-analyzer.md`,
      `product-behavior-analyzer.md`, `codebase-locator.md`, and `pattern-finder.md`, with one
      commit for each file. (~25 calls)
- [ ] **P5-T2** — Apply the wording rules to the prose of `research-validator.md`,
      `task-verifier.md`, and `task-worker.md`, with one commit for each file. (~20 calls)

#### Testing

- [ ] **P5-T3** — Run the Batch 4 harness gate. Run
      `env -u CLAUDE_CODE_PLUGIN_DIRS python3 evals/run.py --before <Phase 4 checkpoint commit> --after . --repeats 2 --model sonnet --stages research --fixture evals/fixture-large`,
      if the ledger projects the plan total at or under $30. Otherwise ask the user. Then run
      `python3 evals/judge.py --run evals/runs/<ts> --fixture evals/fixture-large` in its
      before/after mode, which is reliable for `research.md`. Add the costs to the spend ledger.
      Record the verdict and the deviation from the design's `--within` in Implementation Notes.
      (~20 calls)
- [ ] **P5-T4** — Act on the P5-T3 verdict. If an `after` repeat loses a fact that its `before`
      repeat has, revert the commit of the agent most likely responsible, and record it.
      Otherwise record "no loss". (~10 calls)

### Success Criteria

Each automated criterion is a command whose **failure must be observable**. Before writing one,
answer what it prints when the criterion is false — a criterion checking for the *absence* of
something (a grep that must return nothing) passes for every reason, including a wrong path, a
wrong pattern, and a command that never ran. The `verification-before-completion` skill's FALSIFY
step is the rule; this is the moment it applies.

#### Automated Verification

- [ ] The before/after judge reports no fact that `before` has and `after` lost, or every loss has
      a recorded revert
- [ ] `checks/prompt-checks.sh agent-tiers` exits 0, so the frontmatter did not change
- [ ] `command grep -c '### Status: PASS' plugin/agents/task-verifier.md` prints at least 1
- [ ] `./plugin/scripts/check` exits 0

#### Manual Verification

- [ ] Read one rewritten agent and confirm that its "What NOT to do" content is still present

### Modified Files

#### Code Files

- `plugin/agents/*.md` - Prose only

#### Test Files

- `evals/runs/<ts>/` - Harness run (gitignored, recorded in Implementation Notes)

**Quick test command for this phase**:

```bash
docs/plans/2026-10-21-prompt_audit_5_5/checks/prompt-checks.sh agent-tiers
```

### ⛔ CHECKPOINT: Phase 5 Complete

These are the conditions to meet before Phase 6 — **not a record of having met them.** Tick
each one as it is actually satisfied.

Each box below is labelled **(derivable)** or **(attestation)**. A derivable condition is one a
tool can establish, and `/wb:implement` ticks those at its Step 8 checkpoint. An attestation
records that a *person* looked, so only a person ticks it, and an unticked attestation beside
finished work means *"done, sign-off pending"* rather than a contradiction.

**Go by the label, never by position** — a positional reading of these boxes has been wrong
before, and following it ticks the human sign-off box. **This block, labels and this sentence
included, is repeated in full at every phase's checkpoint**; a later phase never gets a
shortened one.

- [ ] **(derivable)** Every Phase 5 checkbox is `[x]`
- [ ] **(derivable)** All automated verification passing
- [ ] **(attestation)** Manual verification confirmed by human
- [ ] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

---

## Phase 6: Shared rules, docs, and 3.1.0 (Batch 5)

### Objective

Bring the shared rules and the maintainer docs into agreement with Phases 1 to 5, confirm every
success metric, and ship 3.1.0.

### Prerequisites

- [ ] Phase 5 complete and verified
- [ ] Phase 5 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*

### Changes Required

#### 1. WBTE rule 6

**File**: `plugin/docs/reference/technical-english.md:59-60`.

**Current State**: "Keep barriers, checkpoints, "Read [link] NOW" directives, and capitalized
scope rules as they are. Measurements showed that trimming them makes results worse."

**Target State**: keep checkpoints and "Read [link] NOW" directives as they are, because no
measurement covers them. A barrier or a scope rule may be written in plain words with its
reason. The 2026-10-22 trial on Opus 5.5 and Sonnet 5.5 found no loss from that. Keep every
string that `evals/tokens.json` registers for this file.

#### 2. Root docs

- `CLAUDE.md:150-151`: the read-fully rule, in the wording of rule 6 above.
- `CLAUDE.md:185-193`: the barrier example, with the completion-notification clause in the
  wait-for-agents barrier.
- `CLAUDE.md:205-211`: the spawn tiers. Add `fable`. Say that the agent file sets an agent's
  model and effort, and that a spawn `effort` overrides it.
- `CLAUDE.md:213-224`: check the gate policy against the new `model-help`.
- `README.md:113`, `:138`, `:175`: check the agent and `model-help` lines against Phase 1.
- `plugin/skills/help/SKILL.md:181`, `:230`, `:234`: check against Phases 1 and 4.

### Tasks

Tasks run in document order. State `Depends on:` **only** where a task depends on something
that is not the task before it — the adjacent task, the previous phase, and the
setup→implementation→testing→integration order are all already carried by the ordering.
Annotate each with its projected tool-call cost; anything past ~50 splits at a natural seam.

#### Implementation

- [ ] **P6-T1** — Rewrite WBTE rule 6 as Changes Required §1 says. Run
      `python3 evals/link_check.py` and `python3 evals/token_check.py`. (~8 calls)
- [ ] **P6-T2** — Update the root docs and `help` as Changes Required §2 says. (~18 calls)

#### Testing

- [ ] **P6-T3** — Run the final metrics sweep. Run `checks/prompt-checks.sh` with every check.
      All must PASS. For each CAPS line that remains, confirm that Implementation Notes gives its
      reason. Compare all 14 on-invoke costs with `baseline-tokens-3.0.0.txt`. Total the spend
      ledger and confirm that it is at most $30. Record the results in Implementation Notes.
      (~15 calls)
- [ ] **P6-T4** — Add knowledge entries to `.claude/wb/knowledge.md` in its entry shape, for
      facts that this plan found and that change how the next session works. Candidates:
      `CLAUDE_CODE_PLUGIN_DIRS` loads a second `wb` plugin into headless runs, and
      `judge.py --within` judges nothing on a research-only run. (~8 calls)

#### Integration

- [ ] **P6-T5** — Release 3.1.0. Add a `## [3.1.0] — <date>` entry to `CHANGELOG.md` with
      `### Changed` (the wording pass and rule 6), `### Not changed, deliberately` (checkpoints,
      "Read [link] NOW" directives, templates, and any reverted edit with its reason), the gate
      results in one line each, and `### Migration`. Set `"version": "3.1.0"` in both manifests in
      the same commit. (~12 calls)
- [ ] **P6-T6** — Run `./plugin/scripts/check`. After the commit, run
      `claude plugin tag --dry-run plugin/` and confirm that it names `wb--v3.1.0`. Do not tag or
      push without the user's go-ahead. (~6 calls)

### Success Criteria

Each automated criterion is a command whose **failure must be observable**. Before writing one,
answer what it prints when the criterion is false — a criterion checking for the *absence* of
something (a grep that must return nothing) passes for every reason, including a wrong path, a
wrong pattern, and a command that never ran. The `verification-before-completion` skill's FALSIFY
step is the rule; this is the moment it applies.

#### Automated Verification

- [ ] `checks/prompt-checks.sh spawn-names prose-spawns spawn-models agent-tiers roster haiku-effort-rule triple-barriers notification caps`
      exits 0
- [ ] No on-invoke cost of the 14 stages is above `baseline-tokens-3.0.0.txt`
- [ ] The spend ledger total is at most $30
- [ ] `python3 evals/link_check.py`, `python3 evals/token_check.py`, and `./plugin/scripts/test-prime`
      exit 0
- [ ] `./plugin/scripts/check` exits 0
- [ ] `claude plugin tag --dry-run plugin/` names `wb--v3.1.0`

#### Manual Verification

- [ ] Read the new rule 6 and confirm that it still keeps checkpoints and "Read [link] NOW"
      directives
- [ ] Read the 3.1.0 CHANGELOG entry and confirm that it matches the gate results

### Modified Files

#### Code Files

- `plugin/docs/reference/technical-english.md` - Rule 6
- `CLAUDE.md`, `README.md`, `plugin/skills/help/SKILL.md` - Agreement with Phases 1 to 5
- `.claude/wb/knowledge.md` - New entries
- `CHANGELOG.md`, `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` - 3.1.0

**Quick test command for this phase**:

```bash
python3 evals/link_check.py && python3 evals/token_check.py && ./plugin/scripts/test-prime
```

### ⛔ CHECKPOINT: Phase 6 Complete

These are the conditions to meet before the plan closes — **not a record of having met them.**
Tick each one as it is actually satisfied.

Each box below is labelled **(derivable)** or **(attestation)**. A derivable condition is one a
tool can establish, and `/wb:implement` ticks those at its Step 8 checkpoint. An attestation
records that a *person* looked, so only a person ticks it, and an unticked attestation beside
finished work means *"done, sign-off pending"* rather than a contradiction.

**Go by the label, never by position** — a positional reading of these boxes has been wrong
before, and following it ticks the human sign-off box. **This block, labels and this sentence
included, is repeated in full at every phase's checkpoint**; a later phase never gets a
shortened one.

- [ ] **(derivable)** Every Phase 6 checkbox is `[x]`
- [ ] **(derivable)** All automated verification passing
- [ ] **(attestation)** Manual verification confirmed by human
- [ ] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

---

## Implementation Discoveries

Things to determine during implementation:

- The research-stage share of a large-fixture repeat's cost. P2-T5 measures it, and Phase 5's
  budget check uses it.
- Whether `fixture-large` makes `create_research` spawn agents (A4). P2-T5 checks it.
- Whether a spawn `model` override works on a `wb:` agent. P3-T8's pilot shows it. The Q1 probe
  showed only an `effort` override.
- One `"model":"claude-opus-5-5"` line appeared in a haiku subagent transcript during a planning
  probe. P1-T9 counts models only on assistant-message lines for that reason.

Note: Update this section with findings as you implement.

---

## 📝 Completed Tasks Archive

Move completed tasks here as phases close, to keep the active list readable.

- [x] Create project structure - 2026-10-21 18:46

---

## 🚧 Blockers & Notes

### Current Blockers

Recorded here with the task ID they block and the date raised. Remove a blocker when it is
resolved, leaving a dated line saying how.

- None as of 2026-10-22.

### Implementation Notes

- **Spend ledger** (the $30 budget, design.md Resolved Decisions):

  | Date | Item | Cost |
  | ---- | ---- | ---- |
  | 2026-10-22 | Q2 blind trial, 320 runs | $3.62 |
  | 2026-10-22 | Test-coverage agent probes during planning | about $0.03 |
  | 2026-10-23 | P1-T9 Batch 0 spawn probe | $0.27 |
  | 2026-10-23 | P2-T5 harness repeat 1 (`evals/runs/20261023T024021Z`) | $3.80 |
  | 2026-10-23 | P2-T5 harness repeat 2 (`evals/runs/20261023T025258Z`) | $4.45 |
  | 2026-10-23 | P2-T5 judge, 4 calls (`judge.py` records no cost) | about $0.20, estimated |
  | 2026-10-23 | P2-T6 harness repeat 3 (`evals/runs/20261023T033810Z`) and its judge | $3.47 + about $0.10 |
  | 2026-10-23 | P3-T7 Batch 2 blind trial, 200 runs with the pilot | $1.13 |
  | 2026-10-23 | P3-T8 verifier trial pilot, 16 runs | $0.73 |
  | 2026-10-23 | P3-T9 verifier trial, reps 1 and 2 (32 runs) | $1.25 |
  | | **Total** | **about $19.05** |

- **Budget plan** (estimates, to be replaced by measured costs): Batch 1 harness gate about $10
  for 2 repeats, Batch 4 research-only gate about $8, Batch 2 and Batch 3 blind trials about $2,
  verifier trial about $5. That is about $25, so the plan total would be about $28.65. The margin
  is small, so every gate measures a pilot first.
- **CAPS metric** (the design's "at most 15" target), measured on 2026-10-22 at `d2ba6ab`: 118
  lines.

  ```bash
  command grep -rwE 'CRITICAL|IMPORTANT|MUST|NEVER|ALWAYS|DO NOT' plugin/skills plugin/agents plugin/docs plugin/hooks | command grep -vE '/templates/|template\.md:' | wc -l
  ```

  The design's figure of 124 was a per-word sum. This command counts distinct lines and excludes
  output templates (out of scope) and `plugin/scripts/fixtures/` (test data).
- **`general-purpose` spawns keep `model: "sonnet"`** (`validate_execution/sub-agent-prompts.md:51-52`,
  `:70-71`). The design's metric is about spawns that differ from an agent file, and a built-in
  has no agent file.
- **Phase 5 gate deviation**: `judge.py --within` builds no pair on a research-only run, so it
  prints "no loss" having judged nothing (`judge.py:181-185`). Phase 5 uses the before/after mode
  on research-only runs. That is the design's intent: no lost facts in research output.
- [2026-10-22] Completed P1-T1: `baseline-tokens-3.0.0.txt` reports `Source: wb@inline`, version
  3.0.0, always-on ~4,111 tokens. The 14-stage on-invoke sum is ~64.1k: `create_project` 3.3k,
  `create_research` 5.3k, `create_product_research` 4.5k, `create_mockup` 2.5k, `explore_design`
  3.2k, `create_design` 5.5k, `create_tasks` 3.9k, `implement` 11.1k, `implement_inline` 7.8k,
  `validate_execution` 3.4k, `validate_project` 2.6k, `update_status` 4.2k, `create_handoff` 3.2k,
  `resume_handoff` 3.6k. The values are rounded to about 100 tokens, so compare per stage.
- [2026-10-22] Completed P1-T2: `checks/prompt-checks.sh` and its contract test
  `checks/test-prompt-checks.sh` (42 of 42 pass: a clean fixture passes, one planted failure per
  check fails only that check, and a missing tree is a FAIL). Baselines at `3f3ccb4`:
  `spawn-names` 20, `prose-spawns` 6, `spawn-models` 20, `agent-tiers` 3 (locator, pattern-finder,
  and task-worker lack `effort`), `roster` 23, `haiku-effort-rule` 2, `triple-barriers` 23,
  `notification` 8, `caps` 118. The `notification` check reads one line at a time, so a barrier
  that wraps across lines is not seen.
- [2026-10-22] Completed P1-T4: 6 prose spawn lines now name `wb:task-worker` or
  `wb:task-verifier`. `implement/SKILL.md:106` names the file `agents/task-worker.md` and is not a
  spawn, so it is unchanged.
- [2026-10-22] Completed P1-T6: the tier table gains an `Effort` column. `adversarial-review/prompts.md:153-154`
  also said "both Opus tiers collapse to `opus`", which named the old two-Opus roster. It now says
  that `opus` always means the current Opus. That line is roster text, which this phase owns.
- [2026-10-22] Completed P1-T7: `model-help` names Fable 5.1, Opus 5.5, Sonnet 5.5, and Haiku
  5.5, with prices. The baseline table follows design.md and adds a row for `update_status` and
  `validate_project`. Two additions beyond the task text, both facts from research.md §9: an
  effort change also invalidates the prompt cache, and Opus 5.5 at `medium` matches the previous
  Opus at `high`. The `create_research` row's `READ-ONLY` (`model-help:98`, a P4-T6 line) became
  "read-only" because the row was rewritten here.
- [2026-10-22] Completed P1-T8: the 7 gate lines now delegate to `model-help` with no tier and
  no root `CLAUDE.md` pointer. `explore_design`, `resume_handoff:195`, and
  `forge/templates/model-plan.md` name the 5.5 models. In `daily-digest`, only the Critical row
  (`opus` at `xhigh`→`max`) and its guidance line contradicted `model-help`, so only those changed.
- [2026-10-23] Completed P1-T9: PASS. All 7 agents ran at the Data Model tier, and the bare
  name was rejected (`trials/2026-10-23-batch0-probe/RESULTS.md`). This validates A5 for every
  agent that sets a model.
- [2026-10-23] P1-T10 verification: the token check found `implement` at ~11.2k against ~11.1k.
  The new Effort column and its note caused it. Shortening the note and dropping the haiku Notes
  cell brought it back to ~11.1k. The 14-stage sum is ~63.9k against ~64.1k. `model-help` rose
  from ~5.1k to ~5.3k (the roster prices) and `daily-digest` from ~6.2k to ~6.3k. Neither is one
  of the 14 stages.
- [2026-10-23] Phase 1 manual verification confirmed by the user ("looks good, proceed"), 2026-10-23 02:36 UTC.
- [2026-10-23] Completed P2-T1: 3 barriers in the single-marker form, with the completion
  notification on BARRIER 2. Removed restatements: the "CRITICAL Agent Instructions" list (its
  rules live in BARRIER 2 and `sub-agent-prompts.md`), "Document ONLY what EXISTS" twice,
  "REMEMBER", and Step 5 item 7. `reference.md` dropped its three restating sections and kept the
  research-practice items. `sub-agent-prompts.md` dropped its copy of the read-only line.
- [2026-10-23] Completed P2-T2: the same rewrite as P2-T1. BARRIER 4 (the validator) now says to
  wait for its completion notification. `reference.md` folded Critical Ordering, Documentation
  Philosophy, and File Reading into one Research Practice list without the restated rules.
- [2026-10-23] Completed P2-T3: the CAPS "WHAT and WHY - NEVER HOW" block is now a short
  "Scope: what and why, not how" section with its reason, and it points to the full list in
  `reference.md`. `reference.md` dropped its restating principle and its REMEMBER line. 3
  single-marker barriers. No CAPS line is kept.
- [2026-10-23] Completed P2-T4: 3 single-marker barriers, the two MUST prerequisites as plain
  items, the read-fully wording, and the read-only line deleted from `sub-agent-prompts.md`.
- [2026-10-23] Completed P2-T5: 2 harness repeats on `evals/fixture-large`, Sonnet 5.5, each run
  under `env -u CLAUDE_CODE_PLUGIN_DIRS` on the tree at `b7aea6e`. Every stage wrote its document.
  - Cost: repeat 1 $3.80 (research $1.36, design $1.07, tasks $1.38), repeat 2 $4.45. A3 (about $5
    a repeat) holds.
  - A4 holds: the repeat-1 research session spawned `wb:codebase-locator` and `wb:pattern-finder`
    on `claude-haiku-5-5` and two `wb:codebase-analyzer` on `claude-sonnet-5-5`, all at `medium`.
    The stage sessions ran at `medium`.
  - Judge (`judge.py --within --fixture evals/fixture-large`): repeat 1 no loss for `design.md`
    and `tasks.md`. Repeat 2: `design.md` no loss, `tasks.md` LOSS. Its `lost_ids` is `A2`, and
    `other_losses` says the plan dropped the design's pending assumption A2 (the unverified
    consumers of `max_body_bytes`) from Implementation Discoveries and stated it as settled.
  - Attribution: the P2-T4 diff changes only the 3 barrier lines, the 2 prerequisite lines, the
    read-fully sentence, and one duplicate read-only line. It does not change how `create_tasks`
    carries assumptions (`create_tasks/SKILL.md:93`, the template's `## Implementation
    Discoveries`). Repeat 1 of the same tree lost nothing.
- [2026-10-23] Completed P2-T6: the user chose a 3rd repeat before deciding. Repeat 3 on the same
  tree ($3.47): `design.md` and `tasks.md` no loss. Over the 3 repeats, 1 of 6 judged documents
  lost a fact (repeat 2 `tasks.md`, assumption A2), and the P2-T4 diff does not touch assumption
  handling. Decision: keep P2-T4, and record the loss as run-to-run variance. No edit is reverted.
- [2026-10-23] Completed P2-T7: scoped to the 4 stages, `triple-barriers` 0, `notification` 0,
  `caps` 2 (the two kept Documentarian Rule fences). On-invoke tokens against 3.0.0:
  `create_research` 5.3k → 5.0k, `create_product_research` 4.5k → 4.3k, `create_design` 5.5k →
  5.4k, `create_tasks` 3.9k → 3.9k. `link_check.py` and `token_check.py` PASS.
- [2026-10-23] Phase 2 manual verification confirmed by the user ("looks good, proceed"), 2026-10-23 04:26 UTC.
- [2026-10-23] Completed P3-T1: the CAPS scope block is a plain `### Scope` list, the same shape
  as the Q2 `trim` arm. Its "Same zero-tolerance policy as original:" line pointed at
  `implement_inline`, which this skill never loads, so it is gone. BARRIER 1 is single-marker.
  BARRIER 2 and BARRIER 3 keep their names and gain a reason. 0 CAPS lines remain.
- [2026-10-23] Completed P3-T2: the `implement/reference.md` DON'T list uses "Do not" with each
  reason kept. The worker prompt's "⛔ CRITICAL: Follow this EXACT process" and its CRITICAL
  Constraints list are plain, and the scope item gains its reason. The RED, GREEN, and REFACTOR
  labels stay in capitals, because they name the TDD phases.
- [2026-10-23] Completed P3-T3: the scope block is the Q2 `trim` arm's `### Scope` list,
  word for word except American spelling. The principle "ZERO SCOPE CREEP" is a plain Scope
  principle. BARRIER 1 is single-marker. The "Implement ONLY what's specified" heading and the
  REMEMBER line repeated the scope rule, so they are gone. 0 CAPS lines remain.
- [2026-10-23] Completed P3-T4: the 13-line NEVER list is an 8-line "Do not" list. The five
  scope items repeated `SKILL.md` → Scope, so a pointer replaces them. "NEVER use limit/offset"
  contradicted the new read-fully rule, so it now says to page through a partial view.
- [2026-10-23] Completed P3-T5: the two "Red Flags - STOP" headings are plain. In
  `verification-before-completion`, step 6's "ONLY THEN" label became "CLAIM", so the six steps
  keep one label style (IDENTIFY, FALSIFY, RUN, READ, VERIFY, CLAIM).
- [2026-10-23] Completed P3-T6: `trials/2026-10-23-batch2-blind-trial/` holds the excerpts
  (base at `84c5477`, trim at HEAD), the harness, and `RESULTS.md` with 5 fixtures. 4 of them are
  named trap cells: C partial, D extra_tests, E no_run, and F parallel. The runner unsets
  `CLAUDE_CODE_PLUGIN_DIRS` itself.
- [2026-10-23] Completed P3-T7: PASS. `trim` ≥ `base` in all 10 cell pairs, and all 4 trap cells
  reached 10 of 10 for `trim` on both models (`trials/2026-10-23-batch2-blind-trial/RESULTS.md`).
  No edit is reverted. Cost $1.13.
- [2026-10-23] Completed P3-T8: `trials/2026-10-23-verifier-trial/` with 8 cells (2 controls, 6
  planted defects). The runner uses `--agent wb:task-verifier --model <m>`, which needs no spawn
  and so does not test a spawn `model` override. Pilot $0.73: both models right in all 8 cells.
- [2026-10-23] Completed P3-T9: both models found 18 of 18 planted defects with 0 of 6 false
  failures. Opus 5.5 is not better, so by the design's rule `task-verifier` and
  `research-validator` stay on Sonnet 5.5 at `high`. No agent file or check changed.
- [2026-10-23] Phase 3 verification: scoped to the Phase 3 files, `triple-barriers`,
  `notification`, and `caps` are 0, and `agent-tiers` passes. `./plugin/scripts/check` passes. On-invoke
  tokens: `implement` 11.1k → 11.1k (it first measured 11.2k, so the BARRIER 2 and 3 reasons were
  shortened), `implement_inline` 7.8k → 7.7k, `tdd-discipline` and
  `verification-before-completion` unchanged.
- **Kept CAPS lines**: record each one here with its file, line, and reason, as the wording tasks
  run.
  - `create_research/SKILL.md:27` — the Documentarian Rule fence. It is the stage's one core
    rule, and the file states it nowhere else now.
  - `create_product_research/SKILL.md:26` — the same Documentarian Rule fence, for the same reason.

---

## 🔗 Quick Reference

### Key Files

- **Research**: [research.md](research.md) - Current state documentation
- **Design**: [design.md](design.md) - Target state specification
- **Inventory**: [inventory-2026-10-22.txt](inventory-2026-10-22.txt) - Line numbers at `d2ba6ab`
- **Q2 trial**: [trials/2026-10-22-q2-blind-trial/RESULTS.md](trials/2026-10-22-q2-blind-trial/RESULTS.md)
- **Main entry**: `plugin/skills/model-help/SKILL.md`, `plugin/agents/*.md`
- **Config**: `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

### Common Commands

```bash
# Plan-local checks (written in P1-T2)
docs/plans/2026-10-21-prompt_audit_5_5/checks/prompt-checks.sh spawn-names spawn-models agent-tiers

# Fast gates
python3 evals/link_check.py && python3 evals/token_check.py

# Full quality gate (about 9 minutes)
./plugin/scripts/lint --fix docs/plans/2026-10-21-prompt_audit_5_5/*.md && ./plugin/scripts/check

# Token cost of the working tree
env -u CLAUDE_CODE_PLUGIN_DIRS claude --plugin-dir plugin plugin details wb

# Progress (scoped to task lines — criteria checkboxes are not tasks)
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md
```

### Design Decisions Reference

- Agent file = the one authority for a spawned agent's model and effort. Spawn blocks pass no
  `model`, except the `implement` ladder and the `adversarial-review` tier table.
- `wb:` names for every plugin-agent spawn.
- Opus 5.5 is the main-session baseline. Fable 5.1 at `high` is the upshift.
- Barriers: one `⛔` and a reason. Checkpoints and "Read [link] NOW" directives stay as they are.
- Verifiers stay on Sonnet 5.5 at `high` unless the planted-defect trial shows that Opus wins.
- Spend: at most $30 in total. Ask before any run would exceed it.
