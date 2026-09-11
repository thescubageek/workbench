# Status Transition Logic

## Research Status Transitions

```
draft → in-progress
  Trigger: User starts researching, some sections have content

in-progress → complete
  Trigger: All sections populated with real findings
  Requires: No placeholder text like "[To be added]"
```

## Design Status Transitions

```
draft → approved
  Trigger: the human confirms the design at create_design's Step 6
  Requires: research.md is complete; no Pending Decisions row still Open
  NEVER infer this from content. `approved` records a human's judgement, and it is
  the gate /wb:create_tasks and forge both read. Advancing it because the document
  looks finished removes the only review step between a design and the tasks built
  on it — so if you find design.md at `draft` with everything else complete, say so
  and ask; do not flip it.
```

`draft` and `approved` are the only two values. Earlier drafts of this file listed
`ready`/`implementing` for a "plan" document — no stage ever wrote or read those, and
`create_tasks` gates on `approved`, so they are gone.

## Tasks Status Transitions

```
not-started → in-progress
  Trigger: At least one task checkbox is [x]
  Updates: current_phase to the phase holding the first unchecked task
  Note:    Phase 0's planning tasks count. They are ticked while design.md is still
           `draft`, and that is legitimate — see the implementation-task guard in
           SKILL.md Step 3. Do not read that guard as forbidding this transition.

in-progress → complete
  Trigger: Every task checkbox is [x]
  Requires: each phase's manual verification confirmed at its checkpoint
```
