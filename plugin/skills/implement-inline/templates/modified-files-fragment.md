# Modified Files fragment

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Step 5. After the implementation, add or update this section in `tasks.md`.

````markdown
### 📝 Modified Files

#### Code Files
- `path/to/file1.ext` - Implemented [feature]
- `path/to/file2.ext` - Added [functionality]

#### Test Files
- `path/to/test1.spec.ts` - Tests for [feature]
- `path/to/test2.test.ts` - Integration tests for [scenario]

**Quick test commands:**

```bash
# Run only the tests for this phase. The scope limits the tests, and quiet hides green output
scripts/quiet npm test path/to/test1.spec.ts path/to/test2.test.ts
```
````
