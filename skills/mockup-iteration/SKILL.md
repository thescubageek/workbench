---
name: mockup-iteration
description: Iterate on UI mockups, capturing keeps/removes/changes with full fidelity. Versions each iteration and maintains decision log.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(ls:*, mkdir:*), mcp__plugin_playwright_playwright__browser_navigate, mcp__plugin_playwright_playwright__browser_take_screenshot, mcp__plugin_playwright_playwright__browser_snapshot
triggers:
  - mockup feedback
  - iterate on mockup
  - change the mockup
  - keep this
  - remove this
  - update mockup
  - next version
  - refine design
  - show mockup
  - preview mockup
---

# Mockup Iteration Skill

Helps iterate on UI mockups efficiently, capturing decisions without fidelity loss.

## Activation

This skill activates when:

- User provides feedback on a mockup ("keep the header", "remove the sidebar")
- User asks to iterate or create next version
- User discusses mockup changes
- User wants to finalize mockup into design

## Core Behavior

### Finding the Mockup Context

Before processing feedback, locate the mockup:

1. **Find mockup-log.md**: Search for `mockups/mockup-log.md` in current project
2. **Read project_directory** from frontmatter to confirm location
3. **Read current_version** from frontmatter to know active version
4. **Verify v00[N] directory exists** - if not, scan for highest existing

**If mockup-log.md missing:**

```
I can't find an active mockup session.

Options:
1. Start new mockup: /wb:create_mockup [directory] [feature]
2. Point me to existing mockup-log.md location
```

**If giving feedback about non-mockup topic:**

```
I'm treating this as mockup feedback for [feature] (currently v00[N]).
If this isn't about the mockup, let me know.
```

### On Feedback Receipt

When user provides mockup feedback:

1. **Acknowledge and classify** the feedback:
   - **KEEP**: Confirmed requirement - add to "Confirmed" in mockup-log.md
   - **REMOVE**: Rejected idea - add to "Rejected" with rationale
   - **CHANGE**: Modification needed - note for next version
   - **QUESTION**: Needs clarification - create beads issue, ask before proceeding
   - **ASSUMPTION**: Unvalidated belief - create beads issue for validation

   **Compound feedback** (contains multiple types):
   - Split into separate entries
   - "Keep header but make it blue" → KEEP: header layout + CHANGE: header color to blue
   - Each part gets its own log entry

   **Questions and assumptions** → Create beads issues:

   ```bash
   # For questions that need answers:
   bd create "UI Q: [question]" --type=task --priority=2 \
     -d "From mockup iteration. Blocks: finalization"

   # For assumptions that need validation:
   bd create "UI Assumption: [assumption]" --type=task --priority=3 \
     -d "Assuming [X]. If wrong: [impact]. Validate before implementation."
   ```

2. **Update mockup-log.md** immediately:

   ```markdown
   ### Confirmed (KEEP)
   - [Requirement] - confirmed [date] - "[user quote]"

   ### Rejected (REMOVE)
   - [Idea] - rejected [date] - reason: "[user rationale]"
   ```

3. **Summarize understanding** before creating new version:

   ```
   Got it. For the next version:

   ✓ KEEPING: [list]
   ✗ REMOVING: [list]
   ~ CHANGING: [list]
   ? CLARIFYING: [questions if any]

   Ready to create v[N+1]?
   ```

### On Version Request

When user confirms or says "next version":

1. **Read current_version from mockup-log.md frontmatter** (e.g., `current_version: 2`)
2. **Read mockups/v00[N]/mockup.md** fully as base
3. **Read mockups/v00[N]/mockup.html** fully as base
4. **Read mockup-log.md** Running Requirements AND UI Research Reference (for icon system, styling)
5. **Create new version directory**: `mockups/v00[N+1]/` (zero-padded: v001, v002, ..., v010)
6. **Create new mockup.md** incorporating ALL feedback
7. **Create new mockup.html** incorporating ALL feedback
   - Update HTML structure to match new mockup.md
   - Maintain app's styling approach from research
   - Update icons per feedback (add/remove/change)
   - Keep CSS classes consistent with app
8. **Create decisions.md** documenting what changed (delta only)
9. **Visual validation**:
   - Navigate to new mockup.html in Playwright
   - Take screenshot: `mockups/v00[N+1]/preview-v00[N+1].png`
   - Show screenshot to user
10. **Update mockup-log.md**:
    - Frontmatter: `current_version: [N+1]`, `last_updated: [date]`
    - Add version entry to Version History
    - Update Running Requirements sections

### Version Naming

```
v001 - Initial draft
v002 - First iteration
v003 - Second iteration
...
v00N - Final (before design.md)
```

## Iteration Workflow

```
User feedback → Classify → Update log → Confirm understanding → Create version
     ↑                                                              │
     └──────────────────────────────────────────────────────────────┘
```

## Templates

### New Version Entry (mockup-log.md)

```markdown
### v00[N] - [YYYY-MM-DD] - [Brief Description]
- **Status**: In Review
- **Changes from v00[N-1]**:
  - KEPT: [what was preserved]
  - REMOVED: [what was cut]
  - CHANGED: [what was modified]
- **Feedback incorporated**: [summary]
- **Open questions**: [remaining unknowns]
```

### decisions.md for New Version

```markdown
---
version: [N]
created: [YYYY-MM-DD]
previous_version: [N-1]
---

# v00[N] Decisions

## Changes from v00[N-1]

### Added
- [New element] - reason: [user feedback/requirement]

### Removed
- [Removed element] - reason: [user feedback]

### Modified
- [Element]: [old] → [new] - reason: [rationale]

## Feedback Incorporated

| Feedback | Classification | Action Taken |
|----------|---------------|--------------|
| "[user quote]" | KEEP | Preserved [element] |
| "[user quote]" | REMOVE | Cut [element] |
| "[user quote]" | CHANGE | Modified [element] |

## Cumulative Requirements

_All confirmed requirements through this version:_

1. [Requirement from v001]
2. [Requirement from v002]
3. [New requirement this version]

## Still Open

- [ ] [Unresolved question]
```

## Fidelity Preservation

**CRITICAL**: Never lose design decisions. Every piece of feedback must be:

1. **Captured verbatim** - Quote user's exact words
2. **Classified** - KEEP/REMOVE/CHANGE/QUESTION
3. **Recorded** - In mockup-log.md immediately
4. **Incorporated** - In next version or noted as open

### Icon Handling

When updating mockup versions:

1. **Use app's icon system** from research (NOT emojis)
2. **If icon feedback given**:
   - "add a save icon" → Check research for icon system, use that pattern
   - "use text only" → Remove icons, update HTML
   - "change icon to X" → Update using app's icon library
3. **If icon system unclear**:
   - Create beads issue: `bd create "UI Q: Icon for [element]?" --type=task`
   - Ask user before adding icons
4. **Never default to emojis** in mockup.html

### Anti-patterns to Avoid

- Do not assume feedback without recording
- Do not overwrite previous version
- Do not lose "REMOVE" decisions (they inform design)
- Do not use vague summaries instead of specific quotes
- Do not create version without updating log
- Do not use emojis in HTML mockups (use app's icon system or text-only)

## Finalizing to Design

When user says "finalize" or "ready for design":

### Pre-finalization Check

```bash
# Check for unresolved questions/assumptions:
bd list --status=open | grep -E "UI Q:|UI Assumption:"
```

If open issues exist:

```
⚠️ Cannot finalize - unresolved items:

| Issue | Status |
|-------|--------|
| UI Q: [question] | Open |
| UI Assumption: [assumption] | Open |

Options:
1. Resolve these first (answer questions, validate assumptions)
2. Close as "deferred to implementation" if acceptable
3. Close as "out of scope" if not needed
```

### After All Resolved

1. **Compile all KEEP decisions** from mockup-log.md
2. **List all REMOVE decisions** as "Out of Scope"
3. **Verify no open questions** (all UI Q: and UI Assumption: closed)
4. **Generate design.md section**:

```markdown
## UI Design: [Feature]

### Requirements (from mockup iteration)

_Confirmed through [N] mockup iterations_

1. [Requirement] - v00[X]
2. [Requirement] - v00[Y]

### Out of Scope

_Explicitly excluded during mockup iteration_

1. [Excluded item] - reason: [from REMOVE log]

### Final Mockup Reference

- Structure: `mockups/v00[final]/mockup.md`
- Visual: `mockups/v00[final]/mockup.html`
- Screenshot: `mockups/v00[final]/preview-v00[final].png`

### Open Items for Implementation

- [ ] [Remaining question]
```

## Quick Commands

During iteration, user can say:

| Command | Action |
| --------- | -------- |
| "keep [X]" | Add to Confirmed, preserve in next version |
| "remove [X]" | Add to Rejected, cut from next version |
| "change [X] to [Y]" | Note modification for next version |
| "next version" | Create v00[N+1] with all feedback |
| "show mockup" | Open current mockup.html in browser and screenshot |
| "show log" | Display current mockup-log.md |
| "show keeps" | List all confirmed requirements |
| "show removes" | List all rejected ideas |
| "revert to v00[N]" | Create new version based on v00[N] |
| "compare v00[A] and v00[B]" | Show differences between versions |
| "finalize" | Prepare for design.md |

## Visual Preview

### On "show mockup"

When user wants to see the current mockup visually:

1. **Find current version** from mockup-log.md frontmatter
2. **Navigate to mockup.html**:

   ```javascript
   mcp__plugin_playwright_playwright__browser_navigate({
     url: "file:///[absolute-path]/mockups/v00[N]/mockup.html"
   })
   ```

3. **Take screenshot**:

   ```javascript
   mcp__plugin_playwright_playwright__browser_take_screenshot({
     filename: "mockup-preview-current.png",
     fullPage: true
   })
   ```

4. **Show to user**:

   ```
   Current mockup (v00[N]) preview:

   [Screenshot]

   This is the HTML mockup with your app's actual styles.
   Any feedback on what to keep, change, or remove?
   ```

## Revert and Compare

### On "revert to v00[N]"

1. Read mockups/v00[N]/mockup.md and mockup.html as new base
2. Create v00[current+1] with that content (both .md and .html)
3. Take new screenshot for reverted version
4. Note in mockup-log.md: "Reverted to v00[N] base"
5. Decisions from v00[N+1] to v00[current] marked as "superseded by revert"
6. User can still access old versions for reference

### On "compare v00[A] and v00[B]"

Generate visual and structural comparison:

1. **Take screenshots** of both versions (if not already saved)
2. **Generate comparison summary**:

```
## v00[A] → v00[B] Visual Comparison

**Screenshots:**

v00[A]:
[preview-v00A.png]

v00[B]:
[preview-v00B.png]

**Structural changes:**

**Added in v00[B]:**
- [element]

**Removed in v00[B]:**
- [element]

**Changed:**
- [element]: [v00A state] → [v00B state]

**Style/Icon changes:**
- [CSS/icon differences if any]

**Decisions between versions:**
- v00[A+1]: [summary]
- v00[A+2]: [summary]
...
```

## Example Interaction

```
User: "Keep the card layout but remove the sidebar. The header should be sticky."

Claude: Updated mockup-log.md:

✓ KEEPING:
  - Card layout - "Keep the card layout"
  - Header (will make sticky)

✗ REMOVING:
  - Sidebar - "remove the sidebar"

~ CHANGING:
  - Header: static → sticky - "header should be sticky"

Ready to create v002?

User: "Yes, and make the cards 3 columns on desktop"

Claude: Got it, adding to changes:

~ CHANGING:
  - Card grid: current → 3 columns on desktop

Creating v002...

Created mockups/v002/
- mockup.md: Updated ASCII with all changes
- mockup.html: Updated HTML with all changes
- preview-v002.png: Visual screenshot
- decisions.md: Documented rationale
- mockup-log.md: Added v002 entry

[Shows preview-v002.png screenshot]

Visual preview updated with your changes. Anything else to adjust?
```

## Session Continuity

If session ends mid-iteration or user requests handoff:

1. **Capture pending feedback** not yet versioned
2. **Update mockup-log.md** with "Pending Feedback" section:

   ```markdown
   ## Pending Feedback (Not Yet Versioned)
   - "[feedback 1]" - KEEP
   - "[feedback 2]" - CHANGE
   ```

3. **Note in handoff document** (if using /wb:create_handoff):
   - Mockup location: [path]
   - Current version: v00[N]
   - Pending feedback: [count] items

On resume, read mockup-log.md's "Pending Feedback" section first.

## DO NOT

- Do not create mockup versions without reading current mockup.md AND mockup.html first
- Do not skip updating mockup-log.md
- Do not skip visual validation (screenshot after creating new version)
- Do not proceed with ambiguous feedback - ask for clarification
- Do not lose track of cumulative requirements across versions
- Do not assume feedback context - confirm if ambiguous whether it's about the mockup
- Do not use emojis in mockup.html (use app's icon system from research or text-only)
- Do not create HTML with placeholder CSS classes (use actual classes from research)
