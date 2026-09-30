#!/usr/bin/env python3
"""WBTE metric checker for generated documents and chat output.

Maintainer-only. The rules it measures live in
plugin/docs/reference/technical-english.md.

Usage: wbte_check.py [--json] [--chat] [--long-share N] [--max-cluster N]
                     [--dictionary PATH] FILE...

A file ending in .txt is chat output. Every other file is a document.
Exit 0 when every threshold holds, 1 when one breaks, 2 on a usage error.
"""

import argparse
import json
import os
import re
import sys

ID_RE = re.compile(r"\b(P\d+-T\d+|Q\d+|A\d+|PD\d+|D-Q\d+|UIQ\d+)\b")
PAIRED_AFTER = re.compile(r"^[*`]*(\s*\(|\s[—–-]\s|:)")
PAIRED_BEFORE = re.compile(r"\(\s*[*`]*$")
RANGE_BEFORE = re.compile(r"\b(P\d+-T\d+|Q\d+|A\d+|PD\d+|D-Q\d+|UIQ\d+)[*`]*\s*(to|–|-)\s*[*`]*$")
RANGE_AFTER = re.compile(r"^[*`]*\s*(to|–|-)\s*[*`]*(P\d+-T\d+|Q\d+|A\d+|PD\d+|D-Q\d+|UIQ\d+)\b")

STOP_WORDS = set("""
a an the this that these those each every any all some no not none both either neither
and or but nor so yet if then than when while where which who whom whose what why how
of in on at by for from to into onto with without within over under about after before
between through during against among per via as up down out off
i you he she it we they me him her us them my your his its our their
is are was were be been being am has have had do does did can could will would shall
should may might must cannot
there here also only just very more most less least much many few such own same other
one two three four five six seven eight nine ten first second third next last
never always often still already again even instead however therefore thus hence rather
itself themselves himself herself yourself plus
""".split())

DEFAULT_DICTIONARY = os.path.expanduser("~/.claude/wb/wbte-dictionary.tsv")
REFERENCE_DOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugin",
                             "docs", "reference", "technical-english.md")


def technical_nouns(path=REFERENCE_DOC):
    """Multi-word terms from the reference doc's Technical nouns list."""
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return []
    section = re.search(r"^## Technical nouns\n(.*?)^## ", text, flags=re.S | re.M)
    if not section:
        return []
    first_list = section.group(1).split("\n\n")[1]
    terms = []
    for line in first_list.split("\n"):
        if line.startswith("- "):
            terms += [t.strip() for t in line[2:].split(",") if " " in t.strip()]
    return sorted(terms, key=len, reverse=True)


TECHNICAL_NOUNS = technical_nouns()


def strip_markdown(text):
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"^(```|~~~).*?^\1[^\n]*$", "", text, flags=re.S | re.M)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"https?://\S+", "URL", text)
    lines = []
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith("#") or s.startswith("|"):
            lines.append("")
            continue
        lines.append(line)
    return "\n".join(lines)


def blocks(text):
    """Paragraphs and list items, each one a unit of prose."""
    units, current = [], []
    for line in text.split("\n"):
        s = line.strip()
        item = re.match(r"^([-*+]|\d+\.)\s+(\[[ x]\]\s+)?(.*)$", s)
        if not s:
            if current:
                units.append(" ".join(current))
                current = []
        elif item:
            if current:
                units.append(" ".join(current))
            current = [item.group(3)]
        else:
            current.append(s)
    if current:
        units.append(" ".join(current))
    return [u for u in units if u.strip()]


def sentences(unit):
    unit = re.sub(r"`[^`]*`", "CODE", unit)
    unit = re.sub(r"[*_]{1,3}", "", unit)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(✅⛔])", unit)
    return [p.strip() for p in parts if re.search(r"\w", p)]


def words(sentence):
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.-]*", sentence)


def noun_clusters(sentence, max_cluster):
    for term in TECHNICAL_NOUNS:
        sentence = re.sub(r"\b" + re.escape(term) + r"\b", term.replace(" ", "_"),
                          sentence, flags=re.I)
    sentence = re.sub(r"(?<=\w )([A-Z][a-z]+(?: [A-Z][a-z]+)+)",
                      lambda m: m.group(1).replace(" ", "_"), sentence)
    found, run = [], []
    for token in re.findall(r"[A-Za-z][A-Za-z_'’-]*|[^\sA-Za-z]", sentence):
        w = token.lower()
        is_noun_like = (
            token[0].isalpha()
            and token != "CODE"
            and w not in STOP_WORDS
            and not w.endswith(("ed", "ing", "ly", "'s", "’s"))
            and not (w.endswith("s") and not w.endswith(("ss", "us", "is")))
        )
        if is_noun_like:
            run.append(token)
            continue
        if len(run) > max_cluster:
            found.append(" ".join(run))
        run = []
    if len(run) > max_cluster:
        found.append(" ".join(run))
    return found


def lone_ids(raw):
    """IDs with no meaning nearby, by the rule in technical-english.md (Shorthand and IDs).

    Within one paragraph, an ID needs its meaning once. An ID inside another ID's meaning and
    an ID in a range ("P0-T1 to P0-T4") need none.
    """
    text = re.sub(r"^(```|~~~).*?^\1[^\n]*$", "", raw, flags=re.S | re.M)
    hits = []
    for para in re.split(r"\n\s*\n", text):
        paired = set()
        for m in ID_RE.finditer(para):
            ident = m.group(0)
            before = para[max(0, m.start() - 3):m.start()]
            after = para[m.end():m.end() + 5]
            head = para[:m.start()]
            if PAIRED_AFTER.match(after) or PAIRED_BEFORE.search(before):
                paired.add(ident)
                continue
            nested = head.count("(") > head.count(")")
            in_range = (RANGE_BEFORE.search(para[max(0, m.start() - 16):m.start()])
                        or RANGE_AFTER.match(para[m.end():m.end() + 16]))
            if nested or in_range or ident in paired:
                continue
            hits.append(ident)
    return hits


def load_dictionary(path):
    if not path or not os.path.isfile(path):
        return None
    status = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 3:
                continue
            word = cols[0].strip().lower()
            ok = cols[2].strip().lower() in ("approved", "yes", "y", "true", "1")
            status[word] = status.get(word, False) or ok
    return status


def check_file(path, chat, max_cluster, dictionary):
    raw = open(path, encoding="utf-8").read()
    prose = raw if chat else strip_markdown(raw)
    sents = [s for u in blocks(prose) for s in sentences(u)]
    lengths = [len(words(s)) for s in sents]
    joined = re.sub(r"`[^`]*`", "", "\n".join(blocks(prose)))
    result = {
        "file": path,
        "mode": "chat" if chat else "document",
        "sentences": len(sents),
        "words": sum(lengths),
        "over_20": sum(1 for n in lengths if n > 20),
        "over_25": sum(1 for n in lengths if n > 25),
        "over_40": sum(1 for n in lengths if n > 40),
        "max_words": max(lengths) if lengths else 0,
        "semicolons": joined.count(";"),
        "noun_clusters": [c for s in sents for c in noun_clusters(s, max_cluster)],
        "lone_ids": lone_ids(raw) if chat else [],
    }
    if dictionary is not None:
        tokens = [w.lower() for s in sents for w in re.findall(r"[A-Za-z]+", s)]
        result["unapproved_words"] = sorted(
            {w for w in tokens if w in dictionary and not dictionary[w]}
        )
    return result


def main(argv):
    ap = argparse.ArgumentParser(description="WBTE metric checker")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--chat", action="store_true", help="treat every file as chat output")
    ap.add_argument("--long-share", type=float, default=0.05,
                    help="max share of sentences over 25 words (default 0.05)")
    ap.add_argument("--max-cluster", type=int, default=3,
                    help="max words in a noun cluster (default 3)")
    ap.add_argument("--dictionary", default=DEFAULT_DICTIONARY,
                    help="path to the user's dictionary copy (TSV)")
    args = ap.parse_args(argv)

    dictionary = load_dictionary(args.dictionary)
    results = []
    for path in args.files:
        if not os.path.isfile(path):
            print(f"wbte_check: no such file: {path}", file=sys.stderr)
            return 2
        chat = args.chat or path.endswith(".txt")
        results.append(check_file(path, chat, args.max_cluster, dictionary))

    total_sents = sum(r["sentences"] for r in results)
    total_long = sum(r["over_25"] for r in results)
    share = total_long / total_sents if total_sents else 0.0
    failures = []
    if share > args.long_share:
        failures.append(f"{share:.1%} of sentences have more than 25 words "
                        f"(limit {args.long_share:.0%})")
    for r in results:
        if r["semicolons"]:
            failures.append(f"{r['file']}: {r['semicolons']} semicolon(s) in prose")
        if r["lone_ids"]:
            failures.append(f"{r['file']}: ID used alone: {', '.join(r['lone_ids'])}")
        if r["noun_clusters"]:
            failures.append(f"{r['file']}: noun cluster over {args.max_cluster} words: "
                            + "; ".join(r["noun_clusters"]))

    summary = {
        "files": len(results),
        "sentences": total_sents,
        "over_25_share": round(share, 4),
        "dictionary": dictionary is not None,
        "failures": failures,
        "results": results,
    }
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        for r in results:
            print(f"{r['file']} [{r['mode']}]: {r['sentences']} sentences, "
                  f"{r['over_25']} over 25 words, max {r['max_words']}, "
                  f"{r['semicolons']} semicolons, {len(r['noun_clusters'])} noun clusters, "
                  f"{len(r['lone_ids'])} lone IDs"
                  + (f", {len(r['unapproved_words'])} unapproved words"
                     if "unapproved_words" in r else ""))
        print(f"total: {total_sents} sentences, {share:.1%} over 25 words")
        for f in failures:
            print(f"FAIL {f}")
        print("PASS" if not failures else "FAIL")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
