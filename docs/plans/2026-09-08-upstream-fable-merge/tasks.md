---
project: upstream-fable-merge
ticket: N/A
created: 2026-09-08
status: in-progress
last_updated: 2026-09-08
current_phase: 4
total_tasks: 64
completed_tasks: 63
task_tracking: markdown-checkboxes
depends_on: [research.md, design.md]
git_commit: 18dc4a8ee76282e07b7ac100de57d42bc761ca7c
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

- [ ] A `claude --plugin-dir /tmp/wb-probe/plugin` session lists the `probe` skill, and
      invoking it reads `templates.md` and `plugin/docs/reference/probe-ref.md` **without a
      permission prompt** (settles A4) — recorded 2026-09-08 as `NO PROMPT` on both reads with
      the marker `PROBE-REF-RESOLVED` echoed, and **reopened 2026-09-09: A4 is FALSE.** Three
      headless probes denied the read under `--plugin-dir` and again for a marketplace install;
      only `--add-dir` passes. The 2026-09-08 session never recorded its **cwd**, and if it ran
      from inside `/tmp/wb-probe` the working-directory boundary could not fire — so the probe
      was structurally incapable of failing. Left unchecked deliberately: the criterion as
      written is not met, and the release documents the boundary instead of claiming it away.
      **Superseded in mechanism 2026-09-10** — the gate is the ordinary permission-grant flow,
      not the working-directory boundary; see the `2026-09-10, A4 resolved` note below. The
      criterion still fails as written, because interactive **does** prompt
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
- [x] ~~`grep -c 'model:' plugin/agents/*.md` → 1 per file~~; no `effort:` on a haiku agent —
      **criterion amended 2026-09-08 at the Phase 4 sweep.** It was written when there were six
      agents. `P2-T11` added a seventh, `task-worker`, whose design is precisely that it carries
      **no** `model:` — the coordinator picks its tier per spawn from `implement`'s Step 5
      ladder, which is D13's entire point. Working form: the six typed agents each have exactly
      one `model:` and no `effort:` on a haiku one; `task-worker` has none and a `maxTurns` —
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

- [x] **P2-T4** — `create_design`: template = `## Problem Statement` → `## References`;
      prompts = the Step 2 `Task({...})` blocks; reference = `## Important Guidelines`,
      `## Configuration`. Content: D6 (Assumptions and Pending Decisions tables lose their
      `Beads ID` column, gain local IDs; the cold-start check reads markdown records, not
      `bd list`); D10 (consume an `explore_design` decision record when present, formalize
      rather than regenerate); D18 bullets at `:91,:165,:188`. (~30 calls) (completed 2026-09-08 16:34)
- [x] **P2-T5** — `create_project`: template file is large — it embeds four artifact
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
      directory now includes `journal.md`). (~35 calls) (completed 2026-09-08 16:47)

**Execution-planning cluster**

- [x] **P2-T6** — `create_execution` → `create_tasks`, the rewrite (D9). Directory becomes
      `plugin/skills/create_tasks/`. Template = `## Overview` → `## 🔗 Quick Reference`.
      **Delete** `## Beads Issue Tracking` wholesale and all of Step 5's `bd create`/`bd dep
      add` choreography. Reference = `## Important Guidelines`, `## Task Granularity`,
      `## Configuration`. Content: D4 + D7 (the generated tasks.md carries a markdown task
      table with local IDs and document-order execution; a `Depends on:` field only where a
      task genuinely branches); D15 (size tasks by projected tool calls, split past ~50 at a
      natural seam — replacing the "1-4 hours" rule); D5 (the phase checkpoint delegates
      counter updates to `update_status` instead of editing `current_phase` inline);
      D18 bullets at `:69,:154,:175`. Projected past 50 calls, so split — see `P2-T7`.
      (~40 calls) (completed 2026-09-08 17:04)
- [x] **P2-T7** — `create_tasks` supporting files: write `templates.md` (the new tasks.md
      skeleton in the markdown-checkbox convention), `sub-agent-prompts.md` (the three Step 2
      analysis agents), and `examples.md`. Split from `P2-T6` at the SKILL/supporting seam per
      D15. (~25 calls) (completed 2026-09-08 17:12)
- [x] **P2-T8** — `create_execution` alias stub (D9): `plugin/skills/create_execution/` with a
      stub `SKILL.md` (`disable-model-invocation: true`) that announces the rename once and
      then reads the canonical skill. ~~plus one pointer file per supporting file so a stale
      cached body still resolves its reads~~ — **pointer files dropped 2026-09-08** (design.md
      → Resolved Decisions); the four written for this alias were deleted. (~10 calls) (completed 2026-09-08 17:16)

**Implementation cluster**

- [x] **P2-T9** — `implement_tasks` → **`implement_inline`** (PD4): directory becomes
      `plugin/skills/implement_inline/`, frontmatter `name:` changes with it. No output template. Reference = `## Handling Mismatches`,
      `## Resume Logic`, `## TDD Best Practices`, `## Special Considerations`,
      `## Error Handling`, `## Important Guidelines`, `## Configuration` (~180 lines).
      Carry `P1-T7`'s `### Extras and edits` section through the reshape — it stays beside the
      scope block, not in `reference.md`. Content: D4 (reverse `:315-317` and `:684-686` — flipping the checkbox *is* the tracking
      act now); D5 (defer counters to `update_status`); D8a (open a journal entry at task
      start, close it at completion); D18 bullet at `:117`. (~35 calls) (completed 2026-09-08 17:12)
- [x] **P2-T10** — `implement_coordinated` → **`implement`** (PD4), part 1 — **the rename and
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
      the beads gates in this task. (~30 calls) (completed 2026-09-08 17:26)
- [x] **P2-T28** — `implement` (formerly `implement_coordinated`), part 2 — **the tracker
      gates**: this file's beads
      coupling is not one section, it recurs in Steps 2, 4, 6, 7, 8, and 9 (the availability
      probe and stop-and-wait block, `bd ready` task selection, the post-worker `bd show`
      verification, phase-completion `bd show`, the milestone close, and the `bd sync` +
      `git add .beads/` step). Remove all of them and re-derive each from the checkbox surface
      (D4), deferring counters to `update_status` (D5) and opening/closing journal entries
      (D8a). Split from `P2-T10` on tool-call budget per D15 — same file, disjoint regions,
      sequential; the edit-once principle still holds per region. (~30 calls) (completed 2026-09-08 17:26)
- [x] **P2-T11** — `plugin/agents/task-worker.md`: new. The worker contract currently inlined
      in `implement_coordinated`'s prompt template becomes a real agent definition with
      `tools`, `skills: [tdd-discipline]`, and `maxTurns`, and names `/wb:implement` as its
      spawner (PD4). Carries D20's surgical-edit and
      follow-ups-not-fixes constraints (from `P1-T7`) — this agent file is their primary home,
      and the coordinated path inherits them from here rather than restating them. Carries the
      D14 rule that workers do **not** commit, and that closing its own task is its final act — which is what makes
      truncation detectable. (~15 calls) (completed 2026-09-08 17:34)

**Validation and status cluster**

- [x] **P2-T12** — `validate_execution`: template = `## Executive Summary` →
      `## Validation Completed`; prompts = the Step 2 `Task({...})` blocks; reference =
      `## Important Guidelines`, `## Relationship to Other Commands`, `## Configuration`.
      Content: D4 (reverse `:63`, `:203`, `:379` — checkbox state becomes the completion
      signal it reads, not a thing to ignore). (~30 calls) (completed 2026-09-08 17:06)
- [x] **P2-T13** — `validate_project`: template = `## Summary` → `## Validation Details`, plus
      the `## Error Messages` canonical formats; reference = **`## Validation Checklist`** (the
      8-category criteria list — it is read by Step 3, not executed inline) and
      **`## Validation Rules`** (the per-check pseudocode), plus `## Important Guidelines` and
      `## Configuration`. Those two sections make this the largest `reference.md` in the tree
      at roughly 255 lines, so the SKILL.md drops to about 130. Content: D4 (delete the Beads
      Integration and Beads State Alignment checklist categories, the Step 2 beads-state
      validation, the Beads Validation pseudocode, and the `beads_*` required-frontmatter
      list); D6 (validate the markdown planning-record sections instead of orphaned issue
      IDs). (~30 calls) (completed 2026-09-08 17:16)
- [x] **P2-T14** — `update_status`: template = the message and fragment set, which is larger
      than it looks — the "Current Status Analysis" plan message, the per-file frontmatter
      update fragments for research/design/tasks, the success summary, and the three
      Error Handling message templates (~145 lines total); reference =
      `## Status Transition Logic`, `## Smart Status Detection`, `## Error Handling`,
      `## Important Notes`, `## Configuration`. Content: D4 + D5 — this is the file that
      inverts most sharply. Reverse `:110`, `:371`, `:403` ("NEVER check markdown checkboxes")
      into the reconciliation mechanism: count `[x]`/`[ ]`, compare against frontmatter
      counters, report drift, reconcile to the counts. State the sole-writer rule here.
      (~30 calls) (completed 2026-09-08 17:24)

**Execution-path decisions** *(same cluster's files, split out per D15)*

- [x] **P2-T15** — The single worker tier-rule statement (D13), in
      `plugin/skills/implement/SKILL.md` at the point of spawn. **PD2 resolved 2026-09-08**:
      the ladder is haiku for mechanical only · **Opus 4.8 1M (`claude-opus-4-8[1m]`)
      default** · Opus 5 on coordinator judgment for architectural or cross-cutting tasks ·
      Fable never as a first spawn, only as an explicit election after a verified failure,
      always at `effort: high`. Use the `[1m]` variant for the default, not base
      `claude-opus-4-8`. Never annotate `effort` on a haiku spawn. Every other restatement of the tiers becomes a
      pointer to this one — including `reference.md` and the skill README. (~20 calls) (completed 2026-09-08 17:26)
- [x] **P2-T16** — The failure path (D14): replace the two-identical-retry block with the
      truncation-vs-failure discrimination. Inspect the working tree to tell them apart;
      finish or re-delegate the remaining slice for truncation; escalate one rung for a
      verified failure; exactly one escalation, then the phase checkpoint's blocking list.
      Move the commit to the coordinator, after the verifier passes. Update
      `plugin/agents/task-verifier.md` to check scope against the working tree rather than a
      caller-supplied base ref, since workers no longer commit. (~25 calls) (completed 2026-09-08 17:31)
- [x] **P2-T29** — The two `implement_*` alias stubs (PD4), mirroring `P2-T8`:
      `plugin/skills/implement_coordinated/` → `implement` and
      `plugin/skills/implement_tasks/` → `implement_inline`. Each is a stub `SKILL.md`
      (`disable-model-invocation: true`) that announces the rename once and then reads the
      canonical skill. **Stubs only — no pointer files** (decided 2026-09-08, design.md →
      Resolved Decisions). (~10 calls) (completed 2026-09-08 17:37)
- [x] **P2-T17** — `model-help` (D12): add the upshift-ladder semantics — a named next-tier-up
      per phase, entered only by explicit election, never by a baseline. Rename the
      `create_execution` row to `create_tasks`, the `implement_tasks` row to
      `implement_inline`, and add an `implement` row (PD4). Set the worker ladder per PD2 as
      resolved: **Opus 4.8 1M default**, Opus 5 upshift, Fable by election only. **Also add
      the 1M variants to the roster at `:22`** — it currently names four models with no 1M
      forms, so the ladder would otherwise reference a model this authority does not list.
      State which tier's 1M form is the default so roster and ladder cannot drift. Keep the switch-cost
      rule and the advise-never-auto-switch policy verbatim. (~20 calls) (completed 2026-09-08 17:44)

**Handoff cluster**

- [x] **P2-T18** — `create_handoff`: template = `## Quick Start` →
      `## Handoff Verification`; reference = `## Purpose`, `## Important Guidelines`,
      `## Relationship to Other Commands`, `## Configuration`. Content: D4 (drop `bd sync` and
      the `git add .beads/` block); D8a (append a journal pointer to the handoff it wrote);
      D8b (review the session's knowledge candidates against the qualification rule);
      D21 (added 2026-09-08 — a handoff that crosses a machine is one of the two triggers that
      promote a plan directory into git, so the handoff step names the `git add -f` and the
      branch push as the transport); D18 bullet at `:89`. (~32 calls) (completed 2026-09-08 17:53)
- [x] **P2-T19** — `resume_handoff`: reference = `## Purpose`, `## Validation Steps`,
      `## Important Guidelines`, `## Relationship to Other Commands`, `## Error Handling`,
      `## Configuration`; template = `## Output Format`. Content: D4 (drop the beads state
      reload and `:248`'s never-checkboxes rule); D8c (read the journal tail alongside the
      handoff, and read the knowledge file); D18 bullet at `:87`. (~30 calls) (completed 2026-09-08 17:59)

**Remaining stages**

- [x] **P2-T20** — `create_mockup`: templates = `## UI Research Summary`,
      `## Overview`→`## Needs Validation`, `## Feature: [Name]`→`## Design Principles
      Emerging` (~300 lines); prompts = the Step 2 research agents; reference =
      `## Purpose`, `## Output Files`, `## Important Guidelines`,
      `## Relationship to Other Commands`. Content: D6 (`UI Q:` records become markdown with
      `UIQ1` IDs); D18 bullet at `:174`. (~30 calls) (completed 2026-09-08 18:14)
- [x] **P2-T21** — `resolve_questions`: reference = `## Operating Principles`,
      `## Edge Cases`; template = `## Persistence Format Reference`; **examples.md** =
      `## Example Invocation` (a full worked dialogue — the clearest `examples.md` candidate in
      the tree). Content: D6 — delete the beads branch (Step 2 Source B, the
      `bd comments`/`bd close` block in Step 4d, and the Edge Cases line) and keep the markdown
      walk, which becomes the only path. While here, de-duplicate: Step 4d restates the
      decision-record formats that `## Persistence Format Reference` already defines
      canonically — point at the template instead of repeating it. (~25 calls) (completed 2026-09-08 18:22)
- [x] **P2-T22** — `mockup-iteration` skill: drop its four `bd create` sites for
      `UI Q:`/`UI Assumption:` records; use D6's markdown records. Add
      `user-invocable: false` where design.md's D2 calls for it on background skills, and to
      `project-structure`, `status-sync`, `tdd-discipline`,
      `verification-before-completion`. (~20 calls) (completed 2026-09-08 18:28)
- [x] **P2-T23** — `status-sync` (D5): add the frontmatter-drift indicator — compare counters
      against actual `[x]`/`[ ]` counts at phase end and session end, and point at
      `/wb:update_status` on mismatch. Drop the `bd sync` reminder. (~12 calls) (completed 2026-09-08 18:31)
- [x] **P2-T24** — `project-structure` (D4): add the "No external tracker" section stating
      where status lives — checkboxes in tasks.md, counters as a cache, git as the durable
      record. This is the doctrine's home, mirroring where the sibling workflow puts it.
      Also carry **D21** here (added 2026-09-08): plan directories are transient by default,
      promoted into git with `git add -f` when the work must cross a session or machine or when
      the branch is about to merge, and anything that must outlive an abandoned branch belongs
      in `.claude/wb/knowledge.md` rather than a preserved plan directory. (~14 calls)
- [x] **P2-T25** — `daily-digest` and `fetch-issues`: drop their beads source blocks and
      `bd` reads; both already treat beads as optional, so this is deletion plus a line
      about reading plan state from checkboxes. D18 bullets at
      `daily-digest:135`, `fetch-issues:135`. (~15 calls) (completed 2026-09-08 18:36)
- [x] **P2-T26** — Delete `docs/beads-fast-fail.md` and `docs/beads-stealth-mode.md` (D19).
      Runs **after** `P2-T1`–`P2-T25` so the fifteen inbound links are already gone. (~5 calls) (completed 2026-09-08 18:39)
- [x] **P2-T30** — **The rename sweep.** Runs **last** in Phase 2, after `create_tasks`,
      `implement` and `implement_inline` all exist. Repoint every reference to a renamed
      command in the already-reshaped skills — at the time of writing, eleven:
      `create_project/SKILL.md` and `templates.md` (×8 across both),
      `create_design/SKILL.md` and `templates.md` (×2), `create_tasks/templates.md` (×1).
      Excludes `model-help`, which `P2-T17` owns. Placed here rather than in Phase 4 because
      Phase 2 creates the breakage and Phase 2's exit greps verify the fix; placed last so each
      file is touched once rather than once per rename (design.md → Resolved Decisions).
      Verify with the Phase 4 criterion run early:
      `grep -rn "create_execution\|implement_tasks\|implement_coordinated" plugin/skills/ | grep -v '/create_execution/\|/implement_tasks/\|/implement_coordinated/'`
      → only the alias stubs' own self-references. (~12 calls) (completed 2026-09-08 18:44) (completed 2026-09-08 18:31)
- [x] **P2-T27** — Delete `docs/beads-integration-learnings.md` (D19). Separate task from
      `P2-T26` because it is orphaned rather than linked, and because design.md's D8 rationale
      cites it — confirm that citation reads as past-tense before deleting. (~5 calls) (completed 2026-09-08 18:39)

### Success Criteria

#### Automated Verification

- [ ] `grep -rn "bd \|BEADS_MODE\|BEADS_AVAILABLE\|beads_epic\|/beads:" plugin/` → **no hits
      outside the three files with later owners**. Working form:
      `grep -rn "bd \|BEADS_MODE\|BEADS_AVAILABLE\|beads_epic\|/beads:" plugin/ | grep -vE 'plugin/(commands/(forge|help)\.md|hooks/setup-beads-mode\.sh)'`
      **Scoped 2026-09-08**, because Phase 2 cannot clear files it does not own. At the time of
      the decision there were 78 hits: `P2-T20`–`P2-T25` clear 35, and the other 43 are
      `commands/help.md` (33, `P4-T2`), `hooks/setup-beads-mode.sh` (8, `P3-T4`) and
      `commands/forge.md` (2, `P4-T1`). Each exclusion names its owning task, so the carve-out
      is auditable rather than blanket. **The whole-tree assertion is not weakened** — it
      already exists verbatim as a Phase 4 criterion covering `plugin/`, `README.md`,
      `CLAUDE.md` and `docs/`, and that is the real gate. See design.md → Resolved Decisions
- [x] `grep -rln "NEVER treat markdown as source of truth\|tracked ONLY in beads\|NEVER check markdown checkboxes" plugin/` → no hits — cleared at `P2-T14`, the last file holding them
- [x] All six directories exist — canonicals `create_tasks`, `implement`, `implement_inline`
      and aliases `create_execution`, `implement_coordinated`, `implement_tasks` — verified;
      34 skills enumerate, each alias holding a stub `SKILL.md` and nothing else
- [x] `P2-T30`: no reshaped skill names a renamed command except the alias stubs themselves —
      `grep -rn "create_execution\|implement_tasks\|implement_coordinated" plugin/skills/`
      returns only hits inside the three alias directories **and in
      `implement/reference.md`'s `## Migration from implement_tasks` section**, which must name
      the old names — that is what migration guidance is *for*. Same exemption design.md's
      success criteria already grant ("no `bd`, `beads`, or `BEADS_MODE` reference outside the
      migration note"); recorded here rather than mangling the migration text to satisfy a grep.
      14 references repointed across `create_project` (8), `create_design` (2), `create_tasks`
      (1) and `create_research` (2, the missing `wb:` prefixes noted at the research cluster)
- [x] `test ! -e docs/beads-fast-fail.md -a ! -e docs/beads-stealth-mode.md -a ! -e docs/beads-integration-learnings.md`
- [x] `grep -L "allowed-tools" plugin/skills/*/SKILL.md` — no workflow skill missing it
- [x] `grep -c 'user-invocable: false' plugin/skills/*/SKILL.md` — set on every background
      discipline skill: `project-structure`, `status-sync`, `tdd-discipline`,
      `verification-before-completion`, `mockup-iteration` (5)
- [x] `grep -rn "determineModel" plugin/` → no hits (D13)
- [x] Exactly one statement of the worker tier rule:
      `grep -rln 'the one statement of the worker tier rule' plugin/skills/` → **exactly one
      file** (`plugin/skills/implement/SKILL.md`, Step 5).
      **Reworded twice, 2026-09-08, and the second time is the instructive one.**
      It began as `grep -rln "Haiku:.*Sonnet:.*Opus:" plugin/`, written against the one-line
      prose shape `P2-T15` replaced — the ladder became a table, so that returned 0, not 1.
      It was then re-pointed at `claude-opus-4-8[1m]`, which **broke within the hour**: `P2-T17`
      added the 1M variants to `model-help`'s roster, so the model ID appeared in two files. PD2's
      own consequence note had said exactly that would happen, which is the lesson — *a criterion
      keyed to a value named in two places was never going to hold, and the plan said so.*
      Now keyed to a **self-describing marker of the invariant itself** rather than a proxy for
      it: the sentence in `implement`'s Step 5 that declares it is the single statement. That
      survives model renames, roster additions, and reformatting, because the thing being counted
      is the declaration, not a value that happens to appear inside it.
      Remaining `haiku` mentions elsewhere are per-`Task()` pins for research agents, agent
      frontmatter, and the main-session authority `model-help` — which now states the D3
      boundary explicitly and points at `implement` Step 5 rather than restating the ladder
- [x] `./plugin/scripts/lint --all` — clean
- [x] `grep -rn "think deeply\|ultrathink" plugin/ CLAUDE.md` → no hits. The last one was a
      **stale doc comment** at `plugin/scripts/README.md:97` justifying the MD036 lint setting
      "for 'think deeply' directives" — a rationale for a convention the tree no longer has.
      Upstream carries the identical stale line at its own `scripts/README.md:59`. Reworded to
      describe what the rule is actually for; a comment justifying a config by a convention
      that no longer exists is precisely the decay D19 targets
- [x] **The headline metric**: `claude plugin details wb` on-invoke total for the fourteen
      stages is **at least 30% below** the Phase 0 baseline recorded in
      `thoughts/2026-09-08-baseline-measurements.md`, with no stage's content deleted
      (supporting files account for the remainder) — **84.9k → 45.3k = −46.6%**, against a bar
      of ≤59.4k. Thirteen of fourteen stages reshaped; `help` is `P4-T2` and still reads −3%
      (noise). Range across the thirteen: `create_mockup` −70% to `resume_handoff` −25%

#### Manual Verification

- [ ] A `--plugin-dir` session invokes `create_tasks`, and its on-demand `templates.md` read
      happens without a permission prompt
- [ ] Each of the three aliases prints its deprecation notice once and then behaves
      identically to its canonical skill
- [x] Spot-read three reshaped skills: no supporting file is referenced that does not exist,
      and no SKILL.md paraphrases content that moved — **replaced with a mechanical audit of all
      fourteen**, which is strictly stronger than three spot-reads. Every heading in each
      pre-split command (at `b635159`) was compared against the union of headings in its new
      skill directory, excluding fenced content.
- [x] Human confirms the token-cost reduction is real reduction, not content loss —
      **audited mechanically; zero genuine loss.** Of the differences found, all fall into four
      classes, each checked by hand: sections **deleted by design** (D4's beads regions, D13's
      `determineModel`), **renames** (`Step 9: Update Status` → `Reconcile Status`,
      `Evolution from implement_tasks` → `implement_inline`, `Output Format` →
      `Resume confirmation`), **restructures** (Step 6's five `####` sub-headings became a
      numbered list; `Read Documentation Files` folded into Step 1), and **moves into supporting
      files** (`Worker Prompt Template` → `sub-agent-prompts.md`, `Update Modified Files Section`
      → `templates.md`).
      **Two deliberate simplifications, recorded rather than buried**: `create_tasks`' template
      dropped the `Week of [YYYY-MM-DD]` weekly-archive convention for "as phases close" (which
      is how phased plans actually archive), and `validate_project`'s report template dropped
      one *example* warning, Missing Git Metadata — the warning itself survives in the
      `Error message formats` section

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

- [x] **P3-T1** — `plugin/hooks/wb-prime.sh`: the orientation mode (stage chain, plan-directory
      convention, where status lives, checkpoints stop for a human, active plans in the
      repository, pointer to `/wb:help`). Under forty lines of output; `--export` support;
      `.claude/wb/PRIME.md` override. (~20 calls) (completed 2026-09-08 17:52)
- [x] **P3-T2** — Same script, the recovery mode: on a compact payload and on PreCompact,
      print that summarized document contents are paraphrase and the plan documents must be
      re-read before being asserted, naming the active plan directory. **Print only — the hook
      writes nothing** (decided 2026-09-08; D8a's PreCompact journal refresh is dropped because
      `P3-T3`'s bootstrap recomputes those fields from the repository anyway). (~15 calls) (completed 2026-09-08 17:52)
- [x] **P3-T3** — Same script, the D8c bootstrap block: plan position from checkbox counts,
      the journal's last entry with its open/closed state, the knowledge-file line, and the
      journal-vs-tree reconciliation. (~20 calls) (completed 2026-09-08 17:52)
- [x] **P3-T4** — Register the hook in `plugin/.claude-plugin/plugin.json` on SessionStart (all
      triggers) and PreCompact; delete `plugin/hooks/setup-beads-mode.sh` and its registration.
      (~8 calls) (completed 2026-09-08 17:58)
- [x] **P3-T5** — Verify the hook contract mechanically: run it against all four payload shapes
      (startup, compact, PreCompact, empty) with `time`, confirm it stays under budget, makes
      no `bd` call, **writes no file** (the decision of 2026-09-08 — verify with a
      before/after checksum of `journal.md` across a PreCompact run), and exits 0 on an unknown
      payload. Record results in
      `thoughts/2026-09-08-baseline-measurements.md`. (~12 calls) (completed 2026-09-08 17:56)
- [x] **P3-T6** — `plugin/skills/doc-adherence/SKILL.md` (D11): `user-invocable: false`; the
      rule that a claim about what a plan document says requires a read of that document in
      the current context window; the identify → check → read → assert gate; a
      rationalizations table; and a section tying it to `wb-prime.sh`'s compaction signal.
      (~15 calls) (completed 2026-09-08 18:06)
- [x] **P3-T7** — `journal.md` (D8a): add the template to `create_project`'s generated plan
      directory, and the open-at-start / close-at-completion protocol to
      `implement_tasks`, `implement_coordinated`, and `create_handoff`. Include the
      PreCompact refresh of an open entry's mechanical fields. (~20 calls) (completed 2026-09-08 18:08)
- [x] **P3-T8** — `.claude/wb/knowledge.md` (D8b): create the file with its header stating the
      entry shape (fact, why it matters, date, source plan, verification hint) and the
      qualification rule. Wire the on-demand read into the research stages, `create_design`,
      both implementation stages, and `resume_handoff`. Add the correct-on-discovery
      obligation. Seed it with the facts this plan itself established. (~20 calls) (completed 2026-09-08 18:12)
- [x] **P3-T9** — Handoff-over-compact guidance (D11): a phase that would need a second
      compaction hands off instead. Lands in `implement_coordinated`'s recommendation text,
      `create_handoff`'s "when to create" list, and `help`. (~10 calls) (completed 2026-09-08 18:14)
- [x] **P3-T10** — `plugin/skills/explore_design/` (D10): the optional stage — frame, diverge,
      discuss, converge only on explicit approval, record. Writes a `thoughts/` exploration
      document whose **top section is the decision record** — chosen direction, rationale,
      rejected alternatives (D6). Never writes `design.md`. **This is the exact shape `P2-T4`
      already consumes**: `create_design`'s Step 1 scans `[project-dir]/thoughts/` for that
      section, so a divergence here means the consumer silently finds nothing and the feature
      never fires. Decided 2026-09-08, see design.md → Resolved Decisions. Includes the model self-check in D12's shape: recommends Opus, names Fable
      as the available upshift, warns below Opus, never blocks. (~30 calls) (completed 2026-09-08 18:20)
- [x] **P3-T11** — The conditional nudge for `explore_design`: the research stages suggest it
      only when findings show more than one viable approach. Word it against the false-positive
      upstream found and fixed — it fires on evidence, not by default. (~10 calls) (completed 2026-09-08 18:23)

### Success Criteria

#### Automated Verification

- [x] `plugin/hooks/wb-prime.sh` exits 0 on all four payload shapes and on empty stdin, and on an unrecognized event
- [x] `grep -c 'bd ' plugin/hooks/wb-prime.sh` → 0
- [x] The script's runtime is recorded and within the contract it inherited — **45 ms median**, against upstream's <100 ms target and a 5 s registered timeout. It also **writes nothing**, checksum-verified across all five runs
- [x] `test ! -e plugin/hooks/setup-beads-mode.sh`; no reference to it in `plugin.json`
- [x] `grep -c 'PreCompact' plugin/.claude-plugin/plugin.json` → 1
- [x] `ls plugin/skills/doc-adherence/SKILL.md plugin/skills/explore_design/SKILL.md`
- [x] `test -f .claude/wb/knowledge.md`; every entry matches the required shape
      (date, source plan, verification hint present) — 6 entries, each with a **Verified**
      line naming the date and source plan and a **Check it** line giving a command
- [x] `grep -rn "journal.md" plugin/skills/ | wc -l` — referenced by the stages D8a names
- [x] `./plugin/scripts/lint --all` — clean

#### Manual Verification

- [ ] A fresh `--plugin-dir` session's first context contains the orientation and, in this
      repository, names this plan directory
- [~] **The D8 acceptance test**: start a session, open a journal entry, make an uncommitted
      edit, then kill the session without any shutdown step. A new session's first context
      reports the entry as **open**, names the attempted work and next action, and names the
      uncommitted changes — **partially verified 2026-09-10, unplanned.** The end-to-end run
      (`docs/plans/2026-09-09-slugify-maxlength`) took a genuine hard close mid-task, with an
      open `P2-T2` entry and uncommitted work in the tree. **Recovery worked**: the resumed
      session picked up from the journal, completed the task, and replaced the open entry with a
      closed one recording what landed (`3fa7e24`) — which is the half D8a exists for, and it
      was not staged.
      **The bootstrap half is not yet verified**, and the same run found why: the journal
      template's example entries were live `##` headings, so the hook's "most recent entry"
      matcher read the *placeholder* — which ends in `(open)` — rather than the real one. Every
      plan therefore reported a phantom interrupted task from creation onward. Fixed in
      `5fb7025` (shapes fenced; the hook additionally skips a heading whose date is still a
      placeholder). **Re-run needed** against a journal created after that fix, checking the
      first context specifically, not just that resumption succeeded
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

- [x] **P4-T1** — `forge` (D4, D6): rewrite the state-detection ladder at `:51-57`. Its first
      two branches key off documents; every branch after keys off tracker state ("no beads
      issues", "beads phases", "All phases closed in beads"). Re-derive all of them from
      documents — which of research/design/tasks exist, their frontmatter status, and checkbox
      counts. Replace the `bd ready` → claim → close phase loop (`:99`) with document-order
      phase advance. The four barriers (`:84`, `:89`, `:95`, `:111`) read the markdown
      `Q1`/`PD1` records instead of `bd list`. Delete cross-cutting rule 1 (`:110`) with its
      link to the deleted fast-fail doc — the only true markdown hyperlink in the group.
      Repoint `:77`, which instructs reading `commands/create_project.md`, at the relocated
      skill path. Update the sequence to name `create_tasks`. Split out
      `examples.md` (`## Examples`) and keep `## Output style` as the template. (~30 calls) (completed 2026-09-08 18:35)
- [x] **P4-T2** — `help`: delete `## Beads Integration` (`:60-96`), the `/beads:*`
      slash-command tables (`:98-125`), `### CLI vs Slash Commands` (`:127-139`, which exists
      only to contrast with the deleted block), and `### Beads + Git Workflow` (`:141-153`).
      Reverse the per-command annotations that name beads as the status source — notably
      `:181-184` ("Uses beads as source of truth") — and `## Core Principles` item 5
      ("Beads Required"). Delete `:245-246`, which points at the `v1.0.0` tag for a
      "markdown-only workflow": that mode is what this release restores as the only mode.
      Rewrite the workflow chain to include `explore_design` and `create_tasks`, and add a
      "where status lives" section (checkboxes, counters, git) plus D8's continuity artifacts.
      **No supporting-file split** — this stays a single SKILL.md, matching upstream's `help/`,
      which has no siblings. (~25 calls) (completed 2026-09-08 18:42)
- [x] **P4-T3** — `docs/workbench-workflow-guide.md`: the 47 `bd` lines go; the model map gains
      D12's upshift ladder and the `create_tasks` row; the stage chain gains `explore_design`;
      the beads-doc links are removed. Largest single doc rewrite. (~30 calls) (completed 2026-09-08 18:52)
- [x] **P4-T4** — `docs/commands-reference.md`: rename `create_execution` → `create_tasks`
      with the alias noted; drop the beads sections; reconcile `:408` ("Update task checkboxes
      as you complete work") which becomes *correct* under D4 rather than contradictory.
      (~25 calls) (completed 2026-09-08 18:57)
- [x] **P4-T5** — `docs/claude-code-skills-guide.md`: record the progressive-disclosure
      convention, `allowed-tools: Read`, `user-invocable: false`, and the alias-stub pattern as
      house conventions. (~15 calls) (completed 2026-09-08 19:01)
- [x] **P4-T6** — `README.md` and `CLAUDE.md`: the stage chain, the tracker-free tracking
      philosophy replacing "Beads Required", the `plugin/`-aware local-dev instruction, the
      `docs/` shipped-vs-maintainer boundary, and D19's where-rules-may-live rule. Fix the
      duplicated `## Output Discipline` heading in `README.md`. (~20 calls) (completed 2026-09-08 19:06)
- [x] **P4-T7** — `CHANGELOG.md` (D17): new file. A `[2.0.0]` entry with **Breaking**
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
      history is worth keeping anywhere (design.md D19 trade-off). (~20 calls) (completed 2026-09-08 19:10)
- [x] **P4-T8** — Version bump to 2.0.0 in **both** `plugin/.claude-plugin/plugin.json` and
      `.claude-plugin/marketplace.json`, same commit. Verify with
      `claude plugin tag --dry-run plugin/`. (~8 calls) (completed 2026-09-08 19:04)
- [x] **P4-T9** — Final full verification sweep: every automated check from every phase, plus
      the end-to-end pipeline run below. Record results in the journal and close the plan's
      frontmatter status. (~20 calls) (completed 2026-09-08 19:20)
- [ ] **P4-T10** — Tag the release: `claude plugin tag plugin/` (creates `wb--v2.0.0`,
      validating manifest agreement), then push. Note the harness's tag convention is
      `wb--v<version>`, not upstream's `v<version>`. (~6 calls)

### Success Criteria

#### Automated Verification

- [x] `grep -rn "bd \|beads\|BEADS_MODE\|/beads:" plugin/ README.md CLAUDE.md docs/ | grep -v docs/plans | grep -v CHANGELOG.md` → **one hit**, `implement/reference.md`'s Migration section, which design.md's success criteria exempt ("outside the migration note")
- [x] `grep -rn "create_execution" plugin/ docs/ README.md CLAUDE.md | grep -v docs/plans` — only
      as the deprecated alias, plus the migration notes in `implement/reference.md` and
      `commands-reference.md` that exist to name the old command
- [x] `grep -c 'explore_design' plugin/skills/help/SKILL.md CLAUDE.md README.md docs/workbench-workflow-guide.md`
      → 1 or more each (3 / 1 / 1 / 2)
- [ ] Both manifests read `2.0.0`; `claude plugin tag --dry-run plugin/` exits 0 with no
      warnings — manifests done; the tag check runs after the release commit, per `P0-T3`'s
      finding that `tag` refuses a dirty tree
- [x] `CHANGELOG.md` has `### ⚠️ Breaking` and `### Migration` sections under `[2.0.0]`
- [x] `./plugin/scripts/lint --all` — clean (D16 now makes this meaningful)
- [x] `claude plugin details wb` — final inventory and token cost recorded against baseline, in `thoughts/2026-09-08-baseline-measurements.md` → Final measurements

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
  same-directory supporting files (A4; `P0-T1` probes both deliberately) — **answered wrong on
  2026-09-08, corrected 2026-09-09.** The smoke session reported no prompt on either read and
  the assumption was flipped to Validated. It is **false**: `allowed-tools` has nothing to do
  with it. Reads of the plugin directory are gated by the **working-directory boundary**, and
  three headless probes denied them under `--plugin-dir` and again for a marketplace install;
  only `--add-dir` passes. The 2026-09-08 session never recorded its **cwd** — run from inside
  the probe directory, the boundary cannot fire, which is why a real defect measured clean.
  **The transferable lesson is about the probe, not the feature: state the environment a
  measurement was taken in, or the measurement is not reproducible and may not be a measurement
  at all.**
- ~~The real reduction ratio per stage~~ — **answered 2026-09-08.** Final: **84.9k → 45.3k =
  −46.6%** across the fourteen stages, thirteen reshaped. Two findings worth keeping:
  **(1)** line reduction ran roughly **twice** the token reduction, because what moves out —
  fenced blocks, templates of short bracketed lines — is far sparser per line than the prose
  that stays. Size splits by tokens, never by `wc -l`. **(2)** The per-stage range, −70%
  (`create_mockup`) to −25% (`resume_handoff`), tracks the **ratio of template to judgment**,
  not split quality: a stage that is mostly output shapes wins big, a stage that is mostly
  reasoning barely moves, and one whose task *adds* judgment (D8c on `resume_handoff`) moves
  least of all.
- ~~Whether the PreCompact journal refresh can be done in the hook without judgment, or needs a
  model-written line (D8a assumes mechanical fields only)~~ — **answered 2026-09-08: neither,
  because the refresh is unnecessary.** The three mechanical fields are the ones D8c's bootstrap
  recomputes at the next session start, from the repository, which it already treats as
  authoritative over the journal. `wb-prime.sh` stays read-only and print-only, keeping its
  inherited no-subprocess contract and unable to corrupt `journal.md`. D8a amended in place;
  decision in design.md → Resolved Decisions

## 📝 Completed Tasks Archive

Move completed tasks here as phases close, to keep the active list readable.

## 🚧 Blockers & Notes

### Current Blockers

None open.

- **2026-09-08 — the `create_execution` → `create_tasks` rename has seven callers no task
  owns.** Raised by `P2-T6`. **Resolved 2026-09-08** → new task `P2-T30` sweeps them, and every
  other renamed name's callers, once at the end of Phase 2; decision in design.md →
  Resolved Decisions. Original detail retained below for the audit trail. Phase 4's criterion is
  `grep -rn "create_execution" plugin/ docs/ README.md CLAUDE.md | grep -v docs/plans` →
  *only as the deprecated alias*. Eight references currently fail that: `model-help:64` (owned
  by `P2-T17`, fine) and **seven that no task covers** —
  `create_project/SKILL.md:146`, `create_project/templates.md:35,49,298,304`,
  `create_design/templates.md:141`, `create_design/SKILL.md:242`. Not urgent: the alias
  resolves, so nothing is broken — they simply name a deprecated command. But `P4-T1`
  (`forge`), `P4-T2` (`help`) and `P4-T4` (commands-reference) are the only rename-sweep tasks,
  and none of them reaches a `create_*` skill body. Needs either a decision to fix them inside
  the rename that created them, or a new Phase 4 task.

- **2026-09-08 — `lint --all` cannot be clean while `.context/upstream/` exists.** Raised by
  `P0-T4`. `--all` builds its file list with a raw `find .` and a hardcoded exclusion list
  (`scripts/lint:115-125`) that does **not** consult `.gitignore`, so it walked the gitignored
  upstream export and returned 84 findings — **all 84** in `.context/upstream/`, **zero**
  anywhere we author or ship. Pre-existing, not caused by the D16 fix (plain mode already
  exited 1). **Resolved 2026-09-08** → decision recorded in design.md
  (## Technical Decisions → Resolved Decisions); carried by new task `P0-T6`.

### Implementation Notes

### Promotion is a one-time act; plan directories keep growing (2026-09-10)

Found while committing this handoff. `journal.md` — the file D8 exists to provide — **had never
been committed.** It lived on disk, gitignored and untracked, from creation until `fbf6532`.

The cause is not the gitignore policy, which is deliberate (plans are ignored until promoted on
trigger). It is that **promotion happened once, over the files that existed at the time**, and
`journal.md` was created afterward. Nothing re-runs the force-add, and `git status` never
mentions an ignored file, so the omission is invisible by construction. Two other file kinds
land after promotion the same way: `handoff-*.md` and `thoughts/`.

What this cost, honestly: the D8 acceptance test's "recovery worked" result is narrower than it
read. Recovery worked *on the same machine*, off the disk. Had the resumed session been a fresh
clone or the user's second machine, there would have been no journal to resume from — which is
the cross-machine continuity case D8 was written for. The mechanism was sound; its durable copy
did not exist.

`create_handoff` already documents re-running `git add -f <plan-dir>/` (SKILL.md:170), which is
the right instinct and would have caught this. The gap is that nothing *checks*. The check is
one command and returns exactly the stragglers:

```bash
git ls-files --others --ignored --exclude-standard docs/plans/<dir>/
```

Clean across all plans as of `fbf6532`. Filing rather than fixing, per D20 — but note this is
the fourth instance of the plan's recurring lesson, and the sharpest: *when several consumers
agree on a format, something must state it and something must check it.* Here promotion was
stated in four skills and checked in none.

### D8's open-entry heuristic has only two states, and there are three (2026-09-10)

`wb-prime.sh` reads an open entry beside a clean tree as "a session left it open without
finishing the close-out." That is right for the case it was designed for. It is wrong for the
case that actually came up while writing this plan's own handoff: an entry opened because work
is genuinely in flight **in a different process** — a separate Claude testing session — with
nothing uncommitted in this tree to show for it.

The warning is still useful (it sends the reader to the entry, which explains itself), so this
is a follow-up rather than a fix, per D20. If it is worth closing later, the cheap version is a
third state keyed off the entry naming a delegate; the honest version is admitting the working
tree cannot observe another process and saying so in the warning text.

Filed while handing off, which is when the gap became visible — the handoff is the first thing
in this plan to have work pending somewhere the tree cannot see.

- **2026-09-10, the D8 acceptance test happened by accident, and was worth more than the staged
  version.** The end-to-end run took a real hard close mid-task. Recovery worked: the resumed
  session found the open `P2-T2` entry, finished the task, and closed the entry with its commit.
  Several decisions were exercised at once and held —
  **D20** (the worker found dead code, *measured* that it was dead across 33 tests and a 76-pair
  differential probe, then declined to remove it as out of scope and escalated the call to the
  checkpoint — follow-ups-not-fixes and the completeness clause, both firing);
  **D14** (a rejected tool call would have swapped a source file in place while uncommitted work
  sat in the tree; the recovery re-ran the probe in a scratchpad, preserving the
  uncommitted-work signal truncation detection depends on);
  **D5** (counter drift surfaced and deferred to `/wb:update_status` rather than hand-patched);
  **D4** (one task, one commit); **D21** (`docs/` stayed untracked); and the phase checkpoint
  stopped for a human instead of self-certifying.
- **2026-09-10, but the same run found that the bootstrap half was broken — by me.** The
  `journal.md` template `P2-T5` wrote used live `##` headings for its example entries, and the
  hook reads the first `##` as the most recent entry. Since the example ends in `(open)`, every
  generated plan reported an interrupted task from the moment it was created, permanently, while
  the real latest entry was never read. Fixed in `5fb7025`.
  Worth naming plainly: **this is the third time in this plan that something was "verified" by a
  grep or a shape check rather than by running it.** The template linted clean, the hook exited
  0, the matcher matched — and the feature was inverted. The Phase 3 automated checks I ran
  could not have caught it; only reading the hook's actual output against a real generated plan
  could, which is what the end-to-end run did.

- **2026-09-09, live testing falsified A4 and the section-read mechanism with it.** The two
  Phase 2 manual criteria were finally run. Both findings are things no grep could have reached,
  and both were latent in `P4-T9`'s "all green".
  - **A4 is false.** Five headless probes, **each with its cwd recorded**: a Read of a supporting
    file is DENIED under `--plugin-dir` from a project cwd; DENIED for a **marketplace-installed**
    plugin reading its own root; passes only with `--add-dir`; and a discriminating control pair
    showed path-scoped `Read(<plugin-root>/**)` does **not** cross the boundary. **A plugin cannot
    self-grant.** The gate is the working-directory boundary, which `allowed-tools` does not
    touch. `P0-T1`'s probe recorded `NO PROMPT` truthfully and concluded wrongly because **it
    never recorded its working directory** — run from inside the probe directory, the boundary
    cannot fire. *A probe that cannot fail is not evidence, and the way this one could not fail
    was invisible until someone asked where it ran.*
  - **This is a 2.0.0 regression, not an inherited condition.** Installed 1.12.4 has **zero**
    supporting-file read instructions; its stages were monolithic. Progressive disclosure creates
    the dependency.
  - **`Read` has no section parameter.** The 33 "read the `## X` section of templates.md"
    instructions had no correct implementation — only `offset`/`limit`. Observed live: asked for
    a section starting at line **291**, the model read **180–239**, inside a fenced skeleton.
  - **Upstream does not solve either.** It has 11 section-scoped reads (we had 33), no section
    maps at all, and its `CHANGELOG.md:176` makes the same prompt-free claim these probes
    disprove — plausibly true when written, since the boundary setting looks newer than its
    3.0.0. Diverging from upstream here is deliberate.
- **2026-09-09, what was changed in response.**
  - **14 supporting files → 48**, one per readable unit, under `templates/`, `prompts/`,
    `reference/`. A whole-file read now *is* the scoped read. `grep -rn 'Read the \`##'
    plugin/skills/` returns **0**. A renamed heading can no longer break a read silently, and a
    wrong path fails loudly instead of returning the wrong lines.
  - **`allowed-tools` states each skill's real surface** — `implement` names
    `Read, Write, Edit, Glob, Grep, Bash, Task`, `help` names `Read`. It is a pre-approval, so
    this **removes the prompt before writes and commits**; recorded under Breaking rather than
    filed as a doc fix, because it is a behaviour change.
  - **A refused read is a hard stop**, in all 16 manifests. This is the only change that prevents
    wrong output rather than annoyance: a session with outside reads blocked previously wrote a
    plausible document from the manifest alone, with no error.
  - A4 corrected to **false** in design.md, tasks.md, the baseline thoughts doc and the skills
    guide; boundary documented in README and the per-machine migration list; two `wb-prime.sh`
    fixes (plans ordered by date-prefix rather than mtime, elision at a word boundary); two
    knowledge entries.
  - **Cost, stated honestly**: fourteen-stage invocation 46.8k → **51.1k (+9.2%)**, still
    **−39.8%** on the 84.9k baseline and 8.3k inside the ≤59.4k bar. Per-run cost moves the other
    way — `create_mockup` no longer reads 389 lines to write one artifact — and that is the
    number the split was actually for.

- **2026-09-10, A4 resolved: the two probe sets never actually disagreed.** The 2026-09-09
  finding above ("DENIED for a marketplace-installed plugin reading its own root") and a
  2026-09-10 interactive probe that read the same class of file *successfully* are **both
  correct**. They measured contexts that differ in whether anything *can* grant the permission.
  - **There are two denials with two different messages, and conflating them was the whole
    confusion.** `Claude requested permissions to read from …, but you haven't granted it yet`
    is the ordinary grant flow — that is what the plugin cache produces. `… is outside <cwd>;
    the permissions.blockReadsOutsideWorkingDirectories setting blocks reads outside the working
    directories` is the setting, and it does **not** fire on the plugin cache. Three-way
    headless probe, cwd `/tmp/wbe`, no `--add-dir`, no `--plugin-dir`: an in-working-directory
    read **succeeded** (ruling out the tool-permission confound that would fake a denial), the
    cache read was denied by the *grant* message, the tallinn path by the *setting* message.
  - **The variable is permission mode, not headlessness.** `default` → denied; `acceptEdits` →
    denied (so it is not merely "auto mode is permissive"); `bypassPermissions` → succeeds;
    interactive → prompts, and the maintainer confirmed answering that prompt. No persisted
    grant exists for the plugin path — `~/.claude/settings.local.json` holds only
    `Read(//opt/homebrew/**)`-family entries, which proves this machine *does* persist "allow
    always" when chosen — so the interactive success was an allow-once click, not an
    auto-exemption.
  - **There is no design problem underneath.** Progressive disclosure is one prompt on first use
    for interactive users and a hard stop for headless/CI, where nothing can grant. The context
    result stands; nothing was inlined back, no postinstall copier was written.
  - **What was actually wrong was the documentation**, fixed this date. `README.md` asserted
    "every supporting-file read is denied" without `--add-dir` — false for interactive users;
    it and `CHANGELOG.md` both attributed the gate to `blockReadsOutsideWorkingDirectories` —
    wrong mechanism; neither mentioned headless/CI — the real breakage; and
    `grep -rn 'plugins/cache' README.md CHANGELOG.md plugin/` returned **nothing**, so the
    marketplace-install path, which is every copy but a development checkout, had no guidance at
    all. Both now split interactive from headless and name
    `Read(//Users/<you>/.claude/plugins/cache/**)` as the direct grant; the skills guide's
    superseded "working-directory boundary" paragraph was replaced.
  - **`validate_project` does not glob** — raised as a caveat because the probing session had no
    Grep/Glob. Its `reference/` split is **four** files, each reached by an explicit named link
    (`SKILL.md:14`, `:115`, `:153`). There is no glob path, so the untested surface does not
    exist.
  - Still unconfirmed, low risk: the probes ran against **1.12.4's** installed tree; 2.0.0's
    cache path differs only in the version segment.
  - *The transferable lesson: two probes that disagree have usually measured two different
    things. Reading the denial **message** instead of the pass/fail bit is what settled a
    question that had held the release for two days.*

- **2026-09-10, the journal bug's twin, found by Item 3's cold read.**
  `create_tasks/templates/tasks-md-template.md:197-200` pre-printed **four `✅` marks** in the
  phase checkpoint block, so every generated plan asserted its own checkpoint from the moment of
  creation. In the slugify run this produced nine of them (`tasks.md:287-290`, `:473-477`),
  including `✅ Manual verification confirmed by human` while all six of that phase's manual
  boxes were `[ ]`, and `✅ Run /wb:update_status` before `update_status` had ever run — three
  lines above the template's own **"Do not proceed without human confirmation of manual tests."**
  - **Same class as `P2-T5`/`5fb7025`**: template decoration that a reader takes as live state.
    The journal one used `(open)` and fooled a hook; this one used `✅` and fools a human. Both
    linted clean and neither was reachable by any shape check.
  - **This is the cause of the `tasks.md:1021` cold-read failure**, not a separate symptom. A
    cold reader concludes the plan is fully checkpointed and nothing remains, while
    `status: in-progress` says the opposite. Question 3 — "what happens next?" — is not just
    unanswerable but actively misleading.
  - **Fixed**: the block is now four unchecked checkboxes under the sentence *"These are the
    conditions to meet before Phase 2 — not a record of having met them."* Verified with a
    control that fires: the four new lines match the task-ID counter pattern **0** times while
    the template's real task lines match **10**, so the checkpoint cannot inflate any count.
  - **Scope checked, not assumed.** A sweep of every shipped template found `✅` in 15 files;
    all the others are **transient chat messages** (`✅ Design document created`, `✅ Phase
    complete`) where the glyph is true when printed. `create_project/templates/readme-md-template.md:25`
    marks only the one step that has actually happened and leaves the rest `⏳`. The persisted
    artifact written by `create_tasks` was the only defect.
  - *`⏸️ Not Started` in the progress tables is the opposite failure mode and is safe: a
    conservative default that `update_status` reconciles. `✅` was an optimistic false claim
    nothing owned.*

- **2026-09-10, D8 re-verified across sessions: PASS.** The first D8 check was a shape check and
  passed while the feature was inverted, which is why this one was re-run. Session A
  (`/wb:create_project`) wrote `docs/plans/2026-09-10-semver-compare/journal.md` in a scratch
  repo at `~/projects/wb-e2e`; session B was then started fresh and its **real SessionStart
  hook** produced, verbatim:

  ```text
  Active plan: docs/plans/2026-09-10-semver-compare
  Position: phase 0, 1 of 4 tasks done.
  Next unchecked task: **P0-T2** — Complete research using `/wb:create_research docs/plans/2026-09-10-semver-compare`
  Journal: present, no entries yet
  ```

  No phantom interrupted task, no open-entry warning. The hook took the **`present, no entries
  yet`** branch rather than the "most recent entry" branch — which is precisely where the
  placeholder would have surfaced as `(open)`. `5fb7025` holds across sessions.
  - **The verdict is cross-session by construction**, which is what makes it worth anything: the
    writing session deliberately declined to record a verdict, on the grounds that a hand-run of
    `wb-prime.sh` is the same process that wrote the file. That is the discipline the first D8
    check lacked.
  - **The two defenses are independent, and only one is load-bearing for this hook.** The
    matcher is `grep -E '^## ' | grep -vE '\[YYYY|<YYYY|YYYY-MM-DD'` — **not fence-aware**. The
    example headings still sit at column zero inside the ```` ```text ```` fence; what saves them
    is the placeholder filter. Both were added together in `5fb7025` and the reasoning is in
    `wb-prime.sh:145-147`, so this is intentional, not luck.
  - **Filed, not fixed**: `journal-md-template.md:31-32` tells a future editor the examples "are
    shown fenced because an unfenced example is itself a `##` heading, and would be read as the
    most recent entry." That explanation is **wrong** — the fence is not what protects this hook.
    An editor who believed it could swap the `YYYY-MM-DD` placeholders for realistic dates and
    re-open the bug with the fence intact. The hook checks the contract; the template states it
    incorrectly.
  - **Also filed**: `create_project` splits a prose argument positionally into
    project-name / base-dir / ticket-ref with no prompt and no rejection, silently producing a
    wrongly-named plan directory. And the PostToolUse lint hook rewrites every generated file —
    on `journal.md` it only trimmed a space inside inline code, but a formatter with write
    access to the journal is another route to breaking it later.

- **2026-09-10, two fixes taken rather than filed, both pre-tag.**
  - **The journal template explained its own protection wrongly.** It told a future editor the
    examples are fenced "because an unfenced example is itself a heading, and would be read as
    the most recent entry." That is false: the hook's matcher is not fence-aware, the example
    headings still sit at column zero inside the fence, and what actually protects them is the
    placeholder-date filter. An editor who trusted that sentence could swap `YYYY-MM-DD` for a
    realistic date and re-open the original bug with the fence fully intact. Now states the real
    contract — keep the literal placeholder, the fence is readability only. Re-verified: the
    matcher still returns nothing against the template.
  - **The lint hook had no `Bash` matcher, so heredoc writes bypassed it entirely.** Found by
    the end-to-end session, which wrote `research.md` with a Bash heredoc and noticed the format
    gate never fired. This is not an edge case: the harness tells sessions in auto/bypass mode to
    *prefer* Bash for file changes, so **the default path for such a session had no gate at
    all** — and the session recording this note had been doing exactly the same thing all day,
    caught only by running `./plugin/scripts/lint` by hand each time. Two independent sessions,
    same silent bypass.
    - Fixed by adding a `Bash` matcher and a Bash branch that lints the `.md` paths named in the
      command — **but only those modified in the last minute.** Without that guard, merely
      *reading* a markdown file (a `grep`, a `cat`) would have had `--fix` silently rewrite it,
      which is a worse failure than the one being fixed.
    - **Verified with a control that fires**: a Write payload lints; a Bash payload that wrote a
      fresh file lints; a Bash payload that only read a **lint-dirty** file (2 real MD errors,
      confirmed separately) stays silent; a Bash payload with no markdown stays silent. The
      silence is the mtime guard working, not a clean file.
    - Cost measured, since this now runs after *every* Bash call: **~27ms** on the
      no-markdown path, against a 5s timeout.
    - Degrades honestly without `jq`: a Bash command is a multi-line JSON string that grep/sed
      cannot extract reliably, so the Bash branch is skipped rather than guessed at. Write and
      Edit keep their existing fallback.

- **2026-09-10, the end-to-end run (criterion 1020) — what it found.** A full
  `create_project → create_research → explore_design → create_design → create_tasks → implement
  → validate_execution` in a scratch repo, 17 tasks, 43 tests, 13 implementation commits.
  - **Check 1 PASS**: the generated plan carries **zero** pre-printed checkmarks in its
    checkpoint blocks, and the `84da251` framing sentence appears verbatim in all **three**,
    each adapted per phase. Verified in the artifact, not the report.
  - **`lint`'s fallback config used a dead option name — FIXED.** `plugin/scripts/lint` writes a
    temporary markdownlint config when a project has none, and it specified
    `"MD024": { "allow_different_nesting": true }`, which modern markdownlint does not recognise.
    The `create_tasks` template deliberately repeats `### Objective`, `### Prerequisites` and the
    rest once per phase, so MD024 fired on every one. **Measured on the generated plan: 24
    errors with the shipped fallback, 0 with `siblings_only`** — same file, same linter, one
    option name. This repo passed only because its own `.markdownlintrc` already used the
    current name, so wb's template was unlintable *everywhere except here*. A gate that could
    not pass, beside a `lint-hook` that exits 0 regardless, so nothing ever noticed. Corrected
    and re-proved through the real script in a config-less repo.
  - **Workers fabricate completion timestamps.** The plan accumulated times in the *future*
    (18:05, 18:31 recorded at 17:41), three hours in the past (14:32), and non-monotonic
    (17:30 → 17:23) — with `P0` entries in UTC and worker entries in local time.
    `agents/task-worker.md:64` and the template both say to append `(completed YYYY-MM-DD HH:MM)`
    but neither says to **read the clock** or fixes a timezone. Not cosmetic: a cold reader sees
    a task completed ten hours before the plan containing it was generated, which corrupts
    "what is done, and in what order" — criterion 1021 directly. The run normalised against
    `git log`, which is the truthful record. **Filed, not fixed.**
  - **The cold read found two real defects, both in "what happens next" again.** The
    `### Next Action` section contradicted itself — prose saying all 17 tasks were complete and
    to run `validate_execution`, above a stale template line still reading
    `**Run**: /wb:implement`. And the Progress Overview showed every phase `✅ Complete` while
    every checkpoint condition sat unticked. Both corrected in the run. Notably the session
    **refused to tick "Manual verification confirmed by human"**, because no human had — the
    exact self-certification `84da251` removed.
  - **A test that passed for the wrong reason**, found by the coverage agent and independently
    confirmed: all three negative-component forms are rejected, but every one fails on
    core-arity because the leading `-` is consumed by the pre-release partition, so the
    "not a non-negative integer" branch is never reached with an actual negative. Behaviour
    correct, test vacuous. Fifth recurrence of this class on this plan.
  - **Strongest positive result**: the regression agent walked the entire commit history and
    confirmed every RED commit genuinely fails and every GREEN genuinely passes, with test
    counts rising monotonically 8 → 18 → 25 → 33 → 37 → 43. That is direct evidence the
    RED-GREEN cycle was *executed* rather than asserted — something no checkbox can prove.
  - **Item 2 re-confirmed incidentally at end of run**: simulating the hook against the
    now-populated journal read `## 2026-09-10 21:36 — P3-T4 (closed)` as newest, with 13 real
    closed entries, 0 real open, and the fenced template placeholders filtered **by the
    `YYYY-MM-DD` guard rather than by the fence** — independently confirming the correction made
    to that template's explanation.
  - **The human checkpoint was crossed on standing authorization twice more** (Phase 1 and
    Phase 2), each time flagged explicitly rather than self-certified. Same shape as the
    `design.md` approval: a "run to completion" instruction issued *before* the artifact existed
    is being read as confirmation *of* it. Still open.

- **2026-09-10, Item 4 and the closing verdicts.**
  - **Criterion 1021 PASSES.** The corrected `tasks.md` answers all three questions from the
    document alone: 17/17 across 4 phases with a library, a CLI and 43 tests; Phase 3 complete;
    next step is validation, not implementation. Worth stating plainly: **it passed only after
    the cold read failed first and the defects were fixed.** The criterion did its job by
    failing.
  - **The MD024 fix was verified discriminatingly, not just by a clean exit.** Three checks, any
    of which could have failed: the duplicate headings are **still in the file** (4× `### Objective`,
    3× `### Prerequisites`), so the clean result comes from `siblings_only` rather than from the
    document changing; the linter still fails on a deliberately broken file (MD040); and MD024
    **still fires** on a true sibling duplicate under one parent. The rule was narrowed, not
    blinded.
  - **All three deprecated aliases PASS.** Notice fired exactly once each, correct canonical
    loaded (`create_tasks`, `implement`, `implement_inline`), each stub holds only `SKILL.md`
    with no duplicated behaviour, and **nothing wrote** — the plan checksum was unchanged before
    and after. The run deliberately stopped before each canonical executed, since following
    through would have had `create_tasks` regenerate the finished plan. So this verifies
    notice-once and correct dispatch, not downstream behaviour, which the pipeline run exercised
    directly. The `implement_tasks` notice additionally disambiguates `implement` from
    `implement_inline` — the one place a user could pick the wrong successor.
  - **The checkpoint-tick question, answered better than it was asked.** My framing — "two
    derived surfaces with one writer" — was wrong, and treating them as symmetric is itself the
    error. The Progress Overview *is* purely derived. The checkpoint block is **mixed**: of its
    four conditions exactly one (`Every Phase N checkbox is [x]`) is derivable from the
    document, while the other three are attestations about acts outside it — tests were run, a
    human confirmed, `update_status` was run.
    - **So auto-reconciling would be a regression, not a fix.** Having `update_status` tick
      those boxes would machine-tick "Manual verification confirmed by human" on its own
      authority — the `84da251` bug restored through a different door. Correct-but-unticked is
      the right default for an attestation, and this run proves it: leaving that box `[ ]` is
      the only reason the finished plan honestly records that no human ever signed off.
    - **The real defect is narrower and twofold.** (a) *The tick has no owner and no moment* —
      the block says "Tick each one as it is actually satisfied" but no stage ever does it;
      `implement` Step 8 is the natural home, being the one step holding the human's
      confirmation, yet it stops at emitting the completion report. An instruction with no
      executing step means every finished plan self-contradicts. (b) *The block does not
      distinguish facts from attestations*, so an unticked checkpoint under a `✅ Complete`
      phase reads as a contradiction rather than as "work done, sign-off pending."
    - **Filed, not fixed.** Shape of a fix: `implement` Step 8 ticks the mechanically-verifiable
      boxes after its verification run, and the human-confirmation box only after the human
      answers; marking the derivable box as derivable removes the remaining ambiguity.
  - **`/compact` cannot be self-triggered** — it is a built-in CLI command, not a skill, and no
    tool initiates compaction. That limitation is intrinsic to the test rather than incidental:
    the criterion is what the `PreCompact` hook puts in front of a session *without* its
    involvement, the same cross-boundary property that made Item 2 meaningful. It requires the
    human to type it. **Still open — the last unverified criterion.**

- **2026-09-10, `design-md-template.md` contradicted itself about where a resolution is
  recorded — FIXED.** Two bullets eight lines apart gave opposite instructions for the same
  cell: `:126` said **"Resolution goes in `State`, never in `Blocks`"** and explained that
  overwriting `Blocks` destroys the record of why the row mattered, while `:134` told
  `/wb:resolve_questions` to set **`Blocks`** to `— resolved YYYY-MM-DD`. Whichever a session
  followed, the other bullet declared it wrong.
  - The direction was settled by the consumer rather than by preference:
    `resolve_questions/SKILL.md:192` sets the **`State`** cell, and five other templates
    (`create_research`, `create_product_research` ×2, `create_mockup`, and `:126` itself) agree.
    `:134` was the lone outlier. Corrected to `State`, with `Blocks` explicitly left as written.
  - Same class as the journal template's wrong explanation: a shipped file stating a contract
    its own implementation does not follow. Third instance on this plan of *"when several
    consumers agree on a format, something must state it and something must check it"* — here
    two halves of one file disagreed and nothing checked either.

- **2026-09-10, the `/compact` criterion was attempted and returned UNVERIFIED — correctly.**
  The session received no `PreCompact` output and refused to report one. Its evidence was
  positive rather than merely an absence: it still held pre-compaction detail at full fidelity —
  the P2-T1 failure split (33 `<`-variant, 1 `>`-variant `TypeError`), the plan checksum
  `9a68230bfff814be`, and the RED/GREEN ladder 8 → 18 → 25 → 33 → 37 → 43 — all of which a
  compaction would have collapsed into paraphrase, which is exactly what the expected hook line
  warns about. Their survival verbatim is evidence no summarisation occurred.
  - **Verdict recorded as UNVERIFIED, not PASS and not FAIL**, because the precondition never
    happened. Reporting either would have invented evidence for the one criterion whose whole
    value is that it cannot be reproduced from inside the session's own process.
  - **Cause was the instruction, not the plugin**: the `/compact` command was clipped inside a
    larger block of prose, so pasting it sent the slash command as message text and it never
    fired. A slash command has to be sent alone.

- **2026-09-10, `/compact` attempt 2 — the session reported FAIL; the correct verdict is still
  UNVERIFIED, because the test ran in the one state where the feature does nothing.**
  Compaction genuinely occurred this time and no recovery text reached the model, so the
  observation is sound. The *diagnosis* is not.
  - The session concluded the cause was `PreCompact` stdout not being model-visible, citing the
    hook's own header comment (`wb-prime.sh:12-13` — "SessionStart's stdout is model-visible;
    PreCompact's is not"), and explicitly ruled out the early-exit: *"the candidate list was
    non-empty."* **That is the one claim it did not test, and it is false.**
  - `wb-prime.sh:78` reads `[ "$status" = "complete" ] && continue` — the candidate scan
    **skips completed plans**. `docs/plans/2026-09-10-semver-compare/tasks.md` carries
    `status: complete`, so `count` was 0 and line 86 exited before printing anything.
  - **Measured, with a control that fires**: a `PreCompact` payload run against the real plan
    emits **0 bytes**, exit 0. The same payload against a byte-identical copy with only
    `status:` flipped to `in-progress` emits the full four-line recovery text. The difference is
    that one field.
  - **So the criterion was never exercised.** `tasks.md:894` says "triggering `/compact`
    **mid-plan**"; the plan was finished. The test design did not match the criterion, and the
    session's own caveat — *"the recovery text earns its keep on a half-done plan, and that case
    was not exercised"* — was closer to right than its verdict. It found the gap and then did
    not connect it to the early exit.
  - **Two candidate causes remain, and they are separable.** (a) the completed-plan early exit,
    now confirmed to have fired; (b) the stdout-visibility claim in the header comment, which is
    the plugin author's own statement and remains **untested**, because (a) meant no text was
    ever emitted to be seen. The clean experiment is a `/compact` in a session whose active plan
    is **in-progress**: text appears → the comment is stale and the criterion passes; nothing
    appears → (b) is confirmed and the `PreCompact` hook is decorative for every plan.
  - **A third finding stands regardless of which way that lands.** The recovery branch
    `exit 0`s at line 95, *before* the orientation block at 98. So even with visible stdout it
    emits the paraphrase warning, the plan path and two re-read instructions — and never a phase
    or task count. `tasks.md:894` expects "the recovery text" including position; the code
    cannot produce position on its best day. The criterion is broader than the implementation,
    and that mismatch is real independent of visibility.
  - **Filed from the same run**: `tasks.md` frontmatter carried `git_commit: f00d561` against
    HEAD `505a577` — counter drift in the one field `update_status` refreshes from git.
  - *Worth keeping: the session refused to round agreement-after-re-read into a vindication,
    on the grounds that a finished plan has counts that cannot drift, so it was near the
    easiest possible test of a mechanism built for plans in flight. That reasoning was right,
    and it points at exactly the re-test now required.*

- **2026-09-08, adversarial review of Phases 1–4, run after `P4-T9` declared every phase's
  checks green.** Ten findings; **eight fixed in the tree**, two need a live session. The
  pattern is one thing, not ten: **every capability verified by grep passed; every capability
  that had to be *run* was broken or unrun.** `P4-T9` re-ran the greps, which is why it missed
  all of it.
  - `plugin/hooks/wb-prime.sh` — `grep -c … || echo 0` yields `"0\n0"`, because `grep -c`
    prints `0` *and* exits 1. `$((done_n + left_n))` then died with a bash syntax error printed
    into the model's first context. Trigger: any `tasks.md` with no ID-carrying task lines —
    i.e. **every plan freshly made by `/wb:create_project`**. Fixed with a `count()` helper.
  - `plugin/hooks/wb-prime.sh` — `[ -d .git ]` is **false in a git worktree** (`.git` is a
    file) and absent from a subdirectory, so `dirty` stayed 0 and the hook asserted *"the tree
    is clean … not mid-task"* over uncommitted work. That is D8's acceptance test, inverted.
    Now asks git directly.
  - **Two counting conventions shipped side by side**, and the unscoped one was in the
    templates that mint every plan (`create_tasks`, `create_project`) plus `implement_inline`
    Step 3, both resume-logic `reference.md`s and `validate_execution`. On this plan the two
    read 116/133 vs 63/64 — `implement_inline` would report permanent false drift against
    counters `update_status` writes scoped. All twelve sites scoped; `validate_project` keeps
    the unscoped form deliberately, relabelled as the hazard it illustrates.
    **Fourth appearance of this class in one plan.**
  - The generated plan skeleton's four planning tasks carried **no IDs**, while its frontmatter
    claimed `total_tasks: 4`. Every new plan was born with phantom drift. IDs added.
  - `implement` **6c** — "revert or leave the work uncommitted as appropriate" breaks the
    clean-tree invariant `6a`/`6b` depend on: the next worker inherits the blocked task's
    changes, a worker that did nothing reads as truncation, and its verifier fails it for
    files it never opened. Now a WIP commit or a scoped `git restore`, ending clean either way.
  - `implement` **6c** — "leave its checkbox `[ ]`" was an assertion, not an instruction. The
    worker flips the box *before* verification, so the FAIL path arrives at `[x]`; nothing
    un-flipped it, and Step 8's phase gate would pass a failed task. Reset is now step 1 of
    6c — before escalating, so the escalation attempt keeps its truncation signal too.
  - `docs/claude-code-skills-guide.md` — `P4-T5`'s de-beading spliced new text over the old
    bullet and left a truncated sentence with an unclosed backtick
    (``see `hooks/wb-prime.skill activating``). Same block still said the plugin's `commands/`
    files "continue to work unchanged" (no such directory), that background skills "could"
    declare `user-invocable: false` (they do), and listed three **adopted** upgrades under
    "not yet applied". Rewritten.
  - `docs/commands-reference.md:24` — the headline pipeline diagram still ended
    `→ /implement_tasks →`, the deprecated alias, contradicting `CLAUDE.md` and `help`.
    `P4-T4`'s criterion grepped only `create_execution`; Phase 2's rename grep was scoped to
    `plugin/skills/`. Neither net covered `implement_tasks` in `docs/`.
  - `model-help:22` named `claude-fable-5`; the model is Fable 5.1, `claude-fable-5-1` — on the
    branch whose stated purpose is the Fable 5.1 re-baseline.
  - **70 bare `/create_*` references** prefixed to `/wb:`, 20 of them in
    `create_project/templates.md` and therefore written into every generated plan, where a user
    reads them and types them.
  - Measured, not fixed, because nothing is broken by it: **`allowed-tools` on a skill is a
    pre-approval, not a sandbox.** A skill declaring `allowed-tools: Read` performed a `Write`
    under `bypassPermissions`, and under the default mode the write went to the ordinary
    permission prompt rather than being refused. So `implement`'s `allowed-tools: Read` is
    harmless — but the skills guide was advising it as a least-privilege boundary. Corrected
    there.
  - **Still open, and the reason the above existed**: `journal.md` did not exist anywhere,
    including this plan's own directory, though `P3-T7`, `P3-T8` and `P4-T9` are all `[x]` and
    `P4-T9` claims to have recorded into it. D8 — the release's headline new capability — went
    the entire 64-task implementation unexercised, which is precisely why its two code paths
    shipped broken. Journal opened 2026-09-08 19:20, honestly dated. The three manual criteria
    it depends on (Phase 2's `--plugin-dir` read, Phase 3's abrupt-kill test, Phase 4's
    end-to-end run) remain `[ ]` and are the next thing to run.

- **2026-09-08, Phase 4's full sweep caught a fifth stale criterion.** Phase 1's
  `grep -c 'model:' plugin/agents/*.md → 1 per file` failed — correctly, and for a good reason:
  it was written when there were six agents, and `P2-T11` added `task-worker`, whose whole
  design is that it carries **no** pinned model (the coordinator picks the tier per spawn, which
  is D13). Amended in place.
  That is the fifth criterion in this plan written against a state that later work changed
  (`AGENTS.md` grep, two tier-rule rewordings, the Phase 2 beads scope, this). All five share a
  shape: **a criterion written against the tree as it was when the task was authored, rather
  than as it will be when the task runs.** Worth carrying into how criteria are written, not
  just into this plan's record.
- **2026-09-08, Phase 3 tasks complete.** `P3-T7` and most of `P3-T8` turned out to be **already
  done**: the journal protocol and the knowledge-file reads are content decisions (D8a/D8b/D8c)
  that appear in the *per-file* Phase 2 task specs, so they landed as each stage was reshaped.
  What remained was the knowledge file itself. Recorded because a future reader comparing task
  IDs to commits will otherwise think these were skipped.
  `.claude/wb/knowledge.md` seeded with **6 entries**, each carrying the date, the source plan,
  and a **Check it** command. What did *not* qualify is as informative as what did: the task-ID
  contract and the checkbox-counting rule were candidates, and both were rejected because they
  now live in the tree itself (`project-structure`, `create_tasks`) — an entry duplicating a
  shipped rule is the first step toward the two disagreeing.
- **2026-09-08, the conditional nudge (`P3-T11`) is worded against a measured false positive.**
  Upstream shipped this unconditionally and recorded 0/3. Ours fires only when the findings name
  **two or more viable approaches** *and* nothing in the research already decides between them —
  and says so explicitly, because "suggest optionally" without a test is how a nudge becomes
  noise, and noise trains the reader to skip it when it finally matters.
- **2026-09-08, the ID over-count had a second half, and it was the more dangerous one.** Fixing
  the eight counters made them agree on a pattern that **no document required**. A plan author
  numbering tasks `**Setup**` or `**API**` would have had every counter under-count silently.
  The shape is now stated where IDs are minted (`create_tasks`) and in the doctrine
  (`project-structure`), and checked by `validate_project` — which already verified uniqueness,
  so it was one more rule in an existing category. Decision in design.md → Resolved Decisions.
  Third appearance of this class in one plan (A2's note, `P3-T5`'s live over-count, this).
  **When several consumers agree on a format, something must state it and something must check
  it** — otherwise a shared convention decays into a shared bug.
- **2026-09-08, `wb-prime.sh` built (`P3-T1`–`P3-T5`) — and its own first run found a bug in the
  plan's most load-bearing convention.** The bootstrap counted 65 tasks against a frontmatter
  figure of 64; the extra match was `- [ ] **End-to-end**:`, a Phase 4 *criterion* that opens
  with a bold phrase. That is precisely A2's recorded failure mode, hit live. Standardized all
  eight files that count tasks (16 occurrences) on one pattern requiring **at least one digit**
  in the ID — `**End-to-end**` fails on the lowercase, `**API**` (the other shape a criteria
  list produces) fails on the digit, `**P3-T1**` passes. 64 of 64, zero false positives.
  Worth recording *why* it surfaced now rather than earlier: the hook is the first consumer that
  prints the count where a human reads it every session. The same latent error sat in five
  skills, silent, because nothing displayed it. **A number nobody looks at is not verified.**
- **2026-09-08, the content-loss check was done mechanically rather than by spot-read**, since
  that is the risk the Phase 2 checkpoint exists for and three samples cannot cover fourteen
  files. Method: extract every markdown heading from each pre-split command at `b635159`,
  extract the union of headings across its new skill directory, and diff — excluding fenced
  content, since bash comments inside code blocks are not headings (a first pass that did not
  exclude them reported 146 false positives, which is worth knowing before anyone re-runs this).
  Result: **no genuine loss.** Everything absent is a planned deletion, a rename, a restructure
  into a list, a move into a supporting file, or a comment inside a deleted block. The audit is
  reproducible and belongs in the Phase 4 sweep as well.
- **2026-09-08, Phase 2 tasks complete — all 30.** Final fourteen-stage metric:
  **84.9k → 45.3k = −46.6%**, against a bar of ≤59.4k. Thirteen stages reshaped (`help` is
  `P4-T2`), ranging from `create_mockup` **−70%** to `resume_handoff` **−25%**.
  **What separates the top from the bottom is not split quality — it is the ratio of template to
  judgment.** `create_mockup` is 389 lines of templates behind a 157-line skill, and
  section-scoped reads load one at a time. `resume_handoff` is nearly all judgment, and D8c
  *added* to it. A stage that is mostly output shapes wins big; a stage that is mostly reasoning
  barely moves, and no amount of splitting changes that.
- **2026-09-08, the remaining nine tasks in one pass** (`P2-T20`–`P2-T27`, `P2-T30`):
  `create_mockup` and `resolve_questions` reshaped; `mockup-iteration`'s four `bd create` sites
  became `UIQ`/`UIA` rows that **carry their IDs across versions** — a question raised in v001
  keeps `UIQ1` in v004, which is how you see how long it stayed open; `status-sync` rewritten
  from a `bd sync` reminder into the D5 drift indicator, with drift explicitly framed as
  **expected between checkpoints, not an error**; `project-structure` given the "No external
  tracker" doctrine plus D21's persistence rule; `daily-digest`'s beads source block replaced by
  a plan-document reader that treats an **OPEN journal entry as the highest-signal item in the
  digest**; `fetch-issues`' optional beads mirror deleted; the three beads docs removed; and
  `P2-T30` repointed 14 renamed-command references. `user-invocable: false` now on all five
  background skills.
- **2026-09-08, two things needed the migration-note exemption rather than a code change.**
  `P2-T30`'s sweep leaves three hits in `implement/reference.md`'s
  `## Migration from implement_tasks`, which *must* name the old names — that is what migration
  guidance is for. design.md's success criteria already grant exactly this exemption for beads
  ("outside the migration note"), and the same reading applies. Mangling migration text to
  satisfy a grep would defeat the text's only purpose.
  Separately, three inbound links to the now-deleted beads docs survive in
  `hooks/setup-beads-mode.sh` (`P3-T4`), `commands/forge.md` (`P4-T1`) and
  `docs/workbench-workflow-guide.md` (`P4-T3`) — each with a named owner, consistent with the
  scoped-criterion decision taken earlier today.
- **2026-09-08, handoff cluster complete** (`P2-T18`, `P2-T19`). Fourteen-stage total now
  **84.9k → 50.1k = −41.0%**, with only `create_mockup` and `help` untouched. `create_handoff`
  5.1k → 2.8k (−45%); `resume_handoff` 4.4k → 3.3k (−25%, the smallest win of the phase — D8c's
  reconciliation table and the knowledge-file read are *additions*, and they belong in
  `SKILL.md` by definition).
  **The substantive change is that resuming is now a reconciliation, not a restoration.** The
  old Step 3 reloaded tracker state and reclaimed a phase; there is no tracker, so it became
  something better — a table mapping *handoff claim × working-tree reality* to a reading, with
  the rule that **the repository is the authority and the handoff is a report**. The five rows
  are the cases that actually occur: agreement; a completion whose checkbox never flipped;
  in-progress beside uncommitted work (interrupted mid-task); in-progress beside a clean tree
  (never started, or reverted); and an open journal entry, whose "next action" is the most
  reliable thing a cold session has. Any disagreement is named in the confirmation, with which
  side was taken — silently picking one is how a resumed session builds on state nobody checked.
  `create_handoff` gained the D8b knowledge review as a real step with the qualification rule
  stated inline (a task outcome, a plan deviation, or a single-task fact does **not** qualify),
  and the D21 cross-machine trigger: a handoff crossing machines must `git add -f` its plan
  directory, or the receiving machine gets a document pointing at files it cannot see. That
  failure now has its own error message in `resume_handoff`.
- **2026-09-08, `P3-T9` is one-third done, ahead of its phase.** The handoff-over-compact
  guidance landed in `implement`'s Step 9 during the implementation cluster, because Step 9 is
  where that recommendation naturally belongs and writing the step without it would have meant
  reopening the file. Its other two homes — `create_handoff`'s "when to create" list and
  `help` — were **deliberately left**, since both are touched by later tasks anyway
  (`P4-T2` rewrites `help`) and pulling a Phase 3 task across a human checkpoint is different
  from resequencing within a phase. Recorded so `P3-T9` is not re-done in full.
- **2026-09-08, execution-path cluster complete** (`P2-T29`, `P2-T17`). All six skill
  directories now exist — three canonicals and three stub-only aliases — and 34 skills
  enumerate.
  `model-help` took the four changes PD2 and PD4 forced, plus one the plan did not ask for and
  should have: **the D3 boundary is now stated in the skill itself.** "Anything spawned is
  pinned at its definition; anything the session itself runs is advised here." Without that
  sentence, a reader of `model-help` has no way to tell why the worker ladder is absent from the
  one document that is supposed to be the model authority — it reads as an omission rather than
  a deliberate division, and the next person to notice would helpfully restate the ladder there
  and reintroduce exactly the drift D13 forbids.
  The 1M variants are in the roster with a note on *when* to reach for a wide window (holding a
  lot at once) versus when not to (a task that fits — the window costs per token and buys
  nothing), and `claude-opus-4-8[1m]` is named as the coordinated-worker default so roster and
  ladder cannot disagree about which model exists.
- **2026-09-08, the tier-rule criterion took two rewordings, and the second one is the lesson.**
  After `P2-T15` made the original grep unmatchable, I re-pointed it at `claude-opus-4-8[1m]` —
  and it **broke within the hour**, because `P2-T17` added the 1M variants to `model-help`'s
  roster and the ID appeared in two files. PD2's own consequence note had said precisely that
  would happen. A criterion keyed to a *value the plan already predicts will recur* was never
  going to hold. It is now keyed to a self-describing marker of the invariant — the sentence in
  `implement`'s Step 5 declaring itself the single statement — which survives model renames,
  roster additions and reformatting. **Check a proposed criterion against what the plan already
  says will change, before adopting it.**
- **2026-09-08, validation and status cluster complete** (`P2-T12`, `P2-T13`, `P2-T14`) — and
  **the headline metric is cleared with four stages still untouched.**
  **Fourteen-stage total: 84.9k → 53.5k = −37.0%**, against a bar of ≤59.4k. `create_handoff`,
  `resume_handoff`, `create_mockup` and `help` have not been reshaped yet; their −2/−3%
  readings are measurement noise, not progress. Landing at −37.0% against upstream's recorded
  −37.5% is close enough to be worth noting: the design's projection was sound, even though
  the *line-count* proxy it was originally written against overstated per-stage wins by roughly
  half.
  Per stage: `validate_project` **−69%** (5.8k → 1.8k), `update_status` **−60%** (5.3k → 2.1k),
  `validate_execution` **−45%** (5.3k → 2.9k).
- **2026-09-08, the sharpest inversion, and what it actually required.** `update_status` said
  "NEVER check markdown checkboxes" in three places and had to become the thing that counts
  them. The reversal is not a find-and-replace: the skill's *measurement step* had to be built,
  because it never had one — it read status from a tracker. Step 2 is now a count, and every
  downstream decision derives from it. The sole-writer rule (D5) is stated in the skill itself
  with its reasoning: a cache with several writers and no owner is how these fields rotted
  before, and one writer deriving from one source cannot disagree with itself.
  `validate_project` needed the same shift in a different direction. With no second system to
  cross-check against, "do two systems agree?" becomes **"can this document carry the role it
  claims?"** — are tasks checkboxes rather than prose, are the IDs unique, does the declared
  status contradict the boxes, is there stale guidance telling a reader status lives elsewhere.
  Counter drift is a **warning** there, never an error; it is expected between checkpoints.
- **2026-09-08, a criterion caught its own implementation.** `validate_project`'s stale-guidance
  detector originally listed the legacy strings verbatim so it could match them — which made
  Phase 2's own criterion (`grep -rln "NEVER treat markdown as source of truth\|…" plugin/`
  → no hits) fail on the detector itself. Rewritten to describe the predicate rather than
  enumerate the strings: flag any instruction asserting the checkboxes are documentation-only
  or that status is authoritative elsewhere. More robust anyway — the wording varies by vintage,
  and it is the claim that matters, not the phrasing.
- **2026-09-08, implementation cluster complete** — and it took **six** tasks in one pass, not
  four. `P2-T9`, `P2-T10`, `P2-T28` and `P2-T11` as scheduled, **plus `P2-T15` and `P2-T16`
  pulled forward** from the execution-path cluster. Reasoning: all four of `P2-T10`, `P2-T28`,
  `P2-T15` and `P2-T16` edit `plugin/skills/implement/SKILL.md`, and running them in document
  order means four passes over the file the plan calls its deepest-coupled. The split's stated
  reason is **tool-call budget for a delegated worker** (D15) — which does not bind an inline
  coordinator. Doing them separately would also have meant writing the *old* tier prose
  (`Opus: Everything else - DEFAULT`) and the *old* two-retry failure path, then deleting both
  two clusters later; `P2-T10` deletes `determineModel()` but `P2-T15` supplies its
  replacement, so the intermediate state is a file whose tier rule contradicts PD2.
  Results: `implement_tasks` → `implement_inline` **8.0k → 5.1k (−36.3%)**;
  `implement_coordinated` → `implement` **9.8k → 5.8k (−40.8%)**.
  **Running fourteen-stage tally: 48.8k → 27.8k = −43.0%.** The seven stages left need only
  −12.5% to clear the bar.
  One cost worth naming: `implement`'s **always-on** rose from ~40 to ~100 tokens, because PD4
  requires its description to carry the discrimination against `implement_inline` — `implement`
  is now the most generic trigger word in the menu, so the description has to do that work. A
  deliberate trade, and always-on is paid by every session.
- **2026-09-08, what replaced `bd close` as the worker's detectable final act.** D14 hangs
  truncation detection on the worker's *last* action being observable, which under beads was
  `bd close`. Tracker-free, the equivalent is **flipping the task's checkbox in `tasks.md`**,
  and it composes with D14's other half better than the original did: workers do not commit, so
  everything a worker touched sits in the working tree. Checkbox `[x]` + changes = finished;
  checkbox `[ ]` + substantial changes = truncated; checkbox `[ ]` + clean tree = genuine
  failure. Three states, one `git status`, opposite remedies. `agents/task-worker.md` states
  the rule and *why* — flipping early or committing destroys the only signal that separates a
  truncated task from a completed one.
- **2026-09-08, execution-planning cluster complete** (`P2-T6`, `P2-T7`, `P2-T8`). The phase's
  biggest single result: `create_execution` 787 lines → `create_tasks/SKILL.md` **175**, and
  **9.4k → 3.1k on-invoke (−67%)**. The reason it dwarfs the others is that most of the
  reduction is **deletion, not deferral** — roughly 200 lines of `bd create` / `bd dep add` /
  `bd dep` choreography and the whole `## Beads Issue Tracking` block left the tree instead of
  moving to a supporting file. That is D4 paying for D2, exactly as the design predicted.
  **Running tally across the five stages reshaped so far: 31.0k → 16.9k = −45.5%.** Against the
  full fourteen-stage bar (84.9k → ≤59.4k), the nine remaining stages now need only −21% to
  clear it, and every stage so far has beaten that.
  Two notes on what the alias costs: `create_execution` as a stub is **~320 on-invoke and ~30
  always-on**, so the three planned aliases will add roughly **1k on-invoke and ~90 always-on**
  to the tree. Worth stating because it is a real, permanent-until-3.0.0 surcharge that the
  headline metric does not capture — the bar covers the fourteen stages, and an alias is not
  one of them.
  `examples.md` diverges from upstream deliberately: theirs is entirely `bd create` /
  `bd dep add` worked examples, which D4 deletes. Ours covers the two judgment calls this skill
  actually makes and most easily gets wrong — projecting a task's tool-call cost and finding an
  honest seam to split it at, and deciding when a task needs an explicit `Depends on:` rather
  than relying on document order.
- **2026-09-08, design cluster complete** (`P2-T4`, `P2-T5`). Running fourteen-stage tally:
  **21.6k → 14.2k = −34.3%**, comfortably over the bar. Per stage: `create_project`
  **−50%** (4.0k → 2.0k) and `create_design` **−22.4%** (5.8k → 4.5k).
  **The spread is explained, and it is not split quality.** `create_project` is the phase's
  best result because its content is almost entirely template — 368 of its 553 lines — and the
  new section-scoped read means Step 4 pulls in one skeleton per file instead of five.
  `create_design` is the phase's worst because its content decisions are *additive*: D10's
  Mode A / Mode B branch, the D6 table rules, and the knowledge-file read together add ~55
  lines of judgment that must live in `SKILL.md` by definition. A stage can be split perfectly
  and still move little if the task asks it to grow. **Track the aggregate, not the stage** —
  the bar is on the fourteen-stage total, and three of four stages are carrying it.
  The lever noted here was **spent the same day**, not for the tokens but for the convention:
  `create_design`'s three message blocks moved to `templates.md` under named sections, and the
  rule now stands for the nine stages still to come — a multi-line block a skill emits verbatim
  is a template. `create_design` 4.5k → 4.1k (−29.3%); running tally **−36.1%**. See design.md
  → Resolved Decisions.
- **2026-09-08, `P2-T5`/`P3-T7` seam.** `P2-T5` adds `journal.md` to the generated plan
  directory (D8a), which means it needs a template *now* — a fifth file with no template would
  be a defect. So `templates.md` carries a `## journal.md Template` section with the open/closed
  entry shapes and the reasoning for opening entries at the start of work. **`P3-T7` still owns
  the protocol wiring** — opening and closing entries from `implement_tasks`,
  `implement_coordinated` and `create_handoff`, plus the PreCompact refresh of an open entry's
  mechanical fields. Noted because the plan assigns `create_project` to two tasks in different
  phases, which is the one place it knowingly breaks its own edit-once rule.
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
- **2026-09-08, status reconciled by `/wb:update_status`** at the Phase 3 checkpoint:
  `current_phase` 3 → 4, `completed_tasks` 43 → **54 of 64** (84%).
- **2026-09-08, status reconciled by `/wb:update_status`** at the Phase 2 checkpoint:
  `current_phase` 2 → 3, `completed_tasks` 13 → **43 of 64** (67%), `total_tasks` 63 → 64.
  The 30-task drift is the largest of the run and exactly what D5 predicts between checkpoints —
  the counters were last written at the Phase 1 gate, and every task since moved a checkbox
  instead. `status-sync`, rewritten today, is what would have surfaced it.
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
  so A4 and A5 were both marked Validated and the probe was then deleted. Had `P0-T5` run in
  document order, the plan would have had to rebuild the probe to answer its own checkpoint.
  **A5 holds and was re-confirmed by live testing 2026-09-09. A4 does not** — see the
  Implementation Discovery above; and note that deleting the probe is what made re-testing cost
  a rebuild, which is the second reason this conclusion went unchallenged for a day.
- **2026-09-08, four decisions taken via `/wb:resolve_questions`** after Phase 0's automated
  work: A4/A5 validated (**A4 since disproven, 2026-09-09**); `lint --all` scoped to exclude
  `.context/` (new task `P0-T6`);
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
