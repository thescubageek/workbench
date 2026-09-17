---
project: adversarial_loop
ticket: null
created: 2026-09-17
status: not-started
last_updated: 2026-09-17
assignee: scraig
current_phase: 1
total_tasks: 27
completed_tasks: 4
task_tracking: markdown-checkboxes
depends_on: [research.md, design.md]
git_commit: a1793aa
git_branch: adversarial-loop-skill-research
repository: thescubageek/workbench
tags: [tasks, tracking, adversarial_loop]
---

# Execution Plan: adversarial_loop

## Overview

Ship `wb:adversarial-review`, `wb:adversarial-loop` and `wb:reply-to-claude` as plugin skills
that wrap Claude Code's built-in review machinery rather than re-implementing it, and repoint the
three shipped files that already route to a review-skill family the plugin never had.

**Design Approach**: Wrapper + lens injection, scaled by reconnaissance.
**Target State**: an adversarial review runs in any repository — no `REVIEW.md`, no personal
skills, no plan directory — sizing its fleet from what the diff *touches*, always running the
mandatory lenses, and reporting verified findings that each carry a concrete failure scenario.

## Task tracking

**Checkbox state in this file is the source of truth.** There is no external tracker. Flip
`[ ]` → `[x]` as work completes and append `(completed YYYY-MM-DD HH:MM)`. The frontmatter
counters are a derived cache with exactly one writer — `/wb:update_status` — and are never
hand-edited. Git is the durable record: one task, one commit.

This plan directory was promoted in commit `a1793aa`. Promotion is a **one-time** act over the
files that existed at that moment — `journal.md` and `thoughts/` were included, but anything
added later needs `git add -f` of its own, and `git status` never lists ignored files:

```bash
git ls-files --others --ignored --exclude-standard docs/plans/2026-09-17-adversarial_loop/
```

Every task carries a stable local ID (`P2-T7`). **The ID's shape is a contract**: it must match
`[A-Z0-9-]*[0-9][A-Z0-9-]*` — at least one digit — and be bold, immediately after the checkbox.
An ID that does not match makes the task invisible to counting, so `/wb:update_status` writes
wrong totals and the session-start bootstrap reports the wrong position, with nothing erroring.

```bash
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # completed
grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # remaining
```

## Implementation Strategy

### Phase Rationale

The order is set by three dependency findings and one unverified premise.

- **The reference doc must exist before the skill that links it.** Every shipped skill carries
  the hard-stop rule — "if a directed read fails, stop — do not continue from memory" — so a
  skill linking a doc that is not there does not degrade, it halts. Phase 2 writes the doc first.
- **`adversarial-review` must exist before `adversarial-loop`**, which sequences it by name.
  Shipping the loop first would freshly introduce the exact defect this plan exists to remove:
  `daily-digest/SKILL.md:204,278` and `model-help/SKILL.md:160` already point at a review-skill
  family that was never built.
- **The repointing edits must come after the new skills are named and exist**, or they create a
  second dangling reference.
- **The version bump lands last, on a clean tree.** `.claude/wb/knowledge.md` records that
  `claude plugin tag` refuses a dirty tree, so the release check runs *after* the bump commit.
  Both manifests move together or the release is invalid.

Parallel work is available but not exploited by the ordering: `reply-to-claude`, the reference
doc and the three repointing edits are mutually independent. They are sequenced anyway so each
lands in its own commit against a known-good tree.

**Phase 1 is a tracer bullet, and everything after it is contingent.** A1 proved the built-in is
invocable and returns findings; it did **not** prove the whole wrapper shape — recon sizing the
fleet, two legs spawning together, two finding sets merging into one verified report. If that
shape does not hold, Phases 2–5 are wasted work, and it is cheap to learn now.

### Testing Strategy

This plugin ships markdown prompts, so "testing" splits in two and the split is load-bearing.

**Static checks** are greps and resolver loops, modelled on the ones this repo already runs —
`docs/claude-code-skills-guide.md:426-435`'s stub-manifest resolver, and the vocabulary grep
(`grep -c 'think deeply' CLAUDE.md` → 0) from the previous plan. They prove an instruction *says*
the right thing.

**Behavioural checks** need the skill actually run, in a fixture repository, with the working
directory recorded. The previous plan's Phase 0 probe reported `NO PROMPT` truthfully and
concluded wrongly because its cwd was never written down — "a probe that cannot fail is not
evidence." Every behavioural task here records the cwd and the verbatim output.

No static check can establish that a mandatory lens actually fired, that fleet size differed
between two diffs, or that a `REVIEW.md` failed to suppress a lens. Those are Phase 1 and Phase 5
tasks, not greps.

## Progress Overview

| Phase | Status | Tasks | Progress |
|-------|--------|-------|----------|
| Phase 0: Planning | ✅ Complete | 4/4 | 100% |
| Phase 1: Tracer bullet — prove the wrapper shape | ⏸️ Not Started | 0/4 | 0% |
| Phase 2: Reference doc and `wb:adversarial-review` | ⏸️ Not Started | 0/7 | 0% |
| Phase 3: `wb:reply-to-claude` and `wb:adversarial-loop` | ⏸️ Not Started | 0/3 | 0% |
| Phase 4: Repoint the ecosystem | ⏸️ Not Started | 0/4 | 0% |
| Phase 5: Release | ⏸️ Not Started | 0/5 | 0% |

Counts come from the checkboxes below and are reconciled by `/wb:update_status`.

---

## Phase 0: Planning

### Objective

Produce validated research, an approved design, and this execution plan.

### Tasks

- [x] **P0-T1** — Create project structure (completed 2026-09-17 17:51)
- [x] **P0-T2** — Complete research using `/wb:create_research` (completed 2026-09-17 18:00)
- [x] **P0-T3** — Create design document using `/wb:create_design` (completed 2026-09-17 21:31)
- [x] **P0-T4** — Generate execution plan using `/wb:create_tasks` (completed 2026-09-17 23:21)

---

## Phase 1: Tracer bullet — prove the wrapper shape

### Objective

Establish, before any shipped file is written, that the two-leg wrapper shape holds end to end:
reconnaissance sizes the fleet, both legs spawn, and two finding sets merge into one verified
report. Stop the plan here if it does not.

### Why this phase exists

A1 is validated: `Skill(code-review, "low")` returns `forked execution` and findings. That proves
*invocation*. It does not prove the shape the design rests on — that the built-in's findings come
back in a form the wrapper can dedupe and verify against its own lens findings, and that
content-driven sizing actually discriminates between a trivial diff and a risky one.

If the merge is unworkable, the design collapses toward the rejected "thin conductor". If sizing
does not discriminate, the reconnaissance pass is ceremony and the tiering decisions unwind. Both
are cheap to learn now and expensive to learn after five files.

This is a throwaway probe on a scratch path. Nothing under `plugin/` is touched, and the fixture
is deleted at the end of the phase.

### Prerequisites

- [ ] Research complete (`research.md` status `complete`)
- [ ] Design approved (`design.md` status `approved`)
- [ ] `git`, and a `claude` binary whose `Skill` tool can reach `code-review`

### Tasks

- [x] **P1-T1** — Build a throwaway fixture repository at `/tmp/wb-adv-probe/` with an
      `origin/main` baseline and two branches: `trivial` (a docs-only change, no runtime surface)
      and `risky` (a ≤20-line change that narrows a permission check and widens a params
      allowlist — small by line count, high on the reversibility and behavioural-delta axes).
      **Record the working directory in the task's notes**; a probe whose cwd is unrecorded is
      the failure mode the previous plan hit. (~14 calls) (completed 2026-09-17 23:36)
- [x] **P1-T2** — **Pre-register** the probe in `thoughts/2026-09-17-wrapper-shape-probe.md`
      *before running it*: the six-axis rubric, the tier each fixture branch is predicted to get
      and which axis should drive it, the lenses predicted to fire on each, and the explicit
      pass/fail conditions for both halves. Written first so the run cannot be retrofitted — a
      probe whose success conditions are set afterwards is the unfalsifiable kind the previous
      plan hit. (~22 calls) (completed 2026-09-17 23:42)
- [x] **P1-T3** — Run both halves of the probe inline in this session, from a recorded cwd, and
      append verbatim results to the probe document.
      **Half A — does recon discriminate?** Rate the six axes over `/tmp/wb-adv-probe`'s `trivial`
      and `risky` diffs, record the tier and the deciding axis for each, and record which lenses
      fire. No built-in leg: recon is pure analysis of a diff.
      **Half B — do two finding sets merge?** Against *this* repository's own diff, where
      `/code-review` is addressable: take the built-in leg's real output, spawn one wb lens agent
      over the same diff, then dedupe with the built-in's own predicate and run the three-state
      verify over the pooled set. Record whether provenance survived, what deduped, and what the
      verify changed. (~26 calls) (completed 2026-09-17 23:57)
- [x] **P1-T4** — Record the verdict in `thoughts/2026-09-17-wrapper-shape-probe.md`: frontmatter
      with `git_commit`/`git_branch`, the exact commands, the recorded cwd, and verbatim captured
      output — not a paraphrase. State plainly whether the shape holds, and if it does not, which
      design decisions it invalidates. Then delete `/tmp/wb-adv-probe/`. (~15 calls) (completed 2026-09-17 23:58)

### Success Criteria

#### Automated Verification

- [ ] The fixture's two branches differ as intended: `git -C /tmp/wb-adv-probe diff --stat main trivial`
      and `... main risky` both return a diff, and `risky` is ≤20 changed lines
- [ ] `thoughts/2026-09-17-wrapper-shape-probe.md` exists, contains a `cwd:` line, and its
      pre-registration section is dated earlier than its results section
- [ ] `test ! -e /tmp/wb-adv-probe` after P1-T4

#### Manual Verification

- [ ] A human has read the probe document and agrees the shape holds
- [ ] The tier chosen for `risky` is higher than for `trivial`, and the axis that drove it is named
- [ ] The security lens fired on `risky` and did not fire on `trivial`
- [ ] Findings from both legs appear in one deduped, verified report

### Modified Files

Nothing under `plugin/`. This phase writes one plan artifact:

- `thoughts/2026-09-17-wrapper-shape-probe.md` — the verdict, with verbatim evidence

### ⛔ CHECKPOINT: Phase 1 Complete

These are the conditions to meet before the next phase — **not a record of having met them.**
Tick each one as it is actually satisfied.

Each box below is labelled **(derivable)** or **(attestation)**. A derivable condition is one a
tool can establish, and `/wb:implement` ticks those at its Step 8 checkpoint. An attestation
records that a *person* looked, so only a person ticks it, and an unticked attestation beside
finished work means *"done, sign-off pending"* rather than a contradiction.

**Go by the label, never by position** — a positional reading of these boxes has been wrong
before, and following it ticks the human sign-off box. **This block, labels and this sentence
included, is repeated in full at every phase's checkpoint**; a later phase never gets a
shortened one.

- [ ] **(derivable)** Every Phase 1 checkbox is `[x]`
- [ ] **(derivable)** All automated verification passing
- [ ] **(attestation)** Manual verification confirmed by human
- [ ] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

**If the probe failed, stop.** The two-leg design is invalidated and the plan needs re-planning
before any shipped file is written. Every later phase assumes this verdict.

---

## Phase 2: Reference doc and `wb:adversarial-review`

### Objective

Ship the review skill and the one reference doc it reads, with every supporting file in place
before the `SKILL.md` that directs reads into them.

### Prerequisites

- [ ] Phase 1 complete and verified
- [ ] Phase 1 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway.*
- [ ] The probe verdict says the wrapper shape holds

### Changes Required

#### 1. The built-in integration reference

**File**: `plugin/docs/reference/code-review-integration.md` (new)

**Target State** (design.md → Integration Points, and the A4 decision): the single authority on
what the built-in review machinery offers and what wb may rely on. It carries the published
effort semantics (`low`/`medium` precision, `high`→`max` coverage), the `ReportFindings` field
contract, the `/verify` chaining relationship, and — demoted to a dated observation scoped to
prompt-cell selection — the model-family routing table, with a `Check it` command and an explicit
note that it did not predict observed review breadth.

**Pattern Reference**: `plugin/docs/reference/branch-naming.md` — name the authority and the
linking convention, state the rule as a literal template, give trigger conditions, give a
does-not-apply list, then exact one-line report shapes.

#### 2. The review skill

**File**: `plugin/skills/adversarial-review/` (new directory)

**Target State** (design.md → Design Approach): flat four-file layout matching
`plugin/skills/create_research/` — `SKILL.md`, `lenses.md`, `prompts.md`, `templates.md`,
`reference.md`. Frontmatter per PD5: `argument-hint: "[<pr#>|<branch>|<path>] [--effort=<low|medium|high|xhigh|max>]"`.

### Tasks

#### Reference doc first — the skill links it, and a missing directed read halts rather than degrades

- [ ] **P2-T1** — Write `plugin/docs/reference/code-review-integration.md`: published effort
      semantics; the `ReportFindings` field contract including `verdict` and the
      `fixed`/`skipped`/`no_change_needed` lifecycle; the `/verify` chaining relationship and its
      pre-ship exemptions; the model-family observation demoted to prompt-cell selection with its
      `Check it` command and the note that it did not predict observed breadth. Follow
      `branch-naming.md`'s skeleton. (~26 calls)

#### Supporting files before the SKILL.md that directs reads into them

- [ ] **P2-T2** — Write `plugin/skills/adversarial-review/lenses.md`: the lens table keyed on what
      the diff touches, generalised off all Rails/reef vocabulary; the four mandatory triggers
      (auth/permissions/params/uploads/external-calls/PII → security; prompt text, skill files,
      agent definitions → AI-systems; migrations/backfills → data; changed signature with callers
      outside the diff → cross-file tracer); the rule that a mandatory lens pulls the tier up; the
      six-lens runaway guard and the requirement to name any dropped lens and why. (~24 calls)
- [ ] **P2-T3** — Write `plugin/skills/adversarial-review/prompts.md`: verbatim prompts for the
      lens agents and the low-tier stance agent (enclosing function, deleted invariants, blast
      radius), each carrying the evidence contract — a finding without a concrete failure scenario
      is dropped. Model per lens from the four-value enum only (`haiku`/`sonnet`/`opus`/`fable`),
      per A6. (~26 calls)
- [ ] **P2-T4** — Write `plugin/skills/adversarial-review/templates.md`: the `ReportFindings` call
      shape; the one-line-per-finding restatement; the markdown fallback for sessions without the
      tool; the "Checked and clear" coverage list and why carrying it in the restatement does not
      violate the tool's do-not-duplicate rule; the reconnaissance summary shape so the sizing can
      be argued with. (~22 calls)
- [ ] **P2-T5** — Write `plugin/skills/adversarial-review/reference.md`: verify-only mode for
      adjudicating another session's findings; the five reviewer dispositions (valid / wrong /
      over-fitted / real-but-disproportionate / pre-existing); the proportionality gate; the
      coverage check; and "'clean' describes a tree state, not the branch". (~24 calls)

#### Then the skill body

- [ ] **P2-T6** — Write `plugin/skills/adversarial-review/SKILL.md`: frontmatter with the PD5
      argument surface and narrow adversarial triggers; the supporting-file manifest including the
      link to `code-review-integration.md`; the hard-stop paragraph; the reconnaissance step over
      the six axes taking the max; the `REVIEW.md` precedence chain read from the base ref with
      add-never-suppress; the two-leg spawn in one message; the barrier that governs waiting; the
      pooled dedupe using the built-in's own predicate; the three-state verify over the pooled set;
      and the model-help gate line. (~42 calls)

#### Static checks for this phase's invariants

- [ ] **P2-T7** — Add the phase's invariant checks to this plan's Success Criteria as runnable
      commands, and run them: every `../../docs/reference/*.md` link in the new skill resolves; no
      Ruby/Rails/RSpec/Docker/Postgres/Redis vocabulary in any new file; the skill body says
      `git show` for the `REVIEW.md` read rather than `cat`. (~16 calls)

### Success Criteria

#### Automated Verification

- [ ] Lint clean: `./plugin/scripts/lint plugin/docs/reference/code-review-integration.md plugin/skills/adversarial-review/*.md`
- [ ] Every reference link resolves:
      `grep -o '\.\./\.\./docs/reference/[a-z-]*\.md' plugin/skills/adversarial-review/SKILL.md | sort -u | while read p; do [ -e "plugin/${p#../../}" ] || echo "MISS $p"; done` → no output
- [ ] No stack vocabulary ships: `grep -rniE 'ruby|rails|rspec|postgres|redis|docker|rubocop|bundle exec' plugin/skills/adversarial-review/ plugin/docs/reference/code-review-integration.md` → no output
- [ ] Base-ref read is the stated mechanism: `grep -c 'git show' plugin/skills/adversarial-review/SKILL.md` → ≥1
- [ ] Mandatory lenses are stated as non-optional: `grep -ci 'mandatory' plugin/skills/adversarial-review/lenses.md` → ≥4
- [ ] Frontmatter is well formed and singular: `awk '/^---$/{c++} c==1 && /^(name|description|argument-hint|allowed-tools):/' plugin/skills/adversarial-review/SKILL.md` → one line per key, no orphaned block list

#### Manual Verification

- [ ] A human has read `code-review-integration.md` and agrees it states only what wb may rely on
- [ ] The lens table reads as stack-agnostic — a Python or Go repo would select sensibly from it
- [ ] `/wb:adversarial-review` loads in a `--plugin-dir plugin` session and its supporting files
      read without error

### Modified Files

#### New

- `plugin/docs/reference/code-review-integration.md` — the built-in integration authority
- `plugin/skills/adversarial-review/SKILL.md` — the skill body
- `plugin/skills/adversarial-review/lenses.md` — lens table and mandatory triggers
- `plugin/skills/adversarial-review/prompts.md` — verbatim agent prompts
- `plugin/skills/adversarial-review/templates.md` — report shapes
- `plugin/skills/adversarial-review/reference.md` — verify-only mode and adjudication

**Quick check command for this phase**:

```bash
./plugin/scripts/lint plugin/skills/adversarial-review plugin/docs/reference/code-review-integration.md
```

### ⛔ CHECKPOINT: Phase 2 Complete

These are the conditions to meet before the next phase — **not a record of having met them.**
Tick each one as it is actually satisfied.

Each box below is labelled **(derivable)** or **(attestation)**. A derivable condition is one a
tool can establish, and `/wb:implement` ticks those at its Step 8 checkpoint. An attestation
records that a *person* looked, so only a person ticks it, and an unticked attestation beside
finished work means *"done, sign-off pending"* rather than a contradiction.

**Go by the label, never by position** — a positional reading of these boxes has been wrong
before, and following it ticks the human sign-off box. **This block, labels and this sentence
included, is repeated in full at every phase's checkpoint**; a later phase never gets a
shortened one.

- [ ] **(derivable)** Every Phase 2 checkbox is `[x]`
- [ ] **(derivable)** All automated verification passing
- [ ] **(attestation)** Manual verification confirmed by human
- [ ] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

---

## Phase 3: `wb:reply-to-claude` and `wb:adversarial-loop`

### Objective

Ship the loop and the bot-reply skill it names, in that dependency order — the loop sequences
both `adversarial-review` (Phase 2) and `reply-to-claude`, so both must exist first.

### Prerequisites

- [ ] Phase 2 complete and verified
- [ ] Phase 2 manual testing confirmed — *attestation; see the checkpoint block.*
- [ ] `wb:adversarial-review` loads and is invocable by name

### Changes Required

#### 1. The bot-reply skill

**File**: `plugin/skills/reply-to-claude/SKILL.md` (new)

**Current State** (research.md): the personal copy is 54 lines and repo-tied in exactly one place
— `reply-to-claude/SKILL.md:49-50` names `hellobrightline/reef`.

**Target State** (design.md, PD/Q6): repository comes from `gh repo view`; `claude[bot]` is
Anthropic's app login everywhere and stays literal; the reply maps 1:1 to the bot's findings and
states pushback explicitly, naming what was rejected and what was verified.

#### 2. The loop

**File**: `plugin/skills/adversarial-loop/` (new directory)

**Target State** (design.md, Q4 decision): a local core that runs anywhere there is a diff, and
PR phases that engage only if a PR already exists. Hard preconditions at the boundary of whichever
phase engages; never a silent narrower run reported as the same thing. Fix-verification delegates
to the built-in `/verify`. Creating a PR stays out of scope.

### Tasks

- [ ] **P3-T1** — Write `plugin/skills/reply-to-claude/SKILL.md`: derive the repository from
      `gh repo view`; compose an `@claude`-prefixed comment mapping 1:1 to the bot's findings,
      stating explicitly which were rejected, why, and what was verified against real source;
      post with `gh pr comment --body-file` to avoid heredoc mangling. No reef-specific content.
      (~22 calls)
- [ ] **P3-T2** — Write `plugin/skills/adversarial-loop/SKILL.md`: the local core (review →
      adjudicate → fix → `/verify` → re-review until clean) with a reviewable diff as its only
      universal precondition; the PR phases gated on a PR already existing, with `gh`, `Monitor`
      and `claude[bot]` as hard dependencies *where those phases engage*; the stated stop when one
      is missing; "'clean' describes a tree state, not the branch" as the re-review trigger; and
      the explicit non-goal of creating a PR. (~42 calls)
- [ ] **P3-T3** — Write `plugin/skills/adversarial-loop/reference.md`: the reviewer-adjudication
      pass in full; the coverage question ("what did nothing look at?") with its standing
      candidates generalised off reef; the `claude[bot]` mechanics that are harness facts rather
      than repo facts — the login is `claude[bot]` not `claude`, the bot edits its comment in
      place so watch `updated_at`, and the check rollup must be read against the head SHA.
      (~26 calls)

### Success Criteria

#### Automated Verification

- [ ] Lint clean: `./plugin/scripts/lint plugin/skills/reply-to-claude plugin/skills/adversarial-loop`
- [ ] No stack or employer vocabulary:
      `grep -rniE 'ruby|rails|rspec|postgres|redis|docker|rubocop|bundle exec|hellobrightline|reef' plugin/skills/reply-to-claude plugin/skills/adversarial-loop` → no output
- [ ] Cross-skill references resolve:
      `for s in adversarial-review reply-to-claude; do grep -q "$s" plugin/skills/adversarial-loop/SKILL.md && test -d plugin/skills/$s || echo "MISS $s"; done` → no output
- [ ] The loop states its non-goal: `grep -ci 'does not create' plugin/skills/adversarial-loop/SKILL.md` → ≥1
- [ ] `/verify` is the fix-verification path, and no stack probe ships:
      `grep -c '/verify' plugin/skills/adversarial-loop/SKILL.md` → ≥1 and
      `grep -cE 'pg_isready|redis-cli|docker info' plugin/skills/adversarial-loop/SKILL.md` → 0

#### Manual Verification

- [ ] The loop runs its local core to clean in a repository with `gh` unavailable, and says so
- [ ] With a PR present but `claude[bot]` absent, the loop stops with a clear message rather than
      quietly skipping the bot round
- [ ] `reply-to-claude` composes a correct reply in a repository that is not `reef`

### Modified Files

#### New

- `plugin/skills/reply-to-claude/SKILL.md`
- `plugin/skills/adversarial-loop/SKILL.md`
- `plugin/skills/adversarial-loop/reference.md`

### ⛔ CHECKPOINT: Phase 3 Complete

These are the conditions to meet before the next phase — **not a record of having met them.**
Tick each one as it is actually satisfied.

Each box below is labelled **(derivable)** or **(attestation)**. A derivable condition is one a
tool can establish, and `/wb:implement` ticks those at its Step 8 checkpoint. An attestation
records that a *person* looked, so only a person ticks it, and an unticked attestation beside
finished work means *"done, sign-off pending"* rather than a contradiction.

**Go by the label, never by position** — a positional reading of these boxes has been wrong
before, and following it ticks the human sign-off box. **This block, labels and this sentence
included, is repeated in full at every phase's checkpoint**; a later phase never gets a
shortened one.

- [ ] **(derivable)** Every Phase 3 checkbox is `[x]`
- [ ] **(derivable)** All automated verification passing
- [ ] **(attestation)** Manual verification confirmed by human
- [ ] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

---

## Phase 4: Repoint the ecosystem

### Objective

Make every existing reference point at a skill the plugin actually ships, and add the gate rows
that give a review phase a model baseline.

### Prerequisites

- [ ] Phase 3 complete and verified
- [ ] Phase 3 manual testing confirmed — *attestation; see the checkpoint block.*
- [ ] All three new skill directories exist, so the repointed names resolve

### Tasks

- [ ] **P4-T1** — Add the hand-off line to `plugin/skills/review-prep/SKILL.md`: it keeps its
      interactive triggers and gains one line pointing at `adversarial-review` for batch
      bug-hunting. The file has no integration section, so this is a new line rather than an edit
      to an existing bucket. (~9 calls)
- [ ] **P4-T2** — Repoint `plugin/skills/daily-digest/SKILL.md:204` (the Today-item entry-point
      bullet) and `:278` (the review-skills bullet in "Integration with the wb ecosystem") from
      `pr-feedback` / `review` / `review-reef` / `review-strict` to the skills that now exist.
      (~13 calls)
- [ ] **P4-T3** — Repoint `plugin/skills/model-help/SKILL.md:160`'s calibration anchor off
      `review-reef`, and add gate-mode rows for the review and PR-loop phases to the table at
      `:94-103`, matching its four columns exactly (`wb phase`, `Main-session baseline`, `Why`,
      `Cheap work → sub-agents`). (~17 calls)
- [ ] **P4-T4** — Run a dangling-reference sweep across the whole plugin and fix anything it
      finds: no shipped file may name a skill directory that does not exist. (~12 calls)

### Success Criteria

#### Automated Verification

- [ ] No shipped file references a non-existent review skill:
      `grep -rnoE '\b(review-reef|review-strict|review-terse|review-security|pr-feedback)\b' plugin/` → no output
- [ ] Every backticked `wb:`-style skill name in the edited files resolves to a directory:
      `grep -rhoE '`(adversarial-review|adversarial-loop|reply-to-claude)`' plugin/skills/daily-digest plugin/skills/model-help plugin/skills/review-prep | tr -d '`' | sort -u | while read s; do test -d "plugin/skills/$s" || echo "MISS $s"; done` → no output
- [ ] `model-help`'s gate table gained rows: `grep -c '^|`adversarial' plugin/skills/model-help/SKILL.md` → ≥1
- [ ] Lint clean: `./plugin/scripts/lint plugin/skills/review-prep plugin/skills/daily-digest plugin/skills/model-help`

#### Manual Verification

- [ ] `daily-digest`'s Needs-review bucket now routes somewhere that exists
- [ ] The new `model-help` rows read consistently with the existing six

### Modified Files

- `plugin/skills/review-prep/SKILL.md` — hand-off line
- `plugin/skills/daily-digest/SKILL.md` — two repointed references
- `plugin/skills/model-help/SKILL.md` — calibration anchor and gate-mode rows

### ⛔ CHECKPOINT: Phase 4 Complete

These are the conditions to meet before the next phase — **not a record of having met them.**
Tick each one as it is actually satisfied.

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

## Phase 5: Release

### Objective

Ship `2.2.0`, verify it behaves in a session that is not this one, and only then remove the
personal copies the port was made from.

### Prerequisites

- [ ] Phase 4 complete and verified
- [ ] Phase 4 manual testing confirmed — *attestation; see the checkpoint block.*
- [ ] Working tree clean — `claude plugin tag` refuses a dirty tree without `--force`

### Tasks

- [ ] **P5-T1** — Write the `## [2.2.0]` entry in `CHANGELOG.md`: `### Added` for the three skills
      and the reference doc, `### Fixed` for the journal-ordering contract and the two malformed
      frontmatter declarations and the two consumer bugs (`validate_project`'s placeholder-counting
      `openCount`, `daily-digest`'s `grep -l 'OPEN'`), `### Changed` for the repointed references,
      and `### Migration` naming the `claude plugin update` step. Match the existing entries'
      bolded-lead-sentence bullet style. (~22 calls)
- [ ] **P5-T2** — Bump `version` to `2.2.0` in **both** `plugin/.claude-plugin/plugin.json` and
      `.claude-plugin/marketplace.json`; they must match. Commit — the release check runs after
      this commit, not before. (~9 calls)
- [ ] **P5-T3** — Run the release checks on the clean tree: `./plugin/scripts/lint --all`,
      `claude plugin tag --dry-run plugin/`, the manifest-version agreement check, the repo-wide
      vocabulary grep, and the reference-link resolver across every skill. Record the output.
      (~17 calls)
- [ ] **P5-T4** — Behavioural smoke session, from a **recorded cwd** that is not inside the plugin
      directory: `claude --plugin-dir plugin` and confirm `wb:adversarial-review` loads, its
      supporting files read, a review runs against a real diff, the reconnaissance summary names
      the tier and the axis that set it, and `wb:adversarial-loop` reaches clean without `gh`.
      Record verbatim output — a probe that cannot fail is not evidence. (~18 calls)
- [ ] **P5-T5** — Only after P5-T4 passes: delete `~/.claude/skills/adversarial-review`,
      `~/.claude/skills/adversarial-loop` and `~/.claude/skills/reply-to-claude`. These are the
      port's source material and are not reproduced in full in this repository, so this task is
      last and is contingent on the smoke session. Confirm with the user before running the
      deletion. (~9 calls) · Depends on: P5-T4

### Success Criteria

#### Automated Verification

- [ ] Manifest versions agree:
      `diff <(grep -o '"version": "[^"]*"' plugin/.claude-plugin/plugin.json | head -1) <(grep -o '"version": "[^"]*"' .claude-plugin/marketplace.json | head -1)` → empty
- [ ] Lint clean repo-wide: `./plugin/scripts/lint --all`
- [ ] Release check clean: `claude plugin tag --dry-run plugin/`
- [ ] No stack or employer vocabulary anywhere in shipped files:
      `grep -rniE 'ruby|rails|rspec|postgres|redis|docker|rubocop|bundle exec|hellobrightline' plugin/` → no output
- [ ] Every reference link in every skill resolves:
      `grep -rhoE '\.\./\.\./docs/reference/[a-z-]*\.md' plugin/skills/ | sort -u | while read p; do [ -e "plugin/${p#../../}" ] || echo "MISS $p"; done` → no output
- [ ] `CHANGELOG.md` has a `## [2.2.0]` heading

#### Manual Verification

- [ ] The smoke session's cwd is recorded and is **not** inside the plugin directory
- [ ] `wb:adversarial-review` produced a report with a reconnaissance summary naming the tier and
      the deciding axis
- [ ] `wb:adversarial-loop` reached clean with no `gh` available and said so
- [ ] The user has confirmed the deletion of the three personal skills
- [ ] **Evaluate the P1-T2 substitution**: the probe ran inline rather than as a loadable skill
      file, and split across two targets. Did that actually establish what Phase 1 needed, or did
      shipping on a partially-evidenced shape cost something? Record the answer in the probe
      document — this is a deliberate methodological call the user asked to have assessed here,
      not a formality

### Modified Files

- `CHANGELOG.md` — the `[2.2.0]` entry
- `plugin/.claude-plugin/plugin.json` — version
- `.claude-plugin/marketplace.json` — version
- `~/.claude/skills/adversarial-review`, `adversarial-loop`, `reply-to-claude` — deleted (outside
  this repository; P5-T5 only)

### ⛔ CHECKPOINT: Phase 5 Complete

These are the conditions to meet before the next phase — **not a record of having met them.**
Tick each one as it is actually satisfied.

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

## Implementation Discoveries

Things to determine during implementation:

- Whether the built-in's findings arrive structured enough to dedupe against the lens leg without
  parsing prose — Phase 1 answers this, and the answer shapes P2-T6's merge section.
- What a reconnaissance summary should actually look like so the sizing is arguable rather than
  asserted — the shape lands in P2-T4 but will want revising after the first real runs.
- Whether the six-lens guard ever bites in practice, or whether content selection keeps the count
  below it on its own.
- Whether `model-help`'s new gate rows want one row for both new skills or one each.
- **The reconnaissance step must confirm its own measurement ran.** P1-T3's blast-radius grep
  errored under zsh glob expansion and the loop still printed `0 call site(s)` — a failed
  measurement reporting a clean result, in the direction of under-review. The real skill's recon
  section needs this guard; it is not a hypothetical.
- **The verify pass must verify clearances, not only findings.** In P1-T3 one leg explicitly
  cleared a finding the other raised, and the clearance was wrong. "Checked and clear" is an
  assertion, not coverage information.
- **Whether running the probe inline was sufficient.** P1-T2 originally specified a loadable
  `SKILL.md` in the fixture; that is not reachable from a session that cannot start a new one in
  the fixture's directory. The inline substitution tests the shape but not skill loading, which
  P5-T4's smoke session covers instead. Assessed explicitly at P5-T4.

Note: Update this section with findings as you implement.

---

## 🚧 Blockers & Notes

### Current Blockers

Recorded here with the task ID they block and the date raised. Remove a blocker when it is
resolved, leaving a dated line saying how.

- **[2026-09-17] B1 — live defect in committed shipped code, blocks nothing but must not ship.**
  `plugin/skills/daily-digest/sources.md:77`'s open-entry grep has no placeholder filter, so it
  matches the journal template's fenced example heading and reports every untouched plan as having
  interrupted work. Found by the built-in leg during P1-T3 and CONFIRMED empirically (3 matches
  against a real journal). **Attaches to P4-T2**, which already edits that file. Fix: add the same
  `grep -vE '\[YYYY|<YYYY|YYYY-MM-DD'` filter the hook uses.

### Implementation Notes

- **The journal-ordering fix and the two frontmatter fixes already landed** in commit `bd9cfd0`,
  before this plan was written. They are not tasks here, but P5-T1 records them in the changelog
  because PD2 ships them in the same `2.2.0` release.
- **`design.md`'s Out of Scope was corrected** on 2026-09-17 to match PD1: removing the personal
  copies is *in* scope, strictly ordered last. The original line predated the decision.
- **[2026-09-17] P1-T1 — fixture built.** `/tmp/wb-adv-probe` (working tree) with
  `/tmp/wb-adv-probe-origin.git` as its bare origin, so `origin/main` resolves for the base-ref
  read. Built from cwd `/tmp/wb-adv-probe`. Branches: `trivial` (docs only, 4 insertions, no
  runtime surface) and `risky` (`app/auth.py`, **6 changed lines**). The risky diff carries two
  real defects by construction — `ALLOWED_PARAMS` widened to admit `owner_id` and `role`
  (mass-assignment privilege escalation via `update_item`), and the `if not user.get("id")`
  guard deleted so a user with no id matches an item with no owner via `None == None`. Python,
  deliberately: the fixture must not be a stack the lens table could special-case.
- **[2026-09-17] P1-T2/P1-T3 deviated from the plan as written, deliberately.** Two constraints
  surfaced at execution. First, a `SKILL.md` written into the fixture's `.claude/skills/` is only
  loadable by a session *started in that directory*, which this session cannot do — so the probe
  runs inline instead, exercising the wrapper logic without a skill file. Second, `/code-review`
  resolves its target from the current repository, so it cannot be pointed at `/tmp/wb-adv-probe`
  at all. The probe therefore splits: the sizing question is answered against the fixture (recon
  is pure analysis and needs no built-in leg), and the merge question against this repository's
  own diff, where the built-in is addressable and two real runs already exist. P1-T2 became a
  pre-registration step so the run cannot be retrofitted. What this does **not** establish is that
  a skill file loads and executes the shape — P5-T4's smoke session covers that, and P5's manual
  verification now carries an explicit assessment of whether this substitution was adequate.

---

## 🔗 Quick Reference

### Key Files

- **Research**: [research.md](research.md) — what exists, including the built-in's internals
- **Design**: [design.md](design.md) — the approved target state and every resolved decision
- **Exploration**: [thoughts/2026-09-17-adversarial-review-architecture.md](thoughts/2026-09-17-adversarial-review-architecture.md)
- **Main entry**: `plugin/skills/adversarial-review/SKILL.md`
- **Shared rule**: `plugin/docs/reference/code-review-integration.md`

### Common Commands

```bash
# Lint changed markdown
./plugin/scripts/lint

# Lint everything
./plugin/scripts/lint --all

# Release check (clean tree only)
claude plugin tag --dry-run plugin/

# Progress (scoped to task lines — criteria checkboxes are not tasks)
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md
```

### Design Decisions Reference

- **Two legs, one report**: built-in `/code-review` for breadth, wb lenses for domain framing
- **Tier is the max of six axes**, never line count; LOC is a within-tier tie-breaker only
- **Mandatory lenses are content-triggered** and pull the tier up with them
- **`REVIEW.md` from the base ref**, add-never-suppress — a security boundary, not a preference
- **Pool, dedupe once, verify once** — provenance is metadata, not standing
- **`/verify` owns fix-verification**; nothing stack-specific ships
- **One release, `2.2.0`**; `3.0.0` is reserved for the alias removals
