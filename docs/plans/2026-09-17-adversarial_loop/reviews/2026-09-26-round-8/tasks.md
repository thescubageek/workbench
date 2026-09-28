---
project: adversarial_loop
reviews: docs/plans/2026-09-17-adversarial_loop
round: 8
created: 2026-09-26
status: in-progress
total_tasks: 2
completed_tasks: 0
task_tracking: markdown-checkboxes
---

# Remediation — adversarial review round 8

Target: the two candidates round 7's own verification filed in
`reviews/2026-09-21-round-7/tasks.md` → Implementation notes. Neither came from a review pass;
both were measured while closing round 7. No new review was run — PD5-2 chose fewest defects, and
these two are the known set. If this round reaches clean, the release closes.

## How each task is verified

Every task carries its finding's `failure_scenario` as its acceptance criterion, and **the
criterion is run before the fix**. A criterion that passes before the change is not a criterion.

## Tasks

- [x] **R8-T1** — `plugin/skills/update_status/templates/frontmatter-fragments.md:13,37-42` — the
      `tasks.md` fragment's round carve-out stops one row short: it omits `current_phase` for a
      round and still writes `last_updated`, `git_commit` and `git_branch`, three keys
      `plugin/docs/reference/remediation-plan.md:102` lists as absent by design and never
      reported as missing.
      **Fails when:** `/wb:update_status` on a round directory, rendered faithfully from the
      fragment, writes three keys the contract says a round does not carry; the next
      `validate_project` run over that round sees frontmatter §9 does not sanction. Round 7's
      own close followed the reference doc instead of the fragment and wrote only `status`,
      `total_tasks` and `completed_tasks` — two shipped authorities disagreeing, resolved by the
      session's judgement rather than by either file.
      **Acceptance (shape 3)**: dual grep — the carve-out table at `frontmatter-fragments.md:13`
      names all four keys a round omits (`current_phase`, `last_updated`, `git_commit`,
      `git_branch`), and `remediation-plan.md:102` is unchanged, so both files now say the same
      set. RED today: the table names one. (~4 calls) (completed 2026-09-26 19:01)

- [x] **R8-T2** — `plugin/skills/adversarial-review/SKILL.md:293` — the blast-radius search's
      engine varies by invocation, and nothing in the block can tell which ran.
      **Fails when:** in a top-level Bash-tool call `grep` is a shell function from
      `~/.claude/shell-snapshots/` that re-execs as ugrep honouring `.gitignore`, so
      gitignored-but-tracked files are skipped at exit 0 with no diagnostic; the identical line
      inside a script file gets the system binary, because a non-interactive `zsh script.sh`
      never sources the snapshot. Measured: bare `grep` 30 hits against `command grep` 52 on one
      symbol, all dropped files tracked. Neither `search=$?` nor `filter=$?` sees it — the search
      did not fail, it read a smaller tree. The two path spellings R7-T1 had to match are this
      same split: ugrep emits no `./` prefix, the binary does. `.claude/wb/knowledge.md` carries
      the entry and its `Check it`.
      **Corrected severity, carried from round 7:** in this repository the dropped hits are plan
      documents citing a filename, not code callers, and in an ordinary repository the ignored
      tree is build output the measurement is right to skip. The defect is not under-reporting;
      it is that two honest runs of one measurement can disagree and the reconnaissance summary
      reports whichever it got as fact.
      **Acceptance (shape 1 + shape 3)**: execute the knowledge entry's `Check it` as written and
      assert the two counts differ today (RED). After the fix, the block pins its engine —
      `command grep`, so the snapshot function is bypassed and the result is the same in a tool
      call and in a script — and the "details in that command" list gains one bullet stating
      why, with the bullet count and its heading number agreeing (R7-T8's criterion, re-run).
      Then re-run the `Check it` through the block's own spelling and assert the count matches
      `command grep`'s. Do not add an `--ignore-files`-style exclusion in its place: the
      `--exclude-dir=.context` already scopes the search, and a gitignore-honouring engine fails
      toward "isolated". (~6 calls) (completed 2026-09-26 19:06)

### 📝 Modified Files (Round 8)

#### Code Files

- `plugin/skills/update_status/templates/frontmatter-fragments.md` - carve-out row omitting
  `last_updated`, `git_commit`, `git_branch` for a round (R8-T1)
- `plugin/skills/adversarial-review/SKILL.md` - blast-radius search pinned to `command grep`;
  the seventh "details in that command" bullet, heading count updated (R8-T2)

#### Test Files

None. Both acceptance criteria are executed commands — a dual grep and a hash (R8-T1); the
knowledge entry's `Check it`, R7-T8's bullet count and a top-level-versus-script count (R8-T2) —
run against the working tree rather than committed as a test.

**Quick test commands:**

```bash
./plugin/scripts/lint --all
./plugin/scripts/check-guards plugin/
./plugin/scripts/check          # every gate; mostly test-guards
```

## Implementation notes

- **Both tasks were found by verification, not review.** Round 7 ran no review pass over its own
  fix surface; these are what closing the round measured. The breaker has no ledger row for
  round 8 because no findings were adjudicated — the tasks are decisions already taken, filed
  as work.
- **R8-T2 changes a measurement the tier rests on.** After it lands, the next reconnaissance
  summary in this repository will count more call sites than the last one did for the same
  symbol. That is the engine being pinned, not the blast radius growing; say so if it is
  noticed.
- **Not tasked, recorded so it is not lost**: the attestation list still lives only in session
  memory until `implement` Step 8.4 (round 6's checkpoint note); `--since=<ref>` / `--range`
  for `adversarial-review` (PD5-1, deferred to 3.1); the out-of-delta Step 2 and Step 4 items in
  round 7's notes.
