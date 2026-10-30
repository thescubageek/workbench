# Pruning the round plan

**Read this when Phase 1 step 3 directs you to**, before you invoke `implement`. It says which
task lines to delete, when the round is clean, and where to point `implement`.

⛔ **Prune before you invoke, because `implement` cannot read a disposition.** Step 8 writes
the plan before any adjudication exists, so it carries a task for **every** finding that
survived verification — including the ones step 2 just rejected. `implement` takes the first
unchecked task line in the phase and implements *"only what tasks.md specifies"*
(`implement/SKILL.md` → Scope); the task shape in
[../adversarial-review/templates.md](../adversarial-review/templates.md) has no disposition
field, and nothing `implement` reads would carry one. So an unpruned round with two findings
adjudicated `Valid` and four rejected commits six fixes — and the Phase 1 gate still passes,
because it asks only whether the `Valid` ones were resolved.

**Delete the rejected findings' task lines from `## Tasks`.** Rejected is `Wrong`,
`Over-fitted`, and `Pre-existing` — except a `Pre-existing` finding this change made materially
more reachable, which [../adversarial-review/reference.md](../adversarial-review/reference.md)
keeps fixable and which therefore keeps its task. `Valid` stays. `Real but disproportionate`
stays, rewritten to the smaller change, because it takes the finding and rejects only the
remedy. Deletion, not annotation: the unticked checkbox is what `implement` keys on, so a line
left in place gets implemented, and a line ticked to prevent that asserts a fix nobody made.
Leave the frontmatter counters alone — `/wb:update-status` owns them and reconciles them from
the checkboxes. Nothing is lost by deleting — the disposition and the evidence that settled it
go in the ledger at step 5, which is the record of what the round decided; the plan is only the
work list.

**If no task line remains, the round is clean — do not invoke `implement`.** Two arrivals,
reaching the same verdict from different states: the review verified nothing, so Step 8 wrote
no `tasks.md` at all
([../../docs/reference/remediation-plan.md](../../docs/reference/remediation-plan.md)); or the
pruning above deleted every task line because every finding was rejected. Either way no
`Valid` finding remains, which is the Phase 1 gate's success condition rather than a failure.
Invoking `implement` on it would hit its Step 2 stop on "no task lines" — an absence that
correctly means *the review failed to write its findings*, and the one this branch exists to
stop being reported as skill drift or as a broken round.

**On the second arrival, commit the pruned plan yourself.** Step 8 staged the `tasks.md` it
wrote and the pruning above modified it, so the round plan is sitting staged in a tree no
`implement` run will ever commit — and Phase 2's `git status --porcelain` precondition lists
it and hard-fails, on the state this branch calls success. Re-stage it with
`git add -f <round-dir>/tasks.md` and commit it on its own, round number in the message,
before taking the gate. The ledger is not in this commit, because this round's rows do not
exist yet — step 5 commits them. The first arrival wrote no file and has nothing to commit.

No code was fixed, so there is nothing for step 4 to verify and no reworked area for step 6
to re-review: the pass you just took still certifies this tree. Record the
dispositions at step 5 — a round that decided nothing needed fixing is exactly what the ledger
has to show — and take the gate.

**Point it at the round directory, never at the parent plan.** The parent holds the original
plan and `implement` would re-run it. A remediation plan is `tasks.md` alone — the shape
[../../docs/reference/remediation-plan.md](../../docs/reference/remediation-plan.md) defines — and
`implement` Step 1 accepts it. If it instead stops on a missing file or
on "no phases", the two skills have drifted apart: say so and stop, rather than fixing the
round inline and reporting it as the same thing. The clean round is already out of that
sentence — the branch above returns before the invoke — so a file missing *here* is one you
had findings for.

**Why not inline.** An aggregate gate run after twenty-two changes says the tree passes; it
says nothing about whether any individual change did what it should, or broke another. On
this plugin that produced a round where 64% of findings sat in surface the previous round's
fixes had written. The finding already carries its acceptance test — `failure_scenario`,
written by the reviewer before the fix existed — and batch-fixing discards it.
