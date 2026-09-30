# Modified Files fragment

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 7 — aggregate every worker's output into this section of `tasks.md`.

````markdown
### 📝 Modified Files (Phase ${phase})

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
