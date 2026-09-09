# validate_project — reference

Read the **section you need**, when its step directs you to.

Sections: `Validation Checklist` (Step 3) · `Validation Rules` (Step 3) ·
`Important Guidelines` · `Configuration`

## Validation Checklist

The skill validates the following aspects.

### 1. File Structure

- ✅ research.md exists
- ✅ design.md exists
- ✅ tasks.md exists
- ⚠️ Optional: journal.md exists (created with the plan; absent on plans predating it)
- ⚠️ Optional: handoff.md exists (if session transfer occurred)
- ⚠️ Optional: mockup-log.md in mockups/ (if mockup workflow used)

### 2. Frontmatter Completeness

For each file (research.md, design.md, tasks.md):

- ✅ Has valid YAML frontmatter
- ✅ Required fields present: `project`, `created`, `status`, `last_updated`
- ✅ Git metadata present: `git_commit`, `git_branch`
- ✅ tasks.md additionally: `task_tracking`, `current_phase`, `total_tasks`, `completed_tasks`
- ⚠️ Optional fields: `ticket`, `repository`, `researcher`, `planner`, `assignee`

### 3. Task Tracking Integrity

Status lives in tasks.md itself; there is no external tracker to cross-check against. So these
checks are about whether the file can actually carry that role.

- ✅ tasks.md declares `task_tracking: markdown-checkboxes` in frontmatter
- ✅ tasks.md has a section stating where status lives (checkboxes truth, counters a cache, git durable)
- ✅ Every task line is a checkbox (`- [ ]` / `- [x]`), not prose or a bare bullet
- ✅ Every task carries a stable local ID, and IDs are unique
- ✅ Every ID matches `[A-Z0-9-]*[0-9][A-Z0-9-]*` — at least one digit. An ID without one is invisible to every counter in the workflow, silently
- ✅ `completed_tasks` matches `grep -c '^- \[x\]'` over the task lines, and `total_tasks` matches the total
- ⚠️ A `[x]` task with no `(completed …)` stamp — allowed, but the stamp is what makes the log readable
- ❌ Any instruction telling the reader that checkboxes are documentation-only, or that status lives elsewhere — that is a pre-2.0.0 plan and its guidance is now wrong

### 4. Status Consistency

- ✅ research.md status is valid: `draft`, `in-progress`, or `complete`
- ✅ design.md status is valid: `draft`, `ready`, `implementing`, or `complete`
- ✅ tasks.md status is valid: `not-started`, `in-progress`, or `complete`
- ✅ Status progression is logical:
  - Cannot have design `ready` if research is `draft`
  - Cannot have tasks `in-progress` if design is `draft`
  - Cannot have design `complete` if tasks is not `complete`
- ✅ tasks.md status agrees with its own checkboxes: `not-started` with any `[x]`, or `complete` with any `[ ]`, is a contradiction
- ✅ All files have same `last_updated` date (or close)

### 5. Content Completeness

- ✅ No placeholder text like `[To be added]`, `[TBD]`, `[TODO]`
- ✅ research.md has findings sections populated
- ✅ design.md has design decisions documented
- ✅ tasks.md has phases with tasks defined
- ✅ Success criteria are specific, not generic

### 6. Planning Records

Questions, assumptions and pending decisions live as markdown records in the document that
raises them, each with a short local ID and an explicit state.

- ✅ research.md's `## Open Questions` rows carry IDs (`Q1`, `Q2`, …) and a state
- ✅ design.md's `### Assumptions` rows carry IDs (`A1`, …) and a `Validated?` value
- ✅ design.md's `## Pending Decisions` rows carry IDs (`PD1`, …) and name what they block
- ✅ Every resolved row points at where the decision was recorded, rather than restating it in research.md
- ⚠️ An open `PD` row whose `Blocks` names execution start, while tasks.md is already `in-progress` — the plan is running past a decision it said it needed
- ⚠️ IDs that skip or repeat — they are cited from other documents, so they must be stable

### 7. Dependencies

- ✅ design.md references research.md in `depends_on`
- ✅ tasks.md references both research.md and design.md in `depends_on`
- ✅ Dependency chain is complete: research → design → tasks

### 8. Cross-File Consistency

- ✅ Project names match across all files
- ✅ Ticket IDs match (if present)
- ✅ Git metadata is consistent
- ✅ Current phase in tasks.md makes sense given progress

## Validation Rules

### File Structure Validation

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

### Frontmatter Validation

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

### Status Validation

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

### Task Tracking Validation

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

### Planning Record Validation

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

### Content Validation

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

## Important Guidelines

### DO

- ✅ Read ALL files fully before reporting
- ✅ Count the checkboxes rather than trusting the counters — the counts are the fact
- ✅ Report both errors and warnings with clear severity
- ✅ Provide specific, actionable fix suggestions
- ✅ Check that task IDs are present and unique; they are cited from outside the file
- ✅ Check for consistency across all files
- ✅ Offer to help fix issues after reporting

### DON'T

- ❌ Make assumptions about what "should" be there
- ❌ Automatically fix issues without user confirmation
- ❌ Skip checks if some files are missing
- ❌ Report vague problems without specific locations
- ❌ Treat counter drift as an error — it is expected between checkpoints, and `/wb:update_status` is what resolves it
- ❌ Rewrite counters yourself; `/wb:update_status` is their only writer
- ❌ Use limit/offset when reading files

## Configuration

This skill validates project documentation structure and the integrity of its task-tracking surface. It does not modify files unless the user explicitly requests fixes.

**Usage**:

```
/wb:validate_project docs/plans/2025-01-08-my-project
```

**Validation Modes**:

- Default: Full validation with detailed report
- Quick: Check only critical errors (future enhancement)
- Fix: Validate and auto-fix issues (future enhancement)
