# Output style

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
