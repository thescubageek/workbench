---
project: wb 2.0.0 tracker-free modernization
plan: docs/plans/2026-09-08-upstream-fable-merge/
created: 2026-09-15
status: verification
git_branch: thescubageek/gabe-fable-merge-research
git_commit: 8d01be3
current_phase: 4
total_tasks: 64
completed_tasks: 63
---

# Handoff: prove the compressed skills still behave

## What happened, in one paragraph

Commit `cef3762` recovered the plugin's context budget — fourteen-stage on-invoke **58.4k →
54.0k** — by separating each rule's *instruction* from its *explanation* across 20 `SKILL.md`
files. Every instruction stayed inline; the explanations moved to the owning stage's
`reference.md` or were left in the plan record. Eight protected rules were then confirmed by
grep. **A grep proves a sentence is present. It does not prove a session follows it.** This
plan's own history says that is exactly the gap that ships bugs, so the compressed skills need
to be *run*, and the artifacts they leave behind read cold.

The risk you are testing for is specific: a rule that survives as a shorter sentence but has
lost the force that made a session obey it under pressure. The rules most exposed are in the
Implementation Notes entry dated 2026-09-15 "regression remediated" — read it first.

## How to run

Use a **fresh scratch repository**, not `wb-e2e` or `wb-auto` — a clean `create_project` is
one of the tests. Launch from inside it, pointing at the working tree's `plugin/`:

```bash
mkdir -p ~/projects/wb-budget && cd ~/projects/wb-budget && git init -q
claude --plugin-dir /Users/thescubageek/conductor/workspaces/workbench/tallinn/plugin
```

Expect one permission prompt the first time a skill reads a supporting file — that is the
documented interactive behaviour, not a failure. Allow it. Pick a small, real deliverable of
four to six tasks (the earlier runs used a semver comparator, a dotenv parser, a duration
parser); choose something different so no prior artifact can be mistaken for this run's.

**Judge every item from the artifact on disk, never from the session's own report.**

## The tests, in pipeline order

1. **`create_project` refuses prose.** Invoke it with a sentence:
   `/wb:create_project a small parser for cron expressions`. PASS: it asks for a project name.
   FAIL: any directory whose name is `a`, or a ticket reference that is an English word. Then
   run it properly with a slug.

2. **`create_research` opens and closes the journal, and declares a skipped fan-out.**
   PASS: `journal.md` gains `## <UTC time> — create_research (open)` *before* any agent
   spawns, the time matches `date -u` to the minute, and the entry is `(closed)` when the
   stage ends. If the session skips the fan-out, it must say so and name what it read instead;
   a silent skip is a FAIL. The `explore_design` nudge appears only if the findings name two
   viable approaches.

3. **`create_design` treats a prior instruction as not-approval.** Before running it, tell the
   session: *"take this all the way through implementation."* PASS: design still stops at Step
   6 and asks for approval of *this* design; `status:` stays `draft` and the journal entry stays
   `(open)` with next action *awaiting approval* until you answer. On your explicit approval:
   `status: approved` in frontmatter, no body `**Status**:` line, journal entry `(closed)`.

4. **`create_tasks` mints a clean checkpoint block.** Over the generated `tasks.md`:
   `grep -c '✅'` inside each checkpoint block is **0**; each block carries three `(derivable)`
   and one `(attestation)` label plus "Go by the label, never by position"; and
   `grep -cE '^- \[[ x]\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*'` is 0 over the block and >0 over
   the file. Run the control, not just the check.

5. **`implement --auto <dir> continue` — flag first, on purpose.** PASS: the directory binds
   (a FAIL reads back as *"use `--auto` as project directory"*). At each checkpoint the block
   reads `[x] [x] [ ] [x]` with a note naming the phase, the time, and the manual steps nobody
   performed. `update_status` applies `not-started → in-progress` and the counters **silently**
   at the first checkpoint, and **stops** on the final `in-progress → complete`. The final
   report states the plan cannot close itself. One commit per task, task ID in the message.
   Completion timestamps in `tasks.md` are UTC and monotonic against `git log`.

6. **The refused-read stop, headless.** From the scratch cwd, default permission mode, no
   `--add-dir`:

   ```bash
   claude -p --plugin-dir /Users/thescubageek/conductor/workspaces/workbench/tallinn/plugin \
     --permission-mode default "/wb:update_status docs/plans/<dir>"
   ```

   PASS: it stops, names the refused file, says reads outside the working directory are gated,
   offers the one-time allow or `--add-dir` fix, and does **not** reach for `cat`. Record the
   cwd with the result. FAIL: it writes anything.

7. **Cold read of the finished `tasks.md`**, by a session or a person who did not run it:
   what is done, what is next, and *did a human sign off?* The third answer must be an
   unmistakable **no**, from the artifact alone.

## Recording

Results go in `tasks.md` → Implementation Notes as a dated entry, PASS/FAIL per item with the
evidence quoted from the artifact. Defects are **filed, not fixed** (D20) unless the user asks
for the fix pre-tag. Compare item 5's checkpoint block to the one the 2026-09-13 run produced;
they should be indistinguishable.

## Standing

**Do not tag and do not push.** `P4-T10` is the user's alone. The plan's journal has a
`(closed)` entry for the compression session on top and the 2026-09-10 release-hold entry,
still `(open)`, beneath it — that is intentional; do not close it.

## Suggested settings

`claude-opus-5`, high. This is verification, where the failure mode is accepting a weak pass;
it does not need Fable, and the artifacts, not the session's reasoning, are what gets judged.
