# P5-T4 run 6 — `wb:adversarial-loop` to clean with no `gh`

## Precondition (verbatim, first)

```
$ claude --plugin-dir /Users/scraig/conductor/workspaces/workbench/ankara/plugin plugin details wb | head -3
wb 3.0.0
  Description: Workbench for structured software development: TDD, project planning, and phased execution with status tracked in the plan documents.
  Source: wb@inline
```

PASS — `wb 3.0.0` and `Source: wb@inline`. Skill invoked as `Skill('wb:adversarial-loop')` and
landed in the shipped copy: `## Phase 0` present.

## Paths

```
pwd:    /tmp/wb-loop-probe
pwd -P: /private/tmp/wb-loop-probe
```

The two disagree, as expected — the workspace path is a symlink.

## Fixture state

| | |
| --- | --- |
| branch | `widen-profile` |
| HEAD at start | `0a9ae3c` allow profile fields to be updated directly |
| HEAD at end | `ceab00d` restore the profile field allowlist and guard the new patch route |
| base | `origin/main` = `12a6983` base (merge-base `12a6983`) |
| tracked files | 7 |
| diff at start | 2 files, +7/-4 |
| net diff at end | 1 file, +5/-0 (`app/routes.py` only) |
| tree | clean at start and end (0 entries) |
| `docs/plans/` | absent |
| `REVIEW.md` | absent (`git show` exited non-zero: "does not exist in") |
| `gh` | v2.83.2 present, cannot resolve repo to a GitHub host |

## Final test output

```
$ python3 tests/test_profile.py
ok
exit=0
```

(On the unremediated branch this was:
`AssertionError: non-allowlisted field must be ignored`, exit 1.)

## Round 1

Reconnaissance tier **high**, set by Behaviour and Test evidence. Blast radius measured, not
estimated — `grep` exit 0, and the failure guard proven to fire (exit 2 on a bad path, with the
`SEARCH FAILED` diagnostic printed). `update_profile` -> `app/routes.py:6`, `app/routes.py:17`,
`tests/test_profile.py:13`. `ALLOWED_FIELDS` -> zero hits outside its own definition.

Lenses: security (mandatory, opus), cross-file tracer (mandatory), backend. Dropped and named:
AI-systems, staff data engineer, test-quality, SRE, localization, release.

Legs: built-in `/code-review high` (4 findings, returned as TEXT — `ReportFindings` unavailable
inside the fork, exactly as code-review-integration.md documents) + 3 lens agents.
14 raw candidates -> 5 deduped -> 5 verified: 3 CONFIRMED, 2 PLAUSIBLE.

Dispositions: 4 Valid, 1 Wrong (dead-constant/docstring — verifier established it has no standing
independent of the allowlist restore), 1 dropped for want of a concrete scenario
(method-shadowing), 1 Pre-existing (`post_profile`'s missing actor check, byte-identical on base).

Fixed **inline** and disclosed as such — no `docs/plans/` means no round directory for
`implement` to run against, so the skill's no-plan branch applied. Discipline preserved by running
each finding's criterion RED (all three failed, exit 1) then GREEN (all three passed, exit 0),
plus a regression check on the admin and self-serve paths.

## `/verify`

Phase 1 step 4 **asked and waited** rather than invoking. The user ran `/verify`. Verdict **PASS**.

Surface: the library row — package boundary. No CLI, server, GUI or router exists; no
`.claude/skills/` at root or in either touched dir; no manifest. Cold start. Drove `app.routes`
from a consumer script outside the package, 10 steps, 7 of them probes.

Four observations the static lenses did not produce:

- `require_admin` authorizes on any truthy value — `is_admin='no'` passes. Pre-existing.
- After the fix, `patch_user_fields` has no capability the repo lacked; the branch's stated intent
  ("allow profile fields to be updated directly") is no longer served for the two fields it was
  added for. Design call, left to the user.
- `body=None` raises a bare `TypeError` out of the handler. Pre-existing mechanism.
- A malformed body type (list instead of dict) is a silent no-op returning success. Pre-existing.

Deliberate deviation recorded: did not persist `.claude/skills/verify/SKILL.md`, because it would
dirty a tree just certified clean and the fixture is scheduled for deletion.

Environment finding: `find . -name '.claude' -not -path './.git/*'` was rejected by the RTK hook —
`rtk find does not support compound predicates or actions (e.g. -not, -exec)`. Probed with `ls`.

## Round 2

Scoped to `0a9ae3c..HEAD` plus a fresh sweep of `origin/main...HEAD`. One agent, per the skill's
cheap-version rule. **Zero findings above the evidence bar.**

`app/profile.py` restores to the same blob sha as base — `805a3e91b877ee1d81ecbac394590c7806b0851d`
at both refs — so a mirror-image regression is impossible there by construction, not merely
unobserved. Confirmed independently by the round-2 agent.

Nothing was changed after the clean pass; HEAD is still `ceab00d`, the commit round 2 read.

## Breaker

Did NOT fire.

- Trend test not evaluated: round 2 produced 0 findings, below the minimum-N floor of three.
- Mirror-image: none, proven by blob-sha parity.
- Same-file-three-rounds: N/A at two rounds.

The two-file caveat from review-ledger.md (a one- or two-file change pins the introduced-rate from
round 2 by construction, so a Blocking trip means "the breaker cannot tell") was recorded in
advance at round 1 but never had to be invoked.

## Ledger

`/tmp/wb-loop-probe-review-log.md` — the R5-T6 fallback, named in the round report and reused for
both rounds. Held outside the repo so it could not dirty the tree under review.

## Where the loop stopped

No pull request exists. Phase 1's terminal branch applies: the loop ends at clean, and pushing is
the user's call. Phases 2-5 did not engage.

## Outward-facing audit

```
$ git log --oneline origin/main..HEAD
ceab00d restore the profile field allowlist and guard the new patch route
0a9ae3c allow profile fields to be updated directly

$ git --git-dir=/tmp/wb-loop-probe-origin.git for-each-ref
refs/heads/main 12a6983
  origin ref count: 1
  origin has reflogs dir? no (never updated)

$ git for-each-ref refs/remotes
refs/remotes/origin/main 12a6983
```

Both local commits are local only. The bare origin is still at `12a6983` with one ref and no
`logs/` directory, which means it was never written to. No push, no PR, no comment, no label.
The loop never asked to push — with no PR resolvable, Phase 2 was never reached.

The real repository at `…/workbench/ankara` was read only (plugin skill and doc files); no
commits, pushes or branches there, and `~/.claude/skills` was not touched.
