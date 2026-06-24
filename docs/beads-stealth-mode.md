# Beads Mode: git vs stealth

`$BEADS_MODE` is set by the wb SessionStart hook (`hooks/setup-beads-mode.sh`),
which detects whether `.beads/` is git-ignored. wb commands read this variable
and behave identically for task tracking within a session — the modes differ
only in cross-session / cross-machine persistence.

## Git mode (default)

- `.beads/` is tracked in git.
- Beads issues **and** the `.beads/` directory are committed, so state persists
  across sessions and machines via git.
- After `bd sync`, commit `.beads/` to persist
  (e.g. `git add .beads/ && git commit -m "Sync beads state"`).
- Good for personal projects with git-based collaboration.

## Stealth mode

- `.beads/` is git-ignored (local-only), ideally registered in
  `.git/info/exclude` rather than a committed `.gitignore`. Run
  `bd init --stealth` to configure it properly.
- Beads issues are created and tracked locally, but `.beads/` is **not**
  committed — teammates won't see beads tracking. Useful for work repos.
- After `bd sync`, beads state stays local (no git commit).
- For **handoffs**, document next steps manually in the handoff doc, since beads
  state will not travel via git.

## For commands

- **git mode** is the common path — proceed with the normal git-commit/sync
  behavior described above.
- **stealth mode** — follow the stealth rules above; do not commit `.beads/`.
