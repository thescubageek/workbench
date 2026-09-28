---
project: adversarial_loop
created: 2026-09-27
git_commit: 95ffdb4
git_branch: adversarial-loop-skill-research
type: probe record
---

# Two headless probes after round 8

Both run on 2026-09-27 from scratch repositories in `/tmp`, against this checkout's plugin,
headless, backgrounded, ten-minute ceiling. Both are the one-command shape the plan learned to
reach for in P5-T4: `claude -p --plugin-dir <checkout>/plugin --allowedTools=Skill,Read,Bash[,Write] "<instruction>"`
run in a subshell so the session cwd does not move. Fixtures deleted afterwards.

## Probe 1 — a clean round writes nothing (R7-T3's branch)

**Fixture**: `/tmp/wb-probe-clean` (`pwd -P`: `/private/tmp/wb-probe-clean`), bare origin at
`/tmp/wb-probe-clean-origin.git`, `main` pushed, branch `tidy` carrying one docs-only commit
(`README.md`, +2 lines). No `docs/plans/` directory. Instruction: invoke `wb:adversarial-review`
with no arguments, follow through Step 8, report the reconnaissance summary, whether anything
survived, Step 8's exact sentence, and the tree state.

**Result — PASS.** Verbatim from the session:

```
🔎 Reconnaissance — origin/main...HEAD (branch `tidy`), 1 file
   Paths           low    README.md: prose docs, nothing runs it, and no LLM reads it as instructions
   Behaviour       none   adds a blank line and the sentence "A one-line docs change."
   Blast radius    none   measured: `command grep -rnF README` exited 1, filter exited 0, 0 references outside the diff
   Coupling        low    1 subsystem (docs)
   Reversibility   low    fully revertible, no runtime state
   Test evidence   n/a    docs only; `calc.py` is untouched

   Tier: lowest, set by Paths (every axis is trivial)
   Lenses: none (the diff is documentation with no runtime surface) · stance agent (lowest tier, alongside the hunk-scoped built-in)
   Effort: low (precision is enough for a 2-line docs diff)
   Coverage: 1 file / +2 lines resolved  ·  0 lenses + stance agent + the built-in leg
```

- `REVIEW.md` read from `origin/main` at merge-base `2c7dfe1`; absent there, treated as normal.
- Built-in leg `/code-review low`: 0 findings. Stance agent: 0 findings. `ReportFindings` called
  once with an empty array. No coverage shortfall line — the fleet read the whole range.
- Step 8's sentence: *"The round was clean and left no plan by design — nothing survived
  verification, and with no docs/plans directory there is no plan to file a round under."* No
  `tasks.md` written, no `git add -f` run.
- After: `git status --short` empty, `git ls-files --others --ignored --exclude-standard` empty.

What this exercises for the first time: R7-T13's `Coverage:` line (present, no shortfall);
R8-T2's pinned engine (`command grep` appears in the blast-radius measurement); R7-T3's
zero-findings branch and its stated sentence; the two skip reasons for Step 8 arriving together.

## Probe 2 — no `origin/main` fails loudly (Phase 6 manual item, deferred at plan close)

**Fixture**: `/tmp/wb-probe-nobase`, no remote at all, branch `feature` one commit ahead of
`trunk`. Instruction: invoke `wb:adversarial-review` with no arguments, run Step 1 and Step 2's
blocks exactly as written, report stdout and stderr verbatim, whether the range resolved, whether
`REVIEW.md` was read and from where, and where the skill stopped.

**Result — PASS.** Verbatim from the session:

- Step 1 — stdout: nothing. stderr:
  `range did not resolve: 'origin/main' is not a revision here — NOT reviewing`. Exit 1 from
  `return 1` in `resolve_range`. With no target the block took the first branch; `gh pr view`
  found no base, so the fallback was `origin/main...HEAD`, and the `git rev-parse --verify`
  endpoint check rejected `origin/main`. No `range:` line and no `git diff --stat` printed.
- Step 2 — stdout: nothing. stderr:
  `REVIEW.md NOT READ: no base ref resolved from 'origin/main'`. `git merge-base HEAD origin/main`
  returned nothing, so `git show` never ran. **It did not fall back to the index or the working
  tree.**
- Stopped after Step 1. No Step 3, no agents, no findings, no plan.

What this exercises: R7-T6's endpoint verification catching the `base_ref` fallback — the guard
placed for exactly this case doing its job; P6-T1's base-ref read refusing to degrade into a
read of the index, which the Phase 6 manual item asked to see fail rather than silently succeed.

## Not exercised here

The loop's PR phases (design Q4) — running separately against PR #25. A path target wide enough
to trigger the coverage shortfall line: probe 1 confirms the line's absence on a covered range,
not its presence on an uncovered one.
