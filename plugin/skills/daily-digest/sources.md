# daily-digest — source recipes

Copy-paste recipes each Phase-1 collector uses to pull its **since-window** slice.
Every recipe is **read-only** and **best-effort**: if the tool is missing or
unauthorized, report `unavailable: <reason>` and return empty — never block the digest.

Conventions:

- `SINCE` = the window start as ISO date (`YYYY-MM-DD`). Default: contents of
  `.context/daily-digest/last-run`, else 24h ago; on Monday with no last-run, the
  previous Friday.
- **Scrub PHI before returning.** Return keys, numbers, titles, and *categories* —
  replace any patient identifier or Member ID with a placeholder (`[PATIENT]`,
  `[MEMBER_ID]`, `[DOB]`). The patterns are in *PHI patterns* at the bottom of this file;
  match them, do not paraphrase them.
- Return **structured notes**, not raw tool output.

---

## git / GitHub PRs (`gh`, `git`)

**Identity diverges across sources — do not assume one handle.** The GitHub login
(`gh api user --jq .login`), the Jira/SSO identity (`atlassianUserInfo` email), and
`git config user.email` are frequently three different strings (e.g. GitHub
`thescubageek`, Jira/email `you@company.com`, git a personal address). `@me` in `gh`
resolves to the **GitHub login**, which is correct for `gh` queries — but when you
reconcile a work-repo PR (authored under the GitHub login) against a Jira ticket (owned
under the SSO identity) in Phase 2, match on **ticket key in the PR title/branch**, not
on author handle. Capture `ME` and prefer the literal login over `@me` in searches so
the identity in play is explicit.

**Run against the work repo, not necessarily `cwd`.** `gh pr list` defaults to the
current repo; if the digest is invoked from a tooling/plan repo, add
`-R <owner>/<work-repo>` (e.g. `-R acme/widgets`) or the PR queries silently
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

## wb plans (`docs/plans/`)

```bash
# Plan state comes from the plan documents; there is no tracker to query.
# Scope counts to lines carrying a task ID — criteria and prerequisites are
# checkboxes too, and counting them inflates progress.
# `grep -c` prints 0 AND exits 1 on no match, and an unmatched glob leaves $T as the
# literal pattern, so an unguarded count yields an EMPTY string and the -gt test then
# errors instead of reporting. A measurement that failed must not read as a clean zero.
for T in docs/plans/*/tasks.md; do
  [ -e "$T" ] || continue
  done=$(grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' "$T" 2>/dev/null) || true
  left=$(grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' "$T" 2>/dev/null) || true
  [ "${left:-0}" -gt 0 ] && echo "$T: ${done:-0} done, ${left:-0} left"
done

# Today: the first unchecked task in the active plan's current phase
# Progress: tasks whose (completed YYYY-MM-DD ...) stamp falls inside the window
grep -nE '^- \[x\] .*\(completed '"$SINCE" docs/plans/*/tasks.md

# In flight: the NEWEST journal entry being open means work was interrupted mid-task.
# Two things this must get right, both learned from getting them wrong:
#   - discard the template's placeholder headings, or every untouched plan reports
#     interrupted work forever (the hook discards them the same way);
#   - read the NEWEST entry, not any entry — a stale open entry further down is a
#     bookkeeping error, not work in flight.
for J in docs/plans/*/journal.md; do
  [ -e "$J" ] || continue
  newest=$(grep -E '^## ' "$J" 2>/dev/null | grep -vE '\[YYYY|<YYYY|YYYY-MM-DD' | head -1)
  # Normalize the way wb-prime.sh does before testing the suffix. A bare case match is
  # case-sensitive and whitespace-strict, so `(OPEN)` or one trailing space reads as closed
  # here while the hook reports it open — two surfaces disagreeing on the same file.
  case "$(printf '%s' "$newest" | tr 'A-Z' 'a-z' | sed 's/[[:space:]]*$//')" in
    *'(open)') echo "$J: $newest" ;;
  esac
done

# Blocked: the plan says so itself
sed -n '/^### Current Blockers/,/^###/p' docs/plans/*/tasks.md
```

## Jira (Atlassian MCP — `searchJiraIssuesUsingJql`)

Resolve identity once: `atlassianUserInfo`. **Resolve `cloudId` properly — the
site-hostname shortcut is unreliable.** Passing a bare hostname often resolves to a
cloudId that "isn't explicitly granted by the user" and every query fails. Call
`getAccessibleAtlassianResources` first and use the returned `id` (a UUID) as `cloudId`;
cache it. Note the granted host may carry a prefix the shorter name does not (e.g.
`acmecorp.atlassian.net`, not `acme.atlassian.net`) — don't guess it. Use
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

## PHI patterns — canonical

**These live here, in the file the collectors are handed.** A collector is the surface that
touches a raw payload, so a pattern it cannot see is a pattern that does not run. This block was
briefly moved to `SKILL.md` to stop two copies drifting; that removed it from the only surface
that needed it, which is the more dangerous of the two failures — the digest was still written,
still reported clean, and carried whatever the collector had no pattern to catch.

`SKILL.md`'s PHI guardrail states the *rules* and points here for the *patterns*. One copy, in
the place both readers reach: the orchestrator reads this file too.

Scrub anything matching either pattern, plus obvious variants — lowercase, missing or extra
separators, surrounding punctuation:

```text
(?:BM|BC|BA)-[A-Z]{2}-\d{8}        # the canonical form this rule was written against
\b[A-Z]{2}-[A-Z]{2}-\d{6,10}\b     # the general shape, for formats not enumerated above
```

A repository may **add** its own format in its `CLAUDE.md`. It may not narrow or disable these:
a de-identification rule that goes quiet when it is unconfigured still reports clean, which is
worse than having no rule at all.

Checked against realistic digest content, the general pattern does **not** match `TB-2421`,
`PR-42`, ISO dates, or git SHAs — so it does not over-redact the fields a digest is made of.
