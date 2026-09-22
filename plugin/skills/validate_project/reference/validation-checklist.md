# Validation Checklist

The skill validates the following aspects.

**Two shapes, two contracts.** A **phased project** has `research.md`, `design.md` and
`tasks.md`. A **remediation plan** — the shape
[../../../docs/reference/remediation-plan.md](../../../docs/reference/remediation-plan.md) defines — has only
`tasks.md`, and that is correct: a review is not a project, so it has no research or design stage.
That document is the authority on how to recognise one and on the frontmatter keys §9 checks.

On a round, the sections marked below as phased-only do not apply — there is no second file for
them to be about, and reporting each absence as a critical error buries the findings that are
real. Sections **1 (the tasks.md rows and the journal rows)** and **3** apply unchanged, and
**§9** is the round's own contract. Nothing here changes what a phased project is checked
against.

## 1. File Structure

- ✅ research.md exists — *phased project only*
- ✅ design.md exists — *phased project only*
- ✅ tasks.md exists
- ⚠️ Optional: journal.md exists (created with the plan; absent on plans predating it)
- ❌ A `journal.md` entry heading that does not end in a literal `(open)` or `(closed)`. That
  suffix is the only thing the session-start hook, `forge`, `daily-digest`, `resume_handoff` and
  `create_handoff` match on. A heading ending any other way is invisible to all of them, and the
  failure is silent — the next session is told "closed" over work that was interrupted
- ❌ A `journal.md` heading that does not start at column zero. Every reader anchors on that —
  the session-start hook greps `^##`, and this validator's own filters use the same anchor — so
  an indented heading is invisible to **both**, and the validator reports clean on a file the
  hook silently misreads. This is the one journal defect that hides from its own checker
- ❌ An `(open)` entry that is **not the newest**, unless its label carries `[blocked]`. Only
  the most recent entry may be open. A stale one below it is what closing by writing a second
  heading leaves behind, and **a count of open entries never catches it** — the common case
  leaves exactly one. Check position, not quantity. A `[blocked]` entry is the exception because
  `implement` Step 6c creates it on purpose and continues past it, so it sits below a newer entry
  by design
- 📄 Both rules, with the mechanism behind each: `plugin/docs/reference/journal-entries.md`
- ⚠️ Optional: handoff.md exists (if session transfer occurred)
- ⚠️ Optional: mockup-log.md in mockups/ (if mockup workflow used)

## 2. Frontmatter Completeness

*Phased project only — a round's frontmatter is checked by §9, which lists different keys.*

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
- ⚠️ Every `### ⛔ CHECKPOINT` block carries the four `(derivable)`/`(attestation)` labels and "Go by the label, never by position" — the template states it once, so a generated plan that abbreviates later checkpoints is the likely shape
- ❌ A checkpoint block containing a task-ID-shaped line — it inflates every counter
- ❌ Any instruction telling the reader that checkboxes are documentation-only, or that status lives elsewhere — that is a pre-2.0.0 plan and its guidance is now wrong

## 4. Status Consistency

*The research and design rows and the progression rules are phased-only. A round has one status,
in tasks.md, and the last two rows are what apply to it.*

- ✅ research.md status is valid: `draft`, `in-progress`, or `complete`
- ✅ design.md status is valid: `draft` or `approved` — those are the only two. `approved` is
  what `/wb:create_tasks` and `forge` gate on; a design left at `draft` stops the pipeline
- ✅ tasks.md status is valid: `not-started`, `in-progress`, or `complete`
- ✅ Status progression is logical:
  - Cannot have design `approved` if research is not `complete`
  - Cannot have tasks `in-progress` if design is `draft`
- ✅ tasks.md status agrees with its own checkboxes: `not-started` with any `[x]`, or `complete` with any `[ ]`, is a contradiction
- ✅ All files have same `last_updated` date (or close)

**Not mechanised, by design.** These are read by a human or by the model running the skill, and
are marked here so a reader does not mistake the absence of a rule for the absence of a check:
"tasks.md has a section stating where status lives", "every task line is a checkbox rather than
prose" (the rules derive task lines *from* the checkbox shape, so prose tasks are structurally
invisible to them), the `(completed …)` stamp, the checkpoint-label block, and the `A1` /
`Validated?` columns in design.md. Everything else in this document has a counterpart in
`validation-rules.md`.

## 5. Content Completeness

- ✅ No placeholder text like `[To be added]`, `[TBD]`, `[TODO]`
- ✅ research.md has findings sections populated — *phased project only*
- ✅ design.md has design decisions documented — *phased project only*
- ✅ tasks.md has phases with tasks defined — on a round, one `## Tasks` section instead
- ✅ Success criteria are specific, not generic

## 6. Planning Records

*Phased project only — every row here is about research.md or design.md.*

Questions, assumptions and pending decisions live as markdown records in the document that
raises them, each with a short local ID and an explicit state.

- ✅ research.md's `## Open Questions` rows carry IDs (`Q1`, `Q2`, …) and a state
- ✅ design.md's `### Assumptions` rows carry IDs (`A1`, …) and a `Validated?` value
- ✅ design.md's `## Pending Decisions` rows carry IDs (`PD1`, …) and name what they block
- ✅ Every resolved row points at where the decision was recorded, rather than restating it in research.md
- ⚠️ An open `PD` row whose `Blocks` names execution start, while tasks.md is already `in-progress` — the plan is running past a decision it said it needed
- ⚠️ IDs that skip or repeat — they are cited from other documents, so they must be stable

## 7. Dependencies

*Phased project only.* A remediation plan has no upstream document in its own directory, so it
carries no `depends_on` — its upstream is the parent plan, named by `reviews:` and checked in §9.
Requiring the chain of a round reports three critical errors against the shape `/wb:implement`
treats as valid.

- ✅ design.md references research.md in `depends_on`
- ✅ tasks.md references both research.md and design.md in `depends_on`
- ✅ Dependency chain is complete: research → design → tasks

## 8. Cross-File Consistency

*Phased project only — a round has one file, so there is nothing to compare across.*

- ✅ Project names match across all files
- ✅ Ticket IDs match (if present)
- ✅ Git metadata is consistent
- ✅ Current phase in tasks.md makes sense given progress

## 9. Remediation Plan (Review Round)

Checked **instead of** §2, §6, §7 and §8 on a directory recognised as a round. A round is a small
document and this contract is deliberately short — but it is a contract. A branch that validated
nothing would trade a false positive for a blind spot on the only file the round has.

- ✅ Frontmatter carries exactly the keys `remediation-plan.md` lists under *What it has* — the
  set `adversarial-review` Step 8 writes, and nothing else
- ❌ `reviews` names a directory that does not exist — it is the round's only link back to the
  plan under review, and a round whose parent cannot be resolved is unreadable to every reader
  downstream of it
- ⚠️ `round` disagrees with the `-round-N` in the directory name — the two are cited
  interchangeably in commits and journals
- ✅ A `## Tasks` section exists and holds the task lines. A round has one implicit phase and no
  `## Phase N` heading, so `current_phase` is absent **by design** — do not report it missing
- ✅ Absent by design, and never reported: `research.md`, `design.md`, `depends_on`,
  `last_updated`, `git_commit`, `git_branch`
- ✅ Every §3 task-tracking check, unchanged — checkbox task lines, unique IDs carrying a digit,
  counters against the counts, declared status not contradicting the boxes. This is where a
  round's real defects live, and it is why the round is validated at all
