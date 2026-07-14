# daily-digest — artifact template

Write to `.context/daily-digest/<YYYY-MM-DD>.md`. **PHI-free** — refer to work by
ticket key / PR # / issue title only, never patient identifiers or Member IDs. Keep
it tight; this is a plan, not a report.

````markdown
---
date: <YYYY-MM-DD>
window: <SINCE> → now
project: <active project / focus>
branch: <current branch>
generated: <YYYY-MM-DD HH:MM TZ>
sources_ok: [git, beads, jira, calendar]
sources_gap: [sentry, notion, gmail]   # unavailable this run + why (below)
---

# Daily Digest — <date>

**Pulse:** <N> done since <window> · <M> need your review (<K> block others) ·
<P> for today · <B> blocked.

## 🎯 First move

<the single highest-leverage action right now, fully specified + its effort tier>
→ `<entry point, e.g. /wb:forge TB-2421>`

## Today (ranked)

| # | Work item | Sources | Bucket-note | Complexity | Model / Effort | Fan out | Entry point |
| - | --------- | ------- | ----------- | ---------- | -------------- | ------- | ----------- |
| 1 | [JIRA-123](https://your.atlassian.net/browse/JIRA-123) — <title> | [JIRA-123](https://your.atlassian.net/browse/JIRA-123), [#45](https://github.com/o/r/pull/45) | sprint P1 | Complex | opus / high | no | /wb:forge JIRA-123 |
| 2 | <title> | [#48](https://github.com/o/r/pull/48) | changes requested | Moderate | sonnet / medium | ok | [address on #48](https://github.com/o/r/pull/48) |
| 3 | <title> | bd-12 | ready | Trivial | haiku / low | ✅ batch | — |

## 👀 Needs review

**You owe (blocks others):**

- [#PR](https://github.com/o/r/pull/PR) — <title> — <who's waiting> → `<review skill>`

**Awaiting others (your work):**

- [#PR](https://github.com/o/r/pull/PR) — <title> — <state / nudge?>

## ✅ Progress since <window>

- [#PR](https://github.com/o/r/pull/PR) / [KEY](https://your.atlassian.net/browse/KEY) — <title> (merged/closed/resolved)

## ⛔ Blocked

- [KEY](https://your.atlassian.net/browse/KEY) — blocked on <what> → unblocks when <condition>

## 🗓 Day plan (session-sustainable)

- **Free focus time today:** <from calendar — gaps between meetings>
- **Wave 1 (window fresh):** <the Complex/Critical item, focused>
- **Wave 2 (parallel fan-out):** <batch of cheap/independent items>
- **Touch grass / window reset:** <when — near the 5h boundary>
- **Meetings needing prep:** <event → prep item>

## Gaps (sources not loaded)

- <source>: <reason it was unavailable>
````

Rendering notes:

- **Every source reference is a clickable link.** Render each PR, ticket, and Sentry
  issue as a markdown link to the URL its collector returned — `gh`'s `url`, Jira's
  `webUrl`, Sentry's permalink. Never emit a bare `#123` or `TB-2934` when you have its
  URL; the whole point of the digest is one-click navigation to exactly what's needed.
  Link the **Work item** and **Sources** cells, the **Entry point** cell when it targets
  a specific PR/issue, and every bullet in Needs-review / Progress / Blocked. If a
  collector returned no URL for an item, leave it as plain text and don't invent one.
- **Reconciled rows only.** If JIRA-123, PR#45, and bd-12 are the same work, they are
  ONE row with all three (each linked) in the Sources column — never three rows.
- **Effort tiers are required** on every Today row (from the SKILL.md rubric).
- **Diff, not dump.** Progress lists what changed since the window, not the full board.
- Keep Needs-review's "you owe" list first — it usually blocks other people.
- If a source is in `sources_gap`, it MUST also appear under **Gaps** with a reason.
