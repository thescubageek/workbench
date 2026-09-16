---
project: wb 2.0.0 tracker-free modernization
plan: docs/plans/2026-09-08-upstream-fable-merge/
created: 2026-09-15
status: verification
git_branch: thescubageek/gabe-fable-merge-research
git_commit: 833fc94
current_phase: 4
total_tasks: 64
completed_tasks: 63
---

# Handoff: reach 6c and 6a from the environment, not the task

## Where this picks up

Two rounds are recorded in `tasks.md` → Implementation Notes (entries dated 2026-09-15: "run,
not grepped", "findings fixed", "failure paths were run", "adversarial round's findings fixed").
Read those four first. Ten items have passed on the artifact. Two paths have **never been
reached**: `implement` 6c (a verified failure gets exactly one escalation, then a human) and 6a
(truncation diagnosed as truncation, not failure). Every attempt to reach them by planting a
defect *in the task* was absorbed upstream — the coordinator read the contradiction and refused
to spawn, a worker declined an out-of-scope instruction, the pre-split fired on a ~200-call task.
This round reaches them from the **environment**, so the task itself is sound and only the
mechanism under test is unusual.

It also verifies the four fixes from `833fc94`, which no run has exercised yet.

## Method — unchanged from the earlier rounds

- Judge from the artifact on disk, never from the session's report. For ordering claims, use
  the headless session's tool-call stream.
- Every stage runs in its own headless session that has not read this document. Launch them
  with **`--allowedTools=Skill`** — without it, mid-conversation stage calls (`update_status` at
  Step 9, the `model-help` gate) are denied and the run cannot complete.
- Record the cwd and permission settings of every headless run. Write `--disallowedTools=Skill`
  with `=` if you ever need it; the space form swallows the prompt.
- Do not restore or reset a scratch repo while a headless session may still be in its Step 9 —
  that collision cost round two a run.

Plugin path for every launch, except item 2 which uses a modified copy:

```bash
--plugin-dir /Users/thescubageek/conductor/workspaces/workbench/tallinn/plugin
```

Fresh scratch repo: `mkdir -p ~/projects/wb-round3 && cd $_ && git init -q`. Seed it with a
tiny library, **no `.gitignore`** (item 4 needs `__pycache__` to appear untracked), and take it
through `create_project → create_research → create_design → create_tasks` with a plan of two
phases and four to five tasks. Every task's acceptance criterion must include **"the full test
suite passes"** — that is what carries the planted failure to the verifier.

## The tests

1. **6c from the environment — a verifier FAIL on a correct task.** After `create_tasks`,
   add `tests/test_sentinel.py` containing one test that fails unconditionally, and commit it
   as a seed commit so the tree is clean. Then `/wb:implement --auto <dir> 1`. The worker's
   targeted run passes; the verifier's full-suite run cannot. PASS, from the artifact and the
   coordinator's stream: the task's checkbox is **reset to `[ ]` before** the escalation spawn;
   **exactly one** escalation, one rung up from the tier that failed, named in one line; the
   escalated attempt re-verifies and fails again (the sentinel is still there); the tree ends
   clean via a `WIP <id>: blocked …` commit or a `git restore` of the worker's reported paths,
   never `git checkout -- .`; the task is on the blocking list with the reason; **the journal
   entry stays `(open)`, marked blocked, with Next action naming the checkpoint** — this is fix
   (i), never observed; the next task runs. FAIL: a second automatic retry, `[x]` on the blocked
   task, a `(closed)` blocked entry, or leftover changes when the next worker spawned.
   *Record which way it went if the worker instead deletes the sentinel (scope creep → verifier
   FAIL → 6c anyway) or the verifier passes the task by attributing the failure elsewhere. Both
   are findings about those layers, and the second means 6c is still unreached.*

2. **6a — deterministic truncation via a lowered turn limit.** Make a scratch copy of the
   plugin and lower only the worker's limit:

   ```bash
   rm -rf /tmp/wb-trunc && cp -R /Users/thescubageek/conductor/workspaces/workbench/tallinn/plugin /tmp/wb-trunc
   sed -i '' 's/^maxTurns: 60$/maxTurns: 8/' /tmp/wb-trunc/agents/task-worker.md
   grep -n '^maxTurns' /tmp/wb-trunc/agents/task-worker.md   # must read 8
   ```

   Run `/wb:implement --auto <dir> 2` with `--plugin-dir /tmp/wb-trunc` on an ordinary task.
   PASS: 6a reads `[ ]` beside substantial, coherent changes and names it **truncation**; the
   coordinator finishes the remaining slice itself or re-delegates **only what is left**, with
   the landed work described as context; nothing already landed is re-run; the tier is **not**
   raised for it. FAIL: it is called a genuine failure and sent to 6c, or the whole task is
   re-run with the same context. Delete `/tmp/wb-trunc` afterwards.

3. **Staging by path — fix (j).** Over every implementation commit in the scratch repo:
   `git show --stat --format= <sha>` must list **no** `__pycache__/` or `*.pyc` path, and the
   verifier's output for at least one task must carry the new warning naming the untracked
   artifacts and the missing `.gitignore` entry. Control: `git status --short` after the run
   shows `__pycache__/` **untracked**, proving the artifacts existed and were left alone.

4. **Headless `update_status` completes with `--allowedTools=Skill` — the (h) fallback is not
   needed.** At each `--auto` checkpoint the artifact's counters are reconciled
   (`completed_tasks` equals the `[x]` count, `current_phase` advanced) and the checkpoint's
   `update_status` box is `[x]`. Then run one checkpoint **without** the flag: PASS is the
   report saying the skill could not be invoked and the counters were left alone, with
   `completed_tasks` in frontmatter **unchanged** from before the run — not hand-edited.

5. **The presentation wording on resume.** Kill `create_design` at Step 6 as round two did,
   resume cold. PASS: the message reads *"Design document ready for approval at"*, not
   *"created at"*. Small, but it is the one fix from `833fc94` with no other test.

6. **Only if the user has pushed the branch — the literal cache path.** Ask first; if the
   branch is not on GitHub, record this item as *not run — branch unpushed* and stop here.
   If it is: the installed plugin's root must resolve to
   `~/.claude/plugins/cache/<marketplace>/wb/2.0.0/`, which only a GitHub-source install
   produces. The existing `thescubageek-workbench` marketplace tracks the repo's default
   branch, so this needs a marketplace entry at the branch ref. **Confirm with the user before
   every step that changes global plugin state, record `claude plugin list` before and after,
   and restore the original install.** From a scratch cwd with
   `--settings '{"permissions":{"blockReadsOutsideWorkingDirectories":true}}'` and
   `--permission-mode default`, run `/wb:update_status <dir>` headlessly. PASS: the refused
   path names the **cache** directory, the stop fires, no `cat`, `tasks.md` md5 unchanged.

## Recording

One dated entry in `tasks.md` → Implementation Notes, PASS/FAIL per item with the evidence
quoted, cwd and settings for every permission run. Defects are **filed, not fixed** (D20).
Archive any contaminated run under the scratch repo's `scratchpad/`.

## Standing

**Do not tag and do not push.** `P4-T10` is the user's alone; pushing the branch for item 6 is
also theirs. The plan's journal has four `(closed)` entries from today on top and the
2026-09-10 release-hold entry, still `(open)`, beneath them — leave it.

## Suggested settings

`claude-opus-5`, high. Item 1 needs patience: worker, verifier, escalation worker, verifier
again, then the next task.
