---
project: prompt-efficiency
ticket: N/A
created: 2026-05-28
status: draft
last_updated: 2026-06-04
last_updated_note: "Resolved all 4 pending decisions via /wb:resolve_questions"
depends_on: research.md
design_approach: Conservative dedup + terse-directive rewrite (Option B) with conditional beads-stealth extraction, output-token reduction, and cache-aware structuring
---

# Design: Prompt Efficiency for Opus 4.8 Token Optimization

## Problem Statement

The `wb` plugin's prompt surface carries a large, measured layer of repeated
boilerplate: ~10k tokens of BARRIER scaffolding, embedded output templates,
Initial Response blocks, Task() pseudocode, repeated DO-NOT lists, and
beads-mode conditionals (research §12). This boilerplate inflates the token
cost of every command invocation on current-generation Opus 4.8, without
adding proportional value — much of it is verbatim restatement of content that
already appears inline in the same file.

The cost must be reduced **without** degrading the property the prompts are
valued for: highly predictable output and clean command-to-command chaining.
The barriers, documentarian rules, and the output template each command writes
are load-bearing — they are why the outputs are reliable. The waste is in
*how verbosely* those invariants are expressed and in *pure restatement*, not
in the invariants themselves.

Solving this now keeps the plugin economical as it grows (14 commands today)
and establishes a compaction style — grounded in the repo's own precedent —
that future commands can follow rather than re-bloating.

Two cost vectors beyond raw input size shape the design:

- **Prompt caching front-loads the input win.** Because this is a Claude Code
  plugin, cache breakpoints are harness-managed, not author-controlled. On a
  cache *hit*, input is already ~10× cheaper, so input-token compaction
  delivers most of its value on the **first (cache-miss)** invocation of a
  command in a session — repeat invocations are already cheap. The design's
  caching job is therefore to *not break cacheability* (keep boilerplate static
  and uniform) rather than to orchestrate caching.
- **Output tokens are never cached** and are priced above input, so every
  output token saved is a pure, every-time win. The current prompts drive
  avoidable *narration* output (verbose Confirm-Completion recaps, barrier
  announcements, inter-step restatement — research §12, ~800 tokens of
  completion templates alone). Reducing narration is higher-leverage than
  shaving input, and is safe as long as the generated **artifacts** keep their
  structure (the predictability the constraints protect).

### Success Metrics

- Measurable token reduction on a representative command's prompt body
  (target ~400–700 tokens/command, ~10–15% of a typical `create_*` command)
  with **zero** change to the structure of the document that command produces.
- Every inline `⛔⛔⛔ BARRIER` synchronization marker is preserved (count
  unchanged per command).
- Every output-document template stays inline and byte-equivalent in
  structure (the spec a command writes is unchanged).
- Command-to-command chaining is unbroken: each command remains self-contained
  on its always-needed critical path, and the portable Claude Desktop mirror
  still functions standalone.
- A piloted command produces output indistinguishable in structure from its
  pre-change output (predictability preserved, validated before rollout).
- **Output-token reduction**: a measurable drop in *narration* output on a
  piloted command (compacted Confirm-Completion summary + suppressed inter-step
  restatement), with the generated artifact's structure unchanged.
- **Cacheability preserved**: shared boilerplate remains byte-identical across
  files/invocations (no per-invocation variability introduced), so harness
  cache hits are not degraded.

## Design Approach

Adopt **Option B — conservative dedup + terse-directive rewrite** across
`commands/`, `agents/`, and `skills/`, plus a single permitted **extraction**
of the *conditional* beads-stealth block to a runtime-read reference doc.

Three classes of edit, in decreasing safety order:

1. **Remove provably-redundant restatement** (no semantic change):
   - Delete each command's end-of-file `## Synchronization Points` recap. These
     are pure restatement of the inline `⛔⛔⛔ BARRIER` markers and carry no
     unique instruction (verified: see Why This Approach).
   - Collapse in-file slogan repetition (e.g. "Document what IS, not what
     SHOULD BE" appearing 7–9× in one file) down to the load-bearing instances,
     including those embedded in spawned-agent prompts.

2. **Compact verbose preambles into terse directives** using the repo's own
   "Iron Law" / "The Rule" banner precedent, preserving directive *meaning*:
   - The `CRITICAL: YOUR ONLY JOB IS TO DOCUMENT THE CODEBASE AS IT EXISTS`
     header + 5-bullet DO-NOT list → one terse banner.
   - The "Sub-agents are READ-ONLY…" preamble → a single line.
   - The repeated Task() scaffolding (`CRITICAL INSTRUCTIONS:` block + the
     verbatim `DO NOT write any files. Return your findings as a report.`
     closer) → tightened, while each agent's substantive instructions stay.
   - In-place terse rewrite of the near-identical regions shared by
     `create_research.md` and `create_product_research.md`.

3. **Extract the one conditional block** the hybrid rule permits:
   - The `if [ "$BEADS_MODE" = "stealth" ]` handling repeated in 7 commands is
     *conditionally relevant* (only matters in stealth mode). Replace the
     inline block with a short conditional pointer that reads a single new
     runtime reference doc only when stealth mode is detected. The common
     (non-stealth) path then pays neither the block's tokens nor a Read.

4. **Reduce narration output tokens** (never cached; every-time win):
   - Compact the per-command `Confirm Completion` summary templates so the
     emitted recap is terse rather than a multi-line restatement.
   - Add a narration-discipline directive — *act on barriers silently; do not
     restate the plan between steps; emit only the artifact plus a one-line
     completion summary* — preferring a **single global rule in `CLAUDE.md`**
     (auto-loaded, cached, applies to every command from one location) over
     per-command repetition. (Sub-decision in Pending Decisions.)
   - The line held: narration terseness is aggressive and safe; **generated
     artifact structure is left unchanged** (predictability per OPUS-2).

5. **Structure for cacheability** (guardrail, not a new lever):
   - Keep all compacted boilerplate static and uniform across files so
     harness-managed cache prefixes stay byte-identical and reusable.
   - Order spawned-agent `Task()` prompts **stable-first, variable-last** (the
     standardized documentarian/DO-NOT preamble ahead of the task-specific
     detail) so the reusable prefix is as long as possible.

### Why This Approach

- **It targets waste, not invariants.** Verification confirmed the end-of-file
  Synchronization Points recaps are pure restatement with zero unique signal
  (`create_research.md:416-420`, `create_design.md:468-475`,
  `create_execution.md:773-779` all just summarize their inline barriers).
  Removing them loses nothing; the inline `⛔⛔⛔` markers — the reliability
  signal — stay.
- **It reuses an in-repo precedent.** The "Iron Law" / "The Rule" banner
  (`skills/tdd-discipline/SKILL.md:12-17`,
  `skills/verification-before-completion/SKILL.md:12-19`,
  `skills/research-validation/SKILL.md:15-20`) already proves a verbose
  principle can be compressed to a single ALL-CAPS directive line + one
  sentence without losing force. Following an existing convention keeps the
  prompts consistent (a value the user cares about) instead of inventing a new
  style.
- **It honors the hybrid inline rule.** Always-needed critical-path content
  (barriers, documentarian rules, the output template a command writes) stays
  inline. The *only* extraction is the beads-stealth block, which is genuinely
  conditional — exactly the case the hybrid rule says extraction pays off,
  because the common path avoids both the tokens and the latency hop.
- **It respects the consolidation constraint.** Verification confirmed that
  `create_research.md` and `create_product_research.md` cannot be deduped by
  extraction (both must be self-contained; the portable mirror
  `docs/product-research-claude-desktop.md` is a full standalone copy and can't
  read other files). So the design uses in-place terse rewriting only — the
  one viable move under the constraint.
- **It is per-invocation honest.** Because only one command's prompt loads per
  turn, the win is framed as tokens-saved-per-command-invocation, not a repo
  total. Edits concentrate on the content that loads every time a command runs.
- **It follows the cost where caching can't discount it.** Harness prompt
  caching makes repeat-invocation *input* ~10× cheaper, so input compaction's
  value is front-loaded on the cache-miss invocation. Output tokens get no such
  discount and are priced higher, so adding the narration-reduction vector
  attacks the cost that recurs on every run — the highest-leverage savings
  available without touching artifact structure.

## Handoff Reliability Workstream

A related defect shares this effort's root cause: `commands/create_handoff.md`
(and its partner `resume_handoff.md`) frequently produce **incomplete, missing,
or hallucinated** handoffs. The cause is the same bloated-template pattern this
design targets, so the fix is folded in here rather than spun out separately.

### Why handoffs fail (diagnosis)

- **Concrete fake examples in the embedded template seed hallucination.** Step 4
  hands the model a ~6,500-char skeleton seeded with realistic sample data —
  `Modified src/component.ts:45-67` (`create_handoff.md:205`),
  `npm test (45/45 pass)` (`:216`), `+[additions] -[deletions]` (`:398`). To a
  model filling a template these read as data, not illustration, so it echoes
  their *shape and sometimes values* instead of grounding each claim.
- **No pre-write grounding barrier.** Unlike `create_research.md:341`
  (BARRIER 3: "verify NO placeholder values — ALL data MUST be from ACTUAL
  codebase"), `create_handoff` has only a read barrier (`:42`). Nothing forces
  file:lines, metrics, and test results to come from real tool output before
  writing. The "Handoff Verification" checklist (`:400-407`) is for the
  *resumer*, not a gate on the author.
- **It relies on conversation recall — least reliable exactly when handoffs
  happen.** Step 1 says "Review conversation history" (`:59`); handoffs are
  created at session end / context limit, when earlier turns are compacted or
  evicted. There is no fallback to re-derive facts from ground truth
  (`git diff`, `git log`, `bd`, a test run) when recall is degraded.
- **It demands unknowable fields with no omit path.** Session Metadata
  (`:391-398`: duration, lines changed, tests written) and "Overall Progress:
  X% complete" (`:176`) can't be measured by the model without running
  `git diff --stat`; with no "omit if unknown" path it confabulates.
- **~15 ungated optional sections** (Learnings, Problems, Decisions, Blockers,
  Deviations, Edge Cases, Tech Debt…) → the model either leaves placeholder
  scaffolding (incomplete) or invents content (hallucinated).
- **No verified-vs-recalled distinction**, so a guessed blocker reads as
  authoritative as a confirmed one.

### Decisions

- **Add a `create_research`-style pre-write grounding barrier**: every file:line,
  metric, and test result must come from actual `git` / `bd` / test output, or
  be omitted / explicitly marked `unverified`.
- **Strip concrete fake examples to terse field labels** (a token win *and* the
  hallucination cure — same move as the template-compaction philosophy above,
  here justified by reliability rather than only cost).
- **Make sections omit-if-empty; mark unknown fields `unknown`** rather than
  fabricate; drop fields the model cannot measure unless derived from a command.
- **Prefer ground-truth sources over conversation recall**, and **lean on
  native Claude channels for durable context** (see Baseline-Capability Reuse),
  keeping the handoff doc thin: in-flight deltas (beads state, uncommitted
  `git diff`, active blockers, next steps) rather than a full session summary.

### Baseline-Capability Reuse

Research found heavy overlap between the custom handoff flow and native,
already-optimized Claude Code features — so part of the fix is to *defer to
baseline* rather than re-implement:

- **Same-machine resumption** (Quick-Start block, git-commit matching, stale
  detection) is largely redundant with `claude --resume` / `--continue` and
  checkpointing/`/rewind` ("Summarize from here"). Thin it to one line; the doc
  exists for **cross-machine / cross-agent / teammate** transfer.
- **Session-summary sections** overlap **auto-compaction** + **auto memory**
  (`MEMORY.md` + topic files). Push durable learnings to survives-compaction
  channels (CLAUDE.md / rules / auto memory) instead of hand-authoring them.
- **Stable facts** ("Key Code Locations / Project Documents") belong in
  CLAUDE.md, maintainable by the baseline `init` skill.
- **Stays custom** (no baseline equivalent): a git-committed *portable* artifact
  for cross-host transfer, the beads integration, the wb pipeline wiring
  (research/design/tasks re-read + phase claim), and mockup-state capture.
- **Caveat**: every native channel except git-tracked CLAUDE.md is
  machine-local (transcripts, compaction, checkpoints, auto memory). For a
  teammate or CI/headless agent on another host, only the committed doc +
  CLAUDE.md survive — so the thin portable doc still earns its place.

## Technical Decisions

### Architecture

- **Compaction style = the existing banner precedent, not a new format.**
  - Rationale: consistency with `skills/*` precedent; the user values
    predictable, uniform prompts.
  - Trade-off: terse banners carry less explanatory hand-holding than the
    5-bullet lists; we accept this because the directive meaning is preserved
    and the audience is a current Opus model that does not need the long form.
  - Pattern reference: `skills/tdd-discipline/SKILL.md:12-17`.

- **Inline barriers are immutable; only their end-of-file recaps are removed.**
  - Rationale: the `⛔⛔⛔ BARRIER` markers are the load-bearing synchronization
    signal and the source of reliable behavior; verification advised against
    touching them.
  - Trade-off: we leave ~1,150 tokens of inline barrier markup untouched rather
    than risk reliability.
  - Pattern reference: `commands/create_research.md:50,195,341`.

- **Output-document templates stay inline and structurally unchanged.**
  - Rationale: the template is the spec the command writes; it is always-needed
    critical path under the hybrid rule, and compacting it risks output quality
    and predictability.
  - Trade-off: the single largest boilerplate class (~5,600 tokens repo-wide)
    is deliberately left alone.
  - Pattern reference: `commands/create_research.md:216-339`.

- **Narration output is compacted; artifact output is not.**
  - Rationale: output tokens are never cached and recur on every run; narration
    (Confirm-Completion recaps, barrier announcements, inter-step restatement)
    can shrink with no loss of clarity, while the generated artifact's
    structure is what makes chaining predictable.
  - Trade-off: assistant prose between steps becomes terser/less explanatory;
    accepted because the artifact and a one-line summary still convey outcome.
  - Pattern reference: Confirm-Completion templates (research §12).

- **Compaction is cache-aware: static, uniform, stable-prefix-first.**
  - Rationale: harness-managed caching reuses byte-identical prefixes; uniform
    boilerplate wording across files and stable-first ordering of agent prompts
    maximize the reusable prefix and avoid cache-busting variability.
  - Trade-off: rules out per-invocation dynamic phrasing in boilerplate (none
    is currently needed), and asks new commands to match the shared wording.
  - Pattern reference: spawned-agent `Task()` blocks, e.g.
    `commands/create_research.md:97-161`.

### Data Model

- **Conditional-read indirection for beads-stealth.** A new minimal reference
  doc holds the stealth-mode handling once. Each of the 7 affected commands
  keeps a short conditional pointer ("if stealth mode, read <doc>"), so the
  content loads only when the `BEADS_MODE=stealth` branch is actually taken.
  - State/flow design: detection of `BEADS_MODE` stays inline in each command
    (it is always-needed); only the *stealth-branch body* moves behind the
    conditional read.
  - Rationale: matches the hybrid rule's definition of content worth extracting
    — conditional, not always loaded.

- **No frontmatter schema changes.** Command/agent/skill frontmatter
  conventions (research §2) are unchanged. Compaction is body-only.

### Integration Points

- **Command → spawned-agent prompts.** Terse-rewritten Task() blocks must keep
  every substantive per-agent instruction and the documentarian directive that
  agents rely on; only scaffolding/closers compress. The
  Component-Locator → Implementation-Analyzer → Pattern-Finder dispatch
  contract (`commands/create_research.md:97-161`) is preserved.
- **Command → command chaining.** Each command stays self-contained on its
  critical path; no command gains a runtime dependency on another command's
  body.
- **Portable Claude Desktop mirror.** `docs/product-research-claude-desktop.md`
  remains a standalone copy; it does not reference the new beads-stealth doc and
  is not part of the beads extraction (it has no stealth-mode branch concern).
- **Agents & skills.** Agent files (`agents/*`) and skills (`skills/*`) get the
  same terse-directive treatment for their duplicated DO-NOT / documentarian
  preambles, consistent with the banner precedent already living in skills.

## Scope Definition

### In Scope

- `commands/*.md` — remove Synchronization Points recaps; terse-rewrite
  preambles, DO-NOT lists, sub-agent preambles, Task() scaffolding/closers;
  in-place compact the create_research ↔ create_product_research shared regions.
- `agents/*.md` — terse-rewrite duplicated documentarian / DO-NOT / "What NOT
  to Do" preambles per the banner precedent.
- `skills/*/SKILL.md` — minor compaction where the same duplication exists
  (the banner precedent already lives here).
- Creating **one** new minimal runtime-read reference doc as the extraction
  target for the conditional beads-stealth block. (This is the mechanism of an
  in-scope command edit, not a modification of the out-of-scope orphan docs.)
- **Output-token reduction within `commands/`**: compact each command's
  `Confirm Completion` summary template and add a per-command narration-
  discipline directive (act on barriers silently; no inter-step restatement;
  artifact + one-line summary only). The per-command form keeps this inside the
  locked scope.
- Cache-aware structuring of the same edits: uniform boilerplate wording and
  stable-first / variable-last ordering of `Task()` agent prompts.
- **Handoff reliability rework** of `commands/create_handoff.md` and
  `commands/resume_handoff.md`: pre-write grounding barrier, example-stripping,
  omit-if-empty sections, ground-truth-over-recall, and deferral to native
  resumption/memory features (see Handoff Reliability Workstream).
- **Output-discipline (Option C, scope-expansion approved 2026-06-04)**: the
  per-command directive above is the baseline; additionally a global
  narration-discipline rule is added to the repo's own root `CLAUDE.md`, and
  **README setup instructions** show users how to opt the same rule into their
  own `~/.claude/CLAUDE.md` or project `CLAUDE.md`. The global rule is
  documented opt-in, never force-installed into a user's config.

### Out of Scope

- Inline `⛔⛔⛔ BARRIER` markers (preserved; reliability signal).
- Embedded output-document templates (always-needed critical path).
- `think deeply` / `ultrathink` directives (cheap; may aid reasoning quality).
- Extraction of any always-needed content to runtime-read docs.
- Dedup of `create_research.md` ↔ `create_product_research.md` by extraction
  (constraint-blocked; in-place rewrite only).
- Orphan docs `docs/claude-code-skills-guide.md` and
  `docs/product-research-claude-desktop.md` (explicitly out per OPUS-5; the
  mirror must keep working but is not edited for compaction).
- Any change to frontmatter conventions or model-hint tiering semantics.
- Shipping the global output-discipline rule *enabled* into users' own configs
  — the plugin cannot and must not write to a user's `~/.claude/CLAUDE.md`.
  (The rule itself is now in scope as an opt-in; see In Scope. What stays out
  is forcing it on.)
- Setting/relying on a per-command **effort hint** (see Pending Decisions —
  requires verifying model-card claims and Claude Code frontmatter support).

## Success Criteria

### Functional Requirements

- [ ] Each edited command still parses and runs through its full step sequence.
- [ ] Every inline barrier present before the change is present after.
- [ ] Each command's output-document template is structurally unchanged.
- [ ] Beads-stealth behavior is unchanged: stealth mode still triggers the same
      handling (now via conditional read); non-stealth path is unaffected.
- [ ] The portable Claude Desktop mirror still runs standalone.
- [ ] Narration output is terser (compact completion summary; no inter-step
      restatement) while the generated artifact is structurally unchanged.
- [ ] A generated handoff contains no unverified file:lines/metrics: every
      such claim traces to actual `git`/`bd`/test output or is marked
      `unverified`/`unknown`; empty sections are omitted, not placeholder-filled.

### Non-Functional Requirements

- [ ] Token reduction: measurable per-invocation drop on a piloted command
      (~400–700 tokens input), with no loss of directive coverage.
- [ ] Output-token reduction: measurable drop in narration output on the
      piloted command, artifact structure held constant.
- [ ] Cacheability: shared boilerplate stays byte-identical across files and
      invocations; agent prompts ordered stable-first / variable-last.
- [ ] Predictability: a piloted command's output is structurally
      indistinguishable from its pre-change output.
- [ ] Consistency: compaction uses the existing banner precedent uniformly;
      no new bespoke formats introduced.
- [ ] Maintainability: shared structure is expressed once where the constraints
      allow (beads-stealth), reducing future drift.

## Risk Analysis

### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Terse rewrites subtly change model adherence/output structure | High | Med | Preserve directive semantics verbatim in meaning; pilot one command (`create_research`) and compare output structure before rolling out |
| Removing recaps weakens barrier enforcement | Med | Low | Verification confirmed recaps are pure restatement; inline barriers untouched |
| beads-stealth conditional read misfires (reads when it shouldn't, or skips when it should) | Med | Low | Keep `BEADS_MODE` detection inline; gate the Read strictly on the stealth branch; test both modes |
| create_research ↔ create_product_research drift after independent in-place rewrites | Low | Med | Rewrite both in the same pass with matched wording; document the intentional non-extraction in this design |
| Portable mirror silently broken by an extraction assumption | Med | Low | Mirror is excluded from extraction and from edits; verify it still runs standalone |
| Narration-discipline directive suppresses useful signal (e.g. hides a real blocker the user needed to see) | Med | Low | Keep the one-line completion summary mandatory; suppress only restatement/echo, not warnings or errors |
| Cache-busting from non-uniform rewrites (same boilerplate worded differently per file) | Low | Med | Standardize on one banner wording; rewrite shared boilerplate in a single pass |
| Thinning the handoff drops context a cross-host teammate actually needed | Med | Med | Keep the portable doc as the floor for cross-host transfer; only defer *same-machine* resumption to native features; push durable facts to git-tracked CLAUDE.md (not machine-local auto memory) |
| Grounding barrier makes handoffs slower/heavier (forces git/bd/test runs) | Low | Med | Scope mandatory grounding to cheap commands already in the flow (`git diff`, `bd list`); make a test run opt-in |

### Assumptions

Beads is not initialized in this repo (research §, confirmed via `bd doctor`),
so assumptions are tracked here in markdown rather than as beads issues. If
beads is later initialized for this work, promote these to `bd create` tasks.

| Assumption | Validated? | If wrong |
|------------|------------|----------|
| Terse-directive rewrites preserve Opus 4.8 adherence equal to the verbose forms | Pending (pilot) | Predictability/reliability degrades — revert that rewrite class |
| End-of-file recaps contribute nothing to behavior | Verified (Agent 1) | n/a |
| The conditional-read pattern for beads-stealth nets a per-invocation win on the common path | Pending (measure) | Net neutral/negative — keep block inline for stealth commands |
| Compaction can use the banner precedent uniformly across commands/agents/skills | Pending (pilot) | Fall back to per-file compaction without a shared style |
| Narration can be cut without losing user-facing clarity | Pending (pilot) | Restore the fuller completion summary for affected commands |
| "Opus 4.8 low effort ≈ 4.7 high" and "cleaner tokens" hold as claimed | **Verified (directional, 2026-06-24)** — Opus 4.8 exceeds prior Opus at *every* effort level; 4.8-high spends ~the same tokens as 4.7's default (xhigh) while scoring higher; low effort cuts tokens 2–3× on some tasks (Anthropic news + benchmark coverage). Exact "low==4.7-high" equivalence not stated, but the efficiency direction holds. | Effort is a real token lever — use it operationally |
| Claude Code command frontmatter supports an effort hint | **Refuted (2026-06-24)** — frontmatter supports `model:` but not `effort:`; effort is session-level (`/effort`, slider, `settings.effortLevel`). | Do NOT add effort to command frontmatter; keep it a session/operational knob |

## Rejected Alternatives

### Option A — Conservative dedup only (recap removal + slogan collapse)
- **Approach**: Remove only provably-redundant restatement; no rewriting.
- **Rejected because**: Leaves the bulk of the recoverable per-invocation cost
  (verbose preambles, DO-NOT lists, Task() scaffolding) on the table for a
  marginal gain. The banner-rewrite has an in-repo precedent that makes it
  low-risk enough to include.
- **Trade-offs**: Lower risk, but ~half the savings; kept as the fallback if a
  rewrite class fails its pilot.

### Option C — Aggressive restructure (extraction + template/barrier compaction)
- **Approach**: B plus extracting always-needed content to runtime docs and
  compacting templates and barriers.
- **Rejected because**: Directly violates the locked constraints — templates
  are always-needed critical path, barrier compaction sacrifices the
  reliability signal, and extracting always-loaded content adds a latency hop
  with no net win (OPUS-3). Only the conditional beads-stealth extraction
  survives from this option, and it is folded into B.
- **Trade-offs**: Larger nominal savings, but at the cost of the predictability
  and reliability the user explicitly prioritized over token cost.

### Extraction-based consolidation of create_research ↔ create_product_research
- **Approach**: Factor the ~1,350 tokens of shared text into a shared include.
- **Rejected because**: Both commands must be self-contained on the critical
  path, and the portable Desktop mirror cannot read other files at runtime
  (OPUS-4). Verification confirmed extraction is not viable.
- **Trade-offs**: Would have reduced source duplication, but breaks
  self-containment and the portable mirror; replaced by in-place rewriting.

## Pending Decisions

_All decisions resolved as of 2026-06-04 via /wb:resolve_questions._

| Decision Needed | Blocks | Notes |
|-----------------|--------|-------|
| Which command to pilot first for the rewrite-quality validation gate | Rollout to remaining commands | Recommend `create_research.md` (canonical structure; near-mirror of product variant; exercises barriers, Task() blocks, templates, and beads in one file). **Resolved 2026-06-02**: Pilot `create_research.md` first. |
| Acceptance bar for "structurally indistinguishable" output | Sign-off on the rewrite class | Propose: same section headings, same frontmatter fields, same barrier count in the *generated* doc. **Resolved 2026-06-02**: Adopt the objective bar — same section headings + same frontmatter fields + same barrier count in the generated doc. |
| Output-discipline rule: **global in `CLAUDE.md`** (higher ROI, one location, cached) vs **per-command directive** (in-scope, lower blast radius) | Where the narration-discipline directive lives | Global `CLAUDE.md` requires a **scope expansion** beyond the locked commands/agents/skills boundary; per-command stays in scope. Default to per-command unless scope expansion is approved. **Resolved 2026-06-04**: Option C — **both**. Ship the per-command directive as the in-scope baseline AND recommend a global narration-discipline rule. Because the plugin cannot install into users' own configs, the global rule is delivered as **README setup instructions** users opt into (their `~/.claude/CLAUDE.md` or project `CLAUDE.md`), not shipped enabled. Scope expansion approved for: (a) the repo's own root `CLAUDE.md`, and (b) README setup docs — both documentation/opt-in, no forced plugin-wide behavior change. |
| Whether to adopt a lower effort setting for mechanical commands as a complementary lever | Operational usage guidance (not a prompt change) | Blocked on verifying the 4.8-low/4.7-high claim against the model card and confirming frontmatter support; until then, treat effort as a session-level knob. **Resolved 2026-06-04**: Option B — **pursue**. Action item: (1) verify the "Opus 4.8 low ≈ 4.7 high / cleaner tokens" claim against the official Opus 4.8 model card; (2) confirm whether Claude Code command frontmatter supports an effort hint. Promote effort-tiering to an in-scope lever only if BOTH hold; otherwise keep as a session-level operational knob. **Verified 2026-06-24**: claim holds directionally (4.8 beats prior Opus at every effort level; low effort saves 2–3× tokens) BUT frontmatter has no `effort:` field — so NOT promoted to a prompt change. Effort stays a **session-level operational knob**: run mechanical commands (create_project, update_status, validate_*) at lower effort; reserve high/xhigh for research/design/implementation. |

These are sequencing/validation decisions for `/wb:create_execution`, not blockers on the design approach itself.

## References

- Research: [research.md](research.md)
- Compaction precedent: `skills/tdd-discipline/SKILL.md:12-17`,
  `skills/verification-before-completion/SKILL.md:12-19`,
  `skills/research-validation/SKILL.md:15-20`
- Redundant recaps (removal targets): `commands/create_research.md:416-420`,
  `commands/create_design.md:468-475`, `commands/create_execution.md:773-779`
- Near-mirror pair (in-place rewrite): `commands/create_research.md`,
  `commands/create_product_research.md`; portable mirror
  `docs/product-research-claude-desktop.md`
- beads-stealth blocks (extraction source): `commands/create_execution.md:449-460`,
  `commands/implement_tasks.md:154-163`, `commands/create_handoff.md:118-134`,
  `commands/resume_handoff.md:73-87`, `commands/implement_coordinated.md:155-164`,
  `commands/update_status.md:51-57`, `commands/validate_project.md:135-157`
- Locked constraints: research Open Questions OPUS-1 … OPUS-5 (all resolved)
- Output / completion-template targets: research §12 (Confirm Completion
  summary template, ~800 tokens across 4 `create_*` commands)
- Effort-setting / model-card claim: **to verify** against the official Opus
  4.8 model card before relying on it (currently Unverified — see Assumptions)
