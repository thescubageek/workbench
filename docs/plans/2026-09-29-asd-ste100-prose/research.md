---
project: asd-ste100-prose
ticket: null
created: 2026-09-29
created_timestamp: 2026-09-29T17:35:59Z
status: complete
last_updated: 2026-09-29
last_updated_note: "Refreshed after fast-forward to wb 2.1.1 (4b32306): lint-hook behaviour, line refs, versions, test scripts"
researcher: scraig
git_commit: 4b32306
git_branch: wb-2.2.0/asd_ste100_prose
repository: thescubageek/workbench
tags: [research, codebase, asd-ste100-prose]
---

# Research: asd-ste100-prose

**Created**: 2026-09-29
**Last Updated**: 2026-09-29
**Ticket**: N/A

## Research Question

> I want to force the entire workbench to use ASD-STE100 to cut back on AI-slop prose and make
> it easier to understand without compromising quality. This would be a 2.2.0 release that
> precedes the WIP with 3.0.0.

Broken into five areas:

1. Which prose the plugin ships, and which prose it causes to be generated.
2. Which writing rules exist today, and how (or whether) they are enforced.
3. Which existing mechanisms apply one rule across many skills.
4. How the current prose measures against the ASD-STE100 numeric limits, and what the standard
   itself says (issue, rules, licence, tools).
5. How a 2.2.0 on `main` relates to the 3.0.0 work in progress.

## Summary

The plugin ships about 46,000 words of prose in 123 markdown files under `plugin/`: 36 skills,
77 supporting files (41 of them templates that shape generated documents and chat output),
7 agent definitions and 2 shipped reference docs. There are also a SessionStart/PreCompact hook
that prints an orientation block and 36 + 7 frontmatter `description:` fields that the harness
uses to select skills. Maintainer prose outside `plugin/` (README, CLAUDE.md, CHANGELOG, `docs/`,
`.claude/wb/knowledge.md`) adds about 13,700 words. Nothing in the repository mentions
ASD-STE100 or Simplified Technical English.

The writing rules that exist are instructions to the model, not checks. The set is: the
"Output discipline" sentence repeated in 14 skills plus `CLAUDE.md` and a README opt-in; the
`CLAUDE.md` rule that a barrier marker states its reason; "Use clear, unambiguous language";
the Documentarian Rule; and audience-specific plain-language rules in `eli5-clip` and the
product-research surfaces. The only automated text check is `markdownlint`, which runs through
a PostToolUse hook. It has line length off and has no rule about wording. None of the
validators (`validate_project`, `research-validator`, `task-verifier`) look at prose style.
`main` has no CI. The plugin has three ways to apply one rule across skills: a shipped reference
doc that skills link to (`branch-naming.md`, 4 consumers), a skill that other skills delegate to
(`model-help`, 7 consumers), and a sentence copied into each skill (Output discipline, 14
consumers).

Measured against the STE numeric limits, 10.4% of shipped sentences have more than 20 words
and 5.5% have more than 25. No paragraph has more than 6 sentences. Shipped prose has 17.35
em-dashes and 5.64 semicolons per 1,000 words (STE Rule 8.1 prohibits semicolons). ASD-STE100
Issue 9 (2025-01-15) is current, and Issue 10 is scheduled for January 2028. The standard is
free to obtain, but ASD owns the copyright and prohibits reproduction or redistribution without
written permission. "ASD-STE100 Simplified Technical English" is a registered EU trade mark.
The 3.0.0 work lives on `adversarial-loop-skill-research`. That branch already contains 2.1.0,
was once numbered 2.2.0, modifies 48 of the 130 `plugin/` files on `origin/main`, and adds CI
plus a `check` runner. `main` has no CHANGELOG entry for 2.1.0; the 3.0.0 branch carries a
reconstructed one.

## Detailed Findings

### 1. Prose surfaces the plugin ships

**Location**: `plugin/`

**What exists**:

- **Skills**: 36 directories under `plugin/skills/`, each with a `SKILL.md`. Pipeline stages are
  `snake_case` (`create_research`, `implement_inline`); background and utility skills are
  `kebab-case` (`tdd-discipline`, `eli5-clip`). Three are deprecated alias stubs with
  `disable-model-invocation: true` and a description ending "(removed at 3.0.0)":
  `create_execution`, `implement_tasks`, `implement_coordinated`.
- **Supporting files**: 77 other markdown files under `plugin/skills/`. `git ls-files plugin`
  lists 41 paths under a `templates/` directory or named `templates.md`/`*-template.md`. The
  naming convention says what each one produces:
  - `*-template.md` produces a document, for example
    `create_project/templates/research-md-template.md` or
    `create_tasks/templates/tasks-md-template.md`.
  - `*-message.md`, `*-report.md` and `*-request.md` produce chat output, for example
    `create_tasks/templates/plan-presentation-message.md` or
    `implement/templates/phase-completion-report.md`.
  - `*-fragment.md` produces part of an output, for example
    `implement/templates/modified-files-fragment.md`.
  - Other supporting files are `reference.md`, `sub-agent-prompts.md`, `examples.md`,
    `reference/<topic>.md` (`update_status`, `validate_project`) and `prompts/` (`implement`:
    worker, escalation-worker and verifier prompts).
- **Agents**: 7 files in `plugin/agents/`: `codebase-analyzer`, `codebase-locator`,
  `pattern-finder`, `product-behavior-analyzer`, `research-validator`, `task-verifier`,
  `task-worker`. Their bodies are second-person system prompts ("You are a specialist at …").
- **Shipped reference docs**: `plugin/docs/reference/README.md` and `branch-naming.md`.
- **Hook output**: `plugin/hooks/wb-prime.sh` (200 lines) prints a static orientation block
  (`cat <<'ORIENTATION'` at line 27) and state lines on SessionStart and PreCompact.
  `.claude/wb/PRIME.md` in the cwd replaces the static block (comment at line 22).
- **Script output**: `plugin/scripts/lint`, `lint-hook` and `quiet` print status lines to the
  model (see §3).
- **Frontmatter descriptions**: every skill and agent has a `description:` field. The harness
  uses it to decide when to invoke the skill. The maintainer guide gives the formula
  "[What it does] + [When to use] + [Trigger terms]" (`docs/claude-code-skills-guide.md:96`).
- **Maintainer prose (not shipped)**: `README.md`, `CLAUDE.md`, `CHANGELOG.md`,
  `docs/claude-code-skills-guide.md`, `docs/commands-reference.md`,
  `docs/workbench-workflow-guide.md`, `docs/product-research-claude-desktop.md`,
  `.claude/wb/knowledge.md`, `plugin/scripts/README.md`.

**Two kinds of reader**: the files under `plugin/` are instructions that a model reads at
runtime. The templates and message files set the shape of the text that users read: plan
documents, chat summaries, handoffs and reports. Commit-message wording is set in skill text,
for example `implement/SKILL.md:310-311` ("one task, one commit, with the task ID in the
message") and the WIP form at line 352.

### 2. Writing rules that exist today

**What exists**: all of these are instructions in prose. None is checked mechanically.

| Rule | Where | Text (abridged) |
| ---- | ----- | --------------- |
| Output discipline (global) | `CLAUDE.md:9-17` | "keep narration minimal — the artifact is the deliverable"; act on barriers silently; no reproducing document contents; surface only blockers, decisions, errors |
| Output discipline (inline) | 14 `SKILL.md` files, e.g. `validate_project/SKILL.md:22` | "act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary." |
| Output discipline (end-user opt-in) | `README.md:235-246` | a snippet for the user's own `CLAUDE.md`; "The plugin cannot (and does not) write to your personal config" |
| Barrier markers state a reason | `CLAUDE.md:172-175`, `:219-220` | "state the reason in the marker"; "state the reason in a plain sentence" |
| No thinking-depth instructions | `CLAUDE.md:221-222` | "do not instruct the model how hard to think" |
| Clear language | `CLAUDE.md:232` | "Use clear, unambiguous language" |
| Documentarian Rule | `create_research/SKILL.md:23-31`, `create_product_research` same lines | fenced `DOCUMENT WHAT EXISTS — NEVER SUGGEST, CRITIQUE, OR IMPROVE` |
| Plain language for a non-technical reader | `eli5-clip/SKILL.md:14-25` | "No jargon, no internals"; "Short sentences, short paragraphs"; "Lead with the outcome"; "Paste-ready plain text" |
| Plain language for product research | `agents/product-behavior-analyzer.md:40,132-143`; `create_product_research/reference.md:14,54` | "Use plain language — no jargon unless it's a product term users see"; "Write for a product manager" |
| Sentence-count shapes | `explore_design/SKILL.md:97`, `forge/SKILL.md:99`, `model-help/SKILL.md:146`, `resolve_questions/SKILL.md:114,134,198` | "State the decision in one sentence"; "1–2 sentences"; "~2–4 sentences" |

Skills without the inline Output discipline line include `implement`, `resolve_questions`,
`jira-context`, `help`, the three alias stubs and the background skills. `CLAUDE.md` says
`implement` delegates to `model-help`, but `implement/SKILL.md` has no gate-check paragraph.
Its only `model-help` mention is at line 260.

The user-level "Code Comments" rule ("Default to NO comment") is in
`~/.claude/CLAUDE.md` only. No copy of it exists in the repository.

### 3. How text is checked today

**Location**: `plugin/scripts/`, `.markdownlintrc`, `plugin/.claude-plugin/plugin.json`

**How it works**:

1. `plugin.json` registers `scripts/lint-hook` as PostToolUse on `Write`, `Edit` and `Bash`,
   each with `timeout: 5` (the `hooks` block starts at line 15). SessionStart and PreCompact
   run `hooks/wb-prime.sh`. There is no separate `hooks.json`.
2. `lint-hook` reads the tool payload. `WB_LINT_HOOK=0` turns it off (line 11). For a Write or
   Edit `.md` path that `wb_lint_ignored` does not exclude, it calls `lint_one` (lines 33-36):
   `lint --fix <file> 2>&1 | grep -E "(✓|✅|⚠️|Clean|Fixed)" | head -3`. For Bash, it looks at
   `.md` paths named in the command that were modified in the last minute, and only reports
   (`lint_report`, lines 40-42) unless `WB_LINT_FIX_ON_BASH=1`. It always exits 0, so it never
   blocks. (2.1.1 changed the Bash route from fix to report-only.)
3. `lint` calls the `markdownlint` binary (`markdownlint-cli`). If the binary is missing it
   prints install hints and exits 1 (line 83 on). It exits 1 when any file still has findings,
   also after `--fix`. `plugin/scripts/lint-common.sh` holds `wb_lint_ignored()`, the shared
   path-exclusion test (`vendor/`, `node_modules/`, `.git/`, `.context/`, `tmp/`, `.next/`,
   `dist/`, `build/` at any depth, plus `.wblintignore` / `.markdownlintignore`; not
   `.gitignore`).
4. `.markdownlintrc` enables the defaults and turns off `MD013` (line length), `MD033`,
   `MD036`, `MD040`, `MD041` and `MD060`. No rule looks at wording, sentence length or
   vocabulary.
5. The model sees at most the `🔍 Linting markdown:` line plus three marker lines.

**Validators**: `validate_project` checks structure, frontmatter, task-ID shape, counters,
status agreement, Q/A/PD records and cross-file metadata. Its content check looks for literal
placeholders (`[To be added]`, `[TBD]`, `[TODO]`) and sections under 50 characters.
`research-validator` checks paths, snippets, behaviours and patterns against the code.
`task-verifier` checks tests and scope. None checks prose style.

**CI and dependencies on `main`**: no `.github/` directory, no `package.json`. The test scripts
are `plugin/scripts/test-quiet` (tests `quiet`) and `plugin/scripts/test-lint` (contract tests
for `lint` and `lint-hook`, added in 2.1.1). Neither tests skill behaviour or wording.

### 4. Mechanisms that apply one rule across many skills

| Mechanism | Authority | How a consumer refers to it | Consumers |
| --------- | --------- | --------------------------- | --------- |
| Shipped reference doc | `plugin/docs/reference/branch-naming.md` ("the plugin's single authority … Skills link here rather than restating it", lines 3-4) | a manifest bullet naming the other consumers, plus "Read [link] NOW and apply it" at the step, followed by that step's own inputs (`create_project/SKILL.md:16-17,104`) | 4: `create_project`, `jira-context`, `forge`, `implement` |
| Delegate skill | `plugin/skills/model-help/SKILL.md` gate mode (lines 87-137; scope limit at 105) | the same bold `**Model & effort (gate check)**` paragraph, with one phase-specific sentence changed (`create_research/SKILL.md:36`) | 7: 5 by the paragraph (`create_design`, `create_research`, `create_tasks`, `implement_inline`, `validate_execution`), plus `resume_handoff` and `forge` |
| Copied sentence | none; the sentence is the rule | the same sentence in each file, no link | 14 skills, plus `CLAUDE.md:9-17` and `README.md:235-246` |

**Admission test for `plugin/docs/reference/`** (`plugin/docs/reference/README.md:8-17`): a
doc belongs there only if more than one skill needs it, a skill step reads it at runtime, it
states a rule or contract rather than a narrative, and linking beats restating. The same file
(lines 43-47) says a shipped skill may link only into `plugin/docs/reference/`, and that root
`docs/` is never a runtime rules source. `CLAUDE.md` restates this under "Where rules may live".

**Background skills**: `tdd-discipline`, `doc-adherence`, `verification-before-completion`,
`status-sync`, `project-structure` and `mockup-iteration` have `user-invocable: false`. Their
descriptions start with a trigger ("Use when about to claim work is complete …"). The
discipline skills share one body shape: an Iron Law in a fence, a Gate list, a "Common
Rationalizations" table and "Red Flags - STOP". `task-worker.md` preloads one of them through
`skills: [tdd-discipline]`. `doc-adherence/SKILL.md:63-69` says deterministic boundary signals
belong in `hooks/wb-prime.sh`, because skill text does not survive compaction.

**Precedent for a cross-cutting release**: 2.1.0 (commit `46ef587`, tag `wb--v2.1.0`)
introduced `branch-naming.md` and changed 10 files, +216/−33: the new reference doc, five
consuming skills, `CLAUDE.md` and the two manifests.

### 5. Current prose measured against STE limits

**Method**: a script (`/tmp/prose/measure.py`, not in the repo) processed 131 tracked `.md`
files, excluding `docs/plans/`. It removed frontmatter, fenced code, inline code, tables,
headings, HTML comments and URLs. It counted list items as sentences and split sentences on
terminal punctuation followed by an uppercase letter. Limitations: bold lead-ins ("**One
task.**") split off as short fragments (248 of 6,000, 4.1%), which lowers the mean. Colons and
semicolons do not split sentences. The passive check is a heuristic (a form of "be" followed by
`-ed`/`-en`). STE Rules 8.5–8.7 count identifiers and parenthetical text as one word each, and
the script does not.

| Scope | Files | Words | Sentences | Median words | >20 words | >25 words | >40 words | Paras >6 sentences |
| ----- | ----- | ----- | --------- | ------------ | --------- | --------- | --------- | ------------------ |
| `plugin/skills/**/SKILL.md` | 36 | 31,658 | 2,935 | 9 | 11.7% | 6.0% | 10 | 0 of 744 |
| skill supporting files | 77 | 9,298 | 999 | 7 | 8.2% | 4.2% | 3 | 0 of 247 |
| `plugin/agents/` | 7 | 3,787 | 431 | 7 | 6.5% | 4.6% | 1 | 0 of 68 |
| `plugin/docs/reference/` | 2 | 875 | 70 | 10 | 14.3% | 8.6% | 1 | 0 of 13 |
| **Shipped total** (incl. `plugin/scripts/README.md`) | 123 | 45,935 | 4,476 | 8 | 10.4% | 5.5% | 15 | 0 |
| Maintainer (README, CLAUDE, CHANGELOG, `docs/`, knowledge) | 8 | 13,745 | 1,524 | 7 | 10.2% | 5.3% | 5 | 0 |

| Scope | Em-dashes / 1k words | Semicolons / 1k words | ALL-CAPS emphasis tokens | Passive (heuristic) / 1k words |
| ----- | -------------------- | --------------------- | ------------------------ | ------------------------------ |
| Shipped | 17.35 (797) | 5.64 (259) | 123 | 7.34 |
| Maintainer | 14.11 (194) | 4.73 (65) | 21 | 8.51 |

- Files with the highest share of sentences over 25 words (at least 20 sentences each):
  `.claude/wb/knowledge.md` 25.0%, `plugin/agents/task-worker.md` 17.9%, `CHANGELOG.md` 16.5%,
  `plugin/skills/model-help/SKILL.md` 16.3%, `plugin/skills/jira-context/SKILL.md` 15.6%.
- Templates have the highest em-dash density: 46.83 per 1,000 words in `templates/` files.
- ALL-CAPS emphasis in shipped prose: NEVER 37, STOP 29, MUST 17, DO NOT 16, ALWAYS 11,
  CRITICAL 8, IMPORTANT 5. The agents and the reference docs have none.
- Two barrier styles are in use. One uses sirens and STOP, for example
  `create_research/SKILL.md:101`:
  `**⛔⛔⛔ BARRIER 1: STOP! Do NOT proceed to Step 2 until ALL mentioned files are FULLY read ⛔⛔⛔**`
  (23 siren uses in 11 files). The other puts the reason in the marker, which is the form
  `CLAUDE.md:172-177` specifies.
- The phrase "Read [link] NOW" appears 56 times in 22 files. "Never paraphrase from memory"
  appears in 16 files.
- Sample sentence over 40 words, `plugin/agents/task-verifier.md` (63 words): "A failure the
  task did not cause — a test that was already red before the worker started, in a file the task
  never named — does not fail the task, but it is never silently absorbed either: report it under
  `### Baseline failures` with the test name and evidence that it predates the task, so the
  coordinator carries it to the checkpoint and leaves the automated-verification box `[ ]`."

### 6. ASD-STE100: facts about the standard

Sources: asd-ste100.org pages and the Issue 9 PDF (primary, marked **[P]**). Other material is
secondary (**[S]**).

- **Issue and owner [P]**: Issue 9, 2025-01-15, replaces all earlier issues. Issue 8 was
  2021-04-30. The FAQ says "The next issue 10 is scheduled for January 2028." The ASD Simplified
  Technical English Maintenance Group (STEMG) maintains it, and ASD (Brussels) "fully owns" it.
  Issue 9 calls it "an international standard", subtitled "Standard for technical
  documentation".
- **Part 1, 53 writing rules in 9 sections [P]**: Words (1.1–1.14), Multi-word nouns (2.1–2.2),
  Verbs (3.1–3.7), Sentences (4.1–4.5), Procedural writing (5.1–5.5), Descriptive writing
  (6.1–6.6), Safety instructions (7.1–7.3), Punctuation and word count (8.1–8.7), Writing
  practices (9.1–9.4, GR-1, GR-2).
- **Part 2, dictionary [P]**: 875 approved and 1,274 unapproved words. In general each approved
  word has one meaning and one part of speech ("check" is approved only as a noun). The
  dictionary contains no technical nouns or technical verbs. Issue 9 renamed "technical name"
  to **technical noun**. Rule 1.5 lists 22 technical-noun categories, and Category 19 covers
  computer science, information and communication technology. Its examples include AI,
  chatbot, database, file, interface, large language model, metadata, prompt engineering and
  token. Rule 1.12 lists 4 technical-verb categories. Rule 1.8: use the terms approved in "your
  company, industry, or subject field". Using a technical noun or verb "is the only way to use
  words that are not approved."
- **Numeric limits and key rules [P]**:

  | Rule | Limit |
  | ---- | ----- |
  | 5.1 procedural sentence | max 20 words (a sentence in a note: max 25) |
  | 6.3 descriptive sentence | max 25 words |
  | 6.6 paragraph | max 6 sentences; 6.5 one topic per paragraph |
  | 2.1 multi-word noun | max 3 words |
  | 5.2 | one instruction per sentence, unless actions are simultaneous |
  | 5.3 / 5.4 | imperative for instructions; a condition comes first, followed by a comma |
  | 3.2 / 3.4 / 3.5 | only infinitive, imperative, simple present/past/future, past participle as adjective; no perfect or progressive; "-ing" only in technical nouns |
  | 3.6 | active voice; passive in descriptive text only if the agent is unknown |
  | 4.2 / 4.5 | no omitted words or contractions; use articles when applicable |
  | 8.1 | no semicolons |
  | 8.5–8.7 | parenthetical text, identifiers, quoted text, numbers and units each count as one word |
  | 1.14 | American English spelling |

- **Scope [P]**: STE started in aerospace maintenance documentation. It says it is used in
  other industries, and also that "It is not intended for general-purpose writing". It "is
  intended to be used with other applicable specifications … style guides". It has no rules on
  abbreviations, text formatting or units.
- **Licence [P]**: "The standard is available to everyone free of charge", as a PDF. The
  copyright notice says "no reproduction or publication of it, in whole or in part, shall be
  made without the written authority of an officer of ASD". The introduction says:
  "Unauthorized distribution of ASD-STE100 … is strictly prohibited without written permission
  from the STEMG." Irrevocable reproduction rights go only to eight listed groups: ASD, AIA and
  AIAC members, ICCAIA members, their customers, member-country defence ministries, A4A,
  airworthiness authorities, and universities or research institutes for education. None of
  the eight is an open-source or general-public grant.
- **Trade mark [P]**: EU marks 004901195 (2006) and 017966390 (2018). The registered name is
  "ASD-STE100 Simplified Technical English". ASD and STEMG "do not endorse, certify, or
  authorize any software tools, including AI-based ones."
- **AI [P]**: the STEMG white paper "ASD-STE100 Simplified Technical English and Artificial
  Intelligence (AI)" (June 2026) says AI can "compromise controlled natural language
  discipline" and "introduce undetected inaccuracies". It recommends AI as support only, with
  human oversight. The downloads page warns that AI text "can appear clear, authoritative, and
  consistent with STE, even when it does not correctly apply the rules and vocabulary."
- **Tools [S]**:
  - Commercial: HyperSTE, Congree, Acrolinx/markup.ai, Boeing Simplified English Checker, and
    the TechScribe customized LanguageTool (runs locally, supports Issue 9, £400 per user per
    year).
  - Open source, all MIT and all saying they do not ship the ASD dictionary or are not
    compliance checkers: `johnsaigle/ste-lint` (Rust, 7 heuristic checks),
    `mikkovihonen/stelint` (Python/spaCy, Vale-format output, alpha), `stuffbucket/vale` (Go
    CLI plus MCP, uses the OpenSTE wordset), and the OpenSTE wordset (MIT, provenance not
    stated).
  - STE skills for LLM agents: `AminBlg/SimpleEnglish` ("reproduces no spec text or dictionary
    content"; ships an extractor for the user's own copy of the PDF),
    `danyuchn/asd-ste100-skill`, `dandye/ste-writing-style` (a three-tier dictionary).
  - STEMG says checkers cannot check all rules, for example whether a paragraph's first
    sentence is its topic sentence.
  - No peer-reviewed paper on STE for LLM prompts or AI-generated text was found.

### 7. Relationship to the 3.0.0 work in progress

**Location**: local branch `adversarial-loop-skill-research`, checked out in the worktree
`/Users/scraig/conductor/workspaces/workbench/ankara`. The local branch is 16 commits ahead of
`origin/adversarial-loop-skill-research`. The newest local commit is 2fff76c (2026-09-28).

**What exists**:

- **Ancestry**: when measured, `git merge-base origin/main adversarial-loop-skill-research` was
  `46ef587` (2.1.0), so 3.0.0 contains 2.1.0, and `git merge-tree` reported no textual
  conflicts. `origin/main` has since moved to `4b32306` (2.1.1, a lint-hook fix touching
  `plugin/scripts/`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `knowledge.md` and the
  manifests). Its CHANGELOG says "It will be absorbed into 3.0.0." The local `main` ref in this
  repository is stale at `2a6fa62` (2.0.1).
- **Version history**: the 3.0.0 branch's `CHANGELOG.md` has `## [3.0.0] — 2026-09-27` and a
  reconstructed `## [2.1.0] — 2026-09-17` entry. That entry says the gap "was found by the
  adversarial review of 3.0.0 (then numbered 2.2.0)". `main`'s `CHANGELOG.md` has no 2.1.0
  entry; its newest is `## [2.1.1] — 2026-09-29` (line 8), then `## [2.0.1]` (line 90). Tags `wb--v2.0.1` and `wb--v2.1.0`
  exist locally and on the remote.
- **Versioning rule change on 3.0.0**: its CHANGELOG preamble adds that a *major* bump applies
  also "for any change to what the plugin requires of the environment it runs in". `main`'s
  preamble defines minor as "additive skills/agents/hooks".
- **Content**:
  - New skills: `adversarial-review`, `adversarial-loop`, `reply-to-claude`.
  - New reference docs: `code-review-integration.md`, `journal-entries.md`,
    `remediation-plan.md`, `review-ledger.md`.
  - New scripts: `check`, `check-guards` (python3, own lexer, scans shell and fenced shell
    blocks, not prose), `test-guards` (114-case corpus plus mutation testing), `count`,
    `test-count`, `test-phi-patterns`, `shellcheck-gate`, `lib_mutate.py`, plus fixtures.
  - New CI: `.github/workflows/checks.yml` runs `./plugin/scripts/check` on push to `main` and
    on pull requests. It installs shellcheck and `markdownlint-cli@0.49.0`.
  - No prose or writing-style rules: no STE or style-guide text, no wording checks.
    `.markdownlintrc` and `lint-hook` are unchanged.
- **Open sub-plan**: `docs/plans/2026-09-28-guard_lexer_and_pr_identity/` on that branch is
  `status: in-progress`, 3 of 18 tasks. Its README says its fixes "land on the
  `adversarial-loop-skill-research` branch before PR #25 merges, so 3.0.0 ships with them."
- **File overlap**: `origin/main` has 130 files under `plugin/`. 3.0.0 modifies 48 of them
  (39 skill files, 3 agents, `plugin.json`, the hook and 4 scripts), leaves 82 untouched and
  adds 24. The largest prose edits are in `implement/SKILL.md` (+136/−23),
  `implement_inline/SKILL.md` (+84/−14), `verification-before-completion/SKILL.md` (+82/−4),
  `daily-digest/sources.md` (+77/−12), `help/SKILL.md` (+38/−1), `daily-digest/SKILL.md`
  (+33/−12), `validate_project` and `update_status`. Outside `plugin/`, it modifies
  `marketplace.json`, `.claude/wb/knowledge.md`, `.gitignore`, `CHANGELOG.md`, `README.md` and
  `docs/commands-reference.md`. `CLAUDE.md` is identical to `origin/main`.
- **Untouched by 3.0.0 (subset)**: agents `codebase-analyzer`, `codebase-locator`,
  `product-behavior-analyzer`, `research-validator`; both `plugin/docs/reference/` files; the
  `SKILL.md` of `clip`, `create_mockup`, `create_product_research`, `create_project`,
  `doc-adherence`, `eli5-clip`, `explore_design`, `fetch-issues`, `jira-context`,
  `mockup-iteration`, `resolve_questions`, `status-sync`, `tdd-discipline`, `tracer-bullet`;
  and most templates, `reference.md` and `sub-agent-prompts.md` files.
- **Alias removal**: the three alias stubs on `main` say "(removed at 3.0.0)". 3.0.0 modifies
  those stubs rather than deleting them (they are in the 48-file list).

### 8. Release mechanics

- `plugin/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` both carry
  `"version": "2.1.1"`, and they must match (`CLAUDE.md`, "Releasing New Commands/Skills/Agents").
- Users update with `claude plugin update wb@thescubageek-workbench`. The cache is keyed by
  version, so a text-only change needs a version bump to reach installed users.
- Tag convention: `<name>--v<version>`, created with `claude plugin tag plugin/` on a clean
  tree after the bump commit (`.claude/wb/knowledge.md`, entry on `claude plugin tag`).
- CHANGELOG shape (2.0.1, `CHANGELOG.md:90`; 2.1.1 at line 8 follows it): heading `## [x.y.z] — date`, an intro paragraph,
  then `### Fixed`, `### Changed`, `### Migration`. 2.0.0 adds `### ⚠️ Breaking`.
- Recent release commits are titled `wb 2.1.1: … (#26)`, `wb 2.1.0: … (#24)` and `wb 2.0.1: … (#22)`.
- The current branch is `wb-2.2.0/asd_ste100_prose`, which fits
  `plugin/docs/reference/branch-naming.md` (version scope, snake_case description).

## Architecture Documentation

**Current patterns found**:

- **Rules as instructions, checks as markdownlint only**: prose rules live in `CLAUDE.md` and
  skill text. The only automated check is structural markdown lint, and the hook never blocks
  (`lint-hook` ends `exit 0`).
- **Single authority plus links**: `branch-naming.md` and `model-help` each hold a rule in one
  place, with consumer skills pointing to it. `plugin/docs/reference/README.md:8-17` states
  when a rule qualifies for a reference doc.
- **Progressive disclosure**: `SKILL.md` carries control flow, and output shapes live in
  `templates/` files that a step reads "NOW"
  (`docs/claude-code-skills-guide.md`, "House conventions (wb 2.0.0)", line 326 on).
- **Filter, don't block**: `lint-hook` and `quiet` reduce output to marker lines and let work
  continue.

**Component connections**:

- Write/Edit/Bash → `plugin.json` PostToolUse → `scripts/lint-hook` → `scripts/lint --fix` →
  `markdownlint` with `.markdownlintrc` → up to 3 marker lines back to the model.
- SessionStart/PreCompact → `hooks/wb-prime.sh` → orientation text (or `.claude/wb/PRIME.md`).
- Stage skill → "Read `templates/<x>-template.md` NOW" → generated document prose.
- Stage skill → `model-help` gate mode; stage skill → `plugin/docs/reference/branch-naming.md`.

**Conventions observed**:

- Supporting files are listed in a "Supporting files in this directory (read each when its step
  directs you to — never paraphrase from memory)" manifest (15 skills).
- Em-dashes are used as the main parenthetical and separator mark. Older text uses ` - `.
- Chat-output templates use emoji markers: ✅ completion, ⛔ barrier, 📍 drift, 🌿 branch.

## Code References

- `CLAUDE.md:9-17` — global Output Discipline section
- `CLAUDE.md:172-177`, `:219-222`, `:232` — barrier-reason rule, no thinking-depth instructions, "clear, unambiguous language"
- `README.md:235-246` — Output discipline opt-in for end users
- `plugin/skills/validate_project/SKILL.md:22` — one of the 14 inline Output discipline lines
- `plugin/skills/create_research/SKILL.md:23-31` — Documentarian Rule
- `plugin/skills/create_research/SKILL.md:101` — siren-style barrier
- `plugin/skills/eli5-clip/SKILL.md:14-25` — plain-language writing rules
- `plugin/agents/product-behavior-analyzer.md:132-143` — product plain-language rules
- `plugin/.claude-plugin/plugin.json:15-57` — hook registration
- `plugin/scripts/lint:83` — markdownlint presence check
- `plugin/scripts/lint-hook:33-36`, `:40-42` — fix and report-only output filters
- `plugin/scripts/lint-common.sh` — `wb_lint_ignored()` shared exclusions
- `.markdownlintrc` — lint config, MD013 off
- `plugin/docs/reference/README.md:8-17`, `:43-47` — reference-doc admission test and linking rule
- `plugin/docs/reference/branch-naming.md:3-4` — single-authority statement
- `plugin/skills/create_project/SKILL.md:16-17`, `:104` — consumer manifest bullet and "Read … NOW and apply it"
- `plugin/skills/model-help/SKILL.md:87-137` — gate mode; `:105` scope limit
- `plugin/skills/create_research/SKILL.md:36` — model-help gate paragraph (one of 5)
- `plugin/hooks/wb-prime.sh:22`, `:27` — PRIME.md override and orientation block
- `docs/claude-code-skills-guide.md:96`, `:326` — description formula, house conventions
- `CHANGELOG.md:8` — newest entry on `main` (2.1.1)

## Similar Implementations

**Shipped single authority, `plugin/docs/reference/branch-naming.md:3-4`**:

```markdown
**Read this when a step directs you to.** It is the plugin's single authority on what the
working branch is called and when to change it. Skills link here rather than restating it.
```

Consumed by:

- `plugin/skills/create_project/SKILL.md:104` — "Read [../../docs/reference/branch-naming.md](../../docs/reference/branch-naming.md) NOW and apply it. Two inputs it needs, both already parsed in Step 1:"
- `plugin/skills/forge/SKILL.md:89-92`, `plugin/skills/implement/SKILL.md:169-174`, `plugin/skills/jira-context/SKILL.md:97-105` — same shape, each with its own inputs

**Existing writing-rule list, `plugin/skills/eli5-clip/SKILL.md:16-18`**:

```markdown
- **No jargon, no internals.** Strip branch names, file paths, commit hashes, tool names, and terms like API/FTP/301/redirect/manifest/deploy/schema. …
- **Lead with the outcome / good news.** First line says what's true now.
- **Short sentences, short paragraphs.** Assume a phone screen. A few sentences per idea, blank line between ideas.
```

**Background skill with trigger description**: `verification-before-completion`,
`doc-adherence` and `tdd-discipline` (`user-invocable: false`, "Use when about to …"),
preloadable into an agent with `skills:` as `task-worker.md` does.

## Open Questions

*All questions resolved as of 2026-09-29.*

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| Q1 | Which prose does "the entire workbench" cover: (a) model-facing instruction text in `plugin/` (skills, agents, prompts, descriptions), (b) text the workbench makes the model produce (templates, chat output, commits, PR bodies), (c) maintainer docs (README, CLAUDE.md, CHANGELOG, `docs/`), or a combination? | Design scope; which of the ~46k shipped / ~14k maintainer words are in the 2.2.0 surface | **Resolved 2026-09-29** → design.md (## Technical Decisions) |
| Q2 | ASD prohibits reproduction or redistribution of the rules text and dictionary without written permission, and the eight grant groups include no open-source case. Does this repository have, or intend to seek, that permission? If not, the plugin can only paraphrase or refer to the rules and cannot ship the 875-word dictionary. | Design of the rule source and any word-list or checker; wording of any "ASD-STE100" naming (registered trade mark) | **Resolved 2026-09-29** → design.md (## Technical Decisions) |
| Q3 | 3.0.0 modifies 48 of the 130 `plugin/` files and was itself once numbered 2.2.0. If 2.2.0 lands on `main` first, 3.0.0 must re-merge every overlapping file. Which files may 2.2.0 rewrite, and who absorbs the merge onto `adversarial-loop-skill-research`? | Task ordering and the size of the 2.2.0 rewrite | **Resolved 2026-09-29** → design.md (## Technical Decisions) |
| Q4 | How is "without compromising quality" to be shown? The repository has no measurement of skill behaviour (no evals; the test scripts cover only `quiet`, `lint` and `lint-hook`), and markdownlint does not look at wording. | Success criteria in `design.md` | **Resolved 2026-09-29** → design.md (## Technical Decisions) |
| Q5 | Does 2.2.0 add a mechanical prose check, or only rules as instructions? `main` has no CI and no Node or Python dependency beyond `markdownlint-cli`. 3.0.0's revised versioning rule treats a new environment requirement as a *major* change. | Enforcement design, and whether the change fits a minor (2.2.0) version | **Resolved 2026-09-29** → design.md (## Technical Decisions) |

## Next Steps

1. Resolve Q1–Q5 (`/wb:resolve_questions docs/plans/2026-09-29-asd-ste100-prose`). Q2 and Q3
   in particular change the size of the work.
2. Review this research document.
3. Run `/wb:create_design docs/plans/2026-09-29-asd-ste100-prose` to create design decisions.

## References

- Design: [design.md](design.md)
- Tasks: [tasks.md](tasks.md)
- ASD-STE100 Issue 9: <https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf>
- ASD-STE100 FAQ: <https://www.asd-ste100.org/STE_faq.html>
- STEMG AI white paper: <https://www.asd-ste100.org/assets/files/WhitePaper-ASD-STE100_and_AI.pdf>
- STE tools page: <https://www.asd-ste100.org/STEsoftware.html>
