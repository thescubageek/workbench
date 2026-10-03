---
task: P5-T3
created: 2026-09-19 16:20
cwd: /Users/scraig/conductor/workspaces/workbench/ankara
git_commit: 7ed03e5
git_branch: adversarial-loop-skill-research
tree: clean
status: complete
---

# P5-T3 — release checks for 3.0.0

Run on the clean tree **after** the P5-T2 bump commit, because `claude plugin tag` refuses a
dirty tree without `--force`. Output is verbatim; the working directory is in the frontmatter
because a probe whose cwd is unrecorded is the failure mode this plan hit once already.

All nine pass. `check-guards`, `test-count` and `test-quiet` also run inside
`./plugin/scripts/check`, which is green on this commit.

## 1. Manifest versions agree

```text
$ diff <(grep -o '"version": "[^"]*"' plugin/.claude-plugin/plugin.json | head -1) \
       <(grep -o '"version": "[^"]*"' .claude-plugin/marketplace.json | head -1)
(empty)   both read "version": "3.0.0"
```

## 2. Lint clean repo-wide

```text
$ ./plugin/scripts/lint --all
✅ All markdown files are clean!
```

## 3. Release check

```text
$ claude plugin tag --dry-run plugin/
Plugin:  wb
Version: 3.0.0 (from plugin.json)
Marketplace entry: plugins[0] in .../.claude-plugin/marketplace.json (version: 3.0.0)
Tag:     wb--v3.0.0

✔ Dry run — would create tag wb--v3.0.0 at HEAD
  git tag -a wb--v3.0.0 -m "wb 3.0.0"
  git push origin refs/tags/wb--v3.0.0
exit=0
```

The tag name confirms the `<name>--v<version>` convention `.claude/wb/knowledge.md` records,
and that the dry run reads **both** manifests and agrees they match.

## 4. No stack or employer vocabulary, word-anchored

```text
$ grep -rniE '\b(ruby|rails|rspec|postgres|postgresql|redis|docker|rubocop|hellobrightline|brightline)\b|bundle exec' plugin/
(no output)   grep exit 1
```

The anchoring is what makes this runnable at all: unanchored, it matched `rspec` inside
"perspective" and `redis` inside "rediscovering" and could never pass.

## 5. Every reference link in every skill resolves

```text
$ python3 -c "...resolver over plugin/skills/*/SKILL.md..."
(no MISS)
```

## 6. CHANGELOG

```text
$ grep -n '^## \[3.0.0\]' CHANGELOG.md
14:## [3.0.0] — 2026-09-18
```

**Open, and deliberately not changed here**: the entry is dated 2026-09-18, the day it was
written, and the release is not cut until P5-T4 and P5-T5 pass. Set the date when the tag is
created rather than guessing it now — a changelog dated before its own release is wrong in a
way nobody notices.

## 7. Docs accurate at release

```text
$ python3 -c "...help/README/scripts coverage + absent-skill check..."
(no gaps)
```

This one **failed** when first run on 2026-09-19: `test-phi-patterns` and `lib_mutate.py` were
missing from README's Scripts section, both added during round 4. That is precisely the drift
the criterion exists to catch, caught inside the release it would otherwise have shipped in.

## 8. Guard check

```text
$ ./plugin/scripts/check-guards
✅ check-guards: no unguarded measurements (145 files scanned)
exit=0
```

The file count is asserted by `test-guards`' integrity layer, so "145" is a measurement rather
than a claim.

## 9. `test-count`, and `count`'s zero-versus-failure distinction

```text
$ ./plugin/scripts/test-count
test-count: 18 passed, 0 failed, 0 skipped

$ ./plugin/scripts/count 'zzz-no-such-pattern' README.md
0
exit=0                       # a real zero, and the exit code says so

$ ./plugin/scripts/count 'x' /tmp/definitely-not-a-file
count: no such file: /tmp/definitely-not-a-file
exit=2                       # not a zero — the whole reason count exists
```

## What this does not establish

Nothing here runs a skill. P5-T4 is the behavioural half — a session from a recorded cwd
outside the plugin directory, confirming `wb:adversarial-review` loads, its supporting files
read, and the reconnaissance summary names the tier and the axis that set it. These checks are
static; a green static gate over a skill that will not load is exactly the shape this plan has
been arguing about since Phase 1.
