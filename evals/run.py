#!/usr/bin/env python3
"""Before/after driver: run the wb stages headless on the fixture, for two plugin trees.

Maintainer-only. It follows the probe in
docs/plans/2026-09-29-asd-ste100-prose/thoughts/2026-09-30-harness-probe.md.

Usage: run.py --before REF_OR_PATH [--after REF_OR_PATH] [--repeats N] [--model M]
              [--stages research,design,tasks] [--timeout SECONDS] [--fixture DIR]

A tree is a git ref (archived with `git archive <ref> plugin`) or a path to a checkout or a
plugin directory. With no --after, only the before tree runs (a baseline). Each repeat gets a fresh copy of evals/fixture/project with the plan seed at
docs/plans/2026-01-01-fixture/. Stages run in order: create_research, create_design,
create_tasks. A headless run cannot approve a design, so the driver sets `status: approved`
in design.md before create_tasks, and skips create_tasks when design.md was not written.
Every call gets `--add-dir <tree>/plugin`: a resumed session is refused reads of the stage's
own supporting files without it, while a marketplace install can read them. When a stage stops to ask, the driver resumes the session
with one fixed reply. Both trees get the same replies.

Output: evals/runs/<timestamp>/<before|after>/<repeat>/ with the plan documents, the chat
output of each stage (<stage>.txt), the raw JSON (<stage>.json), and meta.json.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FIXTURE = os.path.join(HERE, "fixture")
PLAN_REL = "docs/plans/2026-01-01-fixture"
STAGES = {
    "research": {"skill": "create_research", "doc": "research.md", "question": True},
    "design": {"skill": "create_design", "doc": "design.md", "question": False},
    "tasks": {"skill": "create_tasks", "doc": "tasks.md", "question": False},
}
FOLLOW_UP = ("This is a headless evaluation run and no human can answer. Take the option you "
             "recommend, treat it as chosen, and finish the stage. Do not ask again.")
MAX_FOLLOW_UPS = 2


def build_tree(spec, dest):
    """Materialize a plugin tree at dest/plugin from a git ref or a path."""
    os.makedirs(dest)
    if os.path.isdir(spec):
        src = os.path.join(spec, "plugin") if os.path.isdir(os.path.join(spec, "plugin")) else spec
        shutil.copytree(src, os.path.join(dest, "plugin"),
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        return {"spec": spec, "kind": "path", "source": os.path.abspath(src)}
    sha = subprocess.run(["git", "-C", REPO, "rev-parse", spec], capture_output=True,
                         text=True, check=True).stdout.strip()
    archive = subprocess.run(["git", "-C", REPO, "archive", sha, "plugin"], capture_output=True,
                             check=True).stdout
    subprocess.run(["tar", "-x", "-C", dest], input=archive, check=True)
    return {"spec": spec, "kind": "ref", "sha": sha}


def plugin_version(tree):
    try:
        with open(os.path.join(tree, "plugin", ".claude-plugin", "plugin.json")) as fh:
            return json.load(fh).get("version")
    except (OSError, ValueError):
        return None


def fresh_run_copy(dest, fixture=FIXTURE):
    shutil.copytree(os.path.join(fixture, "project"), dest)
    shutil.copytree(os.path.join(fixture, "plan-seed"), os.path.join(dest, PLAN_REL))
    for cmd in (["git", "init", "-q"], ["git", "add", "-A"],
                ["git", "-c", "user.name=wb-eval", "-c", "user.email=wb-eval@invalid",
                 "commit", "-qm", "fixture"]):
        subprocess.run(cmd, cwd=dest, check=True)


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def claude(args, cwd, timeout):
    start = time.time()
    try:
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        out, err, code = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err, code = f"timeout after {timeout} s", None
    try:
        data = json.loads(out)
    except ValueError:
        data = None
    return {"exit": code, "seconds": round(time.time() - start, 1), "stderr": err,
            "raw": out, "json": data}


def approve_design(path):
    text = read(path)
    if text is None:
        return False
    new, n = re.subn(r"^status:.*$", "status: approved", text, count=1, flags=re.M)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new)
    return n == 1


def run_stage(name, tree, run_dir, out_dir, model, timeout, fixture=FIXTURE):
    stage = STAGES[name]
    doc = os.path.join(run_dir, PLAN_REL, stage["doc"])
    before = read(doc)
    prompt = f"/wb:{stage['skill']} {PLAN_REL}"
    if stage["question"]:
        prompt += " " + read(os.path.join(fixture, "QUESTION.md")).strip()
    plugin = os.path.join(tree, "plugin")
    base = ["claude", "-p", "--plugin-dir", plugin, "--add-dir", plugin,
            "--allowedTools=Skill", "--permission-mode", "acceptEdits",
            "--model", model, "--output-format", "json"]
    calls, texts = [], []
    call = claude(base + [prompt], run_dir, timeout)
    calls.append({"prompt": prompt, **call})
    for _ in range(MAX_FOLLOW_UPS):
        if read(doc) != before or not call["json"] or not call["json"].get("session_id"):
            break
        call = claude(base + ["--resume", call["json"]["session_id"], FOLLOW_UP], run_dir, timeout)
        calls.append({"prompt": FOLLOW_UP, **call})

    for i, c in enumerate(calls):
        texts.append((c["json"] or {}).get("result") or "")
        suffix = "" if i == 0 else f".follow-up-{i}"
        with open(os.path.join(out_dir, f"{name}{suffix}.json"), "w", encoding="utf-8") as fh:
            fh.write(c["raw"])
    with open(os.path.join(out_dir, f"{name}.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n\n".join(t for t in texts if t) + "\n")

    after = read(doc)
    return {
        "stage": name,
        "prompt": prompt,
        "follow_ups": len(calls) - 1,
        "written": after is not None and after != before,
        "exit_codes": [c["exit"] for c in calls],
        "seconds": round(sum(c["seconds"] for c in calls), 1),
        "cost_usd": round(sum((c["json"] or {}).get("total_cost_usd") or 0 for c in calls), 4),
        "stderr": [c["stderr"] for c in calls if c["stderr"]],
    }


def run_repeat(label, tree, repeat, out_root, args):
    out_dir = os.path.join(out_root, label, str(repeat))
    os.makedirs(out_dir)
    work = tempfile.mkdtemp(prefix=f"wb-eval-{label}-{repeat}-")
    run_dir = os.path.join(work, "run")
    fresh_run_copy(run_dir, args.fixture)
    stages = []
    for name in args.stages:
        if name == "tasks":
            design = [s for s in stages if s["stage"] == "design"]
            if design and not design[0]["written"]:
                stages.append({"stage": "tasks", "skipped": "design.md was not written"})
                print(f"  {label} #{repeat} tasks: skipped, design.md was not written", flush=True)
                continue
            stages.append({"stage": "approve", "approved":
                           approve_design(os.path.join(run_dir, PLAN_REL, "design.md"))})
        result = run_stage(name, tree, run_dir, out_dir, args.model, args.timeout, args.fixture)
        stages.append(result)
        print(f"  {label} #{repeat} {name}: written={result['written']} "
              f"follow_ups={result['follow_ups']} {result['seconds']} s", flush=True)
    shutil.copytree(os.path.join(run_dir, PLAN_REL), os.path.join(out_dir, "plan"))
    meta = {"tree": label, "repeat": repeat, "cwd": run_dir, "model": args.model,
            "stages": stages}
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    return meta


def main(argv):
    ap = argparse.ArgumentParser(description="wb before/after stage driver")
    ap.add_argument("--before", required=True, help="git ref or path")
    ap.add_argument("--after", help="git ref or path (omit for a baseline of one tree)")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--model", default="sonnet", help="pinned model (default sonnet)")
    ap.add_argument("--stages", default="research,design,tasks")
    ap.add_argument("--timeout", type=int, default=1200, help="seconds per claude call")
    ap.add_argument("--out", default=os.path.join(HERE, "runs"))
    ap.add_argument("--fixture", default=FIXTURE,
                    help="fixture directory (default evals/fixture)")
    args = ap.parse_args(argv)
    args.fixture = os.path.abspath(args.fixture)
    args.stages = [s for s in args.stages.split(",") if s]
    unknown = [s for s in args.stages if s not in STAGES]
    if unknown or not args.stages:
        print(f"run.py: unknown stage(s): {unknown}", file=sys.stderr)
        return 2

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_root = os.path.join(args.out, stamp)
    trees_dir = tempfile.mkdtemp(prefix="wb-eval-trees-")
    trees = {}
    for label, spec in (("before", args.before), ("after", args.after)):
        if spec is None:
            continue
        path = os.path.join(trees_dir, label)
        info = build_tree(spec, path)
        info["version"] = plugin_version(path)
        trees[label] = (path, info)
    os.makedirs(out_root)
    manifest = {"started": stamp, "model": args.model, "repeats": args.repeats,
                "fixture": os.path.relpath(args.fixture, REPO),
                "stages": args.stages, "follow_up": FOLLOW_UP,
                "trees": {k: v[1] for k, v in trees.items()}, "runs": []}
    print(f"run: {out_root}", flush=True)
    for repeat in range(1, args.repeats + 1):
        for label, (path, _) in trees.items():
            meta = run_repeat(label, path, repeat, out_root, args)
            manifest["runs"].append({"tree": label, "repeat": repeat,
                                     "stages": meta["stages"]})
            with open(os.path.join(out_root, "manifest.json"), "w", encoding="utf-8") as fh:
                json.dump(manifest, fh, indent=2)
    shutil.rmtree(trees_dir, ignore_errors=True)
    failed = [f"{r['tree']} #{r['repeat']} {s['stage']}" for r in manifest["runs"]
              for s in r["stages"] if s.get("written") is False]
    print(f"done: {out_root}")
    for f in failed:
        print(f"NOT WRITTEN {f}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
