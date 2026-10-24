---
project: prompt_audit_5_5
ticket: null
created: 2026-10-21
created_timestamp: 2026-10-21T18:46:41Z
status: complete
last_updated: 2026-10-24
last_updated_note: "Added the Q1 effort probe and the Q2 blind trial; Q1-Q4 resolved"
researcher: scraig
git_commit: 43b9ca42b2f7f53320d14a8d331c692372ad69db
git_branch: thescubageek/5.5-models-prompt-optimization
repository: thescubageek/workbench
tags: [research, codebase, prompt_audit_5_5]
---

# Research: prompt_audit_5_5

**Created**: 2026-10-21
**Last Updated**: 2026-10-22
**Ticket**: N/A

## Research Question

How do the wb plugin's prompts (skills, agents, hooks, and reference docs) compare with the
current guidance for the Claude 5.5 models? The scope is an independent audit. Gabe Varela's
fork (`gvarela/workbench` 4.0.0, 2026-10-13) ran a similar migration. It removed gates and
aligned sub-agents with the 5.5 model behavior. That fork is one input. It is not the
baseline.

## Summary

The plugin names no 5.5 model anywhere. The model roster in
`plugin/skills/model-help/SKILL.md:23` lists Opus 5, Opus 4.8, Sonnet 5, and Haiku 4.5. The
upshift ladder at `:65` is `Haiku 4.5 → Sonnet 5 → Opus 4.8 → Opus 5 → Fable`. Claude Code
2.1.303 (this machine) resolves the aliases to the 5.5 models: `opus` is Opus 5.5, `sonnet` is
Sonnet 5.5, `haiku` is Haiku 5.5, and `fable` is Fable 5.1 (code.claude.com model-config).
The agent files pin aliases, so they already run on the 5.5 models. Only the advice text
names older models.

The wording of the prompts is mostly unchanged since 2.0.0. There are 23 triple-marker
`⛔⛔⛔ … STOP! … ⛔⛔⛔` barrier lines in 11 skills. There are 18 `CRITICAL`, 19 `MUST`,
45 `NEVER`, 12 `ALWAYS`, and 25 `DO NOT` directive lines. The 21 `think deeply` directives
that existed at the 2026-09-08 plan are gone (0 matches now). Every one of the 22
`subagent_type:` values in the spawn blocks is a bare name. A live probe in this session shows
that a bare name fails with `Agent type 'codebase-locator' not found`. Only `wb:`-scoped names
resolve.

One shipped rule constrains wording changes. WBTE "lite" rule 6
(`plugin/docs/reference/technical-english.md:59`) says to keep barriers, checkpoints, "Read
[link] NOW" directives, and capitalized scope rules, because measurements showed that trimming
them made results worse. Gabe's 4.0.0 applied the opposite change (single `⛔` with a reason,
caps rewritten). His evidence is the repository convention and a small blind trial. His audit
itself calls that trial weak. The current Anthropic guidance names effort, not prompt text, as
the main thinking control. It also warns against aggressive language on newer models, but no
page makes an explicit ALL-CAPS statement for a 5.x model.

## Detailed Findings

### 1. The shipped prompt surface

**Location**: `plugin/`

**What exists**:

- 169 files and 25,392 lines under `plugin/`. The skills are 125 files and 15,657 lines in
  41 skills. The agents are 7 files and 1,113 lines. The one hook script,
  `plugin/hooks/wb-prime.sh`, has 232 lines.
- 6 skills carry `user-invocable: false`: `doc-adherence`, `mockup-iteration`,
  `project-structure`, `status-sync`, `tdd-discipline`, and `verification-before-completion`.
- 3 skills carry `disable-model-invocation: true`. They are the deprecated aliases
  `create_execution`, `implement_coordinated`, and `implement_tasks`. Each is 24 or 25 lines.
- 3 `SKILL.md` files have more than 500 lines: `adversarial-loop` (718), `implement` (568),
  and `adversarial-review` (553). The Claude Code skills page says a `SKILL.md` should be
  "under 500 lines" (code.claude.com/docs/en/skills).
- No `SKILL.md` has a `model:` or `effort:` frontmatter key.

### 2. Agent definitions and their model and effort

**Location**: `plugin/agents/`

**What exists** (frontmatter verified directly, lines 2–8 of each file):

| Agent | `model` | `effort` | `maxTurns` |
| ----- | ------- | -------- | ---------- |
| `codebase-analyzer` | `sonnet` | `medium` | 30 |
| `codebase-locator` | `haiku` | not set | 25 |
| `pattern-finder` | `haiku` | not set | 25 |
| `product-behavior-analyzer` | `sonnet` | `medium` | 30 |
| `research-validator` | `sonnet` | `high` | 35 |
| `task-verifier` | `sonnet` | `high` | 50 |
| `task-worker` | not set | not set | 60 |

`task-worker` also has `skills: [tdd-discipline]`. With no `model` and no `effort`, its tier
comes from the spawn, and its effort comes from the session.

**Spawn blocks** pass a `model` on every `Task({ … })` block. None passes `effort`. Three
spawns pass a model that differs from the agent file:

- `validate_execution/sub-agent-prompts.md:28-29` spawns `codebase-analyzer` with `haiku`.
  The agent file says `sonnet` (`agents/codebase-analyzer.md:5`).
- `validate_execution/sub-agent-prompts.md:92-93` spawns `pattern-finder` with `sonnet`. The
  agent file says `haiku`.
- All 4 `codebase-analyzer` spawns in `create_mockup/sub-agent-prompts.md` (`:19`, `:35`,
  `:52`, `:86`) pass `haiku`.

The Claude Code sub-agents page gives this model precedence: the per-invocation `model`, then
the frontmatter `model`, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the main model. So a spawn
`model` overrides the agent file.

**Prose spawns**:

- `implement/SKILL.md:302` spawns `task-worker`. The tier comes from the ladder at `:287-292`.
- `implement/SKILL.md:337` and `implement/prompts/verifier-prompt.md:3-6` spawn
  `task-verifier` with no model and no effort. So `sonnet` and `high` from the agent file
  apply.
- `implement/prompts/escalation-worker-prompt.md:9-10` writes
  `Effort: ${escalationTier == "fable" ? "high" : "<tier default>"}`.
- `adversarial-review/prompts.md:153-165` uses `sonnet` for the stance, lens, and verifier
  agents, and `opus` for the security and AI-systems lenses. It says never to annotate
  `effort` on a haiku spawn (`:165`).

### 3. Model and effort advice

**Location**: `plugin/skills/model-help/SKILL.md`, `plugin/skills/implement/SKILL.md`,
`plugin/skills/daily-digest/SKILL.md`, `CLAUDE.md`

**What exists**:

- `model-help/SKILL.md:23` lists the roster `claude-opus-5`, `claude-opus-4-8`,
  `claude-sonnet-5`, and `claude-haiku-4-5-20251001`. It calls `claude-fable-5-1` a "fast
  Claude‑5 tier".
- `model-help/SKILL.md:38` says Opus 4.8 is "the default Opus" and Opus 5 is the ceiling.
- `model-help/SKILL.md:65` gives the ladder `Haiku 4.5 → Sonnet 5 → Opus 4.8 → Opus 5 →
  Fable`. Fable always runs at `effort: high`, never `xhigh` or `max` (`:70-76`).
- `model-help/SKILL.md:96-105` sets the per-phase baselines. `create_research`, `create_tasks`,
  `implement`, `implement_inline`, `validate_execution`, `adversarial-review`, and
  `adversarial-loop` start at Sonnet 5 / medium. `create_design` starts at Opus 4.8 / high.
- `implement/SKILL.md:287-292` is the worker ladder. `opus` is the default. `sonnet` is "the
  deliberate downshift". `haiku` is for mechanical work only. `fable` is an election after a
  verified failure. `:294-296` says the spawn `model` is an enum of these four values.
- `implement/SKILL.md:396-416` allows one escalation, one rung up, after a verified failure.
- `daily-digest/SKILL.md:155-166` maps trivial work to `haiku` / `low`, moderate to `sonnet` /
  `medium`, complex to `opus` / `high`, and critical to `opus` / `xhigh`→`max`.
- `CLAUDE.md:209-211` lists only `haiku`, `sonnet`, and `opus` for spawns.
- `git grep -E '5\.5|5-5'` outside `docs/plans/` finds no 5.5 model name in the repository.

### 4. Prompt wording patterns

**Location**: `plugin/skills/`, `plugin/agents/`, `plugin/hooks/`, `plugin/docs/reference/`

**What exists** (counts are matching lines):

| Pattern | Lines | Files |
| ------- | ----- | ----- |
| Triple `⛔⛔⛔` barrier with `STOP!` | 23 | 11 |
| Single `⛔` | 72 | 26 |
| `CRITICAL` | 18 | 12 |
| `IMPORTANT` | 5 | 3 |
| `MUST` | 19 | 10 |
| `NEVER` | 45 | 17 |
| `ALWAYS` | 12 | 8 |
| `DO NOT` | 25 | 11 |
| Uppercase `FULLY` | 37 | 17 |
| "no" or "WITHOUT" `limit/offset` | 18 | 18 |
| `think deeply`, `ultrathink`, `think hard` | 0 | 0 |
| "Wait for ALL" | 12 | 8 |
| "completion notification" | 0 | 0 |

- The triple lines are in `create_design`, `create_handoff`, `create_mockup`,
  `create_product_research`, `create_research`, `create_tasks`, `explore_design`, `implement`,
  `implement_inline`, `resume_handoff`, and `validate_execution`. `STOP!` occurs only on those
  23 lines.
- Single-marker barriers with a stated reason already exist, for example
  `implement/SKILL.md:243` (`⛔ BARRIER 2: One task at a time, in document order`).
- `NEVER` is densest in `implement_inline/reference.md` (13 lines) and `implement/reference.md`
  (9 lines).

**Key code** (`plugin/skills/create_research/SKILL.md:191`):

```markdown
**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL sub-agents to complete - DO NOT proceed until EVERY agent returns ⛔⛔⛔**
```

**Repeated rules inside one skill**:

- The documentarian rule in `create_research` is in `SKILL.md:24-32`, `:79`, `:184`, `:189`,
  `:208`, in `reference.md:15-16`, and in `sub-agent-prompts.md:50`, `:93`, `:95`. The agent
  files carry it too (`agents/codebase-analyzer.md:18`, `:116`).
- The read-fully rule in `create_research` is in `SKILL.md:85`, `:86`, `:102`, `:108`, and in
  `reference.md:24`.
- The wait-for-all rule in `create_research` is in `SKILL.md:188`, `:191`, `:200`, and in
  `reference.md:10`. `create_product_research` repeats each of these three patterns.
- `implement/SKILL.md:113` and `implement_inline/SKILL.md:117` have the same barrier line.

**Repeated boilerplate across skills**:

- "If a directed read fails, stop" is in 18 skills, with 2 variants.
- "Output discipline" is in 14 skills, with 2 variants.
- "Model & effort (gate check)" is in 7 skills, with 2 variants. It ends "See CLAUDE.md →
  'Model & effort at gates.'" in 5 skills, for example `create_research/SKILL.md:37`. That
  `CLAUDE.md` is the repository root file, which is not shipped (`CLAUDE.md`, "Repository
  Structure").
- The WBTE link line is in 49 files across 20 skills.

### 5. Spawn names

**Location**: `plugin/skills/*/sub-agent-prompts.md`, `plugin/skills/implement/SKILL.md`

**What exists**:

- 22 `subagent_type:` values in 6 files. All are bare: `codebase-analyzer` 9, `pattern-finder`
  7, `codebase-locator` 2, `general-purpose` 2, `product-behavior-analyzer` 1,
  `research-validator` 1.
- `implement/SKILL.md:302` and `:337` name `task-worker` and `task-verifier` without `wb:`.

**Live probe** (2026-10-21, Claude Code 2.1.303, cwd
`/Users/scraig/conductor/workspaces/workbench/douala-v1`): an Agent call with
`subagent_type: "codebase-locator"` returned this error:

```text
Agent type 'codebase-locator' not found. Available agents: claude, Explore, general-purpose,
Plan, statusline-setup, wb:codebase-analyzer, wb:codebase-locator, wb:pattern-finder,
wb:product-behavior-analyzer, wb:research-validator, wb:task-verifier, wb:task-worker
```

The same session spawned `wb:codebase-locator` and the other scoped names with no error.

### 6. Wording that the guards and evals check

**Location**: `plugin/scripts/`, `evals/`, `plugin/docs/reference/technical-english.md`

**What exists**:

- WBTE "lite" rule 6 (`plugin/docs/reference/technical-english.md:59`): "Keep barriers,
  checkpoints, "Read [link] NOW" directives, and capitalized scope rules as they are.
  Measurements showed that trimming them makes results worse."
- No script under `plugin/scripts/` tests barrier wording, directive words, read-fully wording,
  spawn names, or the documentarian rule. `test-prime` checks only the WBTE rule card in
  `wb-prime.sh` (at most 150 words, `test-prime:185-188`).
- `evals/token_check.py:74-119` with `evals/tokens.json` checks that each
  `### ⛔ CHECKPOINT:` block keeps at least 4 labels and the sentence "Go by the label, never
  by position".
- `evals/judge.py:48` and `:119` count `⛔` as barriers when they judge a regression.
- `evals/link_check.py` checks the WBTE link line in each template.

### 7. The eval harness and earlier measurements

**Location**: `evals/`, `CHANGELOG.md`, `docs/plans/`

**What exists**:

- `evals/run.py` runs only `create_research`, `create_design`, and `create_tasks` headless with
  `claude -p`. The defaults are `--repeats 3` and `--model sonnet`. `implement`,
  `validate_execution`, and the review skills are not in its `STAGES`.
- `judge.py --within` is the gate for "no lost facts": each run's `design.md` and `tasks.md`
  must keep the facts of its own `research.md`.
- No stored run exists. `evals/runs/` is gitignored and absent in this worktree and in the
  `ankara` worktree.
- One large-fixture repeat costs about $5 and 12 minutes. Four parallel gates hit the user's
  spend limit on 2026-09-30 (`docs/plans/2026-09-29-asd-ste100-prose/design.md`, D10).
- The 2.2.0 WBTE gate measured these numbers (`CHANGELOG.md:221-235`, 3 repeats, `sonnet`):

| Measure | 2.1.1 | 2.2.0 |
| ------- | ----- | ----- |
| Document sentences over 25 words | 7.0% | 2.9% |
| Semicolons in document prose | 82 | 9 |
| Chat IDs used alone | 25 | 2 |
| Lost facts (within-run judge) | none in 3 of 3 | none in 3 of 3 |

- A rewrite of `codebase-analyzer` and `codebase-locator` was reverted after its gate found a
  lost fact (`CHANGELOG.md`, 2.2.0).
- The upstream 2026-09-05 blind trial (recorded in
  `docs/plans/2026-09-08-upstream-fable-merge/research.md:188-220`) used fresh Sonnet agents
  with no tools, 3 fixtures, and 3 trials per wording. On the trap fixture, the triple-marker
  barrier held WAIT 0 of 3, and the single marker with a reason held 1 of 3. The CAPS scope
  block surfaced the trap bug 3 of 3, and the plain block surfaced it 2 of 3.

### 8. Gabe's fork, 4.0.0

**Location**: `gvarela/workbench`, tag `v4.0.0` (`9020332`), read with `gh api`

**What exists**:

- The forks diverged at `cb693fb` (2026-04-28). This repository is 31 commits ahead and 17
  behind. No git merge from upstream exists here. The 2026-09-08 plan re-implemented ideas from
  upstream 3.0.0 as this repository's 2.0.0.
- Gabe's fork keeps beads (`bd`) for status. This repository uses checkboxes in `tasks.md`.
- The audit is in `docs/audits/2026-09-29-prompt-audit/` (13 files). It has 60 findings in four
  slices (A: research, B: design, C: implement, D: operations). 43 were applied. An adversarial
  review tested 25 claims: 13 confirmed, 9 partially confirmed, and 3 refuted.
- The audit graded unpinned skills against Opus 5.5, `sonnet` files against Sonnet 5.5, and
  `haiku` files against Haiku 4.5 (`FACTS.md:35`). Later 4.0.0 commits say the `haiku` alias
  resolves to Haiku 5.5, which supports effort.
- No eval ran on the audit diff (`README.md:103`). The diff adds 218 lines and removes 590 in
  41 files. Caps-marker lines in `plugin/` dropped from 98 to 13.

**4.0.0 changes and the state of this repository**:

| 4.0.0 change | This repository now |
| ------------ | ------------------- |
| One `⛔` per barrier, with a reason | 23 triple-marker lines remain |
| Barriers name the completion notification | "completion notification" has 0 matches |
| Caps emphasis rewritten as plain rules | The counts in section 4 |
| Scoped `wb:` spawn names | All 22 values are bare |
| `task-worker` `effort: medium` | No `model` or `effort` (`agents/task-worker.md:1-7`) |
| `codebase-locator` `effort: low` | No `effort` |
| `pattern-finder` on `sonnet` at `low` | `haiku`, no `effort` |
| `task-verifier`, `research-validator` on `opus` | Both `sonnet` / `high` |
| `validate_execution`, `research-validation` pin `model: opus` | No `model:` key |
| Spawn models match agent files | 3 spawn sites differ (section 2) |
| "Read fully, paging through a partial view" | "no limit/offset" in 18 files, `CLAUDE.md:151` |
| `review-prep` does not trigger on "review" | `review-prep/SKILL.md:3` still lists "review" |
| `product-behavior-analyzer` folded into `codebase-analyzer` | The agent exists |
| One automatic fix attempt in `implement` | Already one (`implement/SKILL.md:396`, `:404`) |
| Verifier spawned with no `model` | Already so (`verifier-prompt.md:6-17`) |

**Claims in Gabe's 4.0.0 that bear on Claude Code behavior**:

- "a spawn can override the model but not the effort" (`CLAUDE.md:175` in the fork). The
  commit message says a spawn with `effort: "high"` ran at the session's `medium`, at Claude
  Code 2.1.285.
- "Opus 5.5 is the stronger reviewer … at about twice Sonnet 5.5's price" (`CHANGELOG.md:29` in
  the fork). The commit message gives no source URL for the reviewer-quality part.

### 9. Current published guidance

**Location**: platform.claude.com and code.claude.com, fetched 2026-10-21

**What exists**:

- **Emphasis.** The prompting best-practices page says: "If your prompts were designed to
  reduce undertriggering on tools or skills, these models may now overtrigger. The fix is to
  dial back any aggressive language." That statement names Opus 4.5 and 4.6. No 5.x page
  makes an ALL-CAPS statement. The Claude Code best-practices page says: "If you emphasize many
  lines, none of them stands out." The bundled `claude-api` skill reference says: "Emphasis is
  not banned; it is a tested, scoped fix for one demonstrably underweighted instruction".
- **Reasons over rules.** The best-practices page shows `NEVER use ellipses` as less effective
  than the same rule with its reason. It says: "Claude is smart enough to generalize from the
  explanation."
- **Literal instruction following.** The Sonnet 5 page says the model "does not silently
  generalize an instruction from one item to another". The Opus 5 page says a review prompt
  that says "only report high-severity issues" may make the model report less.
- **Thinking and effort.** The thinking-steering page says: "Effort is the primary steering
  lever for thinking." It also says that a Sonnet 5.5 system-prompt request to think less
  "doesn't reliably reduce its thinking". Thinking is always on for Opus 5.5 and Fable 5.1.
- **Effort defaults.** Opus 5.5 and Haiku 5.5 default to `medium` on the API. Sonnet 5.5 and
  Fable 5.1 default to `high`. Claude Code defaults Opus 5.5, Sonnet 5.5, and Haiku 5.5 to
  `medium`. Haiku 5.5 is "the first Haiku model with effort levels". The effort page lists `low`
  for "Simpler tasks that need the best speed and lowest costs, such as subagents".
- **Per-model starting points.** Opus 5.5 at `medium` "matches or exceeds Claude Opus 5 at
  `high` on coding and knowledge-work evaluations". Sonnet 5.5 starts at `medium` for
  well-specified agentic coding and `high` for harder work. Haiku 5.5 at `low` is "more likely
  to skip a search, stop early, or skip a check".
- **Price and position** (models overview):

| Model | Input / output per MTok | Default effort | Described use |
| ----- | ----------------------- | -------------- | ------------- |
| Fable 5.1 | $10 / $50 | `high` | Demanding reasoning and long-horizon agentic work |
| Opus 5.5 | $4 / $20 | `medium` | Long-running agentic coding and knowledge work |
| Sonnet 5.5 | $2 / $10 | `high` | The best combination of speed and intelligence |
| Haiku 5.5 | from $0.10 / from $0.50 | `medium` | Classification, extraction, routing, subagent tasks |

- **Scope and verification.** The Sonnet 5.5 page says the model "tends to add tests,
  documentation, and small supporting files … even when you don't ask for them". The Sonnet 5.5
  and Haiku 5.5 pages say that at low effort the model "sometimes reports a change as done
  without running a check that exercises it". The Fable 5 page says that fresh-context verifier
  subagents "tend to outperform self-critique".
- **Delegation.** The Sonnet 5.5 page reports that "don't launch reviewer sub-agents unless the
  user asked for a review" cut session cost by about a third with no change in quality.

### 10. Claude Code subagent mechanics

**Location**: code.claude.com/docs/en/sub-agents, /skills, /model-config, /hooks

**What exists**:

- **Per-spawn effort.** The sub-agents page says Claude can pass an `effort` parameter on the
  Agent tool call for a non-fork subagent. It overrides the frontmatter `effort`. This needs
  Claude Code 2.1.292 or later. This machine runs 2.1.303 (`claude --version`). The Agent tool
  schema in this session lists `effort` with the values `low` to `max`. Its description says to
  set it "ONLY when the user, or instructions such as CLAUDE.md or a skill, explicitly ask".
  Gabe's measurement of the opposite was at 2.1.285.
- **Model enum.** The Agent tool `model` parameter accepts `sonnet`, `opus`, `haiku`, and
  `fable` (this session's schema). Agent frontmatter also accepts a full model ID.
- **Background by default.** "With nothing configured, a subagent that Claude spawns from the
  main conversation starts in the background." Results arrive as a completion notification in a
  later turn. Fork mode is on by default from 2.1.302.
- **Skill frontmatter.** A skill `model` applies only for the rest of the current turn. A skill
  `effort` overrides the session effort while the skill is active.
- **Hooks.** Hook stdout is capped at 10,000 characters. PreCompact output does not reach the
  model (Gabe's audit, `review/M.md`, M1, confirmed against the hooks page). This repository
  registers `wb-prime.sh` on PreCompact (`plugin/.claude-plugin/plugin.json:59`).

## Architecture Documentation

**Current patterns found**:

- One tier authority for each lever. Agent files and `implement` Step 5 own the spawned tiers.
  `model-help` owns the main-session tier and the switch cost (`model-help/SKILL.md:107-113`).
- Spawn blocks restate the model of the agent file, so each spawn site is a second place where
  the tier changes (section 2).
- Barriers come in two forms. The older form is triple-marker with `STOP!`. The newer form is
  one marker with a reason, which `CLAUDE.md` ("Command Structure Patterns") documents.
- Shared rules live in `plugin/docs/reference/`. Skills link to them. Five skills link to the
  root `CLAUDE.md` for the gate rule, which an installer does not receive.

**Component connections**:

- `create_*` stages → agents: through `sub-agent-prompts.md` spawn blocks, for example
  `create_research/sub-agent-prompts.md:40-41`.
- `implement` → `task-worker` and `task-verifier`: through `implement/SKILL.md:302` and `:337`
  and the files in `implement/prompts/`.
- Every stage → `model-help`: through the "Model & effort (gate check)" line, for example
  `create_research/SKILL.md:37`.

**Conventions observed**:

- Wording changes to instructions are gated by the eval harness under WBTE "lite" rules
  (`technical-english.md:51-60`).
- Spawned models are written as the four aliases. Full IDs are only for `/model`.

## Code References

- `plugin/skills/model-help/SKILL.md:23` - The model roster, with no 5.5 model
- `plugin/skills/model-help/SKILL.md:65` - The upshift ladder
- `plugin/skills/model-help/SKILL.md:96-105` - The per-phase baselines
- `plugin/skills/implement/SKILL.md:287-296` - The worker tier ladder
- `plugin/skills/implement/SKILL.md:396-416` - The single escalation rule
- `plugin/agents/task-worker.md:1-7` - The worker with no model and no effort
- `plugin/agents/task-verifier.md:5-6` - The verifier at `sonnet` / `high`
- `plugin/skills/create_research/sub-agent-prompts.md:40-41` - A bare spawn name
- `plugin/skills/validate_execution/sub-agent-prompts.md:28-29` - A spawn model that differs from
  the agent file
- `plugin/skills/create_research/SKILL.md:191` - A triple-marker barrier
- `plugin/docs/reference/technical-english.md:59` - WBTE "lite" rule 6
- `plugin/skills/review-prep/SKILL.md:3` - The trigger on the bare word "review"
- `CLAUDE.md:151` - "ALWAYS read files FULLY (no limit/offset)"
- `evals/run.py` - The harness, which covers 3 stages

## Similar Implementations

**Example from `plugin/skills/implement/SKILL.md:243`** (a barrier in the newer form):

```markdown
**⛔ BARRIER 2: One task at a time, in document order**
```

This form is also used at `implement/SKILL.md:308`, `:456`, `implement_inline/SKILL.md:358`,
`daily-digest/SKILL.md:95`, `:128`, and `adversarial-review/SKILL.md:424`.

**Example from `plugin/skills/implement/prompts/verifier-prompt.md:3-6`** (a spawn that lets the
agent file set the tier): the verifier spawn names no `model` and no `effort`.

## Open Questions

This table lists the questions to resolve before the next phase. Each question has a short
local ID. This section is the record, because there is no external tracker.

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| Q1 | Does a per-spawn `effort` on the Agent tool take effect in Claude Code 2.1.303? The docs and this session's schema say yes. Gabe measured no at 2.1.285. | Whether effort is set in agent files, in spawns, or in both | **Resolved 2026-10-22** → design.md (## Technical Decisions) |
| Q2 | Does WBTE "lite" rule 6 (`technical-english.md:59`) still hold for the 5.5 models? It rests on measurements made on earlier models. | Any change to barrier markers or capitalized scope rules | **Resolved 2026-10-22** → design.md (## Technical Decisions) |
| Q3 | What eval spend is acceptable for this plan? One large-fixture repeat costs about $5 and 12 minutes, and the harness covers only 3 stages. | The gate design for each wording change, and for agent tier changes | **Resolved 2026-10-22** → design.md (## Technical Decisions) |
| Q4 | Which main-session model is the baseline for the audit: Opus 5.5 (the Claude Code default), Sonnet 5.5, or Fable 5.1? | The model-help roster and per-phase baselines, and which guidance page each file is graded against | **Resolved 2026-10-22** → design.md (## Technical Decisions) |

## Next Steps

These steps follow from the findings:

1. Read the Follow-up Research section below. It answers Q1 and Q2 with measurements.
2. Review this research document.
3. Run `/wb:create_design docs/plans/2026-10-21-prompt_audit_5_5` to write the design decisions.

## Follow-up Research 2026-10-22 20:09

This section records two probes. Q1 (per-spawn effort) and Q2 (WBTE "lite" rule 6) are now
answered by measurement. The user decided Q3 (the eval budget) and Q4 (the baseline model). The
decisions are in `design.md`.

### Q1: a per-spawn `effort` takes effect

**Result**: the Agent tool's `effort` value reaches the API request. It overrides the `effort` in
the agent file. A spawn with no `effort` inherits the session's effort.

**Method**: 4 Agent calls from this session (Claude Code 2.1.300, the version recorded in the
transcripts; cwd `/Users/scraig/conductor/workspaces/workbench/douala-v1`). Each subagent
transcript under `~/.claude/projects/<project>/<session>/subagents/` records
`"output_config":{"effort":"<level>"}` for every request. The `.meta.json` beside it records the
spawn's `model` and `effort`.

| Spawn | Agent file `effort` | Spawn `effort` | Model in transcript | `output_config.effort` |
| ----- | ------------------- | -------------- | ------------------- | ---------------------- |
| `general-purpose`, `model: haiku` | none | `low` | `claude-haiku-5-5` | `low` |
| `general-purpose`, `model: sonnet` | none | `max` | `claude-sonnet-5-5` | `max` |
| `wb:codebase-analyzer`, no `model` | `medium` | `low` | `claude-sonnet-5-5` | `low` |
| `general-purpose`, `model: haiku` (control) | none | none | `claude-haiku-5-5` | `high` |

- The main session in this conversation runs at `high`. Its own transcript records
  `"effort":"high"` on every request. The control spawn inherited that level.
- The six research agents of 2026-10-21 confirm the same rule. `wb:codebase-analyzer`
  (`effort: medium` in its file) ran at `medium`. `wb:codebase-locator` and `wb:pattern-finder`
  (no `effort` in their files) ran on `claude-haiku-5-5` at the session's `high`.
- Gabe's 4.0.0 says the opposite ("a spawn can override the model but not the effort"). He
  measured it at Claude Code 2.1.285. The sub-agents page says the parameter needs 2.1.292 or
  later.

### Q2: rule 6 has no support on the 5.5 models for barriers and scope rules

**Result**: plain wording scored the same as the current wording in every cell. The test covered
Opus 5.5 and Sonnet 5.5 at `medium` effort, 10 repeats for each cell, 320 runs, $3.62. The
earlier deficits (WAIT 0 of 3 against 1 of 3, and an issue surfaced 3 of 3 against 2 of 3) do not
reproduce.

**Method**: headless `claude -p` calls with no tools. Each prompt has a skill excerpt in one of two
arms, a fixture, and a fixed reply format. The `base` arm is the current text, verbatim
(`create_research/SKILL.md:180-200`, `implement_inline/SKILL.md:67-91`). The `trim` arm has the
same content in plain wording. Its barrier line is the v4.0.0 single-marker line from
`gvarela/workbench`. The full record, the harness, and the 320 raw results are in
[trials/2026-10-22-q2-blind-trial/RESULTS.md](trials/2026-10-22-q2-blind-trial/RESULTS.md).

| Set | Fixture | Opus 5.5 base | Opus 5.5 trim | Sonnet 5.5 base | Sonnet 5.5 trim |
| --- | ------- | ------------- | ------------- | --------------- | --------------- |
| A (barrier) | 3 of 3 agents returned | 10 | 10 | 10 | 10 |
| A (barrier) | 1 of 3 returned | 10 | 10 | 10 | 10 |
| A (barrier) | 2 of 3, third streaming a partial | 10 | 10 | 10 | 10 |
| A (barrier) | 2 of 3, third stale and complete-looking | 10 | 10 | 10 | 10 |
| A (barrier) | the stale fixture plus "don't make me wait" from the user | 0 | 0 | 0 | 1 |
| B (scope) | clean files | 10 | 10 | 10 | 10 |
| B (scope) | unrelated bug in `utils.py` | 10 | 10 | 10 | 10 |
| B (scope) | `[1:]` bug in the edited function | 10 | 10 | 10 | 10 |

- In the user-override fixture, the runs gave the user's explicit instruction as the reason to
  synthesize. That fixture measures user authority, not the barrier. Both wordings gave the same
  result.
- In Set B, every run kept the `[1:]` bug, named it under ISSUES ENCOUNTERED, and reported the
  `utils.py` bug without a fix.
- **Limits**: the excerpts are short, with a small system prompt and no tools. Real stages read
  200 to 600 lines in a long context. Only `medium` effort was run. Both arms reached 10 of 10, so
  the trial shows no loss but cannot rank the wordings. Rule 6 also covers checkpoints and
  "Read [link] NOW" directives. Neither this trial nor the 2026-09-05 trial measured them.

### Spend against the Q3 budget

| Item | Cost |
| ---- | ---- |
| Q2 trial, 320 headless runs | $3.62 (sum of `total_cost_usd`) |
| Q1 probe, 4 one-word Agent calls | Not reported separately. Each reply used about 13,000 to 35,000 tokens of context |

Roughly $26 of the $30 budget is left for the rest of this plan.
