---
name: meta-review
description: Run the engineering-reviewer and workflow-reviewer meta-review agents against the wb plugin itself (a branch, a PR, or a worktree) and produce a combined triaged report. Use before merging a PR or shipping a version bump. Trigger phrases like "review wb", "run the reviewers", "meta-review", "eval this PR", "re-review against main".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(gh auth *, gh pr *, gh repo *, git:*)
---

# Meta-Review wb

Run the two meta-review agents (`engineering-reviewer`, `workflow-reviewer`) against wb's own codebase, in parallel, and produce a combined triaged report. Supports fresh reviews and delta-against-prior reviews.

This is wb's release gate: an adversarial two-lens review of the plugin BEFORE a PR merges or a version bumps. It mirrors the meta-review pattern in the sibling verticals (CaseSmith, Prestwood), adapted for the domain-agnostic kernel:

- **engineering-reviewer** — mechanical correctness: scripts, hooks, plugin/marketplace manifests (incl. version parity), frontmatter, repo structure, security, markdown-as-code.
- **workflow-reviewer** — workflow integrity: documentarian discipline, barriers/checkpoints, research→design→tasks separation, beads-not-TodoWrite, scope control, read-fully protocol.

The two lenses are adversarial and complementary — the worst regressions live on the seam between "the code is fine" and "the prompt still does the right thing."

**Who this skill is for**: wb maintainers checking product quality before merging a PR or shipping a release.

## Activation

Triggered by phrases like:

- "review wb" / "review workbench"
- "run the reviewers" / "run the meta-review"
- "meta-review" / "rerun the meta-review"
- "eval this PR" / "engineering and workflow review of [branch/PR]"
- "re-review against main"
- "check wb quality" / "is this ready to ship?"

## Inputs the Skill Gathers Before Running

Ask the user (or infer from context):

1. **What to review** — one of:
   - A branch name (e.g., `main`, `saskatoon`, `fix/pr2-followup`)
   - A PR number (e.g., "PR #5")
   - A worktree path
   - A commit SHA
2. **Fresh or delta?** — if the same branch/PR was reviewed before, offer a delta that verifies prior findings' status. Otherwise, fresh.
3. **Prior-findings reference** — if delta, where to find the prior report (paste, file path, or chat history).
4. **Scope overrides** — by default both reviewers cover the full tree; allow scoping down (e.g., "only the new skill added in this PR").

If inputs are missing, gather them with brief prompts (or `AskUserQuestion` when available):

1. "What kind of target should I review?" → Branch / PR number / Commit SHA / Worktree path, then a narrow follow-up for the specifier.
2. "Fresh review or delta from a prior review?" → Fresh (baseline triage) / Delta (verify prior findings + surface new issues).
3. If Delta: "Where are the prior findings?" → Paste now / File path / Prior PR comments.

## Core Behavior

### Step 1 — Resolve the Review Scope

Based on the user's input:

- **Branch name**: confirm the branch exists locally or fetch from origin. If it's actively checked out in another worktree, skip checkout; otherwise add a worktree (`git worktree add /tmp/wb-review-<branch> <branch>`) so the review runs against a stable snapshot.
- **PR number**: `gh pr view <N> --json headRefName,headRefOid` to get the branch + SHA, then proceed as above.
- **Commit SHA**: `git worktree add --detach /tmp/wb-review-<sha> <sha>`.
- **Worktree path**: use as-is; confirm it exists and is a git worktree.

Record:

- `REVIEW_PATH` — absolute path the reviewers operate on
- `REVIEW_REF` — the branch/PR/SHA human-readable identifier
- `REVIEW_COMMIT` — the commit SHA the reviewers see

### Step 2 — Confirm Agent Specs Are Accessible

The two review agents live at (relative to the repo root):

- `agents/engineering-reviewer.md`
- `agents/workflow-reviewer.md`

Read these spec files from the checkout this skill runs in (a stable `main` snapshot), NOT from `REVIEW_PATH` — the reviewers operate on `REVIEW_PATH`, but their spec files should be stable across review runs so the spec itself doesn't vary with the branch under review. Derive the repo root at runtime: `REPO_ROOT="$(git -C . rev-parse --show-toplevel)"`, then reference `"$REPO_ROOT/agents/engineering-reviewer.md"` and `.../workflow-reviewer.md`. If either is missing, halt and tell the user to merge the PR that adds them.

### Step 3 — Spawn Both Reviewers in Parallel

Spawn two sub-agents (via the `Agent` / Task tool), one per reviewer, in the SAME message for true parallelism. Each sub-agent's prompt includes:

- Instruction to `Read` its spec file first (`agents/engineering-reviewer.md` or `agents/workflow-reviewer.md`, absolute path).
- `REVIEW_PATH`, `REVIEW_REF`, `REVIEW_COMMIT`.
- Fresh-vs-delta mode. If delta, include the full prior-findings summary with per-item status to verify.
- Scope overrides, if any.
- Output-format instructions (use the spec's Output Format; for delta mode, prepend the Delta section).

Run in the background so the user can do other work while reviews churn. Both reviewers operate READ-ONLY on `REVIEW_PATH` — no file writes outside their reports.

### Step 4 — Collect and Combine Reports

When both reviewers return, build a combined report:

```markdown
# Combined Review Report: <REVIEW_REF>

Commit: <REVIEW_COMMIT>
Generated: <YYYY-MM-DD HH:MM>
Mode: fresh | delta-from-<prior-ref>

## Combined Scorecard

| | Engineering | Workflow |
|---|---|---|
| Critical | N | N |
| Medium | N | N |
| Minor | N | N |
| Notable strengths | N | N |

## Critical Findings (both reviewers)

[merged list — engineering and workflow criticals in severity order]

## Medium Findings (both reviewers)

[merged list — grouped by file path for easy triage]

## Delta from Prior (if delta mode)

Engineering:
  - Prior critical N: ✅ / ⚠️ / ❌
  - ...

Workflow:
  - Prior critical N: ✅ / ⚠️ / ❌
  - ...

## Minor Findings (optional expansion)

[if user asked for full; otherwise summarize counts only]

## Notable Strengths

[merged — what's working well]

## Recommended Priority Order

1. 🔴 fix before merge: [specific items]
2. 🟡 fix before release: [specific items]
3. 🟢 polish / defer: [specific items]

## Version-Bump Check

[engineering-reviewer's version-parity result: if this change touches commands/skills/agents,
confirm plugin.json and marketplace.json versions match AND were bumped — a merge blocker if not]
```

### Step 5 — Offer Next-Step Actions

After the combined report, offer:

- **Open a fix PR** against the reviewed branch/PR — this skill does not write fixes; it can scaffold a follow-up branch.
- **Bump the version** — if the change adds/edits commands, skills, or agents and the version wasn't bumped, bump `plugin.json` and `marketplace.json` together (see `CLAUDE.md` release protocol).
- **Merge the reviewed PR** — if verdict is PASS and the user is satisfied.
- **Re-run later** — if fixes are still pending.

## Delta-Mode Specifics

1. Prior findings may live in chat history, a pasted text, or a file. Accept any format.
2. Extract per-finding identifiers: `file:line` + severity + one-sentence description.
3. Include the full prior-findings list in each sub-agent's prompt with instructions to mark each ✅ RESOLVED / ⚠️ PARTIAL / ❌ NOT RESOLVED in the Delta section.
4. Also ask each sub-agent to surface NEW findings introduced since the prior review (especially regressions caused by fix attempts).

## Fresh-Mode Specifics

1. Both reviewers produce their full Output-Format report.
2. The combined report's Delta section is skipped; only the scorecard, severity-grouped findings, and strengths appear.
3. Optionally save the reports (paste in chat or `docs/reviews/YYYY-MM-DD-<ref>.md`) so the next pass can run as delta.

## Operating Rules

- **Parallelism**: always spawn both reviewers in the SAME tool-call batch for true parallel execution.
- **Background**: run reviews in the background — they're long; don't block the user.
- **Worktree hygiene**: prefer a new worktree per review over branch-switching the main checkout; clean up worktrees this skill created (`git worktree remove`).
- **No file writes during review**: the sub-agents are read-only. Fixes are a separate follow-up.
- **Absolute paths**: give sub-agents absolute paths to both the spec file AND the review target.
- **Stable spec authority**: read the review specs from the current (main) checkout, not from the branch under review, so the spec is stable across runs.
- **Version gate**: never wave through a PR that adds/edits commands, skills, or agents without a matching version bump in both manifests.

## What This Skill Does NOT Do

- ❌ Does not write fixes — that's a follow-up, separate action.
- ❌ Does not modify any files during the review.
- ❌ Does not evaluate end-user project docs (research.md/design.md/tasks.md) — it evaluates the wb product itself. (Validating end-user artifacts is `/wb:validate_project` and the `research-validation` skill.)
- ❌ Does not replace human maintainer judgment — the reviewers are advisory; the maintainer decides what merges.

## Relationship to Other Skills & Agents

- Uses (not installs): `engineering-reviewer`, `workflow-reviewer` agents at `agents/`.
- Distinct from: `validate_project` / `validate_execution` / `research-validation` — those validate an END-USER's project artifacts; this reviews the wb PLUGIN itself before release.
- Called from: maintainer workflows before merging a PR or shipping a version bump.

## Invocation History (append as runs happen)

Each review run can optionally log itself here for future delta reference:

```
- YYYY-MM-DD HH:MM  review <REVIEW_REF> at <REVIEW_COMMIT> — fresh | delta
  engineering: <critical>/<medium>/<minor>
  workflow: <critical>/<medium>/<minor>
  verdict: PASS | PASS WITH ISSUES | FAIL
```

(Keep this log short; trim older entries periodically.)
