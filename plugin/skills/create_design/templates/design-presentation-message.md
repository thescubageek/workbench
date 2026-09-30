# Design presentation message

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 6. Emit this once, when `design.md` is ready for approval. The file is new, or a resumed
run found it complete.

```
✅ The design document is ready for approval: [path]/design.md

Design approach: [selected approach name]

Key decisions:

- [Major decision 1]
- [Major decision 2]
- [Major decision 3]

Pending decisions: [count]

Agent findings used in the design:

- [Finding 1 from verification agents]
- [Finding 2 from integration analysis]

The design document contains:

- Problem statement and success metrics
- Technical architecture decisions
- Scope boundaries
- Risk analysis and mitigation

Review the design, and answer these questions:

- Are the success criteria appropriate?
- Do the technical decisions match your intent?
- Is a risk missing?
- Should an out-of-scope item move into scope?
```
