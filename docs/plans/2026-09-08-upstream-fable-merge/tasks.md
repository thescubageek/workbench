---
project: upstream-fable-merge
ticket: N/A
created: 2026-09-08
status: in-progress
last_updated: 2026-09-08
current_phase: 2
total_tasks: 63
completed_tasks: 13
task_tracking: markdown-checkboxes
depends_on: [research.md, design.md]
git_commit: b635159b1f4a26db24c8c1934029be6f06a47c44
git_branch: thescubageek/gabe-fable-merge-research
---

# Execution Plan: Tracker-Free Modernization (wb 2.0.0)

## Overview

Implementing design.md's D1–D20 — the `plugin/` relocation, progressive-disclosure skill
split, complete beads removal with markdown as the status surface, cross-session continuity,
`create_tasks`, `explore_design`, drift hardening, Fable-as-upshift, the de-duplicated
failure path, and the 2.0.0 cut.

**Design Approach**: tracker-free modernization (design.md → Design Approach)
**Target State**: design.md → Success Criteria, verbatim

**This plan is written in the convention it establishes.** Task status is markdown
checkboxes; counters in frontmatter are a derived cache; there is no external tracker. That
is D4 applied to this plan itself.

## Task tracking

Checkbox state is the source of truth. Flip `[ ]` → `[x]` as work completes and append
`(completed YYYY-MM-DD HH:MM)`. Counters in frontmatter are reconciled by
`/wb:update_status`, never hand-edited (D5).

```bash
grep -c '^- \[x\]' tasks.md    # completed
grep -c '^- \[ \]' tasks.md    # remaining
```

Every task carries a stable ID (`P2-T7`). IDs are the handle to cite from the journal, a
commit message, or a handoff — they exist because checkbox tracking is otherwise positional
(design.md assumption A2), and an ID costs nothing to add now.

## Decisions that gate work

**All resolved 2026-09-08** via `/wb:resolve_questions`. Nothing gates execution.

| ID | Decision | Effect on this plan |
| -- | -------- | ------------------- |
| **PD2** | Worker default tier is **Opus 4.8 1M** (`claude-opus-4-8[1m]`), with Opus 5 as the first upshift rung; Fable by election only after a verified failure | `P2-T15` names that ladder; `P2-T17` sets it in `model-help` |
| **PD3** | D18 **approved in full** | `P1-T6` is unconditional; the "D18:" bullets in Phase 2 all apply |
| **PD4** | All three renames ship in this release | `P2-T9` → `implement_inline`, `P2-T10`/`P2-T28` → `implement`, and `P2-T29` adds the two alias stubs |

Full records with rationale and trade-offs: design.md → Technical Decisions → Resolved
Decisions.

## Implementation Strategy

### Phase Rationale

Ordering is forced by three constraints, not preference:

1. **The relocation must precede the split.** Progressive disclosure needs a stable
   relative-link root (`../../docs/reference/...`), so D1 lands before D2 or every supporting
   link is written twice.
2. **Each file is edited once.** design.md's largest risk is the blast radius, mitigated by
   "the two changes coincide per file." So Phase 2 applies *everything* a stage file needs —
   reshape (D2), beads removal (D4), the instruction reversals, and that file's own content
   decisions (D5/D6/D7/D13/D14/D15/D18) — in a single pass per file. Deliberately **not**
   structured as a de-beads sweep followed by a reshape sweep.
3. **Consumers come last.** `forge` and `help` read the pipeline's shape and naming, so they
   are rewritten after the shape is final. Same for the guides and the changelog.

New capabilities (D8, D10, D11) sit in Phase 3 because they are new files — no double-edit
risk — and because D8c's bootstrap wires into the D11 hook, so they land together.

### Testing Strategy

This is a prompt library: there is no unit-test suite, and inventing one is out of scope. The
verification surface is three mechanical gates plus one human gate, all established or
repaired in Phase 0:

- **`./scripts/lint <files>`** — per-file markdown gate. Trustworthy only after `P0-T4`
  (D16), which is why that fix is in Phase 0 rather than batched with the other small edits.
- **`claude plugin details wb`** — component inventory and projected token cost. This is the
  direct measurement of D2's headline metric; `P0-T2` captures the baseline so the Phase 2
  exit can compare against a recorded number instead of a line-count proxy.
- **`claude plugin tag --dry-run <path>`** — validates that `plugin.json` and the enclosing
  marketplace entry agree, and warns when a `CLAUDE.md` sits at the plugin root where it will
  not be loaded. Both are assertions this plan makes (D1, D17), so the tool checks them.
- **Grep audits** — the beads-removal criteria are stated as greps in design.md's Success
  Criteria; each phase's exit runs the ones for its scope.
- **A `--plugin-dir` smoke session** — the only way to confirm a skill actually loads, its
  on-demand supporting files read without a permission prompt (A4), and an alias stub resolves
  (A5). Human-run, at the Phase 0 checkpoint and again at the Phase 4 checkpoint.

Task sizing follows D15: each task is annotated with a rough tool-call projection, and
anything projecting past ~50 calls is split at a natural seam here rather than discovered
mid-execution.

---

## Phase 0: Resolve the load-bearing unknown, and make the gates trustworthy

### Objective

Prove the `plugin/` layout actually loads before committing 14 files of reshaping to it, and
repair the one gate every later phase depends on.

### Prerequisites

- [x] research.md validated (research.md `status: complete`, all 7 Open Questions closed)
- [x] design.md approved (design.md `status: approved`, 2026-09-08)
- [x] PD2, PD3, PD4 resolved 2026-09-08 — nothing is gated

### Why this phase exists

D2 is the largest work item in the plan and rests entirely on an assumption we have not
tested in *our* install: that a plugin whose runtime lives in a `plugin/` subdirectory, with
skills split across on-demand supporting files, loads correctly under our marketplace
identity (`wb@thescubageek-workbench`) and under `--plugin-dir`. Upstream proves the layout
works for upstream. If it does not work here, D1 and D2 are both invalidated and the plan
reorders around keeping the flat layout — which is cheap to learn now and expensive to learn
after fourteen files.

This is a throwaway probe on a scratch path, not the real relocation. It is deleted at the end
of the phase.

### Tasks

- [x] **P0-T1** — Build a throwaway minimal plugin at `/tmp/wb-probe/` mirroring the target
      layout: `.claude-plugin/marketplace.json` with `"source": "./plugin"`,
      `plugin/.claude-plugin/plugin.json`, and one skill
      `plugin/skills/probe/SKILL.md` carrying `allowed-tools: Read` plus a relative link to
      `plugin/skills/probe/templates.md` and one to `plugin/docs/reference/probe-ref.md`.
      Add a second directory `plugin/skills/probe_old/SKILL.md` as an alias stub that reads
      the canonical skill. (~15 calls) (completed 2026-09-08 12:24)
- [x] **P0-T2** — Record the **baseline** measurements, verbatim, into
      `thoughts/2026-09-08-baseline-measurements.md`: full `claude plugin details wb` output
      (component inventory, always-on total, per-component on-invoke table), and the current
      per-stage `wc -l` for all 16 `commands/*.md`. Phase 2's exit compares against this file.
      (~5 calls) (completed 2026-09-08 12:23)
- [x] **P0-T3** — Run the probe: `claude plugin marketplace add /tmp/wb-probe`, then
      `claude plugin details` on it, then `claude plugin tag --dry-run /tmp/wb-probe`.
      Record for each: does the plugin resolve from a `./plugin` source; does the skill
      enumerate; does `tag --dry-run` report manifest agreement and emit **no** root-CLAUDE.md
      warning. Then remove the probe marketplace. (~10 calls) (completed 2026-09-08 12:27)
- [x] **P0-T4** — Fix `scripts/lint` (D16): move `exit 1` out of the inner
      `if [ -z "$AUTO_FIX" ]` block in the Final status section so it runs whenever
      `ISSUES_FOUND` is true, and add the "some issues could not be auto-fixed" message on the
      `--fix` path. Leave `scripts/lint-hook` exiting 0. (~6 calls) (completed 2026-09-08 12:29)
- [x] **P0-T6** — Exclude `.context/` from `./scripts/lint --all`: add
      `-not -path "./.context/*"` to the `find` exclusion list in the `LINT_ALL` branch,
      beside the existing `node_modules`/`vendor`/`tmp` entries. Authorized 2026-09-08 as a
      scope addition (design.md → Resolved Decisions) after `P0-T4` surfaced that `--all`
      returns 84 findings, all of them in the gitignored upstream export and none in anything
      we author — which would leave every later phase's "lint --all is clean" criterion red.
      Do **not** rebuild the file list from `git ls-files`: `docs/plans/` is gitignored here
      and would drop out of coverage. (~5 calls) (completed 2026-09-08 12:42)
- [x] **P0-T5** — Delete `/tmp/wb-probe/`. Record the probe's verdict in
      `thoughts/2026-09-08-baseline-measurements.md` under a "Layout probe" heading, including
      whether A4 (`allowed-tools: Read` suppresses the permission prompt) and A5 (alias stub
      resolves) were observable from the CLI alone or need the human smoke session. (~5 calls) (completed 2026-09-08 12:43)

### Success Criteria

#### Automated Verification

- [x] `./scripts/lint scripts/lint` — clean (the script is not markdown; lint the touched
      markdown only) — the touched markdown is
      `thoughts/2026-09-08-baseline-measurements.md`: clean
- [x] Fixture check, D16: a markdown file with an unfixable finding returns exit **1** from
      `./scripts/lint <file>` **and** exit **1** from `./scripts/lint --fix <file>`; a clean
      file returns 0 from both — all four cases pass; recorded in the baseline file
- [x] ~~`claude plugin tag --dry-run /tmp/wb-probe`~~ **`--dry-run /tmp/wb-probe/plugin`**
      exits 0 and reports the probe's `plugin.json` and marketplace entry agreeing — the
      command as written fails ("No plugin manifest found"); `tag` takes the directory
      holding `.claude-plugin/plugin.json`, and requires a git repository. Corrected form
      passes; see the baseline file's "Three corrections to this plan's own gate commands"
- [x] `thoughts/2026-09-08-baseline-measurements.md` exists and contains a
      `Projected token cost` block and a 16-row line-count table
- [x] `P0-T6`: `./scripts/lint --all` exits **0** with no findings, and
      `grep -c 'not -path "./.context/\*"' scripts/lint` → 1 — verified; the 16
      `commands/*.md` and the 6 plan documents are still covered

#### Manual Verification

- [x] A `claude --plugin-dir /tmp/wb-probe/plugin` session lists the `probe` skill, and
      invoking it reads `templates.md` and `plugin/docs/reference/probe-ref.md` **without a
      permission prompt** (settles A4) — confirmed 2026-09-08: `NO PROMPT` on both reads,
      marker `PROBE-REF-RESOLVED` echoed. **A4 Validated**, both halves
- [x] In that session, invoking `probe_old` announces the rename once and then behaves as
      `probe` (settles A5) — confirmed 2026-09-08: announced once, then read 2 files.
      **A5 Validated**
- [x] Human confirms the verdict: proceed with D1/D2 as designed, or stop and re-plan —
      **proceed**, confirmed 2026-09-08

### Modified Files

- `scripts/lint` — exit-code fix (D16, `P0-T4`); `.context/` excluded from `--all` (`P0-T6`)
- `docs/plans/2026-09-08-upstream-fable-merge/thoughts/2026-09-08-baseline-measurements.md` — new
- `/tmp/wb-probe/**` — throwaway, deleted by `P0-T5`

### ⛔ CHECKPOINT: Phase 0 Complete

Before Phase 1:

1. Every Phase 0 checkbox is `[x]` — **yes**, `P0-T1`–`P0-T6`
2. The layout probe returned a verdict and it is recorded — **proceed with D1/D2**;
   `thoughts/2026-09-08-baseline-measurements.md` → "Layout probe"
3. The lint fixture check passes in both modes — **yes**, plain 1 / `--fix` 1 on an
   unfixable finding, 0 / 0 on a clean file
4. Baselines are captured — **yes**; the Phase 2 bar is ≤ ~59.4k tok against a
   fourteen-stage baseline of ~84.9k
5. Run `/wb:update_status` to reconcile counters (sole writer, D5)

**If the probe failed**, stop. D1 and D2 are invalidated and the plan needs re-planning
before any file moves. Every later phase assumes this verdict.

**Do not proceed without human confirmation.**

---

## Phase 1: Relocate the tree, pin the sub-agents, drop the auto-loaded stale file

### Objective

Establish the shipped/maintainer boundary and land the changes that touch no stage-file prose,
so Phase 2 opens against a stable layout.

### Prerequisites

- [x] Phase 0 complete, probe verdict positive (2026-09-08)

### Changes Required

#### 1. The relocation (D1)

Move the shipped runtime under `plugin/`: `agents/`, `commands/`, `hooks/`, `scripts/`,
`skills/`, and `.claude-plugin/plugin.json`. Root keeps `.claude-plugin/marketplace.json`
with `"source": "./plugin"`. Root `docs/` stays where it is and becomes maintainer-only —
never shipped. Create `plugin/docs/reference/` as the shipped reference directory.

`commands/` moves as-is in this phase; its contents are reshaped in Phase 2. Moving and
reshaping in one step would make the diff unreadable and defeat per-file review.

#### 2. Sub-agent tiers (D3)

Each of the six files in `plugin/agents/` gains `model:`, `effort:` where the tier supports
it, and `maxTurns:` on the search agents. Values follow design.md D3 and `model-help`'s
existing economics — this is the free lever, pinned at the definition. Never annotate
`effort` on a haiku agent.

#### 3. `AGENTS.md` (D19, first half)

Delete it. Fold anything worth keeping into `CLAUDE.md`'s session protocol, and repoint the
two inbound references at `CLAUDE.md:241` and `docs/workbench-workflow-guide.md:893`.
Independent of beads removal because its only inbound references are documentation links.

### Tasks

- [x] **P1-T1** — Create `plugin/`; `git mv` `agents/`, `commands/`, `hooks/`, `scripts/`,
      `skills/` into it; `git mv .claude-plugin/plugin.json plugin/.claude-plugin/plugin.json`.
      Leave root `.claude-plugin/marketplace.json` in place. (~12 calls) (completed 2026-09-08 13:05)
- [x] **P1-T2** — Set `"source": "./plugin"` in `.claude-plugin/marketplace.json`. Update
      every `${CLAUDE_PLUGIN_ROOT}`-relative path in `plugin/.claude-plugin/plugin.json` that
      no longer resolves, and the `./scripts/lint` invocations in `CLAUDE.md` and `README.md`
      to `./plugin/scripts/lint`. (~10 calls) (completed 2026-09-08 13:07)
- [x] **P1-T3** — Create `plugin/docs/reference/` with a `README.md` stating what belongs
      there: shipped, runtime-referenced material that skills link to instead of restating,
      and nothing else (D19's second half, the shipped side). (~4 calls) (completed 2026-09-08 13:09)
- [x] **P1-T4** — Add `model:`/`effort:`/`maxTurns:` frontmatter to all six
      `plugin/agents/*.md` per D3. (~10 calls) (completed 2026-09-08 13:11)
- [x] **P1-T5** — Delete `AGENTS.md`; fold its keepable content into `CLAUDE.md`'s session
      protocol; repoint the two inbound references. Do **not** carry over any `bd` command —
      those die with D4. (~8 calls) (completed 2026-09-08 13:14)
- [x] **P1-T7** — The two implementation guardrails (D20). Add a `### Extras and edits`
      section immediately after the existing scope block in both
      `plugin/commands/implement_tasks.md` and `plugin/commands/implement_coordinated.md`,
      carrying the surgical-edit rule, the follow-ups-not-fixes rule, and the completeness
      clause ("this is about extras only: implement every behavior the task asks for,
      completely"). Placed here rather than in Phase 2 for two reasons: the scope block is
      currently a dead end that ends in "STOP and ask" with nothing after it, and these
      guardrails should be in the tree **before** the 28-task Phase 2 pass rather than after
      it. The text carries through Phase 2's reshape and becomes `task-worker.md`'s
      constraints at `P2-T11`. Content only — no structural change, so it does not conflict
      with the edit-once rule. (~10 calls) (completed 2026-09-08 13:17)
- [x] **P1-T6** — Rewrite `CLAUDE.md`'s "Working with Commands" list and its
      "Command Structure Patterns" barrier example per D18: one marker per real
      synchronization point with its reason stated; decision points name the decision instead
      of instructing thinking depth. This lands **before** any stage file is trimmed, because
      the list is what regenerates the pattern. Do not touch barrier or scope-block volume.
      (~10 calls) (completed 2026-09-08 13:19)

### Success Criteria

#### Automated Verification

- [x] `test -d plugin/skills && test -f plugin/.claude-plugin/plugin.json && test -f .claude-plugin/marketplace.json`
- [x] `test ! -e AGENTS.md`
- [x] `grep -c '"source": "./plugin"' .claude-plugin/marketplace.json` → 1
- [x] `claude plugin tag --dry-run plugin/` exits 0, reports manifest agreement, and emits
      **no** root-`CLAUDE.md` warning (the warning present at `b902566` is itself the D1
      assertion under test) — **the warning is gone.** Run on a clean tree after the phase
      commit, per `P0-T3`'s finding that `tag` refuses a dirty tree
- [ ] `grep -rn "AGENTS.md" CLAUDE.md docs/ plugin/ | grep -v docs/plans` → **2 hits
      remain**, both in `docs/beads-integration-learnings.md` (`:156`, `:193`), which `P2-T27`
      deletes. `P1-T5` names exactly two inbound references to repoint (`CLAUDE.md:241`,
      `docs/workbench-workflow-guide.md:893`) and both are done; the criterion over-reaches its
      own task by also covering a file scheduled for deletion two phases later. Clears at
      `P2-T27` with no further work
- [x] `grep -c 'model:' plugin/agents/*.md` → 1 per file; no `effort:` on a haiku agent —
      but note this is a **spelling check, not a behaviour check**: neither
      `claude plugin validate` nor `claude plugin details` inspects agent frontmatter at all
      (proven by planting `model: totally-not-a-model` plus a nonsense key — both passed
      silently and the agent still enumerated). What does validate it is the harness itself;
      see the Implementation Note dated 2026-09-08 on `effort`/`maxTurns`
- [x] `./plugin/scripts/lint --all` — no new findings against the Phase 0 baseline: exit 0,
      **0 findings** (the baseline is 0 after `P0-T6`)
- [x] `grep -c 'Extras and edits' plugin/commands/implement_tasks.md plugin/commands/implement_coordinated.md` → 1 each
- [x] `grep -c 'completely' plugin/commands/implement_tasks.md` → 1 or more (the completeness clause)
- [x] `grep -c 'think deeply' CLAUDE.md` → 0

#### Manual Verification

- [x] A `claude --plugin-dir <repo>/plugin` session enumerates the same skill and agent set
      as the Phase 0 baseline recorded — the move changed paths, not inventory. Verified by the
      CLI equivalent, `claude --plugin-dir plugin plugin details wb`: **31 skills, 6 agents,
      2 hooks**, identical to the baseline. **Confirmed live 2026-09-08**: in a
      `claude --plugin-dir <repo>/plugin` session the `/wb:` menu offered the full command
      set and `/wb:help` executed, which proves a body loads *and runs* from the relocated
      path rather than merely being enumerated. The version served is the working tree, not
      the marketplace cache: the same flag and path reported `wb 1.12.5` from the CLI, and
      `--plugin-dir` reads from disk by definition — the 1.12.4 fallback seen earlier
      happened only because the flag pointed at the repository root, which no longer holds a
      manifest
- [x] `git log --stat` for this phase reads as moves plus frontmatter, with no prose changes
      to any `commands/*.md` body — verified mechanically with `git show -M --numstat`:
      **48 renames, of which 40 are byte-identical moves.** The 8 with content changes are the
      6 agents at **+2/−0** each (frontmatter only) and the 2 implementation commands at
      **+16/−0** each (`P1-T7`'s `### Extras and edits`, which the task defines as content-only
      and additive). **Every command body is `−0`** — nothing was reworded or lost, only added

### Modified Files

- `plugin/**` — everything relocated
- `.claude-plugin/marketplace.json` — `source`
- `plugin/.claude-plugin/plugin.json` — hook paths
- `plugin/agents/*.md` (6) — frontmatter tiers
- `plugin/docs/reference/README.md` — new
- `AGENTS.md` — deleted
- `plugin/commands/{implement_tasks,implement_coordinated}.md` — D20 guardrails (content only)
- `CLAUDE.md` — session protocol absorbed; lint path; D18 root rewrite if approved
- `README.md`, `docs/workbench-workflow-guide.md` — path and reference repointing

### ⛔ CHECKPOINT: Phase 1 Complete

1. Every Phase 1 checkbox is `[x]` — **all seven tasks, yes.** One *criterion* is still
   `[ ]`: the `AGENTS.md` grep, whose two remaining hits are in a file `P2-T27` deletes. Left
   unchecked deliberately rather than marked done, because as literally written it is not met.
   It needs no work — it clears when `P2-T27` runs
2. `claude plugin tag --dry-run plugin/` is clean and the CLAUDE.md warning is gone — **yes**
3. A `--plugin-dir` session still loads the full inventory — **yes**, 31/6/2
4. Run `/wb:update_status`

**Do not proceed without human confirmation.**

---

## Phase 2: The per-file pass — reshape and de-beads each stage in one edit

### Objective

Turn each monolithic command into a `SKILL.md` plus on-demand supporting files, remove beads
from it, reverse the instructions that make its markdown surface inert, and apply that file's
own content decisions — all in a single edit per file.

### Prerequisites

- [x] Phase 1 complete (2026-09-08)
- [x] The Phase 0 baseline file exists — this phase's exit measures against it
      (`thoughts/2026-09-08-baseline-measurements.md`; the bar is ≤ ~59.4k tok)

### Changes Required

Every task in this phase applies the same recipe to one file. The split boundaries are given
as **headings, not line numbers**, because line numbers shift as soon as the first edit in a
file lands.

**The recipe, per file:**

1. `plugin/commands/<name>.md` → `plugin/skills/<name>/SKILL.md`; keep frontmatter, add
   `allowed-tools: Read`, add the supporting-file manifest with upstream's wording ("read each
   when its step directs you to — never paraphrase from memory").
2. Move the output-document template block → `templates.md`.
3. Move `Task({...})` spawn blocks and agent prompt text → `sub-agent-prompts.md`.
4. Move tail reference material (`## Important Guidelines`, `## Configuration`,
   `## Error Handling`, `## Resume Logic`, convention tables, troubleshooting) →
   `reference.md`.
5. **Delete** every beads region: `bd` blocks, `$BEADS_MODE`/`$BEADS_AVAILABLE` branches,
   fast-fail gates, `beads_*` frontmatter blocks (D4).
6. **Reverse**, don't just delete, the markdown-inert instructions — the "tracked ONLY in
   beads" / "NEVER treat markdown as source of truth" annotations become the checkbox rule
   (D4). Their exact sites are enumerated in design.md → In Scope.
7. Apply that file's content decisions (listed per task below).
8. `./plugin/scripts/lint` the new files — **per task**. Commit **per cluster**, not per
   task: decided 2026-09-08 (design.md → Resolved Decisions), refining D14's one-task-one-commit
   rule for this phase only, because the reviewable unit here is the cluster. Phases 0, 1, 3
   and 4 remain one commit per task.

### Tasks

**Research cluster**

- [x] **P2-T1** — `create_research`: template = `## Research Question` → `## Next Steps`;
      prompts = `## Parallel Research Strategy`; reference = `## Important Notes` and
      `## Configuration`. Content: D6
      (Open Questions become a markdown table with `Q1` local IDs, not `bd create`); D8c (read
      `.claude/wb/knowledge.md` at Step 1); D18 bullets at `:80,:83,:214`. **Reference scope
      amended 2026-09-08**: `## Important Notes` joins `## Configuration` — the recipe's step 4
      already calls for moving tail reference material, and this was the only stage in the phase
      whose spec omitted it. See design.md → Resolved Decisions. (~30 calls) (completed 2026-09-08 15:22, amended 16:05)
- [x] **P2-T2** — `create_product_research`: template = `## Feature Overview` →
      `## Next Steps`; prompts = `## Parallel Research Strategy`; reference =
      `## Audience: Product Managers`, `## Workflow Position`, `## Important Notes`,
      `## Configuration`. Content: same as `P2-T1`; D18 bullets at `:81,:90,:216`. (~30 calls) (completed 2026-09-08 15:34)
- [x] **P2-T3** — `docs/product-research-claude-desktop.md`: the portable mirror. Bring it
      back into parity with `P2-T2` and add a non-normative header (D19's second half) marking
      it a maintainer-facing portable copy, not a rules source. Stays under `docs/`. (~15 calls) (completed 2026-09-08 15:41)

**Design cluster**

- [ ] **P2-T4** — `create_design`: template = `## Problem Statement` → `## References`;
      prompts = the Step 2 `Task({...})` blocks; reference = `## Important Guidelines`,
      `## Configuration`. Content: D6 (Assumptions and Pending Decisions tables lose their
      `Beads ID` column, gain local IDs; the cold-start check reads markdown records, not
      `bd list`); D10 (consume an `explore_design` decision record when present, formalize
      rather than regenerate); D18 bullets at `:91,:165,:188`. (~30 calls)
- [ ] **P2-T5** — `create_project`: template file is large — it embeds four artifact
      skeletons (`## Overview`→`## Git Information` README, `## Research Question`→
      `## References` research, `## Problem Statement`→`## References` design,
      `## Progress Overview`→`## 🔗 Quick Reference` tasks). All four → **one** `templates.md`
      under four named headings (`## README.md Template`, `## research.md Template`,
      `## design.md Template`, `## tasks.md Template`), and each of Step 4's four creation
      sub-steps directs a read of **its section by name**, not the whole file — decided
      2026-09-08, see design.md → Resolved Decisions;
      reference = `## Important Notes`, `## Error Handling`. Content: D4 (the generated
      tasks.md skeleton gets the checkbox convention and `task_tracking:` frontmatter; delete
      the `:343` note conceding checkboxes are documentation-only); D8a (the generated plan
      directory now includes `journal.md`). (~35 calls)

**Execution-planning cluster**

- [ ] **P2-T6** — `create_execution` → `create_tasks`, the rewrite (D9). Directory becomes
      `plugin/skills/create_tasks/`. Template = `## Overview` → `## 🔗 Quick Reference`.
      **Delete** `## Beads Issue Tracking` wholesale and all of Step 5's `bd create`/`bd dep
      add` choreography. Reference = `## Important Guidelines`, `## Task Granularity`,
      `## Configuration`. Content: D4 + D7 (the generated tasks.md carries a markdown task
      table with local IDs and document-order execution; a `Depends on:` field only where a
      task genuinely branches); D15 (size tasks by projected tool calls, split past ~50 at a
      natural seam — replacing the "1-4 hours" rule); D5 (the phase checkpoint delegates
      counter updates to `update_status` instead of editing `current_phase` inline);
      D18 bullets at `:69,:154,:175`. Projected past 50 calls, so split — see `P2-T7`.
      (~40 calls)
- [ ] **P2-T7** — `create_tasks` supporting files: write `templates.md` (the new tasks.md
      skeleton in the markdown-checkbox convention), `sub-agent-prompts.md` (the three Step 2
      analysis agents), and `examples.md`. Split from `P2-T6` at the SKILL/supporting seam per
      D15. (~25 calls)
- [ ] **P2-T8** — `create_execution` alias stub (D9): `plugin/skills/create_execution/` with a
      stub `SKILL.md` (`disable-model-invocation: true`) that announces the rename once and
      then reads the canonical skill, plus one pointer file per supporting file so a stale
      cached body still resolves its reads. (~10 calls)

**Implementation cluster**

- [ ] **P2-T9** — `implement_tasks` → **`implement_inline`** (PD4): directory becomes
      `plugin/skills/implement_inline/`, frontmatter `name:` changes with it. No output template. Reference = `## Handling Mismatches`,
      `## Resume Logic`, `## TDD Best Practices`, `## Special Considerations`,
      `## Error Handling`, `## Important Guidelines`, `## Configuration` (~180 lines).
      Carry `P1-T7`'s `### Extras and edits` section through the reshape — it stays beside the
      scope block, not in `reference.md`. Content: D4 (reverse `:315-317` and `:684-686` — flipping the checkbox *is* the tracking
      act now); D5 (defer counters to `update_status`); D8a (open a journal entry at task
      start, close it at completion); D18 bullet at `:117`. (~35 calls)
- [ ] **P2-T10** — `implement_coordinated` → **`implement`** (PD4), part 1 — **the rename and
      structural split only**: directory becomes `plugin/skills/implement/`, frontmatter
      `name:` changes with it; its description must carry the discrimination against
      `implement_inline` ("worker agents, main context kept clean" vs "inline on the current
      session model"), since `implement` is now the most generic trigger word in the menu. prompts =
      `## Your Task` → `## Expected Output` (the worker prompt template); templates = the
      Modified-Files fragment, the manual-verification checklist message, and the
      "Phase Complete" report; reference = `## Evolution from implement_tasks`,
      `## Resume Logic`, `## Advantages Over Sequential Implementation`,
      `## Migration from implement_tasks`, `## Important Guidelines`, `## Configuration`.
      **Delete** `## Helper Functions` (the `determineModel()` regex) per D13. Do **not** touch
      the beads gates in this task. (~30 calls)
- [ ] **P2-T28** — `implement` (formerly `implement_coordinated`), part 2 — **the tracker
      gates**: this file's beads
      coupling is not one section, it recurs in Steps 2, 4, 6, 7, 8, and 9 (the availability
      probe and stop-and-wait block, `bd ready` task selection, the post-worker `bd show`
      verification, phase-completion `bd show`, the milestone close, and the `bd sync` +
      `git add .beads/` step). Remove all of them and re-derive each from the checkbox surface
      (D4), deferring counters to `update_status` (D5) and opening/closing journal entries
      (D8a). Split from `P2-T10` on tool-call budget per D15 — same file, disjoint regions,
      sequential; the edit-once principle still holds per region. (~30 calls)
- [ ] **P2-T11** — `plugin/agents/task-worker.md`: new. The worker contract currently inlined
      in `implement_coordinated`'s prompt template becomes a real agent definition with
      `tools`, `skills: [tdd-discipline]`, and `maxTurns`, and names `/wb:implement` as its
      spawner (PD4). Carries D20's surgical-edit and
      follow-ups-not-fixes constraints (from `P1-T7`) — this agent file is their primary home,
      and the coordinated path inherits them from here rather than restating them. Carries the
      D14 rule that workers do **not** commit, and that closing its own task is its final act — which is what makes
      truncation detectable. (~15 calls)

**Validation and status cluster**

- [ ] **P2-T12** — `validate_execution`: template = `## Executive Summary` →
      `## Validation Completed`; prompts = the Step 2 `Task({...})` blocks; reference =
      `## Important Guidelines`, `## Relationship to Other Commands`, `## Configuration`.
      Content: D4 (reverse `:63`, `:203`, `:379` — checkbox state becomes the completion
      signal it reads, not a thing to ignore). (~30 calls)
- [ ] **P2-T13** — `validate_project`: template = `## Summary` → `## Validation Details`, plus
      the `## Error Messages` canonical formats; reference = **`## Validation Checklist`** (the
      8-category criteria list — it is read by Step 3, not executed inline) and
      **`## Validation Rules`** (the per-check pseudocode), plus `## Important Guidelines` and
      `## Configuration`. Those two sections make this the largest `reference.md` in the tree
      at roughly 255 lines, so the SKILL.md drops to about 130. Content: D4 (delete the Beads
      Integration and Beads State Alignment checklist categories, the Step 2 beads-state
      validation, the Beads Validation pseudocode, and the `beads_*` required-frontmatter
      list); D6 (validate the markdown planning-record sections instead of orphaned issue
      IDs). (~30 calls)
- [ ] **P2-T14** — `update_status`: template = the message and fragment set, which is larger
      than it looks — the "Current Status Analysis" plan message, the per-file frontmatter
      update fragments for research/design/tasks, the success summary, and the three
      Error Handling message templates (~145 lines total); reference =
      `## Status Transition Logic`, `## Smart Status Detection`, `## Error Handling`,
      `## Important Notes`, `## Configuration`. Content: D4 + D5 — this is the file that
      inverts most sharply. Reverse `:110`, `:371`, `:403` ("NEVER check markdown checkboxes")
      into the reconciliation mechanism: count `[x]`/`[ ]`, compare against frontmatter
      counters, report drift, reconcile to the counts. State the sole-writer rule here.
      (~30 calls)

**Execution-path decisions** *(same cluster's files, split out per D15)*

- [ ] **P2-T15** — The single worker tier-rule statement (D13), in
      `plugin/skills/implement/SKILL.md` at the point of spawn. **PD2 resolved 2026-09-08**:
      the ladder is haiku for mechanical only · **Opus 4.8 1M (`claude-opus-4-8[1m]`)
      default** · Opus 5 on coordinator judgment for architectural or cross-cutting tasks ·
      Fable never as a first spawn, only as an explicit election after a verified failure,
      always at `effort: high`. Use the `[1m]` variant for the default, not base
      `claude-opus-4-8`. Never annotate `effort` on a haiku spawn. Every other restatement of the tiers becomes a
      pointer to this one — including `reference.md` and the skill README. (~20 calls)
- [ ] **P2-T16** — The failure path (D14): replace the two-identical-retry block with the
      truncation-vs-failure discrimination. Inspect the working tree to tell them apart;
      finish or re-delegate the remaining slice for truncation; escalate one rung for a
      verified failure; exactly one escalation, then the phase checkpoint's blocking list.
      Move the commit to the coordinator, after the verifier passes. Update
      `plugin/agents/task-verifier.md` to check scope against the working tree rather than a
      caller-supplied base ref, since workers no longer commit. (~25 calls)
- [ ] **P2-T29** — The two `implement_*` alias stubs (PD4), mirroring `P2-T8`:
      `plugin/skills/implement_coordinated/` → `implement` and
      `plugin/skills/implement_tasks/` → `implement_inline`. Each is a stub `SKILL.md`
      (`disable-model-invocation: true`) that announces the rename once and then reads the
      canonical skill, plus one pointer file per supporting file the canonical skill has, so a
      session holding a stale cached body still resolves its reads. (~15 calls)
- [ ] **P2-T17** — `model-help` (D12): add the upshift-ladder semantics — a named next-tier-up
      per phase, entered only by explicit election, never by a baseline. Rename the
      `create_execution` row to `create_tasks`, the `implement_tasks` row to
      `implement_inline`, and add an `implement` row (PD4). Set the worker ladder per PD2 as
      resolved: **Opus 4.8 1M default**, Opus 5 upshift, Fable by election only. **Also add
      the 1M variants to the roster at `:22`** — it currently names four models with no 1M
      forms, so the ladder would otherwise reference a model this authority does not list.
      State which tier's 1M form is the default so roster and ladder cannot drift. Keep the switch-cost
      rule and the advise-never-auto-switch policy verbatim. (~20 calls)

**Handoff cluster**

- [ ] **P2-T18** — `create_handoff`: template = `## Quick Start` →
      `## Handoff Verification`; reference = `## Purpose`, `## Important Guidelines`,
      `## Relationship to Other Commands`, `## Configuration`. Content: D4 (drop `bd sync` and
      the `git add .beads/` block); D8a (append a journal pointer to the handoff it wrote);
      D8b (review the session's knowledge candidates against the qualification rule);
      D21 (added 2026-09-08 — a handoff that crosses a machine is one of the two triggers that
      promote a plan directory into git, so the handoff step names the `git add -f` and the
      branch push as the transport); D18 bullet at `:89`. (~32 calls)
- [ ] **P2-T19** — `resume_handoff`: reference = `## Purpose`, `## Validation Steps`,
      `## Important Guidelines`, `## Relationship to Other Commands`, `## Error Handling`,
      `## Configuration`; template = `## Output Format`. Content: D4 (drop the beads state
      reload and `:248`'s never-checkboxes rule); D8c (read the journal tail alongside the
      handoff, and read the knowledge file); D18 bullet at `:87`. (~30 calls)

**Remaining stages**

- [ ] **P2-T20** — `create_mockup`: templates = `## UI Research Summary`,
      `## Overview`→`## Needs Validation`, `## Feature: [Name]`→`## Design Principles
      Emerging` (~300 lines); prompts = the Step 2 research agents; reference =
      `## Purpose`, `## Output Files`, `## Important Guidelines`,
      `## Relationship to Other Commands`. Content: D6 (`UI Q:` records become markdown with
      `UIQ1` IDs); D18 bullet at `:174`. (~30 calls)
- [ ] **P2-T21** — `resolve_questions`: reference = `## Operating Principles`,
      `## Edge Cases`; template = `## Persistence Format Reference`; **examples.md** =
      `## Example Invocation` (a full worked dialogue — the clearest `examples.md` candidate in
      the tree). Content: D6 — delete the beads branch (Step 2 Source B, the
      `bd comments`/`bd close` block in Step 4d, and the Edge Cases line) and keep the markdown
      walk, which becomes the only path. While here, de-duplicate: Step 4d restates the
      decision-record formats that `## Persistence Format Reference` already defines
      canonically — point at the template instead of repeating it. (~25 calls)
- [ ] **P2-T22** — `mockup-iteration` skill: drop its four `bd create` sites for
      `UI Q:`/`UI Assumption:` records; use D6's markdown records. Add
      `user-invocable: false` where design.md's D2 calls for it on background skills, and to
      `project-structure`, `status-sync`, `tdd-discipline`,
      `verification-before-completion`. (~20 calls)
- [ ] **P2-T23** — `status-sync` (D5): add the frontmatter-drift indicator — compare counters
      against actual `[x]`/`[ ]` counts at phase end and session end, and point at
      `/wb:update_status` on mismatch. Drop the `bd sync` reminder. (~12 calls)
- [ ] **P2-T24** — `project-structure` (D4): add the "No external tracker" section stating
      where status lives — checkboxes in tasks.md, counters as a cache, git as the durable
      record. This is the doctrine's home, mirroring where the sibling workflow puts it.
      Also carry **D21** here (added 2026-09-08): plan directories are transient by default,
      promoted into git with `git add -f` when the work must cross a session or machine or when
      the branch is about to merge, and anything that must outlive an abandoned branch belongs
      in `.claude/wb/knowledge.md` rather than a preserved plan directory. (~14 calls)
- [ ] **P2-T25** — `daily-digest` and `fetch-issues`: drop their beads source blocks and
      `bd` reads; both already treat beads as optional, so this is deletion plus a line
      about reading plan state from checkboxes. D18 bullets at
      `daily-digest:135`, `fetch-issues:135`. (~15 calls)
- [ ] **P2-T26** — Delete `docs/beads-fast-fail.md` and `docs/beads-stealth-mode.md` (D19).
      Runs **after** `P2-T1`–`P2-T25` so the fifteen inbound links are already gone. (~5 calls)
- [ ] **P2-T27** — Delete `docs/beads-integration-learnings.md` (D19). Separate task from
      `P2-T26` because it is orphaned rather than linked, and because design.md's D8 rationale
      cites it — confirm that citation reads as past-tense before deleting. (~5 calls)

### Success Criteria

#### Automated Verification

- [ ] `grep -rn "bd \|BEADS_MODE\|BEADS_AVAILABLE\|beads_epic\|/beads:" plugin/` → **no hits**
- [ ] `grep -rln "NEVER treat markdown as source of truth\|tracked ONLY in beads\|NEVER check markdown checkboxes" plugin/` → no hits
- [ ] All six directories exist — canonicals `create_tasks`, `implement`, `implement_inline`
      and aliases `create_execution`, `implement_coordinated`, `implement_tasks`
- [ ] `test ! -e docs/beads-fast-fail.md -a ! -e docs/beads-stealth-mode.md -a ! -e docs/beads-integration-learnings.md`
- [ ] `grep -L "allowed-tools" plugin/skills/*/SKILL.md` — no workflow skill missing it
- [ ] `grep -c 'user-invocable: false' plugin/skills/*/SKILL.md` — set on every background
      discipline skill
- [ ] `grep -rn "determineModel" plugin/` → no hits (D13)
- [ ] Exactly one statement of the worker tier rule:
      `grep -rln "Haiku:.*Sonnet:.*Opus:" plugin/` returns one file
- [ ] `./plugin/scripts/lint --all` — clean, or no new findings vs the Phase 0 baseline
- [ ] `grep -rn "think deeply\|ultrathink" plugin/ CLAUDE.md` → no hits
- [ ] **The headline metric**: `claude plugin details wb` on-invoke total for the fourteen
      stages is **at least 30% below** the Phase 0 baseline recorded in
      `thoughts/2026-09-08-baseline-measurements.md`, with no stage's content deleted
      (supporting files account for the remainder)

#### Manual Verification

- [ ] A `--plugin-dir` session invokes `create_tasks`, and its on-demand `templates.md` read
      happens without a permission prompt
- [ ] Each of the three aliases prints its deprecation notice once and then behaves
      identically to its canonical skill
- [ ] Spot-read three reshaped skills: no supporting file is referenced that does not exist,
      and no SKILL.md paraphrases content that moved
- [ ] Human confirms the token-cost reduction is real reduction, not content loss

### Modified Files

- `plugin/skills/**` — all 16 stages reshaped; `create_tasks/` added; `create_execution/`
  becomes an alias
- `plugin/agents/task-worker.md` — new; `task-verifier.md` — working-tree scope check
- `plugin/skills/{model-help,status-sync,project-structure,mockup-iteration,daily-digest,fetch-issues}/`
- `docs/product-research-claude-desktop.md` — parity + non-normative header
- `docs/beads-fast-fail.md`, `docs/beads-stealth-mode.md`,
  `docs/beads-integration-learnings.md` — deleted

### ⛔ CHECKPOINT: Phase 2 Complete

1. Every Phase 2 checkbox is `[x]`
2. The beads greps return nothing across `plugin/`
3. The token-cost comparison against the Phase 0 baseline meets the 30% bar
4. One tier-rule statement exists
5. Run `/wb:update_status`

**Do not proceed without human confirmation.** This is the phase where content loss would
hide, and the token metric alone cannot distinguish deferral from deletion.

---

## Phase 3: The capabilities that did not exist before

### Objective

Add cross-session continuity, drift hardening, and the optional architecture stage — all new
files, so no stage file is edited twice.

### Prerequisites

- [ ] Phase 2 complete
- [ ] The skill conventions established in Phase 2 are what these new skills follow

### Changes Required

#### 1. The orientation and recovery hook (D11)

One script, `plugin/hooks/wb-prime.sh`, registered on SessionStart for every trigger and on
PreCompact, replacing `setup-beads-mode.sh` in the vacated slot. On a fresh start it prints
the orientation; on a compact trigger it prints the recovery text. Contract inherited from
the file it replaces: no subprocess calls beyond coreutils, well under its time budget, silent
on an unknown payload, exit 0 always. A repository can override the orientation with
`.claude/wb/PRIME.md`; `--export` prints the default.

#### 2. The bootstrap block (D8c)

The same hook, after the orientation: active plan and position from checkbox counts and
frontmatter, the journal's most recent entry verbatim, whether it is open or closed, and one
line naming the knowledge file. Where journal and working tree disagree, say so and name the
tree state — the repository is the authority, never the journal.

#### 3. Continuity artifacts (D8a, D8b)

`journal.md` per plan directory, entries opened at start of work and closed at completion.
`.claude/wb/knowledge.md`, committed, one fact per entry with a date, source plan, and
verification hint.

### Tasks

- [ ] **P3-T1** — `plugin/hooks/wb-prime.sh`: the orientation mode (stage chain, plan-directory
      convention, where status lives, checkpoints stop for a human, active plans in the
      repository, pointer to `/wb:help`). Under forty lines of output; `--export` support;
      `.claude/wb/PRIME.md` override. (~20 calls)
- [ ] **P3-T2** — Same script, the recovery mode: on a compact payload and on PreCompact,
      print that summarized document contents are paraphrase and the plan documents must be
      re-read before being asserted, naming the active plan directory. (~15 calls)
- [ ] **P3-T3** — Same script, the D8c bootstrap block: plan position from checkbox counts,
      the journal's last entry with its open/closed state, the knowledge-file line, and the
      journal-vs-tree reconciliation. (~20 calls)
- [ ] **P3-T4** — Register the hook in `plugin/.claude-plugin/plugin.json` on SessionStart (all
      triggers) and PreCompact; delete `plugin/hooks/setup-beads-mode.sh` and its registration.
      (~8 calls)
- [ ] **P3-T5** — Verify the hook contract mechanically: run it against all four payload shapes
      (startup, compact, PreCompact, empty) with `time`, confirm it stays under budget, makes
      no `bd` call, and exits 0 on an unknown payload. Record results in
      `thoughts/2026-09-08-baseline-measurements.md`. (~12 calls)
- [ ] **P3-T6** — `plugin/skills/doc-adherence/SKILL.md` (D11): `user-invocable: false`; the
      rule that a claim about what a plan document says requires a read of that document in
      the current context window; the identify → check → read → assert gate; a
      rationalizations table; and a section tying it to `wb-prime.sh`'s compaction signal.
      (~15 calls)
- [ ] **P3-T7** — `journal.md` (D8a): add the template to `create_project`'s generated plan
      directory, and the open-at-start / close-at-completion protocol to
      `implement_tasks`, `implement_coordinated`, and `create_handoff`. Include the
      PreCompact refresh of an open entry's mechanical fields. (~20 calls)
- [ ] **P3-T8** — `.claude/wb/knowledge.md` (D8b): create the file with its header stating the
      entry shape (fact, why it matters, date, source plan, verification hint) and the
      qualification rule. Wire the on-demand read into the research stages, `create_design`,
      both implementation stages, and `resume_handoff`. Add the correct-on-discovery
      obligation. Seed it with the facts this plan itself established. (~20 calls)
- [ ] **P3-T9** — Handoff-over-compact guidance (D11): a phase that would need a second
      compaction hands off instead. Lands in `implement_coordinated`'s recommendation text,
      `create_handoff`'s "when to create" list, and `help`. (~10 calls)
- [ ] **P3-T10** — `plugin/skills/explore_design/` (D10): the optional stage — frame, diverge,
      discuss, converge only on explicit approval, record. Writes a `thoughts/` exploration
      document plus a decision record in the markdown decisions log (D6). Never writes
      `design.md`. Includes the model self-check in D12's shape: recommends Opus, names Fable
      as the available upshift, warns below Opus, never blocks. (~30 calls)
- [ ] **P3-T11** — The conditional nudge for `explore_design`: the research stages suggest it
      only when findings show more than one viable approach. Word it against the false-positive
      upstream found and fixed — it fires on evidence, not by default. (~10 calls)

### Success Criteria

#### Automated Verification

- [ ] `plugin/hooks/wb-prime.sh` exits 0 on all four payload shapes and on empty stdin
- [ ] `grep -c 'bd ' plugin/hooks/wb-prime.sh` → 0
- [ ] The script's runtime is recorded and within the contract it inherited
- [ ] `test ! -e plugin/hooks/setup-beads-mode.sh`; no reference to it in `plugin.json`
- [ ] `grep -c 'PreCompact' plugin/.claude-plugin/plugin.json` → 1
- [ ] `ls plugin/skills/doc-adherence/SKILL.md plugin/skills/explore_design/SKILL.md`
- [ ] `test -f .claude/wb/knowledge.md`; every entry matches the required shape
      (date, source plan, verification hint present)
- [ ] `grep -rn "journal.md" plugin/skills/ | wc -l` — referenced by the stages D8a names
- [ ] `./plugin/scripts/lint --all` — clean

#### Manual Verification

- [ ] A fresh `--plugin-dir` session's first context contains the orientation and, in this
      repository, names this plan directory
- [ ] **The D8 acceptance test**: start a session, open a journal entry, make an uncommitted
      edit, then kill the session without any shutdown step. A new session's first context
      reports the entry as **open**, names the attempted work and next action, and names the
      uncommitted changes
- [ ] Triggering `/compact` mid-plan produces the recovery text in the next context
- [ ] `explore_design` on a real question produces a `thoughts/` record and a decision-log
      entry, and `create_design` then formalizes it instead of regenerating options

### Modified Files

- `plugin/hooks/wb-prime.sh` — new; `setup-beads-mode.sh` — deleted
- `plugin/.claude-plugin/plugin.json` — SessionStart + PreCompact registration
- `plugin/skills/doc-adherence/`, `plugin/skills/explore_design/` — new
- `.claude/wb/knowledge.md` — new, committed
- `plugin/skills/{create_project,implement_tasks,implement_coordinated,create_handoff,resume_handoff,create_research,create_product_research,create_design,help}/` — continuity wiring

### ⛔ CHECKPOINT: Phase 3 Complete

1. Every Phase 3 checkbox is `[x]`
2. **The abrupt-kill test passed** — this is the acceptance test for the whole D8 design, and
   a mid-task kill is the case it exists for
3. The hook contract is verified, not assumed
4. Run `/wb:update_status`

**Do not proceed without human confirmation.**

---

## Phase 4: Consumers, documentation, and the cut

### Objective

Rewrite what reads the pipeline's shape, then release.

### Prerequisites

- [ ] Phase 3 complete — naming and shape are final

### Changes Required

`forge` and `help` are last because they describe everything else. `forge` needs real rework,
not reshaping: it currently infers pipeline position from tracker state, and must re-derive it
from document existence, frontmatter status, and checkbox counts. `help` loses its ~95-line
`## Beads Integration` block including the `/beads:*` reference table.

### Tasks

- [ ] **P4-T1** — `forge` (D4, D6): rewrite the state-detection ladder at `:51-57`. Its first
      two branches key off documents; every branch after keys off tracker state ("no beads
      issues", "beads phases", "All phases closed in beads"). Re-derive all of them from
      documents — which of research/design/tasks exist, their frontmatter status, and checkbox
      counts. Replace the `bd ready` → claim → close phase loop (`:99`) with document-order
      phase advance. The four barriers (`:84`, `:89`, `:95`, `:111`) read the markdown
      `Q1`/`PD1` records instead of `bd list`. Delete cross-cutting rule 1 (`:110`) with its
      link to the deleted fast-fail doc — the only true markdown hyperlink in the group.
      Repoint `:77`, which instructs reading `commands/create_project.md`, at the relocated
      skill path. Update the sequence to name `create_tasks`. Split out
      `examples.md` (`## Examples`) and keep `## Output style` as the template. (~30 calls)
- [ ] **P4-T2** — `help`: delete `## Beads Integration` (`:60-96`), the `/beads:*`
      slash-command tables (`:98-125`), `### CLI vs Slash Commands` (`:127-139`, which exists
      only to contrast with the deleted block), and `### Beads + Git Workflow` (`:141-153`).
      Reverse the per-command annotations that name beads as the status source — notably
      `:181-184` ("Uses beads as source of truth") — and `## Core Principles` item 5
      ("Beads Required"). Delete `:245-246`, which points at the `v1.0.0` tag for a
      "markdown-only workflow": that mode is what this release restores as the only mode.
      Rewrite the workflow chain to include `explore_design` and `create_tasks`, and add a
      "where status lives" section (checkboxes, counters, git) plus D8's continuity artifacts.
      **No supporting-file split** — this stays a single SKILL.md, matching upstream's `help/`,
      which has no siblings. (~25 calls)
- [ ] **P4-T3** — `docs/workbench-workflow-guide.md`: the 47 `bd` lines go; the model map gains
      D12's upshift ladder and the `create_tasks` row; the stage chain gains `explore_design`;
      the beads-doc links are removed. Largest single doc rewrite. (~30 calls)
- [ ] **P4-T4** — `docs/commands-reference.md`: rename `create_execution` → `create_tasks`
      with the alias noted; drop the beads sections; reconcile `:408` ("Update task checkboxes
      as you complete work") which becomes *correct* under D4 rather than contradictory.
      (~25 calls)
- [ ] **P4-T5** — `docs/claude-code-skills-guide.md`: record the progressive-disclosure
      convention, `allowed-tools: Read`, `user-invocable: false`, and the alias-stub pattern as
      house conventions. (~15 calls)
- [ ] **P4-T6** — `README.md` and `CLAUDE.md`: the stage chain, the tracker-free tracking
      philosophy replacing "Beads Required", the `plugin/`-aware local-dev instruction, the
      `docs/` shipped-vs-maintainer boundary, and D19's where-rules-may-live rule. Fix the
      duplicated `## Output Discipline` heading in `README.md`. (~20 calls)
- [ ] **P4-T7** — `CHANGELOG.md` (D17): new file. A `[2.0.0]` entry with **Breaking**
      (beads removed; three renames — `create_execution` → `create_tasks`,
      `implement_coordinated` → `implement`, `implement_tasks` → `implement_inline`, each with
      a deprecated alias removed at the next major; tree relocated; `BEADS_MODE` gone;
      `AGENTS.md` gone), **Added** (`explore_design`, `doc-adherence`, `wb-prime.sh`,
      `task-worker`, journal, knowledge file), **Changed**, **Fixed** (the lint exit code), and
      **Migration** — written **per-machine** (A1 resolved: no other people or repos, but
      `wb` is installed on other machines/workspaces holding existing plan directories). On
      each machine: update the plugin and restart; point `--plugin-dir` at `plugin/`; expect
      existing plan directories' beads IDs to stop resolving, with checkbox state now
      authoritative. Do not assume the reader is in this repository looking at this plan. Worth stating plainly in the entry: `help.md:245-246` currently points
      users at the `v1.0.0` tag for a "markdown-only workflow", so this release does not
      invent tracker-free operation — it restores it as the only mode. Fold in the
      `beads-integration-learnings.md` migration narrative here in a few sentences if that
      history is worth keeping anywhere (design.md D19 trade-off). (~20 calls)
- [ ] **P4-T8** — Version bump to 2.0.0 in **both** `plugin/.claude-plugin/plugin.json` and
      `.claude-plugin/marketplace.json`, same commit. Verify with
      `claude plugin tag --dry-run plugin/`. (~8 calls)
- [ ] **P4-T9** — Final full verification sweep: every automated check from every phase, plus
      the end-to-end pipeline run below. Record results in the journal and close the plan's
      frontmatter status. (~20 calls)
- [ ] **P4-T10** — Tag the release: `claude plugin tag plugin/` (creates `wb--v2.0.0`,
      validating manifest agreement), then push. Note the harness's tag convention is
      `wb--v<version>`, not upstream's `v<version>`. (~6 calls)

### Success Criteria

#### Automated Verification

- [ ] `grep -rn "bd \|beads\|BEADS_MODE\|/beads:" plugin/ README.md CLAUDE.md docs/ | grep -v docs/plans | grep -v CHANGELOG.md` → **no hits**
- [ ] `grep -rn "create_execution" plugin/ docs/ README.md CLAUDE.md | grep -v docs/plans` — only
      as the deprecated alias
- [ ] `grep -c 'explore_design' plugin/skills/help/SKILL.md CLAUDE.md README.md docs/workbench-workflow-guide.md`
      → 1 or more each
- [ ] Both manifests read `2.0.0`; `claude plugin tag --dry-run plugin/` exits 0 with no
      warnings
- [ ] `CHANGELOG.md` has `### ⚠️ Breaking` and `### Migration` sections under `[2.0.0]`
- [ ] `./plugin/scripts/lint --all` — clean (D16 now makes this meaningful)
- [ ] `claude plugin details wb` — final inventory and token cost recorded against baseline

#### Manual Verification

- [ ] **End-to-end**: in a scratch repository with no tracker installed, run
      `create_project → create_research → explore_design → create_design → create_tasks →
      implement_tasks → validate_execution` to completion. No stop-and-prompt gate, no
      degraded path, no reference to a tracker
- [ ] `tasks.md` from that run answers "what is done, what phase, what next" on its own
- [ ] The three-session canary: this plan's own later phases were run through
      `--plugin-dir` on the new layout
- [ ] Human confirms the changelog's migration steps are sufficient for their own older plan
      directories

### Modified Files

- `plugin/skills/{forge,help}/` — rewritten
- `docs/{workbench-workflow-guide,commands-reference,claude-code-skills-guide}.md`
- `README.md`, `CLAUDE.md`
- `CHANGELOG.md` — new
- Both manifests — 2.0.0

### ⛔ CHECKPOINT: Phase 4 Complete

1. Every checkbox in every phase is `[x]`
2. The end-to-end run in a tracker-free scratch repository succeeded
3. Both manifests agree and the tag validates
4. Run `/wb:update_status`, then `/wb:validate_execution` against this plan

---

## Implementation Discoveries

To determine during implementation:

- ~~Whether `claude plugin details` can be pointed at a local path, or whether measuring the
  post-change token cost requires installing from a local marketplace first~~ —
  **answered by `P0-T3`**: it can. `claude --plugin-dir <path> plugin details <name>`, with
  the global flag **before** the subcommand; `details` itself takes no `--plugin-dir` option.
  No local install is needed, so `P2`'s exit metric is captured against the working tree
- ~~Whether `allowed-tools: Read` covers reads of `plugin/docs/reference/` as well as
  same-directory supporting files (A4; `P0-T1` probes both deliberately)~~ — **answered
  2026-09-08**: it covers **both**. The smoke session read the sibling `templates.md` and the
  cross-directory `../../docs/reference/probe-ref.md` with no permission prompt on either, and
  echoed the `PROBE-REF-RESOLVED` marker. A5 landed in the same session. Recorded in design.md
  → Resolved Decisions; the assumption rows are flipped
- The real reduction ratio per stage — the −37% figure is a line-count projection, and
  `claude plugin details` measures tokens, so the two will not match exactly. **Being answered
  as the phase runs**; the gap is larger than "not exactly". Running tally, on-invoke tokens:
  `create_research` −30.2% (5.3k → 3.7k, after the `P2-T1` amendment), `create_product_research`
  −38.5% (6.5k → 4.0k). Line reduction ran roughly **twice** the token reduction in both, because
  what moves out — fenced `Task({…})` blocks and templates of short bracketed lines — is much
  sparser per line than the prose that stays. **Size future splits by what the tokens do, not by
  `wc -l`.**
- ~~Whether any of the four `create_project` templates is large enough to warrant its own file
  rather than one `templates.md`~~ — **answered 2026-09-08: no.** README 51 lines, research 75,
  design 82, tasks 81 — 289 total, no outlier, and upstream ships one `templates.md` at 321
  lines for the same four. One file with four named sections, read **by section** per creation
  step. Recorded in design.md → Resolved Decisions, which also generalizes the section-scoped
  read to any supporting file holding several independent blocks
- Whether the PreCompact journal refresh can be done in the hook without judgment, or needs a
  model-written line (D8a assumes mechanical fields only)

## 📝 Completed Tasks Archive

Move completed tasks here as phases close, to keep the active list readable.

## 🚧 Blockers & Notes

### Current Blockers

None open.

- **2026-09-08 — `lint --all` cannot be clean while `.context/upstream/` exists.** Raised by
  `P0-T4`. `--all` builds its file list with a raw `find .` and a hardcoded exclusion list
  (`scripts/lint:115-125`) that does **not** consult `.gitignore`, so it walked the gitignored
  upstream export and returned 84 findings — **all 84** in `.context/upstream/`, **zero**
  anywhere we author or ship. Pre-existing, not caused by the D16 fix (plain mode already
  exited 1). **Resolved 2026-09-08** → decision recorded in design.md
  (## Technical Decisions → Resolved Decisions); carried by new task `P0-T6`.

### Implementation Notes

- **2026-09-08, research cluster complete** (`P2-T1`–`P2-T3`), one commit per the per-cluster
  cadence. **Line count overstates the win; measure tokens.** `create_research` lost 46% of its
  lines but only **22.6%** of its on-invoke tokens (~5.3k → ~4.1k), because what moves out —
  fenced `Task({…})` blocks and a template of short bracketed lines — is far sparser per line
  than the prose that stays. `create_product_research` hit **−38.5%** (~6.5k → ~4.0k). Cluster
  total **11.8k → 8.1k = −31.4%**, so the 30% bar is achievable but not automatic.
  **The variable was `## Important Notes`** — and it was resolved the same day rather than
  carried. `P2-T2` moved it to `reference.md` and cleared the bar; `P2-T1`'s spec said
  `reference = ## Configuration` alone, and it was the task that missed. A survey of all 29
  Phase 2 tasks showed `create_research` was the **only** stage whose spec omitted a tail
  reference section its source file actually has, so `P2-T1` was amended to match the recipe
  (design.md → Resolved Decisions). **Result: `create_research` ~5.3k → ~3.7k = −30.2%; cluster
  11.8k → 7.7k = −34.7%.** Both now clear the bar on their own.
  Two smaller notes: a `reference.md` holding only `## Configuration` is 13 lines, which buys
  almost nothing and adds a drift surface — built as specified, flagged as an observation, not
  changed. And moved blocks were moved **verbatim**: `templates.md` still says
  `/create_design` and `reference.md` still says `/create_research`, both missing the `wb:`
  prefix. Pre-existing, and Phase 4's consumer sweep owns it — a "move this block" task is not
  a licence to reword it.
- **2026-09-08, `P2-T3` deviates from strict parity in one place, deliberately.** The mirror
  did **not** get D8c's `.claude/wb/knowledge.md` read, even though `P2-T2` did. The mirror is
  a Claude Desktop project instruction: there is no wb plugin, no repository checkout, and no
  `.claude/wb/` for it to read, so the instruction could never fire and would only add noise to
  a portable document. Everything else reached parity — the softened Documentarian Rule, all
  three thinking-directive conversions, and the D6 Open Questions table adapted for standalone
  use (its resolution pointer names "wherever this project keeps decisions" rather than
  `design.md`, since a Desktop project has no `design.md`).
- **2026-09-08, Phase 1 complete** (`P1-T1`–`P1-T7`), one commit — a **deliberate deviation**
  from the per-task cadence decided the same day. The reason is that Phase 1's intermediate
  states do not load: a tree moved by `P1-T1` but not yet repointed by `P1-T2` has a manifest
  naming a `source` that no longer holds the plugin. `CLAUDE.md` also carries three separate
  tasks' edits (`P1-T2`'s lint paths, `P1-T5`'s session protocol, `P1-T6`'s D18 rewrite), so no
  path-split could reconstruct per-task commits after the fact. **Phases 3 and 4 return to one
  commit per task; Phase 2 commits per cluster as decided.**
- **2026-09-08, `effort:` and `maxTurns:` are recognized agent-frontmatter keys — established
  the hard way, because the check `P1-T4` was written against does not exist.** The
  `/agents` wizard has been **removed from the harness**, so the frontmatter cannot be
  inspected from inside a session. Worse, the two CLI gates are blind to it: planting
  `model: totally-not-a-model` and `completelyBogusKey: 42` into an agent file made
  `claude plugin validate` report "Validation passed" and left `claude plugin details`
  enumerating all six agents. So Phase 1's `grep -c 'model:'` criterion only proves the string
  is present — it cannot prove the harness honours the pin, which is the thing D3 actually
  buys.
  The positive evidence came from the shipped binary's validator string table
  (`/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe`), which contains
  **`has invalid effort`** and **`has invalid maxTurns`** beside `has invalid name`,
  `has invalid permissionMode` and `has invalid isolation`. Both keys are therefore parsed and
  **value-validated**, and our values (`medium`, `high`, `25`) are in range — an invalid one
  would surface as a load error rather than being ignored.
  *Verify:* `strings <claude binary> | grep -oE "has invalid [a-zA-Z-]+" | sort -u`.
  **Consequence**: the only live check for `P1-T4` is `/plugin` → **Errors** in a
  `--plugin-dir` session, and an empty Errors tab is a real positive signal rather than mere
  absence of evidence. Not run — Phase 1 was closed on the string-table evidence plus a clean
  session start, since a rejected key surfaces as a load error and the session loaded and ran
  `/wb:help` without one. Left as a cheap confirmation for the Phase 2 or Phase 4 smoke
  session rather than a Phase 1 blocker.
  **Bonus for Phase 2**: the same table and string set carry `disable-model-invocation` and
  `user-invocable`, so `P2-T8`/`P2-T29`'s alias stubs and `P2-T22`'s background-skill flags
  rest on recognized fields, not on upstream's word.
- **2026-09-08, `/plugin` → Discover does not list a `--plugin-dir` plugin.** It searches
  marketplaces; an inline plugin is not in one. Use the **Installed** tab. Recorded because
  "No plugins match \"wb\"" reads like a load failure and is not one.
- **2026-09-08, three Phase 1 findings worth carrying forward.** **(a)** `${CLAUDE_PLUGIN_ROOT}`
  needed **no** edit — it resolves to the plugin root, which moved with the hooks, so
  `P1-T2`'s "update every path that no longer resolves" turned out to be a no-op. Same for
  `scripts/lint` itself: it was already cwd-relative and is still run from the repository root,
  so only its *invocations* moved. **(b)** `claude --plugin-dir .` at the repository root no
  longer serves the working tree — it silently falls back to the **installed** plugin (1.12.4).
  It does not error, which is exactly the trap the handoff warned about; from here on the flag
  must point at `plugin/`. **(c)** The relative links to `docs/beads-fast-fail.md` inside five
  command files are now wrong by one level (`../docs/` from `plugin/commands/` needs `../../`).
  Left alone on purpose: `P2-T26` deletes the target and Phase 2 deletes the links, and
  markdownlint does not check relative-file existence, so no gate hides a real problem here.
- **2026-09-08, two Phase 1 criteria over-reach their tasks**, both recorded inline above
  rather than silently passed. The `AGENTS.md` grep also covers a file `P2-T27` deletes, and
  the "no prose changes to any `commands/*.md` body" check conflicts with `P1-T7`, which the
  plan itself places in this phase as a deliberate content-only addition. Neither is a defect
  in the work; both are the plan checking a wider scope than the phase owns.
- **2026-09-08, status reconciled by `/wb:update_status`** at the Phase 1 checkpoint (the
  sole writer, D5): `current_phase` 1 → 2, `completed_tasks` 6 → 13 of 63 (20.6%),
  `git_commit` → the Phase 1 commit.
- **2026-09-08, status reconciled by `/wb:update_status`** (the sole writer, D5): tasks
  `not-started` → `in-progress`, `current_phase` 0 → 1, `total_tasks` 62 → 63 (`P0-T6`
  added), `completed_tasks` 0 → 6 (9.5%), and `git_commit`/`git_branch` added — the
  frontmatter previously carried neither, against the standard in `CLAUDE.md`. design.md
  moved `approved` → `implementing`. Counted from `[x]`-marked task IDs, not from the raw
  checkbox total: `grep -cE '^- \[x\] \*\*P[0-9]-T[0-9]+\*\*'` is 6, while
  `grep -c '^- \[x\]'` is 18 because prerequisites and success criteria are checkboxes too.
  Worth stating because it is exactly assumption A2's positional-identity limitation, and any
  future reconciliation must filter to task IDs or it will over-count.
- **2026-09-08, Phase 0** (`P0-T1`–`P0-T4` complete; `P0-T5`'s deletion held): the layout
  probe returned **proceed with D1/D2 as designed**. Full record in
  `thoughts/2026-09-08-baseline-measurements.md`. Four things changed for later phases:
  **(a)** `claude plugin tag` takes the directory holding `.claude-plugin/plugin.json` — not
  the marketplace root — requires a git repository, and refuses on an uncommitted tree
  without `--force`, so `P4-T8` must verify **after** the bump commit. **(b)** The
  root-`CLAUDE.md` warning does not affect the exit code, so Phase 1 must assert on the
  absence of the warning *text*. Verified in both directions: it fires on a `CLAUDE.md` at
  the plugin root and is silent on one at the repo root outside it — exactly D1's assertion.
  **(c)** `claude --plugin-dir <path> plugin details <name>` measures the working tree, so
  the 1.12.4-vs-1.12.5 cache lag is off the critical path; both readings are identical across
  all fourteen stages. **(d)** The baseline the Phase 2 bar is measured against: fourteen-stage
  on-invoke **~84.9k tok**, so the 30% bar is **≤ ~59.4k**.
- **2026-09-08, `P0-T5` was reordered, not skipped** — and the reorder paid. Its
  `rm -rf /tmp/wb-probe/` ran **after** the checkpoint's human smoke session rather than
  before it, because A4 and A5 are only observable by invoking a skill and deleting the probe
  first would have made the Manual Verification impossible. The session returned `NO PROMPT`
  on **both** on-demand reads — the sibling file and the cross-directory
  `plugin/docs/reference/` file alike — plus a single rename announcement from the alias stub,
  so A4 and A5 are both Validated and the probe was then deleted. Had `P0-T5` run in document
  order, the plan would have had to rebuild the probe to answer its own checkpoint.
- **2026-09-08, four decisions taken via `/wb:resolve_questions`** after Phase 0's automated
  work: A4/A5 validated; `lint --all` scoped to exclude `.context/` (new task `P0-T6`);
  commit cadence set to per-task except Phase 2, which commits per cluster; and **D21**, the
  transient-by-default plan-persistence convention, under which this plan directory was
  force-added into git. Records in design.md → D21 and Resolved Decisions.
- **2026-09-08, prerequisites.** "research.md validated" was flipped on documentary evidence
  — `status: complete` plus all seven Open Questions closed with pointers — because no
  separate `research-validator` run is recorded for this plan.
- **2026-09-08**: Planned. Three mechanical gates were discovered during planning and are
  now load-bearing in the verification strategy: `claude plugin details` (token cost — the
  direct measurement of D2's metric, replacing the line-count proxy),
  `claude plugin tag --dry-run` (manifest agreement plus a root-`CLAUDE.md`-not-shipped
  warning that independently confirms D11's premise), and the repaired `scripts/lint`. The
  harness's release tag convention is `wb--v<version>`.
- **2026-09-08**: Split boundaries are specified by **heading**, not line range. In a
  sequential multi-file refactor, line numbers decay after the first edit in a file; headings
  survive. Two analysis agents were dispatched for line ranges during planning; the heading
  maps proved sufficient and more durable, so their output is corroboration rather than input.
  The group-B report landed after this plan was written and confirmed the splits, correcting
  four details now folded in: `help` takes no supporting-file split (upstream's `help/` has no
  siblings); `resolve_questions` and `forge` each have a clear `examples.md`;
  `resolve_questions` Step 4d duplicates its own canonical format reference and should point
  rather than restate; and `forge:110` holds the only true markdown hyperlink among the
  consumer files, so `P2-T26`'s deletion ordering matters there specifically.
- **2026-09-08**: `help.md:245-246` already tells users to check out `v1.0.0` for a
  "markdown-only workflow". This release is a return, not an invention — worth saying in the
  changelog.
- **2026-09-08**: The group-A report landed after this plan was written and resized one task.
  `implement_coordinated`'s tracker coupling is **not** one section — it recurs in Steps 2, 4,
  6, 7, 8, and 9, and its Resume Logic and Helper Functions are control-flow-integral rather
  than templatable, so it projects to the largest remaining SKILL.md (~559 lines pre-removal)
  even after splitting. `P2-T10` was therefore split into `P2-T10` (structure) and `P2-T28`
  (gates) on tool-call budget per D15. The same report corrected two reference-file scopes:
  `validate_project`'s Validation Checklist and Validation Rules belong in `reference.md`
  (making it the tree's largest at ~255 lines, with SKILL.md down to ~130), and
  `update_status` has ~145 lines of message templates, not just Implementation Notes.
- **Projected post-split SKILL.md sizes** for the seven largest, as a "done" target for
  Phase 2: `implement_coordinated` ~559 pre-gate-removal · `implement_tasks` ~400 ·
  `create_execution`→`create_tasks` ~267 · `update_status` ~160 · `create_mockup` ~155 ·
  `create_design` ~140 · `validate_project` ~130. These are projections from the current
  structure, not targets to force — the authoritative measure is
  `claude plugin details wb` against the Phase 0 baseline.

## 🔗 Quick Reference

### Key Documents

- **Research**: [research.md](research.md) — what exists on both sides and how it maps
- **Design**: [design.md](design.md) — D1–D19 and their rationale
- **Baselines**: `thoughts/2026-09-08-baseline-measurements.md` — written by `P0-T2`

### Gates

```bash
./plugin/scripts/lint --all              # markdown gate (meaningful after P0-T4; scoped by P0-T6)
claude plugin details wb                 # component inventory + projected token cost
claude plugin tag --dry-run plugin/      # manifest agreement + plugin-root warnings
grep -rn "bd \|beads\|BEADS_MODE" plugin/   # beads-removal audit
grep -c '^- \[x\]' tasks.md              # progress
```

### Design Decisions Reference

- **D1/D2** — relocation, then progressive disclosure; relocation first for the link root
- **D4** — no tracker; checkboxes are truth, counters a cache, git the durable record
- **D8** — journal opens at start of work; knowledge is curated and verifiable; the bootstrap
  is reconciled against the working tree, which is the only thing that always survives
- **D12** — Fable is an upshift, never a default
- **D14** — truncation and failure are different events with opposite remedies
- **D19** — delete the stale rule-bearing docs, then constrain where rules may live
- **D21** — plans are transient by default; git promotion happens on a trigger, and the
  knowledge file is what survives an abandoned branch
