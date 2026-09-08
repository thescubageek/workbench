# daily-digest — source recipes

Copy-paste recipes each Phase-1 collector uses to pull its **since-window** slice.
Every recipe is **read-only** and **best-effort**: if the tool is missing or
unauthorized, report `unavailable: <reason>` and return empty — never block the digest.

Conventions:

- `SINCE` = the window start as ISO date (`YYYY-MM-DD`). Default: contents of
  `.context/daily-digest/last-run`, else 24h ago; on Monday with no last-run, the
  previous Friday.
- **Scrub PHI before returning** (see the PHI guardrail in SKILL.md). Return keys,
  numbers, titles, and *categories* — replace any patient identifier / Member ID
  (`(?:BM|BC|BA)-[A-Z]{2}-\d{8}`) with a placeholder.
- Return **structured notes**, not raw tool output.

---

## git / GitHub PRs (`gh`, `git`)

**Identity diverges across sources — do not assume one handle.** The GitHub login
(`gh api user --jq .login`), the Jira/SSO identity (`atlassianUserInfo` email), and
`git config user.email` are frequently three different strings (e.g. GitHub
`thescubageek`, Jira/email `you@company.com`, git a personal address). `@me` in `gh`
resolves to the **GitHub login**, which is correct for `gh` queries — but when you
reconcile a reef PR (authored under the GitHub login) against a Jira ticket (owned
under the SSO identity) in Phase 2, match on **ticket key in the PR title/branch**, not
on author handle. Capture `ME` and prefer the literal login over `@me` in searches so
the identity in play is explicit.

**Run against the work repo, not necessarily `cwd`.** `gh pr list` defaults to the
current repo; if the digest is invoked from a tooling/plan repo, add
`-R <owner>/<work-repo>` (e.g. `-R hellobrightline/reef`) or the PR queries silently
return empty. An empty result from the wrong repo is a false "nothing in flight" — a
gap, not a clean slate.

```bash
gh auth status   # if not authed → unavailable: "gh not authenticated"
ME=$(gh api user --jq .login)   # GitHub login; may differ from Jira/email identity
REPO="${GH_WORK_REPO:-}"        # set to owner/repo when cwd isn't the work repo
R=${REPO:+-R $REPO}             # expands to "-R owner/repo" or empty

# Progress: your merged PRs + commits since window
gh pr list $R --state merged --search "author:$ME merged:>=$SINCE" \
  --json number,title,mergedAt,url
git log --since="$SINCE" --author="$(git config user.email)" --oneline

# Needs review — you owe (blocks others):
gh pr list $R --search "review-requested:$ME -is:draft state:open" \
  --json number,title,url,author,updatedAt
gh pr list $R --search "team-review-requested:$ME -is:draft state:open" --json number,title,url 2>/dev/null

# Needs review — awaiting others on your work; and your PRs needing action:
gh pr list $R --author "$ME" --state open \
  --json number,title,url,reviewDecision,statusCheckRollup,isDraft,updatedAt
# reviewDecision=CHANGES_REQUESTED → Today (address feedback)
# statusCheckRollup has FAILURE → Today (fix CI); reviewDecision="" + not draft → no reviewers assigned yet
```

## beads (`bd`)

```bash
# Fast-fail availability (filesystem only — never `bd doctor`, which can hang).
# See docs/beads-fast-fail.md. Beads is OPTIONAL here: if unavailable, skip + note gap.
if ! { [ "$BEADS_AVAILABLE" = "yes" ] || { command -v bd >/dev/null 2>&1 && [ -d .beads ]; }; }; then
  echo 'unavailable: "bd not installed or .beads/ not initialized"'   # skip, record as gap
fi

# Today (only if available per the check above)
bd ready
bd list --status=in_progress

# Progress: closed since window (bd list is JSONL/table; filter by updated/closed date)
bd list --status=closed --json 2>/dev/null | \
  jq -r --arg s "$SINCE" '.[] | select(.closed_at >= $s or .updated_at >= $s) | "\(.id) \(.title)"'
# Fallback if --json unsupported: bd list --status=closed and filter by the shown date.

bd stats   # headline counts for the pulse line
```

## Jira (Atlassian MCP — `searchJiraIssuesUsingJql`)

Resolve identity once: `atlassianUserInfo`. **Resolve `cloudId` properly — the
site-hostname shortcut is unreliable.** Passing a bare hostname often resolves to a
cloudId that "isn't explicitly granted by the user" and every query fails. Call
`getAccessibleAtlassianResources` first and use the returned `id` (a UUID) as `cloudId`;
cache it. Note the granted host may be prefixed (e.g. `hellobrightline.atlassian.net`,
not `brightline.atlassian.net`) — don't guess it. Use
`responseContentFormat: "markdown"`, `fields: ["summary","status","priority","updated","assignee","issuetype"]`.

**Cap every query.** Set `maxResults` (≤50) and keep `fields` minimal — an unbounded
query over a broad status set (especially any QA/testing status) can exceed the MCP
response token limit and get truncated to a file. Never widen the review query with
catch-all late-stage statuses like `"Ready for Testing"`; those match a large backlog.

**Status vocabulary varies per project — discover it, don't hardcode.** This org's
in-review status is `"Waiting for Review"`, not `"In Review"`. If the review query
returns empty, the status names are likely wrong for the board; check
`getTransitionsForJiraIssue` on a known ticket, or widen cautiously.

```
# Progress — you moved to Done since window:
assignee = currentUser() AND status CHANGED TO ("Done","Closed","Resolved") AFTER "-1d"

# Needs review — your work in review (adjust status names to the board's vocabulary):
assignee = currentUser() AND status IN ("Waiting for Review","In Review","Code Review","In Review (PR)") ORDER BY updated DESC
# reviewer field varies by project; if a "Reviewer"/"Peer Reviewer" custom field exists:
"Reviewer" = currentUser() AND status IN ("Waiting for Review","In Review","Code Review")

# Today — your open-sprint commitments, highest rank first:
assignee = currentUser() AND sprint IN openSprints() AND status IN ("To Do","Open","In Progress","Selected for Development") ORDER BY rank ASC

# Incoming — anything assigned to you updated since window (catches reassignments):
assignee = currentUser() AND updated >= "-1d" AND status NOT IN ("Done","Closed") ORDER BY updated DESC
```

Replace `-1d` with the actual window in Jira duration syntax (`-3d` for a Monday
reaching to Friday). If no Atlassian MCP is connected →
`unavailable: "Atlassian MCP not connected"`.

## Sentry (MCP preferred; REST fallback)

**Prefer the Sentry MCP.** Its tools are deferred/discovered — at run time call
`ToolSearch` with `"sentry issues"` (or `"select:<tool>"` once you know a name) to
load the schemas, then use the issue-search tool. Typical Sentry MCP tools:
`whoami`, an org/project lister, and an issue-search tool taking a Sentry `query`
string. Discover the actual names rather than assuming them.

Query the same two slices with the Sentry search grammar and merge:

- **new**: `is:unresolved firstSeen:-<window>`
- **regressed**: `is:unresolved is:regressed`

Scope to your team's projects; prefer `is:assigned`/`assigned:me` where the tool
supports it. Rank by event count / user count. A regression or a spiking prod error
is **P0-floor** in Phase 3.

**REST fallback** — only if no Sentry MCP is connected. Requires env
`SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, project slug(s); if `SENTRY_AUTH_TOKEN` is unset
AND no MCP → `unavailable: "no Sentry MCP and SENTRY_AUTH_TOKEN not set"`:

```
GET https://sentry.io/api/0/organizations/$SENTRY_ORG/issues/
    ?query=is:unresolved (is:assigned OR assigned:me) firstSeen:-24h
    &statsPeriod=24h&sort=freq
Header: Authorization: Bearer $SENTRY_AUTH_TOKEN
```

**Sentry payloads can contain PHI in event context/breadcrumbs — return only issue
title, culprit, count, and permalink; never event bodies.**

## Notion (Notion MCP connector)

Needs the Notion connector authorized. If not → `unavailable: "Notion connector not authorized"`.

- Search pages/database items **edited since window** where you're assigned or the
  owner (project tracker, RFCs, specs).
- Needs-review: docs/RFCs where you're a reviewer or @-mentioned and status is
  "In review".
- Return page title + URL + status only. **Notion pages may contain PHI — do not
  reproduce body content; reference by title/URL.**

## Gmail (Gmail MCP — `search_threads`)

Needs the Gmail connector. If not → `unavailable: "Gmail connector not authorized"`.
Triage to **actionable, work-relevant** only — do not summarize the whole inbox.

```
newer_than:1d in:inbox -category:promotions -category:social
  (from:github.com OR from:atlassian.net OR from:sentry.io OR from:notion.so
   OR subject:(review OR PR OR "changes requested" OR mention OR blocked OR "action required"))
```

Adjust `newer_than` to the window. For each actionable thread return sender-domain,
subject (PHI-scrubbed), and the action it implies (review X / CI failed on Y /
mentioned in Z). Map GitHub/Jira/Sentry notification emails onto their existing work
item during reconciliation rather than as separate items. **Email bodies may contain
PHI — extract the action, not patient content.**

## Calendar (Google Calendar MCP — `list_events`)

```
list_events for today (primary calendar)
```

Compute **free focus blocks** = gaps between events during working hours → feeds the
Phase 4 window budget. Flag events needing prep (interviews, design reviews, demos)
as their own Today items. Event titles/attendees are generally not PHI, but
**don't reproduce patient-appointment details** if any surface.
