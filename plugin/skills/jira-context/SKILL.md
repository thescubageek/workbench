---
name: jira-context
description: Load context from a Jira ticket's "Agents" section to bootstrap work ("hiveminding" off the ticket). Fetches the ticket via the Atlassian MCP, follows any Agents-section instructions to pull in the files/docs/subsystems it points to, and reports what was loaded. Use when given a Jira key (e.g., TB-2421), when asked to "load ticket context", "hivemind off the ticket", or as the context-bootstrap step inside wb:create_research / wb:forge.
---

# Jira Context Bootstrap

Tickets often carry context other teams or agents already captured. Reusing it —
"hiveminding" off the ticket — avoids re-deriving what's already known. This skill
loads that context and **reports** it. It does **not** perform research, design, or
implementation; it only primes context so a later step (or a human) can verify it
loaded correctly.

## The Rule

```
LOAD WHAT THE TICKET POINTS TO — REPORT IT — DON'T ACT ON IT
```

This is a read-and-load step. Fetch, follow the ticket's `Agents` instructions to
pull context in, then summarize what you now know. Best-effort: never block on a
missing ticket, missing MCP, or missing `Agents` section.

## Prerequisite

An **Atlassian MCP server must be connected** for the fetch to work. If none is
connected, say so and stop — report that context could not be loaded (this is not a
failure of the caller; it just means the shortcut is unavailable).

## Steps

### 1. Resolve a ticket reference

Find a Jira key matching `[A-Z]+-\d+`, in order of preference:

- An explicit ticket in the invocation (e.g., `/wb:jira-context TB-2421`)
- The `ticket:` field in a nearby `research.md` / project frontmatter
- A ticket mentioned in the surrounding request

If none is found, report "no ticket reference found" and stop.

### 2. Fetch the ticket via the Atlassian MCP

Make exactly **one** call — do not enumerate MCP tools, probe response formats, or
choose between candidate tools first. Use the `getJiraIssue` tool (reference it by
that exact name; do not fall back to `fetch` or `search`) with these arguments:

- `issueIdOrKey`: the key from Step 1
- `cloudId`: pass the Jira **site hostname** directly (e.g. `your-org.atlassian.net`).
  The Atlassian MCP accepts a hostname as the cloudId, so this skips a separate
  `getAccessibleAtlassianResources` round-trip. Derive the hostname from any Jira
  link in the request; if none is available, call `getAccessibleAtlassianResources`
  **once** and use the returned `id`.
- `fields`: `["summary", "status", "description"]` — only what this skill needs.
- `responseContentFormat`: `"markdown"` — returns the description as plain markdown,
  so locating the `Agents` heading in Step 3 is a simple text scan rather than an
  Atlassian Document Format (ADF) JSON traversal.

Capture at minimum: summary, status, and the full description body.

If the fetch fails (not found, no access, MCP error), report the specific error and
stop — do not guess at the ticket's contents.

### 3. Locate the `Agents` section

Scan the markdown description for a heading matching `^#{1,6}\s*agents\b`
(case-insensitive) — any level. This section is a deliberate briefing written for AI
agents — the "hive" leaving notes for the next agent.

### 4. Follow the `Agents` instructions to load context

If an `Agents` section exists, treat it as high-priority scoping input and load what
it points to:

- **Read** any files, directories, or prior research/design docs it names — FULLY
  (no limit/offset).
- **Note** subsystems, entry points, code paths, branches, or related tickets it
  calls out.
- **Honor** explicit guidance: "start here", "the relevant code is in X", "skip Y",
  "context lives on branch Z".

Loading means reading and holding the context — not editing, not implementing, not
producing a research/design artifact.

### 5. If there is no `Agents` section

Fall back to the ticket summary + description as background context. Report that no
`Agents` section was present.

### 6. Align the working branch with the ticket

Loading a ticket's context implies you are working (or about to work) that ticket —
so the working branch should be named after it. This is the **one action** this
otherwise read-only skill takes. It is a git state change, so **propose it and act
only on the user's go-ahead**; it is non-blocking (if declined, unavailable, or not
in a git repo, proceed and just note it in the report). Never touch remotes or
force-push here — this only affects the **local** branch name.

Convention: `<TICKET>/<snake_case_description>`, where the description is a short
snake_case slug derived from the ticket summary (e.g. `TB-2421/combobox_aria_pattern`).

Check the current branch (`git branch --show-current`):

- **Already starts with `<TICKET>/`** → nothing to do.
- **On a base branch** (`main`, `master`, `develop`) → offer to create it:
  `git checkout -b <TICKET>/<snake_case_description>`.
- **On another feature branch** that doesn't start with `<TICKET>/` — the branch was
  cut before the ticket was known, or a Conductor worktree pre-created it → offer to
  **rename in place**: `git branch -m <TICKET>/<snake_case_description>`. Do NOT create
  a second branch and orphan the work.
- **Not in a git repo** → skip.

## Output — the verifiable report

Always end with a concise report so the caller (or a human tester) can confirm
context loaded correctly:

```
## Jira Context: [KEY] — [summary]

**Status**: [ticket status]   **Agents section**: present | absent | MCP unavailable
**Branch**: [matches ticket | created | renamed | offered (awaiting go-ahead) | declined | n/a]

### Loaded from the Agents section
- [file/dir/doc read] — [one line on what it contains]
- [subsystem / entry point noted]
- [branch / related ticket]

### Key context now held
- [1-3 bullets summarizing what you now know that you didn't before]

### Not loaded / gaps
- [anything the Agents section referenced that couldn't be found or read]
```

If there was no ticket, no MCP, or no `Agents` section, say exactly that in the
report — an empty-but-honest report is the correct output, not an error.

## Relationship to the wb pipeline

- `wb:create_research` runs this as its **Step 0 (Ticket Context Bootstrap)** before
  decomposing the research question — the loaded context aims the parallel agents.
- `wb:forge` passes its ticket ref through so this bootstrap fires at the research
  phase.
- It is fully usable **standalone** (`/wb:jira-context TB-2421`) to verify that
  ticket context loads correctly, independent of research or forge.
- Because this is where a Jira ticket becomes known in the pipeline, it also aligns
  the **working branch** with the ticket (Step 6) — so downstream commits and the PR
  sit on a `<TICKET>/<snake_case_description>` branch without a separate manual step.
