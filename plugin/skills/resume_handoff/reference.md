# resume_handoff — reference

Read this when a step directs you to.

## Purpose

**Same machine? Use native `claude --resume` instead** — it restores the full prior session (messages + tool results) more reliably than any document. This skill is for **cross-machine / cross-agent / teammate** resumption, where the live session isn't available.

This skill:

- Restores full context from handoff document
- Reads all referenced project files
- Understands problems solved and blockers
- Continues work without repeating discoveries
- Maintains consistency with previous decisions

## Validation Steps

After resuming, verify continuity:

1. **Code State Verification**:

   ```bash
   # Run tests to ensure starting state is good
   npm test  # or appropriate test command

   # Check build still works
   npm run build
   ```

2. **Progress Verification**:
   - Confirm the phase matches the handoff
   - Confirm the checkbox counts match what the handoff claimed
   - Verify no work was lost

3. **Context Verification**:
   - Apply a learning from handoff
   - Reference a solved problem
   - Use a discovered pattern

## Important Guidelines

### Resume Best Practices

1. **Trust the Handoff**: Previous session did the discovery work
2. **Don't Repeat**: Avoid re-solving problems documented
3. **Stay Consistent**: Follow patterns and decisions made
4. **Build on Learnings**: Apply insights discovered
5. **Continue Momentum**: Pick up where left off, don't restart

### When Handoff Conflicts with Code

If handoff says one thing but code shows another:

1. **Trust the code** for current state — the repository is the only thing that always survives; a document records what someone believed at the moment they wrote it
2. **Trust the handoff** for learnings and context — the code cannot tell you what was tried and abandoned
3. **Document the discrepancy** in the resume confirmation, naming which you took
4. **Proceed with caution**
5. **Consider validation** via `/wb:validate_execution`

### Quality Indicators

A successful resume shows:

- Immediate understanding of context
- No repeated discovery work
- Consistent approach with previous session
- Forward progress from exact stopping point
- Application of documented learnings

## Relationship to Other Commands

Common workflows:

**Simple Resume**:

1. **`/wb:resume_handoff`** - Load context
2. `/wb:implement` - Continue implementation
3. `/wb:validate_execution` - Verify when phase complete

**Complex Resume with Validation**:

1. **`/wb:resume_handoff`** - Load context
2. `/wb:validate_execution` - Check actual state
3. Resolve any discrepancies
4. `/wb:implement` - Continue work

**Chain of Handoffs**:

1. **`/wb:resume_handoff`** - Session 2 resumes from Session 1
2. Work on implementation
3. `/wb:create_handoff` - Session 2 creates new handoff
4. [New session]
5. **`/wb:resume_handoff`** - Session 3 continues chain

## Error Handling

### Handoff File Not Found

```
❌ Error: Handoff file not found at [path]

Please check:
1. File path is correct
2. You're in the right repository
3. File wasn't moved or deleted

You may need to:
- Search for handoff files: find . -name "handoff-*.md"
- Start fresh with project documentation
```

### Invalid Handoff Format

```
❌ Error: Handoff document missing critical sections

Required sections not found:
- [Missing section]

This may not be a valid handoff document.
Check the file path or create a new handoff.
```

### Plan Directory Missing

```
❌ Error: Handoff references [project-dir], which does not exist here

Plan directories are gitignored by default, so a handoff that crossed machines
may have arrived without its documents.

On the sending machine:
  git add -f [project-dir]/ && git commit && git push

Then pull here and re-run.
```

## Configuration

This skill restores complete context from handoff documents. It's essential for maintaining continuity across sessions and preventing loss of discovered knowledge.

Best used:

- When resuming incomplete work
- After session timeout or limit
- When switching between models
- For collaborative handoffs between team members

The resume process ensures no context is lost and work continues efficiently without repeating discoveries or solving already-solved problems.
