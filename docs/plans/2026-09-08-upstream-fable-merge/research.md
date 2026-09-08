---
project: upstream-fable-merge
ticket: N/A
created: 2026-09-08
status: complete
last_updated: 2026-09-08
git_commit: 500acc014782b99e117056ec338f5348ed9a1c54
git_branch: thescubageek/gabe-fable-merge-research
repository: thescubageek/workbench
researcher: wolfpacksteve@gmail.com
audience: maintainer
sources: "gvarela/workbench at upstream/main (19e98ee, v3.0.0), exported to .context/upstream/; thescubageek/workbench at b902566 (v1.12.5); merge-base cb693fb"
---

# Research: Upstream (gvarela/workbench) Divergence and the Fable 5.1 Re-baseline

**Created**: 2026-09-08
**Last Updated**: 2026-09-08
**Ticket**: N/A

## Research Question

Gabe (upstream, `gvarela/workbench`) has landed substantial work since our fork diverged —
he specifically named Fable optimization. What did he change, and how does each change map
onto the current architecture of `thescubageek/workbench`?

## Summary

Our repository is a GitHub fork of `gvarela/workbench` (confirmed via
`gh api repos/thescubageek/workbench` → `parent: gvarela/workbench`). The merge-base is
`cb693fb` (2026-04-28). Since then upstream has added 16 commits and reached **v3.0.0**;
we have added 24 commits and reached **v1.12.5**. The two trees have diverged
*structurally*, not just textually: upstream moved its entire shipped runtime under
`plugin/` and migrated every workflow command from `commands/*.md` monoliths to
`skills/<name>/SKILL.md` with progressive-disclosure supporting files, while we kept the
original root-level `commands/` + `skills/` layout and built a different feature set on top
of it (`forge`, `model-help`, `jira-context`, `daily-digest`, `fetch-issues`,
`resolve_questions`, `touch-grass`, `tracer-bullet`, `clip`/`eli5-clip`, `scripts/quiet`).

Only **12 of 64** our-side paths exist at the same path upstream (128 paths), and **11 of
those 12 have diverged**; the single byte-identical file is `.gitattributes`. **Zero**
shipped-runtime paths overlap, because upstream's runtime all lives under `plugin/`. No
upstream commit is git-cherry-pickable into our tree — every adoption is a manual port of
prose into a differently-shaped file.

On the Fable work specifically: upstream's `2026-09-01-fable-5-1-rebaseline` plan ran in two
phases. **Phase 1 was purely additive** and shipped as v2.4.0 — seven guardrail/routing
decisions (D1–D7) targeting documented Fable 5.1 failure modes, plus Fable routed into
exactly two places (escalation after a verified failure, and the `create_tasks`
decomposition stage). **Phase 2 was the evidence-gated trim** (v2.5.0) and mostly *did not
apply*: of the three deferred prompt-modernization trims, only R1 (the
`think deeply`/`ultrathink` directives) landed; R3 (barrier volume) and R4 (scope-block
volume) were **skipped on blind-trial evidence** that the trimmed wording performed
equal-or-worse. Our tree carries **none** of the Phase 1 guardrails (all seven absent) and
**none** of the R1 trim (25 `think deeply`/`ultrathink` sites remain, including the two bare
ones upstream deleted, plus the CLAUDE.md rule that regenerates them). Our barrier and
scope-block volume is already at parity with upstream's *kept* wording, so the two trims
upstream measured and rejected need no action here.

Dispositions (adopt / adapt / skip) are **not** in this document — they belong to
`/wb:create_design`.

---

## 1. Provenance and divergence topology

**Fork relationship** (verified, not inferred):

```
gh api repos/thescubageek/workbench --jq '{parent,source,fork}'
→ {"fork": true, "parent": "gvarela/workbench", "source": "gvarela/workbench"}
```

Upstream was added as a remote for this research: `git remote add upstream
https://github.com/gvarela/workbench.git`, and the tree exported to `.context/upstream/`
(gitignored, per Conductor convention).

| Fact | Value |
| ---- | ----- |
| Merge-base | `cb693fb` — "Make portable prompt a near-mirror of create_product_research command" (2026-04-28) |
| Upstream HEAD | `19e98ee` (2026-09-06), plugin version **3.0.0** |
| Our HEAD | `b902566` (v1.12.5) |
| Commits upstream-only since merge-base | 16 |
| Commits ours-only since merge-base | 24 |
| Aggregate diff, merge-base → upstream | 141 files changed, +15,241 / −6,731 |
| Authorship in our history | Gabe Varela 71 commits, Steve Craig 24 commits |

**Path overlap** (`git ls-tree -r --name-only` on both refs):

- ours: 64 tracked paths; upstream: 128 tracked paths; **common paths: 12**
- of those 12: `IDENTICAL` — `.gitattributes` only. `DIVERGED` — `.claude-plugin/marketplace.json`,
  `.claude/settings.json`, `.gitignore`, `.markdownlintrc`, `CLAUDE.md`, `README.md`,
  `docs/beads-integration-learnings.md`, `docs/claude-code-skills-guide.md`,
  `docs/commands-reference.md`, `docs/product-research-claude-desktop.md`,
  `docs/workbench-workflow-guide.md`
- **no** shipped runtime path is common: upstream's is `plugin/skills/…`, `plugin/agents/…`,
  `plugin/hooks/…`, `plugin/scripts/…`; ours is `commands/…`, `skills/…`, `agents/…`,
  `hooks/…`, `scripts/…`

`docs/claude-code-skills-guide.md` is the closest of the shared docs: 347 lines ours vs 348
upstream, 6 insertions / 5 deletions, identical heading set.

Config-file divergence: our `.markdownlintrc` sets `MD024: {siblings_only: true}` and
`MD060: false`; upstream sets `MD024: {allow_different_nesting: true}` and has no MD060
entry. Upstream's `.claude/settings.json` registers `bd prime` on SessionStart and
PreCompact; ours registers nothing (`{}`).

**Installed-plugin state on this machine**: `~/.claude/plugins/cache/wb/1.12.4` — the
marketplace cache is one patch behind the repo (1.12.5). Marketplaces present:
`thescubageek-workbench`, `claude-plugins-official`.

**`bd` is not installed in this workspace** (`which bd` → not found). Every claim in this
document about bd CLI semantics is sourced from upstream's own documents, **not** verified
against a live binary here.

---

## 2. What upstream shipped since the fork

Sixteen commits, five releases. From `.context/upstream/CHANGELOG.md` and the plan
directories under `.context/upstream/docs/plans/`.

| Version | Date | Contents |
| ------- | ---- | -------- |
| **2.0.0** | 2026-07-31 | The modernization release. Runtime relocated under `plugin/`; all 14 workflow commands migrated `commands/*.md` → `skills/<name>/SKILL.md`; skill cores restructured for context economy (8,439 → ~5,275 lines loaded at invocation, −37.5%); `task-worker` agent introduced; agents given explicit `model:` + `maxTurns`; `bd list -n 0` at 8 truncating sites; atomic `bd update --claim` at 14 sites; `allowed-tools: Read` on workflow skills; `hooks/beads-drift-check.sh` (SessionEnd); `plugin/docs/reference/` shared runtime docs. Requires beads ≥ 1.0.2. |
| **2.1.0** | 2026-07-31 | `explore_design` — optional facilitated architecture-discussion stage between research and design; produces a `thoughts/` exploration record plus a closed `Decide:` beads issue that `create_design` consumes. |
| **2.2.0 / 2.2.1** | 2026-07-31 / 08-21 | `create_execution` → `create_tasks` rename (with deprecated alias stub); worker tiers recalibrated (sonnet default at `effort: xhigh`, haiku mechanical-only, opus architectural); Plan-Defect Deviation Protocol separating plan defects from implementation defects; subagent tool-call-truncation handling. |
| **2.3.0** | 2026-08-26 | Compaction/drift hardening: `hooks/compact-recovery.sh`; `doc-adherence` background skill; progress frontmatter consolidated to a single writer (`update_status`); handoff-over-compact guidance. |
| **2.4.0** | 2026-09-05 | **Fable 5.1 re-baseline Phase 1** (additive). See §3. |
| **2.5.0** | 2026-09-05 | **Fable 5.1 re-baseline Phase 2** (evidence-gated trims). See §3. |
| **2.6.0** | 2026-09-05 | `disable-model-invocation` removed from all workflow skills; descriptions rewritten as trigger text so the model can fire any stage from prose. |
| **3.0.0** | 2026-09-06 | "Tools as intended": `implement_coordinated` → `implement`, `implement_tasks` → `implement_inline`, `create_execution` alias removed; plan **Intent** section with per-stage obligations; stateful `/wb:help` + human-input map; `BEADS_MODE` and `setup-beads-mode.sh` removed; commit-`.beads/` guidance removed everywhere; `wb-prime.sh` orientation/recovery hook; session-start beads sanity check; `docs/beads-guide.md` contract inventory; lint exit-code fix; requires bd ≥ 1.1.0. |

---

## 3. The Fable 5.1 re-baseline, as upstream ran it

Source: `.context/upstream/docs/plans/2026-09-01-fable-5-1-rebaseline/` —
`research.md` (186 lines), `design.md` (184), `tasks.md` (610),
`thoughts/2026-09-01-effort-curves-and-fable-routing.md` (37),
`trials/2026-09-05-blind-trials.md` (47).

### 3.1 The premise upstream recorded

`design.md` Problem Statement: the plugin's model strategy was calibrated against the
Claude 4 generation and re-tuned once in July for Sonnet 5. Fable 5.1 both raises the
ceiling on long-horizon multi-file coding *and* introduces named failure modes the skills
did not guard against, while the vendor simultaneously states that prompts written for
prior models are often too prescriptive for it. `design.md`:

> The premise does not change: consistent execution at controlled cost. Fable goes only
> where a failure is expensive to detect or retry; cheaper models stay where a failure is
> cheap to detect.

`thoughts/2026-09-01-effort-curves-and-fable-routing.md` records the reasoning behind the
routing: the wb workflow deliberately decomposes work into small beads tasks, "which
manufactures the regime where Sonnet saturates," so Fable earns its place only where
decomposition has failed or has not happened yet — escalation after a verified failure, the
`create_tasks` decomposition stage, and `implement_inline` on cross-cutting phases. It also
records that research stays on Sonnet because "Fable at low answers from memory instead of
reading, which cuts against the file-reading protocol."

The same thoughts doc corrects an instinct with system-card data: Sonnet 5 is **monotonic
through `max`** on FrontierCode, CursorBench, and HLE, unlike Sonnet 4.6 (declines at max on
all three) and Opus 4.8 (declines at max on FrontierCode). The two observed "deteriorations"
at `xhigh` are harness effects (Terminus-2 tmux timeouts; a USAMO run capped at `high` by a
300k token limit), not quality.

### 3.2 Phase 1 (v2.4.0) — additive, ten decisions

| ID | Decision | Where it landed upstream |
| -- | -------- | ------------------------ |
| D1 | On a verified FAIL, the **first** fix worker spawns `fable` at `effort: high` (opus fallback); if re-verification fails, the task goes to the phase checkpoint's blocking list — **no second retry** | `plugin/skills/implement/sub-agent-prompts.md:112-128` |
| D2 | `create_tasks` gets `explore_design`'s **Model Self-Check** (Fable recommended, Opus the comfortable minimum, warns below Opus, never blocks) — not a frontmatter pin | `plugin/skills/create_tasks/SKILL.md:26-41` |
| D3 | Fable spawns run at `effort: high`, never `xhigh` (at xhigh on long deliverables 5.1 drafts in thinking then writes again, ≈2× output) | `.context/upstream/CLAUDE.md:167`; `plugin/skills/implement/SKILL.md:198-204` |
| D4 | Surgical-edit sentence + follow-ups-not-fixes sentence, ending with a completeness clause | `plugin/agents/task-worker.md:30-31`; `plugin/skills/implement_inline/SKILL.md:62-66` |
| D5 | Memory surface: `bd remember --key <slug> "<fact>"` at phase completion, with a qualification rule; `create_handoff` reviews the session's entries | `plugin/skills/implement_inline/SKILL.md:406-412`; `plugin/skills/implement/SKILL.md:381-387`; `plugin/skills/create_handoff/SKILL.md:111` |
| D6 | Autonomy paragraph in worker + coordinator task loop, explicitly excluding phase checkpoints and plan-defect halts | `plugin/agents/task-worker.md:25`; `plugin/skills/implement/SKILL.md:191` |
| D7 | `why:` field — the phase goal and who it serves — leads the worker context package and renders first in the prompt | `plugin/skills/implement/reference.md:9-12`; `sub-agent-prompts.md:16-18` |
| D9 | CLAUDE.md "Working with Commands" rewritten *before* any trim lands ("the list is the root that regenerates the patterns") | `.context/upstream/CLAUDE.md` "Working with Commands" |
| D10 | Model map documented: guide rows for `create_tasks` (Fable, Opus fallback), `implement_inline` (Fable for cross-cutting phases), escalation workers (Fable at high) | `.context/upstream/docs/workbench-workflow-guide.md:62-75` |

Upstream's own rationale for adding rather than trimming, quoted from `design.md` D4:
"whole-file rewrites and adjacent fixes are documented 5.1 failures with published one-line
fixes; the scope rules are prohibitions against a current failure and are on the keep list.
The completeness clause guards the one regression risk, under-delivery."

### 3.3 Phase 2 (v2.5.0) — what the blind trials actually returned

Method (`trials/2026-09-05-blind-trials.md`): fresh-context **Sonnet** subagents, no tools,
given only the verbatim instruction block plus a synthesized fixture; 3 fixtures
(clear-positive, clear-negative, trap) × 3 trials × 2 wordings. Pass bar: trimmed ≥ baseline
on every fixture **and** trap 3/3.

**Set A — barrier volume (R3)**: baseline `⛔⛔⛔ BARRIER 2: STOP! Wait for ALL sub-agents…⛔⛔⛔`
vs trimmed `⛔ BARRIER 2: every spawned agent has returned — synthesis on a partial set
produces conclusions the missing report would have changed.`

| fixture | baseline | trimmed |
| ------- | -------- | ------- |
| positive (3/3 returned) | SYNTHESIZE 3/3 | SYNTHESIZE 3/3 |
| negative (1/3 returned) | WAIT 3/3 | WAIT 3/3 |
| trap (2/3 + streaming partial) | WAIT **0/3** | WAIT **1/3** |

Verdict recorded: trap 3/3 fails for *both* wordings. **R3 not applied.** Upstream's note:
"Volume is not what holds the barrier; no barrier text changed."

**Set B — scope-block volume (R4)**: baseline `### CRITICAL: NO SCOPE ADDITIONS - NONE` with
`NEVER` bullets vs trimmed `### Scope` with `Do not` bullets, same content.

| fixture | baseline | trimmed |
| ------- | -------- | ------- |
| positive (clean file) | flag only 3/3 | flag only 3/3 |
| negative (bug in another file) | untouched 3/3 | untouched 3/3 |
| trap (`ITEMS[1:]` in the edited function) | kept 3/3, surfaced 3/3 | kept 3/3, surfaced **2/3** |

Verdict recorded: trimmed < baseline on the trap's reporting half. **R4 scope half not
applied.** Both wordings left the bug in place; "reported" was weak in every run.

**R1 was the only trim applied**: the 21 `think deeply`/`ultrathink` directives became the
directive they introduced (`Decide…`, `Document…`, `Identify…`, `Work out…`), and the two
*bare* ones (in `create_project` and `update_status`) were deleted. Recorded rationale:
"Thinking depth is the session's effort setting, not prompt text."

Verified in the upstream tree today — the converted forms:

- `plugin/skills/create_research/SKILL.md:75` — `**Document what EXISTS in the codebase**`
- `plugin/skills/create_research/SKILL.md:143` — `**Document ONLY what EXISTS**`
- `plugin/skills/create_design/SKILL.md:110` — `**Decide WHAT to build, not HOW to build it**`
- `plugin/skills/create_tasks/SKILL.md:100` — `**Decide HOW to bridge from current state to target state**`
- `plugin/skills/create_tasks/SKILL.md:119` — `**Decide the safest, most logical implementation sequence**`
- `plugin/skills/validate_execution/SKILL.md:129` — `**Identify the gaps between plan and reality**`
- `plugin/skills/create_product_research/SKILL.md:171` — `**Document ONLY what EXISTS, in product language**`
- `plugin/skills/create_handoff/SKILL.md:95` — `**Identify what context would be lost if starting fresh**`
- `plugin/skills/implement/SKILL.md:112` — `**Work out:**` (the colon-list head form)
- `plugin/skills/explore_design/SKILL.md:140` — `**Identify what is actually being decided**` (net-new skill, no counterpart in ours)

And upstream's `create_research/SKILL.md:73-80` shows the `ultrathink about:` list head
became `**Work out:**`, with `**REMEMBER: Document what IS, not what SHOULD BE**` inserted.

The two **bare** directives were deleted outright rather than converted — verified by
reading the surrounding text upstream: `plugin/skills/create_project/SKILL.md:73-75` runs
`### Step 2: Gather Metadata` → blank line → `Collect system metadata for proper tracking:`,
and `plugin/skills/update_status/SKILL.md:108-110` runs `### Step 2: Analyze Actual
Progress` → blank line → `Examine the files to determine actual state:`. Ours still carries
the standalone `**think deeply**` line in exactly those two positions
(`commands/create_project.md:50`, `commands/update_status.md:86`).

Upstream's whole tree now contains exactly **one** occurrence of the phrase, and it is a
stale doc comment: `plugin/scripts/README.md:59` — "Emphasis as heading allowed (for 'think
deeply' directives)".

### 3.4 Out of scope upstream (recorded, not decided)

From `design.md` "Out of Scope" and "Pending Decisions":

- Changing the Sonnet worker default or its `xhigh` effort — "requires a worker-shaped eval
  that does not exist"
- Judgment-level de-prescription (rewriting numbered choreography as goals and constraints)
  on the Fable stages — pending, to be decided on Phase 2 evidence
- Whether the Sonnet worker default moves to `high` with `xhigh` reserved for
  coordinator-flagged hard tasks — pending
- The `wb-eval-harness` project (still at research-needed with no design)

The `thoughts/` doc also records an unexploited observation: on the system-card figures,
**Fable 5 at `low` scores above Sonnet 5 at `xhigh` on both coding benchmarks at roughly the
same cost per task**, and Fable 5.1's 0.025× cache-read rate pushes further in that
direction in long loops. Upstream deliberately kept this out of scope because no published
benchmark uses a TDD-constrained single-task harness like `task-worker`.

---

## 4. Model-and-effort architecture: ours vs upstream

This is the largest architectural difference in the Fable dimension, and it runs in **both**
directions.

### 4.1 What exists in ours

We have a mechanism upstream has no counterpart for: `skills/model-help/SKILL.md` (119
lines), declared in `CLAUDE.md:174-179` as "the plugin's single authority on which Claude
model + reasoning-effort to run at," consulted in **gate mode** by `forge`,
`resume_handoff`, and the `create_*` / `implement_tasks` / `validate_execution` commands
"rather than re-deriving the rubric."

Its contents:

- **Roster** (`skills/model-help/SKILL.md:22`): `claude-opus-5` · `claude-opus-4-8` ·
  `claude-sonnet-5` · `claude-haiku-4-5-20251001`, with — quoted — "`claude-fable-5` (Fable
  5) also exists (fast Claude-5 tier); default to the four above unless the user prefers
  Fable." Effort levels `low · medium · high · xhigh · max`.
- **Two-Opus-tier rule** (`:24`): "Opus 5 is the ceiling… **Opus 4.8 is the default Opus**…
  Downshift 5 → 4.8 whenever 5 would be overkill." No equivalent concept exists upstream —
  every upstream `opus` reference is one flat tier.
- **Task-shape → tier table** (`:38-43`).
- **Per-phase gate baselines** (`:60-66`): `create_research` Sonnet 5/medium; `create_design`
  **Opus 4.8/high** (→ Opus 5/high–max for novel / one-way-door / compliance-critical);
  `create_execution` Sonnet 5/medium; `implement_tasks` Sonnet 5/medium; `validate_execution`
  Sonnet 5/medium → Opus 4.8/high.
- **The two-levers economics** (`:55-56`): "Sub-agent model + effort is **free** — each
  spawned agent is fresh context… **Main-session model/effort costs a context reload** on
  every switch."
- **The switch-cost rule** (`:70-81`): advise a switch only when the tier delta is ≥1 step
  *and* the phase is substantial; cluster same-tier phases; "the floor is inviolable."
- **A one-line gate output template** (`:83-92`), silent when no switch is warranted.

Also ours-only: `skills/daily-digest/SKILL.md:147-152` carries a second, independent
complexity→(model, effort, parallelism) rubric, which `CLAUDE.md:176` names as a thing to
keep consistent with `model-help`.

Where our model choices are actually *pinned*: per-spawn `model:` hints on `Task(…)` calls
inside command bodies — 18 sites across `create_design.md`, `create_execution.md`,
`create_mockup.md`, `create_research.md`, `create_product_research.md`,
`validate_execution.md`. **None** of our six `agents/*.md` files and **none** of our
`skills/*/SKILL.md` files carry `model:`, `effort:`, or `maxTurns:` frontmatter.
`docs/workbench-workflow-guide.md` contains **zero** occurrences of
`model|effort|opus|sonnet|haiku|fable` across all 895 lines.

Our worker tiering lives entirely inside `commands/implement_coordinated.md` and is *not*
delegated to `model-help` (`model-help` only notes in passing at `:65` that
"`implement_coordinated` already picks per-task worker models"):

- prose tier rule, `commands/implement_coordinated.md:264-267`: "Haiku: Simple tasks…
  Sonnet: Standard implementation… **Opus: Everything else (bugs, refactoring,
  architecture) - DEFAULT**"
- a `determineModel(taskDetails)` **keyword-regex function**,
  `commands/implement_coordinated.md:672-710`, returning `'haiku'` on config/docs/rename/
  version/typo patterns, `'sonnet'` on implement/add/create-test/wire-up/update-existing
  patterns, and `'opus'` as the fallthrough ("conservative, better at complex tasks")
- fix-worker escalation, `commands/implement_coordinated.md:435-456`: "Spawn a fix worker
  using the general-purpose agent with **opus** model", **up to 2 retries**, then add to the
  phase checkpoint's blocking list

### 4.2 What exists upstream

Upstream distributes the same information across five loci instead of one:
`CLAUDE.md:163-170` (tier legend), `docs/workbench-workflow-guide.md:62-75` (per-stage
table), agent frontmatter, two skill-level frontmatter pins, and the `implement` skill's own
coordinator-judgment section.

- **Tier legend** (`.context/upstream/CLAUDE.md:163-169`), quoted: "`haiku`: File searches,
  pattern matching, mechanical tasks. **No `effort` support — never annotate haiku agents or
  spawns**… `sonnet`: Default for analysis AND implementation… `opus`: Design and
  architectural or cross-cutting implementation… `fable`: Architecture-critical discussion
  (explore_design), decomposition (create_tasks), and escalation after verified failure.
  **Fable spawns use `effort: high`, never `xhigh`**."
- **Agent frontmatter pins**: `codebase-analyzer` sonnet/medium; `codebase-locator`
  haiku + `maxTurns: 25`; `pattern-finder` haiku + `maxTurns: 25`;
  `product-behavior-analyzer` sonnet/medium; `research-validator` sonnet/high;
  `task-verifier` sonnet/high; `task-worker` no model (per-spawn override) +
  `skills: [tdd-discipline]` + `maxTurns: 60`.
- **Skill frontmatter pins**: `validate_execution/SKILL.md:1-7` sonnet/high;
  `research-validation/SKILL.md:9-10` sonnet/high; `explore_design/SKILL.md` `effort: high`
  with no model pin.
- **Coordinator judgment**, `plugin/skills/implement/SKILL.md:198-204`: "Sonnet: Standard
  implementation including bugs and refactors - **DEFAULT when unsure**… Fable: **never as a
  first spawn** — the escalation target after a verified failure." Upstream's
  `implement/reference.md:57-59` records that the `determineModel()` keyword-regex spec "was
  retired in favor of coordinator judgment (2026-06, prompts-0my)."
- **A tool-call budget rule**, `plugin/skills/implement/SKILL.md:197`: a task projecting past
  ~50 calls splits at its natural seam before spawning.

### 4.3 The mapping

| Upstream mechanism | State in ours |
| ------------------ | ------------- |
| Per-stage session-model table | **Divergent location** — ours is `model-help:60-66`, upstream's is the workflow guide; ours names *different tiers* (see below) |
| Tier legend naming Fable's three roles | **Divergent** — our `CLAUDE.md` delegates to `model-help`, which lists Fable as an available-but-non-default option |
| Per-`Task()` `model:` hints | **Present, identical mechanism** (18 sites) |
| Agent frontmatter `model:`/`effort:`/`maxTurns:` | **Absent** — all six of our agents carry only `name`/`description`/`tools` |
| Skill frontmatter `model:`/`effort:` pins | **Absent** |
| In-skill runtime Model Self-Check (warns if session is below a floor) | **Divergent** — ours is the outward-facing `model-help` gate consultation at command entry (`commands/implement_tasks.md:12`, `commands/resume_handoff.md:199-214`, `commands/forge.md:61-68,116`); upstream duplicates a self-inspecting block per skill |
| Fable as escalation target, one attempt | **Absent** — ours escalates to **opus**, **2 retries** (`commands/implement_coordinated.md:435-456`) |
| `effort: high` for Fable / never annotate haiku | **Absent** |
| Coordinator-judgment worker tiering (regex retired) | **Divergent** — we still ship the regex (`:672-710`) upstream retired, *and* our fallthrough default is **opus** where upstream's is **sonnet** |
| Tool-call budget / ~50-call split rule | **Absent** |
| `maxTurns` caps | **Absent** |
| Centralized advisory skill with switch-cost economics | **Ours-only** — upstream has no counterpart |

**Same stage, different tier** — the substantive disagreements:

| Stage | Ours | Upstream |
| ----- | ---- | -------- |
| Decomposition (`create_execution` / `create_tasks`) | Sonnet 5 / medium — "structuring, not deciding" (`model-help:64`) | **Fable at high**, Opus the comfortable minimum — "decomposition quality sets the ceiling for cheap workers" (`create_tasks/SKILL.md:28`) |
| Coordinated worker default when unsure | **opus** (`implement_coordinated.md:267,709`) | **sonnet** at `effort: xhigh` (`implement/SKILL.md:200`) |
| Fix worker after verified FAIL | opus, 2 retries | **fable at `effort: high`** (opus fallback), 1 retry then checkpoint |
| `create_mockup` research agents | haiku, no effort (5 sites) | sonnet at `effort: low` (5 sites) |
| Fable's role overall | optional, non-default | load-bearing default for two stages plus escalation |
| Opus tiering | two tiers (Opus 5 ceiling / Opus 4.8 default) | one flat `opus` |

---

## 5. Implementation-context guardrails (Fable Phase 1, D4–D7)

All seven Phase 1 guardrail items are **absent** from our tree. Verified by grep across
`agents/`, `commands/`, `skills/`, `docs/`.

| Item | Upstream text (verbatim, abridged) | State in ours |
| ---- | ---------------------------------- | ------------- |
| **Surgical edits** | "when it will not affect the end result, edit a file in place rather than rewriting it — fewer tokens, same outcome" (`task-worker.md:31`; `implement_inline/SKILL.md:66`) | **Absent.** Only hit for "surgical" is `agents/codebase-analyzer.md:109` ("surgical precision", about citation style) |
| **Follow-ups, not fixes** + completeness clause | "if you find a pre-existing bug… don't fix, optimize, or extend it unless the requested behavior cannot work without it — report it under 'issues encountered'… This is about extras only: implement every behavior the task asks for, completely." (`task-worker.md:30`) | **Absent.** We have the inverse (don't *add*) but no discovery-triage rule and no completeness counter-clause |
| **`### Extras and edits` section** | sits immediately after the scope NEVER-list (`implement_inline/SKILL.md:62-66`) | **Absent.** In `commands/implement_tasks.md` the scope block (`:50-58`) is followed directly by `### TDD Implementation Flow` (`:60`) |
| **Memory surface** | `bd remember --key <project>-<slug> "<fact>"` at phase completion + qualification rule + `bd memories`/`bd forget` review in `create_handoff` (`implement_inline/SKILL.md:406-412`; `implement/SKILL.md:381-387`; `create_handoff/SKILL.md:111`) | **Absent.** `grep -rn "bd remember\|bd memories\|bd forget"` → **0 hits**. Durable learnings live only in per-plan `## Implementation Notes` (`commands/implement_tasks.md:490-495`) and the handoff doc itself (`commands/create_handoff.md:100-104`) |
| **Autonomy paragraph** | "You are operating autonomously within this task. Nobody is watching in real time… Before ending your turn, check your last paragraph: if it is a plan, a question, or a promise about work not yet done ('I'll now run…'), do that work now with tool calls… This does not apply to phase checkpoints or plan-defect halts — those stop for a human by design." (`task-worker.md:25`; coordinator variant `implement/SKILL.md:191`) | **Absent** at both worker and coordinator level |
| **`why:` field** | `why: "<one or two sentences from design.md: what this phase delivers and who it serves>"` leads the context package (`implement/reference.md:9-12`) and renders first under `## Context You Need` (`sub-agent-prompts.md:16-18`) | **Divergent.** Our nearest is `design.phaseGoal` (`commands/implement_coordinated.md:205`) — buried third inside `design`, no "who it serves", rendered mid-prompt under `### Design Context` (`:310`) |
| **`task-worker` agent file** | `plugin/agents/task-worker.md` (40 lines): `tools`, `skills: [tdd-discipline]`, `maxTurns: 60`, Contract / Process / Operating Mode / Constraints / Expected Output; spawned by name at `implement/SKILL.md:205`; "DO NOT COMMIT — the coordinator commits after verification" | **Absent.** `ls agents/` → 6 files, no `task-worker.md`; `grep -ril task-worker` → 0 hits. We spawn the generic **general-purpose** agent (`commands/implement_coordinated.md:271`) with the worker contract inlined as a prompt template (`:294-379`), so it cannot declare its own tool list, preloaded skill, or turn cap |

Our existing guardrail surface, for context — this is the substrate the above would attach
to, and it is on a *different axis* (prohibit additions) than upstream's Phase 1 batch
(triage discoveries, autonomy, context completeness):

- scope NEVER-lists: `commands/implement_tasks.md:50-58`, `:672-687`;
  `commands/implement_coordinated.md:68-77`, `:355-361`, `:827-835`
- scope verification: `agents/task-verifier.md:17-22`, `:141-145`
- `skills/tdd-discipline/SKILL.md:15` Iron Law; `skills/verification-before-completion/SKILL.md:15`
  Iron Law

Two of our background skills carry content upstream's do **not**: fail-fast in the RED/GREEN
inner loop (`skills/tdd-discipline/SKILL.md:38`) and the `scripts/quiet` backpressure wrapper
for green runs (`skills/tdd-discipline/SKILL.md:50`,
`skills/verification-before-completion/SKILL.md:72-88`). `scripts/quiet` and
`scripts/test-quiet` exist only in our tree.

Commit discipline also diverges. Upstream 3.0.0: workers **never** commit; the coordinator
commits each task after its verifier passes; `task-verifier` checks scope against the
**working tree** (`git status --short`). Ours: `agents/task-verifier.md` diffs against a
caller-supplied **Base Ref** (`git diff --name-only "$BASE_REF"`) because a worker may commit
several times per task.

---

## 6. Prompt-scaffolding inventory (R1 / R3 / R4 state on both sides)

Counts by `grep -ro` over `agents commands skills CLAUDE.md AGENTS.md` (ours) and
`.context/upstream/plugin .context/upstream/CLAUDE.md` (upstream):

| Signal | OURS | UPSTREAM |
| ------ | ---- | -------- |
| `⛔` (all) | 178 | 184 |
| `⛔⛔⛔` (triple) | 44 | 40 |
| `STOP!` | 22 | 20 |
| `CRITICAL` | 22 | 36 |
| `MUST` | 21 | 16 |
| `NEVER` | 44 | 40 |
| `ALWAYS` | 13 | 12 |
| **`think deeply`** | **21** | **1** (a stale doc comment) |
| **`ultrathink`** | **4** | **0** |
| `NOW and follow it exactly` | 0 | 12 |
| `Wait for ALL` | 8 | 10 |

Reading of the table:

- **R3 and R4 are at parity.** Upstream *kept* the triple-⛔ barriers and the CAPS scope
  blocks after the trials failed the pass bar. Confirmed verbatim upstream today:
  `plugin/skills/create_research/SKILL.md:139` — `**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL
  sub-agents to complete - DO NOT proceed until EVERY agent returns ⛔⛔⛔**` (byte-identical
  to our `commands/create_research.md:210`), and
  `plugin/skills/implement_inline/SKILL.md` still opens its scope block with
  `### CRITICAL: NO SCOPE ADDITIONS - NONE` + `NEVER` bullets — identical in content to our
  `commands/implement_tasks.md:50-58`.
- **R1 is the one real gap.** We carry 25 sites; upstream carries 0 live ones.
- `NOW and follow it exactly` (12 upstream, 0 ours) is an artifact of upstream's
  progressive-disclosure and alias mechanisms — the phrase is how a SKILL.md instructs a
  read of a supporting file or how an alias stub forwards to its canonical skill. It is not a
  scaffolding-volume difference.
- Upstream's higher `CRITICAL` count (36 vs 22) partly reflects the documentarian header
  it kept and we softened (below).

**Our 25 `think deeply` / `ultrathink` sites**, with the two **bare** ones (no object) marked
— note they are in exactly the two files upstream deleted its bare pair from:

| Site | Text |
| ---- | ---- |
| `commands/create_project.md:50` | `**think deeply**` — **BARE** |
| `commands/update_status.md:86` | `**think deeply**` — **BARE** |
| `commands/create_research.md:80` | `**think deeply about what EXISTS in the codebase**` |
| `commands/create_research.md:83` | `2. **Take time to ultrathink about:**` |
| `commands/create_research.md:214` | `**think deeply about documenting ONLY what EXISTS**` |
| `commands/create_design.md:91` | `**think deeply about WHAT to build, not HOW to build it**` |
| `commands/create_design.md:165` | `**think deeply about the actual problem, not the implementation**` |
| `commands/create_design.md:188` | `**think deeply about the single load-bearing uncertainty**` |
| `commands/create_execution.md:69` | `**think deeply about HOW to bridge from current state to target state**` |
| `commands/create_execution.md:154` | `**think deeply about the safest, most logical implementation sequence**` |
| `commands/create_execution.md:175` | `**think deeply about the single load-bearing unknown**` |
| `commands/implement_tasks.md:117` | `**think deeply about implementing ONLY what's specified**` |
| `commands/implement_coordinated.md:117` | `**think deeply about:**` |
| `commands/validate_execution.md:89` | `**think deeply about what was supposed to be built vs what exists**` |
| `commands/validate_execution.md:196` | `**think deeply about gaps between plan and reality**` |
| `commands/validate_project.md:137` | `**think deeply about what you're seeing**` |
| `commands/create_product_research.md:81` | `**ultrathink about what the SOFTWARE DOES from the user's perspective**` |
| `commands/create_product_research.md:90` | `2. **ultrathink about:**` |
| `commands/create_product_research.md:216` | `**ultrathink about documenting ONLY what EXISTS, in product language**` |
| `commands/create_mockup.md:174` | `**think deeply about what information is needed**` |
| `commands/create_handoff.md:89` | `**think deeply about what context would be lost if starting fresh**` |
| `commands/resume_handoff.md:87` | `**think deeply about the context and discoveries documented**` |
| `skills/daily-digest/SKILL.md:135` | `**think deeply about leverage and cost.**` |
| `skills/fetch-issues/SKILL.md:135` | `**think deeply about leverage.**` |
| `CLAUDE.md:191` | `3. Use "think deeply" directives at critical decision points` — **the rule that regenerates them** |

Direct upstream counterparts exist for nine of these (see §3.3). Our
`commands/create_execution.md:175` and `commands/create_design.md:188` ("the single
load-bearing unknown/uncertainty") have **no** upstream counterpart — they are our
`tracer-bullet` integration, not inherited text.

One further site sits outside the grep scope above: `docs/product-research-claude-desktop.md:89`
— `3. **Think deeply about:**` — because that file is a portable Claude-Desktop **mirror** of
`commands/create_product_research.md` and therefore carries a copy of the same scaffolding
(it also holds 4 additional triple-⛔ barriers and 8 `⛔` total). Any R1-style change has a
26th site there, and the mirror is the reason our `docs/` tree reports scaffolding counts of
its own.

**The CLAUDE.md root.** Upstream's D9 rewrote the list *before* trimming, on the reasoning
that "the list is the root that regenerates the patterns; trimming skills without changing it
guarantees regression on the next skill written." The two lists side by side:

Ours, `CLAUDE.md:189-195`:

```
1. Follow existing command patterns
2. Include all three barriers and checkpoints
3. Use "think deeply" directives at critical decision points
4. Maintain the documentarian philosophy for research
5. Separate automated from manual verification
6. Always read files FULLY before processing
7. Use parallel agents for efficiency but wait for ALL to complete
```

Upstream's, `.context/upstream/CLAUDE.md` "Working with Commands":

```
1. Follow existing command patterns
2. Mark each real synchronization point once (⛔ BARRIER for "do not proceed until X",
   ⛔ CHECKPOINT for human confirmation) and state the reason in a plain sentence
3. At decision points, say what the decision is about; do not instruct the model how hard
   to think
4. Maintain the documentarian philosophy for research
5. Separate automated from manual verification
6. Read files fully before processing
7. Spawn independent agents in parallel; synthesize only after all have returned
```

Upstream's `Command Structure Patterns` block also changed from three bare markers to one
marker per point **with its reason stated**:

```
⛔ BARRIER 1: full context read — analysis on partial context produces placeholders
⛔ BARRIER 2: every spawned agent has returned — synthesis on a partial set misses what
   the missing report would have changed
⛔ BARRIER 3: no placeholder values — a placeholder that ships becomes a task nobody can
   execute
⛔ CHECKPOINT: human verification between phases — the next phase builds on what a human
   has accepted
```

Ours, `CLAUDE.md:161-166`, still carries the reasonless triple-marker example.

**Documentarian rule placements.** Upstream extracted the rationale into a shipped shared
doc, `plugin/docs/reference/documentarian-philosophy.md` (32 lines: "Shared reference for the
wb research skills… and every agent they spawn"), and links to it from both research skills
(`create_research/SKILL.md:26`, `create_product_research/SKILL.md:28`) while keeping the CAPS
header `## CRITICAL: YOUR ONLY JOB IS TO DOCUMENT THE CODEBASE AS IT EXISTS` at `:17` in
each. We have **no shared reference doc**; instead we already softened the header to
`## Documentarian Rule` + a fenced `DOCUMENT WHAT EXISTS — NEVER SUGGEST, CRITIQUE, OR
IMPROVE` block (`commands/create_research.md:10-18`,
`commands/create_product_research.md:10-18`) and carry three additional placements in
`create_research` that upstream lacks (`:58` in the jira-context step, `:101` in the
tracer-bullet scoping probe, `:203` in the agent-spawn step). So on the documentarian axis we
independently applied a *softening* upstream measured and declined.

Both trees keep the rule **inline** in the agent files rather than linking out — ours at
`agents/codebase-analyzer.md:9-18,105,107` (ending `## REMEMBER: You are a documentarian, not
a critic`) and `agents/product-behavior-analyzer.md:9-18,136`; upstream at
`plugin/agents/codebase-analyzer.md:112`. Upstream states the reason in its reference doc:
typed wb agents carry the constraint in their own system prompts, "**Ad-hoc
`general-purpose` agents do not** — when a research skill spawns specialized one-off
researchers… the spawning prompt must include the documentarian constraint explicitly. That
is what the 'Remind EVERY agent' instruction in the research skills exists for." Both trees
carry that "Remind EVERY agent" instruction. The reference doc also names the rule's escape
hatch — *unless explicitly asked* — as explicit design: "The discipline forbids unsolicited
judgment, not requested analysis." Both our research commands also share upstream's gap of
having only 2 of the 3 canonical placements in `create_product_research` (no agent-spawn-step
restatement).

Two further scope-block divergences of the same kind, where upstream's block is the *larger*
one: `plugin/skills/create_design/SKILL.md:17-25` expands
`## CRITICAL: This Document is About WHAT and WHY - NEVER HOW` to five DO-NOT/ONLY bullets
plus "The HOW comes later in the execution plan - NOT HERE", against two bullets at our
`commands/create_design.md:12-15`; and `plugin/skills/implement/sub-agent-prompts.md:68-75`
adds the `**DO NOT COMMIT**` bullet to the `## CRITICAL Constraints` block that is otherwise
byte-identical to our `commands/implement_coordinated.md:355-361`.

---

## 7. Structural layout and context economy

**Layout.** Upstream: `.claude-plugin/marketplace.json` at root with `"source": "./plugin"`;
the plugin manifest and the entire shipped runtime under `plugin/`; maintainer docs and plans
in a root `docs/` that installers never receive; a shipped `plugin/docs/reference/` holding
three skill-linked docs (`beads-mode.md` 59 lines, `beads-not-initialized.md` 47,
`documentarian-philosophy.md` 32). Ours: both manifests at root
(`.claude-plugin/marketplace.json` with `"source": "./"`), no `plugin/` subtree, and no
shipped/maintainer split — `commands/`, `agents/`, `skills/`, `hooks/`, `scripts/`, `docs/`
are all top-level and all shipped. We have no shared-reference directory; the nearest
analogue is ad-hoc links to individual `docs/*.md` (e.g. `docs/beads-fast-fail.md` linked
from `commands/implement_coordinated.md:134`, `commands/forge.md:110`,
`commands/create_execution.md:456`, `commands/implement_tasks.md:134`).

**Progressive disclosure.** Upstream splits each stage into `SKILL.md` plus on-demand
`templates.md` / `sub-agent-prompts.md` / `reference.md` / `examples.md`, referenced by
relative link with an explicit instruction (`create_research/SKILL.md:12-15`): "Supporting
files in this directory (read each when its step directs you to — **never paraphrase from
memory**)". Workflow skills carry `allowed-tools: Read` (`create_research/SKILL.md:5`) so
those reads don't prompt for permission mid-skill.

Measured effect, our 14 stage commands vs their upstream counterparts (`wc -l`):

| stage (ours → upstream) | ours | up SKILL.md | up supporting | up total |
| ----------------------- | ---- | ----------- | ------------- | -------- |
| create_research → create_research | 417 | 250 | 219 | 469 |
| create_product_research → create_product_research | 494 | 327 | 235 | 562 |
| create_design → create_design | 505 | 344 | 205 | 549 |
| create_execution → create_tasks | 787 | 426 | 483 | 909 |
| create_project → create_project | 452 | 203 | 321 | 524 |
| create_handoff → create_handoff | 482 | 260 | 263 | 523 |
| resume_handoff → resume_handoff | 407 | 376 | 83 | 459 |
| implement_tasks → implement_inline | 690 | 601 | 90 | 691 |
| implement_coordinated → implement | 841 | 451 | 362 | 813 |
| update_status → update_status | 497 | 377 | 132 | 509 |
| validate_execution → validate_execution | 448 | 236 | 240 | 476 |
| validate_project → validate_project | 546 | 249 | 294 | 543 |
| create_mockup → create_mockup | 653 | 290 | 413 | 703 |
| help → help | 246 | 302 | 0 | 302 |
| **TOTAL** | **7,465** | **4,692** | — | **8,032** |

Upstream's total content is *larger* (8,032 vs 7,465 lines) while what loads at invocation is
**37.1% smaller** (4,692 vs 7,465) — consistent with the −37.5% upstream recorded at v2.0.0.

**Step skeletons are near-identical**, which is what makes a port mechanical rather than a
rewrite. `commands/create_research.md` and `plugin/skills/create_research/SKILL.md` share the
same Step 1–8 headings, the same `## Parallel Research Strategy` / `#### Agent Spawning
Examples` / `#### Parallel Execution` structure, and the same `## Important Notes` /
`### Critical Ordering` / `### Documentation Philosophy` / `### File Reading` tail. Our
divergences in that file are additive: `### Step 0: Ticket Context Bootstrap` (jira-context),
the tracer-bullet scoping probe at `:97-105`, and the inlined output template that upstream
moved to `templates.md`. Upstream's tail adds a `### Synchronization Points` section ours
lacks.

**Naming and stage chain.** Ours (`commands/help.md:25-40`, `CLAUDE.md` Command Workflow):
`create_project → create_research → create_design → create_execution → implement_tasks →
validate_execution`. Upstream: `create_project → create_research → [explore_design
(optional)] → create_design → create_tasks → implement → validate_execution`, with
`implement_inline` beside `implement`. Upstream keeps 24-line deprecated alias stubs at
`plugin/skills/implement_coordinated/` and `plugin/skills/implement_tasks/`
(`disable-model-invocation: true`, announce the rename once, then "Read
[../implement/SKILL.md] NOW and follow it exactly"), plus one pointer file per supporting
file so a session holding a stale skill body still resolves its reads. We have no aliasing
mechanism at all. `explore_design` appears nowhere in our tree
(`grep -rn explore_design commands/ skills/ CLAUDE.md README.md docs/` → 0 hits).

---

## 8. Hooks, compaction, and doc adherence

| Hook / event | Upstream | Ours |
| ------------ | -------- | ---- |
| SessionStart | `plugin/hooks/wb-prime.sh` (94 lines) — orientation on `startup`/`resume`/`clear`/`fork`, recovery text on `compact`; `.claude/wb/PRIME.md` override; `--export` prints the default; contract "<100ms, no bd invocations, plain-text stdout, exit 0 always" | `hooks/setup-beads-mode.sh` (38 lines) — sets `BEADS_AVAILABLE` and `BEADS_MODE` into `$CLAUDE_ENV_FILE`; "uses filesystem + binary checks ONLY… never spawns a `bd` subprocess"; **emits nothing model-visible** |
| PreCompact | `wb-prime.sh` registered | **not registered** (`grep -c "PreCompact" .claude-plugin/plugin.json` → 0) |
| SessionEnd | `plugin/hooks/beads-drift-check.sh` (17 lines) — one `bd config get`; prints a `bd dolt push` reminder only when a Dolt remote is configured | **absent** (`grep -c "SessionEnd"` → 0) |
| PostToolUse (Write/Edit) | `plugin/scripts/lint-hook` | `scripts/lint-hook` — same behavior; ours additionally keeps a legacy `CLAUDE_TOOL_ARGS` fallback (`scripts/lint-hook:9-14`) |

`wb-prime.sh` behavior in detail: on a compact payload it scans `docs/plans/*/tasks.md` for
non-`complete` status and prints "Context was just compacted — any plan-doc summaries above
are paraphrase, not verified content," names the active or candidate plans, and instructs a
full re-read plus a `bd ready` / `bd list` check. On a fresh start it prints the stage chain,
the `docs/plans/<date>-<name>/` convention, "beads holds status and markdown holds the plan",
the checkpoint rule, the session-start sanity check, the active plans, and a `/wb:help`
pointer, ending with the truncation line `bd prime` uses.

**`doc-adherence`** (`plugin/skills/doc-adherence/SKILL.md`, 61 lines,
`user-invocable: false`, `allowed-tools: Read, Glob, Grep, Bash(bd:*)`) carries the Iron Law
`NO ASSERTIONS ABOUT PLAN DOC CONTENTS WITHOUT A READ IN THE CURRENT CONTEXT WINDOW` — "If
the full read isn't visible in this context window, you cannot cite it" — with an
IDENTIFY→CHECK→READ→ASSERT gate, a rationalizations table, and an explicit
"Relationship to the Recovery Hook" section. Upstream records it as blind-trial validated
9/9. **Absent in ours** (`grep -rln doc-adherence` → 0 hits).
`skills/project-structure/SKILL.md` (38 lines) covers document *placement*, not
context-window staleness.

Also from the same upstream release (v2.3.0) and absent here: progress frontmatter
consolidated to `update_status` as **sole writer**, and a corresponding frontmatter-drift
indicator in `status-sync`. Our `skills/status-sync/SKILL.md` has no frontmatter-drift
section; upstream's has one at `:38-42` ("compare tasks.md frontmatter
`completed_tasks`/`current_phase` against beads reality… remind the user to run
`/wb:update_status`"). Upstream also adds handoff-over-compact guidance ("a phase that would
need a second `/compact` hands off instead"); ours has none.

Upstream's three shared background skills also carry trigger-scope text ours lack:
`tdd-discipline` "including quick ad-hoc fixes outside the workflow commands (coordinated
workers preload this skill; solo edits must trigger it)";
`verification-before-completion` "including after ad-hoc fixes and one-off commands, not
just workflow phases". And upstream marks background skills `user-invocable: false`
(`doc-adherence`, `project-structure`, `status-sync`, `tdd-discipline`,
`verification-before-completion`); ours carry no such field.

---

## 9. Beads model divergence

Upstream replaced the two-mode model outright at 3.0.0. `plugin/docs/reference/beads-mode.md`
states three persistence tiers — (1) the local embedded Dolt database under `.beads/`, always
the source of truth; (2) cross-machine continuity via a Dolt remote (`bd dolt push`/`pull`) or
`bd backup`; (3) JSONL export for interchange only, written only when `export.auto` is on or
`bd export` is run — plus a stealth-first setup rule (`:7`), the statement that "`.beads/` is
never committed to git" (`:17`), a bd **1.1.0** floor (`:46`), and a session-start sanity
check (`:36-48`: `bd context`, `bd show <beads_epic>`, `bd stats`, `bd version`) that every
stage reading a plan's beads IDs runs before work, stopping on a missing epic.

Our tree still runs the pre-1.0.2 vocabulary. Counts over
`agents commands skills docs hooks scripts CLAUDE.md AGENTS.md README.md .claude-plugin`:

| Token | Sites in ours | Upstream |
| ----- | ------------- | -------- |
| `BEADS_MODE` | **17** (across `commands/create_execution.md`, `create_handoff.md`, `implement_coordinated.md` ×3, `implement_tasks.md` ×2, `resume_handoff.md`, `update_status.md`, `validate_project.md`, `docs/beads-stealth-mode.md`, `docs/commands-reference.md`, `docs/workbench-workflow-guide.md` ×2, `hooks/setup-beads-mode.sh` ×3) | removed at 3.0.0 |
| `git add .beads` | **9** (`commands/implement_coordinated.md:662`, `implement_tasks.md:504`, `update_status.md:312`, `create_handoff.md:126`, `help.md:146`, `docs/workbench-workflow-guide.md:463,489`, `docs/beads-stealth-mode.md:14`, `docs/beads-integration-learnings.md:154`) | removed everywhere; "Beads' Dolt directory is never committed" |
| `bd sync` | **36** | 0 in guidance (dropped at 2.0.0 for bd ≥ 1.0.2) |
| `bd update --claim` | **0** | the documented claim verb (atomic; "closes the double-claim window in coordinated execution", 14 sites) |
| `--status in_progress` | **21** | replaced by `--claim` in examples |
| `bd dolt push` / `bd backup` | **0** / **0** | the persistence actions |
| `bd remember` / `bd memories` / `bd forget` | **0** | the memory surface (D5) |
| `bd context` / `bd stats` / `bd orphans` / `bd stale` | **0** each | the sanity check + hygiene set |
| `bd doctor` | **16** | named with an embedded-mode caveat (server-only in bd 1.1.0), with `bd stale`/`bd orphans` as the fallback |

Note the internal tension already present on our side: our `.gitignore` ignores `.beads/`
(stealth), while `commands/implement_coordinated.md:661-664` and
`commands/implement_tasks.md:504` still branch on `[ "$BEADS_MODE" != "stealth" ]` to
`git add .beads/ && git commit`, and `docs/beads-stealth-mode.md:10-14` documents git mode as
the default. Also, `docs/beads-fast-fail.md` states availability is detected via
`$BEADS_AVAILABLE` (binary + directory walk), while
`docs/beads-integration-learnings.md` records a resolution of "Standardized on
`ls .beads/beads.db 2>/dev/null`" — a `.db` file that the embedded-Dolt backend does not
produce.

Neither `docs/beads-fast-fail.md`, `docs/beads-stealth-mode.md`,
`docs/beads-integration-learnings.md`, nor `AGENTS.md` names a minimum bd version. We have no
session-start sanity check and no wrong-database case.

Two beads-adjacent things are **ours-only**: `docs/beads-fast-fail.md` (78 lines — the rule
that availability must be probed by filesystem/binary check, never by `bd doctor`, which can
hang since the embedded-Dolt migration) and `docs/beads-stealth-mode.md` (32 lines).
Upstream reached the stealth-first conclusion by a different route (beads' own
`bd init --stealth`) and has no fast-fail doctrine.

---

## 10. The subagent tool-call ceiling

`.context/upstream/docs/subagent-tool-call-ceiling.md` (162 lines, maintainer-only) records:
subagents are cut off at roughly **70 tool calls**, measured across 129 subagent transcripts
(max 70, zero above 70; median/p75/p90 = 27/39/58). It rules out context exhaustion — "a
worker truncated at 70 calls held only 92K tokens while a survivor at 68 calls held 150K" —
and notes 70 is "measured on one machine, one session, one model," not a verified constant.

Two consequences upstream wired into live skill text:

- `plugin/skills/implement/SKILL.md:197` — "Subagents hard-stop when they exhaust their
  tool-call budget (observed near ~70 calls), and the truncated work is always the finishing
  tail. **A task projecting past ~50 calls: split it at its natural seam before spawning.**"
- `plugin/skills/implement/SKILL.md:272` and `reference.md:78-80` — truncation and genuine
  failure are **distinct events needing opposite remedies**, discriminated cheaply by
  `git status`; "**Never retry the whole task**: same task + same context = same budget,
  truncating at the same point." Truncation is detectable only because the `task-worker`
  contract makes `bd close` the worker's final action.

**Ours has nothing on this.** No tool-call budget, no projected-call sizing rule in
`commands/create_execution.md`, and no truncation-vs-failure distinction in
`commands/implement_coordinated.md`'s failure path (`:435-456` treats every FAIL as an
implementation defect and retries with the same context twice — the exact pattern upstream's
doc names as guaranteed to truncate at the same point).

---

## 11. Release mechanics and the lint gate

Upstream has a root `CHANGELOG.md` (197 lines, 1.0.0 → 3.0.0) and a root `RELEASING.md` (50
lines) defining: a two-channel model (`--plugin-dir` dev vs marketplace release); a semver
rubric for a prompt library (patch = prompt bugfixes, minor = additive skills/agents/hooks,
major = removed or renamed commands); a process in which a plan lives on one branch and
merges once carrying the bump; **every cut is tagged** `vX.Y.Z`; a major gets a three-session
`--plugin-dir` canary; a "Verification before any bump" step that runs lint with zero delta,
grep audits, a smoke session, and a **help-drift grep**
(`grep -L "needs from you" plugin/skills/*/SKILL.md`); a rollback rule (revert + new patch);
and a `1.x` maintenance branch holding "the final pre-modernization release (v1.1.0:
`commands/` layout, root-level `.claude-plugin/`, pre-embedded-Dolt beads)" — i.e. the shape
our tree still has.

**We have neither file.** Our release process exists only as the numbered list in
`CLAUDE.md` "Releasing New Commands/Skills/Agents": bump both manifests, commit, push,
`claude plugin update wb@thescubageek-workbench`, restart. No tagging step, no semver rubric,
no pre-bump verification, no canary.

**The lint exit code.** Upstream's 3.0.0 fixed `plugin/scripts/lint` to exit 1 whenever
markdownlint reported an error, "in named-file, changed-files, and `--all` modes, and… from
`--fix` when findings remain; it had always exited 0." Our `scripts/lint` has *already fixed*
the pipeline-subshell half independently and documents it at `scripts/lint:183-186`
("use a here-string, not `echo "$FILES" | while`. A pipe runs the loop in a subshell, so
`ISSUES_FOUND` would never propagate"). But the `--fix` path is still open: at
`scripts/lint:220-225` the `exit 1` sits **inside** `if [ -z "$AUTO_FIX" ]` with no `else`,
so a `--fix` run with un-autofixable findings falls through with no `exit` and returns 0.
Upstream's equivalent (`plugin/scripts/lint:217-223`) puts `exit 1` outside that inner `if`
and adds an "Some issues could not be auto-fixed" message.

Verified empirically in this workspace on a fixture with a duplicate heading:

```
./scripts/lint       /tmp/wblint/bad.md  → exit 1
./scripts/lint --fix /tmp/wblint/bad.md  → exit 0     # findings remained
```

`scripts/lint-hook` on both sides always exits 0 by design, so an edit is never blocked.

---

## 12. Capability inventory

**Ours-only** (no upstream counterpart):

| Capability | Path | Lines |
| ---------- | ---- | ----- |
| `forge` — pipeline sequencer with per-phase model gates and `Q:`/`Decide:` barriers | `commands/forge.md` | 150 |
| `resolve_questions` — walk open `Q:`/`Decide:`/`Validate:`/`UI Q:` one at a time, record each as a decision in design.md, close the source | `commands/resolve_questions.md` | 374 |
| `model-help` — model/effort authority + gate mode | `skills/model-help/SKILL.md` | 119 |
| `daily-digest` — morning catch-up + day plan across Jira/beads/git/Sentry/Notion/Gmail/Calendar with a usage-window budget | `skills/daily-digest/SKILL.md` | 269 |
| `jira-context` — hivemind off a ticket's Agents section via Atlassian MCP | `skills/jira-context/SKILL.md` | 149 |
| `fetch-issues` — reconcile open GitHub issues against PRs and code, rank, write per-issue handoffs | `skills/fetch-issues/SKILL.md` | 302 |
| `touch-grass` — paced, checkpointed long-horizon work with `ScheduleWakeup` | `skills/touch-grass/SKILL.md` | 111 |
| `tracer-bullet` — one cheap probe at the riskiest assumption before fanning out | `skills/tracer-bullet/SKILL.md` | 86 |
| `clip` / `eli5-clip` | `skills/clip/SKILL.md`, `skills/eli5-clip/SKILL.md` | 41 / 52 |
| `scripts/quiet`, `scripts/test-quiet` — exit-code-faithful output backpressure | `scripts/` | — |
| `docs/beads-fast-fail.md`, `docs/beads-stealth-mode.md` | `docs/` | 78 / 32 |
| Branch-naming convention `<TICKET>/<snake_case>` tied to jira-context | `CLAUDE.md` "Branch naming" | — |

**Upstream-only**:

| Capability | Path | Lines |
| ---------- | ---- | ----- |
| `explore_design` — optional facilitated architecture stage (frame→diverge→discuss→converge→record); writes a `thoughts/` record + a closed `Decide:` issue, never design.md | `plugin/skills/explore_design/` | 299 + 116 |
| `doc-adherence` — the context-window read gate | `plugin/skills/doc-adherence/SKILL.md` | 61 |
| `task-worker` agent | `plugin/agents/task-worker.md` | 40 |
| Stateful `help` — Case A/B/C position report + "What each stage needs from you" table | `plugin/skills/help/SKILL.md` | 302 |
| Plan **Intent** section + per-stage obligations (Goal / Success looks like / Non-goals / Amendments; `Intent Coverage` in research; `(refines:)` metrics in design; `→ PASS/FAIL/DEFERRED` in validation) | `create_project/templates.md`, `create_research/SKILL.md:70-71,207,220`, etc. | — |
| `wb-prime.sh` + `beads-drift-check.sh` hooks | `plugin/hooks/` | 94 + 17 |
| `plugin/docs/reference/` shared runtime docs | 3 files | 138 |
| `CHANGELOG.md` + `RELEASING.md` | root | 197 + 50 |
| `docs/beads-guide.md` — maintainer bd contract inventory with a verified-on column | `docs/` | 147 |
| `docs/subagent-tool-call-ceiling.md` | `docs/` | 162 |
| Deprecated-alias stub mechanism (stub SKILL.md + pointer files per supporting file) | `plugin/skills/implement_coordinated/`, `implement_tasks/` | 24 each |

**In both, diverged** — every shared stage file differs; per-file line counts and the
sections unique to each side are in §7's table and §5. Notable content-level divergences
beyond size:

- `agents/task-verifier.md` — same 207 lines both sides, different contract: ours diffs
  against a caller-supplied Base Ref (workers may commit); upstream inspects an uncommitted
  working tree (workers never commit) and pins `model: sonnet` / `effort: high`
- `skills/status-sync/` — ours reminds about `bd sync`; upstream reminds about a configured
  Dolt remote and adds the frontmatter-drift check
- `skills/review-prep/` — 158 lines both sides; the only diff is list-numbering style
- `skills/research-validation/` — 107 vs 109; upstream adds the sonnet/high frontmatter pin
- `skills/mockup-iteration/` — 475 ours vs 380 upstream (ours is the larger)

---

## 13. Places our own in-flight work already answers an upstream decision

Facts about our unmerged branches, relevant because they occupy the same design space:

- `origin/thescubageek/knowledge-store-v1` — 34 files, +4,770 lines: `skills/knowledge-store/SKILL.md`,
  `commands/curate_knowledge.md`, `hooks/knowledge-capture.sh`, `hooks/knowledge-guard.sh`,
  and nine `scripts/knowledge-*` executables with test harnesses, wired into
  `commands/create_research.md`, `resume_handoff.md`, `implement_*.md`, `validate_execution.md`.
  This is a durable-memory subsystem — the same problem upstream's D5 solves with three lines
  of `bd remember` guidance.
- `origin/thescubageek/self-learning-loops-research` — continues the same track (staging,
  curation proposal linter, promotion).
- `origin/runtime-context-backpressure` — the track that produced `scripts/quiet`.
- `origin/prompt-efficiency-research` — our own prompt-efficiency work; its Phase 4–6 commit
  is "beads-stealth extraction, output-discipline, handoff rework", i.e. we arrived at
  stealth beads and output discipline independently of upstream's route.
- `origin/adversarial-review-system` — "adversarial meta-review release gate (v1.2.0)";
  upstream's release gate is `RELEASING.md`'s pre-bump verification instead.
- `origin/encode-tracer-bullet-optimization` — the tracer-bullet skill, which is also the
  source of our two "single load-bearing unknown" directives that have no upstream analogue.

---

## Code References

Ours:

- `skills/model-help/SKILL.md:22,24,38-43,55-56,60-66,70-81,83-92` — roster, two-Opus rule, tier table, two-levers, gate baselines, switch-cost rule, output template
- `CLAUDE.md:161-166` — reasonless triple-marker Command Structure Patterns example
- `CLAUDE.md:174-179` — "Model & effort at gates" policy
- `CLAUDE.md:189-195` — "Working with Commands" list (item 3 is the think-deeply mandate)
- `commands/implement_coordinated.md:264-267` — prose worker tiers, opus default
- `commands/implement_coordinated.md:435-456` — opus fix worker, 2 retries, then blocking list
- `commands/implement_coordinated.md:661-664` — `BEADS_MODE != stealth` → `git add .beads/`
- `commands/implement_coordinated.md:672-710` — `determineModel()` keyword regex
- `commands/implement_coordinated.md:192-231,294-379` — context package and inlined worker prompt template
- `commands/implement_tasks.md:50-58` — scope NEVER-list, immediately followed by `:60` TDD flow
- `commands/create_research.md:10-18,58,97-105,203,210` — documentarian placements, tracer-bullet probe, BARRIER 2
- `scripts/lint:183-186` — the here-string fix and its comment
- `scripts/lint:210-225` — final status block; `exit 1` nested inside the non-`--fix` branch
- `hooks/setup-beads-mode.sh:1-38` — fast-fail availability + `BEADS_MODE`
- `agents/task-verifier.md:17-22,141-145` — scope verification against Base Ref
- `skills/tdd-discipline/SKILL.md:38,50` — fail-fast RED/GREEN and `scripts/quiet` (ours-only)

Upstream (all under `.context/upstream/`):

- `CLAUDE.md:163-170` — tier legend incl. Fable's three roles and the `effort: high` rule
- `CLAUDE.md` "Working with Commands" / "Command Structure Patterns" — the D9 rewrite
- `docs/workbench-workflow-guide.md:62-75` — per-stage session-model table
- `plugin/skills/create_tasks/SKILL.md:26-41` — Model Self-Check (Fable/Opus floor)
- `plugin/skills/explore_design/SKILL.md:22-37,294` — the self-check pattern it came from
- `plugin/skills/implement/SKILL.md:191,197,198-204,205,254-256,272` — autonomy paragraph, tool-call budget, tier rule, task-worker spawn, escalation, truncation handling
- `plugin/skills/implement/sub-agent-prompts.md:16-18,112-128` — `why:` first; fable fix worker, one retry
- `plugin/skills/implement/reference.md:9-12,57-59,78-80` — context package `why:`, regex retirement, never-retry-whole-task
- `plugin/skills/implement_inline/SKILL.md:62-66,406-412` — Extras and edits; `bd remember`
- `plugin/agents/task-worker.md:1-7,25,30-31` — frontmatter, Operating Mode, Constraints
- `plugin/skills/create_handoff/SKILL.md:111` — memory review
- `plugin/skills/doc-adherence/SKILL.md:12-16,26-33,59-61` — Iron Law, gate, hook relationship
- `plugin/skills/help/SKILL.md:36,95` — position report; human-input map
- `plugin/hooks/wb-prime.sh:1-93` — orientation/recovery contract
- `plugin/docs/reference/beads-mode.md:7,11-16,17,36-48` — stealth rule, three tiers, never-commit, sanity check
- `plugin/docs/reference/documentarian-philosophy.md:1-12` — extracted shared rule
- `plugin/scripts/lint:207-224` — the fixed exit path
- `docs/subagent-tool-call-ceiling.md:11,20-31,39-45,87-129,138-155` — the ceiling evidence
- `docs/plans/2026-09-01-fable-5-1-rebaseline/{research.md,design.md,thoughts/,trials/}` — the Fable plan
- `docs/plans/2026-09-05-prompts-h7c-implement-rename-3.0/design.md` D1–D20 — the 3.0.0 plan
- `docs/plans/2026-08-21-prompts-8bj-compaction-drift-hardening/design.md` D1–D4 — compaction hardening
- `RELEASING.md`, `CHANGELOG.md` — release mechanics and the full change log

---

## Open Questions

*All seven resolved as of 2026-09-08 via `/wb:resolve_questions`; decisions live in
`design.md` (## Technical Decisions).*

`bd` is **not installed in this workspace** (`which bd` → not found). Under `design.md`'s D6
these records are markdown-native by design, so there is nothing to file elsewhere.

- **Q**: Does our target model roster include Fable at all as a routine tier? `model-help:22`
  currently says "default to the four above unless the user prefers Fable," which makes
  upstream's Fable-as-default-for-two-stages routing inapplicable as written. Blocks any
  decision on D1/D2/D3.
  - **Resolved 2026-09-08** → decision recorded in `design.md` (## Technical Decisions, D12)
- **Q**: Is our `create_execution` baseline (Sonnet 5/medium, "structuring, not deciding")
  or upstream's (`create_tasks` at Fable/high, "decomposition quality sets the ceiling")
  the correct reading of that stage? The two rubrics disagree on the same stage. Blocks D2.
  - **Resolved 2026-09-08** → decision recorded in `design.md` (## Technical Decisions, D12)
- **Q**: Do we adopt the `task-worker` agent file, or keep the inlined worker prompt template?
  Four of the seven Phase 1 guardrails (surgical edits, follow-ups-not-fixes, autonomy,
  `skills: [tdd-discipline]` preload) live in that file upstream, so the answer determines
  whether they land in one place or five.
  - **Resolved 2026-09-08** → decision recorded in `design.md` (## Technical Decisions, D20);
    the agent file is created by task `P2-T11`
- **Q**: Does the durable-memory obligation route to `bd remember` (upstream D5) or to the
  `knowledge-store` subsystem on `origin/thescubageek/knowledge-store-v1`? These are two
  answers to one problem.
  - **Resolved 2026-09-08** → decision recorded in `design.md` (## Technical Decisions, D8) —
    neither; `knowledge-store` is recorded as out of scope
- **Q**: Do we take the `plugin/` relocation and the `commands/` → `skills/` progressive-
  disclosure migration (a −37% invocation-context win, but it touches all 16 command files,
  both manifests, every doc path, and our fork's install identity), or port upstream's prose
  into our existing monoliths?
  - **Resolved 2026-09-08** → decision recorded in `design.md` (## Technical Decisions, D1/D2)
- **Q**: What bd version floor do we assert, and does `bd sync` still exist? 36 of our sites
  invoke it; upstream dropped it at bd ≥ 1.0.2. Unverifiable here — no `bd` binary.
  - **Resolved 2026-09-08** → moot; `design.md` (## Technical Decisions, D4) removes beads, so
    no version floor is asserted
- **Q**: Does our worker default stay **opus** or move to **sonnet** to match upstream?
  Ours is the more expensive default and upstream changed away from it deliberately
  (prompts-2b5, 2026-07-10).
  - **Resolved 2026-09-08** → decision recorded in `design.md` (## Technical Decisions,
    Resolved Decisions)

---

## Next Steps

1. Review this document.
2. Run `/wb:create_design docs/plans/2026-09-08-upstream-fable-merge/` to record
   adopt / adapt / skip per item, phased by risk. The natural seams the facts suggest:
   the Fable Phase 1 guardrails (additive, no gate needed — upstream's own reasoning);
   the R1 trim plus the CLAUDE.md root that regenerates it; the beads-vocabulary
   realignment (breaking); and the structural migration (largest blast radius, independent
   of the Fable question).
3. Resolve the open questions above — several are prerequisites, not parallel work.
4. Note for whoever picks this up: **R3 and R4 need no action.** Upstream measured both and
   kept its original wording; our barrier and scope-block volume is already at parity with
   what upstream kept.
