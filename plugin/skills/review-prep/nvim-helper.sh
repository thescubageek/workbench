#!/bin/bash
#
# nvim-helper.sh - Helper script for review-prep skill
# Auto-approved via permissions to avoid constant prompts
#
# Usage:
#   nvim-helper.sh setup          # Find or create nvim pane, return pane ID
#   nvim-helper.sh open FILE LINE # Open file at line in nvim pane
#   nvim-helper.sh focus          # Focus the nvim pane
#   nvim-helper.sh status         # Check if nvim pane exists

set -euo pipefail

NVIM_PANE_FILE="/tmp/claude-review-nvim-pane"

find_nvim_pane() {
    tmux list-panes -F "#{pane_id} #{pane_current_command}" 2>/dev/null | grep -i nvim | head -1 | awk '{print $1}'
}

cmd_setup() {
    # Check if we're in tmux
    if [ -z "${TMUX:-}" ]; then
        echo "ERROR: Not in a tmux session"
        exit 1
    fi

    # Find existing nvim pane
    local pane
    pane=$(find_nvim_pane)

    if [ -z "$pane" ]; then
        # Create new nvim pane
        tmux split-window -h "nvim"
        sleep 0.5
        pane=$(find_nvim_pane)
    fi

    if [ -z "$pane" ]; then
        echo "ERROR: Could not find or create nvim pane"
        exit 1
    fi

    # Save pane ID for other commands
    echo "$pane" > "$NVIM_PANE_FILE"
    echo "NVIM_PANE=$pane"
}

cmd_open() {
    local file="${1:-}"
    local line="${2:-1}"

    if [ -z "$file" ]; then
        echo "ERROR: No file specified"
        exit 1
    fi

    # Get saved pane ID or find it
    local pane
    if [ -f "$NVIM_PANE_FILE" ]; then
        pane=$(cat "$NVIM_PANE_FILE")
    else
        pane=$(find_nvim_pane)
    fi

    if [ -z "$pane" ]; then
        echo "ERROR: No nvim pane found. Run 'setup' first."
        exit 1
    fi

    # Open file at line
    tmux send-keys -t "$pane" Escape ":e +${line} ${file}" Enter
    echo "Opened $file at line $line"
}

cmd_focus() {
    local pane
    if [ -f "$NVIM_PANE_FILE" ]; then
        pane=$(cat "$NVIM_PANE_FILE")
    else
        pane=$(find_nvim_pane)
    fi

    if [ -z "$pane" ]; then
        echo "ERROR: No nvim pane found"
        exit 1
    fi

    tmux select-pane -t "$pane"
    echo "Focused nvim pane"
}

cmd_status() {
    local pane
    pane=$(find_nvim_pane)

    if [ -n "$pane" ]; then
        echo "NVIM_PANE=$pane"
        echo "STATUS=ready"
    else
        echo "NVIM_PANE="
        echo "STATUS=not_found"
    fi
}

# Main command dispatch
case "${1:-}" in
    setup)
        cmd_setup
        ;;
    open)
        cmd_open "${2:-}" "${3:-1}"
        ;;
    focus)
        cmd_focus
        ;;
    status)
        cmd_status
        ;;
    *)
        echo "Usage: nvim-helper.sh {setup|open|focus|status}"
        echo ""
        echo "Commands:"
        echo "  setup           Find or create nvim pane"
        echo "  open FILE LINE  Open file at line in nvim"
        echo "  focus           Focus the nvim pane"
        echo "  status          Check nvim pane status"
        exit 1
        ;;
esac
