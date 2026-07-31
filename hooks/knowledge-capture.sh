#!/usr/bin/env bash

# Automatic knowledge capture at turn and subagent boundaries.
#
# Registered on `Stop` and `SubagentStop`. Reads the payload on stdin and writes
# one staged entry per turn into the store's `staging/` tree.
#
# WHY CAPTURE IS AUTOMATIC AND UNGATED
#
#   The four existing capture points in this plugin all fail the same way: they
#   ask the agent to record something at the moment it is finishing and least
#   inclined to do bookkeeping. A turn-boundary event fires regardless of what
#   the agent decides. Signal is not enforced here — it is enforced at promotion,
#   which is the one component the literature is unanimous cannot be skipped.
#
# WHY EVERY AUTOMATIC CAPTURE IS `model-narrated`
#
#   A hook at a turn boundary sees the model's SUMMARY of what happened, never a
#   tool's observation. `knowledge/SCHEMA.md` is explicit that what makes an
#   entry `tool-verified` is that a tool produced an observation the model did
#   not author — and that mislabelling this axis defeats the write policy, which
#   tiers on exactly it. So this hook cannot emit `tool-verified` at all. That is
#   a property of the event, not a conservative default someone could relax:
#   `tool-verified` is reachable only from the command-level capture points,
#   where a validator verdict or a test result actually exists.
#
# SILENT THERE, LOUD HERE
#
#   No `.wb-knowledge.json` — the repo has not opted in, there is nothing to
#   capture into, and a marketplace install must not shout at every user on every
#   turn. Completely silent.
#
#   Config present but the store is unreachable — that repo DID opt in, and its
#   loop is now recording nothing while looking like it works. design.md calls a
#   no-op capture worse than no capture for exactly this reason. Loud on stderr,
#   plus a `systemMessage` so it reaches the user and not only the log.
#
#   Either way, exit 0. A non-zero `Stop` hook BLOCKS the stop and feeds stderr
#   back to the model, which risks a stop-continue-stop loop. Capture is not
#   important enough to hang a session over, so the deterministic health channel
#   is `--selfcheck` rather than an exit code.
#
# Contract, asserted by scripts/test-knowledge-capture:
#   - writes to staging/ and NEVER to entries/ — staged content is ungated, and
#     if retrieval could reach it, ungated content would steer future tickets
#   - the sequence component is allocated by atomic create with retry, because
#     counting existing files is a read-then-write race (knowledge/SCHEMA.md)
#   - success is quiet; failure inside a configured repo is not

set -uo pipefail

HOOK_NAME="knowledge-capture"
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKTREE_SCRIPT="$(cd "$HOOK_DIR/.." && pwd)/scripts/knowledge-worktree"

USE_JQ=0
if [[ "${WB_KNOWLEDGE_NO_JQ:-0}" != "1" ]] && command -v jq >/dev/null 2>&1; then
    USE_JQ=1
fi

usage() {
    cat <<'USAGE'
Usage: knowledge-capture.sh              (Stop / SubagentStop hook; reads JSON on stdin)
       knowledge-capture.sh --selfcheck  (report whether capture is actually working here)
       knowledge-capture.sh --help

Writes one staged knowledge entry per turn into the store declared by
.wb-knowledge.json. Inert in a repo that declares no store. Every automatic
capture is origin: model-narrated — a turn boundary sees the model's summary,
not a tool's observation.

Environment:
  WB_KNOWLEDGE_NO_JQ=1    force the jq-free parsing fallback
USAGE
}

# Loud, but never fatal: a Stop hook that exits non-zero blocks the stop.
complain() {
    local msg="$1"
    echo "$HOOK_NAME: $msg" >&2
    if [[ $USE_JQ -eq 1 ]]; then
        jq -nc --arg m "$HOOK_NAME: $msg" '{systemMessage:$m}'
    else
        local esc="${msg//\\/\\\\}"
        esc="${esc//\"/\\\"}"
        esc="${esc//$'\n'/ }"
        printf '{"systemMessage":"%s: %s"}\n' "$HOOK_NAME" "$esc"
    fi
}

SELFCHECK=0
case "${1:-}" in
    -h | --help) usage; exit 0 ;;
    --selfcheck) SELFCHECK=1 ;;
    "") ;;
    *) usage >&2; exit 64 ;;
esac

# --- Payload -----------------------------------------------------------------

PAYLOAD=""
CWD=""
SESSION=""
AGENT=""
EVENT=""
MESSAGE=""
TRANSCRIPT=""

if [[ $SELFCHECK -eq 0 ]]; then
    PAYLOAD="$(cat)"
    if [[ $USE_JQ -eq 1 ]]; then
        if ! printf '%s' "$PAYLOAD" | jq -e . >/dev/null 2>&1; then
            # Nothing recoverable, and no repo context to know whether this repo
            # even opted in. Stay silent rather than shout in someone else's repo.
            exit 0
        fi
        CWD="$(printf '%s' "$PAYLOAD" | jq -r '.cwd // empty')"
        SESSION="$(printf '%s' "$PAYLOAD" | jq -r '.session_id // empty')"
        AGENT="$(printf '%s' "$PAYLOAD" | jq -r '.agent_id // empty')"
        EVENT="$(printf '%s' "$PAYLOAD" | jq -r '.hook_event_name // "Stop"')"
        MESSAGE="$(printf '%s' "$PAYLOAD" | jq -r '.last_assistant_message // empty')"
        TRANSCRIPT="$(printf '%s' "$PAYLOAD" | jq -r '.agent_transcript_path // .transcript_path // empty')"
    else
        # scripts/lint-hook's idiom. Adequate for the scalar fields; the message
        # needs its JSON string escapes undone by hand.
        jsonstr() {
            printf '%s' "$PAYLOAD" \
                | grep -o "\"$1\"[[:space:]]*:[[:space:]]*\"\(\\\\.\|[^\"\\\\]\)*\"" \
                | head -1 \
                | sed "s/^\"$1\"[[:space:]]*:[[:space:]]*\"//; s/\"$//"
        }
        CWD="$(jsonstr cwd)"
        SESSION="$(jsonstr session_id)"
        AGENT="$(jsonstr agent_id)"
        EVENT="$(jsonstr hook_event_name)"
        TRANSCRIPT="$(jsonstr agent_transcript_path)"
        [[ -z "$TRANSCRIPT" ]] && TRANSCRIPT="$(jsonstr transcript_path)"
        MESSAGE="$(jsonstr last_assistant_message \
            | sed 's/\\n/\
/g; s/\\t/	/g; s/\\"/"/g; s/\\\\/\\/g')"
        [[ -z "$EVENT" ]] && EVENT="Stop"
    fi
fi

[[ -n "$CWD" ]] || CWD="$PWD"

# --- Has this repo opted in? -------------------------------------------------
# Walk up for the config, exactly as hooks/knowledge-guard.sh does. A repo
# without one is not broken, it simply does not use the store.

find_config() {
    local d="$1"
    while [[ -n "$d" && "$d" != "/" ]]; do
        [[ -f "$d/.wb-knowledge.json" ]] && { printf '%s' "$d"; return 0; }
        d="${d%/*}"
    done
    return 1
}

if ! REPO="$(find_config "$CWD")"; then
    if [[ $SELFCHECK -eq 1 ]]; then
        echo "$HOOK_NAME: inert — no .wb-knowledge.json at or above $CWD, so this repo declares no store."
        echo "  Nothing is being captured here, and that is correct rather than broken."
        exit 3
    fi
    exit 0
fi
REPO="$(cd "$REPO" 2>/dev/null && pwd -P)" || exit 0

# --- Resolve the store -------------------------------------------------------

if [[ ! -x "$WORKTREE_SCRIPT" ]]; then
    complain "cannot find scripts/knowledge-worktree next to this hook ($WORKTREE_SCRIPT). Capture is not running; nothing is being recorded."
    [[ $SELFCHECK -eq 1 ]] && exit 5
    exit 0
fi

# stderr to a file rather than folding it into the same command substitution: a
# `STORE=$(...)` written inside one runs in a subshell and never reaches here.
STORE_ERR_FILE="$(mktemp "${TMPDIR:-/tmp}/knowledge-capture.XXXXXX")"
STORE="$(cd "$REPO" && "$WORKTREE_SCRIPT" 2>"$STORE_ERR_FILE")"
STORE_RC=$?
STORE_ERR="$(cat "$STORE_ERR_FILE" 2>/dev/null)"
rm -f "$STORE_ERR_FILE"

if [[ $STORE_RC -ne 0 || -z "${STORE:-}" ]]; then
    complain "the knowledge store is unreachable, so this turn was NOT captured. $STORE_ERR"
    [[ $SELFCHECK -eq 1 ]] && exit "$STORE_RC"
    exit 0
fi

STAGING="$STORE/staging"
if [[ ! -d "$STAGING" ]]; then
    complain "the store at $STORE has no staging/ directory, so this turn was NOT captured."
    [[ $SELFCHECK -eq 1 ]] && exit 6
    exit 0
fi

if [[ $SELFCHECK -eq 1 ]]; then
    echo "$HOOK_NAME: capture is working"
    echo "  repo:     $REPO"
    echo "  store:    $STORE"
    echo "  staging:  $STAGING"
    # Count by ID shape, not by *.md: staging/ carries a README explaining that
    # the tree is ungated, and counting documentation as captured knowledge
    # would misreport an empty store as a working one.
    echo "  entries:  $(find "$STAGING" -type f -name '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-*.md' 2>/dev/null | wc -l | tr -d ' ') staged so far"
    echo "  origin:   model-narrated (always — a turn boundary sees narration, not tool output)"
    exit 0
fi

# --- Nothing to record is not a failure --------------------------------------

if [[ -z "${MESSAGE//[[:space:]]/}" ]]; then
    exit 0
fi

# --- Build the ID ------------------------------------------------------------
# <UTC-date>-<workspace>-<session8>-<agent8|main>-<seq>   (knowledge/SCHEMA.md)

sanitize() { printf '%s' "$1" | tr -cd '[:alnum:]._-' | tr '[:upper:]' '[:lower:]'; }

DATE_PART="$(date -u +%Y%m%d)"
WORKSPACE_PART="$(sanitize "$(basename "$REPO")")"
SESSION_PART="$(sanitize "${SESSION:0:8}")"
[[ -n "$SESSION_PART" ]] || SESSION_PART="nosession"
if [[ -n "$AGENT" ]]; then
    AGENT_PART="$(sanitize "${AGENT:0:8}")"
else
    AGENT_PART="main"
fi
PREFIX="$DATE_PART-$WORKSPACE_PART-$SESSION_PART-$AGENT_PART"

# Atomic create with retry. SCHEMA.md is explicit that counting existing files is
# a read-then-write race and will eventually lose: two subagents can finish in
# the same millisecond, and the first four components are identical for both.
ENTRY=""
for n in $(seq 1 999); do
    candidate="$STAGING/$PREFIX-$(printf '%03d' "$n").md"
    if (set -o noclobber; : > "$candidate") 2>/dev/null; then
        ENTRY="$candidate"
        break
    fi
done

if [[ -z "$ENTRY" ]]; then
    complain "could not allocate an entry id under $PREFIX after 999 attempts; this turn was NOT captured."
    exit 0
fi

# --- Write the entry ---------------------------------------------------------

SHA="$(cd "$REPO" && git rev-parse HEAD 2>/dev/null)"
[[ -n "$SHA" ]] || SHA="unknown"
ID="$(basename "$ENTRY" .md)"

{
    echo "---"
    echo "id: $ID"
    echo "kind: episodic"
    echo "origin: model-narrated"
    echo "confidence: low"
    echo "status: staged"
    echo "scope:"
    echo "  - repo:$WORKSPACE_PART"
    echo "provenance:"
    echo "  verified_at: $SHA"
    echo "  cites: []"
    echo "capture:"
    echo "  event: ${EVENT:-Stop}"
    echo "  session_id: ${SESSION:-unknown}"
    [[ -n "$AGENT" ]] && echo "  agent_id: $AGENT"
    [[ -n "$TRANSCRIPT" ]] && echo "  transcript: $TRANSCRIPT"
    echo "---"
    echo ""
    printf '%s\n' "$MESSAGE"
    echo ""
    echo "<!-- Captured automatically at a $EVENT boundary. Unreviewed: this is the model's own"
    echo "     account of the turn, which is why origin is model-narrated and confidence is low."
    echo "     It cites no files, so the git staleness sweep will report it undecidable rather"
    echo "     than clean. Promotion is where it earns a claim. -->"
} > "$ENTRY"

exit 0
