---
project: asd-ste100-prose
ticket: null
created: 2026-09-29
status: not-started
last_updated: 2026-09-29
current_phase: 1
total_tasks: 38
completed_tasks: 4
task_tracking: markdown-checkboxes
depends_on: [research.md, design.md]
assignee: scraig
git_commit: 4b32306
git_branch: wb-2.2.0/asd_ste100_prose
repository: thescubageek/workbench
tags: [tasks, tracking, asd-ste100-prose]
---

# Execution Plan: wb Technical English (WBTE) — release 2.2.0

## Overview

This plan implements wb Technical English (WBTE) as design.md specifies. WBTE is a writing
standard for workbench output, adapted from the principles of ASD-STE100 Issue 9.

**Design Approach**: Option A. One shipped reference doc holds the rules. A short rule card
prints at every session start. Every output template links to the reference doc. A
maintainer-only eval harness measures each change and decides which skill-prose changes stay.

**Target State**: generated documents and chat summaries score better than 2.1.1 on the WBTE
metrics. They have no semicolons in prose and no ID used alone in chat. The harness finds no
loss of content, and 3.0.0 can merge the release with small, local conflicts only
(design.md, Success Criteria).

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
git ls-files --others --ignored --exclude-standard docs/plans/2026-09-29-asd-ste100-prose/
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

The order follows three constraints that the analysis agents found.

- **Measure before you change.** The success criteria compare against the 2.1.1 output, so the
  harness and a 2.1.1 baseline must exist before any template or skill changes. The "before"
  tree is always available from commit `4b32306` with `git archive`. Only the harness has to
  exist first.
- **Prove the harness driver first.** The whole measurement plan rests on one unverified
  assumption: that a headless `claude -p` run can drive a wb stage well enough to compare
  output (design.md, A6). A headless run that cannot load a stage does not stop. It improvises
  (`.claude/wb/knowledge.md`, headless entry). Phase 1 is a tracer bullet for this assumption.
  If it fails, Phases 2–5 need a different driver, so nothing else starts before it resolves.
- **The rules come before everything that points to them.** The card, the link lines, the
  metric checker and the template rewrites all depend on the exact text of
  `technical-english.md`, in particular its exempt-token list.

After that, the order is by risk. The card (Phase 3) is the change most likely to have no
effect (A1), so it is measured before the large template work. Template rewrites (Phase 4) are
independent of each other and are grouped by skill. The Objective 2 "lite" rewrite (Phase 5)
comes after Objective 1, because it is secondary and each change must pass the harness gate.
Release work comes last, because the handoff, README and CHANGELOG describe the final state.

Based on dependency analysis:

- The 30 non-shared templates do not include each other. Any group can be rewritten in any
  order once the reference doc is final.
- The dictionary skill (Phase 6) depends only on the reference doc's dictionary section. It can
  run in parallel with Phases 3–5 if a second worker is free.
- Link lines in the 11 shared templates must land before the A2 measurement.
- The version bump goes last. The `git merge-tree` check needs the final tree.

### Testing Strategy

- **Contract tests in bash** for the hook, following `plugin/scripts/test-lint`: a `check`
  helper, `mktemp -d` fixtures with `trap … EXIT`, a control case, a summary line, and the
  exit code from the fail count. The new test is `plugin/scripts/test-prime`. It is written
  before the card (RED first).
- **Static checks in the harness** (python3, maintainer-only): the WBTE metric checker, the
  exempt-token registry, and the link-line and single-authority check. Each one is verified
  against a planted failure, so it is known to fire and not only known to pass (the precedent
  in `CHANGELOG.md`, 2.0.1 and 2.1.1).
- **Headless before/after runs** on one fixed fixture, repeated 3 times per tree, with the model
  pinned. The runs produce generated documents and chat output. The metric checker, the parser
  checks, and an LLM fidelity judge score them. A human reads a sample of each report.
- **Token cost** with `claude --plugin-dir plugin plugin details wb` on the baseline and the
  final tree (the flag goes before the subcommand).
- **Manual verification** covers what no script can show: that the card reaches the model after
  compaction in a repo with no active plans (A3), and that the dictionary skill works on the
  real Issue 9 PDF (A4).

## Progress Overview

| Phase | Status | Tasks | Progress |
|-------|--------|-------|----------|
| Phase 0: Planning | ✅ Complete | 4/4 | 100% |
| Phase 1: Tracer bullet — prove the harness driver | ⏸️ Not Started | 0/3 | 0% |
| Phase 2: Rules authority, harness, and baseline | ⏸️ Not Started | 0/8 | 0% |
| Phase 3: Rule card | ⏸️ Not Started | 0/3 | 0% |
| Phase 4: Objective 1 — link lines and template rewrites | ⏸️ Not Started | 0/9 | 0% |
| Phase 5: Objective 2 — gated "lite" rewrite | ⏸️ Not Started | 0/4 | 0% |
| Phase 6: Dictionary skill | ⏸️ Not Started | 0/2 | 0% |
| Phase 7: Documentation, handoff, and release checks | ⏸️ Not Started | 0/5 | 0% |

Counts come from the checkboxes below and are reconciled by `/wb:update_status`.

---

## Phase 0: Planning

- [x] **P0-T1** — Create project structure (completed 2026-09-29 17:35)
- [x] **P0-T2** — Complete research using `/wb:create_research docs/plans/2026-09-29-asd-ste100-prose` (completed 2026-09-29 17:45)
- [x] **P0-T3** — Create design document using `/wb:create_design docs/plans/2026-09-29-asd-ste100-prose` (completed 2026-09-29 23:55)
- [x] **P0-T4** — Generate execution plan using `/wb:create_tasks docs/plans/2026-09-29-asd-ste100-prose` (completed 2026-09-30 00:02)

---

## Phase 1: Tracer bullet — prove the harness driver

### Objective

Show that one headless `claude -p` run can load and complete a wb stage on a fixture, so that
the harness can compare output before and after a change (design.md, A6).

### Prerequisites

- [ ] Research validated
- [ ] Design approved
- [ ] `claude` CLI and python3 on the maintainer machine (both present: `~/.local/bin/claude`,
      `/opt/homebrew/bin/python3`)

### Changes Required

#### 1. Harness fixture

**File**: `evals/fixture/` (new)

**Current State** (from research.md): no `evals/` directory exists. The repository has no
measurement of stage output (research §3).

**Target State** (from design.md): a small, fixed project that the stages can research, with
facts at known `file:line` locations for the fidelity judge.

**Implementation**:

- `evals/fixture/project/` — a tiny self-contained project: 3 or 4 short source files and a
  README. It has at least 3 facts that a research stage must find, each at a known line.
- `evals/fixture/QUESTION.md` — the fixed research question.
- `evals/fixture/expected.json` — the expected facts, with `file:line` for each.
- `evals/fixture/plan-seed/` — a plan directory made from the `create_project` templates of
  2.1.1. It is stored under this name because the repo `.gitignore` entry `docs/plans/` matches
  at any depth. The driver copies it to `docs/plans/2026-01-01-fixture/` in each run copy.

**Rationale**: `create_research` with no plan directory asks the user to confirm a name. A
headless run cannot answer, so the plan directory must exist before the run.

#### 2. Driver probe

**File**: `docs/plans/2026-09-29-asd-ste100-prose/thoughts/2026-09-30-harness-probe.md` (new)

**Implementation**: a throwaway shell sequence, recorded with its cwd, command, model, duration
and result:

```bash
tmp=$(mktemp -d)
git archive 4b32306 plugin | tar -x -C "$tmp/before"   # after mkdir -p "$tmp/before"
cp -R evals/fixture/project "$tmp/run"
mkdir -p "$tmp/run/docs/plans" && cp -R evals/fixture/plan-seed "$tmp/run/docs/plans/2026-01-01-fixture"
cd "$tmp/run" && git init -q && git add -A && git commit -qm fixture
claude -p --plugin-dir "$tmp/before/plugin" --allowedTools=Skill \
  --permission-mode acceptEdits --model sonnet \
  "/wb:create_research docs/plans/2026-01-01-fixture $(cat <repo>/evals/fixture/QUESTION.md)"
```

**Rationale**: the cwd is outside the plugin tree, so the read boundary behaves as it does for
real users (`.claude/wb/knowledge.md`, the cwd entry).
**Pattern Reference**: the Phase 0 probe of `docs/plans/2026-09-08-upstream-fable-merge/tasks.md`.

### Tasks

- [x] **P1-T1** — Promote the plan directory: `git add -f docs/plans/2026-09-29-asd-ste100-prose/`
      and commit it as `P1-T1: promote the asd-ste100-prose plan`. (~5 calls) (completed 2026-09-30 00:16)
- [x] **P1-T2** — Build `evals/fixture/`: `project/` (3–4 source files and a README with at
      least 3 facts at known lines), `QUESTION.md`, `expected.json`, and `plan-seed/` made from
      the 2.1.1 `create_project` templates (`git show 4b32306:plugin/skills/create_project/templates/…`).
      Lint the markdown with `./plugin/scripts/lint`. (~20 calls) (completed 2026-09-30 00:19)
- [x] **P1-T3** — Run the driver probe above against the 2.1.1 tree. Pass means all three: the
      run copy has `docs/plans/2026-01-01-fixture/research.md` with `status: complete`, the file
      cites at least 2 of the expected facts at their `file:line`, and stdout has the
      `✅ research.md updated` completion line. Record the result in
      `thoughts/2026-09-30-harness-probe.md` with cwd, command, model and duration. If the probe
      fails, record why, mark A6 `Invalid` in design.md, and stop at the checkpoint. Phases 2–5
      need a new driver in that case. (~20 calls) (completed 2026-09-30 00:24)

### Success Criteria

#### Automated Verification

- [x] `test -f "$tmp/run/docs/plans/2026-01-01-fixture/research.md"` and
      `grep -q '^status: complete' …/research.md` both succeed in the probe run
- [x] `./plugin/scripts/lint evals/fixture/**/*.md` is clean
- [x] `git ls-files docs/plans/2026-09-29-asd-ste100-prose/` lists `tasks.md`

#### Manual Verification

- [ ] A human reads the probe's `research.md` and confirms that the stage ran as designed and
      did not improvise
- [ ] The probe record names its cwd

### 📝 Modified Files (Phase 1)

#### Code Files

- `evals/fixture/project/README.md`, `evals/fixture/project/src/linkcheck/{__init__,config,checker,cli}.py` - the `linkcheck` fixture project, with facts F1–F6 at known lines (P1-T2)
- `evals/fixture/QUESTION.md` - the fixed research question (P1-T2)
- `evals/fixture/expected.json` - the 6 expected facts, with `id`, `fact`, `ref` (`file:line`) and `contains` (P1-T2)
- `evals/fixture/plan-seed/{README,research,design,tasks,journal}.md` - a plan directory made from the 2.1.1 `create_project` templates (P1-T2)
- `docs/plans/2026-09-29-asd-ste100-prose/thoughts/2026-09-30-harness-probe.md` - the probe record: PASS, with cwd, command, model and duration (P1-T3)

#### Test Files

- none (data and probe tasks)

**Quick test commands:**

```bash
# Run all tests for this phase
./plugin/scripts/lint $(git ls-files 'evals/fixture/*.md')
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
- [ ] **(attestation)** Manual verification confirmed by human
- [ ] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

---

## Phase 2: Rules authority, harness, and baseline

### Objective

Write the single WBTE authority, build the full harness with checks that are proven to fire,
and record the 2.1.1 baseline.

### Prerequisites

- [ ] Phase 1 complete and verified
- [ ] Phase 1 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*
- [ ] A6 is not `Invalid` in design.md

### Changes Required

#### 1. The WBTE reference doc

**File**: `plugin/docs/reference/technical-english.md` (new)

**Current State** (from research.md): `plugin/docs/reference/` holds `README.md` and
`branch-naming.md` only. No file states a writing standard for output (research §2).

**Target State** (from design.md, Data Model): one doc with these sections: credit and scope,
output rules, instruction rules ("lite"), technical nouns (WBTE is one), shorthand and IDs,
exempt tokens, how WBTE combines with Output discipline, optional dictionary, and repo terms in
`.claude/wb/technical-nouns.md`.

**Implementation**: follow the shape of `branch-naming.md`. The title names the rule, the first
paragraph says "Read this when a step directs you to" and that skills link here instead of
restating it. The doc itself is written in WBTE. It contains no ASD rules text and no
dictionary content. The exempt-token list copies each pattern exactly from its parser:

- `plugin/hooks/wb-prime.sh:83,131-136,154,163-165,195`
- `plugin/skills/validate_project/reference/validation-rules.md:22-23,40-44,71,92,98,104,116,129-140,172-178,196`
- `plugin/skills/daily-digest/sources.md:67-68,74,77,80`
- `plugin/skills/implement/SKILL.md:242-245,282,307,320`
- `plugin/agents/task-verifier.md:140,158`

**Pattern Reference**: `plugin/docs/reference/branch-naming.md:1-4`.

#### 2. The harness

**Directory**: `evals/` (new, never shipped)

**Implementation**: python3 scripts with no third-party packages.

- `evals/wbte_check.py` — the WBTE metric checker. It strips frontmatter, code, inline code,
  tables and headings with the research §5 method. It reports sentence-length distribution,
  prose semicolons, IDs used alone (`\b(P\d+-T\d+|Q\d+|A\d+|PD\d+|D-Q\d+|UIQ\d+)\b` with no
  meaning nearby, in chat output), noun clusters over 3 words (heuristic), and unapproved words
  if the user's dictionary copy exists. It exits 1 when a threshold is broken.
- `evals/token_check.py` — the exempt-token registry (`token → files that must contain it`) and
  the counting regexes run against a generated `tasks.md`. It reads each pattern from one
  registry file, `evals/tokens.json`.
- `evals/link_check.py` — every output template has the link line in its first lines, no file
  other than `technical-english.md` restates the rules (3–5 distinctive phrases, with the card
  in `wb-prime.sh` as the one named exception), and no tracked file holds a PDF or dictionary
  text.
- `evals/run.py` — the driver proven in P1-T3. It takes two git refs or paths, builds each
  plugin tree, and runs `create_research`, then `create_design`, then `create_tasks` on a fresh
  fixture copy for each repeat. Before `create_tasks` it sets `status: approved` in the
  generated `design.md`, because a headless run cannot approve. It stores documents and stdout
  under `evals/runs/<timestamp>/<tree>/<repeat>/`.
- `evals/judge.py` — the LLM fidelity judge. It calls `claude -p` with no plugin and compares
  before and after documents for lost facts, `file:line` references, IDs and barriers against
  `evals/fixture/expected.json`. It is calibrated on known-good and known-bad pairs.
- `evals/report.py` — one markdown report per comparison, and `evals/README.md` with usage.
- `evals/fixtures/planted/` — planted-failure inputs for each checker, each with a clean sibling.

**Rationale**: the harness is maintainer tooling (design.md, D-Q4, D-Q5), so python3 is not a
user requirement.
**Pattern Reference**: the research §5 metric method; the planted-failure checks in
`CHANGELOG.md` 2.1.1.

#### 3. Ignore rules

**Files**: `.gitignore`, `.wblintignore` (new)

- `.gitignore` gains `evals/runs/`, `__pycache__/` and `*.pyc`. The last two match what 3.0.0
  adds, so the merge sees the same lines.
- `.wblintignore` lists `evals/fixtures/planted/`, so the lint hook does not "fix" the planted
  failures (`plugin/scripts/lint-common.sh`, `wb_lint_ignored`).

### Tasks

#### Setup

- [ ] **P2-T1** — Write `plugin/docs/reference/technical-english.md` with all nine sections
      from design.md Data Model, and the exempt-token list copied from the parser lines listed
      above. Lint it. (~25 calls)
- [ ] **P2-T2** — Add `evals/runs/`, `__pycache__/` and `*.pyc` to `.gitignore`. Create
      `.wblintignore` with `evals/fixtures/planted/`. Confirm with
      `./plugin/scripts/lint --all` that planted files are skipped. (~6 calls)

#### Implementation

- [ ] **P2-T3** — Write `evals/wbte_check.py` and its planted-failure inputs (semicolons, a
      40-word sentence, a chat summary with `P1-T3` alone, a 5-word noun cluster) plus clean
      siblings. Each planted input must exit 1, and each clean sibling must exit 0. (~35 calls)
- [ ] **P2-T4** — Write `evals/tokens.json` and `evals/token_check.py`. Planted inputs: a task
      ID with no digit, a journal heading with no `(open)` or `(closed)`, a checkpoint block
      without `Go by the label, never by position`. Each must exit 1. (~30 calls)
- [ ] **P2-T5** — Write `evals/link_check.py`. Planted inputs: a template with no link line, a
      file that restates a rule phrase, a tracked `.pdf`. Each must exit 1. Today the check is
      expected to fail on every template, because no link lines exist yet. Record that as the
      RED state. (~25 calls)
- [ ] **P2-T6** — Write `evals/run.py` from the P1-T3 probe: two trees from git refs, a fresh
      fixture copy per repeat, the three stages in order, the `status: approved` step, the model
      pinned with `--model`, and outputs under `evals/runs/`. Run it once with 1 repeat on
      `4b32306` against itself to prove the plumbing. (~40 calls)
- [ ] **P2-T7** — Write `evals/judge.py` and `evals/report.py`, and `evals/README.md`. Calibrate
      the judge on 2 pairs from the P2-T6 run: the real output, and a copy with one `file:line`
      reference and one fact removed. The judge must flag the altered copy in 3 of 3 runs.
      (~35 calls)

#### Integration

- [ ] **P2-T8** — Run the 2.1.1 baseline: `evals/run.py` on `4b32306` with 3 repeats, then
      `wbte_check.py` and `token_check.py` on every output. Also run
      `claude --plugin-dir <before>/plugin plugin details wb` and record the "Projected token
      cost" block. Write the numbers to `thoughts/2026-09-30-baseline.md`. (~25 calls)

### Success Criteria

#### Automated Verification

- [ ] `python3 evals/wbte_check.py evals/fixtures/planted/<each bad file>` exits 1, and each
      clean sibling exits 0
- [ ] `python3 evals/token_check.py` and `python3 evals/link_check.py` fire on every planted
      input
- [ ] `./plugin/scripts/lint plugin/docs/reference/technical-english.md` is clean
- [ ] `./plugin/scripts/lint --all` is clean, and planted fixtures are skipped
- [ ] `grep -ril 'ASD-STE100' plugin/` lists only `technical-english.md` (the credit line)

#### Manual Verification

- [ ] A human reads `technical-english.md` and confirms it is WBTE, has no ASD text, and states
      every design.md Data Model section
- [ ] A human reads one judge verdict and one baseline report and confirms they make sense

### Modified Files

#### Code Files

- `plugin/docs/reference/technical-english.md` — new authority
- `evals/wbte_check.py`, `evals/token_check.py`, `evals/tokens.json`, `evals/link_check.py`,
  `evals/run.py`, `evals/judge.py`, `evals/report.py`, `evals/README.md` — new harness
- `.gitignore`, `.wblintignore`

#### Test Files

- `evals/fixtures/planted/*` — planted failures and clean siblings

**Quick test command for this phase**:

```bash
for f in evals/fixtures/planted/bad-*; do python3 evals/wbte_check.py "$f" && echo "MISSED $f"; done
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

## Phase 3: Rule card

### Objective

Print the WBTE rule card at every session start, prove it with a contract test, and measure
whether it changes chat output (A1).

### Prerequisites

- [ ] Phase 2 complete and verified
- [ ] Phase 2 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*
- [ ] The 2.1.1 baseline is recorded in `thoughts/2026-09-30-baseline.md`

### Changes Required

#### 1. The card in the hook

**File**: `plugin/hooks/wb-prime.sh` (shared with 3.0.0)

**Current State** (from research.md and the test agent):

- `:65-68` — `--export` prints `orientation()` and exits.
- `:70-71` — an empty payload exits with no output.
- `:91-92` — the recovery branch exits with no output when no plan is active.
- `:105-109` — the orientation branch prints `.claude/wb/PRIME.md` or `orientation`.

**Target State** (from design.md): the card prints on startup, resume and compact, with and
without active plans, with and without `PRIME.md`. `WB_TECH_ENGLISH=0` removes only the card.

**Implementation**:

- Add a `card()` function after `orientation()`. It prints the card text and the path
  `docs/reference/technical-english.md` under `${CLAUDE_PLUGIN_ROOT}` with a heredoc.
- In the recovery branch, call `card` before the line `[ "$count" -eq 0 ] && exit 0`.
- In the orientation branch, call `card` after the `PRIME.md`/`orientation` if/else, so the
  `PRIME.md` override does not remove it.
- Guard both calls with `[ "${WB_TECH_ENGLISH:-1}" = "0" ] || card`.
- Leave `--export` and the empty-payload exit unchanged. An empty payload is not a session
  start, and `--export` prints the text that `PRIME.md` replaces, which does not include the
  card.
- Add one bullet to the header comment that names the card and its opt-out.

**Rationale**: these are the smallest edits that cover every session-start path (design.md,
Architecture). 3.0.0 changes only 4 comment lines in this file.
**Pattern Reference**: the `WB_LINT_HOOK` switch at `plugin/scripts/lint-hook:11`.

#### 2. The contract test

**File**: `plugin/scripts/test-prime` (new)

**Implementation**: follow `plugin/scripts/test-lint`. Cases, from the test agent's matrix:
startup with 0, 1 and 2 plans; resume; compact with 0, 1 and 2 plans; `PreCompact`; `PRIME.md`
with startup and with compact at 0 plans; `WB_TECH_ENGLISH=0` (output identical to the unset
run minus the card lines); `WB_TECH_ENGLISH` unset, empty and `1`; `--export` with and without
stdin (no card); empty stdin (no output); an unrecognized payload (record today's behaviour);
exit 0 on every path; no file changes (checksums before and after); wall time under 5 s with
200 plan directories; one run from a subdirectory. Card size proxy: at most 150 words.

### Tasks

- [ ] **P3-T1** — Write `plugin/scripts/test-prime` with every case above. Run it against the
      current hook. The card cases must fail (RED), and every other case must pass. Record the
      RED output in the commit message. (~35 calls)
- [ ] **P3-T2** — Add `card()` and its two guarded calls to `plugin/hooks/wb-prime.sh`, and the
      header bullet. Write the card text (6–8 short imperatives, the ID rule, the path). Run
      `plugin/scripts/test-prime` until it is green, then run `plugin/scripts/test-lint` and
      `plugin/scripts/test-quiet`. Add `./plugin/scripts/test-prime` to `CLAUDE.md` under
      Development Tools, next to `test-lint`. (~20 calls)
- [ ] **P3-T3** — Measure A1: run `evals/run.py` with 3 repeats, comparing `4b32306` with the
      working tree (the card is the only plugin change). Compare the chat-output metrics with
      the baseline. If the metrics do not improve, change the card wording and run again, at
      most 2 more times. Record the verdict and each card version in
      `thoughts/2026-09-30-card-measurement.md`, and set A1 in design.md to `Validated` or
      `Invalid — <what moved and what did not>`. (~30 calls)

### Success Criteria

#### Automated Verification

- [ ] `./plugin/scripts/test-prime` passes
- [ ] `./plugin/scripts/test-lint` and `./plugin/scripts/test-quiet` pass
- [ ] `bash -n plugin/hooks/wb-prime.sh` succeeds
- [ ] The card is at most 150 words (checked in `test-prime`)

#### Manual Verification

- [ ] A3: in a real interactive session, in a repo with no active plans and the working-tree
      plugin (`claude --plugin-dir <repo>/plugin`), run `/compact` and confirm that the card is
      in the next context. Record the cwd and result in `thoughts/2026-09-30-card-measurement.md`,
      and set A3 in design.md
- [ ] A human reads the card and confirms it is short, clear, and WBTE

### Modified Files

#### Code Files

- `plugin/hooks/wb-prime.sh` — `card()` and two guarded calls
- `CLAUDE.md` — one line for `test-prime`

#### Test Files

- `plugin/scripts/test-prime` — new contract test

**Quick test command for this phase**:

```bash
./plugin/scripts/test-prime && ./plugin/scripts/test-lint && ./plugin/scripts/test-quiet
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

## Phase 4: Objective 1 — link lines and template rewrites

### Objective

Give every output template and inline output step the link line, rewrite the non-shared output
templates in WBTE, and show that generated output meets the design's targets.

### Prerequisites

- [ ] Phase 3 complete and verified
- [ ] Phase 3 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*

### Changes Required

#### 1. The link line

**Text** (one line, at the top of the template body, after any title line):

```markdown
Write this output in wb Technical English (WBTE): read [technical-english.md](<relative path>/docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.
```

The relative path depends on depth: `../../../docs/reference/technical-english.md` from
`plugin/skills/<skill>/templates/`, and `../../docs/reference/technical-english.md` from
`plugin/skills/<skill>/`.

**Pattern Reference**: "Read [link] NOW and apply it" at `plugin/skills/create_project/SKILL.md:104`.

#### 2. Shared files: link line only

These files are shared with 3.0.0 (design.md, D-Q3). Each gets the link line and no other
change:

- `plugin/skills/create_project/templates/journal-md-template.md`
- `plugin/skills/create_tasks/templates/tasks-md-template.md`
- `plugin/skills/implement/templates/{manual-verification-request,modified-files-fragment,phase-completion-report}.md`
- `plugin/skills/implement_inline/templates/{manual-verification-request,phase-completion-report}.md`
- `plugin/skills/update_status/templates/{completion-summary,frontmatter-fragments,status-update-plan}.md`
- `plugin/skills/validate_project/templates/validation-report.md`
- `plugin/skills/create_research/SKILL.md`, before the Step 8 completion line (`:248-251`)

#### 3. Non-shared templates: link line and WBTE rewrite

Each rewrite keeps the template's structure, headings, placeholders and every exempt token.
The WBTE rules apply to the prose. The `✅ … Next: /wb:<stage>` shape stays, and its semicolons
change to full stops or commas.

### Tasks

#### Implementation

- [ ] **P4-T1** — Add the link line to the 12 shared locations listed above. Run
      `python3 evals/link_check.py` and confirm that those 12 now pass. (~20 calls)
- [ ] **P4-T2** — Measure A2: run `evals/run.py` with 3 repeats, comparing the Phase 3 tree
      with the P4-T1 tree. Record whether the generated `tasks.md` and chat summaries moved
      towards the targets in `thoughts/2026-09-30-link-measurement.md`. Set A2 in design.md.
      (~20 calls)
- [ ] **P4-T3** — Rewrite in WBTE, with the link line: `create_project/templates/{design-md-template,readme-md-template,research-md-template,tasks-md-template}.md`
      and the Step 5 output block in `create_project/SKILL.md:153-181`. Run
      `evals/token_check.py` and `evals/link_check.py`. (~30 calls)
- [ ] **P4-T4** — Rewrite in WBTE, with the link line: `create_research/templates.md` and
      `create_design/templates/{design-md-template,design-options-message,design-presentation-message,recorded-decision-confirmation-message}.md`.
      Run both checks. (~30 calls)
- [ ] **P4-T5** — Rewrite in WBTE, with the link line: `create_handoff/templates/{handoff-document,completion-message}.md`,
      `resume_handoff/templates.md`, and `explore_design/templates/{exploration-document,completion-message}.md`.
      Run both checks. (~30 calls)
- [ ] **P4-T6** — Rewrite in WBTE, with the link line: `validate_execution/templates.md`,
      `validate_project/templates/error-message-formats.md`, `resolve_questions/templates.md`,
      and `create_tasks/templates/plan-presentation-message.md`. Run both checks. (~30 calls)
- [ ] **P4-T7** — Rewrite in WBTE, with the link line: `create_mockup/templates/{clarifying-questions,decisions-md,mockup-html,mockup-log-md,mockup-md,presentation-message,ui-research-summary}.md`,
      `create_product_research/templates.md`, and the completion line at
      `create_product_research/SKILL.md:236-239`. Run both checks. (~35 calls)
- [ ] **P4-T8** — Rewrite in WBTE, with the link line: `forge/templates/{model-plan,output-style}.md`,
      `daily-digest/digest-template.md`, `touch-grass/state-template.md`,
      `implement/templates/incomplete-worker-message.md`,
      `implement_inline/templates/modified-files-fragment.md`, and the end-of-turn summary at
      `resolve_questions/SKILL.md:205-212`. Run both checks. `link_check.py` must now pass on
      every template. (~30 calls)

#### Integration

- [ ] **P4-T9** — Run `evals/run.py` with 3 repeats, comparing `4b32306` with the P4-T8 tree.
      Run `wbte_check.py`, `token_check.py` and the judge on every output, then `report.py`.
      Check the design.md targets: no prose semicolons, no lone IDs in chat, at most 5% of
      sentences over 25 words and fewer than the baseline, no lost facts. Save the report as
      `thoughts/2026-09-30-objective-1-report.md`. If a target fails, name the template that
      caused it and fix it in this task. (~35 calls)

### Success Criteria

#### Automated Verification

- [ ] `python3 evals/link_check.py` passes on every template and inline step
- [ ] `python3 evals/token_check.py` passes on the generated documents of every repeat
- [ ] `python3 evals/wbte_check.py` meets the design.md thresholds on the P4-T9 outputs
- [ ] `./plugin/scripts/lint --all` is clean

#### Manual Verification

- [ ] A human reads one generated `research.md`, one `design.md`, one `tasks.md` and one chat
      summary from P4-T9, and confirms they are easier to follow than the baseline samples
- [ ] A human confirms the judge verdicts in the report match a spot check

### Modified Files

#### Code Files

- The 12 shared locations in Changes Required §2 (link line only)
- The 30 non-shared templates and 4 inline output steps named in P4-T3 to P4-T8

**Quick test command for this phase**:

```bash
python3 evals/link_check.py && python3 evals/token_check.py && ./plugin/scripts/lint --all
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

## Phase 5: Objective 2 — gated "lite" rewrite

### Objective

Apply the WBTE "lite" rules to the non-shared instruction files that the harness exercises, and
keep each rewrite only if the harness shows no loss.

### Prerequisites

- [ ] Phase 4 complete and verified
- [ ] Phase 4 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*

### Changes Required

#### 1. Which files

design.md says a rewrite is kept "only where the harness shows no loss". The harness runs
`create_project` (through the fixture seed), `create_research`, `create_design` and
`create_tasks`, and the agents they spawn. A rewrite of a file the harness does not exercise
cannot show "no loss", so this phase covers only exercised, non-shared files:

- `plugin/skills/create_research/{reference,sub-agent-prompts}.md`
- `plugin/skills/create_design/{reference,sub-agent-prompts}.md`
- `plugin/skills/create_tasks/{reference,examples,sub-agent-prompts}.md`
- `plugin/agents/{codebase-analyzer,codebase-locator}.md`

The remaining non-shared skill files wait for the post-3.0.0 pass, together with the 48 shared
files. The 3.0.0 handoff (P7-T2) lists them.

#### 2. The gate, for each task

1. Rewrite the files with the "lite" rules from `technical-english.md`. Keep barriers, "Read
   [link] NOW" directives, and capitalized scope rules as they are. The 2.0.0 trials showed that
   trimming them made results worse (R3, R4).
2. Run `evals/run.py` with 3 repeats, comparing the Phase 4 tree with the rewrite applied.
3. Keep the rewrite only if the judge finds no loss in 3 of 3 repeats and `token_check.py`
   passes. Otherwise restore the file from the Phase 4 commit with `git checkout <sha> -- <file>`.
4. Record the verdict per file in `thoughts/2026-09-30-lite-verdicts.md`, in a table with the
   file, repeats, judge result and kept or restored.

### Tasks

- [ ] **P5-T1** — Gate `create_research/{reference,sub-agent-prompts}.md`. (~30 calls)
- [ ] **P5-T2** — Gate `create_design/{reference,sub-agent-prompts}.md`. (~30 calls)
- [ ] **P5-T3** — Gate `create_tasks/{reference,examples,sub-agent-prompts}.md`. (~30 calls)
- [ ] **P5-T4** — Gate `agents/{codebase-analyzer,codebase-locator}.md`. Then measure the token
      cost of the final tree with `claude --plugin-dir plugin plugin details wb` and add it to
      `thoughts/2026-09-30-lite-verdicts.md` beside the baseline. (~30 calls)

### Success Criteria

#### Automated Verification

- [ ] Every kept rewrite has a 3/3 "no loss" verdict in `thoughts/2026-09-30-lite-verdicts.md`
- [ ] `python3 evals/token_check.py` and `python3 evals/link_check.py` pass
- [ ] `./plugin/scripts/lint --all` is clean

#### Manual Verification

- [ ] A human reads the verdict table and one kept rewrite, and confirms that the rewrite did
      not remove meaning

### Modified Files

#### Code Files

- The kept files from the list in Changes Required §1
- `docs/plans/2026-09-29-asd-ste100-prose/thoughts/2026-09-30-lite-verdicts.md`

**Quick test command for this phase**:

```bash
python3 evals/token_check.py && python3 evals/link_check.py
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

## Phase 6: Dictionary skill

### Objective

Give users a way to make their own local copy of the ASD dictionary, with no ASD content in the
repo and no new requirement for users who do not want it.

### Prerequisites

- [ ] Phase 5 complete and verified (or run this phase in parallel with Phases 3–5; it depends
      only on P2-T1)
- [ ] Phase 5 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*

### Changes Required

#### 1. Extractor script

**File**: `plugin/scripts/wbte-dictionary` (new)

**Implementation**: a bash script. Input is a path to the user's Issue 9 PDF. It uses
`pdftotext -layout` if present, otherwise python3 with `pypdf` if importable. If neither is
present, it prints what to install and exits 2. It writes
`${HOME}/.claude/wb/wbte-dictionary.tsv` (word, part of speech, approved or not, alternatives).
It refuses to write inside a git work tree. It never writes anywhere else.

#### 2. The skill

**File**: `plugin/skills/wbte-dictionary/SKILL.md` (new, user-invocable)

**Implementation**: frontmatter `name`, `description` (trigger phrases), `argument-hint:
"[path-to-ASD-STE100-Issue-9.pdf]"`, `allowed-tools: Bash, Read`. Steps: explain that the PDF
is free from asd-ste100.org and that the user must get it, run the extractor, report the entry
count, and say where the copy lives and that it stays out of every repo. Written in WBTE.
**Pattern Reference**: `plugin/skills/eli5-clip/SKILL.md` (small, self-contained skill).

#### 3. The contract test

**File**: `plugin/scripts/test-wbte-dictionary` (new)

**Fixtures**: a tiny PDF or text file made from invented words, generated in the test (no ASD
content); `HOME=$(mktemp -d)`; a `PATH` with no `pdftotext` and no python3.

### Tasks

- [ ] **P6-T1** — Write `plugin/scripts/test-wbte-dictionary` (RED): the invented-word input
      gives the expected TSV rows, no tool gives exit 2 and a message that names both tools,
      the output lands only under the temporary `HOME`, and a run inside a git work tree is
      refused. (~30 calls)
- [ ] **P6-T2** — Write `plugin/scripts/wbte-dictionary` until the test is green, and write
      `plugin/skills/wbte-dictionary/SKILL.md`. Point the dictionary section of
      `technical-english.md` at the skill and the output path. (~30 calls)

### Success Criteria

#### Automated Verification

- [ ] `./plugin/scripts/test-wbte-dictionary` passes
- [ ] `./plugin/scripts/lint plugin/skills/wbte-dictionary/SKILL.md` is clean
- [ ] `git ls-files | grep -iE '\.pdf$|wbte-dictionary\.tsv'` prints nothing

#### Manual Verification

- [ ] A4: a human runs `/wb:wbte-dictionary <path-to-real-Issue-9.pdf>` and confirms that the
      entries are usable (word, part of speech, approved or not, alternatives). Set A4 in
      design.md
- [ ] The skill works from a fresh session, and the plugin still works with no copy present

### Modified Files

#### Code Files

- `plugin/scripts/wbte-dictionary` — new extractor
- `plugin/skills/wbte-dictionary/SKILL.md` — new skill
- `plugin/docs/reference/technical-english.md` — dictionary section points to the skill

#### Test Files

- `plugin/scripts/test-wbte-dictionary`

**Quick test command for this phase**:

```bash
./plugin/scripts/test-wbte-dictionary
```

### ⛔ CHECKPOINT: Phase 6 Complete

These are the conditions to meet before Phase 7 — **not a record of having met them.** Tick
each one as it is actually satisfied.

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

## Phase 7: Documentation, handoff, and release checks

### Objective

Document WBTE for users and maintainers, hand the format to the 3.0.0 branch, bump the version,
and prove the release is ready to merge.

### Prerequisites

- [ ] Phase 6 complete and verified
- [ ] Phase 6 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*

### Changes Required

#### 1. README and CLAUDE.md

- `README.md` — a "wb Technical English (WBTE)" section: what it is, the credit line, the card,
  `WB_TECH_ENGLISH=0` in a `Variable | Effect` table (the 2.1.1 shape at `README.md:267-270`),
  the dictionary skill, and `.claude/wb/technical-nouns.md`.
- `CLAUDE.md` — a pointer under "Working with Commands": new output templates carry the link
  line, and `technical-english.md` is the one place the rules change (the `branch-naming.md`
  pointer at `CLAUDE.md:247` is the model). A line under Development Tools for `evals/`.

#### 2. The 3.0.0 handoff

**File**: `docs/plans/2026-09-29-asd-ste100-prose/handoff-2026-09-30-wbte-for-3.0.0.md` (new),
in the shape of `plugin/skills/create_handoff/templates/handoff-document.md`.

Contents: the new files; the link-line text and the 12 shared locations that have it; the exact
`wb-prime.sh` lines; the list of 48 shared files plus the non-shared, non-exercised skill files
for the post-3.0.0 pass; how to run `evals/` and the gate; the expected merge conflicts.

#### 3. CHANGELOG and version

- `CHANGELOG.md` — `## [2.2.0] — <date>` in the 2.1.1 shape: a prose paragraph, `### Added`,
  `### Changed`, `### Not changed, deliberately` (the 48 shared files, maintainer docs, runtime
  checks), and `### Migration` with `claude plugin update wb@thescubageek-workbench`. Include
  the baseline and final numbers from the harness and the token-cost change.
- `plugin/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` — `"version": "2.2.0"`.

### Tasks

- [ ] **P7-T1** — Write the README section and the two `CLAUDE.md` lines. Lint both. (~15 calls)
- [ ] **P7-T2** — Write `handoff-2026-09-30-wbte-for-3.0.0.md` with every item in Changes
      Required §2. `git add -f` it. (~20 calls)
- [ ] **P7-T3** — Write the CHANGELOG 2.2.0 entry. Bump both manifests to 2.2.0. (~15 calls)
- [ ] **P7-T4** — Run the release checks and record the output in
      `thoughts/2026-09-30-release-checks.md`: `./plugin/scripts/lint --all`,
      `./plugin/scripts/test-lint`, `./plugin/scripts/test-quiet`, `./plugin/scripts/test-prime`,
      `./plugin/scripts/test-wbte-dictionary`, `python3 evals/link_check.py`,
      `python3 evals/token_check.py`, `claude plugin validate plugin/`,
      `claude --plugin-dir plugin plugin details wb`, and
      `git merge-tree --write-tree HEAD adversarial-loop-skill-research` (list the conflicted
      paths). (~20 calls)
- [ ] **P7-T5** — Compare the conflicted paths from P7-T4 with the expected set: link lines,
      `wb-prime.sh`, the manifests, `README.md`, `CHANGELOG.md`, `.gitignore`, `CLAUDE.md`.
      For each unexpected path, reduce the 2.2.0 change or add it to the handoff with a
      resolution note. Run `git merge-tree` again. (~20 calls)

### Success Criteria

#### Automated Verification

- [ ] Every command in P7-T4 exits 0, except `git merge-tree`, whose conflicts are only in the
      expected paths
- [ ] `grep -h '"version"' plugin/.claude-plugin/plugin.json .claude-plugin/marketplace.json`
      shows `2.2.0` twice
- [ ] `git ls-files docs/plans/2026-09-29-asd-ste100-prose/` lists the handoff

#### Manual Verification

- [ ] A human reads the README section, the CHANGELOG entry and the handoff, and confirms that
      they describe the release correctly
- [ ] A smoke session with `claude --plugin-dir <repo>/plugin` shows the card, and one stage
      produces WBTE output

### Modified Files

#### Code Files

- `README.md`, `CLAUDE.md`, `CHANGELOG.md`
- `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- `docs/plans/2026-09-29-asd-ste100-prose/handoff-2026-09-30-wbte-for-3.0.0.md`

**Quick test command for this phase**:

```bash
./plugin/scripts/lint --all && ./plugin/scripts/test-prime && python3 evals/link_check.py
```

### ⛔ CHECKPOINT: Phase 7 Complete

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

- [ ] **(derivable)** Every Phase 7 checkbox is `[x]`
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

- **Harness run cost.** Each repeat runs three stages, and each comparison runs 3 repeats on 2
  trees. Record the wall time and token use of the first full run (P2-T8), and reduce repeats
  or stages if the cost is too high.
- **Judge reliability.** Record how often the judge disagrees with itself across repeats
  (P2-T7). If the rate is high, add mechanical checks before trusting its verdicts.
- **Headless design approval.** The harness sets `status: approved` before `create_tasks`.
  Confirm that `create_tasks` accepts that and does not wait for input.
- **Card wording.** P3-T3 may need up to three card versions. Keep each version and its
  numbers.
- **Unrecognized hook payloads.** The hook header says it is silent on an unrecognized payload,
  but the code prints the orientation. `test-prime` records today's behaviour. It is not
  changed in this plan.

Note: Update this section with findings as you implement.

---

## 📝 Completed Tasks Archive

Move completed tasks here as phases close, to keep the active list readable.

---

## 🚧 Blockers & Notes

### Current Blockers

Recorded here with the task ID they block and the date raised. Remove a blocker when it is
resolved, leaving a dated line saying how.

- None as of 2026-09-30.

### Implementation Notes

- **Objective 2 scope in 2.2.0 is limited to files the harness exercises.** design.md keeps a
  "lite" rewrite only where the harness shows no loss, and a file the harness never runs cannot
  show that. The other non-shared skill files move to the post-3.0.0 pass. The handoff (P7-T2)
  lists them.
- **Pushing, opening the pull request, and tagging are not in this plan.** They are
  outward-facing and need the user's go-ahead. The tag follows the merge, with
  `claude plugin tag plugin/` on a clean tree (`.claude/wb/knowledge.md`).
- **Planned against 2.1.1** (`4b32306`). If `main` moves before Phase 7, rebase and repeat the
  P7-T4 checks.
- [2026-09-30] **Follow-up from P1-T2: three 2.1.1 templates fail markdownlint as written.**
  `create_project/templates/{research,design,tasks}-md-template.md` have no blank lines around
  headings, lists and tables. The lint hook fixes each generated copy after the write. The
  fixture seeds were lint-fixed. The templates were not changed, because that is not in this plan.
- [2026-09-30] **Limit of the P1-T3 probe: the sub-agent fan-out was not tested.** The fixture is
  small, so `create_research` skipped its agents, as the 2.1.1 stage allows. The probe also ran
  with the read boundary off. P2-T6 is the first run that can show whether headless stages
  spawn sub-agents.

---

## 🔗 Quick Reference

### Key Files

- **Research**: [research.md](research.md) - Current state documentation
- **Design**: [design.md](design.md) - Target state specification
- **Main Entry**: `plugin/docs/reference/technical-english.md`
- **Config**: `WB_TECH_ENGLISH` in `plugin/hooks/wb-prime.sh`; `.claude/wb/technical-nouns.md`

### Common Commands

```bash
# Contract tests
./plugin/scripts/test-prime && ./plugin/scripts/test-lint && ./plugin/scripts/test-quiet

# Harness checks
python3 evals/link_check.py && python3 evals/token_check.py

# Before/after comparison (3 repeats)
python3 evals/run.py --before 4b32306 --after HEAD --repeats 3

# Lint
./plugin/scripts/lint --all

# Progress (scoped to task lines — criteria checkboxes are not tasks)
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md
```

### Design Decisions Reference

Quick lookup of key design decisions:

- D1 (delivery): a reference doc plus an always-on rule card, with link lines in templates.
- D2 (name): wb Technical English, WBTE, credited to ASD-STE100 Issue 9, not endorsed by ASD.
- D-Q1 (objectives): output first. Skill prose changes only where the harness shows no loss.
- D-Q2 (licence): paraphrased rules. The user makes their own dictionary copy.
- D-Q3 (3.0.0): link lines only in the 48 shared files, plus a handoff.
- D-Q4 (quality): the eval harness decides.
- D-Q5 (enforcement): instructions at runtime. The checker runs only in the harness.
