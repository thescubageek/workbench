#!/usr/bin/env python3
"""Second score: plant single-line breaks; count how many the corpus catches."""
import os, sys, shutil, tempfile, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run as R

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = R.ROOT

MUT = {
 'A': (os.path.join(ROOT, 'plugin/scripts/check-guards'), [
   ("stop scanning extensionless scripts", "    *.sh|*/scripts/*)", "    *.sh)"),
   ("delete the 0-file refusal",           'if [ "$scanned" -eq 0 ]; then', 'if false; then'),
   ("delete the find-stderr refusal",      'if [ -s "$FIND_ERR" ]; then', 'if false; then'),
   ("delete the missing-target check",     '  if [ ! -e "$t" ]; then', '  if false; then'),
   ("disable the capture detector",        'if [[ "$code" =~ (\\$\\(|`) ]] &&', 'if false && '),
   ("disable the --include detector",      "      *'--include='[!\\'\\\"]*)", "      *'__NEVER_MATCH__'*)"),
   ("disable the glob detector",           'prev_glob_line="$(echo "$text" | sed', 'prev_glob_line=""; : "$(echo "$text" | sed'),
   ("remove the EOF drain",                'if [ -n "$pend_grep_line" ]; then\n    report', 'if false; then\n    report'),
 ]),
 'C': (os.path.join(HERE, 'candidate_c.py'), [
   ("disable the capture detector",   "if COUNTING.search(inner):", "if False and COUNTING.search(inner):"),
   ("disable the --include detector", "for m in re.finditer(r'--include=(\\S+)', line):", "for m in re.finditer(r'__NEVER__', line):"),
   ("disable the glob detector",      "if m and '*' in m.group(1)", "if False and m and '*' in m.group(1)"),
   ("break the comment stripper",     "return ''.join(out)", "return line.split('#')[0]"),
   ("ignore sh/shell fences",         "in ([ 'bash' ], [ 'sh' ], [ 'shell' ])", "in ([ 'bash' ],)"),
   ("break the fence closer",         "len(m.group('f')) >= ln and not m.group('info')", "False"),
   ("treat every capture as guarded", "if not GUARD.search(inner)", "if False and not GUARD.search(inner)"),
   ("drop the glob pending flush",    "    if pend is not None:\n        found.append((pend[0], 'glob'))", "    if False:\n        found.append((pend[0], 'glob'))"),
 ]),
}

def run():
    for name, (path, muts) in MUT.items():
        orig = open(path).read()
        base = R.score(name)
        base_ok = base['tp'] + base['tn']
        print(f"--- candidate {name} (baseline {base_ok}/{len(R.CORPUS)}) ---")
        caught = 0
        for label, old, new in muts:
            if old not in orig:
                print(f"  ??  {label}: anchor not found — mutation skipped"); continue
            tmp = path + '.mut'
            shutil.copy(path, path + '.bak')
            open(path, 'w').write(orig.replace(old, new, 1))
            if path.endswith('check-guards'): os.chmod(path, 0o755)
            try:
                s = R.score(name)
                ok = s['tp'] + s['tn']
            finally:
                shutil.move(path + '.bak', path)
                if path.endswith('check-guards'): os.chmod(path, 0o755)
            if ok < base_ok:
                caught += 1; print(f"  ✓   {label}: caught ({ok} vs {base_ok})")
            else:
                print(f"  ✗   {label}: SURVIVED ({ok} vs {base_ok})")
        print(f"  mutation survivability: {caught}/{len(muts)} caught = {100*caught//len(muts)}%\n")

if __name__ == '__main__':
    run()
