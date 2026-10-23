---
project: prompt_audit_5_5
ticket: null
created: 2026-10-21
created_timestamp: 2026-10-21T18:46:41Z
status: approved
last_updated: 2026-10-23
designer: scraig
git_commit: d8097d329fa43ba63b2e78b21099bdd70baa5d7a
git_branch: thescubageek/5.5-models-prompt-optimization
repository: thescubageek/workbench
tags: [design, architecture, prompt_audit_5_5]
depends_on: research.md
design_approach: Full 5.5 wording pass, in batches, each batch evaluated before the next
---

# Design: prompt_audit_5_5

**Created**: 2026-10-21 18:46 UTC
**Designer**: scraig
**Ticket**: N/A

<!-- The status is only in the frontmatter `status:` field. Do not repeat it here.
     /wb:create_tasks and forge read that field, and it changes. A second copy is out of
     date as soon as the design is approved. `created` and `ticket` are repeated above,
     because they do not change after creation. -->

## Problem Statement

The wb plugin's prompts were written for the Claude 4.x and 5.0 models. The plugin now runs on
the 5.5 models, because the aliases resolve to them (research §"Summary"). Three kinds of
problem follow.

1. **A live defect.** Every one of the 22 `subagent_type:` values in the spawn blocks is a bare
   name, and the Agent tool rejects a bare name (research §5). A stage that copies its spawn
   block verbatim gets an error.
2. **Stale model advice.** `model-help` names Opus 5, Opus 4.8, Sonnet 5, and Haiku 4.5
   (`model-help/SKILL.md:23`, `:65`). Agents with no `effort` inherit the session's effort, so
   the `haiku` locator ran at `high` on 2026-10-21 (research, Follow-up Q1). Three spawn sites
   pass a model that overrides their agent file (research §2). Two files say never to set
   `effort` on a haiku spawn, but Haiku 5.5 supports effort.
3. **Wording that the 5.5 guidance advises against.** There are 23 triple-marker barriers and
   124 lines of CAPS directives (research §4). Some rules are restated four or five times in one
   skill. The guidance says to "dial back any aggressive language" and to give the reason for a
   rule (research §9). WBTE "lite" rule 6 blocked this rewrite, but the Q2 trial found no loss
   from plain wording on Opus 5.5 and Sonnet 5.5 (research, Follow-up Q2).

If the plugin does not change, spawn blocks keep failing, the model advice keeps naming models
that the aliases no longer select, and agents run at whatever effort the session happens to use.

### Success Metrics

- 0 bare `subagent_type` values that name a plugin agent. `general-purpose` stays bare, because
  it is a built-in.
- Every agent file sets `model` and `effort`, except that `task-worker` sets only `effort`
  because `implement` chooses its tier.
- 0 spawn blocks pass a `model` that differs from the agent file.
- 0 current-roster mentions of `claude-opus-4-8`, `claude-opus-5`, `claude-sonnet-5`, or
  `claude-haiku-4-5` under `plugin/`. Dated observations, such as
  `code-review-integration.md:154-161`, stay as history.
- 0 triple-marker barrier lines. Every barrier line states a reason.
- At most 15 CAPS directive lines under `plugin/`, down from 124. Each one that stays has a
  recorded reason.
- Every batch passes its gate before the next batch starts.
- The on-invoke token cost of the fourteen stages does not rise (`claude --plugin-dir plugin
  plugin details wb`).
- Total eval spend for the plan stays at or under $30.

## Design Approach

Apply the full wording pass of Option B, in batches. Each batch is a small set of files with one
evaluation method that matches what the batch changes. A batch merges only after its gate shows
no loss. If one edit in a batch fails its gate, only that edit is reverted, and the rest of the
batch continues.

Batch 0 comes first, because it fixes the live defect and the model facts that later batches
depend on. The order of Batches 1 to 5 is for `/wb:create_tasks` to set.

| Batch | Scope | Gate |
| ----- | ----- | ---- |
| 0 — Spawns and tiers | `wb:` spawn names. Agent files as the one tier authority. `model-help` roster, ladder, and baselines for the 5.5 models. Gate lines that point to `model-help` instead of restating tiers. The stale haiku-effort rule | Mechanical checks (grep counts), plus a transcript probe that each spawn resolves and runs at its intended model and effort |
| 1 — Research, design, and task stages | Wording in `create_research`, `create_product_research`, `create_design`, `create_tasks`, and their supporting files | The `evals/` harness on `evals/fixture-large`, with `judge.py --within` |
| 2 — Implementation stages | Wording in `implement`, `implement_inline`, `tdd-discipline`, `verification-before-completion`, and the worker and verifier prompts | Blind trials in the Q2 style, plus the planted-defect verifier trial |
| 3 — Other stages and skills | Wording in `validate_execution`, `validate_project`, `update_status`, `create_handoff`, `resume_handoff`, `explore_design`, `create_mockup`, `mockup-iteration`, `research-validation`, `review-prep`, and the other skills with triple barriers or CAPS clusters | Blind trials for each barrier and scope pattern that the batch changes. Mechanical checks for the rest |
| 4 — Agent prose | Wording inside the 7 agent files | The `evals/` harness, research stage, on `evals/fixture-large` |
| 5 — Shared rules and docs | WBTE rule 6, root `CLAUDE.md`, `README.md`, `help`, `CHANGELOG.md`, and the version bump | `link_check.py`, `token_check.py`, `test-prime`, lint, and `./plugin/scripts/check` |

### Why This Approach

- The user chose the full wording pass, done in batches and evaluated as the work goes.
- Batches keep a loss traceable to one small change. The 2.2.0 precedent shows why. Its agent
  rewrite passed a one-repeat gate as part of a large change, and was then reverted after a
  later gate found a lost fact (`CHANGELOG.md:289-291`).
- Each batch gets the cheapest gate that can see a loss in what it changes. The harness covers
  only the research, design, and task stages (`evals/run.py:38-44`), and one large-fixture
  repeat costs about $5 (research §7). A blind trial costs about $0.01 a run (research,
  Follow-up Q2). So the harness is spent only on the batches it can test.
- The batches separate agent prose (Batch 4) from stage prose (Batch 1), because the agent files
  are where the 2.2.0 loss happened.
- Batch 0 is mechanical, and it fixes a defect that blocks spawns today.

## Technical Decisions

### Architecture

- **The agent file is the one authority for a spawned agent's model and effort.** Spawn blocks
  do not pass `model` or `effort`. Two places may override, and each states why: the
  `implement` worker ladder, and the `adversarial-review` tier table.
  - Rationale: a spawn `model` overrides the agent file (research §2). Three spawn sites already
    disagree with their agent file. One authority cannot disagree with itself.
  - Trade-off: a stage can no longer choose a cheaper tier for one spawn without an explicit
    override.
  - Pattern reference: `implement/prompts/verifier-prompt.md:3-6` already spawns with no model.
- **Every spawn of a plugin agent uses its `wb:` name.** `general-purpose` and other built-ins
  stay bare.
  - Rationale: the bare name fails (research §5, knowledge entry of 2026-10-21).
  - Trade-off: none found.
- **`model-help` stays the one authority for the main-session tier.** The 7 gate lines stop
  hard-coding a baseline and stop pointing to the root `CLAUDE.md`, which an installer does not
  receive. Each one points to `model-help` gate mode.
  - Rationale: the gate lines restate `model-help/SKILL.md:96-105`, so a roster change leaves
    them stale (research §4, the integration-points agent).
  - Trade-off: a reader of one stage no longer sees its baseline inline.
  - Pattern reference: `forge/SKILL.md:170` already only delegates.
- **Barrier form**: `⛔ BARRIER N: <what must be true> — <reason>`, one marker on one line.
  Barrier numbers and names stay the same.
  - Rationale: this is the documented form (root `CLAUDE.md`, "Command Structure Patterns").
    `technical-english.md:110` cites "BARRIER 2" of `implement` by name.
  - Trade-off: none found. The Q2 trial found no loss.
- **A barrier that waits for agents names the completion notification.** Example: "every
  spawned agent has sent its completion notification".
  - Rationale: subagents run in the background by default, and results arrive as a completion
    notification (research §10). This was the wording of the Q2 `trim` arm.
  - Trade-off: the text names a harness mechanism, so a change to the mechanism would need an
    edit.
- **Checkpoints and "Read [link] NOW" directives keep their current form.**
  - Rationale: no trial has measured them (research, Follow-up Q2). They stay under rule 6.
  - Trade-off: the plugin keeps two registers. Barriers become plain, and these two stay
    emphatic.
- **CAPS directives become plain imperatives with a reason.** A file may keep one emphasized
  line only if that instruction is shown to be underweighted. Each line that stays is recorded
  with its reason in the plan's Implementation Notes.
  - Rationale: "If you emphasize many lines, none of them stands out", and "Emphasis is not
    banned; it is a tested, scoped fix" (research §9).
  - Trade-off: a rule that relied on volume and not on its reason may weaken. The batch gates
    exist to catch that.
- **One statement for each rule in each skill, at the point of use.** Remove restatements such
  as the 5 copies of the read-fully rule in `create_research` (research §4). Put a rationale
  that needs more than one sentence in the skill's `reference.md`, not in `SKILL.md`.
  - Rationale: restatement inflates the register. Rationale in `SKILL.md` caused the
    2026-09-15 token regression, from 46.8k to 58.4k tokens (risk-precedents agent).
  - Trade-off: a skill that loses its summary sections is less scannable for a human.
- **The read-fully rule says to read the whole file, and to page through a partial view with
  `offset` and `limit`.**
  - Rationale: the Read tool returns a partial view for a file over its token limit (Gabe's
    audit, `review/P.md`, P2). "WITHOUT limit/offset" then has no correct way to comply.
  - Trade-off: none found.
- **The `review-prep` trigger no longer fires on the bare word "review".**
  - Rationale: newer models trigger skills more readily (research §9). The bare word also
    matches the built-in `/code-review` and `/wb:adversarial-review`.
  - Trade-off: a user who types only "review" no longer gets the walkthrough.

### Data Model

The tiers that Batch 0 sets in the agent files:

| Agent | `model` | `effort` | Reason |
| ----- | ------- | -------- | ------ |
| `codebase-locator` | `haiku` | `medium` | Haiku 5.5 at `low` is "more likely to skip a search, stop early" (research §9) |
| `pattern-finder` | `haiku` | `medium` | The same reason |
| `codebase-analyzer` | `sonnet` | `medium` | Unchanged |
| `product-behavior-analyzer` | `sonnet` | `medium` | Unchanged |
| `research-validator` | `sonnet` | `high` | Unchanged, unless the verifier trial moves it |
| `task-verifier` | `sonnet` | `high` | Unchanged, unless the verifier trial moves it |
| `task-worker` | not set | `medium` | `implement` sets the tier. `medium` is the fallback effort |

The `implement` worker ladder keeps its four rungs and adds an effort for each:

| Tier | Effort |
| ---- | ------ |
| `haiku` | `medium` |
| `sonnet` | `medium` |
| `opus` (the default) | `medium` |
| `fable` | `high` |

The `model-help` main-session baselines, with Opus 5.5 as the default model (research Q4):

| Phase | Baseline | Upshift |
| ----- | -------- | ------- |
| `create_research`, `create_tasks`, `implement`, `implement_inline`, `adversarial-loop` | Opus 5.5 / `medium` | Opus 5.5 / `high` |
| `create_design`, `validate_execution`, `adversarial-review` | Opus 5.5 / `high` | Fable 5.1 / `high` for novel, one-way-door, or compliance-critical work |
| Mechanical phases, such as `update_status` | Sonnet 5.5 / `medium` | Opus 5.5 / `medium` |

- The upshift ladder becomes `Haiku 5.5 → Sonnet 5.5 → Opus 5.5 → Fable 5.1`. The "two Opus
  tiers" rule goes, because Opus 5.5 is the one current Opus.
- Fable stays at `effort: high` as a cost guard. The switch-cost rule
  (`model-help/SKILL.md:117-128`) does not change.
- Rationale: Opus 5.5 at `medium` "matches or exceeds Claude Opus 5 at `high`" (research §9).
  Sonnet 5.5 costs half of Opus 5.5 ($2/$10 against $4/$20).

### Integration Points

- **Exempt tokens stay exact** (`technical-english.md:103-175`): `### ⛔ CHECKPOINT:` and its
  labels, the verifier headings `### Status: PASS`, `### Status: FAIL`, and
  `### Baseline failures`, the task-line shapes, and the journal headings.
- **Generated documents keep their `⛔` count.** `evals/judge.py:119` counts `⛔` in generated
  text. The templates are not part of this pass, so the count does not change.
- **`evals/link_check.py` `RULE_PHRASES`.** A rewritten skill must not restate a WBTE rule
  phrase.
- **Root `CLAUDE.md`** restates the spawn tiers (`:205-211`, with no `fable`) and the barrier
  form (`:185-193`). Batch 5 updates both. The maintainer docs under `docs/` are history and
  stay as they are.
- **Release mechanics.** `plugin/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
  must carry the same version. Installed users get a change only after a version bump and
  `claude plugin update`.

### Resolved Decisions

- Effort can be set for each spawn. A spawn `effort` overrides the agent file, and a spawn with
  no `effort` inherits the session effort
  - Rationale: the Q1 probe measured it in the API request (`output_config.effort`) on Claude
    Code 2.1.300. The user asked for a probe, not an assumption
  - Trade-off: two places can now set effort for one agent, the agent file and the spawn
  - Source: research.md Q1 · Decided 2026-10-22
- WBTE "lite" rule 6 does not bind barrier markers or capitalized scope rules on the 5.5 models.
  Checkpoints and "Read [link] NOW" directives stay under rule 6, because no trial measured them
  - Rationale: the Q2 blind trial (320 runs, Opus 5.5 and Sonnet 5.5) found no loss from plain
    wording in any cell. The user asked for a probe to settle the question
  - Trade-off: the trial used short excerpts at `medium` effort, so a stage-level check is still
    the stronger evidence for any single rewrite
  - Source: research.md Q2 · Decided 2026-10-22
- The eval budget for this plan is $30. Ask the user before any run would take the total over it
  - Rationale: the user's limit. $3.62 is spent (the Q2 trial)
  - Trade-off: about $26 remains, which is about 5 large-fixture repeats of the stage harness
  - Source: research.md Q3 · Decided 2026-10-22
- Opus 5.5 is the baseline main-session model for the audit
  - Rationale: the user's choice. It is the Claude Code default model on the Anthropic API
  - Trade-off: files that a spawn pins to `sonnet` or `haiku` still run on those models, so their
    guidance pages differ from the baseline
  - Source: research.md Q4 · Decided 2026-10-22
- Option B (the full wording pass) is applied in batches, and each batch is evaluated before the
  next one starts
  - Rationale: the user's choice. It keeps a loss traceable to one small change
  - Trade-off: more gates, and more elapsed time, than one large change
  - Source: Step 4 option choice · Decided 2026-10-22
- `task-verifier` and `research-validator` stay on Sonnet 5.5 at `high`. A planted-defect trial
  in Batch 2 compares Sonnet 5.5 with Opus 5.5. The verifiers move to Opus 5.5 only if Opus
  finds more planted defects with no more false failures
  - Rationale: Gabe's 4.0.0 moved them to Opus, but its commit gives no source for the quality
    claim (research §8). Opus 5.5 costs twice as much as Sonnet 5.5
  - Trade-off: the trial adds a little spend, at about $0.01 to $0.05 a run
  - Source: Step 4 proposal, not disputed by the user · Decided 2026-10-22
- Haiku agents run at `effort: medium`, not `low`
  - Rationale: Haiku 5.5 at `low` is "more likely to skip a search, stop early, or skip a check"
    (research §9). Search is the locator's job
  - Trade-off: a `medium` Haiku spawn costs more than a `low` one
  - Source: Step 4 proposal, not disputed by the user · Decided 2026-10-22
- Batch 0 ships as patch release 3.0.1. Batches 1 to 5 ship together as 3.1.0 after their gates
  pass
  - Rationale: the bare spawn names are a live defect. The plugin cache is keyed by version, so
    a fix reaches installed users only through a version bump (root `CLAUDE.md`, "Releasing")
  - Trade-off: two releases and two update steps for users
  - Source: create_design · Decided 2026-10-22

## Scope Definition

### In Scope

- Batch 0: `wb:` spawn names, agent-file tiers, spawn blocks without `model`, the `model-help`
  roster and baselines, the `implement` ladder efforts, gate lines that delegate, and the removal
  of the stale haiku-effort rule.
- Batches 1 to 4: the wording pass over every shipped skill and agent that has a triple-marker
  barrier, a CAPS directive cluster, a restated rule, or the "no limit/offset" wording.
- The narrower `review-prep` trigger.
- The planted-defect verifier trial and the blind trials for Batches 2 and 3. These are plan-local
  harnesses under `trials/`, like the Q2 trial.
- Batch 5: WBTE rule 6 rewritten to match the Q2 result, root `CLAUDE.md` and `README.md` kept in
  agreement, `CHANGELOG.md` entries, and the 3.0.1 and 3.1.0 version bumps.

### Out of Scope

- Folding `product-behavior-analyzer` into `codebase-analyzer`, as Gabe's 4.0.0 did. It is a
  structural change, not a 5.5 change.
- Output templates. Generated documents keep their current shape and their `⛔` count.
- Checkpoint and "Read [link] NOW" wording. No trial has measured them.
- The PreCompact registration of `wb-prime.sh`, whose output does not reach the model
  (research §10). This is a follow-up.
- Splitting the 3 `SKILL.md` files that exceed 500 lines (research §1). This is a follow-up.
- A sweep for British spelling. Only lines that this pass already edits get American spelling.
- Adding `implement` or `validate_execution` to `evals/run.py`. The plan uses plan-local blind
  trials for those stages.
- The maintainer docs under `docs/`, which are history.
- Gabe's beads-specific fixes, which do not apply to a checkbox plan.

## Success Criteria

### Functional Requirements

- [ ] Every spawn block and prose spawn of a plugin agent uses its `wb:` name, and a transcript
  probe shows that each one resolves.
- [ ] A transcript probe shows that each agent runs at the model and effort in the Data Model
  table.
- [ ] `model-help` names only Haiku 5.5, Sonnet 5.5, Opus 5.5, and Fable 5.1 as current models.
- [ ] No shipped file says that effort cannot or should not be set on a haiku spawn.
- [ ] Every barrier line has one `⛔` and a stated reason. Every barrier that waits for agents
  names the completion notification.
- [ ] Each skill states each of its rules once, at the point of use.
- [ ] WBTE rule 6 matches the Q2 result, and it still keeps checkpoints and "Read [link] NOW"
  directives.
- [ ] The verifier tier matches the result of the planted-defect trial.

### Non-Functional Requirements

- [ ] Fidelity: in the Batch 1 and Batch 4 harness gates, `judge.py --within` finds no lost
  facts in any repeat.
- [ ] Behavior: in each blind trial, the new wording passes at least as many runs as the old
  wording in every cell, and every trap cell reaches at least 9 of 10.
- [ ] Cost: the fourteen-stage on-invoke token cost does not rise.
- [ ] Spend: total eval spend for the plan is at most $30, and the user is asked before any run
  would exceed it.
- [ ] Quality gates: `./plugin/scripts/check` passes after each batch.

## Risk Analysis

### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| A plain rewrite loses behavior at full stage length that the short-excerpt trial could not see | High | Low | Batch 1 and Batch 4 harness gates. Revert only the edit that fails |
| The two harness gates cost more than the $26 that remains | Medium | Medium | Ask the user before a run would exceed $30. The `--stages` option runs only the stages that a batch touches |
| An installed Claude Code older than 2.1.292 ignores spawn `effort` | Low | Low | The agent file sets effort, so the tier holds on any version |
| Removing `model` from spawn blocks changes which model runs where a spawn overrode the agent file | Medium | High (intended) | The Data Model table states the new tier. The Batch 0 probe confirms it |
| A rewritten barrier number or name breaks a cross-reference | Medium | Low | Barrier numbers and names stay the same. `technical-english.md:110` cites "BARRIER 2" |
| Gate commands read as clean when they fail (`grep -c` exit 1, bare `grep` skipping gitignored paths, rtk `diff` exit 0) | Medium | Medium | Use `command grep`, `cmp`, and `rtk proxy` as `.claude/wb/knowledge.md` records |

### Assumptions

This table lists the assumptions that the design depends on. They usually come from gaps in
the research. This table is the record, because there is no external tracker.

| ID | Assumption | Validated? |
| -- | ---------- | ---------- |
| A1 | The Q2 result for barrier and scope wording holds at full stage length. The Batch 1 harness gate tests it | Pending |
| A2 | A Sonnet 5.5 harness gate is a valid proxy for an Opus 5.5 main session. Sonnet 5.5 is the more literal reader, so a loss would show there first | Pending |
| A3 | A large-fixture repeat on Sonnet 5.5 costs about $5, as the 2026-09-30 runs did | Pending |
| A4 | `evals/fixture-large` makes `create_research` spawn its agents, so Batch 4 changes are exercised | Pending |
| A5 | A spawn with no `model` runs the agent file's model. The Q1 probe showed this for `wb:codebase-analyzer` only | Pending |

- **IDs are local and stable.** Number them `A1`, `A2`, and so on, in the order you raise them.
  Never renumber them.
- **State the consequence.** Give an assumption a row only if a wrong assumption changes the
  design. If it changes nothing, it is background and not an assumption.
- **Validation is an edit, not a new record.** `/wb:resolve_questions` changes the cell to
  `Validated YYYY-MM-DD`. If the answer refutes the assumption, it writes `Invalid — [note]`,
  and the note says what must change. Never delete a row.

## Rejected Alternatives

### Option: A — fix what is broken and keep the wording

- **Approach**: Batch 0 only. Leave the barriers and CAPS directives unchanged.
- **Rejected because**: the user wants the 5.5 wording pass. The Q2 trial removed the evidence
  that blocked it.
- **Trade-offs**: smallest diff and almost no eval spend. It leaves the prompts in the register
  that the 5.5 guidance advises against.

### Option: B in one pass

- **Approach**: every wording change across about 40 files in one change, as Gabe's 4.0.0 did.
- **Rejected because**: the user asked for batches. A loss in one large diff is hard to trace,
  and the harness covers only 3 stages.
- **Trade-offs**: one gate and one release. Any loss is harder to find, and the stages outside
  the harness have no test.

### Option: C — two change sets

- **Approach**: Batch 0 as one change set, and the whole wording pass as a second change set
  with one harness gate.
- **Rejected because**: the user preferred smaller batches with a gate for each.
- **Trade-offs**: fewer gates. Each gate covers more, so a loss is harder to trace.

## Pending Decisions

This table lists the design decisions that need stakeholder input before execution starts.
This table is the record, because there is no external tracker.

| ID | Decision Needed | Blocks | State |
| -- | --------------- | ------ | ----- |
| — | None. Every decision is recorded under Technical Decisions | — | — |

Note: resolve every decision that blocks execution before you run `/wb:create_tasks`.

## References

- Research: [research.md](research.md)
- Q2 trial: [trials/2026-10-22-q2-blind-trial/RESULTS.md](trials/2026-10-22-q2-blind-trial/RESULTS.md)
- Tasks: [tasks.md](tasks.md)
- Related designs: `docs/plans/2026-09-29-asd-ste100-prose/design.md` (the WBTE gate method, D7
  and D10)
- External: `gvarela/workbench` v4.0.0, `docs/audits/2026-09-29-prompt-audit/`
- External: platform.claude.com prompting pages for Opus 5.5, Sonnet 5.5, Haiku 5.5, and Fable
  5.1. code.claude.com sub-agents, skills, and model-config pages
