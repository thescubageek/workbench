#!/usr/bin/env bash
# Contract test for prompt-checks.sh: a clean fixture passes every check, one planted
# failure per check makes exactly that check FAIL, and an unreadable tree is a FAIL.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CHECKS="$HERE/prompt-checks.sh"
PASS=0; FAIL=0
check() { if [[ "$2" == 1 ]]; then echo "✓ $1"; PASS=$((PASS+1)); else echo "✗ $1"; FAIL=$((FAIL+1)); fi; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

make_fixture() {
  local r="$1"; rm -rf "$r"; mkdir -p "$r/plugin/skills/x" "$r/plugin/agents" "$r/plugin/docs/reference" "$r/plugin/hooks"
  cat > "$r/plugin/skills/x/sub-agent-prompts.md" <<'M'
Task({
  subagent_type: "wb:codebase-locator"
})
Task({
  subagent_type: "general-purpose",
  model: "sonnet"
})
M
  cat > "$r/plugin/skills/x/SKILL.md" <<'M'
⛔ BARRIER 2: every spawned agent has returned (wait for a completion notification from each one) — synthesis on a partial set misses a report
Read the prompt and spawn the `wb:task-worker` agent with it.
The roster is Opus 5.5, Sonnet 5.5, Haiku 5.5, and Fable 5.1 (`claude-opus-5-5`).
M
  echo "Rules." > "$r/plugin/docs/reference/technical-english.md"
  echo "# hook" > "$r/plugin/hooks/wb-prime.sh"
  local a
  for a in "codebase-locator haiku medium" "pattern-finder haiku medium" "codebase-analyzer sonnet medium" \
           "product-behavior-analyzer sonnet medium" "research-validator sonnet high" "task-verifier sonnet high"; do
    set -- $a
    printf -- '---\nname: %s\ndescription: d\ntools: Read\nmodel: %s\neffort: %s\nmaxTurns: 25\n---\n\nBody.\n' "$1" "$2" "$3" > "$r/plugin/agents/$1.md"
  done
  printf -- '---\nname: task-worker\ndescription: d\ntools: Read\nskills: [tdd-discipline]\neffort: medium\nmaxTurns: 60\n---\n\nBody.\n' > "$r/plugin/agents/task-worker.md"
}

ALL="spawn-names prose-spawns spawn-models agent-tiers roster haiku-effort-rule triple-barriers notification caps"
R="$TMP/repo"
make_fixture "$R"
out="$(PROMPT_CHECKS_REPO="$R" "$CHECKS" $ALL)"; rc=$?
check "clean fixture: exit 0" "$([[ $rc == 0 ]] && echo 1)"
for c in $ALL; do check "clean fixture: $c PASS" "$(grep -q "^$c: .* PASS$" <<<"$out" && echo 1)"; done

plant() {  # plant <check> <shell command run inside the fixture>
  make_fixture "$R"; (cd "$R" && eval "$2")
  local o; o="$(PROMPT_CHECKS_REPO="$R" "$CHECKS" $ALL)"; local rc=$?
  check "planted $1: exit 1" "$([[ $rc == 1 ]] && echo 1)"
  check "planted $1: $1 FAIL" "$(grep -q "^$1: .* FAIL$" <<<"$o" && echo 1)"
  local others; others="$(grep ' FAIL$' <<<"$o" | grep -v "^$1:" | wc -l | tr -d ' ')"
  check "planted $1: no other check FAILs" "$([[ $others == 0 ]] && echo 1)"
}
plant spawn-names        'printf "Task({\n  subagent_type: \"codebase-analyzer\"\n})\n" >> plugin/skills/x/sub-agent-prompts.md'
plant prose-spawns       'echo "Then spawn the \`task-verifier\` agent." >> plugin/skills/x/SKILL.md'
plant spawn-models       'printf "Task({\n  subagent_type: \"wb:pattern-finder\",\n  model: \"haiku\"\n})\n" >> plugin/skills/x/sub-agent-prompts.md'
plant agent-tiers        'sed -i.bak "s/^effort: medium$/effort: low/" plugin/agents/codebase-locator.md && rm plugin/agents/*.bak'
plant roster             'echo "Use Opus 4.8 for design." >> plugin/skills/x/SKILL.md'
plant haiku-effort-rule  'echo "Never annotate \`effort\` on a haiku spawn." >> plugin/skills/x/SKILL.md'
plant haiku-effort-rule  'echo "**Never annotate \`effort\` on a \`haiku\` spawn.**" >> plugin/skills/x/SKILL.md'
plant triple-barriers    'echo "**⛔⛔⛔ BARRIER 9: done ⛔⛔⛔**" >> plugin/skills/x/SKILL.md'
plant notification       'echo "⛔ BARRIER 3: wait for every agent to return — synthesis needs all reports" >> plugin/skills/x/SKILL.md'
plant caps               'for i in $(seq 16); do echo "You MUST do step $i." >> plugin/skills/x/SKILL.md; done'

# A tree the checks cannot read must FAIL, never PASS with a count of 0.
o="$(PROMPT_CHECKS_REPO="$TMP/missing" "$CHECKS" triple-barriers)"; rc=$?
check "missing tree: exit 1" "$([[ $rc == 1 ]] && echo 1)"
check "missing tree: FAIL, not PASS" "$(grep -q 'FAIL$' <<<"$o" && echo 1)"

echo "PASS=$PASS FAIL=$FAIL"
[[ $FAIL -eq 0 ]]
