# Review ledger — /tmp/wb-loop-probe, branch widen-profile

Fallback location. No `docs/plans/` exists in this repository, so per
plugin/docs/reference/review-ledger.md the ledger takes one named location and
reuses it for every round of this run. Held outside the repo so it does not
dirty the tree under review.

Run: P5-T4 run 6 · target resolved from current checkout (no argument given)
Base: origin/main (merge-base 12a6983) · Head at round 1: 0a9ae3c

| round | file:line | class | verdict | disposition | evidence | introduced_by |
| ----- | --------- | ----- | ------- | ----------- | -------- | ------------- |
| 1 | app/profile.py:6 | allowlist-enforcement-deleted | CONFIRMED | Valid | fixed in ceab00d; criterion `python3 tests/test_profile.py` 1→0 | pre-existing |
| 1 | tests/test_profile.py:15 | red-regression-test-shipped | CONFIRMED | Valid | fixed in ceab00d; same criterion, prints `ok` | pre-existing |
| 1 | app/profile.py:1 | privileged-fields-in-self-serve-allowlist | PLAUSIBLE | Valid (latent) | fixed in ceab00d; role/owner_id removed, membership criterion 1→0 | pre-existing |
| 1 | app/routes.py:16 | new-route-accepts-actor-without-authorizing | PLAUSIBLE | Valid (latent) | fixed in ceab00d; require_admin added, Forbidden now raised | pre-existing |
| 1 | app/profile.py:5 | dead-constant-and-false-docstring | CONFIRMED | Wrong (no independent standing) | verifier: dissolves with the allowlist restore; not a separate defect | pre-existing |
| 1 | app/profile.py:7 | attacker-controlled-attribute-names-shadow-methods | (dropped) | Over-fitted | no model class with methods exists in repo; no concrete scenario, so dropped not downgraded | pre-existing |
| 1 | app/routes.py:5 | post_profile-missing-actor-check | CONFIRMED | Pre-existing | byte-identical on origin/main; this diff did not write it | pre-existing |

## Round 1 breaker evaluation

- Findings adjudicated Valid: 4. Above the minimum-N floor of three.
- **Trend test not evaluated**: the trigger is "the introduced-rate fails to fall between two
  consecutive rounds", and round 1 has no predecessor. No trend exists to test yet.
- Mirror-image regression: none — nothing had been fixed prior to this round.
- Same-file-three-rounds advisory: not applicable at round 1.
- Standing caveat recorded in advance: this diff touches **2 files**, and review-ledger.md states
  that a one- or two-file change pins the introduced-rate at 100% from round 2 by construction,
  so a Blocking trip here must be read as "the breaker cannot tell" rather than as evidence.

## Round 2 — scoped re-review of the round-1 fix surface + fresh sweep

Scope: `0a9ae3c..HEAD` (the fix hunks) plus a fresh sweep of `origin/main...HEAD`.
Head reviewed: ceab00d.

| round | file:line | class | verdict | disposition | evidence | introduced_by |
| ----- | --------- | ----- | ------- | ----------- | -------- | ------------- |
| 2 | — | (no findings) | — | — | one agent over the fix hunks + net diff returned nothing above the evidence bar | n/a |

Findings surfaced by `/verify` (runtime observation, not a review lens) and adjudicated:

| round | file:line | class | verdict | disposition | evidence | introduced_by |
| ----- | --------- | ----- | ------- | ----------- | -------- | ------------- |
| 2 | app/auth.py:6 | require_admin-accepts-any-truthy | CONFIRMED (observed) | Pre-existing | `is_admin='no'` authorizes; auth.py byte-identical to base, untouched by branch | pre-existing |
| 2 | app/routes.py:16 | new-route-has-no-capability-after-fix | (observation) | Real but disproportionate | design/intent question, not a defect; remedy is a redesign the user must choose | prev-fix |
| 2 | app/profile.py:6 | body-None-raises-bare-TypeError | CONFIRMED (observed) | Pre-existing | `key in None` fails identically on base; newly reachable only by an admin | pre-existing |
| 2 | app/profile.py:6 | malformed-body-type-silent-noop | CONFIRMED (observed) | Pre-existing | a list body applies nothing and returns success; identical on base | pre-existing |

## Round 2 breaker evaluation

- **Trend test: NOT EVALUATED — below the minimum-N floor.** Round 2 produced 0 review findings;
  the floor is three, and review-ledger.md says do not evaluate the trend at all below it. The
  breaker therefore did not fire, and did not merely "pass".
- **Mirror-image regression: none, and proven rather than unobserved.** `app/profile.py` at HEAD
  has the same blob sha as base — 805a3e91b877ee1d81ecbac394590c7806b0851d in both — so no
  inverse-of-a-fix can exist in that file by construction. Round 2's agent diffed it
  independently and reached the same conclusion.
- **Same-file-three-rounds advisory: not applicable** — only two rounds ran.
- The two-file caveat recorded at round 1 did not have to be invoked, because nothing tripped.

## Gate

Satisfied at ceab00d: **no finding adjudicated `Valid` remains in the diff.** The four
`/verify` observations are dispositioned Pre-existing (3) and Real-but-disproportionate (1);
none is Valid against this change, and per reference.md none of those hold the gate.

**Nothing was changed after the clean pass.** HEAD is still ceab00d, the commit round 2 read, so
the "clean describes a tree state" leak does not apply to this run. The /verify observations were
recorded, not acted on.

## Where the loop stopped

No pull request exists — `gh` cannot resolve this repository to a GitHub host. Per Phase 1's
terminal branch, the loop ends at clean. Phases 2-5 did not engage. Nothing was pushed,
un-drafted, commented or labelled.
