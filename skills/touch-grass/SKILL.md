---
name: touch-grass
description: Use when a research, analysis, audit, migration, or review task is too big for one sitting and must be paced across many segments over hours or days — an extreme deep dive, exhaustive review, or multi-day investigation. Work in checkpointed segments, self-schedule each resume with ScheduleWakeup, and pace spending against the user's time↔money↔quality priorities instead of blasting tokens. Trigger phrases "touch grass", "deep dive", "long-horizon research", "paced research", "paced deep-dive", "long-running analysis", "multi-day research loop", "checkpoint and resume".
---

# Touch Grass

For high-effort work too big for one sitting: don't grind straight through. Work in **segments**, **checkpoint everything to a durable file**, **schedule your own resume**, and **pace spending** against what the user values. Nickname logic: take budget-conscious breaks instead of burning the whole token window in one blast.

This is a **general** discipline — research is the leading example, but it applies equally to large audits, multi-day migrations, exhaustive code/document reviews, and competitive or forensic deep dives. It works on any capable model; nothing here is model-specific.

**Core principle:** A long task survives interruption only if its entire state lives in a file a cold-context model could resume from. Pace the work to the *next* step's cost, not a fixed clock.

## The Iron Law

```
CHECKPOINT BEFORE YOU THINK YOU NEED TO, AND RESCHEDULE EVERY SINGLE TURN.
RESUME MUST BE LOSSLESS FROM state.md ALONE.
```

Five non-negotiables (each is a bug someone already hit — do not improvise around them):

1. **Reschedule EVERY live turn.** A pending `ScheduleWakeup` does NOT survive an intervening user message — any user turn kills the timer. The turn that handles it MUST re-schedule before ending. (This caused an 11-hour stall in the prototype.)
2. **NEVER fan out speculatively.** Depth over breadth. Fully resolve one sub-question before opening the next. One segment = one sub-question.
3. **Verify load-bearing claims with 2 independent sources.** When a claim gates the decision, read the primary source in full; prefer direct API/repo/document inspection over search summaries. Re-verify insider/internal claims against the live source before use.
4. **NEVER cut silently.** Every conscious scope cut gets a row in the budget ledger ("skipped X because Y").
5. **Fresh eyes = fresh CONTEXT, not elapsed time.** A same-session wakeup does NOT reset context and is worthless as a critic.

## When to activate

Activate when **all** hold:
- The task serves one clear decision or deliverable, and
- It's too large to finish in one context window / one sitting, and
- Quality matters enough that grinding through in one pass would degrade it, and
- You can pace it — there's no hard "must finish in the next 3 minutes" constraint.

If it fits in one sitting, don't. This skill's overhead only pays off across segments.

## Inputs (ask if missing)

1. **The question** — the one decision or deliverable the whole loop serves. Every segment must trace to it; cut lines of inquiry that don't.
2. **Triad priorities** — rank **time / money / quality**. This sets pacing stance.
3. **Deadline** (optional) — changes the pacing math.
4. **Checkpoint directory** — default `.context/<slug>/`.

## Step 0 — Create the checkpoint file FIRST

Before any research, copy `state-template.md` (in this skill dir) to `<checkpoint-dir>/state.md` and fill in the Header + Segment plan. The checkpoint file is the spine. Its sections, in order, are the contract:

- **Header** — question, deliverable spec, operating model, deadline, checkpoint/deliverable paths. Numbered **AMENDMENT blocks** appended verbatim when the user changes scope mid-run (never rewrite history — amendments are how later segments inherit changes).
- **Segment plan** — checkbox list. Each segment = one sub-question, sized before running (small/medium/large + est. calls).
- **Budget ledger** — table: segment | estimate | actual | notes. Log every conscious cut.
- **Findings** — one dense, self-contained block per segment, with a confidence level.
- **Decision so far** — running verdict, updated every segment.
- **Sources ledger** — source | takeaway | confidence, with URLs/paths.
- **Next action** — written concretely enough that a cold-context model could execute it verbatim.

## Segment protocol (every wake)

1. **Reload `state.md`.** It is your only memory.
2. **Run exactly the "Next action" segment.** Depth over breadth; fully resolve it before opening the next. Never fan out speculatively.
3. **Verify load-bearing claims** with 2 independent sources (primary sources in full when a claim gates the decision).
4. **Write back**: FINDINGS block + budget-ledger row + updated Decision-so-far + new Next action. Check off the segment.
5. **Schedule the next wake** (rules below).
6. **End-of-turn message: lead with what you FOUND, not what you did.**

## Pacing algorithm

The mechanism is the **`ScheduleWakeup`** tool. Size the wait to the *next* segment's anticipated cost — not a fixed cadence.

- **Effort-aware chunking.** Cheap next segment (local reads, synthesis, modeling) → chain it NOW in the same warm-cache turn; don't schedule at all. Expensive next segment (web fan-out, big PDF reads) → checkpoint and wait for the token window to refill.
- **Cache-window economics.** Prompt cache TTL ≈ 5 min. Waits under ~270s keep the cache warm; anything longer pays a cache-miss, so commit to a real wait (1200s+). **Never pick ~300s** — it's the worst of both: you pay the miss without amortizing it.
- **Don't poll harness-tracked work.** If you kicked off a background agent/command the harness tracks, it re-invokes you on completion — scheduling a short poll for it is wasted. Schedule against *external* state (a deadline, an overnight gap, a source that updates slowly) or against token-window refill.
- **Deadline-aware.** slack = deadline − (remaining segments × realistic per-segment wall-clock). Shrink waits as slack shrinks. If the deadline becomes unreachable, **report it** — never silently degrade quality.
- **Budget stance.** When money outranks time, prefer wall-clock (longer waits) over paid tokens; invert when time outranks money. When unsure which leg bends, ask.

## Wakeup protocol — hard rules

- **MUST end EVERY turn with a fresh `ScheduleWakeup`** while the loop is live. (See Iron Law #1.)
- The wakeup **`prompt` must be self-contained**: reload instruction + checkpoint path + the every-turn-reschedule rule itself, so a cold resume re-enters the loop correctly. For an unattended self-paced loop with no user prompt, use the `<<autonomous-loop-dynamic>>` sentinel.
- If a turn is interrupted before scheduling, the next resume must notice and re-enter the loop from `state.md`.
- **Machine sleep can block wakeups** when no session holds a power assertion. For unattended overnight gaps, tell the user to keep the machine awake.
- A user message mid-loop is **not noise**: check it for AMENDMENTs first, record them verbatim in the Header, then continue.

## Quality moves

- **Fresh-context critic before calling it done.** Spawn a clean-context subagent (via the `Agent` tool) that has no prior knowledge; give it exactly the *original spec + the deliverable + the checkpoint*, and ask for severity-ranked findings (**BLOCKER / MAJOR / MINOR**). Same-session wakeups do NOT count — they carry your context and rubber-stamp your own work. (Prototype yield: 1 blocker + 5 majors on a memo the authoring context thought was finished.)
- **Fix all findings; source anything the critic flags as unverified; log the critic pass** in `state.md`.

## End conditions — stop scheduling

Deliverable written **and** critic pass applied **and** user informed → **STOP** rescheduling. A finished loop that keeps waking is a bug. Say plainly that the loop is closed.

## Red flags — STOP

- Ending a live-loop turn without a fresh `ScheduleWakeup`.
- Uniform hourly chunking when the next segment is 5 minutes of local reads.
- Opening a second sub-question before the current one is resolved.
- Citing an insider/internal claim about a fast-moving source without re-verifying it live.
- A scope cut that isn't in the budget ledger.
- Treating a same-session wakeup as a "fresh eyes" review.
- A completed deliverable that's still scheduling wakeups.

## Integration with wb commands

touch-grass is a **runtime discipline**, orthogonal to the wb research→design→execution pipeline — use it *inside* a long `wb:create_research` or a multi-day investigation, not as a pipeline stage. It composes with:

- **`tracer-bullet`** — before the first segment, fire one probe at the riskiest load-bearing assumption so the segment plan doesn't build on a wrong premise.
- **`wb:loop`** — use `wb:loop` for *fixed-interval* recurring tasks; use touch-grass when the cadence must be *effort-aware and self-paced*. They are different tools for different rhythms.
- **`verification-before-completion`** — the fresh-context critic pass is how touch-grass satisfies "evidence before assertions" for a long-horizon deliverable.
