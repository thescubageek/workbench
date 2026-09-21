# Modified Files fragment

Step 7 — aggregate every worker's output into this section of `tasks.md`.

**One substitution branches on the kind of plan.** A remediation plan
(`docs/plans/<plan>/reviews/<date>-round-N/`) has no numbered phase — `SKILL.md` Step 2 — so a
heading that hard-codes the phase number reads `Phase undefined`.

| Placeholder | Phased plan | Remediation plan |
| ----------- | ----------- | ---------------- |
| `${phaseLabel}` | `Phase <n>` | `Round N`, taken from the round's directory name |

````markdown
### 📝 Modified Files (${phaseLabel})

#### Code Files
${aggregatedCodeFiles.map(f => `- \`${f.path}\` - ${f.description}`).join('\n')}

#### Test Files
${aggregatedTestFiles.map(f => `- \`${f.path}\` - ${f.description}`).join('\n')}

**Quick test commands:**

```bash
# Run all tests for this phase
${generatePhaseTestCommand(aggregatedTestFiles)}
```
````
