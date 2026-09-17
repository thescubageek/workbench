---
name: resume_handoff
description: Resume work from a handoff document created in a previous session
argument-hint: "[handoff-file-path]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Resume Handoff

Resumes work from a handoff document, restoring context and continuing implementation where the previous session left off.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- [templates.md](templates.md) — the resume confirmation message
- [reference.md](reference.md) — purpose, validation steps, resume best practices, handling handoff-vs-code conflicts, workflow position, error handling, configuration
- [../../docs/reference/journal-entries.md](../../docs/reference/journal-entries.md) — where a journal entry goes (newest first, never appended), its heading contract, and when it opens and closes

**If a directed read fails, stop — do not continue from memory.** These files live outside your
project, so a read can be refused. Say which file was refused, that reads outside the working
directory are gated, and that the fix is to allow the read once or to relaunch with
`--add-dir <plugin-path>`. Do not route around a refusal with `cat`.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If handoff path provided** (e.g., `/wb:resume_handoff docs/plans/2025-01-08-auth/handoff-2025-01-08-14-30.md`):
   - Use `$1` as handoff file path
   - Begin resumption process immediately

2. **If no arguments**:

   ```
   I'll resume work from a handoff document. Please provide:
   1. Path to the handoff document (e.g., docs/plans/project/handoff-YYYY-MM-DD-HH-MM.md)

   I'll restore the context and continue where the previous session left off.
   ```

## Process Steps

### Step 1: Read and Validate Handoff

**⛔⛔⛔ BARRIER 1: STOP! Read handoff document COMPLETELY - every section matters ⛔⛔⛔**

Take the handoff file path from the arguments, prompting for it if it is missing.

1. **Read handoff document fully** to understand:
   - Current state and progress
   - Critical learnings and discoveries
   - Problems already solved
   - Active blockers
   - Next steps planned

2. **Extract key information**:
   - Project directory path
   - Current phase and task
   - Git commit reference
   - Uncommitted changes status

3. **Pull latest from remote**:

   ```bash
   git pull    # Get latest commits
   ```

**Identify the context and discoveries the handoff documents**

### Step 2: Read Project Documentation

Based on handoff references, read the project files:

```javascript
// Extract project directory from handoff
const projectDir = /* extracted from handoff */;

// Read all project documentation
const researchFile = `${projectDir}/research.md`;
const designFile = `${projectDir}/design.md`;
const tasksFile = `${projectDir}/tasks.md`;
const journalFile = `${projectDir}/journal.md`;
```

1. **Read research.md** to understand:
   - Original codebase state
   - Patterns to follow
   - Integration points

2. **Read design.md** to understand:
   - What we're building
   - Design decisions made
   - Success criteria

3. **Read tasks.md** to understand:
   - Current phase details
   - Specific tasks to complete
   - Success verification steps

4. **Read `journal.md`'s tail** — the most recent entry, and whether it is **open** or
   **closed**. The handoff says what the previous session *meant* to convey; the journal's last
   entry says what it was in the middle of. They are different, and both matter.

5. **Read `.claude/wb/knowledge.md` if it exists** — durable repository facts with dates and
   verification hints. This is what stops you rediscovering something an earlier plan already
   established. Treat entries as dated claims to re-check, not as current truth, and correct or
   delete any you find false.

If `[project-dir]` does not exist, the handoff crossed a machine without its documents — plan
directories are gitignored by default. See [reference.md](reference.md) → Error Handling.

### Step 3: Reconcile the Handoff Against the Working Tree

**The repository is the authority. The handoff is a report.**

A handoff records what someone believed when they wrote it. Between then and now, work may have
landed, been reverted, or been abandoned mid-flight. So establish real state before acting on
the document:

```bash
git status --short     # uncommitted work — belongs to something that did not finish
git log --oneline -5   # what actually landed
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' [project-dir]/tasks.md   # tasks actually done
grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' [project-dir]/tasks.md   # tasks remaining
```

Scope the counts to lines carrying a task ID — a plan's success criteria and prerequisites are
checkboxes too, and a bare count over-reports progress.

Then compare, and read each disagreement as a signal rather than an error:

| Handoff says | Tree shows | Reading |
| ------------ | ---------- | ------- |
| task N complete | checkbox `[x]`, clean tree | agreed — proceed |
| task N complete | checkbox `[ ]` | the flip never happened, or the work did not land. Check the code before believing either |
| in progress | uncommitted changes | the work was interrupted mid-task. Finish or supersede it before starting anything new |
| in progress | clean tree | the work was not started, or was reverted |
| — | an **open** journal entry | the previous session did not close out. Its "next action" is the most reliable thing you have |

**Name any discrepancy in the resume confirmation**, and say which side you took. Silently
picking one is how a resumed session ends up building on a state nobody verified.

### Step 4: Apply Learnings from Handoff

Before starting work, internalize the critical learnings:

1. **Patterns and Conventions**:
   - Note any discovered patterns mentioned
   - Remember consistency requirements
   - Apply same approaches used previously

2. **Problems Already Solved**:
   - Don't re-solve issues documented in handoff
   - Use the solutions already found
   - Apply workarounds mentioned

3. **Decisions Made**:
   - Maintain consistency with prior decisions
   - Don't revisit settled trade-offs
   - Follow the chosen approach

4. **Known Gotchas**:
   - Be aware of performance issues found
   - Watch for edge cases discovered
   - Avoid pitfalls documented

### Step 5: Address Active Blockers

If handoff documents active blockers:

1. **Review attempted solutions**:
   - Don't repeat failed attempts
   - Understand why previous approaches failed

2. **Try suggested solutions**:
   - Start with potential solutions from handoff
   - Apply insights from previous attempts

3. **Escalate if still blocked**:
   - Document additional attempts
   - Consider if different expertise needed
   - Create new handoff if switching approach

### ⛔ Model/Effort Gate — advise before continuing

**Before resuming work, pause once and advise on the model + effort for the remaining work.** A resume is the cheapest possible moment to switch: you've *just* reloaded the full context, so the switch tax is already paid — landing on the right tier now avoids a mid-phase reload later.

1. From the handoff and the reconciled plan state, identify the phase being resumed (`implement` / `validate` / etc.) and how gnarly the remaining tasks are.
2. Consult the `model-help` skill in **gate mode** with that phase + the project docs + the model the handoff recorded (the confirmation's "Previous Session: ran on [model]").
3. Surface its one-line verdict, e.g.:

   ```
   Model gate — implement (resume): recommend Sonnet 5 / medium. Handoff ran on Opus 5.
   → Switch down (plan is locked; remaining tasks are mechanical — Opus is overkill for the rest).
   ```

   Or, if the remaining work is the hard part, recommend staying/going up — the floor is inviolable, never advise below what the remaining tasks need.

**Advisory and non-blocking.** State the recommendation and the concrete action (`/model <name>`, set effort); the user decides. Never switch on their behalf. If the current tier is already right, say so in one line and continue.

### Step 6: Confirm and Continue

Read [templates.md](templates.md) NOW and present it.

Then open a journal entry for the work you are about to resume — naming the task and the exact
next action — and continue. It goes at the **top** of `journal.md`, never appended to the end:
read [../../docs/reference/journal-entries.md](../../docs/reference/journal-entries.md) NOW and follow
it. If the previous session left an entry **open**, close it first with what actually landed, so
the newest entry describes this session rather than the last one.

The heading shape is a contract — the session-start hook, `forge`, `daily-digest`, `resume_handoff` and `create_handoff` all match on the trailing `(open)` / `(closed)`, and an entry ending any other way is invisible to them. Timestamp from `date -u +"%Y-%m-%d %H:%M"`, never estimated:

```
## YYYY-MM-DD HH:MM — <task-id or short label> (open)
```

Follow the "Next Steps" section from the handoff:

1. Complete the immediate next task specified
2. Apply recommended approach documented
3. Watch for gotchas mentioned
4. Verify work as indicated

### Step 7: Maintain Continuity

As you work:

1. **Stay consistent** with patterns discovered in handoff
2. **Reference solutions** to problems already solved
3. **Flip each task's checkbox in `tasks.md` as you finish it, and commit per task** — that flip is the tracking act, and the commit is the durable record
4. **Document new discoveries** for potential future handoff
5. **Run verification** commands from handoff

## Important Guidelines

See [reference.md](reference.md) — purpose, validation steps, resume best practices, what to do when the handoff conflicts with the code, workflow position, error handling, and configuration.
