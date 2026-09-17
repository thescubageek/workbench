---
created: 2026-09-17
type: probe
project: adversarial_loop
task: P1-T2 (pre-registration) · P1-T3 (results) · P1-T4 (verdict)
status: complete — both halves pass
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

---

## Results — 2026-09-17, appended by P1-T3

**Run cwd**: `/Users/scraig/conductor/workspaces/workbench/ankara` (for both halves; the fixture
was measured from `/tmp/wb-adv-probe` via `git -C`/`cd`, recorded per command below).
**Pre-registration above was not edited.**

### Half A — does reconnaissance discriminate? **PASS**

Measured, not asserted. Commands run from `/tmp/wb-adv-probe`.

| Axis | `trivial` | `risky` | Evidence |
| ---- | --------- | ------- | -------- |
| 1. Path roles | none | **high** | `git diff --name-only main trivial` → `docs/guide.md`; `... main risky` → `app/auth.py` (authorization + params filtering) |
| 2. Behavioural delta | none | **high** | `risky` deletes 4 lines: the `if not user.get("id"): return False` guard, and `ALLOWED_PARAMS` widened to admit `owner_id`, `role` |
| 3. Blast radius | none | med | `grep -rn "$sym" --include='*.py'` → `can_edit` 2 call sites outside the diff, `permitted_params` 2, both in `app/items.py` |
| 4. Coupling breadth | none | low | one top-level dir each: `docs` vs `app` |
| 5. Reversibility | none | med | a privilege widening reachable in production; not a migration |
| 6. Test evidence | none | **high** | 0 test files in the repository; the changed path is uncovered |

**Tier**: `trivial` → lowest (every axis `none`). `risky` → **highest** (max = high).
**Deciding axes for `risky`**: path roles, behavioural delta, and test evidence — three tied at
high. **Mandatory lenses fired**: security (auth + params) on `risky`, and the cross-file tracer
(callers outside the diff). Neither fired on `trivial`.

Against the pre-registered conditions: (1) `risky` strictly higher — yes. (2) deciding axis named
and among path roles / behavioural delta — yes, both. (3) security fires on `risky` only — yes.
(4) per-axis output a human could dispute — yes, the table above.

**Six changed lines produced the highest tier.** That is the LOC-is-not-complexity premise
demonstrated rather than argued.

#### The finding Half A produced about itself

The blast-radius axis is the only one requiring a command rather than a read, and **the first run
of that command was silently wrong**. Written as `grep -rn "$sym" --include=*.py .`, zsh
glob-expanded `--include=*.py`, every grep errored, and the surrounding loop still printed
`0 call site(s) outside the diff`. A measurement that failed reported a clean result.

Re-run with the pattern quoted, the true answer was 2 call sites per symbol — enough to trigger
the cross-file tracer that the wrong answer would have suppressed.

**This is a design input, not an anecdote**: the reconnaissance step must confirm its own
measurement ran, not just read its output. A blast-radius grep that errors returns the same `0`
as a genuinely isolated change, and the failure direction is toward under-review.

### Half B — do two finding sets merge into one verified report? **PASS**

Target: this repository's `main...HEAD` plus working tree. Both legs saw the same diff.

**Built-in leg** (`Skill(code-review, "low")`, forked) returned 3 findings:

- **B1** `plugin/skills/daily-digest/sources.md:77` — the open-entry grep has no placeholder
  filter, so it matches the template's fenced example heading; every untouched plan is reported
  as having interrupted work.
- **B2** `plugin/skills/validate_project/reference/validation-rules.md:92` — the placeholder
  filter was added to `openCount` but not to `malformed`.
- **B3** `plugin/skills/research-validation/SKILL.md:4` — the frontmatter repair also widened
  `allowed-tools` to include `Edit`, giving a documented read-only validator write access.

**wb lens leg** (AI-systems lens, mandatory here because the diff touches skill files and prompt
text) returned 2 findings:

- **L1** `validation-rules.md:91` — `startsWith('## ')` silently drops indented or fenced
  headings, and nothing checks for them.
- **L2** `journal-entries.md:69` — "close in place" is stated as a rule with no check that would
  catch a duplicate-heading close; `openCount > 1` counts, it does not scope by task.

#### Dedupe, using the built-in's own predicate

*Same defect, same location, same reason → keep one.* **Nothing collapsed**, and the near-miss is
the informative part: **B2 (line 92) and L1 (line 91) are adjacent lines in the same file and are
different defects** — B2 is a filter not applied to `malformed`; L1 is headings never entering
`journalHeadings` at all. Location proximity is not identity, and a predicate keyed on location
alone would have wrongly collapsed them.

#### The legs contradicted each other

The lens leg listed `daily-digest/sources.md:77` under **"checked and ruled out"**, asserting the
fix "correctly mirror[s] the hook's own filter." The built-in leg reported it as a defect. Both
cannot be right.

Resolved empirically, not by preferring a source:

```bash
printf '## YYYY-MM-DD HH:MM — <task-id or short label> (open)\n' > /tmp/fresh-journal.md
grep -qE '^## .*\(open\)[[:space:]]*$' /tmp/fresh-journal.md   # → matches
grep -cE '^## .*\(open\)[[:space:]]*$' docs/plans/2026-09-17-adversarial_loop/journal.md  # → 3
```

The hook filters placeholders; the grep at `sources.md:77` does not. **B1 CONFIRMED; the lens
leg's clearance was wrong.** A leg that clears a finding is making a claim, and it is as subject
to verification as one that raises it.

#### Verify pass — what it changed

| ID | Entering | Verified | What changed |
| -- | -------- | -------- | ------------ |
| B1 | asserted defect, denied by the other leg | **CONFIRMED** | Contradiction resolved against source; a real shipped bug |
| B2 | asserted defect | **PLAUSIBLE** | Mechanism real (`malformed` is unfiltered) but no triggering input exists: the template's fenced headings end in `(open)`/`(closed)`, so they never reach `malformed` |
| B3 | asserted defect | **finding accepted, remedy rejected** | The widening is real, but `research-validation`'s own Step 4 writes `validation_status` back, so it needed `Edit` to do its documented job. Reverting would restore a skill that cannot perform its stated behaviour |
| L1 | CONFIRMED-mechanism / PLAUSIBLE-impact | **PLAUSIBLE, likely by design** | `validate_project` matches `wb-prime.sh:154` exactly; the gap is coverage, not inconsistency |
| L2 | PLAUSIBLE | **PLAUSIBLE** | No live instance; unchanged |

Against the pre-registered conditions: (1) the built-in's output decomposed into per-finding
records with file, line and claim, without inventing structure — yes. (2) the predicate ran and
its outcome is stated, including why nothing collapsed — yes. (3) verification changed standing —
yes, on four of five: one confirmed against a direct denial, two downgraded, one accepted with
its remedy rejected.

### Verdict

**The wrapper shape holds.** Both halves pass against conditions written before the run.

Three things the probe established that the design had assumed:

1. **Content-driven sizing discriminates on a 6-line diff**, and the deciding axes are the ones
   the design named.
2. **Provenance is genuinely metadata.** B1 came from the built-in and L1 from the lens leg; after
   verification their standing was set by evidence, not by origin. PD3's "pool, dedupe once,
   verify once" is the right shape.
3. **Verification is doing work, not rubber-stamping.** It overturned a leg's explicit clearance.
   Had the design trusted either leg's labels — the rejected "thin conductor" — B1 would have
   shipped as cleared.

One correction to the design's framing: the verify pass must also verify **clearances**, not only
findings. "Checked and clear" is a claim. The design's Data Model treats that list as coverage
information; it is also an assertion that can be wrong, and was.

### Follow-up raised, not fixed here

**B1 is a live defect in already-committed shipped code** (`plugin/skills/daily-digest/sources.md:77`).
It is not P1-T3's task to fix. Recorded against **P4-T2**, which already edits that file.
