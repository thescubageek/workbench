---
name: explore-design
description: Optional facilitated architecture stage between research and design. Airs the alternatives, runs the trade-off discussion, and converges only on explicit approval — recording the decision at the top of a thoughts/ document for create-design to formalize. Use when research surfaced more than one viable approach and the choice has not been made. Never writes design.md.
argument-hint: "[project-directory] [decision-topic]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Explore Design Options

An optional stage between research and design. The pipeline otherwise goes from facts straight to a locked decision, so the reasoning behind an architecture choice survives only as design.md's Rejected Alternatives — written by the same pass that chose. This stage exists to air the alternatives *before* one is picked, and to keep the reasoning.

Supporting file in this directory (read it when its step directs you to — never paraphrase from memory):

- `templates/` — [exploration-document.md](templates/exploration-document.md) (Step 6) · [completion-message.md](templates/completion-message.md) (Step 7)
- [../../docs/reference/plan-intent.md](../../docs/reference/plan-intent.md) — the README's `## Intent` section that Step 2 frames against, and how Step 6 records an amendment

**If a directed read fails, stop — do not continue from memory.** These files live outside your
project, so a read can be refused. Say which file was refused, that reads outside the working
directory are gated, and that the fix is to allow the read once or to relaunch with
`--add-dir <plugin-path>`. Do not route around a refusal with `cat`.

This stage needs from you: reactions to the directions as they are drafted, and an explicit approval of one before anything is recorded.

**Output discipline**: act on barriers silently; don't restate the plan between steps; emit only the artifact and a one-line completion summary.

## Model Self-Check (do this FIRST)

This is the most judgment-dense, divergent stage in the workflow. **Recommended: Opus 5.5 at `high`. Available upshift: Fable 5.1.**

Check which model this session is running. If it is below Opus 5.5, surface this once:

```
⚠️ Model check: this session is running [model]. explore-design is a
judgment-heavy discussion stage — Opus 5.5 is recommended, and Fable 5.1
is available as an upshift if the decision is genuinely architectural.
Lighter models tend to converge too quickly and miss trade-offs.

Continue on [model], or restart this stage in a stronger session?
```

**Do not block.** If the user chooses to continue, proceed. This is guidance, not enforcement, and it follows the standing policy: advise, never auto-switch. If Fable is elected, run it at `effort: high` — never `xhigh` or `max`.

## Scope: possibilities, not commitments

This stage frames, diverges, discusses, converges on approval, and records. A commitment made
here would skip the review that `create-design` exists for.

- Do not write `design.md` — that is `create-design`'s artifact, and it has one writer
- Do not converge without explicit user approval
- Do not present a single option and call it a discussion
- Do not start implementing, prototyping, or editing source

The output is a `thoughts/` document. If the user walks away mid-exploration, nothing is committed to and nothing is lost.

## Initial Response

When invoked, check for arguments:

1. **If directory and topic provided** (e.g., `/wb:explore-design docs/plans/2025-01-08-auth/ "session storage"`):
   - Use `$1` as project directory, `$2+` as the decision topic
   - Begin at Step 1

2. **If no arguments**:

   ```
   I'll facilitate an architecture discussion. Please provide:
   1. Path to the project documentation directory
   2. What decision are we exploring? (e.g., "how sessions are stored")

   I'll frame the decision space from research.md, draft the directions worth
   considering, and we'll talk through the trade-offs. Nothing gets decided
   until you say so.
   ```

## Process Steps

### Step 1: Entry Gate and Context Reading

⛔ BARRIER 1: research.md is read in full before anything is framed — options need the facts

1. **Check research.md exists and is complete.** This stage reasons from facts; without them it
   generates plausible-sounding options with nothing underneath. If research.md is missing or
   `draft`, say so and stop — `/wb:create-research` comes first.

2. **Read research.md in full.** The constraints that bound every direction come from here.

3. **Read `design.md` if it exists.** If it already records a decision on this topic, say so and
   ask whether the user wants to revisit it — do not silently re-open a settled question.

4. **Check `thoughts/` for an existing exploration on this topic.** If one exists, read it fully.
   A second exploration of the same question should build on the first, not restart it.

5. **Read `.claude/wb/knowledge.md` if it exists** — durable repository facts with verification
   hints. Treat entries as dated claims to re-check, not as current truth.

6. **Read the README's `## Intent` section**, and
   [../../docs/reference/plan-intent.md](../../docs/reference/plan-intent.md) with it. The Goal
   bounds the decision space. A plan with no Intent section has no such obligation. Say so once,
   in the reference doc's form.

### Step 2: Frame the Decision Space

**Identify what is actually being decided**

Before options, get the question right. A badly framed question produces a well-argued wrong answer.

1. **State the decision in one sentence** — the question, not the candidates. Then say how the
   decision serves the Goal, and which success statements it bears on, by ID.
2. **State what is NOT being decided.** The Intent's Non-goals are already out of scope here. Adjacent questions will surface; naming them as
   out-of-scope now stops the discussion sprawling.
3. **List the constraints** any answer must satisfy, each traced to research.md with `file:line`
   or to something the user said.
4. **Name what would make this decision wrong** — the assumption that, if false, invalidates
   whichever way it goes. If that assumption is cheaply checkable, check it now: an hour spent
   here can delete whole directions before they are argued.

Present the framing and **confirm it before diverging**. If the frame is wrong, everything after it is wasted.

### Step 3: Diverge — Draft Directions

Draft **two to four** genuinely different directions. Not variations on one idea.

For each: its concrete shape, a precedent in this codebase (`file:line`) or an explicit "none",
what it buys, what it costs, and the condition under which it is the wrong choice.

Two rules that make this worth doing:

- **No strawmen.** Every direction must be one a reasonable engineer would defend. A lineup
  with one obvious winner is a decision already made, presented as a discussion.
- **"Costs" must be specific.** "More complex" is not a cost. "Adds a second write path that
  has to stay consistent with final-submit" is.

If you cannot find a second defensible direction, say so plainly — the decision may already be
made by the constraints, and that is a useful finding, not a failure of this stage.

### Step 4: Discuss — Trade-off Interview

Work through the trade-offs **with the user**, one thread at a time. This is a conversation, not a report.

- Ask which costs they are actually willing to pay — the answer is usually not what the options table implies
- Surface where two directions differ only cosmetically, and collapse them
- Follow the user's reasoning; when they rule something out, capture **why** in their words
- Let a hybrid emerge if it does, but do not manufacture one to avoid a choice

**⛔ BARRIER 2: Do not converge here** — the user decides when the discussion ends. Discussion
continues until the user signals they are ready.

### Step 5: Converge — ⛔ CHECKPOINT

**Converge only on explicit approval.**

State the direction you believe the discussion reached, the rationale in the user's terms, and what it gives up. Then ask for confirmation in as many words.

Silence, "sounds good", or moving on is **not** approval. A stage whose whole purpose is to make a decision deliberate must not infer one.

If the user is not ready, return to Step 4.

### Step 6: Record the Decision

Read [templates/exploration-document.md](templates/exploration-document.md) NOW and write `[project-dir]/thoughts/YYYY-MM-DD-<topic>.md`.

**The decision record goes at the top of that document**, before the exploration. This is not
formatting: `create-design` scans `thoughts/` for that section and formalizes it. A record
buried below the discussion is a record the consuming stage will not find, and the feature then
fails silently — `create-design` simply takes its no-record path and regenerates options,
discarding everything this stage produced.

Record the **rejected** directions and why, in the same document. That is what `create-design`
carries into design.md's Rejected Alternatives instead of inventing them.

**A direction that changes the Goal or the Non-goals is an amendment, not a detail.** Name the
change and get the user's explicit approval for it, separately from approval of the direction.
Then edit the README's `## Intent` in place and add the dated Amendments line, as
[../../docs/reference/plan-intent.md](../../docs/reference/plan-intent.md) describes. Without
that approval, the direction is out of bounds. Return to Step 4.

**This stage does not write `design.md`.** It has one writer.

### Step 7: Confirm Completion

Read [templates/completion-message.md](templates/completion-message.md) NOW and present it.

## Important Notes

### Why this stage is optional

Most decisions do not need it. It earns its cost when research surfaced **more than one viable
approach** and the choice is not obvious — a one-way door, a load-bearing architectural split, a
place where the codebase offers no precedent. Running it on a decision that was never in doubt
produces a document nobody reads.

### What this stage is not

- Not research — it reasons from research.md, it does not gather facts
- Not design — it produces a recorded decision, not the design document
- Not implementation — nothing is built or prototyped here

### Cold-start discipline

A future session reads the exploration document, not this conversation. Write it so the
reasoning stands alone: quote the user where their words settled something, and state the
rejected directions concretely enough that nobody re-litigates them by accident.
