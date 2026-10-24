# Waiting on CI and the review

**Read this when Phase 3 directs you to.** It bounds the wait for a signal that may never
arrive.

**Every row of the table in [reference.md](reference.md) is a remedy for a signal that arrived and was misread. Phase 3 also
has to handle the signal that never arrives at all** — the bot installed but erroring out, or the
review workflow disabled on this repository. Nothing else in the loop will end that wait: the
thrash breaker needs three findings before it evaluates
([../../docs/reference/review-ledger.md](../../docs/reference/review-ledger.md)), and no findings
is not three.

**So the wait is bounded, and reaching the bound is a result rather than a failure to retry
harder:**

1. **Poll, do not block.** Read the check rollup and the newest `claude[bot]` comment together,
   on an interval of about **2 minutes** — a review takes minutes, and a tighter poll buys
   nothing but rate limit.
2. **Bound it at 30 minutes, or 15 polls, whichever comes first.**
3. **Confirm each poll could have seen something.** Per `reference.md`, a filter on `claude`
   rather than `claude[bot]` matches nothing and returns success, and the bot **edits its comment
   in place** — so compare `updated_at` or the newest comment id, never "is there a new comment".
   Count as arrival only a change against the latest baseline (Phase 2's, or the one Phase 4 re-recorded before the last re-summon): a newest comment id that differs
   from the baseline id, or an `updated_at` later than the baseline's. A baseline-era comment is
   not an arrival. A poll that cannot distinguish "no findings" from "no filter match" has not polled. A poll
   whose `gh` command exits non-zero is a **failed poll**, not an empty one — report its exit
   status and stderr (rate limit, expired token) rather than counting it toward "nothing
   arrived".
4. **At the bound, stop and surface.** Say what did arrive — the rollup state, the baseline, and
   whether any `claude[bot]` comment newer than the baseline arrived, with its `updated_at`. Never
   report "a comment exists" on the strength of a baseline-era comment. Name the two ordinary causes
   above, plus any failed polls separately (so a rate-limited or expired token reads as its own
   cause, not as a slow or broken bot). Then let the user decide.
