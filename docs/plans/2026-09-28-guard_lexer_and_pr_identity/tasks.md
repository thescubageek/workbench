---
project: guard_lexer_and_pr_identity
ticket: null
created: 2026-09-28
created_timestamp: 2026-09-28T20:05:58Z
status: complete
last_updated: 2026-10-01
assignee: scraig
current_phase: 3
total_tasks: 18
completed_tasks: 18
task_tracking: markdown-checkboxes
depends_on: [research.md, design.md]
git_commit: d523862
git_branch: adversarial-loop-skill-research
repository: thescubageek/workbench
tags: [tasks, tracking, guard_lexer_and_pr_identity]
---

# Execution Plan: guard_lexer_and_pr_identity

## Overview

Implementing one lexer for `check-guards` and one identity resolver for `adversarial-review`,
as specified in design.md — the escalation the `adversarial_loop` breaker demanded after round
10, landing on `adversarial-loop-skill-research` before PR #25 merges.

**Design Approach**: One lexer, one resolver — retire two classes the review loop kept
re-finding.
**Target State**: `check-guards` has exactly one definition of quoting context and passes the
117-case corpus with zero unwaived survivors; `adversarial-review` resolves a PR target once, by
commit, refuses a same-name fork by name, fetches an off-checkout head as a disclosed step, and
Step 2 reads the same refs; the generated sweep runs in CI; no new dependency.

## Task tracking

**Checkbox state in this file is the source of truth.** There is no external tracker. Flip
`[ ]` → `[x]` as work completes and append `(completed YYYY-MM-DD HH:MM)`. The frontmatter
counters are a derived cache with exactly one writer — `/wb:update_status` — and are never
hand-edited. Git is the durable record: one task, one commit.

This plan directory is promoted (every file so far committed with `git add -f`). Promotion is
per file, not per directory: anything added later — a new `thoughts/` file, a handoff — needs
`git add -f` of its own, every time, and `git status` never lists ignored files:

```bash
git ls-files --others --ignored --exclude-standard docs/plans/2026-09-28-guard_lexer_and_pr_identity/
```

Every task carries a stable local ID (`P1-T3`). **The ID's shape is a contract**: it must match
`[A-Z0-9-]*[0-9][A-Z0-9-]*` — at least one digit — and be bold, immediately after the checkbox.
An ID that does not match makes the task invisible to counting.

```bash
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # completed
grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # remaining
```

## Implementation Strategy

### Phase Rationale

Three phases, ordered by what each one's acceptance apparatus needs from the one before.

- **Phase 1, the lexer, first**, because its acceptance bar is entirely local — the corpus,
  the curated mutations and the generated sweep — and because the tracer bullet already
  produced the seed (`thoughts/spike/candidates/B/check-guards`) and the exact list of what the
  sweep will say. Nothing in Phase 2 depends on it, but Phase 2 edits a skill whose fenced
  blocks `check-guards` scans, so the scanner is finished before the skill it scans changes.
- **Phase 2, the resolver**, edits one skill file in three steps that share one variable set.
  The resolver block lands first because Step 1 and Step 2 both become its consumers; Step 3's
  two changes ride with the same file. The loop's stop-table row and the live check on PR #25
  close the phase.
- **Phase 3, CI and bookkeeping**, is last because its CI job runs the sweep Phase 1 finishes,
  and its bookkeeping closes the ten round-10 tasks Phases 1 and 2 retire.

**No Phase 0.** Both tracer bullets the breaker required have run and are recorded
(`thoughts/2026-09-28-lexer-tracer-bullet.md`, `thoughts/2026-09-28-identity-tracer-bullet.md`).
The plan rests on their results, not on an assumption.

**Two things the tasks carry so a worker is not left to infer them** — round 7's two
escalations both failed on a worker inventing a rationale it was never handed:

- The lexer's shell rules are in `design.md` → Technical Decisions → "The shell rules the
  lexer encodes"; the seed is `thoughts/spike/candidates/B/check-guards`, and the diff between
  it and the shipped file is the change, minus the `depth` field.
- The resolver's contract is `design.md` → Data Model → "The resolver's output"; the fixture
  recipe is `thoughts/2026-09-28-identity-tracer-bullet.md` → Fixture, including the lesson
  that a bare test origin must have the pull ref pushed explicitly.

### Testing Strategy

**`test-guards` is the test.** The plain suite (corpus + 15 integrity claims + 25 curated
mutations) runs in seconds and is the RED/GREEN for every Phase 1 task. `--generated` takes
minutes and runs **only in the background, never two at once**; it is P1-T2's whole job and
otherwise runs once at the Phase 1 checkpoint. Each Phase 1 task adds its corpus cases first,
records the RED count, then fixes.

**Phase 2 is verified by executing fenced blocks as written**, per the repository's doctrine,
against a scratch fixture with a stubbed `gh` on `PATH` — the identity bullet's recipe. The
edited skill also passes `check-guards plugin/` (shape 6: no bare `$1`; shape 5: no
`PIPESTATUS`; shape 4: publish actions chained), which is the automated check on prose that
executes.

**`command grep` for every measurement**; `rtk proxy git status --porcelain` after any agent
fan-out; `pwd` and `pwd -P` recorded at every fixture.

## Progress Overview

| Phase | Status | Tasks | Progress |
| ----- | ------ | ----- | -------- |
| Phase 0: Planning | ✅ Complete | 4/4 | 100% |
| Phase 1: One lexer | ✅ Complete | 5/5 | 100% |
| Phase 2: One resolver | ✅ Complete (manual verification deferred) | 5/5 | 100% |
| Phase 3: CI and close-out | ✅ Complete (manual verification deferred) | 4/4 | 100% |

Counts come from the checkboxes below and are reconciled by `/wb:update_status`.

---

## Phase 0: Planning

### Objective

Produce validated research, an approved design, and this execution plan.

### Tasks

- [x] **P0-T1** — Create project structure (completed 2026-09-28 20:05)
- [x] **P0-T2** — Complete research using `/wb:create_research docs/plans/2026-09-28-guard_lexer_and_pr_identity` (completed 2026-09-28 20:24)
- [x] **P0-T3** — Create design document using `/wb:create_design docs/plans/2026-09-28-guard_lexer_and_pr_identity` (completed 2026-09-29 01:20)
- [x] **P0-T4** — Generate execution plan using `/wb:create_tasks docs/plans/2026-09-28-guard_lexer_and_pr_identity` (completed 2026-09-29 01:37)

---

## Phase 1: One lexer

### Objective

Replace `check-guards`' three quote trackers with one state machine every consumer reads, land
the corpus cases and mutation equivalents that make it the acceptance bar, and close the three
non-lexing edits that live in the same file. Close R10-T7, T10, T11, T12, T5, T21.

### Prerequisites

- [x] Research complete (`research.md` status `complete`)
- [x] Design approved (`design.md` status `approved`)
- [x] The lexer tracer bullet's seed exists: `thoughts/spike/candidates/B/check-guards`,
      117/117 on the harness after the close-paren fix

### Changes Required

#### 1. The lexer

**File**: `plugin/scripts/check-guards`

**Current State** (research.md → The `check-guards` lexer): three trackers —
`strip_comment` (`:111-131`), `_quote_spans` (`:134-147`), `substitutions()` (`:150-194`) —
none handling a backslash, the third returning only the outermost span; `SHELL_INFO =
{'bash', 'sh', 'shell'}` (`:58`); `GUARD` accepting `|| echo` (`:62`); the shape-6 hint naming
`read -r path` (`:389`); every unclosed fence labelled `'unclosed shell fence'` (`:391, :432`).

**Target State** (design.md → Architecture): one `lex(line)` returning a per-character
`(in_single, in_double, escaped)` and every span in close order; the three consumers rebuilt
on it, `statements()` too; `zsh` in `SHELL_INFO`; the docstring stating the eight shell rules;
context carrying only what is read.

**Implementation**: the seed is the diff between `thoughts/spike/candidates/B/check-guards`
and `plugin/scripts/check-guards` — `lex()` plus the three rebuilt consumers plus `zsh` — with
one change: drop the fourth tuple element (`depth`, `d`, `d + 1`) everywhere; the tuple is
`(sq, dq, escaped)`. The close-paren branch must read `if ch == ')' and not dq and stack and
stack[-1][1] == 'paren':` — the bullet's fix — and the docstring must carry the sentence "a `)`
inside double quotes is literal and closes nothing".

**Rationale**: design.md → Architecture, first three decisions.
**Pattern Reference**: `thoughts/spike/candidates/B/check-guards:111-207` (the seed as scored).

#### 2. The test apparatus

**Files**: `plugin/scripts/test-guards`, `plugin/scripts/fixtures/guard-corpus.json`,
`plugin/scripts/fixtures/mutation-waivers.json`, `plugin/scripts/fixtures/mutation-ratchet.json`

**Current State** (research.md → The test apparatus): 114 corpus cases; 25 curated mutations,
three of which anchor on text the lexer replaces — `'break the quote-aware comment strip'`
(anchor `out, quote = [], None`), `'stop scanning sh/shell fences'` (anchor
`SHELL_INFO = {'bash', 'sh', 'shell'}`), `'make the span finder quote-blind again'` (anchor
`if line[j] == ')' and not q[j]:`); 51 waivers of which 13 go stale under the
new keys; ratchet `{"killed": 344, "of": 395}`.

**Target State** (design.md → Integration Points, first bullet): 117+ cases including the
bullet's three and the sweep's real gaps; 25 curated mutations all applying; no stale waiver;
zero unwaived survivors; ratchet re-based with provenance.

### Tasks

Tasks run in document order. Each Phase 1 task writes its corpus cases first, records the RED
count from `./plugin/scripts/test-guards`, then changes the checker. `--generated` runs only in
P1-T2 and at the checkpoint, backgrounded.

- [x] **P1-T1** — Land `lex()` and the six corpus cases that pin it. Corpus first, into
      `fixtures/guard-corpus.json` with `provenance`: the bullet's three
      (`r10-t10-escaped-dollar-paren` expect 0; `r10-t11-nested-guard-inner` expect 1 at its
      line, `capture`; `r10-t7-zsh-fence-positional` expect 1, `positional` — contents verbatim
      from `thoughts/2026-09-28-lexer-tracer-bullet.md` → "The three cases added"), plus the
      sweep's three real gaps from the same document's survivor table: a double-quoted string
      spanning a `$(` boundary with an unguarded capture inside (must fire); a `;` inside single
      quotes on a chained publish line — `git push && gh pr ready "$PR"; echo 'a;b'` — which
      must **not** split into a second statement (must not fire); a backtick capture opened
      inside double quotes, unguarded (must fire). **RED**: `./plugin/scripts/test-guards`
      reports 114/120 with those six named. Then replace `strip_comment`, `_quote_spans` and
      `substitutions()` with `lex()` and its three readers per Changes Required §1, `depth`
      omitted; add `'zsh'` to `SHELL_INFO`. Then rewrite the three curated mutations whose
      anchors vanished, against `lex()`: *break the backslash handling* (delete the
      `if ch == '\\':` branch), *break single-quote suppression* (make the `sq` branch fall
      through to the `$(` check), *break the save-and-restore of `dq` across a substitution*
      (drop `dq = False` on `$(` open) — each anchored on a line of the new `lex()`, and each
      **shown to fail the corpus** when planted in a scratch copy before it is trusted (A2).
      **GREEN**: corpus 120/120, integrity 15/15, mutations 25/25. Do not run `--generated`
      here. (~35 calls) (completed 2026-09-29 02:12)
- [x] **P1-T2** — Close the generated sweep. Run `./plugin/scripts/test-guards --generated`
      **in the background** and read the survivors file. Expected from the bullet: 13 stale
      waivers (statements in the replaced functions) and a handful of survivors in `lex()` and
      `_quote_spans` — fewer than the bullet's 26 because `depth` is gone. For each stale waiver:
      rewrite its `match` key against the new statement if the mutant still exists, else delete
      it, listing every deletion in the commit message. For each unwaived survivor: a corpus
      case if a real input distinguishes it, otherwise a waiver whose `reason` is an argument.
      Then set `mutation-ratchet.json` to the new `killed`/`of` **once, with provenance in the
      commit message** ("re-based from 344/395 after the lexer rewrite; N mutants added by
      `lex()`"), since the sweep's `killed < prev` rule would otherwise fail on a total that
      changed. **GREEN**: `--generated` reports 0 unwaived, 0 stale, and the plain suite still
      passes. (~30 calls, plus two backgrounded runs of ~4 minutes) (completed 2026-09-29 04:58)
- [x] **P1-T3** — R10-T12: remove `echo` from `GUARD` (`check-guards:62` today,
      `re.compile(r'\|\|\s*(?:true\b|:(?!\w)|echo\b)')` → drop the `|echo\b` alternative). Corpus
      first: a must-fire case `n=$(grep -c foo f.txt || echo 0)` with provenance R10-T12. **RED**:
      119 of 121, that case missed. After the change: **GREEN**, and `./plugin/scripts/check-guards plugin/`
      is either still clean or every shipped line it now flags is fixed in this same task (they
      would be lines that relied on `|| echo` as a guard; the fix is `|| true` with `${n:-0}`,
      the docstring's own minimum bar). (~8 calls) (completed 2026-09-29 05:20)
- [x] **P1-T4** — R10-T5: change the shape-6 fix hint at `check-guards:389` from
      `while IFS=: read -r path _` to `while IFS=: read -r file _`, and add one sentence to the
      module docstring's shape-6 paragraph that `path` is tied to `PATH` under zsh. **RED**
      (shape 3): `command grep -c 'read -r path' plugin/scripts/check-guards` → 1; after: 0 and
      `command grep -c 'read -r file' …` → 1. (~3 calls) (completed 2026-09-29 05:32)
- [x] **P1-T5** — R10-T21: relabel the unclosed-fence finding from `'unclosed shell fence'` to
      `'unclosed fence'` at `check-guards:391` (FIXES key) and `:432` (the `findings.append`),
      with a hint that names the language of the fence left open; map the new label in
      `test-guards`' `SHAPE_OF` to `'fence'` so every existing `fence` case still parses. Corpus
      first: a case whose only content is an unclosed `text` fence, `expect 1`, `expect_at`
      shape `fence`, with provenance R10-T21 — **and** a `test-guards` assertion (integrity claim
      16, in `run_integrity`) that the finding text for that case does not contain the word
      `shell`. **RED**: the new claim fails; **GREEN**: 16/16 integrity. (~8 calls) (completed 2026-09-29 05:45)

### Success Criteria

#### Automated Verification

- [x] `./plugin/scripts/test-guards` → corpus 128/128, integrity 16/16, mutations 25/25 — PASS
      (was 122/122 when planned: P1-T2 was assumed to add no corpus cases and added six, each
      the sole killer of a named survivor — see Implementation Notes)
- [x] `./plugin/scripts/test-guards --generated` (backgrounded) → 0 unwaived survivors, 0 stale
      waivers, ratchet held at the re-based value (378/421 after `93d5a3b`; see Implementation Notes)
- [x] `./plugin/scripts/check-guards plugin/` → clean (shape 6 sees `zsh` fences now; none
      shipped carry a positional token)
- [x] `./plugin/scripts/check` → all gates pass
- [x] The lexer imports nothing new:
      `command grep -nE '^(import|from) ' plugin/scripts/check-guards` → exactly `os`, `re`, `sys`
- [x] The three replaced curated mutations are gone and their equivalents present:
      `command grep -c 'quote-aware comment strip\|sh/shell fences\|quote-blind again' plugin/scripts/test-guards` → 0,
      and each new label appears once
- [x] The context tuple carries three fields: `command grep -c 'ctx\[i\] = (.*, .*, .*, ' plugin/scripts/check-guards` → 0

#### Manual Verification

- [x] A human has read `lex()`'s docstring and agrees every rule in it is the shell's, not the
      corpus's — the design's first risk row (the user, 2026-10-01, after `64ea2d2` relabelled
      two rules as the lexer's own; see Implementation Notes)
- [x] A human has read the P1-T2 waiver deletions and agrees none dropped a mutant that still
      exists under a new key (the user, 2026-10-01, on the measurement in Implementation Notes)

### Modified Files

#### Code Files

- `plugin/scripts/check-guards` — `lex()` replaces three trackers; `zsh` fence; `GUARD`; the
  shape-6 hint; the unclosed-fence label
- `plugin/scripts/test-guards` — three curated mutations rewritten; `SHAPE_OF` entry; integrity
  claim 16

#### Test Files

- `plugin/scripts/fixtures/guard-corpus.json` — eight new cases (P1-T1 six, P1-T3 one, P1-T5 one)
- `plugin/scripts/fixtures/mutation-waivers.json` — stale keys rewritten or deleted; new waivers
  with arguments
- `plugin/scripts/fixtures/mutation-ratchet.json` — re-based once

**Quick test command for this phase**:

```bash
./plugin/scripts/test-guards
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

## Phase 2: One resolver

### Objective

Give `adversarial-review` a single identity step that Steps 1 and 2 consume, with the fetch as
a disclosed step; land the two Step 3 changes that ride with the same file; add the loop's
stop-table row; validate the descendant case live on PR #25. Close R10-T3, T4, T13, T29.

### Prerequisites

- [x] Phase 1 complete and verified
- [x] Phase 1 manual testing confirmed — *an attestation, like the checkpoint's. Under
      `/wb:implement --auto` it stays `[ ]` and the phase proceeds anyway; the previous phase's
      checkpoint records that nobody was asked. Unticked here means deferred, not blocked.*
- [x] The identity bullet's fixture recipe and its lesson (push the pull ref to the test
      origin) are recorded in `thoughts/2026-09-28-identity-tracer-bullet.md`

### Changes Required

#### 1. The resolver

**File**: `plugin/skills/adversarial-review/SKILL.md`

**Current State** (research.md → `adversarial-review` target resolution): Step 1's
`resolve_range()` (`:105-149`) builds `origin/<base>...origin/<head>` from `gh pr view --json
baseRefName,headRefName` and rewrites the right endpoint to `HEAD` when `headRefName` equals
`git branch --show-current` (`:125`); Step 2 (`:209-229`) repeats the lookup and the same
comparison (`:221`) to set `head_ref`; neither reads `headRefOid` or `isCrossRepository`;
nothing fetches.

**Target State** (design.md → Architecture, "resolves a target's identity once", and Data
Model, "The resolver's output"): one fenced block, before Step 1's range, that binds
`review_head`, `review_base` and `review_provenance`, and that Step 1 and Step 2 read.

**Implementation** — the block's shape, written so `check-guards` shape 6 passes it (no bare
positional; `target` is re-stated per block as today):

```bash
# Re-state Step 1's binding: an argument was given → `target=<it>`; none → leave as is.
target=""
review_head=""; review_base=""; review_provenance=""

resolve_identity() {
  if [ -z "${target:-}" ] || [ -e "$target" ]; then
    b=$(gh pr view --json baseRefName --jq .baseRefName 2>/dev/null)
    review_base="origin/${b:-main}"; review_head="HEAD"
    review_provenance="HEAD (current branch; base ${review_base})"
    return 0
  fi
  if printf '%s' "$target" | grep -qE '^[0-9]+$'; then
    json=$(gh pr view "$target" --json headRefOid,headRefName,baseRefName,isCrossRepository) \
      || { echo "could not resolve PR $target via gh — NOT reviewing" >&2; return 1; }
    oid=$(printf '%s' "$json" | jq -r .headRefOid)
    base=$(printf '%s' "$json" | jq -r .baseRefName)
    cross=$(printf '%s' "$json" | jq -r .isCrossRepository)
    review_base="origin/$base"
    if [ "$cross" != true ] && git merge-base --is-ancestor "$oid" HEAD 2>/dev/null; then
      ahead=$(git rev-list --count "$oid..HEAD")
      review_head="HEAD"
      review_provenance="HEAD, $ahead commit(s) ahead of headRefOid $(printf '%s' "$oid" | cut -c1-7) (PR $target, own checkout)"
      return 0
    fi
    git fetch origin "refs/pull/$target/head:refs/remotes/origin/pr/$target" \
      || { echo "could not fetch refs/pull/$target/head — NOT reviewing" >&2; return 1; }
    review_head="origin/pr/$target"
    review_provenance="origin/pr/$target = $(printf '%s' "$oid" | cut -c1-7), fetched (PR $target is not the current checkout$([ "$cross" = true ] && printf ', cross-repository'))"
    return 0
  fi
  b=$(gh pr view "$target" --json baseRefName --jq .baseRefName 2>/dev/null)
  review_base="origin/${b:-main}"; review_head="$target"
  review_provenance="$target (branch; base ${review_base})"
}
resolve_identity || return 1
for ref in "$review_base" "$review_head"; do
  git rev-parse --verify --quiet "$ref^{commit}" >/dev/null && continue
  echo "range did not resolve: '$ref' is not a revision here — NOT reviewing" >&2
  return 1
done
echo "identity: $review_provenance"
```

Step 1's range becomes `range="$review_base...$review_head"` with its existing pathspec
handling; the old four-branch `resolve_range()` and `base_ref()` are deleted. Step 2's block
becomes `base=$(git merge-base "$review_head" "$review_base" 2>/dev/null)` and its
`head_ref`/`base_branch` lookup (`:211-231`) is deleted. `jq` is already a dependency of the
loop's own blocks; if it is absent where a review runs, the three reads become three
`gh --jq` calls — record which spelling landed under Implementation Discoveries.

**Rationale**: design.md → Architecture and Data Model.
**Pattern Reference**: `adversarial-review/SKILL.md:133-140` (the endpoint loop, kept);
`:160-166` (the `return` rule).

#### 2. Step 3

**File**: `plugin/skills/adversarial-review/SKILL.md:313-323`

**Current State**: `filter=$?` after the `while` loop reads the loop body's last command and
is always 0 (research.md → Shell facts, R10-T13); `--exclude-dir=.context` only, so `.git`
matches land in `callers` (R10-T29).

**Target State**: the search excludes `.git` and `.context`; the dead guard and its prose claim
are removed rather than kept as a check that cannot fire (the acceptance rule: a check that
cannot fail is not evidence).

#### 3. The loop's stop table

**File**: `plugin/skills/adversarial-loop/SKILL.md:70-82` and the Phase 0 rule at `:125`

**Current State**: five rows, all confirmation gates; the own-checkout rule is a branch-name
comparison stated in prose.

**Target State** (design.md → Integration Points): one added paragraph after the table — the
fetch is *disclosed, not confirmed*, names the one ref it writes, and is the same class of
write as any `git fetch`; the Phase 0 rule reads the resolver's `review_provenance` ("a
provenance that is not `HEAD` means the PR phases do not run").

### Tasks

- [x] **P2-T1** — Build the identity fixture and record RED for R10-T3 and R10-T4. Recreate the
      bullet's fixture under `/tmp/wb-identity-fixture/` per
      `thoughts/2026-09-28-identity-tracer-bullet.md` → Fixture (local `patch-1` at commit X;
      fork commit Y as `refs/pull/57/head`, **pushed** to a bare origin; stub `gh` on `PATH`
      answering `--json` queries with `headRefName: patch-1`, `isCrossRepository: true`,
      `headRefOid: Y`, `baseRefName: main`; a second stub mode for R10-T4: same-repository,
      `headRefOid` a commit not present locally but present on the origin as
      `refs/pull/42/head`). Run the **shipped** Step 1 block as written against both: **RED** —
      R10-T3 prints `origin/main...HEAD`; R10-T4 prints `origin/main...origin/<head>` at the
      stale ref. Record `pwd`, `pwd -P` and both outputs verbatim in the task's journal entry.
      Keep the fixture for P2-T2 (delete at P2-T5). (~14 calls) (completed 2026-10-01 03:36)
- [x] **P2-T2** — Land the resolver block per Changes Required §1 and rewire Step 1: delete
      `base_ref()` and the four-branch `resolve_range()` body, keep the pathspec handling and the
      endpoint loop, set `range="$review_base...$review_head"`. Update Step 1's prose:
      the "three outcomes" paragraph gains the refusal and the fetch as named outcomes, and the
      Arguments section's sniff rule is unchanged. **GREEN** against P2-T1's fixture: R10-T3
      prints a refusal naming cross-repository and no `...HEAD`; R10-T4 fetches and prints
      `origin/pr/42 = <oid>, fetched`, and `git status --porcelain` in the fixture is empty
      afterwards. Then `./plugin/scripts/check-guards plugin/skills/adversarial-review/` → clean.
      (~22 calls) (completed 2026-10-01 03:40)
- [x] **P2-T3** — Rewire Step 2 to the resolver: replace the `head_ref`/`base_branch` block
      (`SKILL.md:209-231` today) with `base=$(git merge-base "$review_head" "$review_base"
      2>/dev/null)` and the existing `REVIEW.md` read; update the four-outcomes prose so "read
      from the wrong branch" cites `review_provenance`. **RED** (shape 3):
      `command grep -c 'headRefName' plugin/skills/adversarial-review/SKILL.md` → 2 today (Step 1
      and Step 2); after: 1, the resolver's own read. Against P2-T1's fixture in R10-T3 mode,
      Step 2 never runs because the resolver returned 1; in R10-T4 mode it prints
      `REVIEW.md read from origin/main (merge-base …, head origin/pr/42)`. (~10 calls) (completed 2026-10-01 03:43)
- [x] **P2-T4** — Step 3: add `--exclude-dir=.git` beside `--exclude-dir=.context`
      (R10-T29), and remove the `filter=$?` line, its `FILTER FAILED` echo, and the "details"
      bullet that claims a failed filter announces itself (R10-T13) — the count in the "Seven
      details" heading drops to six and the heading says so. **RED** for R10-T29: in a scratch
      clone with a commit message naming `shellcheck-gate`, the block as written prints
      `./.git/…` hits; after: none. **RED** for R10-T13 (shape 3): `command grep -c 'FILTER FAILED'
      plugin/skills/adversarial-review/SKILL.md` → 1; after: 0, and the bullet count equals the
      heading's number (R7-T8's criterion). (~8 calls) (completed 2026-10-01 03:45)
- [x] **P2-T5** — The loop's row and the live check. In `adversarial-loop/SKILL.md`: add the
      disclosed-not-confirmed paragraph after the stop table per Changes Required §3, and
      rewrite the `:125` own-checkout rule to read `review_provenance`. Then **validate A1
      live**: on this checkout of PR #25, run the resolver block with `target=25` as written;
      **assert** it prints `identity: HEAD, N commit(s) ahead of headRefOid 3b4e04b (PR 25, own
      checkout)` with N equal to `git rev-list --count 3b4e04b..HEAD`, and that no fetch ran
      (`git for-each-ref refs/remotes/origin/pr/` prints nothing). Record the output verbatim
      in the journal, flip A1 to `Validated` with the date in `design.md`. Delete
      `/tmp/wb-identity-fixture/`. (~10 calls) (completed 2026-10-01 03:48)

### Success Criteria

#### Automated Verification

- [x] `./plugin/scripts/check-guards plugin/` → clean (every edited fence: no bare `$1`, no
      `PIPESTATUS`, chained publishes)
- [x] `./plugin/scripts/lint plugin/skills/adversarial-review/*.md plugin/skills/adversarial-loop/*.md` → clean
- [x] One resolution, not two: `command grep -c 'headRefName' plugin/skills/adversarial-review/SKILL.md` → 1;
      `command grep -c 'git branch --show-current' plugin/skills/adversarial-review/SKILL.md` → 0
- [x] The fetch writes one ref: `command grep -c 'refs/pull/\$target/head:refs/remotes/origin/pr/' plugin/skills/adversarial-review/SKILL.md` → 1,
      and no `git checkout`, `git switch` or `git branch -` appears in the skill
- [x] The dead guard is gone: `command grep -c 'FILTER FAILED' plugin/skills/adversarial-review/SKILL.md` → 0
- [x] `.git` is excluded: `command grep -c -- '--exclude-dir=.git' plugin/skills/adversarial-review/SKILL.md` → 1
- [x] `./plugin/scripts/check` → all gates pass

#### Manual Verification

- [ ] A human has read the resolver block as an agent would and agrees each of its four exits
      names what happened — own checkout, fetched, refused (no PR), refused (endpoint)
- [ ] A human has read the stop table's new paragraph and agrees "disclosed, not confirmed" is
      the right class for a fetch

### Modified Files

#### Code Files

- `plugin/skills/adversarial-review/SKILL.md` — the resolver block; Step 1 rewired; Step 2's
  duplicate removed; Step 3's exclusion and dead guard
- `plugin/skills/adversarial-loop/SKILL.md` — the stop table paragraph; the Phase 0 rule
- `design.md` — A1 validated

#### Test Files

- none committed; the fixture is a scratch recipe, recorded in the journal with its outputs

**Quick test command for this phase**:

```bash
./plugin/scripts/check-guards plugin/skills/adversarial-review/ plugin/skills/adversarial-loop/ && ./plugin/scripts/lint plugin/skills/adversarial-review/*.md plugin/skills/adversarial-loop/*.md
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
- [ ] **(attestation)** Manual verification confirmed by human
- [x] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

**Closed unattended (`--auto`), Phase 2, 2026-10-01 03:52 UTC.** Nobody performed the two manual steps: (1) read the resolver block as an agent would and confirm each of its four exits names what happened; (2) read the stop table's new paragraph and confirm "disclosed, not confirmed" is the right class for a fetch. Confirmation is deferred, not obtained. Two items for that reader: a cross-repository PR is fetched and reviewed, not refused, while design.md says "refused by name" in three places and P2-T2's GREEN wording says "refusal"; and the stop-table lead-in says "Four actions stop" above five rows (pre-existing).

---

## Phase 3: CI and close-out

### Objective

Put the generated sweep in CI (Q4), correct the runtime figure, close the ten round-10 tasks
this plan retires with pointers, and observe CI's first run (A3).

### Prerequisites

- [ ] Phase 2 complete and verified
- [ ] Phase 2 manual testing confirmed — *attestation; see the checkpoint block.*
- [ ] The sweep passes locally at the Phase 1 checkpoint's re-based ratchet

### Changes Required

#### 1. The CI job

**File**: `.github/workflows/checks.yml`

**Current State**: one job, `check`, running `./plugin/scripts/check` after asserting `python3`
and installing `shellcheck` and `markdownlint-cli@0.49.0`; `permissions: contents: read`.

**Target State** (design.md → Resolved Decisions, Q4): a second job, `mutation-sweep`, on
`ubuntu-latest`, `actions/checkout@v4`, asserting `python3`, running
`./plugin/scripts/test-guards --generated`. It needs neither `shellcheck` nor `markdownlint`.
Same `permissions` block, stated in the job.

#### 2. The runtime figure

**Files**: `plugin/scripts/README.md:211`, `README.md:319`

**Current State**: "~80 seconds against `check`'s ~20", "deliberately not part of `check`".

**Target State**: the sweep runs in CI on every pull request; locally it takes about four
minutes on the maintainer's machine and has been measured at twelve; still not part of `check`.

### Tasks

- [x] **P3-T1** — Add the `mutation-sweep` job to `.github/workflows/checks.yml` per Changes
      Required §1, with a comment stating why it is a separate job (the sweep is minutes; `check`
      is seconds; Q4). **RED** (shape 4): `command grep -c 'test-guards --generated' .github/workflows/checks.yml`
      → 0 today; after: 1. Validate the YAML with whichever parser is present:
      `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/checks.yml'))"`, or
      `ruby -ryaml -e 'YAML.load_file(".github/workflows/checks.yml")'`. (~6 calls) (completed 2026-10-01 03:53)
- [x] **P3-T2** — Correct the runtime figure and the "not part of check" wording in (completed 2026-10-01 03:54)
      `plugin/scripts/README.md:249-250` and `README.md:365` (the lines moved since this plan was
      written; `README.md` has no runtime figure, only "runs separately, because it is slow")
      per Changes Required §2, and add one sentence to each that the ratchet was re-based on the
      lexer rewrite with the date (2026-10-01, now 378 of 421 killed). Where the same paragraph
      states the old totals (`plugin/scripts/README.md:253`, `README.md:368`), correct those
      figures to the re-based ones so the new sentence does not contradict them. **RED** (shape 3,
      rewritten 2026-10-01 because the original `'80 seconds'` grep cannot match a number that
      wraps across two lines): `command grep -c -- '~80' plugin/scripts/README.md` → 1; after: 0.
      `command grep -c 'CI' plugin/scripts/README.md` rises by at least one, and
      `command grep -c 'CI' README.md` rises by at least one. (~6 calls)
- [x] **P3-T3** — Close the ten held round-10 tasks by pointer. In
      `docs/plans/2026-09-17-adversarial_loop/reviews/2026-09-28-round-10/tasks.md`, flip
      R10-T3, T4, T5, T7, T10, T11, T12, T13, T21, T29 to `[x]` with
      `(closed by docs/plans/2026-09-28-guard_lexer_and_pr_identity <task-id>, YYYY-MM-DD)`
      naming the P1/P2 task that closed each; add a dated line to that round's Implementation
      notes and to `review-log.md`'s round-10 breaker section saying the escalation landed and
      naming this plan's design. Do not touch the fifteen ordinary round-10 tasks. Stage with
      `git add -f`. (~8 calls) (completed 2026-10-01 03:55)
- [x] **P3-T4** — Observe CI's first run (A3). **Push is confirmed with the user first** — this
      is the one outward-facing action in the plan. After the push, read the `mutation-sweep`
      job's log on PR #25: assert its `killed`/`of` equals the local re-based ratchet and it
      reports 0 unwaived survivors. If the numbers differ, A3 is `Invalid` — record the delta in
      `design.md`'s Assumptions row and in Implementation Notes, and stop; do not adjust the
      ratchet to match CI. If they agree, flip A3 to `Validated`. (~6 calls, plus the CI wait) (completed 2026-10-01 04:05)

### Success Criteria

#### Automated Verification

- [x] `command grep -c 'test-guards --generated' .github/workflows/checks.yml` → 1
- [x] `./plugin/scripts/lint --all` → clean
- [x] `./plugin/scripts/check` → all gates pass
- [x] The ten held tasks are `[x]`:
      `command grep -cE '^- \[x\] \*\*R10-T(3|4|5|7|10|11|12|13|21|29)\*\*' docs/plans/2026-09-17-adversarial_loop/reviews/2026-09-28-round-10/tasks.md` → 10,
      and the fifteen ordinary ones are untouched:
      `command grep -cE '^- \[ \] \*\*R10-T' docs/plans/2026-09-17-adversarial_loop/reviews/2026-09-28-round-10/tasks.md` → 15

#### Manual Verification

- [x] The `mutation-sweep` job is green on PR #25 with the local ratchet's numbers (A3) — run 36813275478 on `c6451ff`: 378/421 killed, 43 waived, 0 survived, ratchet held
- [ ] A human has read the two README edits and agrees they state what the sweep is now, not
      what it was

### Modified Files

#### Code Files

- `.github/workflows/checks.yml` — the `mutation-sweep` job
- `plugin/scripts/README.md`, `README.md` — runtime and CI wording

#### Plan Files

- `docs/plans/2026-09-17-adversarial_loop/reviews/2026-09-28-round-10/tasks.md`,
  `docs/plans/2026-09-17-adversarial_loop/review-log.md` — ten tasks closed by pointer
- `design.md` — A3 validated or invalidated

**Quick test command for this phase**:

```bash
./plugin/scripts/lint --all && ./plugin/scripts/check
```

### ⛔ CHECKPOINT: Phase 3 Complete

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

- [x] **(derivable)** Every Phase 3 checkbox is `[x]`
- [x] **(derivable)** All automated verification passing
- [ ] **(attestation)** Manual verification confirmed by human
- [x] **(derivable)** `/wb:update_status` run to reconcile the frontmatter counters — it is the
      only writer of those fields, so do not edit `current_phase` or `completed_tasks` by hand

**Do not proceed without human confirmation of manual tests** — unless the phase is being run
under `/wb:implement --auto`, which buys the wait and not the attestation. In that case the
attestation stays `[ ]`, the checkpoint records that the phase closed unattended and names the
manual steps nobody performed, and the confirmation is **deferred, not obtained.**

**Closed unattended (`--auto`), Phase 3, 2026-10-01 04:05 UTC.** Nobody performed the manual step still open: read the two README edits (`plugin/scripts/README.md`, `README.md`) and confirm they state what the sweep is now. The attestation box stays `[ ]`, deferred and not obtained. P3-T4's push was confirmed with the user before it ran. **This is the final phase, and the plan cannot close itself:** `status: in-progress` to `complete` is `/wb:update_status`'s own barrier, which `--auto` does not reach. A person must run it.

---

## Implementation Discoveries

Things to determine during implementation:

- How many survivors the sweep actually leaves once `depth` is gone (the bullet's 26 included
  ~20 from that field) — P1-T2 records the number beside the prediction.
- Whether `jq` is on `PATH` in every environment the review runs in. The resolver block calls
  it directly to split one JSON read into three values; if absent, three `gh --jq` calls do the
  same. Note which spelling landed.
  - P2-T2: the `jq` spelling landed. There is one `gh pr view --json` read and three
    `jq -r` reads of its output. `jq` was `/opt/homebrew/bin/jq` on the fixture machine.
- Whether A3 holds on the first CI run — the sweep has been measured stable on one machine only.

Note: Update this section with findings as you implement.

---

## 📝 Completed Tasks Archive

Move completed tasks here as phases close, to keep the active list readable.

---

## 🚧 Blockers & Notes

### Current Blockers

Recorded here with the task ID they block and the date raised. Remove a blocker when it is
resolved, leaving a dated line saying how.

- none at plan creation

### Implementation Notes

- **[2026-09-28] Provenance.** This plan is the round-10 escalation the `adversarial_loop`
  breaker demanded; it lands on `adversarial-loop-skill-research` before PR #25 merges (the
  user's decision, 2026-09-28). The ten round-10 tasks it retires are listed in P3-T3; the
  fifteen ordinary round-10 tasks are worked after this plan closes, under that round.
- **[2026-09-28] The seed is scored, not trusted.** `thoughts/spike/candidates/B/check-guards`
  reached 117/117 on the harness; P1-T1 still runs the corpus RED first because the seed
  carries the `depth` field the design removes, and a removal is an edit.
- **[2026-09-29] P1-T1: RED was 117/120, not the predicted 114/120.** The three sweep-gap
  cases pass against the old trackers — they pin mutants of the new `lex()`, not defects of the
  old ones — so only the tracer bullet's three were ever RED. Reproduced independently against
  `HEAD:plugin/scripts/check-guards`. The prediction in P1-T1's text was wrong; the
  implementation was not.
- **[2026-09-29] P1-T1 left `SHELL_INFO` with no curated mutation.** The task named all three
  replacements as `lex()` mutations and pinned the total at 25, so the retired
  `stop scanning sh/shell fences` entry had no slot. P1-T2's sweep will emit a `SHELL_INFO`
  mutant and force it killed or waived — check it there rather than adding a 26th mutation.
- **[2026-09-29] Two stale notes in `test-guards` deferred to P1-T2.** The waiver note at
  `:45-49` describes a `break`/`continue` branch of the old `substitutions()` that `lex()` does
  not have.
- **[2026-09-29] P1-T2: the sweep's corpus grew by six, not zero.** Phase 1's automated bar
  was written as `corpus 122/122` on the assumption P1-T2 would close its survivors with
  waivers alone. Six of them were killable by real input instead, and the task's own rule
  prefers a corpus case over a waiver whenever one exists. The bar is corrected to `128/128`
  above; the count is 126 today and P1-T3 and P1-T5 add one each.
- **[2026-09-29] P1-T2: three waivers asserted an equivalence that valid bash falsifies.**
  All three argued that `stack[0][1]` and `stack[-1][1]` (or a missing `continue`) could not be
  told apart, each on a probe set whose lines all placed `|| true` **inside** the substitution.
  With the guard **outside**, the mutant's end-of-line flush swallows it and an unguarded
  capture reads as guarded: `n=$(`grep -c foo f`; echo z) || true`. Two became corpus cases in
  the escalation; the third was deleted by the coordinator after its mutant turned out to be
  killed by one of them. **The generalisable lesson is about the probe set, not the argument**:
  ten probes that share a hidden assumption cannot fail, which is the knowledge file's "a probe
  that cannot fail is not evidence" in a new costume. An equivalence waiver needs probes that
  vary the thing the argument depends on.
- **[2026-09-29] FOLLOW-UP, not fixed: `strip_comment` truncates a line at a `#` inside a
  substitution.** On `echo "x`grep -c foo f # note`"` the `#` inside the backticks is a real
  shell comment, so the substitution does run an unguarded `grep -c` — but `strip_comment`
  cuts the **whole line** there, discarding the closing backtick, so the span never forms and
  `check-guards` reports nothing. A false negative that blinds the capture detector for the rest
  of the line. Found twice independently during P1-T2 and deliberately left alone: a corpus case
  pinning `expect 0` would pin the bug, and fixing it is not P1-T2's task. Needs its own task.
- **[2026-09-30] FOLLOW-UP, not fixed: `check` does not run the 2.2.0 tests.** The merge of
  `main` (wb 2.2.0) at `37aa8ef` added `test-lint`, `test-prime`, `test-wbte-dictionary`,
  `test-pr-template`, `evals/link_check.py` and `evals/token_check.py`. All six pass, but
  `plugin/scripts/check` runs none of them, so CI does not run them either. The user has not
  decided whether to add them. This is outside this plan's scope.
- **[2026-09-30] FOLLOW-UP, not fixed: `README.md` states old `test-guards` numbers.** It says
  114 corpus cases, 15 integrity checks and 344 of 395 mutants killed (`README.md:357-368`).
  Phase 1 left 128, 16 and 377 of 420. P3-T2 does not cover these lines.
- **[2026-09-30] P3-T2's RED cannot fail.** `command grep -c '80 seconds' plugin/scripts/README.md`
  returns 0 today, because `~80` ends `plugin/scripts/README.md:249` and `seconds` starts the next
  line. `README.md` has no runtime figure since the merge. Rewrite P3-T2's RED before it runs.
- **[2026-10-01] The Phase 1 checkpoint's sweep found a waiver that P1-T3 left stale.** P1-T3
  removed `echo` from `GUARD` and ran only the plain suite, so the "regex drop word boundaries"
  waiver kept the old key. `--generated` reported 1 stale waiver and 1 survivor. `93d5a3b`
  re-keys the waiver and removes `echo` from its reason. The sweep now reports 378/421 killed,
  43 waived and 0 survived. The ratchet rose from 377/420. A task that edits a statement in
  `check-guards` must re-key any waiver on that statement, even if the plain suite passes.
- **[2026-10-01] Phase 1 attestations, and the evidence behind them.** (1) The `lex()`
  docstring: probes in bash and zsh 5.9 confirm six of its eight rules, and `lex()` returns
  the shell's spans on each. The other two (an unclosed `$(` runs to end of line; an unclosed
  backtick yields no span) are the lexer's choices for input the shell rejects. `64ea2d2`
  states this in the docstring. `design.md` → "The shell rules the lexer encodes" still lists
  all eight as the shell's. (2) The P1-T2 waiver deletions: `b1640d7` deleted 13 keys and
  added 5. All 13 named statements of the old `substitutions()` loop, and none of them is
  generated from the code before `b1640d7`, at it, or today. The 5 added keys all match a
  mutant today, and the sweep reports 0 survivors. The commit message says 14 deletions. The
  measured count is 13. The user signed off on both.
- **[2026-10-01] Phase 2 complete using coordinated workers**: 5 workers spawned (sequential), 0 escalations, 0 truncations. The phase closed unattended under `--auto`; the two manual-verification boxes and the checkpoint attestation stay `[ ]`.
- **[2026-10-01] P2-T2: a cross-repository PR is fetched, not refused.** The resolver block in Changes Required §1, the design's Resolved Decisions and the tracer bullet agree on the fetch. P2-T2's GREEN wording ("prints a refusal"), P2-T3's ("Step 2 never runs") and the design's phrase "refused by name" (three places) do not. Only a `gh` failure or a failed fetch returns 1. Reconcile the wording, or change the block, before the plan closes.
- **[2026-10-01] P2-T2: a top-level `return` ends a `zsh -c` call.** The resolver call and the endpoint loop therefore sit inside `resolve_range()`, not at block level as the spec block had them. `jq` spelling landed: one `gh --json` read and three `jq -r` reads.
- **[2026-10-01] P2-T3: Step 2 cannot read `review_head` and `review_base` from Step 1.** Each block runs in a fresh shell. Step 2 re-states both from Step 1's `range:` line, as `target` is re-stated, and stops with `REVIEW.md NOT READ` if either is empty. The design's "neither step re-reads `gh`" holds; "reads the resolver's variables" holds only by that re-statement. A branch target containing `...` would break the by-eye split (unchecked).
- **[2026-10-01] P2-T4: the "Seven details" list had no bullet that was only the filter claim.** The claim was the closing sentence of the path-comparison bullet. The worker removed the sentence and folded the short "guard runs before the output is printed" bullet into the status-capture bullet, so the count reads six.
- **[2026-10-01] P2-T5: A1 validated against a moved PR head.** PR 25's head was 149f233, not 3b4e04b, so the task's literal `3b4e04b` and N=29 could not hold. The resolver printed `HEAD, 4 commit(s) ahead of headRefOid 149f233 (PR 25, own checkout)`, N matched `git rev-list --count`, and no ref was fetched. The four commits are P2-T1 to P2-T4. A1 is marked Validated with that note.
- **[2026-10-01] FOLLOW-UP, not fixed: the stop-table lead-in says "Four actions stop" above five rows** (`adversarial-loop/SKILL.md:~74`).
- **[2026-10-01] Phase 3 complete using coordinated workers**: 3 workers spawned (P3-T1 to P3-T3, sequential), 0 escalations, 0 truncations. P3-T4 had no worker: it pushed `c6451ff` (confirmed with the user) and read the CI log. The phase closed unattended under `--auto`.
- **[2026-10-01] P3-T2: the task's lines had moved and its RED could not match.** The coordinator rewrote the RED before the worker ran (`~80`, and `CI` counts) and extended the task to correct the old totals in the same paragraphs (421 mutants, 378 of 421, 43 waived). `README.md` and `plugin/scripts/README.md` still state 114 corpus cases and 15 integrity claims elsewhere (see the 2026-09-30 note).
- **[2026-10-01] P3-T4: A3 validated.** The first CI run of `mutation-sweep` matched the local numbers exactly. The `check` job also passed on `c6451ff`.

---

## 🔗 Quick Reference

### Key Files

- **Research**: [research.md](research.md) — the lexer, the test apparatus, target resolution,
  the identity facts
- **Design**: [design.md](design.md) — one lexer, one resolver; Q1–Q4 as Resolved Decisions
- **Exploration**: [thoughts/2026-09-28-lexer-and-pr-identity.md](thoughts/2026-09-28-lexer-and-pr-identity.md)
- **Tracer bullets**: [thoughts/2026-09-28-lexer-tracer-bullet.md](thoughts/2026-09-28-lexer-tracer-bullet.md),
  [thoughts/2026-09-28-identity-tracer-bullet.md](thoughts/2026-09-28-identity-tracer-bullet.md)
- **Seed**: `thoughts/spike/candidates/B/check-guards`
- **Main entries**: `plugin/scripts/check-guards`, `plugin/skills/adversarial-review/SKILL.md`

### Common Commands

```bash
# The plain suite — RED/GREEN for every Phase 1 task, seconds
./plugin/scripts/test-guards

# The generated sweep — P1-T2 and the Phase 1 checkpoint only; minutes; background it
./plugin/scripts/test-guards --generated

# The scanner over the edited skill — Phase 2's automated check on prose that executes
./plugin/scripts/check-guards plugin/skills/adversarial-review/ plugin/skills/adversarial-loop/

# Every gate
./plugin/scripts/check

# Progress (scoped to task lines — criteria checkboxes are not tasks)
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md
```

### Design Decisions Reference

- **One `lex()`**, context `(in_single, in_double, escaped)`, every span in close order, the
  eight shell rules in its docstring; stdlib only
- **One resolver**: `headRefOid` + `isCrossRepository`; own checkout means descent; otherwise
  fetch `refs/pull/<N>/head` into `origin/pr/<N>`, disclosed, not confirmed; Step 2 reads the
  same refs
- **The sweep joins CI, not `check`**
- **`zsh` is a shell fence**; a `SKILL.md` fence carries no bare `$1`; blocks `return`, never
  `exit`; `command grep` for measurements; `test-guards --generated` never twice at once
