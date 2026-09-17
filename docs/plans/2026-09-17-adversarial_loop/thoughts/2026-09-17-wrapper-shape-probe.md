---
created: 2026-09-17
type: probe
project: adversarial_loop
task: P1-T2 (pre-registration) · P1-T3 (results) · P1-T4 (verdict)
status: pre-registered
cwd: /Users/scraig/conductor/workspaces/workbench/ankara
fixture: /tmp/wb-adv-probe (bare origin at /tmp/wb-adv-probe-origin.git)
git_commit: d994b1f
git_branch: adversarial-loop-skill-research
---

# Probe: does the wrapper shape hold?

## Why this document is written in two sittings

The pre-registration below was written **before the probe ran**, as P1-T2, and is not edited
afterwards. Results are appended as a separate dated section by P1-T3.

That separation is the whole point. The previous plan's Phase 0 probe recorded `NO PROMPT`
truthfully and concluded wrongly, because nobody wrote down the conditions under which it would
have failed — and its `cwd` was never recorded, so it could not have failed. A probe whose
success criteria are written after its results is not evidence about the world; it is a
description of whatever happened.

## What is being probed, and what is not

A1 is already validated: the `Skill` tool invokes the built-in `/code-review`, which runs forked
and returns findings. That is invocation. It is **not** the shape the design rests on.

Two independent questions remain, and they need different targets:

- **Half A — does content-driven reconnaissance discriminate?** Pure analysis of a diff. Needs no
  built-in leg. Run against the fixture, whose two branches were built to differ on content while
  being close in size.
- **Half B — do two finding sets merge into one verified report?** Needs both legs' real output.
  Run against *this* repository, because `/code-review` resolves its target from the current
  repository and cannot be pointed at the fixture.

**Not probed here**: that a `SKILL.md` file loads and executes this shape. A skill written into
the fixture's `.claude/skills/` is only loadable by a session started in that directory, which
this session cannot do. P5-T4's smoke session covers loading; P5's manual verification carries an
explicit assessment of whether this substitution was adequate.

## The rubric (six axes, tier is the maximum)

Each axis is rated `none` / `low` / `med` / `high`. The tier is the **highest** rating any axis
receives — never an average. Line count is not an axis.

| Axis | `high` when |
| ---- | ----------- |
| 1. Path roles | the diff touches auth/authz, input handling, schema/migrations, config/CI, or dependency manifests |
| 2. Behavioural delta | a guard or validation is deleted, a default changed, a permission or allowlist widened, a new external call or persistence write added, error handling removed or broadened |
| 3. Blast radius | changed symbols have callers outside the diff; specs stub what changed |
| 4. Coupling breadth | the diff spans several distinct subsystems |
| 5. Reversibility | a deploy cannot take it back — migrations, backfills, published API, or a privilege change reachable in production |
| 6. Test evidence | the changed path has no coverage, and none is added |

Mandatory lenses fire on content regardless of tier, and pull the tier up with them: security
(auth, permissions, params, uploads, external calls, PII-shaped data); AI-systems (prompt text,
skill files, agent definitions); data (migrations, backfills); cross-file tracer (a changed
symbol with callers outside the diff).

## Predictions, recorded before running

### `trivial` — `docs/guide.md`, 4 insertions

| Axis | Predicted |
| ---- | --------- |
| Path roles | none — documentation |
| Behavioural delta | none |
| Blast radius | none |
| Coupling breadth | none |
| Reversibility | none |
| Test evidence | none — no runtime surface to cover |

**Predicted tier**: lowest. **Predicted lenses**: none mandatory. **Predicted fleet**: the
built-in at `low` plus one stance agent, per the design's lowest tier.

### `risky` — `app/auth.py`, 6 changed lines

| Axis | Predicted | Why |
| ---- | --------- | --- |
| Path roles | **high** | authorization and params filtering |
| Behavioural delta | **high** | a nil guard deleted; an allowlist widened to admit `owner_id` and `role` |
| Blast radius | med | `can_edit` and `permitted_params` are both called from `app/items.py`, outside the diff |
| Coupling breadth | low | one file, one subsystem |
| Reversibility | med | a privilege widening reachable in production, though not a migration |
| Test evidence | high | the repository has no tests at all; the changed path is uncovered |

**Predicted tier**: highest. **Predicted deciding axes**: path roles and behavioural delta.
**Predicted mandatory lenses**: security (auth + params); cross-file tracer (callers outside the
diff). **Predicted fleet**: materially larger than `trivial`'s.

## Pass/fail conditions, recorded before running

### Half A passes only if all four hold

1. `risky` receives a strictly higher tier than `trivial`.
2. The axis that set `risky`'s tier is named, and is one of path roles or behavioural delta.
3. The security lens fires on `risky` and does **not** fire on `trivial`.
4. The reconnaissance output is legible enough that a human could dispute the rating — per-axis,
   not a bare verdict.

**Half A fails** if the two branches receive the same tier, or if the security lens does not fire
on `risky`. Either result invalidates the max-not-mean tiering decision and PD4.

### Half B passes only if all three hold

1. The built-in leg's output decomposes into per-finding records carrying at least file, line and
   a claim — without guessing at boundaries.
2. The pooled set can be deduped by the built-in's own predicate (same defect, same location, same
   reason), and the outcome is stated: which pairs collapsed, or why none did.
3. The three-state verify runs over the pooled set and changes at least one finding's standing —
   a drop, a downgrade to PLAUSIBLE, or a CONFIRMED with a traced path — demonstrating that
   verification is doing work rather than rubber-stamping.

**Half B fails** if the built-in's output cannot be decomposed into per-finding records without
inventing structure, or if the two legs' findings cannot be compared on a common basis. Either
result invalidates PD3 and pushes the design toward the rejected "thin conductor".

## What a failure would cost

Half A failing unwinds PD4 and the six-axis model, and the reconnaissance pass becomes ceremony.
Half B failing unwinds PD3 and the two-leg architecture. Either sends Phase 2 back to design
rather than forward to implementation. That is the point of spending four tasks here.
