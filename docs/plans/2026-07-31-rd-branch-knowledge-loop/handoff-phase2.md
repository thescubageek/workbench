---
project: rd-branch-knowledge-loop
created: 2026-07-31
status: ready
from_session: kyiv (store branch)
for_branch: thescubageek/knowledge-store-v1
resume_at: P1-T9, then Phase 2
---

# Handoff: Knowledge Store — P1-T9 + Phase 2 (Enforcement Boundary)

**Repo**: `thescubageek/workbench` — the `wb` Claude Code plugin
**Your branch**: `thescubageek/knowledge-store-v1` (cut from `main` at `1535d8a`, v1.12.4)
**Head**: `79c8e59` — "Knowledge store: config, schema, and store-access scripts"
**Plan docs**: `/Users/thescubageek/conductor/workspaces/workbench/kyiv/docs/plans/2026-07-31-rd-branch-knowledge-loop/`

Read `design.md` and `tasks.md` fully before touching anything. They are **not on your branch** — see
"Two branches" below. `tasks.md` is the plan of record: 7 phases, 42 tasks, 12 done.

## Two branches, and why

The store branch never merges outbound, so code built on it could never reach an installed user. As of
2026-07-31 the work is split:

| Branch | Holds | Workspace |
| --- | --- | --- |
| `thescubageek/knowledge-store-v1` (yours) | All code: `hooks/`, `scripts/`, `commands/`, `.wb-knowledge.json` | this one |
| `thescubageek/self-learning-loops-research` | `knowledge/**` and `docs/plans/**` only | `kyiv` |

Code flows **feature → `main` → forward-merge into the store branch**. Knowledge never travels the other
way. `docs/plans/` deliberately stays on the store branch: it is gitignored dev-only content
(`.gitignore:7`) and must never reach `main` through your PR.

So: **read and update the plan docs at the `kyiv` path above**, and commit them from that workspace (or
just leave them to whoever is driving there). Do not copy them onto your branch.

## Start here: P1-T9 (added during review, closes a real gap)

Phase 1 shipped `.wb-knowledge.schema.json`, which makes "auto-promote core self-extension"
unexpressible — no such property, `additionalProperties: false` at every level, `model_narrated` pinned
to a `const` rather than an enum. But **nothing validates the config against it.** There is no ajv and no
python `jsonschema` in this repo; the 31 `jq` assertions in `scripts/test-knowledge-config` verify the
schema *says* the right thing, not that anything rejects a config violating it.

Decided: add `ajv` as a **hard dependency** and validate in the test suite. That means a `package.json`
(the repo has none — `markdownlint-cli` is assumed global) and an install note in `scripts/README.md`.
Turn the three negative fixtures described at the foot of `scripts/test-knowledge-config` into real
rejection tests:

- a config carrying `write_policy.core_self_extension` → **rejected**
- one with `model_narrated: "auto-promote"` → **rejected**
- one whose `protected_paths` omits itself → **rejected**

That is what upgrades P1-T6 from "the schema says so" to enforcement.

## Then Phase 2 — the enforcement boundary, 7 tasks

Build `hooks/knowledge-guard.sh`: the three-state `PreToolUse` guard. Inert during normal development,
`ask` in an armed interactive run, hard `deny` in an armed full-auto run. Full task list in `tasks.md`
§ Phase 2.

**Phase 0 already verified every row of that table against Claude Code 2.1.195, by execution.** Don't
re-derive it; the findings are in `design.md` → "Phase 0 Tracer Bullet — Executed Findings":

- `deny` holds in **all five** permission modes, including `bypassPermissions`. Not bypassable.
- `ask` is never silently auto-approved. Confirmed interactively via an A/B: under `accept edits on` a
  control file wrote silently and the sentinel prompted.
- `Stop`/`SubagentStop` fire and write reliably; payloads carry `transcript_path`, and subagent payloads
  add `agent_id` / `agent_transcript_path`. Phase 3 has more substrate than the design assumed.

### The finding that shapes P2-T4 and P2-T5

**Full-auto is not detectable from the hook payload.** `permission_mode` *is* present, but a headless
`claude -p` run reports `"default"` — byte-identical to an interactive session. Attendance can never be
confirmed from inside the hook; the elevated modes are a one-way suspicion signal only.

Concrete rule: **absent a positive interactive assertion from the arming act, treat the run as full-auto
and `deny`.** Arming must be established by the human act that starts the run, outside the agent's tool
layer. If the loop can set its own armed state, or claim interactive when it is full-auto, it downgrades
`deny` to `ask` and self-approves — every other control falls with it.

### Path matching, learned the hard way

The `file_path` a hook receives is a **resolved absolute path, and not necessarily the one anyone typed.**
Claude Code 2.1.195 was observed redirecting `Write` calls into a per-session scratchpad
(`/private/tmp/claude-501/<slug>/<uuid>/scratchpad/`), and `/tmp` arrives as `/private/tmp`. So:

- compare **resolved** paths (symlinks, `/tmp` → `/private/tmp`) against the protected set
- **"outside every protected prefix" is not "safe."** It is the indeterminate case, which the behaviour
  table sends to `deny` inside a configured repo. A naive repo-relative prefix match is both bypassable
  and wrong.

## Testing this thing

Two layers, and you need both — a contract test alone will not catch a registration mistake:

1. **Contract tests** feed a payload to the script on stdin, in the exact `scripts/test-quiet` idiom
   (`check "desc" "$cond"`, PASS/FAIL counters, non-zero exit). This tests the script.
2. **A child `claude -p` session** with `--settings` tests the *registration and enforcement*. Hook config
   is read once at session start, so editing settings mid-session registers nothing and proves nothing.

**Any hook-behaviour probe needs an A/B in the same session.** A single observation cannot separate the
hook's effect from the harness's own default — that mistake already cost one inconclusive round in Phase
0. Working scaffolding is at `/tmp/wb-hook-probe` (hook matches only paths ending `sentinel.txt`;
`PROBE_DECISION` in the settings file selects deny/ask). The full recipe is in `tasks.md` § "Interactive
`ask` check".

TDD is enforced (`skills/tdd-discipline`): **RED before GREEN**, so `scripts/test-knowledge-guard`
(P2-T1) is written and failing before `hooks/knowledge-guard.sh` exists.

## Five things that will bite you

1. **The top risk is breaking other people's repos.** A hook in `plugin.json` fires in every install. The
   answer: inert unless the host repo declares `.wb-knowledge.json`, inert again unless a run is armed.
   Verify by hand in a scratch repo at the Phase 2 checkpoint. This is the one regression that damages
   users, not just this repo.
2. **The enforcement hook is inert during normal development**, so building it does not obstruct building
   it. Phase 2's tests must arm it deliberately to exercise deny/ask.
3. **The arming signal is itself protected.** It is core self-extension by definition.
4. **Never rebase or force-push the store branch.** Rebasing rewrites the commits entry provenance SHAs
   point at. (Your branch is a normal feature branch — rebase it freely.)
5. **`main` has moved to v1.12.4.** P6-T4's bump is `1.12.4 → 1.13.0`, not from `1.12.3`. Both
   `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, and they must match.

## The locked constraint — do not soften it

All **core self-extension** is permanently human-gated. No exceptions, no configurable override, no
earned-autonomy path: (1) the eval corpus and its rubrics, additive-only; (2) the harness components —
`commands/`, `agents/`, `skills/`, `hooks/`, `CLAUDE.md`; (3) **the gate and write-policy config itself**,
the hardest one — if the loop can edit the policy deciding what needs review, every other control is
bypassable in one move. Ambiguous cases are default-denied into that set. The user's framing: "otherwise
we have a huge vector."

This repo's protected set is the **thirteen paths** in `.wb-knowledge.json`, reviewed and confirmed
2026-07-31. `knowledge/staging/` is deliberately excluded so capture can write there — that absence is
load-bearing and `test-knowledge-config` asserts it.

## Repo conventions

- **Beads is not used for this project** — decided 2026-07-31, documentation-only. `P0-T1`-style local
  IDs are the only task identifiers. Do **not** substitute TodoWrite, TaskCreate, or markdown checkboxes;
  `CLAUDE.md` forbids all three. Consequence: cross-session status lives in `tasks.md`'s phase gates plus
  git history, so update them as each phase lands.
- **Hook payload parsing**: `scripts/lint-hook:9-19` is the working in-repo example — JSON on stdin,
  `jq` with a `grep`/`sed` fallback. Reuse the idiom including the fallback; the plugin cannot assume `jq`.
- **Markdown lints automatically** on Write/Edit via PostToolUse; `./scripts/lint --all` to check.
- **Output discipline** (`CLAUDE.md`): the artifact is the deliverable, not the chat. No barrier
  announcements, no reproducing written files back into the conversation.

## State of play

- **Phase 0** — complete. All three hook primitives verified by execution, no assumption left resting on
  documentation.
- **Phase 1** — complete, 8/8, plus P1-T9 outstanding. `knowledge/` layout, `SCHEMA.md` (seven fields, ID
  scheme, one real worked entry), `.wb-knowledge.json` + schema, `scripts/knowledge-worktree`. Tests:
  26/26 worktree, 31/31 config, 9/9 quiet, lint clean.
- **Next** — P1-T9, then Phase 2's 7 tasks.

Model plan: **Opus 5 / high** for Phase 2, with a focused `max` pass on **P2-T4** (arming) and **P2-T5**
(full-auto detection) — the two tasks where getting it subtly wrong yields a boundary that looks real and
isn't. Sub-agent tiering is free; push test scaffolds to Sonnet.

Start with P1-T9, then `/wb:implement_tasks` at Phase 2.
