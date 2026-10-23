import json, glob, re, collections, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
rows = collections.defaultdict(collections.Counter); cost = collections.Counter(); fails = []
for f in sorted(glob.glob(os.path.join(HERE, "..", "runs", "*.json"))):
    d = json.load(open(f)); j = d["job"]; cost[j["model"]] += d.get("total_cost_usd") or 0
    r = d.get("result") or ""
    m = re.findall(r"^#{2,4}\s*Status:\s*(PASS|FAIL)\s*$", r, re.M)
    got = m[0] if len(m) == 1 else ("NONE" if not m else "MULTI")
    c = rows[(j["cell"], j["model"])]; c["n"] += 1; c[got] += 1; c["ok"] += got == j["expected"]
    if got != j["expected"]: fails.append((os.path.basename(f), j["expected"], got))
for k, v in sorted(cost.items()): print(f"cost {k}: ${v:.2f}")
for k in sorted(rows):
    c = rows[k]; print(*k, f"ok {c['ok']}/{c['n']}", {x: c[x] for x in c if x not in ("n", "ok")})
models = sorted({k[1] for k in rows})
for mo in models:
    defects = [k for k in rows if k[1] == mo and k[0] not in ("clean", "baseline_fail")]
    ctrls = [k for k in rows if k[1] == mo and k[0] in ("clean", "baseline_fail")]
    found = sum(rows[k]["FAIL"] for k in defects); nd = sum(rows[k]["n"] for k in defects)
    falsefail = sum(rows[k]["n"] - rows[k]["PASS"] for k in ctrls); nc = sum(rows[k]["n"] for k in ctrls)
    print(f"{mo}: defects found {found}/{nd}, false FAIL or no status on controls {falsefail}/{nc}")
if "-v" in sys.argv:
    for x in fails: print(x)
