# Worker context package

**Read this when Step 3 directs you to.** It gives the shape of the context package each worker
receives.

From the documentation you've read, extract only what workers need. For a remediation plan there
is no `design.md` or `research.md` to extract from: each task carries its own `**Fails when:**`
scenario and acceptance criterion, and those *are* the worker's context — pass the task line
verbatim and fill `design`/`patterns` from the reviewed code itself.

```javascript
const contextPackage = {
  // From design.md — why this phase exists. Renders FIRST in the worker prompt.
  design: {
    why: "one or two sentences: what this phase delivers and who it serves",
    phaseGoal: "what this phase achieves",
    successCriteria: ["criterion 1", "criterion 2"],
    constraints: ["constraint 1", "constraint 2"],
    architecturalApproach: "key decisions"
  },

  // From research.md - patterns workers must follow
  patterns: {
    testingFramework: "jest | pytest | go test | ...",
    testFileLocation: "tests/ | __tests__ | *_test.go | ...",
    fileStructure: "src/ layout | pkg/ layout | ...",
    namingConventions: "camelCase | snake_case | ...",
    importPatterns: "how modules are imported",
    errorHandling: "established patterns"
  },

  // Where the worker flips its checkbox
  tasksFile: `${projectDir}/tasks.md`,

  // Test commands
  testCommands: {
    unit: "npm test | pytest | go test ./...",
    specific: "npm test path/to/file | pytest tests/file.py",
    coverage: "npm test -- --coverage | pytest --cov"
  },

  // File references relevant to this phase
  relevantFiles: [
    "src/feature/file1.ts:123 - existing pattern to follow",
    "tests/feature/test1.spec.ts:45 - test structure example"
  ]
};
```

**Minimize context**: Only include what workers actually need to implement tasks.
