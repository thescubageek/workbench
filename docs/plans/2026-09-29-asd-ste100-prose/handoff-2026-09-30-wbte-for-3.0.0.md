---
created: 2026-09-30T12:36:27+00:00
type: handoff
project: asd-ste100-prose
phase: 7
handoff_reason: the 3.0.0 branch adopts wb Technical English (WBTE) from 2.2.0
last_task: P7-T2 — this handoff
git_commit: 4f35e39
git_branch: wb-2.2.0/asd_ste100_prose
repository: thescubageek/workbench
---

# Handoff: WBTE (2.2.0) for the 3.0.0 branch

**Created**: 2026-09-30 12:36 UTC
**Reason**: `adversarial-loop-skill-research` (3.0.0) merges `main` after 2.2.0 lands. This file
says what 2.2.0 changed, what the merge will conflict on, and what the first release after 3.0.0
must still do.
**Current Phase**: Phase 7 of 7
**Overall Progress**: 36/40 tasks at the time of writing (count the ID-scoped task lines in
`tasks.md`)

## Quick Start

On the same machine, use `claude --resume` instead. This handoff is for the 3.0.0 branch and its
maintainers. To load it as context, run `/wb:resume_handoff docs/plans/2026-09-29-asd-ste100-prose/handoff-2026-09-30-wbte-for-3.0.0.md`.

## Current State Summary

**What the release builds**: wb Technical English (WBTE), a writing standard for workbench
output, adapted from the principles of ASD-STE100 Issue 9 (design.md, D1 and D2).

**Where the work is**: 2.2.0 is on `wb-2.2.0/asd_ste100_prose`, not yet merged or pushed.
The version bump and the release checks are P7-T3 to P7-T5.

**The rule for shared files (D-Q3)**: in the 48 `plugin/` files that 3.0.0 also changes, 2.2.0
adds only a link line, and in `wb-prime.sh` only the rule card. Every prose rewrite of those files
waits for the first release after 3.0.0. One exception (D14): `plugin/scripts/README.md` and
`plugin/skills/help/SKILL.md` each gain a section for the new scripts and skill.

## New files

- `plugin/docs/reference/technical-english.md` — the single authority for the rules. No other
  file restates them, and `evals/link_check.py` checks that.
- `plugin/scripts/test-prime` — 42 contract checks for `wb-prime.sh`, including the card.
- `plugin/scripts/wbte-dictionary`, `plugin/scripts/test-wbte-dictionary` — the extractor for
  the user's own dictionary copy, and its test.
- `plugin/skills/wbte-dictionary/SKILL.md` — `/wb:wbte-dictionary`.
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

It has three hunks, and the file auto-merges with 3.0.0 at `2fff76c` (design.md D5):

1. A header bullet, after "exit 0 always":
   `#   - the WBTE rule card prints on every session start (startup, resume, compact), …`.
   It also says why the card does not print on PreCompact (D13).
2. A new `card()` function after `orientation()`. It prints card v3 (141 words) and the path
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

`git merge-tree --write-tree` of this branch with `adversarial-loop-skill-research` at `2fff76c`
(before the version bump):

| Path | Cause | Resolution |
| ---- | ----- | ---------- |
| `.claude-plugin/marketplace.json`, `plugin/.claude-plugin/plugin.json` | both branches change `version` (this conflict already exists with 2.1.1) | take 3.0.0 |
| `README.md` | both branches edit it (this conflict already exists with 2.1.1) | keep both. 2.2.0 adds the "wb Technical English (WBTE)" section |
| `.gitignore` | both branches append `__pycache__/` and `*.pyc`. 2.2.0 also adds `evals/runs/` | keep one copy of each line, and keep `evals/runs/` |
| `.claude/wb/knowledge.md` | both branches append entries | keep both appended entries |
| `plugin/scripts/README.md` | both branches add script sections after `test-quiet` (D14) | keep both. 2.2.0 adds `wbte-dictionary`, `test-wbte-dictionary` and `test-prime`, and one clause in the `test-lint` entry |
| `plugin/skills/help/SKILL.md` | both branches add entries after `/wb:model-help` (D14) | keep both. 2.2.0 adds the `/wb:wbte-dictionary` entry |

P7-T4 and P7-T5 run the check again on the final tree and record any other path.

## The post-3.0.0 pass

The first release after 3.0.0 (3.0.1 or 3.1.0, design.md D-Q3) must still do these:

1. **Rewrite the prose of the shared files in WBTE.** They have the link line only. The rewrite
   must keep every exempt token (`technical-english.md`, Exempt tokens), and each change must
   pass the harness gate.
2. **Rewrite the shared `create_tasks/templates/tasks-md-template.md` boilerplate** (D8). All
   the semicolons left in generated plans come from its checkpoint block, its ID-shape rule, its
   "Tasks run in document order" note, and its prerequisites line.
3. **Gate the agent draft again.** The lite rewrite of `agents/codebase-analyzer.md` and
   `agents/codebase-locator.md` was restored in P5-T4 after a 1-repeat gate found a loss. The
   draft was in `.context/lite/` on the 2.2.0 machine. Gate it with 3 repeats.
4. **Gate the remaining non-shared instruction files.** 2.2.0 rewrote the output templates and
   the Phase 5 files only.

**The 48 shared files** (`git diff --name-only --diff-filter=M 46ef587 2fff76c -- plugin`,
limited to the files on `4b32306`). The 13 that 2.2.0 changed are listed above. These are the
other 35. Two of them, `plugin/scripts/README.md` and `plugin/skills/help/SKILL.md`, gained
sections in 2.2.0 (D14), but their existing prose is not rewritten:

- `plugin/.claude-plugin/plugin.json`
- `plugin/agents/pattern-finder.md`
- `plugin/agents/task-verifier.md`
- `plugin/agents/task-worker.md`
- `plugin/scripts/README.md`
- `plugin/scripts/lint`
- `plugin/scripts/quiet`
- `plugin/scripts/test-quiet`
- `plugin/skills/create_design/SKILL.md`
- `plugin/skills/create_execution/SKILL.md`
- `plugin/skills/create_handoff/SKILL.md`
- `plugin/skills/create_tasks/SKILL.md`
- `plugin/skills/daily-digest/SKILL.md`
- `plugin/skills/daily-digest/sources.md`
- `plugin/skills/forge/SKILL.md`
- `plugin/skills/help/SKILL.md`
- `plugin/skills/implement/SKILL.md`
- `plugin/skills/implement/reference.md`
- `plugin/skills/implement_coordinated/SKILL.md`
- `plugin/skills/implement_inline/SKILL.md`
- `plugin/skills/implement_inline/reference.md`
- `plugin/skills/implement_tasks/SKILL.md`
- `plugin/skills/model-help/SKILL.md`
- `plugin/skills/project-structure/SKILL.md`
- `plugin/skills/research-validation/SKILL.md`
- `plugin/skills/resume_handoff/SKILL.md`
- `plugin/skills/review-prep/SKILL.md`
- `plugin/skills/touch-grass/SKILL.md`
- `plugin/skills/update_status/SKILL.md`
- `plugin/skills/update_status/reference/error-handling.md`
- `plugin/skills/validate_execution/SKILL.md`
- `plugin/skills/validate_project/SKILL.md`
- `plugin/skills/validate_project/reference/validation-checklist.md`
- `plugin/skills/validate_project/reference/validation-rules.md`
- `plugin/skills/verification-before-completion/SKILL.md`

**The non-shared files that 2.2.0 did not rewrite** (36):

- `plugin/agents/product-behavior-analyzer.md`
- `plugin/agents/research-validator.md`
- `plugin/docs/reference/README.md`
- `plugin/docs/reference/branch-naming.md`
- `plugin/skills/clip/SKILL.md`
- `plugin/skills/create_handoff/reference.md`
- `plugin/skills/create_mockup/SKILL.md`
- `plugin/skills/create_mockup/reference.md`
- `plugin/skills/create_mockup/sub-agent-prompts.md`
- `plugin/skills/create_product_research/reference.md`
- `plugin/skills/create_product_research/sub-agent-prompts.md`
- `plugin/skills/create_project/reference.md`
- `plugin/skills/doc-adherence/SKILL.md`
- `plugin/skills/eli5-clip/SKILL.md`
- `plugin/skills/explore_design/SKILL.md`
- `plugin/skills/fetch-issues/SKILL.md`
- `plugin/skills/forge/examples.md`
- `plugin/skills/implement/prompts/escalation-worker-prompt.md`
- `plugin/skills/implement/prompts/verifier-prompt.md`
- `plugin/skills/implement/prompts/worker-prompt.md`
- `plugin/skills/jira-context/SKILL.md`
- `plugin/skills/mockup-iteration/SKILL.md`
- `plugin/skills/resolve_questions/examples.md`
- `plugin/skills/resolve_questions/reference.md`
- `plugin/skills/resume_handoff/reference.md`
- `plugin/skills/status-sync/SKILL.md`
- `plugin/skills/tdd-discipline/SKILL.md`
- `plugin/skills/tracer-bullet/SKILL.md`
- `plugin/skills/update_status/reference/configuration.md`
- `plugin/skills/update_status/reference/important-notes.md`
- `plugin/skills/update_status/reference/smart-status-detection.md`
- `plugin/skills/update_status/reference/status-transition-logic.md`
- `plugin/skills/validate_execution/reference.md`
- `plugin/skills/validate_execution/sub-agent-prompts.md`
- `plugin/skills/validate_project/reference/configuration.md`
- `plugin/skills/validate_project/reference/important-guidelines.md`

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
  the card. The card has room for 9 more words (`test-prime` limits it to 150).
- A resumed headless session is refused reads of a `--plugin-dir` stage's own files without
  `--add-dir` (`.claude/wb/knowledge.md`).
- `wb_lint_ignored` did not ignore a path that is in both `.gitignore` and `.wblintignore`.
  P8-T2 fixed it in `plugin/scripts/lint-common.sh`, which 3.0.0 does not have yet (it came in
  2.1.1). The fix merges with no conflict.
- A manual `/compact` shows PreCompact's stdout, and that stdout reaches the next context. So
  PreCompact output is model-visible there, against the `wb-prime.sh` header. The card now skips
  PreCompact (P8-T5). The recovery text still prints twice when a plan is active (2.1.1
  behaviour, a follow-up).
- **Known remainder (D11):** the final Objective 1 run has 2 chat IDs used alone, in one
  `create_tasks` summary sentence. If this shows up in real use, a 2.2.x patch tightens it.

## Artifacts and References

### Project Documents

- Research: `docs/plans/2026-09-29-asd-ste100-prose/research.md`
- Design: `docs/plans/2026-09-29-asd-ste100-prose/design.md` (D-Q1 to D-Q5, D1 to D14)
- Tasks: `docs/plans/2026-09-29-asd-ste100-prose/tasks.md`
- Measurements: `thoughts/2026-09-30-baseline.md`, `-card-measurement.md`,
  `-link-measurement.md`, `-objective-1-report.md`, `-judge-calibration.md`, `-lite-verdicts.md`
- Validation: `docs/plans/2026-09-29-asd-ste100-prose/validation-report.md`

## Handoff Verification

Before you use this handoff, check these items:

- [ ] `git merge-tree --write-tree <this branch> adversarial-loop-skill-research` conflicts only
      on the paths above
- [ ] `./plugin/scripts/test-prime` passes on the merged tree
- [ ] `python3 evals/link_check.py` and `python3 evals/token_check.py` pass on the merged tree

---

**Handoff complete.** To resume, run `/wb:resume_handoff docs/plans/2026-09-29-asd-ste100-prose/handoff-2026-09-30-wbte-for-3.0.0.md`.
