---
project: adversarial_loop
reviews: docs/plans/2026-09-17-adversarial_loop
round: 4
created: 2026-09-18
status: complete
last_updated: 2026-09-18
assignee: scraig
current_phase: 1
total_tasks: 8
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
