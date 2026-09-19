#!/usr/bin/env python3
"""Generated mutation operators for check-guards.

The curated mutation list in `test-guards` is author-written, and round 4 established
what that is worth: the same session wrote the tool, the corpus and the mutations, and
an independent party's 24 mutations found 20 survivors behind a green 12/12. A generator
has no blind spot correlated with the author's, because it is not reasoning about the
problem at all — it walks the syntax tree and changes one thing.

Two generators, because the generic one alone misses where this tool's decisions live:

  AST      comparison operators, boolean operators, integer constants, statement deletion
  REGEX    the compiled patterns — collapse alternations, drop anchors, widen quantifiers

Equivalent mutants are the known cost. They are waived in
`fixtures/mutation-waivers.json`, and a waiver carries an argument rather than an entry.
"""
import ast
import copy
import re

CMP_SWAP = {
    ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt,
    ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Is: ast.IsNot, ast.IsNot: ast.Is,
    ast.In: ast.NotIn, ast.NotIn: ast.In,
}

# Weakenings a maintainer plausibly writes, each destroying a distinct kind of precision.
REGEX_WEAKENINGS = [
    ('drop the leading anchor', lambda p: p[1:] if p.startswith('^') else None),
    ('drop the trailing anchor', lambda p: p[:-1] if p.endswith('$') else None),
    ('drop word boundaries', lambda p: p.replace(r'\b', '') if r'\b' in p else None),
    ('make + lazy-optional', lambda p: p.replace('+', '*', 1) if '+' in p else None),
    ('collapse the first alternation',
     lambda p: re.sub(r'\(\?:([^)|]+)\|[^)]*\)', r'(?:\1)', p, count=1)
     if re.search(r'\(\?:[^)|]+\|', p) else None),
    ('widen a bounded quantifier',
     lambda p: re.sub(r'\{\d+,?\d*\}', '*', p, count=1) if re.search(r'\{\d+,?\d*\}', p) else None),
    ('make a negated class permissive',
     lambda p: re.sub(r'\[\^[^\]]+\]', '.', p, count=1) if re.search(r'\[\^[^\]]+\]', p) else None),
]

# Nodes whose deletion is meaningless or fatal rather than informative.
SKIP_DELETE = (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef, ast.Return)


def _positions(tree):
    """Stable identity for a node: its position in a deterministic walk."""
    return {id(n): i for i, n in enumerate(ast.walk(tree))}


def _rebuild(tree, target_index, mutate):
    """Deep-copy the tree, apply `mutate` to the node at `target_index`, unparse."""
    clone = copy.deepcopy(tree)
    nodes = list(ast.walk(clone))
    if target_index >= len(nodes):
        return None
    node = nodes[target_index]
    if mutate(node, clone) is False:
        return None
    try:
        return ast.unparse(ast.fix_missing_locations(clone))
    except Exception:
        return None


def generate(src):
    """-> [(label, mutated_source)]. Deterministic and ordered."""
    tree = ast.parse(src)
    out = []

    main_guard_ids = {
        id(n.test) for n in ast.walk(tree)
        if isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
        and isinstance(n.test.left, ast.Name) and n.test.left.id == '__name__'
    }

    for i, node in enumerate(ast.walk(tree)):
        # The `if __name__ == '__main__'` guard is dispatch, not logic. Inverting it makes
        # the mutant call main() the moment it is imported — with the sweep's own argv —
        # which is counted as caught but prints the tool's error to the sweep's stderr.
        if id(node) in main_guard_ids:
            continue

        # --- comparison operators
        if isinstance(node, ast.Compare):
            for k, op in enumerate(node.ops):
                swap = CMP_SWAP.get(type(op))
                if not swap:
                    continue
                def m(n, _t, k=k, swap=swap):
                    n.ops[k] = swap()
                s = _rebuild(tree, i, m)
                if s:
                    out.append((f'L{node.lineno} cmp {type(op).__name__}->{swap.__name__}', s))

        # --- boolean operators
        elif isinstance(node, ast.BoolOp):
            def m(n, _t):
                n.op = ast.Or() if isinstance(n.op, ast.And) else ast.And()
            s = _rebuild(tree, i, m)
            if s:
                out.append((f'L{node.lineno} bool and<->or', s))

        # --- integer constants
        elif isinstance(node, ast.Constant) and isinstance(node.value, int) \
                and not isinstance(node.value, bool):
            for delta, name in ((1, '+1'), (-1, '-1')):
                def m(n, _t, delta=delta):
                    n.value = n.value + delta
                s = _rebuild(tree, i, m)
                if s:
                    out.append((f'L{node.lineno} int {node.value}{name}', s))

        # --- regex literals
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            pat = node.value
            if not re.search(r'[\\\[\](){}|+*?^$]', pat) or len(pat) < 4:
                continue
            try:
                re.compile(pat)
            except re.error:
                continue
            for label, fn in REGEX_WEAKENINGS:
                new = fn(pat)
                if not new or new == pat:
                    continue
                try:
                    re.compile(new)
                except re.error:
                    continue
                def m(n, _t, new=new):
                    n.value = new
                s = _rebuild(tree, i, m)
                if s:
                    out.append((f'L{node.lineno} regex {label}: {pat[:36]}', s))

    # --- statement deletion, done on the parent body so indices stay meaningful
    for i, node in enumerate(ast.walk(tree)):
        for field in ('body', 'orelse', 'finalbody'):
            body = getattr(node, field, None)
            if not isinstance(body, list) or len(body) < 2:
                continue
            for k, stmt in enumerate(body):
                if isinstance(stmt, SKIP_DELETE):
                    continue
                def m(n, _t, field=field, k=k):
                    getattr(n, field).pop(k)
                s = _rebuild(tree, i, m)
                if s:
                    kind = type(stmt).__name__
                    out.append((f'L{getattr(stmt, "lineno", 0)} del {kind}', s))

    return out
