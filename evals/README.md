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
| `run.py` | Runs `create_research`, `create_design`, and `create_tasks` headless on a fresh copy of the fixture, for one or two plugin trees. |
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
driver sets `status: approved` in `design.md` before `create_tasks`. If `design.md` was not
written, the driver skips `create_tasks` for that repeat. Both trees get the same
treatment.

Output goes to `evals/runs/<timestamp>/<before|after>/<repeat>/`:

- `plan/`: the plan directory after the run
- `<stage>.txt`: the chat output of the stage
- `<stage>.json`: the raw `claude` output, with cost and session ID
- `meta.json`: the working directory, the model, and each stage's result

## Run the checks

```bash
python3 evals/link_check.py
python3 evals/token_check.py
python3 evals/token_check.py <generated>/tasks.md <generated>/journal.md
python3 evals/wbte_check.py <generated>/research.md <chat-output>.txt
```

Each checker exits 0 when every check holds and 1 when a check fails. A file that ends in
`.txt` is chat output for `wbte_check.py`.

Prove that a checker still fires after you change it:

```bash
for f in evals/fixtures/planted/bad-*; do python3 evals/wbte_check.py "$f" && echo "MISSED $f"; done
for f in evals/fixtures/planted/tokens/bad-*; do python3 evals/token_check.py "$f" && echo "MISSED $f"; done
for d in evals/fixtures/planted/links/bad-*/; do python3 evals/link_check.py --root "$d" && echo "MISSED $d"; done
```

## Limits

- The noun-cluster count is a heuristic. Use it as a trend, not as a hard gate.
- The judge is a model output. Read a sample of each report, and compare its verdicts with
  the mechanical counts beside it.
- Each run costs model calls. The report records the wall time and the cost for each tree.
