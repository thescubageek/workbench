---
created: 2026-09-30T12:36:27+00:00
type: handoff
project: asd-ste100-prose
phase: 10
handoff_reason: the 3.0.0 branch adopts wb Technical English (WBTE) from 2.2.0
last_task: P10-T2 — the corrections from the Phase 7 and Phase 8 check
git_commit: 1d45555
git_branch: wb-2.2.0/asd_ste100_prose
repository: thescubageek/workbench
---

# Handoff: WBTE (2.2.0) for the 3.0.0 branch

**Created**: 2026-09-30 12:36 UTC
**Reason**: `adversarial-loop-skill-research` (3.0.0) merges `main` after 2.2.0 lands. This file
says what 2.2.0 changed, what the merge will conflict on, and what the first release after 3.0.0
must still do.
**Updated**: 2026-09-30, after the manual checks of Phases 2 to 8
**Current Phase**: Phase 10 of 10
**Overall Progress**: count the ID-scoped task lines in `tasks.md`. All tasks are done, and the
Phase 7 to 9 sign-offs are with the user

## Quick Start

This handoff is for the 3.0.0 branch and its maintainers. The resume command is at the end.

## Current State Summary

**What the release builds**: wb Technical English (WBTE), a writing standard for workbench
output, adapted from the principles of ASD-STE100 Issue 9 (design.md, D1 and D2).

**Where the work is**: 2.2.0 is on `wb-2.2.0/asd_ste100_prose`, not yet merged or pushed.
The version bump and the release checks are done.

**The rule for shared files (D-Q3)**: 2.2.0 changes 16 of the 48 `plugin/` files that 3.0.0
also changes. 12 get only a link line, `wb-prime.sh` gets only the card, `plugin.json` gets the
version, and `plugin/scripts/README.md` and `plugin/skills/help/SKILL.md` gain new sections
(D14). The other 32 do not change. Every prose rewrite waits for the first release after 3.0.0.

## New files

- `plugin/docs/reference/technical-english.md` — the single authority for the rules. No other
  file restates them, and `evals/link_check.py` checks that.
- `plugin/scripts/test-prime` — 44 contract checks for `wb-prime.sh`, including the card.
- `plugin/scripts/wbte-dictionary`, `plugin/scripts/test-wbte-dictionary` — the extractor for
  the user's own dictionary copy, and its test.
- `plugin/skills/wbte-dictionary/SKILL.md` — `/wb:wbte-dictionary`.
- `plugin/skills/pr-description/` — `/wb:pr-description` and its generic PR template (D15 to
  D17).
- `plugin/scripts/pr-template`, `plugin/scripts/test-pr-template` — the PR-template finder and
  its test.
- `evals/` — the maintainer-only eval harness. It is never shipped. See "Run the harness".
- `.wblintignore` — keeps lint away from `evals/fixtures/planted/` and `evals/runs/`.

## The link line

The text is one line after each template's title line. The relative path depends on depth:
`../../../` from `plugin/skills/<skill>/templates/`, and `../../` from `plugin/skills/<skill>/`.

```markdown
Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.
```

**The 12 shared locations that have it** (each gained exactly 2 lines, the link line and a blank
line):

- `plugin/skills/create_project/templates/journal-md-template.md`
- `plugin/skills/create_research/SKILL.md`
- `plugin/skills/create_tasks/templates/tasks-md-template.md`
- `plugin/skills/implement/templates/manual-verification-request.md`
- `plugin/skills/implement/templates/modified-files-fragment.md`
- `plugin/skills/implement/templates/phase-completion-report.md`
- `plugin/skills/implement_inline/templates/manual-verification-request.md`
- `plugin/skills/implement_inline/templates/phase-completion-report.md`
- `plugin/skills/update_status/templates/completion-summary.md`
- `plugin/skills/update_status/templates/frontmatter-fragments.md`
- `plugin/skills/update_status/templates/status-update-plan.md`
- `plugin/skills/validate_project/templates/validation-report.md`

In `create_research/SKILL.md`, the line sits just before the Step 8 completion line.

## The `wb-prime.sh` change

It has four hunks: the header bullet, `card()`, and one call in each branch. The file
auto-merges with 3.0.0 at `2fff76c` (design.md D5):

1. A header bullet, after "exit 0 always":
   `#   - the WBTE rule card prints on every session start (startup, resume, compact), …`.
   It also says why the card does not print on PreCompact (D13).
2. A new `card()` function after `orientation()`. It prints card v4 (149 words) and the path
   `$CLAUDE_PLUGIN_ROOT/docs/reference/technical-english.md`.
3. Two guarded calls:
   - In the recovery branch, before `[ "$count" -eq 0 ] && exit 0`. It skips PreCompact,
     because a manual `/compact` shows PreCompact's stdout in the next context (P8-T5):

     ```bash
     echo "$payload" | grep -qE '"hook_event_name" *: *"PreCompact"' ||
       [ "${WB_TECH_ENGLISH:-1}" = "0" ] || card
     ```

   - In the orientation branch, after the `PRIME.md`/`orientation` choice:
     `[ "${WB_TECH_ENGLISH:-1}" = "0" ] || { echo ""; card; }`

`--export` and the empty-payload exit do not change. With `WB_TECH_ENGLISH=0`, the output is
byte-identical to 2.1.1. `plugin/scripts/test-prime` proves each path. If 3.0.0 restructures
the orientation or recovery sections, place the two calls again and run `test-prime`.

## Expected merge conflicts

`git merge-tree --write-tree` of this branch with `adversarial-loop-skill-research` at `2fff76c`:

| Path | Cause | Resolution |
| ---- | ----- | ---------- |
| `.claude-plugin/marketplace.json`, `plugin/.claude-plugin/plugin.json` | both branches change `version` (this conflict already exists with 2.1.1) | take 3.0.0 |
| `README.md` | both branches edit it (this conflict already exists with 2.1.1) | keep both. 2.2.0 adds the "wb Technical English (WBTE)" section |
| `.gitignore` | both branches append `__pycache__/` and `*.pyc`. 2.2.0 also adds `evals/runs/` | keep one copy of each line, and keep `evals/runs/` |
| `.claude/wb/knowledge.md` | both branches append entries | keep both appended entries |
| `plugin/scripts/README.md` | both branches add script sections after `test-quiet` (D14) | keep both. 2.2.0 adds `wbte-dictionary`, `test-wbte-dictionary`, `test-prime`, `pr-template` and `test-pr-template`, and one clause in the `test-lint` entry |
| `plugin/skills/help/SKILL.md` | both branches add entries after `/wb:model-help` (D14) | keep both. 2.2.0 adds the `/wb:pr-description` and `/wb:wbte-dictionary` entries |

Run the same check again before the merge. The branches may have moved.

## The post-3.0.0 pass

The first release after 3.0.0 (3.0.1 or 3.1.0, design.md D-Q3) must still do these:

1. **Fix the judge first, before any gated rewrite.** The within-run judge (D7) cannot see a
   loss inside `research.md`. Add a check of each run's `research.md` against the baseline's
   expected facts and values. Also make the judge file a removed `file:line` under `lost_refs`,
   not `other_losses`. Recalibrate once for both (tasks.md, Implementation Notes).
2. **Rewrite the prose of the shared files in WBTE.** They have the link line only. The rewrite
   must keep every exempt token (`technical-english.md`, Exempt tokens), and each change must
   pass the harness gate.
3. **Rewrite the shared `create_tasks/templates/tasks-md-template.md` boilerplate** (D8). All
   the semicolons left in generated plans come from its checkpoint block, its ID-shape rule, its
   "Tasks run in document order" note, and its prerequisites line.
4. **Gate the agent draft again.** The lite rewrite of `agents/codebase-analyzer.md` and
   `agents/codebase-locator.md` was restored in P5-T4 after a 1-repeat gate found a loss. The
   draft was in `.context/lite/` on the 2.2.0 machine. Gate it with 3 repeats.
5. **Gate the remaining non-shared instruction files.** 2.2.0 rewrote the output templates and
   the Phase 5 files only.
6. **Apply the PR rules to 3.0.0's own PR text.** `reply-to-claude` posts PR comments with
   `gh pr comment`. Give its comment step the link line, so that the "Pull requests and commit
   messages" rules of `technical-english.md` apply there too.

**The file lists for this pass.** Make them from git instead of copying a list. The 16 shared
files that 2.2.0 changed are named under "Current State Summary". If `rtk` is installed, run
this through `rtk proxy`, because `rtk` rewrites `grep` and `comm` output.

```bash
git diff --name-only --diff-filter=M 46ef587 2fff76c -- plugin | sort > /tmp/shared
git ls-tree -r --name-only 4b32306 plugin | sort | comm -12 - /tmp/shared > /tmp/shared-48
git diff --name-only 4b32306 <the 2.2.0 merge commit> -- plugin | sort > /tmp/changed

cat /tmp/shared-48       # the 48 shared files: every one needs its prose rewrite
git ls-tree -r --name-only 4b32306 plugin | grep '\.md$' | sort \
  | comm -23 - /tmp/shared-48 | comm -23 - /tmp/changed
                         # 38 non-shared files that 2.2.0 did not rewrite, with the 2 agents of item 4
```

## Run the harness

The harness needs python3 and the `claude` CLI. See `evals/README.md`.

```bash
# the static checks, after any template change
python3 evals/link_check.py && python3 evals/token_check.py

# a gate: one tree against a before-run, on the large fixture
python3 evals/run.py --before <tree-or-ref> --repeats 3 --fixture evals/fixture-large
python3 evals/judge.py --fixture evals/fixture-large --run evals/runs/<timestamp> --within
python3 evals/report.py evals/runs/<timestamp>
```

- **Use `evals/fixture-large/` for any gate on sub-agent prompts or agent files.** On the small
  fixture, the stages read everything themselves and spawn no agents.
- **The gate is the within-run judge (D7).** Each run's `design.md` and `tasks.md` must keep the
  facts, `file:line` references and IDs of its own `research.md`.
- **Run gates one at a time.** Four parallel runs on the large fixture hit the individual spend
  limit on 2026-09-30. A repeat on the large fixture costs about $5 and takes 12 minutes.

## Critical Learnings

### Discoveries Not in Documentation

- A rule that lives only in the reference doc applies in about two runs of three, because the
  model does not always follow the link line (P4-T2). A rule that must always hold belongs on
  the card. Card v4 has 149 words, and `test-prime` limits it to 150, so a new card rule must
  replace old words.

## Artifacts and References

### Project Documents

The plan documents and the `thoughts/` records are in the same directory as this handoff.

## Handoff Verification

Before you use this handoff, check these items:

- [ ] `git merge-tree --write-tree <this branch> adversarial-loop-skill-research` conflicts only
      on the paths above
- [ ] `./plugin/scripts/test-prime` passes on the merged tree
- [ ] `python3 evals/link_check.py` and `python3 evals/token_check.py` pass on the merged tree

---

**Handoff complete.** To resume, run `/wb:resume_handoff docs/plans/2026-09-29-asd-ste100-prose/handoff-2026-09-30-wbte-for-3.0.0.md`.
