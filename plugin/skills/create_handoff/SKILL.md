---
name: create_handoff
description: Create a handoff document to transfer work context to another session or agent
argument-hint: "[project-directory] [handoff-reason]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Create Handoff

Creates a comprehensive handoff document to transfer your work context to another agent or resume in a new session. Captures critical context, learnings, and next steps that aren't in the formal documentation.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- `templates/` — [handoff-document.md](templates/handoff-document.md) (Step 5) · [completion-message.md](templates/completion-message.md) (Step 7)
- [reference.md](reference.md) — purpose, what to include and exclude, handoff quality, when to create one, workflow position, configuration

**If a directed read fails, stop — do not continue from memory.** These files live in the plugin
directory, which is outside your project, so a read of one can be refused. Say which file was
refused, that reads outside the working directory are gated, and that the fix is to allow the
read once or to relaunch with `--add-dir <plugin-path>`. Writing the artifact from this manifest
alone produces a plausible document that was never based on the template — the exact failure the
sentence above exists to prevent. Do not route around a refusal with `cat`.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:create_handoff docs/plans/2025-01-08-my-project/ "switching to opus for complex logic"`):
   - Use `$1` as project directory
   - Use `$2+` as handoff reason (optional)
   - Begin handoff creation

2. **If no arguments**:

   ```
   I'll create a handoff document for your current work. Please provide:
   1. Path to the project documentation directory (e.g., docs/plans/2025-01-08-my-project/)
   2. Reason for handoff (optional, e.g., "session ending", "need different model", "blocked on approval")

   I'll document the current state for seamless continuation.
   ```

## Process Steps

### Step 1: Gather Current State

**⛔⛔⛔ BARRIER 1: STOP! Read ALL project docs AND review conversation history ⛔⛔⛔**

```javascript
const projectDir = $1 || /* prompt for it */;
const handoffReason = $2 || "session transfer";

// Read all project documentation
const researchFile = `${projectDir}/research.md`;
const designFile = `${projectDir}/design.md`;
const tasksFile = `${projectDir}/tasks.md`;
const journalFile = `${projectDir}/journal.md`;
```

1. **Read all project documentation** to understand:
   - Project goals and current status
   - What's been completed
   - What's in progress

2. **Review conversation history** to capture:
   - Recent changes made
   - Problems encountered and solutions
   - Decisions made during implementation
   - Any deviations from plan

3. **Read plan state from `tasks.md`** — it is the record; there is no tracker to query:

   ```bash
   grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md   # tasks done
   grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md   # tasks remaining
   ```

   Scope the count to lines carrying a task ID: a plan's success criteria and prerequisites are
   checkboxes too, and a bare count over-reports progress. Then note the **first unchecked
   task** — that is the "next immediate task" the handoff must name — and anything under
   `## 🚧 Blockers & Notes`.

4. **Read the journal tail.** `journal.md`'s most recent entry says what the last stretch of
   work was attempting. Carry its state into the handoff: an **open** entry beside uncommitted
   changes means a task was interrupted mid-flight, and that is the single most useful thing
   the next session can be told.

5. **Check for mockup state** (if mockups/ exists):

   ```bash
   ls mockups/                     # Check for mockup directory
   # If exists, read mockups/mockup-log.md for current version and pending feedback
   ```

**Identify what context would be lost if starting fresh**

### Step 2: Analyze Work State

Determine the current implementation state:

1. **Implementation Progress**:
   - Which phase are we in?
   - Which tasks are complete/in-progress/blocked?
   - Any partial implementations?

2. **Critical Discoveries**:
   - Unexpected patterns found
   - Gotchas encountered
   - Solutions to tricky problems
   - Performance considerations discovered

3. **Deviations and Decisions**:
   - Where we deviated from plan and why
   - Judgment calls made
   - Trade-offs accepted

4. **Current Blockers**:
   - What's preventing progress
   - What's been tried
   - Potential solutions identified

### Step 3: Review Knowledge Candidates

Before writing the handoff, decide what belongs in `.claude/wb/knowledge.md` instead of — or as
well as — this document. A handoff is read once by the next session; the knowledge file is read
by every session after that.

**An entry qualifies only if it would change how the *next* session works.** It does **not**
qualify if it is:

- a task outcome — the journal has those
- a plan deviation — Implementation Notes has those
- true of only one task

So: a tool that hangs under a particular flag qualifies. A convention this repository follows
that is not obvious from the code qualifies. "Phase 2 took longer than estimated" does not.

Every entry carries the fact, why it matters, the date, the plan it came from, and a
**verification hint** — how a future session can check whether it is still true. That hint is
what keeps the file from becoming a pile of stale assertions read as current rules.

If you find an existing entry that this session proved false, **correct or delete it now**.
That obligation is the other half of what keeps the file trustworthy.

If nothing qualifies, add nothing and say so. An empty review is a normal outcome.

### Step 4: Check Git State

```bash
# Check for uncommitted code changes
git diff

# Note any staged changes
git diff --staged

# Capture current HEAD for frontmatter
git rev-parse HEAD
```

Document any uncommitted work and its purpose. Uncommitted changes beside a completed task are
worth calling out explicitly — under one-task-one-commit they mean something did not finish.

**Is this handoff crossing a machine?** If so, the plan directory has to travel with it.
Plan directories are transient by default and gitignored; a handoff to another machine is one
of the two triggers that promotes one into git:

```bash
git add -f docs/plans/<this-plan>/    # then commit and push the branch
```

Without that, the receiving machine gets a handoff pointing at documents it cannot see.

**⛔⛔⛔ BARRIER 2: STOP! Ground every claim before writing. Every file:line, metric, test result, and progress figure MUST come from actual tool output (`git diff` / `git log` / `git diff --stat`, checkbox counts, a real test run) — never from memory or the template's example values. If a value isn't verified, omit it or mark it `unverified`. Omit empty sections entirely; never fill them with placeholders. Mark genuinely unknown fields `unknown`. ⛔⛔⛔**

### Step 5: Create the Handoff Document

Read [templates/handoff-document.md](templates/handoff-document.md) NOW and write the handoff in that shape.

Save it as:

```
[project-dir]/handoff-YYYY-MM-DD-HH-MM.md
```

Where `YYYY-MM-DD` is the current date and `HH-MM` the current time (24-hour).

### Step 6: Append a Journal Pointer

Append an entry to `journal.md` recording that a handoff was written, and its path. A future
session reading the journal tail then finds the handoff rather than reconstructing the same
state from scratch — the journal is the index, the handoff is the detail.

The heading shape is a contract, because the session-start hook, `forge`, `daily-digest`, `resume_handoff` and `create_handoff` all read it to decide whether work was interrupted:

```
## YYYY-MM-DD HH:MM — <task-id or short label> (closed)
```

Ending in a literal `(open)` or `(closed)` is what makes the state detectable. An entry that ends any other way is invisible to every one of those readers, and the failure is silent — a session reads "closed" over interrupted work.

If an entry is currently **open**, close it first with what actually landed, then add the
pointer. Handing off with an entry left open tells the next session a task was interrupted when
in fact it was deliberately parked.

### Step 7: Confirm

Read [templates/completion-message.md](templates/completion-message.md) NOW and present it.

## Important Guidelines

See [reference.md](reference.md) — purpose, what to include and exclude, handoff quality, when to create a handoff, workflow position, and configuration.
