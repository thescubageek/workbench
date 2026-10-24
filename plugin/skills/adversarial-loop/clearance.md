# Is the head cleared?

**Read this when Phase 5 directs you to**, before you name the label. A bot review certifies the
commit it read. This file says when that clearance covers the current head.

⛔ **The head SHA qualifies the bot too, not just the rollup.** A bot review certifies the commit
it read, exactly as a local pass does — the Phase 1 gate's *""Clean" describes a tree state, not the branch"* paragraph, *"a clean pass certifies the commit it
read"*, and the reviewer is a reviewer either way. So if anything has been pushed since the
comment the bot last updated, its clearance is about a commit that is no longer the head, and
nothing will tell you: `reference.md`'s "The review check reports **skipped** on later pushes" row records that the review check reports **skipped** on
later pushes, which is non-blocking and leaves a green rollup. The CI-only fix that Phase 4
deliberately does not reply to (*"a green-CI fix the bot never raised does not need its own
`@claude` comment"*) is precisely how a head the bot never saw gets here.

**So compare, don't assume.** Neither surface the bot edits carries the SHA its review was
written against — a review's `commit_id` still reads the earlier commit once the bot edits its
comment, and an issue comment has no commit field at all. Compare check-runs instead: read the
bot's review check-run for the current head, via `gh api --paginate
"repos/{owner}/{repo}/commits/$(git rev-parse HEAD)/check-runs" --jq '.check_runs[] | [.name,
.status, .conclusion, .head_sha] | @tsv'` or `gh pr checks`, and confirm a **completed**
check-run for the review exists whose `head_sha` equals `git rev-parse HEAD`. `gh` expands
`{owner}` and `{repo}` from the current repository, and `--paginate` is required: the endpoint
returns 30 check-runs per page, so the bot's can sit on page 2. A **skipped** check-run for HEAD is not
clearance — `reference.md`'s "skipped on later pushes" row records skipped as exactly what a later push produces. If no
completed check-run exists for HEAD, or the newest one is for an older SHA, the branch is not
cleared: fold the unreplied commits into an `@claude` reply and take another Phase 4 round, or
say that the label covers a range the bot did not read. **A range whose only changed path is
the ledger is cleared.** Phase 4 step 4 commits a ledger row after every bot review, so HEAD is
often one ledger commit past the SHA the bot read. Take the newest review check-run on this
branch whose `conclusion` is `success`. A skipped, canceled or failed run is not the bot reading
that SHA. If `git diff --name-only <that run's head_sha>..HEAD` lists only the ledger file, the
bot's clearance covers HEAD. A `git diff` that exits non-zero or prints no path at all is not cleared.
An unknown SHA exits 128 with empty output, so it is not a ledger-only range. The ledger file is `docs/plans/<plan>/review-log.md`, or the path Phase 1
step 5 picked. A range that changes any other path is not cleared. Do not label on the strength
of a rollup alone.

**A newer clean bot comment also clears HEAD.** After a Phase 4 fix push, the review check-run
reports skipped on HEAD. An `@claude` re-review attaches its check-run elsewhere, so neither rule
above clears it. Read the bot's comments, where `<PR>` is Phase 0's `pr`: `gh api --paginate
"repos/{owner}/{repo}/issues/<PR>/comments" --jq '.[] | select(.user.login=="claude[bot]") |
[.id, .updated_at] | @tsv'`. This is the same `claude[bot]` filter Phase 3 polls with. Take the
comment with the latest `updated_at`. HEAD is cleared when all three conditions hold:

1. It is newer than the latest baseline, by the arrival rule in [waiting.md](waiting.md).
2. Its body reports nothing outstanding, read as Phase 4 reads it.
3. `git diff --name-only <the baseline's head SHA>..HEAD` exits 0 and lists nothing or only the
   ledger file.

The ledger file is the one the paragraph above names. The diff catches every commit after the
baseline, whatever its committer date. A `git diff` that exits non-zero is not cleared. A baseline
with no recorded head SHA is not cleared. If any condition fails, HEAD is not cleared. Fold the
commits into an `@claude` reply, or disclose the range, as above.

This is **provisional**: no real `claude[bot]` run has been observed on any repository yet, so
the check-run's name and shape are unconfirmed. Revisit once a real run exists.
