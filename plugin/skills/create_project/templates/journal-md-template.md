# journal.md Template

The generated `journal.md` must contain **no `##` heading until a real entry is written**.
Every reader of this file takes the first `##` line as the most recent entry, so an example
heading left in the document is read as an entry — and since the example ends in `(open)`, the
plan reports an interrupted task from the moment it is created, forever, while the real latest
entry is never seen. Keep the entry shapes fenced, exactly as below.

````markdown
# Session Journal: [Project Name]

Reverse-chronological — **newest entry at the top. No entries yet.**

**Where a new entry goes: directly under the marker comment at the bottom of this preamble,
above every existing entry. Never appended to the end of the file.** This is not a style
preference. The session-start hook picks the most recent entry with
`grep -E '^## ' journal.md | grep -vE '\[YYYY|<YYYY|YYYY-MM-DD' | head -1` — the *first* heading
in the file. An entry written at the bottom is invisible to it, and the failure is silent and
inverted: the hook reports the oldest entry as current, so a resuming session is told the plan is
mid-research when design has already finished, or that an entry is `(open)` when its own
`(closed)` entry sits further down. `forge`, `daily-digest`, `resume_handoff` and
`create_handoff` inherit the same first-heading assumption. For the same reason, "the journal
tail" means the newest entry — which is at the top.

**Entries open when work starts, not when it ends.** A session does not get to choose how it
ends: a token limit, a closed laptop, or a crashed harness runs no shutdown step. An entry
written only at completion would be silent in exactly those cases, and worse than silent — its
tail would still show the last *finished* phase, so the next session would read a confident,
stale record and never learn that work stopped mid-task. Opening on entry makes the default
residue of an abrupt kill correct: an open entry naming what was being attempted and what came
next.

An open entry beside uncommitted changes means an interrupted task. An open entry beside a
**clean** tree is ambiguous and the tree cannot resolve it: the session may have finished without
closing out, or be **blocked waiting on a human** — a design awaiting approval is exactly this,
and it is the correct residue rather than a fault — or still be running in another session, which
this repository cannot observe at all.

**So read the entry's `Next action` before concluding anything.** The working tree is the
authority on whether work is *in flight*; only the entry says what the work was and what it is
waiting for.

**A heading must end in a literal `(open)` or `(closed)`.** That suffix is what every reader
matches on — the session-start hook, `forge`, `daily-digest`, `resume_handoff`,
`create_handoff`. A heading ending any other way is invisible to all of them, and the failure
is silent: the next session is told "closed" over work that was interrupted.

Entries take these two shapes. **Keep the dates as the literal placeholder `YYYY-MM-DD`.** The
session-start hook finds the newest entry with `grep -E '^## '` and then discards headings whose
date is still a placeholder — so the placeholder is what stops these examples being read as a
real entry. The fence is for readability and is *not* the protection: the hook is not
fence-aware, and these headings still begin at column zero inside it. An example rewritten with
a realistic-looking date would be reported as an interrupted task in every plan generated from
this template, silently, from the moment of creation.

```text
## YYYY-MM-DD HH:MM — <task-id or short label> (open)

- **Task/phase**: <ID and one-line description>
- **Next action**: <the literal next thing to do, specific enough to act on cold>
- **Started at**: <commit hash>

## YYYY-MM-DD HH:MM — <task-id or short label> (closed)

- **Task/phase**: <ID and one-line description>
- **Landed**: <what actually changed>
- **Commits**: <range or hashes>
- **Learned**: <anything that changes how the remaining work should proceed — omit if nothing>
- **Blocked by**: <anything blocking — omit if nothing>
```

<!-- Real entries begin below this line, newest first. -->
````
