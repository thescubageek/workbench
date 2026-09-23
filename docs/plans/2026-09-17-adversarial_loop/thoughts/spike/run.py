#!/usr/bin/env python3
"""Spike driver: score candidates A/B/C against corpus.json, then mutation-test each."""
import json, os, subprocess, sys, tempfile, shutil, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
CORPUS = json.load(open(os.path.join(os.path.dirname(__file__), 'corpus.json')))
HERE = os.path.dirname(os.path.abspath(__file__))

def materialise(case, d):
    p = os.path.join(d, case['path'])
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(case['content'].encode().decode('unicode_escape')
                       if '\\n' in case['content'] and '\n' not in case['content'] else case['content'])
    if p.endswith('.sh'): os.chmod(p, 0o755)
    return p

def run_a(d, impl):  return subprocess.run([impl, d], capture_output=True, text=True)
def run_c(d, impl):  return subprocess.run([sys.executable, impl, d], capture_output=True, text=True)

def run_b(d, _impl):
    """shellcheck -o all over shell files + bash fences extracted from markdown."""
    sys.path.insert(0, HERE)
    from candidate_c import md_shell_lines
    files = []
    for r, _, fs in os.walk(d):
        for f in sorted(fs):
            p = os.path.join(r, f)
            if f.endswith('.md'):
                lines = md_shell_lines(open(p, errors='replace').read())
                if lines:
                    t = p + '.extracted.sh'
                    open(t, 'w').write('#!/usr/bin/env bash\n' + '\n'.join(l for _, l in lines) + '\n')
                    files.append(t)
            elif f.endswith('.sh') or (os.sep + 'scripts' + os.sep) in p:
                files.append(p)
    if not files:
        return subprocess.CompletedProcess([], 0, '', '')
    return subprocess.run(['shellcheck', '-o', 'all', '-f', 'gcc', *files], capture_output=True, text=True)

CANDIDATES = {
    'A': (os.path.join(ROOT, 'plugin/scripts/check-guards'), run_a),
    'B': ('shellcheck', run_b),
    'C': (os.path.join(HERE, 'candidate_c.py'), run_c),
}

def score(name, impl_override=None):
    impl, runner = CANDIDATES[name]
    if impl_override: impl = impl_override
    tp = fp = fn = tn = 0
    misses, falses = [], []
    for case in CORPUS:
        d = tempfile.mkdtemp()
        try:
            materialise(case, d)
            r = runner(d, impl)
            fired = r.returncode == 1 and bool(r.stdout.strip())
            if case['expect'] == 1:
                if fired: tp += 1
                else: fn += 1; misses.append(case['id'])
            else:
                if fired: fp += 1; falses.append(case['id'])
                else: tn += 1
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return dict(tp=tp, fn=fn, fp=fp, tn=tn, misses=misses, falses=falses)

if __name__ == '__main__':
    print(f"corpus: {len(CORPUS)} cases "
          f"({sum(1 for c in CORPUS if c['expect']==1)} must-fire, "
          f"{sum(1 for c in CORPUS if c['expect']==0)} must-not-fire)\n")
    results = {}
    for name in ('A', 'B', 'C'):
        s = score(name)
        results[name] = s
        total = len(CORPUS)
        correct = s['tp'] + s['tn']
        print(f"--- candidate {name} ---")
        print(f"  caught {s['tp']}/{s['tp']+s['fn']} must-fire, "
              f"{s['fp']} false positives on {s['fp']+s['tn']} must-not-fire "
              f"-> {correct}/{total} = {100*correct//total}%")
        if s['misses']: print(f"  MISSED: {', '.join(s['misses'])}")
        if s['falses']: print(f"  FALSE+: {', '.join(s['falses'])}")
        print()
    json.dump(results, open(os.path.join(HERE, 'corpus-results.json'), 'w'), indent=1)
