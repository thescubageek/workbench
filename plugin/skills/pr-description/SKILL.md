---
name: pr-description
description: Draft a short, plain PR title and description in wb Technical English (WBTE) from the current branch, using the repository's own PR template (or a generic one), then create or update the PR after the user confirms. Use when the user says "write the PR description", "draft the PR", "open a PR", "create a pull request", "update the PR body", "shorten this PR description", or "/pr-description".
argument-hint: "[base-branch] [--update]"
allowed-tools: Bash, Read
---

Write the PR title, the PR body and your replies in wb Technical English (WBTE): read [technical-english.md](../../docs/reference/technical-english.md) and apply it. Keep every exempt token exactly as it is.

A reviewer reads a PR description between other work. This skill writes one that fits on about
one screen and says what changed, why, and how it was tested. The detail stays in the diff, the
plan, and the ticket.

## 1. Collect the change

1. The base branch is the first argument. If there is none, use the repository's default
   branch: `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`. If `gh` cannot
   answer, use `git symbolic-ref --short refs/remotes/origin/HEAD`, without the `origin/`.
2. Read the commits and the size of the change:

   ```bash
   git log --format='- %s' <base>..HEAD
   git diff --stat <base>...HEAD | tail -1
   ```

3. Read the diff of the files that the commits name, as much as you need to state the change.
   Do not read generated or vendored files.
4. Find the context to link:
   - The ticket key, from the branch name (`<ticket>/<description>`) or the commit subjects.
   - The plan directory, if a `docs/plans/*/tasks.md` has `git_branch:` equal to this branch.
     Link its `README.md`, handoff or `validation-report.md` for detail.
5. Check for an open PR: `gh pr view --json number,title,body,url`. If one exists, or the
   argument is `--update`, this run updates it.

## 2. Find the template

Run the template finder from this skill's base directory:

```bash
<this skill's base directory>/../../scripts/pr-template
```

- **One `repo` line.** Read that file fully, and use its headings and checklists.
- **More than one `repo` line.** List the file names, ask the user which one to use, and wait.
- **A `generic` line.** Read [templates/pr-description.md](templates/pr-description.md) NOW
  and use it.

## 3. Draft the title and the body

Read the "Pull requests and commit messages" section of
[technical-english.md](../../docs/reference/technical-english.md) NOW and apply it. In short:

- Keep the template's headings in their order. Scope each section to what a reviewer needs
  from it. Leave out an empty section, or write "None." if the template requires it.
- Give the change first, then the reason. Name behaviour and decisions, not files or commits.
- Keep exact values that matter, such as a limit, a count, or a `file:line`. Link to plans,
  logs and tables. Do not paste them.
- Keep closing keywords (`Closes #12`), ticket links, template checklists and the session's
  attribution line exactly as they are.
- Never write secrets, credentials, or personal data. In a healthcare repository, this includes
  patient identifiers and member IDs.

Then check the size. Count the words of the body without its checklists and attribution line.
If the count is over 250, cut before you show the draft: shorten each section to its scope and
move the detail behind a link. A complex change can stay longer. Say why in one sentence.

## 4. Show the draft and confirm

Show the title, the body, and the word count. Then ask one question with three choices:
create the PR (or update it), change the draft, or stop. A PR is outward-facing, so do nothing
with `gh` until the user chooses.

## 5. Create or update the PR

Write the body to a temporary file outside the repository, then run one command:

```bash
body=$(mktemp)   # then write the body to "$body"
gh pr create --base <base> --title "<title>" --body-file "$body"   # a new PR
gh pr edit <number> --title "<title>" --body-file "$body"          # an update
rm -f "$body"
```

If the branch has no upstream, `gh pr create` needs it pushed. Ask before you push, and never
force-push. Report the PR URL in one line.
