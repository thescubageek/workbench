# Validation Rules

## File Structure Validation

```javascript
// Required files
const requiredFiles = ['research.md', 'design.md', 'tasks.md'];

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
  tasks: ['task_tracking', 'current_phase', 'total_tasks', 'completed_tasks']
};

// Parse YAML frontmatter
const frontmatter = parseYAML(fileContent);

// Check required fields
for (const field of requiredFields.all) {
  if (!frontmatter[field]) {
    ERROR(`Missing required field: ${field}`);
  }
}
```

## Status Validation

```javascript
const validStatuses = {
  research: ['draft', 'in-progress', 'complete'],
  design: ['draft', 'ready', 'implementing', 'complete'],
  tasks: ['not-started', 'in-progress', 'complete']
};

// Check status is valid
if (!validStatuses[fileType].includes(status)) {
  ERROR(`Invalid status: ${status}. Must be one of: ${validStatuses[fileType]}`);
}

// Check status progression
if (design.status === 'ready' && research.status === 'draft') {
  ERROR('Design cannot be ready if research is still draft');
}

if (tasks.status === 'in-progress' && design.status === 'draft') {
  ERROR('Tasks cannot be in-progress if design is still draft');
}

if (design.status === 'complete' && tasks.status !== 'complete') {
  ERROR('Design cannot be complete if tasks are not complete');
}
```

## Task Tracking Validation

```javascript
// The checkboxes are the record. These checks ask whether the record is well-formed
// and whether the derived counters agree with it — never whether some other system agrees.

const taskLines = tasksContent.match(/^- \[[ x]\] .*$/gm) || [];
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
const journalHeadings = readLines(`${projectDir}/journal.md`).filter(l => l.startsWith('## '));
const malformed = journalHeadings.filter(h => !/\((open|closed)\)\s*$/i.test(h));
if (malformed.length) {
  ERROR(`journal.md heading(s) missing a trailing (open) or (closed): ` +
        malformed.join(', ') +
        ` — invisible to the session-start hook and every other reader`);
}
const openCount = journalHeadings.filter(h => /\(open\)\s*$/i.test(h)).length;
if (openCount > 1) {
  WARN(`journal.md has ${openCount} open entries; only the most recent should be open`);
}

// IDs must be present and unique — they are cited from commits, journals and handoffs.
const ids = [...tasksContent.matchAll(/^- \[[ x]\] \*\*([A-Z0-9-]+)\*\*/gm)].map(m => m[1]);
if (ids.length !== taskLines.length) {
  WARNING(`${taskLines.length - ids.length} task(s) have no local ID`);
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
