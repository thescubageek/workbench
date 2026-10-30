# Plan intent — the shipped rule

**Read this when a step directs you to.** It is the plugin's single authority on a plan's
`## Intent` section: its shape, which stage writes which part, and how the later stages answer
to it. Skills link here rather than restating it.

## What the Intent is

The Intent is the plan's contract with the person who asked for the work. It lives in the plan's
`README.md`, in one section, and it holds four parts:

- **Goal**: one sentence that says what the project is for.
- **Success looks like**: two to four statements, each with a local ID (`S1`, `S2`, …). A person
  can see or check each one when the project has done its job. A statement is observable, not
  numeric. `create_design` refines each statement into metrics later.
- **Non-goals**: what the project will not do. Write "none stated" when there are none.
- **Amendments**: a dated list of changes to the Goal or the Non-goals. It starts as `- none`.

Without the Intent, each stage checks only against the stage before it. Research answers the
question it was given. The design satisfies the research, and validation checks the tasks. No
stage asks whether the work does what the person wanted. The Intent is the one statement every
stage reads.

## Shape

The section goes in `README.md`, directly after `## Overview`:

```markdown
## Intent

**Goal**: Let a support agent see a customer's open orders without leaving the inbox.

**Success looks like**:

- **S1**: An agent opens a conversation and sees that customer's open orders in the side panel.
- **S2**: An order shipped elsewhere disappears from the panel without a page reload.

**Non-goals**:

- Editing orders from the inbox.

**Amendments**:

- none
```

- **Statement IDs are local and stable.** Number them in order. Never renumber them. A removed
  statement keeps its line, struck through with `~~…~~`, and an Amendments line says why.
- **A statement line is not a task line.** It carries no checkbox. A checkbox would put it in
  every counter that reads task lines.

## Which stage writes what

| Stage | Obligation |
| ----- | ---------- |
| `create_project` | Writes the section from text the user confirmed. Writes no file while the Goal, the statements or the Non-goals are empty. |
| `create_research` | Takes the Goal as its research question when the user gives none. Writes `## Intent Coverage` in research.md. Every statement ID goes in exactly one of two lists: findings that bear on it, or no findings that touch it. |
| `explore_design` | Frames the decision against the Goal, and cites the Goal first in the Decision Record. A change to the Goal or the Non-goals needs the user's explicit approval and an Amendments line. |
| `create_design` | Each item under `### Success Metrics` ends with `(refines: S<n>)`. Every statement is refined by at least one metric, or listed on the `**Deferred**:` line with a reason. Records any Goal or Non-goal change as an Amendments line before writing design.md. |
| `create_tasks` | Copies the metrics that refine a statement into the Overview's Target State, with their statement IDs. Each one is checked in the verification of some phase. |
| `validate_execution` | Reports a verdict for each statement. Writes the verdict back to the end of the statement's README line. |
| `help` | Reads all of the above to say where the plan is and what each stage left undone. |

### Coverage is a fact, not a judgment

Research stays a documentarian. "Findings bear on S2" means research found code that the
statement depends on, with a `file:line`. It does not mean the statement can be achieved, and
it does not recommend an approach. "No findings touch S3" is a finding too. Do not drop a
statement from both lists.

```markdown
## Intent Coverage

- **Findings bear on**: S1 — the side panel renders from `Conversation#customer` (`app/models/conversation.rb:42`). S2 — order updates broadcast on `OrdersChannel` (`app/channels/orders_channel.rb:8`)
- **No findings touch**: none
```

### Refining a statement

A statement says what a person will see. A metric says how to check it. Every metric under
`### Success Metrics` names the statement it refines:

```markdown
### Success Metrics

- The side panel lists the customer's open orders, checked by a request spec (refines: S1)
- A shipped order leaves the panel within 2 s of the broadcast (refines: S2)

**Deferred**: none
```

A metric that refines no statement does not belong under Success Metrics. A non-functional bar,
such as "no regression in page load", goes under the design's `## Success Criteria`. A metric
that the Intent does not cover can mean the Intent is missing a statement. In that case, ask the
user, and record an Amendments line if they add one.

`**Deferred**:` names each statement this design does not deliver, and the reason:
`S3 — needs the notification service, which is out of scope (design.md, Out of Scope)`.

## Amendments

A change to the Goal or the Non-goals is an amendment. A change to a statement is an amendment
too. An amendment needs the user's explicit approval. It is never inferred from silence or from
"sounds good". Edit the section in place, and add one line to the Amendments list, newest first:

```markdown
- 2026-10-29 — Non-goals: added "bulk order actions" — the design keeps one order at a time (approved by the user, create_design)
```

Replace `- none` with the first real line. Quote the old wording when the change rewrites it,
because the edit in place removes it.

## Verdicts

`validate_execution` gives each statement exactly one verdict:

| Verdict | When |
| ------- | ---- |
| `PASS` | Every metric that refines the statement has evidence: a passing check or a `file:line`. Any manual check behind it has been confirmed by a person. |
| `FAIL` | A metric that refines it failed, or has no evidence. |
| `DEFERRED` | design.md lists the statement on its `**Deferred**:` line. |

It then writes the verdict at the end of the statement's README line, with the date:

```markdown
- **S1**: An agent opens a conversation and sees that customer's open orders in the side panel. → PASS 2026-10-29
```

A later validation run replaces the suffix. It does not add a second one. A `PASS` that depends
on a manual check stays `FAIL` until a person confirms the check. Do not assume the
confirmation.

## Plans without an Intent

A plan created before wb 3.2.0 has no `## Intent` section. A remediation plan from
`adversarial-review` has no README at all. Neither has an Intent obligation. A stage that finds
no section says so once, in this form, and continues:

```text
Intent: no Intent section (plan predates 3.2.0), so no Intent checks apply.
```

Do not add an Intent section to an older plan unless the user asks for one. A section added
after the design exists does not tell you what the person wanted before the design.
