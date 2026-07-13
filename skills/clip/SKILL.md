---
name: clip
description: Execute the user's instruction, then copy the final result to the system clipboard. Do not output the result as text — only copy it to the clipboard and confirm it was copied. Cross-platform — uses pbcopy on macOS, clip.exe (or clip) on Windows, xclip/xsel on Linux. Trigger phrases like "clip this", "copy this to clipboard", "/clip", or any user request invoking clip.
allowed-tools: Bash
---

Execute the user's instruction below, then copy the final result to the system clipboard. Do not output the result as text — only copy it to the clipboard and confirm it was copied.

## Clipboard command by host OS

Use the command appropriate for the host the skill is running on:

- **macOS**: `pbcopy`
- **Windows** (Git Bash / WSL / Cowork on PC): `clip.exe` (or just `clip` depending on PATH)
- **Linux**: `xclip -selection clipboard -in` or `xsel --clipboard --input`

A portable one-liner that picks the right command and falls back gracefully:

```bash
clipboard_copy() {
  if command -v pbcopy >/dev/null 2>&1; then pbcopy
  elif command -v clip.exe >/dev/null 2>&1; then clip.exe
  elif command -v clip >/dev/null 2>&1; then clip
  elif command -v xclip >/dev/null 2>&1; then xclip -selection clipboard -in
  elif command -v xsel >/dev/null 2>&1; then xsel --clipboard --input
  else
    echo "ERROR: no clipboard command found (tried pbcopy, clip.exe, clip, xclip, xsel)" >&2
    return 1
  fi
}

# Usage: echo "result" | clipboard_copy
```

If no clipboard command is available on the host, surface a clear error rather than echoing the result to stdout — echoing defeats the purpose of the skill.

## Confirmation

After the copy succeeds, confirm with a brief one-line message naming the OS-appropriate command used (e.g., "Copied to clipboard via clip.exe.") so the user knows the operation actually fired and which command path was taken.

$ARGUMENTS
