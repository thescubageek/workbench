#!/usr/bin/env bash
# Plan-local checks for prompt_audit_5_5 (tasks.md P1-T2).
# Usage: prompt-checks.sh <check>...   Prints "name: <count> (target <n>) PASS|FAIL" for each
# check and exits 1 if any check fails. A grep that errors (exit 2) is a FAIL, never a count of 0.
# PROMPT_CHECKS_REPO overrides the repository root. PROMPT_CHECKS_ROOTS (space-separated paths,
# relative to the root) narrows triple-barriers, notification, and caps to some files.
set -u
REPO="${PROMPT_CHECKS_REPO:-$(cd "$(dirname "$0")" && git rev-parse --show-toplevel)}"
ROOTS="${PROMPT_CHECKS_ROOTS:-plugin}"
STATUS=0

# The agent tiers of design.md's Data Model table. "-" means the key must be absent.
EXPECTED_TIERS="
codebase-locator haiku medium
pattern-finder haiku medium
codebase-analyzer sonnet medium
product-behavior-analyzer sonnet medium
research-validator sonnet high
task-verifier sonnet high
task-worker - medium
"

report() {  # report <name> <count> <target> <max-allowed>
  local verdict=PASS
  if [[ "$2" == ERROR ]] || (( $2 > $4 )); then verdict=FAIL; STATUS=1; fi
  echo "$1: $2 (target $3) $verdict"
}

# grep_lines <grep args...>: prints matching lines, and returns 2 if grep errored.
grep_lines() {
  local out rc
  out="$(grep "$@")"; rc=$?
  [[ $rc -eq 2 ]] && return 2
  [[ -n "$out" ]] && printf '%s\n' "$out"
  return 0
}

count() { [[ -z "$1" ]] && echo 0 || printf '%s\n' "$1" | wc -l | tr -d ' '; }

roots() { local r; for r in $ROOTS; do printf '%s\n' "$REPO/$r"; done; }

need_tree() { [[ -d "$REPO/plugin" ]]; }

check_spawn_names() {
  local l; l="$(grep_lines -rnE 'subagent_type: *"' "$REPO/plugin")" || { report spawn-names ERROR 0 0; return; }
  l="$(printf '%s\n' "$l" | grep -vE 'subagent_type: *"(wb:[a-z-]+|general-purpose|Explore|Plan|claude|statusline-setup)"')"
  report spawn-names "$(count "$l")" 0 0
}

check_prose_spawns() {
  local l; l="$(grep_lines -rnE '(spawn|Use) the `?(task-worker|task-verifier)' "$REPO/plugin/skills")" || { report prose-spawns ERROR 0 0; return; }
  report prose-spawns "$(count "$l")" 0 0
}

check_spawn_models() {
  local files n=0 f c
  files="$(find "$REPO/plugin/skills" -name sub-agent-prompts.md 2>/dev/null)"
  [[ -d "$REPO/plugin/skills" ]] || { report spawn-models ERROR 0 0; return; }
  for f in $files; do
    c="$(awk '/subagent_type: *"/ { t=$0 } /^[[:space:]]*model: *"/ { if (t !~ /"general-purpose"/) n++ } END { print n+0 }' "$f")"
    n=$((n + c))
  done
  report spawn-models "$n" 0 0
}

check_agent_tiers() {
  [[ -d "$REPO/plugin/agents" ]] || { report agent-tiers ERROR 0 0; return; }
  local bad=0 name model effort f got_model got_effort
  while read -r name model effort; do
    [[ -z "$name" ]] && continue
    f="$REPO/plugin/agents/$name.md"
    if [[ ! -f "$f" ]]; then bad=$((bad+1)); continue; fi
    got_model="$(awk 'NR>1 && /^---$/ {exit} /^model:/ {print $2}' "$f")"
    got_effort="$(awk 'NR>1 && /^---$/ {exit} /^effort:/ {print $2}' "$f")"
    [[ "$model" == "-" ]] && model=""
    if [[ "$got_model" != "$model" || "$got_effort" != "$effort" ]]; then
      echo "  agent-tiers mismatch: $name model=${got_model:-none} effort=${got_effort:-none}" >&2
      bad=$((bad+1))
    fi
  done <<<"$EXPECTED_TIERS"
  report agent-tiers "$bad" 0 0
}

check_roster() {
  local l
  l="$(grep_lines -rnE 'claude-opus-4-8|claude-opus-5([^-]|$)|claude-sonnet-5([^-]|$)|claude-haiku-4-5|Opus 4\.8|Haiku 4\.5|Opus 5([^.]|$)|Sonnet 5([^.]|$)' "$REPO/plugin")" || { report roster ERROR 0 0; return; }
  l="$(printf '%s\n' "$l" | grep -v 'docs/reference/code-review-integration.md')"
  report roster "$(count "$l")" 0 0
}

check_haiku_effort_rule() {
  local l; l="$(grep_lines -rniE 'never annotate `?effort`? on a `?haiku' "$REPO/plugin")" || { report haiku-effort-rule ERROR 0 0; return; }
  report haiku-effort-rule "$(count "$l")" 0 0
}

check_triple_barriers() {
  local l; l="$(grep_lines -rnF '⛔⛔⛔' $(roots))" || { report triple-barriers ERROR 0 0; return; }
  report triple-barriers "$(count "$l")" 0 0
}

check_notification() {
  local l; l="$(grep_lines -rnE 'BARRIER' $(roots))" || { report notification ERROR 0 0; return; }
  l="$(printf '%s\n' "$l" | grep -iE 'agent' | grep -iE 'wait|return' | grep -v 'completion notification')"
  report notification "$(count "$l")" 0 0
}

check_caps() {
  local d dirs=() r
  for r in $(roots); do
    if [[ "$r" == "$REPO/plugin" ]]; then
      for d in skills agents docs hooks; do dirs+=("$REPO/plugin/$d"); done
    else
      dirs+=("$r")
    fi
  done
  local l; l="$(grep_lines -rwE 'CRITICAL|IMPORTANT|MUST|NEVER|ALWAYS|DO NOT' "${dirs[@]}")" || { report caps ERROR 15 15; return; }
  l="$(printf '%s\n' "$l" | grep -vE '/templates/|template\.md:')"
  report caps "$(count "$l")" 15 15
}

if [[ $# -eq 0 ]]; then
  echo "usage: $0 <check>... (spawn-names prose-spawns spawn-models agent-tiers roster haiku-effort-rule triple-barriers notification caps)" >&2
  exit 2
fi

for c in "$@"; do
  if ! need_tree; then report "$c" ERROR 0 0; continue; fi
  case "$c" in
    spawn-names) check_spawn_names ;;
    prose-spawns) check_prose_spawns ;;
    spawn-models) check_spawn_models ;;
    agent-tiers) check_agent_tiers ;;
    roster) check_roster ;;
    haiku-effort-rule) check_haiku_effort_rule ;;
    triple-barriers) check_triple_barriers ;;
    notification) check_notification ;;
    caps) check_caps ;;
    *) echo "$c: unknown check FAIL"; STATUS=1 ;;
  esac
done
exit $STATUS
