# Manual verification request

Step 6 — emitted at the phase checkpoint, then **stop and wait**.

**Two substitutions branch on the kind of plan.** A remediation plan
(`docs/plans/<plan>/reviews/<date>-round-N/`) has no numbered phase and no `design.md` — SKILL.md
Step 1 and Step 2 — so a template that hard-codes either asks a human to work from a file that
does not exist, under a heading naming a phase nobody wrote.

| Placeholder | Phased plan | Remediation plan |
| ----------- | ----------- | ---------------- |
| `Phase [N]` | the phase number | `Round N`, taken from the round's directory name |
| the manual checks | the phase's manual checks from `design.md` | each outstanding task's own acceptance criterion, quoted from the round's `tasks.md` with the `file:line` it names |

**Never wait on an empty list.** If the round yields no criterion a human must run or judge, write
"no manual steps for this round" and skip the wait — a confirmation of nothing never arrives.

```
✅ Phase [N] Automated Verification Complete

**Automated checks passed:**
- ✅ All tests passing: [test command]
- ✅ Linting clean: [lint command]
- ✅ Build successful: [build command]

**Phase [N] task state:**
- ✅ Every Phase [N] checkbox is [x] ([X] of [X])

**Manual verification required:**

Please perform the following manual checks:

1. [Manual verification item 1]
2. [Manual verification item 2]
3. [Manual verification item 3]

Reply when manual verification is complete and I'll close out the phase.
```
