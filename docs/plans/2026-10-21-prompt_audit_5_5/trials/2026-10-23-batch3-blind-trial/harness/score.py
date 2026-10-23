import json, glob, collections, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import texts
rows = collections.defaultdict(collections.Counter); cost = 0.0; fails = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(HERE, "..", "runs", "*.json"))):
    d = json.load(open(f)); j = d["job"]; cost += d.get("total_cost_usd") or 0
    key = (j["set"], j["fixture"], j["model"], j["arm"]); c = rows[key]; c["n"] += 1
    r = (d.get("result") or "").strip()
    if "error" in d or not r:
        c["error"] += 1; continue
    first = r.splitlines()[0]
    dec = next((w for w in texts.OPTIONS[j["set"]] if f"DECISION: {w}" in first), "OTHER")
    c[dec] += 1; ok = dec == texts.PASS[j["set"]]; c["pass"] += ok
    if not ok: fails[key].append(os.path.basename(f))
print(f"total cost ${cost:.2f}")
for k in sorted(rows):
    c = rows[k]; print(*k, f"pass {c['pass']}/{c['n']}", {x: c[x] for x in c if x not in ("n", "pass")})
if "-v" in sys.argv:
    for k, v in fails.items(): print(k, v)
