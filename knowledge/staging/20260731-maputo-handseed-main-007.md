---
id: 20260731-maputo-handseed-main-007
kind: procedural
origin: tool-verified
confidence: high
status: staged
scope:
  - repo:workbench
  - subsystem:agents
  - ticket-class:validation
provenance:
  verified_at: fd8d39a59a3c825b038c19847ef2dbd6e2feae5b
  cites:
    - path: agents/research-validator.md
      lines: "123-181"
---

`agents/research-validator.md` accepts a knowledge-store entry unchanged — no schema shim needed. Its
contract is "you will receive a path to a research document", and an entry file is that shape; it ignores
the YAML frontmatter harmlessly and validates the claim body.

**Read its overall status, never its per-path table.** Probed with a true/false pair citing the same
files: the true entry returned PASS 4/4, the false one FAIL 0/4 with correct specific corrections — but
on the false entry it marked a cited file `PASS` in the *path* table because the file exists, while
failing every behavioral claim about it. That is correct per its own rubric, since path existence is not
claim accuracy. A document can cite files that all still exist and be entirely wrong.

A single PASS would not have distinguished a working validator from one that rubber-stamps; the false
half of the pair is what made the result mean anything.
