---
id: 20260731-maputo-handseed-main-009
kind: procedural
origin: tool-verified
confidence: medium
status: staged
scope:
  - repo:workbench
  - subsystem:testing
  - ticket-class:testing
provenance:
  verified_at: fd8d39a59a3c825b038c19847ef2dbd6e2feae5b
  cites:
    - path: hooks/knowledge-capture.sh
    - path: scripts/knowledge-read
---

**A health check that counts `*.md` in a directory which also holds documentation lies in the reassuring
direction.** `knowledge-capture --selfcheck` reported "1 staged so far" against a store whose only file
was `staging/README.md` — an empty store reporting as a working one. Counting by ID shape fixed it.

Generalise: when a check counts artifacts in a shared directory, the failure mode is over-counting, and
over-counting always reads as health. Count by the shape of the thing you mean, not by file extension.

Related and verified explicitly: **negative assertions pass on an empty file.** Checks of the form "this
script contains no call to X" hold trivially against a script that does nothing. They catch regressions;
they do not prove the script works. A suite that counts them among its passes overstates its coverage.
