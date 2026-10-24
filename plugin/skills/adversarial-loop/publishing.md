# Publishing

**Read this when Phase 2 or Phase 5 directs you to**, before you run the block. It says what the
publishing blocks check, and why each check is there.

## What the loop writes, and why it confirms

The loop fetches nothing. It serves only the current checkout, so it never pulls a remote branch.
One write belongs to `adversarial-review` and is **disclosed, not confirmed**. When the target is a
pull request that is not the current checkout, `pr-identity` fetches
`refs/pull/<N>/head` into `refs/remotes/<base remote>/pr/<N>`. It writes exactly one
remote-tracking ref. It checks nothing out, creates no branch, and leaves the worktree as it was.
It is the same class of write as any `git fetch`. The review's `identity:` line names the ref it
wrote.

This is the repository norm, not a rule invented here: `plugin/docs/reference/branch-naming.md`
requires confirmation before a git state change, and the root `CLAUDE.md` says work is committed
but the **push is confirmed with the user**. This skill's own Phase 1 already says *"pushing is
the user's call"* — Phases 2 and 4 are the same call.

## The two standing prohibitions

- **Never force-update a remote ref — in any spelling.** `--force`, `--force-with-lease`, and a
  `+refs/heads/…` refspec are the same action, and naming only the first is how the rule gets
  followed past. If a fix round leaves the branch non-fast-forward, that is a situation to surface,
  not to resolve with a flag.
- **Never add a label that triggers an automatic merge.** You cannot reliably tell which labels
  drive automation — nothing here instructs you to read a repository's workflows or branch
  protection, and inferring it is the kind of guess this skill exists to refuse. The confirmation
  table in *What stops for the user* is how this prohibition is actually enforced: **name the label to the user and let
  them confirm it.** Marking something reviewable is not the same as deciding to merge it, and the
  second is the user's.

## What the Phase 2 block refuses

**The block re-runs [`pr-identity`](../../scripts/pr-identity) and publishes only on
`publish=yes`.** The script is the one place that decides whether a push lands on the PR's head.
Re-type the `pr` that Phase 0 printed into the `pr=""` line. The block refuses when the script
exits non-zero, when `publish` is not exactly `yes`, when the script resolves another PR, or when
`push_remote` or `push_ref` is empty or `-`. It pushes to the script's `push_remote` and
`push_ref`, never with a bare `git push`. A refusal skips Phases 2 to 5, as the Phase 0 outcome
table says.

## A clean worktree is a precondition

⛔ **A clean worktree is a precondition, not a courtesy.** The Phase 2 block's chain guards the *failure*
direction only, and this is the no-op direction, which is indistinguishable from success at the
exit status: with the round's fixes still uncommitted, `git push` prints `Everything up-to-date`
and **exits 0** (executed, not assumed), so `&&` passes and `gh pr ready` un-drafts a head that
does not contain them. Two paths reach that state without anyone deciding to. Phase 1's
inline-fix branch — *"if there is no plan directory, fix inline"* — never commits. And
`plugin/scripts/lint-hook` runs `lint --fix` after Write and Edit (after Bash it only reports
by default), so a hook can still dirty the tree after the last commit you made.

## Chained, not sequential

⛔ **Chained, not sequential.** Written as two statements, a failed push still un-drafts — and
un-drafting against a stale head summons `claude[bot]` to review code without the round's fixes,
fires every `ready_for_review` workflow, and cannot be undone because Phase 2 forbids
re-drafting. A fix round that amends or rebases makes a non-fast-forward push the likely failure,
which is exactly the case the prohibitions above say to surface rather than force.

## Check `isDraft` before relying on the un-draft

⛔ **Check `isDraft` before relying on the un-draft.** This skill's own description puts an
already-open pull request in scope, and `gh pr ready` on one is a **no-op that exits 0**: no
`ready_for_review` event fires. Without the block's `isDraft` branch, Phase 2 reports success and Phase 3
waits on a bot review that was never triggered — another absence that means "broken" reading as
one that means "not yet".

## An already-open pull request needs an explicit summons

**An already-open pull request needs an explicit summons.** Per
[reference.md](reference.md), the review check runs on the ready-for-review transition, so once
that transition is spent the only way to summon `claude[bot]` is a leading `@claude` comment.
That is the same publishing action Phase 4 confirms — it is in the *What stops for the user* table, and it is
confirmed here too. Say plainly which route Phase 3 is waiting on; do not enter Phase 3 without
one.

## The label block is chained too

⛔ **Chained, not sequential — the same shape Phase 2's "Chained, not sequential" paragraph requires.** Written as
two statements, a failed `--add-label` is masked: the edit exits non-zero with *"not found"*
where the repository has no label by that name, the unchained `gh pr view` succeeds anyway, and
what it prints is a labels array **without** the label — which is exactly what the confirmation
after the block then reads as success. Executed both ways: sequential leaves the block at exit 0 with an
array on stdout; chained stops at exit 1 and prints nothing.

**Confirm the label is in the array, not that an array appeared.** An empty result and a result
missing one entry look the same at a glance, and this is the last gate before the change is
called reviewable. The check is also only meaningful because `$PR` is bound in the same shell: an
unbound `$PR` makes both commands fail identically, so "the label landed" and "the command never
ran" become indistinguishable. Stop there.
