# wb Technical English (WBTE) — the shipped writing rule

**Read this when a step directs you to.** It is the plugin's single authority on how workbench
output must read. Skills and templates link here. They do not restate these rules.

## Credit and scope

Adapted from the principles of ASD-STE100 Issue 9. Not endorsed by ASD, and not ASD-STE100
compliant.

WBTE is a workbench variant. It keeps the aims of the source standard: one meaning for each
word, short sentences, and no ambiguity. It changes and adds rules where AI-led software
engineering needs them. This file contains no text from the standard and no part of its
dictionary.

WBTE applies to two surfaces:

1. **Output.** This is the text that a person reads: plan documents, handoffs, reports, chat
   summaries, and the conversation. All of the output rules apply.
2. **Instructions.** This is the text that a model reads: skills, agents, and prompts. Only the
   "lite" rules apply, and only where a measurement shows no loss.

## Output rules

Apply these rules to every sentence of output.

1. Write one instruction in each sentence. Use the imperative for an instruction.
2. Put a condition first, then a comma, then the instruction. Example: "If the test fails,
   stop the phase."
3. Write at most 20 words in an instruction sentence.
4. Write at most 25 words in a descriptive sentence.
5. Count each item in backticks as one word. Count a number with its unit as one word.
6. Write at most 6 sentences in a paragraph. Give each paragraph one topic.
7. Use the active voice. Use the passive voice only when the agent is not known.
8. Use simple tenses: present, past, and future. Do not use perfect or progressive tenses
   when a simple tense gives the same meaning.
9. Do not use semicolons in prose. Write two sentences.
10. Do not omit words. Keep articles and verbs. Do not write telegraphic fragments such as
    "Done, tests green, next P2".
11. Do not use a noun cluster of more than 3 words, unless the cluster is a technical noun.
12. Give the result first. Then give the reason.
13. Use one word for one meaning. When you name a thing, use the same name every time.
14. Keep the structure of tables, headings, code blocks, and checklists. Apply the sentence
    rules to the prose inside them.
15. Keep specific values. Do not replace a number, a name, or a `file:line` from the research
    with a general phrase. Write "3 attempts (`config.py:4`)", not "the current default".

## Instruction rules ("lite")

These rules apply to skill, agent, and prompt text. Each rule is optional. Keep the old text
when the eval harness shows that the change makes a stage worse.

1. Prefer short sentences. Split a sentence of more than 25 words when the split keeps the
   meaning.
2. Prefer one instruction in each sentence.
3. Replace a semicolon with a full stop when the two parts are complete sentences.
4. Use the active voice and the imperative for steps.
5. Use one term for one concept in a file.
6. Keep barriers, checkpoints, "Read [link] NOW" directives, and capitalized scope rules as
   they are. Measurements showed that trimming them makes results worse.

## Technical nouns

A technical noun is a term that the reader may see without an explanation. Use these wb terms
as they are:

- WBTE, stage, plan directory, barrier, checkpoint, phase, task, task ID, checkbox
- frontmatter, counter, journal, journal entry, handoff, knowledge entry
- research, design, execution plan, template, fragment, worker, verifier
- skill, agent, hook, rule card, reference doc, exempt token
- commit, branch, working tree, diff, pull request

Also treat these as technical nouns:

- Text in backticks: code, file paths, commands, flags, and literal values.
- The names of tools, languages, and file formats, for example Git, Python, and YAML.
- Common software terms, for example API, database, file, interface, metadata, prompt, and
  token.

Define any other term at its first use, or replace it with a simple word.

## Shorthand and IDs

**In chat, never use an ID alone.** Pair each task, question, assumption, or decision ID with a
short meaning. Write "P1-T3 (the driver probe) passed", not "P1-T3 passed". This applies to
`P1-T3`, `Q2`, `A1`, `PD1`, `D-Q3`, `UIQ2`, and every other ID shape.

- Give the meaning once in each paragraph, at the first mention. A later mention in the same
  paragraph does not repeat it. A new paragraph gives it again.
- An ID inside the meaning of another ID needs no meaning of its own, for example
  "P1-T2 (the A1 check)".
- An ID range can stay bare, for example "P0-T1 to P0-T4" or "A1–A3".

**In documents, keep IDs.** Parsers and validators depend on them. A document does not explain
an ID at each use. The table or list that defines the ID gives its meaning.

**Do not use unexplained shorthand in prose.** This includes these forms:

- An abbreviation that is not a technical noun.
- A symbol used as a word, for example "→" for "then" or "w/" for "with".
- A clipped form, for example "impl", "config", or "repo" in running text.

## Exempt tokens

Parsers and validators match the strings below. Keep each one exactly as it is, also when you
rewrite the prose around it. The sentence rules do not apply to these strings.

**Task lines** (`plugin/hooks/wb-prime.sh:131-136`, `plugin/skills/daily-digest/sources.md:67-68`,
`plugin/skills/validate_project/reference/validation-rules.md:71,104,116`,
`plugin/skills/implement/SKILL.md`, Step 6a, the checkbox check):

- The task-ID shape `[A-Z0-9-]*[0-9][A-Z0-9-]*`. An ID must contain at least one digit.
- A task line starts `- [ ] **ID**` or `- [x] **ID**`. The patterns are
  `^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*` and `^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*`.
- Any checkbox line matches `^- \[[ x]\] .*$`.
- The completion stamp `(completed YYYY-MM-DD HH:MM)`. The digest matches
  `^- \[x\] .*\(completed <date>` (`plugin/skills/daily-digest/sources.md:74`).

**Frontmatter** (`plugin/hooks/wb-prime.sh:83,133`,
`plugin/skills/validate_project/reference/validation-rules.md:22-23,40-44`):

- The hook reads `status:` and `current_phase:` from the first 30 lines.
- Every document needs `project`, `created`, `status`, `last_updated`, `git_commit`, and
  `git_branch`.
- `tasks.md` also needs `task_tracking`, `current_phase`, `total_tasks`, and `completed_tasks`.
  The value `task_tracking: markdown-checkboxes` stays as it is.
- The `status:` values are these:
  - `research.md`: `draft`, `in-progress`, `complete`
  - `design.md`: `draft`, `approved`
  - `tasks.md`: `not-started`, `in-progress`, `complete`

**Journal headings** (`plugin/hooks/wb-prime.sh:154,163-165`,
`plugin/skills/implement/SKILL.md`, Step 5, *Open a journal entry first*,
`plugin/skills/validate_project/reference/validation-rules.md:92,98`,
`plugin/skills/daily-digest/sources.md:77`):

- The shape is `## YYYY-MM-DD HH:MM — <label> (open)` or `## YYYY-MM-DD HH:MM — <label> (closed)`.
- The heading ends in `(open)` or `(closed)`. The validator matches `\((open|closed)\)\s*$` and
  `\(open\)\s*$`.
- The hook reads lines that match `^##`. It skips headings that contain `[YYYY`, `<YYYY`, or
  `YYYY-MM-DD`. So example headings keep the literal placeholder `YYYY-MM-DD`.
- The digest searches journals for the literal string `OPEN`.

**Knowledge entries** (`plugin/hooks/wb-prime.sh:195`): each entry has a line that starts
`- **Verified**`.

**Blockers** (`plugin/skills/daily-digest/sources.md:80`): the section heading
`### Current Blockers`, which ends at the next `###` heading.

**Checkpoints** (`plugin/skills/validate_project/reference/validation-rules.md:129-140`):

- The heading starts `### ⛔ CHECKPOINT:`.
- Each block has at least 4 labels, `**(derivable)**` or `**(attestation)**`, and at least one
  `(attestation)`.
- Each block contains the sentence `Go by the label, never by position`.
- A checkpoint block never contains a line with the task-line shape.

**Planning records** (`plugin/skills/validate_project/reference/validation-rules.md:172-178`,
`plugin/skills/resolve_questions/SKILL.md:190`):

- Question IDs match `^Q\d+$`, in the table under `## Open Questions`.
- Assumption IDs have the shape `A1`, under `### Assumptions`. Pending-decision IDs have the
  shape `PD1`, under `## Pending Decisions`. Mockup question IDs have the shape `UIQ1`.
- A question state is `Open` or starts with `Resolved`. A resolved state names `design.md`:
  `Resolved YYYY-MM-DD → design.md (## Technical Decisions)`.
- An assumption state is `Validated YYYY-MM-DD` or `Invalid — <note>`.

**Verifier reports** (`plugin/agents/task-verifier.md:140,158`,
`plugin/skills/implement/SKILL.md`, Step 6b, the status parse): the headings `### Status: PASS`,
`### Status: FAIL`, and `### Baseline failures`.

**Placeholders** (`plugin/skills/validate_project/reference/validation-rules.md:196`): the
validator searches for `[To be added]`, `[TBD]`, `[TODO]`, and `[Fill this in]`. Keep these
strings exact in templates, so that the validator still finds an unfilled section.

**Completion lines**: the shape `✅ <artifact> — <summary>. Next: /wb:<stage>` stays. No parser
reads it, but users know it. Apply the sentence rules to the words inside the shape.

## WBTE and Output discipline

Output discipline decides how much to say. WBTE decides how to say it. The two rules do not
conflict:

- A one-line summary stays one line. Write it as a complete sentence, not a fragment.
- Say only what the user must act on. Say it in plain words, with no unexplained IDs.
- Do not repeat a document in chat. The document itself follows WBTE.

## Pull requests and commit messages

A PR description and a commit message are output. A reviewer reads them between other work, so
keep them short. All the output rules apply. `/wb:pr-description` drafts a PR title and body
with these rules.

**PR descriptions:**

1. Use the repository's PR template. `plugin/scripts/pr-template` finds it in the places that
   GitHub reads. If the repository has no template, use the generic template of
   `/wb:pr-description`.
2. Keep the template's headings in their order. Do not add headings.
3. Write each section for what a reviewer needs from it. Give the change first, then the reason.
4. If a section has nothing to say, leave it out. If the template requires it, write "None."
5. Aim for one screen: about 150 to 250 words for the whole body. A complex change can be
   longer. Put the detail behind a link to the plan, the handoff, or the ticket.
6. Do not describe each file or each commit. The diff and the log show them.
7. Do not paste plan text, tables of metrics, or test logs. Give the one number that matters,
   and link to the rest. If a number comes from an earlier run, say which one.
8. Write the title in the imperative, in at most 72 characters. Name the change. Keep a ticket
   key prefix if the repository uses one.
9. Keep these exactly as they are: attribution lines, closing keywords such as `Closes #12`,
   the template's checklists and their checkboxes, and ticket links.
10. Never write secrets, credentials, or personal data. In a healthcare repository, this
    includes patient identifiers and member IDs.

**Commit messages:**

1. Write the subject in the imperative, in at most 72 characters, with no full stop. Keep a task
   ID or ticket key prefix where the workflow requires it, for example `P8-T5: …`.
2. A body is optional. If you write one, write a few short lines that say why, not what.
3. Keep trailer lines exactly as they are, for example `Co-Authored-By:`.

## Optional dictionary

The source standard has a dictionary of approved words. ASD does not permit redistribution of
it, so the plugin does not ship it. A user can make a private copy from their own free copy of
the standard. The copy lives outside every repository, at `~/.claude/wb/wbte-dictionary.tsv`.
To make it, run `/wb:wbte-dictionary <path-to-the-pdf>`. The skill runs
`plugin/scripts/wbte-dictionary`, and the file has the columns word, pos, status (`approved` or
`not approved`), and alternatives. The alternatives column is best-effort.

If the copy exists and you are not sure about a word, look up that one word:

```bash
grep -i $'^<word>\t' ~/.claude/wb/wbte-dictionary.tsv
```

Never load the whole dictionary into context. Never copy entries into a repository. If the
copy does not exist, apply the rules without it.

## Repo terms

A repository can list its own technical nouns in `.claude/wb/technical-nouns.md`, one term on
each line. If the file exists, treat those terms as technical nouns. Define any other project
term at its first use, or replace it with a simple word.
