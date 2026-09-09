# Changelog

All notable changes to the `wb` plugin are recorded here.

Versioning follows semver as it applies to a prompt library: **patch** for prompt bugfixes,
**minor** for additive skills/agents/hooks, **major** for removed or renamed stages.

## [2.0.0] — 2026-09-08

The tracker-free modernization. Status moves into the plan documents, the shipped runtime moves
under `plugin/`, and every workflow stage becomes a skill with progressive disclosure.

### ⚠️ Breaking

- **Beads is removed entirely.** No `bd` invocations, no `BEADS_MODE` / `BEADS_AVAILABLE`, no
  `/beads:*` reference, no "Beads Required" principle, no fast-fail gates. Six stages previously
  reached a stop-and-prompt gate on a dependency that had to be installed; none do now.
- **Three stages renamed**, each keeping a deprecated alias that announces the rename once and
  then runs the canonical skill. **All three aliases are removed at 3.0.0.**

  | Old | New | Why |
  | --- | --- | --- |
  | `/wb:create_execution` | `/wb:create_tasks` | a `create_*` stage is named for the artifact it writes, and this one writes `tasks.md` |
  | `/wb:implement_coordinated` | `/wb:implement` | the coordinated path is the *recommended* one, so it carries the plain verb |
  | `/wb:implement_tasks` | `/wb:implement_inline` | names what is actually different about it — it runs inline, on the session model |

- **The shipped tree moved under `plugin/`.** `--plugin-dir` must now point at the
  subdirectory. Pointing it at the repository root **does not error** — it silently serves the
  installed marketplace copy, so working-tree changes become invisible.
- **`AGENTS.md` deleted.** Its session protocol is folded into `CLAUDE.md`. It was a
  conventionally auto-loaded filename carrying stale, beads-only instructions, so it could enter
  a session's context with nothing pointing at it.
- **Three documents deleted**: `docs/beads-fast-fail.md`, `docs/beads-stealth-mode.md`,
  `docs/beads-integration-learnings.md`. They did not merely *describe* a removed subsystem,
  they instructed — and a stale instruction reads as authority.
- **`hooks/setup-beads-mode.sh` deleted**, replaced in the same SessionStart slot by
  `hooks/wb-prime.sh`.

### Added

- **`/wb:explore_design`** — an optional stage between research and design: frame the decision,
  diverge, discuss the trade-offs, converge only on explicit approval, and record the outcome at
  the top of a `thoughts/` document. `create_design` formalizes that record rather than
  regenerating options. Suggested by research *only* when the findings named more than one
  viable approach.
- **`doc-adherence`** — a background skill whose rule is that a claim about what a plan document
  says requires a read of that document in the current context window.
- **`hooks/wb-prime.sh`** — session orientation on a fresh start, compaction-recovery text on a
  compact trigger, and a bootstrap giving plan position, the journal's last entry and whether it
  is open, and a reconciliation against the working tree. Registered on SessionStart and
  PreCompact. It reads only; it never writes.
- **`agents/task-worker`** — the worker contract as a real agent definition, with its tools, a
  preloaded `tdd-discipline` skill, and a turn cap.
- **`journal.md`** per plan directory — entries **open when work starts**, not when it ends, so
  the residue of an abrupt kill is a correct open entry rather than silence.
- **`.claude/wb/knowledge.md`** — committed, curated repository facts, one per entry, each with a
  date and a way to check whether it is still true.
- **Two implementation guardrails**: edit in place rather than rewriting, and report follow-ups
  rather than fixing them — closed with a completeness clause, because a prohibition list
  without one invites under-delivery.

### Changed

- **Every workflow stage is now `plugin/skills/<name>/SKILL.md`** plus supporting files read on
  demand. Invocation-time context across the fourteen stages fell **from ~84.9k to ~45.3k
  tokens (−47%)** with no content removed — the material is deferred, not deleted.
- **Status lives in the plan.** Checkbox state in `tasks.md` is the source of truth, the
  frontmatter counters are a derived cache with exactly one writer (`/wb:update_status`), and
  git is the durable record: one task, one commit.
- **Task IDs are a contract**: bold, matching `[A-Z0-9-]*[0-9][A-Z0-9-]*`, at least one digit.
  Every counter identifies task lines by that shape.
- **Worker failure handling discriminates truncation from genuine failure** and applies opposite
  remedies. A task is never retried whole with the same context — same task plus same context
  spends the same budget and truncates at the same point. One escalation, then the checkpoint's
  blocking list.
- **The worker tier rule is stated once**, at the point of spawn. The `determineModel()` keyword
  regex is retired; its fallthrough was the most expensive tier, so any task whose title missed a
  hand-written pattern was charged at the ceiling.
- **Fable is an upshift, never a default** — reached by explicit election, always at
  `effort: high`.
- **Sub-agents carry `model:` / `effort:` / `maxTurns:` frontmatter.** The search agents had no
  turn bound at all before.
- Tasks are sized by **projected tool calls**, not hours, and split past ~50 at a natural seam.
- `CLAUDE.md`'s command-authoring rules: each synchronization point marked once **with its
  reason**, and decision points naming the decision rather than instructing thinking depth.

### Fixed

- **`./scripts/lint --fix` exited 0 with findings remaining** — the `exit 1` sat inside the
  non-`--fix` branch. A gate that reports success on failure is worse than no gate, and the
  release process cites this one.
- `lint --all` walked gitignored vendored directories, failing on findings that were not ours.

### Migration

**Written per machine.** `wb` is installed on more than one, and each needs these steps
independently — there is no shared state that carries them.

On **each machine** where `wb` is installed:

1. **Update and restart.**

   ```bash
   claude plugin update wb@thescubageek-workbench
   ```

   Then restart Claude, or `/reload-plugins`. A running session holds the old skill bodies.

2. **Point local development at `plugin/`.**

   ```bash
   claude --plugin-dir /path/to/workbench/plugin    # NOT the repository root
   ```

   The root no longer holds the manifest. Pointing there does not error; it silently serves the
   installed copy.

3. **Expect old plan directories to lose their tracker references.** Any `docs/plans/*/tasks.md`
   written before 2.0.0 has `beads_epic`, `beads_phases` and `beads_tasks` in its frontmatter.
   Those IDs no longer resolve, and nothing reads them.

   **Checkbox state in those files is now authoritative.** For each plan still in flight:

   ```bash
   /wb:update_status docs/plans/<the-plan>/
   ```

   It counts the checkboxes and reconciles the counters to them. If a plan's checkboxes were
   never maintained — likely, since the old guidance said not to — reconcile them by hand
   against the code first, then run it.

4. **Old plans may carry stale guidance.** A pre-2.0.0 `tasks.md` can contain a note saying its
   checkboxes are "documentation only". Delete it; that note is now wrong.
   `/wb:validate_project` reports these.

5. **Nothing to uninstall.** Removing `bd` is optional and unrelated — this plugin simply no
   longer calls it.

**Not new, restored.** `help.md` previously pointed users at the `v1.0.0` tag for a
"markdown-only workflow". This release makes that the only mode.

**On the history being dropped**: the SQLite-to-Dolt migration pain and the five-week-stale
export that `docs/beads-integration-learnings.md` recorded are preserved in git, and its one
durable lesson is now load-bearing design rationale rather than a line in a document nobody
linked to — a merged journal-and-rules file decays into stale authority, which is why the
journal and the knowledge file are deliberately separate artifacts.

## [1.x]

Earlier releases are recorded in the git log. `v1.12.5` is the final pre-modernization cut:
`commands/` layout, root-level `.claude-plugin/`, beads-backed tracking.
