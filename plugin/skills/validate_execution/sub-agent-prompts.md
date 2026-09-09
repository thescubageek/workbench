# validate_execution — sub-agent prompts

Read this when Step 2 directs you to. All four spawn together, in parallel — read the file
whole. Use the prompts verbatim, substituting the bracketed placeholders from `tasks.md` and
`research.md`.

**Sub-agents gather information and return findings. They do NOT write files.** You write the
validation report after synthesizing them.

## Agent 1: Verify code changes

```javascript
Task({
  description: "Verify code changes",
  prompt: `Analyze all code changes to verify they match the execution plan.

  From tasks.md, these files should be modified:
  [List files from tasks.md]

  Check:
  - Were all listed files actually modified?
  - Do modifications match specified changes?
  - Are there unexpected modifications?
  - Were any planned changes missed?

  Use git diff to compare changes if needed.
  Return findings only; write nothing.`,
  subagent_type: "codebase-analyzer",
  model: "haiku"
})
```

## Agent 2: Verify test coverage

```javascript
Task({
  description: "Verify test coverage",
  prompt: `Verify that all tests specified in the plan were implemented.

  From tasks.md, these tests were required:
  [List test requirements]

  Check:
  - Do all specified tests exist?
  - Do they test the right scenarios?
  - Are there gaps in coverage?
  - Do all tests pass?

  Run test commands and analyze coverage.
  Return findings only; write nothing.`,
  subagent_type: "general-purpose",
  model: "sonnet"
})
```

## Agent 3: Check for regressions

```javascript
Task({
  description: "Check for regressions",
  prompt: `Verify no existing functionality was broken.

  Run comprehensive checks:
  - All existing tests still pass
  - Build succeeds without warnings
  - No performance degradation
  - No breaking changes to APIs

  Return findings only; write nothing.`,
  subagent_type: "general-purpose",
  model: "sonnet"
})
```

## Agent 4: Analyze patterns and quality

```javascript
Task({
  description: "Analyze patterns and quality",
  prompt: `Verify implementation follows established patterns.

  From research.md, these patterns should be followed:
  [List patterns from research]

  Check:
  - Does new code follow existing patterns?
  - Are conventions maintained?
  - Is error handling consistent?
  - Are there any anti-patterns?

  Return findings only; write nothing.`,
  subagent_type: "pattern-finder",
  model: "sonnet"
})
```

Agents 2 and 3 are ad-hoc `general-purpose` spawns rather than typed wb agents, so they carry
no constraints of their own — everything they must not do has to be in the prompt. Both are
told to return findings and write nothing; keep that line if you adapt them.
