# evals — the wb eval harness

This directory is maintainer tooling. It is never shipped, and nothing under `plugin/` calls
it. It measures stage output before and after a change to the plugin. The rules that it
measures are in `plugin/docs/reference/technical-english.md` (wb Technical English, WBTE).

The harness needs python3 (standard library only) and the `claude` CLI. Neither is a user
requirement.

## Files

| File | What it does |
| ---- | ------------ |
| `fixture/` | The fixed input: a small project (`project/`), the research question (`QUESTION.md`), the expected facts (`expected.json`), and a plan seed (`plan-seed/`). |
| `fixture-large/` | A larger fixture with the same layout. `agents/` holds one fixed task for each research agent (`tasks.json`) and a research document with planted errors (`research.md`). |
| `run.py` | Runs `create-research`, `create-design`, and `create-tasks` headless on a fresh copy of the fixture, for one or two plugin trees. |
| `agent_run.py` | Runs each research agent alone on its fixed task, for one or two plugin trees. |
| `gate.py` | The prose gate. It scores runs from `run.py` or `agent_run.py` and decides PASS, LOSS, or INCONCLUSIVE at a measured false-positive rate. |
| `wbte_check.py` | Measures WBTE metrics: sentence length, prose semicolons, IDs used alone in chat, and noun clusters. |
| `token_check.py` | Checks that templates keep each exempt token, and runs the parser patterns on generated documents. |
| `tokens.json` | The patterns and the token registry that `token_check.py` reads. |
| `link_check.py` | Checks the link lines to the reference doc, the single-authority rule, and that no ASD content is tracked. |
| `judge.py` | An LLM judge. `--within` (the gate) checks that each run's `design.md` and `tasks.md` keep the facts of its own `research.md`. Without it, the judge compares a before document with an after document, which is reliable for `research.md` only. |
| `report.py` | Writes one markdown report for a run. |
| `fixtures/planted/` | Planted failures and clean siblings. Each checker must fail on each bad input. |
| `runs/` | Run output. It is gitignored. |

## Run a comparison

Use the repository root as the working directory.

```bash
python3 evals/run.py --before 4b32306 --after HEAD --repeats 3
python3 evals/judge.py --run evals/runs/<timestamp> --within
python3 evals/report.py evals/runs/<timestamp>
```

A tree is a git ref or a path. A path can be a checkout or a plugin directory, so `.`
measures the working tree. To record a baseline of one tree, omit `--after`.

Each stage is one `claude -p` call from a directory outside the plugin tree. The call uses
`--allowedTools=Skill`, `--permission-mode acceptEdits`, `--add-dir <tree>/plugin`, and a
pinned `--model` (default `sonnet`). Without `--add-dir`, a resumed session is refused reads
of the stage's own supporting files. Some stages stop to ask a question. When that happens, the driver resumes the
session with one fixed reply, at most twice. A headless run cannot approve a design, so the
driver sets `status: approved` in `design.md` before `create-tasks`. If `design.md` was not
written, the driver skips `create-tasks` for that repeat. Both trees get the same
treatment.

Output goes to `evals/runs/<timestamp>/<before|after>/<repeat>/`:

- `plan/`: the plan directory after the run
- `<stage>.txt`: the chat output of the stage
- `<stage>.json`: the raw `claude` output, with cost and session ID
- `meta.json`: the working directory, the model, and each stage's result

## Gate a prose edit

`gate.py` decides whether an edit to stage or agent prose loses content. It compares the loss
with the run-to-run variance that it measures from the before tree.

### The rule

1. Score each run with a count. `facts` counts the expected facts cited at their file:line.
   `files` counts the expected files named. `claims` counts the planted claims judged correctly.
2. Run the after tree n times and the before tree at least 2n times.
3. Split the before runs into two disjoint groups of n, in every way, or in 5,000 random ways.
   Each split gives a drop between two groups that ran the same text.
4. The threshold is the smallest drop that at most 5% of those splits exceed. The measured
   false-positive rate (FPR) is the share of splits that exceed it.
5. The verdict is LOSS when mean(before) − mean(after) exceeds the threshold. Otherwise it is
   PASS.

The verdict is INCONCLUSIVE when the runs cannot measure the rate: fewer than 2 after runs,
fewer than 2n before runs, or fewer than 20 splits. `gate.py` exits 0 on PASS, 1 on LOSS, and 3
on INCONCLUSIVE.

The splits compare n runs with n runs. The gate compares n after runs with all the before runs.
That comparison varies less, so the real false-positive rate is at most the measured one.

### Why the research stage cannot gate a small edit

Six research-stage runs of identical agent text on `fixture-large` cited 4, 5, 9, 9, 10, and 12
of the 19 expected facts. The standard deviation is 3.1 facts. On these runs, the 3.1.0 rule
"after cites fewer facts than before" fires on 48% of before-versus-before splits at 2 repeats.
At a 5% FPR, a 2-repeat stage gate sees only a drop of more than 5 facts.

To see a drop of 2 facts at a 5% FPR, the stage needs about 13 after runs and 26 before runs.
That is about $55 at $1.40 for each research-only run on Sonnet 5.5.

### Gate agent prose

Run each agent alone. This removes the orchestrator's variance: how many agents the stage spawns,
what it asks them, and what it keeps.

```bash
env -u CLAUDE_CODE_PLUGIN_DIRS python3 evals/agent_run.py --before HEAD --after <tree> --repeats 5
python3 evals/gate.py evals/runs/<timestamp>
```

`agent_run.py` runs each agent with `claude -p --agent wb:<name>` on the fixed task in
`fixture-large/agents/tasks.json`. Each prompt is the agent's spawn prompt from its stage, with
the placeholders filled in. The agent's frontmatter sets its model and effort. The before tree
runs twice as often as the after tree, so the gate can measure its FPR. `--agents` limits the run
to some agents, and `--jobs` sets the number of concurrent calls (default 4).

The `files` and `claims` tasks score near their maximum on the current prose. So the gate sees a
loss on these tasks, but it cannot see a gain.

The first gate ran on 2026-10-24, on the 3.1.0 prose edits of the five research agents (run
`20261024T201210Z`). It used 5 after runs and 10 before runs for each agent, and it cost $12.38.

| Agent | Score | Before (mean) | After (mean) | Threshold | Measured FPR | Verdict |
| ----- | ----- | ------------- | ------------ | --------- | ------------ | ------- |
| `codebase-locator` | files, of 24 | 24.0 | 24.0 | 0.0 | 0.000 | PASS |
| `pattern-finder` | facts, of 19 | 10.4 | 10.4 | 0.8 | 0.024 | PASS |
| `codebase-analyzer` | facts, of 19 | 5.6 | 6.0 | 1.6 | 0.016 | PASS |
| `research-validator` | claims, of 14 | 13.7 | 13.8 | 0.6 | 0.000 | PASS |
| `product-behavior-analyzer` | facts, of 19 | 9.0 | 9.2 | 2.8 | 0.028 | PASS |

A measured FPR of 0 comes from 10 before runs. It does not prove a true rate of 0.

### Gate stage prose

Use `run.py` for the before/after runs, and a baseline of the before tree for the extra before
runs. Pass both run directories to `gate.py`.

```bash
env -u CLAUDE_CODE_PLUGIN_DIRS python3 evals/run.py --before <ref> --after <tree> --repeats 13 --stages research --fixture evals/fixture-large
env -u CLAUDE_CODE_PLUGIN_DIRS python3 evals/run.py --before <ref> --repeats 13 --stages research --fixture evals/fixture-large
python3 evals/gate.py evals/runs/<first> evals/runs/<second>
```

For `design.md` and `tasks.md`, use `judge.py --within`. It judges each run against its own
`research.md`, so it does not depend on the research variance.

## Run the checks

```bash
python3 evals/link_check.py
python3 evals/token_check.py
python3 evals/token_check.py <generated>/tasks.md <generated>/journal.md
python3 evals/wbte_check.py <generated>/research.md <chat-output>.txt
python3 evals/wbte_check.py --pr [--template <repo>/.github/pull_request_template.md] <pr-body>.md
```

Each checker exits 0 when every check holds and 1 when a check fails. A file that ends in
`.txt` is chat output for `wbte_check.py`. With `--pr`, `wbte_check.py` also checks a PR body:
it warns above 250 words, and fails above 400 words or above 150 words in one section. With
`--template`, a line copied from the repository's PR template is neither counted nor checked.

Prove that a checker still fires after you change it:

```bash
for f in evals/fixtures/planted/bad-*; do python3 evals/wbte_check.py "$f" && echo "MISSED $f"; done
for f in evals/fixtures/planted/tokens/bad-*; do python3 evals/token_check.py "$f" && echo "MISSED $f"; done
for d in evals/fixtures/planted/links/bad-*/; do python3 evals/link_check.py --root "$d" && echo "MISSED $d"; done
python3 evals/wbte_check.py --pr evals/fixtures/planted/pr/bad-pr-long.md && echo "MISSED the long PR body"
python3 evals/wbte_check.py --pr --template evals/fixtures/planted/pr/template.md evals/fixtures/planted/pr/templated-pr.md || echo "FLAGGED template text"
python3 evals/gate.py --scores evals/fixtures/planted/gate/bad-loss.json >/dev/null && echo "MISSED the planted loss"
python3 evals/gate.py --scores evals/fixtures/planted/gate/clean-same.json >/dev/null || echo "FLAGGED the clean scores"
```

## Limits

- The noun-cluster count is a heuristic. Use it as a trend, not as a hard gate.
- The judge is a model output. Read a sample of each report, and compare its verdicts with
  the mechanical counts beside it.
- Each run costs model calls. The report records the wall time and the cost for each tree.
