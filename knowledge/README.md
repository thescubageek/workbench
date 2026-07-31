# Knowledge Store

Cross-ticket knowledge about **this repository**, accumulated by wb runs and drained through a
human-gated promotion pass.

The wb pipeline is per-ticket by construction: every artifact lands in one timestamped
`docs/plans/<date>-<slug>/` directory that nothing else reads. Four commands already tell the agent to
capture what it learned, and all four terminate locally. This directory is the destination they never
had.

## Layout

| Path | What it holds | Who may write | Read by retrieval |
| --- | --- | --- | --- |
| `entries/` | Promoted knowledge, one file per entry | Humans, via a reviewed promotion diff | **Yes** |
| `staging/` | Raw automatic captures | Anything, ungated | **Never** |
| `SCHEMA.md` | The entry format and ID scheme | Humans | — |
| `INDEX.md` | Generated from `entries/`; never hand-edited | The index generator | — |

`INDEX.md` does not exist yet — there is nothing promoted to index. The generator is not a Phase 1
deliverable; when it lands, the file is written by it and never by hand.

The two trees are separate because they carry different trust. See `entries/README.md` and
`staging/README.md` — the distinction is the whole security model, not a filing convention.

## This branch

The store lives on `thescubageek/self-learning-loops-research`, a long-lived branch that is **never
merged into `main`**. Knowledge improves continuously; plugin delivery is discrete and version-keyed
(`CLAUDE.md` → "Releasing New Commands/Skills/Agents"). Keeping the store off `main` decouples the two.

Access it with `scripts/knowledge-worktree`, which prints the store root path and resolves to an
existing checkout wherever one is — including a sibling Conductor workspace, since git allows a branch
to be checked out in only one worktree at a time.

```bash
STORE="$(scripts/knowledge-worktree)" || exit 1   # fails loudly; never a silent no-op
ls "$STORE/entries"
```

### `main` merges forward into this branch. Never rebase

```bash
git checkout thescubageek/self-learning-loops-research
git merge origin/main          # correct
git rebase origin/main         # NEVER
```

Every entry records the commit SHA it was verified against, and staleness is computed as
`git diff <verified-sha>..HEAD -- <cited paths>`. **Rebasing rewrites the commits those SHAs point at**,
which would silently invalidate every stored reference and destroy the audit trail the design rests on.
The same applies to force-pushing this branch: don't.

Merging forward also keeps the code beside the knowledge, so an entry's `file:line` references resolve
in the store worktree without a second fetch.

The invalidation sweep runs **on sync** — after each forward merge — not only on demand, because every
`main` commit is potential invalidation churn.

## Scope

The store is scoped to the repository it lives in. Entries here are about the wb harness, because in
this repo the harness *is* the codebase. When wb is used on another project, that project gets its own
store about its own code. Cross-repo transfer is deliberately out of scope: negative transfer — where a
retrieved prior strategy makes a dissimilar task worse than no memory at all — is a measured failure
mode, and per-repo scoping is the strongest available counter.

## What is not here yet (v1)

- **No eval corpus.** Promoted entries record a prediction so they are checkable retroactively, but v1
  cannot demonstrate the store improves anything. Don't claim it does.
- **No CI or branch-protection layer.** The enforcement hook covers the agent write path only; human and
  out-of-band writes are unguarded. Build the CI layer *before* the first unattended run.
- **Procedural and episodic entries that cite no files decay undetected.** The git sweep only catches
  entries with cited paths. Handled by curation review, not by invalidation.
