---
plan: docs/plans/2026-09-17-adversarial_loop
task: P5-T4
created: 2026-09-20
session_date: 2026-09-20
cwd: /Users/scraig/conductor/workspaces/workbench/adversarial-loop-skill-research
cwd_physical: /Users/scraig/conductor/workspaces/workbench/ankara
cwd_note: the logical path is a symlink to the physical one; `pwd` and `pwd -P` disagree
git_commit: 90a227a4f4ac9c897ab98e19a940a9f6ea72d84d
git_branch: adversarial-loop-skill-research
git_toplevel: /Users/scraig/conductor/workspaces/workbench/ankara
worktree_status: clean
plugin_version: 3.0.0
model: claude-opus-5[1m]
status: stopped-at-scope-gate
outcome: 2 of 5 report items PASS, 1 FAIL, 2 NOT RUN
---

# P5-T4 — behavioural smoke session

Observation-only session. Nothing was edited, committed or pushed; this file is the sole
write, and it was explicitly requested.

**Filename note.** The task specified `2026-09-19-smoke-session.md`. The session actually ran
on **2026-09-20**. The filename is kept as specified; the frontmatter carries the real date.

---

## 0. Session-level precondition: auto mode was ON

Before the first command, the harness carried this standing instruction:

> While auto mode is active:
> Do your work through the Bash tool wherever it can accomplish the job: read files with cat,
> head, or sed -n, search with grep and find, and make file changes with sed, heredocs, or short
> scripts, rather than using the dedicated Read, Edit, or Write tools. Fall back to a dedicated
> tool only when Bash genuinely cannot do the job.

This is the exact condition report item 2 was written to detect. It is recorded here first so it
cannot be mistaken for a clean run. **Every file read in this session went through `cat`, not
`Read`.** See item 2 for what that costs.

---

## 1. The two mandated probes

### Command — `pwd`

```
pwd
```

### Output — `pwd`

```
/Users/scraig/conductor/workspaces/workbench/adversarial-loop-skill-research
```

### Command — `plugin details wb`

```
claude --plugin-dir plugin plugin details wb | head -4
```

### Output — `plugin details wb`

```
wb 3.0.0
  Description: Workbench for structured software development: TDD, project planning, and phased execution with status tracked in the plan documents.
  Source: wb@inline
```

### cwd discrepancy, resolved

`pwd` did **not** match the primary working directory the session was invoked with
(`/Users/scraig/conductor/workspaces/workbench/ankara`). Chased immediately:

```
$ ls -ld /Users/scraig/conductor/workspaces/workbench/adversarial-loop-skill-research
/Users/scraig/conductor/workspaces/workbench/adversarial-loop-skill-research -> /Users/scraig/conductor/workspaces/workbench/ankara  51B

$ pwd -P
/Users/scraig/conductor/workspaces/workbench/ankara

$ pwd -L
/Users/scraig/conductor/workspaces/workbench/adversarial-loop-skill-research

$ git worktree list
~/projects/workbench                      2a6fa62 [main]
~/conductor/workspaces/workbench/ankara   90a227a [adversarial-loop-skill-research]
```

**Benign.** The additional working directory is a symlink to the primary; same worktree, same
inode. `pwd` reports the alias. Recorded because an unrecorded cwd is what this task exists to
prevent, and because the two spellings will not compare equal in any later automated check.

### Surrounding state

```
$ git rev-parse HEAD
90a227a4f4ac9c897ab98e19a940a9f6ea72d84d
$ git rev-parse --abbrev-ref HEAD
adversarial-loop-skill-research
$ git rev-parse --show-toplevel
/Users/scraig/conductor/workspaces/workbench/ankara
$ git status --short --branch
* adversarial-loop-skill-research...origin/adversarial-loop-skill-research
clean — nothing to commit
$ ls -d docs/plans/2026-09-17-adversarial_loop
docs/plans/2026-09-17-adversarial_loop/
$ ls -d docs/plans/2026-09-17-adversarial_loop/thoughts
docs/plans/2026-09-17-adversarial_loop/thoughts/
$ ls -d plugin
plugin/
```

### Incidental observation: `cd` in a Bash call moves the session cwd

One read was issued as `cd <plugin path> && cat ...`. The harness responded with:

```
# Environment update
 - Primary working directory: /Users/scraig/conductor/workspaces/workbench/ankara/plugin/docs/reference (was /Users/scraig/conductor/workspaces/workbench/ankara)
```

The session's primary working directory followed the `cd`. It was restored on the next call. This
matters for a task whose whole premise is a recorded cwd: **cwd recorded once at the top of a
session is not a durable fact.** Every subsequent command in this transcript is prefixed with an
explicit `cd` to the repo root for that reason.

---

## 2. Report item 1 — did the skill load, and under what name?

**PASS.**

Invoked `/wb:adversarial-review` with **no target**. It loaded as:

```
wb:adversarial-review
```

Base directory reported by the harness:

```
/Users/scraig/conductor/workspaces/workbench/ankara/plugin/skills/adversarial-review
```

Exact name matches the expected `wb:adversarial-review`. Nothing below is moot.

---

## 3. Report item 2 — supporting files read, and the tool used for each

**FAIL.**

| File the skill directed me to read | Step that directed it | Tool actually used |
| ---------------------------------- | --------------------- | ------------------ |
| `plugin/skills/adversarial-review/lenses.md` | Step 3 ("Read lenses.md NOW") | `cat` |
| `plugin/docs/reference/code-review-integration.md` | Step 3 ("Read ... NOW") | `cat` |
| `plugin/skills/adversarial-review/reference.md` | Step 3 / proportionality gate | `cat` |
| `plugin/skills/adversarial-review/templates.md` | Step 3 (summary shape) | `cat` |
| `plugin/skills/adversarial-review/prompts.md` | Step 4 | **not read — never reached** (stopped at scope gate) |
| `plugin/docs/reference/review-ledger.md` | listed in manifest | **not read — no step reached it** |

**Every directed read went through `cat`. Not one went through `Read`.**

Stating this plainly rather than reporting the reads as successful, as instructed:

The content arrived, so the reads "worked" in the shallow sense. But the skill manifest opens
with a hard-stop rule that this session could not exercise:

> **If a directed read fails, stop — do not continue from memory.** These files live outside your
> project, so a read can be refused. Say which file was refused, that reads outside the working
> directory are gated, and that the fix is to allow the read once or to relaunch with
> `--add-dir <plugin-path>`. Do not route around a refusal with `cat`.

Two things follow, and the second is worse than the first:

1. **The rule is addressed to a tool that was not in play.** The gating it describes — a refusal
   for a path outside the working directory — is a `Read`-tool behaviour. Under auto mode the
   reads are `cat` through Bash, which is not subject to that gate. The hard-stop can therefore
   never fire, in either direction. This session proves nothing about whether it works.

2. **The skill's own prohibition names `cat` as the thing not to do**, and auto mode makes `cat`
   the default for everything. The manifest and the harness are in direct conflict, and under
   auto mode the harness wins silently — no warning, no refusal, no trace in the output. A
   maintainer reading only the transcript of a normal run would see clean reads and conclude the
   convention held.

**This run does not validate the plugin's read conventions and must not be cited as having done
so.** A rerun with auto mode off is required before P5-T4's read-convention criterion can be
called met.

Mitigating, and worth recording so the failure is not overstated: in this session the plugin path
was *inside* the working directory (`ankara/plugin/...`), so a `Read` would not have been gated
here either. Exercising the hard-stop needs both auto mode off **and** a plugin installed outside
the working directory — i.e. a marketplace install, not `--plugin-dir`.

---

## 4. Report item 3 — the reconnaissance summary as printed

**PASS.** It names a tier **and** the axis that set it.

Steps that ran before it, verbatim:

### Step 1 — resolve the target

No argument given, so the first branch is correct rather than accidental. `target` left unset.

```
range: origin/main...HEAD
 .claude-plugin/marketplace.json                    |    2 +-
 .claude/wb/knowledge.md                            |   44 +
 .github/workflows/checks.yml                       |   51 +
 .gitignore                                         |    5 +
 CHANGELOG.md                                       |  231 ++-
 README.md                                          |   87 +-
 docs/commands-reference.md                         |    4 +-
 docs/plans/2026-09-17-adversarial_loop/README.md   |   52 +
 docs/plans/2026-09-17-adversarial_loop/design.md   |  817 +++++++++
 .../handoff-2026-09-18-17-55.md                    |  147 ++
 .../handoff-2026-09-19-05-39.md                    |   99 ++
 docs/plans/2026-09-17-adversarial_loop/journal.md  |  804 +++++++++
 docs/plans/2026-09-17-adversarial_loop/research.md |  837 ++++++++++
 .../reviews/2026-09-18-round-4/tasks.md            |  143 ++
 docs/plans/2026-09-17-adversarial_loop/tasks.md    | 1747 ++++++++++++++++++++
 .../2026-09-17-adversarial-review-architecture.md  |  241 +++
 .../thoughts/2026-09-17-wrapper-shape-probe.md     |  267 +++
 ...2026-09-18-check-guards-implementation-probe.md |  133 ++
 ...026-09-18-thrashing-and-remediation-planning.md |  158 ++
 .../thoughts/2026-09-19-release-checks.md          |  125 ++
 .../spike/__pycache__/candidate_c.cpython-314.pyc  |  Bin 0 -> 8133 bytes
 .../thoughts/spike/__pycache__/run.cpython-314.pyc |  Bin 0 -> 7669 bytes
 .../thoughts/spike/candidate_c.py                  |  120 ++
 .../thoughts/spike/corpus-results.json             |   47 +
 .../thoughts/spike/corpus.json                     |  306 ++++
 .../thoughts/spike/mutate.py                       |   60 +
 .../thoughts/spike/run.py                          |   84 +
 plugin/.claude-plugin/plugin.json                  |    2 +-
 plugin/docs/reference/code-review-integration.md   |  171 ++
 plugin/docs/reference/journal-entries.md           |  151 ++
 plugin/docs/reference/review-ledger.md             |  105 ++
 plugin/hooks/wb-prime.sh                           |    4 +
 plugin/scripts/README.md                           |  217 ++-
 plugin/scripts/check                               |   68 +
 plugin/scripts/check-guards                        |  341 ++++
 plugin/scripts/count                               |   39 +
 plugin/scripts/fixtures/guard-corpus.json          |  854 ++++++++++
 plugin/scripts/fixtures/mutation-ratchet.json      |    4 +
 plugin/scripts/fixtures/mutation-survivors.txt     |    8 +
 plugin/scripts/fixtures/mutation-waivers.json      |  194 +++
 plugin/scripts/lib_mutate.py                       |  233 +++
 plugin/scripts/lint                                |    2 +
 plugin/scripts/quiet                               |    6 +-
 plugin/scripts/shellcheck-gate                     |   33 +
 plugin/scripts/test-count                          |  122 ++
 plugin/scripts/test-guards                         |  597 +++++++
 plugin/scripts/test-phi-patterns                   |   58 +
 plugin/scripts/test-quiet                          |    8 +-
 plugin/skills/adversarial-loop/SKILL.md            |  242 +++
 plugin/skills/adversarial-loop/reference.md        |   70 +
 plugin/skills/adversarial-review/SKILL.md          |  311 ++++
 plugin/skills/adversarial-review/lenses.md         |  109 ++
 plugin/skills/adversarial-review/prompts.md        |  166 ++
 plugin/skills/adversarial-review/reference.md      |  135 ++
 plugin/skills/adversarial-review/templates.md      |  191 +++
 plugin/skills/create_design/SKILL.md               |    8 +-
 plugin/skills/create_execution/SKILL.md            |    6 +-
 plugin/skills/create_handoff/SKILL.md              |   10 +-
 .../templates/journal-md-template.md               |   13 +-
 plugin/skills/create_research/SKILL.md             |   10 +-
 plugin/skills/create_tasks/SKILL.md                |    8 +-
 .../create_tasks/templates/tasks-md-template.md    |    6 +
 plugin/skills/daily-digest/SKILL.md                |   45 +-
 plugin/skills/daily-digest/sources.md              |   87 +-
 plugin/skills/forge/SKILL.md                       |    4 +-
 plugin/skills/help/SKILL.md                        |   37 +-
 plugin/skills/implement/SKILL.md                   |    9 +-
 plugin/skills/implement_coordinated/SKILL.md       |    6 +-
 plugin/skills/implement_inline/SKILL.md            |    8 +-
 plugin/skills/implement_tasks/SKILL.md             |    6 +-
 plugin/skills/model-help/SKILL.md                  |    4 +-
 plugin/skills/project-structure/SKILL.md           |    3 +-
 plugin/skills/reply-to-claude/SKILL.md             |  167 ++
 plugin/skills/research-validation/SKILL.md         |    6 +-
 plugin/skills/resume_handoff/SKILL.md              |    7 +-
 plugin/skills/review-prep/SKILL.md                 |    9 +-
 plugin/skills/touch-grass/SKILL.md                 |    2 +-
 plugin/skills/validate_execution/SKILL.md          |    6 +
 .../reference/validation-checklist.md              |   19 +-
 .../validate_project/reference/validation-rules.md |  142 +-
 .../skills/verification-before-completion/SKILL.md |   86 +-
 81 files changed, 11655 insertions(+), 111 deletions(-)
```

### Step 2 — REVIEW.md from the base ref

```
REVIEW.md read from origin/main (merge-base 46ef587b084ea4d84a8a9b4e5b0770778903ba9b)
fatal: path 'REVIEW.md' does not exist in '46ef587b084ea4d84a8a9b4e5b0770778903ba9b'
(exit 128)
```

Correct behaviour: the **Absent** case, which the skill names as normal. The `does not exist in`
tell fired as documented, and the base was resolved and echoed (`origin/main`, merge-base
`46ef587`) rather than collapsing to the index. The anti-pattern the step warns about
(`:REVIEW.md` reading the staged copy and exiting 0) did **not** occur.

### Step 3 — the reconnaissance summary, as printed

```
🔎 Reconnaissance — origin/main...HEAD (wb 3.0.0 release branch), 81 files, +11,655 / −111
   Paths           HIGH    plugin/skills/** is instruction surface (~1,200 new lines across
                           adversarial-review, adversarial-loop, reply-to-claude); release
                           tooling (check, check-guards, lib_mutate.py); CI workflow; session hook
   Behaviour       HIGH    new CI workflow that checks out and EXECUTES repo scripts on PRs;
                           new mandatory gate chain (scripts/check) standing between work and
                           release; wb-prime.sh orientation changed; .gitignore widened;
                           both version manifests bumped 2.x → 3.0.0
   Blast radius    MEASURED (and the instrument is defective — see finding below)
                           shellcheck-gate → 4 real refs incl. caller plugin/scripts/check:52
                           check-guards    → 26 refs across CHANGELOG, README, CI, check, tests
                           lib_mutate      → 6 refs; imported at test-guards:365, :408
                           wb-prime.sh     → 11 refs incl. 2 hook registrations in plugin.json
   Coupling        HIGH    6 subsystems: skills, scripts, CI, hooks, shipped docs, fixtures
   Reversibility   HIGH    3.0.0 in marketplace.json + plugin.json. Per CLAUDE.md the plugin
                           cache is keyed by version; once published and updated, not retractable
   Test evidence   MIXED   substantial new gate coverage (test-guards 597 lines, mutation
                           ratchet, test-count, test-phi-patterns) — but the ~1,200 lines of new
                           instruction surface have no mechanical coverage beyond check-guards'
                           fenced-block scan

   Tier: MAX, set by Reversibility (a version-bumped release publishing makes irreversible);
         Paths ties it via the mandatory AI-systems trigger
   Lenses: AI-systems (mandatory — skill definitions), security (mandatory — CI executes
           author-controlled scripts on fork PRs; PHI patterns), cross-file tracer (mandatory —
           script invocation contracts, hook contract), release engineer (CI, pins, manifests),
           test-quality (597-line test surface)  ·  dropped: none — 5 of 6 cap.
           Not triggered: staff data engineer (no schema/migration), backend, frontend, SRE,
           localization
   Effort: high — coverage over precision; the surface is broad and the release is irreversible
```

**Item 3 verdict: PASS.** Tier is stated (MAX) and the axis that set it is named
(Reversibility, with Paths tying). Not inferred by me — printed by the run. The summary also
satisfies the template's other two rules: blast radius shown as measured call sites, and the
dropped-lens line present (empty, with the untriggered lenses named).

---

## 5. Report item 4 — did the built-in `/code-review` leg run?

**NOT RUN.**

No `Skill(code-review, ...)` call was made, so there is **no result line and no
`(forked execution)` marker to report.** Recorded as not-run, not as pass and not as fail.

Reason: the session stopped at Step 3, before Step 4's spawn. See item 6.

---

## 6. The scope stop

The operating instruction for this session was:

> If the diff turns out to be too large to review in one pass, say so and stop rather than
> silently narrowing the scope.

**It is too large, and the session stopped.**

81 files, 11,655 insertions — an entire release branch. At tier MAX this sizes to five lens
agents plus the built-in leg over roughly 5,000 lines of *shipped runtime* surface (plugin/,
CI, hooks, manifests), with a further ~5,500 lines of plan documentation and spike code in
range. Each lens would sample rather than review, and the resulting report would be
indistinguishable in shape from a genuine pass.

### The finding this produces about the skill

**The skill has no gate that would have caught this, and would not have disclosed it.**

- Its only cap is on **lenses** — six, described in `lenses.md` as "a runaway guard, not a
  target". It caps the fleet, never the diff.
- The **proportionality gate** in `reference.md` governs *fix size versus defect size*
  ("If the fix is larger than the defect, you are over-fitted to the reviewer's framing"). It
  is not a diff-size gate and does not fire here.
- `SKILL.md` Step 1 stops only on two conditions: an **unresolvable** range, and a range that is
  **empty** or "plainly not what was asked for". A range that is enormous is none of those. It
  passes the gate.
- Step 3 rates six axes and selects lenses. **No step asks whether the selected fleet can cover
  the range it just sized.**

Left to run, it would have spawned five lenses over 11.6k lines and emitted `ReportFindings`
with no coverage disclosure attached. The skill does carry disclosure machinery — for a
*different* failure (`If the built-in leg is unavailable ... say so in the report`) and for
dropped lenses — but nothing routes a size overrun into it.

**It did not self-disclose. The stop was imposed by the operator's instruction, not by the
skill.** This is the primary behavioural result of P5-T4.

### Suggested shape of the missing gate

Not implemented — this session is observation-only. Recorded so the next session does not
re-derive it: a seventh consideration at the end of Step 3, after the tier is set, comparing
diff magnitude against the selected fleet, with three outcomes — proceed; proceed **and**
attach a coverage-shortfall line to the report; or stop and ask the caller to scope. The third
is the one that is entirely absent today.

---

## 7. Report item 5 — the findings

**NOT RUN** as a fan-out. No lens agent and no verifier was spawned, so there is no
`ReportFindings` call from this session and no pooled candidate set.

One finding was nonetheless produced **during reconnaissance**, by running the skill's own
prescribed measurement and checking its output. It is reported here with a concrete failure
scenario, verified against source.

### 🔴 CONFIRMED — `plugin/skills/adversarial-review/SKILL.md` (Step 3, blast-radius block)

**Claim:** the prescribed blast-radius command filters by *line content* rather than by *file*,
so it drops the call sites it exists to find — and the error direction is toward believing the
change is isolated.

The block as shipped:

```bash
grep -rnF -- "<changed symbol>" . | grep -v "<the changed file>" | sed 's/^/  /'
```

`grep -rn` emits `path:lineno:content`. The `grep -v "<the changed file>"` is intended to drop
lines *originating in* the changed file. It actually drops **every line whose text mentions that
path** — including the line in another file that invokes it. For any artifact called by path
(every script in `plugin/scripts/`), the caller's invocation line contains the callee's path by
construction, so the callers are exactly what gets filtered out.

**Fails when:** the changed symbol is `shellcheck-gate`. Run as prescribed:

```
$ grep -rnF -- "shellcheck-gate" . | grep -v "plugin/scripts/shellcheck-gate"
  plugin/scripts/README.md:111:### `shellcheck-gate`
  -> hits: 1
```

One hit, a README heading. Reads as an isolated change with no callers.

Corrected to exclude the changed **file** by its path field:

```
$ grep -rnF -- "shellcheck-gate" . | grep -v "^\./plugin/scripts/shellcheck-gate:"
  README.md:267:./plugin/scripts/shellcheck-gate # shellcheck over the plugin's own shell scripts
  plugin/scripts/README.md:111:### `shellcheck-gate`
  plugin/scripts/README.md:119:./plugin/scripts/shellcheck-gate
  plugin/scripts/check:52:  && gate "shell lint"            ./plugin/scripts/shellcheck-gate
  plugin/scripts/shellcheck-gate:28:  echo "❌ shellcheck-gate: found no shell scripts to check — refusing to report clean" >&2
```

The real caller, confirmed directly:

```
$ grep -nF -- "shellcheck-gate" plugin/scripts/check
52:  && gate "shell lint"            ./plugin/scripts/shellcheck-gate
```

`plugin/scripts/check:52` is the sole invocation — the one site a reviewer must see to know that
changing `shellcheck-gate` changes the aggregate release gate. The prescribed form hides it.

**Why this one matters more than its size.** It sits ten lines below prose that states the exact
failure mode it exhibits:

> **Measure the blast radius; do not estimate it.** Run the search, print the call sites it found,
> and confirm it ran — a search that errored returns the same emptiness as a genuinely isolated
> change, and that error direction is toward believing the change is safe.

The block's three documented safeguards (`-F`, `--`, `${PIPESTATUS[0]}`) all defend against
*grep failing loudly*. None defends against grep succeeding and the **filter** silently removing
the answer. Exit status is 0, output is non-empty, every guard passes, and the measurement is
wrong — the silent-success class `check-guards` was written to hunt, in the file that hunts it.

**Reachability (proportionality gate):** live path. It runs on every invocation of this skill
against any diff touching a path-invoked script.

**Suggested fix, not applied:** anchor the filter to the path field —
`grep -v "^\./<the changed file>:"` — or drop the pipe and use `--exclude`.

### Verdict discipline note

This finding did **not** go through the Step 6 verifier agent, because Step 6 was never reached.
It is marked CONFIRMED on the strength of the three commands above, which trace it end to end
(inputs → wrong output) against real source rather than against a summary. Recording the
provenance difference explicitly so a later round does not inherit a confidence it did not earn
through the skill's own machinery — per `reference.md`: *"Never inherit another reviewer's
confidence."*

---

## 8. Scorecard

| # | Item | Verdict |
| - | ---- | ------- |
| 1 | Skill loaded, exact name `wb:adversarial-review` | **PASS** |
| 2 | Supporting files read via `Read` | **FAIL** — all via `cat`; auto mode was on, hard-stop rule could not fire |
| 3 | Reconnaissance summary names tier **and** the axis that set it | **PASS** — MAX, set by Reversibility |
| 4 | Built-in `/code-review` leg ran, with `(forked execution)` | **NOT RUN** — stopped before Step 4 |
| 5 | Findings with verdicts and concrete failure scenarios | **NOT RUN** as fan-out; 1 CONFIRMED finding from reconnaissance, with scenario |

No rounding up. Items 4 and 5 are recorded as not-run rather than as passes.

## 9. What this session did not establish

Stated so the gaps are not filled in by optimism later:

- **Whether the read conventions hold.** Auto mode made the test unrunnable. Requires a rerun
  with auto mode off, against a plugin installed *outside* the working directory.
- **Whether the built-in leg integrates.** Never invoked. The `(forked execution)` claim in
  `code-review-integration.md` is still unverified by this plan's own smoke testing.
- **Whether the verifier, pooling, dedupe, `ReportFindings` emission, the restatement, or the
  remediation-plan write work at all.** Steps 4–8 did not execute.
- **Whether the fleet finds real defects in this release.** No lens ran. The 3.0.0 branch is
  **unreviewed** by this tool.

## 10. Recommended next actions

1. Rerun P5-T4 with auto mode **off**, against a scoped target (a single subsystem — e.g.
   `plugin/scripts/` or `plugin/skills/adversarial-review/`) so Steps 4–8 actually execute.
   Item 2 and items 4–5 all need this.
2. Treat the missing diff-size gate as a finding against `adversarial-review/SKILL.md` Step 3,
   and the blast-radius filter as a finding against the same step. Neither is fixed here.
3. Do not cite this session as evidence that 3.0.0 has been adversarially reviewed. It has not.
