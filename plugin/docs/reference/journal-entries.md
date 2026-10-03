# Journal entries — the shipped rule

**Read this when a step directs you to.** It is the plugin's single authority on where a
`journal.md` entry goes, what its heading must look like, and when it opens and closes. Skills
link here rather than restating it.

## Where the entry goes

**Newest entry at the top. Directly under the marker comment, above every existing entry.**

```markdown
<!-- Real entries begin below this line, newest first. -->

## 2026-09-17 14:02 — create_design (open)     ← the entry you are writing

- **Task/phase**: …

## 2026-09-16 09:30 — create_research (closed) ← everything already there, untouched
```

**Do not append to the end of the file.** The word "append" is wrong for this file and any
instruction that used it was wrong; entries are reverse-chronological.

**An entry ends with a blank line before the next heading.** Insert the new entry *and* a blank
line, or the heading below it fails `MD022/blanks-around-headings` and its own first bullet fails
`MD032/blanks-around-lists`. This matters more than a lint nit usually would: the PostToolUse
hook runs `lint --fix` on any markdown you write, so a missing blank line means the file gets
rewritten underneath you between one step and the next.

**Why it is not a style preference**: the session-start hook picks the most recent entry with

```bash
grep -E '^## ' journal.md | grep -vE '\[YYYY|<YYYY|YYYY-MM-DD' | head -1
```

— `head -1`, the **first** heading in the file. An entry written at the bottom is invisible to
it, and the failure is silent and inverted: the hook reports the *oldest* entry as current. A
session resuming is then told the plan is mid-`create_research` when `create_design` has already
finished, or that an entry is `(open)` when its own `(closed)` entry sits further down the file.
Every other reader — `forge`, `daily-digest`, `resume_handoff`, `create_handoff` — inherits the
same first-heading assumption.

For the same reason, **"the journal tail" never means the end of the file.** Where a skill speaks
of reading the journal's tail, it means the newest entry, which is at the top.

### Which file, when the plan directory is nested

**A remediation plan writes to its parent plan's `journal.md`, not to one of its own.** An
`adversarial-review` round lives at `docs/plans/<plan>/reviews/<date>-round-N/` and holds only
`tasks.md`; its entries go to `docs/plans/<plan>/journal.md`, one directory above the round's
`reviews/` parent.

This is not a convenience. `wb-prime.sh` enumerates plans with `ls -d docs/plans/*/` — one level
deep — and `forge`, `daily-digest`, `resume_handoff` and `create_handoff` all inherit that glob. A
`journal.md` inside a round directory is below it, so no reader would ever open the file: a round's
blocked `[blocked] (open)` entry would be invisible while the parent's journal still read
`(closed)` over it, which is the stale-confident-record failure in its worst form — the parent
looks finished *because* the round's evidence is unreachable.

Name the round in the entry's label so the parent journal stays readable — the round's task IDs
already carry it (`R6-T6`), so the heading reads
`## 2026-09-21 09:14 — R6-T6 (open)` and needs nothing further.

This section is the one statement of the journal rule for a round. The rest of the round's
contract — how to recognise one, what it has and lacks — is [remediation-plan.md](remediation-plan.md),
which links here rather than restating this.

## The heading

```
## YYYY-MM-DD HH:MM — <task-id or short label> (open|closed)
```

- **Read the clock**: `date -u +"%Y-%m-%d %H:%M"`. Never estimate a timestamp, never copy one
  from elsewhere in the file, never reuse the timestamp of the entry you are closing.
- **The trailing `(open)` or `(closed)` is a contract.** The session-start hook, `forge`,
  `daily-digest`, `resume_handoff` and `create_handoff` all match on that literal suffix. A
  heading ending any other way is invisible to all of them, and the failure is silent: the next
  session is told "closed" over work that was interrupted.
- Headings start at column zero. A heading indented or fenced is not found — **by every reader,
  including the checks meant to catch a malformed one**, so this failure hides from its own
  checker. Confirm it with:

  ```bash
  # Indented headings. Must print nothing.
  grep -nE '^[[:space:]]+#{2,}[[:space:]]' journal.md
  ```

  Known limitation: this also fires on a `##` line inside a fenced block that is itself indented
  — inside a list item, say. The generated template keeps its fences at column zero so the case
  does not arise, and a hit is worth a human look either way. A fence-aware check would be more
  precise and more able to be wrong.

## When an entry opens and closes

| Moment | Action |
| ------ | ------ |
| Work starts — before the first read, not after the last write | **Open** an entry |
| Work completes | **Close** that entry in place: change `(open)` to `(closed)` and fill the closing fields |
| You stop to ask a human | **Leave it open** and rewrite its `Next action` to name what you are waiting on |
| A previous session left an entry open | Close it with what actually landed, before opening yours |

**Entries open when work starts, not when it ends.** A session does not get to choose how it
ends: a token limit, a closed laptop, or a crashed harness runs no shutdown step. An entry
written only at completion is silent in exactly those cases, and worse than silent — the newest
entry would still describe the last *finished* phase, so the next session reads a confident,
stale record and never learns that work stopped mid-task.

**Close in place; never write a second heading for the same unit of work.** Change the existing
heading's `(open)` to `(closed)` and fill in the closing fields. Writing a second heading leaves a
stale `(open)` entry below the fold that permanently misrepresents that task's history, and which
of the two the hook reports depends on ordering rather than on truth.

The checkable form of that rule: **only the newest entry may be `(open)`, unless it is marked
`[blocked]`.** Any other `(open)` entry that is not the first real heading is a stale one left by
a second-heading close. A bare count of open entries does not catch it — the common case leaves
exactly one.

```bash
# Stale open entries: any (open) heading that is not the newest and not [blocked].
# Must print nothing.
# Lowercased and right-stripped first, because that is what the hook does — a bare
# grep '(open)' is stricter than the reader it models, so `(OPEN)` or one trailing
# space passes this check while the hook reports the entry as interrupted.
grep -E '^## ' journal.md | grep -vE '\[YYYY|<YYYY|YYYY-MM-DD' | tail -n +2 \
  | tr 'A-Z' 'a-z' | sed 's/[[:space:]]*$//' | grep '(open)$' \
  | grep -vE '\[blocked\][[:space:]]*\(open\)$'
```

### The `[blocked]` marker

A blocked entry is deliberately left open while work continues past it, so it sits below a newer
entry as a matter of course — and it is indistinguishable, to a heading-only check, from the stale
entry a second-heading close leaves behind. The two need opposite remedies, so the entry says which
it is:

```
## YYYY-MM-DD HH:MM — <task-id or short label> [blocked] (open)
```

**The marker goes immediately before the trailing suffix, never after it.** The line must still
end in `(open)` — every reader anchors that test to end-of-line, so a marker placed after the
suffix makes the entry invisible to all of them, which is the failure this file exists to prevent.

Mark an entry `[blocked]` only when the work it names has stopped on something outside the
session's control — a human decision, a checkpoint, an external dependency — and its `Next action`
names what it waits on. **Remove the marker when you close the entry**: `[blocked] (open)` becomes
`(closed)`, because the block is over. A marker left on a closed entry is harmless to the readers
but lies to the next person reading the record.

Do not use it to excuse an entry you forgot to close. The exemption is narrow on purpose: without
it the stale-entry check fires on a state the workflow created intentionally and reports the wrong
cause, and a check that cries wolf on correct files stops being read.

**Match the reader, not the convention.** `wb-prime.sh` lowercases and right-strips a heading
before testing its suffix, and anchors the test to the end of the line. Any check written here
that is stricter than that will pass on a file the hook reads differently — which is a check
that cannot fail in the direction that matters.

Correcting one after the fact: change its state and say what happened, rather than deleting it —
the record of the mistake is worth keeping.

## The two entry shapes

```text
## YYYY-MM-DD HH:MM — <task-id or short label> (open)

- **Task/phase**: <ID and one-line description>
- **Next action**: <the literal next thing to do, specific enough to act on cold>
- **Started at**: <commit hash, or `no-commits-yet`>

## YYYY-MM-DD HH:MM — <task-id or short label> (closed)

- **Task/phase**: <ID and one-line description>
- **Landed**: <what actually changed>
- **Commits**: <range or hashes>
- **Learned**: <anything that changes how the remaining work should proceed — omit if nothing>
- **Blocked by**: <anything blocking — omit if nothing>
```

## When this does not apply

- **No plan directory** — nothing to journal. Skills that run outside `docs/plans/` do not write
  a journal entry at all.
- **`journal.md` absent from a plan directory that otherwise exists** — create it from
  `create_project`'s template rather than starting a bare file, so the marker comment and the
  fenced examples are present. The fenced placeholder headings are load-bearing: the hook
  discards headings whose date is still `YYYY-MM-DD`, and that is what stops the examples being
  read as a real entry.

## Checking it

One command, run against any plan directory — it prints the entry the hook will report, which
must be the newest one:

```bash
grep -E '^## ' <plan-dir>/journal.md | grep -vE '\[YYYY|<YYYY|YYYY-MM-DD' | head -1
```

If that prints an older entry than one further down the file, the ordering is wrong: move the
newer entries above it.
