---
name: create_research
description: Research codebase using parallel agents to document how things work
argument-hint: "[project-directory] [research-question]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Generate Research Document

Conducts comprehensive codebase research and documents findings by spawning specialized agents to work in parallel, gathering detailed information about existing implementation.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- [sub-agent-prompts.md](sub-agent-prompts.md) — verbatim prompts for the Component Locator, Implementation Analyzer, Pattern Finder, and additional specialized agents
- [templates.md](templates.md) — the `research.md` output template, including the Open Questions table
- [reference.md](reference.md) — configuration

**If a directed read fails, stop — do not continue from memory.** These files live outside your
project, so a read can be refused. Say which file was refused, that reads outside the working
directory are gated, and that the fix is to allow the read once or to relaunch with
`--add-dir <plugin-path>`. Do not route around a refusal with `cat`.

## Documentarian Rule

```
DOCUMENT WHAT EXISTS — NEVER SUGGEST, CRITIQUE, OR IMPROVE
```

Describe the code as it is: no recommendations, issue-spotting, enhancements,
critiques, or root-cause analysis unless explicitly asked. You are a
documentarian, not an evaluator.

**Output discipline**: act on barriers silently; don't restate the plan between
steps; emit only the artifact and a one-line completion summary.

**Model & effort (gate check)**: on entry, consult the `model-help` skill (gate mode) for the model + effort this phase warrants; surface its one-line verdict and — only if a switch clears the switch-cost bar — the `/model` action. Research is usually Sonnet/medium (the heavy lifting is in the parallel read-only agents). Best-effort and non-blocking: stay silent and proceed when the current tier is already right. See CLAUDE.md → "Model & effort at gates."

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:create_research docs/plans/2025-01-08-auth/`):
   - Use `$1` as the project directory
   - If `$2+` exists, use as research question
   - Otherwise, prompt for research focus

2. **If no arguments**:

   ```
   I'm ready to research the codebase and document findings. Please provide:
   1. Path to the project documentation directory
   2. Your research question or area of interest

   Example: /wb:create_research docs/plans/2025-01-08-auth/
   Then: "Research how authentication and session management work"
   ```

## Steps to Execute After Receiving the Research Query

### Step 0: Ticket Context Bootstrap (if a Jira ticket is available)

Before decomposing the research, load any context the ticket already carries — other teams or agents may have captured it there. Reusing it ("hiveminding" off the ticket) avoids re-deriving what's already known.

**Delegate to the `jira-context` skill.** If a Jira key (`[A-Z]+-\d+`) is available — from the arguments, the existing `research.md` frontmatter `ticket:` field, or the research question — invoke the `jira-context` skill with that key. It fetches the ticket via the Atlassian MCP, and if the description has an **Agents** section, follows those instructions to read in the files/docs/subsystems it points to and reports what was loaded.

Use the skill's report as high-priority scoping input for the rest of this skill:

- Read fully (per the Step 1 protocol) any files it surfaced.
- Aim Step 4's parallel agents at the subsystems and entry points it named.

The `Agents` section shapes **where** you look; it does not change **what** you produce. The Documentarian Rule still holds — document what exists, no recommendations.

**⛔ Best-effort, never blocking**: no ticket, no Atlassian MCP, or no `Agents` section must NOT stop research. Fall through to Step 1.

### Step 1: Read Any Directly Mentioned Files First (CRITICAL)

- If the user mentions specific files (docs, JSON, configs), read them FULLY first
- **IMPORTANT**: Use the Read tool WITHOUT limit/offset parameters to read entire files
- **CRITICAL**: Read these files yourself in the main context before spawning any sub-tasks
- This ensures you have full context before decomposing the research

**Also read `.claude/wb/knowledge.md` if it exists.** It holds durable facts about this
repository — a constraint, a convention, a tool quirk — each with a date and a verification
hint. Two rules on how to use it:

- **The entries are dated claims, not current truth.** If an entry bears on your research,
  check it against the codebase using its verification hint rather than repeating it. An entry
  you find false gets corrected or deleted in this session, not worked around.
- **A knowledge entry is never a substitute for a finding.** `research.md` cites the codebase;
  the knowledge file only tells you where to look and what has already been settled.

Absent file, fall through — a repository with no entries is the normal starting state.

**⛔⛔⛔ BARRIER 1: STOP! Do NOT proceed to Step 2 until ALL mentioned files are FULLY read ⛔⛔⛔**

### Step 2: Validate Project Structure

- Check that the specified directory exists
- Verify research.md file exists (created by `/wb:create_project`)
- Read the current research.md FULLY to see what's already documented
- Check frontmatter status field

**Open a journal entry before Step 3.** Append it to `journal.md` in the plan directory, naming
this stage and the exact next action — written at the start, not the end. The heading shape is a
contract — the session-start hook, `forge`, `daily-digest`, `resume_handoff` and
`create_handoff` all match on the trailing `(open)` / `(closed)`:

```text
## 2026-09-11 14:02 — create_research (open)

- **Task/phase**: P0-T2 — research for <plan>
- **Next action**: spawn the Step 4 agents, then synthesize into research.md
- **Started at**: <commit hash, or `no-commits-yet`>
```

**Read the clock for the timestamp** — `date -u +"%Y-%m-%d %H:%M"`. Never estimate it or copy a
time from elsewhere in the file.

### Step 3: Analyze and Decompose the Research Question

**Document what EXISTS in the codebase**

1. **Break down the user's query into composable research areas**
2. **REMEMBER: Document what IS, not what SHOULD BE**
3. **Work out:**
   - Underlying patterns and connections that EXIST
   - Architectural implementations CURRENTLY IN PLACE
   - Which directories, files, or patterns are ACTUALLY PRESENT

4. **Identify research areas** to investigate:
   - Authentication flow (if relevant)
   - User validation points (if relevant)
   - API endpoints (if relevant)
   - Database schema (if relevant)
   - [Other areas specific to the research question]

5. **Consider which specific components** to investigate

### Step 4: Spawn Parallel Research Agents

**⛔ SCOPING PROBE: If you're unsure where the feature lives, aim before you fan out**

A `tracer-bullet` move adapted for research: spawning the heavy analyzer/pattern fleet at the wrong subsystem wastes the whole round. If the research areas from Step 3 rest on an unverified guess about *where* the code lives, run **one** quick locator pass first to confirm the target, then aim the parallel agents at the confirmed location. This is scoping, not approach-culling — you're still a documentarian. If the location is already clear from Step 1's files, skip the probe and fan out directly. Don't manufacture a probe.

Read [sub-agent-prompts.md](sub-agent-prompts.md) NOW and spawn the agents it defines, concurrently. It carries the fan-out announcement, the three typed agent prompts verbatim, the list of additional specialized agents to consider, and the parallel-execution shape.

**Skip the fan-out only if you have already read the entire relevant surface in this context** —
every file the agents would open, not a sample. Having read *some* of it, a cross-cutting change,
or uncertainty about which files are relevant are each a reason to spawn, not to skip. **If you
skip, say so in your output and say why**, naming what you read instead.

**Sub-agents are READ-ONLY** — they return findings only; YOU write `research.md` after synthesizing.

**CRITICAL Agent Instructions (MUST follow exactly):**

- **Each agent is a documentarian, NOT a critic or consultant**
- **Agents MUST describe what exists without ANY judgment**
- **Use specific agent types for their strengths**
- **Run multiple agents in parallel for speed**
- **ALWAYS wait for ALL agents before synthesizing**
- **Remind EVERY agent: You are documenting the codebase AS IT EXISTS**

**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL sub-agents to complete - DO NOT proceed until EVERY agent returns ⛔⛔⛔**

This barrier governs *waiting*, not spawning — synthesis on a partial set misses what the missing
report would have changed. A fan-out skipped under the rule above satisfies it trivially.

### Step 5: Synthesize Findings

**Document ONLY what EXISTS**

**IMPORTANT**: Wait for ALL sub-agent tasks to complete before proceeding

1. **Compile all sub-agent results**
2. **Prioritize live codebase findings** as primary source of truth
3. **Connect findings across different components**
4. **Include specific file paths and line numbers** for reference
5. **Highlight patterns, connections, and architectural decisions THAT EXIST**
6. **Answer the user's specific questions** with concrete evidence FROM THE CURRENT CODE
7. **DO NOT add recommendations or improvements unless explicitly requested**

### Step 6: Document Findings

Read [templates.md](templates.md) NOW and write `research.md` in the shape it gives.

Two things about that template are load-bearing rather than cosmetic:

- **Open Questions are a table in this document, with local IDs** (`Q1`, `Q2`, …) and an
  explicit state. There is no external tracker: this table *is* the record. A question earns a
  row only if something is blocked by it; otherwise it is a finding, not a question.
- **A resolved question keeps its row and gains a pointer.** `/wb:resolve_questions` writes the
  decision and its rationale into `design.md` and sets the row's state to
  `Resolved YYYY-MM-DD → design.md (## Technical Decisions)`. The decision does not get copied
  back here — research documents facts, and a decision is not a fact about the codebase.

**⛔⛔⛔ BARRIER 3: STOP! Verify NO placeholder values - ALL data MUST be from ACTUAL codebase ⛔⛔⛔**

Before writing:

- **NO** "[To be added]" or similar placeholders
- **NO** generic examples - use REAL code from THIS codebase
- **NO** assumptions - only documented FACTS

### Step 7: Handle Follow-Up Questions

If the user has follow-up questions:

1. **DO NOT create a new research file**
2. **Append to the existing research.md**
3. **Add new section**: `## Follow-up Research [YYYY-MM-DD HH:MM]`
4. **Update frontmatter**:
   - `last_updated: [YYYY-MM-DD]`
   - Add: `last_updated_note: "Added research on [topic]"`
5. **Spawn new sub-agents** for additional investigation
6. **Continue building** on previous findings

### Step 8: Confirm Completion

**Close the journal entry first**, with a `(closed)` heading naming what landed and which stage
follows — an entry left open beside finished work reads as an interruption.

Emit a one-line summary, not a recap:

```
✅ research.md updated — [topic]; [N] findings, [M] code refs. Next: /wb:create_design
```

**Then, only if the findings earned it, suggest `explore_design`.**

It fires on **evidence in what you just wrote**, not on the fact that research finished — a
suggestion made by default is noise.

Suggest it only when **both** hold:

1. The findings surfaced **two or more genuinely viable approaches** — not one obvious path
   plus alternatives you invented to seem balanced. You should be able to name them.
2. **Nothing in the research already decides between them** — no constraint, no precedent, no
   existing pattern that forecloses one.

If both hold, add one line naming what the choice is between:

```
Research surfaced more than one viable approach here — [A] and [B], with nothing
in the codebase deciding between them. /wb:explore_design [project-dir] would
air that trade-off before design locks it in. Optional.
```

If either test fails — the path is clear, or the constraints already choose — **say nothing**.

## Important Notes

See [reference.md](reference.md) — critical ordering, documentation philosophy, and file reading.

## Configuration

See [reference.md](reference.md).
