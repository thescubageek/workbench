#!/usr/bin/env python3
"""Fidelity judge: does generated output lose content?

Maintainer-only. An LLM (`claude -p`, with no tools, no plugins, and no user settings) makes
each judgment. Mechanical counts run beside it, so a reader can check the verdict.

Two modes:
- Within-run (design.md D7, the gate): does a run's design.md and tasks.md carry forward the
  facts, file:line references and IDs of that run's own research.md?
- Before/after: does an "after" document lose content that the "before" document has? Two
  runs of the same tree choose different designs, so this mode is reliable for research.md
  only (thoughts/2026-09-30-judge-calibration.md).

Usage:
  judge.py --run RUN_DIR --within [--fixture DIR] [--model M]   within-run, every tree and repeat
  judge.py --research FILE --doc FILE [--context FILE] [--model M]
  judge.py --run RUN_DIR [--model M]            before/<n> against after/<n>, every n
  judge.py --before FILE --after FILE [--model M]

With --run, the verdicts go to RUN_DIR/judge/. Exit 0 when no loss is found, 1 when the judge
finds a loss, 2 on a usage or judge error.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EXPECTED = os.path.join(HERE, "fixture", "expected.json")
DOCS = ("research.md", "design.md", "tasks.md")
REF_RE = re.compile(r"[\w./-]+\.[A-Za-z]{1,5}:\d+(?:-\d+)?")
ID_RE = re.compile(r"\*\*([A-Z0-9-]*[0-9][A-Z0-9-]*)\*\*|\b(Q\d+|A\d+|PD\d+|D-Q\d+|UIQ\d+)\b")

PROMPT = """You are a fidelity judge for generated software-planning documents.

Two documents answer the same request about the same small project. BEFORE came from the old
version of a tool, AFTER from the new version. The new version changes only the writing style.
Decide whether AFTER lost content that BEFORE has. A loss is any of these:

- an expected fact (listed below) that BEFORE states and AFTER does not state
- a file:line reference in BEFORE whose fact AFTER does not cite at all
- a task, question, assumption, or decision ID in BEFORE that AFTER drops, when the item
  it names is also gone
- a barrier or checkpoint (a line with ⛔) in BEFORE that AFTER drops

Do not count differences in wording, order, sentence length, or formatting. Do not count
content that AFTER adds. Two runs of a model differ a little. Count only a substantive loss.

Expected facts (id, fact, file:line):
{facts}

Reply with JSON only, no prose, in this shape:
{{"lost_facts": ["F1"], "lost_refs": ["path:line"], "lost_ids": ["P1-T2"],
  "lost_barriers": ["text"], "other_losses": ["text"], "verdict": "loss" or "no-loss"}}

=== BEFORE ({name}) ===
{before}

=== AFTER ({name}) ===
{after}
"""


WITHIN_PROMPT = """You are a fidelity judge for generated software-planning documents.

RESEARCH is the fact base for a small project. {kind} was written from it in the same run.
{context_note}Decide whether {kind} lost or broke content from RESEARCH that it needs. A loss is
any of these:

- a fact in RESEARCH that {kind} contradicts or states wrongly
- a fact in RESEARCH that a decision, requirement, task, or risk in {kind} depends on, and
  that {kind} omits or gets wrong where it is needed
- a file:line reference that {kind} cites for a different fact than RESEARCH gives for it
- an open question, assumption, or pending-decision ID from RESEARCH that {kind} drops while
  the item is still open
- a setting, default, limit, or behavior from RESEARCH that {kind} mentions without the
  RESEARCH value or its file:line, for example "the existing default" with no number and no
  reference

{kind} chose one approach. Do not count a RESEARCH fact that the chosen approach does not
need. Do not count differences in wording, order, sentence length, or formatting. Do not count
content that {kind} adds. Count only a substantive loss.

Expected facts in RESEARCH (id, fact, file:line):
{facts}

Reply with JSON only, no prose, in this shape:
{{"lost_facts": ["F1"], "lost_refs": ["path:line"], "lost_ids": ["Q1"],
  "lost_barriers": [], "other_losses": ["text"], "verdict": "loss" or "no-loss"}}

=== RESEARCH ===
{research}
{context_block}
=== {kind} ({name}) ===
{doc}
"""


def load_facts(path=EXPECTED):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("facts", data) if isinstance(data, dict) else data


def mechanical(text, facts):
    refs = set(REF_RE.findall(text))
    ids = {a or b for a, b in ID_RE.findall(text)}
    cited = []
    for f in facts:
        path, line = f["ref"].rsplit(":", 1)
        base = path.split("/")[-1]
        if any(r.rsplit(":", 1)[0].endswith(base) and r.rsplit(":", 1)[1].split("-")[0] == line
               for r in refs):
            cited.append(f["id"])
    return {"refs": len(refs), "ids": len(ids), "barriers": text.count("⛔"),
            "expected_facts_cited": sorted(cited)}


def ask(prompt, model):
    cwd = tempfile.mkdtemp(prefix="wb-judge-")
    proc = subprocess.run(
        ["claude", "-p", "--tools", "", "--setting-sources", "project", "--strict-mcp-config",
         "--model", model, "--output-format", "json", prompt],
        cwd=cwd, capture_output=True, text=True, timeout=900)
    try:
        result = json.loads(proc.stdout)["result"]
        match = re.search(r"\{.*\}", result, flags=re.S)
        return json.loads(match.group(0))
    except (ValueError, KeyError, TypeError, AttributeError):
        raise RuntimeError(f"judge reply is not JSON: {proc.stdout[:500]} {proc.stderr[:500]}")


def judge_pair(before_path, after_path, model, facts):
    before = open(before_path, encoding="utf-8").read()
    after = open(after_path, encoding="utf-8").read()
    fact_lines = "\n".join(f"- {f['id']}: {f['fact']} ({f['ref']})" for f in facts)
    name = os.path.basename(after_path)
    verdict = ask(PROMPT.format(facts=fact_lines, name=name, before=before, after=after), model)
    return {"before": before_path, "after": after_path, "llm": verdict,
            "mechanical": {"before": mechanical(before, facts), "after": mechanical(after, facts)},
            "loss": verdict.get("verdict") == "loss"}


def judge_within(research_path, doc_path, model, facts, context_path=None):
    research = open(research_path, encoding="utf-8").read()
    doc = open(doc_path, encoding="utf-8").read()
    name = os.path.basename(doc_path)
    kind = "PLAN" if "tasks" in name else "DESIGN"
    context_note, context_block = "", ""
    if context_path:
        context_note = "DESIGN is context only: it says what PLAN must implement.\n"
        context_block = "\n=== DESIGN (context) ===\n" + open(context_path, encoding="utf-8").read() + "\n"
    fact_lines = "\n".join(f"- {f['id']}: {f['fact']} ({f['ref']})" for f in facts)
    verdict = ask(WITHIN_PROMPT.format(kind=kind, context_note=context_note, facts=fact_lines,
                                       research=research, context_block=context_block,
                                       name=name, doc=doc), model)
    return {"before": research_path, "after": doc_path, "mode": "within", "llm": verdict,
            "mechanical": {"before": mechanical(research, facts), "after": mechanical(doc, facts)},
            "loss": verdict.get("verdict") == "loss"}


def judge_run_within(run_dir, model, facts):
    results = []
    os.makedirs(os.path.join(run_dir, "judge"), exist_ok=True)
    for tree in ("before", "after"):
        root = os.path.join(run_dir, tree)
        if not os.path.isdir(root):
            continue
        for repeat in sorted(os.listdir(root), key=lambda s: int(s) if s.isdigit() else 0):
            plan = os.path.join(root, repeat, "plan")
            research = os.path.join(plan, "research.md")
            if not os.path.isfile(research):
                continue
            pairs = []
            design = os.path.join(plan, "design.md")
            tasks = os.path.join(plan, "tasks.md")
            if os.path.isfile(design):
                pairs.append(judge_within(research, design, model, facts))
            if os.path.isfile(tasks):
                pairs.append(judge_within(research, tasks, model, facts,
                                          design if os.path.isfile(design) else None))
            out = {"repeat": f"{tree}/{repeat} (within)", "tree": tree, "mode": "within",
                   "loss": any(p["loss"] for p in pairs), "pairs": pairs}
            with open(os.path.join(run_dir, "judge", f"within-{tree}-{repeat}.json"), "w",
                      encoding="utf-8") as fh:
                json.dump(out, fh, indent=2, ensure_ascii=False)
            results.append(out)
    return results


def judge_run(run_dir, model, facts):
    results = []
    before_root = os.path.join(run_dir, "before")
    after_root = os.path.join(run_dir, "after")
    os.makedirs(os.path.join(run_dir, "judge"), exist_ok=True)
    for repeat in sorted(os.listdir(before_root), key=lambda s: int(s) if s.isdigit() else 0):
        pairs = []
        for doc in DOCS:
            b = os.path.join(before_root, repeat, "plan", doc)
            a = os.path.join(after_root, repeat, "plan", doc)
            if os.path.isfile(b) and os.path.isfile(a):
                pairs.append(judge_pair(b, a, model, facts))
        out = {"repeat": repeat, "loss": any(p["loss"] for p in pairs), "pairs": pairs}
        with open(os.path.join(run_dir, "judge", f"{repeat}.json"), "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, ensure_ascii=False)
        results.append(out)
    return results


def main(argv):
    ap = argparse.ArgumentParser(description="wb fidelity judge")
    ap.add_argument("--run", help="a run directory from run.py")
    ap.add_argument("--before", help="a before document")
    ap.add_argument("--after", help="an after document")
    ap.add_argument("--within", action="store_true",
                    help="with --run: judge each run against its own research.md (D7)")
    ap.add_argument("--research", help="a research.md, for one within-run judgment")
    ap.add_argument("--doc", help="the design.md or tasks.md to judge against --research")
    ap.add_argument("--context", help="with --doc tasks.md: the run's design.md, as context")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--fixture", help="fixture directory whose expected.json lists the facts (default evals/fixture)")
    args = ap.parse_args(argv)
    facts = load_facts(os.path.join(args.fixture, "expected.json") if args.fixture else EXPECTED)
    try:
        if args.run and args.within:
            results = judge_run_within(args.run, args.model, facts)
            for r in results:
                print(f"{r['repeat']}: {'LOSS' if r['loss'] else 'no loss'}")
            return 1 if any(r["loss"] for r in results) else 0
        if args.research and args.doc:
            result = judge_within(args.research, args.doc, args.model, facts, args.context)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 1 if result["loss"] else 0
        if args.run:
            if not os.path.isdir(os.path.join(args.run, "after")):
                print("judge: the run has no after tree", file=sys.stderr)
                return 2
            results = judge_run(args.run, args.model, facts)
            for r in results:
                print(f"repeat {r['repeat']}: {'LOSS' if r['loss'] else 'no loss'}")
            return 1 if any(r["loss"] for r in results) else 0
        if args.before and args.after:
            result = judge_pair(args.before, args.after, args.model, facts)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 1 if result["loss"] else 0
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"judge: {exc}", file=sys.stderr)
        return 2
    ap.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
