# Output style

Write this output in wb Technical English (WBTE): read [technical-english.md](../../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

Emit this after each phase:

```
✅ <phase> complete
   <2-3 bullets on what the phase produced>

⛔ Barriers before <next phase>:
   - <blocker 1>
   - <blocker 2>

Model gate — <next phase>: recommend <Model>/<effort>. Current: <model or unknown>.
   → <Switch (the reload is worth it: …) | Stay (the current model is enough, or the gain is too small)>.

Next: /wb:<next-phase>  (forge runs it unless you say stop)
```

If nothing blocks the next phase, continue. If something blocks it, stop and report the block.
