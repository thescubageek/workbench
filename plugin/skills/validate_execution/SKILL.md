---
name: validate_execution
description: Validate that execution plan was correctly implemented and verify all success criteria
argument-hint: "[project-directory]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Validate Execution

Validates that an execution plan was correctly implemented, verifying all success criteria and identifying any deviations, gaps, or issues.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- [sub-agent-prompts.md](sub-agent-prompts.md) — the four Step 2 validation agents
- [templates.md](templates.md) — the validation report
- [reference.md](reference.md) — validation philosophy, PASS/FAIL criteria, the common-checks list, workflow position, configuration

**If a directed read fails, stop — do not continue from memory.** These files live outside your
project, so a read can be refused. Say which file was refused, that reads outside the working
directory are gated, and that the fix is to allow the read once or to relaunch with
`--add-dir <plugin-path>`. Do not route around a refusal with `cat`.

**Model & effort (gate check)**: on entry, consult the `model-help` skill (gate mode) for the model + effort this phase warrants; surface its one-line verdict and — only if a switch clears the switch-cost bar — the `/model` action. Baseline is Sonnet/medium, rising to Opus/high when the change has wide blast radius, is compliance/security-sensitive, or is hard to verify (mistakes hide until prod) — adversarial checking of sensitive code earns the higher tier. Best-effort and non-blocking: stay silent and proceed when the current tier is already right. See CLAUDE.md → "Model & effort at gates."

## Purpose

This command provides an objective assessment of implementation completeness by:

- Verifying claimed completions match actual code changes
- Running all automated verification checks
- Identifying deviations from the plan
- Documenting gaps or issues found
- Providing clear manual testing requirements

Run this AFTER implementation to ensure quality before merging or deployment.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:validate_execution docs/plans/2025-01-08-my-project/`):
   - Use `$1` as the project directory
   - Read all documentation immediately
   - Begin validation process

2. **If no arguments**:

   ```
   I'll validate the execution of your implementation plan. Please provide:
   1. Path to the project documentation directory (e.g., docs/plans/2025-01-08-my-project/)

   I'll verify that the implementation matches the plan and all success criteria are met.
   ```

## Process Steps

### Step 1: Context Discovery

**⛔⛔⛔ BARRIER 1: STOP! Read ALL documentation FULLY - research.md, design.md, tasks.md ⛔⛔⛔**

Take the project directory from the arguments, prompting for it if it is missing. Then read
`research.md`, `design.md` and `tasks.md` from that directory — **fully**, no `limit` or
`offset`.

1. **Read tasks.md completely** to understand:
   - What phases were planned
   - Success criteria for each phase
   - Modified files listed
   - **Which tasks are claimed complete** — the `[x]` checkboxes. There is no external tracker;
     `tasks.md` is where completion is recorded.

2. **Treat the checkboxes as claims, not as findings.**

   This is the distinction the whole skill turns on. Checkbox state is the source of truth for
   *what the plan says was done* — it is the record, and nothing else holds that record. It is
   **not** evidence that the work happened. Your job is to test the claim against the code.

   ```bash
   grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # tasks claimed complete
   grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md    # tasks claimed outstanding
   ```

   Scoped to lines carrying a task ID: this document's own success criteria are checkboxes,
   and they are what you are validating *with*, not claims to validate.

   Two failure directions, and both matter:

   - **A `[x]` with no corresponding code** — a false completion. This is the one that ships
     broken work, because every later phase built on the assumption it was done.
   - **A `[ ]` whose work is plainly in the code** — an unrecorded completion. Less dangerous,
     but it means the next session redoes finished work, and the counters understate progress.

   Also compare the frontmatter counters against the counts above. A mismatch means
   `/wb:update_status` has not run since the last task — worth noting in the report, but not
   yours to fix here.

3. **Read design.md** to understand:
   - Original design decisions
   - Success metrics defined
   - Scope boundaries

4. **Read research.md** to understand:
   - Original state of the codebase
   - Patterns that should be followed

**Compare what was supposed to be built against what exists**

### Step 2: Spawn Validation Agents

**Use parallel agents to verify implementation comprehensively.**

Read [sub-agent-prompts.md](sub-agent-prompts.md) NOW and spawn the four agents it defines, concurrently.

**Skip the fan-out only if you have already read the entire relevant surface in this context** —
every file the agents would open, not a sample. Having read *some* of it, a cross-cutting change,
or uncertainty about which files are relevant are each a reason to spawn, not to skip. **If you
skip, say so in your output and say why**, naming what you read instead.

**CRITICAL: Sub-agents gather information and return findings. They do NOT write files. YOU (the main agent) will write the validation report after synthesizing their findings.**

**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL validation agents to complete ⛔⛔⛔**

This barrier governs *waiting*, not spawning — synthesis on a partial set misses what the missing
report would have changed. A fan-out skipped under the rule above satisfies it trivially.

### Step 3: Run Automated Verification

For each phase in tasks.md, run ALL automated verification commands:

```bash
# Common verification commands (adapt based on project)
make check      # Linting and formatting
make test       # Unit tests
make integration # Integration tests
make build      # Build verification

# Project-specific commands from tasks.md
[Run any specific commands listed in success criteria]
```

Document the results:

- ✅ Pass: Command succeeded
- ❌ Fail: Command failed (include error)
- ⚠️ Partial: Some issues but not blocking

### Step 4: Analyze Implementation Completeness

**Identify the gaps between plan and reality**

For each phase in tasks.md:

1. **Test every completion claim against the code**:
   - For each task marked `[x]`, find the evidence — the code, the test, the commit. Cite it as
     `file:line`. A claim you cannot evidence is a finding, not an oversight.
   - For each task still `[ ]`, check whether the work is in fact present. If it is, say so —
     the record is wrong in the other direction.
   - Git is the corroborating record: one task, one commit, so the log should show a commit per
     completed task. A phase whose tasks are all `[x]` with no commits behind them is exactly
     the pattern worth flagging.

2. **Verify success criteria**:
   - Were all automated criteria met?
   - Are manual criteria ready for testing?
   - Any criteria impossible to verify?

3. **Identify deviations**:
   - Changes made differently than planned
   - Additional changes not in plan
   - Planned changes not implemented

4. **Assess impact**:
   - Are deviations improvements or problems?
   - Do they affect the overall solution?
   - Should they be documented or reverted?

### Step 5: Generate Validation Report

**⛔⛔⛔ BARRIER 3: STOP! No placeholders in the report — every file:line, metric, test result, and status must come from real tool output (agent findings, checkbox state, verification runs). Omit or mark `unverified` rather than inventing a value. ⛔⛔⛔**

Read [templates.md](templates.md) NOW and write the report in the shape it gives.

### Step 6: Update Documentation

If validation passes with minor issues:

1. **Correct the record where you proved it wrong.** A task you evidenced as complete but left
   `[ ]` gets flipped to `[x]`; a task marked `[x]` that you could not evidence gets flipped
   back to `[ ]` **and** named in the report's Issues section — silently unchecking it would
   lose the finding. Then run `/wb:update_status` so the counters follow.
2. Document any approved deviations
3. Note lessons learned for future projects

If validation fails:

1. Clearly mark which tasks need completion
2. Provide specific guidance for fixes
3. Re-run validation after fixes

## Important Guidelines

See [reference.md](reference.md) — validation philosophy, what makes a PASS vs FAIL, the common-checks list, this skill's place in the workflow, and configuration.
