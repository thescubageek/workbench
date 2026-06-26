---
description: Walk through open questions raised by wb workflow documents one at a time, recording each decision (with rationale) in the design decisions log and closing the source question in markdown and/or beads.
argument-hint: [project-directory]
---

# Resolve Open Questions

Iterates through the unresolved questions surfaced by `/wb:create_research`, `/wb:create_design`, `/wb:create_execution`, or `/wb:create_mockup` and walks the user through them **one question at a time**. Each answer is treated as a **decision**: it is recorded — *with its rationale* — in the canonical decisions log (`design.md`'s `## Technical Decisions`), the source question is closed, and any tracking table (`## Pending Decisions`, `### Assumptions`) is reconciled before moving on. Progress is never lost if the user stops partway.

This command is the bridge between "research/design surfaced N open questions" and "design / execution can now proceed with concrete decisions." Closing the loop means a resolved question does not just get an "answered" marker — it becomes a first-class decision that the next phase (`/wb:create_execution`, `/wb:implement_tasks`) reads from where decisions live, not buried in an Open Questions list.

## What this command does NOT do

- Does NOT answer the questions on the user's behalf. Claude proposes plausible options based on document context; the user picks.
- Does NOT make code changes or commit anything. It only updates wb project markdown and beads issues.
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

   I'll scan research.md / design.md / etc. for "Open Questions" sections and
   pull any beads issues prefixed `Q:`, `Decide:`, `Validate:`, or `UI Q:`.
   ```

## Process Steps

### Step 1: Validate the project directory

- Confirm the directory exists. If not, surface the error and stop.
- List the `.md` files in the directory (typical: `research.md`, `design.md`, `execution.md`, `tasks.md`, `mockup-*.md`).
- Read the frontmatter of each file to surface the project name and current status; mention them back to the user in a single short line.

### Step 2: Gather pending questions from BOTH sources

**⛔ BARRIER: Read all sources before presenting anything to the user. Do not start asking until the full list is known.**

**Source A — Markdown `## Open Questions` (or `## Knowledge Gaps`, `## Questions`) sections.**

For each `.md` file in the directory:

1. Read the file fully.
2. Find any heading matching `^##\s+(Open Questions|Knowledge Gaps|Questions|Decisions Needed)\b` (case-insensitive).
3. Extract the bullets / numbered items beneath it, up to the next `^##` heading.
4. Skip any item that already has a child bullet starting with `**Resolved`, `**Answered`, `**Decided`, or any explicit "resolved on YYYY-MM-DD" marker — those are already closed.
5. Note whether the item or its parent heading carries a **critical** marker — e.g., `(critical)`, `[BLOCKING]`, `**Critical:**`, or an explicit "blocks design/execution" annotation. Critical questions do NOT get an automatic skip option (see Step 4b).
6. Track each remaining item as `{ source: "markdown", file, line_range, text, critical: bool }`.

**Source B — Beads issues (only if `.beads/` exists in the repo).**

Run:

```bash
bd list --status=open --json 2>/dev/null
```

If beads is not initialized or the command fails, skip source B silently.

Otherwise filter results:

- Title starts with `Q:`, `Decide:`, `Validate:`, or `UI Q:`.
- Issue is associated with the current project (heuristic: title or description references the project slug, the directory name, or any of the markdown filenames). If unsure, include it and let the user defer.
- Treat any issue with priority `critical`/`p0` (or a `blocker` label) as **critical**; others default to non-critical.

Track each as `{ source: "beads", id, title, description, critical: bool }`.

**Deduplicate**: if a markdown question and a beads issue clearly refer to the same thing (substring match on the question text), keep ONE entry preferring the beads version (since it has an ID for closure), and remember the markdown line range to also update on resolution. If either side is marked critical, the merged entry is critical.

### Step 3: Confirm the plan with the user

Once the full list is built, send a single short message:

```
Found N open questions across this project:
  1. [first 80 chars of question 1] — markdown:research.md
  2. [first 80 chars of question 2] — beads:prompts-abc (critical)
  ...
Working through them one at a time. Reply with the option letter, or "skip"
to defer a non-critical question. Say "stop" any time to halt.
```

If N == 0, say so plainly (no questions to resolve, exit). Do not invent questions.

### Step 4: Walk the questions one at a time

For each question, in the order they appear in the project documents (markdown first by file order, then beads issues):

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
    "question": "Q [n of N]: <verbatim question text>\n\nFrom: <markdown file or beads id>\nWhy it matters: <one sentence drawn from the doc>",
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
Source: <markdown file or beads id>
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

In both paths: if the answer is a skip, do NOT persist anything — move on to the next question. If the user is trying to skip a **critical** question, confirm explicitly before honoring it (see Edge Cases).

**4d. Persist the decision immediately — do not batch.**

Each answer is a **decision**. Before asking the next question, do all four of the following so the loop is actually closed — a skip persists nothing (see 4c). Use today's date from the environment.

**Capture the rationale (the WHY) first.** wb decisions are "WHAT and WHY," so never store a bare answer. Derive a one-line rationale from the chosen option's framing and the "Why it matters" context. If the user gave reasoning in their reply, use it verbatim. Do NOT burn an extra turn asking for rationale — infer it from context.

**① Land the decision in the decisions log — this is the loop-closing step.**

- **If `design.md` exists**, append the decision under `## Technical Decisions` (place it in the fitting subsection — Architecture / Data Model / Integration Points — or add a `### Resolved Decisions` subsection if none fits), using the wb decision format:

  ```markdown
  - <decision, phrased as a commitment>
    - Rationale: <why — one line>
    - Trade-off: <what we're giving up, or "none">
    - Source: <research.md question | beads:ID> · Decided YYYY-MM-DD
  ```

- **If `design.md` does NOT exist yet** (questions resolved at the research stage, pre-design), there is nowhere canonical to land the decision yet. Record it inline at the source question (see ② interim path) — `/wb:create_design` will promote it into `## Technical Decisions`.

**② Mark the source question resolved — pointer, don't duplicate the decision.**

- **In `research.md`** (facts-only — do NOT embed a decision or rationale here; that violates "Document, Don't Judge"). If `design.md` exists, leave a pointer:

  ```markdown
  - <original question text>
    - **Resolved YYYY-MM-DD** → decision recorded in `design.md` (## Technical Decisions)
  ```

  If `design.md` does not exist yet, record the bare answer inline as an interim and let `/wb:create_design` formalize it:
  `- **Resolved YYYY-MM-DD**: <answer>`

- **In `design.md` / `execution.md` / `mockup-*.md`** (decisions belong here): mark the question resolved in place with the full record:

  ```markdown
  - <original question text>
    - **Decided YYYY-MM-DD**: <answer> — <rationale>
  ```

Keep the original question phrasing intact so the audit trail survives. If multiple files reference the same question, update each.

**③ Reconcile any tracking table the question came from.**

- **`## Pending Decisions` row** (or a `Decide:` bead): the decision is no longer pending. Set the row's `Blocks` cell to `— resolved YYYY-MM-DD` (and ensure the decision itself is recorded per ①).
- **`### Assumptions` row** (or a `Validate:` bead): flip the `Validated?` cell from `Pending` to `Validated YYYY-MM-DD`, or to `Invalid — <note>` if the answer refutes the assumption.

**④ Update beads and the index doc.**

- **For beads-sourced questions**, capture the decision + rationale, then close:

  ```bash
  bd comments <id> add "Decided: <answer> — <rationale>"
  bd close <id> --reason "Resolved via /wb:resolve_questions"
  ```

  Use `bd close ... --reason` rather than `--status closed` (matches the convention in `/wb:help`).
- **For the project's index doc** (if frontmatter has a `last_updated:` field), bump `last_updated:` to today and optionally append a one-line note (e.g. `Resolved 3 open questions via /wb:resolve_questions`).

**4e. Brief acknowledgment, then continue.**

In one short sentence, confirm the decision and where it landed (e.g., "Decided: server-side resume via new `in_progress_responses` column — recorded in design.md (Technical Decisions), bead prompts-abc closed. Moving on."). Then immediately send the next question (Step 4b) and end the turn again.

Do NOT echo the full doc back. Do NOT summarize after every question. Keep cadence tight.

### Step 5: Final summary

After the last question (or when the user halts):

1. Update each touched markdown file once more if needed: if all questions in a file's "Open Questions" section have a `**Resolved`-marked sub-bullet, optionally add a small banner under the section heading: `_All questions resolved as of YYYY-MM-DD._`
2. Send a single end-of-turn message summarizing:
   - How many resolved, how many skipped, how many remain (including any critical ones still open — call those out explicitly).
   - Where the decisions landed (`design.md` `## Technical Decisions`) and which source questions / beads IDs were closed.
   - Suggested next wb step based on the current document phase:
     - If `research.md` had open questions → recommend `/wb:create_design`.
     - If `design.md` had open questions → recommend `/wb:create_execution`.
     - If `execution.md` had open questions → recommend `/wb:implement_tasks` or resuming an existing phase.
   - If any **critical** questions remain unresolved, name them and recommend resolving before advancing phases.

Keep this summary to ≤ 6 lines. The user just had a focused conversation; don't re-explain it.

## Persistence Format Reference

Resolving one question raised in `research.md` touches **two** places: the decision lands in `design.md`, and the source question in `research.md` gets a pointer (research stays facts-only).

**① Decision lands in `design.md` `## Technical Decisions`:**

```markdown
## Technical Decisions

### Data Model
- Partial responses persist server-side via a new `in_progress_responses` column
  - Rationale: aligns with the charting-note autosave precedent; PHI posture already approved for that path
  - Trade-off: one more write path to keep consistent with final-submit
  - Source: research.md question · Decided 2026-05-18
```

**② Source question in `research.md` becomes a pointer (no decision/rationale embedded — facts-only):**

```markdown
## Open Questions

- Should partial answers leave the device (PHI posture)?
  - **Resolved 2026-05-18** → decision recorded in `design.md` (## Technical Decisions)
- Is multi-device resume in scope, or same-device only?
```

**Resolving a question that lives in `design.md`/`execution.md`** (decisions belong there, so record in place):

```markdown
- Should branching semantics change for resumed sessions?
  - **Decided 2026-05-18**: No — resume reuses the existing branch; keeps the state machine single-path. (Rationale: avoids a second code path no one asked for.)
```

**Reconciling tracking tables:**

```markdown
## Pending Decisions
| Decision Needed | Beads ID | Blocks |
|-----------------|----------|--------|
| Persistence layer for partial responses | `prompts-abc` | — resolved 2026-05-18 |

### Assumptions
| Assumption | Beads ID | Validated? |
|------------|----------|------------|
| Autosave precedent covers PHI posture | `prompts-def` | Validated 2026-05-18 |
```

**Beads — comment (with rationale) + close:**

```bash
bd comments prompts-abc add "Decided: server-side persistence via in_progress_responses column — mirrors charting/note.rb autosave; PHI posture pre-approved."
bd close prompts-abc --reason "Resolved via /wb:resolve_questions"
```

## Operating Principles

1. **One question per turn.** Never bundle. The user explicitly asked for serial walkthrough.
2. **Always propose options.** Pull terminology from the actual document — don't ask a generic "Should we do X?" with abstract Yes/No.
3. **Always offer "Skip for now" unless the question is critical.** Critical questions block the next phase; non-critical ones get an explicit defer path so the user can keep moving.
4. **Persist after each answer, not at the end.** A user who quits halfway should keep their progress.
5. **Respect Skip.** If the user picks the skip option or says "skip this one," leave the question open and move on.
6. **No code changes.** This command only touches wb project markdown and beads. It does not edit application code, run tests, or commit.
7. **Don't answer for the user.** Claude proposes options based on doc context; the human decides.
8. **Source of truth is the document, not the conversation.** If the conversation supplies more context, fine — but the canonical resolution lives in the file or the bead.
9. **Prefer structured ask, fall back to plain text.** If `AskUserQuestion` (or an `*__AskUserQuestion` MCP variant) is available, use it; otherwise format the question as text, end the turn, and wait for the user's reply. Never speculate the user's answer.
10. **Close the loop — a resolved question is a decision.** Every non-skipped answer is recorded *with rationale* in the canonical decisions log (`design.md` `## Technical Decisions`), not left as a bare "answered" marker. The source question gets a resolved marker (a pointer when the source is `research.md`, which stays facts-only), and any `## Pending Decisions` / `### Assumptions` table it came from is reconciled.

## Edge Cases

- **No questions found**: tell the user plainly and exit. Don't invent.
- **Beads not initialized**: silently skip source B; only markdown is walked.
- **Question text is ambiguous or trivial**: read it verbatim from the source anyway. If it's truly trivial (e.g., a leftover placeholder), include a `D) Drop — not actually a question` option and remove the bullet if the user picks it.
- **User says "stop" / "halt" / "pause"**: jump to Step 5 immediately with the partial summary.
- **Same question in markdown and beads**: resolve both with the same answer in a single Step 4d cycle.
- **Critical question, user wants to skip anyway**: explain that the question is marked critical and ask the user to either pick an option or confirm they want to override. Only skip after explicit confirmation, and note the override in Step 5.

## Example Invocation

```
User: /wb:resolve_questions docs/plans/2026-05-18-nux-resume-progress/

Claude: Found 5 open questions in research.md (1 critical).
        Working through them one at a time. Reply with a letter or "skip"
        (skip unavailable on critical questions).

Claude: Q 1 of 5: Should partial answers leave the device (PHI posture)?
        Source: research.md
        Why it matters: design must commit to a persistence layer before
        execution can begin.

          A) Persist server-side via new in_progress_responses column
          B) Persist client-side only (localStorage), sync on submit
          C) Hybrid: client buffer with debounced server sync
          S) Skip for now — leave open and revisit later
          O) Other (reply with freeform text)

        Reply with a letter, or type your own answer.

User: A

Claude: Decided: server-side persistence via new in_progress_responses
        column. design.md doesn't exist yet, so recorded inline in
        research.md (interim) — /wb:create_design will promote it into
        Technical Decisions. Moving on.

        Q 2 of 5: ...

... etc ...

Claude: Done — 3 decided, 1 skipped, 1 critical still open.
        - research.md: 3 questions marked Resolved 2026-05-18 with the
          chosen answers (pre-design interim; create_design will fold them
          into Technical Decisions with rationale + trade-offs).
        - Skipped: "Should branching semantics change?" — kept open.
        - Critical & still open: "Which auth provider for SSO?" — resolve
          before `/wb:create_design`.
        Next: resolve the critical item, then `/wb:create_design docs/plans/2026-05-18-nux-resume-progress/`.

(When design.md already exists, the decision instead lands in
design.md `## Technical Decisions` with Rationale/Trade-off, and the
source question gets a pointer — see Persistence Format Reference.)
```
