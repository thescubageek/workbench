#!/usr/bin/env python3
"""Link-line, single-authority, and no-ASD-content checker.

Maintainer-only. Three checks over a plugin tree:

1. Every output template, and each inline output step, links to
   plugin/docs/reference/technical-english.md. A template has the link in its first lines.
2. No file other than the reference doc restates the rules. The card in
   plugin/hooks/wb-prime.sh is the one exception.
3. No tracked file is a PDF or a dictionary copy.

Usage: link_check.py [--root DIR] [--json]

In a git work tree, "tracked" means `git ls-files`. Elsewhere (the planted cases), it means
every file under DIR, plus the paths listed in DIR/.tracked.
Exit 0 when every check holds, 1 when one fails, 2 on a usage error.
"""

import argparse
import json
import os
import re
import subprocess
import sys

REFERENCE = "plugin/docs/reference/technical-english.md"
CARD = "plugin/hooks/wb-prime.sh"
TEMPLATE_RE = re.compile(r"^plugin/skills/[^/]+/(templates/[^/]+\.md|templates\.md|[^/]+-template\.md)$")
INLINE_STEPS = [
    "plugin/skills/create_project/SKILL.md",
    "plugin/skills/create_research/SKILL.md",
    "plugin/skills/create_product_research/SKILL.md",
    "plugin/skills/resolve_questions/SKILL.md",
]
TEMPLATE_HEAD_LINES = 10
LINK_RE = re.compile(r"\]\(([^)\s]*docs/reference/technical-english\.md)\)")
RULE_PHRASES = [
    "Write at most 20 words in an instruction sentence",
    "Write at most 25 words in a descriptive sentence",
    "Count each item in backticks as one word",
    "Do not use semicolons in prose",
    "never use an ID alone",
]
PHRASE_EXEMPT_PREFIXES = ("evals/", "docs/plans/")
DICTIONARY_ROW = re.compile(r"^[^\t\n]+\t[^\t\n]*\t(approved|not approved|unapproved|yes|no)\t",
                            re.I | re.M)
DICTIONARY_MIN_ROWS = 20


def tracked_files(root):
    try:
        out = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True, text=True,
                             check=True).stdout
        top = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
        if os.path.realpath(top) == os.path.realpath(root):
            return [l for l in out.split("\n") if l]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    files = []
    for dirpath, _, names in os.walk(root):
        for name in names:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            if rel != ".tracked":
                files.append(rel)
    extra = os.path.join(root, ".tracked")
    if os.path.isfile(extra):
        files += [l.strip() for l in open(extra, encoding="utf-8") if l.strip()]
    return sorted(files)


def read(root, rel):
    try:
        return open(os.path.join(root, rel), encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return None


def links_to_reference(root, rel, text):
    here = os.path.dirname(os.path.join(root, rel))
    target = os.path.realpath(os.path.join(root, REFERENCE))
    for m in LINK_RE.finditer(text):
        if os.path.realpath(os.path.join(here, m.group(1))) == target:
            return True
    return False


def check_links(root, files):
    failures = []
    templates = [f for f in files if TEMPLATE_RE.match(f)]
    for rel in templates:
        text = read(root, rel) or ""
        head = "\n".join(text.split("\n")[:TEMPLATE_HEAD_LINES])
        if not links_to_reference(root, rel, head):
            failures.append(f"{rel}: no link line to technical-english.md in the first "
                            f"{TEMPLATE_HEAD_LINES} lines")
    steps = [f for f in INLINE_STEPS if f in files]
    for rel in steps:
        if not links_to_reference(root, rel, read(root, rel) or ""):
            failures.append(f"{rel}: the inline output step has no link to technical-english.md")
    return failures, len(templates), len(steps)


def check_authority(root, files):
    failures = []
    reference = read(root, REFERENCE)
    if reference is None:
        return [f"{REFERENCE}: missing"]
    for phrase in RULE_PHRASES:
        if phrase.lower() not in reference.lower():
            failures.append(f"{REFERENCE}: rule phrase {phrase!r} is gone, update RULE_PHRASES")
    for rel in files:
        if rel in (REFERENCE, CARD) or rel.startswith(PHRASE_EXEMPT_PREFIXES):
            continue
        text = read(root, rel)
        if text is None:
            continue
        for phrase in RULE_PHRASES:
            if phrase.lower() in text.lower():
                failures.append(f"{rel}: restates the rule {phrase!r}")
    return failures


def check_no_asd_content(root, files):
    failures = []
    for rel in files:
        low = rel.lower()
        if low.endswith(".pdf"):
            failures.append(f"{rel}: a tracked PDF")
            continue
        if low.endswith("wbte-dictionary.tsv"):
            failures.append(f"{rel}: a tracked dictionary copy")
            continue
        text = read(root, rel)
        if text and len(DICTIONARY_ROW.findall(text)) >= DICTIONARY_MIN_ROWS:
            failures.append(f"{rel}: looks like dictionary text")
    return failures


def main(argv):
    ap = argparse.ArgumentParser(description="link-line and single-authority checker")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    help="tree to check (default: this repository)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.root):
        print(f"link_check: no such directory: {args.root}", file=sys.stderr)
        return 2

    files = tracked_files(args.root)
    link_failures, n_templates, n_steps = check_links(args.root, files)
    failures = link_failures + check_authority(args.root, files) + check_no_asd_content(args.root, files)

    if args.json:
        print(json.dumps({"templates": n_templates, "inline_steps": n_steps,
                          "failures": failures}, indent=2, ensure_ascii=False))
    else:
        print(f"{n_templates} templates, {n_steps} inline steps checked")
        for f in failures:
            print(f"FAIL {f}")
        print("FAIL" if failures else "PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
