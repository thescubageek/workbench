# Changelog

All notable changes to the `wb` plugin are recorded here.

Versioning follows semver as it applies to a prompt library: **patch** for prompt bugfixes,
**minor** for additive skills/agents/hooks, **major** for removed or renamed stages.

## [2.0.1] — 2026-09-16

Two prompt bugfixes in the shipped skill bodies, found by running `/wb:validate_execution`
against the 2.0.0 plan. No behaviour was added or removed; both defects made an instruction
unreadable rather than wrong.

### Fixed

- **Argument-binding pseudo-code arrived at the model already substituted, in 8 stages.**
  `create_design`, `create_handoff`, `create_project`, `create_tasks`, `implement_inline`,
  `resume_handoff`, `validate_execution` and `validate_project` each opened their first step
  with a fenced `javascript` block reading `const projectDir = $1 || /* prompt for it */;`.
  The harness substitutes `$1` before the model sees the text, so the block arrived with the
  path spliced into it — invalid, and **legible only when the binding already worked**, which
  is precisely when the instruction is not needed. All eight now describe the slots in prose,
  matching the shape `implement` Step 1 already carried. `create_project` additionally states
  its refuse-prose rule in the body, having previously carried it only inside the deleted block.
- **All three deprecated-alias stubs named supporting files that no longer exist.** The 2.0.0
  per-section split renamed `templates.md` to `templates/` and `sub-agent-prompts.md` to
  `prompts/` in the canonical skills; the stub manifests were not updated, leaving four wrong
  paths. The stubs still dispatched correctly — their executable instruction is a read of the
  canonical `SKILL.md` — but a session trusting the stub's file list got a failed read. No
  markdown link checker could see this, because a stub's file list is prose rather than links.

### Changed

- `docs/claude-code-skills-guide.md` gains both conventions under House conventions, each with
  a runnable check: a grep that must return nothing for the pseudo-code rule, and a resolver
  loop that must print no `MISS` for stub manifests. Both were verified against a planted
  failure, so they are known to fire rather than merely known to pass. Each defect above
  existed because a convention was stated in one place and checked in none.

### Migration

None. Update the plugin and restart:

```bash
claude plugin update wb@thescubageek-workbench
```

This is a patch release specifically so the version-keyed plugin cache picks the fixes up —
the changes edit files that already existed at 2.0.0, and a same-version cache is not
guaranteed to refresh.

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
- **Each skill's `allowed-tools` now names the tools it actually uses**, where before every
  workflow skill declared `Read` alone. This is **documentation, not a behaviour change** —
  measured both ways: a skill declaring only `Read` still performed a `Write`, and a skill
  declaring `Write` still hit the permission dialog before writing. In this harness version
  `allowed-tools` has no observable effect on the permission path, so writes, edits and commands
  prompt exactly as they did before. The field is now accurate about each stage's real surface,
  which is worth having on its own; do not read it as a grant.

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
  demand. Invocation-time context across the fourteen stages fell **from ~84.9k to ~51.1k
  tokens (−40%)**; nothing was deleted, the material is deferred. The figure was ~46.8k before
  the per-section split and the hard-stop rule, which cost ~9% back in longer manifests — paid
  deliberately, because the mechanism they replace did not work. Per-*run* cost moves the other
  way: a stage now loads only the template it needs rather than a file holding six others.
- **Supporting files are one file per readable unit.** `templates.md` and
  `sub-agent-prompts.md` became `templates/` and `prompts/` directories, one file per output
  shape or agent prompt — 14 multi-section files became 48. The reason is mechanical: the Read
  tool has no section parameter, only line offsets, so an instruction to "read the
  `## Plan presentation message` section" had no correct implementation. Observed in testing, a
  model asked for a section starting at line 291 read lines 180–239 instead. A whole-file read
  of a per-section file **is** the scoped read, so the instruction now matches the tool, and a
  wrong path fails loudly instead of returning the wrong lines.
- **A supporting-file read that is refused is a hard stop.** Every skill's manifest says so:
  name the file, name the cause, name the fix — never write the artifact from the manifest
  alone. Without this, a locked-down session produced a plausible document that was never based
  on the template, with no error shown.
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

2. **Stages now read their templates and prompts from the plugin directory**, which sits
   outside your project. For a marketplace install this needs no grant: a running stage may read
   its own root under `~/.claude/plugins/cache/`, interactively and headless alike (measured
   2026-09-15 with the read boundary forced on). A development checkout run through
   `--plugin-dir` from another directory is gated — one prompt interactively, a denial headless.

   The gate is the ordinary permission-grant flow for a path outside your project. It is *not*
   the `permissions.blockReadsOutsideWorkingDirectories` setting, which governs a different
   boundary and does not fire on the plugin cache. The two produce different denial messages,
   and telling them apart is what settled this.

   1.12.x never asked, because its stages were monolithic files with everything inline. The
   dependency is new in 2.0.0, and it is not avoidable from inside the plugin: `allowed-tools`
   is a pre-approval for the tools it names, not a path grant, and path-scoped
   `Read(<plugin-root>/**)` was measured and does not grant it either.

   **Running a development checkout headless, in CI, or under `claude -p`? Pre-grant it —
   nothing can answer a prompt there.** Under `default` and `acceptEdits` alike the read is
   denied and the stage stops:

   ```json
   { "permissions": { "allow": ["Read(//Users/<you>/.claude/plugins/cache/**)"] } }
   ```

   If you **block** it instead, stages will say so and stop rather than improvise a document
   from a template they could not read. That is deliberate.

3. **Delete any pre-2.0.0 `wb-*` skills from `~/.claude/skills/`.**

   ```bash
   ls -d ~/.claude/skills/wb-* 2>/dev/null   # look before you leap
   rm -rf ~/.claude/skills/wb-*
   ```

   Older installs copied each stage in as a user-level skill (`wb-implement_tasks`,
   `wb-create_execution`, …). Those copies **shadow the plugin**, so you get the old beads-era
   body instead of the 2.0.0 one — including `bd doctor` gates that halt on any plan carrying
   `task_tracking: markdown-checkboxes`, and the instruction "NEVER treat markdown as source of
   truth", which this release inverts. They also pre-empt the deprecated-alias stubs, so the
   rename notice never fires. Found on a real machine during release testing: 13 stale
   directories, ~400 beads references between them.

4. **Point local development at `plugin/`, and add it as a directory.**

   ```bash
   claude --plugin-dir /path/to/workbench/plugin --add-dir /path/to/workbench/plugin
   ```

   The root no longer holds the manifest. Pointing there does not error; it silently serves the
   installed copy. `--add-dir` puts the plugin in scope so the stages can read their own
   supporting files without the prompt above — the local-development counterpart to the
   `permissions.allow` rule in step 2.

5. **Expect old plan directories to lose their tracker references.** Any `docs/plans/*/tasks.md`
   written before 2.0.0 has `beads_epic`, `beads_phases` and `beads_tasks` in its frontmatter.
   Those IDs no longer resolve, and nothing reads them.

   **Checkbox state in those files is now authoritative.** For each plan still in flight:

   ```bash
   /wb:update_status docs/plans/<the-plan>/
   ```

   It counts the checkboxes and reconciles the counters to them. If a plan's checkboxes were
   never maintained — likely, since the old guidance said not to — reconcile them by hand
   against the code first, then run it.

6. **Old plans may carry stale guidance.** A pre-2.0.0 `tasks.md` can contain a note saying its
   checkboxes are "documentation only". Delete it; that note is now wrong.
   `/wb:validate_project` reports these.

7. **Nothing to uninstall.** Removing `bd` is optional and unrelated — this plugin simply no
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
