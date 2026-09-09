# journal.md Template

````markdown
# Session Journal: [Project Name]

Append-only, reverse-chronological — newest entry at the top.

**Entries open when work starts, not when it ends.** A session does not get to choose how it
ends: a token limit, a closed laptop, or a crashed harness runs no shutdown step. An entry
written only at completion would be silent in exactly those cases, and worse than silent — its
tail would still show the last *finished* phase, so the next session would read a confident,
stale record and never learn that work stopped mid-task. Opening on entry makes the default
residue of an abrupt kill correct: an open entry naming what was being attempted and what came
next.

An open entry beside uncommitted changes means an interrupted task. An open entry beside a
clean tree means a session that simply moved on. The working tree is the authority, never this
file.

**The heading must end in a literal `(open)` or `(closed)`.** That suffix is what every reader
of this file matches on — the session-start hook, `forge`, `daily-digest`, `resume_handoff`,
`create_handoff`. A heading ending any other way is invisible to all of them, and the failure is
silent: the next session is told "closed" over work that was interrupted.

## [YYYY-MM-DD HH:MM] — [task-id or short label] (open)

- **Task/phase**: [ID and one-line description]
- **Next action**: [the literal next thing to do, specific enough to act on cold]
- **Started at**: [commit hash]

## [YYYY-MM-DD HH:MM] — [task-id or short label] (closed)

- **Task/phase**: [ID and one-line description]
- **Landed**: [what actually changed]
- **Commits**: [range or hashes]
- **Learned**: [anything that changes how the remaining work should proceed — omit if nothing]
- **Blocked by**: [anything blocking — omit if nothing]
````
