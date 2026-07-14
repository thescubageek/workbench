# Beads Fast-Fail

wb tracks tasks in [beads](https://github.com/steveyegge/beads) (`bd`). But a
command must never **hang or loop** because beads is missing. Since the embedded-Dolt
migration, spawning a `bd` subprocess (even `bd doctor`) can be slow to start — so
probing beads with a `bd` command on every task is exactly what stalls a session.

**The rule:** determine beads availability with a *fast, filesystem-only* check, then
either proceed or degrade cleanly. Never block, retry, or spin on it.

## Fast availability check (no `bd` subprocess)

Availability is computed **once at session start** by `hooks/setup-beads-mode.sh` and
exposed as an env var. Prefer reading the variable — it costs nothing:

```bash
# Preferred: read the SessionStart-computed flag.
[ "$BEADS_AVAILABLE" = "yes" ]   # beads is usable
[ "$BEADS_AVAILABLE" = "no" ]    # beads is NOT usable -> fast-fail path
```

If the variable is unset (hook didn't run, or `.beads/` was created mid-session),
fall back to a pure filesystem + binary probe — still no `bd` subprocess:

```bash
beads_ready() {
  case "$BEADS_AVAILABLE" in
    yes) return 0 ;;
    no)  return 1 ;;
  esac
  command -v bd >/dev/null 2>&1 || return 1          # bd not installed
  d="$PWD"; while [ -n "$d" ]; do                    # .beads/ at cwd or an ancestor
    [ -d "$d/.beads" ] && return 0
    d="${d%/*}"
  done
  return 1
}
```

`bd doctor` is **not** an availability probe. Reserve it for *diagnosing* a `bd`
command that actually errored (see the Beads Error Handling section in CLAUDE.md) —
not for deciding whether beads exists.

## Fast-fail behavior when beads is unavailable

Two categories of caller, two behaviors — both non-blocking:

### Beads-required work (create_execution, implement_tasks, implement_coordinated, forge)

These need status tracking. When `beads_ready` is false, **say it once, offer the
one-liner, and stop or continue per the user — never loop**:

```
⚠️ Beads unavailable (bd not installed or .beads/ not initialized).
   To enable task tracking:  bd init
   Proceeding without beads tracking — status won't persist across sessions.
```

- Surface the message a **single time**; do not re-probe or re-prompt each phase.
- Offer `bd init` as a one-line fix, then honor the user's choice.
- If continuing without beads, track the plan in the markdown files only and say so.
- Do **not** run `bd doctor` in a retry loop hoping it comes up.

### Beads-optional work (daily-digest, status-sync, reminders)

Beads is just one input. When unavailable, **skip it and move on** — record it as a
gap, don't warn loudly:

```
beads: unavailable (skipped) — bd not installed or project not initialized
```

## Summary

- Availability = **filesystem + binary**, decided once at SessionStart (`$BEADS_AVAILABLE`).
- Never probe with a `bd` subprocess; never retry/loop on absence.
- Required callers: one message + `bd init` offer, then proceed or stop.
- Optional callers: skip silently, note the gap.
