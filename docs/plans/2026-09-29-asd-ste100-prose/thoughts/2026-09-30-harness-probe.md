# Harness driver probe (P1-T3)

This record tests assumption A6 in design.md. A6 says a headless `claude -p --plugin-dir <tree> --allowedTools=Skill` run executes a stage well enough for before/after comparison.

**Result: PASS.** All three pass conditions hold. A6 is not marked in design.md, because the task asks for that only on failure.

## Environment

| Field | Value |
| ----- | ----- |
| cwd | `/var/folders/0d/sbn7z4ps0pv7xd5l4t0skfm80000gp/T/tmp.QxAYj5EwSL/run` (the transcript resolves it to `/private/var/...`) |
| `$tmp` | `/var/folders/0d/sbn7z4ps0pv7xd5l4t0skfm80000gp/T/tmp.QxAYj5EwSL` (kept, not deleted) |
| Plugin tree | `$tmp/before/plugin`, from `git archive 4b32306 plugin`. Its `plugin.json` says `2.1.1`. |
| `claude --version` | `2.1.285 (Claude Code)` |
| Model flag | `--model sonnet`. The transcript reports `claude-sonnet-5-5` on every assistant turn. |
| Permission mode | `acceptEdits`. Auto mode was off. |
| `blockReadsOutsideWorkingDirectories` | Not set. The `permissions` object in `~/.claude/settings.json` is empty, so the default applies. `.claude/wb/knowledge.md` records that as off on this machine. The setting was not changed. |
| Start | 2026-09-30T00:22:29Z |
| End | 2026-09-30T00:23:28Z |
| Duration | 59 s |
| Exit code | 0 |
| stdout | `$tmp/stdout.txt` (1189 bytes) |
| stderr | `$tmp/stderr.txt` (empty) |
| Transcript | `~/.claude/projects/-private-var-folders-0d-sbn7z4ps0pv7xd5l4t0skfm80000gp-T-tmp-QxAYj5EwSL-run/e0280514-095f-4308-8d76-d910190f71fc.jsonl` |

The cwd is outside the plugin tree. The two are sibling directories under `$tmp`.

## Command

The setup ran from the repository root. It followed the Phase 1 §2 sequence exactly.

```bash
tmp=$(mktemp -d)
mkdir -p "$tmp/before"
git archive 4b32306 plugin | tar -x -C "$tmp/before"
cp -R evals/fixture/project "$tmp/run"
mkdir -p "$tmp/run/docs/plans" && cp -R evals/fixture/plan-seed "$tmp/run/docs/plans/2026-01-01-fixture"
cd "$tmp/run" && git init -q && git add -A && git commit -qm fixture
claude -p --plugin-dir "$tmp/before/plugin" --allowedTools=Skill \
  --permission-mode acceptEdits --model sonnet \
  "/wb:create_research docs/plans/2026-01-01-fixture $(cat <repo>/evals/fixture/QUESTION.md)"
```

The run added `tee` to both streams, `date` calls around the command, and an `$?` capture. The `claude` arguments were not changed. No diagnostic variant was run.

## Pass conditions

| # | Condition | Check | Result |
| - | --------- | ----- | ------ |
| 1 | `research.md` has `status: complete` | `grep '^status: complete'` on `$tmp/run/docs/plans/2026-01-01-fixture/research.md` | **Holds.** The seed had `status: draft`. |
| 2 | At least 2 expected facts cited at their `file:line` | Each `expected.json` ref searched as `[src/linkcheck/]<file>:<line>` | **Holds.** 4 exact citations, and 2 more as covering ranges. |
| 3 | stdout has the `✅ research.md updated` line | `grep -F '✅ research.md updated'` on `$tmp/stdout.txt` | **Holds.** |

The completion line was:

```text
✅ research.md updated — how linkcheck decides a link is broken; 6 findings, 9 code refs. Next: `/wb:create_design`
```

### Facts cited

| Fact | Expected ref | Exact citation | Covering range |
| ---- | ------------ | -------------- | -------------- |
| F1 | `src/linkcheck/config.py:3` | yes (2) | — |
| F2 | `src/linkcheck/config.py:4` | yes (2) | — |
| F3 | `src/linkcheck/config.py:9` | yes (1) | `config.py:8-9` |
| F4 | `src/linkcheck/checker.py:21` | no | `checker.py:20-21` |
| F5 | `src/linkcheck/checker.py:31` | yes (1) | `checker.py:24-31` |
| F6 | `src/linkcheck/cli.py:18` | no | `cli.py:17-19` |

Only exact citations count toward condition 2. F1, F2, F3 and F5 meet it.

## Stage loaded or improvised

The transcript shows the stage loaded. This is evidence for the human reviewer. It is not the manual check.

- The leading slash command expanded before the session started. The first user turn has the `create_research` body with `Base directory for this skill: $tmp/before/plugin/skills/create_research`.
- The session read `sub-agent-prompts.md`, `templates.md` and `reference.md` from `$tmp/before/plugin/skills/create_research/`. All three reads succeeded. The read boundary did not fire, which is consistent with the setting being off.
- No tool call was denied. There was no permission prompt. Two Bash calls ran (`ls`/`cat`, and `date`/`git rev-parse`).
- The session opened a journal entry before it wrote `research.md`, then closed it. That follows the stage's journal rule. The entry names `P0-T2`, which is the seed `tasks.md` research task.
- The completion line follows the shape in the 2.1.1 `SKILL.md:251`.

## Limits of this result

- **The sub-agent fan-out was not exercised.** The session made no Task calls. It printed "I skipped the agent fan-out" and named the four files it read instead. The 2.1.1 stage allows this at `SKILL.md:173-176` when the whole surface is already in context, and it requires the output to say so. So the skip follows the stage. But it means this probe does not show that sub-agent spawns work headlessly. A larger fixture would be needed to test that.
- The probe ran one stage, `create_research`, on one tree. Other stages were not run.
- The read boundary was off. The result does not show what happens when `blockReadsOutsideWorkingDirectories` is on. In that case `--add-dir <tree>` would be needed (`.claude/wb/knowledge.md`, the read-boundary entry).
- One run gives no measure of run-to-run variance.
