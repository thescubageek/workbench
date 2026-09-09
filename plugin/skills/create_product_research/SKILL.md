---
name: create_product_research
description: Research codebase from a product perspective - features, user flows, behaviors, and patterns
argument-hint: "[project-directory] [research-question]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Generate Product Research Document

Conducts comprehensive codebase research and documents findings from a **product manager's perspective** by spawning specialized agents to work in parallel. Produces a three-layer document: product overview, engineering approach, and technical appendix.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- [reference.md](reference.md) — the **Audience: Product Managers** rules (read before Step 3 and again before Step 5 — they are what makes this skill different from `create_research`), workflow position, important notes, configuration
- [sub-agent-prompts.md](sub-agent-prompts.md) — verbatim prompts for the Component Locator, Product Behavior Analyzer, Pattern Finder, additional specialized agents, and the Step 7 validator
- [templates.md](templates.md) — the `product-research.md` output template, including the Open Questions table

**If a directed read fails, stop — do not continue from memory.** These files live in the plugin
directory, which is outside your project, so a read of one can be refused. Say which file was
refused, that reads outside the working directory are gated, and that the fix is to allow the
read once or to relaunch with `--add-dir <plugin-path>`. Writing the artifact from this manifest
alone produces a plausible document that was never based on the template — the exact failure the
sentence above exists to prevent. Do not route around a refusal with `cat`.

## Documentarian Rule

```
DOCUMENT WHAT EXISTS — NEVER SUGGEST, CRITIQUE, OR IMPROVE
```

Describe the code as it is: no recommendations, issue-spotting, enhancements,
critiques, or root-cause analysis unless explicitly asked. You are a
documentarian, not an evaluator.

**Output discipline**: act on barriers silently; don't restate the plan between
steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:create_product_research docs/plans/2025-01-08-auth/`):
   - Use `$1` as the project directory
   - If `$2+` exists, use as research question
   - Otherwise, prompt for research focus

2. **If no arguments**:

   ```
   I'm ready to research the codebase from a product perspective. Please provide:
   1. Path to the project documentation directory
   2. Your research question or area of interest

   Example: /wb:create_product_research docs/plans/2025-01-08-auth/
   Then: "Research how user authentication works from a product perspective"
   ```

## Steps to Execute After Receiving the Research Query

### Step 1: Read Any Directly Mentioned Files First (CRITICAL)

- If the user mentions specific files (docs, JSON, configs), read them FULLY first
- **IMPORTANT**: Use the Read tool WITHOUT limit/offset parameters to read entire files
- **CRITICAL**: Read these files yourself in the main context before spawning any sub-tasks
- This ensures you have full context before decomposing the research

**Also read `.claude/wb/knowledge.md` if it exists.** It holds durable facts about this
repository — a constraint, a convention, a tool quirk — each with a date and a verification
hint. Reading it here is what stops this session rediscovering what an earlier one already
established. Two rules on how to use it:

- **The entries are dated claims, not current truth.** If an entry bears on your research,
  check it against the codebase using its verification hint rather than repeating it. An entry
  you find false gets corrected or deleted in this session, not worked around.
- **A knowledge entry is never a substitute for a finding.** `product-research.md` cites the
  codebase; the knowledge file only tells you where to look and what has already been settled.

Absent file, no problem — it is created on first use, so a repository with no entries is the
normal starting state. Fall through.

Also read [reference.md](reference.md)'s **Audience: Product Managers** section now. Everything
after this point is shaped by it.

**⛔⛔⛔ BARRIER 1: STOP! Do NOT proceed to Step 2 until ALL mentioned files are FULLY read ⛔⛔⛔**

### Step 2: Validate Project Structure

- Check that the specified directory exists; if not, create it
- Check if product-research.md exists (may be a follow-up)
- If it exists, read it FULLY to see what's already documented
- Check frontmatter status field

### Step 3: Decompose Research Question in Product Terms

**Describe what the SOFTWARE DOES from the user's perspective**

1. **Break down the user's query into product areas**, not code modules:
   - What features are involved? What does the user see and do?
   - What user flows touch this area? What's the happy path? Error paths?
   - What data moves through the system? What does the user provide and receive?
   - What integrations or external services are involved?
   - What configuration controls behavior? What can be changed without code?

2. **REMEMBER: Document what IS, not what SHOULD BE**

3. **Work out:**
   - The user-visible surface of this feature — screens, APIs, messages, states
   - How this feature connects to adjacent features the user also touches
   - What a PM needs to know to make decisions about this area
   - Which parts of the codebase actually implement user-facing behavior

4. **Identify research areas** to investigate:
   - User-facing features and capabilities
   - User flows (happy path and error paths)
   - Data involved (what's collected, stored, displayed)
   - Configuration that affects product behavior
   - Integration points with other systems
   - Error states and recovery paths

5. **Consider which specific components** to investigate

### Step 4: Spawn Parallel Research Agents

Read [sub-agent-prompts.md](sub-agent-prompts.md) NOW and spawn the agents it defines, concurrently. It carries the fan-out announcement, the three typed agent prompts verbatim, the list of additional specialized agents to consider, and the parallel-execution shape.

**When the fan-out is skippable, and when it is not.** Spawn unless you have **already read the
entire relevant surface** in this context — every file the agents would open, not a sample. That
is a real case: a repository of three files, or a change confined to one module you have read
whole. Then the agents can only return what you already hold, and spawning them spends tokens to
learn nothing.

Anything else, spawn. In particular, spawn when you have read *some* of the surface and are
inferring the rest, when the change is cross-cutting, or when you are unsure which files are
relevant — that uncertainty is the thing the fan-out resolves, so treating it as a reason to skip
inverts the purpose.

**If you skip, say so in your output and say why**, naming what you read instead. A silent skip
is indistinguishable from forgetting, and the next reader cannot tell which happened.

**Sub-agents are READ-ONLY** — they return findings only; YOU write `product-research.md` after synthesizing.

**CRITICAL Agent Instructions (MUST follow exactly):**

- **Each agent describes what the software does, NOT how the code works**
- **Agents MUST describe what exists without ANY judgment**
- **Agents MUST include file:line references for every claim**
- **Use specific agent types for their strengths**
- **Run multiple agents in parallel for speed**
- **ALWAYS wait for ALL agents before synthesizing**
- **Remind EVERY agent: You are documenting the codebase AS IT EXISTS**

**⛔⛔⛔ BARRIER 2: STOP! Wait for ALL sub-agents to complete — DO NOT proceed until EVERY agent returns ⛔⛔⛔**

This barrier governs *waiting*, not spawning — synthesis on a
partial set misses what the missing report would have changed. If you skipped the fan-out under
the rule above, there is nothing to wait for and the barrier is satisfied trivially; it is not a
reason to spawn agents you just established would return nothing.

### Step 5: Synthesize Findings into Three Layers

**Document ONLY what EXISTS, in product language**

**IMPORTANT**: Wait for ALL sub-agent tasks to complete before proceeding

1. **Compile all sub-agent results**
2. **Prioritize live codebase findings** as primary source of truth
3. **Connect findings across different components**
4. **Answer the user's specific questions** with concrete evidence FROM THE CURRENT CODE
5. **DO NOT add recommendations or improvements unless explicitly requested**
6. **Organize into three layers**:

**Layer 1 — Product Overview** (the PM reads this):

- Feature overview in plain language
- User flows as numbered narratives
- Product behaviors: "when X, system does Y"
- Data involvement: what data, where it flows
- Error states as user-visible outcomes
- Integration points as capabilities

**Layer 2 — Engineering Approach** (pattern tracking):

- Coding patterns observed (naming, structure, organization)
- Architecture style notes
- Testing approach characterization
- Technology choices relevant to product decisions

**Layer 3 — Technical Appendix** (credibility backing):

- File references grouped by feature area
- Key code snippets for engineering conversations
- Configuration values that affect behavior

If the Audience rules are no longer in this context window, re-read them from
[reference.md](reference.md) before writing a word of Layer 1.

### Step 6: Write Product Research Document

Write the product-research.md file. **Keep the main agent focused on synthesis — sub-agents already did the deep file reading.**

Read [templates.md](templates.md) NOW and write the document in the shape it gives.

Two things about that template are load-bearing rather than cosmetic:

- **Open Questions are a table in this document, with local IDs** (`Q1`, `Q2`, …) and an
  explicit state. There is no external tracker: this table *is* the record. A question earns a
  row only if a decision waits on it; otherwise it is a finding.
- **A resolved question keeps its row and gains a pointer.** `/wb:resolve_questions` writes the
  decision and its rationale into `design.md` and sets the row's state to
  `Resolved YYYY-MM-DD → design.md (## Technical Decisions)`. The decision is not copied back
  here — this document records what the software does, and a decision is not one of those facts.

**⛔⛔⛔ BARRIER 3: STOP! Verify NO placeholder values — ALL data MUST be from ACTUAL codebase ⛔⛔⛔**

Before writing:

- **NO** "[To be added]" or similar placeholders
- **NO** generic examples — use REAL data from THIS codebase
- **NO** assumptions — only documented FACTS

### Step 7: Validate the Written Document

**After writing product-research.md, validate it against the codebase.**

Spawn the validation agent defined in [sub-agent-prompts.md](sub-agent-prompts.md) → "The validation agent (Step 7)". The validator reads the written file directly — no need to pass findings in context.

**⛔⛔⛔ BARRIER 4: STOP! Wait for validation agent to complete before proceeding ⛔⛔⛔**

After validation returns:

- If **PASS**: Update frontmatter `validation_status: passed`
- If **PASS WITH WARNINGS**: Update frontmatter `validation_status: passed_with_warnings`, add UNCERTAIN items to Validation Notes section
- If **FAIL**: Fix the failing claims by re-checking the code, update the document, re-validate

### Step 8: Handle Follow-Up Questions

If the user has follow-up questions:

1. **DO NOT create a new research file**
2. **Append to the existing product-research.md**
3. **Add new section**: `## Follow-up Research [YYYY-MM-DD HH:MM]`
4. **Update frontmatter**:
   - `last_updated: [YYYY-MM-DD]`
   - Add: `last_updated_note: "Added research on [topic]"`
5. **Spawn new sub-agents** for additional investigation
6. **Re-validate** the new claims after writing
7. **Continue building** on previous findings

### Step 9: Confirm Completion

Emit a one-line summary, not a recap:

```
✅ product-research.md updated — [topic]; validation [PASS/WARN]. Next: /wb:create_design
```

**Then, only if the findings earned it, suggest `explore_design`.**

Upstream shipped this nudge unconditionally and measured a 0/3 false-positive rate before
fixing it — an optional stage suggested by default is noise, and noise trains the reader to
skip the suggestion when it finally matters. So it fires on **evidence in what you just wrote**,
not on the fact that research finished.

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
A decision the research already made does not need a discussion stage.

## Important Notes

See [reference.md](reference.md) — critical ordering, documentation philosophy, file reading, the three-layer output contract, validation, and configuration.
