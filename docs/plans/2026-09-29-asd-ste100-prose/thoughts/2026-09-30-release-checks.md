# Release checks (P7-T4)

These are the P7-T4 commands, run on `08c285c` (after the 2.2.0 version bump) on 2026-09-30, from
the repository root.

| Check | Exit | Result |
| ----- | ---- | ------ |
| `./plugin/scripts/lint --all` | 1 | Fails only on gitignored run outputs in `evals/runs/` (MD024 duplicate headings in generated `tasks.md` files). No tracked file has an issue. See the note below |
| `./plugin/scripts/lint $(git ls-files '*.md')` | 0 | Every tracked markdown file is clean |
| `./plugin/scripts/test-lint` | 0 | 15 passed, 0 failed |
| `./plugin/scripts/test-quiet` | 0 | 9 passed, 0 failed |
| `./plugin/scripts/test-prime` | 0 | 40 passed, 0 failed. The card has 141 words |
| `./plugin/scripts/test-wbte-dictionary` | 0 | 13 passed, 0 failed |
| `python3 evals/link_check.py` | 0 | 43 templates and 4 inline steps checked. PASS |
| `python3 evals/token_check.py` | 0 | The registry passes |
| `claude plugin validate plugin/` | 0 | Validation passed |
| `claude --plugin-dir plugin plugin details wb` | 0 | `wb 2.2.0`, 37 skills. Always-on is ~3,412 tokens (2.1.1: ~3,251) |
| `git merge-tree --write-tree HEAD adversarial-loop-skill-research` | 1 | 5 conflicted paths (below) |

**The `lint --all` failure.** `wb_lint_ignored` does not ignore a path that is in both
`.gitignore` and `.wblintignore`, so `--all` lints the gitignored `evals/runs/` output. This
bug predates 2.2.0 (tasks.md, Implementation Notes). The plan's criterion is that every command
in P7-T4 exits 0, except `git merge-tree`. So this check does not meet it, and the P7 automated
box stays `[ ]` with a note.

## Merge conflicts with `adversarial-loop-skill-research` (`2fff76c`)

- `.claude-plugin/marketplace.json`
- `.claude/wb/knowledge.md`
- `.gitignore`
- `README.md`
- `plugin/.claude-plugin/plugin.json`

`plugin/hooks/wb-prime.sh` and all 12 link-line locations merge without a conflict. So does
`CHANGELOG.md`, which 3.0.0 also changes.

## Compared with the expected set (P7-T5)

The expected set is the link lines, `wb-prime.sh`, the manifests, `README.md`, `CHANGELOG.md`,
`.gitignore`, and `CLAUDE.md`.

| Path | Expected? | Action |
| ---- | --------- | ------ |
| `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | yes | none. Take the 3.0.0 version |
| `README.md` | yes | none. Keep both. The resolution is in the handoff |
| `.gitignore` | yes | none. Keep one copy of each line, plus `evals/runs/` |
| `.claude/wb/knowledge.md` | **no** | Not reduced: the new entry records a durable fact that the harness depends on. The handoff has the resolution note: keep both appended entries |

A second `git merge-tree` run, after the handoff note, gives the same 5 paths. No path outside
the expected set is left without a resolution note.
