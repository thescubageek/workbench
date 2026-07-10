---
name: fetch-issues
description: Fetch all open GitHub issues for a repo, research each against the codebase, prioritize them, and write a clippable handoff per issue so any one can be solved in a fresh session. Use when the user says "fetch issues", "triage the open issues", "turn our GitHub issues into handoffs", or gives a repo and asks to prioritize its backlog.
---

# Fetch Issues

Turn a repo's open GitHub issues into a prioritized, research-backed backlog where **every issue is a self-contained, clippable handoff** — copy one, paste it into a new session, and start solving immediately with full context.

## What This Produces

1. A ranked list of every open issue (highest-leverage first).
2. One handoff file per issue under `docs/issues/<date>-<owner-repo>/`.
3. A `README.md` index for that directory with the ranking and a one-line hook per issue.
4. On request, the top handoff (or a chosen one) copied to the clipboard via `pbcopy`.

Each handoff contains a **CLIP block** — a fenced region the user copies verbatim into a fresh session. It carries the problem, acceptance criteria, the codebase locations research found, and a concrete first move, so the new session needs no other context.

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

### Step 2: Research pass (parallel agents)

**⛔ BARRIER 2: Spawn research agents, then wait for ALL to return before ranking.**

For each actionable issue, run a research agent against the codebase. Batch them — spawn agents concurrently (one message, multiple `Agent` calls) for throughput. Use **haiku** for issues that only need file location, **sonnet** for issues needing behavioral tracing.

Each research agent answers, for one issue, **facts only — no fixes yet**:

- **Where** in the code this lives: relevant files with `file:line` references (use `codebase-locator` / `codebase-analyzer`).
- **What exists today**: the current behavior or structure the issue is about.
- **Scope**: how many files/subsystems a fix likely touches.
- **Blockers/unknowns**: missing repro, ambiguous ask, external dependency, needs product decision.
- **Reproducibility** (bugs): can the described behavior be located/confirmed in code?

Prompt template for each agent:

```
Research GitHub issue #<n> "<title>" against this codebase. Facts only, no
recommendations. Report: (1) relevant files with file:line, (2) current
behavior/structure, (3) rough scope in files touched, (4) any blocker or
unknown that would stop someone starting, (5) for bugs, whether the code path
is locatable. Read files fully. Return concise structured notes.
```

Collect all agent outputs before proceeding.

### Step 3: Prioritize

**think deeply about leverage**, then score each issue. Composite score = **Impact × Confidence ÷ Effort**, adjusted by the modifiers below. Rank descending.

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

Produce a ranked table: rank, `#num`, title, category, score, effort, one-line rationale, and blocker (if any).

### Step 4: Write a clippable handoff per issue

**⛔ BARRIER 3: Every handoff must be filled from research — no `[TODO]` or placeholder values in the CLIP block.**

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
rank: <N>
score: <composite>
effort: low | medium | high
blocker: <none | description>
created: <YYYY-MM-DD>
---

# #<number> — <title>

**Rank**: <N> of <total>  ·  **Effort**: <low/med/high>  ·  **Score**: <composite>
**Issue**: https://github.com/<owner/repo>/issues/<number>

## Why this priority
<one paragraph: impact, confidence, effort, and any blocker>

## Research notes
- **Lives in**: `path/to/file.ext:LINE` — <what's there>
- **Current behavior**: <what the code does today>
- **Scope**: <files/subsystems a fix touches>
- **Unknowns / blockers**: <or "none">

---

## 📋 CLIP THIS INTO A NEW SESSION

```text
You are picking up GitHub issue <owner/repo>#<number>: "<title>".
Link: https://github.com/<owner/repo>/issues/<number>

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
<the single most concrete next action — e.g. "Read X fully, reproduce with
`<cmd>`, then write a failing test at `tests/...` before touching `src/...`">

## Constraints
- Follow the repo's existing patterns and TDD (test fails first).
- Scope strictly to this issue — file a new issue for anything else you find.
- When done: reference "<owner/repo>#<number>" in the commit/PR.
```
````

**CLIP block rules:**

- Fully self-contained — a fresh session with zero prior context can act on it.
- Restate the problem; never write "see above" or reference the surrounding file.
- Only cite `file:line` locations that research actually found. If research hit a blocker, say so in the CLIP block and make the first move "resolve the blocker" (e.g. "ask the reporter for a repro").
- Keep it tight: problem, criteria, locations, first move. No essays, no large code dumps.

### Step 5: Index and offer the clipboard

Write `$DIR/README.md`: the ranked table from Step 3, each row linking to its `issue-<n>.md`, plus counts and anything dropped in Step 1.

Then offer to clip:

```bash
# Copy a chosen issue's CLIP block to the clipboard (default: the #1 ranked issue)
# Extract only the fenced text block under "CLIP THIS INTO A NEW SESSION"
pbcopy < <(sed -n '/CLIP THIS/,/^```$/p' "$DIR/issue-<number>.md")
```

Tell the user it's on the clipboard and ready to paste into a new session. Offer to clip any other issue by number.

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

- **Read fully.** Every issue body and every referenced comment — no offset/limit.
- **Facts before fixes.** Research documents what exists; the CLIP block proposes the first move, not a full solution.
- **No silent truncation.** If you cap at the limit or drop issues, say which and why.
- **One issue = one handoff.** Don't merge related issues; cross-link them in "Research notes" instead.
- **Confirm cost above the default limit.** Per-issue research fans out agents; check before processing large backlogs.
- **Don't touch the repo.** This skill reads GitHub and the codebase and writes handoff docs — it does not edit code, comment on issues, or change issue state.
