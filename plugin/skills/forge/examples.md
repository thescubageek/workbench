# forge — examples

Read this if the invocation shape is unclear.

## Examples

- `/wb:forge docs/plans/2026-05-12-project-roar/` — pick up the in-flight Roar project at its current pipeline phase
- `/wb:forge TB-2421` — start a new forge for ticket TB-2421 (will run `create_project` first)
- `/wb:forge TB-2421 design` — forge stops after design phase, doesn't enter execution
- `/wb:forge` (no args) — prompt for ticket or directory

## What each detected state looks like

State detection reads documents, not a tracker. These are the cases and the evidence for each:

| Evidence in the plan directory | Detected state | Next stage |
| ------------------------------ | -------------- | ---------- |
| directory does not exist | nothing started | `create_project` |
| `research.md` missing, or `status: draft` with placeholder sections | research not done | `create_research` |
| `research.md` `status: complete`, `design.md` missing or `status: draft` | design not done | `create_design` |
| `design.md` `status: approved`, `tasks.md` has no phases or no task lines | not decomposed | `create_tasks` |
| `tasks.md` has task checkboxes, at least one `[ ]` | mid-implementation | `implement` |
| every task checkbox `[x]` | implementation done | `validate_execution` |

Two readings that are easy to get wrong:

- **A `tasks.md` that exists but has no task lines is not "decomposed".** `create_project`
  writes a skeleton with planning checkboxes; that is not a plan. Look for task lines carrying
  a local ID.
- **`current_phase` is a cache, not evidence.** If it disagrees with the checkboxes, the
  checkboxes win — and `/wb:update_status` at the next transition reconciles it.
