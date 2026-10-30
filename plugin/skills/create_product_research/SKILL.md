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
- [../../docs/reference/plan-intent.md](../../docs/reference/plan-intent.md) — the README's `## Intent` section, which Step 3 decomposes against and Step 6 reports coverage of

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

This stage needs from you: the product question, or a confirmation of the one derived from the plan's Goal.

**Output discipline**: act on barriers silently; don't restate the plan between
steps; emit only the artifact and a one-line completion summary.

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:create_product_research docs/plans/2025-01-08-auth/`):
   - Use `$1` as the project directory
   - If `$2+` exists, use as research question
   - Otherwise, derive the question from the README's `## Intent` Goal and confirm it in one
     line. Prompt for a research focus only when the plan has no Intent section

2. **If no arguments**:

   ```
   I'm ready to research the codebase from a product perspective. Please provide:
   1. Path to the project documentation directory
   2. Your research question or area of interest

   Example: /wb:create_product_research docs/plans/2025-01-08-auth/
   Then: "Research how user authentication works from a product perspective"
   ```

## Steps to Execute After Receiving the Research Query

### Step 1: Read Any Directly Mentioned Files First

- If the user mentions specific files (docs, JSON, configs), read each one in full first. Read
  the whole file. If Read returns a partial view, page through it with `offset` and `limit`.
- Read these files yourself, in the main context, before you spawn any agent. Decomposing the
  research needs their full content.

**Also read `.claude/wb/knowledge.md` if it exists.** It holds durable facts about this
repository — a constraint, a convention, a tool quirk — each with a date and a verification
hint. Two rules on how to use it:

- **The entries are dated claims, not current truth.** If an entry bears on your research,
  check it against the codebase using its verification hint rather than repeating it. An entry
  you find false gets corrected or deleted in this session, not worked around.
- **A knowledge entry is never a substitute for a finding.** `product-research.md` cites the
  codebase; the knowledge file only tells you where to look and what has already been settled.

Absent file, fall through — a repository with no entries is the normal starting state.

Also read [reference.md](reference.md)'s **Audience: Product Managers** section now. Everything
after this point is shaped by it.

⛔ BARRIER 1: every file the user mentioned is read in full — a decomposition built on a partial read aims the agents at the wrong places

### Step 2: Validate Project Structure

- Check that the specified directory exists; if not, create it
- Check if product-research.md exists (may be a follow-up)
- If it exists, read it in full to see what is already documented
- Check frontmatter status field

### Step 3: Decompose Research Question in Product Terms

**Describe what the software does, from the user's perspective**

Read the README's `## Intent` section and
[../../docs/reference/plan-intent.md](../../docs/reference/plan-intent.md) first. The "Success
looks like" statements are already in product terms, so decompose against them. A plan with no
Intent section has no such obligation. Say so once, in the reference doc's form.

1. **Break down the user's query into product areas**, not code modules:
   - What features are involved? What does the user see and do?
   - What user flows touch this area? What's the happy path? Error paths?
   - What data moves through the system? What does the user provide and receive?
   - What integrations or external services are involved?
   - What configuration controls behavior? What can be changed without code?

2. **Work out:**
   - The user-visible surface of this feature — screens, APIs, messages, states
   - How this feature connects to adjacent features the user also touches
   - What a PM needs to know to make decisions about this area
   - Which parts of the codebase actually implement user-facing behavior

3. **Identify research areas** to investigate:
   - User-facing features and capabilities
   - User flows (happy path and error paths)
   - Data involved (what's collected, stored, displayed)
   - Configuration that affects product behavior
   - Integration points with other systems
   - Error states and recovery paths

4. **Consider which specific components** to investigate

### Step 4: Spawn Parallel Research Agents

Read [sub-agent-prompts.md](sub-agent-prompts.md) NOW and spawn the agents it defines, concurrently. It carries the fan-out announcement, the three typed agent prompts verbatim, the list of additional specialized agents to consider, and the parallel-execution shape.

**Skip the fan-out only if you have already read the entire relevant surface in this context** —
every file the agents would open, not a sample. Having read *some* of it, a cross-cutting change,
or uncertainty about which files are relevant are each a reason to spawn, not to skip. **If you
skip, say so in your output and say why**, naming what you read instead.

**Sub-agents are read-only.** They return findings only, and you write `product-research.md`
after you synthesize them.

⛔ BARRIER 2: every spawned agent has returned (subagents run in the background, so wait for a completion notification from each one) — synthesis on a partial set misses what the missing report would have changed

This barrier governs waiting, not spawning. A fan-out skipped under the rule above satisfies it
trivially.

### Step 5: Synthesize Findings into Three Layers

Write in product language.

1. **Compile all sub-agent results**
2. **Prioritize live codebase findings** as primary source of truth
3. **Connect findings across different components**
4. **Answer the user's specific questions** with concrete evidence from the current code
5. **Organize into three layers**:

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

Three things about that template are load-bearing rather than cosmetic:

- **Intent Coverage lists every success statement exactly once**, in "Findings bear on" or in
  "No findings touch", as the reference doc describes. It states what exists, not whether the
  statement can be met.
- **Open Questions are a table in this document, with local IDs** (`Q1`, `Q2`, …) and an
  explicit state. There is no external tracker: this table *is* the record. A question earns a
  row only if a decision waits on it; otherwise it is a finding.
- **A resolved question keeps its row and gains a pointer.** `/wb:resolve_questions` writes the
  decision and its rationale into `design.md` and sets the row's state to
  `Resolved YYYY-MM-DD → design.md (## Technical Decisions)`. The decision is not copied back
  here — this document records what the software does, and a decision is not one of those facts.

⛔ BARRIER 3: no placeholder values — every value comes from the actual codebase, because a placeholder that ships becomes a finding nobody can check

Before writing:

- No "[To be added]" or similar placeholders.
- No generic examples. Use real data from this codebase.
- No assumptions. Write only documented facts.

### Step 7: Validate the Written Document

**After writing product-research.md, validate it against the codebase.**

Spawn the validation agent defined in [sub-agent-prompts.md](sub-agent-prompts.md) → "The validation agent (Step 7)". The validator reads the written file directly — no need to pass findings in context.

⛔ BARRIER 4: the validation agent has returned (wait for its completion notification) — a completion reported before validation certifies claims that nobody checked

After validation returns:

- If **PASS**: Update frontmatter `validation_status: passed`
- If **PASS WITH WARNINGS**: Update frontmatter `validation_status: passed_with_warnings`, add UNCERTAIN items to Validation Notes section
- If **FAIL**: Fix the failing claims by re-checking the code, update the document, re-validate

### Step 8: Handle Follow-Up Questions

If the user has follow-up questions:

1. **Do not create a new research file**
2. **Append to the existing product-research.md**
3. **Add new section**: `## Follow-up Research [YYYY-MM-DD HH:MM]`
4. **Update frontmatter**:
   - `last_updated: [YYYY-MM-DD]`
   - Add: `last_updated_note: "Added research on [topic]"`
5. **Spawn new sub-agents** for additional investigation
6. **Re-validate** the new claims after writing
7. **Continue building** on previous findings

### Step 9: Confirm Completion

Write this output in wb Technical English (WBTE): read [technical-english.md](../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Emit a one-line summary, not a recap:

```
✅ product-research.md updated — [topic]. Validation: [PASS/WARN]. Next: /wb:create_design
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

See [reference.md](reference.md) — research practice, the three-layer output contract, validation, and configuration.
