# Workbench Workflow Guide

Comprehensive guide to the wb workflow stages, where status lives, and best practices.

## Table of Contents

- [Quick Start](#quick-start)
- [Complete Workflow](#complete-workflow)
- [Where status lives](#where-status-lives)
- [Mockup Workflow](#mockup-workflow)
- [Core Philosophy](#core-philosophy)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd prompts

# Install globally for Claude Code
./scripts/install-commands --claude

# Nothing else to initialize — status lives in the plan documents.
```

### Basic Workflow

```bash
# 1. Initialize project
/wb:create_project my-feature docs/plans TICKET-123

# 2. Research codebase
/wb:create_research docs/plans/2025-01-15-TICKET-123-my-feature
> Research existing patterns for X

# 3. Create mockup (optional - for UI features)
/wb:create_mockup docs/plans/2025-01-15-TICKET-123-my-feature "settings panel"

# 4. Explore the alternatives (optional — only if research found more than one viable approach)
/wb:explore_design docs/plans/2025-01-15-TICKET-123-my-feature "how sessions are stored"

# 5. Design decisions
/wb:create_design docs/plans/2025-01-15-TICKET-123-my-feature

# 6. Create execution plan
/wb:create_tasks docs/plans/2025-01-15-TICKET-123-my-feature

# 7. Implement with TDD (worker agents; /wb:implement_inline runs it in this session)
/wb:implement docs/plans/2025-01-15-TICKET-123-my-feature

# 8. Validate implementation
/wb:validate_execution docs/plans/2025-01-15-TICKET-123-my-feature
```

## Complete Workflow

### Stage 1: Project Initialization

**Command**: `/wb:create_project`

Creates timestamped documentation structure with metadata tracking.

**Creates**:

```
docs/plans/2025-01-15-TICKET-123-feature-name/
├── README.md      # Navigation and overview
├── research.md    # Research findings (status: draft)
├── design.md      # Design decisions (status: draft)
└── tasks.md       # Execution plan (status: not-started)
```

**Captures**:

- Git metadata (commit, branch, repository)
- User information
- Timestamps
- Project/ticket identifiers

### Stage 2: Research

**Command**: `/wb:create_research`

Documents codebase objectively using parallel research agents.

**Process**:

1. Reads mentioned files FULLY (⛔ BARRIER 1)
2. Spawns parallel agents (⛔ BARRIER 2 - wait for ALL):
   - Code Locator: WHERE components live
   - Code Analyzer: HOW code works
   - Pattern Finder: Similar implementations
3. Synthesizes findings (⛔ BARRIER 3 - no placeholders)
4. Writes structured research.md

**Critical Rule**: "Document what IS, not what SHOULD BE"

**Output**: research.md with file:line references, patterns, architecture documentation

### Stage 3: UI Mockup (Optional)

**Command**: `/wb:create_mockup`

**For UI features only** - researches UI patterns and creates HTML mockups.

**Process**:

1. Research existing UI (5 parallel agents):
   - Layout patterns
   - Component library
   - Styling approach
   - Similar features
   - **Icon system** (Font Awesome, Material Icons, etc.)
2. Ask clarifying questions
3. Create ASCII structure (mockup.md)
4. **Create HTML mockup** (mockup.html) with app's actual styles
5. **Visual validation** with Playwright screenshot
6. Iterate with `mockup-iteration` skill

**Creates**:

```
mockups/
├── mockup-log.md          # Decision log
└── v001/
    ├── mockup.md          # ASCII structure
    ├── mockup.html        # HTML with real styles
    ├── preview-v001.png   # Screenshot
    └── decisions.md       # Rationale
```

**Beads Integration**:

- Creates `UI Q: [question]` issues for unresolved questions
- Creates `UI Assumption: [assumption]` issues for unvalidated beliefs
- Blocks finalization until all UI issues resolved
- Reads the latest mockup.md Open Questions table for rows still `Open`

**Icon Handling**:

- **Never uses emojis** in HTML mockups
- Uses discovered icon system from research
- Adds a `UIQ` row to the mockup if the icon system is unclear
- Asks user before adding icons if no system found

**Iteration**:

```bash
# User provides feedback
"Keep the card layout but remove the sidebar"
→ Skill updates mockup-log.md (KEEP/REMOVE)
→ Creates v002 with changes
→ Shows new screenshot

# Show current mockup
"show mockup"
→ Opens HTML in browser, screenshots

# Finalize to design
"finalize"
→ Checks for open UI Q: issues
→ Compiles KEEP decisions into requirements
→ Lists REMOVE decisions as out of scope
```

### Stage 3b: Explore Design Options (Optional)

**Command**: `/wb:explore_design`

Airs the alternatives *before* one is chosen. The pipeline otherwise goes from facts straight to
a locked decision, so the reasoning behind an architecture choice survives only as design.md's
Rejected Alternatives — written by the same pass that chose.

**When it earns its cost**: research surfaced **more than one viable approach** and nothing in
the codebase decides between them. `create_research` suggests it only under those two
conditions; running it on a decision that was never in doubt produces a document nobody reads.

**Process**:

1. Frame the decision — the question, what is explicitly *not* being decided, and the
   constraints any answer must satisfy
2. Diverge — two to four genuinely different directions, each with a precedent, what it buys,
   what it costs, and when it is the wrong choice. No strawmen
3. Discuss the trade-offs with the user, one thread at a time
4. ⛔ CHECKPOINT — converge **only** on explicit approval. Silence is not approval
5. Record — the decision at the **top** of a `thoughts/` document, with the rejected
   alternatives and why

**Output**: `thoughts/YYYY-MM-DD-<topic>.md`. It never writes `design.md` — `create_design`
finds the record, presents it for confirmation, and formalizes it, carrying the rejected
alternatives across rather than inventing new ones.

### Stage 4: Design

**Command**: `/wb:create_design`

Creates architectural design decisions (WHAT and WHY).

**Process**:

1. Reads research and mockup decisions
2. Spawns verification agents
3. Presents design options with trade-offs
4. Interactive discussion
5. Documents approved design

**Structure**:

- Problem statement
- Design approach with rationale
- Technical decisions
- Scope (in/out)
- Success criteria
- Risk analysis
- Rejected alternatives

**Critical**: WHAT and WHY only - never HOW

### Stage 5: Execution Plan

**Command**: `/wb:create_tasks`

Transforms design into detailed phased execution plan.

**Process**:

1. Reads research and design completely
2. Spawns analysis agents:
   - Dependency analysis
   - Test coverage planning
   - Rollback procedures
3. Generates phased plan with embedded tasks

**Beads Integration**:

Writes the phased task list. Each task is a checkbox carrying a stable local ID and a projected
tool-call cost:

```markdown
#### Implementation

- [ ] **P1-T4** — Create [Component] class at `src/component.ts` (~20 calls)
- [ ] **P1-T5** — Modify [ExistingComponent] at `src/existing.ts:45` (~15 calls)
```

Ordering **is** the dependency graph: phases run in document order, tasks run in order within a
phase. A task depending on something other than the task before it says so in one `Depends on:`
field; nothing else encodes dependencies. If many tasks need one, the phase is ordered wrong.

Tasks are sized by projected **tool calls**, not hours — anything past ~50 splits at a natural
seam before it is ever spawned, because truncation is a function of call count and always eats
the finishing tail.

### Stage 6: Implementation

**Command**: `/wb:implement`

Implements using TDD, one task at a time.

```bash
# 1. Find the next task: the first unchecked line in the current phase
grep -m1 -E '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md

# 2. Open a journal entry naming the task and the exact next action

# 3. TDD cycle — Red: failing test / Green: minimum code / Refactor: clean up

# 4. Flip the checkbox. This IS the act of recording it done:
#    - [ ] **P1-T4** ...  ->  - [x] **P1-T4** ... (completed 2026-09-08 14:32)

# 5. Commit — one task, one commit, task ID in the message

# 6. Close the journal entry with what landed and its commit
```

**Phase completion is "every checkbox in the phase is `[x]`".** There is nothing else to close.
At the ⛔ CHECKPOINT run the automated verification, ask the human for the manual checks, then
run `/wb:update_status` to reconcile the counters.

With `/wb:implement`, a worker does steps 2–4 in fresh context and the coordinator does step 5
after a verifier passes. That split is what makes an unfinished task detectable: workers never
commit, so a flipped checkbox in an uncommitted tree means finished, while an unflipped one
beside real changes means the worker exhausted its tool-call budget.

### Stage 7: Validation

**Command**: `/wb:validate_execution`

Validates implementation matches plan.

**Process**:

1. Spawns validation agents
2. Compares actual vs planned implementation
3. Identifies deviations
4. Generates comprehensive report

**Checks**:

- All tasks completed
- Success criteria met
- Test coverage adequate
- Documentation updated
- No unintended changes

### Stage 8: Status Updates

**Command**: `/wb:update_status`

Syncs status across all files based on actual progress.

**Process**:

1. Reads ALL files fully
2. Counts the checkboxes in tasks.md (the source of truth)
3. Determines actual state
4. Proposes updates
5. Applies consistently

**Status Progressions**:

```
research.md: draft → in-progress → complete
design.md: draft → ready → implementing → complete
tasks.md: not-started → in-progress → complete
```

### Handoff (Multi-Session)

**Commands**: `/wb:create_handoff`, `/wb:resume_handoff`

**Create Handoff**:

```bash
/wb:create_handoff docs/plans/2025-01-15-TICKET-123-feature
```

Captures:

- Current progress and phase
- Critical learnings not in docs
- Problems solved
- Active blockers
- **Open questions and blockers**, cited by their local IDs
- Next steps
- Git state

**Resume Handoff**:

```bash
/wb:resume_handoff docs/plans/2025-01-15-TICKET-123-feature/handoff-2025-01-15.md
```

Restores:

- Full context
- Learnings and patterns
- Continues from exact point
- Applies discovered solutions

## Where status lives

There is no external tracker. Nothing to install, nothing to initialize, nothing that can be
unavailable — which is the point: before 2.0.0, six stages halted on a dependency that had to
be present.

### The three surfaces

| Surface | Holds | Written by |
| ------- | ----- | ---------- |
| Checkboxes in `tasks.md` | task and phase status | whoever finishes the task |
| Frontmatter counters | a derived cache of those counts | `/wb:update_status`, and nothing else |
| Git | the durable record | one task, one commit, task ID in the message |

**Flipping a checkbox is the act of recording a task done** — not a note about it. A finished
task with an unflipped box is indistinguishable from unfinished work to the next session.

```bash
# Progress, at any time. Scope to lines carrying a task ID: a plan's own success
# criteria and prerequisites are checkboxes too.
grep -cE '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md
grep -cE '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' tasks.md
```

### The counters are a cache, and drift is normal

Implementation stages flip checkboxes and defer the counters to `/wb:update_status`, which is
their **only** writer. That single-writer rule is the whole mechanism: a cache with several
writers and no owner is how these fields rotted before.

So the counters lag between checkpoints. That is expected, not an error. `status-sync` surfaces
the drift, `/wb:update_status` reconciles it, and **the checkboxes are always what's right**.

### Task IDs are a contract

Every task line carries a bold local ID matching `[A-Z0-9-]*[0-9][A-Z0-9-]*` — uppercase,
hyphens, **at least one digit** (`P2-T7`, `T14`).

This is not a style preference. Every counter in the workflow identifies task lines by that
shape, so an ID without a digit makes its task **invisible to counting**: wrong totals, wrong
reported position, and nothing erroring. `/wb:validate_project` checks it.

### Planning records

Questions, assumptions and pending decisions live in the document that raises them, each with a
short local ID and an explicit state:

| Record | Lives in | ID |
| ------ | -------- | -- |
| Open question | `research.md` → `## Open Questions` | `Q1` |
| Assumption | `design.md` → `### Assumptions` | `A1` |
| Pending decision | `design.md` → `## Pending Decisions` | `PD1` |
| UI question | `mockups/v00N/mockup.md` | `UIQ1` |

`/wb:resolve_questions` walks them one at a time, records each answer as a decision with its
rationale in `design.md`, and marks the source row resolved. **Rows are never deleted** — the
audit trail is the point.

### Continuity across sessions

| Artifact | Scope | Read when |
| -------- | ----- | --------- |
| `journal.md` | one plan | session start (the tail), and on resume |
| `.claude/wb/knowledge.md` | the repository, committed | before research, design, implementation |
| `handoff-*.md` | one transfer | by `/wb:resume_handoff` |

**Journal entries open when work starts, not when it ends.** A session does not choose how it
ends, so an entry written only at completion is silent in exactly the cases it exists for —
and worse than silent, because its tail would still show the last *finished* phase.

The session-start hook (`hooks/wb-prime.sh`) prints the plan's position, the journal's last
entry and whether it is open, and reconciles both against the working tree. **The repository is
always the authority**; the hook never reports the journal as fact when the two disagree.

### Model and effort

This guide does not carry a per-stage model table. `model-help` is the single authority for
main-session model and effort, and sub-agent tiers are pinned in each agent's own frontmatter —
anything spawned is pinned at its definition, anything the session runs is advised by
`model-help`. Two documents naming tiers is how they drift.

Run `/wb:model-help` for the per-phase baselines, the upshift ladder, and the switch-cost rule.

## Mockup Workflow

### When to Use

Use `/wb:create_mockup` for:

- New UI features
- UI redesigns
- Complex layouts
- Features requiring visual validation

Skip for:

- Backend-only features
- API changes
- Simple text changes

### Research Phase

Spawns 5 parallel agents:

1. **Layout Patterns**: Grid systems, flex patterns, containers, breakpoints
2. **Component Library**: Buttons, forms, cards, modals, naming conventions
3. **Styling Approach**: Tailwind vs CSS Modules vs styled-components, tokens, theme
4. **Similar Features**: Existing panels/modals for reference
5. **Icon System**: Font Awesome, Material Icons, Heroicons, SVG sprites, custom, or none

### Icon System Research

**What it finds**:

- Library name and version
- Where icons imported/defined (file:line)
- Usage pattern (`<i class="fa-solid fa-save">` vs `<Icon name="save">`)
- Sizing conventions
- Color conventions
- Examples with file:line references

**If no system found**:

- Documents "None - text only"
- Adds a `UIQ` row if icons are needed and no system exists
- Never defaults to emojis

### Mockup Creation

**ASCII Structure** (mockup.md):

- Quick layout discussion
- Component specifications
- State documentation
- Interaction flows

**HTML Mockup** (mockup.html):

- Imports app's actual stylesheets
- Uses component HTML from research (file:line)
- Applies actual CSS classes (no placeholders)
- Follows icon system from research
- Standalone - opens directly in browser

**Example HTML**:

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-100">
  <header class="bg-white shadow-md px-6 py-4">
    <h1 class="text-2xl font-bold text-gray-900">
      <i class="fa-solid fa-cog mr-2"></i>
      Settings
    </h1>
  </header>

  <main class="container mx-auto px-6 py-8">
    <div class="bg-white rounded-lg shadow p-6">
      <!-- Real component HTML from research -->
    </div>
  </main>
</body>
</html>
```

### Visual Validation

After creating HTML:

```javascript
// Navigate to mockup
mcp__plugin_playwright_playwright__browser_navigate({
  url: "file:///absolute/path/to/mockup.html"
})

// Screenshot
mcp__plugin_playwright_playwright__browser_take_screenshot({
  filename: "preview-v001.png",
  fullPage: true
})
```

Shows screenshot to user for validation.

### Iteration

**Feedback Classification**:

- **KEEP**: Confirmed requirement → add to mockup-log.md "Confirmed"
- **REMOVE**: Rejected idea → add to "Rejected" with reason
- **CHANGE**: Modification needed → note for next version
- **QUESTION**: Needs clarification → a `UIQ` row in the current mockup.md
- **ASSUMPTION**: Unvalidated belief → a `UIA` row in the current mockup.md

**Version Creation**:

```bash
# User: "Keep header but make sticky, remove sidebar"

# Skill updates mockup-log.md:
## Confirmed (KEEP)
- Header layout - confirmed 2025-01-15 - "Keep header"
- Sticky positioning - confirmed 2025-01-15 - "make sticky"

## Rejected (REMOVE)
- Sidebar navigation - rejected 2025-01-15 - "remove sidebar"

# Creates v002:
mockups/v002/
├── mockup.md          # Updated ASCII
├── mockup.html        # Updated HTML
├── preview-v002.png   # New screenshot
└── decisions.md       # Delta from v001
```

### Finalization

Before finalizing to design.md:

```bash
# Check for open issues
grep -A20 "^## Open Questions" mockups/v00N/mockup.md   # any row still Open?
```

**If open issues exist**:

- Must resolve questions
- Must validate assumptions
- Or close as "deferred to implementation"

**After all resolved**:

- Compile all KEEP decisions → requirements
- List all REMOVE decisions → out of scope
- Export to design.md section:

```markdown
## UI Design: Settings Panel

### Requirements (from mockup iteration)

_Confirmed through 3 mockup iterations_

1. Sticky header with icon - v001
2. Two-column layout on desktop - v002
3. Icon system: Font Awesome 6.4.0 - v001

### Out of Scope

_Explicitly excluded during mockup iteration_

1. Sidebar navigation - removed v002, reason: "cluttered UI"
2. Dark mode toggle - removed v003, reason: "phase 2 feature"

### Final Mockup Reference

- Structure: `mockups/v003/mockup.md`
- Visual: `mockups/v003/mockup.html`
- Screenshot: `mockups/v003/preview-v003.png`
```

## Core Philosophy

### Document, Don't Judge

Research describes what EXISTS, not what should be changed.

**Why**:

- Clear understanding of current state
- Unbiased analysis
- Better planning decisions
- Reduced assumptions

**Agent Instructions**:

```
You are documenting the codebase as it exists.
DO NOT suggest improvements or identify issues.
Document what IS, not what SHOULD BE.
```

### Explicit Barriers

Synchronization points prevent rushing ahead.

**Types**:

- **⛔ BARRIER 1**: After file reading - full context required
- **⛔ BARRIER 2**: After agent spawning - wait for ALL
- **⛔ BARRIER 3**: Before writing - no placeholders allowed
- **⛔ CHECKPOINT**: Between phases - human verification required

**Why**:

- Prevents incomplete context
- Ensures parallel work completes
- Validates before proceeding
- Catches issues early

### Dual Verification

Separate automated and manual checks.

**Automated** (CI can run):

- Unit tests
- Integration tests
- Linting
- Build verification

**Manual** (Human required):

- UI functionality
- UX validation
- Performance testing
- Edge case verification
- Visual appearance

### Zero Scope Creep

Tasks come ONLY from plans.

**Why**:

- Predictable delivery
- Clear expectations
- Controlled changes
- Traceable work
- Measurable progress

**Enforcement**:

- Beads issues created from plan only
- No ad-hoc task creation during implementation
- Changes require design update → new execution plan

## Best Practices

### Research Phase

- Read files FULLY (no limit/offset)
- Document objectively
- Include all file:line references
- Find existing patterns
- Note how components interact
- Never suggest improvements

### Mockup Phase

- Research icon system first
- Use app's actual styles
- Never use emojis in HTML
- Record unknowns as `Q`/`A` rows in the document that raises them
- Screenshot after each version
- Resolve all UI Q: before finalizing

### Planning Phase

- Discuss before writing
- Define out of scope
- Make success criteria measurable
- Phase for incremental value
- Include rollback procedures

### Implementation Phase

- Take the first unchecked task in the current phase
- Open a journal entry before touching code
- Follow TDD cycle strictly
- Flip the checkbox when done, then commit
- Run `/wb:update_status` at each phase checkpoint
- Respect phase boundaries
- Stop at checkpoints

### Session Management

**At session end**:

- Flip every finished task's checkbox
- Run `/wb:update_status`
- Commit the work — one task, one commit
- Create handoff if needed

**At session start**:

- Git mode: `git pull`
- Read tasks.md for the first unchecked task
- Read the journal tail for an open entry
- Resume from handoff if exists

## Troubleshooting

### Beads Issues

**"The counters disagree with the checkboxes"**:

```bash
/wb:update_status [project-dir]   # the checkboxes are right; this reconciles
```

**"database locked"**:

- Wait and retry
- Check for stale processes

**"issue not found"**:

```bash
grep -n '^- \[' tasks.md   # find the task line
```

### Mockup Issues

**No icon system found**:

- Document as "None - text only"
- Add a `UIQ` row if icons are needed
- Ask user for direction

**HTML mockup not rendering**:

- Check stylesheet imports
- Verify paths are correct
- Use CDN links for testing

**Screenshot not showing**:

- Check Playwright is installed
- Verify file path is absolute
- Check browser can access file

### Agent Issues

**Agents not finding files**:

- Be specific about directories
- Check file patterns in prompts
- Verify files exist

**Placeholder values in output**:

- ⛔ BARRIER 3 violation
- Re-run with complete context
- Never proceed with placeholders

### Status Issues

**Status progression blocked**:

- Verify all tasks complete
- Check the checkboxes in tasks.md
- Ensure checkpoints passed

**Inconsistent status across files**:

- Run `/wb:update_status`
- It counts the checkboxes and reconciles the counters to them

## Additional Resources

- [Commands Reference](commands-reference.md) - Detailed command documentation
- [CLAUDE.md](../CLAUDE.md) - Session protocol and repository conventions
- [Skills Guide](claude-code-skills-guide.md) - Skills documentation
