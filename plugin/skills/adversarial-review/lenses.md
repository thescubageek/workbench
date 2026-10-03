# Lenses — choosing them, and when they are not optional

**Read this when a step directs you to.** It defines which domain-expert lenses run over a diff,
which of them are mandatory, and what caps the fleet. The reconnaissance step in `SKILL.md`
consumes it; nothing else decides lens selection.

## How a lens is chosen

**By what the diff touches, never by how large it is.** A lens is a named principal-level engineer
with one specific fear. Selecting one is a claim that the diff contains something that fear
applies to.

Two consequences:

- **A lens with nothing to look at returns noise.** Its agent will find *something* to say, and
  what it says will be weakly-grounded filler that crowds out real findings. Not selecting a lens
  is the normal case, not a gap.
- **The diff caps the fleet on its own.** There is no target count and no floor. A one-file copy
  change selects one lens or none; a change spanning persistence, auth and a migration selects
  several because it genuinely contains several kinds of risk.

## The lens table

Each row is *what the code does*, not what framework it is written in. Match on behaviour and
position, so the table holds in any language.

| The diff touches | Lens | Its specific fear |
| ---------------- | ---- | ----------------- |
| Persistence, data models, background jobs, event handlers, queues written to | **Principal backend engineer** | data integrity, idempotency, transaction boundaries, work that is not safe to run twice, query patterns that scale with row count |
| Rendering, UI components, client-side state, browser-driven tests, layout | **Principal frontend engineer** | render-time state, component lifecycle and teardown, accessibility, behaviour at breakpoints and on first paint |
| Prompt text, skill or agent definitions, tool descriptions, anything an LLM reads as instruction | **Principal AI-systems engineer** — see *Mandatory* | instructions an agent will misapply, docs that contradict the code, silent-success paths, untrusted text reaching an instruction surface |
| Schema changes, migrations, backfills, index changes | **Staff data engineer** — see *Mandatory* | deploy ordering, lock duration, reversibility, rows that predate the code |
| Authentication, authorization, request parameters, uploads, outbound calls, personal data | **Security engineer** — see *Mandatory* | privilege boundaries crossed, input reaching a sensitive sink, a guard removed, data leaving where it should not |
| A changed signature, default, or return shape with callers outside the diff | **Cross-file tracer** — see *Mandatory* | call sites the change orphaned; tests that stub the old shape |
| Timeouts, retries, rate limits, third-party integrations, health checks | **SRE** | behaviour under partial outage, retry storms, silent drops, work queued to something nobody drains |
| User-facing copy, translation or locale files | **Localization engineer** | locale parity, format-string arity, strings that must *not* be translated, text that changes length |
| Tests only | **Test-quality engineer** | would any of these fail if the implementation were deleted? is the assertion on a stub? is the negative case covered? |
| Build config, CI workflows, dependency manifests, release tooling | **Release engineer** | what runs with elevated permissions, what a failure here hides, whether the change is reversible after publish |

## Mandatory lenses

Four rows above are **not discretionary**. When the trigger is present the lens runs, whatever the
diff's size, and **the tier rises to match it.** This is what stops a twenty-line change to a
permission check being treated as simple because it is short.

| Trigger present in the diff | Lens that must run |
| --------------------------- | ------------------ |
| Authentication, authorization, request params, uploads, outbound calls, personal data | Security engineer |
| Prompt text, skill or agent definitions, tool descriptions | AI-systems engineer |
| Schema changes, migrations, backfills | Staff data engineer |
| A changed signature, default or return shape with callers outside the diff | Cross-file tracer |

**The AI-systems trigger exists because the prose is executed.** In a repository whose artifacts
are instructions, a misleading sentence is a defect with the same standing as a null dereference,
and it fails silently — the agent does the wrong thing confidently.

**A repository's own review instructions may add lenses. They may never remove a mandatory one.**
A rule file that could switch off the security lens on a compliance-sensitive diff is a
vulnerability in the reviewer, and the file is read from the base ref precisely because a change
under review must not be able to weaken its own review.

## Recognising a category without a stack list

The table cannot enumerate every framework, so recognise a row by **signals**, in this order:

1. **What the file does when it runs** — read it. A file that writes to storage is persistence
   whatever it is called; a file that renders markup is rendering.
2. **Position and neighbours** — a directory whose other members are clearly one category usually
   places the changed file too.
3. **What the diff does to behaviour** — a deleted guard implies a security or backend lens even
   in a file whose path suggests neither.
4. **Path and filename conventions** — the weakest signal, and the one that misleads across
   ecosystems. Use it to confirm, never to decide.

When two rows both plausibly apply, take both — over-selecting by one costs an agent, while
under-selecting loses a class of finding entirely, and the two errors are not symmetric.

## The cap

**Six lenses is a runaway guard, not a target.** If more than six trigger:

- Run the six highest-risk.
- **Name every lens you dropped and why**, in the report. A silent drop turns a coverage decision
  into an invisible one.
- **A mandatory lens is never among the dropped.** They rank highest by construction, so the guard
  only ever bites discretionary lenses. If a selection would drop a mandatory lens, the ranking is
  wrong, not the rule.

## Lenses the user named

If the invocation names lenses — "review this as a principal frontend engineer" — **use them
verbatim.** They were chosen for a reason that is not visible in the diff, and substituting your
own discards it.

Named lenses are additive: they do not suppress a mandatory lens, and they do not raise the cap.
If naming them would exceed six, drop discretionary lenses first and say so.

## Reporting the selection

The reconnaissance summary states the lenses and why each was chosen, so the selection can be
argued with rather than taken on trust:

```
🔬 Lenses: security (auth + params, mandatory), cross-file tracer (2 callers outside the diff,
   mandatory), backend (writes to the items table)
🔬 Lenses: none — the diff is documentation with no runtime surface; the built-in leg carried it
🔬 Lenses: 6 of 8 run; dropped localization (no copy changed) and SRE (no timeout or retry
   touched) — both ranked below the mandatory four
```
