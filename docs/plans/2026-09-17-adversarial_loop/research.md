---
project: adversarial_loop
ticket: null
created: 2026-09-17
created_timestamp: 2026-09-17T17:51:46Z
status: complete
last_updated: 2026-09-19
last_updated_note: "Added research on Claude Code built-in review skills, the official marketplace review plugins, and published adversarial-review patterns"
researcher: scraig
git_commit: 02e43d2513b9f6ed76006a8d5a30078b22dc1708
git_branch: adversarial-loop-skill-research
repository: thescubageek/workbench
tags: [research, codebase, adversarial_loop]
---

# Research: adversarial_loop

**Created**: 2026-09-17
**Last Updated**: 2026-09-17
**Ticket**: N/A

## Research Question

Should the `adversarial-review` and `adversarial-loop` skills that exist on this machine be
pulled into the standard workbench plugin? What other skills would have to come with them,
that are not currently included, for them to work? They are meant to be repo-agnostic but
oriented towards engineering tasks.

## Summary

Both skills exist as user-level skills on this machine — `~/.claude/skills/adversarial-review/SKILL.md`
(143 lines) and `~/.claude/skills/adversarial-loop/SKILL.md` (236 lines) — and both are
currently enumerated in this session's skill list, so they are live, not archived. Between
them they reference eight other skills by name. Three of those (`reply-to-claude`, `sclip`,
`model-help`) resolve to something readable; `model-help` resolves to the wb plugin itself.
Four (`review-reef`, `review-security`, `review-strict`, `review-terse`) are **dangling
symlinks** into `/Users/scraig/projects/prompts/claude-code/skills/`, a directory that does not
exist on this machine — so `adversarial-review`'s single largest stated dependency, the
`review-reef` rule catalogue it is told to read rather than restate, is unreadable today.

The wb plugin has no code-review or PR-lifecycle surface at all. Greps across `plugin/` for
`CONFIRMED`, `claude[bot]`, `ready for review`, `gh pr ready` and `origin/main` return zero
hits. What it does have is the reverse problem: two shipped files already reference a
review-skill family that has never existed in the plugin —
`plugin/skills/daily-digest/SKILL.md:204` and `:278` route work to `pr-feedback` / `review` /
`review-reef` / `review-strict`, and `plugin/skills/model-help/SKILL.md:160` carries a
calibration anchor for `review-reef` specifically. The word "adversarial" is already shipped
vocabulary in `model-help` (`:38`, `:57`, `:81`) and `validate_execution` (`:23`).

Neither skill is repo-agnostic as written. `adversarial-review` names Rails, Turbo/Stimulus,
`belongs_to_yaml_model`, `member` vs `staffer`, CA-only journeys, `en`/`es` locale parity and
PHI in its lens table and hunt list; `adversarial-loop` hardcodes `bundle exec rubocop`,
`docker`/`pg_isready`/`redis-cli` preflight probes, `~/.rbenv` gem paths, `Settings.utility.redis_url`,
RSpec closure-binding semantics, and the `TB-3447` incident the playbook's GitHub gotchas came
from. The plugin does, however, have an established precedent for shipping both
company-specific content (`daily-digest`'s HIPAA/PHI guardrail, `TB-2421` as the standing
example ticket key) and multi-stack examples presented as "or" lists (`implement/SKILL.md:386-389`).

## Detailed Findings

### The two skills as they exist

**Location**: `/Users/scraig/.claude/skills/adversarial-review/` and
`/Users/scraig/.claude/skills/adversarial-loop/` — one `SKILL.md` each, no supporting files.

**What exists**:

- `adversarial-review/SKILL.md` — 143 lines. Frontmatter carries `name`, `description`, and
  `allowed-tools` as a YAML block list: `Read`, `Grep`, `Glob`, `Bash`, `Agent`, `WebFetch`
  (`adversarial-review/SKILL.md:4-11`). Six numbered process sections: resolve the target,
  read whole files plus blast radius, pick 2–4 named principal-engineer lenses, the hunt list,
  a per-finding verification pass, and a verify-only mode for adjudicating another session's
  findings.
- `adversarial-loop/SKILL.md` — 236 lines. Frontmatter carries only `name` and `description`
  (`adversarial-loop/SKILL.md:1-4`) — **no `allowed-tools` block**. Five phases plus a
  "Phase 1.5 — adjudicate the reviewers" section, sequencing existing skills rather than
  re-implementing review logic (`adversarial-loop/SKILL.md:8-9`: "Sequences the skills that
  already exist. It does not re-implement review logic; it enforces the ordering and the gates
  between phases.").

**How adversarial-review works**:

1. Resolve the diff target — `git diff origin/main...HEAD` by default, or
   `gh pr diff <n>` / `gh pr view <n> --json title,body,files` for a PR
   (`adversarial-review/SKILL.md:30-34`); state the target and size before reviewing.
2. Read whole files plus blast radius — `git log --oneline -5 -- <file>` and `grep -rn` sweeps
   for changed method names, old copy fragments in specs (`:44-48`). Load root `CLAUDE.md`,
   every `.rules/*.md` whose globs match a touched file, and `review-reef` §4 (`:50`).
3. Pick 2–4 lenses from an eight-row table keyed on what the diff touches (`:56-65`). Two rows
   are marked **mandatory**: the AI-systems lens when `.claude/skills/**`, `app/agents/**`,
   `app/models/ai/**` or any prompt text is touched (`:60`), and the security lens for
   compliance-sensitive diffs (`:62`).
4. Spawn one `Agent` per lens **in a single message** so they run concurrently; default Sonnet,
   Opus for security and AI-systems lenses on sensitive code (`:69`).
5. Verify every finding before reporting: trace the actual path, construct concrete failing
   input, label **CONFIRMED** / **PLAUSIBLE** / drop (`:87-97`). "Do not run the test suite to
   verify — specs stall/OOM in Conductor. Offer `/sclip` instead" (`:99`).
6. Output format is a fixed markdown shape with 🔴 CONFIRMED / 🟡 PLAUSIBLE headings, each
   carrying a `**Fails when:**` line, plus a capped "Checked and clear" coverage list
   (`:109-126`).

**How adversarial-loop works**:

The documented flow (`adversarial-loop/SKILL.md:11-23`):

```
draft PR exists
   ↓
/adversarial-review  →  apply fixes  →  re-review        (repeat until clean)
   ↓ ⛔ gate: review returns no CONFIRMED findings
gh pr ready          (this is what summons claude[bot])
   ↓
wait on CI + claude[bot] review
   ↓
fix what it raises  →  push  →  /reply-to-claude          (repeat until LGTM)
   ↓ ⛔ gate: claude[bot] says no issues remaining AND CI green on HEAD
add label "ready for review"
```

Preconditions are stated as hard stops: a draft PR must already exist ("this skill starts at an
open draft, it does not create one", `:27-28`), never add the `ready to auto-merge` label
(`:29-30`), never `--force` push (`:31`).

Phase 1.5 is the most portable part of the file — five dispositions for adjudicating a
reviewer's findings (Valid / Wrong / Over-fitted / Real but disproportionate / Pre-existing,
`:51-62`), a proportionality gate (`:74-83`), a coverage check ("lenses only find what they're
pointed at", `:85-96`), reviewer scoring (`:98-103`), and the statement that "'Clean' describes
a tree state, not the branch" (`:105-112`).

### Dependency inventory — every cross-reference in the two files

| Referenced | Where | Exists on this machine? |
| ---------- | ----- | ----------------------- |
| `review-reef` | `adversarial-review/SKILL.md:15,23,50,97` | **No** — dangling symlink |
| `review-security`, `review-terse`, `review-strict` | `adversarial-review/SKILL.md:24` | **No** — dangling symlinks |
| `review-proposal` | `adversarial-review/SKILL.md:24` | Yes — `~/.claude/skills/review-proposal/SKILL.md`, 430 lines |
| `model-help` | `adversarial-review/SKILL.md:38` | Yes — **as the wb plugin skill**, no user-level copy |
| `sclip` | `adversarial-review/SKILL.md:99` | Yes — `~/.claude/skills/sclip/SKILL.md`, 67 lines |
| `adversarial-review` | `adversarial-loop/SKILL.md:14,34` | Yes — the sibling skill |
| `reply-to-claude` | `adversarial-loop/SKILL.md:20,206` | Yes — `~/.claude/skills/reply-to-claude/SKILL.md`, 54 lines |

**The dangling symlinks** (verified `2026-09-17` via `ls -la ~/.claude/skills/`):

```
review-reef     -> /Users/scraig/projects/prompts/claude-code/skills/review-reef
review-security -> /Users/scraig/projects/prompts/claude-code/skills/review-security
review-strict   -> /Users/scraig/projects/prompts/claude-code/skills/review-strict
review-terse    -> /Users/scraig/projects/prompts/claude-code/skills/review-terse
review          -> /Users/scraig/projects/prompts/claude-code/skills/review
```

`cat ~/.claude/skills/review-reef/SKILL.md` returns `No such file or directory`.
`/Users/scraig/projects/prompts/` does not exist. Six further entries point into the same
missing tree — `review-prep`, `status-sync`, `tdd-discipline`, `verification-before-completion`,
`mockup-iteration`, `project-structure` — all of which are names the wb plugin now ships itself.

This matters directly to the research question: `adversarial-review/SKILL.md:23` instructs
**"Read `~/.claude/skills/review-reef/SKILL.md` rather than restating it"**, and §5's
deduplication step (`:97`) tells the reviewer to "drop `review-reef`'s known false positives".
The rule catalogue, the org-wide engineering-guide digest, and the false-positive kill list that
the skill's aggression is bought with are all *by reference* to a file that cannot be read.

**Harness tools and external CLIs required**:

| Requirement | adversarial-review | adversarial-loop |
| ----------- | ------------------ | ---------------- |
| `Agent` (sub-agent spawn) | `:69`, declared at `:9` | via adversarial-review |
| `Monitor` | — | `:176` ("Arm one Monitor for both signals") |
| `WebFetch` | declared at `:10` | — |
| `git` | `:31-32`, `:45` | `:189` (`git rev-parse HEAD`) |
| `gh` | `:33` | `:33`, `:168`, `:195`, `:222`, `:225` |
| `docker`, `pg_isready`, `redis-cli` | — | `:124-126` |
| `bundle exec rubocop` | — | `:166` |
| `ruby -e` | — | `:139` |

### Repo- and company-specific content, verbatim

**`adversarial-review/SKILL.md`** — 10 passages tie it to the reef codebase:

- `:15` — "`review-reef` audits a change against a rule catalogue and optimizes for zero false positives."
- `:23` — "the rule catalogue (`.rules/` + Brightline Engineering Guide digest) and the Reef false-positive guards"
- `:58` — lens row: "Principal Rails engineer — data integrity, idempotency, transaction boundaries, N+1s"
- `:59` — "Turbo/Stimulus lifecycle"
- `:60` — mandatory AI lens keyed on Rails-shaped paths: "`app/agents/**`, `app/models/ai/**`"
- `:62` — "Auth, PHI, params, uploads, external calls | Security engineer — **mandatory** for compliance-sensitive diffs"
- `:64` — "Localization engineer — es parity, `tú`-form, format strings, untranslated SMS \"STOP\""
- `:76` — "`belongs_to_yaml_model` FK readers return Symbols (`:coaching`, not `\"coaching\"`); … Postgres drops fractional seconds"
- `:77` — "member vs staffer, region-gated journeys (CA-only), `en` vs `es`"
- `:97` — "Ruby 3.4 `it`, un-namespaced `app/controllers/staffers/`, `YamlModel` treated as AR, `.ts` Stimulus controllers"
- `:99` — "specs stall/OOM in Conductor"

**`adversarial-loop/SKILL.md`** — the repo-specificity is concentrated in Phases 1.5, 2 and 3:

- `:70-72` — a named production-regression example: seeding a counter with `Rails.cache.fetch { 0 }` writes a marshalled `Entry` so the subsequent `INCRBY` raises
- `:124-126` — the service preflight block (`docker info`, `pg_isready -h localhost -p 5432`, `redis-cli -h localhost ping`)
- `:136` — "the Acuity breaker specs dial `Settings.utility.redis_url`"
- `:147-163` — five RSpec-specific authoring traps: `describe`-level lambda `self` binding vs `instance_double`/`let`, partially-passing parametrised tables, route-helper names from `as:`/`namespace`, `before_action` region/care-model gates, `turbo-stream` `target=` assertions
- `:166` — "Run lint first (`bundle exec rubocop` in reef — it works in Conductor now)"
- `:178-189` — the GitHub gotchas, all attributed to "the TB-3447 run": the bot login is `claude[bot]` not `claude`, the bot edits its comment in place, the `claude-pr-review` check shows `SKIPPED` on later pushes, read the rollup against `headRefOid`
- `:203` — "the installed gem under `~/.rbenv/.../gems/`, not memory"
- `:234` — "in the TB-3447 run, CI caught a spec-scope bug that four adversarial passes missed"

The GitHub/`gh` mechanics at `:178-196` are the one block that is stack-agnostic but
*harness*-specific: it describes Anthropic's `claude[bot]` PR-review integration, not anything
about Ruby or reef.

### What the wb plugin already has — and what it does not

**Zero hits** across the entire `plugin/` tree (verified 2026-09-17) for: `CONFIRMED`,
`claude[bot]`, `ready for review`, `gh pr ready`, `origin/main`. There is no PR-lifecycle
automation, no draft handling, no CI polling, and no confidence-graded finding vocabulary
anywhere in the plugin.

**The plugin already references a review-skill family it does not ship**:

- `plugin/skills/daily-digest/SKILL.md:204` — "PR review you owe → `pr-feedback` / `review` / `review-reef` per its size."
- `plugin/skills/daily-digest/SKILL.md:278` — "**review skills** (`pr-feedback`, `review`, `review-reef`, `review-strict`) — the …"
- `plugin/skills/model-help/SKILL.md:160` — "**Reef `review-reef` on a clinical notes-fan-out PR** → Opus 5 / high (compliance-critical, cross-file, adversarial). Bump to max for a focused pass on the sign-and-lock core."

None of `pr-feedback`, `review`, `review-reef`, `review-strict` exists under `plugin/skills/`.

**"Adversarial" is already shipped vocabulary**:

- `plugin/skills/model-help/SKILL.md:38` — Opus 5 is reserved for "…wide blast radius, adversarial review of sensitive code."
- `plugin/skills/model-help/SKILL.md:57` — tier table row ending "· adversarial review of sensitive code | Opus 5 | high → max |"
- `plugin/skills/model-help/SKILL.md:81` — "**xhigh/max** for the thorniest multi-constraint problems or adversarial verification"
- `plugin/skills/validate_execution/SKILL.md:23` — "adversarial checking of sensitive code earns the higher tier"

**The closest existing surfaces**:

| Skill | What it does | Relation |
| ----- | ------------ | -------- |
| `plugin/skills/review-prep/SKILL.md` | Interactive tmux/nvim diff walkthrough; `git diff main..HEAD --stat` (`:45`); groups hunks by problem (`:48-62`), TDD check per file (`:83-96`), code-smell table (`:150-158`), ends "Ready for PR? [yes/concerns]" (`:120-131`) | Owns the trigger phrases "review", "walk through changes", "prep for PR" (`:3`). Human-paced, no agent fan-out, no finding labels |
| `plugin/skills/validate_execution/SKILL.md` | Spawns 4 parallel validation agents (`:110-126`), runs local `make check`/`test`/`build` (`:132-141`), treats checkboxes as claims not findings (`:74-97`); PASS/FAIL + gap tables | Same fan-out-then-synthesize shape; subject is plan-vs-code fidelity, not code correctness |
| `plugin/agents/task-verifier.md` | Per-task verification: runs task tests, `git status --short`/`git diff` (`:97-98`), scope-creep check (`:89-119`), `### Status: PASS/FAIL` template (`:137-173`); separates baseline failures (`:66-71`, `:158-159`) | Explicitly disclaims review: "Don't evaluate quality/style, suggest refactoring, or analyze architecture decisions" (`:214`) |
| `plugin/skills/fetch-issues/SKILL.md` | `gh issue list`, `gh pr list --json number,title,state,url,headRefName,mergedAt,closingIssuesReferences,body` (`:73-79`) | The plugin's deepest `gh` usage; read-only, never writes to GitHub (`:290`) |
| `plugin/skills/daily-digest/sources.md` | `gh pr list … --json number,title,url,reviewDecision,statusCheckRollup,isDraft,updatedAt` (`:54-55`), interprets `CHANGES_REQUESTED` and `statusCheckRollup` `FAILURE` (`:56-57`) | The only place the plugin reads CI status; read-only triage |

Four distinct structured-report shapes already ship: `validate_execution`'s PASS/FAIL gap
report, `task-verifier`'s `### Status: PASS/FAIL` with ✅/⚠️/❌ markers, `review-prep`'s Review
Summary, and `fetch-issues`'s `ready` / `fix-in-flight` / `fixed-merged` / `stale-fixed` STATE
table. A CONFIRMED / PLAUSIBLE vocabulary would be a fifth; no existing shape uses
confidence-graded labels.

`plugin/skills/model-help/SKILL.md`'s gate-mode per-phase table (`:94-103`) has rows for
`create_research`, `create_design`, `create_tasks`, `implement`, `implement_inline` and
`validate_execution` — and no row for any review or PR-loop skill. The only guidance that would
apply is the free-text `review-reef` calibration anchor at `:160`.

### The plugin's shipping contract for a new skill

**Discovery is directory-based.** `plugin/.claude-plugin/plugin.json` carries no `skills`,
`commands` or `agents` array — a skill ships by existing at `plugin/skills/<name>/SKILL.md`.
The `wb:` prefix is derived from `"name": "wb"` at `plugin/.claude-plugin/plugin.json:2` and
never appears in a skill file.

**Frontmatter keys observed across all 43 shipped skills**:

- `name` — universal, first key, matches the directory name.
- `description` — universal, one long line carrying the "Use when …" trigger phrases.
- `allowed-tools` — 28 of 43 files; comma-separated, sometimes tool-scoped
  (`Bash(ls:*, mkdir:*)`). Example: `plugin/skills/create_research/SKILL.md:5`.
- `argument-hint` — 21 files, e.g. `plugin/skills/forge/SKILL.md:4`.
- `disable-model-invocation: true` — 3 files, all deprecated aliases
  (`plugin/skills/create_execution/SKILL.md:5`, `implement_tasks/SKILL.md:5`,
  `implement_coordinated/SKILL.md:5`).
- `user-invocable: false` — 6 background/enforcement skills
  (`doc-adherence`, `project-structure`, `mockup-iteration`,
  `verification-before-completion`, `status-sync`, `tdd-discipline`).
- `triggers:` — exactly one file, `plugin/skills/mockup-iteration/SKILL.md:6-13`.

**Supporting-file convention**, verbatim from `plugin/skills/create_research/SKILL.md:9-18`:

```markdown
Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- [sub-agent-prompts.md](sub-agent-prompts.md) — verbatim prompts for …

**If a directed read fails, stop — do not continue from memory.** These files live outside your
project, so a read can be refused. Say which file was refused, that reads outside the working
directory are gated, and that the fix is to allow the read once or to relaunch with
`--add-dir <plugin-path>`. Do not route around a refusal with `cat`.
```

The same two-part pattern recurs at `plugin/skills/forge/SKILL.md:13-20` and
`plugin/skills/daily-digest/SKILL.md:19-22`.

**Runtime-readable rules** may live only in `plugin/docs/reference/` (`CLAUDE.md:34-35`:
"a shipped skill may link only into `plugin/docs/reference/`. Nothing under root `docs/` is read
at runtime."). That directory currently holds `README.md` and `branch-naming.md`. Four skills
link into it with the relative form `../../docs/reference/branch-naming.md`
(`create_project/SKILL.md:16,104`; `forge/SKILL.md:16,91`; `implement/SKILL.md:21,172`;
`jira-context/SKILL.md:97`).

**The model-help gate paragraph** appears word-for-word in five stage skills
(`create_design`, `create_research`, `create_tasks`, `implement_inline`, `validate_execution`).
Text at `plugin/skills/create_research/SKILL.md:25`:

> **Model & effort (gate check)**: on entry, consult the `model-help` skill (gate mode) for the
> model + effort this phase warrants; surface its one-line verdict and — only if a switch clears
> the switch-cost bar — the `/model` action. … Best-effort and non-blocking: stay silent and
> proceed when the current tier is already right. See CLAUDE.md → "Model & effort at gates."

**Agents** are files at `plugin/agents/*.md` with their own frontmatter — `name`,
`description`, `tools`, `model`, and optionally `effort`, `maxTurns`, `skills`. Skills spawn
them by `subagent_type` string matching the agent's `name`
(`plugin/skills/create_research/sub-agent-prompts.md:40,61,80`). Existing tiers: `haiku` for
`codebase-locator` and `pattern-finder`; `sonnet` + `effort: medium` for `codebase-analyzer`
and `product-behavior-analyzer`; `sonnet` + `effort: high` for `research-validator` and
`task-verifier`. `validate_execution/sub-agent-prompts.md:51,70` also spawns
`subagent_type: "general-purpose"`, which is not defined under `plugin/agents/`.

**Release mechanics** (`CLAUDE.md` § "Releasing New Commands/Skills/Agents"): the cache at
`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` is keyed by version, so new files do
not appear until the version bumps in **both** `plugin/.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json` (currently `2.1.0` in both) **and** the user runs
`claude plugin update wb@thescubageek-workbench`.

**Markdown lint** (`.markdownlintrc`): `default: true` with `MD013`/`line-length` off,
`MD033` (inline HTML) off, `MD036` (emphasis as heading) off, `MD040` (fenced language) off,
`MD041` off, `MD060` off, `MD003` ATX headings, `MD007` 2-space list indent,
`MD024 siblings_only`. `plugin/scripts/lint-hook` runs `lint --fix` automatically on
Write/Edit of any `.md`, wired at `plugin/.claude-plugin/plugin.json` PostToolUse.

### How shipped wb skills stay repo-agnostic

**Probe-don't-assume / delegate to the plan.** No shipped skill parses `package.json` or
`Gemfile`. The concrete command is read out of the repo's own `research.md`/`tasks.md`:

- `plugin/skills/implement/SKILL.md:385-389` — "`# Adapt these to actual commands from tasks.md`"
  followed by `scripts/quiet make test # or npm test, go test ./..., pytest`, and the same
  pattern for lint, typecheck and build.
- `plugin/skills/implement/SKILL.md:198,210-213` — the worker context package carries
  `testingFramework: "jest | pytest | go test | ..."` as an extracted value, not a constant.
- `plugin/skills/tdd-discipline/SKILL.md:39` — "`pytest -x`, `jest --bail`, `go test -failfast`,
  `cargo test` (stops by default)".

A grep of `plugin/` for `rspec|rubocop|bundle exec|rails|docker|psql|redis|ruby` returns **zero**
hits. Only JS/Python/Go tooling appears, always in "or" lists.

**Optional dependency as best-effort, never blocking** — the established wording:

- `plugin/skills/jira-context/SKILL.md:20-22` — "Best-effort: never block on a missing ticket,
  missing MCP, or missing `Agents` section."
- `plugin/skills/create_research/SKILL.md:80` — "**⛔ Best-effort, never blocking**: no ticket,
  no Atlassian MCP, or no `Agents` section must NOT stop research."
- `plugin/skills/daily-digest/SKILL.md:116-120` — "If a source's tool is unavailable or
  unauthorized … the collector reports `unavailable: <reason>` and returns empty — **never block
  the digest on one source.**"
- `plugin/docs/reference/branch-naming.md:72` — "**Non-blocking.** Declined, unavailable, or not
  a git repo → proceed with the work on the current branch…"

**Tooling-availability guards** already in shipped code:

- `plugin/skills/clip/SKILL.md:20-30` — `command -v` chain `pbcopy` → `clip.exe` → `clip` →
  `xclip` → `xsel`, ending in an explicit error branch. Duplicated at
  `plugin/skills/eli5-clip/SKILL.md:33-37`.
- `plugin/scripts/lint:79-86` — `command -v markdownlint` guard with install instructions.
- `plugin/scripts/lint:88-92` — git-repo guard that falls back to `LINT_ALL=true`.
- `plugin/skills/create_project/SKILL.md:71-74` — every git read guarded:
  `git rev-parse HEAD 2>/dev/null || echo "not-in-git"`.

**Per-repository escape hatches** that a shipped skill can read:

- `.claude/wb/knowledge.md` — durable repo facts, read "if it exists" by `create_research`
  (`:89-99`), `resume_handoff:104`, `explore_design:88`, `implement:138`, `implement_inline:139`,
  `create_design:140`, `create_product_research:65`. Discovered and counted by
  `plugin/hooks/wb-prime.sh:190-198`.
- `.claude/wb/PRIME.md` — replaces the static session-start orientation entirely
  (`plugin/hooks/wb-prime.sh:105-109`).

**Company-specific content that shipped anyway** — the precedent cuts both ways:

- `plugin/skills/daily-digest/SKILL.md:229-246` — a full `## PHI guardrail` section, including
  `:231` "**Brightline is a HIPAA-covered behavioral-health org.**" and `:237` the Member ID
  regex `(?:BM|BC|BA)-[A-Z]{2}-\d{8}`.
- `plugin/skills/daily-digest/sources.md:26,33` — "reconcile a **reef** PR" and
  `-R hellobrightline/reef`; `:89-90` the `hellobrightline.atlassian.net` host quirk;
  `:98-100` "**Status vocabulary varies per project — discover it, don't hardcode.** This org's
  in-review status is 'Waiting for Review', not 'In Review'."
- `TB-2421` is the standing example ticket key across `plugin/skills/jira-context/SKILL.md:3,36,101,139`,
  `plugin/skills/forge/SKILL.md:57`, `plugin/skills/forge/examples.md:8-9`, and
  `plugin/docs/reference/branch-naming.md:16,86-88`.
- `plugin/skills/model-help/SKILL.md:161` — "(e.g. TB-2936 Zoom `zoom_url`)".

No hits anywhere in the repo for `Acuity`, `Smartling`, or `staffer`.

## Code References

- `/Users/scraig/.claude/skills/adversarial-review/SKILL.md:4-11` — frontmatter, `allowed-tools` block list
- `/Users/scraig/.claude/skills/adversarial-review/SKILL.md:23` — the unreadable `review-reef` dependency
- `/Users/scraig/.claude/skills/adversarial-review/SKILL.md:56-65` — the lens table
- `/Users/scraig/.claude/skills/adversarial-review/SKILL.md:87-97` — the verification pass, CONFIRMED/PLAUSIBLE
- `/Users/scraig/.claude/skills/adversarial-review/SKILL.md:109-126` — output format
- `/Users/scraig/.claude/skills/adversarial-loop/SKILL.md:1-4` — frontmatter, no `allowed-tools`
- `/Users/scraig/.claude/skills/adversarial-loop/SKILL.md:11-23` — the phase flow diagram
- `/Users/scraig/.claude/skills/adversarial-loop/SKILL.md:51-62` — the five reviewer dispositions
- `/Users/scraig/.claude/skills/adversarial-loop/SKILL.md:105-112` — "'Clean' describes a tree state"
- `/Users/scraig/.claude/skills/adversarial-loop/SKILL.md:178-196` — the `claude[bot]` / CI gotchas
- `plugin/skills/daily-digest/SKILL.md:204,278` — dangling references to the review-skill family
- `plugin/skills/model-help/SKILL.md:38,57,81,160` — "adversarial" vocabulary and the `review-reef` anchor
- `plugin/skills/model-help/SKILL.md:94-103` — gate-mode per-phase table, no review row
- `plugin/skills/review-prep/SKILL.md:3` — the trigger phrases a new review skill would compete with
- `plugin/skills/validate_execution/SKILL.md:110-126` — the existing parallel-agent fan-out
- `plugin/agents/task-verifier.md:137-173,214` — existing report shape and its explicit non-review disclaimer
- `plugin/skills/create_research/SKILL.md:9-18` — supporting-file convention and hard-stop paragraph
- `plugin/skills/create_research/SKILL.md:25` — the model-help gate paragraph, verbatim
- `plugin/.claude-plugin/plugin.json:2-3` — plugin name and version; no skills array
- `CLAUDE.md:34-35` — where runtime-readable rules may live
- `plugin/hooks/wb-prime.sh:105-109,190-198` — `.claude/wb/PRIME.md` and `knowledge.md` discovery

## Similar Implementations

**The closest existing fan-out-then-synthesize pattern** is `plugin/skills/create_research/`
itself — a `SKILL.md` that defers verbatim agent prompts to `sub-agent-prompts.md`, an output
shape to `templates.md`, and configuration to `reference.md`, with `⛔ BARRIER` markers between
spawn, wait and synthesize. `validate_execution` uses the same three-file split.
`adversarial-review`'s lens table + per-lens agent + synthesis is structurally the same shape in
a single file.

**The closest existing best-effort-external-dependency pattern** is
`plugin/skills/daily-digest/sources.md`, where each source recipe states its dependency and the
exact `unavailable: <reason>` string to return when it is missing — `:121` for Atlassian,
`:140-142` for Sentry (including a REST fallback via `SENTRY_AUTH_TOKEN`), `:156` for Notion,
`:167` for Gmail.

**The closest existing repo-supplied-configuration pattern** is `.claude/wb/knowledge.md`, whose
entry shape is defined in `plugin/skills/create_handoff/SKILL.md:116-134` and whose read
convention ("if it exists … absent file, fall through") is stated at
`plugin/skills/create_research/SKILL.md:89-99`.

## Open Questions

*All questions resolved as of 2026-09-17.*

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| Q1 | `adversarial-review` delegates its rule catalogue, org-guide digest and false-positive kill list to `review-reef`, which is unreadable on this machine. Does a portable version inline a generic equivalent, read a repo-supplied file (`.claude/wb/` convention), or drop the dependency? | The scope of the port — this is the single largest content gap | **Resolved 2026-09-17** → design.md (## Technical Decisions) |
| Q2 | Does a shipped `adversarial-review` take the `review-prep` trigger phrases ("review", "prep for PR", `plugin/skills/review-prep/SKILL.md:3`), or does `review-prep` get amended to hand off? | Naming and frontmatter `description` for both skills | **Resolved 2026-09-17** → design.md (## Technical Decisions) |
| Q3 | `plugin/skills/daily-digest/SKILL.md:204,278` and `plugin/skills/model-help/SKILL.md:160` route to `pr-feedback` / `review` / `review-reef` / `review-strict`, none of which the plugin ships. Do those references get repointed at the new skill, or does the new skill adopt one of those names? | Whether the port is 2 files or 2 files + edits to 2 shipped skills | **Resolved 2026-09-17** → design.md (## Technical Decisions) |
| Q4 | `adversarial-loop` requires `gh`, the `Monitor` tool, and a GitHub repo with the `claude[bot]` PR-review integration installed. Are those hard preconditions with a stated stop, or best-effort per `jira-context/SKILL.md:20-22`? | The loop skill's precondition section and its `allowed-tools` | **Resolved 2026-09-17** → design.md (## Technical Decisions) |
| Q5 | `adversarial-loop`'s spec-preflight (`:124-126`) and lint step (`:166`) are hardcoded to Docker/Postgres/Redis and `bundle exec rubocop`. Does the port read commands from `tasks.md` the way `implement/SKILL.md:385-389` does, or probe, or ask? | How Phase 1's fix-verify step is written | **Resolved 2026-09-17** → design.md (## Technical Decisions) |
| Q6 | `adversarial-loop` names `reply-to-claude` and `sclip`, both user-level skills tied to `hellobrightline/reef` (`reply-to-claude/SKILL.md:49-50`) and to `bclear && bert` / `yarn spec` (`sclip/SKILL.md:12-13`). Do generic equivalents ship alongside, or does the loop inline what it needs? | Whether the port is 2 skills or 4 | **Resolved 2026-09-17** → design.md (## Technical Decisions) |
| Q7 | Does a CONFIRMED / PLAUSIBLE report become the plugin's fifth structured-report vocabulary, or align with an existing one (`task-verifier`'s PASS/FAIL, `validate_execution`'s gap table)? | The output-format section of the review skill | **Resolved 2026-09-17** → design.md (## Technical Decisions) |
| Q8 | `model-help`'s gate-mode table (`:94-103`) has no row for a review or PR-loop phase. Does the port add rows there? | Whether `model-help/SKILL.md` is in the change set | **Resolved 2026-09-17** → design.md (## Technical Decisions) |

## Next Steps

1. Resolve Q1 first — it determines whether this is a port or a rewrite. The `review-reef`
   dependency is load-bearing in `adversarial-review` (`:23`, `:50`, `:97`) and unreadable.
2. Resolve Q2 and Q3 together — they are one naming decision with two consequences.
3. Run `/wb:create_design docs/plans/2026-09-17-adversarial_loop` to record the decisions.

---

## Follow-up Research 2026-09-17 11:30

**Question**: what does a standard Claude Code install already ship for code review, what do
Anthropic's official marketplace plugins ship, and what are the published community patterns —
so that a wb adversarial skill borrows the standard machinery rather than reinventing it?

### `/code-review` is a built-in, and it is far more machinery than the earlier pass assumed

`/code-review` is compiled into the Claude Code binary
(`/Users/scraig/.local/share/claude/versions/2.1.272`, Mach-O arm64). It is registered
alongside `simplify`, `verify`, `commit` and `pr` through one internal command registrar, with
`aliases:["review"]` and `userInvocable: true`. Extraction method for everything below:
`strings -n 6 <binary> > /tmp/cc-strings.txt`, then offset-window extraction around anchors. All
quotes are verbatim from that dump.

**Shipped description string** (identical to the entry this session's harness lists for the
`Skill` tool, which is what confirms it is invocable programmatically, not only by a user typing
a slash command):

> "Review the current diff, or a PR number/branch/path target, for correctness bugs and
> reuse/simplification/efficiency cleanups at the given effort level (low/medium: fewer,
> high-confidence findings; high→max: broader coverage, may include uncertain findings; ultra:
> deep multi-agent review in the cloud (requires claude.ai account access)); with no level
> given, it reuses the level you typed last. Pass --comment to post findings as inline PR
> comments, or --fix to apply the findings to the working tree after the review."

**Argument surface**: `[low|medium|high|xhigh|max|ultra] [--fix] [--comment] [<pr#>|<branch>|<path>]`.
Levels match case-insensitively with prefix matching (`^(low|med|hig|xhi|max)[a-z]*$`).

**Effort is a real behavioral dial, not a label.** Per-level prompts, with their own tag lines
quoted verbatim from the binary:

| Level | Tag line | Shape |
| ----- | -------- | ----- |
| `low` | `low effort → 1 diff pass → no verify → ≤4 findings` | One diff read, hunk-visible bugs only, no subagents, skips test/fixture hunks |
| `medium` | `medium effort → 3+5 angles × 6 candidates → 1-vote verify → ≤8 findings` | 8 parallel finder subagents; "reviewing for **precision**" |
| `high` | `high effort → 3+5 angles × 6 candidates → 1-vote verify (recall-biased) → ≤10 findings` | Same 8 angles; "reviewing for **recall** … Err on the side of surfacing" |
| `xhigh` / `max` | `xhigh effort → 5+5 angles × 8 candidates → 1-vote verify → sweep → ≤15 findings` | 10 parallel finder subagents, 8 candidates each, plus a gap sweep |

**The angle taxonomy** (what the built-in already fans out over):

- Correctness — **A** line-by-line hunk scan *plus the enclosing function* ("bugs in unchanged
  lines of a touched function are in scope"); **B** removed-behavior auditor ("For every line the
  diff DELETES or replaces, name the invariant or behavior it enforced, then search the new code
  for where that invariant is re-established"); **C** cross-file caller/callee tracer;
  **D** language-pitfall specialist (high+); **E** wrapper/proxy correctness (high+).
- Cleanup — Reuse, Simplification, Efficiency.
- **Conventions (CLAUDE.md)** — "Find the CLAUDE.md files that govern the changed code: the
  user-level `~/.claude/CLAUDE.md`, the repo-root CLAUDE.md, plus any CLAUDE.md or
  CLAUDE.local.md in a directory that is an ancestor of a changed file… Only flag a violation
  when you can quote the exact rule and the exact line that breaks it."
- **Altitude** — "Check that each change fixes the root cause at the right depth rather than
  patching a symptom with a fragile bandaid."

**The finding vocabulary is already CONFIRMED / PLAUSIBLE / REFUTED.** Verbatim from the binary:

```
## Phase 2 — Verify (1-vote, 3-state)
… run **one verifier** via the ${Task} tool:
give it the diff, the relevant file(s), and the candidate; it returns exactly
one of **CONFIRMED / PLAUSIBLE / REFUTED**.
Keep **CONFIRMED and PLAUSIBLE**. Drop REFUTED.
```

with decision criteria:

```
- **CONFIRMED** — can name the inputs/state that trigger it and the wrong
  output or crash. Quote the line.
- **PLAUSIBLE** — mechanism is real, trigger is uncertain (timing, env,
  config). State what would confirm it.
- **REFUTED** — factually wrong (code doesn't say that) or guarded elsewhere.
  Quote the line that proves it.
```

This is the same discipline `adversarial-review/SKILL.md:87-97` specifies, arrived at
independently.

**An observation about wiring, stated with its uncertainty.** The verify and sweep blocks above
exist as named template variables in the bundle (`Bt`, `vi`, `wi`, `bi`, `ki`, `Ht`), and each
appears exactly once — at its own definition. The live per-level composers instead carry
`## Phase 2 — Dedup and self-check (no subagent verify)` and `## Phase 2 — Dedup only (no
verify)`, and the xhigh/max composer runs straight from Phase 1 to the output cap with "This is
recall mode — a single non-REFUTED vote carries the finding. Do NOT drop on uncertainty."
Read from minified strings rather than source, so treat as an observation about this build
(2.1.272), not a settled fact: **the three-state verifier prompt ships, but no live effort path
in this build appears to call it.**

**Model-family routing.** A table keyed on model (`ae`) selects a different prompt per family.
Under `claude-opus-5`, `medium` and `high` both resolve to the same minimal cell (`o5-bmin`) —
a short single-pass prompt that ends "submit at most 15 findings via the ReportFindings tool."
Under `claude-opus-4-8`, every level runs its angles **inline**, not as subagents ("in sequence
yourself, in THIS context — do NOT spawn subagents for them … Do NOT run verifiers; do NOT
re-judge"). Default and `claude-sonnet-5` families get the full parallel fan-out.

**Finder budget scales with diff size**: `Math.max(2, Math.min(8, Math.ceil(lines_changed/150)))`,
computed from a hardened `git diff --numstat` invocation
(`GIT_ALLOW_PROTOCOL=none`, `GIT_NO_LAZY_FETCH=1`, `GIT_TERMINAL_PROMPT=0`).

**Graceful degradation is built in.** If the Task/agent tool is unavailable, every angle runs
inline in one pass, with a disclosure requirement: "State clearly in your summary that this was
a single-pass review done without the [Task] tool, not the full multi-agent fan-out, so whoever
reads it isn't misled about what actually ran."

**`--comment`**: posts one inline PR comment per finding via
`mcp__github_inline_comment__create_inline_comment`, falling back to
`gh api repos/{owner}/{repo}/pulls/{pr}/comments`, and on GitLab to `glab mr note`.

**`--fix`**: applies findings to the working tree, then "call ReportFindings again with the same
findings, each carrying an `outcome`: `fixed`, `no_change_needed` … or `skipped`."

**Post-review chaining**: "if `/verify` has NOT run this session and the diff has a runtime
surface … invoke `/verify` now — this review checks that the diff reads right; `/verify` checks
that it runs right."

**Level persistence**: `codeReviewLastEffort` is a persisted setting, written only when the user
types an explicit level, surfaced as "Reusing {last} effort, the level you typed last time."

**Telemetry** logs `tengu_code_review_routed` with `effort_level`, `effort_source`,
`uses_report_findings_tool`, `has_fix`, `has_comment`, `has_target`, `model_family`,
`finder_budget`, `agent_tool_available`.

**`ultra`** routes to a separate `ultrareview` command gated on claude.ai account access; its
review logic runs server-side ("Claude Code on the web") and is **not** present in the client
binary.

### The `ReportFindings` tool is the shipped structured-output channel

Tool name constant `rH="ReportFindings"`. Its description and field descriptions in the binary
match this session's live tool schema exactly:

- `findings[]` — "Verified findings, most-severe first; empty if none survived" (`maxItems: 32`)
- `file` — "Repo-relative path of the file the finding is in"
- `line` — "1-indexed line the finding anchors to"
- `summary` — "One-sentence statement of the defect"
- `short_summary` — "the claim compressed to ≤60 characters, no rationale or consequence clause"
- `failure_scenario` — "concrete inputs/state → wrong output/crash"
- `category` — "Short kebab-case slug… `correctness`, `simplification`, `efficiency`, `test-coverage`";
  the composer also names `reuse`, `altitude`, `conventions`
- `verdict` — "Set when a verify pass ran; absent on inline-only reviews" — enum `CONFIRMED | PLAUSIBLE`
- `outcome` — "Set ONLY when re-reporting after applying fixes" — enum `fixed | skipped | no_change_needed`
- `level` — "Effort level the review ran at"

The tool's own description gates its use: "Use this only when the active code-review
instructions tell you to report findings with this tool; otherwise follow whatever output format
those instructions specify." So a wb skill that wants host-UI rendering must say so in its own
instructions.

### `/security-review` and `/simplify`

**`/security-review`** ships as a static markdown body (no effort tiers, no `ReportFindings`).
`description: Complete a security review of the pending changes on the current branch`. It
targets `git diff origin/HEAD...`, runs a 3-phase methodology (repo-context research →
comparative analysis against the repo's existing secure patterns → vulnerability assessment),
and enumerates five categories: Input Validation, Authentication & Authorization, Crypto &
Secrets Management, Injection & Code Execution, Data Exposure. Discipline, verbatim:
"MINIMIZE FALSE POSITIVES: Only flag issues where you're >80% confident of actual
exploitability"; a hard-exclusion list (DoS, secrets on disk, rate limiting, memory/CPU
exhaustion, hardening gaps, theoretical race conditions, outdated third-party libraries); and a
two-stage subagent fan-out — one identification sub-task, then **one parallel
false-positive-filtering sub-task per candidate**, dropping anything scored below 8/10. Output is
markdown only: "Your final reply must contain the markdown report and nothing else."

**`/simplify`**: `description: Review the changed code for reuse, simplification, efficiency,
and altitude cleanups, then apply the fixes. Quality only — it does not hunt for bugs; use
/code-review for that.` Tag: `/simplify → 4 cleanup agents in parallel → apply the fixes`. No
effort tiers, no `ReportFindings`, and it always applies fixes — there is no `--fix` flag
because fixing is the point. It reuses `/code-review`'s Reuse / Simplification / Efficiency /
Altitude angle text and omits the correctness angles and the Conventions angle.

### Anthropic's official marketplace — what the review plugins actually contain

`/Users/scraig/.claude/plugins/marketplaces/claude-plugins-official/` lists 308 plugins; 39 are
checked out locally. Three are review-related.

**`plugins/code-review/`** — one slash command, no skills or agents.
`commands/code-review.md:1-5` frontmatter restricts tools to `gh` reads plus `gh pr comment`.
Its pipeline: Haiku eligibility gate → Haiku CLAUDE.md-path lister → Haiku PR summarizer →
**5 parallel Sonnet agents** (CLAUDE.md compliance, shallow bug scan, git blame/history, prior
PRs touching these files, code-comment compliance) → per-issue **Haiku scorer** agents on a
0/25/50/75/100 confidence rubric → `Filter out any issues with a score less than 80`
(`:26`) → post via `gh pr comment`. Its false-positive exclusion list (`:33-42`) names
pre-existing issues, pedantic nitpicks, anything a linter/typechecker/CI catches, and issues on
lines the user did not modify. **No extension point** — `README.md:200-217` says customizing
means editing the command file.

**`plugins/pr-review-toolkit/`** — six agents (`code-reviewer`, `code-simplifier`,
`comment-analyzer`, `pr-test-analyzer`, `silent-failure-hunter`, `type-design-analyzer`) behind
`commands/review-pr.md`, whose `argument-hint` is `[review-aspects]` and which accepts
`comments | tests | errors | types | code | simplify | all` plus a `parallel` modifier
(`review-pr.md:22-28`, `:109-113`). `agents/code-reviewer.md:1-6` is `model: opus`; the rest are
`model: inherit` except `code-simplifier` (`model: opus`). Confidence floor is again
`Only report issues with confidence ≥ 80` (`code-reviewer.md:41`). Aggregated output is
Critical / Important / Suggestions / Positive Observations / Recommended Action.
**It never calls `gh pr ready`, never polls CI, never applies labels.**

**`plugins/feature-dev/agents/code-reviewer.md`** — `model: sonnet`, same 0–100 confidence rubric
and ≥80 floor; invoked in Phase 6 of `feature-dev` as **3 parallel copies with different
focuses** (simplicity/DRY, bugs/correctness, conventions/abstractions).

**Across every locally checked-out official plugin**: no `gh pr ready`, no CI check-run polling,
no reaction to a GitHub bot review, no label application, and no call to `ReportFindings`. The
PR-lifecycle loop `adversarial-loop` describes has **no official equivalent**.

### Published external patterns

- **Anthropic's hosted Code Review GitHub App** (`https://code.claude.com/docs/en/code-review`,
  Team/Enterprise, research preview) — "multiple agents analyze the diff and surrounding code in
  parallel on Anthropic infrastructure. Each agent looks for a different class of issue, then a
  verification step checks candidates against actual code behavior to filter out false
  positives." Severities: 🔴 Important, 🟡 Nit, 🟣 Pre-existing. **Its customization surface is
  a repo file**: `CLAUDE.md` for general project rules, and **`REVIEW.md` for review-only
  instructions consumed directly by the finding/verification/ranking agents** — the closest
  official precedent for a repo-supplied strictness dial. Triggers include `@claude review`,
  `@claude review always`, `@claude review once`.
- **`anthropics/claude-code-action`** (`https://code.claude.com/docs/en/github-actions`) — the
  documented workflow triggers on `pull_request: types: [opened, synchronize, ready_for_review,
  reopened]`, and "Claude skips draft and closed pull requests, pull requests it judges not to
  need a review… and pull requests that already have a comment from Claude." In interactive mode
  it "replies in a comment on the same issue or PR and **updates it as it works**" — which is the
  documented basis for `adversarial-loop/SKILL.md:181-182`'s "the bot edits its existing comment
  in place."
- **`anthropics/claude-code-security-review`** — a real Anthropic-owned GitHub Action. Its README
  states it is **not hardened against prompt injection and should only be used on trusted PRs**.
- **`review-strict` is not a distributed artifact.** `https://registry.npmjs.org/review-strict`
  returns `{"error":"Not found"}`; no marketplace plugin or skill by that exact name was found.
  What is real is a `<language>-strict` **suffix convention** (`0xMassi/claude-skills` ships
  `typescript-strict`, `rust-strict`, `go-strict`, … plus a `code-review` orchestrator that calls
  them). A `strict=true` **flag** on a review skill could not be confirmed in any published
  source, including Matt Pocock's own code-review skill
  (`https://www.aihero.dev/skills-code-review`), which runs two fixed always-on axes (Standards,
  Spec) with no strictness parameter.
- **`thermo-nuclear-code-quality-review`** is a real distributed SKILL.md
  (`heyimcarlos/agent-skills/skills/engineering/thermo-nuclear-code-quality-review/SKILL.md`).
  Content: "Do not let a PR push a file from under 1000 lines to over 1000 lines without a strong
  structural reason"; rejects pass-through abstractions and broad types; output is a six-tier
  prioritized findings list; "Do not approve merely because behavior seems correct."
- **Multi-persona adversarial review, published examples**: `wan-huiyan/agent-review-panel` —
  4–6 personas auto-selected from content type and ten technology signal groups, parallel fan-out
  → 1–3 rounds of debate → claim verification against source → an Opus "Supreme Judge" →
  a post-judge verification gate. `alirezarezvani/claude-skills` adversarial-reviewer — three
  fixed personas (Saboteur, New Hire, Security Auditor) with a forcing function: "Each persona
  MUST produce at least one finding. If a persona finds nothing wrong, it has not looked hard
  enough"; findings caught by 2+ personas are promoted one severity level; verdicts
  BLOCK / CONCERNS / CLEAN.

### `/verify` is a built-in that already implements repo-skill precedence

`/verify` is registered as a bundled **skill** (not a prompt string) — it loads `SKILL_MD` and
`SKILL_FILES` from a separate bundled chunk. Its description, verbatim:

> "Verify that a code change actually does what it's supposed to by exercising it end-to-end and
> observing behavior — drive the affected flow, not just tests or typecheck. Run before
> committing nontrivial changes; **bootstraps this repo's project verify skill if none exists
> yet.** Don't invoke it on a diff that only touches tests, docs, or other code with no runtime
> surface to drive (a change to product source always has one) — there's nothing to observe."

Two things follow. First, `/code-review` chains into it deliberately: "if `/verify` has NOT run
this session and the diff has a runtime surface (not test-only or docs-only per the pre-ship
exemptions), invoke `/verify` now — this review checks that the diff reads right; `/verify`
checks that it runs right." Second, **"bootstraps this repo's project verify skill if none exists
yet" is first-party precedent for the prefer-the-repo's-own-skill pattern**, including the
bootstrap fallback — the same shape as the `REVIEW.md` chain recorded for Q1.

### What this changes about the earlier findings

1. **Q7 is effectively answered.** CONFIRMED / PLAUSIBLE is not a fifth wb vocabulary — it is the
   harness's own, with a first-class rendering path (`ReportFindings`). A wb review skill that
   emits it is conforming, not inventing.
2. **Q1's premise shifts.** The generic rule catalogue `adversarial-review` was deferring to
   `review-reef` for is substantially covered by the built-in's Conventions angle, which already
   walks `~/.claude/CLAUDE.md`, the repo root `CLAUDE.md`, and every ancestor `CLAUDE.md` /
   `CLAUDE.local.md` of a changed file. What the built-in does **not** cover is a repo's own
   rule directory (reef's `.rules/`, 17 files) or a repo's false-positive kill list.
3. **A repo-supplied review-instruction file has official precedent** — `REVIEW.md`, consumed by
   Anthropic's hosted Code Review. That is a stronger discovery convention than globbing
   `.claude/skills/`.
4. **`review-strict` should not be treated as a known artifact.** It exists on this machine only
   as a dangling symlink, and nowhere as a distributed skill. `strict` as a *modifier* is the
   real pattern worth borrowing; `review-strict` as a *name* is not.
5. **The PR-lifecycle loop has no official or marketplace equivalent.** `adversarial-loop`'s
   draft → review → `gh pr ready` → bot → label sequence is genuinely absent from everything
   Anthropic ships and from every official plugin on disk.

### Follow-up Code References

- `/Users/scraig/.local/share/claude/versions/2.1.272` — built-in `code-review`, `simplify`,
  `security-review`, `verify`; `ReportFindings` (`rH`); effort table (`ae`); finder-budget formula
- `/Users/scraig/.claude/plugins/marketplaces/claude-plugins-official/.claude-plugin/marketplace.json` — 308 plugins
- `…/plugins/code-review/commands/code-review.md:1-5,20-28,33-42,52-91` — the official command
- `…/plugins/pr-review-toolkit/commands/review-pr.md:22-28,109-113` — aspect + `parallel` args
- `…/plugins/pr-review-toolkit/agents/code-reviewer.md:1-6,33-41` — `model: opus`, ≥80 floor
- `…/plugins/feature-dev/agents/code-reviewer.md:1-7` — `model: sonnet`, 3 parallel copies
- `https://code.claude.com/docs/en/code-review` — hosted service; `REVIEW.md` customization
- `https://code.claude.com/docs/en/github-actions` — trigger types, draft skipping, in-place edits

### Follow-up Open Questions

*All questions resolved as of 2026-09-17.*

| ID | Question | Blocks | State |
| -- | -------- | ------ | ----- |
| Q9 | Does the wb skill adopt `REVIEW.md` as the repo-supplied review-instruction convention (official precedent) instead of, or alongside, discovering a repo-local review skill? | The discovery mechanism | **Resolved 2026-09-17** → design.md (## Technical Decisions), collapsed into Q1 |
| Q10 | The built-in's behavior varies by **main-session model family** — under `claude-opus-5`, `medium` and `high` collapse to one minimal prompt and Opus 4.8 never spawns subagents. Does the wb wrapper account for that, and does `model-help`'s advice change because of it? | Whether the wrapper pins effort, model, or both | **Resolved 2026-09-17** → design.md (## Technical Decisions) |
| Q11 | Does the wb skill emit `ReportFindings` (host-UI rendering, `verdict`/`outcome` lifecycle) or its own markdown, given the tool's "use this only when the active code-review instructions tell you to" gate? | The output-format section | **Resolved 2026-09-17** → design.md (## Technical Decisions) |

## Follow-up Research 2026-09-18 — the fix-phase defect rate

**Facts only.** What the remedy should be is `design.md`'s question; this section records what
four adversarial review rounds against this branch measured. Every figure below is derived from
the plan documents and `git`, not from recollection.

### Findings per round, and where they sat

| Round | Findings | In surface the previous fix phase created or rewrote | Scope reviewed |
| ----- | -------- | --------------------------------------------------- | -------------- |
| 1 | 22 | — (first pass) | full diff, 6 legs |
| 2 | 22 | 14 (64%) | full diff, 6 legs |
| 3 | 12 | ~8 (67%) | scoped — ~12% of the surface, 2 legs |
| 4 | 20 | ~9 | scoped — Phase 9's rewrite, 4 legs |

Round 3 examined roughly an eighth of round 2's surface with a third of the lenses and returned
two thirds of its findings in code the previous round's fixes had written.

The round-2 figure was published twice before it was counted. An early note said "four of 22";
a later one said "a third". The itemised count is 14, recorded in the journal entry for
2026-09-18 and in `tasks.md` Phase 7. Both earlier figures understated it.

### Commit shapes of the two fix phases

Derived from `git show --name-only`:

| Commit | Files | Phase |
| ------ | ----- | ----- |
| `46b90f4` | 9 | Phase 6, tasks 1–9 |
| `410c908` | 7 | Phase 6, tasks 10–16 |
| `3e350e8` | 7 | Phase 6, tasks 17–21 |
| `1990b40` | 13 | **Phase 7, all 22 tasks** |

Phase 6 closed 21 tasks in three commits; Phase 7 closed 22 in one. In both phases the
repository's gates were run once, after the last change.

### Mirror-image regressions

Two findings were the inverse of a defect the same fix phase had just closed:

- Round 3 raised *"a fixed `/tmp/reply.md` is reused across runs"*. The Phase 7 fix used a
  `mktemp` template whose `X`s were not trailing, which on BSD returns a literal fixed path.
  Round 4 raised the same defect at the same `file:line`.
- Round 3 raised *"a guard on a later capture excuses an earlier unguarded one"*. The Phase 7
  fix produced *"a guard on an earlier capture excuses a later one"*. Round 4 raised it.

A third instance occurred inside Phase 9 and was caught before commit: the first draft of the
rewritten `check-guards` used `break` where `continue` belonged, reproducing the second item
above. The corpus case `s1-guard-on-earlier`, written before the implementation, failed.

### Files recurring across rounds

Three appeared in rounds 1, 2 and 3:

- `plugin/scripts/check-guards`
- `plugin/skills/adversarial-review/SKILL.md`
- `plugin/skills/reply-to-claude/SKILL.md`

`check-guards` also appeared in round 4, in six findings, after being rewritten.

### What the loop recorded between rounds

Nothing. At the time of measurement `adversarial-loop` instructed *"Record the disposition and
its evidence"* and named no destination; no step wrote one, and `adversarial-review` was
stateless per pass. There was no artifact from which round N−1's findings could be compared to
round N's.

### Measurements of the verification apparatus

- `test-guards` at the close of Phase 9 reported 12/12 mutations caught. An independent
  reviewer, given the implementation and not the corpus, wrote 24 mutations; 20 survived.
- Four of Phase 7's guard additions — the zero-file refusal, the `find`-stderr refusal, the
  missing-target check, and the `*/scripts/*` case arm — could each be deleted by a one-line
  edit with the suite still reporting green.
- Scored against mechanically generated mutations rather than author-written ones, the rebuilt
  `check-guards` killed 198 of 293.
