# Beads Integration Learnings

Captured during the integration of beads with the wb workflow (prompts-917).

## Session 2026-01-31

### Learning 1: Permission Wildcards

**Context**: Task prompts-jrw - adding bd permissions

**Discovery**: When adding tool permissions incrementally during a session, you can end up with redundant specific permissions alongside a wildcard that covers them all.

**Before** (redundant):

```json
"Bash(bd list:*)",
"Bash(bd doctor)",
"Bash(bd create:*)",
"Bash(bd:*)"
```

**After** (clean):

```json
"Bash(bd:*)"
```

**Takeaway**: Periodically review permissions for redundancy. Prefer wildcards when you trust the tool category.

### Learning 2: Beads Workflow Basics

The core workflow is:

1. `bd ready` - Find unblocked work
2. `bd show <id>` - Review full context
3. `bd update <id> --status in_progress` - Claim it
4. Do the work
5. `bd close <id>` - Mark complete
6. `bd sync` - Persist to git

Key insight: `bd show` displays what the task BLOCKS - helps understand impact of completing it.

### Learning 3: Graceful Degradation for Beads Integration

**Context**: Task prompts-lul - updating create_execution command

**Discovery**: When integrating beads into existing workflows, check for availability first:

```bash
bd stats 2>/dev/null && echo "BEADS_AVAILABLE=true" || echo "BEADS_AVAILABLE=false"
```

**Design principle**: Beads should enhance the workflow, not break it. If beads isn't initialized:

- Fall back to markdown-only tracking
- Don't error or require beads
- Keep the existing workflow functional

**Integration pattern**:

1. Keep tasks.md as human-readable documentation (always created)
2. Add beads issues as structured tracking layer (optional)
3. Link them via frontmatter (`beads_epic`, `beads_phases`)
4. Both systems stay in sync through the workflow

### Learning 4: Phase-Level vs Task-Level Beads Issues

**Decision**: Create beads issues at the **phase level**, not individual task level.

**Rationale**:

- Phases are natural checkpoints (have dependencies, success criteria)
- Individual tasks are too granular (would create noise)
- Markdown checkboxes work well for within-phase tracking
- Beads handles cross-session, cross-phase coordination

**Structure**:

```
Epic: "Project Implementation"
  └── Phase 1 issue (blocks Phase 2)
  └── Phase 2 issue (blocked by Phase 1)
  └── Phase 3 issue (blocked by Phase 2)
```

Tasks within phases stay as markdown checkboxes in tasks.md.

### Learning 5: TodoWrite + Beads Serve Different Purposes

**Context**: Task prompts-3kb - updating implement_tasks command

**Discovery**: TodoWrite and beads aren't competing - they complement each other:

| Tool | Scope | Survives | Purpose |
|------|-------|----------|---------|
| TodoWrite | Session | No (compaction clears) | Within-session progress tracking |
| Beads | Cross-session | Yes (git-backed) | Phase/milestone tracking |

**Integration pattern**:

- Use **TodoWrite** for "what am I doing right now" (granular tasks)
- Use **Beads** for "what phase am I in" (coarse milestones)
- Both can be active simultaneously

**Resume workflow with both**:

1. `bd ready` - What phases are available?
2. `bd update [phase] --status in_progress` - Claim the phase
3. `TodoWrite([...])` - Set up session tasks
4. Work...
5. `bd close [phase]` - Complete the phase
6. `bd sync` - Persist to git

### Learning 6: bd show Output Format

**Context**: Reading bd show output during workflow

**Key fields displayed**:

- **DEPENDS ON**: Tasks this one waits for (shows ✓ if complete)
- **BLOCKS**: Tasks waiting on this one
- **Owner**: Who claimed it
- **Status**: Current state (open, in_progress, closed)

This dependency visibility is powerful for understanding work sequencing.

### Learning 7: Feature Detection for Graceful Degradation

**Context**: Task prompts-de6 - updating status-sync skill

**Pattern**: Check for beads presence before using beads commands:

```bash
ls .beads/beads.db 2>/dev/null && echo "BEADS_PROJECT" || echo "MARKDOWN_ONLY"
```

**Why this matters**: Skills and commands should work in both:

- Beads-enabled projects (use bd commands)
- Markdown-only projects (use original behavior)

This keeps the workflow portable and non-breaking for users who haven't adopted beads yet.

### Learning 8: bd sync is the Session-End Ritual

**Context**: Updating reminder behavior

**Key insight**: `bd sync` is to beads what "commit and push" is to git.

**Session close checklist** (beads projects):

1. `bd close` any completed issues
2. `bd sync` to persist to JSONL/git
3. `git add .beads/ && git commit && git push`

The AGENTS.md in this repo already captures this pattern.

### Learning 9: Beads as Source of Truth for Phase Status

**Context**: Task prompts-bma - updating update_status command

**Key principle**: When beads is enabled, it's the authoritative source for phase/task status:

```bash
bd show [phase-id]  # Authoritative status
```

**Why markdown may lag**:

- Checkboxes are manually updated
- Frontmatter requires explicit update
- Beads status changes immediately with `bd close`

**Reconciliation strategy**:

1. Read beads state first (`bd list`, `bd show`)
2. Cross-check against markdown
3. If mismatch, beads wins
4. Update markdown to reflect beads state

This maintains human-readable markdown while using beads for reliable cross-session tracking.

### Learning 10: Documentation Layering

**Context**: Task prompts-yu3 - updating documentation

**Documentation structure with beads**:

| File | Purpose | Audience |
| ------ | --------- | ---------- |
| README.md | Overview, quick start | New users |
| CLAUDE.md | Agent instructions | Claude Code |
| AGENTS.md | Session protocol | AI agents |
| wb/README.md | Command reference | Users of wb commands |
| docs/beads-integration-learnings.md | This file | Future sessions |

**Key principle**: Each file has a specific audience and purpose. Don't duplicate - reference.

### Summary: Beads Integration Complete

The wb workflow now supports beads with graceful degradation:

1. **create_execution**: Creates phase issues with dependencies (Step 5)
2. **implement_tasks**: Uses bd ready/update/close for phase tracking
3. **status-sync skill**: Detects beads vs markdown-only, reminds appropriately
4. **update_status**: Uses beads as source of truth when available

**Without beads**: Everything still works using markdown checkboxes.

**With beads**: Cross-session persistence, dependency tracking, authoritative status.

---

## Code Review Findings (Post-Integration)

### Critical Fix: Beads Detection Method

**Problem**: Inconsistent detection across files:

- Some used `bd stats 2>/dev/null` (tests if CLI works)
- Some used `ls .beads/beads.db` (tests if project initialized)

**Resolution**: Standardized on `ls .beads/beads.db 2>/dev/null`

**Rationale**: Tests actual project state. A globally installed `bd` CLI shouldn't trigger beads workflow in a non-beads project.

### Clarification: TodoWrite + Beads

**Problem**: Mixed signals about whether TodoWrite is fallback or complement.

**Resolution**: Made explicit:

- **Always use TodoWrite** for session tracking
- **Additionally use beads** (if available) for cross-session tracking
- They are complementary, not mutually exclusive

### Verified: bd dep add Syntax

Confirmed `bd dep add <blocked-id> <blocker-id>` is correct:

- `bd dep add phase2 phase1` = "phase2 depends on phase1"
- Phase 2 is blocked by Phase 1 ✓

### Remaining Token Optimization (prompts-qh5)

Not addressed yet:

1. README.md duplicates wb/README.md beads section (~400 tokens)
2. Step 5 in create_execution.md could reference external doc (~1000 tokens)
3. Beads command syntax repeated in 3+ places
4. Consider extracting common patterns to references
