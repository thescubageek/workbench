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

# Compound statements whose header line names the block a statement sits in.
COMPOUND = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try)

KEY_WIDTH = 64


def _head(src, node):
    """The first source line of `node`, stripped and bounded.

    The first line is enough because a compound statement leads with its header and a simple
    one usually fits on a line. Bounding it keeps a key readable in the waivers file, which a
    person has to review; two keys that collide after truncation are caught by the uniqueness
    pass below rather than by hoping.
    """
    seg = ast.get_source_segment(src, node)
    if not seg:
        return ''
    line = ' '.join(seg.splitlines()[0].split())
    return line if len(line) <= KEY_WIDTH else line[:KEY_WIDTH] + '...'


def _places(tree, src):
    """node id -> (scope, enclosing-block header, own statement header).

    This is what makes a mutant addressable by something other than a line number. A line
    number moves when anything above it changes, so every waiver keyed on one is unhooked by
    an unrelated edit — silently, because a waiver that matches nothing and a mutant that is
    genuinely caught look identical from the outside.
    """
    out = {id(tree): ('<module>', '', '')}

    def walk(node, scope, block, stmt):
        for child in ast.iter_child_nodes(node):
            c_scope, c_block, c_stmt = scope, block, stmt
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                c_scope, c_block, c_stmt = child.name, '', ''
            elif isinstance(child, ast.stmt):
                c_block = _head(src, node) if isinstance(node, COMPOUND) else block
                c_stmt = _head(src, child)
            out[id(child)] = (c_scope, c_block, c_stmt)
            walk(child, c_scope, c_block, c_stmt)

    walk(tree, '<module>', '', '')
    return out


def _key(places, node, op):
    scope, block, stmt = places.get(id(node), ('<module>', '', ''))
    return ' | '.join(x for x in (scope, block, stmt, op) if x)


def _disambiguate(out):
    """Append `#n` to keys that repeat, so a waiver can only ever address one mutant.

    Two identical statements in one block — `continue` in both arms of an if/else, the same
    `i += 1` twice — produce the same key, and a waiver matching two mutants would silently
    excuse one nobody argued about. The index is positional and so is the one fragile part
    left, but it orders only the collisions inside a single block rather than every line in
    the file.
    """
    seen = {}
    for e in out:
        seen[e[1]] = seen.get(e[1], 0) + 1
    run = {}
    fixed = []
    for label, key, src in out:
        if seen[key] > 1:
            run[key] = run.get(key, 0) + 1
            key = f'{key} #{run[key]}'
        fixed.append((label, key, src))
    return fixed


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
    """-> [(label, key, mutated_source)]. Deterministic and ordered.

    `label` is for reading — it leads with the line number, which is what a person wants when
    they go and look. `key` is for waivers, and carries no line number at all.
    """
    tree = ast.parse(src)
    places = _places(tree, src)
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
                    o = f'cmp {type(op).__name__}->{swap.__name__}'
                    out.append((f'L{node.lineno} {o}', _key(places, node, o), s))

        # --- boolean operators
        elif isinstance(node, ast.BoolOp):
            def m(n, _t):
                n.op = ast.Or() if isinstance(n.op, ast.And) else ast.And()
            s = _rebuild(tree, i, m)
            if s:
                out.append((f'L{node.lineno} bool and<->or',
                            _key(places, node, 'bool and<->or'), s))

        # --- integer constants
        elif isinstance(node, ast.Constant) and isinstance(node.value, int) \
                and not isinstance(node.value, bool):
            for delta, name in ((1, '+1'), (-1, '-1')):
                def m(n, _t, delta=delta):
                    n.value = n.value + delta
                s = _rebuild(tree, i, m)
                if s:
                    o = f'int {node.value}{name}'
                    out.append((f'L{node.lineno} {o}', _key(places, node, o), s))

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
                    o = f'regex {label}: {pat[:36]}'
                    out.append((f'L{node.lineno} {o}', _key(places, node, o), s))

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
                    o = f'del {type(stmt).__name__}'
                    if field != 'body':
                        o += f' ({field})'
                    out.append((f'L{getattr(stmt, "lineno", 0)} {o}',
                                _key(places, stmt, o), s))

    return _disambiguate(out)
