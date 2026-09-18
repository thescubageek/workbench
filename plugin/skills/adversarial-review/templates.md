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
```

Three rules for it:

- **State the axis that set the tier**, not just the tier. The tier is the maximum of the axes, so
  naming the maximum is naming the reason.
- **Blast radius is measured, not estimated**, and the measurement is shown as the call sites
  found. A search that errored returns the same emptiness as a genuinely isolated change, and the
  error direction is toward believing the change is safe.
- **Name every dropped lens and why.** A silent drop turns a coverage decision into an invisible
  one.

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

`🔴` for CONFIRMED, `🟡` for PLAUSIBLE. This is a restatement, not a second report: the tool's
"do not also print the findings as text" rule is about producing a competing report, and one line
per finding is what the built-in's own prompt prescribes for the same reason.

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
