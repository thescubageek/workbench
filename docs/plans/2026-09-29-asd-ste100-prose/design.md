---
project: asd-ste100-prose
ticket: null
created: 2026-09-29
created_timestamp: 2026-09-29T17:35:59Z
status: approved
last_updated: 2026-09-30
designer: scraig
git_commit: 4b32306
git_branch: wb-2.2.0/asd_ste100_prose
repository: thescubageek/workbench
tags: [design, architecture, asd-ste100-prose]
depends_on: research.md
design_approach: "Option A — reference doc plus always-on rule card"
---

# Design: asd-ste100-prose

**Created**: 2026-09-29 17:35 UTC
**Designer**: scraig
**Ticket**: N/A

<!-- Status lives in frontmatter `status:` only. Do not restate it here: it is the field
     /wb:create_tasks and forge gate on, it changes, and a second copy goes stale the moment
     the design is approved. `created` and `ticket` are repeated above because they never
     change after creation. -->

## Problem Statement

The user finds some workbench output hard to follow. The cause is jargon and shorthand in two
places: the conversation, and the plan documents that the stages write (`research.md`,
`design.md`, `tasks.md`, handoffs, reports). The plugin has no rule about how output text must
read. Its only writing rules are about how much to say ("Output discipline") and about specific
audiences (`eli5-clip`, product research) (research §2). No check looks at wording (research §3).

Release 2.2.0 adds a writing standard for output: **wb Technical English**. It is adapted from
the principles of ASD-STE100 Issue 9. It also simplifies skill prose where that does not reduce
skill quality. The release must come before 3.0.0 and must not stall it.

If the problem is not solved, the output stays hard to read. Each later skill also adds more of
the same prose, because new skills copy the style of the existing ones.

### Success Metrics

- Generated plan documents and chat summaries score better on the wb Technical English metrics
  than the same output from 2.1.1, measured by the eval harness on the same fixture.
- Generated output has no semicolons in prose and no task, question, or decision ID used alone
  in chat.
- The eval harness finds no loss of content (facts, `file:line` references, IDs, barriers) in
  any accepted change.
- 3.0.0 can merge 2.2.0 with small, local conflicts only.

## Design Approach

The rules live in one shipped reference doc. A short rule card prints at every session start,
so the rules are in context for the whole conversation, also after compaction. Each template
that produces output starts with a link line to the reference doc. A maintainer-only eval
harness measures the output before and after each change and decides which skill-prose changes
are kept.

The release has two separate objectives (D-Q1):

1. **Objective 1 — output (priority).** The conversation and the generated documents follow wb
   Technical English.
2. **Objective 2 — skill prose "lite" (secondary).** Skill instruction text is simplified only
   where the harness shows no loss. Where looser prose gives better results, it stays.

### Why This Approach

- The session-start hook is the only channel that is present in every session and after
  compaction (research §1, `plugin/hooks/wb-prime.sh:12-18`). `doc-adherence/SKILL.md:63-69`
  already says that boundary rules belong in the hook, because skill text does not survive
  compaction. Objective 1 includes the conversation, so it needs this channel.
- A single reference doc follows the `branch-naming.md` precedent (2.1.0, research §4). It meets
  all four admission tests in `plugin/docs/reference/README.md:8-17`. More than one skill needs
  it, a skill step reads it at runtime, it states a rule, and linking is better than copying.
- Link lines are the smallest possible edit to the 48 files that 3.0.0 also changes (D-Q3).
- The harness gives the "measure before you claim" discipline that 2.0.0 used. In 2.0.0, trims
  that measured worse (R3, R4) were not applied (`CHANGELOG.md`, 2.0.0 entry). Objective 2
  needs the same gate.

## Technical Decisions

### Architecture

- **One authority for the rules: `plugin/docs/reference/technical-english.md`.**
  - It holds the full wb Technical English rules, the wb technical-noun list, the shorthand and
    ID rules, the list of exempt tokens, and the credit line.
  - No other file states the rules. Other files link to it.
  - Rationale: stale copies of a rule that keep instructing are a recorded failure in this
    repo (`plugin/docs/reference/README.md:36-47`).
  - Trade-off: a stage must read one more file when it writes output. This costs tokens.
  - Pattern reference: `plugin/docs/reference/branch-naming.md:3-4`.

- **An always-on rule card from `wb-prime.sh`.**
  - The card is a compact summary of the output rules in about 5 to 8 lines. It ends with the
    path to the reference doc.
  - It prints on every SessionStart source (startup, resume, compact). This includes the
    compact path when a repo has no active plans. Today that path exits with no output
    (`wb-prime.sh`, recovery mode, `[ "$count" -eq 0 ] && exit 0`).
  - It prints outside the block that `.claude/wb/PRIME.md` replaces. A repo that overrides the
    orientation text keeps the card.
  - `WB_TECH_ENGLISH=0` turns the card off. This follows the `WB_LINT_HOOK=0` precedent from
    2.1.1 (`plugin/scripts/README.md:72`).
  - Rationale: this is the only way to cover the conversation between stages and after
    compaction.
  - Trade-off: every session pays the token cost of the card. This includes sessions in repos
    that do not use wb plans.
  - Pattern reference: the recovery text at `wb-prime.sh:91-101`.

- **Link lines at the point of output.**
  - Every template that produces a document or chat output starts with one line that links to
    the reference doc.
  - A stage that writes output with no template (for example the `create_research` Step 8
    completion line) gets the link line at that step.
  - In the 48 shared files, the link line is the only change (D-Q3).
  - Rationale: the rule card reminds the model, and the link line gives the full rules at the
    moment the model writes.
  - Pattern reference: "Read [link] NOW and apply it" (`create_project/SKILL.md:104`).

- **Objective 2 is gated by the harness, change by change.**
  - The "lite" rules for instruction prose are a separate, smaller section of the reference doc.
  - The skill-prose rewrite covers only the 82 `plugin/` files that 3.0.0 does not touch
    (D-Q3).
  - The release keeps a rewrite of a skill file only if the harness shows no loss of fidelity
    and no drop in behaviour for that stage. If the harness shows a loss, the old text stays.
  - Rationale: the user does not want lower skill quality in exchange for simpler prose
    (D-Q1). The 2.0.0 blind trials showed that some trims make results worse (R3, R4).
  - Trade-off: until the post-3.0.0 pass, skill prose is not consistent across files.

- **The eval harness is maintainer tooling at the repo root (`evals/`), never shipped.**
  - It runs fixed stage prompts headless on a fixed fixture, with two plugin trees: before and
    after.
  - It uses python3 and the `claude` CLI. Neither becomes a user requirement, because nothing
    under `plugin/` calls the harness (D-Q5).
  - Rationale: root `docs/` is for maintainer documents and is never a runtime source
    (`CLAUDE.md`, "Where rules may live"). A separate root directory keeps tooling apart from
    documents.
  - Trade-off: a maintainer must remember to run it. No CI runs it on `main`.

- **The user's own dictionary copy is optional and lives outside every repo.**
  - A new user-invocable skill helps the user make the copy (D-Q2). The user gets the free
    Issue 9 PDF from ASD. The skill extracts the dictionary on the user's machine to a
    user-level path under `~/.claude/wb/`.
  - The extraction uses a tool the user already has (`pdftotext`, or python3 with a PDF
    library). If neither is present, the skill says what to install and stops. The plugin
    works without the dictionary.
  - At runtime, the reference doc tells the model to look up single words in the copy when it
    is not sure about a word. The model never loads the whole dictionary.
  - The harness checker also uses the copy, if it exists, to count unapproved words.
  - Rationale: ASD prohibits redistribution, so the dictionary cannot be in the repo. A
    user-level path means the copy is never committed to any repo by accident.
  - Trade-off: users without the copy get the rules but no dictionary check.

### Data Model

**Contents of `technical-english.md`** (what it holds, not its final wording):

| Section | Holds |
| ------- | ----- |
| Credit and scope | "Adapted from the principles of ASD-STE100 Issue 9. Not endorsed by ASD, and not ASD-STE100 compliant." The surfaces it covers. No ASD rules text and no dictionary content. |
| Output rules | The rules for documents and chat. See the rule list below. |
| Instruction rules ("lite") | The smaller rule set for skill prose. Every item is optional where the harness shows a loss. |
| Technical nouns | The wb terms that may be used without explanation (plan directory, stage, barrier, checkpoint, frontmatter, journal entry, task ID, and similar). Code, paths, and commands in backticks count as technical nouns. |
| Shorthand and IDs | IDs such as `P1-T3`, `Q2`, `PD1`, `D-Q3` are never used alone in chat. They are paired with a short meaning. Documents keep IDs because parsers depend on them. No unexplained abbreviations or symbol shorthand in prose. |
| Exempt tokens | The strings that parsers and validators match. They stay exactly as they are. See Integration Points. |
| How it combines with Output discipline | Output discipline decides how much to say. wb Technical English decides how to say it. A one-line summary stays one line, but it is a complete sentence and not a telegraphic fragment. |
| Optional dictionary | Where the user's copy lives, and how to look up a word in it. |
| Repo terms | A repo can list its own technical nouns in `.claude/wb/technical-nouns.md`. If the file exists, the model treats those terms as approved. Other repo jargon is defined at first use or replaced. |

**Output rules** (adapted in spirit from ASD-STE100, research §6):

- One instruction in each sentence. Instructions use the imperative. A condition comes first.
- At most 20 words in an instruction sentence and 25 words in a descriptive sentence. Text in
  backticks counts as one word (ASD Rules 8.5–8.7).
- At most 6 sentences in a paragraph, and one topic in each paragraph.
- Active voice. Simple tenses.
- No semicolons in prose.
- No omitted words. Use articles and verbs, not telegraphic fragments.
- Noun clusters of at most 3 words, unless the cluster is a technical noun.
- Lead with the result, then give the reason.
- Tables, headings, code blocks, and checklists keep their structure. The sentence rules apply
  to the prose inside them.

**Contents of the rule card:** the six to eight most important output rules as short
imperatives, the ID rule, and the path to the reference doc. The final text is written in the
execution phase and measured by the harness.

### Integration Points

- **`plugin/hooks/wb-prime.sh`** (shared with 3.0.0). The card prints in both the orientation
  and the recovery branch, independent of the active-plan count and of `PRIME.md`. The hook
  contract does not change: it only reads, it always exits 0, and it prints plain text.
  3.0.0's only change to this file is 4 comment lines.
- **Templates** (research §1, integration findings):
  - Not shared with 3.0.0, so rewritten in wb Technical English plus a link line. These are
    `create_project` document templates (except the journal template), `create_research/templates.md`,
    `create_design/templates/*`, `create_handoff/templates/*`, `explore_design/templates/*`,
    `create_tasks/templates/plan-presentation-message.md`, `resume_handoff/templates.md`,
    `validate_execution/templates.md`, `resolve_questions/templates.md`, `forge/templates/*`,
    `create_mockup/templates/*`, `create_product_research/templates.md`,
    `daily-digest/digest-template.md`, `touch-grass/state-template.md`,
    `implement/templates/incomplete-worker-message.md`,
    `implement_inline/templates/modified-files-fragment.md`,
    `validate_project/templates/error-message-formats.md`.
  - Shared with 3.0.0, so only a link line. These are
    `create_project/templates/journal-md-template.md`,
    `create_tasks/templates/tasks-md-template.md`, `implement/templates/*` (three files),
    `implement_inline/templates/{manual-verification-request,phase-completion-report}.md`,
    `update_status/templates/*`, `validate_project/templates/validation-report.md`.
- **Exempt tokens.** The rewrite must not change any of these (integration findings):
  - Task-ID regex `[A-Z0-9-]*[0-9][A-Z0-9-]*` and bold task lines `- [ ] **ID**`.
  - Journal headings `## YYYY-MM-DD HH:MM — <label> (open)` and `(closed)`.
  - `status:` values, `current_phase:`, `task_tracking: markdown-checkboxes`.
  - Q, A, PD, and UIQ ID shapes, and the section headings `## Open Questions`,
    `## Pending Decisions`, `### Assumptions`.
  - State literals: `Resolved YYYY-MM-DD → design.md (## Technical Decisions)`,
    `Validated YYYY-MM-DD`, `Invalid — <note>`.
  - Checkpoint text: `### ⛔ CHECKPOINT:`, `**(derivable)**`, `**(attestation)**`,
    `Go by the label, never by position`.
  - Report text: `### Status: PASS`, `### Baseline failures`, `(completed YYYY-MM-DD HH:MM)`,
    `### Current Blockers`, and the placeholder strings the validator searches for.
- **Stage completion lines.** The `✅ … Next: /wb:<stage>` shape stays. No parser reads it, but
  users recognize it. In files not shared with 3.0.0, the semicolons in it are replaced. The
  `create_research` Step 8 line is in a shared file, so it gets only the link line. The
  reference doc says that the STE rules apply to the words inside the fixed shape.
- **Agents and sub-agent prompts.** Agent reports reach the user only through the calling
  stage, which writes the document under the output rules. The prompts in files not shared
  with 3.0.0 are in scope for Objective 2 only, and through the harness gate.
- **README and CHANGELOG.** The README gets a short section on wb Technical English: what it
  is, the card, `WB_TECH_ENGLISH=0`, and the optional dictionary. The CHANGELOG gets a 2.2.0
  entry. These are release documentation, not a prose rewrite (D-Q1).
- **3.0.0 handoff.** The release includes a handoff document for the
  `adversarial-loop-skill-research` branch. It lists the new files, the link-line pattern, the
  `wb-prime.sh` lines, the 48 files for the post-3.0.0 pass, and how to run the harness.
- **Version.** `plugin.json` and `marketplace.json` go to 2.2.0. All additions are new files or
  new output, and no new user requirement exists. This is a minor release under both the
  `main` and the 3.0.0 versioning rules (research §7).

### Resolved Decisions

- **D-Q1 — Two separate objectives, output first.** Objective 1 (priority): conversational
  output and generated plan documents (`research.md`, `design.md`, `tasks.md`, and the other
  template-driven artifacts) are written in ASD-STE100, so that a human can follow them without
  having to decode jargon or shorthand. Objective 2 (secondary): skills get an ASD-STE100 "lite"
  treatment where it helps "lock in" that mode of writing for Claude. It applies only where it
  does not reduce skill integrity, performance, or robustness. Where looser conventions give
  better results, the skill keeps them.
  - Rationale (user's words): "right now it can sometimes be really hard for me to follow the
    output because of jargon and shorthand"; "I do NOT want to compromise skill integrity,
    performance, or robustness by downgrading the prose when maintaining looser conventions
    would improve results."
  - Trade-off: the model reads instruction prose, and a human reads output prose. The two
    surfaces get different standards, so one rule does not cover both.
  - Maintainer docs (README, CLAUDE.md, CHANGELOG, `docs/`): not named in the answer; not in
    either objective.
  - Source: research.md Q1 · Decided 2026-09-29
- **D-Q2 — The plugin paraphrases the rules, the user supplies their own copy, and the variant
  is adapted "in spirit".**
  - The plugin states the rules in its own words and ships no ASD rules text and no dictionary.
  - If the user keeps their own free copy of ASD-STE100 Issue 9 at a known local path, the
    plugin also uses its approved-word dictionary. Nothing from ASD is committed to the repo.
  - The plugin helps the user make that local copy (obtain the PDF, then extract the
    dictionary on their own machine) instead of just telling them it is optional.
  - The rules are a workbench variant adapted "in spirit" for AI-led software engineering and
    this harness. The wording can differ from ASD's, and rules can change or be added where
    that serves the workbench.
  - Rationale (user's words): "we can use different words in the rules if they benefit us. We
    are copying 'in spirit' but modifying to fit the needs of AI-led software engineering and
    this workbench harness."
  - Trade-off: without the local copy, only the paraphrased rules apply and no dictionary
    check runs. The two setups give different levels of enforcement.
  - Constraint carried forward: "ASD-STE100 Simplified Technical English" is a registered EU
    trade mark (research §6), and ASD and STEMG endorse no tools. The name of the adapted
    variant, and how it credits ASD-STE100, are for design to settle.
  - Source: research.md Q2 · Decided 2026-09-29
- **D-Q3 — Keep edits to the 48 shared files minimal, hand off to the 3.0.0 branch, and move
  the shared-file prose upgrade to after 3.0.0.**
  - The rule lives in new files. In the 48 `plugin/` files that 3.0.0 also changes, 2.2.0
    adds only short link lines, the way `branch-naming.md` is wired in.
  - The skills "lite" rewrite (objective 2, D-Q1) applies in 2.2.0 only to the 82 `plugin/`
    files that 3.0.0 does not touch.
  - 2.2.0 includes a handoff document for the `adversarial-loop-skill-research` (3.0.0+)
    branch. It tells that branch how to adopt the new format.
  - The prose upgrade of the shared files happens after the adversarial loop ships, in 3.0.1
    or 3.1.0. The exact version number is still open.
  - Rationale (user's words): "I am concerned that this will cause an additional series of
    adversarial loop failures and stall out 3.0.0, so maybe the prose upgrade happens in
    3.0.1/3.1.0 after we get the adversarial loop shipped."
  - Trade-off: until the follow-up release, skill prose is inconsistent, with some files
    rewritten and some not. The output rule (objective 1) applies to both.
  - Source: research.md Q3 · Decided 2026-09-29
- **D-Q4 — A small eval harness shows "without compromising quality".**
  - The harness has fixed prompts for each stage, which it runs headless (`claude -p`) before
    and after the change.
  - It scores the results on the STE metrics (research §5 method) and uses an LLM judge to
    check content fidelity: no lost facts, `file:line` references or barriers.
  - The harness stays in the repo for later releases, including the 3.0.1/3.1.0 shared-file
    pass (D-Q3).
  - Rationale: it gives a repeatable measurement for both objectives (D-Q1). Objective 1 needs
    output readability to improve, and objective 2 needs skill behaviour to hold. Today the
    repo measures neither.
  - Trade-off: the harness is new maintainer infrastructure with real run cost (model calls
    per stage per run), and an LLM judge is itself a model output that needs checking.
    Whether it ships under `plugin/` or stays maintainer-only is for design to settle,
    together with Q5.
  - Source: research.md Q4 · Decided 2026-09-29
- **D-Q5 — At runtime the rules are instructions only, and the mechanical checker exists only
  inside the eval harness.**
  - The STE rules reach the model as instruction text. No new check runs on a user's machine,
    and the PostToolUse lint hook stays as it is.
  - The mechanical STE checker (sentence length, semicolons, banned shorthand, and similar
    measurable rules) is maintainer tooling that runs inside the eval harness (D-Q4).
  - Rationale: it adds no environment requirement for users, so the change fits a minor
    2.2.0. The 3.0.0 branch's versioning rule treats a new requirement as major. It also keeps
    the runtime surface out of the lint-hook area that 2.1.1 just changed.
  - Trade-off: users get no automatic STE feedback while they work. Whether output follows the
    rules depends on the model following the instructions. The harness measures this, but only
    when a maintainer runs it.
  - Source: research.md Q5 · Decided 2026-09-29
- **D1 — Delivery: reference doc plus always-on rule card (Option A).** Chosen over a
  background skill and over a hook that carries all the rules. See Rejected Alternatives.
  - Rationale: the conversation is part of Objective 1, and the hook is the only channel that
    covers it in every session and after compaction.
  - Trade-off: a small edit to `wb-prime.sh`, which 3.0.0 also changes, and a token cost in
    every session.
  - Source: create_design Step 4 · Decided 2026-09-29
- **D2 — Name: "wb Technical English", abbreviated WBTE.** The reference doc credits the
  source as "adapted from the principles of ASD-STE100 Issue 9" and says ASD does not endorse
  it. WBTE is on the technical-noun list, so it may be used without expansion after the
  reference doc defines it.
  - Rationale: the name is close to the source, but it does not use the registered mark
    "ASD-STE100 Simplified Technical English" (research §6).
  - Trade-off: the name is less recognizable than "STE" to people who know the standard.
  - Source: create_design Step 4 · Decided 2026-09-29

- **D3 — A2 (does the model follow a link line?) stays open until P4-T2 measures it.**
  - Rationale: the card already gives most of the document gains. Only a measurement can
    show what the link line adds.
  - Trade-off: the Phase 4 rewrites start before A2 is known.
  - Source: design.md A2 · Decided 2026-09-30

- **D4 — The dictionary copy promises the word, the part of speech and the approved status.
  Alternatives are best-effort.**
  - Probe (2026-09-30, the user's own copy, `pdftotext -layout`, cwd outside every repo): the
    434 pages convert in 0.8 s. A simple pattern finds about 1,926 headword lines with a part
    of speech, about 90% of the ~2,149 listed words. Approved words are in uppercase (615) and
    unapproved words in lowercase (1,311), so the status is reliable. 1,850 entries wrap onto
    a continuation line, so alternatives need column parsing across lines.
  - Rationale: the three reliable columns are enough for a one-word lookup and for the
    harness count of unapproved words. Alternatives add value where parsing works.
  - Trade-off: some rows have an empty alternatives cell. The extractor must not guess.
  - Source: design.md A4 · Decided 2026-09-30

- **D5 — A5 is validated at `2fff76c`, and P7-T4 checks it again.**
  - Check (2026-09-30): `git diff 4b32306 adversarial-loop-skill-research -- plugin/hooks/wb-prime.sh`
    shows the same 4 `shellcheck` comment lines, away from the card's lines.
    `git merge-tree --write-tree HEAD adversarial-loop-skill-research` auto-merges
    `wb-prime.sh`.
  - The merge has 5 conflicts. Three of them already exist between 2.1.1 (`4b32306`) and the
    3.0.0 branch: both manifests and `README.md`. 2.2.0 adds two: `.gitignore` (both branches
    append the bytecode lines) and `.claude/wb/knowledge.md` (both append entries).
  - Rationale: the card placement holds today. The 3.0.0 branch is still moving, so the
    release check must repeat the test.
  - Trade-off: `knowledge.md` is not in the P7-T5 expected set, so the 3.0.0 handoff needs a
    resolution note for it (keep both appended entries).
  - Source: design.md A5 · Decided 2026-09-30

- **D6 — A6 stays open until a larger fixture tests the sub-agent fan-out.**
  - Evidence so far: P1-T3 passed. Every run since has written its documents (9 of 9 stages
    when the network held), with two conditions. The driver passes `--add-dir <tree>/plugin`,
    and `create_design` gets one fixed follow-up reply. On the small fixture, the stages skip
    their sub-agent fan-out, so no run has shown that a headless stage can spawn its agents.
  - Rationale (the user's choice): a stage that never spawns its agents is not the stage
    that users run on a real codebase.
  - Trade-off: the Phase 4 and Phase 5 measurements rest on a partly validated driver. A
    larger fixture is a follow-up (tasks.md, Implementation Notes). It is not a new task.
  - Update 2026-09-30: the user added the larger fixture as P5-T5. On it, every stage spawned
    its agents, so A6 is validated.
  - Source: design.md A6 · Decided 2026-09-30

- **D7 — The "no loss" gate judges each run against its own `research.md`.**
  - The gate asks whether every fact, `file:line` reference, ID and barrier in a run's
    `research.md` is carried into that run's `design.md` and `tasks.md`. A rewrite passes when
    no repeat shows a loss (3 of 3), in both trees.
  - Why not before/after: two runs of the same tree got a "loss" verdict on `design.md`,
    because each run chose a different design (`thoughts/2026-09-30-judge-calibration.md`).
    A check inside one run does not depend on which design the run chose.
  - Rationale (the user's choice): fidelity is about carrying facts forward, and a run carries
    its own facts.
  - Trade-off: `judge.py` needs a new within-run mode, and that mode needs calibration: a
    planted loss is found 3 of 3, and a real run on 2.1.1 shows no loss. This work is not in
    the task list yet. It must land before P4-T9 and Phase 5.
  - Update 2026-09-30: P4-T10 added and calibrated the within-run mode, before P4-T9.
  - Source: tasks.md, Implementation Discoveries (the P2-T7 finding) · Decided 2026-09-30

- **D8 — Accept the semicolons in the shared `tasks.md` boilerplate for 2.2.0.**
  - The remaining document semicolons come from fixed text in
    `create_tasks/templates/tasks-md-template.md`: the checkpoint block, the ID-shape rule, the
    "Tasks run in document order" note, and the prerequisites line. The model copies this
    text into every plan.
  - Rationale (the user's choice): the template is shared with 3.0.0, and D-Q3 allows only the
    link line there. The post-3.0.0 pass rewrites it.
  - Trade-off: the "no semicolons in prose" target is met everywhere except in this
    boilerplate. The 3.0.0 handoff (P7-T2) names it.
  - Source: P4-T9, thoughts/2026-09-30-objective-1-report.md · Decided 2026-09-30
- **D9 — The chat ID rule works per paragraph.**
  - Give an ID its meaning once in each paragraph, at the first mention. A later mention in
    the same paragraph does not repeat it. An ID inside another ID's meaning needs no meaning
    of its own. A range such as "P0-T1 to P0-T4" can stay bare. A document does not explain
    an ID at each use.
  - Rationale (the user's words): "avoid redundancy within the same paragraph on IDs but not
    across the entire prose of an output. We do not need the rule inside of output docs to
    fully explain each abbreviation."
  - Trade-off: a long message repeats a meaning in each paragraph. Card rule 1,
    `technical-english.md` (Shorthand and IDs) and `wbte_check.py` all state the same rule,
    and every run is scored again with the corrected detector.
  - Source: P4-T9 · Decided 2026-09-30

- **D10 — The Phase 5 gates use 1 repeat each, not 3.**
  - At about 01:38 on 2026-09-30, four parallel runs on the large fixture hit the user's
    individual spend limit. The later stages failed with no output. Each repeat on the large
    fixture costs about $5 and takes 12 minutes.
  - Rationale (the user's choice): finishing 3 repeats for each gate needed about $60 more.
    Objective 2 is secondary (D-Q1).
  - Trade-off: a verdict is "no loss in 1 of 1", not "3 of 3". The verdict table says so, and
    the post-3.0.0 pass can measure again with 3 repeats.
  - Source: P5-T5 · Decided 2026-09-30

- **D11 — Accept the 2 remaining chat IDs for 2.2.0, as a known remainder.**
  - In the final P4-T9 run, one `create_tasks` summary sentence has 2 IDs used alone. The
    CHANGELOG and the 3.0.0 handoff name this remainder.
  - Rationale (the user's words): accept it, "but with notes that if it occurs I will come back
    for a patch fix to tighten it up". The count is within run-to-run variance (1 to 7).
  - Trade-off: the "no ID used alone in chat" target is met everywhere except this sentence. A
    report of it in real use starts a 2.2.x patch.
  - Source: design.md PD1 · Decided 2026-09-30

- **D12 — Tick each design.md success criterion that the evidence supports.**
  - Each ticked box names its evidence. A box met with an exception names the decision (D5,
    D8, D10, D11). The `validate_project` criterion and the dictionary-skill criterion stay open,
    because no run or person has shown them yet. The token-cost criterion waits for the
    per-stage line in the CHANGELOG.
  - Rationale: a reader of the design sees what is met and where the proof is.
  - Trade-off: a ticked box with an exception reads as "met" at a glance. The note carries the
    exception.
  - Source: design.md PD2 · Decided 2026-09-30

- **D13 — Find the cause of the duplicate card after `/compact` before 2.2.0 ships.**
  - First, read the A3 session transcript. Each card prints its own plugin root in the
    `Full rules:` line, so two different roots mean two loaded copies of wb. If the transcript
    does not settle it, the user runs an interactive session with only `--plugin-dir` and runs
    `/compact`. A duplicate that remains goes upstream. A duplicate that goes away was the
    double load.
  - Rationale (the user's choice): know the cause before the release ships, not after.
  - Trade-off: a manual interactive step before release, for a cost of about 190 tokens after
    each compaction.
  - Update 2026-09-30: the transcript settled it, so no interactive run was needed. The second
    copy was the PreCompact output, which a manual `/compact` shows in its stdout. P8-T5 stops the
    card on PreCompact (`thoughts/2026-09-30-card-measurement.md`).
  - Source: design.md PD3 · Decided 2026-09-30

- **D14 — Document the new scripts and skill now, in two files shared with 3.0.0.**
  - `plugin/scripts/README.md` gets `wbte-dictionary`, `test-prime` and `test-wbte-dictionary`.
    `plugin/skills/help/SKILL.md` gets `/wb:wbte-dictionary`. This is an exception to D-Q3,
    which allows only link lines in the shared files.
  - Rationale (the user's choice): a user who reads `/wb:help` or the scripts README must find
    the new parts in 2.2.0, even at the cost of a merge conflict.
  - Trade-off: up to two new merge conflicts. The handoff gets a resolution note for each file
    that conflicts.
  - Source: design.md PD4 · Decided 2026-09-30

- **D15 — PR descriptions follow WBTE through three channels: the card, a reference section, and
  `/wb:pr-description`.**
  - No stage writes a PR description today. The harness default writes it, and only the card is
    in context at that moment. So a card rule names PR descriptions and commit messages and
    points to a new section, "Pull requests and commit messages", in `technical-english.md`.
  - The new skill `/wb:pr-description` drafts the title and body from the branch. It runs
    `gh pr create` or `gh pr edit` only after the user confirms, because a PR is outward-facing.
  - Rationale (the user's words): a teammate asked "Please stop sending me long AI diatribes
    for me to parse". PR descriptions must use WBTE and be "designed for brevity, simplicity
    and human consumption".
  - Trade-off: the card has 9 free words, so other card wording gets shorter. The card changes
    again after the A1 measurement.
  - Source: user request, 2026-09-30 · Decided 2026-09-30
- **D16 — The rule covers PR descriptions and commit messages.**
  - A commit subject has at most 72 characters and uses the imperative. A body is optional,
    has a few short lines, and says why.
  - Rationale: a long commit body is the same problem in a smaller place.
  - Source: user request, 2026-09-30 · Decided 2026-09-30
- **D17 — The repository's PR template sets the sections. Each section gets only as much text
  as its content needs, and the whole body aims to fit on one screen.**
  - The skill finds the repository's PR template in the places GitHub reads. If there is none,
    it uses a generic template that ships with the skill.
  - Each section is scoped to what a reviewer needs from it. A section with nothing to say is
    left out, or gets "None" if the template requires it. Detail goes behind a link to the plan
    or handoff, not into the body.
  - The target is one screen, about 150 to 250 words. It is a soft target: a complex change can
    be longer.
  - Rationale (the user's words): "per-section based on the existing pull request template per
    the repo we are in … Ideally the entire PR description with all sections fits inside a
    single fold of the screen (but not hard rule because some stuff is more complex)".
  - Trade-off: a soft target cannot be enforced exactly. The harness checker warns above the
    target and fails only on a clear diatribe.
  - Source: user request, 2026-09-30 · Decided 2026-09-30

## Scope Definition

### In Scope

- `plugin/docs/reference/technical-english.md`, the single authority for the rules.
- The rule card in `wb-prime.sh`, on every SessionStart source, with the `WB_TECH_ENGLISH=0`
  opt-out.
- Link lines in every output template and in each inline output step.
- A wb Technical English rewrite of the output templates that 3.0.0 does not change.
- The Objective 2 "lite" rewrite of skill, agent, and prompt files that 3.0.0 does not change,
  kept only where the harness shows no loss.
- Support for repo technical nouns in `.claude/wb/technical-nouns.md`.
- A user-invocable skill that helps the user extract their own dictionary copy.
- PR descriptions and commit messages in WBTE: a card rule, a reference section, and the
  `/wb:pr-description` skill (D15 to D17).
- The eval harness under `evals/`: fixture, stage prompts, STE metric checker, fidelity judge,
  and a before/after report.
- The 3.0.0 handoff document, the README section, the CHANGELOG 2.2.0 entry, and the version
  bump.

### Out of Scope

- Prose changes in the 48 shared files beyond one link line each. These wait for the first
  release after 3.0.0 (D-Q3).
- A prose rewrite of maintainer docs: README (beyond the new section), `CLAUDE.md`,
  `CHANGELOG.md` history, `docs/` (D-Q1).
- Any check at runtime, in the lint hook, or in CI (D-Q5).
- Any ASD rules text or dictionary content in the repo (D-Q2).
- Changes to parser tokens, ID shapes, or the journal heading contract.
- The missing 2.1.0 CHANGELOG entry on `main`. The 3.0.0 branch already has a reconstructed
  entry (research §7).

## Success Criteria

### Functional Requirements

- [x] Every session start prints the rule card. This includes startup, resume, and compact,
  with and without active plans, and with and without `.claude/wb/PRIME.md`.
  *(Evidence: `plugin/scripts/test-prime:81-113`, and A3 in an interactive session)*
- [x] `WB_TECH_ENGLISH=0` stops the card and changes nothing else in the hook output.
  *(Evidence: `test-prime:124-130`. The output is byte-identical to 2.1.1 in 8 payload cases,
  `validation-report.md`)*
- [x] Every output template and inline output step links to `technical-english.md`, and no
  other file restates the rules.
  *(Evidence: `python3 evals/link_check.py` passes on 43 templates and 4 inline steps)*
- [x] Generated documents from the harness fixture have no semicolons in prose.
  *(Met with the D8 exception: 9 remain, all from the shared `tasks.md` boilerplate.
  `thoughts/2026-09-30-objective-1-report.md`)*
- [x] Chat summaries from the harness fixture never use a task, question, or decision ID alone.
  *(Met with the D11 exception: 2 IDs in one sentence of the final run.
  `thoughts/2026-09-30-objective-1-report.md`)*
- [x] The share of generated sentences over 25 words is lower than the 2.1.1 baseline on the
  same fixture, and at most 5%.
  *(Evidence: 2.9% against 7.0% for 2.1.1, `thoughts/2026-09-30-objective-1-report.md`)*
- [ ] Documents generated after the change pass `validate_project`, and every parser pattern
  listed under Integration Points still matches.
  *(Open: `token_check.py` checks the parser patterns, and only the known missing git keys fail.
  No run has used the `validate_project` stage itself)*
- [ ] The dictionary skill produces a local copy from a user-supplied Issue 9 PDF, or says
  clearly which tool is missing.
  *(Open until the Phase 6 attestation. `test-wbte-dictionary` passes, and a development run of
  the script on the user's PDF gave 1,975 entries. Nobody has run the skill in a fresh session)*
- [x] The fidelity judge finds no lost facts, `file:line` references, IDs, or barriers in each
  accepted skill rewrite, over repeated runs.
  *(Met with the D10 exception: 1 repeat for each gate, not 3.
  `thoughts/2026-09-30-lite-verdicts.md`)*
- [x] The 3.0.0 handoff document exists and lists every item named under Integration Points.
  *(Evidence: `handoff-2026-09-30-wbte-for-3.0.0.md` has a section for each item)*

### Non-Functional Requirements

- [x] Token cost: the rule card adds at most about 200 tokens to each session. The change in
  per-stage cost is measured with `claude --plugin-dir plugin plugin details wb` and reported
  in the CHANGELOG.
  *(Evidence: the card is 141 words, about 190 tokens. The CHANGELOG 2.2.0 table reports the
  always-on and per-stage costs from `thoughts/2026-09-30-lite-verdicts.md`)*
- [x] Reliability: the hook contract is unchanged. It only reads, it always exits 0, and it
  stays inside the 5-second timeout.
  *(Evidence: `test-prime:152-172`. 200 plan directories take about 2.5 s, the same as 2.1.1)*
- [x] Compatibility: no new user requirement. The plugin works without python3, `pdftotext`,
  or the dictionary copy.
  *(Evidence: only the dictionary script and skill name python3 or `pdftotext`. Every harness
  run worked with no dictionary copy present)*
- [x] Merge: `git merge-tree` of 2.2.0 and the 3.0.0 branch shows conflicts only in link lines,
  `wb-prime.sh`, the manifests, `README.md`, and `CHANGELOG.md`.
  *(Met with the D5 exception: `.gitignore` and `.claude/wb/knowledge.md` also conflict. Both are
  append-only, and the handoff has their resolution notes)*
- [x] Legal: the repo contains no ASD rules text and no dictionary content. The name does not
  use the registered mark.
  *(Evidence: `link_check.py` finds no PDF or dictionary text. No `.pdf` or `.tsv` is tracked)*

## Risk Analysis

### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| The rule card does not change chat output enough | High | Med | The harness measures chat summaries before and after. The card wording is changed until the metrics move. |
| A template rewrite changes a token that a parser matches | High | Med | The exempt-token list in the reference doc. The harness runs `validate_project` and the parser patterns on generated documents. |
| A skill "lite" rewrite lowers stage behaviour | High | Med | Each rewrite is kept only if the harness shows no loss (the 2.0.0 R3/R4 precedent). |
| Simpler words remove technical precision ("dumbing down") | High | Med | Technical nouns and backticked code are allowed. The fidelity judge checks for lost facts. |
| The LLM judge is wrong | Med | Med | Mechanical checks run beside the judge. A human reads a sample of each report. Repeated runs, not one run. |
| Merge conflicts slow down 3.0.0 | High | Low | Link lines only in shared files, a small `wb-prime.sh` edit, the handoff document, and a `git merge-tree` check before release. |
| The card applies in repos and chats where the user does not want it | Med | Med | `WB_TECH_ENGLISH=0`. The README says how to turn it off. |
| Rule conflict with Output discipline ("one-line summary") | Med | High | The reference doc says how the two combine. Brevity stays, and fragments go. |
| Per-stage token cost grows because stages read one more file | Med | Med | The reference doc is short. The cost is measured and reported. |
| Trade mark or copyright problem | Med | Low | No ASD text in the repo, the name "wb Technical English", and a non-endorsement line. |

### Assumptions

| ID | Assumption | Validated? |
| -- | ---------- | ---------- |
| A1 | A short rule card at session start changes the style of chat output in a way the harness can measure. If not, Objective 1 needs a stronger channel for the conversation. | Validated 2026-09-30 |
| A2 | The model follows a link line at the top of a template when it writes the document. If not, the rules must go into the template text, and the 48 shared templates wait for the post-3.0.0 pass. | Validated 2026-09-30 — the model read the reference doc in 4 of 6 linked stage runs (`thoughts/2026-09-30-link-measurement.md`) |
| A3 | SessionStart output with `source=compact` reaches the model when no plan is active. The 2026-09-10 measurement covered only the case with an active plan (`wb-prime.sh:12-18`). If not, the card is lost after compaction in repos without plans. | Validated 2026-09-30 |
| A4 | Text extraction from the Issue 9 PDF keeps the dictionary entries usable (word, part of speech, approved or not, alternatives). If not, the dictionary skill offers only the approved-word list, or is dropped. | Validated 2026-09-30 — for word, part of speech and status. Alternatives are best-effort (see D4) |
| A5 | 3.0.0 does not restructure the orientation and recovery sections of `wb-prime.sh` before it merges. Today it adds only 4 comment lines. If it does, the card placement must be redone in the handoff. | Validated 2026-09-30 — for `adversarial-loop-skill-research` at `2fff76c`. P7-T4 checks again (see D5) |
| A6 | Headless `claude -p --plugin-dir <tree> --allowedTools=Skill` runs the stages well enough for before/after comparison (`.claude/wb/knowledge.md`, headless entry). If not, the harness needs a different driver. | Validated 2026-09-30 — with `--add-dir <tree>/plugin` and one fixed reply to `create_design`. On the large fixture, every stage spawned its agents (`thoughts/2026-09-30-lite-verdicts.md`, see D6) |

## Rejected Alternatives

### Option: Background writing skill (Option B)

- **Approach**: a `user-invocable: false` skill holds the rules. Skills link to it, and agents
  preload it with `skills:`.
- **Rejected because**: a skill loads only when its description matches, so it does not
  reliably cover the conversation between stages. Skill text does not survive compaction
  (`doc-adherence/SKILL.md:63-69`). The conversation is part of the priority objective.
- **Trade-offs**: no edit to `wb-prime.sh` and no per-session token cost, but weak coverage
  where the user feels the problem most.

### Option: The hook carries all the rules (Option C)

- **Approach**: the full rules go into the session-start output, with no reference doc.
- **Rejected because**: it has the highest token cost in every session and the largest edit to
  a file that 3.0.0 also changes.
- **Trade-offs**: one place to change and always present, but expensive and harder to merge.

### Option: Ship ASD text or the dictionary

- **Approach**: include ASD rules text or the 875-word dictionary in the plugin.
- **Rejected because**: ASD prohibits reproduction and distribution without written permission
  (research §6, D-Q2).
- **Trade-offs**: stronger enforcement, but a copyright problem.

### Option: A mechanical check at runtime or in CI

- **Approach**: report wb Technical English findings from the lint hook or from CI.
- **Rejected because**: it adds a user requirement or CI work, and it touches the lint-hook
  area that 2.1.1 just changed (D-Q5).
- **Trade-offs**: feedback while the user works, but a larger and riskier release.

### Option: Rewrite the 48 shared files now

- **Approach**: apply the rewrite to every file, and let 3.0.0 absorb the conflicts.
- **Rejected because**: it risks more adversarial-loop failures and could stall 3.0.0 (D-Q3).
- **Trade-offs**: consistent prose sooner, but a risk to the release that matters more now.

## Pending Decisions

| ID | Decision Needed | Blocks | State |
| -- | --------------- | ------ | ----- |
| PD1 | In the final P4-T9 run, 2 chat IDs are still used alone, in one `create_tasks` summary sentence. Accept this for 2.2.0, or change the card or `plan-presentation-message.md` and measure again (about $4.50 and 15 minutes a run)? | the Phase 4 attestation | Resolved 2026-09-30 → design.md (## Technical Decisions) |
| PD2 | Every box under Success Criteria in this document is `[ ]`. Tick each box that the evidence supports, with a pointer to the evidence, and leave the rest open? Or leave all of them as they are? | closing the plan | Resolved 2026-09-30 → design.md (## Technical Decisions) |
| PD3 | After `/compact`, the card is in the context twice (the A3 finding). `plugin.json` registers `wb-prime.sh` once for SessionStart, so the cause is probably in the harness. Investigate before 2.2.0 ships, or keep it as a follow-up? | none (post-compaction token cost only) | Resolved 2026-09-30 → design.md (## Technical Decisions) |
| PD4 | `plugin/scripts/README.md` does not document `wbte-dictionary`, `test-prime` or `test-wbte-dictionary`, and `help/SKILL.md` does not name `/wb:wbte-dictionary`. Both files are shared with 3.0.0. Add the lines now, with a new merge conflict, or list them in the 3.0.0 handoff for the post-3.0.0 pass? | none | Resolved 2026-09-30 → design.md (## Technical Decisions) |

The version number of the post-3.0.0 pass (3.0.1 or 3.1.0) is still open (D-Q3). It blocks
nothing in 2.2.0, so it is a note and not a pending decision. The handoff document calls it
"the first release after 3.0.0".

## References

- Research: [research.md](research.md)
- Precedent: `plugin/docs/reference/branch-naming.md` (2.1.0)
- Hook: `plugin/hooks/wb-prime.sh`
- Measurement precedent: `docs/plans/2026-09-08-upstream-fable-merge/` (2.0.0 blind trials R3,
  R4, and the token-cost baseline)
- ASD-STE100 Issue 9: <https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf>
