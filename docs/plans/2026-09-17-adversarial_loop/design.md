---
project: adversarial_loop
ticket: null
created: 2026-09-17
created_timestamp: 2026-09-17T17:51:46Z
status: approved
last_updated: 2026-09-17
designer: scraig
git_commit: 46ef587b084ea4d84a8a9b4e5b0770778903ba9b
git_branch: adversarial-loop-skill-research
repository: thescubageek/workbench
tags: [design, architecture, adversarial_loop]
depends_on: research.md
design_approach: Wrapper + lens injection, scaled by reconnaissance
---

# Design: adversarial_loop

**Created**: 2026-09-17 17:51 UTC
**Designer**: scraig
**Ticket**: N/A

<!-- Status lives in frontmatter `status:` only. Do not restate it here: it is the field
     /wb:create_tasks and forge gate on, it changes, and a second copy goes stale the moment
     the design is approved. `created` and `ticket` are repeated above because they never
     change after creation. -->

## Problem Statement

Two adversarial review skills exist on one machine as user-level skills and cannot be used by
anyone else, in any other repository, on any other machine. They are also partly broken where
they stand: `adversarial-review` is instructed to read `review-reef` for its rule catalogue,
org-guide digest and false-positive kill list, and that skill is a dangling symlink into a
directory that no longer exists. Both files are written against one Rails codebase — Turbo and
Stimulus, `belongs_to_yaml_model`, `bundle exec rubocop`, `~/.rbenv`, `Settings.utility.redis_url`,
`member` vs `staffer`, CA-only journeys, `en`/`es` parity.

The `wb` plugin has the mirror-image problem. It ships **no** review surface at all — no
`CONFIRMED`, no `claude[bot]`, no `gh pr ready`, no `origin/main` anywhere under `plugin/` — while
three shipped files already route work to a review-skill family that has never existed:
`daily-digest/SKILL.md:204` and `:278` send PR review to `pr-feedback` / `review` / `review-reef` /
`review-strict`, and `model-help/SKILL.md:160` carries a tiering anchor for `review-reef`. Those
lines have pointed at nothing since they were written.

Between the two sits machinery neither uses. A standard Claude Code install ships `/code-review`
(8–10 parallel finder subagents, a `CONFIRMED / PLAUSIBLE / REFUTED` vocabulary, the
`ReportFindings` structured-output tool, `--fix` and `--comment`), `/verify` (drives a change
end-to-end and bootstraps a repo's own verify skill when none exists), and `/security-review`.
Re-implementing any of that would be duplicated work that decays as the built-ins improve.

**Why now**: the review family is the one part of the daily workflow that lives entirely outside
the plugin, so it is the part that cannot be shared, versioned, or fixed once. Every week it stays
personal is a week the plugin's own routing points at skills that do not exist.

**If we do not solve it**: `daily-digest` keeps recommending nonexistent skills, `model-help`'s
calibration keeps anchoring on one, the adversarial pass stays unavailable in every repository but
one, and the accumulated review discipline — the reviewer-adjudication dispositions, the coverage
check, the proportionality gate — stays untracked in files no one else can read.

### Success Metrics

- A user with only the `wb` plugin installed can run an adversarial review in a repository that
  has never seen wb before, with no personal skills and no `REVIEW.md`, and get a report.
- `grep -rn "review-reef\|review-strict" plugin/` returns only deliberate references to skills the
  plugin actually ships.
- No Ruby, Rails, RSpec, Docker, Postgres, Redis or reef vocabulary appears anywhere under
  `plugin/` — the property the plugin holds today and must not lose.
- A small, unremarkable diff costs materially less than a wide or compliance-sensitive one, and
  the difference is driven by what the diff touches rather than by its size.
- The adversarial stance is present at every tier, including the cheapest.

## Design Approach

`wb:adversarial-review` is a **wrapper with an injection leg**. It does not re-implement code
review. It runs a cheap reconnaissance pass over the diff, uses that to size the work, invokes the
built-in `/code-review` for the generic sweep, fans out a small number of named domain-expert
lenses that the built-in does not have, then merges, dedupes, verifies and reports once through
`ReportFindings`.

`wb:adversarial-loop` is a **sequencer**. It owns ordering and gates, not review logic. Its local
core — review, adjudicate, fix, re-verify, re-review until clean — runs anywhere there is a diff.
Its PR phases engage only when a pull request already exists.

`wb:reply-to-claude` is a **small, independently invocable skill** for answering `claude[bot]`
with an explicit statement of what was accepted and what was pushed back on.

### Why This Approach

- **The built-in is not a thin reviewer, so wrapping beats rebuilding.** It already fans out
  8 finder angles at `medium`/`high` and 10 at `xhigh`/`max`, including a removed-behavior auditor,
  a cross-file tracer, an altitude check, and a Conventions angle that walks `~/.claude/CLAUDE.md`,
  the repo root, and every ancestor `CLAUDE.md`/`CLAUDE.local.md` of a changed file. Duplicating
  that is work that rots.
- **What it lacks is exactly what the personal skill had.** Named domain-expert lenses — the thing
  actually asked for out loud, "review as a principal frontend engineer" — and, in build 2.1.272, a
  wired-in verification pass: the three-state verifier prompt ships but the live effort paths read
  `Phase 2 — Dedup only (no verify)`.
- **It aligns with how this plugin already composes.** `forge/SKILL.md:180` states the principle:
  "a sequencer, not a re-implementation of the underlying `wb:*` stages. Always invoke the existing
  stages rather than duplicating their logic." This design applies the same rule outward, to
  built-ins.
- **The fan-out-then-synthesize shape is already the house pattern**, in
  `create_research/SKILL.md` Step 4 and `validate_execution/SKILL.md:110-126`, down to the barrier
  that governs waiting rather than spawning.
- **Varying agent count at runtime has precedent.** `fetch-issues/SKILL.md:99-103` spawns one
  research agent per open issue and picks haiku or sonnet per issue;
  `daily-digest/SKILL.md:95-99` spawns one collector per available source. Reconnaissance-driven
  fleet sizing is not a new idea here, only a new input to it.
- **Deciding a tier by its hardest part is already the plugin's rule.** `model-help/SKILL.md:42-49`
  scores across dimensions and takes the highest — "a task is only as cheap as its riskiest part" —
  and `daily-digest/SKILL.md:168` says "size to the hardest sub-problem." The max-not-mean tiering
  rule is that rule, applied to a diff.

## Technical Decisions

### Architecture

- **Two legs, one report.** A built-in leg (`/code-review` at a chosen effort) and a wb lens leg
  (N domain-expert agents), spawned together, merged into a single deduped, verified finding set.
  - Rationale: the built-in supplies breadth that would be expensive to rebuild; the lens leg
    supplies the domain framing it has no way to express.
  - Trade-off: two finding sets with different provenance must be reconciled, and only one of them
    arrives with a `verdict`.
  - Pattern reference: `plugin/skills/validate_execution/SKILL.md:110-126`.

- **A reconnaissance pass decides the shape, and it runs before anything is spawned.**
  - Rationale: fleet size is the dominant cost, and it is decided before any of it is paid. This is
    the `tracer-bullet` discipline (`plugin/skills/tracer-bullet/SKILL.md`), which
    `create_research/SKILL.md:110` already applies as a scoping probe.
  - Trade-off: one extra step on every review, including trivial ones.

- **Tier is derived from six signal axes, taking the maximum.** Path roles; behavioral deltas
  (deleted guards, changed defaults, widened permissions, new external calls); measured blast
  radius; coupling breadth; reversibility; test evidence.
  - Rationale: "LOC are not an indicator of complexity alone." A three-line permission change and a
    signature change with forty call sites are both small and neither is simple.
  - Trade-off: reconnaissance can be wrong, and a wrong tier is silent.
  - Pattern reference: `plugin/skills/model-help/SKILL.md:42-49`.

- **Lines changed is a within-tier tie-breaker only**, plus a pass-through hint to the built-in leg,
  which computes its own finder budget as `max(2, min(8, ceil(lines_changed/150)))`.

- **Certain lenses are mandatory on content, and pull the tier up with them.** Auth, permissions,
  params, uploads, external calls and PII-shaped data require the security lens; prompt text, skill
  files and agent definitions require the AI-systems lens; migrations and backfills require the data
  lens; a changed signature with callers outside the diff requires the cross-file tracer.
  - Rationale: this is what stops a twenty-line auth change being treated as simple.
  - Precedent: `adversarial-review/SKILL.md:60,62` already marks two of these mandatory.

- **The adversarial stance is constant across tiers; only the fleet varies.** At the lowest tier the
  built-in runs its hunk-only pass and a single wb stance agent covers the enclosing function,
  deleted invariants and blast radius.
  - Rationale: the built-in at `low` explicitly says "Do not flag style, naming, perf, missing
    tests, or anything outside the hunk", so layering the stance onto that invocation would
    contradict it. Two legs with explicitly different scopes dissolves the contradiction.
  - Trade-off: even a trivial review costs two agents rather than one.

- **`adversarial-loop` is a sequencer with a local core and PR-phase extensions.** Recorded in full
  under Resolved Decisions.

### Data Model

There is no database here; the "data" is the record shapes this design commits to.

- **The finding record is `ReportFindings`' schema, not a wb invention** — `file`, `line`,
  `summary`, `short_summary`, `failure_scenario`, `category`, `verdict` (`CONFIRMED` / `PLAUSIBLE`),
  `outcome` (`fixed` / `skipped` / `no_change_needed`), and a top-level `level`.
  - The `outcome` lifecycle is what lets `adversarial-loop` re-report between rounds instead of
    restating a whole review.
  - `category` uses the built-in's own kebab-case slugs — `correctness`, `simplification`,
    `efficiency`, `reuse`, `altitude`, `conventions`, `test-coverage`.

- **The reconnaissance assessment is a transient record**, not persisted: per-axis rating, the
  resulting tier, the selected lens set with the trigger that selected each, and the chosen effort.
  It is stated in the review's output so the sizing can be argued with.

- **The repo rule contract is `REVIEW.md`**, read from the base ref. It contributes rules and
  false-positive entries and may name a rules directory or a repo skill. It can add; it can never
  suppress a mandatory lens.

- **The "Checked and clear" coverage list has no `ReportFindings` field** and is carried in the text
  restatement. It is not a finding, so this does not violate the tool's "do not also print the
  findings as text" instruction.

### Integration Points

- **Built-in `/code-review`** — invoked with an effort level and a target. **This is the plugin's
  first invocation of a built-in Claude Code skill**; every existing cross-skill call is wb-to-wb
  (`forge` → stages, `create_research` Step 0 → `jira-context`, the `model-help` gate paragraph).
  There is no in-repo idiom to copy.
- **Built-in `/verify`** — owns fix-verification for `adversarial-loop`, including repo-command
  discovery and its own pre-ship exemptions.
- **`ReportFindings`** — the output channel, opted into explicitly because the tool gates itself on
  the active review instructions naming it.
- **`model-help`** — consulted in gate mode for a task-warranted upshift advisory, and gaining rows
  of its own so a review phase has a baseline.
- **`git` / `gh` / `Monitor` / `claude[bot]`** — required only by the PR phases of the loop, and
  hard where those phases engage.
- **Edited shipped files**: `review-prep/SKILL.md` (hand-off line), `daily-digest/SKILL.md:204,278`
  (repointed), `model-help/SKILL.md:160` plus its gate table (repointed and extended).
- **New shipped reference doc** under `plugin/docs/reference/`, holding the built-in's effort
  semantics and the model-family observation with a `Check it` command. It satisfies the four tests
  in `plugin/docs/reference/README.md`: more than one skill needs it, it is read at runtime, it
  states a contract, and linking beats restating.
- **Not integrated**: `wb-prime.sh`'s session-start orientation is a static heredoc that does not
  enumerate skills, so new skills require no registration there — and equally will not appear there
  unless the heredoc is edited by hand.

### Resolved Decisions

- **Repo-specific review knowledge is sourced through a `REVIEW.md` precedence chain**, not
  through skill discovery.
  - Rung 1: repo-root `REVIEW.md`, **read from the base ref** (`git show origin/main:REVIEW.md`),
    never the working tree or PR head. It may point at a rules directory (reef's `.rules/`) or
    name a repo skill to delegate to.
  - Rung 2: absent that, the built-in `/code-review` Conventions angle alone, which already walks
    `~/.claude/CLAUDE.md`, the repo root, and every ancestor `CLAUDE.md` / `CLAUDE.local.md` of a
    changed file.
  - Rationale: `REVIEW.md` is Anthropic's own documented extension point — the hosted Code Review
    service feeds it directly to its finding/verification/ranking agents — so a repo that writes
    one gets value from both that service and wb. Globbing `.claude/skills/` for "a review skill"
    mis-delegates on a case that exists today: reef ships `reef-dep-review`, a real review skill
    scoped to lockfile diffs, which would wrongly receive a feature-PR review.
  - Constraint: **a repo file can add, never suppress.** It contributes rules and false-positive
    entries; it cannot disable a mandatory lens. Otherwise the security lens on a
    compliance-sensitive diff is switched off by a careless config line, silently.
  - Constraint: **base-ref read is a security boundary.** This skill runs on other people's PRs;
    a PR that edits `REVIEW.md` to declare auth findings "known false positives" is a live
    prompt-injection attack on the reviewer itself.
  - Trade-off: a repo whose review knowledge lives in a skill must write a short `REVIEW.md` to
    be found. One-time cost, paid to avoid mis-delegation.
  - Source: research.md Q1 (collapses Q9) · Decided 2026-09-17

- **Trigger phrases stay narrow; `review-prep` gains a hand-off line.**
  - `wb:adversarial-review` triggers only on explicit adversarial phrasing — "adversarial
    review", "hunt for bugs in this branch", "review as a principal `<domain>` engineer", "is
    this finding accurate".
  - `plugin/skills/review-prep/SKILL.md:3` keeps its interactive triggers and gains one hand-off
    line pointing at `adversarial-review` for batch bug-hunting.
  - Bare "review" stays with the built-in `/code-review`, which ships `aliases:["review"]` — the
    collision is with a first-party command, not only with `review-prep`.
  - Rationale: someone who says "review my branch" wanting a batch hunt currently lands in a tmux
    walkthrough. One line fixes that without contesting a built-in alias.
  - Trade-off: `review-prep` joins the change set.
  - Source: research.md Q2 · Decided 2026-09-17

- **`adversarial-loop` has a local core plus PR-phase extensions; preconditions are hard at the
  boundary of whichever phases engage.**
  - The only universal precondition is **a reviewable diff**. Review → adjudicate → fix →
    re-review until clean runs with no `gh`, no PR, and no GitHub at all.
  - An **open PR is not required.** If one exists, the PR phases (flip to ready, `claude[bot]`
    rounds, label) join the loop; if not, the loop ends at clean and the user pushes when ready.
    This explicitly overrides the source skill's precondition
    (`adversarial-loop/SKILL.md:27-28`, "this skill starts at an open draft").
  - Where a PR phase **does** engage, its dependencies are **hard**: `gh` present and
    authenticated, `Monitor` available, `claude[bot]` installed. Stop with a clear message rather
    than silently running a narrower loop and calling it the same thing.
  - Rationale: `jira-context`'s best-effort posture fits a dependency that *enriches*. Here the
    dependency *is* the phase — a loop that silently skipped the bot round and reported success
    would be lying about what ran.
  - Inferred, flag if wrong: creating a PR stays out of scope, preserving the source skill's rule.
  - Source: research.md Q4 · Decided 2026-09-17

- **Fix-verification delegates to the built-in `/verify`; nothing stack-specific ships.**
  - After each fix round the loop invokes `/verify` rather than running tests or lint itself. No
    `docker info` / `pg_isready` / `redis-cli` probes, no `bundle exec rubocop`, no command table.
  - `/verify` discovers this repo's commands, drives the affected flow end-to-end, and
    "bootstraps this repo's project verify skill if none exists yet" — so the repo-specific
    problem is solved once, upstream, by the standard install.
  - wb inherits its pre-ship exemptions: skip on a diff with no runtime surface (docs-only,
    test-only).
  - Rationale: `implement/SKILL.md:385-389`'s "read the commands from `tasks.md`" precedent cannot
    carry here — on someone else's PR there is no `tasks.md`. `/code-review` already chains into
    `/verify` for exactly this division of labour: "this review checks that the diff reads right;
    `/verify` checks that it runs right."
  - Trade-off: the loop's fix-verification is only as good as `/verify` is in a given repo, and wb
    has no lever on that.
  - Source: research.md Q5 · Decided 2026-09-17

- **Three skills ship: `wb:adversarial-review`, `wb:adversarial-loop`, `wb:reply-to-claude`.**
  - `sclip` is dropped, not ported. Its only referent is `adversarial-review/SKILL.md:99`
    ("Offer `/sclip` instead"), a role `/verify` now owns.
  - `reply-to-claude` ships as a generic wb skill rather than being inlined into Phase 4: it is
    independently invocable, which matters because replying to `claude[bot]` happens outside the
    loop as often as inside it, and shipping it lets the reef-tied personal copy be deleted.
  - Genericising it is one line of work: `reply-to-claude/SKILL.md:49-50` is the only repo-tied
    content, and `claude[bot]` is Anthropic's app login everywhere while the repo comes from
    `gh repo view`.
  - Trade-off: a third skill directory, and `adversarial-loop` declares a cross-skill dependency.
  - Source: research.md Q6 · Decided 2026-09-17

- **The review normalizes to a model-independent shape, and leans on `model-help` to advise an
  upshift when the task warrants one.**
  - The tier fixes the *intended shape* — effective angle coverage, lens count, verification
    depth. The wrapper reaches that shape whatever model the session starts on, by choosing the
    effort token **and** by sizing the wb lens leg. Fan-out and lenses track complexity, not the
    starting model.
  - Separately, and non-blocking: `model-help` advises an upshift when the *task* warrants it
    (compliance/PHI, wide blast radius, one-way door) — consistent with the plugin's
    advise-never-auto-switch policy.
  - **Mitigation for the brittleness this buys**: the model-family mapping is an undocumented
    internal read from minified strings in build 2.1.272, so it does not get hardcoded inside the
    skill. It lives in one shipped reference doc — `plugin/docs/reference/` per `CLAUDE.md:34-35`
    — with a `Check it` command, the way `branch-naming.md` is the single authority for its rule.
  - **Prefer measuring to predicting**: where the wrapper can observe that the built-in leg came
    back thin, it tops up the wb lens leg rather than relying on the mapping being current. The
    mapping is the hint; the observed result is the authority.
  - Trade-off: accepted coupling to an undocumented internal, confined to one file with a
    verification command.
  - Source: research.md Q10 · Decided 2026-09-17

- **Output is `ReportFindings` plus a one-line-per-finding restatement, with a markdown fallback.**
  - Emit `ReportFindings` when the tool is present: `verdict` (CONFIRMED / PLAUSIBLE), `category`,
    `failure_scenario`, and the `fixed` / `skipped` / `no_change_needed` outcome lifecycle, which
    is what lets `adversarial-loop` re-report between rounds instead of restating a whole review.
  - Follow it with the restatement the built-in's own Opus-5 prompt specifies — "one line each,
    `file:line — summary` — so they stay visible in sessions that do not render tool output."
  - Fall back to markdown when the tool is absent.
  - The skill must **opt in explicitly**: the tool gates itself on "use this only when the active
    code-review instructions tell you to report findings with this tool."
  - Open detail for `create_design`: the "Checked and clear" coverage list has no `ReportFindings`
    field. It is not a finding, so carrying it in the restatement does not violate the tool's
    "do not also print the findings as text" rule.
  - Source: research.md Q11 · Decided 2026-09-17

- **`daily-digest` and `model-help` are repointed at the new skills; `review-strict` is not
  adopted as a name.**
  - `plugin/skills/daily-digest/SKILL.md:204,278` and `plugin/skills/model-help/SKILL.md:160`
    currently route to `pr-feedback` / `review` / `review-reef` / `review-strict`, none of which
    the plugin ships.
  - `review-strict` is not a distributed artifact anywhere — `registry.npmjs.org/review-strict`
    returns `{"error":"Not found"}` and no marketplace plugin or skill carries the name. The real
    convention in the wild is a `<language>-strict` suffix, not a review skill by that name. So
    those lines were pointing at nothing from the start and get repointed rather than preserved.
  - Source: research.md Q3 · Decided 2026-09-17

- **The finding vocabulary is CONFIRMED / PLAUSIBLE, because it is the harness's own.**
  - Not a fifth wb report vocabulary alongside `validate_execution`'s PASS/FAIL,
    `task-verifier`'s `### Status`, `review-prep`'s Review Summary and `fetch-issues`'s STATE
    table. The built-in ships the same three-state criteria verbatim (CONFIRMED / PLAUSIBLE /
    REFUTED, keep the first two, drop REFUTED), and `ReportFindings` renders it.
  - Source: research.md Q7 · Decided 2026-09-17

- **`model-help` gains gate rows for the review and PR-loop phases.**
  - Its gate-mode table (`plugin/skills/model-help/SKILL.md:94-103`) currently covers
    `create_research` through `validate_execution` and has no row for a review phase; the only
    applicable guidance is the free-text `review-reef` calibration anchor at `:160`.
  - Source: research.md Q8 · Decided 2026-09-17

- **A wb skill invokes a built-in through the `Skill` tool, and the built-in runs forked.**
  - Probed live on this plan's own working tree: `Skill(code-review, "low")` returned
    `Skill "code-review" completed (forked execution)` with three findings. The invocation idiom
    the design had no in-repo precedent for is simply the `Skill` tool, same as any wb-to-wb call.
  - "Forked execution" matches the built-in's own `getContext` branch, so the review does not
    consume the calling session's context — which is what makes the two-leg design affordable.
  - Consequence for the design: the wrapper leg is real. Had this failed, the design collapsed to
    re-implementing the sweep.
  - Source: design.md A1 · Validated 2026-09-17

- **The verification pass is wb's to supply in this build.**
  - The three-state verifier prompt ships (`Phase 2 — Verify (1-vote, 3-state)`, with
    CONFIRMED / PLAUSIBLE / REFUTED criteria) but the live per-level composers read
    `Phase 2 — Dedup only (no verify)` and `Phase 2 — Dedup and self-check (no subagent verify)`,
    and the xhigh/max text says "a single non-REFUTED vote carries the finding. Do NOT drop on
    uncertainty."
  - Scoped to build 2.1.272 and read from minified strings, which is exactly why the observation
    lives in a reference doc with a `Check it` command rather than in the skill body.
  - Source: design.md A2 · Validated 2026-09-17

- **The base-ref read works, and an absent `REVIEW.md` is a normal outcome rather than an error.**
  - `git show origin/main:<path>` succeeds for a tracked file; for a missing one it exits non-zero
    with `fatal: path 'REVIEW.md' does not exist in 'origin/main'`. The skill treats that exit as
    "this repo has no REVIEW.md" and falls to the next rung — it is not a failure to report.
  - `origin/main` resolves locally, including for a fork's PR, because the base ref belongs to the
    upstream being reviewed.
  - Source: design.md A5 · Validated 2026-09-17

- **The personal `~/.claude/skills/adversarial-review`, `adversarial-loop` and `reply-to-claude`
  are deleted once the wb versions ship and are confirmed working.**
  - Rationale: one skill per name. These three differ from the six existing personal/plugin
    collisions in that the personal copies are **readable**, so they enumerate alongside the wb
    ones with near-identical descriptions, and model-driven selection between them is undetermined.
    Deleting removes the condition rather than testing it.
  - **Sequencing constraint**: the personal files are the port's source material and are not
    reproduced in full anywhere in this repository. They are deleted **after** the wb versions
    exist and are verified — never before, or the source is gone.
  - Trade-off: no fallback to the personal versions if the wb ones regress. Accepted; the wb
    versions live in git.
  - Source: design.md PD1 (settles A3) · Decided 2026-09-17

- **One release: `2.2.0`, carrying the adversarial skills and the separate fixes together.**
  - `plugin/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` both move
    `2.1.0 → 2.2.0`; they must match.
  - Minor rather than patch because `CLAUDE.md` maps adding skills to the features case.
  - **Not `3.0.0`**: `CLAUDE.md` and all three deprecated alias stubs promise those aliases are
    removed at 3.0.0. Bumping there would either force that removal into this change or break a
    published promise.
  - Trade-off: the journal-ordering fix waits for the feature rather than shipping on its own.
  - Source: design.md PD2 · Decided 2026-09-17

- **Both legs produce candidates; the pooled set is deduped once and verified once.**
  - Provenance is metadata, not status. A finding from the built-in leg has no more standing than
    one from a wb lens until it has been verified.
  - Dedupe predicate is the built-in's own: *same defect, same location, same reason → keep one.*
    Borrowed rather than invented, so the two legs' outputs collapse on the same rule the built-in
    already applies internally.
  - The three-state verify then runs over the whole pooled set. Everything reported carries a wb
    verdict and a concrete failure scenario, whichever leg surfaced it.
  - Rationale: A2 established that no live effort path verifies in this build, and the built-in's
    own xhigh text says "a single non-REFUTED vote carries the finding. Do NOT drop on
    uncertainty." Passing those through as pre-verified would import exactly the gap wb exists to
    close.
  - Trade-off: verification is paid over both legs, not one.
  - Source: design.md PD3 · Decided 2026-09-17

- **Lens count is whatever the diff's content triggers; 6 is a runaway guard, not a target.**
  - No floor, no target count. A lens with nothing to look at returns noise, so the diff caps the
    fleet on its own.
  - If more than six trigger, run the six highest-risk and **name the dropped lenses and why** in
    the report. Because mandatory lenses are highest-risk by construction, the ranking never drops
    one — the guard bites only on discretionary lenses.
  - **Tiers have no numeric cut-points.** The tier is the maximum of the six axis ratings; the
    axis definitions *are* the cut-points. This follows from rejecting LOC as a selector — a range
    would reintroduce the thing that was rejected.
  - Trade-off: cost per review is bounded only loosely, by what the diff touches.
  - Source: design.md PD4 · Decided 2026-09-17

- **Argument surface: one type-sniffed positional target, effort as a named override flag.**
  - `argument-hint: "[<pr#>|<branch>|<path>] [--effort=<low|medium|high|xhigh|max>]"`.
  - The positional is sniffed the way `forge/SKILL.md:64` sniffs path-vs-ticket-vs-empty; the flag
    is stripped before positional binding and matched by name, order-independent, per
    `implement/SKILL.md:32-36`. This avoids the enumerated-slot-then-sniffed-slot combination,
    which has no idiom anywhere in the plugin.
  - Rationale: reconnaissance sizes the work by design. A required effort positional would invite
    overriding the thing the design just built; a flag reads as the override it is.
  - **Named lenses stay a natural-language affordance, not a flag.** "review as a principal
    frontend engineer" is already an advertised trigger, and the source skill's rule holds: if the
    user named lenses, use them verbatim rather than substituting your own.
  - Trade-off: no machine-readable way to pin a lens set.
  - Source: design.md PD5 · Decided 2026-09-17

- **The effort token is chosen from published semantics; the model-family mapping is demoted to a
  dated observation about prompt-cell selection.**
  - Established by tracer bullet, not inference: on `claude-opus-5`, `/code-review high` returned
    seven findings with a scope statement and severity ranking against `low`'s three. Coverage
    broadened as documented, on the exact family where the extracted routing table predicted
    `high` would collapse into the same minimal `o5-bmin` cell as `medium`.
  - **The mapping was not wrong so much as narrower than it was being asked to be.** Effort
    plausibly drives two levers — which prompt cell is selected, *and* the reasoning effort the
    review runs at — and the extracted table only ever described the first. It is kept, scoped to
    prompt-cell selection, with its `Check it` and an explicit note that it did not predict
    observed review breadth.
  - **Weakness in the evidence, recorded rather than smoothed over**: the `high` run's own scope
    line covers commit `46ef587` *plus* the working tree, a wider scope than the `low` run took,
    and the tree gained seven lines between runs. Some of 3 → 7 is plausibly scope, not effort.
    One observation per level, on stochastic output.
  - Not probed further because the decision is robust either way: the token comes from published
    semantics, and the design already observes whether the built-in leg came back thin and tops up
    the lens leg — which fires regardless of *why* it was thin.
  - Source: design.md A4 · Validated 2026-09-17

- **A review round's remediation lives under the plan it reviews, not inside it**:
  `docs/plans/<plan>/reviews/<date>-round-N/tasks.md`, with a findings ledger at
  `docs/plans/<plan>/review-log.md`.
  - **Decided against the single-surface arrangement because it demonstrably broke**, not on
    preference. At the time of deciding, this plan's own frontmatter read `current_phase: 5,
    68/80` while work was happening in Phase 8 — the "first unchecked task" rule pointed at the
    release tasks that had been deliberately blocked, and the session-start hook reported that
    to every new session. The plan began at 29 tasks and reached 80; **51 of the 80 were review
    remediation**, so `68/80` no longer answered the question the plan exists to answer.
  - **Nested, not a sibling plan directory.** Verified mechanically: `wb-prime.sh:81` globs
    `docs/plans/*/` at exactly one level, so `reviews/<round>/tasks.md` is invisible to it. A
    sibling `docs/plans/<date>-review/` would sort newer and silently *become* the active plan,
    hiding the original — a worse defect than the one being fixed.
  - **A remediation plan is not a project.** It has no research or design stage: the review is
    the research and the findings are the design input. Routing it through `create_project`
    would produce a `research.md` and `design.md` that exist only to be empty.
  - **Per-round directories make the circuit breaker mechanical** — round N's ledger reads round
    N−1's as a sibling, so "has the introduced-rate decayed?" is a computation rather than a
    judgement.
  - **Cost, accepted rather than hidden**: two status surfaces, in a repository whose stated rule
    is that status lives in the plan. Mitigated by one *one-directional* link — the parent plan's
    Implementation Notes gains a line per round — because two-directional links drift.
    `validate_project` must also tolerate a `tasks.md` with no `research.md`/`design.md` beside
    it; that is a real change, not free.
  - Source: tasks.md Q8-1 · Decided 2026-09-18

- **A finding's acceptance criterion is mechanical wherever one can be written, and an
  attestation wherever one cannot — never a check that cannot fail.**
  - The governing rule is `verification-before-completion`'s FALSIFY step applied to the
    criterion itself: **what would this print if the fix were absent?** If that has no answer,
    there is no criterion, and the finding is category 6 below rather than a fabricated check.
  - Six shapes:

    | | Finding shape | Acceptance criterion |
    | - | ------------- | -------------------- |
    | 1 | Has a fenced command | Execute the block **as written**; assert the stated outcome |
    | 2 | Defect in a shell script | A case in `test-guards` / `test-count` that fails before and passes after |
    | 3 | Two files contradict | **Dual grep** — the wrong phrasing absent *and* the right phrasing present at a named `file:line` |
    | 4 | Something missing | Grep for presence at the expected location, plus a negative control proving the grep can fail |
    | 5 | Reference integrity | A resolver script — dangling links, undefined identifiers, nonexistent skill names |
    | 6 | Genuine judgement | **No mechanical criterion.** Label `(attestation)`, name who must look |

  - **Run the criterion before the fix, not only after.** For shape 1 that is the RED step, and
    it is what three review rounds never did: `$target` is read seventeen times and assigned
    nowhere, and the three-`range=` block overwrote itself — both would have fallen out the first
    time anyone executed those blocks as written.
  - **Absence is not a check on its own** (shapes 3 and 4): a grep returning nothing passes for
    wrong path, wrong pattern and wrong encoding as readily as for success. Hence the dual
    assertion and the negative control.
  - **Evidence the escape hatch is rare, not a loophole**: all 11 open round-3 findings were
    classified against this and **every one lands in shapes 1–5** — five test cases, two
    executable blocks, two dual-greps, one resolver, one mixed. Zero required attestation.
    Rounds 1–2 carried more prose-judgement findings, so it will not always be zero; it was never
    the majority.
  - Source: tasks.md Q8-2 · Decided 2026-09-18

- **`check-guards` is rebuilt on candidate C's approach — real CommonMark fence parsing plus
  substitution-span analysis — rather than patched a fourth time.**
  - Decided on the spike's two scores, read against a pre-registration written before any
    candidate existed: corpus 97% vs A's 89%, mutation survivability 87% vs A's 50%.
  - **The cross-check is what makes it decisive**: A's four surviving mutations are exactly the
    four round 3 found by hand. An independent method reproduced that finding, so the second
    score is measuring something real rather than flattering the new implementation.
  - **`shellcheck` was rejected as the engine**, and not because it is bad: `SC2312` flags every
    masked return value, so it fires on `n=$(count foo f) || exit 2` and on `[ -e "$x" ] ||
    continue` alike — 10 false positives against 15 correct files — and missed the unquoted
    `--include` glob entirely. Filtering it to these three shapes means re-implementing the
    policy layer, which is the part that keeps breaking.
  - **What the spike did not decide, and this decision inherits**: candidate C is a ~130-line
    probe with no tests of its own, one known false positive (`ok-status-next-line`, which needs
    next-line lookahead for `$?`) and one uncovered mutation (the fence closer — a corpus gap,
    not an implementation gap). The rebuild is a phase with the corpus as its acceptance
    criteria, not a copy of the spike.
  - **Consequence for remediation**: the six open round-3 findings inside `check-guards` are
    closed **by replacement**, not fixed. Only the non-`check-guards` findings are planned.
  - Source: thoughts/2026-09-18-check-guards-implementation-probe.md · Decided 2026-09-18

- **`shellcheck` is adopted as an independent linter for the plugin's own shell scripts**, a
  separate question from the engine decision above and answered differently.
  - Default severity only — `-o all` is what produces the noise, and the noise is what gets a
    gate switched off.
  - Scoped to actual scripts. The naive `plugin/scripts/*` glob feeds `README.md` to the parser
    and produces seven spurious errors; the scope must exclude `.md`.
  - It already earns its place: a default run found `cd` without `|| exit` in
    `plugin/scripts/check:17` and `check-guards:35` — a failed `cd` scans the wrong tree — and
    two dead assignments at `test-count:68-69` left behind by the P7-T15 rewrite.
  - **Those findings are not fixed ad hoc.** They enter the remediation plan like any others,
    which is this phase's own discipline applied to its own output.
  - Source: tasks.md P8-T5 · Decided 2026-09-18

- **The circuit breaker is a trend test, blocking on its two narrow triggers and advisory on the
  wide one, computed from the ledger rather than judged by the session.**
  - **Blocking**: a **mirror-image regression** (a new finding that is the inverse of one already
    fixed), and the **introduced-rate failing to fall** between two consecutive rounds.
    **Advisory**: the **same file** appearing in three consecutive rounds — that has legitimate
    causes (a large file, a file under active development, the file the work is *about*).
  - **Blocking here, despite the plugin's non-blocking advisory precedent, because the failure
    mode is different.** A model advisory is a cost optimisation — getting it wrong wastes
    tokens. This guards against continuing to ship defects while believing you are fixing them.
    The decisive evidence is that a human had to notice: with an advisory the session would have
    printed a line and carried on, because every individual fix looked reasonable.
  - **Blocking means stop and surface, not refuse.** The user says proceed and it proceeds. The
    asymmetry that matters is that a block requires an answer while an advisory can be stepped
    past silently.
  - **Computed, not judged.** `introduced_by` is derived from
    `git diff <previous-round-base>..HEAD --name-only`. A breaker the session evaluates for
    itself is the loop marking its own homework — the failure this plugin already names as
    *"'Checked and clear' is a set of claims, not coverage"*.
  - **A trend test, not a threshold.** Fire on *"the rate did not fall from round N−1 to N"*, not
    on *"the rate exceeds X%"*. Scale-free, needs no magic number, and it transplants. This
    plan's own data — `—, 64%, 67%` — trips a direction test without anyone having guessed 60%.
    It is also the correct shape: the original diagnosis was that *the gate is a level test and
    so cannot see oscillation*, and fixing that with another level test would repeat the mistake.
  - **Minimum-N floor.** Below three findings in a round the rate is meaningless — 1 of 2 is 50%
    and says nothing. Below the floor, do not evaluate the trend.
  - **Provenance ships with the numbers.** Any threshold is recorded as *"derived from this plan,
    rounds 1–3, n=1"*. One repository, one plan, prose-heavy, with the same model reviewing and
    fixing. The **relation** generalises — a mirror-image regression is a semantic relation, not
    a rate. The **numbers** do not: a repository with real tests would start far below 64%.
  - Source: tasks.md Q8-3, Q8-4 · Decided 2026-09-18

## Scope Definition

### In Scope

- Three new shipped skills: `wb:adversarial-review`, `wb:adversarial-loop`, `wb:reply-to-claude`.
- One new shipped reference doc under `plugin/docs/reference/` covering the built-in review
  machinery's effort semantics and the model-family observation, with a `Check it` command.
- Edits to three shipped skills: `review-prep` (hand-off line), `daily-digest` (repoint both
  review-family references), `model-help` (repoint the calibration anchor, add gate-mode rows for
  the review and PR-loop phases).
- Genericising `reply-to-claude` so it carries no repository-specific content.
- A version bump in `plugin/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, which
  is how new skills reach an installed user at all.

### Out of Scope

- **Porting `sclip`.** Its only referent was `adversarial-review/SKILL.md:99`, a role `/verify`
  now owns.
- **Creating pull requests.** The loop starts from whatever exists and never opens a PR.
- **The hosted Code Review GitHub App.** A separate, Team/Enterprise, server-side product; this
  design consumes the same `REVIEW.md` convention but does not configure or depend on it.
- **GitLab.** The built-in's `--comment` has a `glab` path; nothing in this design targets it.
- **Re-implementing any part of `/code-review`, `/verify` or `/security-review`.**
- **Fixing the plugin's journal-ordering defect.** Discovered during this stage and fixed
  separately; it is unrelated to review and belongs in its own commit.
- **Anything that would delete the personal `~/.claude/skills/adversarial-*` copies before the wb
  versions are verified.** PD1 moved their removal *into* scope, but strictly ordered last: those
  files are the port's source material and are not reproduced in full in this repository.

## Success Criteria

### Functional Requirements

- [ ] An adversarial review runs in a repository with no `REVIEW.md`, no personal skills, and no
      plan directory, and produces findings.
- [ ] A review on a small, low-risk diff runs a materially smaller fleet than one on a wide or
      compliance-sensitive diff, and the report states which tier was chosen and why.
- [ ] A diff touching auth, params, uploads, external calls or PII-shaped data always runs the
      security lens, whatever its size.
- [ ] A diff touching prompt text, skill files or agent definitions always runs the AI-systems lens.
- [ ] Every reported finding carries a concrete failure scenario; anything without one is dropped.
- [ ] A repository supplying a `REVIEW.md` has its rules and false-positive entries honoured, read
      from the base ref, and cannot thereby disable a mandatory lens.
- [ ] `adversarial-loop` completes a review-to-clean cycle with no `gh`, no PR and no GitHub.
- [ ] Where a PR exists, the loop stops with a clear message rather than silently skipping a PR
      phase whose dependency is missing.
- [ ] `daily-digest` and `model-help` route only to skills the plugin ships.

### Non-Functional Requirements

- [ ] **Portability**: no Ruby, Rails, RSpec, Docker, Postgres, Redis or employer-specific
      vocabulary in any shipped file — the property `plugin/` holds today.
- [ ] **Consistency across models**: fan-out and lens selection track diff complexity, not the
      session's starting model.
- [ ] **Containment of coupling**: every dependence on an undocumented harness internal lives in
      one reference doc, each with a command that shows whether it is still true.
- [ ] **Honest reporting**: a review that ran a narrower fleet than its tier implies says so, in
      the same way the built-in discloses a single-pass run.
- [ ] **Security**: repo-supplied review instructions are read from the base ref, and PR titles and
      bodies are treated as untrusted data that can never lower a tier.

## Risk Analysis

### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| The built-in's internals drift — effort cells, angle counts, the model-family table | Med | High | Confine the mapping to one reference doc with a `Check it` command; prefer measuring the built-in leg's actual output over predicting it |
| The personal `~/.claude/skills/adversarial-*` copies shadow or out-compete the shipped skills | High | Med | PD1; `.claude/wb/knowledge.md` records that user-level copies won over plugin skills before, non-deterministically |
| No precedent for invoking a built-in from a wb skill — the idiom may not work as written | High | Med | A1; cheapest probe in the plan, and it gates everything else |
| Two legs cost more than one on every review | Med | High | Reconnaissance tiering exists for this; the lowest tier is two agents total |
| `ReportFindings` absent or ungated in some sessions | Low | Med | Markdown fallback, already decided |
| `/verify` is weak or unbootstrapped in a given repo, so fix-verification is thin | Med | Med | Report it plainly rather than implying verification happened |
| A `REVIEW.md` is used to suppress findings on a fork's PR | High | Low | Base-ref read plus add-never-suppress, both recorded as constraints |
| Three new skills ship but users never see them without a version bump and an explicit update | Med | High | Version bump is in scope; `CLAUDE.md`'s release steps are explicit that nothing else works |

### Assumptions

*All assumptions resolved as of 2026-09-17.*

Assumptions this design rests on, usually from research's knowledge gaps. This table is the
record — there is no external tracker.

| ID | Assumption | Validated? |
| -- | ---------- | ---------- |
| A1 | A plugin skill can invoke a built-in (`/code-review`, `/verify`) via the `Skill` tool and receive its findings back usefully. Nothing in `plugin/` has ever done this; if false, the wrapper leg is impossible and the design collapses toward re-implementing the sweep | Validated 2026-09-17 |
| A2 | In build 2.1.272 no live effort path calls the three-state verifier, so wb's verification pass adds real coverage. Read from minified strings. If false, the verify leg is redundant work | Validated 2026-09-17 |
| A3 | The shipped `wb:adversarial-review` is actually reachable while the same-named personal skill exists. If false, the whole feature is invisible on the one machine that most wants it | Resolved 2026-09-17 — PD1 removes the condition |
| A4 | The built-in's effort semantics (`low`/`medium` precision, `high`→`max` coverage) are stable even though the internal cell mapping is not. If false, the effort token cannot be chosen from documented behaviour and the mapping must move into the skill | Validated 2026-09-17 |
| A5 | `git show <base-ref>:REVIEW.md` is available in the environments where reviews run, including on a PR from a fork. If false, the base-ref security boundary needs another mechanism | Validated 2026-09-17 |
| A6 | Sub-agent lens tiering can only select among `haiku`, `sonnet`, `opus`, `fable` — the Task tool's `model` is an enum, per `.claude/wb/knowledge.md`. Any lens ladder naming Opus 4.8 versus Opus 5 collapses to one value | Validated 2026-09-17 |

- **IDs are local and stable**: `A1`, `A2`, … in the order raised, never renumbered.
- **State the consequence.** An assumption worth a row is one where being wrong changes the
  design; if being wrong changes nothing, it is background, not an assumption.
- **Validating is an edit, not a new record.** `/wb:resolve_questions` flips the cell to
  `Validated YYYY-MM-DD`, or to `Invalid — [note]` with what the answer forces to change.
  Rows are never deleted.

## Rejected Alternatives

Carried across from `thoughts/2026-09-17-adversarial-review-architecture.md`, where each was argued
rather than invented here.

### Option: Thin conductor

- **Approach**: delegate the entire pass to `/code-review`, and add only adjudication of its
  output plus the three-state verification.
- **Rejected because**: it can only comment on the built-in's findings, never add a lens to the
  fan-out. A compliance, accessibility or AI-systems lens cannot be expressed as an annotation on
  someone else's finding set.
- **Trade-offs**: would have been the smallest file with no duplicated taxonomy and free inheritance
  of Anthropic's improvements; gives up the named domain framing that is the feature's point.

### Option: Modifier-only, no review skill

- **Approach**: ship the selector rather than the reviewer — decide which review runs and at what
  effort, layering adversarial modifiers onto whichever was picked, then hand off.
- **Rejected because**: the hunt list, the reviewer-adjudication dispositions and the coverage
  check would have nowhere to live but a reference doc; verify-only mode disappears; "run just the
  adversarial pass" stops being invocable.
- **Trade-offs**: smallest surface and nothing to keep in sync with the built-in's taxonomy.

### Option: LOC-driven tiering

- **Approach**: select the tier arithmetically from lines changed.
- **Rejected because**: line count is not complexity. A three-line permission change and a
  signature change with forty call sites are both small and neither is simple, and the failure mode
  is silent under-review of exactly the diffs that most need it.
- **Trade-offs**: would have been trivially cheap to compute and fully deterministic.

### Option: Fuzzy repo-skill discovery

- **Approach**: glob `<repo>/.claude/skills/` for a review skill and prefer it.
- **Rejected because**: it mis-delegates on a case that exists today — reef ships
  `reef-dep-review`, a genuine review skill scoped to lockfile diffs, which would wrongly receive a
  feature-PR review. Making it safe requires a naming contract, and once a contract is needed a
  declared file is the simpler one.
- **Trade-offs**: zero setup for repos that already have such a skill.

### Option: Hardcode the built-in's model-family routing table

- **Approach**: encode the effort-cell mapping in the skill so a tier always yields the intended
  fan-out shape on any model.
- **Rejected because**: the table is an undocumented internal read from minified strings in one
  build; a shipped skill encoding it rots silently, and the failure mode is a review that quietly
  does less than it claims.
- **Trade-offs**: would guarantee the intended shape today. Kept in weakened form — the mapping
  lives in one reference doc with a verification command, and observation of the actual result
  outranks it.

## Pending Decisions

*All pending decisions resolved as of 2026-09-17.*

Design decisions that need stakeholder input before execution can start. This table is the
record — there is no external tracker.

| ID | Decision Needed | Blocks | State |
| -- | --------------- | ------ | ----- |
| PD1 | What happens to the personal `~/.claude/skills/adversarial-review`, `adversarial-loop` and `reply-to-claude` — deleted, left in place, or replaced with a pointer. Bears directly on A3, since the shipped skills may be unreachable while they exist | validating the feature works at all on this machine | Resolved 2026-09-17 → design.md (## Technical Decisions) |
| PD2 | Version bump size for three new skills plus a new reference doc. `CLAUDE.md` offers only "1.0.0 → 1.1.0 for features"; no major-bump trigger is documented | the release step, and therefore any installed user seeing the skills | Resolved 2026-09-17 → design.md (## Technical Decisions) |
| PD3 | The merge and dedupe rule between the built-in leg and the lens leg — two finding sets with different provenance, only one carrying a `verdict` before wb's verify pass runs | writing the review skill's synthesis section | Resolved 2026-09-17 → design.md (## Technical Decisions) |
| PD4 | Exact tier cut-points and the lens cap. Four normally and six at the top tier was proposed and never ratified; the underlying rule — lenses match what the diff touches, and a lens with nothing to look at returns noise — is settled | writing the reconnaissance section | Resolved 2026-09-17 → design.md (## Technical Decisions) |
| PD5 | Whether the new skills carry `argument-hint` for an enumerated effort slot followed by a type-sniffed target. No shipped skill combines an enumerated first slot with a sniffed second slot, so there is no idiom to copy | the skills' frontmatter and argument-parsing sections | Resolved 2026-09-17 → design.md (## Technical Decisions) |

- **IDs are local and stable**: `PD1`, `PD2`, … in the order raised, never renumbered.
- **Resolution goes in `State`, never in `Blocks`.** `/wb:resolve_questions` sets State to
  `Resolved YYYY-MM-DD → design.md (## Technical Decisions)`. `Blocks` keeps saying what the
  decision blocked — overwriting it destroys the record of why the row mattered, which is the
  half of the audit trail that is hard to reconstruct later.
- **A row needs a real blockee.** If nothing is blocked, it is a preference, not a pending
  decision — decide it here and record it under Technical Decisions.

Note: Decisions blocking execution should be resolved before `/wb:create_tasks`.

## References

- Research: [research.md](research.md)
- Exploration: [thoughts/2026-09-17-adversarial-review-architecture.md](thoughts/2026-09-17-adversarial-review-architecture.md)
- Tasks: [tasks.md](tasks.md)
- Repository knowledge: `.claude/wb/knowledge.md` — the Task tool `model` enum entry bears on A6
- Reference-doc contract: `plugin/docs/reference/README.md`
