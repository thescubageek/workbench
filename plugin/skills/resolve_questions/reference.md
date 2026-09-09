# resolve_questions — reference

Read this when a step directs you to.

## Operating Principles

1. **One question per turn.** Never bundle. The user explicitly asked for serial walkthrough.
2. **Always propose options.** Pull terminology from the actual document — don't ask a generic "Should we do X?" with abstract Yes/No.
3. **Always offer "Skip for now" unless the question is critical.** Critical questions block the next phase; non-critical ones get an explicit defer path so the user can keep moving.
4. **Persist after each answer, not at the end.** A user who quits halfway should keep their progress.
5. **Respect Skip.** If the user picks the skip option or says "skip this one," leave the question open and move on.
6. **No code changes.** This skill only touches wb project markdown. It does not edit application code, run tests, or commit.
7. **Don't answer for the user.** Claude proposes options based on doc context; the human decides.
8. **Source of truth is the document, not the conversation.** If the conversation supplies more context, fine — but the canonical resolution lives in the file.
9. **Prefer structured ask, fall back to plain text.** If `AskUserQuestion` (or an `*__AskUserQuestion` MCP variant) is available, use it; otherwise format the question as text, end the turn, and wait for the user's reply. Never speculate the user's answer.
10. **Close the loop — a resolved question is a decision.** Every non-skipped answer is recorded *with rationale* in the canonical decisions log (`design.md` `## Technical Decisions`), not left as a bare "answered" marker. The source question keeps its row and gains a resolved marker (a pointer when the source is `research.md`, which stays facts-only), and any `## Pending Decisions` / `### Assumptions` table it came from is reconciled. **Rows are never deleted** — the audit trail is the point.

## Edge Cases

- **No questions found**: tell the user plainly and exit. Don't invent.
- **Question text is ambiguous or trivial**: read it verbatim from the source anyway. If it's truly trivial (e.g., a leftover placeholder), include a `D) Drop — not actually a question` option and remove the bullet if the user picks it.
- **User says "stop" / "halt" / "pause"**: jump to Step 5 immediately with the partial summary.
- **The same question in two documents**: resolve both in a single Step 4d cycle, with the decision recorded once and each source row pointing at it.
- **Critical question, user wants to skip anyway**: explain that the question is marked critical and ask the user to either pick an option or confirm they want to override. Only skip after explicit confirmation, and note the override in Step 5.
