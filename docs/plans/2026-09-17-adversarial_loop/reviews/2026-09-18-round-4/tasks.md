---
project: adversarial_loop
reviews: docs/plans/2026-09-17-adversarial_loop
round: 4
created: 2026-09-18
status: in-progress
last_updated: 2026-09-18
assignee: scraig
current_phase: 1
total_tasks: 18
completed_tasks: 8
task_tracking: markdown-checkboxes
git_branch: adversarial-loop-skill-research
repository: thescubageek/workbench
---

# Remediation — adversarial review round 4

The first use of the mechanism Q8-1 and Q8-2 decided: a review round emits a **plan**, not a
patch. This one was written by hand because P8-T3 has not yet taught `adversarial-review` to
emit it — so if the shape is awkward here, that is the signal to change the design before it
ships, not after.

**Scope: the `check-guards` / `test-guards` defects only.** Round 4 raised 20 findings; the
other 12 are carried in the parent plan and are not in scope here. This set was pulled forward
because the generated mutator (P8 follow-on) must not run against a tool with known live
defects — you would be hardening the harness around behaviour you are about to change.

## How each task is verified

Per the Q8-2 taxonomy, every task carries the finding's `failure_scenario` as its acceptance
criterion, and **the criterion is run before the fix** — a RED step. A criterion that passes
before the change is not a criterion.

Most of these are shape 2 (a case in the corpus that fails before and passes after). Where a
finding cannot be expressed as a corpus case, the task says which shape it uses and why.

## Tasks

- [x] **R4-T1** — `test-guards:148` mutates the **tracked** `check-guards`; a signal leaves a
      disarmed checker on disk and the next run reads the mutant as its restore baseline.
      **Fails when:** SIGTERM 6s into a ~19s run leaves `if True or GUARD.search(...)` on disk,
      still executable, still exiting 0. Reachable by a CI cancel or a Bash-tool timeout.
      **Acceptance (shape 2 + shape 1)**: mutate a temp copy, never `CG`; assert a sha256 of the
      tracked file is unchanged across a full run; a planted SIGTERM leaves the file intact.
      **First — this is a prerequisite for any larger mutation sweep.** (~12 calls)
- [x] **R4-T2** — `check-guards:241` — `main()` chdirs to the repo root before resolving targets,
      so a relative path scans the workbench tree and reports its file count.
      **Fails when:** from `/tmp/victim`, `check-guards plugin` prints `✅ … (142 files scanned)`
      having never opened `/tmp/victim/plugin/scripts/bad.sh`. The scanned-count guard is
      satisfied by the wrong tree. **Acceptance (shape 1)**: resolve targets to absolute paths
      *before* any chdir; a relative target from another cwd scans that cwd's tree. (~10 calls)
- [x] **R4-T3** — `check-guards:106` — `substitutions()` counts parens without tracking quotes.
      **Fails when:** `n=$(sed 's/)//' f.txt | grep -c foo)` reports clean; and
      `n=$(grep -c ")" f.txt || true)` is falsely reported. **Acceptance (shape 2)**: both as
      corpus cases, one must-fire and one must-not-fire. (~12 calls)
- [x] **R4-T4** — `check-guards:111` — an unpaired backtick `break`s the span scan, discarding
      every later substitution on the line.
      **Fails when:** `echo "100\`" ; n=$(grep -c foo f.txt)` reports clean.
      **Acceptance (shape 2)**: corpus case. (~8 calls)
- [x] **R4-T5** — `check-guards:146` — the `$?` lookahead is unsound in both directions: in
      markdown it indexes the fenced-line list and so hops across fences; in shell it accepts
      any following `$?` regardless of which command it belongs to; and a blank line before a
      genuine test produces a false positive.
      **Fails when:** a capture on the last line of one fence is "guarded" by a `$?` in a later
      unrelated fence; `n=$(grep -c foo f)` then `mkdir -p /tmp/out; rc=$?` is accepted.
      **Acceptance (shape 2)**: three corpus cases — cross-fence, wrong-command, blank-line.
      (~14 calls)
- [x] **R4-T6** — `check-guards:42` — `GUARD`'s trailing `\b` after the `:` alternative can never
      match, so the documented minimum-bar guard is reported.
      **Fails when:** `n=$(grep -c x f) || :` is reported unguarded, blocking CI on correct code.
      **Acceptance (shape 2)**: must-not-fire corpus case. (~7 calls)
- [x] **R4-T7** — `check-guards:159` — a correctly guarded one-line `for` glob is reported, with
      a fix suggestion already present on the line.
      **Fails when:** `for f in docs/*.md; do [ -e "$f" ] || continue; echo "$f"; done` exits 1.
      **Acceptance (shape 2)**: must-not-fire corpus case, plus a must-fire one-liner *without*
      a guard so the fix is not simply "stop checking one-liners". (~11 calls)
- [x] **R4-T8** — `check-guards:62` — a `bash` fence nested inside a `markdown`/`text` fence is
      entered as live shell, defeating the documented escape hatch.
      **Fails when:** the README's own prescribed way to show a counter-example is scanned.
      **Acceptance (shape 2)**: must-not-fire corpus case. Verdict was PLAUSIBLE; confirm or
      refute it first and record which. (~10 calls)

## Tasks — the rest of round 4 (outside `check-guards`)

Ten findings remained after R4-T1..T8. They were deferred, not dropped: the `check-guards`
set was pulled forward because the generated mutation sweep must not run against a tool with
known live defects.

- [ ] **R4-T9** — `daily-digest/sources.md:223` — the shipped patterns match none of the
      variants the same paragraph orders the collector to catch, while `sources.md:15` says
      "match them, do not paraphrase them". **Fails when:** a hand-typed `bm-ca-12345678` —
      the most common form — matches neither regex and reaches the digest.
      **Acceptance (shape 1)**: a probe that extracts the patterns *from the shipped file* and
      runs them against lowercase, no-separator and spaced variants. (~12 calls)
- [ ] **R4-T10** — `adversarial-review/SKILL.md:59` — `$target` is read seventeen times and
      assigned nowhere, so the `if/elif` chain always takes its first branch.
      **Fails when:** executing the Step 1 block verbatim prints `range: origin/main...HEAD`
      for any argument. **Acceptance (shape 1)**: run the block as written with a PR number
      and see it resolve to that PR. (~12 calls)
- [ ] **R4-T11** — `validation-rules.md:155` — the `depends_on` check requires an array; both
      shipped design templates emit a scalar, so it errors on every generated plan.
      **Acceptance (shape 1)**: evaluate the rule against the shipped templates. (~9 calls)
- [ ] **R4-T12** — `validation-rules.md:205` — narrowing `taskLines` made it a subset of `ids`,
      so the missing-ID check computes a negative and is structurally dead.
      **Acceptance (shape 1)**: evaluate both regexes against a plan with an ID-less task.
      (~9 calls)
- [ ] **R4-T13** — `test-guards:158` — a mutation counts as caught whenever the score drops, so
      new false positives are indistinguishable from a broken detector.
      **Acceptance (shape 2)**: require `fn` to rise, and prove it by a mutation that is caught
      only via false positives. (~11 calls)
- [ ] **R4-T14** — `test-count:64` / `test-quiet` — seven of eight planted regressions survived,
      including dropping `--` from `grep -cE --`, which silently returns a wrong count.
      **Acceptance (shape 2)**: a case per regression, each failing before. (~16 calls)
- [ ] **R4-T15** — `reply-to-claude/SKILL.md:100` — the confirm-before-publishing instruction
      sits seventeen lines *after* the `gh pr comment` block it gates.
      **Acceptance (shape 3)**: dual grep — the gate appears before the command, and the
      command is not reachable without passing it. (~8 calls)
- [ ] **R4-T16** — `adversarial-loop/SKILL.md:41` — the flow diagram still states the CONFIRMED
      gate the prose 85 lines below explains is wrong.
      **Acceptance (shape 3)**: the old wording is absent AND the new wording is present.
      (~7 calls)
- [ ] **R4-T17** — `daily-digest/SKILL.md:103` — the orchestrator is told to point collectors at
      `sources.md` but never directed to read it, so the red flag it owns has no matcher.
      **Acceptance (shape 3)**: a directed read exists for the orchestrator. (~8 calls)
- [ ] **R4-T18** — `CHANGELOG.md:147` — the 2.2.0 entry claims the plugin names no employer and
      defers the member-ID format to a repository `CLAUDE.md`; commit `3ce6af9` falsified both.
      **Acceptance (shape 3)**: every claim in the entry is checkable and checks out. (~9 calls)

## Success Criteria

- [ ] `./plugin/scripts/test-guards` — corpus, integrity and mutations all green, with the
      corpus grown by the cases above
- [ ] Every task's criterion was observed to **fail before** its fix (recorded per task)
- [ ] `./plugin/scripts/check` passes
- [ ] No finding fixed without a criterion that can fail

## Not in scope

Round 4's other 12 findings — `$target` unbound, `depends_on` scalar/array, the flow-diagram
contradiction, the PHI variant gap, the changelog claim, the validation-rules dead check, the
reply-to-claude gate ordering, and the `test-count`/`test-quiet` coverage holes. They belong to
the parent plan's remediation and are listed there.
