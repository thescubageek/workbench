---
created: 2026-09-17
type: exploration
project: adversarial_loop
topic: how a shipped, repo-agnostic adversarial review relates to Claude Code's built-in review machinery
status: decided
---

# Exploration: how a shipped adversarial review relates to the built-in review machinery

## Decision Record

**Chosen direction**: **Wrapper + lens injection, scaled by reconnaissance.** `wb:adversarial-review`
invokes the built-in `/code-review` for the generic sweep and, in the same message, fans out a
small number of named domain-expert lenses the built-in does not have. Findings from both legs
are merged, deduped, verified with a three-state vote, and reported once. How many lenses run,
and at what effort, is decided by a cheap reconnaissance pass over *what the diff touches* — never
by line count alone.

**Rationale**: in the user's terms — "we want to borrow, not steal, but leverage anything that is
part of the standard Claude install", and "not every review warrants a full scale out of all the
lenses (we should only use those appropriate), and simpler PRs should downshift to the
`low`/`medium` effort with only one or two agents used as needed — but should still maintain the
adversarial stance." The built-in already supplies proven angle coverage (8 finder angles at
`medium`/`high`, 10 at `xhigh`/`max`, including a removed-behavior auditor and a Conventions angle
that walks every ancestor `CLAUDE.md`). What it does not supply is the named domain-expert
framing — "review as a principal frontend engineer" — which is the thing actually reached for, and,
in build 2.1.272, a wired-in verification pass.

**Rejected**:

- **A — thin conductor** (delegate the whole pass to `/code-review`, add only adjudication) — it
  can only adjudicate the built-in's output, never add a lens to the fan-out. That forecloses the
  differentiator: a compliance, a11y, or AI-systems lens cannot be expressed as a comment on
  someone else's findings.
- **C — modifier-only, no review skill** (ship the selector, hand off) — the hunt list, the
  Phase 1.5 adjudication disciplines and the coverage check would have nowhere to live but a
  reference doc, verify-only mode disappears, and "run just the adversarial pass" stops being
  invocable. The selector is worth having, but it is not the whole product.
- **LOC-driven tiering** (rejected mid-discussion, and it had been in the author's own first
  draft) — "LOC are not an indicator of complexity alone." A three-line permission change and a
  signature change with forty call sites are both small and neither is simple.
- **Fuzzy repo-skill discovery** — globbing `<repo>/.claude/skills/` for "a review skill"
  mis-delegates on a case that exists today: reef ships `reef-dep-review`, a genuine review skill
  scoped to lockfile diffs, which would wrongly receive a feature-PR review.
- **Hardcoding the built-in's model-family routing table** — kept out of the skill body and
  confined to one reference doc with a `Check it` command, because it was read from minified
  strings in one build and will drift silently.

**Revisit if**: the built-in's verify pass becomes wired into live effort paths. The three-state
verifier prompt (`CONFIRMED / PLAUSIBLE / REFUTED`) already ships in build 2.1.272 but no live
effort path appears to call it; the live composers say `Phase 2 — Dedup only (no verify)`. If
Anthropic wires it up, the verification half of the wb layer becomes redundant and this collapses
toward direction A. Also revisit if the built-in gains a lens/persona extension point — that would
make the injection leg unnecessary.

**Decided**: 2026-09-17, with scraig, after 4 rounds of discussion.

---

## The Decision Space

**What is actually being decided**: how a shipped, repo-agnostic adversarial review obtains its
coverage — by re-implementing a review, by delegating to the built-in, or by wrapping it and
adding what it lacks.

**What is NOT being decided here**: the repo-specific rule source (settled separately as the
`REVIEW.md` chain, `research.md` Q1/Q9); `adversarial-loop`'s preconditions (Q4); fix-verification
(Q5); the shipped skill count (Q6); output format (Q7/Q11); `model-help` rows (Q8). All of those
were walked through `/wb:resolve_questions` and are recorded in `design.md`.

**Constraints that bound any answer**:

- A shipped skill may link only into `plugin/docs/reference/`; nothing under root `docs/` is read
  at runtime (`CLAUDE.md:34-35`).
- No Rails/RSpec/reef vocabulary ships — `plugin/` currently has zero hits for
  `rspec|rubocop|bundle exec|rails|docker|psql|redis|ruby`.
- Optional dependencies are best-effort and non-blocking (`jira-context/SKILL.md:20-22`,
  `create_research/SKILL.md:80`).
- **From the user**: the skill runs on other people's PRs, so it cannot assume a plan directory,
  a design document, or an author to ask. This is the first wb skill with no `research.md` /
  `design.md` / `tasks.md` to read.
- **From the user**: behavior should be "same-ish in terms of fan out and lenses based on
  complexity regardless of starting model."

**What would make this decision wrong**: if the built-in `/code-review` were a thin single-pass
reviewer. It is not — it fans out 8–10 finder subagents with a taxonomy that overlaps
`adversarial-review`'s hunt list substantially, which is exactly why wrapping beats
re-implementing. Conversely, if `/code-review` ever gained user-supplied lenses, the injection leg
would be dead weight.

## Directions Considered

### A — Thin conductor

- **Shape**: resolve target → pick the repo override → invoke `/code-review` at a mapped effort →
  add only what it doesn't do: the three-state verify pass over its candidates, plus
  `adversarial-loop`'s Phase 1.5 adjudication. Emit `ReportFindings` with `verdict` set.
- **Precedent**: `plugin/skills/forge/SKILL.md:178` — "a sequencer, not a re-implementation".
- **Buys**: no duplicated taxonomy, inherits Anthropic's improvements for free, small file.
- **Costs**: inherits the model-family routing, so the effort modifier is partly inert on Opus 5
  where `medium` and `high` resolve to the same minimal cell; and no lens can be added to the
  fan-out, only commented on afterwards.
- **Fails if**: the value is in *which* lenses run rather than in verifying what ran.

### B — Wrapper + lens injection (chosen)

- **Shape**: `/code-review` for the generic sweep, and in the same message N wb lens agents drawn
  from a generalized version of `adversarial-review/SKILL.md:56-65`'s table
  (data / frontend / AI-systems / security / SRE / migrations / i18n / test-quality). Merge,
  dedupe, three-state verify, report once.
- **Precedent**: `plugin/skills/validate_execution/SKILL.md:110-126` — parallel agent fan-out then
  synthesis.
- **Buys**: keeps the built-in's proven angle coverage **and** the domain-expert framing that is
  the actual differentiator; the lens table is the natural place for the repo-specific hook-in.
- **Costs**: 8–10 built-in agents plus N lenses is real money, and the skill now owns a merge and
  dedupe rule between two finding sets with different provenance.
- **Fails if**: the diff is small and unremarkable — the built-in alone at `low`/`medium` is
  already the right tool. This is what the reconnaissance tiering exists to prevent.

### C — Modifier-only, no review skill

- **Shape**: ship the selector, not the reviewer. It decides which review runs (repo-specific →
  `REVIEW.md`-informed built-in → built-in) and at what effort, layering adversarial modifiers as
  instructions onto whichever it picked.
- **Precedent**: `plugin/skills/model-help/SKILL.md:3` — gate mode advises and selects, never does
  the work.
- **Buys**: smallest surface, nothing to keep in sync with Anthropic's taxonomy, and
  "prefer repo-specific" *is* the whole product.
- **Costs**: the hunt list, Phase 1.5 adjudication and coverage check have nowhere to live but a
  reference doc; verify-only mode disappears; "run just the adversarial pass" stops being a thing
  you can invoke.
- **Fails if**: you want the adversarial pass to be something you can iterate on.

## The reconnaissance model (the refinement that shaped B)

The first draft of B tiered on lines changed. That was rejected: *"LOC are not an indicator of
complexity alone — if determined non-trivial, there needs to be analysis in terms of what it
touches to determine risk and complexity (possibly derived from existing design etc docs but since
adversarial-review is also used on other peoples PRs we can't assume that)."*

So tier becomes an **output of a cheap reconnaissance pass**, not an arithmetic input — a
`tracer-bullet`-shaped probe (`plugin/skills/tracer-bullet/SKILL.md`; the same "aim before you fan
out" idea `create_research/SKILL.md:110` uses as a scoping probe) that culls fleet size before it
is paid for.

**Six signal axes, all derivable from the diff plus the repo alone — no plan documents:**

1. **What the paths are, by role** — schema/migration, auth & authorization, input handling,
   external I/O, config & CI, dependency manifests, i18n, tests, docs, generated files. Inferred
   from path shape and file content, not a hardcoded stack list.
2. **What the change does to behavior** — deleted guards and validations, changed defaults,
   widened types or permissions, new external calls, new persistence writes, error handling
   removed or broadened. The built-in's Angle B already names this class; here it is a *triage*
   signal, not only a finding source.
3. **Measured blast radius** — call sites of changed symbols outside the diff, plus specs that
   stub what changed. This is the axis LOC misses entirely, and it is cheap: one grep per changed
   export.
4. **Coupling breadth** — how many distinct subsystems the diff spans, not how many lines.
5. **Reversibility** — migrations, backfills, published API surface, anything a deploy cannot take
   back.
6. **Evidence present** — do tests change alongside the source, and is the new path covered?

**The tiering rule is max, not mean.** One axis firing high sets the tier. An irreversible
migration is top tier at nine lines with every other axis trivial. Averaging is what produces the
"small so it's simple" failure this rule exists to prevent.

**LOC keeps exactly one job**: a tie-breaker for fleet size *within* a tier, and a pass-through
scaling hint for the built-in leg, which computes its own finder budget as
`max(2, min(8, ceil(lines_changed/150)))` — a formula already load-bearing inside the built-in and
not worth fighting.

**Mandatory lenses are content-triggered and pull the tier up with them**: auth / permissions /
params / uploads / external calls / PII-shaped data → security lens; prompt text, skill files,
agent definitions → AI-systems lens (`adversarial-review/SKILL.md:60` already makes this one
mandatory, and it is the case where the prose *is* executed); migrations / backfills / schema →
data lens; a changed signature with callers outside the diff → cross-file tracer.

**On someone else's PR**, two further rules: the PR title and body are untrusted input, read to
understand intent and never to lower a tier (Anthropic's own security scanner carries this guard
verbatim); and an absent plan directory is the normal case, not a degraded one.

## Discussion

**Where the premise had to be corrected twice, and both corrections mattered.**

The first was `review-strict`. The exploration opened with it as the generic fallback, on the
user's suggestion. It is not a shipped Claude Code skill — the binary contains 62 occurrences of
`code-review` and 9 of `security-review`, and zero of `review-strict`; `registry.npmjs.org/review-strict`
returns `{"error":"Not found"}`; and the only real convention in the wild is a `<language>-strict`
suffix. On this machine it exists solely as a dangling symlink into a missing
`/Users/scraig/projects/prompts/` tree. What the user was reaching for turned out to be real as a
*modifier* — strictness as a dial on a review — and that survived into the design as the effort
ladder. The name did not.

The second was the assumption that the built-in was a lightweight single-pass reviewer. Reading
it out of the binary showed the opposite, and reshaped the whole decision: it fans out 8–10 finder
subagents; its taxonomy already includes the removed-behavior auditor, the cross-file tracer, the
altitude check and a Conventions angle that walks every ancestor `CLAUDE.md`; and its finding
vocabulary is already `CONFIRMED / PLAUSIBLE / REFUTED` with criteria nearly identical to
`adversarial-review/SKILL.md:87-97`. Once that was on the table, re-implementing a reviewer stopped
being defensible and the question narrowed to what to add.

**A non-obvious result worth keeping.** The wb layer's contribution is *not uniform across the
ladder*, and it is largest at the ends for opposite reasons. At `high` the built-in is already
recall-biased — "you are reviewing for **recall** … Err on the side of surfacing" — which is most
of the adversarial stance already. At `low` it is the opposite: one diff pass, hunk-only, and
explicitly "Do not flag style, naming, perf, missing tests, or anything outside the hunk." So at
the bottom of the ladder wb supplies the *stance* the built-in deliberately withholds; at the top
it supplies the *verification* this build appears not to wire up.

That asymmetry produced a concrete conflict at the lowest tier: invoking `/code-review low` and
then layering "read the enclosing function, chase the blast radius" contradicts the sub-skill just
invoked. Resolved by giving the two legs explicitly different scopes — the built-in does its cheap
hunk sweep, and one wb stance agent does the enclosing-function, deleted-invariant and blast-radius
pass. Two agents at the bottom tier; the stance survives the downshift, which was the property the
user asked for.

**On normalizing across models.** The user's call: *"it should normalize across family and lenses
so that it behaves similarly regardless of model, but should also lean on model-help to advise if
it thinks that upshifting before running it would be best based on the task at hand — I want the
adversarial review to behave same-ish in terms of fan out and lenses based on complexity regardless
of starting model."* The tier fixes the intended shape; the wrapper reaches it by choosing the
effort token and sizing the lens leg. The brittleness this buys — the model-family routing table is
an undocumented internal — is confined to one reference doc with a `Check it` command, and the
skill prefers *measuring* whether the built-in leg came back thin over *predicting* that it will.

## Open Threads

- **The merge/dedupe rule between the two legs** is named as a cost but not specified. Two finding
  sets with different provenance, one of which may carry a `verdict` and one of which will not
  until wb's verify pass runs. `create_design` owns this.
- **Whether the "Checked and clear" coverage list survives.** It has no `ReportFindings` field. It
  is not a finding, so carrying it in the text restatement does not violate the tool's
  "do not also print the findings as text" rule — but that reading should be confirmed rather than
  assumed.
- **The exact tier cut-points and the lens cap** — 4 normally, 6 at the top tier was proposed and
  not explicitly ratified; the underlying rule (lenses match what the diff touches, and a lens with
  nothing to look at returns noise) is settled, the numbers are not.
- **Whether `adversarial-loop` ever offers to create a PR.** Recorded as inferred-out-of-scope,
  preserving the source skill's rule (`adversarial-loop/SKILL.md:27-28`), flagged for correction.
