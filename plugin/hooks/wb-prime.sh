#!/bin/bash
# SessionStart/PreCompact hook: session-start orientation, the plan bootstrap, and
# compaction recovery.
#
# Contract (inherited from the hook this replaces):
#   - fast: filesystem reads plus one cheap `git status` (which fails quietly and
#     costs nothing outside a repository)
#   - reads only. It NEVER writes a file, and in particular never touches journal.md:
#     an append-only record that a hook could corrupt is worse than no record. The
#     mechanical fields a PreCompact write would have refreshed are recomputed here,
#     at session start, from the repository — which is authoritative anyway.
#   - plain-text stdout. SessionStart's stdout is model-visible; PreCompact's is not,
#     but the hook still exits 0 and prints harmlessly.
#   - silent on an empty or unrecognized payload
#   - exit 0 always. A hook that fails a session start is worse than no hook.
#
# Override: `.claude/wb/PRIME.md` in the cwd replaces the static orientation block
# (the recovery text and the bootstrap are never overridden — they are facts, not prose).
# `--export` prints the default orientation and exits, regardless of stdin.

orientation() {
  cat <<'ORIENTATION'
wb: structured development workflow. Orientation for this session.

Stages, in order. Each reads the previous stage's document and stops if it is missing or not approved:
  /wb:create_project     -> docs/plans/<date>-<name>/ with README, research.md, design.md, tasks.md, journal.md
  /wb:create_research    -> research.md: facts only, file:line references, no recommendations
  /wb:explore_design     -> optional: air the alternatives; records the decision at the top of a thoughts/ document
  /wb:create_design      -> design.md: what to build and why; needs research.md complete
  /wb:create_tasks       -> tasks.md: phased plan, every task a checkbox with a local ID; needs design.md approved
  /wb:implement          -> the recommended path: one worker per task, verified, committed, one phase at a time
  /wb:implement_inline   -> the same plan, coded inline on this session's model
  /wb:validate_execution -> pass/fail against design.md and tasks.md after a phase or the plan
  /wb:create_handoff, /wb:resume_handoff -> carry context across sessions, models, and machines

Where status lives — there is no external tracker:
  Checkbox state in tasks.md is the truth. Flipping `- [ ]` to `- [x]` IS the act of recording a task done.
  The frontmatter counters are a derived cache. /wb:update_status is their only writer; never hand-edit them.
  Git is the durable record: one task, one commit, task ID in the message.
  Questions, assumptions and pending decisions live in the document that raises them, with local IDs (Q1, A1, PD1).

Conventions:
  Plans live in docs/plans/<date>-<name>/ and are gitignored until promoted with `git add -f`.
  Checkpoints stop for a human between phases. Never declare a phase complete while one of its checkboxes is `[ ]`.
  Long form: /wb:help. Replace this text for a repository with .claude/wb/PRIME.md (print the default with hooks/wb-prime.sh --export).
ORIENTATION
}

# `grep -c` prints `0` AND exits 1 when nothing matches. `|| echo 0` would therefore
# print a *second* zero, and every arithmetic use of the result would then die with a
# syntax error — which is exactly what a freshly generated tasks.md (no task lines yet)
# produced. Swallow the status; default only the file-missing case, where grep prints
# nothing at all.
count() {
  n=$(grep -cE "$1" "$2" 2>/dev/null) || true
  echo "${n:-0}"
}

if [ "$1" = "--export" ]; then
  orientation
  exit 0
fi

payload=$(cat 2>/dev/null || true)
[ -z "$payload" ] && exit 0

# Active plans: any docs/plans/*/tasks.md whose status is not complete, newest first.
# Ordered by directory NAME descending, not by mtime. Plan directories are
# `YYYY-MM-DD-<slug>`, so reverse-lexical is date order — and it survives a fresh clone
# or a branch checkout, which stamp every file with the same mtime and make `ls -t`
# arbitrary. That matters because the `Active plan:` line below is read downstream as the
# answer to "which plan", so an arbitrary winner is a wrong answer, not just an odd sort.
candidates=""
if [ -d docs/plans ]; then
  for f in $(ls -d docs/plans/*/ 2>/dev/null | sort -r | sed 's|$|tasks.md|'); do
    [ -f "$f" ] || continue
    status=$(sed -n '1,30p' "$f" | grep -m1 '^status:' | sed 's/^status:[[:space:]]*//')
    [ "$status" = "complete" ] && continue
    candidates="$candidates${candidates:+ }$(basename "$(dirname "$f")")"
  done
fi
count=$(echo "$candidates" | wc -w | tr -d ' ')

# ---------------------------------------------------------------- recovery mode
if echo "$payload" | grep -qE '"compact"|PreCompact'; then
  [ "$count" -eq 0 ] && exit 0
  echo "Context was just compacted — any plan-doc summaries above are paraphrase, not verified content."
  if [ "$count" -eq 1 ]; then
    echo "Active plan: docs/plans/$candidates"
  else
    echo "Candidate plans (newest first): $candidates"
  fi
  echo "Before asserting what research.md/design.md/tasks.md say, re-read them fully from the plan directory above."
  echo "Read task status from the checkboxes in tasks.md, not from the summary — the summary is where stale counts survive."
  exit 0
fi

# ------------------------------------------------------------ orientation mode
if [ -f .claude/wb/PRIME.md ]; then
  cat .claude/wb/PRIME.md
else
  orientation
fi

# ------------------------------------------------- bootstrap (D8c), read-only
if [ "$count" -eq 0 ]; then
  echo ""
  echo "Active plans in this repository: none"
  exit 0
fi

plan=$(echo "$candidates" | cut -d' ' -f1)
dir="docs/plans/$plan"
tasks="$dir/tasks.md"

echo ""
if [ "$count" -eq 1 ]; then
  echo "Active plan: $dir"
else
  echo "Active plan: $dir  (also open: $(echo "$candidates" | cut -d' ' -f2-))"
fi

# Position. Scope the counts to lines carrying a task ID: a plan's success criteria
# and prerequisites are checkboxes too, and counting them overstates progress.
done_n=$(count '^- \[x\] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' "$tasks")
left_n=$(count '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' "$tasks")
phase=$(sed -n '1,30p' "$tasks" | grep -m1 '^current_phase:' | sed 's/^current_phase:[[:space:]]*//')
if [ $((done_n + left_n)) -gt 0 ]; then
  echo "Position: phase ${phase:-?}, $done_n of $((done_n + left_n)) tasks done."
  next=$(grep -m1 -E '^- \[ \] \*\*[A-Z0-9-]*[0-9][A-Z0-9-]*\*\*' "$tasks" 2>/dev/null | sed 's/^- \[ \] //')
  # Trim at a word boundary and mark the elision. A bare `cut` stops mid-word, which
  # reads as a truncation bug rather than as a deliberate one-line summary.
  if [ ${#next} -gt 100 ]; then
    next="$(printf '%s' "$next" | cut -c1-97 | sed 's/[[:space:]][^[:space:]]*$//')…"
  fi
  [ -n "$next" ] && echo "Next unchecked task: $next"
fi

# Journal tail, and whether the last entry is open.
journal="$dir/journal.md"
entry_open=no
if [ -f "$journal" ]; then
  last=$(grep -m1 -E '^## ' "$journal" 2>/dev/null)
  if [ -n "$last" ]; then
    echo "Journal, most recent entry: $last"
    # The state lives in a trailing `(open)` / `(closed)`, matched case-insensitively and
    # ANCHORED to the end of the heading. Not a substring search for "OPEN": that misses the
    # lowercase form a writer reaches for unprompted, and it false-positives on a closed
    # entry whose title contains "reopened". The shape is stated at every site that writes an
    # entry — create_project's template, implement, implement_inline, create_handoff,
    # resume_handoff — and checked by validate_project.
    case "$(printf '%s' "$last" | tr 'A-Z' 'a-z' | sed 's/[[:space:]]*$//')" in
      *'(open)') entry_open=yes ;;
    esac
  else
    echo "Journal: present, no entries yet"
  fi
fi

# Reconcile against the working tree. The repository is the authority — never report
# the journal as fact when the two disagree.
# Never test `[ -d .git ]`: in a git worktree `.git` is a *file*, and in any session
# started from a subdirectory it is absent entirely — both cases would report a dirty
# tree as clean and invert the reading below. Ask git instead; outside a repository it
# fails quietly and the count is 0.
dirty=$(git status --porcelain --untracked-files=no 2>/dev/null | grep -c . || true)
dirty=${dirty:-0}
if [ "$entry_open" = yes ] && [ "$dirty" -gt 0 ]; then
  echo "!! That entry is OPEN and the tree has $dirty uncommitted file(s): a task was interrupted mid-flight."
  echo "   Finish or supersede it before starting anything new. The entry's next action is the most reliable thing here."
elif [ "$entry_open" = yes ]; then
  echo "!! That entry is OPEN but the tree is clean: a session left it open without finishing the close-out, not mid-task."
elif [ "$dirty" -gt 0 ]; then
  echo "!! The last entry is closed but the tree has $dirty uncommitted file(s) — something ran outside the journal. Check before trusting either."
fi

# Knowledge file: named, not printed. It is read on demand by the stages that benefit.
kb=".claude/wb/knowledge.md"
if [ -f "$kb" ]; then
  # Count real entries by their Verified line — '^## ' would also count the file's own
  # header sections and the shape example inside its fenced block.
  n=$(count '^- \*\*Verified\*\*' "$kb")
  n=$((n > 0 ? n - 1 : 0))   # the shape example carries one too
  echo "Repository knowledge: $kb ($n entries) — read it before research, design, or implementation."
fi

exit 0
