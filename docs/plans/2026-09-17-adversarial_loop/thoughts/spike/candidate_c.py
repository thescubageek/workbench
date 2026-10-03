#!/usr/bin/env python3
"""Candidate C: real CommonMark fence parse + substitution-span analysis.
Throwaway spike implementation. Exit 1 if findings, 0 if clean, 2 if the scan could not run."""
import sys, os, re

FENCE = re.compile(r'^(?P<ind>[ ]{0,3})(?P<f>`{3,}|~{3,})[ \t]*(?P<info>\S*)')
COUNTING = re.compile(r'\bgrep\b[^|;)`]*?\s(?:-[A-Za-z]*c|--count)\b')
GUARD = re.compile(r'\|\|\s*(?:true|:|echo)\b')

def md_shell_lines(text):
    """Yield (lineno, line) for lines inside bash/sh/shell fences. Real CommonMark rules:
    the closer must be the same char, at least as long, and carry no info string."""
    out, inb, ch, ln = [], False, '', 0
    for i, line in enumerate(text.splitlines(), 1):
        m = FENCE.match(line)
        if not inb:
            if m and m.group('info').lower().split()[0:1] in ([ 'bash' ], [ 'sh' ], [ 'shell' ]):
                inb, ch, ln = True, m.group('f')[0], len(m.group('f'))
            continue
        if m and m.group('f')[0] == ch and len(m.group('f')) >= ln and not m.group('info'):
            inb = False
            continue
        out.append((i, line))
    return out

def strip_comment(line):
    """Remove a trailing comment, respecting quotes. '#' inside a string is not a comment."""
    out, q = [], None
    for i, chx in enumerate(line):
        if q:
            out.append(chx)
            if chx == q: q = None
        elif chx in '"\'':
            q = chx; out.append(chx)
        elif chx == '#' and (i == 0 or line[i-1].isspace()):
            break
        else:
            out.append(chx)
    return ''.join(out)

def spans(line):
    """Every $( ... ) and ` ... ` substitution span as (start, end_of_inner, close_idx)."""
    res, i = [], 0
    while i < len(line):
        if line.startswith('$(', i):
            depth, j = 1, i + 2
            while j < len(line) and depth:
                if line.startswith('$(', j): depth += 1; j += 2; continue
                if line[j] == ')': depth -= 1
                j += 1
            res.append((i + 2, j - 1)); i = j
        elif line[i] == '`':
            j = line.find('`', i + 1)
            if j == -1: break
            res.append((i + 1, j)); i = j + 1
        else:
            i += 1
    return res

def analyse(lines):
    found, pend = [], None
    for no, raw in lines:
        line = strip_comment(raw)
        if not line.strip():
            pass
        # shape 1 -- a counting grep inside a substitution whose status is discarded
        for a, b in spans(line):
            inner = line[a:b]
            if COUNTING.search(inner):
                after = line[b:]
                if not GUARD.search(inner) and not re.match(r'^[`)]?\s*\|\|\s*(true|:|echo)\b', after):
                    found.append((no, 'capture'))
                    break
        # shape 2 -- unquoted --include glob
        for m in re.finditer(r'--include=(\S+)', line):
            if not m.group(1).startswith(('"', "'")):
                found.append((no, 'include')); break
        # shape 3 -- for over a glob, with a 4-line guard window
        if pend is not None:
            if re.search(r'(?:\[\[?|test)\s+!?\s*-[efsr]\s', line) or re.search(r'(?:^|;|&&|\|\|)\s*continue\b', line):
                pend = None
            else:
                pend = (pend[0], pend[1] + 1)
                if pend[1] >= 4:
                    found.append((pend[0], 'glob')); pend = None
        m = re.match(r'^\s*for\s+[A-Za-z_]\w*\s+in\s+(.*?)(?:;\s*do)?\s*$', line)
        if m and '*' in m.group(1) and not re.search(r'\[[@*]\]', m.group(1)):
            pend = (no, 0)
    if pend is not None:
        found.append((pend[0], 'glob'))
    return found

def main(targets):
    for t in targets:
        if not os.path.exists(t):
            print(f"candidate-c: no such path: {t}", file=sys.stderr); return 2
    hits, scanned = [], 0
    for t in targets:
        walk = [t] if os.path.isfile(t) else [os.path.join(r, f) for r, _, fs in os.walk(t) for f in sorted(fs)]
        for f in walk:
            if os.path.basename(f) in ('candidate_c.py',):
                continue
            try: text = open(f, errors='replace').read()
            except OSError: continue
            if f.endswith('.md'):
                lines = md_shell_lines(text)
            elif f.endswith('.sh') or (os.sep + 'scripts' + os.sep) in f:
                lines = list(enumerate(text.splitlines(), 1))
            else:
                continue
            scanned += 1
            for no, shape in analyse(lines):
                hits.append(f"{f}:{no} {shape}")
    if scanned == 0:
        print(f"candidate-c: scanned 0 files under {targets}", file=sys.stderr); return 2
    for h in hits: print(h)
    return 1 if hits else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:] or ['plugin']))
