# Built-in review machinery — what wb may rely on

**Read this when a step directs you to.** It is the plugin's single authority on what Claude
Code's built-in review commands provide, which parts of that are safe to build on, and which are
observations that may rot. Skills link here rather than restating it.

Everything below was read out of a shipped binary and confirmed by running it. Where a claim is
weaker than that, it says so — that distinction is the point of the document.

## What the built-ins are

Three commands ship with Claude Code. **Two of them are invocable by the model through the
`Skill` tool; `/verify` is not.** `Skill('verify')` returns

> `Skill verify cannot be used with Skill tool due to disable-model-invocation. Ask the user to
> run /verify themselves — it cannot be invoked via the Skill tool. Do not replicate this
> skill's workflow by other means — it is reserved for explicit user invocation.`

Measured 2026-09-20; `code-review` and `security-review` both load. This paragraph previously
said all three were invocable, and a skill was written against that — `adversarial-loop` Phase 1
step 4 read "Invoke `/verify`", which the model cannot do. **A step delegating to `/verify` has
to stop and ask the user**, and note the error's last sentence: substituting your own equivalent
is explicitly out of bounds, so the honest fallback is to report that fix-verification did not
run, not to improvise one.

| Command | What it does | Output |
| ------- | ------------ | ------ |
| `/code-review` | Reviews a diff for correctness bugs and reuse/simplification/efficiency cleanups. Fans out parallel finder angles. | `ReportFindings`, or text |
| `/verify` | Exercises a change end to end and observes behaviour — "drive the affected flow, not just tests or typecheck". Bootstraps a repo's own verify skill if none exists. | Prose |
| `/security-review` | A security-only pass over the current branch, with its own severity and confidence scales. | Markdown only |

**They run forked.** A `Skill` call to `/code-review` does not consume the calling session's
context, which is what makes wrapping one affordable rather than ruinous.

**The result line has two spellings, and only one of them was written down here.** A short
review returns `completed (forked execution)`. A long one returns
`launched (forked execution, running in the background)` and the caller waits on it as a
background agent — observed 2026-09-20 on `/code-review high` over a 312-line diff, which took
3m54s. A wrapper that waits for the word `completed` will wait forever on the second shape.
Treat "forked" as the thing to match on; treat the rest as unstable.

**`ReportFindings` was not available inside the fork.** The built-in leg reported the tool
unavailable and fell back to prose, while the tool was available in the calling session that
spawned it. So a wrapper must be able to read the built-in leg's findings as **text**, and
cannot require the structured channel from a leg it did not itself emit. **Observed three times, on
two different repositories** (2026-09-20), so it is a property of the fork rather than of one
run. It is recorded because the failure is silent — prose findings still arrive, just without
the fields.

## The argument surface

```
/code-review [low|medium|high|xhigh|max|ultra] [--fix] [--comment] [<pr#>|<branch>|<path>]
```

- **Effort** is matched case-insensitively with prefix matching, so `med` resolves to `medium`.
- **`--fix`** applies findings to the working tree, then re-reports each with an `outcome`.
- **`--comment`** posts findings as inline PR comments on GitHub, or a single note on a GitLab MR.
- **`ultra`** routes to a cloud review and requires claude.ai account access. Its logic is not in
  the client, so nothing here describes it.
- **With no effort given, it reuses the level typed last** — a persisted setting. A skill that
  wants a specific level must pass one.

**It resolves its target from the current repository.** A branch or path argument is resolved
against the repo the session is running in. It cannot be pointed at a different checkout.

## Choosing the effort token

Pick from the **published semantics**, which are documented and stable:

| Level | What the documentation promises |
| ----- | ------------------------------- |
| `low`, `medium` | fewer, high-confidence findings — precision |
| `high` → `max` | broader coverage, may include uncertain findings — recall |

That is the whole contract, and it is the only part of the effort machinery a skill may encode.

**Do not encode which prompt the level selects internally.** See the dated observation at the end
of this document for why.

## The finding contract

`ReportFindings` is the structured-output channel. Its fields:

| Field | Meaning |
| ----- | ------- |
| `file`, `line` | repo-relative path, 1-indexed line |
| `summary` | one sentence stating the defect |
| `short_summary` | the claim compressed to ≤60 characters, no rationale clause |
| `failure_scenario` | concrete inputs/state → wrong output or crash |
| `category` | kebab-case slug: `correctness`, `simplification`, `efficiency`, `reuse`, `altitude`, `conventions`, `test-coverage` |
| `verdict` | `CONFIRMED` or `PLAUSIBLE` — set only when a verify pass ran |
| `outcome` | `fixed`, `skipped`, `no_change_needed` — set only when re-reporting after fixes |
| `level` | the effort the review ran at |

Three rules come with it:

1. **The tool gates itself.** Its own description says to use it "only when the active code-review
   instructions tell you to report findings with this tool." A skill that wants it must say so
   explicitly in its own body; inheriting the intent is not enough.
2. **Call it once**, with findings ranked most-severe first, and do not also print them as text.
   **wb deviates here, deliberately and narrowly**: its review skills add a one-line-per-finding
   restatement after the call, because a forked or non-rendering session receives nothing
   otherwise and `adversarial-loop` adjudicates from what it receives. The bounds are set in
   `adversarial-review/templates.md` — one line each, no scenario, no fix. A skill that wants more
   than that is writing the competing report this rule forbids.
3. **Re-report after fixes**, with an `outcome` on each finding. The host UI's per-finding status
   updates only from that call; without it the findings stay marked unresolved.

The `verdict` vocabulary is the harness's own — the built-in's internal criteria are
`CONFIRMED` / `PLAUSIBLE` / `REFUTED`, keeping the first two and dropping the third. A wb skill
emitting those values is conforming, not inventing.

## Chaining into `/verify`

`/code-review` chains into `/verify` by design, and states the division of labour: *this review
checks that the diff reads right; `/verify` checks that it runs right.*

A skill that needs to know whether a change actually works delegates to `/verify` rather than
running tests itself. Two things come free with that:

- **Repo-specific command discovery.** `/verify` finds this repository's commands and, per its own
  description, "bootstraps this repo's project verify skill if none exists yet."
- **Pre-ship exemptions.** It should not be invoked on a diff with no runtime surface — test-only
  or docs-only changes have nothing to observe.

## What may be relied on, and what may not

**Rely on these.** They are documented, or directly observable, and a skill may encode them:

- The command names, the argument surface, and the flag meanings.
- The published effort semantics — precision at the bottom, coverage at the top.
- The `ReportFindings` field names and enum values.
- That a `Skill` call to a built-in runs forked.
- That `/code-review` resolves its target from the current repository.

**Do not rely on these.** They are internals, and a skill that encodes them fails silently when
they change:

- How many finder agents run at a given effort level.
- Which internal prompt a given effort level selects, on a given model family.
- Whether a verification pass runs inside the built-in. **Assume it does not** — see below.
- Anything about the cloud `ultra` path, which is not in the client at all.

**Prefer measuring to predicting.** Where a skill can observe that a review came back thinner than
expected, it should act on the observation rather than on any assumption about why.

## Dated observation: internal prompt-cell selection

**Verified 2026-09-17, against build 2.1.272. Scoped to prompt-cell selection only. This did not
predict observed behaviour — treat it as background, not as a rule.**

Reading the binary's strings shows a routing table keyed on model family, selecting a different
internal prompt per effort level. Under `claude-opus-5` it maps both `medium` and `high` to the
same minimal cell; under `claude-opus-4-8` the angles run inline rather than as subagents. The
same strings contain a fully written three-state verifier prompt
(`Phase 2 — Verify (1-vote, 3-state)`) while the live per-level composers read
`Phase 2 — Dedup only (no verify)`.

**What happened when this was tested.** Running `/code-review` at `low` and then at `high` on the
same repository under `claude-opus-5` — the family where the table predicts `high` collapses into
the minimal cell — produced 3 findings and then 7, with the higher level adding a scope statement
and severity ranking. Coverage broadened as the published semantics say it should. The table did
not predict that.

The likeliest reading is that effort drives two levers — which prompt is selected *and* the
reasoning effort the review runs at — and this table only ever described the first. It is kept
because it cost real effort to obtain and would matter if cell selection ever did bite; it is
demoted because it answers a narrower question than it appears to.

**Check it**:

```bash
strings "$(readlink -f "$(command -v claude)")" \
  | grep -oE 'Dedup only \(no verify\)|Dedup and self-check \(no subagent verify\)|Verify \(1-vote[^)]*\)' \
  | sort -u
```

On build 2.1.272 that prints four lines: two `Dedup` composer headings that run live, and two
`Verify` headings that exist but are not reached. **If the `Dedup only (no verify)` line
disappears**, the built-in may have wired its verifier in, and any wb skill supplying its own
verification pass should be re-examined for redundancy.

*(Match on those tails rather than on the full heading: the em-dash arrives from `strings` as the
literal seven-character sequence `\u2014`, so a pattern written with a real em-dash — or with `.`
standing in for one — matches nothing and the check silently passes.)*

## Reporting it

One line, in the calling stage's normal output — not a section:

```
🔍 Built-in leg: /code-review high → 7 findings (forked)
🔍 Built-in leg: /code-review low → 0 findings; lens leg carried the pass
🔍 Built-in leg: unavailable — Skill call declined; ran the wb lenses only, and said so
```
