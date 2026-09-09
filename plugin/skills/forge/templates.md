# forge — templates

Read this when a step directs you to.

## Output style

After each phase:

```
✅ <phase> complete
   <2-3 bullets of what was produced>

⛔ Barriers before <next phase>:
   - <blocker 1>
   - <blocker 2>

Model gate — <next phase>: recommend <Model>/<effort>. Current: <model or unknown>.
   → <Switch (worth the reload: …) | Stay (sufficient / delta too small)>.

Next: /wb:<next-phase>  (forge will invoke unless you say stop)
```

If everything is clear, advance. If anything is blocked, stop and report.

## Model plan

Emitted once, at the start of a forge, for the phases still ahead.

```
Model plan (this forge): research Sonnet/med → design Opus/high ⬆ → create_tasks Sonnet/med ⬇ → implement Sonnet/med → validate Sonnet/med
Switches: up to Opus for design, back to Sonnet after. Everything else stays put.
```

Skip the table for a trivial single-phase pickup; a one-liner is enough.
