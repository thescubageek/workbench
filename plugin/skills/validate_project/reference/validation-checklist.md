# Validation Checklist

The skill validates the following aspects.

## 1. File Structure

- ✅ research.md exists
- ✅ design.md exists
- ✅ tasks.md exists
- ⚠️ Optional: journal.md exists (created with the plan; absent on plans predating it)
- ❌ A `journal.md` entry heading that does not end in a literal `(open)` or `(closed)`. That
  suffix is the only thing the session-start hook, `forge`, `daily-digest`, `resume_handoff` and
  `create_handoff` match on. A heading ending any other way is invisible to all of them, and the
  failure is silent — the next session is told "closed" over work that was interrupted
- ❌ More than one `(open)` entry. Entries open at the start of work and close at its end, so two
  open at once means a session never closed out; the tail no longer describes the present
- ⚠️ Optional: handoff.md exists (if session transfer occurred)
- ⚠️ Optional: mockup-log.md in mockups/ (if mockup workflow used)

## 2. Frontmatter Completeness

For each file (research.md, design.md, tasks.md):

- ✅ Has valid YAML frontmatter
- ✅ Required fields present: `project`, `created`, `status`, `last_updated`
- ✅ Git metadata present: `git_commit`, `git_branch`
- ✅ tasks.md additionally: `task_tracking`, `current_phase`, `total_tasks`, `completed_tasks`
- ⚠️ Optional fields: `ticket`, `repository`, `researcher`, `planner`, `assignee`

## 3. Task Tracking Integrity

Status lives in tasks.md itself; there is no external tracker to cross-check against. So these
checks are about whether the file can actually carry that role.

- ✅ tasks.md declares `task_tracking: markdown-checkboxes` in frontmatter
- ✅ tasks.md has a section stating where status lives (checkboxes truth, counters a cache, git durable)
- ✅ Every task line is a checkbox (`- [ ]` / `- [x]`), not prose or a bare bullet
- ✅ Every task carries a stable local ID, and IDs are unique
- ✅ Every ID matches `[A-Z0-9-]*[0-9][A-Z0-9-]*` — at least one digit. An ID without one is invisible to every counter in the workflow, silently
- ✅ `completed_tasks` matches the count of `^- \[x\] \*\*<ID>\*\*` lines and `total_tasks` the count of all ID-carrying task lines — scoped to the ID shape, never a raw `grep -c '^- \[x\]'`
- ⚠️ A `[x]` task with no `(completed …)` stamp — allowed, but the stamp is what makes the log readable
- ❌ Any instruction telling the reader that checkboxes are documentation-only, or that status lives elsewhere — that is a pre-2.0.0 plan and its guidance is now wrong

## 4. Status Consistency

- ✅ research.md status is valid: `draft`, `in-progress`, or `complete`
- ✅ design.md status is valid: `draft` or `approved` — those are the only two. `approved` is
  what `/wb:create_tasks` and `forge` gate on; a design left at `draft` stops the pipeline
- ✅ tasks.md status is valid: `not-started`, `in-progress`, or `complete`
- ✅ Status progression is logical:
  - Cannot have design `approved` if research is not `complete`
  - Cannot have tasks `in-progress` if design is `draft`
- ✅ tasks.md status agrees with its own checkboxes: `not-started` with any `[x]`, or `complete` with any `[ ]`, is a contradiction
- ✅ All files have same `last_updated` date (or close)

## 5. Content Completeness

- ✅ No placeholder text like `[To be added]`, `[TBD]`, `[TODO]`
- ✅ research.md has findings sections populated
- ✅ design.md has design decisions documented
- ✅ tasks.md has phases with tasks defined
- ✅ Success criteria are specific, not generic

## 6. Planning Records

Questions, assumptions and pending decisions live as markdown records in the document that
raises them, each with a short local ID and an explicit state.

- ✅ research.md's `## Open Questions` rows carry IDs (`Q1`, `Q2`, …) and a state
- ✅ design.md's `### Assumptions` rows carry IDs (`A1`, …) and a `Validated?` value
- ✅ design.md's `## Pending Decisions` rows carry IDs (`PD1`, …) and name what they block
- ✅ Every resolved row points at where the decision was recorded, rather than restating it in research.md
- ⚠️ An open `PD` row whose `Blocks` names execution start, while tasks.md is already `in-progress` — the plan is running past a decision it said it needed
- ⚠️ IDs that skip or repeat — they are cited from other documents, so they must be stable

## 7. Dependencies

- ✅ design.md references research.md in `depends_on`
- ✅ tasks.md references both research.md and design.md in `depends_on`
- ✅ Dependency chain is complete: research → design → tasks

## 8. Cross-File Consistency

- ✅ Project names match across all files
- ✅ Ticket IDs match (if present)
- ✅ Git metadata is consistent
- ✅ Current phase in tasks.md makes sense given progress
