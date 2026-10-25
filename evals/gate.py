#!/usr/bin/env python3
"""Prose gate: decide whether an "after" tree scores lower than a "before" tree, at a measured
false-positive rate.

Maintainer-only. It reads run directories from run.py (the research stage) or agent_run.py (one
agent at a time), scores each run mechanically, and decides one verdict for each unit. A unit is
one agent, or `stage:research`.

The rule, for a unit with n after runs and at least 2n before runs:
- The score of a run is a count: expected facts cited at their file:line (`facts`), expected
  files named (`files`), or planted claims judged correctly (`claims`). <fixture>/agents/tasks.json
  names each agent's kind.
- The null distribution is the drop, mean(X) - mean(Y), over splits of the before runs into
  two disjoint groups X and Y of n runs each. Both groups ran the same text, so each drop is
  run-to-run variance.
- The threshold is the smallest drop that at most --alpha of the null splits exceed. The
  measured false-positive rate (FPR) is the share of null splits that exceed it.
- LOSS when mean(before) - mean(after) exceeds the threshold. Otherwise PASS. INCONCLUSIVE when
  there are fewer than 2n before runs, fewer than 2 after runs, or too few null splits to
  resolve --alpha.

The null splits compare n with n. The gate compares n after runs with all the before runs, which
varies less, so the real false-positive rate is at most the measured one.

Usage:
  gate.py RUN_DIR [RUN_DIR ...] [--alpha A]   score the runs, write RUN_DIR/gate.md and gate.json
  gate.py --scores FILE [--alpha A]           decide from {"unit": {"before": [...], "after": [...]}}

Exit 0 when every unit passes, 1 when a unit shows a loss, 3 when a unit is inconclusive and
none shows a loss, 2 on a usage error.
"""

import argparse
import itertools
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from judge import load_facts  # noqa: E402

MAX_SPLITS = 5000
STATUS_RE = re.compile(r"\b(PASS|FAIL|STALE|MISSING|UNCERTAIN)\b")
WRONG = {"FAIL", "STALE", "MISSING"}
REF_RE = re.compile(r"(?:([\w./-]+\.[A-Za-z]{1,5})|(?<![\w:/])):(\d+)(?:-\d+)?")
FILE_RE = re.compile(r"[\w./-]+\.[A-Za-z]{1,5}\b")


def cited_refs(text):
    """(file name, line) pairs. A bare `:N` belongs to the last file named before it, because
    an analyzer often names a file once in a heading and then cites its lines alone."""
    refs, last = set(), None
    for m in re.finditer(f"{REF_RE.pattern}|{FILE_RE.pattern}", text):
        if m.group(2) is None:
            last = m.group(0).split("/")[-1]
            continue
        if m.group(1):
            last = m.group(1).split("/")[-1]
        if last:
            refs.add((last, m.group(2)))
    return refs


def score_facts(text, facts):
    refs = cited_refs(text)
    return {f["id"] for f in facts
            if (f["ref"].rsplit(":", 1)[0].split("/")[-1], f["ref"].rsplit(":", 1)[1]) in refs}


def score_files(text, files):
    """Expected files named in text, by file name: a locator often lists a name under its directory."""
    return {f for f in files
            if re.search(r"(?<![\w.])" + re.escape(f.rsplit("/", 1)[-1]) + r"\b", text)}


def claim_status(text, cid):
    """The status on the claim's table row, else on the first other line that names it."""
    lines = text.splitlines()
    row = re.compile(rf"^\|\s*\**`?{cid}`?\**\s*\|")
    for line in [l for l in lines if row.match(l)] + [l for l in lines if re.search(rf"\b{cid}\b", l)]:
        m = STATUS_RE.search(line)
        if m:
            return m.group(1)
    return None


def score_claims(text, claims):
    correct = set()
    for cid, want in claims.items():
        got = claim_status(text, cid)
        if got and got != "UNCERTAIN" and (got in WRONG) == (want in WRONG):
            correct.add(cid)
    return correct


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def collect(run_dir):
    """Return {unit: {tree: [set of scored items, one per run]}} for one run directory."""
    manifest = json.load(open(os.path.join(run_dir, "manifest.json"), encoding="utf-8"))
    fixture = os.path.join(REPO, manifest.get("fixture") or "evals/fixture")
    facts = load_facts(os.path.join(fixture, "expected.json"))
    units = {}
    if manifest.get("kind") == "agents":
        tasks = json.load(open(os.path.join(fixture, "agents", "tasks.json"),
                               encoding="utf-8"))["agents"]
        for m in manifest["runs"]:
            if not m.get("written"):
                continue
            task = tasks[m["agent"]]
            text = read(os.path.join(run_dir, m["tree"], m["agent"], str(m["repeat"]), "output.md"))
            if task["score"] == "claims":
                items = score_claims(text, task["claims"])
            elif task["score"] == "files":
                items = score_files(text, task["files"])
            else:
                items = score_facts(text, facts)
            units.setdefault(m["agent"], {}).setdefault(m["tree"], []).append(items)
        return units
    for run in manifest["runs"]:
        written = any(s["stage"] == "research" and s.get("written") for s in run["stages"])
        path = os.path.join(run_dir, run["tree"], str(run["repeat"]), "plan", "research.md")
        if written and os.path.isfile(path):
            units.setdefault("stage:research", {}).setdefault(run["tree"], []).append(
                score_facts(read(path), facts))
    return units


def mean(xs):
    return sum(xs) / len(xs)


def null_drops(before, n):
    """Drops mean(X) - mean(Y) over disjoint splits of before into two groups of n."""
    idx = range(len(before))
    pairs = []
    if len(before) <= 12:
        for x in itertools.combinations(idx, n):
            rest = [i for i in idx if i not in x]
            pairs += [(x, y) for y in itertools.combinations(rest, n)]
    if not pairs or len(pairs) > MAX_SPLITS:
        rng = random.Random(0)
        pairs = []
        for _ in range(MAX_SPLITS):
            pick = rng.sample(list(idx), 2 * n)
            pairs.append((pick[:n], pick[n:]))
    return [mean([before[i] for i in x]) - mean([before[i] for i in y]) for x, y in pairs]


def decide(before, after, alpha):
    n = len(after)
    out = {"before": before, "after": after, "n": n,
           "before_mean": round(mean(before), 2) if before else None,
           "after_mean": round(mean(after), 2) if after else None}
    if n < 2 or len(before) < 2 * n:
        out.update(verdict="INCONCLUSIVE",
                   reason=f"needs at least 2 after runs and {2 * n} before runs")
        return out
    drops = sorted(null_drops(before, n))
    if len(drops) * alpha < 1:
        out.update(verdict="INCONCLUSIVE",
                   reason=f"{len(drops)} null splits cannot resolve an alpha of {alpha}")
        return out
    threshold = next(d for d in drops if sum(1 for e in drops if e > d) <= alpha * len(drops))
    drop = mean(before) - mean(after)
    out.update(drop=round(drop, 2), threshold=round(threshold, 2),
               fpr=round(sum(1 for e in drops if e > threshold) / len(drops), 3),
               splits=len(drops), verdict="LOSS" if drop > threshold + 1e-9 else "PASS")
    return out


def stable_losses(before_items, after_items, share=0.8):
    """Items that at least `share` of before runs have and no after run has. Information only."""
    if not before_items or not after_items:
        return []
    every = set().union(*before_items)
    return sorted(i for i in every
                  if sum(i in s for s in before_items) >= share * len(before_items)
                  and not any(i in s for s in after_items))


def render(results, alpha):
    lines = ["# Prose gate", "",
             f"Rule: LOSS when the mean drop exceeds the threshold that at most {alpha:.0%} of "
             "before-versus-before splits exceed.", "",
             "| Unit | Before (mean) | After (mean) | Drop | Threshold | Measured FPR | Verdict |",
             "| ---- | ------------- | ------------ | ---- | --------- | ------------ | ------- |"]
    for unit, r in results.items():
        lines.append(f"| {unit} | {r['before']} ({r['before_mean']}) | {r['after']} ({r['after_mean']}) | "
                     f"{r.get('drop', '-')} | {r.get('threshold', '-')} | {r.get('fpr', '-')} | "
                     f"{r['verdict']} |")
    notes = [f"- {u}: {r['reason']}" for u, r in results.items() if r.get("reason")]
    notes += [f"- {u}: before cites, after never cites: {', '.join(r['stable_losses'])}"
              for u, r in results.items() if r.get("stable_losses")]
    if notes:
        lines += ["", "## Notes", ""] + notes
    return "\n".join(lines) + "\n"


def main(argv):
    ap = argparse.ArgumentParser(description="wb prose gate")
    ap.add_argument("runs", nargs="*", help="run directories from run.py or agent_run.py")
    ap.add_argument("--scores", help="a JSON file of scores, instead of run directories")
    ap.add_argument("--alpha", type=float, default=0.05, help="false-positive budget (default 0.05)")
    args = ap.parse_args(argv)
    if bool(args.scores) == bool(args.runs):
        ap.print_usage(sys.stderr)
        return 2
    results = {}
    if args.scores:
        data = json.load(open(args.scores, encoding="utf-8"))
        for unit, arms in data.items():
            results[unit] = decide(arms.get("before", []), arms.get("after", []), args.alpha)
    else:
        merged = {}
        for run_dir in args.runs:
            if not os.path.isfile(os.path.join(run_dir, "manifest.json")):
                print(f"gate: no manifest.json in {run_dir}", file=sys.stderr)
                return 2
            for unit, trees in collect(run_dir).items():
                for tree, items in trees.items():
                    merged.setdefault(unit, {}).setdefault(tree, []).extend(items)
        for unit, trees in merged.items():
            b, a = trees.get("before", []), trees.get("after", [])
            results[unit] = decide([len(s) for s in b], [len(s) for s in a], args.alpha)
            results[unit]["stable_losses"] = stable_losses(b, a)
        with open(os.path.join(args.runs[0], "gate.json"), "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
        with open(os.path.join(args.runs[0], "gate.md"), "w", encoding="utf-8") as fh:
            fh.write(render(results, args.alpha))
    print(render(results, args.alpha), end="")
    verdicts = {r["verdict"] for r in results.values()}
    if "LOSS" in verdicts:
        return 1
    return 3 if "INCONCLUSIVE" in verdicts or not results else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
