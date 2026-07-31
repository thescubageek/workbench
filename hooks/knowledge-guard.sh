#!/usr/bin/env bash

# PreToolUse guard for the knowledge loop's protected-path boundary.
#
# Reads a PreToolUse payload on stdin (same shape scripts/lint-hook parses),
# resolves the target path, consults .wb-knowledge.json, and emits a
# permissionDecision. Three states:
#
#   | Context                            | Decision |
#   | no .wb-knowledge.json in host repo | inert    |  fail-OPEN across repos
#   | config present, no run armed       | inert    |
#   | armed, interactive                 | ask      |
#   | armed, full-auto / unattended      | deny     |
#   | config present, path indeterminate | deny     |  fail-CLOSED within a repo
#
# WHY THE TWO DEFAULTS POINT OPPOSITE WAYS
#
#   ARMING defaults OFF. This hook ships in a marketplace plugin and fires in
#   every install. A false positive blocks someone editing their own commands/
#   or skills/ — the highest-impact risk in design.md's risk table, and a
#   regression that damages users rather than this repo.
#
#   INTERACTIVE defaults OFF. A false positive lets an unattended run downgrade
#   deny to ask and then self-approve. Every other control falls with it.
#
# WHAT ARMING IS, AND WHY IT IS AN ENVIRONMENT VARIABLE
#
#   WB_SELF_EXTENSION is read from the environment of the process that started
#   the session, which is the human act that initiates a self-extension or
#   curation run:
#
#       WB_SELF_EXTENSION=interactive claude          # armed, human present
#       WB_SELF_EXTENSION=full-auto  claude -p ...    # armed, unattended
#
#   Verified by execution 2026-07-31 (Claude Code 2.1.195, probe at
#   /tmp/wb-arm-probe), as an A/B in the same session:
#     - a launch-time env var DOES reach this hook (control run with no var set
#       saw it unset, so the value is genuinely the launch environment's);
#     - an `export WB_SELF_EXTENSION=full-auto` run by the agent's OWN Bash tool
#       executed successfully and did NOT change what this hook subsequently
#       saw. Tool-layer processes are children; they cannot mutate the parent
#       environment this hook inherits.
#
#   Honest limit, per tasks.md's Implementation Discoveries: unreachable for the
#   RUNNING session, influenceable for a LATER one. `.claude/settings.json` has
#   an `env` block that Claude Code applies at session start, so an agent able to
#   write it could arm a future session. That is why .claude/ is in the protected
#   set — and note the influence only runs in the safe direction: arming a run
#   that was not armed adds friction, it does not remove any. The dangerous claim
#   is "interactive", and Phase 0 established that `ask` degrades to outright
#   refusal in every non-interactive mode, so a headless run that successfully
#   claimed interactive would still be refused. Belt and braces.
#
# WHY FULL-AUTO IS ASSUMED RATHER THAN DETECTED
#
#   Phase 0: a headless `claude -p` run reports "permission_mode":"default",
#   byte-identical to an interactive session. Attendance can never be confirmed
#   from inside a hook. permission_mode is therefore used in ONE direction only —
#   it may VETO an interactive claim (an elevated mode suggests nobody is
#   watching), never confirm one.
#
# KNOWN HOLE, NAMED RATHER THAN PAPERED OVER
#
#   This guard sees Write/Edit-family tool calls. A shell redirect through the
#   Bash tool (`printf x > commands/help.md`) produces NO PreToolUse Write event
#   and is not seen — confirmed by execution in the same probe run. Matching
#   paths inside arbitrary shell strings is unreliable, and an unreliable control
#   that fires on `grep -r commands/` would train the operator to disarm. The
#   designed answer is the deferred CI / CODEOWNERS layer (design.md → "Enforcement
#   is hook-only for v1"), which must be built before the first unattended run.
#
# Contract, asserted by scripts/test-knowledge-guard:
#   - inert means SILENT: empty stdout, exit 0
#   - a decision is one line of JSON on stdout, exit 0
#   - it never emits permissionDecision "allow", which would suppress the user's
#     own permission prompts for that call
#   - while armed, any path it cannot resolve to a determinate answer is denied

set -uo pipefail

GUARD_NAME="knowledge-guard"

# --- Arming, read first ------------------------------------------------------
# Before anything that can fail, so the EXIT trap below knows whether it must
# fail closed. Unset or empty is not armed; "interactive" is the only value that
# asserts a human is present; anything else is treated as unattended.

ARM_RAW="${WB_SELF_EXTENSION:-}"
if [[ -z "$ARM_RAW" ]]; then
    ARMED=0
    INTERACTIVE_ASSERTED=0
else
    ARMED=1
    if [[ "$ARM_RAW" == "interactive" ]]; then
        INTERACTIVE_ASSERTED=1
    else
        INTERACTIVE_ASSERTED=0
    fi
fi

RESOLVED=0

emit() {
    local decision="$1" reason="$2"
    RESOLVED=1
    if command -v jq >/dev/null 2>&1 && [[ "${WB_KNOWLEDGE_NO_JQ:-0}" != "1" ]]; then
        jq -nc --arg d "$decision" --arg r "$reason" \
            '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:$d,permissionDecisionReason:$r}}'
    else
        # Minimal escaping: the reasons this script produces contain no control
        # characters, and paths may contain quotes or backslashes.
        local esc="${reason//\\/\\\\}"
        esc="${esc//\"/\\\"}"
        printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"%s","permissionDecisionReason":"%s"}}\n' \
            "$decision" "$esc"
    fi
}

# The three-state decision, and the ONLY place `ask` can be produced. Used for a
# path that is determinately inside the protected set: there, a present human has
# something concrete to approve ("apply proposal 7"), which is what the locked
# constraint means by a human in the loop.
refuse() {
    local why="$1"
    if [[ $INTERACTIVE_ASSERTED -eq 1 && "${MODE_PERMITS_ASK:-0}" == "1" ]]; then
        emit ask "$GUARD_NAME: $why Approve only if you intend this write."
    else
        emit deny "$GUARD_NAME: $why ${DENY_WHY:-This run is treated as unattended, so core self-extension is refused rather than prompted.}"
    fi
}

# The indeterminate case, which is NOT three-state — it denies even with a human
# present. design.md's non-functional requirement is explicit: "if the hook
# cannot determine whether a path is protected, it denies." Prompting here would
# ask a human to approve a write the system itself cannot characterise, which is
# a rubber stamp wearing a gate's clothing. The operator's recourse is to fix the
# path or re-run unarmed, both of which are better than a blind approval.
deny_hard() {
    local what="$1" why="$2"
    emit deny "$GUARD_NAME: $what $why Enforcement fails closed inside a configured repository, with no interactive override: a path that cannot be shown to sit outside the protected set is treated as inside it."
}

# Pass-through and inert are the same observable thing — silence — but they are
# different conclusions, so they are marked separately for the fail-closed trap.
pass() { RESOLVED=1; exit 0; }

# Any exit while armed that did not reach a conclusion is a bug, and a bug in a
# boundary must fail closed rather than silently stop protecting.
finish() {
    [[ $RESOLVED -eq 1 ]] && return
    [[ $ARMED -eq 1 ]] || return
    RESOLVED=1
    emit deny "$GUARD_NAME: internal error before a decision was reached. Refusing the write: enforcement could not be established, and silence is indistinguishable from a working inert hook."
}
trap finish EXIT

USE_JQ=0
if [[ "${WB_KNOWLEDGE_NO_JQ:-0}" != "1" ]] && command -v jq >/dev/null 2>&1; then
    USE_JQ=1
fi

# --- Locate the config -------------------------------------------------------
# Walk up from the session cwd looking for .wb-knowledge.json. The directory
# holding it IS the boundary root: protected_paths are relative to it. A plain
# upward walk rather than `git rev-parse` keeps this free of a git dependency and
# of a subprocess on the hot path, matching hooks/setup-beads-mode.sh.

find_config() {
    local d="$1"
    while [[ -n "$d" && "$d" != "/" ]]; do
        if [[ -f "$d/.wb-knowledge.json" ]]; then
            printf '%s' "$d"
            return 0
        fi
        d="${d%/*}"
    done
    [[ -f "/.wb-knowledge.json" ]] && { printf '/'; return 0; }
    return 1
}

read_protected() {
    if [[ $USE_JQ -eq 1 ]]; then
        jq -r '.protected_paths[]? | select(type == "string")' "$CONFIG" 2>/dev/null
    else
        # Pull the protected_paths array textually. jq is the real path; this is
        # the scripts/lint-hook fallback discipline applied to a small,
        # hand-maintained config.
        awk '
            /"protected_paths"/ { inblock = 1 }
            inblock {
                line = $0
                sub(/.*"protected_paths"[[:space:]]*:[[:space:]]*\[/, "", line)
                if (index(line, "]") > 0) { sub(/\].*/, "", line); print line; exit }
                print line
            }
        ' "$CONFIG" 2>/dev/null | grep -o '"[^"]*"' | sed 's/^"//; s/"$//' | grep -v '^protected_paths$'
    fi
}

# --- Path handling -----------------------------------------------------------
# Two normalisations, because neither alone is sufficient:
#   lexical  — collapses . and .. textually, catching a traversal through a
#              directory that does not exist yet, which no amount of symlink
#              resolution can see
#   real     — resolves symlinks via the deepest existing ancestor, catching a
#              link that points into a protected tree, and normalising macOS's
#              /tmp -> /private/tmp (which Phase 0 observed arriving that way)
#
# They are composed rather than chosen between. Resolving a lexically-normalised
# path and resolving the raw path can legitimately differ when a symlink is
# followed by '..', so BOTH results are kept as candidates and the rules over
# them are monotone toward deny:
#   protected     if ANY candidate lands in the protected set
#   indeterminate if ANY candidate lands outside the boundary root
# Adding a candidate can only ever make the answer stricter, never laxer.

lexical_path() {
    local p="$1" part
    [[ "$p" = /* ]] || p="$BASE_DIR/$p"
    local -a out=()
    local IFS='/'
    for part in $p; do
        case "$part" in
            '' | '.') ;;
            '..') [[ ${#out[@]} -gt 0 ]] && out=("${out[@]:0:${#out[@]}-1}") ;;
            *) out+=("$part") ;;
        esac
    done
    if [[ ${#out[@]} -eq 0 ]]; then
        printf '/'
    else
        printf '/%s' "${out[@]}"
    fi
}

real_path() {
    local p="$1"
    [[ "$p" = /* ]] || p="$BASE_DIR/$p"
    local rest="${p##*/}" dir="${p%/*}"
    [[ -z "$dir" ]] && dir="/"
    while [[ ! -d "$dir" && "$dir" != "/" ]]; do
        rest="${dir##*/}/$rest"
        dir="${dir%/*}"
        [[ -z "$dir" ]] && dir="/"
    done
    local real
    real="$(cd "$dir" 2>/dev/null && pwd -P)" || return 1
    [[ "$real" == "/" ]] && real=""
    printf '%s/%s' "$real" "$rest"
}

# Returns the matching entry on stdout, 0 if protected.
protected_entry() {
    local path="$1" entry stripped
    for entry in "${PROTECTED[@]}"; do
        stripped="${entry%/}"
        [[ -z "$stripped" ]] && continue
        if [[ "$path" == "$ROOT/$stripped" || "$path" == "$ROOT/$stripped"/* ]]; then
            printf '%s' "$entry"
            return 0
        fi
    done
    return 1
}

inside_root() {
    [[ "$1" == "$ROOT" || "$1" == "$ROOT"/* ]]
}

# --- Modes -------------------------------------------------------------------

usage() {
    cat <<'USAGE'
Usage: knowledge-guard.sh              (PreToolUse hook; reads JSON on stdin)
       knowledge-guard.sh --selfcheck  (report whether enforcement is available here)
       knowledge-guard.sh --help

Guards the protected-path set declared in .wb-knowledge.json against writes made
by an ARMED self-extension run. Inert during ordinary development, and inert in
any repository that does not declare a config.

Arming (set by the human act that starts the run, never by the agent):
  WB_SELF_EXTENSION=interactive   armed; a human is present -> protected writes ask
  WB_SELF_EXTENSION=full-auto     armed; unattended        -> protected writes deny
  (unset)                         not armed                -> inert

Environment:
  WB_KNOWLEDGE_NO_JQ=1            force the jq-free parsing fallback
USAGE
}

SELFCHECK=0
case "${1:-}" in
    -h | --help)
        RESOLVED=1
        usage
        exit 0
        ;;
    --selfcheck)
        SELFCHECK=1
        ;;
    "") ;;
    *)
        RESOLVED=1
        usage >&2
        exit 64
        ;;
esac

# --- Read the payload --------------------------------------------------------

PAYLOAD=""
CWD=""
TOOL=""
if [[ $SELFCHECK -eq 0 ]]; then
    PAYLOAD="$(cat)"
    [[ -z "$PAYLOAD" ]] && PAYLOAD="${CLAUDE_TOOL_ARGS:-}"

    if [[ $USE_JQ -eq 1 ]]; then
        if ! printf '%s' "$PAYLOAD" | jq -e . >/dev/null 2>&1; then
            # Unparseable payload. Not armed, nothing to do; armed, this is the
            # indeterminate case and the boundary refuses.
            [[ $ARMED -eq 1 ]] || pass
            deny_hard "Cannot determine what this call would write." \
                "The PreToolUse payload did not parse as JSON, so the write target is unknown."
            exit 0
        fi
        CWD="$(printf '%s' "$PAYLOAD" | jq -r '.cwd // empty')"
        TOOL="$(printf '%s' "$PAYLOAD" | jq -r '.tool_name // empty')"
        MODE="$(printf '%s' "$PAYLOAD" | jq -r 'if has("permission_mode") then .permission_mode else "__ABSENT__" end')"
    else
        CWD="$(printf '%s' "$PAYLOAD" | grep -o '"cwd"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/')"
        TOOL="$(printf '%s' "$PAYLOAD" | grep -o '"tool_name"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/')"
        MODE="$(printf '%s' "$PAYLOAD" | grep -o '"permission_mode"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/')"
        [[ -z "$MODE" ]] && MODE="__ABSENT__"
    fi
fi

[[ -n "$CWD" ]] || CWD="$PWD"
BASE_DIR="$CWD"

# --- Is this repo configured at all? -----------------------------------------

if ! ROOT_RAW="$(find_config "$CWD")"; then
    if [[ $SELFCHECK -eq 1 ]]; then
        RESOLVED=1
        echo "$GUARD_NAME: enforcement UNAVAILABLE — no .wb-knowledge.json at or above $CWD"
        echo "  The guard is inert here by design. A marketplace install must never deny"
        echo "  writes in a repository that has not opted in."
        exit 3
    fi
    pass   # Row 1: fail-open across repos.
fi

ROOT="$(cd "$ROOT_RAW" 2>/dev/null && pwd -P)" || ROOT="$ROOT_RAW"
CONFIG="$ROOT/.wb-knowledge.json"

# --- Not armed: inert, before anything else can fail -------------------------
# Ordering matters. Ordinary development must not be able to trip this hook even
# when the config is broken, or a bad merge would block the maintainer fixing it.

if [[ $ARMED -eq 0 && $SELFCHECK -eq 0 ]]; then
    pass   # Row 2.
fi

# --- Read the boundary -------------------------------------------------------

CONFIG_OK=1
if [[ $USE_JQ -eq 1 ]] && ! jq -e . "$CONFIG" >/dev/null 2>&1; then
    CONFIG_OK=0
fi

PROTECTED=()
if [[ $CONFIG_OK -eq 1 ]]; then
    while IFS= read -r line; do
        [[ -n "$line" ]] && PROTECTED+=("$line")
    done < <(read_protected)
fi

if [[ $SELFCHECK -eq 1 ]]; then
    RESOLVED=1
    if [[ $CONFIG_OK -eq 0 ]]; then
        echo "$GUARD_NAME: enforcement UNAVAILABLE — $CONFIG is not valid JSON"
        echo "  An armed run will refuse every guarded write until this parses."
        exit 4
    fi
    if [[ ${#PROTECTED[@]} -eq 0 ]]; then
        echo "$GUARD_NAME: enforcement UNAVAILABLE — $CONFIG declares no protected_paths"
        echo "  There is no boundary to enforce. An armed run will refuse every guarded write."
        exit 4
    fi
    echo "$GUARD_NAME: enforcement AVAILABLE"
    echo "  repo root: $ROOT"
    echo "  config:    $CONFIG"
    echo "  boundary:  ${#PROTECTED[@]} protected paths"
    if [[ $ARMED -eq 0 ]]; then
        echo "  armed:     no — WB_SELF_EXTENSION is unset, so the guard is inert this session"
    elif [[ $INTERACTIVE_ASSERTED -eq 1 ]]; then
        echo "  armed:     yes, interactive — protected writes will prompt for approval"
    else
        echo "  armed:     yes, unattended ('$ARM_RAW') — protected writes will be refused"
    fi
    if [[ $USE_JQ -eq 1 ]]; then
        echo "  parser:    jq"
    else
        echo "  parser:    jq-free fallback"
    fi
    exit 0
fi

# --- Armed from here. Every failure below refuses. ---------------------------

# permission_mode may only VETO an interactive claim, never establish one.
# default and acceptEdits are the two modes compatible with a human at a
# terminal — acceptEdits is the mode Phase 0's human-run A/B actually observed
# prompting. Everything else, including an absent or unrecognised value, is
# treated as possibly-unattended and collapses ask to deny.
MODE_PERMITS_ASK=0
case "$MODE" in
    default | acceptEdits) MODE_PERMITS_ASK=1 ;;
    *) MODE_PERMITS_ASK=0 ;;
esac
if [[ $INTERACTIVE_ASSERTED -eq 1 && $MODE_PERMITS_ASK -eq 0 ]]; then
    DENY_WHY="The run asserted 'interactive', but permission_mode is '$MODE' — a mode that suggests nobody is watching. An interactive assertion can be vetoed by the permission mode, never confirmed by it, so this is treated as unattended."
fi

if [[ $CONFIG_OK -eq 0 ]]; then
    deny_hard "Cannot establish the protected-path boundary." \
        "$CONFIG is not valid JSON, so the protected set cannot be read. Run 'hooks/knowledge-guard.sh --selfcheck' to confirm; an unenforced boundary must not be mistaken for a passing one."
    exit 0
fi

if [[ ${#PROTECTED[@]} -eq 0 ]]; then
    deny_hard "Cannot establish the protected-path boundary." \
        "$CONFIG declares no protected_paths, so there is nothing to enforce."
    exit 0
fi

# Tools that do not write are never the concern. An unrecognised or absent tool
# name falls through to the path check, which refuses when it finds nothing.
case "$TOOL" in
    Read | Grep | Glob | LS | Bash | WebFetch | WebSearch | Task | TodoWrite) pass ;;
esac

# --- Extract the target ------------------------------------------------------

TARGETS=()
if [[ $USE_JQ -eq 1 ]]; then
    while IFS= read -r line; do
        [[ -n "$line" ]] && TARGETS+=("$line")
    done < <(printf '%s' "$PAYLOAD" | jq -r '[.tool_input.file_path?, .tool_input.notebook_path?, .tool_input.path?] | .[] | select(type == "string" and . != "")' 2>/dev/null)
else
    # The fallback cannot tell a real field from the same text appearing inside
    # tool_input.content, so it takes EVERY candidate and protects if ANY of them
    # is protected. A decoy can only add candidates, never remove the real one,
    # so the ambiguity resolves toward deny.
    while IFS= read -r line; do
        [[ -n "$line" ]] && TARGETS+=("$line")
    done < <(printf '%s' "$PAYLOAD" \
        | grep -o '"\(file_path\|notebook_path\)"[[:space:]]*:[[:space:]]*"[^"]*"' \
        | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/')
fi

if [[ ${#TARGETS[@]} -eq 0 ]]; then
    deny_hard "Cannot determine what this call would write." \
        "The call carries no file path, so it cannot be shown to fall outside the protected set."
    exit 0
fi

# --- Decide ------------------------------------------------------------------

for target in "${TARGETS[@]}"; do
    lex="$(lexical_path "$target")"
    via_lex="$(real_path "$lex")" || via_lex="$lex"
    via_raw="$(real_path "$target")" || via_raw="$lex"

    CANDIDATES=("$via_lex")
    [[ "$via_raw" != "$via_lex" ]] && CANDIDATES+=("$via_raw")

    for candidate in "${CANDIDATES[@]}"; do
        if entry="$(protected_entry "$candidate")"; then
            refuse "'$target' resolves to $candidate, inside the protected path '$entry'. That path is core self-extension: the machinery that steers or evaluates this system, which is permanently human-gated."
            exit 0
        fi
    done

    # Phase 0: the path a hook receives is resolved and absolute, and is not
    # necessarily the one anyone named — writes were observed being redirected
    # into /private/tmp/claude-501/<slug>/<uuid>/scratchpad/. So "outside every
    # protected prefix" is NOT "safe"; a naive repo-relative prefix match is both
    # bypassable and wrong. Outside the boundary root is the indeterminate case.
    for candidate in "${CANDIDATES[@]}"; do
        if ! inside_root "$candidate"; then
            deny_hard "'$target' resolves to $candidate, outside the repository at $ROOT that declares the boundary." \
                "Out there the protected set has no meaning, so the write cannot be shown to be safe. Claude Code has been observed redirecting writes into a per-session scratchpad, which is exactly this shape."
            exit 0
        fi
    done
done

pass
