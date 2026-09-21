# Validation Rules

## Which contract to validate against

```javascript
// A remediation plan has only `tasks.md`, and that is correct. `adversarial-review` Step 8
// writes `docs/plans/<plan>/reviews/<date>-round-N/tasks.md`; a review is not a project, so it
// has no research or design stage. Recognise one by a `reviews:` key in its frontmatter or a
// `reviews/<date>-round-N/` path, and take `tasks.md` alone as the whole plan.
//
// This switches the contract; it does not switch validation off. Everything gated on isRound
// below is a rule that can only be about a second file — asserting it against a round produces
// a critical error on the exact shape /wb:implement and /wb:update_status now accept, and
// buries the round's real defects under three that cannot be acted on. What a round IS checked
// against is `validateRoundStructure` at the end of this section, plus every task-tracking rule
// unchanged: the checkboxes are the whole plan there, so they matter more, not less.
const isRound =
  (tasksFrontmatter && 'reviews' in tasksFrontmatter) ||
  /(^|\/)reviews\/[^/]+-round-\d+\/?$/.test(projectDir);
```

## File Structure Validation

```javascript
// Required files. A round has no research or design stage to require files from.
const requiredFiles = isRound
  ? ['tasks.md']
  : ['research.md', 'design.md', 'tasks.md'];

// Check each exists
for (const file of requiredFiles) {
  if (!exists(`${projectDir}/${file}`)) {
    ERROR(`Missing required file: ${file}`);
  }
}
```

## Frontmatter Validation

```javascript
// Required fields per file
const requiredFields = {
  all: ['project', 'created', 'status', 'last_updated', 'git_commit', 'git_branch'],
  tasks: ['task_tracking', 'current_phase', 'total_tasks', 'completed_tasks'],
  // A round's frontmatter is the set `adversarial-review` Step 8 writes, and nothing else.
  // `last_updated`, `git_commit`, `git_branch` and `current_phase` are absent BY DESIGN —
  // a round has one implicit phase and is written in one sitting — so demanding them reports
  // four missing fields on a correctly generated file.
  round: ['project', 'reviews', 'round', 'created', 'status',
          'task_tracking', 'total_tasks', 'completed_tasks']
};

// Parse YAML frontmatter
const frontmatter = parseYAML(fileContent);

// Check required fields. BOTH lists — `tasks` was declared and never iterated, so a
// tasks.md missing `total_tasks` was not reported as a missing field at all; it fell through
// to the counter-drift check and surfaced as "frontmatter says undefined/undefined", which
// points the reader at /wb:update_status instead of at the absent field.
// Note `!frontmatter[field]` is deliberate rather than a presence test: `completed_tasks: 0`
// is legitimately falsy, so check the key's existence, not its truthiness.
const fieldsFor = (file) =>
  isRound ? requiredFields.round
  : file === 'tasks.md' ? [...requiredFields.all, ...requiredFields.tasks]
  : requiredFields.all;

for (const field of fieldsFor(currentFile)) {
  if (!(field in frontmatter)) {
    ERROR(`Missing required field: ${field}`);
  }
}
```

## Status Validation

```javascript
const validStatuses = {
  research: ['draft', 'in-progress', 'complete'],
  design: ['draft', 'approved'],   // approved is what create_tasks and forge gate on
  tasks: ['not-started', 'in-progress', 'complete']
};

// Check status is valid
if (!validStatuses[fileType].includes(status)) {
  ERROR(`Invalid status: ${status}. Must be one of: ${validStatuses[fileType]}`);
}

// Check status progression. Both rules compare two documents, so neither has anything to say
// about a round — `design.status` there is undefined, and an unguarded comparison either throws
// or reports a design that was never supposed to exist.
if (!isRound) {
  if (design.status === 'approved' && research.status !== 'complete') {
    ERROR('Design cannot be approved while research is not complete');
  }

  if (tasks.status === 'in-progress' && design.status === 'draft') {
    ERROR('Tasks cannot be in-progress while design is still draft — ' +
          'approve the design at /wb:create_design Step 6, or explain why work started early');
  }
}

// design.md has no 'complete': it is draft or approved, and stays approved once the work
// built on it lands. Completion is tasks.md's state, not the design's.
```

## Task Tracking Validation

```javascript
// The checkboxes are the record. These checks ask whether the record is well-formed
// and whether the derived counters agree with it — never whether some other system agrees.

// Scoped to the ID shape. An unscoped /^- \[[ x]\] / also matches success criteria,
// prerequisites and checkpoint boxes — on this repository's own plan that is 149 lines
// against 50 real tasks — and the drift check below would then report correct counters as
// wrong and tell the user to overwrite them. validation-checklist.md states the same rule,
// and SKILL.md calls the unscoped form "the mistake that makes every counter look drifted".
const taskLines = tasksContent.match(/^- \[[ x]\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*/gm) || [];
const done = taskLines.filter(l => l.startsWith('- [x]')).length;
const total = taskLines.length;

if (!tasksFrontmatter.task_tracking) {
  ERROR('tasks.md does not declare task_tracking — a pre-2.0.0 plan, or a malformed one');
}

// Counters are a derived cache with one writer. Drift is expected between checkpoints;
// it is a WARNING pointing at /wb:update_status, never an ERROR, and the counts win.
if (tasksFrontmatter.completed_tasks !== done || tasksFrontmatter.total_tasks !== total) {
  WARNING(
    `Counter drift: frontmatter says ${tasksFrontmatter.completed_tasks}/${tasksFrontmatter.total_tasks}, ` +
    `checkboxes say ${done}/${total}. The checkboxes are correct. Run /wb:update_status.`
  );
}

// Journal entry headings carry the open/closed state in a trailing marker. Every consumer
// matches on that suffix, so a heading without it reads as closed — which is the dangerous
// direction: interrupted work reported as finished.
// journal.md is OPTIONAL — the checklist marks it so, and plans predating journals have none.
// Reading it unconditionally threw before any journal check could run, and took the rest of
// the validation with it.
const journalPath = `${projectDir}/journal.md`;
if (!exists(journalPath)) {
  INFO('journal.md absent — journal checks skipped (optional; plans predating it have none)');
} else {
const journalLines = readLines(journalPath);

// A heading must start at column zero. Both readers anchor on that — the session-start hook
// greps `^## ` and the filter below uses startsWith — so an indented heading is invisible to
// BOTH, and the validator would otherwise report clean on a file the hook silently misreads.
// This is the one journal defect that hides from its own checker.
const indentedHeadings = journalLines.filter(l => /^[ \t]+#{2,}\s/.test(l));
if (indentedHeadings.length) {
  ERROR(`journal.md has ${indentedHeadings.length} indented heading(s): ` +
        indentedHeadings.map(h => h.trim()).join(', ') +
        ` — invisible to the session-start hook and to every check below. ` +
        `Headings start at column zero; see plugin/docs/reference/journal-entries.md`);
}

const journalHeadings = journalLines.filter(l => l.startsWith('## '));

// Placeholder headings from the template are not entries — the session-start hook discards them
// the same way, so this filter must match it or a fresh plan reports forever. Everything below
// works on realHeadings, in file order, newest first.
const realHeadings = journalHeadings.filter(h => !/\[YYYY|<YYYY|YYYY-MM-DD/.test(h));

const malformed = realHeadings.filter(h => !/\((open|closed)\)\s*$/i.test(h));
if (malformed.length) {
  ERROR(`journal.md heading(s) missing a trailing (open) or (closed): ` +
        malformed.join(', ') +
        ` — invisible to the session-start hook and every other reader`);
}

// Only the NEWEST entry may be open. A stale (open) heading further down is what a
// second-heading close leaves behind, and the common case leaves exactly one — so a bare
// count never fires on it. Check position, not quantity.
//
// Exempt `[blocked]`. A blocked entry is deliberately left open while work continues past it
// (implement Step 6c), so it sits below a newer entry by design. Without this the check fires
// on a state the workflow created on purpose AND names the wrong cause, and a check that cries
// wolf on correct files stops being read. The marker sits before the suffix, so the heading
// still ends in `(open)` and every reader that anchors on that suffix is undisturbed.
const staleOpen = realHeadings.slice(1)
  .filter(h => /\(open\)\s*$/i.test(h) && !/\[blocked\]\s*\(open\)\s*$/i.test(h));
if (staleOpen.length) {
  ERROR(`journal.md has ${staleOpen.length} stale open entr(y|ies) below the newest: ` +
        staleOpen.join(', ') +
        ` — closed by writing a second heading instead of editing in place. ` +
        `If the work is genuinely blocked, mark the heading ` +
        `\`<label> [blocked] (open)\` instead. ` +
        `See plugin/docs/reference/journal-entries.md`);
}
}  // end: journal.md present

// ---------------------------------------------------------------------------
// Checklist §7 and §8 — Dependencies and cross-file consistency. Both are about relationships
// BETWEEN documents, so both are phased-only: a round has one file, no upstream sibling to
// point `depends_on` at, and nothing to be consistent with. Its upstream is the parent plan,
// named by `reviews:` and resolved in validateRoundStructure below.
// ---------------------------------------------------------------------------
if (!isRound) {

// Checklist §7 — Dependencies. Declared in validation-checklist.md and previously
// unimplemented, so the chain it describes was never actually checked.
//
// A YAML scalar is legitimate here and is what BOTH shipped design templates emit
// (`depends_on: research.md`); only the tasks template uses flow-sequence syntax. Requiring
// an array made this rule ERROR on every plan the plugin itself generates. Normalise instead
// of rejecting — the rule's job is the dependency chain, not the spelling.
const dependsOn = (fm) => {
  const d = fm.depends_on;
  if (Array.isArray(d)) return d;
  if (typeof d === 'string') return d.split(',').map(x => x.trim()).filter(Boolean);
  return [];
};

if (!dependsOn(designFrontmatter).includes('research.md')) {
  ERROR('design.md does not list research.md in depends_on — the chain research → design → tasks is what tells a resuming session which document is upstream');
}
for (const dep of ['research.md', 'design.md']) {
  if (!dependsOn(tasksFrontmatter).includes(dep)) {
    ERROR(`tasks.md does not list ${dep} in depends_on`);
  }
}

// Checklist §8 — Cross-file consistency. Same: declared, never implemented.
// Git metadata is compared for PRESENCE and branch agreement only. git_commit
// legitimately differs between files — each records the commit current when that
// file was last written — so comparing those would fire on every healthy plan.
// ---------------------------------------------------------------------------
const allFm = { 'research.md': researchFrontmatter, 'design.md': designFrontmatter, 'tasks.md': tasksFrontmatter };

const projects = new Set(Object.values(allFm).map(f => f.project));
if (projects.size > 1) {
  ERROR(`project name differs across files: ${[...projects].join(' / ')}`);
}

const tickets = new Set(Object.values(allFm).map(f => f.ticket).filter(t => t != null && t !== 'null'));
if (tickets.size > 1) {
  ERROR(`ticket differs across files: ${[...tickets].join(' / ')}`);
}

const branches = new Set(Object.values(allFm).map(f => f.git_branch).filter(Boolean));
if (branches.size > 1) {
  WARN(`git_branch differs across files (${[...branches].join(' / ')}) — expected when a plan spans branches, worth a look when it does not`);
}

// §4's last_updated agreement. A WARNING, not an error: files are legitimately written at
// different times within a session, and "or close" is what the checklist says.
const updated = new Set(Object.values(allFm).map(f => f.last_updated).filter(Boolean));
if (updated.size > 2) {
  WARN(`last_updated spans ${updated.size} dates (${[...updated].sort().join(', ')}) — the plan may have been partially updated`);
}

}  // end: phased-project-only (§7, §8)

// ---------------------------------------------------------------------------
// Checklist §9 — the round's own contract. This is what replaces §2's `all` list, §6, §7 and
// §8 on a round. It is short on purpose: a round is one file. But a branch that validated
// nothing would trade a false positive for a blind spot on the only file the plan has, and the
// task-tracking rules above — which a round needs MORE than a phased plan does, because there
// is no design.md to fall back on — run unchanged either way.
// ---------------------------------------------------------------------------
function validateRoundStructure() {
  // `reviews` is the round's only link back to the plan under review. A round whose parent
  // cannot be resolved is unreadable to everyone downstream, and the path is written by hand.
  const parent = tasksFrontmatter.reviews;
  if (parent && !exists(parent)) {
    ERROR(`reviews: points at ${parent}, which does not exist — a round whose parent plan ` +
          `cannot be resolved has no context for any of its findings`);
  }

  // `round` and the directory's `-round-N` are cited interchangeably from commits and journals.
  const dirRound = (projectDir.match(/-round-(\d+)\/?$/) || [])[1];
  if (dirRound && Number(tasksFrontmatter.round) !== Number(dirRound)) {
    WARNING(`round: ${tasksFrontmatter.round} but the directory says round ${dirRound}`);
  }

  // A round has one implicit phase under `## Tasks` — there is no `## Phase N` heading and no
  // current_phase, by design. Check the section exists; do not check for a phase.
  if (!/^## Tasks\s*$/m.test(tasksContent)) {
    ERROR(`tasks.md has no '## Tasks' section — adversarial-review Step 8 writes the round's ` +
          `task lines under it, and every reader of the round looks for it there`);
  }
}

if (isRound) validateRoundStructure();

// Current phase must name a phase that exists. Inert on a round twice over — no `## Phase N`
// headings and no `current_phase` key — so it needs no guard, and must keep both conditions.
const phaseHeadings = tasksContent.match(/^## Phase (\d+)/gm) || [];
const phaseNumbers = phaseHeadings.map(h => parseInt(h.match(/(\d+)/)[1], 10));
if (phaseNumbers.length && tasksFrontmatter.current_phase != null &&
    !phaseNumbers.includes(Number(tasksFrontmatter.current_phase))) {
  ERROR(`current_phase is ${tasksFrontmatter.current_phase}, but tasks.md defines phases ${phaseNumbers.join(', ')}`);
}

// IDs must be present and unique — they are cited from commits, journals and handoffs.
// Every bold-prefixed checkbox line is a candidate task; `taskLines` is the subset whose ID
// carries a digit. Narrowing taskLines without narrowing this made it a SUBSET of ids, so the
// subtraction went negative — `-1 task(s) have no local ID` — and the check became
// structurally dead: taskLines only ever contains lines that already have a conforming ID, so
// a task without one could never be counted. Compare against the candidates, not the survivors.
const candidates = [...tasksContent.matchAll(/^- \[[ x]\] \*\*([A-Z0-9-]+)\*\*/gm)].map(m => m[1]);
const ids = candidates.filter(id => /[0-9]/.test(id));
const idless = candidates.filter(id => !/[0-9]/.test(id));
if (idless.length) {
  WARNING(`${idless.length} task(s) have an ID with no digit — invisible to every counter: ` +
          idless.join(', '));
}
const dupes = ids.filter((id, i) => ids.indexOf(id) !== i);
if (dupes.length) {
  ERROR(`Duplicate task IDs: ${[...new Set(dupes)].join(', ')}`);
}

// Shape, not just presence. Counters identify task lines by this pattern, so an ID
// that does not match is not a style issue — the task vanishes from every count,
// and nothing errors. This is the one ID rule worth failing a validation over.
const badShape = ids.filter(id => !/^[A-Z0-9-]*[0-9][A-Z0-9-]*$/.test(id));
if (badShape.length) {
  ERROR(
    `Task IDs not matching [A-Z0-9-]*[0-9][A-Z0-9-]* (need at least one digit): ` +
    `${badShape.join(', ')}. These tasks are invisible to /wb:update_status, status-sync ` +
    `and the session-start bootstrap.`
  );
}

// Every phase checkpoint must carry the full block: the (derivable)/(attestation) labels and
// the go-by-the-label rule. The template states the block once; a generated plan that
// abbreviates later checkpoints leaves a reader at Phase 4 with four boxes and no instruction
// for reading them — which is how the human sign-off box gets ticked by position.
const checkpointBlocks = splitOn(tasksContent, /^### ⛔ CHECKPOINT:/m);
for (const block of checkpointBlocks) {
  const labels = (block.match(/\*\*\((derivable|attestation)\)\*\*/g) || []).length;
  if (labels < 4 || !/\(attestation\)/.test(block)) {
    WARNING(`Checkpoint "${block.heading}" is missing (derivable)/(attestation) labels — abbreviated block`);
  }
  if (!/Go by the label, never by position/.test(block)) {
    WARNING(`Checkpoint "${block.heading}" omits "Go by the label, never by position"`);
  }
  if (/^- \[[ x]\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*/m.test(block)) {
    ERROR(`Checkpoint "${block.heading}" contains a task-ID-shaped line — it will inflate the task count`);
  }
}

// Status must not contradict the checkboxes.
if (tasksFrontmatter.status === 'not-started' && done > 0) {
  ERROR(`tasks.md status is not-started but ${done} task(s) are [x]`);
}
if (tasksFrontmatter.status === 'complete' && done < total) {
  ERROR(`tasks.md status is complete but ${total - done} task(s) are still [ ]`);
}

// Stale pre-2.0.0 guidance actively misleads a reader about where status lives.
// Match on meaning, not on a fixed string list: flag any instruction asserting that the
// checkboxes are documentation-only, that they must not be updated or consulted for status,
// or that status is authoritative in some system outside this file. The wording varies by
// vintage; the claim is what matters.
for (const claim of findStatusDisclaimers(tasksContent)) {
  ERROR(
    `tasks.md line ${claim.line} tells the reader status does not live in these checkboxes ` +
    `("${claim.excerpt}"). It does. This plan predates 2.0.0 — delete the note.`
  );
}
```

## Planning Record Validation

```javascript
// D6: questions, assumptions and pending decisions are markdown records with local IDs.
// There are no issue IDs to resolve, so the checks are about shape and staleness.
//
// Every rule here parses researchContent or designContent, so the whole section is
// phased-only. On a round both are undefined: unguarded, this throws and takes the rest of
// the validation with it — the same failure the journal check had before it was made optional.
if (!isRound) {

const openQuestions = parseTable(researchContent, '## Open Questions');
for (const row of openQuestions) {
  if (!/^Q\d+$/.test(row.id)) {
    WARNING(`Open question has no stable local ID: "${row.question?.slice(0, 50)}"`);
  }
  if (!row.state) {
    WARNING(`Open question ${row.id} has no state (Open / Resolved …)`);
  }
  if (/^Resolved/.test(row.state) && !/design\.md/.test(row.state)) {
    WARNING(`${row.id} is resolved but does not point at where the decision was recorded`);
  }
}

const pending = parseTable(designContent, '## Pending Decisions');
for (const row of pending) {
  const stillOpen = !/resolved/i.test(row.blocks);
  if (stillOpen && /execution/i.test(row.blocks) && tasksFrontmatter.status === 'in-progress') {
    WARNING(`${row.id} says it blocks execution start, but tasks.md is already in-progress`);
  }
}

}  // end: phased-project-only (§6)
```

## Content Validation

```javascript
// Check for placeholders
const placeholders = ['[To be added]', '[TBD]', '[TODO]', '[Fill this in]'];

for (const placeholder of placeholders) {
  if (fileContent.includes(placeholder)) {
    WARNING(`Found placeholder text: ${placeholder} in ${filename}`);
  }
}

// Check for empty sections
const sections = extractSections(fileContent);
for (const section of sections) {
  if (section.content.trim().length < 50) {
    WARNING(`Section appears empty or very short: ${section.title}`);
  }
}
```
