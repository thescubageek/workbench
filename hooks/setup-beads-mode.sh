#!/usr/bin/env bash
# Detect beads AVAILABILITY and MODE once at session start.
# Exposes two env vars for wb commands/skills (see docs/beads-fast-fail.md):
#   BEADS_AVAILABLE = yes | no      -> bd binary installed AND a .beads/ dir exists
#   BEADS_MODE      = stealth | git -> how .beads/ persists (only meaningful when available)
#
# FAST-FAIL: uses filesystem + binary checks ONLY. It never spawns a `bd`
# subprocess -- since the embedded-Dolt migration, `bd doctor`/`bd <cmd>` can be
# slow to start, and probing beads on every task is what makes sessions hang.
# Determining availability once, cheaply, here lets commands read a variable.

if [ -z "$CLAUDE_ENV_FILE" ]; then
  exit 0
fi

# Availability: bd on PATH, and a .beads/ dir at cwd or any ancestor (beads
# searches upward). Pure shell -- no `bd`, no `find`, no per-check subprocess.
beads_available=no
if command -v bd >/dev/null 2>&1; then
  d="$PWD"
  while [ -n "$d" ]; do
    if [ -d "$d/.beads" ]; then
      beads_available=yes
      break
    fi
    d="${d%/*}"
  done
fi
echo "export BEADS_AVAILABLE=$beads_available" >> "$CLAUDE_ENV_FILE"

# Mode: whether .beads/ is git-ignored (stealth) or tracked (git).
if git check-ignore -q .beads/ 2>/dev/null; then
  echo 'export BEADS_MODE=stealth' >> "$CLAUDE_ENV_FILE"
else
  echo 'export BEADS_MODE=git' >> "$CLAUDE_ENV_FILE"
fi

exit 0
