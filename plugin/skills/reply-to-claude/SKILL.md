---
name: reply-to-claude
description: Reply to a claude[bot] PR review with a comment that maps one-to-one to its findings and states the pushback explicitly — what was fixed, what was rejected and why, and what was verified against real source. Use when the user says "reply to claude", "respond to the bot review", "answer claude's review", or after fixing what a bot review raised.
argument-hint: "[<pr#>]"
allowed-tools: Read, Glob, Grep, Bash, Write
---

# Reply to a bot review

`claude[bot]` reviews a pull request and leaves findings. This composes the reply: one entry per
finding, saying what actually happened to it.

**Why the reply matters more than it looks.** A review round ends with the bot's findings and your
changes sitting in separate places, and nothing connects them. A reply that maps one-to-one is
what lets the next reader — human or bot — see which findings were accepted, which were rejected,
and on what evidence. A reply that says "addressed feedback" carries none of that.

## Preconditions

- `gh` available and authenticated, and a pull request for the current branch.
- A `claude[bot]` review to reply to. If there is none, say so and stop — this skill answers a
  review; it does not solicit one.

## Step 1: Resolve the pull request and the repository

Take the PR number from the argument if given, otherwise from the current branch. **Derive the
repository rather than assuming it:**

```bash
gh repo view --json nameWithOwner --jq .nameWithOwner
gh pr view --json number,headRefName,url
```

## Step 2: Collect the findings, from all three surfaces

Bot findings arrive on three different GitHub surfaces, and a reply that misses one looks like it
ignored a finding:

```bash
gh api "repos/$REPO/pulls/$PR/reviews"   --jq '.[] | select(.user.login=="claude[bot]") | .body'
gh api "repos/$REPO/pulls/$PR/comments"  --jq '.[] | select(.user.login=="claude[bot]") | "\(.path):\(.line) \(.body)"'
gh api "repos/$REPO/issues/$PR/comments" --jq '.[] | select(.user.login=="claude[bot]") | .body'
```

**The login is `claude[bot]`, not `claude`.** A filter on `claude` matches nothing on the API and
returns silently, which reads as "no findings" rather than as an error. Confirm the filter matched
something before concluding there is nothing to reply to.

**The bot edits its comment in place** as it works, so the newest body is the whole of what it
said — compare `updated_at`, not just whether a new comment appeared.

## Step 3: Decide each finding's disposition before writing anything

Read [../adversarial-review/reference.md](../adversarial-review/reference.md) NOW for the five
dispositions. They apply unchanged here: a bot's finding is a claim, and a label it assigned
itself is not evidence.

**Verify against real source, not memory.** When a finding turns on a library's behaviour, read
the installed version of that library — not what you recall of it, and not a summary. A bot
finding that is wrong is common enough that applying them unexamined introduces defects.

## Step 4: Write the reply to a file, then post it

```bash
gh pr comment "$PR" --body-file /tmp/reply.md
```

Compose the body with the Write tool rather than a shell heredoc — backticks, `$`, and quotes in
a code-heavy reply get mangled by the shell, and the mangling is silent.

The body:

```text
@claude Thanks — here is what changed and what did not.

**Fixed**
- <finding, one line> — <what changed, and where>

**Rejected**
- <finding, one line> — <why it does not hold, with the file:line that disproves it>

**Rejected remedy, finding accepted**
- <finding> — real, but <why the suggested fix was wrong>; did <what> instead

**Deferred**
- <finding> — <why it is out of scope here, and where it is tracked>
```

Three rules for the body:

- **The leading `@claude` re-summons the bot.** Omit it and the reply is a comment nobody reads.
- **Every finding it raised gets a line.** A finding you silently skip reads as one you missed.
- **State the pushback plainly.** "This does not hold because `parser.py:88` already rejects that
  input" is useful to a reader; "not applicable" is not. If a suggested fix would have broken
  something, say what, and say how you confirmed it.

## Step 5: Report

One line: the comment URL, how many findings were fixed, rejected and deferred, and — if it is
worth knowing — how the source scored. *"Four of five findings did not hold"* is information the
human needs in order to weigh the next round.
