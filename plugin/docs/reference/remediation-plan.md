# The remediation plan — the shipped contract

A remediation plan is what an `adversarial-review` round leaves behind: one `tasks.md`, one task
per verified finding, each carrying its finding's failure scenario as its acceptance criterion.
`adversarial-review` Step 8 writes it; `adversarial-loop`, `implement`, `implement_inline`,
`update_status` and `validate_project` all consume it. Every one of those skills links here for
what the shape *is*. What each does *about* it stays in that skill's own steps.

**A remediation plan has only `tasks.md`, and that is correct.** A review is not a project, so it
has no research or design stage — the review *is* the research and the findings are the design
input. A consumer that reaches for `research.md` or `design.md` and stops, or that routes the
user to `/wb:create_project`, is wrong about the workflow rather than right about the plan:
`create_project` would manufacture two files that exist only to be empty.

## Where it lives

```
docs/plans/<plan>/reviews/<date>-round-<N>/tasks.md
```

**Under** the plan it reviews, never beside it, and never inside its `tasks.md`. `wb-prime.sh`
enumerates plans with `ls -d docs/plans/*/` — one level deep — and `forge`, `daily-digest`,
`resume_handoff` and `create_handoff` inherit that glob. Nested one level deeper, a round never
competes to be the active plan and never distorts the parent's counters. A sibling
`docs/plans/<date>-review/` would sort newer and silently *become* the active plan, hiding the
original — a worse defect than the one the round exists to fix.

## Promoting it

That path is inside `docs/plans/`, which is **gitignored** — so the round is written where git
will not stage it by default. **Whoever writes the plan stages it, in the same step, with
`git add -f`:**

```bash
git add -f docs/plans/<plan>/reviews/<date>-round-<N>/tasks.md
```

The `-f` is needed every time. A plain `git add` **exits 1 even on an already-tracked plan
file** — it updates the index and fails anyway, so the `&&` chain breaks just the same — and
"this plan was promoted once" is therefore not a reason to drop it. `-f` overrides the ignore
rule without widening the pathspec, so staging stays by path. The rest of the reasoning is stated
once, in [`implement` step 6b](../../skills/implement/SKILL.md): on a plan file git is not yet
tracking, the same command exits 1 with "The following paths are ignored" and stages nothing.

**Stage it; do not commit it.** The commit belongs to the caller, not to the round, and
committing from the round would put the plan in a commit ahead of the work it lists — against
*one task, one commit*. Staging is what the round owes: the file enters the index, where
`git clean -fdx` no longer reaches it, and the caller's next commit carries it. Three callers,
and a round says which one it is handing to:

- Under `adversarial-loop` with tasks to run — `implement` step 6b's per-task commit.
- Under `adversarial-loop` with every finding rejected — `implement` is never invoked, so the
  loop commits the pruned plan itself before its clean-tree precondition
  ([adversarial-loop](../../skills/adversarial-loop/SKILL.md) Phase 1 step 3).
- Standalone — the user's, once they have read the round.

**Nothing written, nothing to promote.** A round that verified no findings writes no `tasks.md`
at all (below), and `git add -f` on a path that does not exist is
`fatal: pathspec ... did not match any files`, exit 128. Stage only when the write happened.

**An unpromoted round hides.** `git status --short` does not list *untracked* ignored files, so a
round nobody staged is invisible there: every later "confirm the tree is clean" reads clean over
the only durable artifact the round produced, and a `git clean -fdx` or a worktree teardown takes
it with nothing left to show that it existed.

## How to recognise one

Either test is sufficient; a consumer checks both because a hand-moved directory can lose one:

1. `tasks.md` carries a `reviews:` key in its frontmatter, or
2. the directory path matches `reviews/<something>-round-<digits>/`.

The canonical form, for anything that reasons in code:

```javascript
const isRound =
  (tasksFrontmatter && 'reviews' in tasksFrontmatter) ||
  /(^|\/)reviews\/[^/]+-round-\d+\/?$/.test(projectDir);
```

## What it has, and what it deliberately lacks

**Has:** `tasks.md`, with this frontmatter and nothing else — the set Step 8 writes:

```text
---
project: <parent plan's project>
reviews: docs/plans/<plan>
round: <N>
created: <date>
status: in-progress
total_tasks: <N>
completed_tasks: 0
task_tracking: markdown-checkboxes
---
```

Below the frontmatter: a title, a `## How each task is verified` section stating the RED rule, and
**one `## Tasks` section** holding every task line. Task IDs are `R<N>-T<n>` — the round number is
in the ID, which is what keeps a round's entries legible in the parent's journal.

**Lacks, by design, and never reported as missing:** `research.md`, `design.md`, `journal.md`
(see below), a `depends_on` chain, `current_phase`, `## Phase N` headings, `last_updated`,
`git_commit`, `git_branch`. A round has **one implicit phase** — its `## Tasks` section — so
wherever a consumer substitutes a phase label, the label is `Round <N>` from the directory name,
and there is no phase after it to proceed to.

`reviews:` is the round's only link back to the plan under review. A round whose `reviews:` does
not resolve is unreadable to everything downstream of it, and that is the one structural error
worth a critical.

## A round with nothing to fix

**A round that verified no findings writes no `tasks.md` at all** — not an empty one. The absence
is the round's success state, and it is stated here so the skills either side of it cannot
disagree about what it means.

An empty plan file would be the worse artifact. `implement` Step 2 stops on a plan with no task
lines and sends the caller back to re-run the review — the right response to a review that failed
to write its findings, and exactly the wrong one for a review that had none to write. Writing
nothing keeps those two absences apart. The round's record is the review's own report, an empty
`ReportFindings`, plus the ledger entry under `adversarial-loop`.

So a missing round directory is not an error on its own; it is an error only to a caller that
knows a finding survived. A round directory that *exists* with a `## Tasks` section holding no
task lines is the error.

## The journal

A round writes **no journal of its own**. Its entries go in the parent plan's
`docs/plans/<plan>/journal.md`, labelled with the round's task IDs. The rule, and the reason a
journal inside the round directory would be invisible to every reader, is stated once in
[journal-entries.md](journal-entries.md) → *Which file, when the plan directory is nested*.

## Resolving `<plan>`, `<N>` and `<date>`

These are Step 8's placeholders, and two sessions writing a round must land on the same values.

| Placeholder | Rule |
| ----------- | ---- |
| `<plan>` | The plan directory the caller names. `adversarial-loop` resolves the active plan and passes it. With no caller and exactly one `docs/plans/*/tasks.md` at `status: in-progress`, use that one. Otherwise **skip Step 8 and say so** — the findings are the output, and guessing a plan directory files a round against the wrong work. |
| `<N>` | One more than the highest `-round-<N>` already present under `docs/plans/<plan>/reviews/`, across every date. Never reuse a number: a second `round-6` overwrites the first round's `[x]` checkboxes. |
| `<date>` | `date -u +%F` — UTC, the same clock the journal contract uses. Directories dated locally before this rule existed keep their names; the round number, not the date, is what readers cite. |

## Checking it

The recognition rule is stated **here and nowhere else**. This must name exactly one file:

```bash
grep -rlF 'a `reviews:` key in its frontmatter' plugin/
```

Every consumer that branches on the round shape links to this document rather than restating it.
This must print nothing:

```bash
for s in implement implement_inline update_status validate_project adversarial-loop; do
  grep -q 'remediation-plan.md' "plugin/skills/$s/SKILL.md" || echo "MISS $s"
done
```
