# implement — reference

Read this when a step directs you to.

## Evolution from implement_inline

This skill evolves `implement_inline` with one key improvement:

- **Coordinator Pattern**: Main agent orchestrates, workers implement in fresh context
- **Context Efficiency**: Main window stays clean, workers are ephemeral
- **Sequential Execution**: Simple, predictable, no coordination complexity
- **Fresh Context**: Each task starts with clean slate, no accumulation

**All learnings preserved:**

- ⛔ BARRIER synchronization points
- TDD cycle enforcement (Red → Green → Refactor)
- Checkbox state in `tasks.md` as the single status surface
- ZERO SCOPE CREEP discipline
- Phase boundary verification
- Manual verification checkpoints

## Resume Logic

When resuming work (phase = "continue"), `tasks.md` tells you where you are — there is no
separate tracker to reload.

1. **Read `tasks.md` FULLY.** The first `- [ ]` task in the current phase is the next task.

   ```bash
   grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # completed
   grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # remaining
   ```

   Scoped to lines carrying a task ID — the criteria checkboxes are not tasks, and counting
   them manufactures drift against the counters.

   If the frontmatter counters disagree with these counts, the checkboxes are right and the
   counters are stale.

2. **Inspect the working tree before anything else.**

   ```bash
   git status --short
   ```

   Uncommitted changes here mean a previous worker returned but its task was never committed —
   so verification or the commit did not happen. Diagnose it with Step 6's discrimination
   before spawning anything new; re-spawning over a half-finished tree is how one truncation
   becomes two.

3. **Read the journal tail.** An **open** entry in `journal.md` names what the previous session
   was attempting and the next action it intended.

4. **Review context**: tasks.md Implementation Notes, research.md, design.md, and
   `.claude/wb/knowledge.md` if present. A remediation plan (recognise one by a `reviews:` key
   in its frontmatter or a `reviews/<date>-round-N/` path) has no research.md or design.md —
   tasks.md alone is the whole plan.

5. **Continue coordination**: extract the context package, take the next unchecked task, spawn.

## Advantages Over Sequential Implementation

### Context Efficiency (PRIMARY BENEFIT)

**Sequential** (`implement_inline`):

```
Main context grows: Research + Design + Task1 + Task2 + Task3 + ...
Token usage: Linear growth, can exhaust window, requires compaction
```

**Coordinated** (`implement`):

```
Main context: Research + Design + Coordination logic (stays constant)
Worker contexts: Minimal context per task (ephemeral, discarded after completion)
Token usage: Main stays constant, workers are isolated
```

**Result**: No context accumulation in main session, no need for compaction

#### Why this matters: the ~75k "smart zone"

Models do their best work inside a bounded working context — empirically a
"smart zone" of roughly **75k tokens**. Past that, recall and reasoning degrade
well before the hard context limit is reached. The coordinator/fresh-worker
split exists to keep the main session inside that zone: the coordinator holds
only research + design + coordination logic (constant), and each worker starts
fresh and is discarded, so neither accumulates toward the degradation cliff.

This is the same backpressure principle that governs runtime tool output
(see `scripts/quiet` and the `tdd-discipline` GREEN step): every token that
conveys nothing — a 200-line all-green test run, a finished task's transcript —
is a token stolen from the smart zone. Architecture (fresh workers) handles the
*accumulated* context; output backpressure handles the *per-iteration* context.
Both serve the same budget.

> Source: humanlayer, "context-efficient backpressure" —
> <https://www.humanlayer.dev/blog/context-efficient-backpressure>.
> The article's own thesis (human time costs ~10x tokens; over-conservative
> models waste more via re-runs) is why this reduces cost without trading away
> reliability — failures still surface in full.

### Error Isolation

**Sequential**: Error in Task 3 pollutes context for Tasks 4, 5, 6...

**Coordinated**: Error in Worker 3 isolated, doesn't affect Workers 4, 5, 6

- Fresh start for each task
- Failures are localized

### Model Selection

**Sequential**: All tasks use the session model

**Coordinated**: right tier per task, chosen by coordinator judgment over the task's content.
The ladder is stated once, in SKILL.md Step 5 — this section does not restate it.

## Migration from implement_tasks

To migrate existing projects:

1. **No changes needed to documentation structure** (research.md, design.md, tasks.md)
2. **Switch command**: use `/wb:implement` instead of `/wb:implement_coordinated`
   (`/wb:implement_inline` is the renamed `implement_tasks`, and still runs inline)
3. **Existing plans written against a tracker**: their beads IDs no longer resolve. Checkbox
   state in `tasks.md` is authoritative; run `/wb:update_status` once to reconcile the
   frontmatter counters against it.

Both paths produce identical results. The coordinated version keeps the main session context
clean.

## Important Guidelines

### DO

- ✅ Extract minimal context packages for workers
- ✅ Spawn workers sequentially (one at a time)
- ✅ Choose the tier by judgment over the task's content, per Step 5's ladder
- ✅ Wait for each worker to complete before next
- ✅ Inspect the working tree before diagnosing any incomplete worker
- ✅ Commit each task yourself, after its verifier passes
- ✅ Aggregate worker outputs thoroughly
- ✅ All `implement_inline` best practices

### DON'T (ABSOLUTELY FORBIDDEN)

- ❌ All prohibitions from `implement_inline`
- ❌ **NEVER** spawn multiple workers in parallel (keep it simple)
- ❌ **NEVER** allow workers to add scope
- ❌ **NEVER** pass entire docs to workers (extract context)
- ❌ **NEVER** proceed without waiting for worker completion
- ❌ **NEVER** skip worker output aggregation
- ❌ **NEVER** retry a whole task with the same context — same task plus same context spends the same budget and truncates at the same point
- ❌ **NEVER** escalate more than once on a verified failure; the second attempt goes to the phase checkpoint's blocking list instead
- ❌ **NEVER** let a worker commit; the coordinator commits after verification, and that is what makes an unfinished task detectable
- ❌ **NEVER** declare a phase complete while any of its checkboxes is `[ ]`

## Why the Step 6 and Step 8 rules are shaped this way

`SKILL.md` carries the instruction; the reason lives here. The full evidence, with dates and
measurements, is in the 2026-09-08 upstream-fable-merge plan's Implementation Notes.

- **The `--auto` paragraph names no positional placeholder.** The harness substitutes
  placeholder values into skill text, so a sentence naming the first placeholder read back as
  "strip the flag before binding `<the directory>`" — circular, and legible only when the
  binding already worked. The binding really did fail once: `/wb:implement --auto <dir>` bound
  the flag as the directory.
- **6c resets the checkbox before escalating** because the worker flips it as its final act,
  before verification. Without the reset, 6a cannot tell a truncated escalation attempt from a
  finished one.
- **6c ends with a clean tree** because a blocked task's leftovers make the next worker's
  "did nothing" look like substantial changes — misdiagnosed as truncation — and make its
  verifier fail it for files it never opened.
- **The attestation stays unticked under `--auto`.** A run that ticked "Manual verification
  confirmed by human" on its own authority would make every finished plan assert a sign-off
  that never happened — the pre-printed-✅ template defect reintroduced systematically. Leaving
  it `[ ]` keeps "unattended" and "approved" distinguishable when the plan is the only witness.
- **The final-phase statement** exists because an unattended run always ends at
  `status: in-progress`: `complete` is a claim, gated by `update_status`'s barrier, and a user
  not told this discovers a plan that looks unfinished.
- **The `update_status` box is ticked after Step 9 runs it, not at Step 8**, because ticking it
  first asserts something not yet done — the attestation error in miniature.

## Configuration

This skill coordinates task implementation using sequential worker agents with focused context. It preserves all disciplines from `implement_inline` while keeping the main session context clean.

**Recommended for**: Long phases with many tasks, sessions where context compaction would be disruptive, or when you want the main window available for monitoring/debugging.
