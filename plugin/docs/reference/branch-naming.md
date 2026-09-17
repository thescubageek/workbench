# Branch naming — the shipped rule

**Read this when a step directs you to.** It is the plugin's single authority on what the
working branch is called and when to change it. Skills link here rather than restating it.

## The name

```
<scope>/<snake_case_description>
```

`<scope>` is the work's most specific external anchor, chosen by this precedence:

| Precedence | Scope | Example branch |
| ---------- | ----- | -------------- |
| 1 | **Ticket key** — `[A-Z]+-\d+`, verbatim, original case | `TB-2421/combobox_aria_pattern` |
| 2 | **Release version** — `<package>-<version>` when the work targets a known release | `wb-2.1.0/branch_naming_policy` |
| 3 | **Neither is known** | `fix_stale_alias_manifests` — bare description, no slash |

- **A ticket and a version both known → the ticket wins.** It is the more specific anchor, and
  the version is recoverable from the diff while the ticket is not. Do not concatenate them.
- **`<package>`** is the shipped artifact's own name (`wb`), not the repository or directory
  name. A repo with no meaningful package name uses the bare version: `v2.1.0/...`.
- **`<snake_case_description>`** is two to five words naming *the change*, lowercase, `_`
  separated. It comes from the ticket summary, the plan's project name, or the diff — **never
  from the user's last message.** "commit and push" is an instruction to you, not a description
  of the work, and a branch named after one is the failure this rule exists to prevent.

## When to act — at the first moment a good name is knowable

Do not wait for the commit. Each of these is a trigger, and the first one to fire wins:

- A **ticket reference resolves** (`jira-context` Step 6).
- A **plan directory is created** (`create_project`) — the project name and ticket ref are both
  in hand at that moment.
- A **release version is decided** — a version bump written to a manifest, or a plan named for
  a release.
- **Before the first commit** of an implementation stage, as a backstop for work that reached
  code without any of the above firing.

## What counts as a branch that needs replacing

Rename when the current branch is any of these:

- **Missing a scope you now know.** The main case: a ticket or release version is known and the
  branch name does not carry it.
- **A placeholder.** An agent harness or worktree tool named it before the work was understood:
  a single unrelated codeword (`honiara`), a slug of the user's prompt (`commit-and-push`),
  `wip`, `feature`, `patch-1`, `claude/*`, `codex/*`, `cursor/*`, a bare date or hash.

Leave it alone when:

- It **already carries the right scope** — a differing description is not worth a rename.
- It carries a **different ticket's scope.** That branch may belong to other work; say what you
  found and ask rather than renaming.
- You are **not in a git repository**.

## How to act

**Rename in place. Never cut a second branch** — that orphans the work on the old name and
splits the history across two places.

| Current branch | Action |
| -------------- | ------ |
| A base branch (`main`, `master`, `develop`) | `git checkout -b <new-name>` |
| Any other branch | `git branch -m <new-name>` |

Three constraints on running it:

1. **Confirm with the user first.** This is a git state change, and the branch name is theirs.
   Propose the exact name and the exact command.
2. **Non-blocking.** Declined, unavailable, or not a git repo → proceed with the work on the
   current branch and note it in the stage's output. A naming preference never gates real work.
3. **A branch that has already been pushed is a different question.** `git branch -m` renames
   only the local branch, leaving the remote one behind and the upstream dangling — and if a PR
   is already open against it, the rename does not follow. Say that the branch is published,
   and let the user choose: keep the published name, or rename and follow through with
   `git push -u origin <new-name>` plus `git push origin --delete <old-name>`. Never delete a
   remote branch without that explicit go-ahead.

## Reporting it

One line, in the stage's normal output — not a section:

```
🌿 Branch: renamed honiara → TB-2421/combobox_aria_pattern
🌿 Branch: commit-and-push is a placeholder; TB-2421/combobox_aria_pattern fits — rename it?
🌿 Branch: already scoped to TB-2421 — unchanged
```
