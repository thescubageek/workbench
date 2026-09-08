---
name: fetch-issues
description: Fetch all open GitHub issues for a repo, reconcile each against PRs and the actual code state, research the genuinely-unaddressed ones, prioritize them, and write a clippable handoff per issue so any one can be solved in a fresh session. Use when the user says "fetch issues", "triage the open issues", "turn our GitHub issues into handoffs", or gives a repo and asks to prioritize its backlog.
---

# Fetch Issues

Turn a repo's open GitHub issues into a prioritized, research-backed backlog where **every issue is a self-contained, clippable handoff** — copy one, paste it into a new session, and start solving immediately with full context.

**The issue tracker is a set of claims to verify, not a source of truth.** An issue being open does not mean the work is undone: it may already be fixed on the default branch, sitting in an open PR awaiting review, or made obsolete by code that already does what it asks. This skill **reconciles issue ↔ PR ↔ code** before ranking anything, so it never hands the user redundant or already-solved work as fresh ready-to-start work.

## What This Produces

1. A **state** for every open issue (`ready`, `fix-in-flight`, `fixed-merged`, `stale-fixed`) derived from PRs, git history, and the code — not from the issue text.
2. A ranked list of the genuinely-**ready** issues (highest-leverage first), with already-handled/in-review issues surfaced *separately and above* the ready ranking so the user isn't handed redundant work.
3. One handoff file per issue under `docs/issues/<date>-<owner-repo>/`.
4. A `README.md` index for that directory with the ranking (including **State** and **Linked PR** columns) and a one-line hook per issue.
5. On request, the top handoff (or a chosen one) copied to the clipboard via `pbcopy`.

Each handoff contains a **CLIP block** — a fenced region the user copies verbatim into a fresh session. It carries the problem, acceptance criteria, the codebase locations research found, and a concrete first move, so the new session needs no other context. When a fix already exists, the CLIP block's first move is "review/merge the existing PR and verify," never "start from scratch."

## When to Activate

- "fetch issues", "triage open issues", "prioritize the backlog"
- "turn the GitHub issues into handoffs so I can knock them out"
- A repo (URL, `owner/repo`, or "this repo") plus an ask to research/rank issues

## Inputs

- **Repo** (optional): `owner/repo`, a GitHub URL, or empty for the current repo.
- **Limit** (optional): max issues to process (default 30; warn and confirm above 50 — research is per-issue and costs tokens).
- **Filters** (optional): labels to include/exclude, e.g. only `bug`, exclude `wontfix`.

---

## Process

### Step 1: Resolve the repo and fetch open issues

**⛔ BARRIER 1: Fetch the full issue set before analyzing anything. No partial passes.**

```bash
gh auth status                      # confirm authenticated; if not, tell the user to run `gh auth login`

# Resolve repo: use the argument, else the current repo
REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"

# Pull all open issues with the fields research needs (exclude PRs — gh issue list already does)
gh issue list --repo "$REPO" --state open --limit 30 \
  --json number,title,labels,assignees,createdAt,updatedAt,author,comments,body
```

Then, for any issue whose body references discussion, pull its comments so nothing is missed:

```bash
gh issue view <number> --repo "$REPO" --comments
```

Read every issue body **fully** — no skimming, no truncation. Note the category of each issue (bug / feature / docs / chore / question) and any labels signalling severity (`security`, `p0`, `regression`) or disposition (`blocked`, `needs-info`, `wontfix`).

**Filter out** issues that are not actionable work: `wontfix`, `duplicate`, `question`/`discussion` with no ask, and anything the user's filters exclude. List what you dropped and why — never silently truncate.

### Step 2: Reconcile each issue against PRs and code state

**⛔ BARRIER 2: Every open issue gets a STATE from the repo before any ranking or research. An open issue is a claim, not a fact — verify it.**

Before assuming an issue is unaddressed work, cross-reference it against pull requests and git history. This is the pass that catches "issue #122 is already fixed in commit `4801b96` on an open PR #172" — the case where naive triage re-researches and hands out work that's already done or in review.

For **each** open issue number `N`, gather evidence:

```bash
# 1. Linked PRs — open AND merged/closed — that mention the issue in title or body
gh pr list --repo "$REPO" --state all --search "$N in:title,body" \
  --json number,title,state,url,headRefName,mergedAt,closingIssuesReferences,body

# 2. The issue's own timeline / linked closing references (when the API exposes them)
gh issue view "$N" --repo "$REPO" \
  --json number,title,state,closedByPullRequestsReferences,timelineItems 2>/dev/null \
  || gh issue view "$N" --repo "$REPO" --json number,title,state

# 3. Git history across ALL branches for closing keywords and bare references
git log --all -i --grep="#$N\b" --oneline
git log --all -iE --grep="(fix|fixes|fixed|close|closes|closed|resolve|resolves|resolved)[^0-9]*$N\b" --oneline
```

For any PR the search surfaces, read its body and commits and look for **closing keywords** tying it to `N` (`fix/fixes/fixed/close/closes/closed/resolve/resolves/resolved #N`). Confirm the PR actually references *this* issue — `#12` is not `#122`; match the whole number.

Then assign each issue exactly one **STATE**:

| STATE | Trigger | What it means for the user |
| ------- | --------- | ---------------------------- |
| **`fixed-merged`** | A merged PR or a commit **on the default branch** closes it (closing keyword or `closingIssuesReferences`). | Work is done and shipped. **Recommend closing the issue** — do NOT write a "go solve this" handoff. |
| **`fix-in-flight`** | An **open** PR, or an unmerged branch/commit, references it. | A fix exists and is awaiting review. Handoff becomes **"review & merge PR #X"** (linked), NOT "start from scratch." |
| **`stale-fixed`** | No PR, but the current code on the default branch **already does what the issue asks** (confirmed in Step 3 research). | Likely obsolete. **Flag as likely-obsolete; recommend verify-and-close.** |
| **`ready`** | No linked PR, no closing commit, and code does not yet satisfy the ask. | Genuinely unaddressed → normal research + handoff. |

Record, per issue: the STATE, the **linked PR number(s) and state**, any **closing commit SHA**, and a one-line evidence note. Issues classified `fixed-merged` or `fix-in-flight` here still get a handoff, but a *reconciliation* handoff (see Step 5), not a research handoff. `stale-fixed` is confirmed in the research pass below (the research question "does the code already satisfy this?" is what promotes a `ready`-looking issue to `stale-fixed`).

### Step 3: Research pass (parallel agents)

**⛔ BARRIER 3: Spawn research agents, then wait for ALL to return before ranking.**

For each issue **not already classified `fixed-merged`** (those need only a close recommendation, not codebase research), run a research agent against the codebase. Batch them — spawn agents concurrently (one message, multiple `Agent` calls) for throughput. Use **haiku** for issues that only need file location, **sonnet** for issues needing behavioral tracing or an "already resolved?" judgement.

Each research agent answers, for one issue, **facts only — no fixes yet**:

- **Already resolved?** — the explicit first question: *does the current code on the default branch already satisfy what this issue asks?* Report a `likely_already_resolved` boolean **with evidence** — a commit SHA, PR number, or `file:line` showing the behavior is already present — not just a hunch. If a PR was flagged in Step 2, check whether its changes are already merged into the working tree.
- **Where** in the code this lives: relevant files with `file:line` references (use `codebase-locator` / `codebase-analyzer`).
- **What exists today**: the current behavior or structure the issue is about.
- **Scope**: how many files/subsystems a fix likely touches.
- **Blockers/unknowns**: missing repro, ambiguous ask, external dependency, needs product decision.
- **Reproducibility** (bugs): can the described behavior be located/confirmed in code — or does the code already handle the reported case?

Prompt template for each agent:

```
Research GitHub issue #<n> "<title>" against this codebase. Facts only, no
recommendations. FIRST answer explicitly: does the current code on the default
branch ALREADY satisfy what this issue asks? Return `likely_already_resolved`
(true/false) WITH concrete evidence — commit SHA, PR #, or file:line proving the
behavior is already present — not a guess. <If Step 2 linked PR #X, add: "PR #X
may address this; check whether its changes are already in the working tree.">
Then report: (1) relevant files with file:line, (2) current behavior/structure,
(3) rough scope in files touched, (4) any blocker or unknown that would stop
someone starting, (5) for bugs, whether the code path is locatable or already
handled. Read files fully. Return concise structured notes.
```

When a research agent returns `likely_already_resolved: true` with solid evidence and the issue had **no** linked PR, promote its STATE from `ready` to **`stale-fixed`**. If the evidence points to a specific merged PR/commit, treat it as **`fixed-merged`** instead.

Collect all agent outputs before proceeding.

### Step 4: Prioritize

**think deeply about leverage.** First **partition by STATE**: `fixed-merged`, `fix-in-flight`, and `stale-fixed` issues are *already-handled* — they do NOT enter the ready-work ranking and are never scored as fresh work. Only **`ready`** issues get the composite score below.

Score each `ready` issue: composite = **Impact × Confidence ÷ Effort**, adjusted by the modifiers below. Rank descending.

| Dimension | High (3) | Medium (2) | Low (1) |
| ----------- | ---------- | ------------ | --------- |
| **Impact** | security, data loss, broken core flow, blocks others | degraded UX, common annoyance | cosmetic, edge case, nice-to-have |
| **Confidence** | clear repro + research located the code | mostly clear, minor unknowns | vague ask, no repro, needs product input |
| **Effort** (inverse) | 1 file / localized | few files / one subsystem | cross-cutting / architectural |

Modifiers:

- **+** labelled `security`/`p0`/`regression` → floor at top tier.
- **−** `blocked`, `needs-info`, or research found a hard blocker → sink below ready work, and say what unblocks it.
- **−** stale (`updatedAt` old) AND low impact → deprioritize.
- **Quick wins** (high impact, low effort, high confidence) surface near the top even if not the absolute highest impact.

Produce a ranked table of the `ready` issues: rank, `#num`, title, category, score, effort, one-line rationale, and blocker (if any). Keep a separate list of the already-handled issues (`fixed-merged` / `fix-in-flight` / `stale-fixed`) with their linked PR and recommended action (close / review-merge / verify-and-close) — these render *above* the ready ranking in the README (Step 6).

### Step 5: Write a clippable handoff per issue

**⛔ BARRIER 4: Every handoff must be filled from reconciliation + research — no `[TODO]` or placeholder values in the CLIP block. A handoff for an already-fixed or in-flight issue must point at the existing PR, not at a from-scratch implementation.**

```bash
DIR="docs/issues/$(date +%Y-%m-%d)-$(echo "$REPO" | tr '/' '-')"
mkdir -p "$DIR"
```

Write `$DIR/issue-<number>.md` for each issue using the template below. The file has two parts: metadata/context for the human triager, and the **CLIP block** they copy into a new session.

````markdown
---
issue: <number>
repo: <owner/repo>
url: https://github.com/<owner/repo>/issues/<number>
title: <title>
category: bug | feature | docs | chore
labels: [<labels>]
state: ready | fix-in-flight | fixed-merged | stale-fixed
linked_pr: <none | #X (open) | #X (merged)>
closing_commit: <none | SHA>
rank: <N | n/a — already handled>
score: <composite | n/a>
effort: low | medium | high
blocker: <none | description>
created: <YYYY-MM-DD>
---

# #<number> — <title>

**State**: <state>  ·  **Linked PR**: <#X / none>  ·  **Rank**: <N of <total> | already handled>
**Effort**: <low/med/high>  ·  **Score**: <composite | n/a>
**Issue**: https://github.com/<owner/repo>/issues/<number>

## State & reconciliation
<one paragraph: the STATE and the evidence for it — linked PR (with state), closing
commit SHA, or the file:line proving the code already satisfies the ask. For a
`ready` issue: "no linked PR or closing commit found; code does not yet satisfy this.">

## Why this priority
<one paragraph: impact, confidence, effort, and any blocker. For already-handled
issues: why it needs no fresh work — just review/merge or verify-and-close.>

## Research notes
- **Already resolved?**: <yes/no> — <evidence: PR #X / commit SHA / file:line, or "no">
- **Lives in**: `path/to/file.ext:LINE` — <what's there>
- **Current behavior**: <what the code does today>
- **Scope**: <files/subsystems a fix touches>
- **Unknowns / blockers**: <or "none">

---

## 📋 CLIP THIS INTO A NEW SESSION

```text
You are picking up GitHub issue <owner/repo>#<number>: "<title>".
Link: https://github.com/<owner/repo>/issues/<number>

## Status
<For ready: "No existing fix found — this is unaddressed.">
<For fix-in-flight: "A fix already exists in PR #X (OPEN): <pr-url>. Do NOT
reimplement — your job is to review and land it.">
<For fixed-merged: "Already fixed and merged (PR #X / commit SHA). This issue
should be CLOSED, not solved — verify then close.">
<For stale-fixed: "The current code already appears to satisfy this (evidence:
file:line / SHA). Likely obsolete — verify then close.">

## Problem
<self-contained restatement of the issue — no "see above">

## Acceptance criteria
- <concrete, checkable outcome 1>
- <concrete, checkable outcome 2>

## Where to work (from research)
- `path/to/file.ext:LINE` — <relevance>
- `path/to/other.ext` — <relevance>

## Current behavior
<what happens today, so the solver knows the starting point>

## Suggested first move
<ready: the single most concrete next action — e.g. "Read X fully, reproduce
with `<cmd>`, then write a failing test at `tests/...` before touching `src/...`">
<fix-in-flight: "Review/merge PR #X (<url>) and verify on staging — check it
meets the acceptance criteria above; do NOT start a fresh implementation.">
<fixed-merged / stale-fixed: "Verify the fix (PR #X / commit SHA / file:line)
against the acceptance criteria, then close the issue referencing it.">

## Constraints
- Follow the repo's existing patterns and TDD (test fails first) — for READY work only.
- If a fix already exists, review/merge it; do not duplicate it.
- Scope strictly to this issue — file a new issue for anything else you find.
- When done: reference "<owner/repo>#<number>" in the commit/PR.
```
````

**CLIP block rules:**

- Fully self-contained — a fresh session with zero prior context can act on it.
- Restate the problem; never write "see above" or reference the surrounding file.
- **Lead with the reconciled Status.** If a fix exists (`fix-in-flight` / `fixed-merged` / `stale-fixed`), the first move MUST be "review/merge PR #X and verify" or "verify and close" — never "write a failing test and start implementing." Only `ready` issues get a from-scratch first move.
- Only cite `file:line` locations that research actually found. If research hit a blocker, say so in the CLIP block and make the first move "resolve the blocker" (e.g. "ask the reporter for a repro").
- Keep it tight: status, problem, criteria, locations, first move. No essays, no large code dumps.

### Step 6: Index and offer the clipboard

Write `$DIR/README.md`. Put already-handled work **first**, then the ready ranking:

1. **`## Already handled / in review — verify & close`** — a table of every `fixed-merged`, `fix-in-flight`, and `stale-fixed` issue: `#num`, title, **State**, **Linked PR**, and recommended action (close / review-merge PR #X / verify-and-close). This section sits ABOVE the ready ranking so the user sees redundant/in-review work first and doesn't pick it up as fresh.
2. **`## Ready to work`** — the ranked table from Step 4, each row linking to its `issue-<n>.md`. Columns: rank, `#num`, title, category, **State**, **Linked PR**, score, effort, one-line rationale, blocker.
3. Counts (ready vs already-handled) and anything dropped in Step 1.

Then offer to clip:

```bash
# Copy a chosen issue's CLIP block to the clipboard (default: the #1 ranked issue)
# Extract only the fenced text block under "CLIP THIS INTO A NEW SESSION"
pbcopy < <(sed -n '/CLIP THIS/,/^```$/p' "$DIR/issue-<number>.md")
```

By default clip the top **ready** issue — never default to an already-handled one. If every issue is already handled, say so plainly ("nothing ready to start — N issues are fixed/in-review, see the verify-&-close list") instead of clipping redundant work. Tell the user it's on the clipboard and ready to paste into a new session. Offer to clip any other issue by number.

---

## Optional: track in beads

If the repo uses beads (`.beads/` present) and the user wants the backlog tracked locally, offer to mirror the ranking:

```bash
bd create --title "<owner/repo>#<n>: <title>" \
  --description "GH issue <url>. Handoff: <DIR>/issue-<n>.md" \
  --type=bug|feature|task --priority=<0-4 from rank>
```

Map rank tiers to priority (top → P0/P1, mid → P2, tail → P3/P4). Don't do this unprompted — it adds local issues the user may not want.

## Guidelines

- **Reconcile before ranking.** The issue tracker is claims to verify, not facts. Every issue gets a STATE from PRs + git history + code *before* it's scored. Never present already-solved or in-review work as fresh ready-to-start work.
- **Match issue numbers exactly.** `#12` ≠ `#122`. When scanning PRs, commits, and grep output for a reference, match the whole number (`\b#N\b`) so you don't mislabel an issue off a coincidental substring.
- **Evidence, not vibes.** `likely_already_resolved` and every already-handled STATE must carry a concrete pointer — PR #, commit SHA, or `file:line`. No pointer → treat as `ready`.
- **Read fully.** Every issue body and every referenced comment — no offset/limit.
- **Facts before fixes.** Research documents what exists; the CLIP block proposes the first move, not a full solution.
- **No silent truncation.** If you cap at the limit or drop issues, say which and why.
- **One issue = one handoff.** Don't merge related issues; cross-link them in "Research notes" instead.
- **Confirm cost above the default limit.** Per-issue research fans out agents; check before processing large backlogs.
- **Don't touch the repo.** This skill reads GitHub and the codebase and writes handoff docs — it does not edit code, comment on issues, merge PRs, or change issue state. Recommending "close this" or "merge PR #X" is advice for the user, not an action the skill takes.
