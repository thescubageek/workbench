#!/usr/bin/env python3
"""Write RUN_DIR/report.md for a run from run.py.

Maintainer-only. It runs wbte_check.py on the documents and on the chat output of each tree,
token_check.py on each document, and reads the judge verdicts from RUN_DIR/judge/ if they
exist.

Usage: report.py RUN_DIR [--out FILE]
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from judge import load_facts, mechanical  # noqa: E402

DOC_STAGES = {"research": "research.md", "design": "design.md", "tasks": "tasks.md"}


def tool(script, args):
    proc = subprocess.run([sys.executable, os.path.join(HERE, script), "--json", *args],
                          capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return None


def tree_files(run_dir, tree, manifest):
    docs, chats, runs = [], [], []
    for run in manifest["runs"]:
        if run["tree"] != tree:
            continue
        base = os.path.join(run_dir, tree, str(run["repeat"]))
        runs.append(run)
        for stage in run["stages"]:
            name = stage["stage"]
            if name in DOC_STAGES and stage.get("written"):
                docs.append(os.path.join(base, "plan", DOC_STAGES[name]))
            txt = os.path.join(base, f"{name}.txt")
            if name in DOC_STAGES and os.path.isfile(txt) and os.path.getsize(txt) > 1:
                chats.append(txt)
    return docs, chats, runs


def tree_summary(run_dir, tree, manifest, facts):
    docs, chats, runs = tree_files(run_dir, tree, manifest)
    doc_m = tool("wbte_check.py", docs) if docs else None
    chat_m = tool("wbte_check.py", chats) if chats else None
    tokens = tool("token_check.py", docs) if docs else None
    stages = [s for r in runs for s in r["stages"] if s["stage"] in DOC_STAGES]
    cited = []
    for r in runs:
        path = os.path.join(run_dir, tree, str(r["repeat"]), "plan", "research.md")
        if os.path.isfile(path):
            cited.append(len(mechanical(open(path, encoding="utf-8").read(), facts)
                             ["expected_facts_cited"]))

    def total(m, key):
        return sum(len(x[key]) if isinstance(x[key], list) else x[key] for x in m["results"]) if m else 0

    return {
        "repeats": len(runs),
        "stages_written": sum(1 for s in stages if s.get("written")),
        "stages_run": len(stages),
        "follow_ups": sum(s.get("follow_ups", 0) for s in stages),
        "seconds": round(sum(s.get("seconds", 0) for s in stages)),
        "cost_usd": round(sum(s.get("cost_usd", 0) for s in stages), 2),
        "doc_sentences": doc_m["sentences"] if doc_m else 0,
        "doc_over_25_share": doc_m["over_25_share"] if doc_m else 0,
        "doc_semicolons": total(doc_m, "semicolons"),
        "doc_noun_clusters": total(doc_m, "noun_clusters"),
        "doc_max_words": max((x["max_words"] for x in doc_m["results"]), default=0) if doc_m else 0,
        "chat_sentences": chat_m["sentences"] if chat_m else 0,
        "chat_over_25_share": chat_m["over_25_share"] if chat_m else 0,
        "chat_semicolons": total(chat_m, "semicolons"),
        "chat_lone_ids": total(chat_m, "lone_ids"),
        "token_failures": sum(len(r["failures"]) for r in tokens["results"]) if tokens else 0,
        "token_failure_lines": [f"{os.path.relpath(r['file'], run_dir)}: {f}"
                                for r in (tokens["results"] if tokens else []) for f in r["failures"]],
        "facts_cited_per_repeat": cited,
    }


ROWS = [
    ("Stages written / run", lambda s: f"{s['stages_written']} / {s['stages_run']}"),
    ("Follow-up replies", lambda s: s["follow_ups"]),
    ("Document sentences", lambda s: s["doc_sentences"]),
    ("Document sentences over 25 words", lambda s: f"{s['doc_over_25_share']:.1%}"),
    ("Longest document sentence (words)", lambda s: s["doc_max_words"]),
    ("Document semicolons", lambda s: s["doc_semicolons"]),
    ("Document noun clusters (heuristic)", lambda s: s["doc_noun_clusters"]),
    ("Chat sentences", lambda s: s["chat_sentences"]),
    ("Chat sentences over 25 words", lambda s: f"{s['chat_over_25_share']:.1%}"),
    ("Chat semicolons", lambda s: s["chat_semicolons"]),
    ("Chat IDs used alone", lambda s: s["chat_lone_ids"]),
    ("Parser-token failures", lambda s: s["token_failures"]),
    ("Expected facts cited in research.md, per repeat", lambda s: ", ".join(map(str, s["facts_cited_per_repeat"])) or "none"),
    ("Wall time (s)", lambda s: s["seconds"]),
    ("Cost (USD)", lambda s: s["cost_usd"]),
]


def render(run_dir, manifest, summaries, verdicts):
    trees = list(summaries)
    lines = [f"# Eval report: {manifest['started']}", ""]
    lines += ["This report compares the output of each plugin tree on the fixture. "
              "The metric rules are in `plugin/docs/reference/technical-english.md`.", ""]
    lines += ["| Tree | Source | Version |", "| ---- | ------ | ------- |"]
    for t, info in manifest["trees"].items():
        src = info.get("sha", info.get("source", info.get("spec")))
        lines.append(f"| {t} | `{src}` | {info.get('version')} |")
    lines += ["", f"Model: `{manifest['model']}`. Repeats: {manifest['repeats']}. "
              f"Stages: {', '.join(manifest['stages'])}.", ""]
    lines += ["## Metrics", "", "| Metric | " + " | ".join(trees) + " |",
              "| ------ | " + " | ".join("---" for _ in trees) + " |"]
    for label, fn in ROWS:
        lines.append(f"| {label} | " + " | ".join(str(fn(summaries[t])) for t in trees) + " |")
    lines += ["", "## Fidelity judge", ""]
    if verdicts:
        lines += ["| Repeat | Verdict | Lost facts | Lost refs | Lost IDs | Lost barriers | Other |",
                  "| ------ | ------- | ---------- | --------- | -------- | ------------- | ----- |"]
        for v in verdicts:
            agg = {k: sorted({x for p in v["pairs"] for x in p["llm"].get(k, [])})
                   for k in ("lost_facts", "lost_refs", "lost_ids", "lost_barriers", "other_losses")}
            lines.append(f"| {v['repeat']} | {'loss' if v['loss'] else 'no loss'} | "
                         + " | ".join(", ".join(agg[k]) or "none" for k in agg) + " |")
    else:
        lines.append("No judge verdicts. Run `python3 evals/judge.py --run <dir>` first.")
    failures = [(t, f) for t in trees for f in summaries[t]["token_failure_lines"]]
    lines += ["", "## Parser-token failures", ""]
    lines += [f"- {t}: {f}" for t, f in failures] or ["None."]
    lines += ["", "## Read a sample", "",
              "A human reads one document and one chat output from each tree. "
              "The files are in `<tree>/<repeat>/plan/` and `<tree>/<repeat>/<stage>.txt`.", ""]
    return "\n".join(lines)


def main(argv):
    ap = argparse.ArgumentParser(description="write the eval report for a run")
    ap.add_argument("run_dir")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    manifest_path = os.path.join(args.run_dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        print(f"report: no manifest.json in {args.run_dir}", file=sys.stderr)
        return 2
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    facts = load_facts()
    summaries = {t: tree_summary(args.run_dir, t, manifest, facts) for t in manifest["trees"]}
    judge_dir = os.path.join(args.run_dir, "judge")
    verdicts = [json.load(open(os.path.join(judge_dir, f), encoding="utf-8"))
                for f in sorted(os.listdir(judge_dir))] if os.path.isdir(judge_dir) else []
    out = args.out or os.path.join(args.run_dir, "report.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(render(args.run_dir, manifest, summaries, verdicts))
    with open(os.path.splitext(out)[0] + ".json", "w", encoding="utf-8") as fh:
        json.dump(summaries, fh, indent=2)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
