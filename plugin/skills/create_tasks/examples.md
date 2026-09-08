# create_tasks — examples

Read the section a step directs you to. These are the two judgment calls this skill makes that
are easy to get wrong, worked through — sizing a task so a delegated worker can finish it, and
deciding when a task needs an explicit dependency at all.

## Sizing a task by projected tool calls

Wall-clock time does not predict whether a task fits a single delegated worker; **tool calls
do**. A one-hour task touching 3 files is ~20 calls; a one-hour task touching 12 files is ~80.

Project the calls before writing the task down. A rough count of what a worker actually spends:

| Work | Calls |
| ---- | ----- |
| Read a file it must understand fully | 1 each |
| Grep/glob to locate something | 1–2 each |
| Edit a file | 1–2 each (more if the edit is iterative) |
| Run the test suite | 1 per run, and there are always several |
| Commit, verify, report | 3–5 for the tail |

Worked example — **too big**:

```
Convert the settings module to the new config API
  12 source files to read          12
  12 edits                         18   (some take two passes)
  6 test files to update           12
  test runs                         8
  finishing tail                    5
                                  ---
                                  ~55 calls, and the estimate is optimistic
```

That projects past ~50, so it gets split before it is ever spawned.

## Splitting a task at its natural seam

The seam is usually **source change, then test conversion** — they are separately verifiable
anyway, which is what makes the split honest rather than arbitrary.

```
- [ ] **P2-T4** — Convert the settings module's 12 source files to the new config API.
      Leave the tests on the old API; they still pass through the compatibility shim. (~30 calls)
- [ ] **P2-T5** — Convert the settings module's 6 test files to the new config API and
      delete the compatibility shim. Depends on: P2-T4. (~25 calls)
```

Two properties make this a good split and not just a smaller one:

- **Each half is independently verifiable.** After `P2-T4` the suite is green; after `P2-T5`
  it is green again. A split that leaves the tree broken in between is not a seam, it is a
  fracture.
- **The dependency is real**, so it is stated. See below.

Bad split, for contrast: "convert files 1–6" then "convert files 7–12". Same size, but the
tree is half-migrated in between, nothing verifies, and the second half inherits whatever the
first half got wrong.

## When a task needs a "Depends on" field

**Phases run in document order, and tasks run in order within a phase.** That ordering is
already the dependency graph for the common case, so writing it out again adds nothing.

State `Depends on:` **only** where a task depends on something that is not simply the task
before it:

```
- [ ] **P3-T2** — Wire the new exporter into the CLI. Depends on: P1-T4 (the exporter
      interface), not the adjacent P3-T1. (~15 calls)
```

Do **not** write a `Depends on:` field for:

- the task immediately before it in the same phase — that is document order
- the previous phase — phases are already sequential
- "setup before implementation before tests" — that is the category order the phase already has

If most tasks in a phase need explicit dependencies, the phase is ordered wrong. Reorder it so
document order carries the dependencies, and keep the field for the genuine exceptions.
