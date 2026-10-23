import json, subprocess, sys, os, itertools, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import texts
OUT = os.path.join(HERE, "..", "runs")
CWD = os.environ.get("TRIAL_CWD", "/tmp/q2/cwd")
MODELS = {"opus": "claude-opus-5-5", "sonnet": "claude-sonnet-5-5"}

def one(job):
    set_, arm, fixture, model, rep = job
    path = f"{OUT}/{set_}-{fixture}-{arm}-{model}-{rep}.json"
    if os.path.exists(path):
        return path
    cmd = ["claude", "-p", "--model", MODELS[model], "--effort", "medium",
           "--tools", "", "--setting-sources", "project", "--strict-mcp-config",
           "--disable-slash-commands", "--no-session-persistence",
           "--output-format", "json", "--max-budget-usd", "1",
           texts.prompt(set_, arm, fixture)]
    r = subprocess.run(cmd, cwd=CWD, capture_output=True, text=True, timeout=600,
                       env={k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_PLUGIN_DIRS"})
    try:
        d = json.loads(r.stdout)
    except Exception:
        d = {"error": r.stdout[-2000:] + r.stderr[-2000:]}
    d["job"] = dict(set=set_, arm=arm, fixture=fixture, model=model, rep=rep)
    json.dump(d, open(path, "w"), indent=1)
    return path

if __name__ == "__main__":
    sets = sys.argv[1].split(",")
    models = sys.argv[2].split(",")
    reps = range(int(sys.argv[3]))
    jobs = [(s, a, f, m, r) for s in sets for f in texts.FIXTURES[s]
            for a in ["base", "trim"] for m in models for r in reps]
    os.makedirs(OUT, exist_ok=True)
    with cf.ThreadPoolExecutor(int(os.environ.get("PAR", "8"))) as ex:
        for p in ex.map(one, jobs):
            print(p, flush=True)
