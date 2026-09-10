---
project: wb 2.0.0 tracker-free modernization
plan: docs/plans/2026-09-08-upstream-fable-merge/
created: 2026-09-10
status: blocked-on-verification
git_branch: thescubageek/gabe-fable-merge-research
git_commit: 7d155de
current_phase: 4
total_tasks: 64
completed_tasks: 63
---

# Handoff: wb 2.0.0, held one task short of the tag

## Start here — there is work in flight you did not start

**A separate Claude testing session is running a four-item follow-up right now. Evaluating its
results is your first step. Do not begin anything else, and do not re-run its items yourself —
you would be racing it.**

Ask the user for that session's output before doing anything. If it has not finished, wait or
ask them to paste what it has so far. Everything below is context for reading that output
correctly; none of it is a task to pick up cold.

The four items, in the order the follow-up puts them:

1. **The release blocker** — can a *marketplace-installed* 2.0.0 read its own supporting files?
2. **Re-run the D8 bootstrap check** against a journal created after `5fb7025`.
3. **Close out the slugify run's Phase 2 checkpoint**, including the early-return decision.
4. **Spot-checks**: `/compact` recovery text, the three deprecated aliases, `explore_design`.

## Where the work stands

63 of 64 tasks are done and committed. Working tree is clean at `7d155de`. The one unchecked
task is **`P4-T10`** — `claude plugin tag plugin/`, which creates `wb--v2.0.0` — and it is held
on purpose, not forgotten.

Tagging and pushing are outward-facing. They need the user's explicit go-ahead regardless of
how item 1 comes back.

## The release blocker, in full

D2 converted every command monolith into `SKILL.md` plus supporting files that skills read **on
demand**. That is what produced the headline result: fourteen-stage on-invoke context went
**84.9k → 46.8k tokens, −44.9%**, against a bar of ≤59.4k.

The whole result depends on those on-demand reads succeeding.

- Under `--plugin-dir`, supporting files sit **inside** the working directory. Reads succeed.
- Installed from the marketplace, they sit in `~/.claude/plugins/cache/<marketplace>/wb/<version>/skills/...`
  — **outside every working directory.**

With `permissions.blockReadsOutsideWorkingDirectories: true` (which the user has set in their
own `~/.claude/settings.json`), that second read may be blocked. If it is, progressive
disclosure is broken for every installed copy — which is every copy except this development
checkout — and it fails *quietly*: the skill just runs on whatever `SKILL.md` alone carries.

**Every read test so far used `--add-dir` or a `--plugin-dir` checkout.** None of them
exercised the installed path. That is precisely why this is still open: the passing tests do
not cover the failing case. The follow-up's item 1 opens by asking whether `/add-dir` was used,
because if it was, that session's result is void.

**If item 1 is clean**: tag `wb--v2.0.0`, with the user's go-ahead.
**If item 1 is blocked**: stop. This is a design problem, not packaging. Candidate directions —
inline supporting content back into `SKILL.md` (surrenders most of the −44.9%), ship a
postinstall that copies into the project, or document an `additionalDirectories` requirement as
an install step. They differ enough that the failure mode should pick between them. Do not pick
one before seeing how it fails.

## What "verified" has meant on this plan, and why to distrust it

Three times, something was confirmed by a grep or a shape check and was still wrong. The most
expensive was the journal bug: `P2-T5`'s template wrote its example entries as **live `##`
headings**, and the session-start hook matches the first `##` as the most recent entry. The
example ends in `(open)`, so *every generated plan reported a phantom interrupted task from the
moment it was created*. The template linted clean. The hook exited 0. The matcher matched. The
feature was inverted, and only an end-to-end run caught it. Fixed in `5fb7025`.

Read the four items in that light. "The grep returns nothing" is not a pass for any of them.
Item 2 exists specifically because the *first* D8 verification was a shape check.

Also inherited, and worth keeping: **when several consumers agree on a format, something must
state it and something must check it.** Several bugs here were two readers quietly disagreeing.

## Found while writing this handoff — read before judging item 2

`journal.md` **had never been committed.** It sat on disk, gitignored and untracked, from
creation until `fbf6532`. Fixed there; all plan files are tracked now.

This narrows a result you will otherwise misread. The D8 acceptance test reported "recovery
worked" — and it did, *on the same machine, off the local disk*. A fresh clone or the user's
second machine would have found no journal at all, which is the cross-machine case D8 was
written for. The mechanism is sound. Its durable copy did not exist.

The cause is structural, not a slip: plans are gitignored until promoted, promotion is a
**one-time** `git add -f` over the files that exist at that moment, and `journal.md`,
`handoff-*.md` and `thoughts/` all appear afterward. `git status` never lists ignored files, so
this class of omission is invisible unless asked for directly:

```bash
git ls-files --others --ignored --exclude-standard docs/plans/<dir>/
```

Run that before any handoff or push. Clean across all plans as of `ccc21ec`.

## Decisions already made — do not reopen

- **D13 / the worker tier ladder.** `agents/task-worker.md` deliberately carries **no `model:`**
  so the tier is chosen per spawn. `ac950ed` restated the ladder in values the Task tool's enum
  actually accepts. This churned three times; it is settled.
- **The one tier-rule statement** is found by `grep -rln 'the one statement of the worker tier
  rule' plugin/skills/` → exactly 1. It is anchored to that self-describing marker rather than
  to a model ID, because pinning it to `claude-opus-4-8[1m]` broke within the hour.
- **The deprecated aliases stay** (`create_execution`, `implement_coordinated`,
  `implement_tasks`) — stubs only, no pointers, `disable-model-invocation: true`.
- **Task IDs must contain a digit** — `[A-Z0-9-]*[0-9][A-Z0-9-]*`. A permissive pattern once
  matched `**End-to-end**` and reported 65 tasks out of 64.
- **The three-session canary is explicitly not needed.** This run plus the hardening exceeds it.
- **D20: follow-ups, not fixes.** Out-of-scope discoveries get filed in Implementation Notes.
  A worker on this plan measured that some code was dead, then correctly declined to delete it.

## Orientation for a cold session

Run the session-start hook and read what it prints — it is the intended entry point and it
works:

```bash
echo -n '{"hook_event_name":"SessionStart","source":"startup"}' | ./plugin/hooks/wb-prime.sh
```

Then read, in order: `docs/plans/2026-09-08-upstream-fable-merge/tasks.md` (checkboxes are the
source of truth; the Implementation Notes at the bottom carry every deviation and finding),
`journal.md` (top entry is open and describes this hold), and `.claude/wb/knowledge.md`.

One known quirk: the hook will warn that the top journal entry is open beside a clean tree, and
read that as a missed close-out. Here it means work is in flight **in another session**, which
the working tree cannot observe. Filed as a follow-up in Implementation Notes.

## Suggested settings

`claude-opus-5[1m]`. Item 1 may turn into a design decision under a shipped-artifact constraint,
and items 2–4 are verification work where the failure mode is accepting a weak pass.
