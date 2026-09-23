# Output shapes

**Read this when a step directs you to.** These are the shapes the review emits. Use them as
given — the parts that look decorative are the parts other tooling and later rounds read.

## The reconnaissance summary

Emitted **before anything is spawned**, so the cost about to be incurred is visible and arguable
before it is paid. A tier asserted without its evidence is a number nobody can dispute.

```text
🔎 Reconnaissance — <target>, <N> files
   Paths           <rating>   <what was seen>
   Behaviour       <rating>   <what the diff does to behaviour>
   Blast radius    <rating>   <measured: callers outside the diff, by symbol>
   Coupling        <rating>   <distinct subsystems touched>
   Reversibility   <rating>   <what a deploy could not take back>
   Test evidence   <rating>   <coverage of the changed path>

   Tier: <tier>, set by <the axis that rated highest>
   Lenses: <lens (trigger)>, <lens (trigger)>  ·  dropped: <lens (why)>
   Effort: <token> — <why that token>
   Coverage: <N> files / <±L> lines resolved  ·  <M> lenses + the built-in leg
```

Four rules for it:

- **State the axis that set the tier**, not just the tier. The tier is the maximum of the axes, so
  naming the maximum is naming the reason.
- **Blast radius is measured, not estimated**, and the measurement is shown as the call sites
  found. A search that errored returns the same emptiness as a genuinely isolated change, and the
  error direction is toward believing the change is safe.
- **Name every dropped lens and why.** A silent drop turns a coverage decision into an invisible
  one.
- **State the resolved range beside the fleet that will read it.** The coverage line is the two
  measurements side by side — the size Step 1 printed, and the fleet just sized from it. A tier and
  a lens count with nothing to scale them against cannot be argued with.

### The coverage shortfall

The coverage line says what was bought. When the fleet is covering more than it read, the report
says that too — one line, emitted alongside the findings, in the voice the built-in uses to
disclose a single-pass run.

```text
⚠️ Coverage shortfall — 81 files / +11,655 lines, 5 lenses + the built-in leg: the lens triggers
   matched 12 files, and the other 69 were reached by the built-in leg alone
⚠️ Coverage shortfall — a 137-line delta read as 948 lines of surrounding file; the lens findings
   rest on more surface than the diff shows
```

Two rules for it:

- **Emit it only when it is true, and never as a score.** A fleet that read its range in full emits
  nothing here; the line's absence is the claim that the pass covered what it names. There is no
  size at which it fires — the trigger is the comparison stated in `SKILL.md` Step 3, not a
  threshold.
- **It discloses, it does not stop.** A range wider than its fleet still runs and is still
  reported. A review that covered less than it claims is the failure this whole skill exists to
  prevent, and saying so costs one line; narrowing the target is the user's act, not the skill's.

## The findings

Emit `ReportFindings` once, with the verified findings ranked most-severe first — an empty array
if nothing survived. The skill must say so explicitly, because the tool gates itself on the active
instructions naming it.

```text
ReportFindings({
  level: "<effort the review ran at>",
  findings: [
    {
      file: "<repo-relative path>",
      line: <1-indexed>,
      summary: "<one sentence stating the defect>",
      short_summary: "<the claim in ≤60 chars, no rationale clause>",
      failure_scenario: "<concrete inputs/state → wrong output or crash>",
      category: "<correctness | simplification | efficiency | reuse | altitude | conventions | test-coverage>",
      verdict: "<CONFIRMED | PLAUSIBLE>"
    }
  ]
})
```

**Every finding carries a `failure_scenario`.** A candidate that reached the report without one
was not verified, and the verify pass drops it rather than lowering its verdict.

### The restatement

After the tool call, restate the findings — one line each — so they survive in sessions that do
not render tool output:

```text
🔴 app/auth.py:14 — deleted nil guard lets an anonymous user match an ownerless record
🟡 app/items.py:7 — widened allowlist admits owner_id, reachable only via the bulk path
```

`🔴` for CONFIRMED, `🟡` for PLAUSIBLE. There is no third glyph: `REFUTED` is dropped and
`STYLE` goes in *Checked and clear*, per [reference.md](reference.md).

**This is a documented deviation, not a reading of the rule.** `ReportFindings` says plainly: call
it once and *do not also print the findings as text*. wb prints one line per finding anyway,
because a forked or non-rendering session otherwise receives nothing — and `adversarial-loop`
adjudicates from what it receives, so a suppressed restatement gives it an empty finding set and a
gate that passes for the wrong reason. The deviation is recorded in
[../../docs/reference/code-review-integration.md](../../docs/reference/code-review-integration.md)
so the two files state one rule between them rather than two.

Its bounds are what keep it a restatement rather than a competing report: **one line per finding,
no failure scenario, no fix, no severity prose.** Anything more is the second report the tool is
telling you not to write.

## Checked and clear

A short list of what was hunted and found to hold, capped at about six lines, factual, never
praise. It exists so the same ground is not re-reviewed next round.

```text
Checked and clear
- Nil handling on the paginated path — `items.py:22` returns early on an empty page
- Idempotency of the retry — the upsert is keyed on the request id, `jobs.py:41`
```

**A clearance is a claim, and it is verified like any other.** This list is not coverage
information; it asserts that something was examined and holds. In this plugin's own probe, one
reviewer explicitly cleared a finding that another raised, and the clearance was wrong — so:

- Each line names the `file:line` that makes it true. A clearance with nothing to point at is an
  impression, and impressions do not go in this list.
- A clearance that contradicts another reviewer's finding is **not** a resolution. Both go to the
  verifier, and the source decides.

Carrying this list alongside `ReportFindings` does not violate the do-not-duplicate rule: these
are not findings, and there is no field for them.

## The remediation plan

Written at `docs/plans/<plan>/reviews/<date>-round-N/tasks.md` — **under** the plan it reviews,
not inside it. Nested one level deeper than `docs/plans/*/`, which is what the session-start
hook globs, so a review's bookkeeping never competes to be the active plan or distorts the
parent's counters. A sibling plan directory would sort newer and silently become the active
plan: a worse defect than the one being fixed. That location is gitignored, so writing the file
is only half of emitting it — stage it with `git add -f`, per
[../../docs/reference/remediation-plan.md](../../docs/reference/remediation-plan.md) →
*Promoting it*.

```text
---
project: <parent plan's project>
reviews: docs/plans/<plan>
round: <N>
created: <date>
status: in-progress
total_tasks: <N>
completed_tasks: 0
task_tracking: markdown-checkboxes
---

# Remediation — adversarial review round <N>

## How each task is verified

Every task carries its finding's `failure_scenario` as its acceptance criterion, and **the
criterion is run before the fix**. A criterion that passes before the change is not a criterion.

## Tasks

- [ ] **R<N>-T1** — `<file>:<line>` — <the finding, one line>.
      **Fails when:** <the failure_scenario, verbatim>.
      **Acceptance (shape <n>)**: <the check, from the taxonomy below>. (~N calls)
```

**The acceptance criterion comes from the shape of the finding**, and where none can be written
the task says so rather than inventing one:

| | Finding shape | Criterion |
| - | ------------- | --------- |
| 1 | Has a fenced command | Execute the block **as written**; assert the stated outcome |
| 2 | Defect in a script | A test case that fails before and passes after |
| 3 | Two files contradict | **Dual grep** — the wrong phrasing absent *and* the right one present at a named `file:line` |
| 4 | Something missing | Grep for presence, plus a negative control proving the grep can fail |
| 5 | Reference integrity | A resolver — dangling links, undefined identifiers, nonexistent skill names |
| 6 | Genuine judgement | **No mechanical criterion.** Label `(attestation)`, name who must look |

**FALSIFY the criterion itself**: *what would this print if the fix were absent?* No answer means
shape 6, not a fabricated check. **Absence is never a check on its own** — a grep returning
nothing passes for wrong path, wrong pattern and wrong encoding as readily as for success.

## When `ReportFindings` is unavailable

Fall back to markdown, and **say that the fallback was used** — a report that looks different for
an environmental reason should say why, not leave the reader to infer it.

```text
## Adversarial review — <target>
Lenses: <a>, <b> · <N> files · <N> confirmed, <N> plausible · reported as markdown (tool unavailable)

### 🔴 CONFIRMED — `app/auth.py:14` — <one-line claim>
**Fails when:** <concrete inputs/state> → <wrong output or crash>
**Fix:** <specific change>

### 🟡 PLAUSIBLE — `app/items.py:7` — <one-line claim>
**Fails when:** <scenario>
**Unverified:** <the link that could not be traced>
**Fix:** <specific change>
```

## Re-reporting after fixes

When findings are fixed later — in this session, by `adversarial-loop`'s next round, or
incidentally — call `ReportFindings` **again** with the same findings, each carrying an `outcome`:

| `outcome` | Means |
| --------- | ----- |
| `fixed` | the change landed |
| `no_change_needed` | the finding was wrong, or already handled |
| `skipped` | real, but deliberately not applied |

Make that call before any prose summary. The host UI's per-finding status updates only from it,
and without it the findings stay marked unresolved. Then give one line per `skipped` finding
saying why — a skip with no reason is indistinguishable from an oversight.
