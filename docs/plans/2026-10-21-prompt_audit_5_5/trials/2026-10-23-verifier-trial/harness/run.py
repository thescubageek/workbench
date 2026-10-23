import json, subprocess, sys, os, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fixtures
OUT = os.path.join(HERE, "..", "runs")
PLUGIN = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "..", "plugin"))
WORK = "/tmp/vtrial"

def one(job):
    cell, model, rep = job
    path = f"{OUT}/{cell}-{model}-{rep}.json"
    if os.path.exists(path):
        return path
    repo = f"{WORK}/{cell}-{model}-{rep}"
    summary = fixtures.build(cell, repo)
    cmd = ["claude", "-p", "--plugin-dir", PLUGIN, "--agent", "wb:task-verifier", "--model", model,
           "--effort", "high", "--allowedTools", "Bash,Read,Grep,Glob", "--setting-sources", "project",
           "--strict-mcp-config", "--no-session-persistence", "--output-format", "json",
           "--max-budget-usd", "1.50", fixtures.prompt(summary)]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_PLUGIN_DIRS"}
    r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=1200, env=env)
    try:
        d = json.loads(r.stdout)
    except Exception:
        d = {"error": r.stdout[-2000:] + r.stderr[-2000:]}
    d["job"] = dict(cell=cell, model=model, rep=rep, expected=fixtures.CELLS[cell])
    json.dump(d, open(path, "w"), indent=1)
    return path

if __name__ == "__main__":
    cells = sys.argv[1].split(",") if sys.argv[1] != "all" else list(fixtures.CELLS)
    models = sys.argv[2].split(","); reps = range(int(sys.argv[3]))
    os.makedirs(OUT, exist_ok=True)
    jobs = [(c, m, r) for c in cells for m in models for r in reps]
    with cf.ThreadPoolExecutor(int(os.environ.get("PAR", "4"))) as ex:
        for p in ex.map(one, jobs):
            print(p, flush=True)
