#!/usr/bin/env python3
"""Agent driver: run each research agent headless on one fixed task, for one or two plugin trees.

Maintainer-only. A research-stage run varies with the orchestrator: how many agents it spawns,
what it asks them, and what it keeps. This driver removes that variance. It runs each agent
alone (`claude -p --agent wb:<name>`) on the fixed task in <fixture>/agents/tasks.json, so two
trees differ only in the agent's own prose. gate.py scores the output and decides.

Usage: agent_run.py --before REF_OR_PATH [--after REF_OR_PATH] [--repeats N]
                    [--before-repeats N] [--agents a,b] [--jobs N] [--timeout SECONDS]
                    [--fixture DIR]

A tree is a git ref or a path, as for run.py. The before tree runs --before-repeats times
(default twice --repeats), because gate.py measures its false-positive rate by splitting the
before runs into two groups of --repeats. The agent's frontmatter sets its model and effort, so
the driver passes no --model. Each run gets a fresh git copy of <fixture>/project, with
<fixture>/agents/research.md at docs/research.md for the research-validator task.

Output: evals/runs/<timestamp>/<tree>/<agent>/<repeat>/ with output.md (the agent's reply),
output.json (the raw `claude` output), and meta.json. manifest.json lists every run.
"""

import argparse
import concurrent.futures
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run import REPO, build_tree, claude, plugin_version  # noqa: E402

FIXTURE = os.path.join(HERE, "fixture-large")


def load_tasks(fixture):
    with open(os.path.join(fixture, "agents", "tasks.json"), encoding="utf-8") as fh:
        return json.load(fh)["agents"]


def fresh_copy(dest, fixture):
    shutil.copytree(os.path.join(fixture, "project"), dest)
    os.makedirs(os.path.join(dest, "docs"), exist_ok=True)
    shutil.copy(os.path.join(fixture, "agents", "research.md"),
                os.path.join(dest, "docs", "research.md"))
    for cmd in (["git", "init", "-q"], ["git", "add", "-A"],
                ["git", "-c", "user.name=wb-eval", "-c", "user.email=wb-eval@invalid",
                 "commit", "-qm", "fixture"]):
        subprocess.run(cmd, cwd=dest, check=True)


def run_one(job, tasks, args, out_root):
    label, tree, agent, repeat = job
    out_dir = os.path.join(out_root, label, agent, str(repeat))
    os.makedirs(out_dir)
    work = tempfile.mkdtemp(prefix=f"wb-agent-{label}-{agent}-{repeat}-")
    run_dir = os.path.join(work, "run")
    fresh_copy(run_dir, args.fixture)
    plugin = os.path.join(tree, "plugin")
    call = claude(["claude", "-p", "--plugin-dir", plugin, "--add-dir", plugin,
                   "--agent", f"wb:{agent}", "--setting-sources", "project",
                   "--strict-mcp-config", "--output-format", "json", tasks[agent]["prompt"]],
                  run_dir, args.timeout)
    data = call["json"] or {}
    with open(os.path.join(out_dir, "output.json"), "w", encoding="utf-8") as fh:
        fh.write(call["raw"])
    with open(os.path.join(out_dir, "output.md"), "w", encoding="utf-8") as fh:
        fh.write((data.get("result") or "") + "\n")
    meta = {"tree": label, "agent": agent, "repeat": repeat, "cwd": run_dir,
            "exit": call["exit"], "seconds": call["seconds"],
            "cost_usd": round(data.get("total_cost_usd") or 0, 4),
            "turns": data.get("num_turns"), "models": sorted(data.get("modelUsage") or {}),
            "permission_denials": len(data.get("permission_denials") or []),
            "written": bool(data.get("result")), "stderr": call["stderr"]}
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    shutil.rmtree(work, ignore_errors=True)
    return meta


def main(argv):
    ap = argparse.ArgumentParser(description="wb agent-level driver")
    ap.add_argument("--before", required=True, help="git ref or path")
    ap.add_argument("--after", help="git ref or path (omit for a baseline of one tree)")
    ap.add_argument("--repeats", type=int, default=5, help="after-tree runs per agent")
    ap.add_argument("--before-repeats", type=int,
                    help="before-tree runs per agent (default twice --repeats)")
    ap.add_argument("--agents", help="comma-separated agent names (default every task)")
    ap.add_argument("--jobs", type=int, default=4, help="concurrent claude calls")
    ap.add_argument("--timeout", type=int, default=900, help="seconds per claude call")
    ap.add_argument("--out", default=os.path.join(HERE, "runs"))
    ap.add_argument("--fixture", default=FIXTURE, help="fixture directory (default evals/fixture-large)")
    args = ap.parse_args(argv)
    args.fixture = os.path.abspath(args.fixture)
    tasks = load_tasks(args.fixture)
    agents = [a for a in (args.agents or ",".join(tasks)).split(",") if a]
    unknown = [a for a in agents if a not in tasks]
    if unknown or not agents:
        print(f"agent_run.py: no task for agent(s): {unknown}", file=sys.stderr)
        return 2
    before_repeats = args.before_repeats or 2 * args.repeats

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
    counts = {"before": before_repeats, "after": args.repeats}
    jobs = [(label, path, agent, repeat)
            for repeat in range(1, max(counts[t] for t in trees) + 1)
            for agent in agents for label, (path, _) in trees.items() if repeat <= counts[label]]
    manifest = {"kind": "agents", "started": stamp, "fixture": os.path.relpath(args.fixture, REPO),
                "agents": agents, "repeats": {t: counts[t] for t in trees},
                "trees": {k: v[1] for k, v in trees.items()}, "runs": []}
    lock = threading.Lock()
    print(f"run: {out_root} ({len(jobs)} calls)", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(run_one, job, tasks, args, out_root) for job in jobs]
        for fut in concurrent.futures.as_completed(futures):
            meta = fut.result()
            with lock:
                manifest["runs"].append(meta)
                with open(os.path.join(out_root, "manifest.json"), "w", encoding="utf-8") as fh:
                    json.dump(manifest, fh, indent=2)
            print(f"  {meta['tree']} {meta['agent']} #{meta['repeat']}: "
                  f"written={meta['written']} {meta['seconds']} s ${meta['cost_usd']}", flush=True)
    shutil.rmtree(trees_dir, ignore_errors=True)
    failed = [f"{m['tree']} {m['agent']} #{m['repeat']}" for m in manifest["runs"] if not m["written"]]
    cost = sum(m["cost_usd"] for m in manifest["runs"])
    print(f"done: {out_root} (${cost:.2f})")
    for f in failed:
        print(f"NO OUTPUT {f}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
