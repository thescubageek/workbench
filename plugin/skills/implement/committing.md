# Committing a task

**Read this when Step 6b directs you to**, before you stage anything.

**Stage the plan's own files with `git add -f`, every time.** `docs/plans/` is gitignored, so a
plain `git add <plan-dir>/tasks.md` exits 1 with "The following paths are ignored", stages
nothing, and breaks the `&&` chain — the commit never runs, and one task, one commit fails on the
first passing task of the plan. The `&&` below is what makes that true: separate the three
commands by newlines and a failed stage lets the commit land **without** the plan files. A plain
`git add` exits 1 even on an already-tracked plan file — staging it and failing anyway, which
breaks the `&&` chain just the same — so "this plan was promoted once" is not a reason to drop
the `-f`. The `-f` overrides gitignore; it never widens the pathspec, so the by-path rule in Step 6b
still holds.

```bash
git add ${workerReportedFiles} &&                        # code — by path, no -f
git add -f ${planDir}/tasks.md ${planDir}/journal.md &&  # plan files — always -f
git commit -m "${taskId}: ..."
```

On a remediation round (`docs/plans/<plan>/reviews/<date>-round-N/`, which holds only `tasks.md`)
the journal is the parent plan's, so stage `${planDir}/../../journal.md` in its place — naming
`${planDir}/journal.md` exits 128 and the commit never runs (see
[which file, when the plan directory is nested](../../docs/reference/journal-entries.md)):

```bash
git add ${workerReportedFiles} &&                           # code — by path, no -f
git add -f ${planDir}/tasks.md ${planDir}/../../journal.md &&  # round tasks.md + parent journal
git commit -m "${taskId}: ..."
```

**A failed stage hides.** `git status --short` does not list *untracked* ignored files, so an
unpromoted plan directory's `tasks.md` is invisible there — 6a's discriminator, 6c's "end clean
either way" and Step 8.2's clean check all read clean over a plan file that was never committed.
(A *tracked* plan file that is merely modified does show, so the blindness is specific to a
directory nothing has promoted.) Confirm what the
commit actually contains (`git show --stat HEAD`) rather than inferring it from a clean tree.

**Committing after each passing task is what makes an unfinished task detectable.** After a passing task the tree
is clean, so any uncommitted work belongs to something that did not finish.
