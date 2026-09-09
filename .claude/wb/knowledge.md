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
