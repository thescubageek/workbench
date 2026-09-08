---
name: daily-digest
description: Morning "catch me up + plan my day" orchestrator. Restores active-project context, pulls what changed since yesterday across Jira, beads, git/GitHub PRs, Sentry, Notion, Gmail, and Calendar, then produces a prioritized, session-sustainable day plan — buckets work into Progress / Needs-review / Today / Blocked, assigns each task a complexity→(model, effort, parallelism) tier for cost-optimized results, budgets the day against the rolling 5-hour usage window and your meetings, and hands work off to forge / review skills / fetch-issues with touch-grass pacing (including breaks). Use at the start of a work session, or when the user says "daily digest", "morning digest", "catch me up", "what should I work on today", "start my day", "plan my day", "standup for myself".
argument-hint: "[since-date?] [project-or-ticket?]"
---

# Daily Digest

The first thing you run each morning. Restore context fast, see everything that
moved since you last worked, and leave with a **paced, prioritized plan** you can
execute all day without blowing the 5-hour usage window — hyper-focused, maximally
fanned out, and cost-optimized per task.

**Core principle:** A good morning digest replaces the 20 minutes you'd spend
tab-hopping across Jira/GitHub/Sentry/email with one reconciled picture — *the same
work item seen from six tools is one line, not six* — and turns that picture into a
plan that assigns the right model + effort to each task and paces the day so quality
never degrades and the window never runs dry.

This skill **orchestrates** the wb ecosystem; it does not re-implement it. It hands
plannable tickets to `forge`, reviews to the review skills, GitHub backlog to
`fetch-issues`, and paces long fan-out days with `touch-grass`.

## The Iron Law

```
RECONCILE BEFORE YOU RANK. NEVER WRITE PHI. ALWAYS LEAVE A CONCRETE FIRST MOVE.
```

- **Reconcile before you rank** — one work item may appear as a Jira ticket, its PR,
  its beads issue, and a Sentry error. Group them into ONE item before prioritizing,
  or the day plan double-counts and misleads.
- **Never write PHI** — see [PHI guardrail](#phi-guardrail). This is a HIPAA-covered
  org; the sources this skill reads (email, Jira, Sentry, Notion) can carry patient
  data. The digest and every `.context/` file it writes must be PHI-free.
- **A digest with no first move failed.** The deliverable is not a status report; it's
  a plan. Every "Today" item ends in a concrete next action and its effort tier.

## When to activate

- Start of a work session / "start my day", "plan my day", "catch me up".
- "daily digest", "morning digest", "what should I work on today", "self standup".
- After time away (returning from PTO → widen the window to "since I last worked").

Not for: a single ticket's context (use `jira-context`), triaging a GitHub backlog
in isolation (use `fetch-issues`), or executing one ticket (use `forge`).

## Inputs (infer, don't interrogate)

1. **Window** (`$1`, optional) — how far back "since yesterday" reaches. Default:
   since the **last digest run** (read `.context/daily-digest/last-run`), else 24h.
   **Weekend-aware:** on a Monday with no last-run, reach back to Friday morning.
   Returning from time off → the user says so; widen accordingly.
2. **Focus** (`$2`, optional) — a project dir or ticket to center the day on. Default:
   auto-detect the active project (Phase 0).
3. **Identity** — the current user (for "assigned to me" / "review-requested:@me"
   queries). Derive from `git config user.email`, `gh api user`, and
   `atlassianUserInfo`; don't ask.

---

## Phase 0 — Restore context (fast, local, ~1 min)

Rebuild "where was I" before reaching for any network source. All local:

```bash
git branch --show-current
git log --oneline -10 --author="$(git config user.email)"
git status --short
```

- **Active project:** most-recently-modified dir under `docs/plans/`; cross-check
  against the current branch name and any in-progress beads.
- **In-flight work:** `bd list --status=in_progress` and `bd ready` (top few).
- **Last handoff:** newest `docs/plans/**/handoff*.md` or `.context/**` — read it
  FULLY if present (this is the highest-signal context restore).
- **Last digest:** read `.context/daily-digest/<prev-date>.md` if present — yesterday's
  "Today" list is the baseline you diff against.

Emit nothing yet. Hold this as the frame that aims Phase 1.

## Phase 1 — Gather (parallel fan-out, read-only)

**⛔ BARRIER 1: Spawn one collector per available source, then wait for ALL before
reconciling.** Collectors are read-only and independent — fan them out concurrently
(one message, multiple `Agent` calls) for speed and cost. Use **haiku** for
mechanical pulls (git, PR lists, calendar) and **sonnet** for sources needing
judgement (email triage, Sentry severity, Notion relevance).

Each collector pulls the **since-window** slice for its source and returns
**PHI-scrubbed, structured notes** — never raw dumps. The exact per-source query
recipes (with env vars and fallbacks) live in [sources.md](sources.md); point each
collector at it. Sources and what each contributes:

| Source | Tool | Progress (done) | Needs review | Today / incoming |
| --- | --- | --- | --- | --- |
| **git / GitHub PRs** | `gh`, `git` | your merged PRs + commits since window | `review-requested:@me`; your PRs with new comments/failed CI | draft/changes-requested PRs to finish |
| **beads** | `bd` | issues closed since window | issues in a review state | `bd ready`, `bd list --status=in_progress` |
| **Jira** | Atlassian MCP | issues you moved to Done since window | `assignee=me AND status="In Review"`; where you're reviewer | open-sprint issues assigned to you, by rank |
| **Sentry** | Sentry MCP (REST fallback) | issues you resolved | — | new / regressed / spiking issues in your projects since window |
| **Notion** | Notion MCP | pages/db items you completed | docs/RFCs awaiting your review | tracker items assigned to you, updated since window |
| **Gmail** | Gmail MCP | — | review requests, mentions, CI/Sentry/Jira notifications needing action | actionable threads since window |
| **Calendar** | Calendar MCP | — | — | today's events → **free-focus-time budget** + prep needed |

**Source availability is best-effort.** If a source's tool is unavailable or
unauthorized (Notion connector not authed, no Sentry MCP/token, no Atlassian MCP),
the collector reports `unavailable: <reason>` and returns empty — **never block the
digest on one source.** Log every skipped source as an explicit gap (see Iron Law of
`touch-grass`: no silent cuts).

Collect all collector outputs before Phase 2.

## Phase 2 — Reconcile & bucket

**⛔ BARRIER 2: Deduplicate across sources into unified work items BEFORE ranking.**

The same work shows up in many tools. Group them: match on ticket key in branch/PR
names, PR↔issue closing refs, beads issue titles referencing a Jira key, Sentry
issue linked to a ticket, email subjects quoting a key. One **work item** = one row,
carrying all its source links.

Then assign each unified item to exactly one bucket:

- **✅ Progress (since window)** — merged/closed/resolved/done. Celebrate briefly;
  this is the diff against yesterday's plan, not today's work.
- **👀 Needs review** — split into *you owe a review* (blocks others — usually
  highest urgency) and *awaiting others' review of your work* (nudge-worthy).
- **🎯 Today** — ready or in-progress work: sprint commitments, `bd ready`, PRs with
  changes requested, actionable email/Sentry items.
- **⛔ Blocked** — waiting on a dependency, decision, or someone else. Note what
  unblocks each.

## Phase 3 — Prioritize + effort/model advisory

**think deeply about leverage and cost.** Rank the **Today** bucket, then tag each
item with the model + effort that fits its *hardest* sub-problem — not its average.

Priority = **Impact × Urgency ÷ Effort**, with floors: *reviews that block others*
and *P0/security/prod-down (Sentry regressions, `security`/`p0` labels)* float to the
top; blocked items sink with a note on what unblocks them.

### Complexity → model + effort rubric

Match the tool to the task. Cheap tasks fan out in parallel; expensive reasoning is
serialized and focused. This is the cost-optimization lever.

| Complexity | Signals | Model | Effort | Fan out? |
| --- | --- | --- | --- | --- |
| **Trivial / mechanical** | rename, doc/comment fix, lint, dependency bump, copy change, single obvious line | `haiku` | `low` | ✅ heavily — batch in parallel subagents/workspaces |
| **Moderate** | localized bug fix, single-file feature, writing tests for known behavior, straightforward PR review | `sonnet` | `medium` | ✅ 2–3 at once if independent |
| **Complex** | cross-cutting change, ambiguous requirements, new subsystem, non-trivial refactor, security-adjacent, tricky review | `opus` | `high` | ⚠️ serialize — needs your attention |
| **Critical / novel** | architecture decision, data-integrity/prod risk, novel algorithm, high-blast-radius, one-way door | `opus` | `xhigh`→`max` | ❌ one at a time, full focus |

Guidance:

- **Size to the hardest sub-problem.** A "simple" ticket with one gnarly decision is
  Complex, not Moderate.
- **Reserve `opus`/`xhigh`+ for the one or two hardest items of the day.** Burning max
  effort on mechanical work is the most common cost waste.
- **Uncertain which tier?** Fire a `tracer-bullet` first — one cheap probe at the
  riskiest assumption often collapses a "Complex" into a "Moderate" (or reveals it's
  a "Critical" one-way door before you commit).
- **Reviews:** most PR reviews are Moderate (`sonnet`/`medium`); a security or
  architecture review is Complex+.

## Phase 4 — The session-sustainable day plan

Turn the ranked, tagged list into a **paced plan** that maximizes fan-out without
exhausting the rolling **5-hour usage window** or ignoring your calendar.

1. **Budget the window.** Compute free focus time from Calendar (today's events →
   gaps). The 5-hour usage window is a *rolling* limit; heavy parallel fan-out and
   `opus`/`xhigh` work drain it fastest. Plan the day as **waves**:
   - **Wave 1 (window fresh):** front-load the highest-leverage Complex/Critical item
     while you're sharp and the budget is full — one focused stream.
   - **Wave 2 (parallel):** fan out the batch of Trivial/Moderate independent items
     across subagents/parallel workspaces — cheap, concurrent, high throughput.
   - **Touch grass:** schedule a real break at/near the window boundary — it doubles
     as a usage-window reset. Don't grind through the boundary; quality degrades and
     the window stalls you anyway.
2. **Respect meetings.** Slot deep-focus items into the largest calendar gaps; put
   short reviews/mechanical batches into the fragments between meetings. Flag any
   meeting that needs prep as its own Today item.
3. **Pace with `touch-grass`** when the day's load clearly exceeds one window or one
   sitting: check its budget/pacing discipline into effect, checkpoint the plan to
   `.context/daily-digest/<date>.md`, and use `ScheduleWakeup` to resume the next wave
   after a break/window-reset. Only do this for genuinely multi-window days — a normal
   day doesn't need the ceremony.
4. **Wire each Today item to its entry point:**
   - Plannable ticket → `/wb:forge <ticket>` (research → design → execution).
   - A ticket you'll pick up → `/wb:jira-context <KEY>` first to hivemind off it.
   - PR review you owe → `pr-feedback` / `review` / `review-reef` per its size.
   - GitHub backlog to knock out → `fetch-issues`.
   - Long analysis/audit → `touch-grass`.

## Phase 5 — Write the digest, offer the first move

1. Write the digest to `.context/daily-digest/<YYYY-MM-DD>.md` using
   [digest-template.md](digest-template.md). **PHI-free** (see guardrail). This is the
   durable artifact — a cold context (or you at 2pm) can reload the plan from it.
   **Every PR / ticket / Sentry reference is a clickable markdown link** to the URL its
   collector returned (`gh` `url`, Jira `webUrl`, Sentry permalink) — the digest is a
   click-through launchpad, not just a status list. Preserve these URLs through Phase 2
   reconciliation so a merged work item keeps all its source links.
2. Record the run: write today's ISO date to `.context/daily-digest/last-run` so the
   next digest's window starts here.
3. **Present tightly.** Lead with the headline, not the process:
   - One-line pulse: *"N done since Friday · M need your review (K block others) ·
     P for today · Q blocked."*
   - The ranked **Today** table with effort tiers.
   - The **first move** — the single highest-leverage action right now — and offer to
     start it (`forge` it / clip it / open the review). Don't make the user ask.
4. Note every **gap** (sources that were unavailable) so the picture's edges are honest.

---

## PHI guardrail

**Brightline is a HIPAA-covered behavioral-health org.** Gmail, Jira, Sentry, and
Notion routinely contain Protected Health Information. This skill reads those sources
to *plan work*, and MUST NOT surface or persist PHI.

- **Never write PHI** into the digest, `.context/` files, `bd` issues, commit
  messages, or clipboard. Refer to work by ticket key / PR number / issue title —
  never by patient name, DOB, address, contact info, or **Member ID**
  (`(?:BM|BC|BA)-[A-Z]{2}-\d{8}` and obvious variants).
- **Collectors scrub at the source.** Instruct each collector to return
  identifiers/subjects and *categories* of content, not PHI values. If a Jira summary
  or email subject embeds a patient identifier, replace it with a placeholder
  (`[PATIENT]`, `[MEMBER_ID]`, `[DOB]`) and reference the item by its key/number.
- **When a work item can't be described without PHI**, name it by its key/number and
  note "details in source (contains PHI — not reproduced here)."
- If genuine PHI *processing* is ever required, that's out of scope for a digest —
  route to the approved BAA-covered workflow, don't improvise.

## Quality moves

- **Honest edges.** Every unavailable source is a listed gap, never a silent omission.
  A digest that quietly skipped Sentry looks complete but isn't.
- **Diff, don't restate.** Progress is measured against yesterday's plan — surface
  what *changed*, not the full board state.
- **One first move.** If you can only give the user one thing, give the single
  highest-leverage next action, fully specified with its effort tier.
- **Re-runnable.** Running twice in a day = "what changed since the last run," not a
  duplicate morning report.

## Red flags — STOP

- Ranking before reconciling (the same work counted 3×).
- Any patient identifier or Member ID in the digest or a `.context/` file.
- A "Today" list with no effort tiers or no first move.
- Assigning `opus`/`xhigh` to mechanical work, or `haiku` to an architecture decision.
- Silently dropping a source that failed to load.
- Planning a full day of heavy fan-out with no break/window-reset — you'll stall
  mid-afternoon.

## Integration with the wb ecosystem

- **`forge`** — the execution entry point for each plannable Today ticket.
- **`jira-context`** — bootstrap a ticket's context before forging it.
- **`fetch-issues`** — when the day's work is "knock out the GitHub backlog."
- **`touch-grass`** — the pacing engine for multi-window days; daily-digest sets up
  the plan, touch-grass sustains it across breaks/window-resets.
- **`tracer-bullet`** — fire before committing to a Complex/Critical item whose tier
  is uncertain.
- **review skills** (`pr-feedback`, `review`, `review-reef`, `review-strict`) — the
  entry points for the Needs-review bucket.
- **`status-sync`** — end-of-day counterpart; daily-digest opens the session,
  status-sync helps close it clean.
