# Shipped runtime reference

**This directory is part of the installed plugin.** Everything here is read at runtime by a
skill that links to it instead of restating its contents.

## What belongs here

A document belongs in `plugin/docs/reference/` when all four are true:

1. **More than one skill needs it.** A rule used by exactly one skill belongs in that skill's
   own directory as a supporting file, not here.
2. **It is read at runtime**, by a skill step that directs the read — not consulted by a
   maintainer.
3. **It states a rule or a contract**, not a narrative. History, migration stories, and
   session logs are not reference material.
4. **Linking beats restating.** The alternative is the same paragraph copied into several
   skills, where the copies drift.

Link to it from the skill with a relative path and an explicit read instruction, the way the
supporting-file manifests do — never paraphrase it from memory. Permission follows the plugin
root, not the skill directory: a marketplace-installed stage reads here without a prompt
(measured 2026-09-15, headless, boundary forced on), while a `--plugin-dir` checkout run from
another directory is gated like any other supporting file. `allowed-tools: Read` does not
change either case — it is a tool pre-approval, not a path grant.

## What does not belong here

- **Maintainer-facing material.** Root `docs/` is for maintainers and is never shipped. That
  is the boundary: if an installer does not need it at runtime, it does not go under
  `plugin/`.
- **Plan artifacts.** Those live in `docs/plans/<date>-<name>/`.
- **Anything single-skill.** Use a supporting file in the skill's own directory.
- **Retained history.** If history is worth keeping, keep it under `docs/` and mark it
  non-normative at the top so it cannot be read as current guidance.

## Why the boundary is a rule and not a preference

The plugin has already been bitten by the alternative. Documents that outlived their subject
kept *instructing* — a stale instruction reads as authority in a way a stale description does
not — and one of them contradicted the shipped rules for months while nothing linked to it, so
nothing warned a session before a grep surfaced it.

Two rules follow, and they are the whole point of this directory existing:

- A shipped skill may link **only** into `plugin/docs/reference/`. If a skill needs a rule,
  the rule is here or it is in the skill.
- Nothing under root `docs/` is ever a runtime rules source.
