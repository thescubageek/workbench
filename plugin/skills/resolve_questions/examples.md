# resolve_questions — examples

Read this if the cadence of the walkthrough is unclear. One full worked dialogue, start to
finish, including a skip and an unresolved critical question.

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
