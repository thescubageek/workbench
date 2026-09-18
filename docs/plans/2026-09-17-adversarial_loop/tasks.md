---
project: adversarial_loop
ticket: null
created: 2026-09-17
status: in-progress
last_updated: 2026-09-18
assignee: scraig
current_phase: 3
total_tasks: 29
completed_tasks: 15
task_tracking: markdown-checkboxes
depends_on: [research.md, design.md]
git_commit: 02e23bd
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
| Phase 1: Tracer bullet — prove the wrapper shape | ✅ Complete | 4/4 | 100% |
| Phase 2: Reference doc and `wb:adversarial-review` | ✅ Complete | 7/7 | 100% |
| Phase 3: `wb:reply-to-claude` and `wb:adversarial-loop` | 🔄 In Progress | 0/3 | 0% |
| Phase 4: Repoint the ecosystem | ⏸️ Not Started | 0/5 | 0% |
| Phase 5: Release | ⏸️ Not Started | 0/6 | 0% |

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

- [x] Research complete (`research.md` status `complete`)
- [x] Design approved (`design.md` status `approved`)
- [x] `git`, and a `claude` binary whose `Skill` tool can reach `code-review`

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

- [x] The fixture's two branches differ as intended: `git -C /tmp/wb-adv-probe diff --stat main trivial`
      and `... main risky` both return a diff, and `risky` is ≤20 changed lines
- [x] `thoughts/2026-09-17-wrapper-shape-probe.md` exists, contains a `cwd:` line, and its
      pre-registration section is dated earlier than its results section
- [x] `test ! -e /tmp/wb-adv-probe` after P1-T4

#### Manual Verification

- [x] A human has read the probe document and agrees the shape holds
- [x] The tier chosen for `risky` is higher than for `trivial`, and the axis that drove it is named
- [x] The security lens fired on `risky` and did not fire on `trivial`
- [x] Findings from both legs appear in one deduped, verified report

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

- [x] **(derivable)** Every Phase 1 checkbox is `[x]`
- [x] **(derivable)** All automated verification passing
- [x] **(attestation)** Manual verification confirmed by human — confirmed 2026-09-17
- [x] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
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

- [x] Phase 1 complete and verified
- [x] Phase 1 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway.*
- [x] The probe verdict says the wrapper shape holds

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

- [x] **P2-T1** — Write `plugin/docs/reference/code-review-integration.md`: published effort
      semantics; the `ReportFindings` field contract including `verdict` and the
      `fixed`/`skipped`/`no_change_needed` lifecycle; the `/verify` chaining relationship and its
      pre-ship exemptions; the model-family observation demoted to prompt-cell selection with its
      `Check it` command and the note that it did not predict observed breadth. Follow
      `branch-naming.md`'s skeleton. (~26 calls) (completed 2026-09-18 00:09)

#### Supporting files before the SKILL.md that directs reads into them

- [x] **P2-T2** — Write `plugin/skills/adversarial-review/lenses.md`: the lens table keyed on what
      the diff touches, generalised off all Rails/reef vocabulary; the four mandatory triggers
      (auth/permissions/params/uploads/external-calls/PII → security; prompt text, skill files,
      agent definitions → AI-systems; migrations/backfills → data; changed signature with callers
      outside the diff → cross-file tracer); the rule that a mandatory lens pulls the tier up; the
      six-lens runaway guard and the requirement to name any dropped lens and why. (~24 calls)
      (completed 2026-09-18 00:24)
- [x] **P2-T3** — Write `plugin/skills/adversarial-review/prompts.md`: verbatim prompts for the
      lens agents and the low-tier stance agent (enclosing function, deleted invariants, blast
      radius), each carrying the evidence contract — a finding without a concrete failure scenario
      is dropped. Model per lens from the four-value enum only (`haiku`/`sonnet`/`opus`/`fable`),
      per A6. (~26 calls) (completed 2026-09-18 00:27)
- [x] **P2-T4** — Write `plugin/skills/adversarial-review/templates.md`: the `ReportFindings` call
      shape; the one-line-per-finding restatement; the markdown fallback for sessions without the
      tool; the "Checked and clear" coverage list and why carrying it in the restatement does not
      violate the tool's do-not-duplicate rule; the reconnaissance summary shape so the sizing can
      be argued with. (~22 calls) (completed 2026-09-18 00:51)
- [x] **P2-T5** — Write `plugin/skills/adversarial-review/reference.md`: verify-only mode for
      adjudicating another session's findings; the five reviewer dispositions (valid / wrong /
      over-fitted / real-but-disproportionate / pre-existing); the proportionality gate; the
      coverage check; and "'clean' describes a tree state, not the branch". (~24 calls) (completed 2026-09-18 00:54)

#### Then the skill body

- [x] **P2-T6** — Write `plugin/skills/adversarial-review/SKILL.md`: frontmatter with the PD5
      argument surface and narrow adversarial triggers; the supporting-file manifest including the
      link to `code-review-integration.md`; the hard-stop paragraph; the reconnaissance step over
      the six axes taking the max; the `REVIEW.md` precedence chain read from the base ref with
      add-never-suppress; the two-leg spawn in one message; the barrier that governs waiting; the
      pooled dedupe using the built-in's own predicate; the three-state verify over the pooled set;
      and the model-help gate line. (~42 calls) (completed 2026-09-18 17:20)

#### Static checks for this phase's invariants

- [x] **P2-T7** — Add the phase's invariant checks to this plan's Success Criteria as runnable
      commands, and run them: every `../../docs/reference/*.md` link in the new skill resolves; no
      Ruby/Rails/RSpec/Docker/Postgres/Redis vocabulary in any new file; the skill body says
      `git show` for the `REVIEW.md` read rather than `cat`. (~16 calls) (completed 2026-09-18 17:25)

### Success Criteria

#### Automated Verification

Each check below prints what it found rather than counting it, and each absence check was run
against a planted failure so it is known to fire. Commands are shell-agnostic — the earlier
`while read ... [ -e ]` form parse-errors under zsh, which would have made the link check silently
unrunnable rather than failing.

- [x] Lint clean: `./plugin/scripts/lint plugin/docs/reference/code-review-integration.md plugin/skills/adversarial-review/*.md`
- [x] Guard check clean: `./plugin/scripts/check-guards` → exit 0
- [x] Every link in the skill resolves — prints `MISS` per broken link, nothing when clean:

```bash
python3 -c "
import re,os,sys
b='plugin/skills/adversarial-review'
ls=sorted(set(re.findall(r'\]\(([^)]+\.md)\)', open(b+'/SKILL.md').read())))
bad=[l for l in ls if not os.path.exists(os.path.normpath(os.path.join(b,l)))]
print('\n'.join('MISS '+x for x in bad))"
```

- [x] No stack or employer vocabulary — prints the offending lines, nothing when clean:
      `grep -rniE 'ruby|rails|rspec|turbo|stimulus|postgres|redis|docker|rubocop|bundle exec|hellobrightline|reef|rbenv|staffer' plugin/skills/adversarial-review/ plugin/docs/reference/code-review-integration.md`
- [x] The base-ref read is the stated mechanism — prints the `git show` line, not a count:
      `grep -n 'git show' plugin/skills/adversarial-review/SKILL.md`
- [x] Mandatory lenses are marked in the table — prints one row per mandatory lens:
      `grep -n 'see \*Mandatory\*' plugin/skills/adversarial-review/lenses.md`
- [x] Frontmatter is well formed and singular — prints one line per key, and zero orphaned
      block-list entries:
      `awk '/^---$/{c++; next} c==1{print} c==2{exit}' plugin/skills/adversarial-review/SKILL.md`
- [x] The plugin loads and enumerates the new skill:
      `claude --plugin-dir plugin plugin details wb` → `adversarial-review` appears in the skill inventory

#### Manual Verification

- [x] A human has read `code-review-integration.md` and agrees it states only what wb may rely on
- [x] The lens table reads as stack-agnostic — a Python or Go repo would select sensibly from it
- [x] `/wb:adversarial-review` loads in a `--plugin-dir plugin` session and its supporting files
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

- [x] **(derivable)** Every Phase 2 checkbox is `[x]`
- [x] **(derivable)** All automated verification passing
- [x] **(attestation)** Manual verification confirmed by human — confirmed 2026-09-18
- [x] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
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

- [x] Phase 2 complete and verified
- [x] Phase 2 manual testing confirmed — *attestation; see the checkpoint block.*
- [x] `wb:adversarial-review` loads and is invocable by name

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
- [ ] **P3-T3** — Write `plugin/skills/adversarial-loop/reference.md`: **link** to
      `adversarial-review/reference.md` for the adjudication pass rather than restating it —
      P2-T5 wrote it as the authority, and two statements of the five dispositions would drift; the coverage question ("what did nothing look at?") with its standing
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
      *The B1 grep defect originally bundled here was pulled forward and fixed on 2026-09-17; this
      task is now the repointing only.* (~11 calls)
- [ ] **P4-T3** — Repoint `plugin/skills/model-help/SKILL.md:160`'s calibration anchor off
      `review-reef`, and add gate-mode rows for the review and PR-loop phases to the table at
      `:94-103`, matching its four columns exactly (`wb phase`, `Main-session baseline`, `Why`,
      `Cheap work → sub-agents`). (~17 calls)
*Order note: P4-T5 sits before P4-T4 deliberately. Tasks run in document order, and the
dangling-reference sweep has to be the last thing in the phase or it will not cover the
documentation change that precedes it. The IDs are left as filed rather than renumbered, since
P4-T5 is already cited by commit.*

- [ ] **P4-T5** — Re-sync `plugin/skills/help/SKILL.md` and `README.md` so both cover
      `adversarial-loop` and `reply-to-claude` once Phase 3 has created them. The audit and the
      backfill for everything *else* was done 2026-09-18 — help was missing nine user-invocable
      skills, eight of them predating this work, and neither file mentioned the shipped reference
      docs. Run the same coverage check that found it: every user-invocable skill appears in help,
      every skill appears in README, and **nothing names a skill that does not exist**. (~12 calls)
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
- [ ] Docs cover every shipped skill and name no absent one — prints the gaps, nothing when clean:

```bash
python3 -c "
import os,glob
h=open('plugin/skills/help/SKILL.md').read(); r=open('README.md').read()
for f in sorted(glob.glob('plugin/skills/*/SKILL.md')):
    n=os.path.basename(os.path.dirname(f)); fm=open(f).read().split('---')[1]
    if 'disable-model-invocation: true' in fm: continue
    if 'user-invocable: false' not in fm and n not in h: print('MISSING from help:',n)
    if n not in r: print('MISSING from README:',n)
for ghost in ('review-reef','review-strict','pr-feedback'):
    if ghost in h or ghost in r: print('NAMES ABSENT SKILL:',ghost)"
```

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

- [ ] **P5-T6** — Ship `plugin/scripts/count` with a contract test, and repoint the counting
      idioms that remain in shipped skills at it. The wrapper returns a count on success and a
      *distinguishable* failure otherwise, so the correct path is shorter than the unguarded one —
      the same reason `scripts/quiet` exists. Contract test follows `scripts/test-quiet`: a real
      count, a zero-match count, a missing file, and an unreadable file must each be
      distinguishable. **This is the third of three responses to the silent-measurement class;
      items 1 and 2 shipped 2026-09-18 and this one must land before the effort is called
      complete.** (~20 calls)

### Success Criteria

#### Automated Verification

- [ ] Manifest versions agree:
      `diff <(grep -o '"version": "[^"]*"' plugin/.claude-plugin/plugin.json | head -1) <(grep -o '"version": "[^"]*"' .claude-plugin/marketplace.json | head -1)` → empty
- [ ] Lint clean repo-wide: `./plugin/scripts/lint --all`
- [ ] Release check clean: `claude plugin tag --dry-run plugin/`
- [ ] No stack or employer vocabulary anywhere in shipped files:
      `grep -rniE 'ruby|rails|rspec|postgres|redis|docker|rubocop|bundle exec|hellobrightline' plugin/` → no output
- [ ] Every reference link in every skill resolves — same shell-agnostic form P2-T7 settled on,
      generalised across `plugin/skills/`; prints `MISS` per broken link:

```bash
python3 -c "
import re,os,glob
bad=[]
for f in glob.glob('plugin/skills/*/SKILL.md'):
    b=os.path.dirname(f)
    for l in re.findall(r'\]\(([^)]+\.md)\)', open(f).read()):
        t=os.path.normpath(os.path.join(b,l))
        if not os.path.exists(t): bad.append(f+' -> '+l)
print('\n'.join('MISS '+x for x in bad))"
```

- [ ] `CHANGELOG.md` has a `## [2.2.0]` heading
- [ ] Guard check clean: `./plugin/scripts/check-guards` → exit 0
- [ ] `./plugin/scripts/test-count` passes, and `scripts/count` distinguishes a zero count from a
      failed one

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

- **[2026-09-18] Process hazard: the lint hook fixes files after you check them.** The
  PostToolUse hook runs `lint --fix` on every markdown write, so the sequence write → check →
  commit can capture the *pre-fix* state while the fix lands in the working tree afterwards. That
  happened once here: `lint --all` reported FAIL, the commit went in, and the hook's correction
  was left uncommitted. Verify the **committed** content, not the working tree —
  `git show HEAD:<path> > /tmp/x && ./plugin/scripts/lint /tmp/x` — which is the same
  confirm-the-measurement discipline applied to what git actually holds.
- **[2026-09-18] P2-T6 declared `Skill` in `allowed-tools`, with no precedent.** Ten shipped
  skills declare `Task`; none had ever declared `Skill`, and this skill invokes a built-in through
  it. Measured rather than assumed: `claude --plugin-dir plugin plugin details wb` loads clean and
  enumerates 37 skills including `adversarial-review`, so the value is at worst inert. Cost is
  ~180 always-on / ~3.3k on-invoke — below `create_research` (~5.3k) and `implement` (~8.1k),
  which is the right order for a skill that pushes its work to forked agents.
- **[2026-09-18] Silent-measurement class: three responses, two shipped.** The prose rule
  (FALSIFY) demonstrably did not prevent recurrence — instance four happened inside the
  verification of the fix for instance three. So the response moved from stating the rule to
  removing the need to remember it. **(1) `plugin/scripts/check-guards`** greps shipped shell and
  fenced `bash` blocks for the three shapes whose failure reads as clean, and found two real
  instances on its first run — `scripts/quiet:34`, in the script whose whole job is honest
  reporting. **(2) `verification-before-completion` now prefers listing to counting**, because all
  four instances were counts and a count destroys the signal that would have caught it.
  **(3) `scripts/count` is P5-T6**, still owed.
  The check itself had the same bug it hunts: `FOUND=1` set inside a pipeline subshell never
  reached the parent, so it found a defect and reported clean. `plugin/scripts/lint` already
  carries a comment about that exact trap. Third occurrence in this repository.
  A deliberate counter-example in a `bash` fence also tripped it; resolved by a convention —
  counter-examples go in a `text` fence — rather than a suppression marker, since a marker can
  silence a real finding and a fence language cannot.
- **[2026-09-18] L1 closed — the last unfixed defect from the P1-T3 probe.** An indented `##`
  heading is invisible to *both* readers: `wb-prime.sh` greps `^##` and `validate_project`
  filters `startsWith('## ')`, so the hook silently misreads the file and the validator reports it
  clean. The defect hid from its own checker. Fixed with an indented-heading ERROR in
  `validation-rules.md` placed *before* the extraction, and a `Check it` in `journal-entries.md`;
  both falsified against a planted indented entry and a clean file. The known false-positive case
  — an indented fenced example — is recorded in the rule rather than solved, since a fence-aware
  check would be more precise and more able to be wrong.
  An audit of every defect raised this session confirmed the rest were already fixed. B3
  (`research-validation` gaining `Edit`) stands as a decision, not a defect: reverting it would
  restore a skill that cannot perform its own documented Step 4.
- **[2026-09-18] P2-T3 placed the verifier prompt in `prompts.md`, which the task did not assign.**
  The task names the lens and stance prompts; P2-T6 assigns SKILL.md the verify *step*. The prompt
  itself had no assigned home, and a verbatim agent prompt inline in SKILL.md would break the
  pattern every other fan-out skill follows. Placed in `prompts.md` with a note in the file saying
  why.
- **[2026-09-18] Process note: three Implementation Notes were lost to a shared failure.** A
  multi-step edit script whose early `assert` fails kills every later step in the same script, and
  the surrounding shell still commits. Twice the work landed while its record did not. The fix is
  to verify each write landed rather than trusting the script ran — the same "confirm the
  measurement ran" rule this session keeps rediscovering, applied to editing rather than checking.
- **[2026-09-18] Root cause of the recurring silent-check class, fixed at the user's request.**
  Three instances this session (probe blast-radius grep, `daily-digest`'s collector, this plan's
  own reference doc) were all patched individually before anyone asked why they kept happening.
  The cause: the principle — *a check that cannot fail is not evidence* — existed in four places,
  none of them shipped and runtime-read (`.claude/wb/knowledge.md`, the maintainer-only skills
  guide, and two plans' prose). The one shipped skill whose whole job is evidence-before-claims,
  `verification-before-completion`, did not contain it, and its gate (IDENTIFY → RUN → READ →
  VERIFY) **passed all three failures**: a command was identified, run, its output read, and the
  output said clean. Fixed by adding a **FALSIFY** step to that gate, with the mechanism table,
  the see-it-fail-once instruction, and the authoring red flags; pointed at from the two places
  checks are written and run (`create_tasks`' template, `validate_execution` Step 3). Stated once,
  referenced twice, no fourth copy. Verified retrospectively against all three instances, and the
  first was reproduced precisely — under zsh it reports 0 callers where 1 exists, while bash hides
  the defect entirely, which is now recorded as its own red flag.
- **[2026-09-18] P2-T1 — the reference doc's own `Check it` command failed on first write.**
  It matched `Phase 2 . (Verify|Dedup)`, but `strings` emits the em-dash as the literal
  seven-character sequence `\u2014`, so `.` matched nothing and the check silently returned
  clean. Rewritten to match on the distinctive headings' tails, which is encoding-independent,
  and verified to both return the expected four lines and go silent when the trigger line is
  absent. The failure is recorded in the doc itself so the next person does not rediscover it.
- **[2026-09-17] Out-of-plan fix, at the user's request: B1 and the silent-measurement class.**
  Both in `daily-digest/sources.md`. B1 is described in Blockers above. The second is the class
  the P1-T3 probe found in itself: `grep -cE` on a possibly-absent file, with an unguarded glob,
  so an unmatched glob produced an empty count and `[ "$left" -gt 0 ]` errored instead of
  reporting — exit 2 with two grep errors. `wb-prime.sh:55-63` already documents this exact trap
  and guards against it; this collector did not. Now guarded the same way, verified under bash
  semantics against an unmatched glob (old: exit 2 with errors; new: exit 0) and against a plan
  with zero completed tasks (still reports `0 done, 1 left` — no regression).
  An audit for the probe's *own* variant — an unquoted `--include` glob — found no instances in
  shipped code.
- **[2026-09-17] Out-of-plan fix, at the user's request: the two causes behind the journal lint
  failure.** Symptom was MD022/MD032 on every entry this session added. Cause 1 —
  `journal-entries.md` gave the entry shape but never said an entry ends with a blank line before
  the next heading, so following the contract exactly produced lint failures, and the PostToolUse
  hook then rewrote the file underneath the session. Cause 2 — "close in place" was stated but
  unenforceable: `validate_project`'s `openCount > 1` cannot catch a *single* stale open entry,
  which is what a second-heading close leaves, and this plan's own journal contained one.
  Both fixed: the blank-line rule is now in the contract, and the count check is replaced by a
  position check (only the newest entry may be `(open)`), verified against a planted failure and
  against a legitimate single open entry. B2 from the probe was fixed in the same block, since
  the rewrite covered those lines.
- **[2026-09-17] B1 — RESOLVED, pulled forward from P4-T2 at the user's request.**
  `plugin/skills/daily-digest/sources.md` reported every untouched plan as having interrupted
  work, because its open-entry grep had no placeholder filter. Fixed by reading the *newest* real
  entry per journal rather than matching any `(open)` line anywhere — which also stops a stale
  open entry (a bookkeeping error) being reported as work in flight. Verified against three
  planted journals: only the genuinely interrupted one now reports, where the old code reported
  all three.

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
