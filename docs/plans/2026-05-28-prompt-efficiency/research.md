---
project: prompt-efficiency
ticket: N/A
created: 2026-05-28
status: complete
last_updated: 2026-06-07
last_updated_note: "Added §16 handoff-command structure and §17 native-capability inventory"
researcher: scraig
git_commit: cb693fb
git_branch: prompt-efficiency-research
repository: karachi-v1
---

# Research: Prompt Efficiency for Opus 4.x Token/Performance Optimization

**Created**: 2026-05-28
**Last Updated**: 2026-05-28
**Ticket**: N/A

## Research Question

How could the existing prompts (commands, agents, skills) in this plugin be made more efficient in terms of Opus 4.8 and token/performance optimization?

> **Documentarian scope note**: this research describes what EXISTS in the current prompts — file sizes, structural patterns, repeated boilerplate, barrier scaffolding, agent-spawn templates, and embedded output templates. It deliberately makes no optimization recommendations. The subsequent `/wb:create_design` step will decide what (if anything) to change. Note also that "Opus 4.8" is the user-supplied framing; the most recent shipped Opus model in this environment is Opus 4.7. Findings here apply to any current-generation Opus model.

## Summary

The plugin's runtime prompt surface (commands + agents + skills + auto-loaded CLAUDE.md) totals **~285,800 bytes / 9,758 lines / ~71,400 estimated tokens** (at ~4 chars/token). `commands/` alone is **215 KB / 7,422 lines / ~53,800 tokens** — 58 % of the total prompt bytes. The five largest individual prompt files in the repo account for ~28 % of all bytes.

The repository follows a single, highly consistent structural template across its 14 slash commands. Each command embeds (1) an `## Initial Response` argument-parsing scaffold, (2) sequential `### Step N` blocks with one or more `⛔⛔⛔ BARRIER N: STOP! ... ⛔⛔⛔` synchronization markers, (3) a `### Step N: Spawn Parallel Research Agents` block with pseudo-JS `Task({...})` examples that take `subagent_type` and `model` keys, (4) a full verbatim markdown template of the output document the command produces, and (5) a closing `## Important Notes` / `## Synchronization Points` recap that restates the barriers. The same documentarian philosophy (e.g., "Document what IS, not what SHOULD BE") is restated in CLAUDE.md, in command headers, in agent-spawn boilerplate, and in the agent files themselves.

Cross-file duplication is most concentrated between the research/design/execution family of `create_*` commands, and most pronounced between `commands/create_research.md` and `commands/create_product_research.md`, which are explicitly described in repo commits as "near-mirror" siblings. Recurring boilerplate identified by the pattern agent includes the `## CRITICAL: YOUR ONLY JOB IS TO DOCUMENT THE CODEBASE AS IT EXISTS` header + 5-bullet DO-NOT list (appears in 5 files), the "Sub-agents are READ-ONLY" preamble (5 files), the `BARRIER` scaffolding (49+ inline + a duplicated end-of-file recap in 9 files), the canonical Component-Locator → Implementation-Analyzer → Pattern-Finder agent trio (2 files verbatim), the dated example `docs/plans/2025-01-08-...` (13+ files), and embedded output templates totaling ~25 KB of literal markdown skeleton inside command bodies.

## Detailed Findings

### 1. Inventory & Token Budget

**Location**: `commands/`, `agents/`, `skills/`, `docs/`, repo root

**What exists** (sorted by group, largest within group first; token estimates use 4 chars/token):

| Group | Files | Bytes | Lines | ~Tokens |
|---|---:|---:|---:|---:|
| `commands/` (runtime, loaded when invoked) | 14 | 215,185 | 7,422 | 53,796 |
| `agents/` (runtime, dispatched via Task) | 6 | 29,074 | 916 | 7,269 |
| `skills/` (auto-activated on match) | 7 | 26,831 | 999 | 6,709 |
| `docs/` (reference-only, not auto-loaded) | 5 | 87,840 | 3,245 | 21,960 |
| Root: CLAUDE.md / AGENTS.md / README.md | 3 | 14,689 | 421 | 3,672 |
| **Grand total** | **35** | **373,619** | **13,003** | **93,405** |

**Top 5 largest prompt files (by bytes)**:

1. [`commands/implement_coordinated.md`](commands/implement_coordinated.md) — 23,852 bytes / 808 lines / ~5,963 tokens
2. [`commands/create_execution.md`](commands/create_execution.md) — 23,614 bytes / 783 lines / ~5,904 tokens
3. [`docs/commands-reference.md`](docs/commands-reference.md) — 22,249 bytes / 873 lines / ~5,562 tokens *(reference-only)*
4. [`docs/claude-code-skills-guide.md`](docs/claude-code-skills-guide.md) — 21,525 bytes / 834 lines / ~5,381 tokens *(reference-only; **0 inbound links** — orphan)*
5. [`docs/workbench-workflow-guide.md`](docs/workbench-workflow-guide.md) — 19,532 bytes / 837 lines / ~4,883 tokens *(reference-only)*

**Auto-loaded context** (loaded into every Claude Code session in this repo): only `CLAUDE.md` (1,909 tokens). Nothing in `docs/` auto-loads.

**Orphan reference docs** (zero inbound markdown links found anywhere in the repo):

- `docs/claude-code-skills-guide.md` — 21,525 bytes
- `docs/product-research-claude-desktop.md` — 16,759 bytes (a portable mirror of `commands/create_product_research.md` for Claude Desktop use; commit `cb693fb` describes it as "Make portable prompt a near-mirror of create_product_research command")

Combined ~9,571 tokens of reference text with no in-repo navigation entry points.

**Runtime-loadable budget** (commands + agents + skills + CLAUDE.md, if everything loaded simultaneously): 285,779 bytes / 9,758 lines / **~71,445 tokens**. In practice only one command's prompt + invoked agents + matched skills load per turn.

### 2. Frontmatter Conventions

**Location**: `commands/*.md` lines 1–4, `agents/*.md` lines 1–4, `skills/*/SKILL.md` lines 1–16

**What exists**:

- **Commands**: every command uses exactly two frontmatter fields — `description:` and `argument-hint:` — and nothing else. No command sets `model:`, `tools:`, or `allowed-tools:`. Consistency is 14/14 across `create_project.md:1-4` through `help.md:1-4`.
- **Agents**: every agent file uses `name:`, `description:`, and `tools:`. No agent declares `model:`. Tool lists vary per role (e.g. `codebase-locator.md:4` allows `Grep, Glob, Bash(find:*, ls:*)`; `task-verifier.md:4` allows `Bash, Read, Grep, Glob`).
- **Skills**: 7/7 declare `name:` + `description:`. `allowed-tools:` appears inline in `status-sync/SKILL.md:4` and `mockup-iteration/SKILL.md:4`; as a YAML list in `research-validation/SKILL.md:4-8` and `review-prep/SKILL.md:4-8`; and is absent from `project-structure/SKILL.md`, `tdd-discipline/SKILL.md`, and `verification-before-completion/SKILL.md`. Only `mockup-iteration/SKILL.md:5-15` declares explicit `triggers:`.

**Prose-style frontmatter spec listing** (the field names enumerated as documentation rather than as YAML) also exists in `CLAUDE.md:118-122`, `commands/update_status.md:80-90`, and `commands/validate_project.md:286-292`.

### 3. Command Section Structure

**Location**: all 14 files under `commands/`

**What exists** — every command follows a near-identical macro-structure. The recurring sections are:

1. **Title heading** (`# <Verb Phrase>`) — line 6 or 7
2. **`## CRITICAL: ...` header** (commands that produce documentation start with this) — `create_research.md:10`, `create_product_research.md:10`, `create_design.md:10`, `update_status.md:10`
3. **`## Initial Response`** — argument-parsing scaffold present in 14/14 commands; canonical structure shown below
4. **`## Process Steps` / `## Steps to Execute ...`** — numbered `### Step N` subsections
5. **`## Important Notes` / `## Important Guidelines`** — appears in 13/14 commands (only `help.md` omits)
6. **`## Synchronization Points`** — end-of-file BARRIER recap, present in 9 commands
7. **`## Configuration`** — closing one-liner example, present in 12/14

**Initial Response boilerplate** (repeats in ~14 commands, ~350–500 chars per instance):

```
## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:[name] docs/plans/2025-01-08-[topic]/`):
   - Use `$1` as the project directory
   ...

2. **If no arguments**:

   ```
   I'll help you... Please provide:
   ...
   ```
```

Estimated cumulative cost across 14 commands: ~5,000 chars / ~1,100 tokens.

### 4. Barrier and Checkpoint Scaffolding

**Location**: inline throughout `commands/*.md`; also restated in `## Synchronization Points` sections at end-of-file

**What exists**:

- **Shouting-style barriers** (`⛔⛔⛔ BARRIER N: STOP! ... ⛔⛔⛔`) appear inline at decision points across 14 commands. Examples:
  - [`commands/create_research.md:50`](commands/create_research.md) — `**⛔⛔⛔ BARRIER 1: STOP! Do NOT proceed to Step 2 until ALL mentioned files are FULLY read ⛔⛔⛔**`
  - [`commands/create_research.md:195`](commands/create_research.md) — `**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL sub-agents to complete - DO NOT proceed until EVERY agent returns ⛔⛔⛔**`
  - [`commands/create_research.md:341`](commands/create_research.md) — `**⛔⛔⛔ BARRIER 3: STOP! Verify NO placeholder values - ALL data MUST be from ACTUAL codebase ⛔⛔⛔**`
  - [`commands/create_product_research.md:68`](commands/create_product_research.md) — verbatim duplicate of `create_research.md:50`
  - [`commands/implement_coordinated.md:83`](commands/implement_coordinated.md) — verbatim duplicate of `implement_tasks.md:82`

- **Abbreviated barriers** (`⛔ BARRIER N`) — used in `create_design.md:346`, `create_project.md:383`, `create_mockup.md:129,224,372,473`, `implement_tasks.md:329`, `implement_coordinated.md:234,374,486`, `update_status.md:41,198,268`, `validate_project.md:99`.

- **Checkpoint markers** — `create_execution.md:334`, `implement_tasks.md:370`, `implement_coordinated.md:521`, and the design-specific `**⛔ DECISION POINT**` / `**⛔ APPROVAL GATE**` at `create_design.md:472,474`.

- **End-of-file Synchronization Points recap** (restates BARRIER 1/2/3 a second time inside the same file): `create_research.md:416-420`, `create_design.md:468-475`, `create_execution.md:773-779`, `implement_tasks.md:669-674`, `validate_execution.md:419-423`, `validate_project.md:508-512`, `create_product_research.md:519-524`, `create_project.md:441-446`, `create_mockup.md` (similar block).

**Aggregate occurrence count**: 49+ barrier lines across the in-scope command files. Per-line ~80–110 chars; combined ~5,500 chars / ~1,250 tokens of barrier markup.

### 5. "Think Deeply" / "Ultrathink" Directives

**Location**: inline in command bodies, typically at the top of analysis-heavy steps

**What exists** — quoted with file:line:

- `commands/create_research.md:61` — `**think deeply about what EXISTS in the codebase**`
- `commands/create_research.md:67` — `**Take time to ultrathink about:**`
- `commands/create_research.md:199` — `**think deeply about documenting ONLY what EXISTS**`
- `commands/create_product_research.md:80,90,223` — three `ultrathink` directives
- `commands/create_design.md:87,161` — two `think deeply` directives
- `commands/create_execution.md:65,150` — two `think deeply` directives
- `commands/implement_tasks.md:113`, `implement_coordinated.md:117`
- `commands/validate_execution.md:70,178`, `validate_project.md:125`, `update_status.md:94`, `create_project.md:49`
- `commands/create_handoff.md:86`, `resume_handoff.md:93`, `create_mockup.md:173`

Total: ~20 directives across commands.

### 6. Agent-Spawning Template (Pseudo-JS `Task({...})` Blocks)

**Location**: 6 commands embed pseudo-JS `Task()` code blocks: `create_research.md`, `create_product_research.md`, `create_design.md`, `create_execution.md`, `validate_execution.md`, `create_mockup.md`. `implement_coordinated.md` uses a prose description plus a JavaScript `determineModel()` helper (lines 661–699) that classifies tasks into haiku/sonnet/opus via regex pattern lists.

**What exists** — the canonical block uses the four keys `description`, `prompt`, `subagent_type`, `model`:

```javascript
Task({
  description: "Find [feature] components",
  prompt: `Find all files related to [feature].
  ...
  DO NOT write any files. Return your findings as a report.`,
  subagent_type: "codebase-locator",
  model: "haiku"
})
```

**Model hints used** (across 22 Task() blocks total):

- `haiku` — file searches, pattern matching: `create_research.md:114,160`, `create_design.md:120,154`, `create_execution.md:143`, `validate_execution.md:97,131`, `create_mockup.md:58,74,91,106,125`, `create_product_research.md:140,194`
- `sonnet` — analysis, integration, test design: `create_research.md:141`, `create_design.md:139`, `create_execution.md:101,124`, `validate_execution.md:116,149`, `create_product_research.md:169`, `create_product_research.md:423` (validator)
- `opus` — declared as a model hint in CLAUDE.md:130–135 documentation but no `model: "opus"` literal is currently spawned in any command. The `determineModel()` helper at `implement_coordinated.md:661-699` is the one place where opus is selected dynamically.

**Cross-file duplication**: the canonical "Component Locator → Implementation Analyzer → Pattern Finder" trio appears nearly verbatim in `create_research.md:97-161` and `create_product_research.md:122-195`; the product variant swaps `codebase-analyzer` for `product-behavior-analyzer` but keeps the same skeleton. Estimated shared boilerplate ~6,000 chars / ~1,350 tokens between those two files alone.

Each Task() prompt body follows a fixed 4-section structure: lead sentence → `Find:` / `Analyze:` bulleted list → `CRITICAL INSTRUCTIONS:` block → closing `DO NOT write any files. Return your findings as a report.` Per-block boilerplate (instruction header + closer) is ~150 chars × 22 blocks ≈ 3,300 chars / ~750 tokens repeated.

### 7. "Sub-Agents Are Read-Only" Preamble

**Location**: 5 commands

**What exists**:

- [`commands/create_research.md:83`](commands/create_research.md) — `**CRITICAL: Sub-agents are READ-ONLY. They gather information and return findings. They do NOT write files. YOU (the main agent) will write research.md after synthesizing their findings.**`
- [`commands/create_design.md:98`](commands/create_design.md) — same, file = `design.md`
- [`commands/create_execution.md:76`](commands/create_execution.md) — same, file = `tasks.md`
- [`commands/create_product_research.md:110`](commands/create_product_research.md) — variant: "as reports", file = `product-research.md`
- [`commands/validate_execution.md:76`](commands/validate_execution.md) — variant: "Sub-agents gather information..." (drops "READ-ONLY")

Per-instance ~220 chars / ~50 tokens; total ~1,100 chars / ~250 tokens.

### 8. "Document What IS" Slogan and "DO NOT" List

**Location**: appears as a section header + 5-bullet list, and standalone as a slogan

**What exists**:

The `## CRITICAL: YOUR ONLY JOB IS TO DOCUMENT THE CODEBASE AS IT EXISTS` header + 5-bullet `DO NOT` list:

```
- **DO NOT** suggest improvements or changes unless explicitly asked
- **DO NOT** identify issues or problems unless explicitly asked
- **DO NOT** propose enhancements or optimizations
- **DO NOT** critique the implementation or architecture
- **DO NOT** perform root cause analysis unless explicitly asked
```

Appears verbatim at:

- `commands/create_research.md:10-19`
- `commands/create_product_research.md:10-19`
- `agents/codebase-analyzer.md:9-15` (4-bullet abbreviated form)
- `agents/product-behavior-analyzer.md:9-17` (8-bullet form)
- `docs/product-research-claude-desktop.md:20-27` (portable mirror)

Total in-block bytes: ~1,800 chars / ~400 tokens of header + list across 5 files.

The standalone slogan `Document what IS, not what SHOULD BE` appears 18 times across in-scope command/agent files (7 hits in `create_research.md`, 9 in `create_product_research.md`, 2 in `agents/product-behavior-analyzer.md`); plus additional occurrences in CLAUDE.md, README.md, and docs/. Per-instance ~38 chars; in-scope total ~680 chars / ~180 tokens.

### 9. Embedded Output Templates

**Location**: every `create_*` command embeds a full markdown skeleton of the file it produces inside its prompt body

**What exists**:

- [`commands/create_research.md:216-339`](commands/create_research.md) — full `research.md` template, ~3,200 chars (frontmatter + Research Question, Summary, Detailed Findings, Architecture Documentation, Code References, Similar Implementations, Open Questions, Next Steps)
- [`commands/create_product_research.md:261-390`](commands/create_product_research.md) — full `product-research.md` template (3-layer structure), ~3,500 chars
- [`commands/create_design.md:219-344`](commands/create_design.md) — full `design.md` template, ~3,500 chars
- [`commands/create_execution.md:173-429`](commands/create_execution.md) — full `tasks.md` template, ~9,000 chars
- [`commands/create_project.md:86-381`](commands/create_project.md) — four embedded templates: README.md (86-136), research.md skeleton (140-214), design.md skeleton (218-299), tasks.md skeleton (303-381)
- [`commands/create_handoff.md:155-411`](commands/create_handoff.md) — full handoff document template, ~6,500 chars
- [`commands/create_mockup.md:228-330`](commands/create_mockup.md) — `mockup.md` template; plus `decisions.md` template (334-368), full HTML mockup boilerplate (387-454), `mockup-log.md` template (513-561)
- [`commands/validate_execution.md:205-353`](commands/validate_execution.md) — full validation report template, ~4,800 chars
- [`commands/validate_project.md:194-301`](commands/validate_project.md) — validation report template

**Aggregate**: embedded output templates total ~25,000 chars / ~5,600 tokens of literal markdown skeleton inside command prompts.

**Repeated frontmatter YAML embedding** (the same 5-line YAML block restated in many commands): ~15 instances totaling ~2,000 chars / ~450 tokens. Notable sites include `create_project.md:142,220,305` (3× in one file) and `update_status.md:207,218,239` (3× in one file).

### 10. Agent File Structure (`agents/`)

**Location**: `agents/*.md`

**What exists** — each of the six agents follows a near-identical 7-section template:

| Agent | Lines | Has "CRITICAL: YOUR ONLY JOB" block? | Sections present |
|---|---:|---|---|
| `codebase-analyzer.md` | 113 | Yes (L9-15) | role, CRITICAL, Core Responsibilities, Analysis Strategy, Output Format, Important Guidelines, What NOT to Do, REMEMBER |
| `codebase-locator.md` | 115 | No | role, Core Responsibilities, Search Strategy, Output Format, Search Techniques, Important Guidelines, What NOT to Do |
| `pattern-finder.md` | 127 | No | role, Core Responsibilities, Pattern Search Strategy, Output Format, Search Techniques, Important Guidelines, What NOT to Do |
| `product-behavior-analyzer.md` | 149 | Yes (L9-17) | role, CRITICAL, CRITICAL: EVERY CLAIM MUST BE TRACEABLE, Core Responsibilities, Analysis Strategy (4 steps), Output Format, Important Guidelines, What NOT to Do, REMEMBER |
| `research-validator.md` | 224 | No | role, Core Responsibilities, Validation Strategy (5 steps), Output Format, Determining Overall Status, Special Cases, Important Guidelines, What NOT to Do, REMEMBER |
| `task-verifier.md` | 188 | No | role, Core Responsibilities, Verification Strategy (4 steps), Output Format, Verification Checks, Failure Handling, Important Guidelines, What NOT to Do, Special Cases, Remember |

The `## What NOT to Do` section is present in 6/6 agents. The `## REMEMBER` closing section is present in 4/6 (absent from `codebase-locator.md` and `pattern-finder.md`).

### 11. Skills Structure (`skills/`)

**Location**: `skills/*/SKILL.md`

**What exists**:

| Skill | Lines | Body density / notable structure |
|---|---:|---|
| `mockup-iteration/SKILL.md` | 461 | Outlier — nearly 5× next-longest skill. Sections include Activation, Core Behavior, Iteration Workflow, Templates, Fidelity Preservation, Finalizing to Design, Quick Commands, Visual Preview, Revert and Compare, Example Interaction, Session Continuity, DO NOT |
| `review-prep/SKILL.md` | 158 | References sibling `nvim-helper.sh` |
| `research-validation/SKILL.md` | 107 | Uses "The Rule" framing with fenced ASCII rule banner (L14-16); strong purpose overlap with `agents/research-validator.md` |
| `tdd-discipline/SKILL.md` | 93 | "The Iron Law" framing (L12) + ASCII rule banner |
| `verification-before-completion/SKILL.md` | 87 | "The Iron Law" framing (L12) + ASCII rule banner; near-identical "Common Rationalizations" table format as `tdd-discipline/SKILL.md` |
| `status-sync/SKILL.md` | 59 | Beads-mode reminder skill |
| `project-structure/SKILL.md` | 34 | Shortest skill; pure rules content |

Three skills (`tdd-discipline`, `verification-before-completion`, `research-validation`) share a common framing: a single-line ASCII rule banner under "The Iron Law" / "The Rule" header. `tdd-discipline:58-66` and `verification-before-completion:42-52` use nearly identical "Common Rationalizations" tables.

### 12. Cross-File Repetition Quantified

**Location**: spans `commands/`, `agents/`, CLAUDE.md, `docs/`

**What exists** — summary table compiled from the pattern-finder agent's per-pattern measurements:

| Repeated pattern | Files containing | Per-instance ~chars | Total ~chars | Total ~tokens |
|---|---:|---:|---:|---:|
| Embedded output templates (research.md, design.md, tasks.md, validation-report, product-research.md, handoff) | 9 commands | varies (3,200–9,000) | ~25,000 | ~5,600 |
| `Task({...})` JS-pseudocode blocks | 22 blocks across 6 commands | ~540 avg | ~12,000 | ~2,700 |
| BARRIER lines (inline) | 49+ in 14 commands | ~100 | ~5,000 | ~1,150 |
| End-of-file Synchronization Points recap | 9 commands | ~500 | ~4,500 | ~1,000 |
| Initial Response boilerplate | 14 commands | ~400 | ~5,000 | ~1,100 |
| Frontmatter YAML re-embedding | 15+ instances | ~130 | ~2,000 | ~450 |
| `CRITICAL: YOUR ONLY JOB` header + 5-bullet DO-NOT list | 5 files | ~360 | ~1,800 | ~400 |
| `Sub-agents are READ-ONLY` preamble | 5 files | ~220 | ~1,100 | ~250 |
| `Confirm Completion` summary template | 4 create_* commands | ~900 | ~3,600 | ~800 |
| `"DO NOT write any files. Return..."` closing | 16 inline | ~63 | ~1,000 | ~225 |
| `Document what IS, not what SHOULD BE` slogan | 18 in-scope hits | ~38 | ~680 | ~180 |
| `think deeply` / `ultrathink` directives | ~20 across commands | ~40 | ~800 | ~180 |

**Strongest cross-file duplicate pair**: `commands/create_research.md` ↔ `commands/create_product_research.md` are explicitly described in commit `cb693fb` as "near-mirror" siblings. Shared near-verbatim regions (identical CRITICAL header, identical DO-NOT list, identical Initial Response, identical BARRIER 1 and BARRIER 3 wording, identical 7-bullet "CRITICAL Agent Instructions" block, identical Documentation Philosophy section, identical Synchronization Points recap) total ~6,000 chars / ~1,350 tokens of overlap between just those two files.

### 13. Reference Material Not Currently Loaded

**Location**: `docs/`

**What exists** — none of the 5 files in `docs/` are auto-loaded into the agent context. They are referenced only when a command explicitly reads them or when a user opens them.

| File | Bytes | ~Tokens | Inbound markdown links |
|---|---:|---:|---:|
| `docs/commands-reference.md` | 22,249 | 5,562 | 2 (CLAUDE.md, README.md) |
| `docs/claude-code-skills-guide.md` | 21,525 | 5,381 | **0 (orphan)** |
| `docs/workbench-workflow-guide.md` | 19,532 | 4,883 | 1 (README.md) |
| `docs/product-research-claude-desktop.md` | 16,759 | 4,190 | **0 (orphan)** — portable mirror of `commands/create_product_research.md` |
| `docs/beads-integration-learnings.md` | 7,775 | 1,944 | 1 (self-reference) |

### 14. Beads Integration Boilerplate

**Location**: 7 commands and CLAUDE.md

**What exists** — the same beads-mode detection block (`if [ "$BEADS_MODE" = "stealth" ]; then ... fi`) is restated with minor wording variations at:

- `commands/create_execution.md:449-460`
- `commands/implement_tasks.md:154-163`
- `commands/create_handoff.md:118-134`
- `commands/resume_handoff.md:73-87`
- `commands/implement_coordinated.md:155-164`
- `commands/update_status.md:51-57`
- `commands/validate_project.md:135-157`

The same `bd ready` / `bd update` / `bd close` quick-reference block is also reproduced in `CLAUDE.md:201-208`, `commands/create_execution.md:629-636`, `commands/implement_tasks.md`, `commands/implement_coordinated.md`, and `commands/help.md:86-92`. The assertion "Beads is source of truth, markdown is documentation" is restated at `implement_tasks.md:236-237,667`, `create_execution.md:637`, `update_status.md:117,375-377`, `validate_project.md:505`.

A nearly identical Beads Tracking frontmatter spec (`beads_epic`, `beads_phases`, `beads_tasks`) is embedded in `create_execution.md:586-605`, `implement_tasks.md:174-185`, `implement_coordinated.md:170-178`.

### 15. Example Project Paths and Dates

**Location**: `## Initial Response` blocks in all commands

**What exists** — a single example path is reused across 13+ commands:

- `docs/plans/2025-01-08-auth/` or `docs/plans/2025-01-08-my-project/` — appears in `create_research.md:25,37`, `create_product_research.md:35,47`, `create_design.md:24,33`, `create_execution.md:14,23`, `validate_execution.md:26,35`, `validate_project.md:14,22`, `create_project.md:77-78`, `create_handoff.md:24,32`, `create_mockup.md:22`, `implement_tasks.md:14,28`, `implement_coordinated.md:34,48`, `update_status.md:23,34`, `resume_handoff.md:23`.
- Second dated example `docs/plans/2025-10-07-my-project/` appears in `create_research.md:428`, `create_product_research.md:531`, `update_status.md:499`, `validate_project.md:520`.

### 16. Handoff Command Structure (`create_handoff.md` / `resume_handoff.md`)

**Location**: `commands/create_handoff.md`, `commands/resume_handoff.md`

**What exists** (facts only):

- `create_handoff.md` embeds a single ~6,500-char output template at
  `:155-411`. The template is seeded with concrete sample values rather than
  abstract placeholders, e.g. `Modified src/component.ts:45-67` (`:205`),
  `npm test (45/45 pass)` (`:216`), `Updated config/settings.json:12` (`:208`),
  `+[additions] -[deletions]` (`:398`).
- The command has one barrier — BARRIER 1 "Read ALL project docs AND review
  conversation history" (`:42`). There is no pre-write placeholder/grounding
  barrier equivalent to `create_research.md:341` (BARRIER 3).
- Step 1 instructs "Review conversation history to capture recent changes,
  problems, decisions" (`:59-64`) as a primary source.
- The template contains ~15 major sections, several with multi-field numbered
  sub-structures: Current State, Work Completed, Critical Learnings, Problems
  Solved, Decisions Made, Active + Resolved Blockers, Deviations, Edge Cases,
  Technical Debt, Uncommitted Changes, Next Steps, Mockup State, Artifacts,
  Session Metadata, Handoff Verification.
- Session Metadata (`:391-398`) requests session duration, lines changed
  (+/-), tests written, and model used. "Overall Progress: [X]% complete"
  appears at `:176`. No "omit if unknown" path is given for these fields.
- The "Handoff Verification" checklist (`:400-407`) is addressed to the agent
  resuming the work, not to the author before writing.
- A "Don't Include" guidance list exists at `:461-465`.

### 17. Native Claude Code Capabilities Overlapping the wb Flow

**Location**: external (Claude Code platform features); inventory gathered via
web research, cited below.

**What exists** (per cited Anthropic/Claude Code docs):

- **Session resume / branch / transcripts** — `--resume` / `--continue` /
  `/resume` restore prior session message history incl. tool results, per
  project dir. <https://code.claude.com/docs/en/sessions>
- **Auto-compaction + `/compact`** — server-side summarization preserving
  decisions, unresolved bugs, and recently-accessed files.
  <https://code.claude.com/docs/en/context-window>
- **Checkpointing / `/rewind`** — auto-saves code+conversation before changes;
  "Summarize from here" option; Bash-tool edits are NOT checkpointed.
  <https://code.claude.com/docs/en/agent-sdk/file-checkpointing>
- **CLAUDE.md auto-load** — loaded every session, survives compaction
  (re-read from disk). <https://code.claude.com/docs/en/memory>
- **Auto memory** (`MEMORY.md` + topic files) — Claude writes its own notes to
  `~/.claude/projects/<project>/memory/`; machine-local, shared across
  worktrees, not git-shared. <https://code.claude.com/docs/en/memory>
- **Baseline (Anthropic-shipped) skills present in-session**: `init`
  (generate/maintain CLAUDE.md), `review`, `security-review`. The repo-local
  `review-*`, `tdd-discipline`, `status-sync`, `verification-before-completion`
  are project/user skills, not baseline.
- **Boundary fact**: transcripts, compaction, checkpoints, and auto memory are
  all machine-local; only git-tracked CLAUDE.md and a committed doc transfer
  across hosts/agents.

## Architecture Documentation

**Current patterns found**:

- **Documentarian invariant**: every research/analysis-spawning command opens with a "document what IS, not what SHOULD BE" declaration and propagates it into every spawned agent's prompt. Examples: `create_research.md:10-19`, `create_product_research.md:10-19`, embedded into Task() prompts at `create_research.md:130-136` and `create_product_research.md:155-162`.
- **Sequential barrier protocol**: commands declare 2–5 inline `⛔⛔⛔ BARRIER N` synchronization points and then restate them as a `## Synchronization Points` recap at end of file. Example pairs: `create_research.md:50,195,341` (inline) ↔ `create_research.md:416-420` (recap); `create_design.md:60,157,346` (inline) ↔ `create_design.md:468-475` (recap).
- **Parallel-agents-then-synthesize pipeline**: 6 commands spawn 3–5 parallel Task() agents with explicit `subagent_type` and `model` keys, wait at BARRIER 2 for all to return, then synthesize. The "Component Locator → Implementation Analyzer → Pattern Finder" triple is the canonical instance.
- **Model-hint tiering**: documented in `CLAUDE.md:130-135` as haiku/sonnet/opus tiers. Concrete usage in commands maps to: file search/pattern → `haiku`; analysis/integration/test → `sonnet`; opus is currently selected only by `implement_coordinated.md:661-699`'s `determineModel()` helper, never via static `model: "opus"` in a Task() literal.
- **Output-template embedding**: each `create_*` command embeds the literal markdown skeleton of the file it writes, with `[placeholder]` tokens. Example: `create_research.md:216-339` embeds the full research.md skeleton this very file was generated from.
- **Beads-mode bash conditional**: 7 commands include a near-identical `if [ "$BEADS_MODE" = "stealth" ]` block with command-specific tail logic.

**Component connections**:

- Slash commands (`commands/*.md`) → spawn agents (`agents/*.md`) via `Task({ subagent_type, model })` blocks. Each command file lists the canonical agents it will dispatch in a "Parallel Research Strategy" preamble.
- `commands/*.md` → reference `docs/commands-reference.md` and `docs/workbench-workflow-guide.md` but never read them at runtime.
- `CLAUDE.md` → auto-loaded; declares the documentarian principles that command files restate verbatim.
- `skills/*/SKILL.md` → auto-activated based on `description:` keyword match (and explicit `triggers:` in `mockup-iteration/`); operate independently of commands.

**Conventions observed**:

- Commands are named `commands/<verb_noun>.md`; agents are named `agents/<role>.md`; skills live under `skills/<kebab-name>/SKILL.md`.
- Frontmatter for commands uses only `description` + `argument-hint`.
- Frontmatter for agents uses `name`, `description`, `tools` — no `model`.
- BARRIER markers are formatted as `**⛔⛔⛔ BARRIER N: STOP! ... ⛔⛔⛔**` (with two visually distinct variants: triple-emoji inline and single-emoji recap).
- The `## What NOT to Do` section appears in every agent file (6/6).

## Code References

Quick reference list (all paths absolute under `/Users/scraig/conductor/workspaces/prompts/karachi-v1/`):

- `commands/implement_coordinated.md:1-808` — largest command (23.8 KB); contains the `determineModel()` JS helper at lines 661-699 that dynamically picks haiku/sonnet/opus
- `commands/create_execution.md:173-429` — largest single embedded template (~9,000 chars `tasks.md` skeleton)
- `commands/create_research.md:97-161` — canonical 3-agent Task() block
- `commands/create_product_research.md:122-195` — near-mirror of `create_research.md:97-161`
- `commands/create_research.md:10-19` — canonical "CRITICAL: YOUR ONLY JOB" + DO-NOT list
- `commands/create_research.md:50,195,341` — canonical 3-barrier scaffolding
- `commands/create_research.md:416-420` — end-of-file Synchronization Points recap
- `commands/create_research.md:185-193` — canonical 7-bullet "CRITICAL Agent Instructions" block
- `agents/codebase-analyzer.md:1-113` — canonical agent file structure
- `agents/research-validator.md:1-224` — longest agent file
- `CLAUDE.md:107-135` — Core Command Philosophy + Agent Spawning model-hint documentation
- `CLAUDE.md:118-122` — prose frontmatter spec
- `docs/commands-reference.md`, `docs/claude-code-skills-guide.md`, `docs/workbench-workflow-guide.md` — reference docs not auto-loaded
- `hooks/setup-beads-mode.sh:1-13` — SessionStart hook (non-prompt)

## Similar Implementations

The codebase already contains a precedent for prompt-density reduction in the form of skills that use a **single-line ASCII rule banner** instead of long prose preambles. This pattern exists at:

- `skills/tdd-discipline/SKILL.md:12-16` — `## The Iron Law` header followed by:

  ```
  NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
  ```

- `skills/verification-before-completion/SKILL.md:12-16` — `## The Iron Law` header followed by:

  ```
  NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
  ```

- `skills/research-validation/SKILL.md:15-21` — `## The Rule` header with a similar banner

These three skills replace what would otherwise be a multi-paragraph principle declaration with a single declarative line. The same is structurally true of the agent `## REMEMBER` closing sections (`codebase-analyzer.md:110`, `product-behavior-analyzer.md:147`, etc.), which condense the documentarian principle into one closing line.

A second precedent for compactness: `skills/project-structure/SKILL.md` is 34 lines total and still encodes a full rule set (research-vs-design-vs-tasks separation) — the shortest skill in the repo.

## Open Questions

Open questions raised by this research that may need resolution before `/wb:create_design`:

- **OPUS-1**: Does "Opus 4.8" refer to a specific upcoming model version, or is the user asking about current-generation Opus (4.7) capabilities?
  - **Resolved 2026-05-31**: Opus 4.8 is a real, shipped model — the agent running this research is now Opus 4.8. The 4.7 generation (which produced the original research) was unaware of 4.8. Optimization should target current Opus 4.8 capabilities.
- **OPUS-2**: Is the optimization target (a) reducing token cost, (b) reducing latency, (c) improving model adherence, or (d) some combination?
  - **Resolved 2026-05-31**: Token cost is the bigger priority — BUT reduction must not reduce the quality or reliability of the final output. The current prompts are valued for being highly predictable and for feeding cleanly into each other; that property must be preserved.
- **OPUS-3**: Are reference docs (`docs/commands-reference.md`, etc.) intended to be human-facing only, or should commands be able to read them at runtime? Blocks: any design decision about deduplicating command-body content into reference docs.
  - **Resolved 2026-05-31**: Hybrid. The always-needed critical path (barriers, documentarian rules, the output template a command is about to write) stays INLINE in the command body — inlining is cheaper on both tokens and latency for content loaded every invocation. Only conditional content (e.g., the beads-stealth block) or explanatory/non-critical material may move to runtime-read reference docs, where the token win is real because the content isn't always loaded. Rationale: a runtime `Read` adds a tool round-trip (latency) plus overhead tokens and still pays full content cost once loaded, so it only pays off for conditionally-needed content. Shrinking the source repo via dedup is a maintenance benefit, not a per-invocation token benefit.
- **OPUS-4**: Is the verbatim duplication between `create_research.md` and `create_product_research.md` (~1,350 tokens of near-identical text) intentional for portability/Claude Desktop reasons, or is consolidation acceptable? Commit `cb693fb` framing ("near-mirror") suggests intentional, but explicit confirmation is needed before design.
  - **Resolved 2026-05-31**: Consolidation IS on the table. The design phase may factor shared structure between the two commands — subject to the hybrid rule from OPUS-3 (both commands must remain self-contained on their always-needed critical path). Note the portable Claude Desktop mirror (`docs/product-research-claude-desktop.md`) must still function standalone, so any factored block cannot live only in a runtime-read doc the portable prompt can't reach.
- **OPUS-5**: Are the orphan docs (`docs/claude-code-skills-guide.md`, `docs/product-research-claude-desktop.md`) still in active use, or can they be removed from the optimization scope? Blocks: scope clarity in design.
  - **Resolved 2026-05-31**: Out of scope. Both orphan docs are left untouched. The optimization targets only `commands/`, `agents/`, and `skills/`.

*(Beads is not initialized for this research at this stage — questions are listed here for resolution via `/wb:resolve_questions` or follow-up.)*

_All open questions resolved as of 2026-05-31._

## Next Steps

Based on the research findings:

1. **Resolve OPUS-1 through OPUS-5** with the user — particularly the optimization target (token cost vs latency vs model adherence) and whether `create_product_research.md` ↔ `create_research.md` consolidation is on the table.
2. Review this research document.
3. Run `/wb:create_design` to make explicit decisions about which of the documented patterns to keep, restructure, or factor out.
