---
name: eli5-clip
description: Summarize recent work/changes as a warm, plain-language ("explain like I'm 5") instant-message (Slack/text) for a NON-TECHNICAL person, then copy it to the clipboard ready to paste — do NOT print the message body as text. Cross-platform clipboard (pbcopy/clip.exe/xclip/xsel). Trigger phrases like "eli5 clip", "clip an eli5 summary", "imv eli5", "plain-language recap for [person] to send in Slack", "clip a summary of these changes for [client]", "/eli5-clip".
allowed-tools: Bash
---

Turn what was just done (or a subject the user names) into a friendly, plain-language message a non-technical person can read and act on, then copy it to the system clipboard so the user can paste it straight into Slack / text / email. Do NOT output the message body as text — only copy it and confirm.

## 1. Figure out the subject and audience

- **Subject** — default to the work/changes just completed in this conversation (the thing the user most recently had you do). If the user points at something specific (a diff, a decision, a doc), summarize that instead.
- **Audience** — a non-technical stakeholder: a client, a spouse, a manager, a friend. If the user names them (e.g. "for Autumn"), write to that person by name and match a tone that fits them (warm and casual for a client/friend; a touch more neutral for a manager). If unspecified, write to a generic smart non-technical reader.

## 2. Write it ELI5

Translate the work into outcomes and everyday language. Rules:

- **No jargon, no internals.** Strip branch names, file paths, commit hashes, tool names, and terms like API/FTP/301/redirect/manifest/deploy/schema. Say what it *means* for them ("I rebuilt your page on the new website"), not how it was done.
- **Lead with the outcome / good news.** First line says what's true now.
- **Short sentences, short paragraphs.** Assume a phone screen. A few sentences per idea, blank line between ideas.
- **Call out what they need to do** in a short numbered list, phrased as plain questions/choices — only if there are real decisions or actions for them. If there are none, say "nothing you need to do."
- **Warm and human.** A little emoji is fine and friendly; don't overdo it. Sound like a person, not a status report.
- **Summarize, don't dump.** Pick the few things that matter to *them*. Skip anything purely internal.
- **Paste-ready plain text.** No markdown headings, no bullets with `-`/`*` markup, no code blocks. Use plain line breaks and simple "1)" "2)" numbering. It's going straight into a chat box.
- Keep it tight — a short greeting, 1–3 short paragraphs, an optional short numbered list, a warm close.

## 3. Copy to the clipboard (do not print the body)

Pipe the finished message to this portable helper:

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
# Usage: cat <<'EOF' | clipboard_copy … EOF
```

- Write the message with a quoted heredoc (`<<'EOF'`) so apostrophes/quotes/emoji pass through literally.
- If no clipboard command exists, surface a clear error — do not echo the message to stdout (that defeats the purpose).
- **One message → one copy.** If the user explicitly asks for several separate messages, copy each as its own chained `clipboard_copy` call (separate calls, not one combined blob) so a clipboard-history manager (e.g. Clipy) captures each as a distinct clip; copy them in reverse priority so the most important ends up as the live clipboard.

## 4. Confirm

Do NOT print the message body. Confirm in one line naming the OS command used (e.g. "ELI5 summary copied to clipboard via pbcopy."). You may add a one-line note of what it summarized and to whom, but never the full text.
