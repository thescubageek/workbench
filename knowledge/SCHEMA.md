# Entry Schema

One entry per file. YAML frontmatter carries the machine-readable fields; the body carries the claim.
Applies to both `staging/` and `entries/` — promotion moves a file between trees and adds review
metadata, it does not reshape it.

## Fields

Seven required fields. Each exists because some other part of the design cannot work without it — this
is the minimum set, not a wish list.

| Field | Required | Purpose | Without it |
| --- | --- | --- | --- |
| `id` | always | Stable identity | Deltas address documents instead of entries, so concurrent proposals conflict |
| `claim` (body) | always | The knowledge itself, one dense self-contained block | — |
| `provenance` | always | Cited `file:line` refs + the SHA verified against | Staleness stops being computable and needs a model call |
| `confidence` | always | `high` / `medium` / `low` | Retrieval cannot weight, curation cannot triage |
| `scope` | always | Repo / subsystem / ticket-class tags | No defence against negative transfer; retrieval is wholesale |
| `kind` | always | `semantic` / `procedural` / `episodic` | The invalidation path cannot tell which entries it can even reason about |
| `origin` | always | `tool-verified` / `model-narrated` | The write policy has no axis to tier on |
| `status` | always | `staged` / `promoted` / `deprecated` | — |
| `prediction` | promoted only | The entry's expected effect, checkable later | Promotion stays trial-and-error instead of a falsifiable contract |

### `kind`

- **`semantic`** — how something works. "The plugin registers hooks in X, payloads arrive as Y."
- **`procedural`** — how to do a class of change here. "Releasing means bumping both version files."
- **`episodic`** — what happened on a particular ticket and why. "We tried X on ticket N; it failed
  because Z."

The distinction is not filing. Only entries that cite files are reachable by the git staleness sweep;
procedural and episodic entries that cite nothing decay on a clock nothing observes, and are the
curation pass's problem rather than the sweep's. `kind` is how you tell which is which.

### `origin`

- **`tool-verified`** — derived from tool output: test results, a diff, a validator verdict, an executed
  probe.
- **`model-narrated`** — everything else, including anything a model concluded, summarised, or inferred.

This is the axis the write policy tiers on, so **mislabelling it defeats the policy**. When unsure, it is
`model-narrated`. "The model read a file and reported what it said" is narration, not verification —
reading is not a test. What makes a capture `tool-verified` is that a tool produced an observation the
model did not author.

### `provenance`

```yaml
provenance:
  verified_at: <full 40-char SHA the claim was checked against>
  cites:
    - path: relative/path/from/repo/root
      lines: "10-45"        # optional; omit for whole-file claims
```

`verified_at` must be a real commit on this branch. Staleness is then a computed predicate, not a stored
flag:

```bash
git diff <verified_at>..HEAD -- <cited paths>
```

Non-empty means *suspect* — not wrong, just unverified since. Suspect entries go to
`agents/research-validator.md` for an actual verdict. Cheap check first, expensive check only on the
suspects.

## ID scheme

```text
<UTC-date>-<workspace>-<session8>-<agent8|main>-<seq>
20260731-kyiv-38409c98-main-001
```

Collision-freedom matters because parallel Conductor workspaces share **one** store checkout (git allows
one worktree per branch), so simultaneous captures write into the same directory.

| Component | Example | Why it is needed |
| --- | --- | --- |
| UTC date | `20260731` | Sorts chronologically, reads at a glance, bounds any scan by time |
| workspace | `kyiv` | Two workspaces on the same repo capturing in the same second |
| session (8 chars) | `38409c98` | Two runs in the same workspace; taken from `session_id` in the hook payload |
| agent (8 chars) or `main` | `main` | Two subagents finishing simultaneously in one session; from `agent_id` on `SubagentStop` |
| sequence | `001` | Several captures within one run |

The first four components make a collision unlikely. They do not make it impossible — two subagents can
finish in the same millisecond — so **the writer must allocate the sequence by atomic create** (`set -C`
/ `O_EXCL`) and retry on failure, rather than by counting existing files. Counting is a read-then-write
race and will eventually lose. The components give legibility; the atomic create gives the guarantee.

## Template

```markdown
---
id: 20260731-kyiv-38409c98-main-001
kind: semantic
origin: tool-verified
confidence: high
status: staged
scope:
  - repo:workbench
  - subsystem:hooks
provenance:
  verified_at: 38409c985e98a861312fcaa37525ece1417e1123
  cites:
    - path: .claude-plugin/plugin.json
      lines: "10-45"
---

<the claim: one dense, self-contained block that makes sense to a reader with no other context>
```

## A real entry

Not a stub — this is a true claim about this repository, verified at the SHA it names, and it is the
first content the store was built to hold.

```markdown
---
id: 20260731-kyiv-38409c98-main-001
kind: procedural
origin: tool-verified
confidence: high
status: staged
scope:
  - repo:workbench
  - subsystem:hooks
provenance:
  verified_at: 38409c985e98a861312fcaa37525ece1417e1123
  cites:
    - path: .claude-plugin/plugin.json
      lines: "10-45"
    - path: scripts/lint-hook
      lines: "9-19"
---

Hooks in this plugin are registered in `.claude-plugin/plugin.json` under a top-level `hooks` key
(`:10-45`), not in `.claude/settings.json` — the repo's `.claude/settings.json` is an empty object and
exists for local developer config only. Each hook entry is `{type: "command", command:
"${CLAUDE_PLUGIN_ROOT}/...", timeout: N}`, and `CLAUDE_PLUGIN_ROOT` is what makes the path work under a
marketplace install, where the plugin is cached at a version-keyed path rather than checked out.

Every hook script receives its event payload as **JSON on stdin** — not as an environment variable.
`scripts/lint-hook:9-19` is the in-repo reference: it reads stdin into `PAYLOAD`, extracts
`.tool_input.file_path` with `jq`, and falls back to `grep`/`sed` when `jq` is absent. New hooks should
copy that idiom rather than re-deriving it, including the fallback — the plugin cannot assume `jq` on a
user's machine.

Two consequences that cost time if unknown. First, **hook configuration is read once at session start**,
so editing a settings file mid-session registers nothing; a hook change is only exercised by a fresh
session, which for testing means a child `claude -p` run with `--settings`. Second, the `file_path` a
hook receives is a **resolved absolute path and not necessarily the one anyone typed** — Claude Code
2.1.195 was observed redirecting `Write` calls into a per-session scratchpad
(`/private/tmp/claude-501/<slug>/<uuid>/scratchpad/`), and `/tmp` arrives as `/private/tmp`. Any hook
matching on paths must compare resolved paths, and must not treat "outside my expected prefix" as
"irrelevant".

Verified by executing `PreToolUse`, `Stop`, and `SubagentStop` probes against Claude Code 2.1.195 as
headless child sessions; all three delivered JSON on stdin with the documented shape.
```

Why this is `tool-verified` rather than `model-narrated`: the claims about stdin delivery, session-start
snapshotting, and path resolution were each established by running a probe and observing the result. The
cited line ranges were read, but reading is not what makes it verified — the executed probes are.
