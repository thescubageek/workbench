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
- **Also (2026-09-20) — the flag works from any cwd, and the way it fails when omitted looks
  like a plugin defect.** A probe launched from `/tmp` reported `wb:adversarial-loop` as
  `Unknown skill` and concluded `--plugin-dir` "contributed nothing" and that the `wb:`
  namespace was being served by the stale installed 2.1.0. Measured: with the flag, from `/tmp`,
  headless, the skill loads from the checkout — and adding `--add-dir` alongside changes
  nothing. **Without** the flag the error is verbatim
  `Unknown skill: wb:adversarial-loop (the listed skill is 'adversarial-loop', without the 'wb:'
  prefix)`, and the session sees the installed copy's skill list. So that error means the flag
  was **absent**, not ineffective. Check the flag took effect before drawing any conclusion from
  a session's behaviour.
- **Verified**: 2026-09-08, extended 2026-09-20 · `docs/plans/2026-09-08-upstream-fable-merge/`,
  `docs/plans/2026-09-17-adversarial_loop/`
- **Check it**: `claude --plugin-dir . plugin details wb` reports `Source: wb@<marketplace>` and
  the installed version; `--plugin-dir plugin` reports `Source: wb@inline` and the working-tree
  version. That one line is the whole test — version and `Source:` together — and it is worth
  running as the first act of any session that is about to measure plugin behaviour.

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
- **Also**: the gate is the `permissions.blockReadsOutsideWorkingDirectories` setting, and it is
  **off** in this machine's `~/.claude/settings.json`. A read-boundary test must force it on —
  `--settings '{"permissions":{"blockReadsOutsideWorkingDirectories":true}}'` — or it measures
  nothing: run verbatim on 2026-09-15, nothing was refused and the stage completed.
- **Also, and this narrows the whole entry (2026-09-15)**: the gate follows the *plugin root*.
  A **marketplace-installed** stage read four supporting files out of
  `~/.claude/plugins/cache/thescubageek-workbench/wb/2.0.0/` in a headless `default`-mode
  session with the boundary forced on, while Bash in the same session was gated — so a running
  skill may read its own installed root. A *bare* Read of the same cache from a session with no
  stage running is still refused by the grant flow (re-probed 2026-09-15, with and without the
  boundary setting, no persisted grant). Only a `--plugin-dir` **checkout** run from another
  cwd is gated for a running stage. The release blocker this entry was written for does not
  exist for installed copies.
- **Also — the rule was finally exercised, 2026-09-20, and it holds.** In the one configuration
  where the gate can fire for a running stage (a `--plugin-dir` checkout, boundary forced on, cwd
  a git repo that is *not* a parent of the plugin), `adversarial-review`'s Step 3 read of
  `lenses.md` was refused, and the session **stopped at the first directed read**: it used `Read`,
  did not route around with `cat`, named the file, and gave the `--add-dir` remedy. Note what this
  cost to discover — two interactive smoke runs measured nothing here, because in both the plugin
  sat *inside* the working directory, so the boundary could not fire in either permission mode.
  **It is a one-command headless probe, not an interactive session**: build a scratch repo in
  `/tmp` with an `origin/main` and a one-line diff, then
  `claude -p --plugin-dir <repo>/plugin --settings '{"permissions":{"blockReadsOutsideWorkingDirectories":true}}' --allowedTools=Skill,Read,Bash "<instruction>"`.
- **Verified**: 2026-09-09, narrowed 2026-09-15, rule exercised 2026-09-20 ·
  `docs/plans/2026-09-08-upstream-fable-merge/`,
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
- **Also, and this is what makes recording it harder than it sounds (2026-09-20)**: the cwd is
  not a durable fact for the length of a session, and it has two spellings. A Bash call prefixed
  with `cd` **moves the session's primary working directory** — the harness announces it with an
  `Environment update` block and it persists into later calls. And a Conductor workspace path can
  be a symlink: `pwd` reported `.../workbench/adversarial-loop-skill-research` where `pwd -P`
  resolved to `.../workbench/ankara`, the same tree under two names that no automated comparison
  will ever call equal. Record **both** spellings, and re-record the cwd at the point of each
  measurement rather than once at the top.
- **Verified**: 2026-09-09, extended 2026-09-20 · `docs/plans/2026-09-08-upstream-fable-merge/`,
  `docs/plans/2026-09-17-adversarial_loop/thoughts/2026-09-19-smoke-session.md`
- **Check it**: `grep -A12 'A4 re-probed' docs/plans/2026-09-08-upstream-fable-merge/thoughts/2026-09-08-baseline-measurements.md`
  — the probe table carries a `cwd` column. For the symlink half: `pwd; pwd -P` in a Conductor
  workspace, and `git worktree list` to confirm it is one tree rather than two.

## Auto mode bypasses the plugin's read conventions

- **Why it matters**: in auto mode the harness instructs the model to prefer `cat`/`head`/`sed`
  over the Read tool, and sandboxed Bash is not subject to the working-directory boundary. So in
  auto mode `--add-dir` is unnecessary, a blocked read is not actually blocked, and the
  hard-stop rule in every skill manifest cannot fire — the failure it guards against never
  arrives. Every permission dialog advertises "Tip: auto mode handles these prompts for you" at
  the top, so this is the path of least resistance, not an unusual setting. Any test of read
  behaviour must confirm auto mode is **off** first, or it measures nothing.
- **Also (2026-09-20)**: **a new session can start with auto mode already on.** Two consecutive
  P5-T4 runs were launched believing it was off and both arrived carrying the
  `While auto mode is active` instruction; only an explicit toggle mid-session cleared it. So
  "I started a fresh session" is not evidence the mode is off. Have the session state, as its
  own first act, whether that instruction is present, and stop if it is — a run that proceeds
  under it cannot measure read behaviour in either direction.
- **Verified**: 2026-09-09, extended 2026-09-20 · `docs/plans/2026-09-08-upstream-fable-merge/`,
  `docs/plans/2026-09-17-adversarial_loop/`
- **Check it**: ask a session mid-run which tool it used to read a skill's supporting file —
  `cat` means auto mode, `Read` means not. Or have it report whether a
  `While auto mode is active` block is present in its context before it runs anything.

## Pre-2.0.0 `wb-*` skills in `~/.claude/skills/` shadow the plugin

- **Why it matters**: an older install copied each stage in as a user-level skill
  (`wb-implement_tasks`, `wb-create_execution`, …). They win over the plugin's `wb:` skills, so a
  session silently gets the beads-era body — `bd doctor` gates that halt on
  `task_tracking: markdown-checkboxes` plans, and "NEVER treat markdown as source of truth" — and
  the deprecated-alias stubs never announce. Resolution between `wb:X` and `wb-X` is not
  deterministic: one alias reached the plugin stub and two reached the stale copies in the same
  session.
- **Also (2026-09-20) — a same-named personal skill wins the BARE name deterministically, even
  with the plugin loaded.** With `--plugin-dir` in effect and the 3.0.0 plugin enumerating,
  `Skill('adversarial-loop')` resolved to `~/.claude/skills/adversarial-loop/SKILL.md` — the
  236-line personal copy — while `Skill('wb:adversarial-loop')` resolved to the 379-line shipped
  one. Not ambiguous, not a race: the prefix decides. This is the concrete form of design A3, and
  the reason P5-T5 deletes the three personal copies: a user who types the skill's own name gets
  the wrong artifact.
- **Verified**: 2026-09-09, extended 2026-09-20 · `docs/plans/2026-09-08-upstream-fable-merge/`
  (13 stale directories found on this machine, ~400 beads references; removed),
  `docs/plans/2026-09-17-adversarial_loop/`
- **Check it**: `ls -d ~/.claude/skills/wb-* 2>/dev/null` → no output. For the same-name case:
  `ls -d ~/.claude/skills/adversarial-* ~/.claude/skills/reply-to-claude 2>/dev/null` → no output
  once P5-T5 has run.

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
- **Resolved 2026-09-10**: `implement`'s Step 5 ladder is now stated in those four values —
  `haiku → sonnet → opus → fable`, with `opus` the default and `sonnet` the deliberate
  downshift. Full IDs remain correct for the *main-session* model via `/model`, which is what
  `model-help` governs; the two vocabularies are now distinguished in both files.

## Tracked files under `docs/plans/` still need `git add -f`, every time

- **Why it matters**: promotion is not one-time in practice. `docs/plans` is gitignored, and
  `git add <plan-dir>/tasks.md` on an **already-tracked** file still exits 1 with "The
  following paths are ignored", so a session that stages its status edits the ordinary way
  gets a failed `&&` chain and no commit — `git status` shows the modification, which makes the
  refusal look like something else. Stage plan files with `git add -f` unconditionally.
- **Verified**: 2026-09-15 · `docs/plans/2026-09-08-upstream-fable-merge/`
- **Check it**: on a clean tree, `git add docs/plans/<dir>/tasks.md` prints the ignored-paths
  hint and exits 1; `git add -f` on the same path exits 0.

## Headless sessions cannot invoke a wb stage mid-conversation without `--allowedTools=Skill`

- **Why it matters**: under `-p`, a `Skill` tool call for `wb:<stage>` is denied in
  `acceptEdits` mode; only a slash command that *leads* the prompt is expanded before the session
  starts. A headless session that cannot load a stage does not stop — one improvised the whole
  pipeline from the SessionStart orientation and wrote `status: approved` into `design.md` with
  no human asked, which is the failure the approval rule exists to prevent, reached by never
  loading the rule. Pass `--allowedTools=Skill`, or lead the prompt with the one stage to run.
  The orientation block now says to stop rather than reconstruct a stage, as a second defence.
- **Also**: this lands on *scheduled* steps too — `implement` Step 9's `/wb:update_status` and
  `create_tasks`'s `model-help` gate were denied on every headless `--auto` run, so counters
  stay stale until an interactive session reconciles them. Launch headless runs with
  `--allowedTools=Skill`. And `--disallowedTools` is variadic: write `--disallowedTools=Skill`,
  or it swallows the prompt.
- **Verified**: 2026-09-15 · `docs/plans/2026-09-08-upstream-fable-merge/`
- **Check it**: `claude -p --plugin-dir plugin --permission-mode acceptEdits "Use the Skill tool to invoke wb:help"`
  → the Skill call is denied; add `--allowedTools=Skill` → `/wb:help` runs.

## A local marketplace needs a relative `./` source, and does not exercise the cache path

- **Why it matters**: `claude plugin marketplace add <dir>` rejects a `marketplace.json` whose
  plugin `source` is an absolute path (`must start with "./"`), so a local test marketplace must
  carry a copy of `plugin/` beside it. And for a Directory-source marketplace the installed
  plugin's root resolves to the **marketplace source directory**, not
  `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` — the cache is populated but never
  read. So a local install proves the read boundary fires on an out-of-tree path, but the
  literal cache path that a real (GitHub-source) install reads can only be tested from a pushed
  branch.
- **Verified**: 2026-09-15 · `docs/plans/2026-09-08-upstream-fable-merge/`
- **Check it**: install from a local marketplace, run a stage with the read boundary forced on,
  and read the refused path in its output — it names the marketplace source directory.

## A plugin skill can invoke a built-in Claude Code skill, and it runs forked

- **Why it matters**: `Skill(code-review, "low")` from inside a wb skill returns
  `Skill "code-review" completed (forked execution)` with findings. Forked means it does **not**
  consume the calling session's context, which is what makes wrapping a built-in affordable
  rather than ruinous. Before this was measured, no shipped skill had ever invoked a built-in and
  the whole `adversarial-review` design rested on the assumption that it was possible.
- **Also**: declaring `Skill` in a skill's `allowed-tools` does not break loading — the plugin
  enumerates normally. Whether it actually *pre-approves* the call is still unproven; loading
  cleanly only establishes that the value is at worst inert.
- **Verified**: 2026-09-18 · `docs/plans/2026-09-17-adversarial_loop/`
- **Check it**: invoke `Skill(code-review, "low")` from a session with a diff; the result line
  says `(forked execution)`.

## The PostToolUse lint hook rewrites markdown *after* you check it

- **Why it matters**: the hook runs `lint --fix` on every markdown Write/Edit, so the sequence
  write → check → commit can capture the **pre-fix** state while the fix lands in the working tree
  afterwards. That happened once: `lint --all` reported FAIL, the commit went in, and the hook's
  correction was left uncommitted. Verify the **committed** content, not the working tree.
- **Also (2026-09-20)**: the hook runs `lint --fix`, and **MD024 and MD025 are not auto-fixable**
  — duplicate sibling headings and a second top-level heading survive it. So a document generated
  in bulk can pass the hook, look clean, and fail `lint --all` later, which fails the `markdown
  lint` gate inside `./plugin/scripts/check` with nothing in the generating session having warned.
  MD025 also counts a frontmatter `title:` key as the document's title, so a file carrying both
  `title:` and an `# H1` trips it; the convention in this repository is the H1 and no `title:`.
- **Verified**: 2026-09-18, extended 2026-09-20 · `docs/plans/2026-09-17-adversarial_loop/`
- **Check it**: `git show HEAD:<path> > /tmp/x && ./plugin/scripts/lint /tmp/x` — if that fails
  while the working copy passes, the hook fixed it after the commit. For the un-fixable half:
  write a file with two `# H1`s, watch the hook leave it, then run `./plugin/scripts/lint --all`.

## `strings` emits non-ASCII as literal escape sequences

- **Why it matters**: an em-dash in the Claude binary arrives from `strings` as the seven
  characters `—`, not as `—`. A grep written with the real character — or with `.` standing
  in for one — matches nothing and the check silently passes. This produced an unfirable
  verification command that read as clean.
- **Verified**: 2026-09-18 · `docs/plans/2026-09-17-adversarial_loop/`
- **Check it**: `strings "$(readlink -f "$(command -v claude)")" | grep -c 'Dedup only'` returns
  a non-zero count while a pattern written with a literal em-dash returns none.

## markdownlint reads a fence indented under a list item as an indented code block

- **Why it matters**: a ```` ``` ```` block indented to sit inside a `- [ ]` item fails MD046
  (`Expected: fenced; Actual: indented`) and `lint --all` fails. Multi-line commands in a plan's
  success criteria hit this. Dedent the fence to column zero; the list resumes after it and every
  checkbox counter anchors on `^- \[`, so counting is unaffected.
- **Verified**: 2026-09-18 · `docs/plans/2026-09-17-adversarial_loop/`
- **Check it**: indent a fenced block six spaces under a list item and run
  `./plugin/scripts/lint <file>` — it reports MD046.

## A fenced `bash` block in a shipped skill is executed by **zsh**, not bash

- **Why it matters**: this repository's doctrine is that a fenced `bash` block in a skill is
  *run*, not illustrated — `plugin/scripts/check-guards` exists for that reason. But the Bash
  tool's shell is `/bin/zsh` (5.9 here), and two bash behaviours those blocks were written
  against are absent. Both shipped, both failed silently, both in `adversarial-review`:
  - **`PIPESTATUS` is a bash array.** In zsh it expands to nothing, so `search=${PIPESTATUS[0]}`
    left `search` empty, `[ "" -le 1 ]` was true, and a `grep` that exited 2 passed its guard
    without a word. The guard's own prose said it existed to catch exactly that. zsh's array is
    `$pipestatus` and is 1-indexed; there is no portable spelling, so take the status from `$?`
    on the line after the command instead of from a pipeline.
  - **zsh does not word-split unquoted expansions.** `range="origin/main...HEAD -- some/path";
    git diff --stat $range` reaches git as one argument and dies with `fatal: ambiguous
    argument`. Keep a pathspec in its own variable and quote both.
  - **The one place that non-splitting helps**: an optional argument spells as
    `cmd ${var:+"$var"}` — unset contributes *no* word at all (zsh drops an unquoted null
    word), set contributes exactly one, and a value containing a space stays one word.
    Identical in bash, so a block using it is safe under either. `adversarial-loop`'s
    `gh pr view ${target:+"$target"} --json number` is the shipped use.
- **Why it went four review rounds undetected**: only the *path*-target form put a space in the
  variable, and no round had ever run that form. A block is not exercised by being read.
- **Verified**: 2026-09-20 · `docs/plans/2026-09-17-adversarial_loop/` — P5-T4 run 2,
  `thoughts/2026-09-20-smoke-session-run2.md`; the `${var:+"$var"}` half added in round-5
  remediation, executed in both shells
- **Check it**: `echo "$0 ${ZSH_VERSION:-no-zsh} ${BASH_VERSION:-no-bash}"` through the Bash
  tool reports `/bin/zsh 5.9 no-bash`; and
  `x=$(grep -rnF -- q /no/such/path 2>/dev/null); echo "dollar-question=$? pipestatus=${PIPESTATUS[0]:-<empty>}"`
  prints a real status beside an empty `PIPESTATUS`.
