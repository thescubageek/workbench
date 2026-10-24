# The round's ledger

**Read this when Phase 1 step 5 or Phase 4 step 4 directs you to**, before you write a row. The
rows' format and the thrash breaker are in
[../../docs/reference/review-ledger.md](../../docs/reference/review-ledger.md).

## Where it lives

**The ledger needs a location even where `docs/plans/` does not exist** — the same no-plan
case step 3 already handles. `docs/plans/<plan>/review-log.md` when there is a plan;
otherwise pick one file, **name it in the round report**, and reuse it for every round of this
run. If you cannot write one at all, stop and say so rather than running on.

## Which round number the rows use

**The ledger rows use the `<N>` of the round directory this round's review wrote.** Its
`tasks.md` frontmatter `round:` holds it. Do not evaluate `<N>` again here, because Step 8 has
already written `round-<N>` and "one more than the highest" now names the next round. A round
whose review wrote no directory (a clean round, or any round with no plan directory) has no
`round:` to read. Evaluate `<N>` now, by the `<N>` row in
[remediation-plan.md](../../docs/reference/remediation-plan.md).

## When to commit it

**Commit the ledger in Phase 1 step 5, after the rows are written.** No earlier commit can carry
them. `implement`'s per-task commits ran at step 3, before this round's dispositions existed.
A clean round has no `implement` run at all. A clean round writes one `clean-round` row, as
[review-ledger.md](../../docs/reference/review-ledger.md) defines. Stage with `-f`, as
[remediation-plan.md's "Promoting it"](../../docs/reference/remediation-plan.md) explains, and
chain the commit to the stage:

## What the commit block checks

Do this on every round, including a clean one, so Phase 2's clean-tree precondition reads the
state this loop calls success. A no-plan ledger outside `docs/plans/` is committed the same
way, at whatever path was picked above. With no plan directory, set `L` to that picked path
instead of `docs/plans/<plan>/review-log.md`. The commit is scoped to the ledger, so work already
staged stays staged for its own task's commit. A clean round commits its `clean-round` row,
and a repeat run does not add a second one. Only round 1 may create the ledger. Any later round
whose ledger does not exist exits non-zero. A `findings` with a leading zero exits non-zero. A
non-zero `findings` that is not the number of rows that start `| <N> |` exits non-zero. Stop
there and correct the rows or the count. Do not run on.

## A bot round

**Commit the ledger in Phase 4 step 4, after the rows are written**, with the block that Phase 1
step 5 shows. Re-state `findings` as the number of ledger rows this bot round wrote. Rejected
findings count, because they get rows too. `findings=0` means the round wrote no rows, and the
block then writes the `clean-round` row. Use the bot round's label `<M>b<k>` wherever the block
says `<N>`. Commit the ledger after the fix commit and before Phase 4's push, so the push
carries the rows. Do it also on a round where every finding was rejected and step 3 had
nothing to fix. Rows that are only staged are in no commit when Phase 5 labels the head.

## Why the block refuses a missing ledger

**A breaker that cannot fire is worse than none**, because its presence is what licenses
proceeding. Both Blocking triggers in
[../../docs/reference/review-ledger.md](../../docs/reference/review-ledger.md) read this file,
and against a file that was never created they read clean: rounds 2 and 3 oscillate in exactly
the mirror-image shape that document describes, round 4 reports no trend, and the loop pushes,
un-drafts and labels on the strength of a check that never had data.
