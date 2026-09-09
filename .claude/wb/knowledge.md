# Repository knowledge

Durable facts about **this repository** — a constraint, a convention, a tool quirk — that would
change how the next session works. Committed, so it travels with the repository.

## What qualifies

One fact per entry. It qualifies only if it would change how the **next** session works.

It does **not** qualify if it is:

- a task outcome — `journal.md` has those
- a plan deviation — a plan's Implementation Notes has those
- true of only one task

## Entry shape

```markdown
## <the fact, as a claim>

- **Why it matters**: <what a session would do differently>
- **Verified**: YYYY-MM-DD · <plan directory it came from>
- **Check it**: <a command or observation that shows whether it is still true>
```

The **Check it** line is the part that keeps this file from decaying. An entry is a dated
claim, not a standing rule: a session that finds one false **corrects or deletes it in the same
session**. That obligation is the other half of what makes the file trustworthy — without it,
this becomes the merged diary-and-rules file whose stale entries read as current authority, and
we have the in-repo cautionary example for that.

---

## `--plugin-dir` must point at `plugin/`, not the repository root

- **Why it matters**: after the 2.0.0 relocation the manifest lives in `plugin/`. A session
  started with `--plugin-dir .` does not error — it silently falls back to the **installed**
  marketplace copy, so working-tree changes are invisible and you debug the wrong files.
- **Verified**: 2026-09-08 · `docs/plans/2026-09-08-upstream-fable-merge/`
- **Check it**: `claude --plugin-dir . plugin details wb` reports `Source: wb@<marketplace>` and
  the installed version; `--plugin-dir plugin` reports `Source: wb@inline` and the working-tree
  version.

## `claude plugin details` can measure the working tree, via the global flag

- **Why it matters**: `claude plugin details <name>` alone requires the plugin to be installed,
  so it reports the marketplace cache, which lags the repository. Measuring a change you just
  made needs `claude --plugin-dir <path> plugin details <name>` — the flag goes **before** the
  `plugin` subcommand. `details` itself takes no `--plugin-dir` option.
- **Why else**: this is the direct measurement of per-skill token cost, so it is the tool for
  any question about what a change costs at invocation.
- **Verified**: 2026-09-08 · `docs/plans/2026-09-08-upstream-fable-merge/`
- **Check it**: `claude --plugin-dir plugin plugin details wb` prints a "Projected token cost"
  block; `claude plugin details wb --plugin-dir plugin` errors with `unknown option`.

## `claude plugin tag` wants the plugin directory, a git repo, and a clean tree

- **Why it matters**: three separate failures, all cheap to avoid. It takes the path to the
  directory holding `.claude-plugin/plugin.json` (so `plugin/`, not the repository root); it
  refuses to run outside a git repository; and it refuses a dirty working tree without
  `--force`. That last one means a release check must run **after** the version-bump commit,
  not before it.
- **Also**: this harness's tag convention is `<name>--v<version>` (`wb--v2.0.0`), not `v<version>`.
- **Verified**: 2026-09-08 · `docs/plans/2026-09-08-upstream-fable-merge/`
- **Check it**: `claude plugin tag --dry-run plugin/` on a clean tree prints the tag it would
  create; pointing it at the repository root reports "No plugin manifest found".

## `claude plugin validate` and `details` do not inspect agent frontmatter at all

- **Why it matters**: a green `validate` says nothing about whether an agent's `model:`,
  `effort:` or `maxTurns:` are correct — a nonsense model name and an invented key both pass
  silently, and the agent still enumerates. Do not treat those commands as a check on agent
  configuration.
- **What does validate it**: the harness at load time. Its error strings include
  `has invalid effort` and `has invalid maxTurns`, so both keys are parsed and value-checked;
  a bad value surfaces as a load error in `/plugin` → Errors, not as a CLI failure.
- **Verified**: 2026-09-08 · `docs/plans/2026-09-08-upstream-fable-merge/`
- **Check it**: `strings "$(readlink -f "$(command -v claude)")" | grep -oE "has invalid [a-zA-Z-]+" | sort -u`

## The `/agents` wizard has been removed from the harness

- **Why it matters**: it is the obvious way to inspect subagent configuration and it no longer
  exists, so a session that reaches for it loses time. Agent definitions are files —
  `plugin/agents/*.md` — and are read directly.
- **Verified**: 2026-09-08 · `docs/plans/2026-09-08-upstream-fable-merge/`
- **Check it**: `/agents` in a session prints "The /agents wizard has been removed."

## `./plugin/scripts/lint --all` does not consult `.gitignore`

- **Why it matters**: it walks the tree with a hardcoded exclusion list
  (`node_modules`, `.git`, `.context`, `vendor`, `tmp`, `.next`, `dist`, `build`). Any *other*
  gitignored directory holding markdown — a vendored export, a scratch area — gets linted and
  fails the gate for findings that are not ours. The fix is to add the path to that list, not
  to reinterpret the gate.
- **Verified**: 2026-09-08 · `docs/plans/2026-09-08-upstream-fable-merge/`
- **Check it**: `sed -n '/LINT_ALL.*true/,/^else/p' plugin/scripts/lint` shows the `find`
  exclusion list.

## Plugin-directory reads are gated by the working-directory boundary

- **Why it matters**: every wb stage reads supporting files from the plugin directory, which is
  outside the project in every real configuration — under `--plugin-dir` *and* under a
  marketplace install reading its own root. The read is gated, so the first stage a session runs
  asks permission (once; the grant is persistent). `allowed-tools` does **not** exempt it: it is
  a pre-approval for the tools it names, not a path grant, and path-scoped
  `Read(<plugin-root>/**)` was probed and does not cross the boundary either. **A plugin cannot
  self-grant.** The only proven fix is `--add-dir <plugin-path>`. This is what falsified
  assumption A4, which had been recorded Validated on a probe whose session cwd was never
  written down — run from inside the plugin directory, the boundary cannot fire.
- **Verified**: 2026-09-09 · `docs/plans/2026-09-08-upstream-fable-merge/`
- **Check it**: from a cwd that is not a parent of the plugin —
  `claude --plugin-dir <repo>/plugin -p "Use the Read tool to read <repo>/plugin/skills/help/SKILL.md. Reply DENIED or the first line."`
  → `DENIED`; adding `--add-dir <repo>/plugin` → the first line.

## State the cwd of any permission or path measurement

- **Why it matters**: a measurement of permission behaviour is only meaningful with the working
  directory it was taken in, because the working-directory boundary is defined relative to it.
  The Phase 0 layout probe recorded `NO PROMPT` truthfully and concluded wrongly, purely because
  the environment field was missing — a real defect measured clean for a day. Generalise it: a
  probe that cannot fail is not evidence, and the way this one could not fail was invisible
  until someone asked where it ran.
- **Verified**: 2026-09-09 · `docs/plans/2026-09-08-upstream-fable-merge/`
- **Check it**: `grep -A12 'A4 re-probed' docs/plans/2026-09-08-upstream-fable-merge/thoughts/2026-09-08-baseline-measurements.md`
  — the probe table carries a `cwd` column.

## Auto mode bypasses the plugin's read conventions

- **Why it matters**: in auto mode the harness instructs the model to prefer `cat`/`head`/`sed`
  over the Read tool, and sandboxed Bash is not subject to the working-directory boundary. So in
  auto mode `--add-dir` is unnecessary, a blocked read is not actually blocked, and the
  hard-stop rule in every skill manifest cannot fire — the failure it guards against never
  arrives. Every permission dialog advertises "Tip: auto mode handles these prompts for you" at
  the top, so this is the path of least resistance, not an unusual setting. Any test of read
  behaviour must confirm auto mode is **off** first, or it measures nothing.
- **Verified**: 2026-09-09 · `docs/plans/2026-09-08-upstream-fable-merge/`
- **Check it**: ask a session mid-run which tool it used to read a skill's supporting file —
  `cat` means auto mode, `Read` means not.

## Pre-2.0.0 `wb-*` skills in `~/.claude/skills/` shadow the plugin

- **Why it matters**: an older install copied each stage in as a user-level skill
  (`wb-implement_tasks`, `wb-create_execution`, …). They win over the plugin's `wb:` skills, so a
  session silently gets the beads-era body — `bd doctor` gates that halt on
  `task_tracking: markdown-checkboxes` plans, and "NEVER treat markdown as source of truth" — and
  the deprecated-alias stubs never announce. Resolution between `wb:X` and `wb-X` is not
  deterministic: one alias reached the plugin stub and two reached the stale copies in the same
  session.
- **Verified**: 2026-09-09 · `docs/plans/2026-09-08-upstream-fable-merge/` (13 stale directories
  found on this machine, ~400 beads references; removed)
- **Check it**: `ls -d ~/.claude/skills/wb-* 2>/dev/null` → no output.

## The Task tool's `model` is an enum — full model IDs cannot be pinned per spawn

- **Why it matters**: `implement`'s worker-tier ladder (PD2) names `claude-opus-4-8[1m]` as the
  default rung and `claude-opus-5` as the first upshift, but the Task/Agent tool's `model`
  parameter accepts only `sonnet | opus | haiku | fable`. Both Opus rungs collapse to `opus`, so
  the ladder's middle step is unspecifiable and 6c's "Opus 4.8 1M → Opus 5" escalation is a
  no-op. `haiku` and `fable` are selectable, so the bottom and top rungs work. An agent
  *definition*'s frontmatter does accept a full ID, so a fixed tier can be pinned there — just
  not varied per spawn, which is what D13 requires.
- **Verified**: 2026-09-09 · `docs/plans/2026-09-08-upstream-fable-merge/` — surfaced by a live
  `/wb:implement` run, which stated the limitation at the point of spawn
- **Check it**: the Agent tool's schema — `model` carries
  `"enum": ["sonnet","opus","haiku","fable"]`.
