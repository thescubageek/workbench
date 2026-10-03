---
project: adversarial_loop
task: P5-T4
run: 2
date: 2026-09-20
cwd: /Users/scraig/conductor/workspaces/workbench/adversarial-loop-skill-research
cwd_physical: /Users/scraig/conductor/workspaces/workbench/ankara
git_commit: a15c35a9f6e757e46ec5e4e0c97b3b573ef41414
git_branch: adversarial-loop-skill-research
auto_mode: "off (exited before any command ran)"
---

# P5-T4 run 2 — behavioural smoke session for `wb:adversarial-review`

Run 2 of the P5-T4 behavioural smoke session, from a recorded cwd outside the plugin. Run 1
stopped at scope after failing item 2. This run reached every step, including Steps 5–8, which
had never executed in any prior run.

Verdict in one line: **the skill runs end to end and its instructions hold, with one defect found
in the skill itself** — the Step 3 guard cannot fire under the shell the harness actually uses.

## Precondition

The session opened with auto mode **active**. Its instruction, verbatim from the harness:

```
While auto mode is active:

Do your work through the Bash tool wherever it can accomplish the job: read files with cat,
head, or sed -n, search with grep and find, and make file changes with sed, heredocs, or short
scripts, rather than using the dedicated Read, Edit, or Write tools. Fall back to a dedicated
tool only when Bash genuinely cannot do the job.
```

Per the run brief this is a hard stop, so nothing was run. The mode was then turned off and the
harness confirmed:

```
## Exited Auto Mode

You have exited auto mode. Resume using the dedicated tools for file reads, searches, and edits.
```

Everything below ran after that confirmation. **Precondition: PASS**, on the second attempt.

One environmental observation worth keeping: the session was launched believing auto mode was
off, and it was on. Either the toggle does not apply to new sessions or it is sticky across a
session boundary. Worth confirming the setting reads OFF before the next run rather than assuming
a fresh session clears it.

## Working directory

The workspace path is a symlink and the two spellings disagree, as the brief warned:

```
$ pwd
/Users/scraig/conductor/workspaces/workbench/adversarial-loop-skill-research
$ pwd -P
/Users/scraig/conductor/workspaces/workbench/ankara
$ git rev-parse HEAD
a15c35a9f6e757e46ec5e4e0c97b3b573ef41414
$ git rev-parse --abbrev-ref HEAD
adversarial-loop-skill-research
```

The logical spelling is the branch-named directory listed in the environment as an additional
working directory; the physical is `ankara`, the primary. The skill's own base directory resolved
to the physical spelling (`…/ankara/plugin/skills/adversarial-review`), and every `Read` in this
run used absolute physical paths. No Bash call was prefixed with `cd`.

Re-stated at the point of the final write, unchanged:

```
pwd:      /Users/scraig/conductor/workspaces/workbench/adversarial-loop-skill-research
pwd -P:   /Users/scraig/conductor/workspaces/workbench/ankara
commit:   a15c35a9f6e757e46ec5e4e0c97b3b573ef41414
branch:   adversarial-loop-skill-research
status:   0 modified/untracked
```

Plugin under test:

```
$ claude --plugin-dir plugin plugin details wb | head -4
wb 3.0.0
  Description: Workbench for structured software development: TDD, project planning, and phased execution with status tracked in the plan documents.
  Source: wb@inline
```

## Item 1 — did the skill load, and under what name

**PASS.** Invoked as `wb:adversarial-review` with argument `plugin/skills/adversarial-loop`. The
harness returned `Launching skill: wb:adversarial-review` and the body arrived with its base
directory stated as
`/Users/scraig/conductor/workspaces/workbench/ankara/plugin/skills/adversarial-review`, followed
by `ARGUMENTS: plugin/skills/adversarial-loop`.

## Item 2 — supporting files, and the tool used for each

**PASS.** Every directed read used `Read`. No `cat`, `sed -n` or `head` was used to read any
file in this run.

| File | Directed by | Tool |
| ---- | ----------- | ---- |
| `adversarial-review/lenses.md` | Step 3 | `Read` |
| `plugin/docs/reference/code-review-integration.md` | Step 3 | `Read` |
| `adversarial-review/templates.md` | Steps 3 and 7 | `Read` |
| `adversarial-review/prompts.md` | Step 4 | `Read` |
| `adversarial-review/reference.md` | proportionality gate / coverage check | `Read` |
| `adversarial-loop/SKILL.md` (under review) | the diff | `Read` |
| `adversarial-loop/reference.md` (under review) | the diff | `Read` |

No read was refused. The manifest's hard-stop rule on `cat` therefore never had cause to fire —
which is a clean result, not an untested one: the run brief's point was that under auto mode the
rule is unfirable in *either* direction, and with auto mode off it was firable and simply had no
trigger.

Bash was used only for git plumbing, the blast-radius measurement, the guard probes and the gate
scripts — never to read a file the skill directed.

## Item 3 — the reconnaissance summary as printed

**PASS.** The tier is named and so is the axis that set it.

```text
🔎 Reconnaissance — origin/main...HEAD -- plugin/skills/adversarial-loop, 2 files (+312, -0)
   Paths           high     skill definition + reference; prose an LLM executes as
                            instruction, including fenced bash blocks a model runs
   Behaviour       high     introduces a sequencer holding push / `gh pr ready` /
                            `gh pr comment` / label authority, and deliberately pulls
                            author-controlled PR text into a context holding Bash
   Blast radius    medium   measured: 19 references outside the diff (CHANGELOG.md:43,128;
                            README.md:127; help/SKILL.md:190; model-help/SKILL.md:105;
                            daily-digest/SKILL.md:298-299; reply-to-claude/SKILL.md:100;
                            adversarial-review/{SKILL.md:39,277,292, templates.md:76,180,
                            reference.md:6}; code-review-integration.md:79). All 312 lines
                            are insertions — no signature changed, so these are
                            descriptive references, not orphaned call sites
   Coupling        medium   sequences adversarial-review, implement, /verify,
                            reply-to-claude, review-ledger; described by 6 other files
   Reversibility   low      two new documentation files; nothing deployed, nothing migrated
   Test evidence   medium   check-guards scans the fenced blocks and passes (7 files, exit 0);
                            no test asserts the prose rules

   Tier: high, set by Behaviour (publishing authority + author-controlled text reaching an
         instruction surface); Paths ties at high
   Lenses: AI-systems (skill/prompt text, mandatory), security (outbound calls + push and
           label authority + untrusted bot text to an instruction surface, mandatory),
           release engineer (gh pr ready, labels, what runs with elevated permission),
           cross-file tracer (19 outside references describing this skill's behaviour)
           · dropped: none — 4 of 6, under the cap
   Effort: high — the defects here are contradictions between files, which is a coverage
           problem; precision-mode returns too few to find them
```

The scope stop did **not** fire at this size, as the brief predicted it should not.

## Item 4 — the blast-radius measurement

**Split verdict. The exclusion fix: PASS. The guard line: FAIL — it cannot fire in this shell.**

### The anchored exclusion, as run

```bash
grep -rnF -- "adversarial-loop" . | grep -vE "^(\./)?plugin/skills/adversarial-loop/" | sed 's/^/  /'
search=${PIPESTATUS[0]}
[ "$search" -le 1 ] || echo "SEARCH FAILED (grep exit $search) — NOT an isolated change" >&2
```

Output, unedited:

```
  CHANGELOG.md:43:- **`wb:adversarial-loop` — a sequencer that drives a change to reviewable.** It owns ordering
  CHANGELOG.md:128:- *(found by the dogfood review)* **`adversarial-loop` declared no write tool** despite applying
  README.md:127:- **`adversarial-loop`** - Drives a change to reviewable: review, adjudicate, fix, re-verify until clean; if a PR exists, also flips to ready, waits on CI and `claude[bot]`, and replies until resolved
  plugin/docs/reference/code-review-integration.md:79:   otherwise and `adversarial-loop` adjudicates from what it receives. The bounds are set in
  .context/attachments/LY9984/pasted_text_2026-09-20_14-09-24.txt:34:      r/workspaces/workbench/adversarial-loop-skill-research; echo
  .context/attachments/LY9984/pasted_text_2026-09-20_14-09-24.txt:149:                             adversarial-review, adversarial-loop,
  .context/attachments/LY9984/pasted_text_2026-09-20_14-09-24.txt:255:  /Users/scraig/conductor/workspaces/workbench/adversarial-loop-skill-
  plugin/skills/reply-to-claude/SKILL.md:100:consumes review CI. `adversarial-loop` lists it in *What stops for the user*, and each round is
  plugin/skills/daily-digest/SKILL.md:298-299 (two lines, elided here for width)
  plugin/skills/adversarial-review/reference.md:6:`adversarial-loop` reads this file rather than restating it. The dispositions below are the same
  plugin/skills/adversarial-review/templates.md:76:because a forked or non-rendering session otherwise receives nothing — and `adversarial-loop`
  plugin/skills/adversarial-review/templates.md:180:When findings are fixed later — in this session, by `adversarial-loop`'s next round, or
  plugin/skills/adversarial-review/SKILL.md:39:It does **not** fix anything. Findings are reported; `adversarial-loop` is what applies them.
  plugin/skills/adversarial-review/SKILL.md:277:**Do not run the test suite to verify.** That is `/verify`'s job, and `adversarial-loop` invokes
  plugin/skills/adversarial-review/SKILL.md:292:[templates.md](templates.md), then stop. This skill does not fix anything; `adversarial-loop`
  plugin/skills/model-help/SKILL.md:105:| `adversarial-loop` | Sonnet 5 / medium | A sequencer: it orders rounds and holds gates, ...
  plugin/skills/help/SKILL.md:190:| `/wb:adversarial-loop [<pr#>\|<branch>] [--effort=<level>]` | Drives a change to reviewable: ...
  .claude/wb/knowledge.md:140:  be a symlink: `pwd` reported `.../workbench/adversarial-loop-skill-research` where `pwd -P`
=== guard probe: PIPESTATUS[0]='' pipestatus[1]='0' ===
```

19 call sites, the changed directory's own lines correctly excluded. The anchored form works and
the `(\./)?` alternation was necessary — this grep emits no leading `./`, so an anchor written for
the other spelling would have filtered nothing.

### The guard line cannot fire

The probe appended to the block is the finding. `PIPESTATUS[0]` came back **empty**, while zsh's
own `pipestatus[1]` held `0`. `PIPESTATUS` is a bash array; zsh does not define it.

Controlled test:

```
--- A: guard with empty search var (the zsh reality) ---
guard: passed (no failure reported)
exit=0

--- B: force a real grep failure, verbatim skill block ---
B produced no SEARCH FAILED line above? search=''

--- C: same forced failure under bash ---
SEARCH FAILED (grep exit 2) — NOT an isolated change
```

Under bash a grep exiting 2 fires the guard. Under zsh — the shell the Bash tool actually uses,
confirmed as `/bin/zsh`, `ZSH_VERSION=5.9`, `BASH_VERSION=none` — `search` is empty,
`[ "" -le 1 ]` evaluates **true**, and a broken search reads as an isolated change.

That is precisely the failure direction the block was written to prevent: its own prose says
"this measurement's errors all point toward believing the change is safe". The guard is inert in
the shell it runs in.

`check-guards` does not cover it — `grep -n "PIPESTATUS\|pipestatus" plugin/scripts/check-guards`
returns nothing, and the script reports clean on both skills:

```
✅ check-guards: no unguarded measurements (7 files scanned)
exit=0
```

This defect is in `adversarial-review/SKILL.md`, not in the diff under review, so it was recorded
here rather than emitted through `ReportFindings`. It should become its own task.

### A second, same-cause defect at Step 1

Step 1's resolution block failed outright on the path-target form:

```
range: origin/main...HEAD -- plugin/skills/adversarial-loop
fatal: ambiguous argument 'origin/main...HEAD -- plugin/skills/adversarial-loop': unknown revision or path not in the working tree.
```

Cause is the same shell mismatch: `git diff --stat $range` relies on word-splitting an unquoted
expansion, which zsh does not do by default. Demonstrated side by side:

```
$ for w in $range; do echo "[$w]"; done              # zsh
[origin/main...HEAD -- plugin/skills/adversarial-loop]

$ bash -c 'for w in $range; do echo "[$w]"; done'    # bash
[origin/main...HEAD]
[--]
[plugin/skills/adversarial-loop]
```

Only the **path** form puts a space in `$range`, so branch and PR targets are unaffected — which
is why this survived four rounds of review: the form that breaks is the one nothing had run.
The run was carried forward by invoking the diff manually; the skill was not edited.

## Item 5 — the built-in leg

**PASS.** `Skill(code-review, "high plugin/skills/adversarial-loop")` returned:

```
Skill "code-review" launched (forked execution, running in the background).

Running in the background as @code-review
```

The result line does say `(forked execution)`. Note the exact wording differs from the form
`code-review-integration.md:21` predicts — that document says a call returns
`completed (forked execution)`; the observed line is `launched (forked execution, running in the
background)`. Same guarantee, different string; worth a dated note in that file if anything ever
matches on it.

It returned 9 findings and reported that **`ReportFindings` was not available inside the fork**,
so it fell back to prose. The tool *is* available in this main session and was used at Step 7 —
so the fallback is a property of the forked child, not of the environment.

## Item 6 — Steps 5 through 8

All four ran. None had executed in any prior session.

### Step 5, the pooled dedupe

**Ran.** 23 raw candidates from five legs — built-in 9, security 6, AI-systems 6, release 2,
cross-file tracer 0 — collapsed to 18 on the predicate *same defect, same location, same reason*:

- `SKILL.md:4` unbound positional target — built-in and AI-systems
- `SKILL.md:113` `implement` vs the review directory — built-in and AI-systems
- `SKILL.md:5`/`:64` `Monitor` — built-in, security and AI-systems, three independent legs
- `reference.md:33-37` narrative correction — security and AI-systems

One pair was deliberately *not* collapsed: AI-systems raised the Phase 2 `&&` chain as defective
while security placed the same chain in *Checked and clear*. Step 6's rule for a clearance that
contradicts a finding was followed — both went to a verifier.

### Step 6, the three-state verify

**Ran**, 18 verifiers, one per surviving candidate, `sonnet` per `prompts.md` except the contested
pair which ran `opus`. All three verdicts were exercised: **10 CONFIRMED, 2 PLAUSIBLE, 6 REFUTED**.
The REFUTED ones were dropped rather than downgraded.

The verify pass earned its cost twice over:

- The `Monitor` finding — raised independently by three of five legs, and the kind of consensus
  that reads as certainty — was **REFUTED** against
  `docs/claude-code-skills-guide.md:302`, which records the repository having measured
  `allowed-tools` in both directions and found it neither restricts nor grants. Three legs would
  have shipped a wrong finding.
- The contested clearance was **overturned**. The tiebreak found the two reviewers were not in
  conflict at all: security cleared the `&&` against a *failed* push, which is true; AI-systems
  raised a *successful no-op* push, which `&&` does not guard. The clearance answered a claim the
  finding never made. It also strengthened the finding, locating a worse trigger inside the skill
  — the no-plan-directory inline-fix path at `:126`, which has no commit step, so the round's own
  fixes are what go unpushed.

### Step 7, the `ReportFindings` emission and the restatement

**Ran.** One `ReportFindings` call, `level: "high"`, 12 findings ranked most-severe first, each
carrying `file`, `line`, `summary`, `short_summary`, `failure_scenario`, `category` and `verdict`.
The harness acknowledged `12 findings reported`. The one-line-per-finding restatement followed,
`🔴` for CONFIRMED and `🟡` for PLAUSIBLE, then a six-line *Checked and clear* with a `file:line`
on each entry.

### Step 8, the remediation plan

**Ran.** Written to
`docs/plans/2026-09-17-adversarial_loop/reviews/2026-09-20-round-5/tasks.md` — round 5, since
`2026-09-18-round-4` already existed. 10 tasks `R5-T1` … `R5-T10`, each carrying its
`failure_scenario` verbatim as its acceptance criterion with a named shape from the taxonomy.
The two PLAUSIBLE findings were recorded without tasks under the proportionality gate, each with
its unverified link and its cheapest close. The six REFUTED findings were recorded with the line
that disproved them, so the next round resolves them from the record rather than re-arguing.

Nesting is correct: the round directory sits one level below `docs/plans/*/`, so the session-start
hook's glob does not pick it up as a competing active plan.

## Item 7 — the findings

**PASS on the evidence contract.** All 12 carry a concrete failure scenario; the six that could
not were REFUTED and dropped rather than reported at a lower verdict.

```text
🔴 SKILL.md:4 — unbound positional target; Phases 2/4/5 un-draft and label the current branch's PR
🔴 SKILL.md:177 — `&&` guards a failed push, not a successful no-op; un-drafts at a stale head
🔴 SKILL.md:189 — `gh pr ready` no-ops on a non-draft PR, so claude[bot] is never summoned
🔴 SKILL.md:216 — Phase 5 ties only CI to the head SHA, never the bot's clearance
🔴 SKILL.md:201 — Phase 4 pushes at step 2; the provenance rule is read at step 3
🔴 SKILL.md:131 — no plan directory means no ledger, and the blocking breaker never evaluates
🔴 SKILL.md:113 — `implement` hard-stops on the phase-less review directory the loop points it at
🔴 SKILL.md:191 — Phase 3 supplies no wait procedure, timeout or escalation
🔴 SKILL.md:222 — unchained label edit/view reads a failed `--add-label` as success
🔴 SKILL.md:175 — no release gate covers the two publish blocks; a de-chained regression ships green
🟡 SKILL.md:224 — label name has no stated source and sits in a substitution-live shell position
🟡 SKILL.md:202 — Phase 4 drops /verify, `implement` and the ledger row
```

Two were verified by execution rather than by reading. The release-gate finding was confirmed by
building a scratch copy of `SKILL.md` with `&&` replaced by `;` and running `check-guards` against
it — it returned `✅ check-guards: no unguarded measurements (1 files scanned)`, exit 0. The
`gh pr ready` no-op was confirmed against cli/cli's `pkg/cmd/pr/ready/ready.go`, where `!pr.IsDraft`
returns nil without issuing a mutation.

### How the reviewers scored

| Leg | Raised | Survived | Note |
| --- | ------ | -------- | ---- |
| Built-in `/code-review high` | 9 | 6 | strongest on flow defects; `ReportFindings` unavailable in the fork |
| Security | 6 | 3 | two of three refutations were its own over-reach on prohibition wording |
| AI-systems | 6 | 4 | found the no-op push nobody else saw |
| Release engineer | 2 | 1 | the one that held was verified empirically, not argued |
| Cross-file tracer | 0 | 0 | a clean result with a checked list behind it, not a silent zero |

The two mandatory `opus` lenses justified their tier. The cross-file tracer returning zero is the
correct outcome for a diff of pure insertions — no signature changed, so there was nothing to
orphan — and it is worth noting that it said so with a list rather than with silence.

## What this run establishes, and what it does not

Established: the skill loads, reads its supporting files with `Read`, sizes itself with a named
axis, measures rather than estimates blast radius, wraps the built-in, pools and dedupes across
five legs, verifies in three states, emits `ReportFindings` once with a restatement, and writes a
remediation plan to the right nested path. Steps 5–8 all work.

Not established, and deliberately out of scope: `wb:adversarial-loop` reaching clean without `gh`.
That is the other half of P5-T4 and comes after this one passes.

Two defects for the next round, both in `adversarial-review/SKILL.md` rather than in the reviewed
diff, both the same root cause — fenced blocks written in bash and executed in zsh:

1. Step 3's `${PIPESTATUS[0]}` guard is inert. Under zsh the variable is empty, the test passes,
   and a failed search reads as an isolated change.
2. Step 1's `git diff --stat $range` fails on a path target, because zsh does not word-split
   unquoted expansions.

Both are invisible to `check-guards`, which has no rule for either shape. A fix for the guard
should also add the shape to `plugin/scripts/fixtures/guard-corpus.json` so `test-guards` holds
the line.

## Session hygiene

Nothing was committed and nothing was pushed. Two files were written, both new, both under the
gitignored plan tree — `reviews/2026-09-20-round-5/tasks.md` (the skill's own Step 8 output) and
this transcript. `git status --porcelain` reports 0 entries. No file under `plugin/` was modified,
and the skill under observation was not edited despite two defects being found in it.

One side effect worth recording: the release-gate verifier was instructed to build its scratch
copy outside the repository, and doing so caused the harness to add `/private/tmp/scratch_verify`
as an additional working directory for the session. Harmless here, but a verifier that writes
anywhere can widen the session's directory set.
