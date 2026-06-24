---
project: prompt-efficiency
ticket: N/A
created: 2026-05-28
status: complete
last_updated: 2026-06-24
current_phase: 6
total_tasks: 37
completed_tasks: 37
depends_on: [research.md, design.md]
beads_epic: prompts-2n3
beads_phases:
  phase1_milestone: prompts-ph3
  phase2_milestone: prompts-p0f
  phase3_milestone: prompts-8lg
  phase4_milestone: prompts-4ot
  phase5_milestone: prompts-hd1
  phase6_milestone: prompts-c8y
beads_tasks:
  T1.1: prompts-9ab
  T1.2: prompts-49v
  T1.3: prompts-zuu
  T1.4: prompts-sid
  T1.5: prompts-a77
  T1.6: prompts-omg
  T1.7: prompts-gpq
  T1.8: prompts-d28
  T1.9: prompts-69p
  T2.1: prompts-a4n
  T2.2: prompts-c9f
  T2.3: prompts-a21
  T2.4: prompts-yx8
  T2.5: prompts-0md
  T2.6: prompts-b3g
  T2.7: prompts-x51
  T2.8: prompts-xww
  T2.9: prompts-pp5
  T3.1: prompts-khh
  T3.2: prompts-af7
  T3.3: prompts-ato
  T3.4: prompts-3z4
  T4.1: prompts-q45
  T4.2: prompts-xvu
  T4.3: prompts-6oj
  T4.4: prompts-v1g
  T5.1: prompts-q2p
  T5.2: prompts-y5u
  T5.3: prompts-lda
  T5.4: prompts-bnh
  T5.5: prompts-fik
  T6.1: prompts-2en
  T6.2: prompts-p39
  T6.3: prompts-djt
  T6.4: prompts-fuh
  T6.5: prompts-cnf
  T6.6: prompts-hwj
---

# Execution Plan: Prompt Efficiency for Opus 4.8 Token Optimization

## Overview

Implementing the token/output optimization specified in design.md: conservative
dedup + terse-directive rewrite (Option B), conditional beads-stealth extraction,
output-token (narration) reduction, cache-aware structuring, and a handoff
reliability rework — across `commands/`, `agents/`, `skills/`, plus the
scope-expansion items (root `CLAUDE.md` rule + README opt-in docs).

**Design Approach**: terse-rewrite the boilerplate, preserve all invariants
(inline barriers, output templates, documentarian rules), reuse the in-repo
"Iron Law" banner precedent.
**Target State**: ~400–700 input tokens/command saved + measurable narration
output reduction, with the generated artifacts structurally unchanged.

## Implementation Strategy

### Phase Rationale

Ordered by the design's **pilot-first validation gate** and risk:

- **Phase 1 (Pilot)** applies *every* edit class to a single command
  (`create_research.md`) and validates against the acceptance bar before any
  rollout. This de-risks the highest-impact risk in design.md ("terse rewrites
  subtly change adherence/output structure") on one file, cheaply reversible.
- **Phase 2 (Rollout)** only proceeds once the pilot passes; it applies the
  *validated* style to the remaining 13 commands in one uniform pass (uniformity
  is required for cacheability — same boilerplate must be byte-identical).
- **Phase 3 (Agents & skills)** is independent and lower-risk.
- **Phase 4 (beads-stealth extraction)** is a distinct mechanism requiring
  both-mode testing, so it is isolated.
- **Phase 5 (Output-discipline scope-expansion)** adds the global `CLAUDE.md`
  rule + README opt-in (the approved out-of-locked-scope items).
- **Phase 6 (Handoff reliability)** is the largest single-file rework and is
  reliability- rather than token-driven; isolated so it can proceed in parallel
  with 2–5 if desired.

### Testing Strategy

No unit-test framework exists; verification is **lint + structural diff + token
delta** (confirmed by tooling agent):

- **Lint**: `./scripts/lint <files>` (markdownlint; PostToolUse hook auto-fixes
  on Write/Edit, non-blocking). Must exit 0 before any phase checkpoint.
- **Token delta proxy**: `wc -c <file>` ÷ 4 (the research's established
  chars/token proxy; no in-repo tokenizer). Record before/after per file.
- **Structural-equivalence (pilot)**: generate a `research.md` with the
  compacted command and diff its *shape* against the baseline
  `docs/plans/2026-05-28-prompt-efficiency/research.md`:
  same top-level section headings (8), same frontmatter field set, same
  `### N.` Detailed-Findings subsection pattern, barrier count = 0 in output.
- **beads-stealth**: exercise both `BEADS_MODE=stealth` and git-mode paths.

## Task Tracking

✅ **Beads initialized** (git mode, prefix `prompts`, shared from main repo
`/Users/scraig/projects/prompts` per worktree setup). Epic `prompts-2n3`, 6
phase milestones, 37 task issues created with dependencies. Status lives in
beads (this markdown is the PLAN). Use `bd ready` for actionable work,
`bd update <id> --status in_progress` to claim, `bd close <id>` to complete.
Task→beads-ID map is in frontmatter `beads_tasks`.

---

## Phase 1: Pilot — Compact `create_research.md` + Validate

### Objective
Apply all applicable edit classes to the single canonical command, then prove
the acceptance bar (structure preserved, lint clean, tokens down) before rollout.

### Prerequisites
- [ ] Research validated, design approved (done)
- [ ] Baseline captured: `cp docs/plans/2026-05-28-prompt-efficiency/research.md /tmp/research.baseline.md`
- [ ] Baseline byte count recorded: `wc -c commands/create_research.md`

### Changes Required

#### 1. `commands/create_research.md` — apply the full edit set

**Current State** (from inventory): CRITICAL/DO-NOT block at `:10-19`;
sub-agent READ-ONLY preamble at `:83`; 3 Task() closers at `:111,138,157`;
"Document what IS" slogan ×7 (`:19,64,136,189,204,348,403`); Confirm Completion
template at `:363-390`; Synchronization Points recap at `:416-421`. Inline
`⛔⛔⛔ BARRIER` markers at `:50,195,341` and the embedded research.md template
at `:216-339`.

**Target State**: same barriers, same embedded template (untouched), boilerplate
compacted to the banner precedent, narration directive added.

**Canonical terse forms to use (reused verbatim everywhere for cacheability):**

```
## Documentarian Rule

`DOCUMENT WHAT EXISTS — NEVER SUGGEST, CRITIQUE, OR IMPROVE`

Describe the code as it is: no recommendations, issue-spotting, enhancements,
critiques, or root-cause analysis unless explicitly asked.
```

```
**Sub-agents are READ-ONLY** — they return findings only; YOU write `research.md` after synthesizing.
```

```
Task() closer →  Return findings only; write nothing.
```

```
**Output discipline**: act on barriers silently; don't restate the plan between
steps; emit only the artifact and a one-line completion summary.
```

**Constraints**: do NOT touch the 3 inline `⛔⛔⛔ BARRIER` lines or the embedded
template (`:216-339`). Keep one load-bearing "document what IS" instance (incl.
the one inside the agent-prompt text); remove the redundant repeats.

### Tasks
- T1.1 Capture baseline (copy research.md, record byte count) — setup
- T1.2 Replace CRITICAL/DO-NOT block (`:10-19`) with the Documentarian Rule banner
- T1.3 Collapse the 7 "Document what IS" slogans to the load-bearing instance(s)
- T1.4 Replace sub-agent READ-ONLY preamble (`:83`) with the one-liner
- T1.5 Tighten the 3 Task() closers to the terse closer; reorder each Task() prompt stable-first / variable-last (shared documentarian preamble ahead of task specifics)
- T1.6 Compact the Confirm Completion template (`:363-390`) to a terse one-line-summary form
- T1.7 Add the Output-discipline directive near the top of the process steps
- T1.8 Delete the Synchronization Points recap (`:416-421`)
- T1.9 Verify the 3 inline barriers and the embedded template are byte-unchanged

### Success Criteria

#### Automated Verification
- [ ] Lint clean: `./scripts/lint commands/create_research.md` exits 0
- [ ] Token delta recorded: `before − after` bytes ÷ 4 ≥ target (~150–400 tokens for this file); reduction reported
- [ ] Inline barrier count unchanged: `grep -c '⛔⛔⛔ BARRIER' commands/create_research.md` == pre-edit value

#### Manual Verification (the validation gate)
- [ ] Run the compacted `/wb:create_research` on a real question; capture output `research.md`
- [ ] Section headings identical to baseline: `diff <(grep '^#' /tmp/research.baseline.md) <(grep '^#' <new>)` → only content differs, not structure
- [ ] Frontmatter field set matches baseline (project, ticket, created, status, last_updated, researcher, git_commit, git_branch, repository)
- [ ] `### N.` Detailed-Findings subsection pattern preserved; output barrier count = 0
- [ ] Read-through of Summary + one finding: documentarian quality unchanged

### Modified Files
- `commands/create_research.md` — full compaction pilot

### ⛔ CHECKPOINT: Phase 1 Complete
Before Phase 2:
1. ✅ Lint clean; token reduction recorded
2. ✅ Structural diff shows preserved shape; read-through confirms quality
3. ✅ **Human confirmation that the compacted style is approved for rollout**
4. ✅ If the gate FAILS: fall back to Option A (recap removal + slogan collapse only) for the failing edit class, per design Rejected Alternatives
5. ✅ Update frontmatter: `current_phase: 2`

**Do not proceed without human sign-off on the pilot output.**

---

## Phase 2: Roll Out Compaction to Remaining Commands

### Objective
Apply the validated style uniformly to the other 13 commands.

### Prerequisites
- [ ] Phase 1 gate passed and approved
- [ ] Use the exact same terse-form strings from Phase 1 (cacheability requires byte-identical boilerplate)

### Changes Required

#### Sync-point recap removal (7 remaining of 8)
Delete the end-of-file `## Synchronization Points` recap in:
`create_design.md:468-479`, `create_execution.md:773-780`,
`create_product_research.md:519-524`, `create_project.md:441-446`,
`implement_tasks.md:669-680`, `validate_execution.md:419-424`,
`validate_project.md:508-513`. (Inline barriers stay.)

#### Banner / preamble / closer rewrites
- CRITICAL/DO-NOT banner → `create_product_research.md:10-19`.
- Sub-agent READ-ONLY one-liner → `create_design.md:98`, `create_execution.md:76`, `create_product_research.md:110`.
- Task() closer tightening + stable-first ordering → `create_design.md` (3), `create_execution.md` (3), `create_product_research.md` (3), `validate_execution.md` (4).
- "Document what IS" slogan collapse → `create_product_research.md` (×7).

#### Confirm Completion + narration directive
- Compact Confirm Completion template → `create_product_research.md:448-476`.
- Add the Output-discipline directive to every command that emits inter-step narration (all `create_*`, `validate_*`, `implement_*`, `update_status`).

#### create_research ↔ create_product_research in-place mirror
- Rewrite the shared near-identical regions in BOTH files with matched wording in a single pass (no extraction; preserve product-specific 3-layer template, product-behavior-analyzer swap, validation step). Confirm the portable mirror `docs/product-research-claude-desktop.md` is NOT edited and still standalone.

### Tasks
- T2.1 Remove the 7 remaining Synchronization Points recaps
- T2.2 Apply Documentarian Rule banner to create_product_research
- T2.3 Apply sub-agent one-liner to the 3 commands
- T2.4 Tighten Task() closers + reorder (4 commands, 13 blocks) 
- T2.5 Collapse create_product_research slogans
- T2.6 Compact create_product_research Confirm Completion template
- T2.7 Add Output-discipline directive across narrating commands
- T2.8 In-place mirror rewrite of create_research ↔ create_product_research shared regions
- T2.9 Confirm `docs/product-research-claude-desktop.md` unchanged + still standalone

### Success Criteria
#### Automated
- [ ] `./scripts/lint --all` exits 0
- [ ] Per-file token deltas recorded; aggregate reduction reported
- [ ] Each edited command's inline barrier count unchanged (grep check)
- [ ] Boilerplate byte-identical across files: the banner/one-liner/closer strings match exactly (diff-check a sample pair)
#### Manual
- [ ] Spot-run 2 commands (e.g. `create_design`, `validate_execution`); outputs structurally intact
- [ ] create_product_research still produces its 3-layer product-research.md

### ⛔ CHECKPOINT: Phase 2 Complete
1. ✅ Lint clean repo-wide; deltas recorded
2. ✅ Spot-runs confirm no structural regressions
3. ✅ Human confirmation
4. ✅ Update frontmatter: `current_phase: 3`

---

## Phase 3: Compact Agents & Skills

### Objective
Apply the banner precedent to agent/skill boilerplate.

### Prerequisites
- [ ] Phase 2 complete (style finalized)

### Changes Required
- CRITICAL/DO-NOT banner → `agents/codebase-analyzer.md:9-16`, `agents/product-behavior-analyzer.md:9-17,18-24` (keep the traceability mandate as a distinct one-liner).
- Terse-rewrite the `## What NOT to Do` section in all 6 agents (`codebase-analyzer:101`, `codebase-locator:107`, `pattern-finder:121`, `product-behavior-analyzer:137`, `research-validator:214`, `task-verifier:155`) to a compact directive, preserving each agent's specific prohibitions.
- Collapse the 2 "Document what IS" slogans in `product-behavior-analyzer.md:16,150`.
- `skills/*`: the Iron Law/The Rule banners (`tdd-discipline:12-16`, `verification-before-completion:12-16`, `research-validation:15-19`) are the *precedent* — leave them; apply minor compaction only where duplicate preamble exists.

### Tasks
- T3.1 Banner-rewrite the 2 agent CRITICAL blocks
- T3.2 Terse-rewrite the 6 agent "What NOT to Do" sections
- T3.3 Collapse product-behavior-analyzer slogans
- T3.4 Skills compaction pass (only genuine duplication; banners untouched)

### Success Criteria
#### Automated
- [ ] `./scripts/lint agents/ skills/` exits 0
- [ ] Token deltas recorded per agent/skill
#### Manual
- [ ] Each agent still states its role + specific prohibitions (read-through)

### ⛔ CHECKPOINT: Phase 3 Complete — human confirm; `current_phase: 4`

---

## Phase 4: Extract the Conditional beads-stealth Block

### Objective
Move the stealth-branch body to one runtime-read doc; replace 7 inline blocks
with a conditional pointer. Common (non-stealth) path pays neither tokens nor a Read.

### Prerequisites
- [ ] Phases 1–2 complete (commands stabilized)

### Changes Required
- Create `docs/beads-stealth-mode.md` (one minimal doc) holding the stealth-mode handling currently duplicated.
- In each of the 7 sites, keep inline: `BEADS_MODE` detection + git-mode handling (always-needed). Replace only the stealth-branch body with a pointer, e.g.:

```
Detect mode via `BEADS_MODE` (set by the SessionStart hook).
- git mode (default): <existing inline git-mode handling stays>
- stealth mode: read `docs/beads-stealth-mode.md` and follow it.
```

Sites: `create_execution.md:451`, `implement_tasks.md:156`, `create_handoff.md:119`, `resume_handoff.md:75`, `implement_coordinated.md:159`, `update_status.md:52`, `validate_project.md:136`.

### Tasks
- T4.1 Author `docs/beads-stealth-mode.md` from the canonical stealth block
- T4.2 Replace the 7 inline stealth-branch bodies with the conditional pointer (git-mode handling stays inline)
- T4.3 Test git-mode path (default): behavior unchanged
- T4.4 Test stealth path (`BEADS_MODE=stealth`): doc is read and followed

### Success Criteria
#### Automated
- [ ] `./scripts/lint` exits 0; token delta recorded across the 7 commands
- [ ] `grep -L` confirms the verbose stealth echo block is gone from the 7 files
#### Manual
- [ ] Both modes verified; non-stealth path performs no extra Read

### ⛔ CHECKPOINT: Phase 4 Complete — human confirm both modes; `current_phase: 5`

---

## Phase 5: Output-Discipline Scope-Expansion + Effort Verification

### Objective
Deliver Option C's global half + the README opt-in, and close the effort-setting
action item (Q4).

### Prerequisites
- [ ] Per-command narration directive already shipped (Phases 1–2)

### Changes Required
- Add a concise **narration-discipline rule** to the repo's own root `CLAUDE.md` (scope-expansion approved 2026-06-04): act on barriers silently; no inter-step restatement; artifact + one-line summary.
- Add **README setup instructions**: how a user opts the same rule into their `~/.claude/CLAUDE.md` or a project `CLAUDE.md`. Explicitly state the plugin does NOT auto-install it.
- **Effort-setting verification** (Q4): verify the "Opus 4.8 low ≈ 4.7 high / cleaner tokens" claim against the official model card AND whether Claude Code command frontmatter supports an effort hint. Record the finding; only if BOTH hold, open a follow-up to add effort hints (otherwise document as a session-level knob).

### Tasks
- T5.1 Add narration-discipline rule to root `CLAUDE.md`
- T5.2 Add README opt-in setup instructions (+ "not auto-installed" note)
- T5.3 Verify effort claim against model card; record result
- T5.4 Verify frontmatter effort-hint support; record result
- T5.5 Decide: promote effort-tiering (only if both T5.3/T5.4 hold) or document as operational knob

### Success Criteria
#### Automated
- [ ] `./scripts/lint CLAUDE.md README.md` exits 0
#### Manual
- [ ] README instructions are runnable by a new user (walk through them)
- [ ] Effort findings recorded in design.md Assumptions (flip Unverified → Verified/Refuted)

### ⛔ CHECKPOINT: Phase 5 Complete — human confirm; `current_phase: 6`

---

## Phase 6: Handoff Reliability Rework

### Objective
Make `create_handoff.md` / `resume_handoff.md` produce grounded, thin, non-hallucinated handoffs.

### Prerequisites
- [ ] Independent of Phases 2–5; may run in parallel after Phase 1 establishes the style

### Changes Required

#### `commands/create_handoff.md`
- **Add a pre-write grounding barrier** (new `⛔⛔⛔ BARRIER` before the Step 4 template write): *Every file:line, metric, test result, and progress figure MUST come from actual tool output (`git diff`/`git log`/`git diff --stat`, `bd`, a test run) or be omitted / marked `unverified`. Never carry template example values into the output.*
- **Strip concrete sample values** in the template (`:205` `src/component.ts:45-67`, `:216` `npm test (45/45 pass)`, `:208`, `:398` `+[additions] -[deletions]`) → abstract field labels.
- **Omit-if-empty**: instruct that the ~15 optional sections are dropped when empty, not placeholder-filled; unknown fields written as `unknown`.
- **Drop unmeasurable Session Metadata** (`:391-399`) unless derived from a command (e.g. lines from `git diff --stat`); remove the bare "Overall Progress: X%" (`:175`) unless computed from `bd stats`.
- **Thin same-machine resume** (Quick-Start `:177-189`): one line deferring to `claude --resume`; keep the portable doc for cross-host/cross-agent transfer; push durable learnings to git-tracked `CLAUDE.md`.

#### `commands/resume_handoff.md`
- Try native `--resume` first; keep doc-based resume for cross-boundary only.
- Drop stale-detection / git-commit-matching ceremony (`:242-262`, validation flow) that native resume handles; retain beads + pipeline re-read.

### Tasks
- T6.1 Add pre-write grounding barrier to create_handoff
- T6.2 Strip concrete example values from the template
- T6.3 Add omit-if-empty + `unknown` field rules
- T6.4 Remove/anchor unmeasurable Session Metadata + Overall Progress
- T6.5 Thin the Quick-Start / same-machine resume block
- T6.6 resume_handoff: native-resume-first; drop stale/commit-match ceremony; keep beads + pipeline wiring

### Success Criteria
#### Automated
- [ ] `./scripts/lint commands/create_handoff.md commands/resume_handoff.md` exits 0
- [ ] Token delta recorded (this is the largest single reduction)
- [ ] New grounding barrier present: `grep -c '⛔⛔⛔ BARRIER' commands/create_handoff.md` increased by 1
#### Manual
- [ ] Generate a handoff on real session state: every file:line/metric traces to tool output or is marked `unverified`; empty sections omitted; no fabricated values
- [ ] resume_handoff still restores beads/phase state and re-reads the pipeline docs

### ⛔ CHECKPOINT: Phase 6 Complete — human confirm grounded output; mark project done

---

## Implementation Discoveries
_Update during implementation:_
- Exact per-file token deltas (fill in as edits land).
- Whether the narration directive belongs better in each command's header vs after Initial Response (decide during pilot).
- beads-stealth doc final path (`docs/beads-stealth-mode.md` proposed).

## 🚧 Blockers & Notes
### Current Blockers
- None. Run `bd blocked` for the live dependency-gated view.
### Implementation Notes
- Cacheability depends on byte-identical boilerplate: never reword the canonical terse strings per-file.
- [2026-06-24] Phase 1 pilot (create_research.md): −1,367 bytes / ~341 tok / 10%; output template byte-identical; barriers 3→3. Accepted by-construction.
- [2026-06-24] Behavioral validation (live runs): `create_research` (Test 1) and `create_product_research` (Test 2, via `--plugin-dir`) both PASS — documentarian tone preserved, output template/3-layer structure intact, agents spawned + BARRIER 2 honored, product validation (BARRIER 4) ran, chaining clean. Test 2's validator independently counted 41 ⛔ markers intact and surfaced the new "return findings only; write nothing" closer + output-discipline line. Test 2 emitted a one-line completion summary; Test 1 still produced a verbose chat recap → reinforces firming the Phase 5 global CLAUDE.md narration rule. Unrelated: SessionStart hook path error under --plugin-dir (`./.claude/hooks/...` missing) — environment/config, not a compaction change.
- [2026-06-24] Phase 4: beads-stealth extraction. New `docs/beads-stealth-mode.md`; 6 commands' explanatory blocks → conditional pointer (read only in stealth); operational commit/sync kept inline; validate_project's stealth-*validation* left inline (operational, not boilerplate). −58 net lines; git path byte-preserved.
- [2026-06-24] Phase 5: added a firm Output Discipline rule to repo CLAUDE.md + README opt-in instructions (scope-expansion). Effort verified: claim holds directionally but frontmatter has no `effort:` field → effort kept as session-level operational knob, not a prompt change.
- [2026-06-24] Phase 6: handoff reliability rework. create_handoff +grounding BARRIER 2, stripped fake example values, omit-if-empty/unknown rules, anchored Session Metadata to tooling, thinned Quick Start to native --resume. resume_handoff: native-resume-first, dropped commit-match + stale-detection ceremony, kept beads+pipeline. −95 net lines.
- [2026-06-24] Phase 3: 6 agents, −23 net lines. Documentarian Rule banner on codebase-analyzer + product-behavior-analyzer; all 6 "What NOT to Do" sections compacted (cross-referencing the banner where redundant); product-behavior slogan reduced to 1. T3.4 skills = no-op: the targeted boilerplate classes don't exist in skills (banners are the precedent we copied; skill-specific DO-NOT content left intact).
- [2026-06-24] Phase 2: 8 command files, −106 net lines. Sync-recap removal covered all 8 commands that had one (inventory-confirmed). T2.5 stable-first reorder applied to product_research Agent 2 only (illustrative-template reorder is marginal for cache vs. dispatch-time; documented). T2.7 output-discipline directive added to the core pipeline (create_*/validate_*/implement_tasks); update_status, implement_coordinated, create_mockup intentionally rely on the Phase 5 global CLAUDE.md rule instead of a per-file line.

## 🔗 Quick Reference
### Key Files
- Research: [research.md](research.md) · Design: [design.md](design.md)
- Pilot target: `commands/create_research.md`
- Baseline for structural diff: `docs/plans/2026-05-28-prompt-efficiency/research.md`
### Common Commands
```bash
./scripts/lint --all                 # lint
wc -c commands/create_research.md    # token proxy (÷4)
grep -c '⛔⛔⛔ BARRIER' <file>        # barrier-count invariant check
```
### Design Decisions Reference
- Pilot first = `create_research.md`; acceptance bar = same headings + frontmatter + barrier count.
- Inline barriers + output templates = untouched. Only the conditional beads-stealth block is extracted.
- Output-discipline = per-command baseline + global CLAUDE.md rule + README opt-in (Option C).

---

## Beads Issue Tracking

This project uses beads for ALL task status (git mode, prefix `prompts`).

**Epic**: `prompts-2n3`

**Phase Milestones**: P1 `prompts-ph3` · P2 `prompts-p0f` · P3 `prompts-8lg` ·
P4 `prompts-4ot` · P5 `prompts-hd1` · P6 `prompts-c8y`
(chain: P2←P1←…; P6 runs parallel after P1)

**Granular tasks**: see frontmatter `beads_tasks`.

**Essential commands**: `bd ready` · `bd show <id>` ·
`bd update <id> --status in_progress` · `bd close <id>` · `bd blocked` · `bd sync`

Beads is the source of truth for status — do NOT use markdown checkboxes for tracking.
