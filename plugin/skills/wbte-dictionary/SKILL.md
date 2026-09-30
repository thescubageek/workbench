---
name: wbte-dictionary
description: Make a private, local copy of the ASD-STE100 approved-word dictionary from the user's own free copy of the Issue 9 PDF, for wb Technical English (WBTE) word lookups. The copy lives under ~/.claude/wb/ and never in a repository. Trigger phrases like "wbte dictionary", "set up the STE dictionary", "extract the dictionary from my ASD-STE100 PDF", "/wbte-dictionary".
argument-hint: "[path-to-ASD-STE100-Issue-9.pdf]"
allowed-tools: Bash, Read
---

Write your replies in this skill in wb Technical English (WBTE): read [technical-english.md](../../docs/reference/technical-english.md) and apply it.

This skill makes a private copy of the approved-word dictionary for WBTE. The plugin works
without the copy. With the copy, the model can look up a single word when it is not sure, and
the eval harness can count unapproved words.

ASD does not permit redistribution of the standard, so the plugin ships no part of it. The
user gets the PDF from ASD and runs the extraction on their own machine. The copy stays out of
every repository.

## 1. Find the PDF

The PDF path is the argument. If there is no argument, tell the user these facts, then stop
and wait for a path:

- The standard is ASD-STE100 Issue 9. It is free of charge from ASD:
  <https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf>
- The user downloads it. The plugin cannot download it for them.
- The next step is `/wb:wbte-dictionary <path-to-the-pdf>`.

## 2. Run the extractor

Run the script from this skill's base directory:

```bash
<this skill's base directory>/../../scripts/wbte-dictionary "<path-to-the-pdf>"
```

The script uses `pdftotext` if it is installed. Otherwise it uses python3 with `pypdf`. It
writes `~/.claude/wb/wbte-dictionary.tsv` and nothing else.

## 3. Report the result

- **Exit 0.** Report the entry count and the number of approved words from the script output.
  Say that the copy is at `~/.claude/wb/wbte-dictionary.tsv`, outside every repository.
  Say that the alternatives column is best-effort, so some rows have it empty.
- **Exit 2 with "no PDF text extractor found".** Show the two install options that the script
  printed. Stop. The plugin still works without the copy.
- **Exit 2 with another message.** Show the message. The file is probably not the Issue 9
  PDF.
- **Exit 3.** The home directory is inside a git work tree. Show the message, and do not
  work around it. A copy inside a repository could be committed by accident.

Do not print dictionary entries in the conversation. Do not copy the file into a repository.
