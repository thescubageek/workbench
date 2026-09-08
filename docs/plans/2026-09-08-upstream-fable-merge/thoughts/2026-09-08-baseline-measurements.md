---
project: upstream-fable-merge
created: 2026-09-08
last_updated: 2026-09-08
author: wolfpacksteve@gmail.com
git_commit: b9025662a57fd8ef3000454c7f4e2cabae4db427
git_branch: thescubageek/gabe-fable-merge-research
written_by: P0-T2
purpose: Before-measurements that Phase 2's exit compares against, plus the Phase 0 layout-probe verdict
---

# Baseline measurements (Phase 0)

Written by task `P0-T2`. Phase 2's exit criterion — "the on-invoke total for the fourteen
stages is at least 30% below the Phase 0 baseline" — measures against the numbers recorded
here. Nothing in this file is a target; it is a record of what was true before any file moved.

## Measurement caveat, recorded before the numbers

`claude plugin details wb` reports the **installed marketplace cache**, which is at
**1.12.4** while the repository is at **1.12.5** (`claude plugin list` → `Version: 1.12.4`).
The two differ by one patch (`b902566`, "Name the working branch after the loaded Jira
ticket"), which touched `skills/jira-context/SKILL.md` and `CLAUDE.md` — not any of the
fourteen stage files this metric covers.

**Resolved by `P0-T3`**: `claude --plugin-dir <path> plugin details <name>` works — the
global flag goes **before** the `plugin` subcommand — so the metric can be taken against the
**working tree** and the cache is not on the critical path at all. Both readings were taken
and the fourteen stages are **identical** in each; the only component that differs is
`jira-context` (~1.8k cached vs ~2.4k in-tree), which is precisely the `b902566` patch.
The cache lag therefore does not affect this metric. Phase 2 should measure with
`claude --plugin-dir . plugin details wb` (after Phase 1, `--plugin-dir plugin/`), not
against the cache.

## `claude plugin details wb` — verbatim

Captured 2026-09-08 at `b902566` (cache at 1.12.4).

```text
wb 1.12.4
  Workbench for structured software development with TDD, project planning, and beads integration.
  Source: wb@thescubageek-workbench

Component inventory
  Skills (31)  clip, create_design, create_execution, create_handoff, create_mockup, create_product_research, create_project, create_research, daily-digest, eli5-clip, fetch-issues, forge, help, implement_coordinated, implement_tasks, jira-context, mockup-iteration, model-help, project-structure, research-validation, resolve_questions, resume_handoff, review-prep, status-sync, tdd-discipline, touch-grass, tracer-bullet, update_status, validate_execution, validate_project, verification-before-completion
  Agents (6)  product-behavior-analyzer, codebase-analyzer, pattern-finder, codebase-locator, research-validator, task-verifier
  Hooks (2)  SessionStart, PostToolUse  (harness-only — no model context cost)
  MCP servers (0)
  LSP servers (0)

Projected token cost
  Always-on:   ~2,762 tok   added to every session

Per-component (rounded)
  component                       always-on  on-invoke
  eli5-clip                            ~160      ~1.4k
  jira-context                         ~150      ~1.8k
  review-prep                           ~80      ~1.2k
  tdd-discipline                        ~70      ~1.2k
  clip                                 ~130       ~560
  mockup-iteration                      ~50      ~4.7k
  daily-digest                         ~260      ~5.7k
  tracer-bullet                        ~110      ~1.5k
  model-help                           ~230      ~3.8k
  project-structure                     ~70       ~330
  status-sync                           ~30       ~490
  touch-grass                          ~200      ~3.3k
  fetch-issues                         ~140      ~7.2k
  verification-before-completion        ~70      ~1.1k
  research-validation                   ~90       ~940
  product-behavior-analyzer             ~80      ~2.1k
  codebase-analyzer                     ~60      ~1.1k
  pattern-finder                        ~60      ~1.2k
  codebase-locator                      ~70      ~1.1k
  research-validator                    ~70        ~3k
  task-verifier                         ~60        ~2k
  create_design                         ~30      ~5.8k
  create_project                        ~30        ~4k
  resolve_questions                     ~70      ~8.1k
  implement_coordinated                 ~40      ~9.8k
  help                                  ~20      ~3.2k
  create_product_research               ~40      ~6.5k
  create_execution                      ~30      ~9.4k
  implement_tasks                       ~30        ~8k
  forge                                 ~50      ~3.3k
  create_research                       ~30      ~5.3k
  validate_execution                    ~40      ~5.3k
  validate_project                      ~30      ~5.8k
  update_status                         ~30      ~5.3k
  resume_handoff                        ~30      ~4.4k
  create_mockup                         ~30        ~7k
  create_handoff                        ~30      ~5.1k

  On-invoke cost is paid each time a skill or agent fires.
  Token counts are estimates and may differ from actual usage.
```

## Projected token cost — the numbers Phase 2 is measured against

| Metric | Baseline |
| ------ | -------- |
| Always-on, added to every session | **~2,762 tok** |
| On-invoke total, the **fourteen stages** | **~84.9k tok** |
| On-invoke total, all 16 `commands/*.md` stages | **~96.3k tok** |
| Phase 2 bar: 30% below the fourteen-stage total | **≤ ~59.4k tok** |

The fourteen stages are the set research.md §7 tabulates against upstream — every
`commands/*.md` except `forge` (~3.3k) and `resolve_questions` (~8.1k), which have no
upstream counterpart and are therefore excluded from the −37% comparison.

Per-stage on-invoke, extracted from the block above:

| Stage | On-invoke | Always-on |
| ----- | --------- | --------- |
| implement_coordinated | ~9.8k | ~40 |
| create_execution | ~9.4k | ~30 |
| resolve_questions *(excluded from the 14)* | ~8.1k | ~70 |
| implement_tasks | ~8.0k | ~30 |
| create_mockup | ~7.0k | ~30 |
| create_product_research | ~6.5k | ~40 |
| create_design | ~5.8k | ~30 |
| validate_project | ~5.8k | ~30 |
| create_research | ~5.3k | ~30 |
| update_status | ~5.3k | ~30 |
| validate_execution | ~5.3k | ~40 |
| create_handoff | ~5.1k | ~30 |
| resume_handoff | ~4.4k | ~30 |
| create_project | ~4.0k | ~30 |
| forge *(excluded from the 14)* | ~3.3k | ~50 |
| help | ~3.2k | ~20 |

## Per-stage line counts — all 16 `commands/*.md`

`wc -l` at `b902566`. This is the line-count proxy the design was originally written
against; it is retained because it is the only measure that can be taken against the
**working tree** rather than the installed cache.

| Stage file | Lines |
| ---------- | ----- |
| `commands/create_design.md` | 505 |
| `commands/create_execution.md` | 787 |
| `commands/create_handoff.md` | 482 |
| `commands/create_mockup.md` | 653 |
| `commands/create_product_research.md` | 494 |
| `commands/create_project.md` | 452 |
| `commands/create_research.md` | 417 |
| `commands/forge.md` | 150 |
| `commands/help.md` | 246 |
| `commands/implement_coordinated.md` | 841 |
| `commands/implement_tasks.md` | 690 |
| `commands/resolve_questions.md` | 374 |
| `commands/resume_handoff.md` | 407 |
| `commands/update_status.md` | 497 |
| `commands/validate_execution.md` | 448 |
| `commands/validate_project.md` | 546 |
| **TOTAL (16 files)** | **7989** |

The fourteen-stage subset totals **7,465** lines (the 16-file total less `forge` at 150 and
`resolve_questions` at 374), which is the figure research.md §7 compares against upstream's
4,692 loaded lines.

## Component inventory, for the Phase 1 no-inventory-change check

| Kind | Count |
| ---- | ----- |
| Skills | 31 |
| Agents | 6 |
| Hooks | 2 (SessionStart, PostToolUse — harness-only, no model context cost) |
| MCP servers | 0 |
| LSP servers | 0 |

Phase 1's manual verification is that a `--plugin-dir <repo>/plugin` session enumerates this
same set — the relocation changes paths, not inventory.

---

## Lint gate baseline (`P0-T4`, D16)

### The fixture check, before and after the fix

Fixture: a markdown file with a duplicate sibling heading (`MD024`), which markdownlint
cannot auto-fix. A clean file is the control.

| Invocation | Before `P0-T4` | After `P0-T4` | Required |
| ---------- | -------------- | ------------- | -------- |
| `./scripts/lint <bad>` | 1 | 1 | 1 |
| `./scripts/lint --fix <bad>` | **0** | **1** | 1 |
| `./scripts/lint <good>` | 0 | 0 | 0 |
| `./scripts/lint --fix <good>` | 0 | 0 | 0 |

Two behaviours were confirmed unchanged by the fix: a finding that markdownlint **can**
auto-fix still repairs the file and exits 0 (so `--fix` did not become a blanket failure),
and `scripts/lint-hook` still exits 0 so an edit is never blocked.

### `./scripts/lint --all` baseline — read this before Phase 1

`./scripts/lint --all` exits **1** at `b902566`, with **84 findings**. The distribution is
the whole point:

| Scope | Findings |
| ----- | -------- |
| `./.context/upstream/**` — the gitignored upstream export | **84** |
| Everything we author or ship | **0** |

Our own tree is clean. Every finding belongs to the vendored upstream tree, because
`--all` builds its file list with a raw `find .` and a hardcoded exclusion list
(`scripts/lint:115-125`) that names `node_modules`, `.git`, `vendor`, `tmp`, `.next`,
`dist`, `build` — and **does not consult `.gitignore`**, so `.context/` is walked.

This is pre-existing and **not** caused by the D16 fix: plain (non-`--fix`) mode already
exited 1 before the fix, so `--all` already failed. But it means the later phases' criterion
"`./plugin/scripts/lint --all` — clean" is **unmeetable as written** while `.context/upstream/`
is present in the workspace. Recorded as a plan defect for a human at the Phase 0 checkpoint;
no task in this plan authorizes changing the `--all` file list, so nothing was changed.

The usable form of that gate today is either the per-file mode the phases already use
(`./scripts/lint <files>`) or `--all` filtered to our own tree:

```bash
./scripts/lint --all 2>&1 | grep ' error ' | grep -v '^\./\.context/'    # expect: empty
```

---

## Layout probe (`P0-T3`, verdict recorded by `P0-T5`)

### What was probed

A throwaway plugin at `/tmp/wb-probe/` mirroring D1's target layout: root
`.claude-plugin/marketplace.json` with `"source": "./plugin"`,
`plugin/.claude-plugin/plugin.json`, one skill at `plugin/skills/probe/SKILL.md` carrying
`allowed-tools: Read` and relative links to a sibling `templates.md` **and** to
`../../docs/reference/probe-ref.md`, plus a `plugin/skills/probe_old/SKILL.md` alias stub
(`disable-model-invocation: true`) that reads the canonical skill.

### Results

| Question | Result |
| -------- | ------ |
| Does a marketplace with `"source": "./plugin"` register? | **Yes** — `claude plugin marketplace add /tmp/wb-probe` succeeded and listed as `Source: Directory (/tmp/wb-probe)` |
| Do both manifests validate? | **Yes** — `claude plugin validate` passed on the marketplace manifest and on `plugin/.claude-plugin/plugin.json` |
| Does the plugin install from that `./plugin` source under a local marketplace identity? | **Yes** — `claude plugin install wbprobe@wb-probe` succeeded, scope user |
| Does the skill set enumerate from the subdirectory layout? | **Yes** — `Skills (2) probe, probe_old` from both the installed plugin (`Source: wbprobe@wb-probe`) and `--plugin-dir` (`Source: wbprobe@inline`) |
| Does `tag --dry-run` report manifest agreement across the `./plugin` boundary? | **Yes** — `Marketplace entry: plugins[0] in /tmp/wb-probe/.claude-plugin/marketplace.json (version: 0.1.0)`, exit 0 |
| Tag convention | `wbprobe--v0.1.0` — confirms `<name>--v<version>`, **not** upstream's `v<version>` |
| Does `tag --dry-run` emit a root-`CLAUDE.md` warning on the probe? | **No** — and see the two-way check below |

### Three corrections to this plan's own gate commands

Each of these is a command written into `tasks.md` that does not work as written.

1. **`claude plugin tag` takes the path to the directory holding `.claude-plugin/plugin.json`,
   not the marketplace root.** `claude plugin tag --dry-run /tmp/wb-probe` fails with
   "No plugin manifest found. Expected /tmp/wb-probe/.claude-plugin/plugin.json." So
   `P0-T3`'s and Phase 0's stated `--dry-run /tmp/wb-probe` is wrong; the working form is
   `--dry-run /tmp/wb-probe/plugin`. Phase 1's and Phase 4's `--dry-run plugin/` are already
   correct.
2. **`claude plugin tag` requires a git repository**: "… is not inside a git repository.
   Dependency tags are resolved via `git ls-remote`, so the plugin must live in a git repo."
   The probe had to be `git init`-ed and committed before the gate could run at all. It also
   **refuses on an uncommitted working tree** ("Uncommitted changes affecting this release")
   unless `--force` — so `P4-T8`'s "verify with `claude plugin tag --dry-run plugin/`" must
   run **after** the version-bump commit, not before it.
3. **`claude plugin details` takes no `--plugin-dir` option**, but the global flag before the
   subcommand works: `claude --plugin-dir <path> plugin details <name>`. `claude plugin
   details <name>` alone requires the plugin to be *installed*. This closes the
   Implementation Discovery that asked whether measuring post-change token cost requires
   installing from a local marketplace first — **it does not**.

### The root-`CLAUDE.md` warning, verified in both directions

Discovery 2 in the implementation handoff claimed the warning is present today and that its
disappearance is the verification that D1 landed. Both halves now hold mechanically:

| Layout | `tag --dry-run` output |
| ------ | ---------------------- |
| Our tree at `b902566` (`plugin.json` and `CLAUDE.md` both at the repo root) | `⚠ CLAUDE.md: CLAUDE.md at the plugin root is not loaded as project context.` |
| Probe with a `CLAUDE.md` planted **inside** `plugin/` | same warning, on `plugin/CLAUDE.md` |
| Probe with a `CLAUDE.md` at the **repo root**, outside the plugin dir | **silent** |

So the check is precisely "a `CLAUDE.md` at the plugin root", which is what D1 moves away
from. One caveat for Phase 1's gate: the warning does **not** change the exit code — our
tree emits it and still exits 0. Phase 1 must assert on the absence of the warning **text**,
not on the exit status.

### A4 and A5 — not settleable from the CLI, settled by the smoke session

`claude plugin details` enumerates components but never fires a skill, so neither assumption
was observable from the CLI alone. Both were exercised by a human
`claude --plugin-dir /tmp/wb-probe/plugin` session on 2026-09-08, which is why the probe
directory was retained past the end of `P0-T3` instead of being deleted there.

Verbatim from that session:

```text
probe_old is now probe. Running probe. Update your invocation — this alias is removed at the
next major.

  Read 2 files

LAYOUT PROBE
  skill enumerated from ./plugin source: YES
  sibling templates.md read:             NO PROMPT
  docs/reference/probe-ref.md read:      NO PROMPT
  marker from probe-ref.md:              PROBE-REF-RESOLVED
```

- **A4 — Validated, both halves.** The sibling read and the read that climbs out of the skill
  directory into `plugin/docs/reference/` were each unprompted. The cross-directory half was
  the one design.md flagged as uncertain, and it is what D19's "a shipped skill may link only
  into `plugin/docs/reference/`" rule depends on. The echoed `PROBE-REF-RESOLVED` marker is
  what distinguishes a real read from a paraphrase.
- **A5 — Validated.** `probe_old` announced the rename exactly once, then ran `probe` and read
  both of its supporting files. Note the shape of the evidence: marketplace **install and
  enumeration** of both skills was proven by the CLI (`Source: wbprobe@wb-probe`), while alias
  **invocation** was proven under `--plugin-dir`. Phase 4's marketplace-install alias check is
  therefore still worth running.

Both rows in design.md's `### Assumptions` table are flipped to Validated, and the decision is
recorded in design.md → Technical Decisions → Resolved Decisions.

### Verdict

**Proceed with D1 and D2 as designed**, on the CLI-observable evidence: the `./plugin`
source resolves, installs, enumerates, and validates; manifest agreement is checked across
the boundary; and the root-`CLAUDE.md` warning behaves exactly as D1 predicts. The two
open assumptions (A4, A5) concern *permission-prompt ergonomics and alias behaviour at
invocation*, not whether the layout loads — so they gate the Phase 0 checkpoint's human
sign-off, not the structural verdict.
