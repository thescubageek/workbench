#!/usr/bin/env python3
"""Exempt-token and parser-pattern checker.

Maintainer-only. Patterns and the token registry live in evals/tokens.json.

Usage:
  token_check.py [--root DIR]       every registry token is in each file listed for it
  token_check.py [--json] FILE...   run the parser patterns on generated documents

A document's type comes from its name: *tasks.md, *journal.md, *research.md, *design.md.
Exit 0 when every check holds, 1 when one fails, 2 on a usage error.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.join(HERE, "tokens.json")


def load(path=REGISTRY):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check_registry(cfg, root):
    failures = []
    for token, files in cfg["registry"].items():
        for rel in files:
            path = os.path.join(root, rel)
            if not os.path.isfile(path):
                failures.append(f"{rel}: file is missing (registry token {token!r})")
            elif token not in open(path, encoding="utf-8").read():
                failures.append(f"{rel}: exempt token {token!r} is missing")
    return failures


def doc_type(path):
    name = os.path.basename(path)
    for kind in ("tasks", "journal", "research", "design"):
        if name.endswith(f"{kind}.md"):
            return kind
    return None


def frontmatter(text):
    m = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).split("\n"):
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t", "-")):
            fields[key.strip()] = value.strip()
    return fields


def check_frontmatter(cfg, kind, text):
    fm = frontmatter(text)
    if fm is None:
        return ["no frontmatter"]
    spec = cfg["frontmatter"]
    required = spec["required_all"] + (spec["required_tasks"] if kind == "tasks" else [])
    failures = [f"frontmatter key {k!r} is missing" for k in required if k not in fm]
    allowed = spec["status_values"].get(kind)
    if allowed and fm.get("status") not in allowed:
        failures.append(f"status {fm.get('status')!r} is not one of {allowed}")
    return failures


def checkpoint_blocks(p, lines):
    start, end = re.compile(p["checkpoint_heading"]), re.compile(p["checkpoint_end"])
    blocks, current = [], None
    for line in lines:
        if start.match(line):
            if current:
                blocks.append(current)
            current = [line]
        elif current is not None:
            if end.match(line):
                blocks.append(current)
                current = None
            else:
                current.append(line)
    if current:
        blocks.append(current)
    return blocks


def check_tasks(cfg, text):
    p = cfg["patterns"]
    lines = text.split("\n")
    failures = []
    shape = re.compile(p["id_shape"])
    bold = re.compile(p["bold_task_line"])
    for n, line in enumerate(lines, 1):
        m = bold.match(line)
        if m and not shape.match(m.group(1)):
            failures.append(f"line {n}: task ID {m.group(1)!r} has no digit")
    done = sum(1 for line in lines if re.match(p["task_done"], line))
    left = sum(1 for line in lines if re.match(p["task_open"], line))
    if done + left == 0:
        failures.append("no task line matches the task-ID pattern")
    blocks = checkpoint_blocks(p, lines)
    for block in blocks:
        body = "\n".join(block)
        heading = block[0].strip()
        labels = re.findall(p["checkpoint_label"], body)
        if len(labels) < p["checkpoint_min_labels"] or "attestation" not in labels:
            failures.append(f"{heading}: fewer than {p['checkpoint_min_labels']} labels "
                            "or no (attestation) label")
        if p["checkpoint_phrase"] not in body:
            failures.append(f"{heading}: missing {p['checkpoint_phrase']!r}")
        if any(re.match(p["task_done"], l) or re.match(p["task_open"], l) for l in block):
            failures.append(f"{heading}: contains a task-ID-shaped line")
    return failures, {"done": done, "remaining": left, "checkpoints": len(blocks)}


def check_journal(cfg, text):
    p = cfg["patterns"]
    failures = []
    headings = [l for l in text.split("\n")
                if re.match(p["journal_heading"], l) and not re.search(p["journal_placeholder"], l)]
    for h in headings:
        if not re.search(p["journal_suffix"], h, flags=re.I):
            failures.append(f"journal heading does not end in (open) or (closed): {h!r}")
    return failures, {"entries": len(headings)}


def check_document(cfg, path):
    text = open(path, encoding="utf-8").read()
    kind = doc_type(path)
    failures, stats = [], {}
    if kind == "tasks":
        failures, stats = check_tasks(cfg, text)
    elif kind == "journal":
        failures, stats = check_journal(cfg, text)
    if kind in ("tasks", "research", "design"):
        failures += check_frontmatter(cfg, kind, text)
    return {"file": path, "type": kind, "stats": stats, "failures": failures}


def main(argv):
    ap = argparse.ArgumentParser(description="exempt-token and parser-pattern checker")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--root", default=os.path.dirname(HERE),
                    help="repository root for the registry check (default: this repo)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = ap.parse_args(argv)
    cfg = load()

    if not args.files:
        failures = check_registry(cfg, args.root)
        results = [{"file": "registry", "type": None, "stats": {}, "failures": failures}]
    else:
        results = []
        for path in args.files:
            if not os.path.isfile(path):
                print(f"token_check: no such file: {path}", file=sys.stderr)
                return 2
            results.append(check_document(cfg, path))

    failed = any(r["failures"] for r in results)
    if args.json:
        print(json.dumps({"failed": failed, "results": results}, indent=2, ensure_ascii=False))
    else:
        for r in results:
            stats = ", ".join(f"{k} {v}" for k, v in r["stats"].items())
            print(f"{r['file']}" + (f" [{r['type']}]" if r["type"] else "")
                  + (f": {stats}" if stats else ""))
            for f in r["failures"]:
                print(f"FAIL {f}")
        print("FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
