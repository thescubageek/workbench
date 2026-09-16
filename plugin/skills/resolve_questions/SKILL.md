---
name: resolve_questions
description: Walk through open questions raised by wb workflow documents one at a time, recording each decision (with rationale) in the design decisions log and closing the source question.
argument-hint: "[project-directory]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Resolve Open Questions

Iterates through the unresolved questions surfaced by `/wb:create_research`, `/wb:create_design`, `/wb:create_tasks`, or `/wb:create_mockup` and walks the user through them **one question at a time**. Each answer is treated as a **decision**: it is recorded — *with its rationale* — in the canonical decisions log (`design.md`'s `## Technical Decisions`), the source question is marked resolved, and any tracking table (`## Pending Decisions`, `### Assumptions`) is reconciled before moving on. Progress is never lost if the user stops partway.

This skill is the bridge between "research/design surfaced N open questions" and "design / execution can now proceed with concrete decisions." Closing the loop means a resolved question does not just get an "answered" marker — it becomes a first-class decision that the next phase reads from where decisions live, not buried in an Open Questions list.

Supporting files in this directory (read each when its step directs you to — never paraphrase from memory):

- [templates.md](templates.md) — the **canonical** record shapes for every persistence path (Step 4d)
- [reference.md](reference.md) — operating principles and edge cases
- [examples.md](examples.md) — one full worked dialogue, including a skip and an unresolved critical question

**If a directed read fails, stop — do not continue from memory.** These files live outside your
project, so a read can be refused. Say which file was refused, that reads outside the working
directory are gated, and that the fix is to allow the read once or to relaunch with
`--add-dir <plugin-path>`. Do not route around a refusal with `cat`.

## What this skill does NOT do

- Does NOT answer the questions on the user's behalf. Claude proposes plausible options based on document context; the user picks.
- Does NOT make code changes or commit anything. It only updates wb project markdown.
- Does NOT batch all questions into one prompt. Strictly one question per turn.

## Initial Response

When invoked, check for arguments:

1. **If directory provided** (e.g., `/wb:resolve_questions docs/plans/2026-05-18-foo/`):
   - Use `$1` as the project directory.
   - Proceed to Step 1.

2. **If no arguments**:

   ```
   I'll walk through open questions one at a time. Please provide:
   1. Path to the wb project directory (e.g., docs/plans/2026-05-18-foo/)

   I'll scan research.md / design.md / etc. for open questions, assumptions,
   and pending decisions.
   ```

## Process Steps

### Step 1: Validate the project directory

- Confirm the directory exists. If not, surface the error and stop.
- List the `.md` files in the directory (typical: `research.md`, `design.md`, `tasks.md`, `mockups/**/mockup.md`).
- Read the frontmatter of each file to surface the project name and current status; mention them back to the user in a single short line.

### Step 2: Gather every open record

**⛔ BARRIER: Read all sources before presenting anything to the user. Do not start asking until the full list is known.**

Planning records live in the document that raises them — there is no external tracker to query, so the documents *are* the list. Read each `.md` file in the directory fully and collect:

1. **`## Open Questions`** (also `## Knowledge Gaps`, `## Questions`, `## Decisions Needed`) — usually a table with `Q` IDs, a `Blocks` column, and a state. Older plans may use bullets; read those the same way.
2. **`## Pending Decisions`** — `PD` IDs, with what each blocks.
3. **`### Assumptions`** — `A` IDs, with a `Validated?` state.
4. **`UIQ` rows** in any `mockups/**/mockup.md`.

Skip anything already carrying `**Resolved`, `**Answered`, `**Decided`, `Validated`, or an explicit `resolved YYYY-MM-DD` marker — those are closed.

Note whether an item is **critical**: an explicit marker (`(critical)`, `[BLOCKING]`, `**Critical:**`), or a `Blocks` value naming a phase that has already started. Critical items do not get an automatic skip option (Step 4b).

Track each as `{ file, id, text, blocks, critical }`.

**The same question in two documents is one entry.** Resolve it once, and update every row that references it.

### Step 3: Confirm the plan with the user

Once the full list is built, send a single short message:

```
Found N open questions across this project:
  1. [first 80 chars of question 1] — research.md Q1
  2. [first 80 chars of question 2] — design.md PD2 (critical)
  ...
Working through them one at a time. Reply with the option letter, or "skip"
to defer a non-critical question. Say "stop" any time to halt.
```

If N == 0, say so plainly (no questions to resolve, exit). Do not invent questions.

### Step 4: Walk the questions one at a time

For each question, in the order they appear in the project documents (by file order, then by ID):

**4a. Propose options based on document context.**

Read the surrounding context of the question (the section it lives in, the document's Summary, the document's "Architecture Documentation" section, and any nearby commitments). Propose **2–4 concrete answer options** that are:

- Mutually exclusive (the user is picking one direction).
- Phrased as decisions, not summaries ("Persist server-side via new column" not "Server-side persistence is an option").
- Specific to this codebase / context — pull terminology, file paths, or model names from the doc.

**4b. Ask the question. Prefer the structured `AskUserQuestion` tool when available; fall back to plain text.**

Two paths — pick based on what tools are actually available in the current session. The `AskUserQuestion` tool is built into Claude Code (v2.0.21+) and is also exposed by some hosts via MCP (e.g., a name ending in `__AskUserQuestion`). Look at your tool list before each ask; do not assume.

**Path 1 — Structured (preferred when available).**

If a tool named `AskUserQuestion` (or any `*__AskUserQuestion` variant) is in your tool list, call it with a SINGLE question. The exact schema is in the tool's own definition — follow that — but the shape is consistently a `questions` array where each entry has a `question` string and an `options` list. Single-select (the default). For example:

```json
{
  "questions": [{
    "question": "Q [n of N]: <verbatim question text>\n\nFrom: <file and record ID>\nWhy it matters: <one sentence drawn from the doc>",
    "options": ["<option A>", "<option B>", "<option C>", "Skip for now"]
  }]
}
```

Notes for the structured path:

- One question per call. Do NOT batch multiple questions into the `questions` array, even though the tool accepts up to 4.
- **Include `"Skip for now"` as the final option unless the question is critical.** Omit it for critical questions and prepend a one-line note to the `question` text: `(Critical — must be resolved before the next phase.)`
- Many hosts auto-append an "Other" / freeform option to capture custom text. Do NOT add one yourself; let the host handle it. If the host does not auto-append one, the user can still reply with a follow-up message and you can record that as an "Other" answer.
- The tool response gives you the chosen option string (or freeform text). Treat that as the answer.

**Path 2 — Plain text (fallback when no structured ask tool is available).**

If no `AskUserQuestion`-style tool is available, format the question as a single message and stop, waiting for the user's reply:

```
Q [n of N]: <verbatim question text>
Source: <file and record ID>
Why it matters: <one sentence drawn from the doc>

  A) <option A>
  B) <option B>
  C) <option C>
  S) Skip for now — leave open and revisit later
  O) Other (reply with freeform text)

Reply with a letter, or type your own answer.
```

Rules for the plain-text path:

- **Always include `S) Skip for now`** unless the question is critical. Critical questions omit the skip option and include a short note: `_This question is marked critical; it must be resolved before the next phase._`
- Letter the proposed answers starting at `A`. The `S` (skip) and `O` (other) letters are reserved — don't reuse them for proposed options.
- After sending the question, **end the turn**. Do not call any other tools. Wait for the user's reply.

**Shared rules (both paths):**

- One question per turn — never bundle.
- Pull terminology from the actual document; don't ask generic "Should we do X?" with abstract Yes/No.
- Options must be mutually exclusive and phrased as decisions, not summaries.

**4c. Interpret the answer.**

For the **structured path**, the tool response gives you the chosen option string (or freeform "Other" text). If the option string is `"Skip for now"`, treat it as a skip. Otherwise treat the string as the resolution.

For the **plain-text path**, parse the user's reply:

- A single letter (`A`, `B`, `C`, `D`, `S`, `O`, case-insensitive) → maps to the matching option.
- Freeform text without a letter → treat as an "Other" answer; record it verbatim.
- `skip`, `defer`, `later`, `pass` → treat as `S` (skip).
- `stop`, `halt`, `pause`, `quit` → jump to Step 5 with the partial summary.
- Ambiguous or contradictory reply → ask ONE follow-up message to clarify before proceeding.

In both paths: if the answer is a skip, do NOT persist anything — move on to the next question. If the user is trying to skip a **critical** question, confirm explicitly before honoring it (see [reference.md](reference.md) → Edge Cases).

**4d. Persist the decision immediately — do not batch.**

Each answer is a **decision**. Read [templates.md](templates.md) NOW — it holds the canonical shape for every record below, so that there is one definition to keep correct rather than several that drift.

**Capture the rationale (the WHY) first.** wb decisions are "WHAT and WHY," so never store a bare answer. Derive a one-line rationale from the chosen option's framing and the "Why it matters" context. If the user gave reasoning in their reply, use it verbatim. Do NOT burn an extra turn asking for rationale — infer it from context.

Then do all three, in order:

**① Land the decision in the decisions log — this is the loop-closing step.**

- **If `design.md` exists**, append the decision under `## Technical Decisions`, in the fitting subsection (Architecture / Data Model / Integration Points), or a `### Resolved Decisions` subsection if none fits.
- **If `design.md` does not exist yet** (questions resolved at the research stage, pre-design), there is nowhere canonical to land it. Record the bare answer at the source row as an interim; `/wb:create_design` will promote it.

**② Mark the source record resolved — a pointer, not a copy.**

`research.md` stays facts-only, so its row gets a pointer to where the decision lives, never the decision itself. Records in `design.md`, `tasks.md` or a mockup get the full resolution in place, since decisions belong there.

**Keep the original question text intact, and keep the row.** The audit trail is the point — a deleted row loses both the question and the fact that it was asked.

**③ Reconcile the tracking table it came from.** A `## Pending Decisions` row's **`State`** cell becomes `Resolved YYYY-MM-DD → design.md (## Technical Decisions)`; an `### Assumptions` row's `Validated?` cell becomes `Validated YYYY-MM-DD`, or `Invalid — <note>` if the answer refutes it.

**Never write the resolution into `Blocks`.** That cell records what the decision was holding up, and it stays true after the decision is made — a reader asking "why did this matter?" has nowhere else to look. A plan whose Pending Decisions table predates the `State` column has three columns; add the column rather than overloading `Blocks`.

Finally, if the project's index doc has a `last_updated:` field, bump it to today.

**4e. Brief acknowledgment, then continue.**

In one short sentence, confirm the decision and where it landed (e.g., "Decided: server-side resume via new `in_progress_responses` column — recorded in design.md (Technical Decisions), research.md Q1 marked resolved. Moving on."). Then immediately send the next question (Step 4b) and end the turn again.

Do NOT echo the full doc back. Do NOT summarize after every question. Keep cadence tight.

### Step 5: Final summary

After the last question (or when the user halts):

1. If every question in a file's Open Questions section is now resolved, optionally add a banner under the heading: `_All questions resolved as of YYYY-MM-DD._`
2. Send a single end-of-turn message summarizing:
   - How many resolved, how many skipped, how many remain — naming any **critical** ones still open explicitly.
   - Where the decisions landed, and which source records were marked resolved.
   - The suggested next wb step: `research.md` questions → `/wb:create_design`; `design.md` → `/wb:create_tasks`; `tasks.md` → `/wb:implement` or resuming a phase.

Keep this summary to ≤ 6 lines. The user just had a focused conversation; don't re-explain it.

## Operating Principles

See [reference.md](reference.md) — the ten operating principles and the edge cases. [examples.md](examples.md) has one full worked dialogue if the cadence is unclear.
