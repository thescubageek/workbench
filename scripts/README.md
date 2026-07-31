# Scripts

Utility scripts for the project.

## Install

```bash
npm install
```

Required once per clone, before running `test-knowledge-config`. It installs `ajv`, the repo's only
node dependency — a **hard** one, because `.wb-knowledge.json` is the trust anchor of the knowledge
loop and a config that violates its schema must be *rejected*, not merely un-asserted.

`node_modules/` is gitignored and is **never** shipped. A marketplace install has no `node_modules`,
so nothing on the runtime path — the guard hook, capture — may depend on `ajv` or on
`validate-json-schema`. Dev-time only.

`markdownlint-cli` is still expected globally (see `lint` below); it is not managed by `package.json`.

## Available Scripts

### `lint`

Lints markdown files using markdownlint.

```bash
# Lint only changed markdown files (default)
./scripts/lint

# Auto-fix issues in changed files
./scripts/lint --fix

# Lint all markdown files in the project
./scripts/lint --all

# Auto-fix all markdown files
./scripts/lint --all --fix

# Show help
./scripts/lint --help
```

**Features:**

- By default, only lints files that have been changed (git diff)
- Excludes common directories (node_modules, .git, vendor, etc.)
- Uses `.markdownlintrc` for configuration if present
- Provides clear output with file status indicators
- Supports auto-fixing with the `--fix` flag

**Requirements:**

- markdownlint-cli (`npm install -g markdownlint-cli` or `brew install markdownlint-cli`)
- git (for detecting changed files)

### `lint-hook`

Hook script used by Claude Code to automatically lint markdown files after they are created or edited.

```bash
# This script is automatically triggered by Claude Code hooks
# It's configured in the plugin manifest: .claude-plugin/plugin.json (hooks block)
```

**Features:**

- Automatically runs after Write or Edit tools modify markdown files
- Attempts to auto-fix issues with markdownlint
- Shows concise output in Claude Code interface
- Non-blocking (won't stop operations if linting fails)

### `quiet`

Runner-agnostic output backpressure for the TDD/verification loop. Wraps any
command: a green run collapses to a single checkmark plus the command's own
summary line; a red run dumps the full captured log so no failure detail is
lost. The wrapped command's exit code is always passed through unchanged.

```bash
# Green run -> one checkmark + summary line; full output suppressed to a tmpfile
./scripts/quiet pytest -q
./scripts/quiet make test

# Red run -> full output is printed verbatim, original exit code preserved
./scripts/quiet go test ./...
```

**Features:**

- Generalizes the `lint-hook` pattern (run → keep a marker line → suppress the rest) to any runner
- Success path keeps the model inside its working-context "smart zone" (a 200-line green run becomes ~2 lines)
- Failure output is never truncated — full log on any non-zero exit
- Exit-code-faithful, so `verification-before-completion` checks keep working
- Opt-in: invoke it explicitly; nothing is wrapped automatically

**Verify the contract:**

```bash
./scripts/test-quiet
```

### `test-quiet`

Contract tests for `quiet` (success collapse, failure dump, exit-code pass-through). Run after changing `quiet`.

### `knowledge-worktree`

Resolves the knowledge store for this repo and prints its root path on stdout. The store lives on a
long-lived branch declared in `.wb-knowledge.json`; git allows a branch to be checked out in only one
worktree at a time, so this **resolves to an existing checkout wherever it already is** — including a
sibling Conductor workspace — rather than competing for one. Only when nothing holds the branch does it
create a worktree.

```bash
STORE="$(./scripts/knowledge-worktree)" || exit 1
ls "$STORE/entries"
```

**Contract:**

- On success, stdout is the store root path and nothing else
- Every failure is non-zero, legible, and on stderr — **never a silent no-op**, because a capture that
  quietly writes nowhere looks like a working loop while recording nothing
- Repeated runs return the identical path and create nothing extra

**Exit codes:** `2` not in a git repo · `3` no `.wb-knowledge.json` · `4` store branch missing ·
`5` checkout has no store root · `6` worktree creation failed

**Environment:** `WB_KNOWLEDGE_WORKTREE` overrides where a worktree is created;
`WB_KNOWLEDGE_NO_JQ=1` forces the jq-free parsing fallback.

### `test-knowledge-worktree`

Contract tests for `knowledge-worktree`. Builds throwaway git repos under a temp dir — never touches the
real repository or its worktrees. Covers the resolve/create/reuse cases, idempotency, the
branch-held-by-another-worktree case, the jq-free fallback, and every loud-failure path.

### `validate-json-schema`

Validates JSON documents against a JSON Schema using `ajv`. Written for one job — proving that
`.wb-knowledge.json` is *enforced* by `.wb-knowledge.schema.json` rather than merely described by it —
but takes any schema and any number of data files.

```bash
./scripts/validate-json-schema .wb-knowledge.schema.json .wb-knowledge.json
```

**Exit codes:** `0` all valid · `1` at least one document invalid (errors on stderr) · `2` usage error,
unreadable file, or a schema that will not compile · `3` `ajv` not installed — run `npm install`.

Dev-time only; see the install note above.

### `test-knowledge-config`

Contract tests for `.wb-knowledge.json` and `.wb-knowledge.schema.json`, in two layers.

**Structural (`jq`)** — the trust anchor holds: the config declares itself protected, the harness paths
and the files pinning the validator are covered, `knowledge/staging/` is *not* covered (capture must be
able to write there), every declared path actually exists, and — the negative assertions that matter
most — core self-extension has no policy surface anywhere in either file.

**Enforcement (`ajv`, via `validate-json-schema`)** — the schema is executed, not just read. Mutated
copies of the live config are fed to a real validator and each must be rejected: one carrying
`write_policy.core_self_extension`, one with `model_narrated: "auto-promote"`, one whose
`protected_paths` omits itself, and nine more. A **positive control** runs alongside them — relaxing
`tool_verified` to `auto-promote`, the one axis the policy may relax, must still be *accepted* — because
without it every rejection would also pass against a validator that simply refuses everything.

Run it after any edit to either file. If the negative assertions start failing, a bypass has been
reintroduced. Requires `npm install` first.

### `test-knowledge-guard`

Contract tests for `hooks/knowledge-guard.sh`, the three-state `PreToolUse` guard. Feeds payloads to
the script on stdin in throwaway git repos and asserts every row of the behaviour table, plus path
resolution (symlinks, `..`, `/tmp` → `/private/tmp`), the jq-free fallback, output hygiene, and the two
cases the boundary actually rests on:

- **arming cannot be set from anything the agent can write** — an in-repo marker file, a fabricated
  payload field, and `tool_input.content` claiming `interactive` all change nothing
- **interactive is asserted, never inferred** — `permission_mode` may *veto* an interactive claim but
  can never establish one, because a headless run reports `"default"` exactly like an interactive one

This tests the script. It cannot test whether Claude Code ever calls it — see the probe below.

### `probe-knowledge-guard`

**Opt-in; spawns real `claude -p` sessions and costs model calls.** Not part of `npm test`.

Tests what the contract test structurally cannot: registration and enforcement. Hook configuration is
read once at session start, so an in-session settings edit registers nothing — only a child session
with `--settings` exercises the real path. Three runs, each an A/B against a control file the guard
ignores:

| Run | Repo | Armed | Expected |
| --- | --- | --- | --- |
| A | configured | `full-auto` | control written, sentinel **refused** |
| B | configured | no | control written, sentinel **written** |
| C | unconfigured | `full-auto` | control written, sentinel **written** |

B is what makes A mean anything — a guard that denied everything would look identical without it. C is
the regression that matters most to users: a marketplace install must never deny writes in a repo that
has not opted in.

```bash
./scripts/probe-knowledge-guard              # uses haiku
WB_PROBE_MODEL=sonnet ./scripts/probe-knowledge-guard
```

Not covered: the interactive `ask` row, which cannot be observed headlessly and needs a human at a
terminal.

### `test-knowledge-capture`

Contract tests for `hooks/knowledge-capture.sh`, the automatic `Stop` / `SubagentStop` capture. Feeds
payloads on stdin in throwaway git repos and asserts the entry shape from `knowledge/SCHEMA.md`, the
five-component ID scheme, and the properties that carry the design:

- **it writes to `staging/` and never to `entries/`** — staged content is ungated, and if retrieval
  could reach it, unreviewed content would steer future tickets
- **every capture is `origin: model-narrated`**, and the hook contains no path that can emit
  `tool-verified` at all — a turn boundary sees the model's summary, never a tool's observation
- **8 simultaneous captures produce 8 distinct files** — the sequence is allocated by atomic create
  with retry, because counting existing files is a read-then-write race
- **silent in an unconfigured repo, loud in a configured one whose store is unreachable**

Store *resolution* is not re-tested here; `test-knowledge-worktree` already covers it.

### `knowledge-sweep`

The git-only staleness sweep. For each promoted entry it runs
`git diff --name-only <verified_at>..HEAD -- <cited paths>` and classifies the result. **No model calls
and no `jq`** — entry frontmatter is YAML, and the whole economy of the design is that this check is free
over the entire store so only the suspects cost anything.

```bash
./scripts/knowledge-sweep              # promoted entries
./scripts/knowledge-sweep --staging    # include ungated captures too
```

| Verdict | Meaning |
| --- | --- |
| `clean` | Nothing cited has changed since `verified_at` |
| `suspect` | Something cited changed — **not wrong, just unverified since**. Refer to `agents/research-validator.md` |
| `undecidable` | The question cannot be asked: no cites, no SHA, or a SHA this repo does not have |

**`undecidable` is the one that matters.** An entry citing no files trivially has no changed cited
files, and calling that `clean` would launder "I cannot tell" into "I checked". It is also the common
case, not a corner case — every automatic capture cites nothing.

### `knowledge-read`

The retrieval path. Returns **promoted** entries matching any given scope tag, ranked and bounded.

```bash
./scripts/knowledge-read --scope subsystem:hooks --limit 3
./scripts/knowledge-read --paths          # paths only, for feeding to Read
./scripts/knowledge-read                  # defaults to repo:<this repo>, limit 5
```

**It reads `entries/` and nothing else.** Staged content is ungated, auto-captured and unreviewed;
surfacing it would let content nothing has reviewed steer the next ticket, which is the exact vector the
promotion gate exists to close. There is no flag to include it — `--staging` is an *error* with an
explanation, not an option.

Bounded always: default limit 5, hard ceiling 25, and the default scope is `repo:<this repo>` rather than
"everything". A wholesale load is not a generous default — retrieval noise and negative transfer are the
measured failure modes and both worsen as the store grows.

Ranking is specificity first: more matching scope tags, then higher confidence, then id. Deprecated
entries are never returned.

**Exit codes:** `0` read, possibly zero matches · `3` no `.wb-knowledge.json` · `4` store unreachable ·
`64` usage. **Callers must treat any non-zero as "no knowledge available" and continue** — the read path
is best-effort and never blocking.

### `test-knowledge-read`

Contract tests for the above. This script exists because the execution plan originally specified
retrieval as *prose inside a command*, which would have made every property below unverifiable — this
repo has no way to test markdown, and `./scripts/lint` checks formatting only. Retrieval's failure modes
are silent, so they need a test rather than a promise.

Covers: the staging invariant asserted three ways (a decoy staged entry that matches every filter, a
source check that no path into the tree is constructed, and the refused flag); deprecated and
non-promoted entries excluded; scope filtering and OR-ing; the default limit, an explicit limit, and the
hard ceiling; both ranking rules; and that an unavailable store exits non-zero with an empty stdout so a
caller can pipe it safely.

### `knowledge-sync`

Merges the upstream branch forward into the store branch, **then sweeps**. The two are one command
because every `main` commit is potential invalidation churn, so entries should be re-classified as the
code moves under them rather than at some later moment of remembering.

```bash
./scripts/knowledge-sync --dry-run
./scripts/knowledge-sync
```

**There is deliberately no `--rebase`, and passing it is an error rather than a no-op.** Rebasing the
store branch rewrites the commits that entry provenance SHAs point at, so every stored `verified_at`
would stop resolving — silently, with no error at the moment of damage.

**Exit codes:** `2` not a git repo · `3` no `.wb-knowledge.json` · `4` store unreachable · `5` the store
checkout is not on the store branch · `6` merge failed or the checkout is dirty

### `test-knowledge-sweep`

Contract tests for both of the above. Covers each verdict including the deleted-file and
mixed-cites cases, the three distinct routes to `undecidable`, that staging is excluded by default, and
that `knowledge-sync` refuses `--rebase` and refuses to merge into the wrong branch.

Two of its checks — "makes no model calls", "needs no jq" — are **negative** assertions that would pass
on an empty file. They exist to catch a future regression, not to prove the script works; the other
twenty-odd behavioural checks do that.

### `knowledge-proposal-lint`

Validates a curation proposal against the rules `/wb:curate_knowledge` is supposed to follow.

```bash
./scripts/knowledge-proposal-lint knowledge/proposals/<dir>
```

A curation pass makes judgments no script can check — whether a claim is durable, whether a merge is
wise. But most of the ways a pass goes *wrong* are visible in what it produced, so: **validate the
artifact, not the judgment.** That turns "the pass followed its own rules" from trust into a test.

Checks: the operation is one of the four; **the diversity rule** (see below); no `FAIL`/`UNCERTAIN`
entry is promoted; every promotion carries a non-vacuous prediction; deprecates carry a reason and no
prediction; the entry is schema-valid with a real SHA and resolving cites; no placeholder survived;
nothing targets a protected path.

**The diversity rule runs the way the design states it, which is the opposite of the intuitive reading.**
A merge names the ticket class each source wins on. If those classes **differ**, the merge is *refused* —
each entry wins somewhere, so collapsing them yields one canonical best practice that is second-best
everywhere. A merge is justified only when the sources win on the *same* class, i.e. they genuinely
duplicate. Naming no classes is also a rejection: an unanswered check is not a passed one.

**Exit codes:** `0` all valid · `1` violations, each named with its file · `2` usage or no such directory.

### `test-knowledge-proposal-lint`

Contract tests, 36 checks, mutation-style: one well-formed proposal plus a single targeted change per
case, so every rejection is attributable to the one thing that differs. Includes the positive control —
the unmutated proposal must be **accepted** — without which every rejection would pass against a linter
that refuses everything.

## The knowledge guard

`hooks/knowledge-guard.sh` is registered on `PreToolUse` for `Write|Edit|MultiEdit|NotebookEdit` in
`.claude-plugin/plugin.json`. It is inert unless the repo declares `.wb-knowledge.json` **and** the
session was armed:

```bash
WB_SELF_EXTENSION=interactive claude          # armed, human present  -> protected writes ask
WB_SELF_EXTENSION=full-auto  claude -p ...    # armed, unattended     -> protected writes deny
claude                                        # not armed             -> inert
./hooks/knowledge-guard.sh --selfcheck        # is enforcement actually available here?
```

Arming is an environment variable because that is the one channel the agent cannot reach: tool-layer
processes are children of the session and cannot mutate the environment the hook inherits. Verified by
execution — an `export WB_SELF_EXTENSION=full-auto` run by the agent's own Bash tool did not change
what the hook subsequently saw.

**Known hole, stated rather than papered over:** a shell redirect through the Bash tool
(`printf x > commands/help.md`) produces no `PreToolUse` Write event and is not seen. The designed
answer is the CI / CODEOWNERS layer, which must exist before the first unattended run.

## Configuration

The project uses `.markdownlintrc` for markdownlint configuration. Current settings:

- Line length checking disabled (for long code blocks)
- Inline HTML allowed
- Emphasis as heading allowed (for "think deeply" directives)
- Fenced code blocks without language specification allowed

## Claude Code Hooks

The project has automatic markdown linting configured via Claude Code hooks in the plugin manifest `.claude-plugin/plugin.json` (`hooks` block):

- **PostToolUse hooks** for Write and Edit tools
- Automatically runs `${CLAUDE_PLUGIN_ROOT}/scripts/lint-hook` after any markdown file is created or modified
- Attempts to auto-fix common markdown issues
- Shows brief status messages in the Claude Code interface

To disable automatic linting, remove or comment out the `hooks` section in `.claude-plugin/plugin.json`.
