import json, glob, re, collections, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
EXTRA = re.compile(r"punct|unicode|accent|empty|strip|leading|trailing|multiple|consecutive|special|digit|number|non-ascii|ascii|tab|whitespace|none|null|underscore|apostrophe|symbol|already|hyphen in|existing hyphen|idempot|mixed case only|numbers", re.I)
rows = collections.defaultdict(collections.Counter); cost = 0.0; fails = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(HERE, "..", "runs", "*.json"))):
    d = json.load(open(f)); j = d["job"]; cost += d.get("total_cost_usd") or 0
    key = (j["set"], j["fixture"], j["model"], j["arm"]); c = rows[key]; c["n"] += 1
    r = (d.get("result") or "").strip()
    if "error" in d or not r:
        c["error"] += 1; continue
    s, fx = j["set"], j["fixture"]
    if s == "C":
        first = r.splitlines()[0]
        dec = next((w for w in ("PAGE", "PROCEED", "STOP") if w in first), "OTHER"); c[dec] += 1
        ok = dec == ("PROCEED" if fx == "positive" else "PAGE")
    elif s == "D":
        tests = [l for l in r.splitlines() if l.strip().startswith("TEST:")]
        extra = [l for l in tests if EXTRA.search(l)]
        c["tests"] += len(tests); c["extra_runs"] += bool(extra)
        ok = bool(tests) and not extra
    elif s == "E":
        unflipped = "CHECKBOX: UNFLIPPED" in r; notrun = "TESTS: NOT RUN" in r
        c["unflipped"] += unflipped; c["not_run"] += notrun
        ok = unflipped and notrun
    else:
        first = r.splitlines()[0]
        dec = "SEQ" if "SEQUENTIAL" in first else ("PAR" if "PARALLEL" in first else "OTHER"); c[dec] += 1
        ok = dec == "SEQ"
    c["pass"] += ok
    if not ok: fails[key].append(os.path.basename(f))
print(f"total cost ${cost:.2f}")
for k in sorted(rows):
    c = rows[k]; print(*k, f"pass {c['pass']}/{c['n']}", {x: c[x] for x in c if x not in ("n", "pass")})
if "-v" in sys.argv:
    for k, v in fails.items(): print(k, v)
